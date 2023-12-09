import cv2
from pyzbar.pyzbar import decode
import requests
from pprint import pprint

count = 0
def detect_and_print_qr_codes(frame):
    global count
    decoded_objects = decode(frame)
    for obj in decoded_objects:
        data = obj.data.decode('utf-8')
        count += 1
        print(f"{count}.QR Code Terdeteksi: {data}")
        resp = requests.post('https://sprintmasters.up.railway.app/api/from-machine/', json={
            "code_loker": data
        })
        pprint(resp.json())
        raise Exception("Donee!!")

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Kamera tidak dapat diakses")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Gagal membaca frame")
            break
        detect_and_print_qr_codes(frame)
        cv2.imshow('Kamera QR', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
