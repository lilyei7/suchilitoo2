#!/usr/bin/env python
"""
Script para probar específicamente la URL que causaba el error 500
"""
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario
from django.test import Client

# Usar el superuser existente
admin_user = Usuario.objects.filter(is_superuser=True).first()
client = Client()
client.force_login(admin_user)

print("=== PROBANDO URL QUE CAUSABA ERROR 500 ===")

# Esta es la URL exacta que estaba fallando
url = '/dashboard/entradas-salidas/filtrar?tipo=todos&sucursal=todos'
print(f"URL: {url}")

response = client.get(url)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"Success: {data['success']}")
    print(f"Movimientos encontrados: {len(data.get('movimientos', []))}")
    
    # Mostrar algunos movimientos para verificar que están funcionando
    if data.get('movimientos'):
        print("\nPrimeros 3 movimientos:")
        for i, mov in enumerate(data['movimientos'][:3]):
            print(f"  {i+1}. ID: {mov['id']}, Tipo: {mov['tipo']}, Sucursal: {mov['sucursal']}, Insumo: {mov['insumo']}")
else:
    print(f"ERROR: {response.content.decode()}")

print("\n=== PRUEBAS ADICIONALES ===")

# Probar otras variaciones
tests = [
    {'tipo': 'entrada', 'sucursal': 'todos'},
    {'tipo': 'salida', 'sucursal': 'todos'},
    {'tipo': 'todos', 'sucursal': '1'},
    {'tipo': 'entrada'},
    {'sucursal': 'todos'},
    {}  # Sin parámetros
]

for i, params in enumerate(tests, 1):
    params_str = '&'.join([f'{k}={v}' for k, v in params.items()])
    url = f'/dashboard/entradas-salidas/filtrar?{params_str}' if params_str else '/dashboard/entradas-salidas/filtrar'
    
    print(f"\n{i}. Probando: {url}")
    response = client.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success: {data['success']}, Movimientos: {len(data.get('movimientos', []))}")
    else:
        print(f"   ❌ Error {response.status_code}: {response.content.decode()[:100]}...")

print("\n=== TODAS LAS PRUEBAS COMPLETADAS ===")
