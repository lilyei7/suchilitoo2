from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Usamos importación absoluta en lugar de relativa
from dashboard.views.base_views import get_sidebar_context

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:principal')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard:principal')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'dashboard/login.html')

def logout_view(request):
    logout(request)
    return redirect('dashboard:login')
