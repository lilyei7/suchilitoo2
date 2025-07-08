#!/usr/bin/env python
"""
Script para verificar insumos sin inventario y crear registros de inventario
"""
import os
import sys

# Agregar el directorio del proyecto al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

import django
django.setup()

from restaurant.models import Insumo, Inventario
from accounts.models import Sucursal
from decimal import Decimal

def verificar_insumos_sin_inventario():
    print("🔍 VERIFICANDO INSUMOS SIN INVENTARIO")
    print("=" * 60)
    
    # Obtener todos los insumos activos
    insumos_totales = Insumo.objects.filter(activo=True).count()
    print(f"📦 Total de insumos activos: {insumos_totales}")
    
    # Obtener insumos que tienen inventario
    insumos_con_inventario = Inventario.objects.values_list('insumo_id', flat=True).distinct()
    insumos_con_inventario_count = len(set(insumos_con_inventario))
    print(f"✅ Insumos con inventario: {insumos_con_inventario_count}")
    
    # Obtener insumos sin inventario
    insumos_sin_inventario = Insumo.objects.filter(activo=True).exclude(id__in=insumos_con_inventario)
    insumos_sin_inventario_count = insumos_sin_inventario.count()
    print(f"❌ Insumos SIN inventario: {insumos_sin_inventario_count}")
    
    print("\n" + "=" * 60)
    
    if insumos_sin_inventario_count > 0:
        print("📋 INSUMOS SIN INVENTARIO:")
        for insumo in insumos_sin_inventario:
            print(f"   ID: {insumo.id} | {insumo.codigo} - {insumo.nombre}")
            print(f"      Categoría: {insumo.categoria.nombre if insumo.categoria else 'Sin categoría'}")
            print(f"      Tipo: {insumo.tipo}")
            print(f"      Fecha creación: {insumo.fecha_creacion}")
            print()
    
    return insumos_sin_inventario

def obtener_sucursales():
    """Obtener sucursales activas"""
    sucursales = Sucursal.objects.filter(activa=True)
    print(f"🏢 SUCURSALES ACTIVAS: {sucursales.count()}")
    for sucursal in sucursales:
        print(f"   ID: {sucursal.id} | {sucursal.nombre}")
    return sucursales

def crear_inventarios_para_insumos(insumos_sin_inventario, sucursales):
    """Crear registros de inventario para insumos que no los tienen"""
    if not insumos_sin_inventario:
        print("✅ Todos los insumos ya tienen inventario")
        return
    
    if not sucursales:
        print("❌ No hay sucursales activas para crear inventario")
        return
    
    print(f"\n🔧 CREANDO INVENTARIOS PARA {insumos_sin_inventario.count()} INSUMOS...")
    
    # Crear inventario en todas las sucursales para cada insumo
    inventarios_creados = 0
    
    for insumo in insumos_sin_inventario:
        print(f"\n📦 Procesando: {insumo.codigo} - {insumo.nombre}")
        
        for sucursal in sucursales:
            # Verificar si ya existe inventario para este insumo en esta sucursal
            inventario_existente = Inventario.objects.filter(
                insumo=insumo, 
                sucursal=sucursal            ).first()
            
            if not inventario_existente:
                # Crear nuevo registro de inventario
                inventario = Inventario.objects.create(
                    insumo=insumo,
                    sucursal=sucursal,
                    cantidad_actual=Decimal('0.00'),
                    cantidad_reservada=Decimal('0.00'),
                    costo_unitario=insumo.precio_unitario
                )
                inventarios_creados += 1
                print(f"   ✅ Inventario creado en {sucursal.nombre}")
            else:
                print(f"   ℹ️ Ya existe inventario en {sucursal.nombre}")
    
    print(f"\n🎉 COMPLETADO: Se crearon {inventarios_creados} registros de inventario")

def mostrar_resumen_final():
    """Mostrar resumen final después de crear inventarios"""
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL:")
    
    # Recalcular estadísticas
    insumos_totales = Insumo.objects.filter(activo=True).count()
    insumos_con_inventario = Inventario.objects.values_list('insumo_id', flat=True).distinct()
    insumos_con_inventario_count = len(set(insumos_con_inventario))
    
    print(f"   📦 Total de insumos activos: {insumos_totales}")
    print(f"   ✅ Insumos con inventario: {insumos_con_inventario_count}")
    print(f"   ❌ Insumos sin inventario: {insumos_totales - insumos_con_inventario_count}")
    
    # Mostrar últimos insumos creados
    ultimos_insumos = Insumo.objects.filter(activo=True).order_by('-fecha_creacion')[:5]
    print(f"\n📅 ÚLTIMOS INSUMOS CREADOS:")
    for insumo in ultimos_insumos:
        tiene_inventario = Inventario.objects.filter(insumo=insumo).exists()
        estado = "✅" if tiene_inventario else "❌"
        print(f"   {estado} {insumo.codigo} - {insumo.nombre} ({insumo.fecha_creacion})")

if __name__ == "__main__":
    print("🚀 INICIANDO VERIFICACIÓN DE INVENTARIOS\n")
    
    # Verificar estado actual
    insumos_sin_inventario = verificar_insumos_sin_inventario()
    
    # Obtener sucursales
    sucursales = obtener_sucursales()
    
    if insumos_sin_inventario.count() > 0:
        print(f"\n❓ ¿Desea crear registros de inventario para {insumos_sin_inventario.count()} insumos? (y/n)")
        respuesta = input().lower().strip()
        
        if respuesta in ['y', 'yes', 'sí', 'si', '1']:
            crear_inventarios_para_insumos(insumos_sin_inventario, sucursales)
        else:
            print("⚠️ No se crearon registros de inventario")
    
    # Mostrar resumen final
    mostrar_resumen_final()
    
    print("\n✅ Proceso completado")
