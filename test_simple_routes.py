#!/usr/bin/env python
"""
Script simple para probar las rutas principales
"""
import os
import sys
import django
from django.test import Client

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def test_simple():
    client = Client()
    
    # Login como admin
    from accounts.models import Usuario
    
    try:
        admin_user = Usuario.objects.get(username='admin')
    except Usuario.DoesNotExist:
        admin_user = Usuario.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123',
            nombre='Admin',
            apellido='Test'
        )
        print("✅ Usuario admin creado")
    
    login_success = client.login(username='admin', password='admin123')
    print(f"🔐 Login exitoso: {login_success}")
    
    if not login_success:
        print("❌ No se pudo hacer login")
        return
    
    # Probar rutas directamente
    test_urls = [
        '/dashboard/insumos-compuestos/',
        '/dashboard/proveedores/',
        '/dashboard/recetas/',
        '/dashboard/reportes/',
        '/dashboard/entradas-salidas/'
    ]
    
    for url in test_urls:
        try:
            response = client.get(url)
            print(f"{url} - Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                if 'Entradas y Salidas' in content and 'entradas-salidas' not in url:
                    print("   ❌ ERROR: Contenido incorrecto")
                else:
                    print("   ✅ OK")
            elif response.status_code == 302:
                print("   ⚠️  Redirección")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Excepción: {str(e)}")

if __name__ == "__main__":
    print("🚀 Prueba simple de rutas...")
    test_simple()
    print("✅ Prueba completada")
