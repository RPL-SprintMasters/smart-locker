from django.db import models
from authentication.models import UserManage, Pengguna, Admin

class GrupLoker(models.Model):
    nama_loker = models.CharField(max_length=15)
    alamat_loker = models.CharField(max_length=15)
    harga_loker = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class Loker(models.Model):
    grup_loker = models.ForeignKey(GrupLoker, on_delete=models.CASCADE)
    nomor_loker = models.IntegerField(default=0)
    status_loker = models.BooleanField(default=False)

class TransaksiPeminjaman(models.Model):
    pengguna = models.ForeignKey(Pengguna, on_delete=models.CASCADE)
    loker = models.ForeignKey(Loker, on_delete=models.CASCADE)
    mulaipinjam = models.DateField(auto_now=True)
    akhirpinjam = models.DateField(auto_now=True)
    total_harga = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=15)

class TopupHistory(models.Model):
    pengguna = models.ForeignKey(Pengguna, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=15)
    tanggal = models.DateField(auto_now=True)
    nominal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    metode_pembayaran = models.CharField(max_length=15)

class Notifikasi(models.Model):
    pengguna = models.ManyToManyField(Pengguna)
    pembuat = models.ForeignKey(Admin, on_delete=models.CASCADE)
    waktu = models.DateField(auto_now=True)
    judul = models.CharField(max_length=15)
    pesan = models.TextField()

class LokerAction(models.Model):
    uuid_code = models.CharField(max_length=36)
    pengguna = models.ForeignKey(Pengguna, on_delete=models.SET_NULL, null=True)
    loker = models.ForeignKey(Loker, on_delete=models.CASCADE)
    command = models.CharField(max_length=10)
    img_name = models.CharField(max_length=36, default='')