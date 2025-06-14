#!/usr/bin/env python
"""
Script de verificación final para confirmar que el inventario se muestra correctamente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario, Sucursal
from restaurant.models import Insumo, Inventario, CategoriaInsumo

def main():
    print("🔍 === VERIFICACIÓN FINAL DEL INVENTARIO ===\n")
    
    # 1. Estado actual de la base de datos
    print("1️⃣ ESTADO ACTUAL DE LA BASE DE DATOS:")
    total_insumos = Insumo.objects.count()
    total_inventarios = Inventario.objects.count()
    total_sucursales = Sucursal.objects.filter(activa=True).count()
    
    print(f"   📊 Total de insumos: {total_insumos}")
    print(f"   📦 Total de inventarios: {total_inventarios}")
    print(f"   🏢 Total de sucursales activas: {total_sucursales}")
    print(f"   🔢 Inventarios esperados: {total_insumos * total_sucursales}")
    
    # 2. Últimos insumos creados
    print("\n2️⃣ ÚLTIMOS 10 INSUMOS CREADOS:")
    ultimos_insumos = Insumo.objects.order_by('-id')[:10]
    for i, insumo in enumerate(ultimos_insumos, 1):
        inventarios_count = Inventario.objects.filter(insumo=insumo).count()
        print(f"   {i:2d}. ID:{insumo.id:3d} | {insumo.nombre:25s} | Inventarios: {inventarios_count}")
        
        # Verificar si tiene inventarios en todas las sucursales
        for sucursal in Sucursal.objects.filter(activa=True):
            try:
                inventario = Inventario.objects.get(insumo=insumo, sucursal=sucursal)
                print(f"       ✅ {sucursal.nombre}: {inventario.cantidad_actual}")
            except Inventario.DoesNotExist:
                print(f"       ❌ {sucursal.nombre}: SIN INVENTARIO")
    
    # 3. Simular exactamente lo que ve el usuario jhayco
    print("\n3️⃣ SIMULACIÓN DE LA VISTA PARA USUARIO 'jhayco':")
    try:
        usuario = Usuario.objects.get(username='jhayco')
        sucursal = getattr(usuario, 'sucursal', None)
        
        print(f"   👤 Usuario: {usuario.username}")
        print(f"   🏢 Sucursal: {sucursal.nombre if sucursal else 'Sin asignar'}")
        
        # Simular la lógica de la vista
        if sucursal:
            inventarios = Inventario.objects.filter(sucursal=sucursal)
        else:
            inventarios = Inventario.objects.all()
        
        print(f"   📦 Total inventarios que debería ver: {inventarios.count()}")
        
        # Mostrar los primeros 5 y últimos 5
        print(f"   📋 Primeros 5 inventarios:")
        for i, inv in enumerate(inventarios[:5], 1):
            print(f"      {i}. {inv.insumo.nombre} ({inv.sucursal.nombre}): {inv.cantidad_actual}")
        
        if inventarios.count() > 5:
            print(f"   📋 Últimos 5 inventarios:")
            for i, inv in enumerate(inventarios.order_by('-id')[:5], 1):
                print(f"      {i}. {inv.insumo.nombre} ({inv.sucursal.nombre}): {inv.cantidad_actual}")
        
    except Usuario.DoesNotExist:
        print("   ❌ Usuario 'jhayco' no encontrado")
    
    # 4. Verificar insumos sin inventario
    print("\n4️⃣ VERIFICAR INSUMOS SIN INVENTARIO:")
    insumos_sin_inventario = []
    for insumo in Insumo.objects.all():
        if not Inventario.objects.filter(insumo=insumo).exists():
            insumos_sin_inventario.append(insumo)
    
    if insumos_sin_inventario:
        print(f"   ⚠️ Encontrados {len(insumos_sin_inventario)} insumos sin inventario:")
        for insumo in insumos_sin_inventario:
            print(f"      - {insumo.nombre} (ID: {insumo.id})")
    else:
        print("   ✅ Todos los insumos tienen inventario")
    
    # 5. Generar reporte final
    print("\n5️⃣ REPORTE FINAL:")
    inventarios_esperados = total_insumos * total_sucursales
    if total_inventarios == inventarios_esperados:
        print("   ✅ ESTADO: PERFECTO - Todos los insumos tienen inventario en todas las sucursales")
    else:
        print(f"   ⚠️ ESTADO: INCOMPLETO - Faltan {inventarios_esperados - total_inventarios} registros de inventario")
    
    print(f"\n🎯 === RESULTADO FINAL ===")
    print(f"📊 El usuario 'jhayco' debería ver {inventarios.count() if 'inventarios' in locals() else 'N/A'} inventarios en la página web")
    print(f"🔍 Si no los ve, el problema está en el frontend (JavaScript/Template)")
    print(f"\n✅ === VERIFICACIÓN COMPLETADA ===")

if __name__ == "__main__":
    main()
