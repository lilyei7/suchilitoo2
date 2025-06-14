#!/usr/bin/env python3
"""
Script para diagnosticar completamente el problema de FOREIGN KEY constraint
al asignar insumos a proveedores.
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.db import transaction, connection
from restaurant.models import Insumo, CategoriaInsumo, UnidadMedida
from dashboard.models import Proveedor, ProveedorInsumo
from django.contrib.auth import get_user_model

User = get_user_model()

def print_separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_database_integrity():
    """Verifica la integridad de la base de datos"""
    print_separator("VERIFICACIÓN DE INTEGRIDAD DE LA BASE DE DATOS")
    
    # Verificar tablas principales
    print("📊 Conteo de registros:")
    print(f"   Insumos: {Insumo.objects.count()}")
    print(f"   Proveedores: {Proveedor.objects.count()}")
    print(f"   ProveedorInsumo: {ProveedorInsumo.objects.count()}")
    print(f"   CategoriaInsumo: {CategoriaInsumo.objects.count()}")
    print(f"   UnidadMedida: {UnidadMedida.objects.count()}")
    
    # Verificar estructura de tablas
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(restaurant_insumo);")
        insumo_columns = cursor.fetchall()
        print(f"\n📋 Estructura tabla restaurant_insumo:")
        for col in insumo_columns:
            print(f"   {col[1]} ({col[2]}) - PK: {bool(col[5])} - NotNull: {bool(col[3])}")
        
        cursor.execute("PRAGMA table_info(dashboard_proveedorinsumo);")
        proveedor_insumo_columns = cursor.fetchall()
        print(f"\n📋 Estructura tabla dashboard_proveedorinsumo:")
        for col in proveedor_insumo_columns:
            print(f"   {col[1]} ({col[2]}) - PK: {bool(col[5])} - NotNull: {bool(col[3])}")
        
        # Verificar claves foráneas
        cursor.execute("PRAGMA foreign_key_list(dashboard_proveedorinsumo);")
        foreign_keys = cursor.fetchall()
        print(f"\n🔗 Claves foráneas en dashboard_proveedorinsumo:")
        for fk in foreign_keys:
            print(f"   {fk[3]} -> {fk[2]}.{fk[4]}")

def test_create_sample_data():
    """Crea datos de prueba si no existen"""
    print_separator("CREACIÓN DE DATOS DE PRUEBA")
    
    # Crear o obtener categoría
    categoria, created = CategoriaInsumo.objects.get_or_create(
        nombre="Pescados y Mariscos",
        defaults={'descripcion': 'Ingredientes principales para sushi'}
    )
    print(f"{'✅ Creada' if created else '📋 Existe'} categoría: {categoria.nombre}")
      # Crear o obtener unidad de medida
    unidad, created = UnidadMedida.objects.get_or_create(
        nombre="kg",
        defaults={'abreviacion': 'kg'}
    )
    print(f"{'✅ Creada' if created else '📋 Existe'} unidad: {unidad.nombre}")
      # Crear o obtener insumo
    insumo, created = Insumo.objects.get_or_create(
        nombre="Salmón Fresco TEST",
        defaults={
            'codigo': 'SAL-TEST-001',
            'tipo': 'basico',
            'categoria': categoria,
            'unidad_medida': unidad,
            'precio_unitario': 25.50,
            'stock_minimo': 2.0,
            'perecedero': True,
            'activo': True
        }
    )
    print(f"{'✅ Creado' if created else '📋 Existe'} insumo: {insumo.nombre} (ID: {insumo.id})")
      # Crear o obtener proveedor
    proveedor, created = Proveedor.objects.get_or_create(
        nombre_comercial="Mariscos Pacífico TEST",
        defaults={
            'razon_social': 'Mariscos Pacífico S.A.',
            'rfc': '12345678-9',
            'email': 'contacto@mariscospacifico.com',
            'telefono': '+56912345678',
            'direccion': 'Puerto Montt, Chile',
            'estado': 'activo'
        }
    )
    print(f"{'✅ Creado' if created else '📋 Existe'} proveedor: {proveedor.nombre_comercial} (ID: {proveedor.id})")
    
    return insumo, proveedor

def test_direct_orm_assignment(insumo, proveedor):
    """Prueba asignar insumo a proveedor directamente con ORM"""
    print_separator("PRUEBA DIRECTA CON ORM")
    
    try:
        # Primero limpiar cualquier relación existente
        existing = ProveedorInsumo.objects.filter(proveedor=proveedor, insumo=insumo)
        if existing.exists():
            print(f"🧹 Eliminando relación existente...")
            existing.delete()
        
        # Crear nueva relación
        print(f"🔗 Creando relación ORM directa:")
        print(f"   Proveedor: {proveedor.id} - {proveedor.nombre_comercial}")
        print(f"   Insumo: {insumo.id} - {insumo.nombre}")
        
        with transaction.atomic():
            proveedor_insumo = ProveedorInsumo.objects.create(
                proveedor=proveedor,
                insumo=insumo,
                precio_unitario=25.50,
                cantidad_minima=1.0,
                tiempo_entrega_dias=2,
                notas="Prueba de asignación directa",
                activo=True
            )
            
        print(f"✅ Relación creada exitosamente:")
        print(f"   ID: {proveedor_insumo.id}")
        print(f"   Precio: ${proveedor_insumo.precio_unitario}")
        print(f"   Precio final: ${proveedor_insumo.precio_final()}")
        
        return proveedor_insumo
        
    except Exception as e:
        print(f"❌ Error al crear relación ORM: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return None

def test_simulate_view_call(insumo, proveedor):
    """Simula la llamada desde la vista"""
    print_separator("SIMULACIÓN DE LLAMADA DESDE VISTA")
    
    from django.test import RequestFactory
    from django.contrib.auth.models import AnonymousUser
    from dashboard.views import asignar_insumo_proveedor
    import json
    
    try:
        factory = RequestFactory()
        
        # Crear request POST simulado
        post_data = {
            'insumo_id': str(insumo.id),
            'precio_unitario': '25.50',
            'cantidad_minima': '1',
            'tiempo_entrega_dias': '2',
            'observaciones': 'Prueba desde simulación de vista'
        }
        
        print(f"📤 Datos POST simulados:")
        for key, value in post_data.items():
            print(f"   {key}: {value}")
        
        request = factory.post(f'/proveedores/{proveedor.id}/asignar_insumo/', post_data)
        request.user = AnonymousUser()  # Para simplificar, sin autenticación
        
        # Llamar a la vista
        print(f"🔄 Llamando a asignar_insumo_proveedor({proveedor.id})...")
        response = asignar_insumo_proveedor(request, proveedor.id)
        
        # Analizar respuesta
        response_data = json.loads(response.content.decode('utf-8'))
        print(f"📥 Respuesta de la vista:")
        print(f"   Status: {response.status_code}")
        print(f"   Success: {response_data.get('success')}")
        print(f"   Message: {response_data.get('message')}")
        
        if response_data.get('success'):
            print(f"✅ Vista funcionó correctamente")
            return True
        else:
            print(f"❌ Vista falló: {response_data.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Error en simulación de vista: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_check_constraints():
    """Verifica las constraints de la base de datos"""
    print_separator("VERIFICACIÓN DE CONSTRAINTS")
    
    with connection.cursor() as cursor:
        # Verificar que foreign keys están habilitadas
        cursor.execute("PRAGMA foreign_keys;")
        fk_enabled = cursor.fetchone()[0]
        print(f"🔐 Foreign Keys habilitadas: {'✅ Sí' if fk_enabled else '❌ No'}")
        
        # Verificar integridad de la base de datos
        cursor.execute("PRAGMA integrity_check;")
        integrity = cursor.fetchall()
        print(f"🔍 Integridad de BD: {integrity[0][0] if integrity else 'Sin datos'}")
        
        # Verificar foreign key check
        cursor.execute("PRAGMA foreign_key_check;")
        fk_check = cursor.fetchall()
        if fk_check:
            print(f"⚠️ Problemas de FK encontrados:")
            for issue in fk_check:
                print(f"   {issue}")
        else:
            print(f"✅ No se encontraron problemas de Foreign Keys")

def main():
    """Función principal"""
    print("🔍 DIAGNÓSTICO COMPLETO DE FOREIGN KEY CONSTRAINT")
    
    try:
        # 1. Verificar integridad
        test_check_constraints()
        test_database_integrity()
        
        # 2. Crear datos de prueba
        insumo, proveedor = test_create_sample_data()
        
        # 3. Probar asignación directa con ORM
        proveedor_insumo = test_direct_orm_assignment(insumo, proveedor)
        
        if proveedor_insumo:
            print(f"\n✅ ORM funciona correctamente, ahora probando vista...")
            
            # Limpiar para probar vista
            proveedor_insumo.delete()
            
            # 4. Probar simulación de vista
            vista_ok = test_simulate_view_call(insumo, proveedor)
            
            if vista_ok:
                print(f"\n🎉 DIAGNÓSTICO COMPLETO: Todo funciona correctamente!")
            else:
                print(f"\n❌ PROBLEMA ENCONTRADO: La vista tiene errores")
        else:
            print(f"\n❌ PROBLEMA CRÍTICO: El ORM básico no funciona")
            
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO en main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
