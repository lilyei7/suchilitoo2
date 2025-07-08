#!/usr/bin/env python
"""
Script simplificado para probar la eliminación de productos
"""

import os
import django
import sys
import logging
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importar modelos relevantes
from django.db import connection, transaction
from restaurant.models import ProductoVenta

def print_separator(title=None):
    """Imprime un separador con título opcional"""
    if title:
        print("\n" + "="*20 + f" {title} " + "="*20)
    else:
        print("\n" + "="*50)

def listar_productos():
    """Lista todos los productos en la base de datos"""
    print_separator("PRODUCTOS ACTUALES")
    productos = ProductoVenta.objects.all().order_by('id')
    print(f"Total de productos encontrados: {productos.count()}")
    
    if productos.count() > 0:
        for producto in productos:
            print(f"ID: {producto.id} | Nombre: {producto.nombre} | Precio: ${producto.precio}")
    else:
        print("No hay productos en la base de datos.")
    
    return productos

def eliminar_producto(producto_id):
    """Intenta eliminar un producto por su ID"""
    print_separator("ELIMINANDO PRODUCTO")
    print(f"Intentando eliminar producto ID: {producto_id}")
    
    try:
        # Buscar el producto
        producto = ProductoVenta.objects.get(id=producto_id)
        print(f"Producto encontrado: {producto.nombre} (ID: {producto.id})")
        
        # Mostrar información del producto
        print(f"Información del producto:")
        print(f"  - Nombre: {producto.nombre}")
        print(f"  - Código: {producto.codigo}")
        print(f"  - Precio: ${producto.precio}")
        print(f"  - Categoría: {producto.categoria.nombre if producto.categoria else 'Sin categoría'}")
        
        # Eliminar el producto
        with transaction.atomic():
            print(f"Ejecutando DELETE FROM restaurant_productoventa WHERE id = {producto_id}")
            producto.delete()
            print(f"Producto eliminado correctamente")
            
        # Verificar si el producto fue eliminado
        if not ProductoVenta.objects.filter(id=producto_id).exists():
            print(f"✅ Verificación exitosa: El producto ya no existe en la base de datos")
            return True
        else:
            print(f"❌ ERROR: El producto sigue existiendo en la base de datos después de eliminarlo")
            return False
            
    except ProductoVenta.DoesNotExist:
        print(f"Producto con ID {producto_id} no existe")
        return True
    except Exception as e:
        print(f"Error al eliminar producto: {str(e)}")
        return False

def forzar_eliminacion(producto_id):
    """Fuerza la eliminación de un producto usando SQL directo"""
    print_separator("FORZANDO ELIMINACIÓN")
    print(f"Forzando eliminación del producto ID: {producto_id}")
    
    try:
        # Verificar si el producto existe
        if not ProductoVenta.objects.filter(id=producto_id).exists():
            print(f"Producto con ID {producto_id} no existe. Nada que eliminar.")
            return True
        
        # Obtener información del producto antes de eliminarlo
        producto = ProductoVenta.objects.get(id=producto_id)
        nombre = producto.nombre
        
        # Eliminar usando SQL directo
        with connection.cursor() as cursor:
            # Primero eliminar relaciones (si existen)
            try:
                cursor.execute("DELETE FROM restaurant_productoreceta WHERE producto_id = %s", [producto_id])
                print(f"Eliminadas {cursor.rowcount} relaciones de recetas")
            except Exception as e:
                print(f"Error al eliminar relaciones de recetas: {e}")
            
            # Eliminar el producto
            cursor.execute("DELETE FROM restaurant_productoventa WHERE id = %s", [producto_id])
            rows_affected = cursor.rowcount
            print(f"Filas afectadas: {rows_affected}")
            
            if rows_affected > 0:
                print(f"✅ Producto '{nombre}' eliminado correctamente mediante SQL directo")
                return True
            else:
                print(f"❌ No se pudo eliminar el producto mediante SQL directo")
                return False
    except Exception as e:
        print(f"Error al forzar eliminación: {str(e)}")
        return False

def main():
    """Función principal"""
    print_separator("TEST DE ELIMINACIÓN DE PRODUCTOS")
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Listar productos actuales
    productos = listar_productos()
    
    if productos.count() == 0:
        print("\nNo hay productos para eliminar.")
        return
    
    # Determinar el ID del producto
    if len(sys.argv) > 1:
        try:
            producto_id = int(sys.argv[1])
            print(f"\nUsando producto ID {producto_id} pasado como argumento")
        except ValueError:
            print(f"\nID inválido: {sys.argv[1]}")
            return
    else:
        print("\nProductos disponibles:")
        for i, producto in enumerate(productos):
            print(f"{i+1}. ID: {producto.id} | {producto.nombre}")
        
        try:
            seleccion = int(input("\nSeleccione el número del producto (o 0 para salir): "))
            if seleccion == 0:
                print("Saliendo...")
                return
            
            producto_id = productos[seleccion-1].id
        except (ValueError, IndexError):
            print("Selección inválida. Saliendo...")
            return
    
    # Intentar eliminación normal
    eliminado = eliminar_producto(producto_id)
    
    if not eliminado:
        respuesta = input("\n¿Desea forzar la eliminación? (s/n): ")
        if respuesta.lower() in ['s', 'si', 'y', 'yes']:
            forzar_eliminacion(producto_id)
    
    # Listar productos después de la acción
    print_separator("ESTADO FINAL")
    listar_productos()

if __name__ == "__main__":
    main()
