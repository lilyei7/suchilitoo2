#!/usr/bin/env python
"""Script para cargar datos iniciales del sistema"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Sucursal, Rol
from restaurant.models import (
    CategoriaInsumo, UnidadMedida, Proveedor, Insumo, 
    CategoriaProducto, CheckListItem
)

def crear_datos_iniciales():
    print("Creando datos iniciales...")
    
    # Crear Sucursales
    sucursal1, created = Sucursal.objects.get_or_create(
        nombre="Sucursal Centro",
        defaults={
            'direccion': 'Av. Principal 123, Centro',
            'telefono': '555-0001',
            'email': 'centro@sushirestaurant.com',
            'fecha_apertura': '2024-01-01'
        }
    )
    if created:
        print(f"✓ Creada sucursal: {sucursal1.nombre}")
    
    sucursal2, created = Sucursal.objects.get_or_create(
        nombre="Sucursal Norte",
        defaults={
            'direccion': 'Calle Norte 456, Zona Norte',
            'telefono': '555-0002',
            'email': 'norte@sushirestaurant.com',
            'fecha_apertura': '2024-02-01'
        }
    )
    if created:
        print(f"✓ Creada sucursal: {sucursal2.nombre}")
    
    # Crear Roles
    roles_data = [
        ('admin', 'Administrador del sistema con acceso completo'),
        ('gerente', 'Gerente de sucursal'),
        ('supervisor', 'Supervisor de turno'),
        ('cajero', 'Encargado de ventas y caja'),
        ('cocinero', 'Chef y ayudante de cocina'),
        ('mesero', 'Atención al cliente'),
        ('inventario', 'Encargado de inventario y almacén'),
        ('rrhh', 'Recursos humanos'),
    ]
    
    for nombre, descripcion in roles_data:
        rol, created = Rol.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': descripcion}
        )
        if created:
            print(f"✓ Creado rol: {rol.get_nombre_display()}")
    
    # Crear Unidades de Medida
    unidades_data = [
        ('Kilogramo', 'kg'),
        ('Gramo', 'g'),
        ('Litro', 'lt'),
        ('Mililitro', 'ml'),
        ('Unidad', 'ud'),
        ('Porción', 'porción'),
        ('Paquete', 'paq'),
        ('Lata', 'lata'),
    ]
    
    for nombre, abrev in unidades_data:
        unidad, created = UnidadMedida.objects.get_or_create(
            nombre=nombre,
            defaults={'abreviacion': abrev}
        )
        if created:
            print(f"✓ Creada unidad: {unidad}")
    
    # Crear Categorías de Insumos
    categorias_insumo = [
        'Pescados y Mariscos',
        'Vegetales',
        'Cereales y Granos',
        'Condimentos y Especias',
        'Salsas',
        'Aceites',
        'Lácteos',
        'Bebidas',
        'Empaques',
        'Limpieza',
    ]
    
    for nombre in categorias_insumo:
        categoria, created = CategoriaInsumo.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': f'Categoría para {nombre.lower()}'}
        )
        if created:
            print(f"✓ Creada categoría insumo: {categoria.nombre}")
    
    # Crear Proveedores
    proveedores_data = [
        ('Pescadería El Mar', 'Juan Pérez', '555-1001', 'pescaderia@elmar.com', 'Mercado Central Local 15'),
        ('Vegetales Frescos SRL', 'María González', '555-1002', 'ventas@vegetalesfrescos.com', 'Zona Industrial Km 5'),
        ('Importadora Asia', 'Carlos Chen', '555-1003', 'info@importadoraasia.com', 'Puerto, Almacén 22'),
        ('Distribuidora Nacional', 'Ana Torres', '555-1004', 'distribuidora@nacional.com', 'Av. Comercial 789'),
    ]
    
    for nombre, contacto, telefono, email, direccion in proveedores_data:
        proveedor, created = Proveedor.objects.get_or_create(
            nombre=nombre,
            defaults={
                'contacto': contacto,
                'telefono': telefono,
                'email': email,
                'direccion': direccion
            }
        )
        if created:
            print(f"✓ Creado proveedor: {proveedor.nombre}")
    
    # Crear algunos insumos básicos
    kg = UnidadMedida.objects.get(nombre='Kilogramo')
    g = UnidadMedida.objects.get(nombre='Gramo')
    ml = UnidadMedida.objects.get(nombre='Mililitro')
    ud = UnidadMedida.objects.get(nombre='Unidad')
    
    pescados_cat = CategoriaInsumo.objects.get(nombre='Pescados y Mariscos')
    vegetales_cat = CategoriaInsumo.objects.get(nombre='Vegetales')
    cereales_cat = CategoriaInsumo.objects.get(nombre='Cereales y Granos')
    condimentos_cat = CategoriaInsumo.objects.get(nombre='Condimentos y Especias')
    
    insumos_data = [
        ('SALMON001', 'Salmón Fresco', pescados_cat, kg, Decimal('45.00'), Decimal('1.0'), True, 3),
        ('ATUN001', 'Atún Fresco', pescados_cat, kg, Decimal('38.00'), Decimal('1.0'), True, 2),
        ('ARROZ001', 'Arroz para Sushi', cereales_cat, kg, Decimal('4.50'), Decimal('5.0'), False, None),
        ('ALGA001', 'Alga Nori', condimentos_cat, g, Decimal('0.15'), Decimal('100.0'), False, None),
        ('PEPINO001', 'Pepino', vegetales_cat, ud, Decimal('0.50'), Decimal('10.0'), True, 7),
        ('PALTA001', 'Palta/Aguacate', vegetales_cat, ud, Decimal('1.20'), Decimal('5.0'), True, 5),
    ]
    
    proveedor_principal = Proveedor.objects.first()
    
    for codigo, nombre, categoria, unidad, precio, stock_min, perecedero, dias_venc in insumos_data:
        insumo, created = Insumo.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'categoria': categoria,
                'unidad_medida': unidad,
                'precio_unitario': precio,
                'stock_minimo': stock_min,
                'proveedor_principal': proveedor_principal,
                'perecedero': perecedero,
                'dias_vencimiento': dias_venc
            }
        )
        if created:
            print(f"✓ Creado insumo: {insumo}")
    
    # Crear Categorías de Productos
    categorias_producto = [
        'Makis',
        'Nigiris',
        'Sashimis',
        'Rolls Especiales',
        'Entradas',
        'Sopas',
        'Bebidas',
        'Postres',
    ]
    
    for nombre in categorias_producto:
        categoria, created = CategoriaProducto.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': f'Categoría de {nombre.lower()}'}
        )
        if created:
            print(f"✓ Creada categoría producto: {categoria.nombre}")
    
    # Crear CheckList Items
    checklist_items = [
        ('Verificar temperatura de refrigeradores', 'Revisar que todos los refrigeradores estén entre 2-4°C', 'apertura', True, 1),
        ('Encender equipos de cocina', 'Encender plancha, freidora y otros equipos', 'apertura', True, 2),
        ('Revisar stock de ingredientes principales', 'Verificar disponibilidad de pescado fresco', 'apertura', True, 3),
        ('Limpiar y desinfectar superficies', 'Limpiar todas las superficies de trabajo', 'apertura', True, 4),
        
        ('Contar caja', 'Hacer arqueo de caja del día', 'cierre', True, 1),
        ('Apagar equipos', 'Apagar todos los equipos de cocina', 'cierre', True, 2),
        ('Limpiar cocina', 'Limpieza profunda de la cocina', 'cierre', True, 3),
        ('Guardar productos perecederos', 'Almacenar correctamente productos refrigerados', 'cierre', True, 4),
        
        ('Limpieza de baños', 'Limpiar y desinfectar baños', 'limpieza', True, 1),
        ('Limpieza de mesas', 'Limpiar y desinfectar todas las mesas', 'limpieza', True, 2),
        ('Trapear pisos', 'Trapear todos los pisos del restaurante', 'limpieza', True, 3),
        
        ('Verificar salidas de emergencia', 'Confirmar que las salidas estén despejadas', 'seguridad', True, 1),
        ('Revisar extintores', 'Verificar estado de extintores', 'seguridad', False, 2),
        
        ('Conteo físico de inventario', 'Realizar conteo de productos principales', 'inventario', False, 1),
        ('Revisar fechas de vencimiento', 'Verificar productos próximos a vencer', 'inventario', True, 2),
    ]
    
    for nombre, desc, tipo, obligatorio, orden in checklist_items:
        item, created = CheckListItem.objects.get_or_create(
            nombre=nombre,
            defaults={
                'descripcion': desc,
                'tipo': tipo,
                'obligatorio': obligatorio,
                'orden': orden
            }
        )
        if created:
            print(f"✓ Creado checklist item: {item.nombre}")
    
    print("\n🎉 Datos iniciales creados exitosamente!")
    print("\nPuedes acceder al admin en: http://127.0.0.1:8000/admin/")
    print("Usuario: jhayco")
    print("Contraseña: la que configuraste")

if __name__ == '__main__':
    crear_datos_iniciales()
