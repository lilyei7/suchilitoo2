#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import Orden, OrdenItem, Mesa
from restaurant.models import ProductoVenta
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

def crear_ordenes_prueba_completas():
    """Crear órdenes de prueba para validar la funcionalidad del dashboard"""
    print("=== CREANDO ÓRDENES DE PRUEBA ===")
    
    # Obtener datos necesarios
    try:
        mesa = Mesa.objects.first()
        mesero = User.objects.filter(groups__name='Mesero').first() or User.objects.first()
        productos = ProductoVenta.objects.filter(disponible=True)[:3]
        
        if not mesa:
            print("❌ No hay mesas disponibles")
            return
        if not mesero:
            print("❌ No hay meseros disponibles")
            return
        if not productos:
            print("❌ No hay productos disponibles")
            return
        
        print(f"✅ Mesa: {mesa.numero}")
        print(f"✅ Mesero: {mesero.username}")
        print(f"✅ Productos disponibles: {len(productos)}")
        
        # Crear 3 órdenes en diferentes estados
        ordenes_datos = [
            {'estado': 'confirmada', 'nombre': 'TEST-NUEVA'},
            {'estado': 'en_preparacion', 'nombre': 'TEST-PREP'},
            {'estado': 'confirmada', 'nombre': 'TEST-FINALIZAR'},
        ]
        
        for i, datos in enumerate(ordenes_datos):
            print(f"\nCreando orden {datos['nombre']}...")
            
            # Crear orden
            orden = Orden.objects.create(
                numero_orden=datos['nombre'],
                mesa=mesa,
                mesero=mesero,
                estado=datos['estado'],
                tipo_servicio='mesa',
                fecha_creacion=timezone.now(),
            )
            
            # Agregar items
            for j, producto in enumerate(productos):
                cantidad = j + 1
                precio = producto.precio
                item = OrdenItem.objects.create(
                    orden=orden,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    subtotal=precio * cantidad
                )
                print(f"  + {cantidad}x {producto.nombre} - ${item.subtotal}")
            
            # Calcular totales
            orden.calcular_totales()
            print(f"  ✅ Orden {orden.numero_orden} creada: {orden.estado} - Total: ${orden.total}")
            
        print("\n=== VERIFICANDO ESTADOS DE ÓRDENES ===")
        
        # Verificar órdenes activas del día
        hoy = timezone.now().date()
        ordenes_hoy = Orden.objects.filter(fecha_creacion__date=hoy)
        ordenes_activas = ordenes_hoy.filter(estado__in=['pendiente', 'confirmada', 'en_preparacion'])
        ordenes_completadas = ordenes_hoy.filter(estado__in=['lista', 'entregada', 'completada', 'cerrada'])
        
        print(f"📊 Total órdenes del día: {ordenes_hoy.count()}")
        print(f"🔄 Órdenes activas: {ordenes_activas.count()}")
        print(f"✅ Órdenes completadas: {ordenes_completadas.count()}")
        
        print("\n📋 Órdenes activas:")
        for orden in ordenes_activas[:10]:  # Mostrar solo las primeras 10
            print(f"  - {orden.numero_orden}: {orden.estado} (Mesa {orden.mesa.numero})")
        
        print("\n📋 Órdenes completadas:")
        for orden in ordenes_completadas[:10]:  # Mostrar solo las primeras 10
            fecha_final = orden.fecha_lista or orden.fecha_entrega or orden.fecha_cierre
            print(f"  - {orden.numero_orden}: {orden.estado} - Finalizada: {fecha_final}")
        
        print("\n🎯 INSTRUCCIONES PARA PRUEBA:")
        print("1. Ve al dashboard de cocina: http://127.0.0.1:8000/cocina/")
        print("2. Verifica que aparezcan las órdenes TEST-NUEVA, TEST-PREP y TEST-FINALIZAR")
        print("3. Haz clic en 'Finalizar Orden' en TEST-FINALIZAR")
        print("4. Cambia al tab 'Pedidos Completados'")
        print("5. Verifica que TEST-FINALIZAR aparezca en el tab de completados")
        
    except Exception as e:
        print(f"❌ Error creando órdenes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    crear_ordenes_prueba_completas()
