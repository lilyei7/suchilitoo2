import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta

def verificar_productos():
    print("\n=== VERIFICACIÓN DE PRODUCTOS ===")
    print("=" * 40)
    
    # 1. Obtener todos los productos
    todos_productos = ProductoVenta.objects.all()
    print(f"\nTotal de productos en la base de datos: {todos_productos.count()}")
    
    # 2. Mostrar cada producto con sus detalles
    print("\nDETALLE DE PRODUCTOS:")
    print("-" * 80)
    print(f"{'ID':<6} {'CÓDIGO':<10} {'NOMBRE':<30} {'DISPONIBLE':<10} {'PRECIO':<10}")
    print("-" * 80)
    
    for producto in todos_productos:
        print(f"{producto.id:<6} {producto.codigo:<10} {producto.nombre:<30} {str(producto.disponible):<10} ${producto.precio}")
    
    # 3. Conteos específicos
    activos = todos_productos.filter(disponible=True).count()
    inactivos = todos_productos.filter(disponible=False).count()
    
    print("\nRESUMEN:")
    print(f"Productos activos: {activos}")
    print(f"Productos inactivos: {inactivos}")
    
    # 4. Verificar si hay productos sin categoría
    sin_categoria = todos_productos.filter(categoria__isnull=True).count()
    print(f"Productos sin categoría: {sin_categoria}")

if __name__ == '__main__':
    try:
        verificar_productos()
    except Exception as e:
        print(f"\nError al verificar productos: {str(e)}")
    finally:
        print("\n=== FIN DE LA VERIFICACIÓN ===")
