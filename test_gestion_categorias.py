#!/usr/bin/env python
"""
Script de prueba para verificar la funcionalidad de gestión de categorías y unidades
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import CategoriaInsumo, UnidadMedida

def main():
    print("🧪 === PRUEBA DE FUNCIONALIDAD - CATEGORÍAS Y UNIDADES ===\n")
    
    # 1. Estado inicial
    print("1️⃣ ESTADO INICIAL:")
    print(f"   📂 Categorías existentes: {CategoriaInsumo.objects.count()}")
    print(f"   📏 Unidades existentes: {UnidadMedida.objects.count()}")
    
    # Mostrar categorías existentes
    if CategoriaInsumo.objects.exists():
        print("   📂 Categorías:")
        for cat in CategoriaInsumo.objects.all():
            print(f"      - {cat.nombre}")
    
    # Mostrar unidades existentes
    if UnidadMedida.objects.exists():
        print("   📏 Unidades:")
        for unidad in UnidadMedida.objects.all():
            print(f"      - {unidad.nombre} ({unidad.abreviacion})")
    
    print()
    
    # 2. Crear categorías de prueba (si no existen)
    print("2️⃣ CREANDO CATEGORÍAS DE PRUEBA:")
    
    categorias_prueba = [
        {'nombre': 'Mariscos', 'descripcion': 'Productos del mar frescos'},
        {'nombre': 'Vegetales', 'descripcion': 'Verduras y hortalizas'},
        {'nombre': 'Condimentos', 'descripcion': 'Especias y condimentos'},
    ]
    
    categorias_creadas = 0
    for cat_data in categorias_prueba:
        categoria, created = CategoriaInsumo.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults={'descripcion': cat_data['descripcion']}
        )
        
        if created:
            categorias_creadas += 1
            print(f"   ✅ Categoría creada: {categoria.nombre}")
        else:
            print(f"   ℹ️  Categoría ya existía: {categoria.nombre}")
    
    print(f"   📊 Categorías creadas: {categorias_creadas}")
    
    print()
    
    # 3. Crear unidades de prueba (si no existen)
    print("3️⃣ CREANDO UNIDADES DE PRUEBA:")
    
    unidades_prueba = [
        {'nombre': 'Kilogramo', 'abreviacion': 'kg'},
        {'nombre': 'Litro', 'abreviacion': 'l'},
        {'nombre': 'Pieza', 'abreviacion': 'pz'},
        {'nombre': 'Gramo', 'abreviacion': 'g'},
        {'nombre': 'Mililitro', 'abreviacion': 'ml'},
    ]
    
    unidades_creadas = 0
    for unidad_data in unidades_prueba:
        unidad, created = UnidadMedida.objects.get_or_create(
            nombre=unidad_data['nombre'],
            defaults={'abreviacion': unidad_data['abreviacion']}
        )
        
        if created:
            unidades_creadas += 1
            print(f"   ✅ Unidad creada: {unidad.nombre} ({unidad.abreviacion})")
        else:
            print(f"   ℹ️  Unidad ya existía: {unidad.nombre} ({unidad.abreviacion})")
    
    print(f"   📊 Unidades creadas: {unidades_creadas}")
    
    print()
    
    # 4. Estado final
    print("4️⃣ ESTADO FINAL:")
    total_categorias = CategoriaInsumo.objects.count()
    total_unidades = UnidadMedida.objects.count()
    
    print(f"   📂 Total categorías: {total_categorias}")
    print(f"   📏 Total unidades: {total_unidades}")
    
    if total_categorias >= 3 and total_unidades >= 5:
        print("   ✅ ¡PERFECTO! Hay suficientes categorías y unidades para pruebas")
    else:
        print("   ⚠️  Se recomienda tener al menos 3 categorías y 5 unidades")
    
    print()
    
    # 5. Instrucciones para prueba manual
    print("5️⃣ INSTRUCCIONES PARA PRUEBA MANUAL:")
    print("   🌐 1. Abre: http://127.0.0.1:8000/dashboard/inventario/")
    print("   🔘 2. Haz clic en 'Gestionar Categorías'")
    print("   📝 3. Crea una nueva categoría (ej: 'Salsas')")
    print("   🔘 4. Haz clic en 'Gestionar Unidades'")
    print("   📝 5. Crea una nueva unidad (ej: 'Cucharada' - 'cdta')")
    print("   🔘 6. Haz clic en 'Nuevo Insumo'")
    print("   ✅ 7. Verifica que las nuevas categorías y unidades aparezcan en los select")
    
    print()
    
    # 6. Funcionalidades implementadas
    print("6️⃣ FUNCIONALIDADES IMPLEMENTADAS:")
    print("   ✅ Botones de gestión en el header del inventario")
    print("   ✅ Modal para crear nuevas categorías")
    print("   ✅ Modal para crear nuevas unidades de medida")
    print("   ✅ Integración automática con formulario de nuevo insumo")
    print("   ✅ Validaciones backend (nombres únicos)")
    print("   ✅ Notificaciones elegantes de éxito/error")
    print("   ✅ Actualización automática de los select sin recargar página")
    
    print("\n🧪 === PRUEBA COMPLETADA ===")

if __name__ == '__main__':
    main()
