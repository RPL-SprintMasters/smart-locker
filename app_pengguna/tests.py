from django.test import TestCase, Client, override_settings
from django.urls import reverse
from .models import *

@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class AppPenggunaViewsTestCase(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = UserManage.objects.create_user(username='testuser', password='testpassword')
        self.admin_user = UserManage.objects.create_user(username='adminuser', password='adminpassword')
        self.admin = Admin.objects.create(user=self.admin_user, is_online=True)

        # Create other necessary objects for testing
        self.grup_loker = GrupLoker.objects.create(nama_loker='Test Group', alamat_loker='Test Address', harga_loker=10.0)
        self.loker = Loker.objects.create(grup_loker=self.grup_loker, nomor_loker=1, status_loker=False)
        self.pengguna = Pengguna.objects.create(user=self.user, saldo=50.0, free_peminjaman=5)
        self.transaksi_peminjaman = TransaksiPeminjaman.objects.create(uuid_code=str(uuid.uuid4()), pengguna=self.pengguna, loker=self.loker, total_harga=0.0, status="ONGOING", is_scanned_open=False, is_scanned_close=False)
        self.topup_history = TopupHistory.objects.create(pengguna=self.pengguna, order_id=uuid.uuid4(), status='Pending', nominal=20.0, metode_pembayaran='Bank', img_payment='img_url', directlink_url='direct_link')
        self.notifikasi = Notifikasi.objects.create(pembuat=self.admin, judul='Test Notification', pesan='This is a test notification')
        self.feedback = Feedback.objects.create(transaksi=self.transaksi_peminjaman, rating=4, message='Test feedback message')

        # Set up the client for making HTTP requests
        self.client = Client()

    def test_dashboard_pengguna(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('app_pengguna:dashboard_pengguna'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['username'], 'testuser')
        self.assertTemplateUsed(response, 'dashboard_pengguna.html')

    def test_daftar_lokasi(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('app_pengguna:daftar_lokasi'))
        self.assertEqual(response.status_code, 200)
        # Add more assertions specific to daftar_lokasi view...

    def test_daftar_loker(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('app_pengguna:daftar_loker', args=[self.grup_loker.id]))
        self.assertEqual(response.status_code, 200)
        # Add more assertions specific to daftar_loker view...

    def test_pinjam_loker(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('app_pengguna:pinjam_loker'))
        self.assertEqual(response.status_code, 302)  # Redirect to daftar_lokasi

    def test_open_loker(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('app_pengguna:open_loker', args=[self.loker.id]))
        self.assertEqual(response.status_code, 200)
        # Add more assertions specific to open_loker view...

    def test_kembalikan_loker(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('app_pengguna:kembalikan_loker'))
        self.assertEqual(response.status_code, 200)
        # Add more assertions specific to kembalikan_loker view...

    def test_close_loker(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('app_pengguna:close_loker', args=[self.transaksi_peminjaman.id]))
        self.assertEqual(response.status_code, 200)
        # Add more assertions specific to close_loker view...

    def test_view_notification(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('app_pengguna:view_notification'))
        self.assertEqual(response.status_code, 200)
        # Add more assertions specific to view_notification view...

    def test_hubungi_admin(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('app_pengguna:hubungi_admin'))
        self.assertEqual(response.status_code, 302)  # Redirect to WhatsApp link

    def test_feedback(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('app_pengguna:feedback', args=[self.transaksi_peminjaman.id]))
        self.assertEqual(response.status_code, 200)
        # Add more assertions specific to feedback view...

    def test_history_transaksi(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('app_pengguna:history_transaksi'))
        self.assertEqual(response.status_code, 200)
        # Add more assertions specific to history_transaksi view...

    def test_topup(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('app_pengguna:topup'))
        self.assertEqual(response.status_code, 200)
        # Add more assertions specific to topup view...

    def test_history_topup(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('app_pengguna:history_topup'))
        self.assertEqual(response.status_code, 200)
        # Add more assertions specific to history_topup view...

    def test_detail_transaction_topup(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('app_pengguna:detail_transaction_topup', args=[str(self.topup_history.order_id)]))
        self.assertEqual(response.status_code, 200)
        # Add more assertions specific to detail_transaction_topup view...

