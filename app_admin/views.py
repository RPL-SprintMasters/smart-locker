from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_admin(request):
    context = dict()
    username = request.user.username
    context['username'] = username
    return render(request, 'dashboard_admin.html', context=context)