import os
import django
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

# Ahora ejecutar las consultas
from dashboard.models import *
from dashboard.models_ventas import *

def create_receta_xxx2():
    print("=== CREANDO RECETA PARA PRODUCTO xxx2 ===")
    print()
    
    try:
        # Obtener el producto xxx2
        producto_xxx2 = ProductoVenta.objects.get(id=121)
        print(f"Producto encontrado: {producto_xxx2.nombre} (ID: {producto_xxx2.id})")
        
        # Verificar si ya tiene receta
        try:
            receta_existente = producto_xxx2.receta
            if receta_existente:
                print(f"❌ El producto ya tiene receta: {receta_existente.id}")
                return
        except:
            print("✅ El producto no tiene receta, procediendo a crear una...")
        
        # Crear nueva receta
        nueva_receta = Receta.objects.create(
            producto=producto_xxx2,
            tiempo_preparacion=10,  # 10 minutos
            porciones=1,
            instrucciones="Receta básica para alga nori xxx2: Preparar alga nori con ingredientes básicos.",
            notas="Receta creada automáticamente",
            activo=True
        )
        
        print(f"✅ Receta creada exitosamente:")
        print(f"  - Receta ID: {nueva_receta.id}")
        print(f"  - Producto: {nueva_receta.producto.nombre}")
        print(f"  - Tiempo: {nueva_receta.tiempo_preparacion} minutos")
        print(f"  - Porciones: {nueva_receta.porciones}")
        print(f"  - Activo: {nueva_receta.activo}")
        
        # Verificar que la receta se creó correctamente
        print("\n=== VERIFICACIÓN ===")
        producto_actualizado = ProductoVenta.objects.get(id=121)
        try:
            receta_verificada = producto_actualizado.receta
            if receta_verificada:
                print(f"✅ Verificación exitosa: Producto {producto_actualizado.nombre} ahora tiene receta {receta_verificada.id}")
            else:
                print("❌ Error: No se pudo verificar la receta")
        except Exception as e:
            print(f"❌ Error en la verificación: {e}")
            
    except ProductoVenta.DoesNotExist:
        print("❌ Producto xxx2 no encontrado")
    except Exception as e:
        print(f"❌ Error creando receta: {e}")

def test_mesero_order():
    print("\n=== PROBANDO CREACIÓN DE ORDEN COMO MESERO ===")
    print()
    
    try:
        # Simular el proceso que hace el mesero
        producto_xxx2 = ProductoVenta.objects.get(id=121)
        print(f"Producto para orden: {producto_xxx2.nombre}")
        
        # Verificar que tenga receta
        try:
            receta = producto_xxx2.receta
            if receta:
                print(f"✅ Producto tiene receta: {receta.id}")
                print("✅ El mesero ahora puede crear órdenes con este producto")
            else:
                print("❌ El producto NO tiene receta - el mesero no puede crear órdenes")
        except Exception as e:
            print(f"❌ Error accediendo receta: {e}")
            
    except ProductoVenta.DoesNotExist:
        print("❌ Producto xxx2 no encontrado")

if __name__ == "__main__":
    create_receta_xxx2()
    test_mesero_order()
