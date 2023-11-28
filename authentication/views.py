import math
import random
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
import uuid
from django.shortcuts import render, redirect
from authentication.models import Admin, OTPtoUser, Pengguna, UserManage
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.core.mail import send_mail 
from utility.util import *

#################### CREATE DUMMY OBJECT ####################
from authentication.models import UserManage, Admin, Pengguna, OTPtoUser
from app_pengguna.models import GrupLoker, Loker, TransaksiPeminjaman, TopupHistory, Notifikasi
try:
    UserManage.objects.create_superuser(username="admin", email="admin@gmail.com", password="admin")
except:
    pass
try:
    user = UserManage.objects.create_user(username="dummy_admin", password="dummy_admin", telephone_number="1234567890", is_admin=True, is_pengguna=False)
    admin = Admin.objects.create(user=user)
    user = UserManage.objects.create_user(username="dummy_pengguna", password="dummy_pengguna", telephone_number="1234567890", is_admin=False, is_pengguna=True)    
    pengguna = Pengguna.objects.create(user=user, saldo=100.00)
    otp = OTPtoUser.objects.create(kode_otp="123456", user=user, is_verified=True)

    grup_loker = GrupLoker.objects.create(nama_loker="Loker Group 1", alamat_loker="Jl. Contoh No. 123", harga_loker=50.00)
    loker = Loker.objects.create(grup_loker=grup_loker, nomor_loker=1, status_loker=False)
    transaksi = TransaksiPeminjaman.objects.create(pengguna=pengguna, loker=loker, total_harga=50.00, status="FINISHED")

    topup = TopupHistory.objects.create(pengguna=pengguna, status="Sukses", nominal=50.00, metode_pembayaran="Transfer Bank")
    admin_user = Admin.objects.get(user=user)
    notifikasi = Notifikasi.objects.create(pembuat=admin_user, judul="Pemberitahuan", pesan="Ini adalah pesan pemberitahuan.")
    notifikasi.pengguna.add(pengguna)
except:
    pass
try:
    user = UserManage.objects.create_user(username="dummy_admin2", password="dummy_admin2", telephone_number="1234567890", is_admin=True, is_pengguna=False)
    admin = Admin.objects.create(user=user)
    user = UserManage.objects.create_user(username="dummy_pengguna2", password="dummy_pengguna2", telephone_number="1234567890", is_admin=False, is_pengguna=True)    
    pengguna = Pengguna.objects.create(user=user, saldo=75.00)
    otp = OTPtoUser.objects.create(kode_otp="4256gd", user=user, is_verified=True)

    grup_loker = GrupLoker.objects.create(nama_loker="Loker Group 2", alamat_loker="Jl. Contoh No. 123", harga_loker=50.00)
    loker = Loker.objects.create(grup_loker=grup_loker, nomor_loker=1, status_loker=False)
    transaksi = TransaksiPeminjaman.objects.create(pengguna=pengguna, loker=loker, total_harga=50.00, status="FINISHED")
    loker = Loker.objects.create(grup_loker=grup_loker, nomor_loker=2, status_loker=False)
    transaksi = TransaksiPeminjaman.objects.create(pengguna=pengguna, loker=loker, total_harga=6.00, status="ONGOING")
    
    topup = TopupHistory.objects.create(pengguna=pengguna, status="Sukses", nominal=50.00, metode_pembayaran="OVO")
    admin_user = Admin.objects.get(user=user)
    notifikasi = Notifikasi.objects.create(pembuat=admin_user, judul="Pemberitahuan", pesan="Ini adalah pesan pemberitahuan.")
    notifikasi.pengguna.add(pengguna)
except:
    pass
##############################################################

def home(request):
    return render(request, 'home.html')

def login(request):
    context = dict()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            if user.is_admin:
                return redirect('app_admin:dashboard_admin')
            else:
                try:
                    otp_obj = OTPtoUser.objects.get(user=user)
                    if not otp_obj.is_verified:
                        return redirect('authentication:verify_otp')
                except OTPtoUser.DoesNotExist:
                    pass
                return redirect('app_pengguna:dashboard_pengguna')
        else:
            context['message'] = 'Invalid credentials'
            context['message_flag'] = 'danger'
            return render(request, 'login.html', context=context)

    return render(request, 'login.html', context=context)

def verify_otp(request):
    context = dict()
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        user = request.user

        try:
            otp_obj = OTPtoUser.objects.get(user=user)
            if otp_obj.is_verified:
                if user.is_pengguna:
                    return redirect('app_pengguna:dashboard_pengguna')
                else:
                    return redirect('app_admin:dashboard_admin')

            if otp_entered == otp_obj.kode_otp:
                otp_obj.is_verified = True
                otp_obj.save()
                # messages.success(request, 'OTP verification successful!')
                context["message"] = 'OTP verification successful!'
                context["message_flag"] = 'success'
                if user.is_pengguna:
                    return redirect('app_pengguna:dashboard_pengguna')
                else:
                    return redirect('app_admin:dashboard_admin')
            else:
                # messages.error(request, 'Invalid OTP. Please try again.')
                context["message"] = 'Invalid OTP. Please try again.'
                context["message_flag"] = 'danger'
        except OTPtoUser.DoesNotExist:
            pass

    return render(request, 'verify_otp.html', context=context)

def dashboard(request):
    return render(request, 'dashboard.html')

def register(request):
    return render(request, 'register.html')

def register_admin(request):
    context = dict()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        telephone = request.POST['telephone']

        try:
            user = UserManage.objects.create_user(username=username, password=password)
        except:
            context["message"] = 'Email sudah digunakan'
            context["message_flag"] = 'danger'
            return render(request, 'register_admin.html', context=context)
        user.telephone_number = telephone
        user.is_admin = True
        user.save()

        otp_code = generateOTP()
        send_mail(
            "Konfirmasi Akun Smart Locker",
            f'Berikut merupakan kode OTP kamu, kamu dapat melakukan konfirmasi dengan memasukan code tersebut pada aplikasi\n\n{otp_code}',
            "rudolfalbertus9182@gmail.com",
            [str(username).strip()],
            fail_silently=False,
        )

        otp_obj = OTPtoUser.objects.create(kode_otp=otp_code, user=user)
        otp_obj.save()

        admin = Admin.objects.create(user=user)
        admin.save()

        # messages.success(request, 'Registration successful!')
        auth_login(request, user)
        return redirect('authentication:verify_otp')
    return render(request, 'register_admin.html', context=context)

def register_user(request):
    context = dict()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        telephone = request.POST['telephone']

        try:
            user = UserManage.objects.create_user(username=username, password=password)
        except:
            context["message"] = 'Email sudah digunakan'
            context["message_flag"] = 'danger'
            return render(request, 'register_user.html', context=context)
        user.telephone_number = telephone
        user.is_pengguna = True
        user.save()

        otp_code = generateOTP()
        send_mail(
            "Konfirmasi Akun Smart Locker",
            f'Berikut merupakan kode OTP kamu, kamu dapat melakukan konfirmasi dengan memasukan code tersebut pada aplikasi\n\n{otp_code}',
            "rudolfalbertus9182@gmail.com",
            [str(username).strip()],
            fail_silently=False,
        )

        otp_obj = OTPtoUser.objects.create(kode_otp=otp_code, user=user)
        otp_obj.save()

        pengguna = Pengguna.objects.create(user=user)
        pengguna.save()

        # messages.success(request, 'Registration successful!')
        context['username'] = username
        context["message"] = 'Registration successful!'
        auth_login(request, user)
        return redirect('authentication:verify_otp')
    return render(request, 'register_user.html', context=context)