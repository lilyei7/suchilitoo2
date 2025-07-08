#!/usr/bin/env python
"""
Script para verificar que el dashboard principal carga correctamente
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from accounts.models import Usuario, Sucursal

def test_dashboard_access():
    print("🔍 Probando acceso al dashboard...")
    
    client = Client()
    
    try:
        # Crear usuario de prueba si no existe
        User = get_user_model()
        usuario, created = Usuario.objects.get_or_create(
            username='admin_test',
            defaults={
                'email': 'admin@test.com',
                'first_name': 'Admin',
                'last_name': 'Test',
                'rol': 'gerente'
            }
        )
        
        if created:
            usuario.set_password('admin123')
            usuario.save()
            print("✅ Usuario de prueba creado")
        
        # Probar login
        login_success = client.login(username='admin_test', password='admin123')
        if login_success:
            print("✅ Login exitoso")
        else:
            print("⚠️ Login falló, pero continuamos...")
        
        # Probar acceso a páginas principales
        urls_to_test = [
            '/dashboard/',
            '/dashboard/inventario/',
            '/dashboard/sucursales/',
            '/dashboard/checklist/',
        ]
        
        for url in urls_to_test:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {url} - OK (200)")
            elif response.status_code == 302:
                print(f"🔄 {url} - Redireccionado (302)")
            else:
                print(f"⚠️ {url} - Status: {response.status_code}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_dashboard_access()
