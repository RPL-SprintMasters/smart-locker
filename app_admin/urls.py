from django.urls import path
from app_admin.views import *

app_name = 'app_admin'
urlpatterns = [
    path('dashboard/', dashboard_admin, name='dashboard_admin'),
    path('manage/', manage, name='manage'),
]