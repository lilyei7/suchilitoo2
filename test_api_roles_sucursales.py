#!/usr/bin/env python
"""
Script para probar la API de roles y sucursales
"""
import os
import sys
import django
import json
import requests

# Configurar el entorno de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth import get_user_model
from accounts.models import Rol, Sucursal

User = get_user_model()

def test_api_roles_sucursales():
    """Probar la API de roles y sucursales"""
    # Crear un cliente para las pruebas
    client = Client()
    
    # Verificar que haya un usuario admin
    if not User.objects.filter(is_superuser=True).exists():
        print("❌ No hay usuarios administradores. Creando uno...")
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123456'
        )
        print("✅ Usuario admin creado")
    
    # Iniciar sesión con un usuario admin
    admin = User.objects.filter(is_superuser=True).first()
    client.force_login(admin)
    
    # Obtener roles y sucursales
    response = client.get('/dashboard/api/sucursales-roles/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    
    # Verificar respuesta
    if response.status_code == 200:
        data = json.loads(response.content)
        print("Respuesta del servidor:")
        print(json.dumps(data, indent=2))
        
        if data.get('success'):
            print("\n✅ API de roles y sucursales funcionando correctamente")
            
            # Verificar roles
            if len(data.get('roles', [])) == 0:
                print("❌ No se encontraron roles activos")
            else:
                print(f"✅ Se encontraron {len(data['roles'])} roles")
                
            # Verificar sucursales
            if len(data.get('sucursales', [])) == 0:
                print("❌ No se encontraron sucursales activas")
            else:
                print(f"✅ Se encontraron {len(data['sucursales'])} sucursales")
        else:
            print(f"❌ Error en la API: {data.get('message')}")
    else:
        print(f"❌ Error en la respuesta: {response.status_code}")

if __name__ == "__main__":
    print("Probando API de roles y sucursales...")
    test_api_roles_sucursales()
    
    # Mostrar información adicional
    print("\nInformación adicional:")
    print(f"- Roles activos en la base de datos: {Rol.objects.filter(activo=True).count()}")
    print(f"- Sucursales activas en la base de datos: {Sucursal.objects.filter(activa=True).count()}")
