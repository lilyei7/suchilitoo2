#!/usr/bin/env python3
"""
Test para diagnosticar problemas del editor de croquis
"""
import os
import django
import sys

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User
from accounts.models import Sucursal
from dashboard.models_ventas import Mesa

def test_croquis_debug():
    print("🔍 DIAGNÓSTICO DEL EDITOR DE CROQUIS")
    print("=" * 50)
    
    # 1. Verificar mesas existentes
    print("\n1. VERIFICANDO MESAS EXISTENTES:")
    sucursales = Sucursal.objects.all()
    for sucursal in sucursales:
        mesas = Mesa.objects.filter(sucursal=sucursal, activo=True)
        print(f"   Sucursal: {sucursal.nombre} ({sucursal.id})")
        print(f"   Mesas activas: {mesas.count()}")
        if mesas.exists():
            for mesa in mesas[:3]:  # Mostrar solo las primeras 3
                print(f"     • Mesa {mesa.numero} - {mesa.capacidad} personas - Estado: {mesa.estado}")
        else:
            print("     ❌ No hay mesas activas")
    
    # 2. Test de la API de mesas
    print("\n2. TESTEANDO API DE MESAS:")
    client = Client()
    
    # Crear usuario admin para test
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    
    client.force_login(admin_user)
    
    for sucursal in sucursales[:2]:  # Test solo las primeras 2 sucursales
        url = f'/dashboard/api/croquis/mesas/{sucursal.id}/'
        print(f"   Testing URL: {url}")
        
        try:
            response = client.get(url)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Success: {data.get('success', False)}")
                print(f"   Mesas en respuesta: {len(data.get('mesas', []))}")
                
                if data.get('mesas'):
                    for mesa in data['mesas'][:2]:
                        print(f"     • Mesa API: {mesa.get('numero')} - {mesa.get('capacidad')} personas")
            else:
                print(f"   ❌ Error: {response.status_code}")
                if hasattr(response, 'content'):
                    print(f"   Content: {response.content.decode()[:200]}")
                    
        except Exception as e:
            print(f"   ❌ Excepción: {e}")
    
    # 3. Verificar CSRF token en template
    print("\n3. VERIFICANDO CSRF EN TEMPLATE:")
    template_path = "dashboard/templates/dashboard/croquis_editor.html"
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        csrf_token_present = '{% csrf_token %}' in content
        csrf_middleware_present = 'csrfmiddlewaretoken' in content
        
        print(f"   CSRF token presente: {csrf_token_present}")
        print(f"   Referencias a csrfmiddlewaretoken: {csrf_middleware_present}")
        
        if csrf_token_present and csrf_middleware_present:
            print("   ✅ CSRF configurado correctamente")
        else:
            print("   ⚠️ Posibles problemas con CSRF")
            
    except FileNotFoundError:
        print(f"   ❌ Template no encontrado: {template_path}")
    
    # 4. Crear mesas de prueba si no existen
    print("\n4. CREANDO MESAS DE PRUEBA SI NECESARIO:")
    for sucursal in sucursales:
        mesas_count = Mesa.objects.filter(sucursal=sucursal, activo=True).count()
        if mesas_count == 0:
            print(f"   Creando mesas para {sucursal.nombre}...")
            for i in range(1, 6):  # Crear 5 mesas
                Mesa.objects.get_or_create(
                    sucursal=sucursal,
                    numero=i,
                    defaults={
                        'nombre': f'Mesa {i}',
                        'capacidad': 4,
                        'estado': 'disponible',
                        'activo': True
                    }
                )
            print(f"   ✅ Mesas creadas para {sucursal.nombre}")
        else:
            print(f"   ✅ {sucursal.nombre} ya tiene {mesas_count} mesas")
    
    print("\n" + "=" * 50)
    print("DIAGNÓSTICO COMPLETADO")
    print("\nPróximos pasos:")
    print("1. Verificar que las mesas se cargan en el editor")
    print("2. Probar guardar layout sin error 403")
    print("3. Verificar vinculación de mesas")

if __name__ == '__main__':
    test_croquis_debug()
