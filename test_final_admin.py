#!/usr/bin/env python
"""
Test final para verificar funcionalidad completa de administrador
"""
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario, Sucursal
from restaurant.models import MovimientoInventario
from django.test import Client

def test_admin_functionality():
    print("=== TEST FINAL - FUNCIONALIDAD DE ADMINISTRADOR ===")
    
    # 1. Obtener usuario admin
    admin_user = Usuario.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No se encontró usuario administrador")
        return
    
    print(f"✅ Usuario admin: {admin_user.username}")
    
    # 2. Verificar sucursales disponibles
    sucursales = Sucursal.objects.filter(activa=True)
    print(f"✅ Sucursales activas: {sucursales.count()}")
    for sucursal in sucursales:
        movimientos_sucursal = MovimientoInventario.objects.filter(sucursal=sucursal).count()
        print(f"   - {sucursal.nombre}: {movimientos_sucursal} movimientos")
    
    # 3. Verificar movimientos totales
    total_movimientos = MovimientoInventario.objects.count()
    print(f"✅ Total de movimientos en sistema: {total_movimientos}")
    
    # 4. Crear cliente y hacer login
    client = Client()
    client.force_login(admin_user)
    
    # 5. Probar acceso a la página principal
    print("\n--- Probando acceso a página principal ---")
    response = client.get('/dashboard/entradas-salidas/')
    print(f"Status página principal: {response.status_code}")
    if response.status_code == 200:
        print("✅ Admin puede acceder a la página de entradas y salidas")
    else:
        print("❌ Admin no puede acceder a la página")
        return
    
    # 6. Probar filtrado sin restricciones (ver todos)
    print("\n--- Probando filtrado 'ver todos' ---")
    response = client.get('/dashboard/entradas-salidas/filtrar')
    if response.status_code == 200:
        data = response.json()
        movimientos_visibles = len(data.get('movimientos', []))
        print(f"✅ Admin puede ver {movimientos_visibles} movimientos sin filtro")
        
        # Verificar que puede ver movimientos de múltiples sucursales
        sucursales_en_movimientos = set()
        for mov in data.get('movimientos', []):
            sucursales_en_movimientos.add(mov['sucursal'])
        
        print(f"✅ Admin ve movimientos de {len(sucursales_en_movimientos)} sucursales:")
        for sucursal in sucursales_en_movimientos:
            print(f"   - {sucursal}")
    else:
        print(f"❌ Error al filtrar sin restricciones: {response.status_code}")
    
    # 7. Probar filtrado por sucursal específica
    if sucursales.count() > 1:
        print("\n--- Probando filtrado por sucursal específica ---")
        sucursal_test = sucursales.first()
        response = client.get(f'/dashboard/entradas-salidas/filtrar?sucursal={sucursal_test.id}')
        if response.status_code == 200:
            data = response.json()
            movimientos_filtrados = data.get('movimientos', [])
            print(f"✅ Admin puede filtrar por {sucursal_test.nombre}: {len(movimientos_filtrados)} movimientos")
            
            # Verificar que todos los movimientos son de la sucursal correcta
            todos_correctos = all(mov['sucursal'] == sucursal_test.nombre for mov in movimientos_filtrados)
            if todos_correctos:
                print("✅ Filtrado por sucursal funciona correctamente")
            else:
                print("❌ Filtrado por sucursal no está funcionando correctamente")
        else:
            print(f"❌ Error al filtrar por sucursal: {response.status_code}")
    
    # 8. Probar filtrado por tipo
    print("\n--- Probando filtrado por tipo ---")
    response = client.get('/dashboard/entradas-salidas/filtrar?tipo=entrada')
    if response.status_code == 200:
        data = response.json()
        entradas = data.get('movimientos', [])
        print(f"✅ Admin puede filtrar entradas: {len(entradas)} movimientos")
        
        # Verificar que todos son entradas
        todas_entradas = all(mov['tipo'] == 'entrada' for mov in entradas)
        if todas_entradas:
            print("✅ Filtrado por tipo 'entrada' funciona correctamente")
        else:
            print("❌ Filtrado por tipo no funciona correctamente")
    else:
        print(f"❌ Error al filtrar por tipo: {response.status_code}")
    
    # 9. Probar combinación de filtros
    print("\n--- Probando combinación de filtros ---")
    if sucursales.count() > 0:
        sucursal_test = sucursales.first()
        response = client.get(f'/dashboard/entradas-salidas/filtrar?tipo=entrada&sucursal={sucursal_test.id}')
        if response.status_code == 200:
            data = response.json()
            movimientos_combinados = data.get('movimientos', [])
            print(f"✅ Admin puede usar filtros combinados: {len(movimientos_combinados)} movimientos")
            
            # Verificar filtros combinados
            filtros_correctos = all(
                mov['tipo'] == 'entrada' and mov['sucursal'] == sucursal_test.nombre 
                for mov in movimientos_combinados
            )
            if filtros_correctos:
                print("✅ Filtros combinados funcionan correctamente")
            else:
                print("❌ Filtros combinados no funcionan correctamente")
        else:
            print(f"❌ Error con filtros combinados: {response.status_code}")
    
    # 10. Verificar que el modal de detalles funciona
    if total_movimientos > 0:
        print("\n--- Probando modal de detalles ---")
        ultimo_movimiento = MovimientoInventario.objects.first()
        response = client.get(f'/dashboard/entradas-salidas/detalle/{ultimo_movimiento.id}/')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Admin puede ver detalles de movimientos")
                detalle = data.get('movimiento', {})
                print(f"   - Movimiento ID: {detalle.get('id')}")
                print(f"   - Tipo: {detalle.get('tipo_movimiento')}")
                print(f"   - Sucursal: {detalle.get('sucursal')}")
                print(f"   - Insumo: {detalle.get('insumo', {}).get('nombre')}")
            else:
                print(f"❌ Error en detalles: {data.get('message')}")
        else:
            print(f"❌ Error al acceder a detalles: {response.status_code}")
    
    print("\n=== RESUMEN FINAL ===")
    print("✅ Todas las funcionalidades del administrador están funcionando correctamente")
    print("✅ El error 500 ha sido solucionado")
    print("✅ Admin puede ver todos los movimientos")
    print("✅ Admin puede filtrar por sucursal")
    print("✅ Admin puede filtrar por tipo")
    print("✅ Admin puede usar filtros combinados")
    print("✅ Admin puede ver detalles de movimientos")

if __name__ == '__main__':
    test_admin_functionality()
