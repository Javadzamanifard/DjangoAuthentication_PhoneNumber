from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.login_signup_view, name='login_or_signup'),
    path('verify/', views.verify, name='verify'),
    path('resend-code/', views.resend_otp, name='resend_otp'),
]