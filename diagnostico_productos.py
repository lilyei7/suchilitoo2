#!/usr/bin/env python
"""
Script de diagnóstico para verificar qué productos se están enviando a la plantilla
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta, CategoriaProducto
from django.db.models import Q

def diagnostico_productos():
    print("=" * 70)
    print("🔍 DIAGNÓSTICO COMPLETO - PRODUCTOS VENTA")
    print("=" * 70)
    
    # 1. Verificar productos en la base de datos
    print("\n1️⃣ PRODUCTOS EN LA BASE DE DATOS:")
    todos_productos = ProductoVenta.objects.all()
    print(f"   Total en DB: {todos_productos.count()}")
    
    for producto in todos_productos:
        estado = "ACTIVO" if producto.disponible else "INACTIVO"
        categoria = producto.categoria.nombre if producto.categoria else "Sin categoría"
        print(f"   - ID: {producto.id} | {producto.nombre} | {estado} | Cat: {categoria}")
    
    # 2. Simular exactamente la vista lista_productos_venta
    print("\n2️⃣ SIMULACIÓN EXACTA DE LA VISTA:")
    
    # Paso 1: Query inicial (como en la vista)
    productos = ProductoVenta.objects.select_related('categoria').all()
    print(f"   Query inicial: {productos.count()} productos")
    print(f"   SQL: {productos.query}")
    
    # Paso 2: Ordenamiento (como en la vista)
    productos = productos.order_by('categoria__nombre', 'nombre')
    print(f"   Después de ordenar: {productos.count()} productos")
    
    # Paso 3: Sin filtros GET (simular request sin parámetros)
    categoria_id = None  # request.GET.get('categoria')
    query = None         # request.GET.get('q')
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
        print(f"   Filtro por categoría aplicado: {productos.count()} productos")
        
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | 
            Q(codigo__icontains=query) | 
            Q(descripcion__icontains=query)
        )
        print(f"   Filtro de búsqueda aplicado: {productos.count()} productos")
    
    # Paso 4: Evaluación final (como en la vista)
    productos_final = list(productos)  # Forzar evaluación del queryset
    total_productos = len(productos_final)
    activos = len([p for p in productos_final if p.disponible])
    inactivos = total_productos - activos
    
    print(f"\n3️⃣ RESULTADO FINAL DE LA VISTA:")
    print(f"   Total productos enviados a template: {total_productos}")
    print(f"   Activos: {activos}")
    print(f"   Inactivos: {inactivos}")
    
    print(f"\n   Productos que llegan al template:")
    for producto in productos_final:
        estado = "ACTIVO" if producto.disponible else "INACTIVO"
        categoria = producto.categoria.nombre if producto.categoria else "Sin categoría"
        print(f"   - {producto.nombre} ({estado}) - {categoria}")
    
    # 4. Verificar si hay algún manager personalizado
    print(f"\n4️⃣ VERIFICACIÓN DE MANAGERS:")
    
    # Verificar el manager default
    default_manager = ProductoVenta._default_manager
    print(f"   Manager por defecto: {default_manager}")
    print(f"   Clase del manager: {type(default_manager)}")
    
    # Verificar si .objects es el mismo que _default_manager
    objects_manager = ProductoVenta.objects
    print(f"   Manager .objects: {objects_manager}")
    print(f"   ¿Son el mismo? {default_manager is objects_manager}")
    
    # 5. Verificar directamente con SQL
    print(f"\n5️⃣ VERIFICACIÓN DIRECTA CON SQL:")
    from django.db import connection
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nombre, disponible FROM restaurant_productoventa ORDER BY nombre")
        rows = cursor.fetchall()
        print(f"   Productos desde SQL directo: {len(rows)}")
        for row in rows:
            estado = "ACTIVO" if row[2] else "INACTIVO"
            print(f"   - ID: {row[0]} | {row[1]} | {estado}")
    
    # 6. Problema potencial identificado
    print(f"\n6️⃣ ANÁLISIS DEL PROBLEMA:")
    
    if total_productos < todos_productos.count():
        print("   ❌ PROBLEMA ENCONTRADO: La vista no devuelve todos los productos")
        print("      Algún filtro oculto está eliminando productos")
    elif inactivos == 0 and todos_productos.filter(disponible=False).exists():
        print("   ❌ PROBLEMA ENCONTRADO: Hay productos inactivos en DB pero no llegan a la vista")
    elif total_productos == todos_productos.count() and inactivos > 0:
        print("   ✅ La vista está correcta - debe ser un problema en el template")
    else:
        print("   ⚠️  Situación ambigua - revisar logs del servidor")
    
    return productos_final

if __name__ == "__main__":
    productos = diagnostico_productos()
