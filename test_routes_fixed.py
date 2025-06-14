#!/usr/bin/env python
"""
Script para probar todas las rutas corregidas del sistema
"""
import os
import sys
import django
from django.test import Client
from django.urls import reverse

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def test_fixed_routes():
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
    
    # URLs problemáticas que deberían estar corregidas
    test_urls = [
        ('dashboard:insumos_compuestos', 'Insumos Compuestos - CORREGIDO'),
        ('dashboard:proveedores', 'Proveedores - CORREGIDO'),
        ('dashboard:recetas', 'Recetas - NUEVO'),
        ('dashboard:reportes', 'Reportes - NUEVO'),
        ('dashboard:entradas_salidas', 'Entradas/Salidas'),
        ('dashboard:insumos_elaborados', 'Insumos Elaborados'),
    ]
    
    print("\n🔍 Probando rutas corregidas...")
    
    for url_name, description in test_urls:
        try:
            url = reverse(url_name)
            print(f"\n📍 Probando {description}")
            print(f"   URL: {url}")
            
            response = client.get(url)
            status = response.status_code
            print(f"   Status: {status}")
            
            if status == 200:
                content = response.content.decode('utf-8')
                
                # Verificar que NO contenga contenido de entradas y salidas cuando no debería
                if 'Entradas y Salidas' in content and 'entradas-salidas' not in url:
                    print("   ❌ ERROR: Contenido incorrecto (mostrando Entradas y Salidas)")
                elif 'Insumos Compuestos' in content and 'insumos-compuestos' in url:
                    print("   ✅ CORRECTO: Muestra contenido de Insumos Compuestos")
                elif 'Proveedores' in content and 'proveedores' in url:
                    print("   ✅ CORRECTO: Muestra contenido de Proveedores")
                elif 'Recetas' in content and 'recetas' in url:
                    print("   ✅ CORRECTO: Muestra contenido de Recetas")
                elif 'Reportes' in content and 'reportes' in url:
                    print("   ✅ CORRECTO: Muestra contenido de Reportes")
                elif 'Entradas y Salidas' in content and 'entradas-salidas' in url:
                    print("   ✅ CORRECTO: Muestra contenido de Entradas y Salidas")
                elif 'Insumos Elaborados' in content and 'insumos-elaborados' in url:
                    print("   ✅ CORRECTO: Muestra contenido de Insumos Elaborados")
                else:
                    print("   ⚠️  VERIFICAR: Contenido no identificado claramente")
                    
            elif status == 302:
                print("   ⚠️  Redirección (posible problema de auth)")
            elif status == 404:
                print("   ❌ ERROR 404: Ruta no encontrada")
            elif status == 500:
                print("   ❌ ERROR 500: Error interno del servidor")
            else:
                print(f"   ⚠️  Status inesperado: {status}")
                
        except Exception as e:
            print(f"   ❌ Excepción: {str(e)}")
    
    print("\n🔍 Probando APIs específicas...")
    
    # Probar APIs
    api_urls = [
        ('/dashboard/api/form-data/', 'API Form Data'),
        ('/dashboard/api/insumos-basicos/', 'API Insumos Básicos'),
        ('/dashboard/api/categorias/', 'API Categorías'),
        ('/dashboard/api/unidades-medida/', 'API Unidades de Medida'),
    ]
    
    for url, description in api_urls:
        try:
            print(f"\n📡 Probando {description}")
            response = client.get(url)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        print("   ✅ API responde correctamente")
                    else:
                        print(f"   ⚠️  API responde con error: {data.get('error', 'Unknown')}")
                except:
                    print("   ⚠️  Respuesta no es JSON válido")
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Excepción: {str(e)}")

if __name__ == "__main__":
    print("🚀 Probando correcciones del sistema de ruteo...")
    test_fixed_routes()
    print("\n✅ Pruebas completadas")
