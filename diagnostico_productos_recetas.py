import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta, CategoriaProducto, Receta

print("=== DIAGNÓSTICO DE PRODUCTOS Y RECETAS ===")

# 1. Verificar productos directamente
print("\n1. PRODUCTOS EN BASE DE DATOS:")
productos_todos = ProductoVenta.objects.all()
print(f"Total productos en DB: {productos_todos.count()}")

productos_disponibles = ProductoVenta.objects.filter(disponible=True)
print(f"Productos disponibles: {productos_disponibles.count()}")

for producto in productos_disponibles[:10]:
    print(f"  - {producto.id}: {producto.nombre} (disponible: {producto.disponible})")

print("\n2. RECETAS EN BASE DE DATOS:")
recetas_todas = Receta.objects.all() if hasattr(django, 'Receta') else []
try:
    recetas_todas = Receta.objects.all()
    print(f"Total recetas en DB: {recetas_todas.count()}")
    
    recetas_activas = Receta.objects.filter(activo=True)
    print(f"Recetas activas: {recetas_activas.count()}")
    
    for receta in recetas_activas[:10]:
        print(f"  - Receta {receta.id}: {receta.producto.nombre} (activa: {receta.activo})")
        
    print("\n3. PRODUCTOS CON RECETAS ACTIVAS:")
    productos_con_recetas = ProductoVenta.objects.filter(
        receta__activo=True,
        disponible=True
    ).distinct()
    print(f"Productos con recetas activas: {productos_con_recetas.count()}")
    
    for producto in productos_con_recetas:
        print(f"  - {producto.id}: {producto.nombre}")
        
except Exception as e:
    print(f"Error con recetas: {e}")

print("\n4. CATEGORÍAS:")
categorias = CategoriaProducto.objects.filter(activo=True)
print(f"Categorías activas: {categorias.count()}")

for categoria in categorias:
    productos_en_categoria = ProductoVenta.objects.filter(
        categoria=categoria,
        disponible=True
    ).count()
    print(f"  - {categoria.nombre}: {productos_en_categoria} productos")

print("\n5. VERIFICANDO LA FUNCIÓN obtener_productos_menu():")

from mesero.views import obtener_productos_menu

try:
    productos_menu = obtener_productos_menu()
    print(f"Productos devueltos por obtener_productos_menu(): {len(productos_menu)} categorías")
    
    total_productos = sum(len(productos) for productos in productos_menu.values())
    print(f"Total productos: {total_productos}")
    
    for categoria, productos in productos_menu.items():
        print(f"  - {categoria}: {len(productos)} productos")
        for producto in productos[:3]:  # Primeros 3
            print(f"    * {producto.get('nombre', 'Sin nombre')}")
            
except Exception as e:
    print(f"Error ejecutando obtener_productos_menu(): {e}")

print("\n6. BUSCANDO VISTA QUE HACE CONSULTAS CON RECETAS:")
import inspect
from mesero import views

# Buscar todas las funciones en views
for name, obj in inspect.getmembers(views):
    if inspect.isfunction(obj):
        source = inspect.getsource(obj)
        if 'receta' in source.lower() or 'restaurant_receta' in source.lower():
            print(f"Función {name} usa recetas:")
            lines = source.split('\n')
            for i, line in enumerate(lines):
                if 'receta' in line.lower():
                    print(f"  Línea {i+1}: {line.strip()}")

print("\n=== FIN DEL DIAGNÓSTICO ===")
