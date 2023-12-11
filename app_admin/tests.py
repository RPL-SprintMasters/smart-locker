from django.test import TestCase, Client, override_settings
from django.urls import reverse
from .models import *
from authentication.models import UserManage, Admin, Pengguna

@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class AppAdminViewsTestCase(TestCase):
    def setUp(self):
        self.admin_user = UserManage.objects.create_user(username='adminuser', password='adminpassword', is_admin=True)
        self.admin = Admin.objects.create(user=self.admin_user, is_online=True)

        self.client = Client()

    def test_dashboard_admin(self):
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('app_admin:dashboard_admin'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_admin.html')
        # Add more assertions specific to the dashboard_admin view...

    def test_dashboard_admin_not_logged_in(self):
        response = self.client.get(reverse('app_admin:dashboard_admin'))
        self.assertEqual(response.status_code, 302)  # Redirect to login page

    def test_manage(self):
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('app_admin:manage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manage.html')
        # Add more assertions specific to the manage view...

    def test_manage_not_logged_in(self):
        response = self.client.get(reverse('app_admin:manage'))
        self.assertEqual(response.status_code, 302)  # Redirect to login page

    def test_add_notification(self):
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('app_admin:add_notification'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_notification.html')
        # Add more assertions specific to the add_notification view...

    def test_add_notification_not_logged_in(self):
        response = self.client.get(reverse('app_admin:add_notification'))
        self.assertEqual(response.status_code, 302)  # Redirect to login page

    def test_add_notification_post(self):
        self.client.login(username='adminuser', password='adminpassword')
        data = {
            'title_notification': 'Test Notification',
            'message_notification': 'This is a test notification',
            'recipients': ['testuser']
        }
        response = self.client.post(reverse('app_admin:add_notification'), data)
        self.assertEqual(response.status_code, 200)  # Assuming a success status for simplicity
        # Add more assertions specific to the add_notification view after a POST request...
