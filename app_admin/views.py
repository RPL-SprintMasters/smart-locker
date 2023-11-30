from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required

from authentication.models import *
from app_pengguna.models import *

@login_required
def dashboard_admin(request):
    context = dict()
    username = request.user.username
    context['username'] = username
    return render(request, 'dashboard_admin.html', context=context)

@login_required
def manage(request):
    context = dict()
    username = request.user.username
    context['username'] = username
    return render(request, 'manage.html', context=context)

@login_required
def add_notification(request):
    context = dict()
    if request.method == 'POST':
        title_notification = request.POST.get('title_notification')
        message_notification = request.POST.get('message_notification')
        recipients = request.POST.getlist('recipients')

        admin_pembuat = Admin.objects.get(user=request.user)

        notifikasi = Notifikasi.objects.create(
            pembuat=admin_pembuat,
            judul=title_notification,
            pesan=message_notification
        )
        
        for username in recipients:
            try:
                pengguna = Pengguna.objects.get(user__username=username)
                notifikasi.pengguna.add(pengguna)
            except:
                print(f"error: {username}")
        notifikasi.save()
        context['status'] = 'success'
        
    username = request.user.username
    context['username'] = username
    all_pengguna = Pengguna.objects.all()
    context['all_pengguna'] = all_pengguna
    return render(request, 'add_notification.html', context=context)