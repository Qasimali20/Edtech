from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import update_session_auth_hash
from .forms import registerForm
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
# Create your views here.

def home_view(request):
    return render(request, 'login/home.html')

def register_view(request):
    if request.method == "POST":
        form = registerForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')  # Redirect to login page after successful registration
    else:
        form = registerForm()

    return render(request, 'login/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return JsonResponse({'message': 'Login successful!'})
        else:
            return JsonResponse({'message': 'Invalid username or password.'}, status=400)

    return render(request, 'login/login.html')


def logout_view(request):
    if request.method == "POST":
        # Check if the logout confirmation flag is set in the session
        if request.session.get('logout_confirmed', False):
            logout(request)
            request.session.flush()
            messages.success(request, "You have been logged out.")
            return redirect('home')  # Redirect to home page after logout
        else:
            # Set a flag in the session to indicate the confirmation step
            request.session['logout_confirmed'] = True
            return render(request, 'login/logout.html')
    
    # Handle other methods if needed (e.g., GET)
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'login/profile.html')

# Protected view
class ProtectedView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request):
        return render(request, 'login/protected.html')

# Request Password Reset View
class RequestPasswordResetView(View):
    def get(self, request):
        return render(request, 'login/request_reset.html')

    def post(self, request):
        username = request.POST.get('username')
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Construct the password reset URL
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm') + f'?uidb64={uid}&token={token}'
            )

            # Send reset URL to the user
            send_mail(
                'Password Reset Request',
                f'Please click the link below to reset your password:\n{reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )

            messages.success(request, 'Password reset link sent to your email.')
            return render(request, 'login/request_reset.html')
        else:
            messages.error(request, 'Username not found.')
            return render(request, 'login/request_reset.html')

# Password Reset Confirm View
class PasswordResetConfirmView(View):
    def get(self, request):
        uidb64 = request.GET.get('uidb64')
        token = request.GET.get('token')
        
        if uidb64 and token:
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None
            
            if user is not None and default_token_generator.check_token(user, token):
                form = SetPasswordForm(user=user)
                return render(request, 'login/reset_confirm.html', {'form': form})
            else:
                messages.error(request, 'The link is invalid or has expired.')
                return redirect('home')
        else:
            return redirect('home')

    def post(self, request):
        uidb64 = request.GET.get('uidb64')
        token = request.GET.get('token')
        
        if uidb64 and token:
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None
            
            if user is not None and default_token_generator.check_token(user, token):
                form = SetPasswordForm(user=user, data=request.POST)
                if form.is_valid():
                    form.save()
                    update_session_auth_hash(request, user)  # Keep the user logged in after password change
                    # messages.success(request, 'Your password has been reset successfully.')
                    return render(request, 'login/reset_confirm.html', {'form': form, 'password_reset_done': True})
                else:
                    return render(request, 'login/reset_confirm.html', {'form': form})
            else:
                messages.error(request, 'The link is invalid or has expired.')
                return redirect('home')
        else:
            return redirect('home')

