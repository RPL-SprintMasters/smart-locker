from django.contrib import admin

from app_pengguna.models import *

# Register your models here.
admin.site.register(GrupLoker)
admin.site.register(Loker)
admin.site.register(TransaksiPeminjaman)
admin.site.register(TopupHistory)
admin.site.register(Notifikasi)
admin.site.register(Feedback)