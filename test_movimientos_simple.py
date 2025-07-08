#!/usr/bin/env python
"""
Test específico para la creación de movimientos de inventario
"""
import os
import sys
import django

# Configuración de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from accounts.models import Usuario, Sucursal, Rol
from restaurant.models import Insumo, CategoriaInsumo, UnidadMedida, Inventario, MovimientoInventario
from dashboard.models import Proveedor
from decimal import Decimal

print('\n🚀 TEST REGISTRO DE MOVIMIENTOS')
print('='*50)

# Crear cliente de prueba
client = Client()

# Obtener datos de prueba
admin = Usuario.objects.filter(is_superuser=True).first()
sucursal = Sucursal.objects.filter(activa=True).first()
insumo = Insumo.objects.filter(activo=True).first()

print(f'👤 Usuario: {admin.username}')
print(f'🏢 Sucursal: {sucursal.nombre}')
print(f'📦 Insumo: {insumo.nombre}')

# Login
client.force_login(admin)

# Verificar inventario inicial
try:
    inventario = Inventario.objects.get(sucursal=sucursal, insumo=insumo)
    cantidad_inicial = inventario.cantidad_actual
    print(f'📊 Stock inicial: {cantidad_inicial} {insumo.unidad_medida.abreviacion}')
except Inventario.DoesNotExist:
    cantidad_inicial = Decimal('0')
    print(f'📊 No hay inventario previo, iniciando en: {cantidad_inicial}')

print('\n🔄 TEST 1: Crear ENTRADA...')
entrada_data = {
    'tipoMovimiento': 'entrada',
    'sucursalMovimiento': sucursal.id,
    'motivoMovimiento': 'compra',
    'insumoMovimiento': insumo.id,
    'cantidadMovimiento': '10.0',
    'costoUnitario': '15.50',
    'observacionesMovimiento': 'Entrada de prueba'
}

response = client.post('/dashboard/entradas-salidas/crear-movimiento', entrada_data)
print(f'Status Code: {response.status_code}')

if response.status_code == 200:
    try:
        data = response.json()
        print(f'Response JSON: {data}')
        
        if data.get('success'):
            print('✅ ENTRADA registrada exitosamente')
            print(f'🆔 ID Movimiento: {data.get("movimiento_id")}')
            print(f'📊 Nueva cantidad: {data.get("nueva_cantidad")}')
        else:
            print(f'❌ Error: {data.get("message")}')
    except Exception as e:
        print(f'❌ Error parseando JSON: {e}')
        print(f'Raw response: {response.content.decode()[:500]}')
else:
    print(f'❌ Error HTTP: {response.status_code}')
    print(f'Response: {response.content.decode()[:500]}')

print('\n🔄 TEST 2: Crear SALIDA...')
salida_data = {
    'tipoMovimiento': 'salida',
    'sucursalMovimiento': sucursal.id,
    'motivoMovimiento': 'venta',
    'insumoMovimiento': insumo.id,
    'cantidadMovimiento': '2.5',
    'observacionesMovimiento': 'Salida de prueba'
}

response = client.post('/dashboard/entradas-salidas/crear-movimiento', salida_data)
print(f'Status Code: {response.status_code}')

if response.status_code == 200:
    try:
        data = response.json()
        print(f'Response JSON: {data}')
        
        if data.get('success'):
            print('✅ SALIDA registrada exitosamente')
            print(f'🆔 ID Movimiento: {data.get("movimiento_id")}')
            print(f'📊 Nueva cantidad: {data.get("nueva_cantidad")}')
        else:
            print(f'❌ Error: {data.get("message")}')
    except Exception as e:
        print(f'❌ Error parseando JSON: {e}')
        print(f'Raw response: {response.content.decode()[:500]}')
else:
    print(f'❌ Error HTTP: {response.status_code}')
    print(f'Response: {response.content.decode()[:500]}')

# Verificar movimientos en BD
print('\n📋 Verificando movimientos en base de datos...')
movimientos = MovimientoInventario.objects.filter(
    sucursal=sucursal, 
    insumo=insumo
).order_by('-created_at')[:5]

for mov in movimientos:
    tipo_icon = '⬆️' if mov.tipo_movimiento == 'entrada' else '⬇️'
    print(f'{tipo_icon} {mov.tipo_movimiento.upper()} - {mov.cantidad} - {mov.motivo} - {mov.created_at}')

# Verificar inventario final
try:
    inventario_final = Inventario.objects.get(sucursal=sucursal, insumo=insumo)
    cantidad_final = inventario_final.cantidad_actual
    print(f'\n📊 Stock final: {cantidad_final} {insumo.unidad_medida.abreviacion}')
    diferencia = cantidad_final - cantidad_inicial
    print(f'📈 Diferencia total: {diferencia}')
except Inventario.DoesNotExist:
    print('\n❌ No se encontró inventario final')

print('\n✅ TEST DE MOVIMIENTOS COMPLETADO')
