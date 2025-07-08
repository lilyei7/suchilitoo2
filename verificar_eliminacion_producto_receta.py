import os
import django
import sys
from decimal import Decimal

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta, CategoriaProducto, Receta, ProductoReceta
from django.db import transaction

def verificar_eliminacion_producto_receta():
    """
    Verifica que al eliminar un producto, la receta asociada no se elimine
    """
    print("=== VERIFICACIÓN DE ELIMINACIÓN DE PRODUCTO Y RECETA ===")
    
    # 1. Crear una categoría si no existe
    categoria, created = CategoriaProducto.objects.get_or_create(
        nombre="Test Categoría",
        defaults={'descripcion': 'Categoría para pruebas'}
    )
    print(f"Categoría {'creada' if created else 'existente'}: {categoria.nombre}")
    
    # 2. Crear un producto de prueba
    codigo_prueba = "TEST-PROD-123"
    
    try:
        # Borrar el producto si ya existe (para pruebas repetidas)
        ProductoVenta.objects.filter(codigo=codigo_prueba).delete()
        print(f"Producto previo con código {codigo_prueba} eliminado")
    except Exception:
        pass
    
    print("\n1. Creando producto de prueba...")
    producto = ProductoVenta.objects.create(
        codigo=codigo_prueba,
        nombre="Producto de Prueba",
        descripcion="Producto para verificar eliminación",
        precio=Decimal('10.99'),
        categoria=categoria,
        disponible=True
    )
    print(f"  ✓ Producto creado con ID: {producto.id}")
    
    # 3. Crear una receta asociada al producto
    print("\n2. Creando receta asociada...")
    receta = Receta.objects.create(
        producto=producto,
        tiempo_preparacion=15,
        porciones=2,
        instrucciones="Instrucciones de prueba",
        activo=True
    )
    print(f"  ✓ Receta creada con ID: {receta.id}")
    
    # Verificar que la relación esté establecida
    producto_refrescado = ProductoVenta.objects.get(id=producto.id)
    print(f"  ✓ Producto tiene receta asignada: {hasattr(producto_refrescado, 'receta')}")
    print(f"  ✓ ID de la receta asociada: {producto_refrescado.receta.id}")
    
    # 4. Eliminar el producto
    print("\n3. Eliminando el producto...")
    producto_id = producto.id
    receta_id = receta.id
    
    with transaction.atomic():
        producto.delete()
    
    print(f"  ✓ Producto con ID {producto_id} eliminado")
    
    # 5. Verificar que la receta siga existiendo
    print("\n4. Verificando que la receta siga existiendo...")
    try:
        receta_despues = Receta.objects.get(id=receta_id)
        print(f"  ✓ ¡ÉXITO! La receta con ID {receta_id} sigue existiendo")
        print(f"  ✓ La receta ya no tiene producto asociado: {receta_despues.producto is None}")
    except Receta.DoesNotExist:
        print(f"  ✗ ERROR: La receta con ID {receta_id} se eliminó junto con el producto")
    
    print("\n=== FIN DE LA VERIFICACIÓN ===")

if __name__ == "__main__":
    verificar_eliminacion_producto_receta()
