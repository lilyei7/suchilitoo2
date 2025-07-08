#!/usr/bin/env python
"""
Script para probar la unificación de proveedores en los detalles de insumos.
Verificará que el API devuelva tanto el proveedor principal como los asignados via ProveedorInsumo.
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
    print("🔍 PROBANDO UNIFICACIÓN DE PROVEEDORES EN API DE DETALLES")
    print("=" * 60)
    
    try:
        # Buscar un usuario admin para hacer las peticiones
        admin_user = Usuario.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = Usuario.objects.filter(rol__nombre='Administrador').first()
        
        if not admin_user:
            print("❌ No se encontró un usuario administrador")
            return
        
        print(f"✅ Usuario encontrado: {admin_user.username} ({admin_user.rol.nombre if admin_user.rol else 'Sin rol'})")
        
        # Crear cliente y hacer login
        client = Client()
        client.force_login(admin_user)
        
        # Buscar un insumo para probar
        insumo = Insumo.objects.first()
        if not insumo:
            print("❌ No se encontraron insumos en la base de datos")
            return
        
        print(f"\n📦 Insumo de prueba: {insumo.nombre} (ID: {insumo.id})")
        
        # Verificar estado actual del insumo
        print(f"   - Proveedor principal: {insumo.proveedor_principal.nombre if insumo.proveedor_principal else 'Ninguno'}")
        
        # Verificar relaciones ProveedorInsumo
        relaciones = ProveedorInsumo.objects.filter(insumo=insumo, activo=True)
        print(f"   - Relaciones ProveedorInsumo activas: {relaciones.count()}")
        
        for relacion in relaciones:
            print(f"     * {relacion.proveedor.nombre_comercial} - ${relacion.precio_final()}")
        
        # Hacer petición al API
        print(f"\n🌐 Llamando al API: /dashboard/insumos/{insumo.id}/detalle/")
        response = client.get(f'/dashboard/insumos/{insumo.id}/detalle/', 
                             HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        if response.status_code != 200:
            print(f"❌ Error en API: {response.status_code}")
            print(f"   Contenido: {response.content.decode()}")
            return
        
        data = response.json()
        print("✅ API respondió correctamente")
        
        # Verificar datos de proveedores en la respuesta
        print(f"\n📋 RESPUESTA DEL API:")
        print(f"   - Proveedor (compatibilidad): {data.get('proveedor', 'N/A')}")
        print(f"   - Lista de proveedores: {len(data.get('proveedores', []))} proveedores")
        
        if 'proveedores' in data:
            for i, prov in enumerate(data['proveedores'], 1):
                print(f"     {i}. {prov['nombre']} ({prov['tipo']})")
                print(f"        - Precio: ${prov['precio_unitario']}")
                print(f"        - Contacto: {prov['contacto'] or 'N/A'}")
                print(f"        - Teléfono: {prov['telefono'] or 'N/A'}")
                print(f"        - Email: {prov['email'] or 'N/A'}")
                if prov['tiempo_entrega']:
                    print(f"        - Tiempo entrega: {prov['tiempo_entrega']} días")
                if prov['cantidad_minima'] and prov['cantidad_minima'] != '1':
                    print(f"        - Cantidad mínima: {prov['cantidad_minima']}")
                if prov['notas']:
                    print(f"        - Notas: {prov['notas']}")
                print()
        else:
            print("❌ No se encontró la lista 'proveedores' en la respuesta")
        
        # Verificar que el API incluye ambos tipos de proveedores
        tiene_principal = insumo.proveedor_principal is not None
        tiene_relaciones = relaciones.count() > 0
        
        proveedores_en_api = data.get('proveedores', [])
        tipos_en_api = [p['tipo'] for p in proveedores_en_api]
        
        print(f"\n🔍 VERIFICACIÓN:")
        print(f"   - Insumo tiene proveedor principal: {tiene_principal}")
        print(f"   - Insumo tiene relaciones ProveedorInsumo: {tiene_relaciones}")
        print(f"   - API devuelve proveedores: {len(proveedores_en_api)}")
        print(f"   - Tipos en API: {tipos_en_api}")
        
        # Verificaciones
        if tiene_principal and 'principal' not in tipos_en_api:
            print("⚠️  ADVERTENCIA: Insumo tiene proveedor principal pero no aparece en API")
        
        if tiene_relaciones and 'asignado' not in tipos_en_api:
            print("⚠️  ADVERTENCIA: Insumo tiene relaciones ProveedorInsumo pero no aparecen en API")
        
        if len(proveedores_en_api) == 0 and (tiene_principal or tiene_relaciones):
            print("❌ ERROR: Insumo tiene proveedores pero API no devuelve ninguno")
        
        if len(proveedores_en_api) > 0 and not (tiene_principal or tiene_relaciones):
            print("❌ ERROR: API devuelve proveedores pero insumo no tiene ninguno asignado")
        
        if len(proveedores_en_api) > 0:
            print("✅ ÉXITO: API devuelve proveedores correctamente")
            
        # Test adicional: Si no hay proveedores, crear uno y asignarlo
        if len(proveedores_en_api) == 0:
            print(f"\n🔧 CREANDO PROVEEDOR DE PRUEBA...")
            try:
                proveedor_test = Proveedor.objects.create(
                    nombre_comercial="Proveedor Test Unificación",
                    persona_contacto="Juan Pérez",
                    telefono="555-1234",
                    email="test@proveedor.com",
                    creado_por=admin_user
                )
                
                # Crear relación ProveedorInsumo
                relacion_test = ProveedorInsumo.objects.create(
                    proveedor=proveedor_test,
                    insumo=insumo,
                    precio_unitario=15.50,
                    cantidad_minima=5,
                    tiempo_entrega_dias=3,
                    notas="Proveedor de prueba para verificar unificación"
                )
                
                print(f"✅ Proveedor creado y asignado: {proveedor_test.nombre_comercial}")
                
                # Hacer nueva petición al API
                response2 = client.get(f'/dashboard/insumos/{insumo.id}/detalle/', 
                                     HTTP_X_REQUESTED_WITH='XMLHttpRequest')
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    proveedores_nuevos = data2.get('proveedores', [])
                    print(f"✅ Nueva consulta API: {len(proveedores_nuevos)} proveedores")
                    
                    # Verificar que el proveedor test aparece
                    nombres_proveedores = [p['nombre'] for p in proveedores_nuevos]
                    if "Proveedor Test Unificación" in nombres_proveedores:
                        print("✅ ÉXITO: Proveedor test aparece en API")
                    else:
                        print("❌ ERROR: Proveedor test NO aparece en API")
                        print(f"   Proveedores en API: {nombres_proveedores}")
                
                # Limpiar: eliminar proveedor test
                relacion_test.delete()
                proveedor_test.delete()
                print("🧹 Proveedor test eliminado")
                
            except Exception as e:
                print(f"❌ Error creando proveedor test: {e}")
        
        print(f"\n✅ PRUEBA COMPLETADA")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
