import os
import django
import traceback
import uuid
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Receta, RecetaInsumo, ProductoVenta
from django.db import transaction

def verify_recipe_system():
    """Verificación completa del sistema de recetas"""
    try:
        # 1. Verificar que hay recetas en el sistema
        recetas = Receta.objects.filter(activa=True)
        print(f"✅ El sistema tiene {recetas.count()} recetas activas")
        
        if recetas.count() == 0:
            print("⚠️ No hay recetas para verificar. Cree algunas recetas primero.")
            return
        
        # 2. Verificar que las recetas tienen ingredientes
        for receta in recetas:
            ingredientes = RecetaInsumo.objects.filter(receta=receta)
            print(f"Receta '{receta.nombre}' (ID: {receta.id}) tiene {ingredientes.count()} ingredientes")
            if ingredientes.count() == 0:
                print(f"⚠️ La receta '{receta.nombre}' no tiene ingredientes")
        
        # 3. Probar duplicación de una receta
        receta_prueba = recetas.first()
        print(f"\n🔍 Probando duplicación de receta: {receta_prueba.nombre} (ID: {receta_prueba.id})")
        
        # Conteo de recetas antes de duplicar
        count_antes = Receta.objects.count()
        
        # Duplicar receta
        with transaction.atomic():
            nueva_receta = Receta.objects.create(
                nombre=f"{receta_prueba.nombre} (Copia Verificación)",
                descripcion=receta_prueba.descripcion,
                instrucciones=receta_prueba.instrucciones,
                tiempo_preparacion=receta_prueba.tiempo_preparacion,
                porciones=receta_prueba.porciones,
                costo_total=receta_prueba.costo_total,
                activa=True
            )
            
            # Copiar ingredientes
            ingredientes_original = RecetaInsumo.objects.filter(receta=receta_prueba)
            for ingrediente in ingredientes_original:
                RecetaInsumo.objects.create(
                    receta=nueva_receta,
                    insumo=ingrediente.insumo,
                    cantidad=ingrediente.cantidad
                )
              # Verificar si tiene producto asociado
            try:
                producto_original = ProductoVenta.objects.get(receta=receta_prueba)
                if producto_original:
                    nuevo_codigo = f"{producto_original.codigo}_copia_{uuid.uuid4().hex[:8]}"
                    ProductoVenta.objects.create(
                        nombre=f"{producto_original.nombre} (Copia)",
                        descripcion=producto_original.descripcion,
                        codigo=nuevo_codigo,
                        precio=producto_original.precio,
                        categoria=producto_original.categoria,
                        receta=nueva_receta,
                        disponible=True,
                        imagen=producto_original.imagen
                    )
            except ProductoVenta.DoesNotExist:
                pass
        
        # Conteo después de duplicar
        count_despues = Receta.objects.count()
        
        if count_despues > count_antes:
            print(f"✅ Duplicación exitosa! Nueva receta: {nueva_receta.nombre} (ID: {nueva_receta.id})")
            
            # Verificar ingredientes duplicados
            nuevos_ingredientes = RecetaInsumo.objects.filter(receta=nueva_receta)
            print(f"✅ La receta duplicada tiene {nuevos_ingredientes.count()} ingredientes")
            
            # Verificar producto duplicado
            try:
                producto_nuevo = ProductoVenta.objects.get(receta=nueva_receta)
                print(f"✅ Producto de venta duplicado: {producto_nuevo.nombre}")
            except ProductoVenta.DoesNotExist:
                if not ProductoVenta.objects.filter(receta=receta_prueba).exists():
                    print("ℹ️ La receta original no tenía producto asociado, así que no se duplicó ninguno")
                else:
                    print("❌ Error: No se duplicó el producto de venta")
        else:
            print("❌ Error: No se pudo duplicar la receta")
        
        print("\n📋 Verificación del sistema de recetas completada!")
    except Exception as e:
        print(f"❌ Error durante la verificación: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    verify_recipe_system()

if __name__ == "__main__":
    verify_recipe_system()
