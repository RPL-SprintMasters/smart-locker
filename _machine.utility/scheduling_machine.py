import requests
from pprint import pprint
from datetime import datetime, timezone
import time

DURASI = 15 # 15 menit
durasi_sec = DURASI * 60

stored_sended = dict()

while True:
    resp = requests.post('https://dev-sprintmasters.up.railway.app/api/get-all-transaksi/')
    data = resp.json()
    # pprint(data)

    for key, value in data.items():
        timestamp_str = value['mulaipinjam']
        timestamp_str = timestamp_str.rstrip('Z')
        datetime_obj = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%f')
        datetime_obj_utc = datetime_obj.replace(tzinfo=timezone.utc)

        value['mulaipinjam'] = datetime_obj_utc
        value['selisih'] = (datetime.now(timezone.utc)-datetime_obj_utc).total_seconds()

        if not (key in stored_sended):
            stored_sended[key] = 0 

    for key, value in data.items():
        diff_durasi = value['selisih']//durasi_sec
        if (stored_sended[key] < diff_durasi):
            stored_sended[key] = diff_durasi
            resp = requests.post('https://dev-sprintmasters.up.railway.app/api/post-transaksi/', json={
                "uuid_code": key,
                "durasi": f"{DURASI} menit"
            })
            pprint(resp.json())

    print(stored_sended)
    time.sleep(5)