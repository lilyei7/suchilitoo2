#!/usr/bin/env python
"""
Script simple para verificar la URL de filtrado desde el shell de Django
"""
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from accounts.models import Usuario, Rol

# Crear cliente de prueba
client = Client()

# Intentar obtener usuario admin
try:
    admin_users = Usuario.objects.filter(rol__nombre='admin')
    if admin_users.exists():
        admin_user = admin_users.first()
        print(f"Encontrado usuario admin: {admin_user.username}")
        
        # Hacer login
        client.force_login(admin_user)
          # Probar endpoint de filtrado
        response = client.get('/dashboard/entradas-salidas/filtrar')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data['success']}")
            print(f"Movimientos: {len(data.get('movimientos', []))}")
        else:
            print(f"Error: {response.content.decode()}")
    else:
        print("No se encontró usuario admin")
        
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
