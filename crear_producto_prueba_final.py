"""
Script para crear un producto de prueba para verificar la funcionalidad de eliminación.
"""

import os
import sys
import django
import random
import string
import webbrowser
from django.utils import timezone

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sushi_core.settings")
django.setup()

# Importar modelos
from restaurant.models import ProductoVenta, CategoriaProducto, Unidad

def print_title(title):
    """Imprime un título formateado."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "*"))
    print("=" * 80)

def print_section(section):
    """Imprime una sección formateada."""
    print("\n" + "-" * 80)
    print(f" {section} ".center(80, "-"))
    print("-" * 80)

def generate_random_string(length=8):
    """Genera una cadena aleatoria."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def crear_producto_prueba():
    """Crea un producto de prueba para la eliminación."""
    print_section("Creando producto de prueba para eliminación")
    
    # Obtener o crear una categoría
    try:
        categoria = CategoriaProducto.objects.first()
        if not categoria:
            print("Creando categoría de prueba...")
            categoria = CategoriaProducto.objects.create(
                nombre="Categoría de Prueba",
                descripcion="Categoría para pruebas de eliminación"
            )
    except Exception as e:
        print(f"Error al obtener/crear categoría: {e}")
        return None
    
    # Obtener o crear una unidad
    try:
        unidad = Unidad.objects.first()
        if not unidad:
            print("Creando unidad de prueba...")
            unidad = Unidad.objects.create(
                nombre="Unidad",
                simbolo="u"
            )
    except Exception as e:
        print(f"Error al obtener/crear unidad: {e}")
        return None
    
    # Crear el producto
    try:
        nombre = f"Producto Test Eliminación {generate_random_string()}"
        precio = random.uniform(50, 200)
        
        producto = ProductoVenta.objects.create(
            nombre=nombre,
            descripcion="Producto creado para probar la funcionalidad de eliminación",
            precio=precio,
            categoria=categoria,
            unidad=unidad,
            disponible=True,
            fecha_creacion=timezone.now()
        )
        
        print(f"✅ Producto creado exitosamente:")
        print(f"   ID: {producto.id}")
        print(f"   Nombre: {producto.nombre}")
        print(f"   Precio: ${producto.precio:.2f}")
        print(f"   Categoría: {producto.categoria.nombre}")
        
        return producto
    except Exception as e:
        print(f"❌ Error al crear producto: {e}")
        return None

def abrir_navegador(producto_id):
    """Abre el navegador en la página de productos."""
    print_section("Abriendo navegador para verificar producto")
    
    url = "http://localhost:8000/dashboard/productos-venta/"
    print(f"Abriendo {url} en el navegador...")
    webbrowser.open(url)
    
    print("\nInstrucciones para probar la eliminación:")
    print(f"1. Busca el producto con ID: {producto_id}")
    print("2. Haz clic en el botón 'Eliminar'")
    print("3. Confirma la eliminación en el modal")
    print("4. Verifica que no aparezcan errores en la consola del navegador (F12)")
    print("5. Verifica que el producto se elimine correctamente")

def main():
    """Función principal del script."""
    print_title("CREACIÓN DE PRODUCTO DE PRUEBA PARA ELIMINACIÓN")
    
    # Crear producto de prueba
    producto = crear_producto_prueba()
    
    if producto:
        print("\n✅ Producto creado exitosamente para pruebas de eliminación")
        
        # Preguntar si se desea abrir el navegador
        print("\n¿Deseas abrir el navegador para probar la eliminación? (s/n)")
        choice = input().lower()
        
        if choice == 's':
            abrir_navegador(producto.id)
        else:
            print("\nPuedes probar la eliminación manualmente accediendo a:")
            print("http://localhost:8000/dashboard/productos-venta/")
            print(f"Busca el producto con ID: {producto.id}")
    else:
        print("\n❌ No se pudo crear el producto de prueba")

if __name__ == "__main__":
    main()
