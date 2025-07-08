#!/usr/bin/env python
"""
Script para crear productos de prueba para testing de eliminación
"""

import os
import django
import random
import sys
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

# Importar modelos
from restaurant.models import ProductoVenta, CategoriaProducto, Insumo
from django.contrib.auth.models import User

def crear_producto_prueba(nombre=None, precio=None, categoria_id=None):
    """Crea un producto de prueba para testing de eliminación"""
    if nombre is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre = f"Producto Test {timestamp}"
    
    if precio is None:
        precio = random.randint(1000, 5000)  # Precio entre 1000 y 5000
    
    # Obtener una categoría existente o crear una por defecto
    if categoria_id:
        try:
            categoria = CategoriaProducto.objects.get(id=categoria_id)
        except CategoriaProducto.DoesNotExist:
            print(f"Categoría con ID {categoria_id} no existe. Usando una categoría aleatoria.")
            categorias = CategoriaProducto.objects.all()
            if categorias.exists():
                categoria = random.choice(categorias)
            else:
                categoria = CategoriaProducto.objects.create(nombre="Categoría Test")
    else:
        categorias = CategoriaProducto.objects.all()
        if categorias.exists():
            categoria = random.choice(categorias)
        else:
            categoria = CategoriaProducto.objects.create(nombre="Categoría Test")
    
    # Crear el producto
    producto = ProductoVenta.objects.create(
        codigo=f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}",
        nombre=nombre,
        precio=precio,
        descripcion=f"Producto de prueba para testing de eliminación. Creado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        imagen="default.jpg",  # Imagen por defecto
        categoria=categoria,
        disponible=True,
        tipo='plato'
    )
    
    print(f"Producto creado: {producto.nombre} (ID: {producto.id})")
    print(f"Precio: ${producto.precio}")
    print(f"Categoría: {producto.categoria.nombre} (ID: {producto.categoria.id})")
    
    return producto

def main():
    """Función principal"""
    print("="*50)
    print("CREADOR DE PRODUCTOS DE PRUEBA")
    print("="*50)
    
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Django version: {django.get_version()}")
    print(f"Python version: {sys.version}")
    
    # Opciones
    print("\nOpciones:")
    print("1. Crear producto con datos automáticos")
    print("2. Crear producto con datos personalizados")
    print("3. Crear múltiples productos de prueba")
    
    try:
        opcion = int(input("\nSeleccione una opción (1-3): "))
    except ValueError:
        opcion = 1  # Por defecto opción 1
    
    if opcion == 1:
        # Producto con datos automáticos
        producto = crear_producto_prueba()
        print("\nProducto de prueba creado con éxito:")
        print(f"ID: {producto.id}")
        print(f"Nombre: {producto.nombre}")
        print(f"Precio: ${producto.precio}")
        print(f"Categoría: {producto.categoria.nombre}")
    
    elif opcion == 2:
        # Producto con datos personalizados
        nombre = input("\nNombre del producto: ")
        if not nombre:
            nombre = f"Producto Test {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            precio = int(input("Precio del producto: "))
        except ValueError:
            precio = random.randint(1000, 5000)
        
        try:
            categoria_id = int(input("ID de la categoría (o Enter para usar una aleatoria): "))
        except ValueError:
            categoria_id = None
        
        producto = crear_producto_prueba(nombre, precio, categoria_id)
        print("\nProducto personalizado creado con éxito:")
        print(f"ID: {producto.id}")
        print(f"Nombre: {producto.nombre}")
        print(f"Precio: ${producto.precio}")
        print(f"Categoría: {producto.categoria.nombre}")
    
    elif opcion == 3:
        # Crear múltiples productos
        try:
            cantidad = int(input("\nCantidad de productos a crear: "))
            if cantidad <= 0:
                cantidad = 5
        except ValueError:
            cantidad = 5
        
        print(f"\nCreando {cantidad} productos de prueba...")
        productos = []
        
        for i in range(cantidad):
            nombre = f"Producto Test {i+1} - {datetime.now().strftime('%H%M%S')}"
            producto = crear_producto_prueba(nombre)
            productos.append(producto)
        
        print("\nProductos creados:")
        for p in productos:
            print(f"- ID: {p.id}, Nombre: {p.nombre}, Precio: ${p.precio}, Categoría: {p.categoria.nombre}")
    
    else:
        print("Opción no válida.")

if __name__ == "__main__":
    main()
