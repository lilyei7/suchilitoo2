import os
import django
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

# Ahora ejecutar las consultas
from dashboard.models import *
from dashboard.models_ventas import *

def investigate_recetas():
    print("=== INVESTIGACIÓN DETALLADA DE RECETAS ===")
    print()
    
    # Verificar todas las recetas
    print("=== TODAS LAS RECETAS ===")
    recetas = Receta.objects.all()
    print(f"Total recetas: {recetas.count()}")
    
    for receta in recetas:
        print(f"\nReceta ID: {receta.id}")
        print(f"  - Producto ID: {receta.producto_id}")
        print(f"  - Tiempo preparación: {receta.tiempo_preparacion}")
        print(f"  - Porciones: {receta.porciones}")
        print(f"  - Activo: {receta.activo}")
        print(f"  - Instrucciones: {receta.instrucciones[:50] if receta.instrucciones else 'N/A'}...")
        
        # Verificar el producto asociado
        if receta.producto:
            print(f"  - Producto asociado: {receta.producto.id} - {receta.producto.nombre}")
        else:
            print(f"  - ❌ No tiene producto asociado")
    
    print("\n=== PRODUCTOS SIN RECETA ===")
    productos_sin_receta = []
    todos_productos = ProductoVenta.objects.all()
    
    for producto in todos_productos:
        try:
            receta = producto.receta
            if not receta:
                productos_sin_receta.append(producto)
        except Exception:
            productos_sin_receta.append(producto)
    
    print(f"Productos sin receta: {len(productos_sin_receta)}")
    for producto in productos_sin_receta:
        print(f"  - {producto.id}: {producto.nombre}")
    
    print("\n=== VERIFICANDO PRODUCTO xxx2 ESPECÍFICAMENTE ===")
    try:
        producto_xxx2 = ProductoVenta.objects.get(id=121)
        print(f"Producto xxx2 encontrado: {producto_xxx2.nombre}")
        
        # Verificar si tiene receta
        try:
            receta = producto_xxx2.receta
            if receta:
                print(f"  ✅ Tiene receta: {receta.id}")
            else:
                print(f"  ❌ No tiene receta asignada")
        except Exception as e:
            print(f"  ❌ Error accediendo receta: {e}")
            
        # Buscar recetas huérfanas que podrían ser para este producto
        print("\n  Buscando recetas huérfanas...")
        recetas_huerfanas = Receta.objects.filter(producto=None)
        print(f"  Recetas sin producto: {recetas_huerfanas.count()}")
        
        for receta in recetas_huerfanas:
            print(f"    - Receta ID: {receta.id}, Instrucciones: {receta.instrucciones[:30] if receta.instrucciones else 'N/A'}...")
            
    except ProductoVenta.DoesNotExist:
        print("Producto xxx2 no encontrado")
    
    print("\n=== VERIFICANDO PRODUCTO nalga nori ESPECÍFICAMENTE ===")
    try:
        producto_nori = ProductoVenta.objects.get(id=120)
        print(f"Producto nalga nori encontrado: {producto_nori.nombre}")
        
        # Verificar si tiene receta
        try:
            receta = producto_nori.receta
            if receta:
                print(f"  ✅ Tiene receta: {receta.id}")
                print(f"  - Instrucciones: {receta.instrucciones[:50] if receta.instrucciones else 'N/A'}...")
            else:
                print(f"  ❌ No tiene receta asignada")
        except Exception as e:
            print(f"  ❌ Error accediendo receta: {e}")
            
    except ProductoVenta.DoesNotExist:
        print("Producto nalga nori no encontrado")

if __name__ == "__main__":
    investigate_recetas()
