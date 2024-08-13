from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from .forms import registerForm
from django.contrib import messages
# Create your views here.

def home_view(request):
    return render(request, 'articles/home.html')

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

    return render(request, 'articles/register.html', {'form': form})
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('protected')  # Redirect to protected page after login
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'articles/login.html')

    return render(request, 'articles/login.html')

def logout_view(request):
    if request.method == "POST":
        # Check if the logout confirmation flag is set in the session
        if request.session.get('logout_confirmed', False):
            logout(request)
            request.session.flush()
            messages.success(request, "You have been logged out.")
            return redirect('home')  # Redirect to login page after logout
        else:
            # Set a flag in the session to indicate the confirmation step
            request.session['logout_confirmed'] = True
            return render(request, 'articles/logout.html')
    
    # Handle other methods if needed (e.g., GET)
    # For simplicity, assuming that only POST requests are used
    return redirect('home')

 # Render logout confirmation template

@login_required
def profile_view(request):
    return render(request, 'articles/profile.html')

# Protected view
class ProtectedView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request):
        return render(request, 'articles/protected.html')
