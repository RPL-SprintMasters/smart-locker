from django.urls import path
from app_pengguna.views import *

app_name = 'app_pengguna'
urlpatterns = [
    path('dashboard/', dashboard_pengguna, name='dashboard_pengguna'),
    path('daftar-lokasi/', daftar_lokasi, name='daftar_lokasi'),
    path('daftar-loker/<int:grup_loker_id>/', daftar_loker, name='daftar_loker'),
    path('pinjam-loker/', pinjam_loker, name='pinjam_loker'),
    path('open-loker/<int:loker_id>/', open_loker, name='open_loker'),
    path('kembalikan_loker/', kembalikan_loker, name='kembalikan_loker'),
    path('close-loker/<int:transaksi_id>/', close_loker, name='close_loker'),
    path('view-notification/', view_notification, name='view_notification'),
    path('hubungi-admin/', hubungi_admin, name='hubungi_admin'),
    path('topup/', topup, name='topup'),
    path('detail/<str:order_id>/', detail_transaction_topup, name='detail_transaction_topup'),
]