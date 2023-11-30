from django.db import models
from django.contrib.auth.models import AbstractUser

class UserManage(AbstractUser):
    username = models.CharField(max_length=12, unique=True)
    telephone_number = models.CharField(max_length=15, default="")
    is_admin = models.BooleanField(default=False)
    is_pengguna = models.BooleanField(default=False)

class Admin(models.Model):
    user = models.OneToOneField(UserManage, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)

class Pengguna(models.Model):
    user = models.OneToOneField(UserManage, on_delete=models.CASCADE)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class OTPtoUser(models.Model):
    kode_otp = models.CharField(max_length=15)
    user = models.OneToOneField(UserManage, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)