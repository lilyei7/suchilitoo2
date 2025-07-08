#!/usr/bin/env python
"""
Script para debuggear usuarios y roles
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

def main():
    print('=== USUARIOS EXISTENTES ===')
    for user in User.objects.all():
        print(f'Usuario: {user.username} ({user.first_name})')
        print(f'  - is_superuser: {user.is_superuser}')
        print(f'  - is_staff: {user.is_staff}')
        print(f'  - groups: {list(user.groups.values_list("name", flat=True))}')
        if hasattr(user, 'rol') and user.rol:
            print(f'  - rol: {user.rol.nombre}')
        else:
            print(f'  - rol: Sin rol asignado')
        print()

    print('=== ROLES EXISTENTES ===')
    for rol in Rol.objects.all():
        print(f'Rol: {rol.nombre} - {rol.descripcion}')

if __name__ == '__main__':
    main()
