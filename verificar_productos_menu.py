#!/usr/bin/env python3
"""
Script para verificar qué productos están disponibles en la base de datos
y asegurar que el menú del mesero muestre solo datos reales.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta, CategoriaProducto
from collections import defaultdict

def main():
    print("🔍 Verificando productos disponibles en la base de datos...")
    print("=" * 60)
    
    # Obtener todas las categorías
    categorias = CategoriaProducto.objects.filter(activo=True).order_by('nombre')
    print(f"📂 Categorías activas encontradas: {categorias.count()}")
    for categoria in categorias:
        print(f"   - {categoria.nombre} (Orden: {categoria.orden})")
    
    # Obtener todos los productos
    productos_totales = ProductoVenta.objects.all()
    productos_activos = ProductoVenta.objects.filter(disponible=True)
    
    print(f"\n📦 Productos en total: {productos_totales.count()}")
    print(f"✅ Productos activos/disponibles: {productos_activos.count()}")
    print(f"❌ Productos inactivos: {productos_totales.count() - productos_activos.count()}")
    
    # Mostrar productos activos organizados por categoría
    print(f"\n📋 PRODUCTOS ACTIVOS POR CATEGORÍA:")
    print("-" * 40)
    
    productos_por_categoria = defaultdict(list)
    
    for producto in productos_activos.select_related('categoria'):
        categoria_nombre = producto.categoria.nombre if producto.categoria else 'Sin Categoría'
        productos_por_categoria[categoria_nombre].append(producto)
    
    if productos_por_categoria:
        for categoria, productos in productos_por_categoria.items():
            print(f"\n🏷️  {categoria} ({len(productos)} productos):")
            for producto in productos:
                precio_texto = f"${producto.precio:.2f}" if producto.precio else "Sin precio"
                disponible_texto = "✅" if producto.disponible else "❌"
                print(f"   {disponible_texto} {producto.nombre} - {precio_texto}")
                if producto.descripcion:
                    print(f"      📝 {producto.descripcion[:60]}...")
    else:
        print("❌ No hay productos activos en la base de datos")
    
    # Verificar si hay productos sin categoría
    productos_sin_categoria = productos_activos.filter(categoria__isnull=True)
    if productos_sin_categoria.exists():
        print(f"\n⚠️  Productos activos sin categoría: {productos_sin_categoria.count()}")
        for producto in productos_sin_categoria:
            print(f"   - {producto.nombre}")
    
    print(f"\n📊 RESUMEN PARA EL MENÚ DEL MESERO:")
    print("-" * 40)
    total_categorias = len(productos_por_categoria)
    total_productos = sum(len(productos) for productos in productos_por_categoria.values())
    
    print(f"✅ Categorías con productos: {total_categorias}")
    print(f"✅ Total de productos disponibles: {total_productos}")
    
    if total_productos == 0:
        print("\n🚨 PROBLEMA: No hay productos activos para mostrar en el menú")
        print("💡 Soluciones:")
        print("   1. Crear productos nuevos en el dashboard de administración")
        print("   2. Activar productos existentes (cambiar disponible=True)")
        print("   3. Asignar categorías a los productos existentes")
    else:
        print(f"\n✅ El menú del mesero puede mostrar {total_productos} productos organizados en {total_categorias} categorías")
    
    return total_productos > 0

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Base de datos lista para el menú del mesero")
    else:
        print("\n❌ Se requiere configurar productos en la base de datos")
    
    sys.exit(0 if success else 1)
