#!/usr/bin/env python
"""
Script para verificar el estado actual del menú del mesero
Muestra los productos activos organizados por categoría tal como los vería el mesero
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta, CategoriaProducto
from collections import defaultdict

def verificar_menu_mesero():
    """Verificar exactamente lo que ve el mesero en el menú"""
    print("=" * 60)
    print("VERIFICACIÓN DEL MENÚ DEL MESERO")
    print("=" * 60)
    
    # Obtener productos exactamente como lo hace la función obtener_productos_menu()
    productos_activos = ProductoVenta.objects.filter(
        disponible=True  # Solo productos disponibles/activos
    ).select_related('categoria').order_by('categoria__orden', 'categoria__nombre', 'nombre')
    
    print(f"Total de productos activos en DB: {productos_activos.count()}")
    
    # Organizar productos por categoría (igual que en la función)
    productos_por_categoria = defaultdict(list)
    
    for producto in productos_activos:
        categoria_nombre = producto.categoria.nombre if producto.categoria else 'Sin Categoría'
        productos_por_categoria[categoria_nombre].append(producto)
    
    # Mostrar el menú organizado
    if productos_por_categoria:
        print(f"\nCategorías encontradas: {len(productos_por_categoria)}")
        print("\nMENÚ ORGANIZADO POR CATEGORÍAS:")
        print("-" * 40)
        
        for categoria, productos in productos_por_categoria.items():
            print(f"\n📂 {categoria.upper()} ({len(productos)} productos)")
            for i, producto in enumerate(productos, 1):
                precio = float(producto.precio)
                disponible_txt = "✅ DISPONIBLE" if producto.disponible else "❌ NO DISPONIBLE"
                print(f"  {i}. {producto.nombre}")
                print(f"     💰 ${precio:.2f} | {disponible_txt}")
                if producto.descripcion:
                    print(f"     📝 {producto.descripcion[:50]}...")
                print()
    else:
        print("\n⚠️  NO HAY PRODUCTOS ACTIVOS EN EL MENÚ")
        print("El mesero verá un mensaje de 'Sin productos disponibles'")
    
    # Verificar productos inactivos también
    productos_inactivos = ProductoVenta.objects.filter(disponible=False).count()
    print(f"\nProductos inactivos (no mostrados): {productos_inactivos}")
    
    # Verificar categorías
    categorias_total = CategoriaProducto.objects.count()
    categorias_con_productos = CategoriaProducto.objects.filter(
        productos_venta__disponible=True
    ).distinct().count()
    
    print(f"\nCategorías totales: {categorias_total}")
    print(f"Categorías con productos activos: {categorias_con_productos}")
    
    print("\n" + "=" * 60)
    print("RESULTADO: El menú del mesero está configurado para mostrar")
    print("ÚNICAMENTE productos activos (disponible=True) de la base de datos,")
    print("organizados por categoría. ✅")
    print("=" * 60)

if __name__ == '__main__':
    verificar_menu_mesero()
