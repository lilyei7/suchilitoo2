#!/usr/bin/env python3
"""
Script para crear datos de prueba para el sistema de inventario automático.
Crea insumos, recetas, productos de venta e inventario inicial.
"""

import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import (
    ProductoVenta, Receta, RecetaInsumo, Insumo, InsumoCompuesto,
    CategoriaInsumo, UnidadMedida, CategoriaProducto, Inventario,
    MovimientoInventario, Proveedor
)
from accounts.models import Sucursal
from django.contrib.auth import get_user_model

User = get_user_model()

def crear_datos_inventario():
    """
    Crea datos de prueba para el sistema de inventario automático
    """
    print("🔧 Creando datos de prueba para inventario automático...")
    
    # Obtener o crear sucursal
    sucursal = Sucursal.objects.first()
    if not sucursal:
        sucursal = Sucursal.objects.create(
            nombre="Sucursal Principal",
            codigo="001",
            direccion="Calle Principal 123",
            telefono="02-234-5678",
            email="principal@sushi.com",
            activa=True
        )
        print(f"✅ Sucursal creada: {sucursal.nombre}")
    
    # Crear proveedor
    proveedor, created = Proveedor.objects.get_or_create(
        nombre="Proveedor de Sushi",
        defaults={
            'ruc': '1234567890',
            'direccion': 'Av. Los Sushis 456',
            'contacto': 'Juan Pérez',
            'telefono': '09-876-5432',
            'email': 'ventas@proveedorsushi.com'
        }
    )
    if created:
        print(f"✅ Proveedor creado: {proveedor.nombre}")
    
    # Crear categorías de insumos
    categorias_insumo = {
        'Pescados': CategoriaInsumo.objects.get_or_create(
            nombre='Pescados',
            defaults={'descripcion': 'Pescados frescos para sushi'}
        )[0],
        'Vegetales': CategoriaInsumo.objects.get_or_create(
            nombre='Vegetales',
            defaults={'descripcion': 'Vegetales frescos'}
        )[0],
        'Arroces': CategoriaInsumo.objects.get_or_create(
            nombre='Arroces',
            defaults={'descripcion': 'Tipos de arroz'}
        )[0],
        'Salsas': CategoriaInsumo.objects.get_or_create(
            nombre='Salsas',
            defaults={'descripcion': 'Salsas y condimentos'}
        )[0],
        'Algas': CategoriaInsumo.objects.get_or_create(
            nombre='Algas',
            defaults={'descripcion': 'Algas marinas'}
        )[0],
    }
    print("✅ Categorías de insumos creadas")
    
    # Crear unidades de medida
    unidades = {
        'gr': UnidadMedida.objects.get_or_create(
            nombre='Gramos',
            defaults={'abreviacion': 'gr'}
        )[0],
        'kg': UnidadMedida.objects.get_or_create(
            nombre='Kilogramos',
            defaults={'abreviacion': 'kg'}
        )[0],
        'ml': UnidadMedida.objects.get_or_create(
            nombre='Mililitros',
            defaults={'abreviacion': 'ml'}
        )[0],
        'und': UnidadMedida.objects.get_or_create(
            nombre='Unidades',
            defaults={'abreviacion': 'und'}
        )[0],
        'pza': UnidadMedida.objects.get_or_create(
            nombre='Piezas',
            defaults={'abreviacion': 'pza'}
        )[0],
    }
    print("✅ Unidades de medida creadas")
    
    # Crear insumos básicos
    insumos_basicos = [
        {
            'codigo': 'SAL001',
            'nombre': 'Salmón fresco',
            'categoria': categorias_insumo['Pescados'],
            'unidad': unidades['gr'],
            'precio': Decimal('0.08'),  # $0.08 por gramo
            'stock_actual': Decimal('2000'),  # 2kg
            'stock_minimo': Decimal('500'),
        },
        {
            'codigo': 'ATU001',
            'nombre': 'Atún fresco',
            'categoria': categorias_insumo['Pescados'],
            'unidad': unidades['gr'],
            'precio': Decimal('0.10'),  # $0.10 por gramo
            'stock_actual': Decimal('1500'),  # 1.5kg
            'stock_minimo': Decimal('300'),
        },
        {
            'codigo': 'ARR001',
            'nombre': 'Arroz para sushi',
            'categoria': categorias_insumo['Arroces'],
            'unidad': unidades['gr'],
            'precio': Decimal('0.003'),  # $0.003 por gramo
            'stock_actual': Decimal('5000'),  # 5kg
            'stock_minimo': Decimal('1000'),
        },
        {
            'codigo': 'NOR001',
            'nombre': 'Alga nori',
            'categoria': categorias_insumo['Algas'],
            'unidad': unidades['pza'],
            'precio': Decimal('0.25'),  # $0.25 por hoja
            'stock_actual': Decimal('100'),  # 100 hojas
            'stock_minimo': Decimal('20'),
        },
        {
            'codigo': 'PEP001',
            'nombre': 'Pepino',
            'categoria': categorias_insumo['Vegetales'],
            'unidad': unidades['gr'],
            'precio': Decimal('0.004'),  # $0.004 por gramo
            'stock_actual': Decimal('2000'),  # 2kg
            'stock_minimo': Decimal('500'),
        },
        {
            'codigo': 'PAL001',
            'nombre': 'Palta',
            'categoria': categorias_insumo['Vegetales'],
            'unidad': unidades['gr'],
            'precio': Decimal('0.008'),  # $0.008 por gramo
            'stock_actual': Decimal('1000'),  # 1kg
            'stock_minimo': Decimal('200'),
        },
        {
            'codigo': 'SES001',
            'nombre': 'Semillas de sésamo',
            'categoria': categorias_insumo['Vegetales'],
            'unidad': unidades['gr'],
            'precio': Decimal('0.02'),  # $0.02 por gramo
            'stock_actual': Decimal('500'),  # 500gr
            'stock_minimo': Decimal('100'),
        },
        {
            'codigo': 'SOY001',
            'nombre': 'Salsa de soja',
            'categoria': categorias_insumo['Salsas'],
            'unidad': unidades['ml'],
            'precio': Decimal('0.005'),  # $0.005 por ml
            'stock_actual': Decimal('1000'),  # 1 litro
            'stock_minimo': Decimal('200'),
        },
        {
            'codigo': 'WAS001',
            'nombre': 'Wasabi',
            'categoria': categorias_insumo['Salsas'],
            'unidad': unidades['gr'],
            'precio': Decimal('0.15'),  # $0.15 por gramo
            'stock_actual': Decimal('200'),  # 200gr
            'stock_minimo': Decimal('50'),
        },
    ]
    
    # Crear los insumos básicos
    for insumo_data in insumos_basicos:
        insumo, created = Insumo.objects.get_or_create(
            codigo=insumo_data['codigo'],
            defaults={
                'nombre': insumo_data['nombre'],
                'tipo': 'basico',
                'categoria': insumo_data['categoria'],
                'unidad_medida': insumo_data['unidad'],
                'precio_unitario': insumo_data['precio'],
                'stock_actual': insumo_data['stock_actual'],
                'stock_minimo': insumo_data['stock_minimo'],
                'proveedor_principal': proveedor,
                'perecedero': True,
                'dias_vencimiento': 3
            }
        )
        
        if created:
            print(f"✅ Insumo básico creado: {insumo.nombre}")
            
            # Crear inventario para este insumo
            Inventario.objects.get_or_create(
                sucursal=sucursal,
                insumo=insumo,
                defaults={
                    'cantidad_actual': insumo_data['stock_actual'],
                    'cantidad_reservada': Decimal('0'),
                    'costo_unitario': insumo_data['precio']
                }
            )
    
    # Crear insumo compuesto: "Arroz sazonado"
    arroz_base = Insumo.objects.get(codigo='ARR001')
    
    arroz_sazonado, created = Insumo.objects.get_or_create(
        codigo='ARRS001',
        defaults={
            'nombre': 'Arroz sazonado para sushi',
            'tipo': 'compuesto',
            'categoria': categorias_insumo['Arroces'],
            'unidad_medida': unidades['gr'],
            'precio_unitario': Decimal('0.004'),  # Precio calculado
            'stock_actual': Decimal('0'),  # Se produce según demanda
            'stock_minimo': Decimal('0'),
        }
    )
    
    if created:
        print(f"✅ Insumo compuesto creado: {arroz_sazonado.nombre}")
        
        # Crear los componentes del arroz sazonado
        InsumoCompuesto.objects.get_or_create(
            insumo_compuesto=arroz_sazonado,
            insumo_componente=arroz_base,
            defaults={'cantidad': Decimal('1.0')}  # 1gr de arroz = 1gr de arroz sazonado
        )
    
    # Crear insumo elaborado: "Mezcla de sésamo"
    sesamo_base = Insumo.objects.get(codigo='SES001')
    
    mezcla_sesamo, created = Insumo.objects.get_or_create(
        codigo='MESS001',
        defaults={
            'nombre': 'Mezcla de sésamo tostado',
            'tipo': 'elaborado',
            'categoria': categorias_insumo['Vegetales'],
            'unidad_medida': unidades['gr'],
            'precio_unitario': Decimal('0.025'),  # Precio con procesamiento
            'stock_actual': Decimal('0'),  # Se produce según demanda
            'stock_minimo': Decimal('0'),
            'tiempo_preparacion': 15,  # 15 minutos de preparación
        }
    )
    
    if created:
        print(f"✅ Insumo elaborado creado: {mezcla_sesamo.nombre}")
        
        # Crear los componentes de la mezcla de sésamo
        InsumoCompuesto.objects.get_or_create(
            insumo_compuesto=mezcla_sesamo,
            insumo_componente=sesamo_base,
            defaults={'cantidad': Decimal('1.0')}  # 1gr de sésamo = 1gr de mezcla
        )
    
    # Crear categoría de productos
    categoria_rolls, created = CategoriaProducto.objects.get_or_create(
        nombre='Rolls',
        defaults={'descripcion': 'Rolls de sushi', 'orden': 1}
    )
    if created:
        print(f"✅ Categoría de producto creada: {categoria_rolls.nombre}")
    
    # Crear producto de venta: "California Roll"
    california_roll, created = ProductoVenta.objects.get_or_create(
        codigo='ROLL001',
        defaults={
            'nombre': 'California Roll',
            'descripcion': 'Delicioso roll con salmón, palta y pepino',
            'precio': Decimal('12.50'),
            'categoria': categoria_rolls,
            'tipo': 'plato',
            'disponible': True,
            'calorias': 250
        }
    )
    
    if created:
        print(f"✅ Producto creado: {california_roll.nombre}")
        
        # Crear receta para el California Roll
        receta, created = Receta.objects.get_or_create(
            producto=california_roll,
            defaults={
                'tiempo_preparacion': 10,
                'porciones': 1,
                'instrucciones': 'Preparar roll californiano con ingredientes frescos',
                'notas': 'Servir con salsa de soja y wasabi'
            }
        )
        
        if created:
            print(f"✅ Receta creada para: {california_roll.nombre}")
            
            # Agregar insumos a la receta
            insumos_receta = [
                {
                    'insumo': arroz_sazonado,
                    'cantidad': Decimal('120'),  # 120gr de arroz sazonado
                    'orden': 1
                },
                {
                    'insumo': Insumo.objects.get(codigo='SAL001'),
                    'cantidad': Decimal('80'),  # 80gr de salmón
                    'orden': 2
                },
                {
                    'insumo': Insumo.objects.get(codigo='PAL001'),
                    'cantidad': Decimal('40'),  # 40gr de palta
                    'orden': 3
                },
                {
                    'insumo': Insumo.objects.get(codigo='PEP001'),
                    'cantidad': Decimal('30'),  # 30gr de pepino
                    'orden': 4
                },
                {
                    'insumo': Insumo.objects.get(codigo='NOR001'),
                    'cantidad': Decimal('1'),  # 1 hoja de nori
                    'orden': 5
                },
                {
                    'insumo': mezcla_sesamo,
                    'cantidad': Decimal('5'),  # 5gr de sésamo
                    'orden': 6
                }
            ]
            
            for insumo_data in insumos_receta:
                RecetaInsumo.objects.get_or_create(
                    receta=receta,
                    insumo=insumo_data['insumo'],
                    defaults={
                        'cantidad': insumo_data['cantidad'],
                        'orden': insumo_data['orden']
                    }
                )
            
            print(f"✅ Insumos agregados a la receta de {california_roll.nombre}")
    
    # Crear producto de venta: "Sashimi de Atún"
    sashimi_atun, created = ProductoVenta.objects.get_or_create(
        codigo='SASH001',
        defaults={
            'nombre': 'Sashimi de Atún',
            'descripcion': 'Finas láminas de atún fresco',
            'precio': Decimal('15.00'),
            'categoria': categoria_rolls,
            'tipo': 'plato',
            'disponible': True,
            'calorias': 180
        }
    )
    
    if created:
        print(f"✅ Producto creado: {sashimi_atun.nombre}")
        
        # Crear receta para el Sashimi de Atún
        receta, created = Receta.objects.get_or_create(
            producto=sashimi_atun,
            defaults={
                'tiempo_preparacion': 5,
                'porciones': 1,
                'instrucciones': 'Cortar atún en láminas finas',
                'notas': 'Servir con wasabi y salsa de soja'
            }
        )
        
        if created:
            print(f"✅ Receta creada para: {sashimi_atun.nombre}")
            
            # Agregar insumos a la receta
            RecetaInsumo.objects.get_or_create(
                receta=receta,
                insumo=Insumo.objects.get(codigo='ATU001'),
                defaults={
                    'cantidad': Decimal('120'),  # 120gr de atún
                    'orden': 1
                }
            )
            
            print(f"✅ Insumos agregados a la receta de {sashimi_atun.nombre}")
    
    print("\\n" + "="*50)
    print("✅ DATOS DE INVENTARIO CREADOS EXITOSAMENTE")
    print("="*50)
    
    # Mostrar resumen
    print(f"📊 Resumen:")
    print(f"  - Insumos básicos: {Insumo.objects.filter(tipo='basico').count()}")
    print(f"  - Insumos compuestos: {Insumo.objects.filter(tipo='compuesto').count()}")
    print(f"  - Insumos elaborados: {Insumo.objects.filter(tipo='elaborado').count()}")
    print(f"  - Productos de venta: {ProductoVenta.objects.count()}")
    print(f"  - Recetas: {Receta.objects.count()}")
    print(f"  - Inventarios: {Inventario.objects.count()}")
    
    print("\\n📋 Productos disponibles:")
    for producto in ProductoVenta.objects.all():
        print(f"  - {producto.nombre} (${producto.precio})")
    
    print("\\n🧪 Listo para probar el sistema de inventario automático!")

if __name__ == "__main__":
    crear_datos_inventario()
