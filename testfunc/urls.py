from django.urls import path
from . import views

urlpatterns = [    
    path('tests/', views.list_tests, name='list_tests'),
    path('tests/<int:test_id>/', views.test_details, name='test_details'),
    path('tests/<int:test_id>/submit/', views.submit_answers, name='submit_answers'),
    path('tests/<int:test_id>/results/', views.user_test_results, name='user_test_results'),
    path('performance/', views.user_performance, name='user_performance'),
]