import os
import django
import sys
import requests
import json
from decimal import Decimal

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from restaurant.models import CategoriaProducto, Receta, ProductoVenta, RecetaInsumo, Insumo, UnidadMedida, CategoriaInsumo

User = get_user_model()

def duplicar_receta_test():
    """
    Prueba el proceso de duplicación de recetas
    """
    print("Probando duplicación de recetas...")
    
    # Verificar recetas existentes
    recetas = Receta.objects.select_related('producto').all()
    print(f"Recetas disponibles antes de duplicación: {recetas.count()}")
    
    if recetas.count() == 0:
        print("No hay recetas para duplicar.")
        return
    
    # Tomar la primera receta para duplicar
    receta_original = recetas.first()
    print(f"Duplicando receta: {receta_original.producto.nombre} (ID: {receta_original.id})")
    
    # Obtener producto original
    producto_original = receta_original.producto
    
    # Generar código único para el nuevo producto
    import time
    timestamp = int(time.time())
    codigo_unico = f"REC{timestamp:010d}"
    
    # Crear copia del producto
    producto_nuevo = ProductoVenta.objects.create(
        nombre=f"Duplicación test - {producto_original.nombre}",
        descripcion=producto_original.descripcion,
        codigo=codigo_unico,
        precio=producto_original.precio,
        costo=producto_original.costo,
        tipo=producto_original.tipo,
        disponible=True,
        categoria=producto_original.categoria
    )
    
    # Crear copia de la receta
    receta_nueva = Receta.objects.create(
        producto=producto_nuevo,
        tiempo_preparacion=receta_original.tiempo_preparacion,
        porciones=receta_original.porciones,
        instrucciones=receta_original.instrucciones,
        activo=True
    )
    
    # Copiar ingredientes
    ingredientes_originales = RecetaInsumo.objects.filter(receta=receta_original)
    for ingrediente in ingredientes_originales:
        RecetaInsumo.objects.create(
            receta=receta_nueva,
            insumo=ingrediente.insumo,
            cantidad=ingrediente.cantidad,
            opcional=ingrediente.opcional,
            notas=ingrediente.notas,
            orden=ingrediente.orden
        )
    
    print(f"✅ Receta duplicada correctamente con ID: {receta_nueva.id}")
    
    # Verificar ingredientes de la nueva receta
    nuevos_ingredientes = RecetaInsumo.objects.filter(receta=receta_nueva)
    print(f"Ingredientes en la receta duplicada: {nuevos_ingredientes.count()}")
    
    for ingrediente in nuevos_ingredientes:
        print(f"  - {ingrediente.insumo.nombre}: {ingrediente.cantidad} {ingrediente.insumo.unidad_medida.nombre if ingrediente.insumo.unidad_medida else 'unidad'}")
    
    # Verificar recetas después de duplicación
    recetas_despues = Receta.objects.all()
    print(f"Recetas disponibles después de duplicación: {recetas_despues.count()}")
    
    return receta_nueva.id

if __name__ == "__main__":
    duplicar_receta_test()
