#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from accounts.models import Usuario
from dashboard.models import Proveedor, ProveedorInsumo

print('=== TESTING ENTRADAS Y SALIDAS ENDPOINT ===')

# Crear cliente de test
client = Client()

# Buscar usuario admin
user = Usuario.objects.filter(is_superuser=True).first()
if not user:
    print('ERROR: No se encontró usuario admin')
    sys.exit(1)

# Hacer login
client.force_login(user)
print(f'✓ Login como: {user.username}')

# Test 1: Solo sucursal
print('\n1. Test: Solo sucursal (ID=1)')
response = client.get('/dashboard/entradas-salidas/obtener-insumos?sucursal_id=1')
if response.status_code == 200:
    data = response.json()
    print(f'   ✓ Success: {data.get("success")}')
    print(f'   ✓ Insumos encontrados: {len(data.get("insumos", []))}')
else:
    print(f'   ✗ Error: Status {response.status_code}')

# Test 2: Sucursal + Proveedor
print('\n2. Test: Sucursal + Proveedor (sucursal=1, proveedor=1)')
response = client.get('/dashboard/entradas-salidas/obtener-insumos?sucursal_id=1&proveedor_id=1')
if response.status_code == 200:
    data = response.json()
    print(f'   ✓ Success: {data.get("success")}')
    print(f'   ✓ Insumos encontrados: {len(data.get("insumos", []))}')
    
    if data.get('insumos'):
        print('   ✓ Primeros insumos:')
        for insumo in data['insumos'][:3]:
            precio = insumo.get('precio_unitario', 0)
            print(f'      - {insumo["codigo"]} - {insumo["nombre"]} (${precio})')
    else:
        print('   ⚠ No hay insumos para este proveedor')
else:
    print(f'   ✗ Error: Status {response.status_code}')

# Test 3: Proveedor inexistente
print('\n3. Test: Proveedor inexistente (sucursal=1, proveedor=999)')
response = client.get('/dashboard/entradas-salidas/obtener-insumos?sucursal_id=1&proveedor_id=999')
if response.status_code == 200:
    data = response.json()
    print(f'   ✓ Success: {data.get("success")}')
    print(f'   ✓ Insumos encontrados: {len(data.get("insumos", []))}')
else:
    print(f'   ✗ Error: Status {response.status_code}')

print('\n=== TEST COMPLETO ===')
