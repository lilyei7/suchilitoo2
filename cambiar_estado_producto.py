import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta

def activar_producto():
    print("\n=== ACTIVANDO PRODUCTO TEMPORAL ===")
    
    try:
        # Encontrar el producto inactivo
        producto = ProductoVenta.objects.get(codigo='76116')
        print(f"Producto encontrado: {producto.nombre}")
        print(f"Estado actual: {'ACTIVO' if producto.disponible else 'INACTIVO'}")
        
        # Cambiar estado
        producto.disponible = True
        producto.save()
        
        print(f"Producto activado exitosamente")
        print(f"Nuevo estado: {'ACTIVO' if producto.disponible else 'INACTIVO'}")
        
        # Verificar
        producto_verificacion = ProductoVenta.objects.get(id=producto.id)
        print(f"Verificación: {'ACTIVO' if producto_verificacion.disponible else 'INACTIVO'}")
        
    except ProductoVenta.DoesNotExist:
        print("Producto no encontrado")
    except Exception as e:
        print(f"Error: {str(e)}")

def desactivar_producto():
    print("\n=== DESACTIVANDO PRODUCTO ===")
    
    try:
        # Encontrar el producto activo
        producto = ProductoVenta.objects.get(codigo='76116')
        print(f"Producto encontrado: {producto.nombre}")
        print(f"Estado actual: {'ACTIVO' if producto.disponible else 'INACTIVO'}")
        
        # Cambiar estado
        producto.disponible = False
        producto.save()
        
        print(f"Producto desactivado exitosamente")
        print(f"Nuevo estado: {'ACTIVO' if producto.disponible else 'INACTIVO'}")
        
    except ProductoVenta.DoesNotExist:
        print("Producto no encontrado")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'activar':
        activar_producto()
    elif len(sys.argv) > 1 and sys.argv[1] == 'desactivar':
        desactivar_producto()
    else:
        print("Uso:")
        print("python cambiar_estado_producto.py activar   # Para activar el producto")
        print("python cambiar_estado_producto.py desactivar # Para desactivar el producto")
