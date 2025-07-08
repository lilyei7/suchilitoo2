#!/usr/bin/env python
"""
Script para verificar y crear usuarios admin
"""
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario, Rol

# Verificar usuarios existentes
print("=== USUARIOS EXISTENTES ===")
usuarios = Usuario.objects.all()
for user in usuarios:
    print(f"- {user.username} (Rol: {user.rol.nombre if user.rol else 'Sin rol'}, Superuser: {user.is_superuser})")

print("\n=== ROLES EXISTENTES ===")
roles = Rol.objects.all()
for rol in roles:
    print(f"- {rol.nombre}")

# Verificar si hay admin
admin_users = Usuario.objects.filter(rol__nombre='admin')
superusers = Usuario.objects.filter(is_superuser=True)

print(f"\nUsuarios admin (por rol): {admin_users.count()}")
print(f"Superusuarios: {superusers.count()}")

# Si hay superuser, úsalo
if superusers.exists():
    admin_user = superusers.first()
    print(f"Usando superuser: {admin_user.username}")
    
    # Probar endpoint
    from django.test import Client
    client = Client()
    client.force_login(admin_user)
    
    print("\n=== PROBANDO ENDPOINT ===")
    
    # Probar filtrar sin parámetros
    print("1. Sin parámetros:")
    response = client.get('/dashboard/entradas-salidas/filtrar')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data['success']}")
        print(f"   Movimientos: {len(data.get('movimientos', []))}")
    else:
        print(f"   Error: {response.content.decode()}")
    
    # Probar con sucursal=todos
    print("\n2. Con sucursal=todos:")
    response = client.get('/dashboard/entradas-salidas/filtrar?sucursal=todos')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data['success']}")
        print(f"   Movimientos: {len(data.get('movimientos', []))}")
    else:
        print(f"   Error: {response.content.decode()}")
    
    # Probar con tipo=todos
    print("\n3. Con tipo=todos:")
    response = client.get('/dashboard/entradas-salidas/filtrar?tipo=todos')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data['success']}")
        print(f"   Movimientos: {len(data.get('movimientos', []))}")
    else:
        print(f"   Error: {response.content.decode()}")
        
    # Probar la combinación problemática
    print("\n4. Con tipo=todos&sucursal=todos:")
    response = client.get('/dashboard/entradas-salidas/filtrar?tipo=todos&sucursal=todos')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data['success']}")
        print(f"   Movimientos: {len(data.get('movimientos', []))}")
    else:
        print(f"   Error: {response.content.decode()}")

else:
    print("No se encontró superuser disponible para pruebas")
