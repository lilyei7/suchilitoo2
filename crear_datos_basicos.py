#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para crear datos básicos de categorías y unidades si no existen
"""

import os
import sys
import django

# Configurar Django
sys.path.append(r'c:\Users\olcha\Desktop\sushi_restaurant')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import CategoriaInsumo, UnidadMedida

def crear_categorias_basicas():
    """Crear categorías básicas si no existen"""
    categorias_basicas = [
        ('Proteínas', 'Carnes, pescados y mariscos'),
        ('Vegetales', 'Verduras y hortalizas frescas'),
        ('Granos y Cereales', 'Arroz, quinoa y otros granos'),
        ('Condimentos', 'Especias, salsas y condimentos'),
        ('Lácteos', 'Leche, quesos y derivados lácteos'),
        ('Aceites y Grasas', 'Aceites para cocinar y mantequillas'),
        ('Bebidas', 'Bebidas y líquidos'),
        ('Empaques', 'Materiales de empaque y presentación'),
    ]
    
    print("📦 Creando categorías básicas...")
    categorias_creadas = 0
    
    for nombre, descripcion in categorias_basicas:
        categoria, created = CategoriaInsumo.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': descripcion}
        )
        if created:
            categorias_creadas += 1
            print(f"   ✅ Categoría creada: {nombre}")
        else:
            print(f"   ℹ️  Categoría ya existe: {nombre}")
    
    print(f"📊 Total categorías creadas: {categorias_creadas}")
    return categorias_creadas

def crear_unidades_basicas():
    """Crear unidades de medida básicas si no existen"""
    unidades_basicas = [
        ('Kilogramo', 'kg'),
        ('Gramo', 'g'),
        ('Litro', 'L'),
        ('Mililitro', 'ml'),
        ('Unidad', 'und'),
        ('Paquete', 'paq'),
        ('Botella', 'bot'),
        ('Lata', 'lata'),
        ('Caja', 'caja'),
        ('Metro', 'm'),
        ('Libra', 'lb'),
        ('Onza', 'oz'),
    ]
    
    print("\n📏 Creando unidades de medida básicas...")
    unidades_creadas = 0
    
    for nombre, abreviacion in unidades_basicas:
        unidad, created = UnidadMedida.objects.get_or_create(
            nombre=nombre,
            defaults={
                'abreviacion': abreviacion
            }
        )
        if created:
            unidades_creadas += 1
            print(f"   ✅ Unidad creada: {nombre} ({abreviacion})")
        else:
            print(f"   ℹ️  Unidad ya existe: {nombre} ({abreviacion})")
    
    print(f"📊 Total unidades creadas: {unidades_creadas}")
    return unidades_creadas

def verificar_datos():
    """Verificar que los datos estén creados correctamente"""
    print("\n🔍 Verificando datos en la base de datos...")
    
    # Contar categorías
    total_categorias = CategoriaInsumo.objects.count()
    print(f"📦 Total categorías en BD: {total_categorias}")
    
    if total_categorias > 0:
        print("✅ Categorías disponibles:")
        for cat in CategoriaInsumo.objects.all()[:5]:
            print(f"   • {cat.nombre}")
        if total_categorias > 5:
            print(f"   • ... y {total_categorias - 5} más")
    
    # Contar unidades
    total_unidades = UnidadMedida.objects.count()
    print(f"\n📏 Total unidades en BD: {total_unidades}")
    
    if total_unidades > 0:
        print("✅ Unidades disponibles:")
        for unidad in UnidadMedida.objects.all()[:5]:
            print(f"   • {unidad.nombre} ({unidad.abreviacion})")
        if total_unidades > 5:
            print(f"   • ... y {total_unidades - 5} más")
    
    return total_categorias > 0 and total_unidades > 0

def main():
    """Función principal"""
    print("🚀 CREACIÓN DE DATOS BÁSICOS PARA FORMULARIOS")
    print("=" * 50)
    
    try:
        # Crear categorías
        cat_creadas = crear_categorias_basicas()
        
        # Crear unidades
        unid_creadas = crear_unidades_basicas()
        
        # Verificar datos
        datos_ok = verificar_datos()
        
        print("\n" + "=" * 50)
        print("📊 RESUMEN:")
        print(f"✅ Categorías creadas: {cat_creadas}")
        print(f"✅ Unidades creadas: {unid_creadas}")
        
        if datos_ok:
            print("\n🎉 ¡ÉXITO! Los datos básicos han sido creados")
            print("✅ Los selects de categorías y unidades ahora deberían funcionar")
            print("\n💡 Próximo paso:")
            print("   1. Recarga la página del inventario")
            print("   2. Abre el modal 'Nuevo Insumo'")
            print("   3. Verifica que los selects tengan opciones")
        else:
            print("\n⚠️  PROBLEMA: No se pudieron verificar los datos")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("💡 Asegúrate de que el servidor Django esté corriendo")

if __name__ == "__main__":
    main()
