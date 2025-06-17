import os
import django
import sys
from decimal import Decimal

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from restaurant.models import Receta, ProductoVenta, RecetaInsumo

User = get_user_model()

def actualizar_costos_recetas():
    """
    Actualiza los costos de todas las recetas en base a sus ingredientes
    """
    print("Actualizando costos de recetas basado en ingredientes...")
    
    # Obtener todas las recetas
    recetas = Receta.objects.select_related('producto').all()
    print(f"Recetas encontradas: {recetas.count()}")
    
    for receta in recetas:
        # Calcular costo total de ingredientes
        ingredientes = RecetaInsumo.objects.filter(receta=receta).select_related('insumo')
        
        costo_total = Decimal('0.00')
        for ingrediente in ingredientes:
            precio_unitario = ingrediente.insumo.precio_unitario or Decimal('0.00')
            cantidad = ingrediente.cantidad or Decimal('0.00')
            costo_ingrediente = precio_unitario * cantidad
            costo_total += costo_ingrediente
        
        # Actualizar el costo del producto si es diferente
        if receta.producto.costo != costo_total:
            antes = receta.producto.costo
            receta.producto.costo = costo_total
            receta.producto.save()
            print(f"  ✅ {receta.producto.nombre}: Costo actualizado de ${float(antes):.2f} a ${float(costo_total):.2f}")
        else:
            print(f"  ✓ {receta.producto.nombre}: Costo ya está actualizado: ${float(costo_total):.2f}")
    
    print("\nActualización de costos completada.")

if __name__ == "__main__":
    actualizar_costos_recetas()
