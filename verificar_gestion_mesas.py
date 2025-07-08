#!/usr/bin/env python
"""
Script para verificar que la gestión de mesas funciona correctamente
"""
import os
import django
from django.test import Client

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

print("=== VERIFICACIÓN DE GESTIÓN DE MESAS ===")

# Crear cliente de prueba
client = Client()

# Login como admin
print("0. Haciendo login...")
login_response = client.post('/dashboard/login/', {
    'username': 'jhayco',  # Usuario admin
    'password': '123456'
})
print(f"   Login estado: {login_response.status_code}")

if login_response.status_code == 302:
    print("   ✓ Login exitoso (redirigido)")
else:
    print("   ✗ Login falló")

# 1. Verificar que podemos acceder a la página
print("1. Probando acceso a la página de sucursales...")
response = client.get('/dashboard/sucursales/')
print(f"   Estado: {response.status_code}")

if response.status_code == 200:
    content = response.content.decode('utf-8')
    
    # Verificar elementos clave
    elementos_check = [
        'gestionarMesas',
        'modalGestionarMesas',
        'Gestionar Mesas',
        'formularioNuevaMesa',
        'gridMesas'
    ]
    
    print("2. Verificando elementos JavaScript y HTML:")
    for elemento in elementos_check:
        if elemento in content:
            print(f"   ✓ {elemento} - PRESENTE")
        else:
            print(f"   ✗ {elemento} - FALTANTE")
    
    # Verificar APIs
    print("3. Verificando APIs de mesas:")
    
    # API para listar mesas de sucursal 1
    api_response = client.get('/dashboard/api/sucursales/1/mesas/')
    print(f"   API listar mesas: {api_response.status_code}")
    
    if api_response.status_code == 200:
        data = api_response.json()
        if data.get('success'):
            print(f"   ✓ API funcionando - {len(data.get('mesas', []))} mesas encontradas")
        else:
            print(f"   ✗ API error: {data.get('message', 'Sin mensaje')}")
    
    print("\n4. URLs importantes para probar:")
    print("   - Dashboard: http://localhost:8000/dashboard/sucursales/")
    print("   - API mesas: http://localhost:8000/dashboard/api/sucursales/1/mesas/")
    
    print("\n5. Pasos para probar:")
    print("   1. Ir a http://localhost:8000/dashboard/sucursales/")
    print("   2. Hacer clic en el botón '...' de cualquier sucursal")
    print("   3. Hacer clic en 'Gestionar Mesas'")
    print("   4. Debería abrirse el modal con las mesas")
    
else:
    print(f"❌ No se pudo acceder a la página: {response.status_code}")

print("\n=== FIN DE LA VERIFICACIÓN ===")
