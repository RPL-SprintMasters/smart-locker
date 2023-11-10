import datetime
import time
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from app_pengguna.models import *
import qrcode
from io import BytesIO
import uuid

from project_django import settings
from utility.util import *

@login_required
def dashboard_pengguna(request):
    context = dict()
    username = request.user.username
    context['username'] = username
    return render(request, 'dashboard_pengguna.html', context=context)

@login_required
def daftar_lokasi(request):
    context = dict()
    username = request.user.username
    context['username'] = username
    
    grup_loker_list = GrupLoker.objects.all().order_by('nama_loker')
    context['grup_loker_list'] = grup_loker_list

    if 'from_pinjam_loker' in request.session:
        context['judul'] = 'Pilih Lokasi untuk Peminjaman Loker'
        context['action_command'] = 'Pilih Loker'
    else:
        context['judul'] = 'Pilih Lokasi untuk melihat daftar Loker'
        context['action_command'] = 'View Loker'

    return render(request, 'daftar_lokasi.html', context=context)

@login_required
def daftar_loker(request, grup_loker_id):
    context = dict()
    username = request.user.username
    context['username'] = username
    
    if 'from_pinjam_loker' in request.session:
        loker_list = Loker.objects.filter(grup_loker__id=grup_loker_id, status_loker=False)
    else:
        loker_list = Loker.objects.filter(grup_loker__id=grup_loker_id)
    context['loker_list'] = loker_list

    if 'from_pinjam_loker' in request.session:
        context['judul'] = 'Pilih Loker untuk Dipinjam'
        context['from_pinjam_loker'] = True
    else:
        context['judul'] = 'Daftar Loker'
        context['from_pinjam_loker'] = False

    return render(request, 'daftar_loker.html', context=context)

@login_required
def pinjam_loker(request):
    context = dict()
    username = request.user.username
    context['username'] = username

    request.session['from_pinjam_loker'] = True
    return redirect('app_pengguna:daftar_lokasi')

@login_required
def open_loker(request, loker_id):
    context = dict()
    username = request.user.username
    context['username'] = username

    pengguna_obj = get_object_or_404(Pengguna, user=request.user)
    loker = get_object_or_404(Loker, id=loker_id)

    loker.status_loker = True
    loker.save()
    existing_transaksi_peminjaman = TransaksiPeminjaman.objects.filter(pengguna=pengguna_obj, loker=loker, total_harga=0.0, status="ONGOING")
    existing_loker_action = LokerAction.objects.filter(loker=loker, command="OPEN", pengguna=pengguna_obj)
    if (not existing_transaksi_peminjaman) or (not existing_loker_action):
        uuid_open_loker = str(uuid.uuid4())
        if (not existing_transaksi_peminjaman):
            TransaksiPeminjaman.objects.create(pengguna=pengguna_obj, loker=loker, mulaipinjam=datetime.datetime.now(), total_harga=0.0, status="ONGOING")

        img = qrcode.make(uuid_open_loker)
        img_name = 'qr' + str(time.time()) + '.png'
        make_dir('media')
        img.save(settings.MEDIA_ROOT + '\\' + img_name)
        LokerAction.objects.create(pengguna=pengguna_obj, uuid_code=uuid_open_loker, loker=loker, command="OPEN", img_name=img_name)

        context['loker'] = loker
        context['img_name'] = img_name
    else:
        loker_action = existing_loker_action[0]
        context['loker'] = loker_action.loker
        context['img_name'] = loker_action.img_name

    if 'from_pinjam_loker' in request.session:
        del request.session['from_pinjam_loker']
    return render(request, 'open_loker.html', context=context)