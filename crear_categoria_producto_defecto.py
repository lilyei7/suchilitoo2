import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import CategoriaProducto

def crear_categoria_producto_defecto():
    """Crear una categoría de producto por defecto para las recetas"""
    
    categoria, created = CategoriaProducto.objects.get_or_create(
        nombre='Platos del Menú',
        defaults={
            'descripcion': 'Categoría por defecto para productos creados a partir de recetas',
            'activa': True
        }
    )
    
    if created:
        print(f"✅ Categoría de producto creada: {categoria.nombre}")
    else:
        print(f"ℹ️ Categoría de producto ya existe: {categoria.nombre}")
    
    print(f"ID de la categoría: {categoria.id}")
    return categoria

if __name__ == "__main__":
    crear_categoria_producto_defecto()
