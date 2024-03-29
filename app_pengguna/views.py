import datetime
import time
import json
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from app_pengguna.models import *
import qrcode
from io import BytesIO
import uuid
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import os
from project_django import settings
from utility.util import *
import midtransclient
from django.http import HttpResponse, HttpResponseNotFound
from django.core import serializers
from project_django.settings import PAYMENT_CLIENT_KEY, PAYMENT_SERVER_KEY
import base64
from django.http import JsonResponse

@login_required
def dashboard_pengguna(request):
    context = dict()
    username = request.user.username
    context['username'] = username
    User = UserManage.objects.get(username = username)
    if 'from_pinjam_loker' in request.session:
        del request.session['from_pinjam_loker']
    pengguna = Pengguna.objects.get(user=User)
    context['saldo_user'] = pengguna.saldo
    context['pinjaman_aktif'] = TransaksiPeminjaman.objects.filter(pengguna = pengguna, status="ONGOING")
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
    
    grup_loker = get_object_or_404(GrupLoker, id=grup_loker_id)
    if 'from_pinjam_loker' in request.session:
        loker_list = Loker.objects.filter(grup_loker__id=grup_loker_id, status_loker=False)
    else:
        loker_list = Loker.objects.filter(grup_loker__id=grup_loker_id)
    context['grup_loker'] = grup_loker
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

    check_is_ever_scanned = TransaksiPeminjaman.objects.filter(pengguna=pengguna_obj, loker=loker, total_harga=0.0, status="ONGOING", is_scanned_open=True)
    if (check_is_ever_scanned):
        context['loker'] = loker
        context["message"] = 'Anda telah sukses meminjam loker'
        context["message_flag"] = 'success'
        return render(request, 'open_loker.html', context=context)

    loker.status_loker = True # true is used
    loker.save()
    existing_transaksi_peminjaman = TransaksiPeminjaman.objects.filter(pengguna=pengguna_obj, loker=loker, total_harga=0.0, status="ONGOING")
    if (not existing_transaksi_peminjaman):
        uuid_open_loker = str(uuid.uuid4())
        transaksi_peminjaman = TransaksiPeminjaman.objects.create(uuid_code=uuid_open_loker, pengguna=pengguna_obj, loker=loker, mulaipinjam=timezone.now(), total_harga=0.0, status="ONGOING")

        img = qrcode.make(f"O_{uuid_open_loker}")
        img_byte_array = BytesIO()
        img.save(img_byte_array)
        img_byte_array = img_byte_array.getvalue()
        img_base64 = base64.b64encode(img_byte_array).decode('utf-8')

        context['loker'] = loker
        context['img_base64'] = img_base64
    else:
        transaksi_peminjaman = existing_transaksi_peminjaman[0]
        context['loker'] = transaksi_peminjaman.loker

        img = qrcode.make(f"O_{transaksi_peminjaman.uuid_code}")
        img_byte_array = BytesIO()
        img.save(img_byte_array)
        img_byte_array = img_byte_array.getvalue()
        img_base64 = base64.b64encode(img_byte_array).decode('utf-8')

        context['img_base64'] = img_base64
    print(transaksi_peminjaman.uuid_code)
    
    if 'from_pinjam_loker' in request.session:
        del request.session['from_pinjam_loker']
    return render(request, 'open_loker.html', context=context)

@login_required
def kembalikan_loker(request):
    context = dict()
    username = request.user.username
    context['username'] = username
    
    pengguna_obj = get_object_or_404(Pengguna, user=request.user)
    transaksi_peminjaman_all = TransaksiPeminjaman.objects.filter(pengguna=pengguna_obj, total_harga=0.0, status="ONGOING")
    context['transaksi_peminjaman_all'] = transaksi_peminjaman_all

    return render(request, 'kembalikan_loker.html', context=context)

