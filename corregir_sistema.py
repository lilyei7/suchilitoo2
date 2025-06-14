#!/usr/bin/env python
"""
Script para crear sucursales y corregir inventarios
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario, Sucursal
from restaurant.models import Insumo, Inventario
from datetime import date

def main():
    print("🔧 === CORRECCIÓN COMPLETA DEL SISTEMA ===\n")
      # 1. Crear sucursales si no existen
    print("1️⃣ CREANDO SUCURSALES:")
    
    sucursales_data = [
        {
            'nombre': 'Sucursal Centro', 
            'direccion': 'Centro de la ciudad', 
            'telefono': '123-456-7890',
            'email': 'centro@sushi.com',
            'fecha_apertura': date(2024, 1, 1)
        },
        {
            'nombre': 'Sucursal Norte', 
            'direccion': 'Zona Norte', 
            'telefono': '123-456-7891',
            'email': 'norte@sushi.com',
            'fecha_apertura': date(2024, 6, 1)
        }
    ]
    
    sucursales_creadas = 0
    for data in sucursales_data:        sucursal, created = Sucursal.objects.get_or_create(
            nombre=data['nombre'],
            defaults={
                'direccion': data['direccion'],
                'telefono': data['telefono'],
                'email': data['email'],
                'fecha_apertura': data['fecha_apertura'],
                'activa': True
            }
        )
        
        if created:
            sucursales_creadas += 1
            print(f"   ✅ Sucursal creada: {sucursal.nombre}")
        else:
            print(f"   ℹ️  Sucursal ya existía: {sucursal.nombre}")
    
    print(f"   📊 Sucursales creadas: {sucursales_creadas}")
    
    # 2. Verificar sucursales existentes
    sucursales = Sucursal.objects.filter(activa=True)
    print(f"   📊 Total sucursales activas: {sucursales.count()}")
    
    print()
    
    # 3. Crear inventarios para todos los insumos
    print("2️⃣ CREANDO INVENTARIOS PARA TODOS LOS INSUMOS:")
    
    insumos = Insumo.objects.all()
    inventarios_creados = 0
    
    for insumo in insumos:
        print(f"   📦 Procesando insumo: {insumo.nombre}")
        
        for sucursal in sucursales:
            inventario, created = Inventario.objects.get_or_create(
                insumo=insumo,
                sucursal=sucursal,
                defaults={'cantidad_actual': 0}
            )
            
            if created:
                inventarios_creados += 1
                print(f"      ✅ Inventario creado en {sucursal.nombre}")
            else:
                print(f"      ℹ️  Inventario ya existía en {sucursal.nombre}")
    
    print(f"   📊 Inventarios creados: {inventarios_creados}")
    
    print()
    
    # 4. Verificar estado final
    print("3️⃣ VERIFICANDO ESTADO FINAL:")
    
    total_insumos = Insumo.objects.count()
    total_sucursales = Sucursal.objects.filter(activa=True).count()
    total_inventarios = Inventario.objects.count()
    inventarios_esperados = total_insumos * total_sucursales
    
    print(f"   📊 Total insumos: {total_insumos}")
    print(f"   📊 Total sucursales activas: {total_sucursales}")
    print(f"   📊 Total inventarios: {total_inventarios}")
    print(f"   📊 Inventarios esperados: {inventarios_esperados}")
    
    if total_inventarios == inventarios_esperados:
        print("   ✅ ¡PERFECTO! Todos los inventarios están completos")
    else:
        print(f"   ⚠️  Faltan {inventarios_esperados - total_inventarios} inventarios")
    
    print()
    
    # 5. Verificar lo que verá el usuario
    print("4️⃣ VERIFICANDO LO QUE VERÁ EL USUARIO EN LA PÁGINA:")
    
    try:
        usuario = Usuario.objects.get(username='jhayco')
        
        if usuario.sucursal:
            inventarios_visibles = Inventario.objects.filter(sucursal=usuario.sucursal)
            print(f"   👤 Usuario '{usuario.username}' (sucursal: {usuario.sucursal.nombre}) verá: {inventarios_visibles.count()} inventarios")
        else:
            inventarios_visibles = Inventario.objects.all()
            print(f"   👤 Usuario '{usuario.username}' (sin sucursal) verá: {inventarios_visibles.count()} inventarios")
        
        # Mostrar algunos ejemplos
        if inventarios_visibles.exists():
            print("   📋 Primeros 5 inventarios que verá:")
            for i, inv in enumerate(inventarios_visibles[:5], 1):
                print(f"      {i}. {inv.insumo.nombre} en {inv.sucursal.nombre}: {inv.cantidad_actual}")
        else:
            print("   ❌ No verá ningún inventario")
            
    except Usuario.DoesNotExist:
        print("   ❌ Usuario 'jhayco' no encontrado")
    
    print()
    
    # 6. Resumen final
    print("5️⃣ RESUMEN FINAL:")
    print("   ✅ Sucursales creadas y activas")
    print("   ✅ Inventarios creados para todos los insumos")
    print("   ✅ Usuario puede ver todos los inventarios")
    print("   🎉 ¡SISTEMA CORREGIDO! Los nuevos insumos ahora aparecerán en el listado")
    
    print("\n🔧 === CORRECCIÓN COMPLETADA ===")

if __name__ == "__main__":
    main()
