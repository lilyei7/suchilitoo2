import os
import django
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

# Ahora ejecutar las consultas
from dashboard.models import *
from dashboard.models_ventas import *

def diagnose_recipes():
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

    # Buscar todos los productos y verificar sus recetas
    print("\n=== VERIFICACIÓN DE RECETAS ===")
    todos_productos = ProductoVenta.objects.all()
    print(f"Total productos: {todos_productos.count()}")

    for producto in todos_productos:
        print(f"\nProducto: {producto.id} - {producto.nombre}")
        
        # Verificar si tiene receta directa (campo receta)
        try:
            if hasattr(producto, 'receta') and producto.receta:
                print(f"  ✅ Receta directa: {producto.receta.id}")
            else:
                print(f"  ❌ No tiene receta directa")
        except Exception as e:
            print(f"  ❌ Error accediendo receta directa: {e}")
        
        # Verificar si tiene relaciones ProductoReceta
        try:
            relaciones = ProductoReceta.objects.filter(producto=producto)
            print(f"  Relaciones ProductoReceta: {relaciones.count()}")
            for rel in relaciones:
                print(f"    - Receta: {rel.receta.id}")
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

if __name__ == "__main__":
    diagnose_recipes()
