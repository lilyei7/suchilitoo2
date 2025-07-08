#!/usr/bin/env python
"""
Script para testear los permisos de cajero
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from cajero.permissions import get_user_permissions

User = get_user_model()

def test_permissions():
    print('=== TEST DE PERMISOS ===')
    
    # Testear cada usuario
    for user in User.objects.all():
        print(f'\nUsuario: {user.username} ({user.first_name})')
        permissions = get_user_permissions(user)
        
        print(f'  Role display: {permissions["role_display"]}')
        print(f'  Can access POS: {permissions["can_access_pos"]}')
        print(f'  Can view sales: {permissions["can_view_sales"]}')
        print(f'  Can cancel sales: {permissions["can_cancel_sales"]}')
        print(f'  Is cajero: {permissions["is_cajero"]}')
        print(f'  Is gerente: {permissions["is_gerente"]}')
        print(f'  Is admin: {permissions["is_admin"]}')

if __name__ == '__main__':
    test_permissions()
