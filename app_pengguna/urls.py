from django.urls import path
from app_pengguna.views import *

app_name = 'app_pengguna'
urlpatterns = [
    path('dashboard/', dashboard_pengguna, name='dashboard_pengguna'),
    path('daftar_lokasi/', daftar_lokasi, name='daftar_lokasi'),
    path('daftar_loker/<int:grup_loker_id>/', daftar_loker, name='daftar_loker'),
    path('pinjam_loker/', pinjam_loker, name='pinjam_loker'),
    path('open_loker/<int:loker_id>/', open_loker, name='open_loker'),
]