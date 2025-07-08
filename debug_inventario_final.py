#!/usr/bin/env python
"""
Script para depurar el inventario final y confirmar que la tabla se muestra correctamente
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suchilitoo.settings')
django.setup()

from accounts.models import Usuario
from restaurant.models import Insumo, Sucursal, Inventario
from django.test import Client

def test_inventario_response():
    """Test que la respuesta del inventario contenga los datos correctos"""
    
    print("=== DEBUGGING INVENTARIO FINAL ===")
    
    # Crear un cliente de prueba
    client = Client()
    
    # Obtener un usuario admin
    admin_user = Usuario.objects.filter(rol='admin').first()
    if not admin_user:
        print("❌ No se encontró usuario admin")
        return
    
    print(f"✅ Usuario admin encontrado: {admin_user.username}")
    
    # Login como admin
    client.force_login(admin_user)
    
    # Hacer petición GET al inventario
    response = client.get('/dashboard/inventario/')
    
    print(f"✅ Response status: {response.status_code}")
    print(f"✅ Response context keys: {list(response.context.keys())}")
    
    # Verificar contexto
    context = response.context
    insumos_con_inventario = context.get('insumos_con_inventario', [])
    
    print(f"✅ insumos_con_inventario count: {len(insumos_con_inventario)}")
    
    if insumos_con_inventario:
        print("✅ Primeros 3 elementos de insumos_con_inventario:")
        for i, item in enumerate(insumos_con_inventario[:3]):
            print(f"  {i+1}. Insumo: {item['insumo'].nombre}")
            print(f"     Stock actual: {item['stock_actual']}")
            print(f"     Estado: {item['estado']}")
            print(f"     Sucursal: {item['sucursal'].nombre if item['sucursal'] else 'N/A'}")
            print("     ---")
    
    # Verificar si hay contenido HTML en la respuesta
    content = response.content.decode('utf-8')
    
    # Buscar por elementos clave de la tabla
    table_indicators = [
        'insumos_con_inventario',
        'table-responsive',
        'insumo-row',
        'Stock Actual',
        'Estado'
    ]
    
    print("✅ Verificando contenido HTML:")
    for indicator in table_indicators:
        if indicator in content:
            print(f"  ✅ Encontrado: {indicator}")
        else:
            print(f"  ❌ NO encontrado: {indicator}")
    
    # Buscar por nombres de insumos específicos
    print("✅ Verificando presencia de nombres de insumos:")
    insumos = Insumo.objects.all()[:3]
    for insumo in insumos:
        if insumo.nombre in content:
            print(f"  ✅ Insumo encontrado en HTML: {insumo.nombre}")
        else:
            print(f"  ❌ Insumo NO encontrado en HTML: {insumo.nombre}")

def test_gerente_access():
    """Test acceso como gerente"""
    
    print("\n=== TEST GERENTE ACCESS ===")
    
    client = Client()
    
    # Obtener un usuario gerente
    gerente = Usuario.objects.filter(rol='gerente').first()
    if not gerente:
        print("❌ No se encontró usuario gerente")
        return
    
    print(f"✅ Usuario gerente encontrado: {gerente.username}")
    print(f"✅ Sucursal del gerente: {gerente.sucursal.nombre if gerente.sucursal else 'N/A'}")
    
    # Login como gerente
    client.force_login(gerente)
    
    # Hacer petición GET al inventario
    response = client.get('/dashboard/inventario/')
    
    print(f"✅ Response status: {response.status_code}")
    
    context = response.context
    insumos_con_inventario = context.get('insumos_con_inventario', [])
    es_admin = context.get('es_admin', False)
    user_sucursal = context.get('user_sucursal')
    
    print(f"✅ Es admin: {es_admin}")
    print(f"✅ User sucursal: {user_sucursal.nombre if user_sucursal else 'N/A'}")
    print(f"✅ insumos_con_inventario count: {len(insumos_con_inventario)}")
    
    if insumos_con_inventario:
        print("✅ Todos los insumos pertenecen a la sucursal del gerente:")
        for item in insumos_con_inventario:
            sucursal_item = item['sucursal'].nombre if item['sucursal'] else 'N/A'
            esperada = user_sucursal.nombre if user_sucursal else 'N/A'
            match = sucursal_item == esperada
            print(f"  Insumo: {item['insumo'].nombre}, Sucursal: {sucursal_item}, Match: {'✅' if match else '❌'}")

if __name__ == "__main__":
    test_inventario_response()
    test_gerente_access()
