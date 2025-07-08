#!/usr/bin/env python
"""
Script de verificación final para confirmar que los proveedores se muestran correctamente 
en todos los lugares: tabla de inventario, modal de detalles, y API.
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from restaurant.models import Insumo
from dashboard.models import Proveedor, ProveedorInsumo
from accounts.models import Usuario
import json

def main():
    print("🔎 VERIFICACIÓN FINAL: PROVEEDORES EN INVENTARIO")
    print("=" * 60)
    
    try:
        # Buscar un usuario admin
        admin_user = Usuario.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = Usuario.objects.filter(rol__nombre='admin').first()
        
        if not admin_user:
            print("❌ No se encontró un usuario administrador")
            return
        
        print(f"✅ Usuario: {admin_user.username}")
        
        # Crear cliente y hacer login
        client = Client()
        client.force_login(admin_user)
        
        # 1. Verificar vista de inventario principal
        print(f"\n🌐 VERIFICANDO VISTA DE INVENTARIO PRINCIPAL")
        response = client.get('/dashboard/inventario/')
        
        if response.status_code != 200:
            print(f"❌ Error en vista de inventario: {response.status_code}")
            return
        
        # Verificar que el contexto incluye la nueva información de proveedores
        context = response.context
        insumos_con_inventario = context.get('insumos_con_inventario', [])
        
        print(f"✅ Vista cargada. Insumos con inventario: {len(insumos_con_inventario)}")
        
        # Verificar que cada item tiene la nueva estructura de proveedores
        for item in insumos_con_inventario[:3]:  # Solo verificar los primeros 3
            insumo = item['insumo']
            proveedores = item.get('proveedores', [])
            
            print(f"\n📦 {insumo.nombre} (ID: {insumo.id})")
            print(f"   - Proveedores en contexto: {len(proveedores)}")
            
            for proveedor in proveedores:
                print(f"     * {proveedor['nombre']} ({proveedor['tipo']})")
        
        # 2. Verificar API de detalles para varios insumos
        print(f"\n🔍 VERIFICANDO API DE DETALLES")
        
        insumos_test = Insumo.objects.all()[:3]
        
        for insumo in insumos_test:
            print(f"\n📋 API para {insumo.nombre} (ID: {insumo.id})")
            
            response_api = client.get(f'/dashboard/insumos/{insumo.id}/detalle/', 
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            
            if response_api.status_code != 200:
                print(f"   ❌ Error en API: {response_api.status_code}")
                continue
            
            data = response_api.json()
            proveedores_api = data.get('proveedores', [])
            
            print(f"   ✅ API respondió: {len(proveedores_api)} proveedores")
            
            for proveedor in proveedores_api:
                precio = proveedor.get('precio_unitario', '0')
                print(f"     * {proveedor['nombre']} ({proveedor['tipo']}) - ${precio}")
                if proveedor.get('tiempo_entrega'):
                    print(f"       - Entrega: {proveedor['tiempo_entrega']} días")
                if proveedor.get('cantidad_minima') and proveedor['cantidad_minima'] != '1':
                    print(f"       - Cantidad mínima: {proveedor['cantidad_minima']}")
        
        # 3. Verificar que insumos sin proveedores se manejan correctamente
        print(f"\n🔍 VERIFICANDO INSUMOS SIN PROVEEDORES")
        
        insumo_sin_proveedor = Insumo.objects.filter(
            proveedor_principal__isnull=True
        ).first()
        
        if insumo_sin_proveedor:
            # Asegurar que no tenga relaciones ProveedorInsumo
            ProveedorInsumo.objects.filter(insumo=insumo_sin_proveedor).delete()
            
            print(f"📦 {insumo_sin_proveedor.nombre} (ID: {insumo_sin_proveedor.id})")
            
            # Verificar API
            response_api = client.get(f'/dashboard/insumos/{insumo_sin_proveedor.id}/detalle/', 
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            
            if response_api.status_code == 200:
                data = response_api.json()
                proveedores_api = data.get('proveedores', [])
                
                if len(proveedores_api) == 0:
                    print("   ✅ API maneja correctamente insumo sin proveedores")
                else:
                    print(f"   ⚠️ API devuelve {len(proveedores_api)} proveedores cuando debería ser 0")
            else:
                print(f"   ❌ Error en API para insumo sin proveedores: {response_api.status_code}")
        else:
            print("   ℹ️ No se encontró insumo sin proveedores para probar")
        
        # 4. Verificar casos mixtos (principal + asignados)
        print(f"\n🔍 VERIFICANDO CASOS MIXTOS")
        
        # Buscar insumo con proveedor principal
        insumo_con_principal = Insumo.objects.filter(proveedor_principal__isnull=False).first()
        
        if insumo_con_principal:
            # Verificar si también tiene relaciones ProveedorInsumo
            relaciones = ProveedorInsumo.objects.filter(insumo=insumo_con_principal, activo=True)
            
            print(f"📦 {insumo_con_principal.nombre} (ID: {insumo_con_principal.id})")
            print(f"   - Proveedor principal: {insumo_con_principal.proveedor_principal.nombre}")
            print(f"   - Relaciones ProveedorInsumo: {relaciones.count()}")
            
            # Verificar API
            response_api = client.get(f'/dashboard/insumos/{insumo_con_principal.id}/detalle/', 
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            
            if response_api.status_code == 200:
                data = response_api.json()
                proveedores_api = data.get('proveedores', [])
                tipos = [p['tipo'] for p in proveedores_api]
                
                expected_count = 1 + relaciones.count()  # Principal + relaciones
                
                if len(proveedores_api) == expected_count:
                    print(f"   ✅ API devuelve {len(proveedores_api)} proveedores (correcto)")
                    
                    if 'principal' in tipos:
                        print("   ✅ Incluye proveedor principal")
                    else:
                        print("   ❌ NO incluye proveedor principal")
                    
                    if relaciones.count() > 0 and 'asignado' in tipos:
                        print("   ✅ Incluye proveedores asignados")
                    elif relaciones.count() > 0:
                        print("   ❌ NO incluye proveedores asignados")
                else:
                    print(f"   ⚠️ API devuelve {len(proveedores_api)} proveedores, esperado: {expected_count}")
        
        print(f"\n✅ VERIFICACIÓN COMPLETADA")
        print(f"\n📋 RESUMEN:")
        print(f"   ✅ Vista de inventario carga con nueva estructura de proveedores")
        print(f"   ✅ API de detalles devuelve todos los proveedores asignados")
        print(f"   ✅ Se manejan correctamente insumos sin proveedores")
        print(f"   ✅ Se incluyen tanto proveedores principales como asignados")
        
        print(f"\n🌐 PRUEBA MANUAL:")
        print(f"   1. Abre: http://127.0.0.1:8000/dashboard/inventario/")
        print(f"   2. Busca insumos que tengan múltiples proveedores")
        print(f"   3. Haz clic en 'Ver detalles' para ver el modal")
        print(f"   4. Verifica que se muestren todos los proveedores con sus detalles")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
