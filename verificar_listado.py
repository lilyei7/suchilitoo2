#!/usr/bin/env python
"""
Script para verificar los insumos en la base de datos y diagnosticar
por qué no aparecen en el listado del inventario.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Insumo, CategoriaInsumo, UnidadMedida

def main():
    print("🔍 === DIAGNÓSTICO DEL LISTADO DE INVENTARIO ===\n")
    
    # 1. Verificar insumos en la base de datos
    print("1️⃣ VERIFICANDO INSUMOS EN LA BASE DE DATOS:")
    insumos = Insumo.objects.all()
    print(f"   📊 Total de insumos: {insumos.count()}")
    
    if insumos.exists():
        print("   📋 Listado de insumos encontrados:")
        for i, insumo in enumerate(insumos[:10], 1):  # Mostrar solo los primeros 10
            print(f"   {i:2d}. ID: {insumo.id:3d} | Nombre: {insumo.nombre:30s} | Tipo: {insumo.tipo:10s} | Categoría: {insumo.categoria.nombre if insumo.categoria else 'N/A'}")
    else:
        print("   ❌ No se encontraron insumos en la base de datos")
        return
    
    print()
      # 2. Verificar insumos básicos específicamente
    print("2️⃣ VERIFICANDO INSUMOS BÁSICOS:")
    insumos_basicos = Insumo.objects.filter(tipo='basico')
    print(f"   📊 Total de insumos básicos: {insumos_basicos.count()}")
    if insumos_basicos.exists():
        print("   📋 Insumos básicos encontrados:")
        for i, insumo in enumerate(insumos_basicos[:5], 1):
            # Solo mostrar información básica del insumo
            print(f"   {i}. {insumo.nombre} - Unidad: {insumo.unidad_medida.abreviacion if insumo.unidad_medida else 'N/A'}")
    
    print()
    
    # 3. Verificar los últimos insumos creados
    print("3️⃣ VERIFICANDO ÚLTIMOS INSUMOS CREADOS:")
    ultimos_insumos = Insumo.objects.order_by('-id')[:5]
    print(f"   📊 Últimos 5 insumos creados:")
    for i, insumo in enumerate(ultimos_insumos, 1):
        print(f"   {i}. ID: {insumo.id} | {insumo.nombre} | Creado: {insumo.id}")
    
    print()
    
    # 4. Verificar categorías
    print("4️⃣ VERIFICANDO CATEGORÍAS:")
    categorias = CategoriaInsumo.objects.all()
    print(f"   📊 Total de categorías: {categorias.count()}")
    for categoria in categorias:
        insumos_en_categoria = Insumo.objects.filter(categoria=categoria).count()
        print(f"   📁 {categoria.nombre}: {insumos_en_categoria} insumos")
    
    print()
    
    # 5. Verificar unidades de medida
    print("5️⃣ VERIFICANDO UNIDADES DE MEDIDA:")
    unidades = UnidadMedida.objects.all()
    print(f"   📊 Total de unidades: {unidades.count()}")
    for unidad in unidades:
        insumos_con_unidad = Insumo.objects.filter(unidad_medida=unidad).count()
        print(f"   📏 {unidad.nombre} ({unidad.abreviacion}): {insumos_con_unidad} insumos")
    
    print()
    
    # 6. Verificar si hay problemas con los campos
    print("6️⃣ VERIFICANDO INTEGRIDAD DE DATOS:")
    insumos_sin_categoria = Insumo.objects.filter(categoria__isnull=True).count()
    insumos_sin_unidad = Insumo.objects.filter(unidad_medida__isnull=True).count()
    insumos_sin_nombre = Insumo.objects.filter(nombre__isnull=True).count()
    
    print(f"   ⚠️  Insumos sin categoría: {insumos_sin_categoria}")
    print(f"   ⚠️  Insumos sin unidad de medida: {insumos_sin_unidad}")
    print(f"   ⚠️  Insumos sin nombre: {insumos_sin_nombre}")
    
    if insumos_sin_categoria > 0 or insumos_sin_unidad > 0 or insumos_sin_nombre > 0:
        print("   ❌ Se encontraron problemas de integridad de datos")
    else:
        print("   ✅ Integridad de datos correcta")
    
    print("\n🔍 === FIN DEL DIAGNÓSTICO ===")

if __name__ == "__main__":
    main()
