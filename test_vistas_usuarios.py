#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from accounts.models import Usuario

print('=== TESTING VISTAS CON DIFERENTES USUARIOS ===')

client = Client()

# Test 1: Usuario admin
print('\n1. Test con usuario ADMIN:')
admin_user = Usuario.objects.filter(is_superuser=True).first()
if admin_user:
    client.force_login(admin_user)
    response = client.get('/dashboard/entradas-salidas/')
    
    if response.status_code == 200:
        print(f'   ✓ Página carga correctamente')        # Verificar contexto
        context = response.context
        if context:
            print(f'   ✓ Sucursales disponibles: {context["sucursales"].count()}')
            print(f'   ✓ Proveedores disponibles: {context["proveedores"].count()}')
            print(f'   ✓ Es admin: {context.get("is_admin", False)}')
            print(f'   ✓ Sucursal fija: {context.get("user_sucursal")}')
        else:
            print('   ⚠ No hay contexto disponible')
    else:
        print(f'   ✗ Error: Status {response.status_code}')
else:
    print('   ✗ No se encontró usuario admin')

# Test 2: Usuario gerente
print('\n2. Test con usuario GERENTE:')
gerente_user = Usuario.objects.filter(rol__nombre='gerente', sucursal__isnull=False).first()
if gerente_user:
    client.force_login(gerente_user)
    response = client.get('/dashboard/entradas-salidas/')
    
    if response.status_code == 200:
        print(f'   ✓ Página carga correctamente')
        # Verificar contexto
        context = response.context
        if context:
            print(f'   ✓ Sucursales disponibles: {context["sucursales"].count()}')
            print(f'   ✓ Proveedores disponibles: {context["proveedores"].count()}')
            print(f'   ✓ Es admin: {context.get("is_admin", False)}')
            print(f'   ✓ Sucursal fija: {context.get("user_sucursal")}')
            
            # Verificar que solo ve su sucursal
            sucursales = list(context["sucursales"])
            if len(sucursales) == 1 and sucursales[0] == gerente_user.sucursal:
                print(f'   ✓ Solo ve su sucursal: {sucursales[0].nombre}')
            else:
                print(f'   ⚠ Ve múltiples sucursales: {[s.nombre for s in sucursales]}')
                
            # Verificar proveedores de su sucursal
            proveedores = list(context["proveedores"])
            print(f'   ✓ Proveedores de su sucursal: {[p.nombre_comercial for p in proveedores]}')
        else:
            print('   ⚠ No hay contexto disponible')
    else:
        print(f'   ✗ Error: Status {response.status_code}')
else:
    print('   ✗ No se encontró usuario gerente con sucursal')

# Test 3: Endpoint de insumos por proveedor
print('\n3. Test endpoint obtener-insumos con gerente:')
if gerente_user:
    sucursal_id = gerente_user.sucursal.id
    # Obtener un proveedor de esa sucursal
    from dashboard.models import Proveedor
    proveedor = Proveedor.objects.filter(sucursal=gerente_user.sucursal, estado='activo').first()
    
    if proveedor:
        url = f'/dashboard/entradas-salidas/obtener-insumos?sucursal_id={sucursal_id}&proveedor_id={proveedor.id}'
        response = client.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f'   ✓ Endpoint funciona: {data.get("success")}')
            print(f'   ✓ Insumos del proveedor: {len(data.get("insumos", []))}')
            
            for insumo in data.get("insumos", [])[:2]:
                print(f'     * {insumo["codigo"]} - {insumo["nombre"]} (${insumo["precio_unitario"]})')
        else:
            print(f'   ✗ Error: Status {response.status_code}')
    else:
        print('   ⚠ No hay proveedores en la sucursal del gerente')

print('\n=== TEST COMPLETO ===')
