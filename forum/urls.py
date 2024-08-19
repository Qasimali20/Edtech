from django.urls import path
from . import views

urlpatterns = [
    path('thread', views.thread_list, name='thread_list'),
    path('thread/<int:thread_id>/', views.thread_detail, name='thread_detail'),
    path('thread/create/', views.create_thread, name='create_thread'),
    path('post/<int:post_id>/comment/', views.post_comment, name='post_comment'),
]
