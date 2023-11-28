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
    logout(request)
    return redirect('authentication:home')

@csrf_exempt
def api_from_machine(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code_raw = data['code_loker']
        command = str(code_raw).split("_")[0]
        uuid_code = uuid.UUID(str(code_raw).split("_")[-1])
        transaksi = TransaksiPeminjaman.objects.filter(uuid_code=uuid_code)[0]
        if command == 'O':
            resp = {
                'success':True,
                'message':f'Sukses memulai peminjaman pada loker nomor {transaksi.loker.nomor_loker}',
            }
            transaksi.is_scanned_open = True
            transaksi.mulaipinjam = timezone.now()
            transaksi.save()
            return JsonResponse(resp, status = 200)
        elif command == 'C':
            resp = {
                'success':True,
                'message':f'Sukses menyelesaikan peminjaman pada loker nomor {transaksi.loker.nomor_loker}',
            }
            transaksi.is_scanned_close = True
            transaksi.akhirpinjam = timezone.now()
            transaksi.status = "FINISHED"
            selisih_waktu = transaksi.akhirpinjam - transaksi.mulaipinjam
            selisih_15min = math.ceil(selisih_waktu.total_seconds() / 900)
            transaksi.total_harga = transaksi.loker.grup_loker.harga_loker * selisih_15min
            transaksi.save()

            pengguna_obj = get_object_or_404(Pengguna, user=transaksi.pengguna.user) # mendapatkan object pengguna
            loker = get_object_or_404(Loker, id=transaksi.loker.id)   # user.getLokerFromId(loker_id)

            if str(transaksi.pengguna.user.username).endswith("@ui.ac.id"):
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
                pengguna_obj.saldo = new_saldo # pengguna_obj.setSaldo(new_saldo)
            else:
                pengguna_obj.saldo -= transaksi.total_harga # pengguna_obj.reduceBalance(transaksi_peminjaman.getTotalHarga())
            pengguna_obj.save()

            return JsonResponse(resp, status = 200)
    else:
        return JsonResponse({"status": "error"}, status = 401)