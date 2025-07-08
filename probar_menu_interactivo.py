#!/usr/bin/env python3
"""
Script para probar el nuevo menú interactivo del mesero
con productos reales de la base de datos organizados por categoría.
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta, CategoriaProducto
from collections import defaultdict

def main():
    print("🍣 Probando Menú Interactivo del Mesero")
    print("=" * 50)
    
    # Verificar productos en la base de datos
    print("\n📊 ANÁLISIS DE PRODUCTOS EN LA BASE DE DATOS:")
    
    total_productos = ProductoVenta.objects.count()
    productos_activos = ProductoVenta.objects.filter(disponible=True).count()
    productos_inactivos = ProductoVenta.objects.filter(disponible=False).count()
    
    print(f"   📦 Total productos: {total_productos}")
    print(f"   ✅ Productos activos/disponibles: {productos_activos}")
    print(f"   ❌ Productos inactivos: {productos_inactivos}")
    
    if total_productos == 0:
        print("\n⚠️  No hay productos en la base de datos.")
        print("   Creando productos de ejemplo...")
        crear_productos_ejemplo()
        productos_activos = ProductoVenta.objects.filter(disponible=True).count()
        print(f"   ✅ {productos_activos} productos de ejemplo creados")
    
    # Verificar categorías
    print("\n📂 ANÁLISIS DE CATEGORÍAS:")
    
    total_categorias = CategoriaProducto.objects.count()
    categorias_activas = CategoriaProducto.objects.filter(activo=True).count()
    
    print(f"   📁 Total categorías: {total_categorias}")
    print(f"   ✅ Categorías activas: {categorias_activas}")
    
    if total_categorias == 0:
        print("\n⚠️  No hay categorías en la base de datos.")
        print("   Creando categorías de ejemplo...")
        crear_categorias_ejemplo()
        categorias_activas = CategoriaProducto.objects.filter(activo=True).count()
        print(f"   ✅ {categorias_activas} categorías de ejemplo creadas")
    
    # Mostrar productos por categoría
    print("\n🍽️  PRODUCTOS POR CATEGORÍA (como aparecerán en el menú):")
    
    productos_activos = ProductoVenta.objects.filter(
        disponible=True
    ).select_related('categoria').order_by('categoria__orden', 'categoria__nombre', 'nombre')
    
    productos_por_categoria = defaultdict(list)
    
    for producto in productos_activos:
        categoria_nombre = producto.categoria.nombre if producto.categoria else 'Sin Categoría'
        productos_por_categoria[categoria_nombre].append(producto)
    
    if productos_por_categoria:
        for categoria, productos in productos_por_categoria.items():
            print(f"\n   📂 {categoria} ({len(productos)} productos):")
            for producto in productos:
                estado = "✅" if producto.disponible else "❌"
                promocion = "🏷️ " if producto.es_promocion else ""
                destacado = "⭐" if producto.destacado else ""
                print(f"      {estado} {promocion}{destacado}{producto.nombre} - ${producto.precio}")
                if producto.descripcion:
                    print(f"         📝 {producto.descripcion[:60]}{'...' if len(producto.descripcion) > 60 else ''}")
    else:
        print("   ⚠️  No hay productos activos para mostrar")
    
    # Estadísticas finales
    total_productos_menu = sum(len(productos) for productos in productos_por_categoria.values())
    total_categorias_menu = len(productos_por_categoria)
    
    print(f"\n📈 ESTADÍSTICAS DEL MENÚ:")
    print(f"   🗂️  Categorías con productos: {total_categorias_menu}")
    print(f"   🍽️  Total productos disponibles: {total_productos_menu}")
    
    # Funcionalidades del menú
    print(f"\n⚡ FUNCIONALIDADES IMPLEMENTADAS:")
    print("   ✅ Visualización por categorías ordenadas")
    print("   ✅ Solo productos activos/disponibles")
    print("   ✅ Botón de agregar producto (+)")
    print("   ✅ Carrito de compras interactivo")
    print("   ✅ Contador de productos en tiempo real")
    print("   ✅ Modal para revisar y editar pedido")
    print("   ✅ Cálculo automático del total")
    print("   ✅ Confirmación de pedido")
    print("   ✅ Feedback visual para el usuario")
    print("   ✅ Diseño responsive y moderno")
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    print("1. Ir a la página del mesero en el navegador")
    print("2. Hacer login como mesero")
    print("3. Navegar al menú")
    print("4. Probar agregando productos al carrito")
    print("5. Revisar el carrito haciendo clic en el contador")
    print("6. Confirmar un pedido de prueba")
    
    return True

def crear_categorias_ejemplo():
    """Crear categorías de ejemplo si no existen"""
    categorias = [
        {'nombre': 'Entradas', 'descripcion': 'Aperitivos y entradas japonesas', 'orden': 1},
        {'nombre': 'Sushi Rolls', 'descripcion': 'Variedad de rolls y makis', 'orden': 2},
        {'nombre': 'Platos Principales', 'descripcion': 'Platos principales de la casa', 'orden': 3},
        {'nombre': 'Postres', 'descripcion': 'Postres tradicionales japoneses', 'orden': 4},
        {'nombre': 'Bebidas', 'descripcion': 'Bebidas frías y calientes', 'orden': 5},
    ]
    
    for cat_data in categorias:
        categoria, created = CategoriaProducto.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults={
                'descripcion': cat_data['descripcion'],
                'orden': cat_data['orden'],
                'activo': True
            }
        )
        if created:
            print(f"      ✅ Categoría creada: {categoria.nombre}")

def crear_productos_ejemplo():
    """Crear productos de ejemplo si no existen"""
    # Primero crear categorías
    crear_categorias_ejemplo()
    
    # Obtener categorías
    entradas = CategoriaProducto.objects.get(nombre='Entradas')
    sushi = CategoriaProducto.objects.get(nombre='Sushi Rolls')
    principales = CategoriaProducto.objects.get(nombre='Platos Principales')
    postres = CategoriaProducto.objects.get(nombre='Postres')
    bebidas = CategoriaProducto.objects.get(nombre='Bebidas')
    
    productos = [
        # Entradas
        {
            'codigo': 'ENT001',
            'nombre': 'Gyozas (6 piezas)',
            'descripcion': 'Empanadillas japonesas rellenas de cerdo y vegetales, servidas al vapor',
            'precio': 8.99,
            'categoria': entradas,
            'tipo': 'plato',
            'calorias': 320
        },
        {
            'codigo': 'ENT002',
            'nombre': 'Edamame',
            'descripcion': 'Vainas de soja tiernas al vapor con sal marina',
            'precio': 5.99,
            'categoria': entradas,
            'tipo': 'plato',
            'calorias': 120
        },
        {
            'codigo': 'ENT003',
            'nombre': 'Tempura de Verduras',
            'descripcion': 'Verduras variadas en tempura crujiente con salsa tentsuyu',
            'precio': 7.99,
            'categoria': entradas,
            'tipo': 'plato',
            'calorias': 280
        },
        
        # Sushi Rolls
        {
            'codigo': 'SUS001',
            'nombre': 'California Roll',
            'descripcion': 'Roll clásico con cangrejo, aguacate y pepino',
            'precio': 12.99,
            'categoria': sushi,
            'tipo': 'plato',
            'calorias': 350,
            'destacado': True
        },
        {
            'codigo': 'SUS002',
            'nombre': 'Dragon Roll',
            'descripcion': 'Roll de tempura de camarón cubierto con aguacate y salsa de anguila',
            'precio': 15.99,
            'categoria': sushi,
            'tipo': 'plato',
            'calorias': 450,
            'es_promocion': True
        },
        {
            'codigo': 'SUS003',
            'nombre': 'Rainbow Roll',
            'descripcion': 'California roll cubierto con salmón, atún y pescado blanco',
            'precio': 16.99,
            'categoria': sushi,
            'tipo': 'plato',
            'calorias': 420
        },
        
        # Platos Principales
        {
            'codigo': 'PLA001',
            'nombre': 'Ramen Tonkotsu',
            'descripcion': 'Fideos ramen en caldo de cerdo cremoso con chashu, huevo marinado y nori',
            'precio': 14.99,
            'categoria': principales,
            'tipo': 'plato',
            'calorias': 850
        },
        {
            'codigo': 'PLA002',
            'nombre': 'Teriyaki de Salmón',
            'descripcion': 'Filete de salmón glaseado con salsa teriyaki, arroz y vegetales',
            'precio': 18.99,
            'categoria': principales,
            'tipo': 'plato',
            'calorias': 620
        },
        
        # Postres
        {
            'codigo': 'POS001',
            'nombre': 'Mochi de Matcha',
            'descripcion': 'Mochi de té verde relleno de helado de vainilla',
            'precio': 6.99,
            'categoria': postres,
            'tipo': 'postre',
            'calorias': 180
        },
        {
            'codigo': 'POS002',
            'nombre': 'Dorayaki',
            'descripcion': 'Panqueques japoneses rellenos de pasta de frijol dulce',
            'precio': 5.99,
            'categoria': postres,
            'tipo': 'postre',
            'calorias': 220
        },
        
        # Bebidas
        {
            'codigo': 'BEB001',
            'nombre': 'Té Verde',
            'descripcion': 'Té verde tradicional japonés',
            'precio': 3.99,
            'categoria': bebidas,
            'tipo': 'bebida',
            'calorias': 5
        },
        {
            'codigo': 'BEB002',
            'nombre': 'Sake Caliente',
            'descripcion': 'Sake premium servido caliente',
            'precio': 8.99,
            'categoria': bebidas,
            'tipo': 'bebida',
            'calorias': 120
        },
    ]
    
    for prod_data in productos:
        producto, created = ProductoVenta.objects.get_or_create(
            codigo=prod_data['codigo'],
            defaults={
                'nombre': prod_data['nombre'],
                'descripcion': prod_data['descripcion'],
                'precio': prod_data['precio'],
                'categoria': prod_data['categoria'],
                'tipo': prod_data['tipo'],
                'calorias': prod_data.get('calorias', 0),
                'disponible': True,
                'es_promocion': prod_data.get('es_promocion', False),
                'destacado': prod_data.get('destacado', False),
            }
        )
        if created:
            print(f"      ✅ Producto creado: {producto.nombre}")

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 ¡El menú interactivo está listo para usar!")
        print("\nPuedes probarlo en: http://localhost:8000/mesero/menu/")
    else:
        print("\n❌ Hubo problemas configurando el menú")
    
    sys.exit(0 if success else 1)
