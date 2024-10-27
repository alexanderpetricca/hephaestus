from django.urls import path, include

from accounts import views


urlpatterns = [
    # AllAuth Overrides
    path('password/change/', views.CustomPasswordChangeView.as_view(), name='account_change_password'),
    path('password/change-done/', views.PasswordChangeDoneView.as_view(), name='account_change_password_done'),
    
    # AllAuth
    path('', include('allauth.urls')),
]