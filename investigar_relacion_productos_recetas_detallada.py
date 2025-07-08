#!/usr/bin/env python
"""
Script para investigar la relación detallada entre ProductoVenta y Receta
Enfocado en productos que pueden tener hasta 2 recetas
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

try:
    django.setup()
except Exception as e:
    print(f"Error al configurar Django: {e}")
    sys.exit(1)

from restaurant.models import ProductoVenta, Receta, Insumo, RecetaInsumo

def investigar_productos_con_multiples_recetas():
    """Investigar productos que tienen múltiples recetas"""
    print("🔍 INVESTIGANDO PRODUCTOS CON MÚLTIPLES RECETAS")
    print("=" * 60)
    
    # Buscar productos que tienen recetas (relación OneToOne)
    productos_con_recetas = {}
    
    # Debido a que es OneToOneField, buscamos directamente las recetas
    recetas = Receta.objects.all()
    
    for receta in recetas:
        if receta.producto:
            producto_id = receta.producto.id
            if producto_id not in productos_con_recetas:
                productos_con_recetas[producto_id] = {
                    'producto': receta.producto,
                    'recetas': [],
                    'count': 0
                }
            productos_con_recetas[producto_id]['recetas'].append(receta)
            productos_con_recetas[producto_id]['count'] += 1
    
    print(f"\n📊 Total de productos con recetas: {len(productos_con_recetas)}")
    
    # Productos con múltiples recetas (esto sería extraño con OneToOneField)
    productos_multiples = {k: v for k, v in productos_con_recetas.items() if v['count'] > 1}
    print(f"📊 Productos con múltiples recetas: {len(productos_multiples)}")
    
    # Productos sin recetas
    productos_sin_recetas = ProductoVenta.objects.exclude(
        id__in=productos_con_recetas.keys()
    )
    print(f"📊 Productos SIN recetas: {productos_sin_recetas.count()}")
    
    return productos_con_recetas, productos_multiples, productos_sin_recetas

def mostrar_productos_multiples_recetas(productos_multiples):
    """Mostrar detalles de productos con múltiples recetas"""
    print("\n\n🔍 PRODUCTOS CON MÚLTIPLES RECETAS")
    print("=" * 60)
    
    if not productos_multiples:
        print("❌ No hay productos con múltiples recetas")
        return
    
    for producto_data in productos_multiples.values():
        producto = producto_data['producto']
        recetas = producto_data['recetas']
        
        print(f"\n🍽️ Producto: {producto.nombre}")
        print(f"   ID: {producto.id}")
        print(f"   Precio: ${producto.precio}")
        print(f"   Cantidad de recetas: {len(recetas)}")
        
        for i, receta in enumerate(recetas, 1):
            print(f"\n   📝 Receta {i}: {receta.nombre}")
            print(f"      ID: {receta.id}")
            print(f"      Rendimiento: {receta.rendimiento}")
            
            # Mostrar insumos de esta receta
            receta_insumos = RecetaInsumo.objects.filter(receta=receta)
            if receta_insumos.exists():
                print(f"      Insumos ({receta_insumos.count()}):")
                for ri in receta_insumos:
                    print(f"        • {ri.insumo.nombre}: {ri.cantidad} {ri.insumo.unidad_medida}")
                else:
                    print(f"        • {ri.insumo.nombre}: {ri.cantidad}")  # Sin unidad si no existe
            else:
                print(f"      ❌ Sin insumos definidos")

def mostrar_productos_sin_recetas(productos_sin_recetas):
    """Mostrar productos que no tienen recetas"""
    print("\n\n❌ PRODUCTOS SIN RECETAS")
    print("=" * 60)
    
    if not productos_sin_recetas.exists():
        print("✅ Todos los productos tienen recetas")
        return
    
    print(f"Total: {productos_sin_recetas.count()}")
    
    for producto in productos_sin_recetas:
        print(f"\n🍽️ {producto.nombre}")
        print(f"   ID: {producto.id}")
        print(f"   Precio: ${producto.precio}")
        print(f"   Disponible: {producto.disponible}")

def investigar_casos_especificos():
    """Investigar casos específicos mencionados"""
    print("\n\n🔍 CASOS ESPECÍFICOS")
    print("=" * 60)
    
    casos = [
        "algas con nalgas",
        "algas alas algas con algas",
        "alga nori"
    ]
    
    for caso in casos:
        print(f"\n🔍 Buscando: '{caso}'")
        
        # Buscar en productos
        productos = ProductoVenta.objects.filter(nombre__icontains=caso)
        print(f"   Productos encontrados: {productos.count()}")
        
        for producto in productos:
            recetas = Receta.objects.filter(producto=producto)
            print(f"   • {producto.nombre} (ID: {producto.id}) - {recetas.count()} recetas")
            
            for receta in recetas:
                print(f"     - Receta: {receta.nombre} (ID: {receta.id})")

def analizar_logica_seleccion_receta():
    """Analizar cómo se debería seleccionar la receta correcta"""
    print("\n\n🤔 ANÁLISIS: LÓGICA DE SELECCIÓN DE RECETA")
    print("=" * 60)
    
    print("❓ PREGUNTAS CLAVE:")
    print("1. ¿Cuándo un producto tiene 2 recetas, cuál se debe usar?")
    print("2. ¿Hay algún campo que indique la receta 'principal' o 'activa'?")
    print("3. ¿Las 2 recetas son para diferentes tamaños/porciones?")
    print("4. ¿O son recetas alternativas para el mismo producto?")
    
    # Revisar campos de la tabla Receta
    from django.db import connection
    
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(mesero_receta)")
        columns = cursor.fetchall()
        
        print(f"\n📋 CAMPOS DE LA TABLA 'Receta':")
        for col in columns:
            print(f"   • {col[1]} ({col[2]})")

def main():
    print("🔍 INVESTIGACIÓN DETALLADA: PRODUCTOS Y RECETAS")
    print("=" * 80)
    
    # Investigar productos con múltiples recetas
    productos_con_recetas, productos_multiples, productos_sin_recetas = investigar_productos_con_multiples_recetas()
    
    # Mostrar detalles
    mostrar_productos_multiples_recetas(productos_multiples)
    mostrar_productos_sin_recetas(productos_sin_recetas)
    
    # Investigar casos específicos
    investigar_casos_especificos()
    
    # Analizar lógica de selección
    analizar_logica_seleccion_receta()
    
    print("\n" + "=" * 80)
    print("🎯 CONCLUSIONES:")
    print("• Necesitamos definir la lógica para seleccionar la receta correcta")
    print("• cuando un producto tiene múltiples recetas")
    print("• Esto afecta directamente la deducción de inventario")

if __name__ == "__main__":
    main()
