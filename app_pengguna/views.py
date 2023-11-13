import datetime
import time
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from app_pengguna.models import *
import qrcode
from io import BytesIO
import uuid
from django.utils import timezone

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

make_dir('media')
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
    if (not existing_transaksi_peminjaman):
        uuid_open_loker = str(uuid.uuid4())
        if (not existing_transaksi_peminjaman):
            TransaksiPeminjaman.objects.create(uuid_code=uuid_open_loker, pengguna=pengguna_obj, loker=loker, mulaipinjam=timezone.now(), total_harga=0.0, status="ONGOING")

        img = qrcode.make(f"O_{uuid_open_loker}")
        img_name = f"O_{uuid_open_loker}.png"
        img.save(settings.MEDIA_ROOT + '\\' + img_name)

        context['loker'] = loker
        context['img_name'] = img_name
    else:
        transaksi_peminjaman = existing_transaksi_peminjaman[0]
        context['loker'] = transaksi_peminjaman.loker
        context['img_name'] = f"O_{transaksi_peminjaman.uuid_code}.png"

    if 'from_pinjam_loker' in request.session:
        del request.session['from_pinjam_loker']
    return render(request, 'open_loker.html', context=context)

@login_required
def kembalikan_loker(request):
    context = dict()
    username = request.user.username
    context['username'] = username
    
    pengguna_obj = get_object_or_404(Pengguna, user=request.user)
    transaksi_peminjaman = TransaksiPeminjaman.objects.filter(pengguna=pengguna_obj, total_harga=0.0, status="ONGOING")
    loker_list = [transaksi.loker for transaksi in transaksi_peminjaman]
    context['loker_list'] = loker_list

    return render(request, 'kembalikan_loker.html', context=context)

@login_required
def close_loker(request, loker_id):
    context = dict()
    username = request.user.username
    context['username'] = username

    pengguna_obj = get_object_or_404(Pengguna, user=request.user)
    loker = get_object_or_404(Loker, id=loker_id)

    loker.status_loker = False
    loker.save()
    existing_transaksi_peminjaman_ongoing = TransaksiPeminjaman.objects.filter(pengguna=pengguna_obj, loker=loker, total_harga=0.0, status="ONGOING")
    existing_transaksi_peminjaman_finished = TransaksiPeminjaman.objects.filter(pengguna=pengguna_obj, loker=loker, status="FINISHED")
    if (existing_transaksi_peminjaman_ongoing):
        transaksi_peminjaman = existing_transaksi_peminjaman_ongoing[0]

        transaksi_peminjaman.akhirpinjam = timezone.now()
        transaksi_peminjaman.status = "FINISHED"
        print(transaksi_peminjaman.akhirpinjam)
        print(transaksi_peminjaman.mulaipinjam)
        selisih_waktu = transaksi_peminjaman.akhirpinjam - transaksi_peminjaman.mulaipinjam
        selisih_15min = math.ceil(selisih_waktu.total_seconds() / 900)
        transaksi_peminjaman.total_harga = transaksi_peminjaman.loker.grup_loker.harga_loker * selisih_15min
        transaksi_peminjaman.save()

        if str(username).endswith("@ui.ac.id"):
            today = datetime.date.today()
            transaksi_peminjaman_hari_ini = TransaksiPeminjaman.objects.filter(
                pengguna=pengguna_obj,
                loker=loker,
                status="FINISHED",
                mulaipinjam__date=today,
                akhirpinjam__date=today
            ).order_by('mulaipinjam')
            new_saldo = sum([transaksi.total_harga for transaksi in transaksi_peminjaman_hari_ini])
            curr_15m = 0
            for i, transaksi in enumerate(transaksi_peminjaman_hari_ini):
                curr_15m += (transaksi.total_harga//transaksi.loker.grup_loker.harga_loker)
                if (curr_15m >= 8):
                    lebih = curr_15m - 8
                    new_saldo -= transaksi.loker.grup_loker.harga_loker*lebih
                    break
                new_saldo -= transaksi.total_harga
            pengguna_obj.saldo = new_saldo
        else:
            pengguna_obj.saldo -= transaksi_peminjaman.total_harga
        pengguna_obj.save()

        img = qrcode.make(f"C_{transaksi_peminjaman.uuid_code}")
        img_name = f"C_{transaksi_peminjaman.uuid_code}.png"
        img.save(settings.MEDIA_ROOT + '\\' + img_name)

        context['loker'] = loker
        context['img_name'] = img_name
    elif (existing_transaksi_peminjaman_finished):
        transaksi_peminjaman = existing_transaksi_peminjaman_finished.order_by('-mulaipinjam')[0]
        context['loker'] = transaksi_peminjaman.loker
        context['img_name'] = f"C_{transaksi_peminjaman.uuid_code}.png"
    return render(request, 'close_loker.html', context=context)