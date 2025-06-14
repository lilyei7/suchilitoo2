#!/usr/bin/env python
"""
Script para crear insumos compuestos de ejemplo para probar insumos elaborados
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Insumo, InsumoCompuesto, CategoriaInsumo, UnidadMedida, Proveedor

def crear_insumos_compuestos():
    """Crear insumos compuestos como base para insumos elaborados"""
    print("🍱 Creando insumos compuestos para usar como base en elaborados...")
    
    # Verificar que existan categorías y unidades
    categoria_prep, _ = CategoriaInsumo.objects.get_or_create(
        nombre="Preparaciones",
        defaults={'descripcion': "Preparaciones y mezclas"}
    )
    
    categoria_salsas, _ = CategoriaInsumo.objects.get_or_create(
        nombre="Salsas",
        defaults={'descripcion': "Salsas y aderezos"}
    )
    
    unidad_gr, _ = UnidadMedida.objects.get_or_create(
        nombre="Gramos", 
        defaults={'abreviacion': "gr"}
    )
    
    unidad_ml, _ = UnidadMedida.objects.get_or_create(
        nombre="Mililitros", 
        defaults={'abreviacion': "ml"}
    )
    
    unidad_unidad, _ = UnidadMedida.objects.get_or_create(
        nombre="Unidad", 
        defaults={'abreviacion': "un"}
    )
    
    # Crear insumos básicos si no existen
    insumos_basicos = [
        ('ARROZ-001', 'Arroz para Sushi', 'Cereales', 2.50, unidad_gr),
        ('VINAGRE-001', 'Vinagre de Arroz', 'Condimentos', 8.00, unidad_ml),
        ('AZUCAR-001', 'Azúcar Blanca', 'Endulzantes', 1.20, unidad_gr),
        ('SAL-001', 'Sal Marina', 'Condimentos', 0.80, unidad_gr),
        ('SALMON-001', 'Salmón Fresco', 'Pescados', 45.00, unidad_gr),
        ('AGUACATE-001', 'Aguacate Hass', 'Vegetales', 3.20, unidad_gr),
        ('NORI-001', 'Alga Nori', 'Algas', 12.00, unidad_unidad),
        ('SESAMO-001', 'Semillas de Sésamo', 'Semillas', 15.00, unidad_gr),
        ('MAYONESA-001', 'Mayonesa Japonesa', 'Salsas', 6.50, unidad_ml),
        ('SRIRACHA-001', 'Salsa Sriracha', 'Salsas', 8.20, unidad_ml),
    ]
    
    categoria_cereales, _ = CategoriaInsumo.objects.get_or_create(
        nombre="Cereales", defaults={'descripcion': "Cereales y granos"}
    )
    categoria_condimentos, _ = CategoriaInsumo.objects.get_or_create(
        nombre="Condimentos", defaults={'descripcion': "Condimentos y especias"}
    )
    categoria_endulzantes, _ = CategoriaInsumo.objects.get_or_create(
        nombre="Endulzantes", defaults={'descripcion': "Azúcares y endulzantes"}
    )
    categoria_pescados, _ = CategoriaInsumo.objects.get_or_create(
        nombre="Pescados", defaults={'descripcion': "Pescados y mariscos"}
    )
    categoria_vegetales, _ = CategoriaInsumo.objects.get_or_create(
        nombre="Vegetales", defaults={'descripcion': "Verduras y vegetales"}
    )
    categoria_algas, _ = CategoriaInsumo.objects.get_or_create(
        nombre="Algas", defaults={'descripcion': "Algas marinas"}
    )
    categoria_semillas, _ = CategoriaInsumo.objects.get_or_create(
        nombre="Semillas", defaults={'descripcion': "Semillas y frutos secos"}
    )
    
    categorias_map = {
        'Cereales': categoria_cereales,
        'Condimentos': categoria_condimentos,
        'Endulzantes': categoria_endulzantes,
        'Pescados': categoria_pescados,
        'Vegetales': categoria_vegetales,
        'Algas': categoria_algas,
        'Semillas': categoria_semillas,
        'Salsas': categoria_salsas,
    }
    
    print("Creando insumos básicos...")
    for codigo, nombre, cat_nombre, precio, unidad in insumos_basicos:
        insumo, created = Insumo.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'categoria': categorias_map[cat_nombre],
                'unidad_medida': unidad,
                'tipo': 'basico',
                'precio_unitario': precio,
                'stock_minimo': 10,
                'activo': True
            }
        )
        if created:
            print(f"  ✅ Creado: {codigo} - {nombre}")
        else:
            print(f"  ⏩ Ya existe: {codigo} - {nombre}")
    
    # Crear insumos compuestos
    print("\nCreando insumos compuestos...")
    
    # 1. Arroz de Sushi (compuesto)
    arroz_sushi, created = Insumo.objects.get_or_create(
        codigo='COMP-ARROZ-001',
        defaults={
            'nombre': 'Arroz de Sushi Preparado',
            'categoria': categoria_prep,
            'unidad_medida': unidad_gr,
            'tipo': 'compuesto',
            'precio_unitario': 0,  # Se calculará
            'cantidad_producida': 1000,  # 1kg de arroz preparado
            'stock_minimo': 100,
            'descripcion': 'Arroz de sushi cocido y sazonado con vinagre',
            'activo': True
        }
    )
    
    if created:
        # Componentes del arroz de sushi
        componentes_arroz = [
            ('ARROZ-001', 500),      # 500g arroz crudo
            ('VINAGRE-001', 80),     # 80ml vinagre
            ('AZUCAR-001', 30),      # 30g azúcar
            ('SAL-001', 10),         # 10g sal
        ]
        
        costo_total = 0
        for i, (codigo_comp, cantidad) in enumerate(componentes_arroz):
            insumo_componente = Insumo.objects.get(codigo=codigo_comp)
            costo = cantidad * insumo_componente.precio_unitario
            costo_total += costo
            
            InsumoCompuesto.objects.create(
                insumo_compuesto=arroz_sushi,
                insumo_componente=insumo_componente,
                cantidad=cantidad,
                orden=i + 1
            )
        
        # Actualizar precio unitario
        arroz_sushi.precio_unitario = costo_total / arroz_sushi.cantidad_producida
        arroz_sushi.save()
        print(f"  ✅ Creado: {arroz_sushi.codigo} - {arroz_sushi.nombre} (${costo_total:.2f}/kg)")
    
    # 2. Salsa Spicy Mayo (compuesta)
    salsa_spicy, created = Insumo.objects.get_or_create(
        codigo='COMP-SALSA-001',
        defaults={
            'nombre': 'Salsa Spicy Mayo',
            'categoria': categoria_salsas,
            'unidad_medida': unidad_ml,
            'tipo': 'compuesto',
            'precio_unitario': 0,
            'cantidad_producida': 500,  # 500ml de salsa
            'stock_minimo': 50,
            'descripcion': 'Mayonesa japonesa con sriracha',
            'activo': True
        }
    )
    
    if created:
        componentes_salsa = [
            ('MAYONESA-001', 400),   # 400ml mayonesa
            ('SRIRACHA-001', 100),   # 100ml sriracha
        ]
        
        costo_total = 0
        for i, (codigo_comp, cantidad) in enumerate(componentes_salsa):
            insumo_componente = Insumo.objects.get(codigo=codigo_comp)
            costo = cantidad * insumo_componente.precio_unitario
            costo_total += costo
            
            InsumoCompuesto.objects.create(
                insumo_compuesto=salsa_spicy,
                insumo_componente=insumo_componente,
                cantidad=cantidad,
                orden=i + 1
            )
        
        salsa_spicy.precio_unitario = costo_total / salsa_spicy.cantidad_producida
        salsa_spicy.save()
        print(f"  ✅ Creado: {salsa_spicy.codigo} - {salsa_spicy.nombre} (${costo_total:.2f}/500ml)")
    
    # 3. Mix de Sésamo Tostado (compuesto)
    mix_sesamo, created = Insumo.objects.get_or_create(
        codigo='COMP-SESAMO-001',
        defaults={
            'nombre': 'Mix de Sésamo Tostado',
            'categoria': categoria_prep,
            'unidad_medida': unidad_gr,
            'tipo': 'compuesto',
            'precio_unitario': 0,
            'cantidad_producida': 200,  # 200g de mix
            'stock_minimo': 20,
            'descripcion': 'Semillas de sésamo tostadas y condimentadas',
            'activo': True
        }
    )
    
    if created:
        componentes_sesamo = [
            ('SESAMO-001', 180),     # 180g sésamo
            ('SAL-001', 20),         # 20g sal
        ]
        
        costo_total = 0
        for i, (codigo_comp, cantidad) in enumerate(componentes_sesamo):
            insumo_componente = Insumo.objects.get(codigo=codigo_comp)
            costo = cantidad * insumo_componente.precio_unitario
            costo_total += costo
            
            InsumoCompuesto.objects.create(
                insumo_compuesto=mix_sesamo,
                insumo_componente=insumo_componente,
                cantidad=cantidad,
                orden=i + 1
            )
        
        mix_sesamo.precio_unitario = costo_total / mix_sesamo.cantidad_producida
        mix_sesamo.save()
        print(f"  ✅ Creado: {mix_sesamo.codigo} - {mix_sesamo.nombre} (${costo_total:.2f}/200g)")
    
    print(f"\n✅ Proceso completado. Insumos compuestos disponibles:")
    insumos_compuestos = Insumo.objects.filter(tipo='compuesto', activo=True)
    for insumo in insumos_compuestos:
        print(f"   • {insumo.codigo} - {insumo.nombre} (${insumo.precio_unitario:.2f}/{insumo.unidad_medida.abreviacion})")
    
    print(f"\n🎯 Total de insumos compuestos: {insumos_compuestos.count()}")
    print("📋 Ahora puedes usar estos insumos compuestos como base para crear insumos elaborados")

if __name__ == '__main__':
    crear_insumos_compuestos()
