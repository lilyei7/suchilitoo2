#!/usr/bin/env python
"""
Script para probar el inventario con filtros por sucursal
"""
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario, Sucursal
from django.test import Client

def test_inventario_por_sucursal():
    print("=== PRUEBA DE INVENTARIO POR SUCURSAL ===")
    
    # 1. Obtener usuarios
    admin_user = Usuario.objects.filter(is_superuser=True).first()
    gerente_user = Usuario.objects.filter(rol__nombre='gerente').first()
    
    if not admin_user:
        print("❌ No se encontró usuario administrador")
        return
    
    print(f"✅ Usuario admin: {admin_user.username}")
    
    if gerente_user:
        print(f"✅ Usuario gerente: {gerente_user.username} (Sucursal: {gerente_user.sucursal.nombre if gerente_user.sucursal else 'Sin sucursal'})")
    else:
        print("⚠️ No se encontró usuario gerente")
    
    # 2. Obtener sucursales
    sucursales = Sucursal.objects.filter(activa=True)
    print(f"✅ Sucursales disponibles: {sucursales.count()}")
    for sucursal in sucursales:
        print(f"   - {sucursal.nombre} (ID: {sucursal.id})")
    
    # 3. Probar como ADMINISTRADOR
    print(f"\n--- PRUEBAS COMO ADMINISTRADOR ---")
    client = Client()
    client.force_login(admin_user)
    
    # Inventario sin filtros (debería ver todo)
    print("1. Inventario sin filtros:")
    response = client.get('/dashboard/inventario/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        context = response.context
        print(f"   ✅ Insumos con inventario: {len(context.get('insumos_con_inventario', []))}")
        print(f"   ✅ Es admin: {context.get('es_admin', False)}")
        print(f"   ✅ Sucursales disponibles: {len(context.get('sucursales_disponibles', []))}")
        print(f"   ✅ Total insumos: {context.get('total_insumos', 0)}")
        print(f"   ✅ Stock bajo: {context.get('insumos_stock_bajo', 0)}")
    
    # Inventario filtrado por primera sucursal
    if sucursales.exists():
        sucursal_test = sucursales.first()
        print(f"\n2. Inventario filtrado por {sucursal_test.nombre}:")
        response = client.get(f'/dashboard/inventario/?sucursal={sucursal_test.id}')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            context = response.context
            print(f"   ✅ Insumos filtrados: {len(context.get('insumos_con_inventario', []))}")
            print(f"   ✅ Sucursal seleccionada: {context.get('sucursal_seleccionada')}")
            print(f"   ✅ Filtro sucursal: {context.get('filtro_sucursal')}")
    
    # 4. Probar como GERENTE (si existe)
    if gerente_user and gerente_user.sucursal:
        print(f"\n--- PRUEBAS COMO GERENTE ---")
        client.force_login(gerente_user)
        
        print(f"1. Inventario como gerente de {gerente_user.sucursal.nombre}:")
        response = client.get('/dashboard/inventario/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            context = response.context
            print(f"   ✅ Insumos visibles: {len(context.get('insumos_con_inventario', []))}")
            print(f"   ✅ Es admin: {context.get('es_admin', False)}")
            print(f"   ✅ Sucursales disponibles: {len(context.get('sucursales_disponibles', []))}")
            print(f"   ✅ Sucursal del usuario: {context.get('user_sucursal')}")
            
            # Verificar que solo ve insumos de su sucursal
            for item in context.get('insumos_con_inventario', []):
                for inventario in item.get('inventarios', []):
                    if inventario.sucursal != gerente_user.sucursal:
                        print(f"   ❌ ERROR: Gerente ve insumo de otra sucursal: {inventario.sucursal.nombre}")
                        break
                else:
                    continue
                break
            else:
                print(f"   ✅ Gerente solo ve insumos de su sucursal")
        
        # Intentar filtrar por otra sucursal (no debería tener efecto)
        if sucursales.count() > 1:
            otra_sucursal = sucursales.exclude(id=gerente_user.sucursal.id).first()
            if otra_sucursal:
                print(f"\n2. Gerente intenta filtrar por {otra_sucursal.nombre} (debería ignorarse):")
                response = client.get(f'/dashboard/inventario/?sucursal={otra_sucursal.id}')
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    context = response.context
                    print(f"   ✅ Insumos visibles: {len(context.get('insumos_con_inventario', []))}")
                    print(f"   ✅ Sucursal efectiva: {context.get('sucursal_seleccionada')}")
    
    # 5. Verificar filtros adicionales
    print(f"\n--- PRUEBAS DE FILTROS ADICIONALES ---")
    client.force_login(admin_user)
    
    # Filtro por estado
    print("1. Filtro por estado 'bajo':")
    response = client.get('/dashboard/inventario/?estado=bajo')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        context = response.context
        bajo_count = len([item for item in context.get('insumos_con_inventario', []) if item.get('estado_stock') == 'bajo'])
        print(f"   ✅ Insumos con stock bajo encontrados: {bajo_count}")
    
    # Filtro por búsqueda
    print("\n2. Filtro por búsqueda 'xxx':")
    response = client.get('/dashboard/inventario/?buscar=xxx')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        context = response.context
        print(f"   ✅ Insumos encontrados con 'xxx': {len(context.get('insumos_con_inventario', []))}")
    
    print("\n=== PRUEBAS COMPLETADAS ===")

if __name__ == '__main__':
    test_inventario_por_sucursal()
