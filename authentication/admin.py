from django.contrib import admin

from authentication.models import *

# Register your models here.
admin.site.register(UserManage)
admin.site.register(Admin)
admin.site.register(Pengguna)
admin.site.register(OTPtoUser)