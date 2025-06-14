#!/usr/bin/env python
"""
Script para diagnosticar problemas de autenticación
"""
import os
import sys
import django

# Configurar Django ANTES de cualquier import
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.sessions.models import Session

def diagnose_auth():
    print("🔍 Diagnosticando problemas de autenticación...")
    
    from accounts.models import Usuario
    
    # Verificar usuarios
    usuarios = Usuario.objects.all()
    print(f"👤 Usuarios en la base de datos: {usuarios.count()}")
    for user in usuarios:
        print(f"   - {user.username} (activo: {user.is_active}, staff: {user.is_staff}, superuser: {user.is_superuser})")
    
    # Verificar sesiones activas
    sesiones = Session.objects.all()
    print(f"🔐 Sesiones activas: {sesiones.count()}")
    
    # Probar login con cliente de prueba
    client = Client()
    
    # Intentar login con diferentes usuarios
    test_users = [
        ('admin', 'admin123'),
        ('test', 'test123'),
    ]
    
    for username, password in test_users:
        print(f"\n🔐 Probando login con {username}...")
        
        # Verificar que el usuario existe
        try:
            user = Usuario.objects.get(username=username)
            print(f"   ✅ Usuario encontrado: {user}")
        except Usuario.DoesNotExist:
            print(f"   ❌ Usuario {username} no existe")
            continue
        
        # Intentar login
        login_success = client.login(username=username, password=password)
        print(f"   Login exitoso: {login_success}")
        
        if login_success:
            # Probar acceso a páginas protegidas
            protected_urls = [
                '/dashboard/',
                '/dashboard/inventario/',
                '/dashboard/insumos-elaborados/',
                '/dashboard/insumos-compuestos/',
                '/dashboard/proveedores/',
            ]
            
            for url in protected_urls:
                response = client.get(url)
                print(f"   {url}: {response.status_code}")
                if response.status_code == 302:
                    print(f"      ↳ Redirección a: {response.url}")
        
        # Logout
        client.logout()
        print(f"   Logout completado")

if __name__ == "__main__":
    diagnose_auth()
