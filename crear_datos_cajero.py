#!/usr/bin/env python
"""
Script para crear datos de prueba para el app de cajero
Ejecutar: python manage.py shell < crear_datos_cajero.py
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Usuario, Sucursal, Rol
from restaurant.models import ProductoVenta, CategoriaProducto
from decimal import Decimal

User = get_user_model()

def crear_datos_cajero():
    print("Creando datos de prueba para el app de cajero...")
    
    # 1. Crear o obtener sucursal
    sucursal, created = Sucursal.objects.get_or_create(
        nombre="Sucursal Principal",
        defaults={
            'direccion': 'Av. Principal 123',
            'telefono': '555-1234',
            'activa': True
        }
    )
    if created:
        print(f"✓ Sucursal creada: {sucursal.nombre}")
    else:
        print(f"✓ Sucursal existente: {sucursal.nombre}")
    
    # 2. Crear rol de cajero
    rol_cajero, created = Rol.objects.get_or_create(
        nombre='cajero',
        defaults={'descripcion': 'Cajero del restaurante'}
    )
    if created:
        print(f"✓ Rol cajero creado")
    
    # 3. Crear usuario cajero de prueba
    try:
        cajero = Usuario.objects.get(username='cajero1')
        print(f"✓ Usuario cajero existente: {cajero.username}")
    except Usuario.DoesNotExist:
        cajero = Usuario.objects.create_user(
            username='cajero1',
            email='cajero1@sushi.com',
            password='123456',
            first_name='Juan',
            last_name='Pérez',
            sucursal=sucursal,
            rol=rol_cajero
        )
        print(f"✓ Usuario cajero creado: {cajero.username}")
    
    # 4. Asignar sucursal y rol si no los tiene
    if not cajero.sucursal:
        cajero.sucursal = sucursal
        cajero.save()
        print(f"✓ Sucursal asignada al cajero")
    
    if not cajero.rol:
        cajero.rol = rol_cajero
        cajero.save()
        print(f"✓ Rol asignado al cajero")
    
    # 5. Crear categorías de productos
    categorias_data = [
        {'nombre': 'Sushi', 'descripcion': 'Rollos y piezas de sushi'},
        {'nombre': 'Sashimi', 'descripcion': 'Cortes de pescado fresco'},
        {'nombre': 'Entradas', 'descripcion': 'Aperitivos y entradas'},
        {'nombre': 'Bebidas', 'descripcion': 'Bebidas frías y calientes'},
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
    
    # 6. Crear productos de ejemplo
    productos_data = [
        # Sushi
        {'nombre': 'California Roll', 'categoria': 'Sushi', 'precio': 12.50, 'descripcion': 'Rollo con cangrejo, aguacate y pepino'},
        {'nombre': 'Philadelphia Roll', 'categoria': 'Sushi', 'precio': 14.00, 'descripcion': 'Rollo con salmón, queso crema y pepino'},
        {'nombre': 'Spicy Tuna Roll', 'categoria': 'Sushi', 'precio': 15.50, 'descripcion': 'Rollo picante de atún'},
        {'nombre': 'Dragon Roll', 'categoria': 'Sushi', 'precio': 18.00, 'descripcion': 'Rollo especial con anguila y aguacate'},
        
        # Sashimi
        {'nombre': 'Sashimi de Salmón', 'categoria': 'Sashimi', 'precio': 16.00, 'descripcion': '6 piezas de salmón fresco'},
        {'nombre': 'Sashimi de Atún', 'categoria': 'Sashimi', 'precio': 18.00, 'descripcion': '6 piezas de atún fresco'},
        {'nombre': 'Sashimi Mixto', 'categoria': 'Sashimi', 'precio': 22.00, 'descripcion': 'Variedad de pescados frescos'},
        
        # Entradas
        {'nombre': 'Gyoza', 'categoria': 'Entradas', 'precio': 8.50, 'descripcion': 'Empanadillas japonesas (6 piezas)'},
        {'nombre': 'Edamame', 'categoria': 'Entradas', 'precio': 5.50, 'descripcion': 'Vainas de soja cocidas'},
        {'nombre': 'Tempura de Vegetales', 'categoria': 'Entradas', 'precio': 9.00, 'descripcion': 'Vegetales en tempura crujiente'},
        {'nombre': 'Sopa Miso', 'categoria': 'Entradas', 'precio': 4.50, 'descripcion': 'Sopa tradicional japonesa'},
        
        # Bebidas
        {'nombre': 'Té Verde', 'categoria': 'Bebidas', 'precio': 3.00, 'descripcion': 'Té verde japonés caliente'},
        {'nombre': 'Sake Caliente', 'categoria': 'Bebidas', 'precio': 8.00, 'descripcion': 'Sake tradicional servido caliente'},
        {'nombre': 'Coca Cola', 'categoria': 'Bebidas', 'precio': 2.50, 'descripcion': 'Refresco de cola 350ml'},
        {'nombre': 'Agua Mineral', 'categoria': 'Bebidas', 'precio': 2.00, 'descripcion': 'Agua mineral 500ml'},
        
        # Postres
        {'nombre': 'Mochi', 'categoria': 'Postres', 'precio': 6.00, 'descripcion': 'Dulce japonés de arroz (3 piezas)'},
        {'nombre': 'Helado Tempura', 'categoria': 'Postres', 'precio': 7.50, 'descripcion': 'Helado envuelto en tempura'},
        {'nombre': 'Dorayaki', 'categoria': 'Postres', 'precio': 5.50, 'descripcion': 'Pancake japonés relleno'},
    ]
    
    for prod_data in productos_data:
        # Generar un código único para el producto
        codigo = prod_data['nombre'].replace(' ', '').upper()[:10]
        
        producto, created = ProductoVenta.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': prod_data['nombre'],
                'categoria': categorias[prod_data['categoria']],
                'precio': Decimal(str(prod_data['precio'])),
                'descripcion': prod_data['descripcion'],
                'disponible': True,
                'tipo': 'plato'
            }
        )
        if created:
            print(f"✓ Producto creado: {producto.nombre} - ${producto.precio}")
    
    print("\n" + "="*50)
    print("DATOS DE PRUEBA CREADOS EXITOSAMENTE")
    print("="*50)
    print(f"Usuario cajero: cajero1")
    print(f"Contraseña: 123456")
    print(f"Sucursal: {sucursal.nombre}")
    print(f"Productos creados: {ProductoVenta.objects.count()}")
    print(f"Categorías creadas: {CategoriaProducto.objects.count()}")
    print("\nAccede a: http://127.0.0.1:8000/cajero/")
    print("="*50)

if __name__ == "__main__":
    crear_datos_cajero()
