from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('login.urls')),
    path('',include('testfunc.urls')),
    path('',include('forum.urls')),
    path('',include('chatbot.urls')),
]
