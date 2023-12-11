import uuid
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from authentication.models import UserManage, Admin, OTPtoUser, Pengguna
from app_pengguna.models import GrupLoker, Loker, TransaksiPeminjaman, TopupHistory, Notifikasi

@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class AuthenticationViewsTestCase(TestCase):
    def setUp(self):
        # Create necessary objects for testing
        self.admin_user = UserManage.objects.create_superuser(username='admin2357346', email='admin@gmail.com', password='admin')
        self.dummy_admin_user = UserManage.objects.create_superuser(username='dummy_admin2357346', email='admin1@gmail.com', password='dummy_admin', telephone_number='1234567890', is_admin=True, is_pengguna=False)
        self.dummy_pengguna_user = UserManage.objects.create_user(username='dummy_pengguna2357346', password='dummy_pengguna', telephone_number='1234567890', is_admin=False, is_pengguna=True)
        self.dummy_admin2_user = UserManage.objects.create_superuser(username='dummy_admin22357346', email='admin2@gmail.com', password='dummy_admin2', telephone_number='1234567890', is_admin=True, is_pengguna=False)
        self.dummy_pengguna2_user = UserManage.objects.create_user(username='dummy_pengguna22357346', password='dummy_pengguna2', telephone_number='1234567890', is_admin=False, is_pengguna=True)
        self.dummy_admin3_user = UserManage.objects.create_superuser(username='dummy_admin3_22357346', email='admin2@gmail.com', password='dummy_admin2', telephone_number='1234567890', is_admin=True, is_pengguna=False)
        self.dummy_pengguna3_user = UserManage.objects.create_user(username='dummy_pengguna3_22357346', password='dummy_pengguna2', telephone_number='1234567890', is_admin=False, is_pengguna=True)
        
        self.dummy_admin = Admin.objects.create(user=self.dummy_admin_user)
        self.dummy_admin2 = Admin.objects.create(user=self.dummy_admin2_user)
        self.dummy_admin3 = Admin.objects.create(user=self.dummy_admin3_user)

        self.dummy_pengguna = Pengguna.objects.create(user=self.dummy_pengguna_user, saldo=100.00)
        self.dummy_pengguna2 = Pengguna.objects.create(user=self.dummy_pengguna2_user, saldo=75.00)
        self.dummy_pengguna3 = Pengguna.objects.create(user=self.dummy_pengguna3_user, saldo=75.00)

        self.dummy_otp = OTPtoUser.objects.create(kode_otp='123456', user=self.dummy_pengguna_user, is_verified=True)
        self.dummy_otp2 = OTPtoUser.objects.create(kode_otp='4256gd', user=self.dummy_pengguna2_user, is_verified=True)
        self.dummy_otp3 = OTPtoUser.objects.create(kode_otp='123456', user=self.dummy_pengguna3_user, is_verified=False)

        self.grup_loker = GrupLoker.objects.create(nama_loker='Loker Group 1', alamat_loker='Jl. Contoh No. 123', harga_loker=50.00)
        self.loker = Loker.objects.create(grup_loker=self.grup_loker, nomor_loker=1, status_loker=False)
        self.transaksi = TransaksiPeminjaman.objects.create(uuid_code=uuid.uuid4(), pengguna=self.dummy_pengguna, loker=self.loker, total_harga=50.00, status='FINISHED')

        self.topup_history = TopupHistory.objects.create(pengguna=self.dummy_pengguna, status='Sukses', nominal=50.00, metode_pembayaran='Transfer Bank')
        self.notifikasi = Notifikasi.objects.create(pembuat=self.dummy_admin, judul='Pemberitahuan', pesan='Ini adalah pesan pemberitahuan.')
        self.notifikasi.pengguna.add(self.dummy_pengguna)

        # Set up the client for making HTTP requests
        self.client = Client()

    def test_home_view(self):
        response = self.client.get(reverse('authentication:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_login_view(self):
        response = self.client.get(reverse('authentication:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_verify_otp_view(self):
        self.client.login(username='dummy_pengguna3_22357346', password='dummy_pengguna2')
        response = self.client.get(reverse('authentication:verify_otp'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'verify_otp.html')

    def test_dashboard_pengguna(self):
        self.client.login(username='dummy_pengguna2357346', password='dummy_pengguna')
        response = self.client.get(reverse('app_pengguna:dashboard_pengguna'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_pengguna.html')

    def test_dashboard_admin(self):
        self.client.login(username='dummy_admin2357346', password='dummy_admin')
        response = self.client.get(reverse('app_admin:dashboard_admin'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_admin.html')

    def test_register_admin_view(self):
        response = self.client.get(reverse('authentication:register_admin'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_admin.html')

    def test_register_user_view(self):
        response = self.client.get(reverse('authentication:register_user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_user.html')
