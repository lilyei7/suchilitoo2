#!/usr/bin/env python
"""
Script para crear un producto de prueba y verificar la eliminación desde la UI
"""

import os
import django
import sys
import random
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

# Importar modelos
from restaurant.models import ProductoVenta, CategoriaProducto

def crear_producto_prueba():
    """Crea un producto de prueba para verificar la eliminación"""
    print("Creando producto de prueba...")
    
    # Obtener una categoría
    categorias = CategoriaProducto.objects.filter(activo=True)
    if categorias.exists():
        categoria = categorias.first()
    else:
        print("Creando categoría de prueba...")
        categoria = CategoriaProducto.objects.create(
            nombre="Categoría de Prueba",
            descripcion="Categoría creada para pruebas",
            orden=100,
            activo=True
        )
    
    # Crear producto aleatorio
    rand_num = random.randint(1000, 9999)
    producto = ProductoVenta.objects.create(
        codigo=f"TEST-{rand_num}",
        nombre=f"Producto Prueba UI {rand_num}",
        descripcion="Producto creado para probar la eliminación desde la UI",
        precio=Decimal(f"{random.randint(10, 50)}.{random.randint(0, 99):02d}"),
        costo=Decimal(f"{random.randint(5, 30)}.{random.randint(0, 99):02d}"),
        margen=Decimal("0.30"),
        categoria=categoria,
        disponible=True,
        es_promocion=False,
        destacado=False,
        calorias=random.randint(100, 500)
    )
    
    print(f"Producto creado exitosamente:")
    print(f"ID: {producto.id}")
    print(f"Nombre: {producto.nombre}")
    print(f"Código: {producto.codigo}")
    print(f"Precio: ${producto.precio}")
    print(f"Categoría: {producto.categoria.nombre}")
    
    return producto

if __name__ == "__main__":
    crear_producto_prueba()
