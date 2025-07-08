#!/usr/bin/env python
"""
Script para probar específicamente las restricciones de acceso a sucursales.
Solo admin y superadmin deben tener acceso.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario, Rol, Sucursal
from dashboard.utils.permissions import has_module_access
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

def test_sucursales_access():
    """Prueba el acceso al módulo de sucursales por rol"""
    print("=" * 60)
    print("PRUEBA DE ACCESO AL MÓDULO SUCURSALES")
    print("=" * 60)
    
    # Obtener usuarios de diferentes roles
    roles_test = [
        ('admin', '✅ DEBE tener acceso'),
        ('gerente', '❌ NO debe tener acceso'),
        ('supervisor', '❌ NO debe tener acceso'),
        ('cajero', '❌ NO debe tener acceso'),
        ('cocinero', '❌ NO debe tener acceso')
    ]
    
    print("🏪 ACCESO AL MÓDULO SUCURSALES:")
    print("-" * 40)
    
    for rol_nombre, expectativa in roles_test:
        try:
            # Buscar usuario con este rol
            rol = Rol.objects.filter(nombre=rol_nombre).first()
            if rol:
                usuario = Usuario.objects.filter(rol=rol).first()
                if usuario:
                    tiene_acceso = has_module_access(usuario, 'sucursales')
                    resultado = "✅ ACCESO" if tiene_acceso else "❌ BLOQUEADO"
                    estado = "✅" if (tiene_acceso and rol_nombre == 'admin') or (not tiene_acceso and rol_nombre != 'admin') else "⚠️  ERROR"
                    print(f"   {rol_nombre.upper():12} | {resultado:12} | {expectativa} {estado}")
                else:
                    print(f"   {rol_nombre.upper():12} | Sin usuario    | {expectativa}")
            else:
                print(f"   {rol_nombre.upper():12} | Sin rol       | {expectativa}")
        except Exception as e:
            print(f"   {rol_nombre.upper():12} | ERROR: {e}")
    
    # Probar superusuario
    try:
        superuser = Usuario.objects.filter(is_superuser=True).first()
        if superuser:
            tiene_acceso = has_module_access(superuser, 'sucursales')
            resultado = "✅ ACCESO" if tiene_acceso else "❌ BLOQUEADO"
            estado = "✅" if tiene_acceso else "⚠️  ERROR"
            print(f"   {'SUPERUSER':12} | {resultado:12} | ✅ DEBE tener acceso {estado}")
        else:
            print(f"   {'SUPERUSER':12} | Sin usuario    | ✅ DEBE tener acceso")
    except Exception as e:
        print(f"   {'SUPERUSER':12} | ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("RESUMEN DE SUCURSALES:")
    print("✅ SOLO DEBEN TENER ACCESO:")
    print("   - admin")
    print("   - superuser")
    print("\n❌ NO DEBEN TENER ACCESO:")
    print("   - gerente")
    print("   - supervisor") 
    print("   - cajero")
    print("   - cocinero")
    print("=" * 60)

def test_sucursales_view_protection():
    """Prueba la protección de las vistas de sucursales"""
    print("\n" + "=" * 60)
    print("PRUEBA DE PROTECCIÓN DE VISTAS DE SUCURSALES")
    print("=" * 60)
    
    from django.test import Client
    from django.urls import reverse
    
    client = Client()
    
    # Obtener usuarios de prueba
    try:
        gerente = Usuario.objects.filter(rol__nombre='gerente').first()
        admin = Usuario.objects.filter(is_superuser=True).first()
        
        if gerente:
            print(f"\n👤 PROBANDO CON GERENTE: {gerente.username}")
            
            # Hacer login como gerente
            client.force_login(gerente)
            
            try:
                response = client.get('/dashboard/sucursales/')
                if response.status_code == 403:
                    print("   ✅ Vista sucursales BLOQUEADA correctamente")
                elif response.status_code == 302:
                    print("   ✅ Vista sucursales redirigida (sin acceso)")
                else:
                    print(f"   ⚠️  Vista sucursales respuesta inesperada: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error probando vista: {e}")
            
            client.logout()
        
        if admin:
            print(f"\n👤 PROBANDO CON ADMIN: {admin.username}")
            
            # Hacer login como admin
            client.force_login(admin)
            
            try:
                response = client.get('/dashboard/sucursales/')
                if response.status_code == 200:
                    print("   ✅ Vista sucursales ACCESIBLE correctamente")
                else:
                    print(f"   ⚠️  Vista sucursales respuesta inesperada: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error probando vista: {e}")
            
            client.logout()
    
    except Exception as e:
        print(f"❌ Error en prueba de vistas: {e}")

if __name__ == "__main__":
    test_sucursales_access()
    test_sucursales_view_protection()
