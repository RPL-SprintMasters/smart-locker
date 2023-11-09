from django.urls import path
from authentication.views import *

app_name = 'authentication'
urlpatterns = [
    path('', home, name='home'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('register_admin/', register_admin, name='register_technician'),
    path('register_user/', register_user, name='register_staff'),
    path('verify_otp/', verify_otp, name='verify_otp'),
]