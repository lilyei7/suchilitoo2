#!/usr/bin/env python
"""
Test de login programático para debuggear el problema
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.messages import get_messages
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from cajero.views import login_view

User = get_user_model()

def test_login():
    # Probar con el usuario Juan (cajero1)
    username = 'cajero1'
    password = 'cajero123'
    
    print(f'=== TEST LOGIN PARA {username} ===')
    
    # Primero verificar que el usuario existe
    try:
        user = User.objects.get(username=username)
        print(f'Usuario encontrado: {user.username} ({user.first_name})')
        print(f'Rol: {user.rol.nombre if user.rol else "Sin rol"}')
    except User.DoesNotExist:
        print(f'Usuario {username} no existe')
        return
    
    # Probar autenticación
    user = authenticate(username=username, password=password)
    if user:
        print('✓ Autenticación exitosa')
        
        # Verificar permisos
        from cajero.permissions import get_user_permissions
        permissions = get_user_permissions(user)
        print(f'Permisos: {permissions}')
        
    else:
        print('✗ Autenticación fallida')
    
    # Probar con cliente de Django
    client = Client()
    response = client.post('/cajero/login/', {
        'username': username,
        'password': password
    })
    
    print(f'Response status: {response.status_code}')
    if response.status_code == 302:
        print(f'Redirect to: {response.url}')
    
    # Verificar mensajes
    messages = list(get_messages(response.wsgi_request))
    print(f'Messages: {[str(m) for m in messages]}')

if __name__ == '__main__':
    test_login()
