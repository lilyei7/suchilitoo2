#!/usr/bin/env python
"""
Script para diagnosticar específicamente por qué no aparecen los insumos 
en el listado del inventario.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Insumo, CategoriaInsumo, UnidadMedida, Inventario, MovimientoInventario
from accounts.models import Sucursal, Usuario

def main():
    print("🔍 === DIAGNÓSTICO ESPECÍFICO DEL INVENTARIO ===\n")
    
    # 1. Verificar insumos en la base de datos
    print("1️⃣ VERIFICANDO INSUMOS:")
    insumos = Insumo.objects.all()
    print(f"   📊 Total de insumos: {insumos.count()}")
    
    # 2. Verificar tabla de inventario (que es lo que muestra la página)
    print("\n2️⃣ VERIFICANDO TABLA INVENTARIO:")
    inventarios = Inventario.objects.all()
    print(f"   📊 Total de registros en inventario: {inventarios.count()}")
    
    if inventarios.exists():
        print("   📋 Registros de inventario encontrados:")
        for i, inv in enumerate(inventarios[:10], 1):
            print(f"   {i:2d}. Sucursal: {inv.sucursal.nombre:20s} | Insumo: {inv.insumo.nombre:30s} | Cantidad: {inv.cantidad_actual}")
    else:
        print("   ❌ NO HAY REGISTROS EN LA TABLA INVENTARIO")
        print("   🔍 Esto explica por qué no aparece nada en el listado!")
    
    # 3. Verificar sucursales
    print("\n3️⃣ VERIFICANDO SUCURSALES:")
    sucursales = Sucursal.objects.all()
    print(f"   📊 Total de sucursales: {sucursales.count()}")
    for sucursal in sucursales:
        inventarios_sucursal = Inventario.objects.filter(sucursal=sucursal).count()
        print(f"   🏢 {sucursal.nombre}: {inventarios_sucursal} insumos en inventario (Activa: {sucursal.activa})")
    
    # 4. Verificar últimos movimientos
    print("\n4️⃣ VERIFICANDO MOVIMIENTOS DE INVENTARIO:")
    movimientos = MovimientoInventario.objects.all().order_by('-created_at')
    print(f"   📊 Total de movimientos: {movimientos.count()}")
    
    if movimientos.exists():
        print("   📋 Últimos 5 movimientos:")
        for i, mov in enumerate(movimientos[:5], 1):
            print(f"   {i}. {mov.created_at.strftime('%Y-%m-%d %H:%M')} | {mov.tipo_movimiento:8s} | {mov.insumo.nombre:25s} | {mov.cantidad:8.2f} | {mov.sucursal.nombre}")
    
    # 5. Verificar insumos sin inventario
    print("\n5️⃣ IDENTIFICANDO INSUMOS SIN INVENTARIO:")
    insumos_sin_inventario = []
    for insumo in insumos:
        tiene_inventario = Inventario.objects.filter(insumo=insumo).exists()
        if not tiene_inventario:
            insumos_sin_inventario.append(insumo)
    
    print(f"   📊 Insumos sin inventario: {len(insumos_sin_inventario)}")
    if insumos_sin_inventario:
        print("   📋 Lista de insumos sin inventario:")
        for i, insumo in enumerate(insumos_sin_inventario[:10], 1):
            print(f"   {i:2d}. {insumo.codigo} - {insumo.nombre}")
    
    # 6. Diagnosticar la causa más probable
    print("\n6️⃣ DIAGNÓSTICO Y SOLUCIÓN:")
    if inventarios.count() == 0:
        print("   🎯 PROBLEMA IDENTIFICADO:")
        print("   ❌ No hay registros en la tabla 'Inventario'")
        print("   📝 La página del dashboard muestra los registros de 'Inventario', no de 'Insumo'")
        print("   🔧 SOLUCIÓN: Crear registros de inventario para los insumos existentes")
        
        print("\n   💡 OPCIONES DE SOLUCIÓN:")
        print("   1. Ejecutar script de corrección automática")
        print("   2. Crear manualmente inventarios desde el admin")
        print("   3. Usar la función de crear insumos desde el formulario web")
        
        respuesta = input("\n   ❓ ¿Deseas ejecutar la corrección automática? (s/n): ").lower()
        if respuesta == 's':
            print("\n🔧 === EJECUTANDO CORRECCIÓN AUTOMÁTICA ===")
            corregir_inventarios()
        else:
            print("   ℹ️  Corrección cancelada. Puedes ejecutar este script más tarde.")
    
    elif inventarios.count() < insumos.count():
        print("   ⚠️  PROBLEMA PARCIAL:")
        print(f"   📊 Hay {insumos.count()} insumos pero solo {inventarios.count()} inventarios")
        print("   🔧 Algunos insumos no tienen inventario asociado")
        
        respuesta = input("\n   ❓ ¿Deseas crear inventarios para los insumos faltantes? (s/n): ").lower()
        if respuesta == 's':
            print("\n🔧 === CREANDO INVENTARIOS FALTANTES ===")
            crear_inventarios_faltantes()
    else:
        print("   ✅ Los datos parecen estar correctos")
        print("   🤔 El problema podría estar en la vista o template")

def corregir_inventarios():
    """Crear inventarios para todos los insumos existentes"""
    try:
        sucursales_activas = Sucursal.objects.filter(activa=True)
        if not sucursales_activas.exists():
            print("   ❌ No hay sucursales activas")
            return
        
        insumos_sin_inventario = []
        for insumo in Insumo.objects.all():
            if not Inventario.objects.filter(insumo=insumo).exists():
                insumos_sin_inventario.append(insumo)
        
        print(f"   📊 Creando inventarios para {len(insumos_sin_inventario)} insumos...")
        
        total_creados = 0
        for insumo in insumos_sin_inventario:
            for sucursal in sucursales_activas:
                # Crear inventario con stock inicial de 0
                inventario = Inventario.objects.create(
                    sucursal=sucursal,
                    insumo=insumo,
                    cantidad_actual=0
                )
                total_creados += 1
                print(f"   ✅ Inventario creado: {sucursal.nombre} - {insumo.nombre}")
        
        print(f"\n   🎉 ¡CORRECCIÓN COMPLETADA!")
        print(f"   📊 Se crearon {total_creados} registros de inventario")
        print(f"   ✅ Ahora deberían aparecer {len(insumos_sin_inventario)} insumos en el listado")
        
    except Exception as e:
        print(f"   ❌ Error durante la corrección: {e}")

def crear_inventarios_faltantes():
    """Crear inventarios solo para insumos que no los tienen"""
    corregir_inventarios()

if __name__ == "__main__":
    main()
