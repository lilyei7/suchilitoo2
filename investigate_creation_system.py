import os
import django
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

# Ahora ejecutar las consultas
from dashboard.models import *
from dashboard.models_ventas import *
from restaurant.models_producto_receta import ProductoReceta

def investigate_producto_creation_system():
    print("=== INVESTIGACIÓN DEL SISTEMA DE CREACIÓN DE PRODUCTOS ===")
    print()
    
    # 1. Verificar el modelo ProductoReceta
    print("1. VERIFICANDO MODELO ProductoReceta")
    try:
        relaciones = ProductoReceta.objects.all()
        print(f"Total relaciones ProductoReceta: {relaciones.count()}")
        
        for rel in relaciones:
            print(f"  - ProductoReceta ID: {rel.id}")
            print(f"    Producto: {rel.producto.id} - {rel.producto.nombre}")
            print(f"    Receta: {rel.receta.id}")
            print()
    except Exception as e:
        print(f"❌ Error con ProductoReceta: {e}")
    
    # 2. Verificar las recetas directas
    print("2. VERIFICANDO RECETAS DIRECTAS (OneToOneField)")
    recetas = Receta.objects.all()
    print(f"Total recetas: {recetas.count()}")
    
    for receta in recetas:
        print(f"  - Receta ID: {receta.id}")
        print(f"    Producto directo: {receta.producto.id if receta.producto else 'None'} - {receta.producto.nombre if receta.producto else 'None'}")
        print(f"    Tiempo: {receta.tiempo_preparacion} min")
        print(f"    Activo: {receta.activo}")
        print()
    
    # 3. Verificar el producto xxx2 específicamente
    print("3. VERIFICANDO PRODUCTO xxx2 EN AMBOS SISTEMAS")
    try:
        producto_xxx2 = ProductoVenta.objects.get(id=121)
        print(f"Producto: {producto_xxx2.nombre} (ID: {producto_xxx2.id})")
        
        # Verificar en ProductoReceta
        relaciones_xxx2 = ProductoReceta.objects.filter(producto=producto_xxx2)
        print(f"  Relaciones ProductoReceta: {relaciones_xxx2.count()}")
        for rel in relaciones_xxx2:
            print(f"    - Receta {rel.receta.id}")
        
        # Verificar receta directa
        try:
            receta_directa = producto_xxx2.receta
            if receta_directa:
                print(f"  ✅ Receta directa: {receta_directa.id}")
            else:
                print(f"  ❌ No tiene receta directa")
        except Exception as e:
            print(f"  ❌ Error accediendo receta directa: {e}")
            
    except ProductoVenta.DoesNotExist:
        print("❌ Producto xxx2 no encontrado")
    
    # 4. Verificar si hay inconsistencias
    print("4. VERIFICANDO INCONSISTENCIAS EN EL SISTEMA")
    print()
    
    # Productos que tienen ProductoReceta pero no receta directa
    productos_con_inconsistencias = []
    for producto in ProductoVenta.objects.all():
        tiene_producto_receta = ProductoReceta.objects.filter(producto=producto).exists()
        try:
            tiene_receta_directa = bool(producto.receta)
        except:
            tiene_receta_directa = False
            
        if tiene_producto_receta != tiene_receta_directa:
            productos_con_inconsistencias.append({
                'producto': producto,
                'tiene_producto_receta': tiene_producto_receta,
                'tiene_receta_directa': tiene_receta_directa
            })
    
    print(f"Productos con inconsistencias: {len(productos_con_inconsistencias)}")
    for item in productos_con_inconsistencias:
        producto = item['producto']
        print(f"  - {producto.id}: {producto.nombre}")
        print(f"    ProductoReceta: {'✅' if item['tiene_producto_receta'] else '❌'}")
        print(f"    Receta directa: {'✅' if item['tiene_receta_directa'] else '❌'}")

if __name__ == "__main__":
    investigate_producto_creation_system()
