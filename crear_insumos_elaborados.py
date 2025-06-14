#!/usr/bin/env python
"""Script para crear insumos elaborados de ejemplo"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import (
    Insumo, CategoriaInsumo, UnidadMedida, Receta, RecetaInsumo
)

def crear_insumos_elaborados():
    print("Creando insumos elaborados de ejemplo...")
    
    # Obtener categorías y unidades existentes
    try:
        salsas_cat = CategoriaInsumo.objects.get(nombre='Salsas')
    except CategoriaInsumo.DoesNotExist:
        salsas_cat = CategoriaInsumo.objects.create(
            nombre='Salsas',
            descripcion='Salsas y aderezos preparados'
        )
    
    try:
        elaborados_cat = CategoriaInsumo.objects.create(
            nombre='Preparaciones Elaboradas',
            descripcion='Insumos que requieren preparación especial'
        )
    except:
        elaborados_cat = CategoriaInsumo.objects.get(nombre='Preparaciones Elaboradas')
    
    ml = UnidadMedida.objects.get(nombre='Mililitro')
    g = UnidadMedida.objects.get(nombre='Gramo')
    porcion = UnidadMedida.objects.get(nombre='Porción')
    
    # Crear insumos elaborados
    insumos_elaborados_data = [
        ('SALSA001', 'Salsa de Soja Especial', salsas_cat, ml, Decimal('0.05'), Decimal('500.0')),
        ('SALSA002', 'Salsa Teriyaki Casera', salsas_cat, ml, Decimal('0.08'), Decimal('300.0')),
        ('SALSA003', 'Salsa Picante Mayo', salsas_cat, ml, Decimal('0.06'), Decimal('400.0')),
        ('PREP001', 'Arroz de Sushi Preparado', elaborados_cat, g, Decimal('0.012'), Decimal('2000.0')),
        ('PREP002', 'Tempura Mix Preparado', elaborados_cat, g, Decimal('0.15'), Decimal('500.0')),
        ('PREP003', 'Aguacate Marinado', elaborados_cat, porcion, Decimal('1.50'), Decimal('20.0')),
        ('PREP004', 'Pepino Encurtido', elaborados_cat, g, Decimal('0.03'), Decimal('1000.0')),
        ('PREP005', 'Salmón Ahumado Prep', elaborados_cat, g, Decimal('0.35'), Decimal('200.0')),
    ]
    
    for codigo, nombre, categoria, unidad, precio, stock_min in insumos_elaborados_data:
        insumo, created = Insumo.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'categoria': categoria,
                'unidad_medida': unidad,
                'tipo': 'elaborado',
                'precio_unitario': precio,
                'stock_minimo': stock_min,
                'perecedero': True,
                'dias_vencimiento': 3
            }
        )
        if created:
            print(f"✓ Creado insumo elaborado: {insumo}")
    
    # Crear algunas recetas para los insumos elaborados
    salsa_soja, created = Receta.objects.get_or_create(
        nombre='Salsa de Soja Especial',
        defaults={
            'descripcion': 'Salsa de soja con ingredientes especiales',
            'instrucciones': '1. Mezclar soja base con mirin\n2. Agregar azúcar\n3. Reducir a fuego lento',
            'tiempo_preparacion': 15,
            'porciones': 500
        }
    )
    
    if created:
        print(f"✓ Creada receta: {salsa_soja}")
    
    print("\n🎉 Insumos elaborados creados exitosamente!")

if __name__ == '__main__':
    crear_insumos_elaborados()
