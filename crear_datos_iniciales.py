#!/usr/bin/env python
"""
Script para crear datos iniciales del sistema de insumos
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import CategoriaInsumo, UnidadMedida, Insumo

def crear_categorias_insumos():
    """Crear categorías de insumos básicas"""
    categorias = [
        {'nombre': 'Pescados y Mariscos', 'descripcion': 'Pescados frescos, mariscos y productos del mar'},
        {'nombre': 'Vegetales', 'descripcion': 'Verduras frescas y hortalizas'},
        {'nombre': 'Condimentos y Especias', 'descripcion': 'Condimentos, especias y sazonadores'},
        {'nombre': 'Salsas', 'descripcion': 'Salsas preparadas y aderezos'},
        {'nombre': 'Cereales y Granos', 'descripcion': 'Arroz, quinoa y otros cereales'},
        {'nombre': 'Lácteos', 'descripcion': 'Productos lácteos y derivados'},
        {'nombre': 'Aceites y Vinagres', 'descripcion': 'Aceites de cocina y vinagres'},
        {'nombre': 'Empaques', 'descripcion': 'Materiales de empaque y presentación'},
        {'nombre': 'Utensilios', 'descripcion': 'Utensilios de cocina desechables'},
    ]
    
    for cat_data in categorias:
        categoria, created = CategoriaInsumo.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults={'descripcion': cat_data['descripcion']}
        )
        if created:
            print(f"✓ Categoría creada: {categoria.nombre}")
        else:
            print(f"- Categoría ya existe: {categoria.nombre}")

def crear_unidades_medida():
    """Crear unidades de medida básicas"""
    unidades = [
        {'nombre': 'Kilogramo', 'abreviacion': 'kg'},
        {'nombre': 'Gramo', 'abreviacion': 'g'},
        {'nombre': 'Litro', 'abreviacion': 'l'},
        {'nombre': 'Mililitro', 'abreviacion': 'ml'},
        {'nombre': 'Unidad', 'abreviacion': 'un'},
        {'nombre': 'Pieza', 'abreviacion': 'pz'},
        {'nombre': 'Paquete', 'abreviacion': 'paq'},
        {'nombre': 'Caja', 'abreviacion': 'caja'},
        {'nombre': 'Bolsa', 'abreviacion': 'bolsa'},
        {'nombre': 'Lata', 'abreviacion': 'lata'},
    ]
    
    for unidad_data in unidades:
        unidad, created = UnidadMedida.objects.get_or_create(
            nombre=unidad_data['nombre'],
            defaults={'abreviacion': unidad_data['abreviacion']}
        )
        if created:
            print(f"✓ Unidad de medida creada: {unidad.nombre} ({unidad.abreviacion})")
        else:
            print(f"- Unidad de medida ya existe: {unidad.nombre} ({unidad.abreviacion})")

def crear_insumos_ejemplo():
    """Crear algunos insumos de ejemplo"""
    try:
        categoria_pescados = CategoriaInsumo.objects.get(nombre='Pescados y Mariscos')
        categoria_vegetales = CategoriaInsumo.objects.get(nombre='Vegetales')
        categoria_condimentos = CategoriaInsumo.objects.get(nombre='Condimentos y Especias')
        categoria_cereales = CategoriaInsumo.objects.get(nombre='Cereales y Granos')
        
        unidad_kg = UnidadMedida.objects.get(abreviacion='kg')
        unidad_g = UnidadMedida.objects.get(abreviacion='g')
        unidad_un = UnidadMedida.objects.get(abreviacion='un')
        unidad_paq = UnidadMedida.objects.get(abreviacion='paq')
        
        insumos_ejemplo = [
            {
                'codigo': 'SALMON001',
                'nombre': 'Salmón Fresco',
                'categoria': categoria_pescados,
                'unidad_medida': unidad_kg,
                'tipo': 'basico',
                'precio_unitario': 25000,
                'stock_minimo': 2
            },
            {
                'codigo': 'ATUN001',
                'nombre': 'Atún Rojo',
                'categoria': categoria_pescados,
                'unidad_medida': unidad_kg,
                'tipo': 'basico',
                'precio_unitario': 35000,
                'stock_minimo': 1
            },
            {
                'codigo': 'AGUAC001',
                'nombre': 'Aguacate Hass',
                'categoria': categoria_vegetales,
                'unidad_medida': unidad_un,
                'tipo': 'basico',
                'precio_unitario': 2500,
                'stock_minimo': 10
            },
            {
                'codigo': 'ARROZ001',
                'nombre': 'Arroz para Sushi',
                'categoria': categoria_cereales,
                'unidad_medida': unidad_kg,
                'tipo': 'basico',
                'precio_unitario': 8000,
                'stock_minimo': 5
            },
            {
                'codigo': 'NORI001',
                'nombre': 'Alga Nori',
                'categoria': categoria_condimentos,
                'unidad_medida': unidad_paq,
                'tipo': 'basico',
                'precio_unitario': 12000,
                'stock_minimo': 3
            },
            {
                'codigo': 'WASAB001',
                'nombre': 'Wasabi en Polvo',
                'categoria': categoria_condimentos,
                'unidad_medida': unidad_g,
                'tipo': 'basico',
                'precio_unitario': 150,
                'stock_minimo': 100
            }
        ]
        
        for insumo_data in insumos_ejemplo:
            insumo, created = Insumo.objects.get_or_create(
                codigo=insumo_data['codigo'],
                defaults=insumo_data
            )
            if created:
                print(f"✓ Insumo creado: {insumo.nombre} ({insumo.codigo})")
            else:
                print(f"- Insumo ya existe: {insumo.nombre} ({insumo.codigo})")
                
    except Exception as e:
        print(f"Error al crear insumos de ejemplo: {e}")

def main():
    print("=== Creando datos iniciales del sistema ===")
    print("\n1. Creando categorías de insumos...")
    crear_categorias_insumos()
    
    print("\n2. Creando unidades de medida...")
    crear_unidades_medida()
    
    print("\n3. Creando insumos de ejemplo...")
    crear_insumos_ejemplo()
    
    print("\n✅ ¡Datos iniciales creados exitosamente!")
    print("\nPuedes acceder al sistema y comenzar a gestionar insumos.")

if __name__ == '__main__':
    main()
