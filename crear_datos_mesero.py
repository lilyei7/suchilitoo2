#!/usr/bin/env python
"""
Script para crear datos de prueba para el sistema de mesero.
Incluye mesas, productos de venta básicos, y usuarios de prueba.
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import Mesa, Turno
from restaurant.models import ProductoVenta, CategoriaProducto
from accounts.models import Sucursal, Rol, Usuario
from decimal import Decimal
import random

def crear_datos_mesero():
    print("🍣 Creando datos de prueba para el sistema de mesero...")
    
    # 1. Crear Sucursal de prueba
    sucursal, created = Sucursal.objects.get_or_create(
        nombre="Sucursal Principal",
        defaults={
            'direccion': 'Av. Principal 123',
            'telefono': '555-0123',
            'activa': True
        }
    )
    if created:
        print(f"✓ Sucursal creada: {sucursal.nombre}")
    else:
        print(f"✓ Sucursal existente: {sucursal.nombre}")
    
    # 2. Crear Roles
    rol_mesero, created = Rol.objects.get_or_create(
        nombre='mesero',
        defaults={'descripcion': 'Mesero del restaurante'}
    )
    if created:
        print(f"✓ Rol creado: {rol_mesero.nombre}")
    
    rol_gerente, created = Rol.objects.get_or_create(
        nombre='gerente',
        defaults={'descripcion': 'Gerente del restaurante'}
    )
    if created:
        print(f"✓ Rol creado: {rol_gerente.nombre}")
    
    # 3. Crear usuarios de prueba
    # Usuario mesero
    if not Usuario.objects.filter(username='mesero1').exists():
        user_mesero = Usuario.objects.create_user(
            username='mesero1',
            password='mesero123',
            first_name='Juan',
            last_name='Pérez',
            email='mesero1@sushi.com'
        )
        user_mesero.rol = rol_mesero
        user_mesero.sucursal_asignada = sucursal
        user_mesero.save()
        print(f"✓ Usuario mesero creado: {user_mesero.username}")
    else:
        print("✓ Usuario mesero ya existe")
    
    # Usuario gerente
    if not Usuario.objects.filter(username='gerente1').exists():
        user_gerente = Usuario.objects.create_user(
            username='gerente1',
            password='gerente123',
            first_name='María',
            last_name='González',
            email='gerente1@sushi.com'
        )
        user_gerente.rol = rol_gerente
        user_gerente.sucursal_asignada = sucursal
        user_gerente.save()
        print(f"✓ Usuario gerente creado: {user_gerente.username}")
    else:
        print("✓ Usuario gerente ya existe")
    
    # 4. Crear Mesas
    mesas_data = [
        {'numero': 1, 'capacidad': 2},
        {'numero': 2, 'capacidad': 4},
        {'numero': 3, 'capacidad': 2},
        {'numero': 4, 'capacidad': 6},
        {'numero': 5, 'capacidad': 4},
        {'numero': 6, 'capacidad': 2},
        {'numero': 7, 'capacidad': 8},
        {'numero': 8, 'capacidad': 4},
    ]
    
    for mesa_data in mesas_data:
        mesa, created = Mesa.objects.get_or_create(
            numero=mesa_data['numero'],
            defaults={
                'capacidad': mesa_data['capacidad'],
                'sucursal': sucursal,
                'activa': True
            }
        )
        if created:
            print(f"✓ Mesa creada: Mesa {mesa.numero} ({mesa.capacidad} personas)")
    
    # 5. Crear Categorías de Productos
    categorias_data = [
        {'nombre': 'Sushi', 'descripcion': 'Rollos de sushi tradicionales'},
        {'nombre': 'Sashimi', 'descripcion': 'Pescado fresco sin arroz'},
        {'nombre': 'Makis', 'descripcion': 'Rollos especiales'},
        {'nombre': 'Tempura', 'descripcion': 'Productos empanizados'},
        {'nombre': 'Sopas', 'descripcion': 'Sopas japonesas'},
        {'nombre': 'Bebidas', 'descripcion': 'Bebidas y tés'},
        {'nombre': 'Postres', 'descripcion': 'Postres japoneses'},
    ]
    
    categorias = {}
    for cat_data in categorias_data:
        categoria, created = CategoriaProducto.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults={'descripcion': cat_data['descripcion']}
        )
        categorias[cat_data['nombre']] = categoria
        if created:
            print(f"✓ Categoría creada: {categoria.nombre}")
    
    # 6. Crear Productos de Venta
    productos_data = [
        # Sushi
        {'codigo': 'SUSHI001', 'nombre': 'California Roll', 'categoria': 'Sushi', 'precio': 12.50, 'descripcion': 'Cangrejo, aguacate y pepino'},
        {'codigo': 'SUSHI002', 'nombre': 'Philadelphia Roll', 'categoria': 'Sushi', 'precio': 14.00, 'descripcion': 'Salmón, queso crema y pepino'},
        {'codigo': 'SUSHI003', 'nombre': 'Spicy Tuna Roll', 'categoria': 'Sushi', 'precio': 13.50, 'descripcion': 'Atún picante con mayo sriracha'},
        {'codigo': 'SUSHI004', 'nombre': 'Dragon Roll', 'categoria': 'Sushi', 'precio': 16.00, 'descripcion': 'Tempura de camarón, aguacate encima'},
        {'codigo': 'SUSHI005', 'nombre': 'Salmon Avocado Roll', 'categoria': 'Sushi', 'precio': 11.50, 'descripcion': 'Salmón fresco y aguacate'},
        
        # Sashimi
        {'codigo': 'SASH001', 'nombre': 'Sashimi de Salmón', 'categoria': 'Sashimi', 'precio': 15.00, 'descripcion': '6 piezas de salmón fresco'},
        {'codigo': 'SASH002', 'nombre': 'Sashimi de Atún', 'categoria': 'Sashimi', 'precio': 17.00, 'descripcion': '6 piezas de atún rojo'},
        {'codigo': 'SASH003', 'nombre': 'Sashimi Mixto', 'categoria': 'Sashimi', 'precio': 22.00, 'descripcion': '9 piezas variadas'},
        
        # Makis
        {'codigo': 'MAKI001', 'nombre': 'Maki de Pepino', 'categoria': 'Makis', 'precio': 8.00, 'descripcion': 'Rollo simple de pepino'},
        {'codigo': 'MAKI002', 'nombre': 'Maki de Salmón', 'categoria': 'Makis', 'precio': 10.00, 'descripcion': 'Rollo simple de salmón'},
        {'codigo': 'MAKI003', 'nombre': 'Maki de Atún', 'categoria': 'Makis', 'precio': 11.00, 'descripcion': 'Rollo simple de atún'},
        
        # Tempura
        {'codigo': 'TEMP001', 'nombre': 'Tempura de Camarón', 'categoria': 'Tempura', 'precio': 14.00, 'descripcion': '5 piezas de camarón empanizado'},
        {'codigo': 'TEMP002', 'nombre': 'Tempura de Verduras', 'categoria': 'Tempura', 'precio': 12.00, 'descripcion': 'Verduras mixtas empanizadas'},
        {'codigo': 'TEMP003', 'nombre': 'Tempura Mixta', 'categoria': 'Tempura', 'precio': 16.00, 'descripcion': 'Camarón y verduras'},
        
        # Sopas
        {'codigo': 'SOPA001', 'nombre': 'Sopa Miso', 'categoria': 'Sopas', 'precio': 6.00, 'descripcion': 'Sopa tradicional de miso'},
        {'codigo': 'SOPA002', 'nombre': 'Ramen de Pollo', 'categoria': 'Sopas', 'precio': 18.00, 'descripcion': 'Ramen con caldo de pollo'},
        {'codigo': 'SOPA003', 'nombre': 'Udon de Verduras', 'categoria': 'Sopas', 'precio': 15.00, 'descripcion': 'Fideos udon con verduras'},
        
        # Bebidas
        {'codigo': 'BEB001', 'nombre': 'Té Verde', 'categoria': 'Bebidas', 'precio': 4.00, 'descripcion': 'Té verde japonés tradicional'},
        {'codigo': 'BEB002', 'nombre': 'Sake Caliente', 'categoria': 'Bebidas', 'precio': 8.00, 'descripcion': 'Sake japonés servido caliente'},
        {'codigo': 'BEB003', 'nombre': 'Coca Cola', 'categoria': 'Bebidas', 'precio': 3.50, 'descripcion': 'Refresco de cola'},
        {'codigo': 'BEB004', 'nombre': 'Agua Mineral', 'categoria': 'Bebidas', 'precio': 2.50, 'descripcion': 'Agua mineral natural'},
        
        # Postres
        {'codigo': 'POST001', 'nombre': 'Mochi de Té Verde', 'categoria': 'Postres', 'precio': 7.00, 'descripcion': 'Helado de té verde en mochi'},
        {'codigo': 'POST002', 'nombre': 'Tempura de Helado', 'categoria': 'Postres', 'precio': 9.00, 'descripcion': 'Helado empanizado y frito'},
        {'codigo': 'POST003', 'nombre': 'Dorayaki', 'categoria': 'Postres', 'precio': 6.00, 'descripcion': 'Pancake japonés con dulce de frijol'},
    ]
    
    for prod_data in productos_data:
        producto, created = ProductoVenta.objects.get_or_create(
            codigo=prod_data['codigo'],
            defaults={
                'nombre': prod_data['nombre'],
                'categoria': categorias[prod_data['categoria']],
                'precio': Decimal(str(prod_data['precio'])),
                'descripcion': prod_data['descripcion'],
                'disponible': True,
                'costo': Decimal(str(prod_data['precio'] * 0.6)),  # Costo estimado 60% del precio
            }
        )
        if created:
            print(f"✓ Producto creado: {producto.nombre} (${producto.precio})")
    
    print("\n🎉 ¡Datos de prueba creados exitosamente!")
    print("\n📋 Resumen:")
    print(f"   • Sucursales: {Sucursal.objects.count()}")
    print(f"   • Mesas: {Mesa.objects.count()}")
    print(f"   • Categorías: {CategoriaProducto.objects.count()}")
    print(f"   • Productos: {ProductoVenta.objects.count()}")
    print(f"   • Usuarios: {Usuario.objects.count()}")
    
    print("\n🔑 Credenciales de prueba:")
    print("   • Mesero: mesero1 / mesero123")
    print("   • Gerente: gerente1 / gerente123")
    print("   • Admin: admin / admin (si existe)")
    
    print("\n🌐 URLs disponibles:")
    print("   • Login: http://127.0.0.1:8000/mesero/login/")
    print("   • Dashboard: http://127.0.0.1:8000/mesero/")
    print("   • Mesas: http://127.0.0.1:8000/mesero/mesas/")
    print("   • Menú: http://127.0.0.1:8000/mesero/menu/")

if __name__ == '__main__':
    crear_datos_mesero()
