import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Receta, RecetaInsumo
from django.db import transaction

def test_duplicar_receta():
    """Test para verificar la funcionalidad de duplicación de recetas"""
    # Obtener la primera receta activa para probar
    try:
        receta_original = Receta.objects.filter(activa=True).first()
        if not receta_original:
            print("No hay recetas activas para probar la duplicación.")
            return
        
        print(f"Receta original: {receta_original.nombre}, ID: {receta_original.id}")
        
        # Obtener los ingredientes originales
        ingredientes_original = RecetaInsumo.objects.filter(receta=receta_original)
        print(f"La receta original tiene {ingredientes_original.count()} ingredientes")
        
        # Simular la duplicación
        with transaction.atomic():
            # Crear una nueva receta con los datos de la original
            nueva_receta = Receta.objects.create(
                nombre=f"{receta_original.nombre} (Copia)",
                descripcion=receta_original.descripcion,
                instrucciones=receta_original.instrucciones,
                tiempo_preparacion=receta_original.tiempo_preparacion,
                porciones=receta_original.porciones,
                costo_total=receta_original.costo_total,
                activa=True
            )
            
            # Copiar los ingredientes
            for ingrediente in ingredientes_original:
                RecetaInsumo.objects.create(
                    receta=nueva_receta,
                    insumo=ingrediente.insumo,
                    cantidad=ingrediente.cantidad
                )
            
            print(f"Receta duplicada creada con éxito: {nueva_receta.nombre}, ID: {nueva_receta.id}")
            
            # Verificar que los ingredientes se copiaron correctamente
            nuevos_ingredientes = RecetaInsumo.objects.filter(receta=nueva_receta)
            print(f"La receta duplicada tiene {nuevos_ingredientes.count()} ingredientes")
            
            if ingredientes_original.count() == nuevos_ingredientes.count():
                print("✅ La duplicación de ingredientes fue exitosa")
            else:
                print("❌ La duplicación de ingredientes falló")
        
    except Exception as e:
        print(f"Error al duplicar la receta: {str(e)}")

if __name__ == "__main__":
    test_duplicar_receta()
