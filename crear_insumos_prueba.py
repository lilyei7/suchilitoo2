#!/usr/bin/env python
"""
Script para crear insumos de prueba para probar el sistema de recetas
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import (
    Insumo, CategoriaInsumo, UnidadMedida, InsumoElaborado, InsumoCompuesto
)
from decimal import Decimal

def crear_insumos_prueba():
    print("🔧 Creando insumos de prueba...")
    
    # Crear categorías si no existen
    cat_pescado, _ = CategoriaInsumo.objects.get_or_create(
        nombre="Pescado",
        defaults={'descripcion': 'Pescados y mariscos frescos'}
    )
    
    cat_arroz, _ = CategoriaInsumo.objects.get_or_create(
        nombre="Cereales",
        defaults={'descripcion': 'Arroz y cereales'}
    )
    
    cat_vegetales, _ = CategoriaInsumo.objects.get_or_create(
        nombre="Vegetales",
        defaults={'descripcion': 'Vegetales y verduras'}
    )
    
    # Crear unidades de medida si no existen
    kg, _ = UnidadMedida.objects.get_or_create(
        nombre="Kilogramo",
        defaults={'abreviacion': 'kg'}
    )
    
    unidad, _ = UnidadMedida.objects.get_or_create(
        nombre="Unidad",
        defaults={'abreviacion': 'und'}
    )
    
    litro, _ = UnidadMedida.objects.get_or_create(
        nombre="Litro",
        defaults={'abreviacion': 'L'}
    )
      # Crear insumos básicos
    insumos_basicos = [
        {
            'codigo': 'SALMON-001',
            'nombre': 'Salmón fresco',
            'categoria': cat_pescado,
            'unidad_medida': kg,
            'precio_unitario': Decimal('45.00'),
            'stock_minimo': Decimal('1.0'),
        },
        {
            'codigo': 'ATUN-001',
            'nombre': 'Atún fresco',
            'categoria': cat_pescado,
            'unidad_medida': kg,
            'precio_unitario': Decimal('50.00'),
            'stock_minimo': Decimal('1.0'),
        },
        {
            'codigo': 'ARROZ-001',
            'nombre': 'Arroz para sushi',
            'categoria': cat_arroz,
            'unidad_medida': kg,
            'precio_unitario': Decimal('8.00'),
            'stock_minimo': Decimal('5.0'),
        },
        {
            'codigo': 'NORI-001',
            'nombre': 'Alga Nori',
            'categoria': cat_vegetales,
            'unidad_medida': unidad,
            'precio_unitario': Decimal('0.50'),
            'stock_minimo': Decimal('20.0'),
        },
        {
            'codigo': 'PEPINO-001',
            'nombre': 'Pepino',
            'categoria': cat_vegetales,
            'unidad_medida': unidad,
            'precio_unitario': Decimal('1.50'),
            'stock_minimo': Decimal('10.0'),
        },
        {
            'codigo': 'AGUACATE-001',
            'nombre': 'Aguacate',
            'categoria': cat_vegetales,
            'unidad_medida': unidad,
            'precio_unitario': Decimal('2.00'),
            'stock_minimo': Decimal('10.0'),
        },
    ]
    
    for insumo_data in insumos_basicos:
        insumo, created = Insumo.objects.get_or_create(
            codigo=insumo_data['codigo'],
            defaults={
                **insumo_data,
                'tipo': 'basico',
                'activo': True
            }
        )
        if created:
            print(f"✅ Insumo básico creado: {insumo.nombre}")
        else:
            print(f"⚠️  Insumo básico ya existe: {insumo.nombre}")
      # Crear algunos insumos compuestos
    arroz_sushi, created = Insumo.objects.get_or_create(
        codigo='ARROZ-SUSHI-001',
        defaults={
            'nombre': 'Arroz para sushi preparado',
            'categoria': cat_arroz,
            'tipo': 'compuesto',
            'unidad_medida': kg,
            'precio_unitario': Decimal('12.00'),
            'stock_minimo': Decimal('2.0'),
            'activo': True
        }
    )
    if created:
        print(f"✅ Insumo compuesto creado: {arroz_sushi.nombre}")
        
        # Crear componentes del arroz para sushi
        arroz_base = Insumo.objects.get(codigo='ARROZ-001')
        InsumoCompuesto.objects.get_or_create(
            insumo_compuesto=arroz_sushi,
            insumo_componente=arroz_base,
            defaults={
                'cantidad': Decimal('1.0'),
                'orden': 1
            }
        )
      # Crear algunos insumos elaborados
    salmon_especial, created = Insumo.objects.get_or_create(
        codigo='SALMON-ESP-001',
        defaults={
            'nombre': 'Salmón especial marinado',
            'categoria': cat_pescado,
            'tipo': 'elaborado',
            'unidad_medida': kg,
            'precio_unitario': Decimal('60.00'),
            'stock_minimo': Decimal('0.5'),
            'activo': True
        }
    )
    if created:
        print(f"✅ Insumo elaborado creado: {salmon_especial.nombre}")
        
        # Crear componentes del salmón especial
        salmon_base = Insumo.objects.get(codigo='SALMON-001')
        InsumoElaborado.objects.get_or_create(
            insumo_elaborado=salmon_especial,
            insumo_componente=salmon_base,
            defaults={
                'cantidad': Decimal('1.0'),
                'tiempo_preparacion_minutos': 30,
                'instrucciones': 'Marinar el salmón por 30 minutos',
                'orden': 1
            }
        )
    
    print("\n🎉 ¡Insumos de prueba creados exitosamente!")
    print("\nInsumos disponibles:")
    
    basicos = Insumo.objects.filter(tipo='basico', activo=True).count()
    compuestos = Insumo.objects.filter(tipo='compuesto', activo=True).count()
    elaborados = Insumo.objects.filter(tipo='elaborado', activo=True).count()
    
    print(f"- Básicos: {basicos}")
    print(f"- Compuestos: {compuestos}")
    print(f"- Elaborados: {elaborados}")
    print(f"- Total: {basicos + compuestos + elaborados}")

if __name__ == '__main__':
    crear_insumos_prueba()
