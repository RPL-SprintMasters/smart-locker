from django.utils import timezone
import datetime
import math
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from app_pengguna.models import *
import uuid

def logout_view(request):
    user = request.user
    if user.is_admin:
        admin_obj = Admin.objects.filter(user=user)[0]
        admin_obj.is_online = False
        admin_obj.save()
    logout(request)
    return redirect('authentication:home')

@csrf_exempt
def api_get_all_transaksi(request):
    resp = {}
    all_transaksi = TransaksiPeminjaman.objects.all()
    for transaksi in all_transaksi:
        dictio = {}
        dictio['mulaipinjam'] = transaksi.mulaipinjam
        resp[f'{transaksi.uuid_code}'] = dictio
    return JsonResponse(resp, status = 200)

@csrf_exempt
def api_post_transaksi(request):
    resp = {}
    if request.method == 'POST':
        data = json.loads(request.body)
        uuid_code = data['uuid_code']
        durasi = data['durasi']
        transaksi = TransaksiPeminjaman.objects.filter(uuid_code=uuid_code)[0]

        notifikasi = Notifikasi.objects.create(
            judul=f"Jangan Lupa Mengembalikan loker {transaksi.loker.nomor_loker} pada {transaksi.loker.grup_loker.alamat_loker}",
            pesan=f"Anda telah menggunakan loker selama {durasi} menit, jangan lupa untuk menyelesaikan peminjaman"
        )
        notifikasi.pengguna.add(transaksi.pengguna)
        notifikasi.save()

        resp['success'] = True
        resp['message'] = "Sukses mengirimkan notif"
    return JsonResponse(resp, status = 200)

@csrf_exempt
def api_from_machine(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code_raw = data['code_loker']
        command = str(code_raw).split("_")[0]
        try:
            uuid_code = uuid.UUID(str(code_raw).split("_")[-1])
            transaksi = TransaksiPeminjaman.objects.filter(uuid_code=uuid_code)[0]
        except:
            resp = {
                'success':False,
                'message':f'Tidak ditemukan transaksi dengan ID {str(code_raw).split("_")[1]}',
            }
            return JsonResponse(resp, status = 400)
        if command == 'O':
            if (not transaksi.is_scanned_open):
                transaksi.is_scanned_open = True
                transaksi.mulaipinjam = timezone.now()
                transaksi.save()
                resp = {
                    'success':True,
                    'message':f'Sukses memulai peminjaman pada loker nomor {transaksi.loker.nomor_loker}',
                    'no_loker':transaksi.loker.nomor_loker
                }
                return JsonResponse(resp, status = 200)
            else:
                resp = {
                    'success':False,
                    'message':f'Sudah pernah di scan transaksi peminjaman dengan ID {uuid_code}',
                    'no_loker':transaksi.loker.nomor_loker
                }
                return JsonResponse(resp, status = 400)
        elif command == 'C':
            if (not transaksi.is_scanned_close):
                transaksi.is_scanned_close = True
                transaksi.akhirpinjam = timezone.now()
                transaksi.status = "FINISHED"
                selisih_waktu = transaksi.akhirpinjam - transaksi.mulaipinjam
                selisih_15min = math.ceil(selisih_waktu.total_seconds() / 900)
                transaksi.total_harga = transaksi.loker.grup_loker.harga_loker * selisih_15min

                pengguna_obj = get_object_or_404(Pengguna, user=transaksi.pengguna.user) # mendapatkan object pengguna
                loker = get_object_or_404(Loker, id=transaksi.loker.id)   # user.getLokerFromId(loker_id)

                if str(transaksi.pengguna.user.username).endswith("@ui.ac.id"):
                    today = datetime.date.today()
                    if (pengguna_obj.current_free != today):
                        pengguna_obj.free_peminjaman = 8
                        pengguna_obj.current_free = today
                    if (pengguna_obj.current_free==today):
                        gap = pengguna_obj.free_peminjaman - selisih_15min
                        real_gap = 0
                        if (gap < 0 and pengguna_obj.free_peminjaman >= 0):
                            real_gap = abs(gap)
                        elif (gap < 0 and pengguna_obj.free_peminjaman < 0):
                            real_gap = abs(selisih_15min)
                        if ((pengguna_obj.saldo - (transaksi.loker.grup_loker.harga_loker * real_gap)) < 0):
                            resp = {
                                'success':False,
                                'message':f'Saldo anda tidak mencukupi silakan kembali ke dashboard untuk topup',
                                'no_loker':None
                            }
                            return JsonResponse(resp, status = 400)
                        pengguna_obj.saldo -= transaksi.loker.grup_loker.harga_loker * (real_gap) # pengguna_obj.reduceBalance(transaksi.getLoker().getGrupLoker().getHargaLoker()*real_gap)
                else:
                    if ((pengguna_obj.saldo - transaksi.total_harga) < 0):
                        resp = {
                            'success':False,
                            'message':f'Saldo anda tidak mencukupi silakan kembali ke dashboard untuk topup',
                            'no_loker':None
                        }
                        return JsonResponse(resp, status = 400)
                    pengguna_obj.saldo -= transaksi.total_harga # pengguna_obj.reduceBalance(transaksi_peminjaman.getTotalHarga())
                pengguna_obj.save()
                transaksi.save()
                resp = {
                    'success':True,
                    'message':f'Sukses menyelesaikan peminjaman pada loker nomor {transaksi.loker.nomor_loker}',
                    'no_loker':transaksi.loker.nomor_loker
                }
                return JsonResponse(resp, status = 200)
            else:
                resp = {
                    'success':False,
                    'message':f'Sudah pernah di scan transaksi pengembalian dengan ID {uuid_code}',
                    'no_loker':transaksi.loker.nomor_loker
                }
                return JsonResponse(resp, status = 400)

    else:
        return JsonResponse({"status": "error"}, status = 401)