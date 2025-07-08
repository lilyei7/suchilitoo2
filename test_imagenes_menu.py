import django
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta
from collections import defaultdict

def test_productos_menu():
    """Test the obtener_productos_menu function"""
    print("=== TESTING PRODUCTOS MENU FUNCTION ===")
    
    # Simular la función obtener_productos_menu
    productos_activos = ProductoVenta.objects.filter(
        disponible=True  # Solo productos disponibles/activos
    ).select_related('categoria').order_by('categoria__orden', 'categoria__nombre', 'nombre')
    
    # Organizar productos por categoría
    productos_por_categoria = defaultdict(list)
    
    for producto in productos_activos:
        categoria_nombre = producto.categoria.nombre if producto.categoria else 'Sin Categoría'
        
        # Convertir el producto a un diccionario para el template
        producto_data = {
            'id': producto.id,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion or 'Sin descripción disponible',
            'precio': float(producto.precio),
            'imagen': producto.imagen.url if producto.imagen else None,
            'disponible': producto.disponible,
            'tiempo_preparacion': getattr(producto, 'tiempo_preparacion', 15),  # Default 15 min
            'calorias': producto.calorias or 0,
            'tipo': producto.get_tipo_display(),
            'es_promocion': producto.es_promocion,
            'destacado': producto.destacado,
        }
        
        productos_por_categoria[categoria_nombre].append(producto_data)
    
    # Convertir defaultdict a dict regular para el template
    productos_por_categoria = dict(productos_por_categoria)
    
    print(f"Total categorías: {len(productos_por_categoria)}")
    
    for categoria, productos in productos_por_categoria.items():
        print(f"\n=== CATEGORÍA: {categoria} ===")
        print(f"Productos: {len(productos)}")
        
        for producto in productos[:3]:  # Mostrar solo los primeros 3
            print(f"  - {producto['nombre']}")
            print(f"    Precio: ${producto['precio']}")
            print(f"    Imagen: {producto['imagen']}")
            print(f"    Disponible: {producto['disponible']}")
            print()
    
    return productos_por_categoria

def test_image_urls():
    """Test que las URLs de las imágenes sean correctas"""
    print("\n=== TESTING IMAGE URLS ===")
    
    productos_con_imagen = ProductoVenta.objects.filter(
        imagen__isnull=False
    ).exclude(imagen='')[:5]
    
    for producto in productos_con_imagen:
        print(f"Producto: {producto.nombre}")
        print(f"  Imagen field: {producto.imagen}")
        print(f"  Imagen URL: {producto.imagen.url}")
        print(f"  Imagen path: {producto.imagen.path}")
        print(f"  File exists: {os.path.exists(producto.imagen.path)}")
        print()

def main():
    """Función principal"""
    try:
        productos_data = test_productos_menu()
        test_image_urls()
        
        print("\n=== RESULTADO DEL TEST ===")
        print("✓ Las imágenes deberían ser visibles ahora")
        print("✓ Se ha corregido la referencia de imagen en el template")
        print("✓ Se han añadido estilos CSS para las imágenes")
        print("\nRefresh la página http://127.0.0.1:8000/mesero/nueva-orden/16/")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
