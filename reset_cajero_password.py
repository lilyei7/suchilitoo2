#!/usr/bin/env python
"""
Script para crear usuarios con contraseñas válidas
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Rol

User = get_user_model()

def reset_cajero_password():
    try:
        user = User.objects.get(username='cajero1')
        user.set_password('cajero123')
        user.save()
        print(f'✓ Contraseña actualizada para {user.username}')
        
        # Verificar que la contraseña funciona
        from django.contrib.auth import authenticate
        test_user = authenticate(username='cajero1', password='cajero123')
        if test_user:
            print('✓ Autenticación verificada correctamente')
        else:
            print('✗ Autenticación aún falla')
            
    except User.DoesNotExist:
        print('Usuario cajero1 no existe')

if __name__ == '__main__':
    reset_cajero_password()
