#!/usr/bin/env python
"""
Script para probar la nueva API de insumos disponibles
"""
import os
import sys
import django
from django.test import Client

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def test_api_insumos():
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
    
    # Probar la nueva API
    print("\n🔍 Probando nueva API de insumos para elaborados...")
    
    response = client.get('/dashboard/insumos-elaborados/insumos-disponibles/')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if data.get('success'):
                print("✅ API funciona correctamente!")
                print(f"📊 Insumos encontrados: {len(data['insumos'])}")
                print(f"   - Básicos: {data['total_basicos']}")
                print(f"   - Compuestos: {data['total_compuestos']}")
                
                # Mostrar algunos ejemplos
                print("\n📦 Ejemplos de insumos disponibles:")
                for insumo in data['insumos'][:5]:  # Mostrar los primeros 5
                    print(f"   - {insumo['nombre']} ({insumo['tipo']}) - ${insumo['precio_unitario']}/{insumo['unidad_abrev']}")
                
                if len(data['insumos']) > 5:
                    print(f"   ... y {len(data['insumos']) - 5} más")
                    
            else:
                print(f"❌ Error en la API: {data.get('error')}")
        except Exception as e:
            print(f"❌ Error procesando respuesta JSON: {e}")
    else:
        print(f"❌ Error HTTP: {response.status_code}")

if __name__ == "__main__":
    test_api_insumos()
