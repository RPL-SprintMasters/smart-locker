"""project_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include 
from django.contrib.auth.views import LogoutView 
from .views import *
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from app_pengguna.views import receive_notification

urlpatterns = [
    path('admin_django/', admin.site.urls),
    path('', include('authentication.urls')),
    path('admin/', include('app_admin.urls')),
    path('pengguna/', include('app_pengguna.urls')),
    path('logout/', logout_view, name='logout'),
    path('api/from-machine/', api_from_machine, name='api_from_machine'),
    path('api/get-all-transaksi/', api_get_all_transaksi, name='api_get_all_transaksi'),
    path('api/post-transaksi/', api_post_transaksi, name='api_post_transaksi'),
    path('api/notif-topup', receive_notification, name='receive_notification'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)