@login_required
def close_loker(request, transaksi_id):
    context = dict()
    username = request.user.username
    context['username'] = username

    transaksi_peminjaman = get_object_or_404(TransaksiPeminjaman, id=transaksi_id)
    loker = transaksi_peminjaman.loker  # transaksi.getLoker()
    
    if (transaksi_peminjaman.status == "FINISHED") and (transaksi_peminjaman.is_scanned_close):
        context['transaksi'] = transaksi_peminjaman
        context["message"] = 'Anda telah sukses mengembalikan loker, silakan kembali ke Dashboard atau berikan penilaian'
        context["message_flag"] = 'success'
        return render(request, 'close_loker.html', context=context)

    loker.status_loker = False # false is not used
    loker.save()

    img = qrcode.make(f"C_{transaksi_peminjaman.uuid_code}")
    img_byte_array = BytesIO()
    img.save(img_byte_array)
    img_byte_array = img_byte_array.getvalue()
    img_base64 = base64.b64encode(img_byte_array).decode('utf-8')

    context['transaksi'] = transaksi_peminjaman
    context['img_base64'] = img_base64

    return render(request, 'close_loker.html', context=context)

@login_required
def view_notification(request):
    context = dict()
    all_notification = Notifikasi.objects.filter(pengguna=Pengguna.objects.filter(user=request.user)[0]).order_by('-id')
    context['all_notification'] = all_notification
    return render(request, 'view_notification.html', context=context)

@login_required
def hubungi_admin(request):
    context = dict()
    all_available_admin = Admin.objects.filter(is_online=True)
    if (all_available_admin):
        available_admin = all_available_admin[0]
    else:
        available_admin = Admin.objects.all()[0]
    user_admin = available_admin.user
    whatsapp_link = f'https://api.whatsapp.com/send?phone={user_admin.telephone_number}&text=Halo admin saya {request.user.username} saya terdapat permasalah <KASUS>\n\nBerikut merupakan rinciannya:\n\n<RINCIAN-PERMASALAHAN>'
    return redirect(whatsapp_link)

@login_required
def feedback(request, transaksi_id):
    context = dict()
    if request.method == 'POST':
        transaksi = get_object_or_404(TransaksiPeminjaman, id=transaksi_id)

        rating = request.POST.get('rating')
        message_feedback = request.POST.get('message_feedback')

        feedback_instance = Feedback(transaksi=transaksi, rating=rating, message=message_feedback)
        feedback_instance.save()
        context['status'] = 'success'
        context['message'] = 'Your service form has been successfully submitted.'
        return render(request, 'feedback.html', context=context)
    try:
        Feedback.objects.filter(transaksi=get_object_or_404(TransaksiPeminjaman, id=transaksi_id))[0]
        context['status'] = 'success'
        context['message'] = 'Anda sudah pernah mengirimkan feeedback'
        return render(request, 'feedback.html', context=context)
    except:
        return render(request, 'feedback.html', context=context)

@login_required
def history_transaksi(request):
    context = dict()
    all_transaksi = TransaksiPeminjaman.objects.filter(pengguna=Pengguna.objects.filter(user=request.user)[0])
    rendered_transaksi = []
    for transaksi in all_transaksi:
        try:
            Feedback.objects.filter(transaksi=transaksi)[0]
            is_done_feedback = True
        except:
            is_done_feedback = False
        transaksi.mulaipinjam = transaksi.mulaipinjam + datetime.timedelta(hours=7)
        transaksi.akhirpinjam = transaksi.akhirpinjam + datetime.timedelta(hours=7)
        rendered_transaksi.append((transaksi, is_done_feedback))
    context['all_transaksi'] = rendered_transaksi
    return render(request, 'history_transaksi.html', context=context)
  
