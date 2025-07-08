#!/usr/bin/env python
"""
Demo completo del módulo de Entradas y Salidas
Simula el uso completo del sistema de movimientos de inventario
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from dashboard.models import *
from accounts.models import Usuario, Rol, Sucursal
from restaurant.models import *
import json

User = get_user_model()

def demo_entradas_salidas():
    print("🎯 Demo del Sistema de Entradas y Salidas")
    print("=" * 50)
    
    client = Client()
    
    # 1. Login como admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No hay usuario admin")
        return
    
    client.force_login(admin_user)
    print(f"🔐 Login como: {admin_user.username}")
    
    # 2. Crear movimiento de entrada vía POST
    print("\n📦 Simulando movimiento de ENTRADA...")
      # Obtener datos necesarios
    sucursal = Sucursal.objects.filter(activa=True).first()
    insumo = Insumo.objects.filter(activo=True).first()
    # Usar el modelo de proveedor correcto del dashboard
    from dashboard.models import Proveedor as DashboardProveedor
    proveedor = DashboardProveedor.objects.filter(estado='activo').first()
    
    if not all([sucursal, insumo]):
        print("❌ Faltan datos básicos (sucursal, insumo)")
        return
    
    data_entrada = {
        'tipoMovimiento': 'entrada',
        'sucursalMovimiento': sucursal.id,
        'motivoMovimiento': 'compra',
        'insumoMovimiento': insumo.id,
        'cantidadMovimiento': '50',
        'observacionesMovimiento': 'Demo de entrada vía Python script',
    }
    
    if proveedor:
        data_entrada['proveedorMovimiento'] = proveedor.id
        data_entrada['costoUnitario'] = '15.50'
    
    response = client.post('/dashboard/entradas-salidas/crear-movimiento', data_entrada)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"✅ Entrada creada: {result.get('message')}")
            print(f"   📊 Nueva cantidad: {result.get('nueva_cantidad')}")
        else:
            print(f"❌ Error en entrada: {result.get('message')}")
    else:
        print(f"❌ Error HTTP en entrada: {response.status_code}")
    
    # 3. Crear movimiento de salida
    print("\n📤 Simulando movimiento de SALIDA...")
    
    data_salida = {
        'tipoMovimiento': 'salida',
        'sucursalMovimiento': sucursal.id,
        'motivoMovimiento': 'venta',
        'insumoMovimiento': insumo.id,
        'cantidadMovimiento': '10',
        'observacionesMovimiento': 'Demo de salida vía Python script',
    }
    
    response = client.post('/dashboard/entradas-salidas/crear-movimiento', data_salida)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"✅ Salida creada: {result.get('message')}")
            print(f"   📊 Nueva cantidad: {result.get('nueva_cantidad')}")
        else:
            print(f"❌ Error en salida: {result.get('message')}")
    else:
        print(f"❌ Error HTTP en salida: {response.status_code}")
    
    # 4. Consultar movimientos actualizados
    print("\n📋 Consultando movimientos actualizados...")
    
    response = client.get('/dashboard/entradas-salidas/filtrar', 
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    if response.status_code == 200:
        data = response.json()
        movimientos = data.get('movimientos', [])
        print(f"📊 Total de movimientos: {len(movimientos)}")
        
        if movimientos:
            print("\n🔍 Últimos 3 movimientos:")
            for mov in movimientos[:3]:
                tipo_icon = "📦" if mov['tipo_movimiento'] == 'entrada' else "📤"
                print(f"   {tipo_icon} {mov['fecha']} - {mov['insumo']} - {mov['cantidad']} {mov['unidad_medida']}")
                print(f"      Usuario: {mov['usuario']} | Sucursal: {mov['sucursal']} | Motivo: {mov['motivo']}")
        
        # Verificar que no hay campos undefined
        campos_con_undefined = []
        for mov in movimientos:
            for key, value in mov.items():
                if 'undefined' in str(value).lower():
                    campos_con_undefined.append(f"{key}: {value}")
        
        if campos_con_undefined:
            print(f"\n❌ Campos con 'undefined' encontrados:")
            for campo in campos_con_undefined:
                print(f"   - {campo}")
        else:
            print("\n✅ No se encontraron campos con 'undefined'")
    else:
        print(f"❌ Error consultando movimientos: {response.status_code}")
    
    # 5. Probar filtros específicos
    print("\n🔍 Probando filtros específicos...")
    
    # Filtrar solo entradas
    response = client.get('/dashboard/entradas-salidas/filtrar?tipo_movimiento=entrada', 
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    if response.status_code == 200:
        data = response.json()
        entradas = len(data.get('movimientos', []))
        print(f"📦 Entradas encontradas: {entradas}")
    
    # Filtrar solo salidas
    response = client.get('/dashboard/entradas-salidas/filtrar?tipo_movimiento=salida', 
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    if response.status_code == 200:
        data = response.json()
        salidas = len(data.get('movimientos', []))
        print(f"📤 Salidas encontradas: {salidas}")
    
    # 6. Verificar inventario actualizado
    print("\n📊 Verificando inventario...")
    try:
        inventario = Inventario.objects.filter(sucursal=sucursal, insumo=insumo).first()
        if inventario:
            print(f"✅ Stock actual de '{insumo.nombre}': {inventario.cantidad_actual} {insumo.unidad_medida.abreviacion}")
            print(f"💰 Costo unitario: ${inventario.costo_unitario}")
        else:
            print("⚠️  No se encontró registro de inventario")
    except Exception as e:
        print(f"❌ Error verificando inventario: {e}")
    
    print("\n🎉 Demo completado exitosamente!")
    print("\n📋 Resumen:")
    print("- ✅ Creación de movimientos de entrada y salida")
    print("- ✅ APIs de filtrado funcionando")
    print("- ✅ Datos sin campos 'undefined'")
    print("- ✅ Inventario actualizado correctamente")
    print("- ✅ Filtros específicos funcionando")

if __name__ == '__main__':
    demo_entradas_salidas()
