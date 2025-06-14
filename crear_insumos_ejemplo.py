#!/usr/bin/env python
"""
Script para crear insumos de ejemplo para probar el sistema
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def crear_insumos_ejemplo():
    from restaurant.models import Insumo, CategoriaInsumo, UnidadMedida, InsumoCompuesto
    from decimal import Decimal
    
    print("🚀 Creando insumos de ejemplo...")
    
    # Crear categorías si no existen
    categorias = {}
    for nombre in ['Pescados', 'Verduras', 'Condimentos', 'Elaborados']:
        categoria, created = CategoriaInsumo.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': f'Categoría de {nombre.lower()}'}
        )
        categorias[nombre] = categoria
        if created:
            print(f"✅ Categoría creada: {nombre}")
    
    # Crear unidades de medida si no existen
    unidades = {}
    unidades_data = [
        ('Kilogramo', 'kg'),
        ('Gramo', 'g'),
        ('Litro', 'L'),
        ('Mililitro', 'ml'),
        ('Unidad', 'und'),
        ('Pieza', 'pza')
    ]
    
    for nombre, abrev in unidades_data:
        unidad, created = UnidadMedida.objects.get_or_create(
            nombre=nombre,
            defaults={'abreviacion': abrev}
        )
        unidades[abrev] = unidad
        if created:
            print(f"✅ Unidad creada: {nombre} ({abrev})")
    
    # Crear insumos básicos
    insumos_basicos_data = [
        # Pescados
        ('SALM-001', 'Salmón Fresco', categorias['Pescados'], unidades['kg'], Decimal('25.50')),
        ('ATUN-001', 'Atún Fresco', categorias['Pescados'], unidades['kg'], Decimal('28.00')),
        ('CAMR-001', 'Camarón Jumbo', categorias['Pescados'], unidades['kg'], Decimal('35.00')),
        
        # Verduras
        ('PEPI-001', 'Pepino', categorias['Verduras'], unidades['kg'], Decimal('3.50')),
        ('AGUA-001', 'Aguacate', categorias['Verduras'], unidades['kg'], Decimal('8.00')),
        ('ZANA-001', 'Zanahoria', categorias['Verduras'], unidades['kg'], Decimal('2.50')),
        
        # Condimentos
        ('ARRI-001', 'Arroz para Sushi', categorias['Condimentos'], unidades['kg'], Decimal('4.50')),
        ('NORI-001', 'Alga Nori', categorias['Condimentos'], unidades['pza'], Decimal('0.75')),
        ('SOYU-001', 'Salsa de Soya', categorias['Condimentos'], unidades['ml'], Decimal('0.02')),
        ('WASA-001', 'Wasabi', categorias['Condimentos'], unidades['g'], Decimal('0.15')),
    ]
    
    insumos_basicos = {}
    for codigo, nombre, categoria, unidad, precio in insumos_basicos_data:
        insumo, created = Insumo.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'categoria': categoria,
                'unidad_medida': unidad,
                'tipo': 'basico',
                'precio_unitario': precio,
                'stock_minimo': Decimal('5.0'),
                'activo': True
            }
        )
        insumos_basicos[codigo] = insumo
        if created:
            print(f"✅ Insumo básico creado: {nombre} (${precio}/{unidad.abreviacion})")
    
    # Crear insumos compuestos
    print("\n🔧 Creando insumos compuestos...")
    
    # 1. Arroz Preparado para Sushi
    arroz_prep, created = Insumo.objects.get_or_create(
        codigo='ARPR-001',
        defaults={
            'nombre': 'Arroz Preparado para Sushi',
            'categoria': categorias['Elaborados'],
            'unidad_medida': unidades['kg'],
            'tipo': 'compuesto',
            'precio_unitario': Decimal('6.50'),
            'cantidad_producida': Decimal('1.0'),
            'descripcion': 'Arroz cocido y preparado con vinagre de arroz',
            'activo': True
        }
    )
    
    if created:
        print(f"✅ Insumo compuesto creado: {arroz_prep.nombre}")
        
        # Componentes del arroz preparado
        InsumoCompuesto.objects.get_or_create(
            insumo_compuesto=arroz_prep,
            insumo_componente=insumos_basicos['ARRI-001'],
            defaults={'cantidad': Decimal('1.0'), 'orden': 1}
        )
        print(f"   - Componente: {insumos_basicos['ARRI-001'].nombre}")
    
    # 2. Mezcla de Vegetables para Sushi
    veggie_mix, created = Insumo.objects.get_or_create(
        codigo='VMIX-001',
        defaults={
            'nombre': 'Mezcla de Vegetales para Sushi',
            'categoria': categorias['Elaborados'],
            'unidad_medida': unidades['kg'],
            'tipo': 'compuesto',
            'precio_unitario': Decimal('12.00'),
            'cantidad_producida': Decimal('1.0'),
            'descripcion': 'Mezcla preparada de pepino, aguacate y zanahoria',
            'activo': True
        }
    )
    
    if created:
        print(f"✅ Insumo compuesto creado: {veggie_mix.nombre}")
        
        # Componentes de la mezcla de vegetales
        componentes_veggie = [
            (insumos_basicos['PEPI-001'], Decimal('0.3')),
            (insumos_basicos['AGUA-001'], Decimal('0.4')),
            (insumos_basicos['ZANA-001'], Decimal('0.3'))
        ]
        
        for i, (insumo, cantidad) in enumerate(componentes_veggie, 1):
            InsumoCompuesto.objects.get_or_create(
                insumo_compuesto=veggie_mix,
                insumo_componente=insumo,
                defaults={'cantidad': cantidad, 'orden': i}
            )
            print(f"   - Componente: {insumo.nombre} ({cantidad} {insumo.unidad_medida.abreviacion})")
    
    print(f"\n✅ Proceso completado!")
    print(f"📊 Resumen:")
    print(f"   - Insumos básicos: {Insumo.objects.filter(tipo='basico').count()}")
    print(f"   - Insumos compuestos: {Insumo.objects.filter(tipo='compuesto').count()}")
    print(f"   - Total componentes: {InsumoCompuesto.objects.count()}")

if __name__ == "__main__":
    crear_insumos_ejemplo()