def topup(request):
    context = dict()

    if(request.method == "POST"):
        try:
            pengguna_obj = get_object_or_404(Pengguna, user=request.user)
            nominal = request.POST['nominal']
            paymentMethod = request.POST['paymentMethod']
            
        except:
            return redirect('app_pengguna:dashboard_pengguna')
        
        topupObj = TopupHistory.objects.create(pengguna=pengguna_obj, status='Pending', tanggal=datetime.datetime.now(),time=time.strftime("%H:%M", time.localtime()),  nominal=nominal, metode_pembayaran=paymentMethod)
        paymentMethod = paymentMethod.lower()

        try:            
            # Create Core API instance
            core_api = midtransclient.CoreApi(
                is_production=False,
                server_key=PAYMENT_SERVER_KEY,
                client_key=PAYMENT_CLIENT_KEY
            )
            # Build API parameter
            param = {
                "payment_type": paymentMethod,
                "transaction_details": {
                    "gross_amount": nominal,
                    "order_id": str(topupObj.order_id) ,
                },
                "gopay": {
                }
            }
            # charge transaction
            charge_response = core_api.charge(param)
            # charge_response = json.loads(str(charge_response))
            actions = charge_response["actions"]

            topupObj.img_payment = actions[0]["url"]
            topupObj.directlink_url = actions[1]["url"]
            topupObj.save()
            # redirect url
            return redirect('app_pengguna:detail_transaction_topup', order_id=str(topupObj.order_id))

        except:
            TopupHistory.delete(topupObj)
            return redirect('app_pengguna:dashboard_pengguna')

    return render(request, 'topup.html', context=context)

@login_required
def history_topup(request):
    context = dict()
    user = get_object_or_404(Pengguna, user=request.user)
    topupList = TopupHistory.objects.filter(pengguna = user)
    print(topupList)
    if(len(topupList) == 0):
        context['status'] = False
    else:
        context['status'] = True

    context['data'] = topupList
    return render(request, 'history_topup.html' , context=context)

@login_required
def detail_transaction_topup(request, order_id):
    context = dict()
    user = get_object_or_404(Pengguna, user=request.user)

    try:
        topupDetail = TopupHistory.objects.get(pengguna=user,order_id=uuid.UUID(order_id))
    except:
        return render(request, '404.html' , context=context)

    if topupDetail is not None:
        if str(topupDetail.status) == "Sukses":
            active = False
        else:
            active = True
            
        context = {
            "order_id": str(topupDetail.order_id)[:13],
            "status": str(topupDetail.status),
            "tanggal": topupDetail.tanggal.strftime("%d %B %Y"),
            "time": str(topupDetail.time)[0:5],
            "nominal": topupDetail.nominal,
            "metodePembayaran": topupDetail.metode_pembayaran,
            'active': active,
            "url":{
                "direct_link":topupDetail.directlink_url,
                "img_link":topupDetail.img_payment
            }
        }
        return render(request, 'detail_topup.html' , context=context)
    else:
        return render(request, '404.html' , context=context)
    
@csrf_exempt 
def receive_notification(request):
    if(request.method == "POST"):
        data = request.body
        data = data.decode('utf-8')
        data_dict = json.loads(data)

        order_id = data_dict['order_id']
        transaction_status = data_dict['transaction_status']
        fraud_status = data_dict['fraud_status']
        
        try:
            topup_obj = TopupHistory.objects.get(order_id = uuid.UUID(order_id))
            users_obj = topup_obj.pengguna
            if transaction_status == 'capture' or transaction_status == 'settlement':
                if fraud_status == 'challenge':
                    topup_obj.status =  fraud_status
                elif fraud_status == 'accept':
                    topup_obj.status = 'Sukses'
                users_obj.saldo = users_obj.saldo + topup_obj.nominal
                users_obj.save()
            elif transaction_status == 'cancel' or transaction_status == 'deny' or transaction_status == 'expire':
                topup_obj.status =  'Gagal'

            elif transaction_status == 'pending':
                topup_obj.status =  'Pending'

            topup_obj.save()
            return JsonResponse({
                'success':True,

            }, status = 200)
        except:
            return  JsonResponse({
                'success':True,
                'message': "Data tidak ditemukan"
            }, status = 200)
    return JsonResponse({
                'success':True,
                'message': "Data tidak ditemukan"
            }, status = 400)
