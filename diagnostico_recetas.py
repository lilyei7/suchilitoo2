#!/usr/bin/env python
import os
import sys

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suchilitoo2.settings')

import django
django.setup()

from dashboard.models import *
from dashboard.models_ventas import *

print("=== DIAGNÓSTICO DE RELACIÓN PRODUCTO-RECETA ===")
print()

# Buscar el producto xxx2 (alga nori)
productos = ProductoVenta.objects.filter(nombre__icontains="xxx2")
print(f"Productos que contienen 'xxx2': {productos.count()}")
for p in productos:
    print(f"  - {p.id}: {p.nombre}")

# También buscar por alga nori
productos_alga = ProductoVenta.objects.filter(nombre__icontains="alga")
print(f"\nProductos que contienen 'alga': {productos_alga.count()}")
for p in productos_alga:
    print(f"  - {p.id}: {p.nombre}")

# También buscar por nori
productos_nori = ProductoVenta.objects.filter(nombre__icontains="nori")
print(f"\nProductos que contienen 'nori': {productos_nori.count()}")
for p in productos_nori:
    print(f"  - {p.id}: {p.nombre}")

# Buscar todos los productos y sus recetas
print("\n=== TODOS LOS PRODUCTOS DE VENTA ===")
todos_productos = ProductoVenta.objects.all()
print(f"Total productos: {todos_productos.count()}")

for producto in todos_productos:
    print(f"\nProducto: {producto.id} - {producto.nombre}")
    
    # Verificar si tiene receta directa (OneToOneField)
    try:
        receta_directa = producto.receta
        if receta_directa:
            print(f"  ✅ Receta directa: {receta_directa.id} - {receta_directa.nombre if hasattr(receta_directa, 'nombre') else 'Sin nombre'}")
        else:
            print(f"  ❌ No tiene receta directa")
    except Exception as e:
        print(f"  ❌ Error accediendo receta directa: {e}")
    
    # Verificar si tiene relaciones ProductoReceta
    try:
        relaciones = ProductoReceta.objects.filter(producto=producto)
        print(f"  Relaciones ProductoReceta: {relaciones.count()}")
        for rel in relaciones:
            print(f"    - Receta: {rel.receta.id} - {rel.receta.nombre if hasattr(rel.receta, 'nombre') else 'Sin nombre'}")
    except Exception as e:
        print(f"  ❌ Error accediendo relaciones: {e}")

# Buscar recetas que contengan "nori"
print("\n=== RECETAS QUE CONTIENEN 'NORI' ===")
recetas_nori = Receta.objects.filter(nombre__icontains="nori")
print(f"Total recetas con 'nori': {recetas_nori.count()}")
for receta in recetas_nori:
    print(f"  - {receta.id}: {receta.nombre}")
    # Verificar si tiene producto asociado
    try:
        if hasattr(receta, 'producto') and receta.producto:
            print(f"    ✅ Producto asociado: {receta.producto.id} - {receta.producto.nombre}")
        else:
            print(f"    ❌ No tiene producto asociado")
    except Exception as e:
        print(f"    ❌ Error verificando producto: {e}")

print("\n=== VERIFICANDO ESTRUCTURA DE MODELOS ===")
print(f"Modelo ProductoVenta: {ProductoVenta}")
print(f"Modelo Receta: {Receta}")
print(f"Modelo ProductoReceta: {ProductoReceta}")

# Verificar los campos del modelo ProductoVenta
print(f"\nCampos de ProductoVenta:")
for field in ProductoVenta._meta.fields:
    print(f"  - {field.name}: {field.__class__.__name__}")

# Verificar los campos del modelo Receta
print(f"\nCampos de Receta:")
for field in Receta._meta.fields:
    print(f"  - {field.name}: {field.__class__.__name__}")
