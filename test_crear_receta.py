import os
import django
import sys
import requests
import json
from getpass import getpass

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from restaurant.models import CategoriaProducto, Receta, ProductoVenta, RecetaInsumo, Insumo

User = get_user_model()

def test_crear_receta():
    """
    Prueba la creación de una receta directamente usando los modelos
    """
    print("Creando una receta de prueba usando modelos...")
    
    # Verificar que existan categorías
    categorias = CategoriaProducto.objects.all()
    if not categorias.exists():
        print("No hay categorías disponibles. Creando una categoría...")
        categoria = CategoriaProducto.objects.create(
            nombre="Categoria de Prueba",
            descripcion="Categoría creada para pruebas"
        )
    else:
        categoria = categorias.first()
    
    # Crear producto para la receta
    producto = ProductoVenta.objects.create(
        nombre="Receta de Prueba",
        descripcion="Receta creada para pruebas",
        codigo=f"REC{ProductoVenta.objects.count() + 1:04d}",
        precio=15.99,
        costo=8.50,
        tipo='plato',
        disponible=True,
        categoria=categoria
    )
    
    # Crear receta
    receta = Receta.objects.create(
        producto=producto,
        tiempo_preparacion=30,
        porciones=2,
        instrucciones="1. Paso 1\n2. Paso 2\n3. Paso 3",
        activo=True
    )
    
    print(f"Receta creada: {receta.producto.nombre} (ID: {receta.id})")
    
    # Agregar ingredientes
    insumos = Insumo.objects.all()
    if insumos.exists():
        for i, insumo in enumerate(insumos[:3]):  # Usar los primeros 3 insumos
            RecetaInsumo.objects.create(
                receta=receta,
                insumo=insumo,
                cantidad=100 + i*50,  # 100, 150, 200
                orden=i+1,
                opcional=False
            )
            print(f"  - Ingrediente añadido: {insumo.nombre} ({insumo.unidad_medida})")
    
    return receta

if __name__ == "__main__":
    receta = test_crear_receta()
    
    # Verificar recetas
    print("\nVerificando recetas después de la prueba:")
    recetas = Receta.objects.select_related('producto').all()
    print(f"Recetas disponibles: {recetas.count()}")
    for r in recetas:
        print(f"  - {r.producto.nombre} (ID: {r.id})")
        ingredientes = RecetaInsumo.objects.filter(receta=r).count()
        print(f"    Ingredientes: {ingredientes}")
