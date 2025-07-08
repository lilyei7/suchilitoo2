#!/usr/bin/env python
"""
Script para crear órdenes con tiempos realistas basados en la hora actual
para mostrar timers en tiempo real con segundos y minutos
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import (
    Orden, Mesa, OrdenItem
)
from restaurant.models import ProductoVenta, CategoriaProducto
from accounts.models import Sucursal, Usuario

def crear_ordenes_tiempo_real():
    """Crear órdenes con diferentes tiempos para mostrar timers realistas"""
    
    # Obtener o crear sucursal
    sucursal, created = Sucursal.objects.get_or_create(
        nombre="Sucursal Principal",
        defaults={
            'direccion': 'Av. Principal 123',
            'telefono': '555-0123',
            'activa': True
        }
    )
    
    # Obtener o crear datos necesarios
    try:
        mesa1 = Mesa.objects.get(numero="1", sucursal=sucursal)
    except Mesa.DoesNotExist:
        mesa1 = Mesa.objects.create(numero="1", capacidad=4, sucursal=sucursal, estado='disponible')
    
    try:
        mesa2 = Mesa.objects.get(numero="2", sucursal=sucursal)
    except Mesa.DoesNotExist:
        mesa2 = Mesa.objects.create(numero="2", capacidad=6, sucursal=sucursal, estado='disponible')
        
    try:
        mesa3 = Mesa.objects.get(numero="3", sucursal=sucursal)
    except Mesa.DoesNotExist:
        mesa3 = Mesa.objects.create(numero="3", capacidad=2, sucursal=sucursal, estado='disponible')

    # Obtener o crear categoría
    categoria, created = CategoriaProducto.objects.get_or_create(
        nombre="Sushi",
        defaults={'descripcion': 'Rollos de sushi tradicionales', 'activo': True}
    )

    # Obtener o crear productos
    productos = []
    productos_info = [
        ("CAL001", "California Roll", 15, 25.99),
        ("PHI001", "Philadelphia Roll", 18, 28.50),
        ("TEM001", "Tempura Roll", 20, 32.00),
        ("SAL001", "Salmon Sashimi", 12, 18.75),
        ("DRA001", "Dragon Roll", 25, 35.99),
        ("RAI001", "Rainbow Roll", 22, 30.25),
    ]
    
    for codigo, nombre, tiempo_prep, precio in productos_info:
        producto, created = ProductoVenta.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'categoria': categoria,
                'precio': precio,
                'disponible': True,
                'tipo': 'plato'
            }
        )
        productos.append(producto)

    # Obtener mesero
    try:
        mesero = Usuario.objects.filter(rol__nombre='mesero').first()
        if not mesero:
            # Obtener el rol de mesero
            from accounts.models import Rol
            rol_mesero, created = Rol.objects.get_or_create(
                nombre='mesero',
                defaults={'descripcion': 'Mesero del restaurante'}
            )
            
            mesero = Usuario.objects.create_user(
                username='mesero_test',
                first_name='Carlos',
                last_name='Mesero',
                rol=rol_mesero,
                sucursal=sucursal
            )
    except:
        mesero = None

    # Hora actual como referencia
    ahora = datetime.now()
    
    # Limpiar órdenes existentes para evitar duplicados
    Orden.objects.filter(estado__in=['pendiente', 'en_preparacion']).delete()
    
    print(f"🕒 Hora actual: {ahora.strftime('%H:%M:%S')}")
    print("Creando órdenes con tiempos realistas...")

    # ORDEN 1: Recién creada (hace 30 segundos) - Mostrará segundos
    orden1_fecha = ahora - timedelta(seconds=30)
    orden1 = Orden.objects.create(
        numero_orden=f"ORD-{int(ahora.timestamp())}-1",
        mesa=mesa1,
        mesero=mesero,
        estado='en_preparacion',
        fecha_creacion=orden1_fecha,
        observaciones="Sin wasabi, extra jengibre"
    )
    
    # Agregar items
    OrdenItem.objects.create(orden=orden1, producto=productos[0], cantidad=2, precio_unitario=productos[0].precio)  # California Roll
    OrdenItem.objects.create(orden=orden1, producto=productos[3], cantidad=1, precio_unitario=productos[3].precio)  # Salmon Sashimi
    
    print(f"✅ Orden #{orden1.numero_orden} - Mesa {mesa1.numero} (hace 30 segundos)")

    # ORDEN 2: Hace 2 minutos y 15 segundos - Mostrará minutos y segundos
    orden2_fecha = ahora - timedelta(minutes=2, seconds=15)
    orden2 = Orden.objects.create(
        numero_orden=f"ORD-{int(ahora.timestamp())}-2",
        mesa=mesa2,
        mesero=mesero,
        estado='en_preparacion',
        fecha_creacion=orden2_fecha,
        observaciones="Mesa VIP - Servir primero el sashimi"
    )
    
    OrdenItem.objects.create(orden=orden2, producto=productos[1], cantidad=1, precio_unitario=productos[1].precio)  # Philadelphia Roll
    OrdenItem.objects.create(orden=orden2, producto=productos[4], cantidad=1, precio_unitario=productos[4].precio)  # Dragon Roll
    
    print(f"✅ Orden #{orden2.numero_orden} - Mesa {mesa2.numero} (hace 2m 15s)")

    # ORDEN 3: Hace 5 minutos y 45 segundos - En tolerancia
    orden3_fecha = ahora - timedelta(minutes=5, seconds=45)
    orden3 = Orden.objects.create(
        numero_orden=f"ORD-{int(ahora.timestamp())}-3",
        mesa=mesa3,
        mesero=mesero,
        estado='en_preparacion',
        fecha_creacion=orden3_fecha,
        observaciones="Sin cebolla, alergia"
    )
    
    OrdenItem.objects.create(orden=orden3, producto=productos[2], cantidad=2, precio_unitario=productos[2].precio)  # Tempura Roll
    OrdenItem.objects.create(orden=orden3, producto=productos[5], cantidad=1, precio_unitario=productos[5].precio)  # Rainbow Roll
    
    print(f"✅ Orden #{orden3.numero_orden} - Mesa {mesa3.numero} (hace 5m 45s)")

    # ORDEN 4: Hace 12 minutos - Ligeramente retrasada
    orden4_fecha = ahora - timedelta(minutes=12)
    orden4 = Orden.objects.create(
        numero_orden=f"ORD-{int(ahora.timestamp())}-4",
        mesa=mesa1,
        mesero=mesero,
        estado='en_preparacion',
        fecha_creacion=orden4_fecha,
        observaciones="Orden para llevar"
    )
    
    OrdenItem.objects.create(orden=orden4, producto=productos[0], cantidad=3, precio_unitario=productos[0].precio)  # California Roll
    OrdenItem.objects.create(orden=orden4, producto=productos[1], cantidad=2, precio_unitario=productos[1].precio)  # Philadelphia Roll
    
    print(f"⚠️ Orden #{orden4.numero_orden} - Mesa {mesa1.numero} (hace 12m) - EN TOLERANCIA")

    # ORDEN 5: Hace 25 minutos - RETRASADA
    orden5_fecha = ahora - timedelta(minutes=25)
    orden5 = Orden.objects.create(
        numero_orden=f"ORD-{int(ahora.timestamp())}-5",
        mesa=mesa2,
        mesero=mesero,
        estado='en_preparacion',
        fecha_creacion=orden5_fecha,
        observaciones="¡URGENTE! - Cliente esperando hace tiempo"
    )
    
    OrdenItem.objects.create(orden=orden5, producto=productos[4], cantidad=2, precio_unitario=productos[4].precio)  # Dragon Roll
    OrdenItem.objects.create(orden=orden5, producto=productos[5], cantidad=2, precio_unitario=productos[5].precio)  # Rainbow Roll
    OrdenItem.objects.create(orden=orden5, producto=productos[3], cantidad=3, precio_unitario=productos[3].precio)  # Salmon Sashimi
    
    print(f"🚨 Orden #{orden5.numero_orden} - Mesa {mesa2.numero} (hace 25m) - RETRASADA")

    # ORDEN COMPLETADA para pruebas del tab
    orden_completada_fecha = ahora - timedelta(minutes=35)
    orden_completada = Orden.objects.create(
        numero_orden=f"ORD-{int(ahora.timestamp())}-C1",
        mesa=mesa3,
        mesero=mesero,
        estado='entregada',
        fecha_creacion=orden_completada_fecha,
        fecha_lista=ahora - timedelta(minutes=3),
        observaciones="Orden completada de prueba"
    )
    
    OrdenItem.objects.create(orden=orden_completada, producto=productos[0], cantidad=1, precio_unitario=productos[0].precio)
    
    print(f"✅ Orden #{orden_completada.numero_orden} - COMPLETADA (hace 3m)")

    print("\n" + "="*60)
    print("🍣 ÓRDENES DE TIEMPO REAL CREADAS EXITOSAMENTE")
    print("="*60)
    print(f"📊 Resumen:")
    print(f"   • Orden reciente (30s): Mostrará segundos")
    print(f"   • Orden media (2m 15s): Mostrará min:seg")
    print(f"   • Orden tolerancia (5m 45s): Mostrará minutos")
    print(f"   • Orden en progreso (12m): Estado tolerancia")
    print(f"   • Orden retrasada (25m): Estado crítico")
    print(f"   • Orden completada: Para pruebas del tab")
    print("\n🔄 Los timers se actualizarán cada segundo en el dashboard")
    print("💡 Visita: http://127.0.0.1:8000/cocina/dashboard/")

if __name__ == '__main__':
    crear_ordenes_tiempo_real()
