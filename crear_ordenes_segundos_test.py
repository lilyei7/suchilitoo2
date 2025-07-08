#!/usr/bin/env python3
"""
Script para crear órdenes de prueba con tiempos muy recientes
para demostrar la funcionalidad de timer en tiempo real con segundos.
"""

import os
import django
import sys
from datetime import datetime, timedelta
from django.utils import timezone
import random

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import Orden, OrdenItem, Mesa
from restaurant.models import ProductoVenta, CategoriaProducto
from accounts.models import Usuario, Sucursal

def crear_ordenes_segundos_test():
    """Crear órdenes de prueba con tiempos muy recientes para test de segundos"""
    
    print("🍣 Creando órdenes de prueba para test de timer en segundos...")
    
    # Obtener o crear datos necesarios
    try:
        sucursal = Sucursal.objects.first()
        if not sucursal:
            sucursal = Sucursal.objects.create(
                nombre="Sucursal Test",
                direccion="Test Address",
                telefono="555-0000"
            )
            print(f"✅ Creada sucursal: {sucursal.nombre}")
        
        # Crear mesas si no existen
        mesas = []
        for i in range(1, 6):  # Mesas 1-5
            mesa, created = Mesa.objects.get_or_create(
                numero=i,
                sucursal=sucursal,
                defaults={'capacidad': 4}
            )
            mesas.append(mesa)
            if created:
                print(f"✅ Creada mesa {mesa.numero}")
        
        # Obtener un mesero
        mesero = Usuario.objects.filter(
            groups__name__in=['Mesero', 'Meseros']
        ).first()
        
        if not mesero:
            # Crear un mesero de prueba
            from django.contrib.auth.models import Group
            mesero = Usuario.objects.create_user(
                username='mesero_test_segundos',
                password='password123',
                first_name='Mesero',
                last_name='Test Segundos',
                email='mesero_segundos@test.com',
                sucursal=sucursal
            )
            
            group, _ = Group.objects.get_or_create(name='Meseros')
            mesero.groups.add(group)
            print(f"✅ Creado mesero: {mesero.get_full_name()}")
        
        # Obtener productos
        productos = list(ProductoVenta.objects.all()[:10])
        if not productos:
            # Crear algunos productos básicos
            categoria, _ = CategoriaProducto.objects.get_or_create(
                nombre="Sushi Test",
                defaults={'descripcion': 'Categoría test para sushi'}
            )
            
            productos_crear = [
                ('California Roll', 12.50),
                ('Salmón Nigiri', 3.50),
                ('Tuna Roll', 10.00),
                ('Miso Soup', 4.50),
                ('Edamame', 5.00),
            ]
            
            for nombre, precio in productos_crear:
                producto, created = ProductoVenta.objects.get_or_create(
                    nombre=nombre,
                    defaults={
                        'precio': precio,
                        'categoria': categoria,
                        'disponible': True,
                        'descripcion': f'Producto test: {nombre}'
                    }
                )
                productos.append(producto)
                if created:
                    print(f"✅ Creado producto: {nombre}")
        
        # Hora actual
        ahora = timezone.now()
        
        # Crear órdenes con diferentes tiempos para test de segundos
        ordenes_crear = [
            # Orden muy reciente (5 segundos)
            {
                'offset_seconds': -5,
                'mesa': mesas[0],
                'descripcion': 'Orden de 5 segundos atrás'
            },
            # Orden reciente (15 segundos)
            {
                'offset_seconds': -15,
                'mesa': mesas[1],
                'descripcion': 'Orden de 15 segundos atrás'
            },
            # Orden reciente (30 segundos)
            {
                'offset_seconds': -30,
                'mesa': mesas[2],
                'descripcion': 'Orden de 30 segundos atrás'
            },
            # Orden reciente (45 segundos)
            {
                'offset_seconds': -45,
                'mesa': mesas[3],
                'descripción': 'Orden de 45 segundos atrás'
            },
            # Orden de casi 1 minuto (55 segundos)
            {
                'offset_seconds': -55,
                'mesa': mesas[4],
                'descripcion': 'Orden de 55 segundos atrás'
            }
        ]
        
        ordenes_creadas = []
        
        for i, orden_data in enumerate(ordenes_crear):
            # Calcular fecha de creación
            fecha_creacion = ahora + timedelta(seconds=orden_data['offset_seconds'])
            
            # Crear la orden
            orden = Orden.objects.create(
                mesa=orden_data['mesa'],
                mesero=mesero,
                estado='confirmada',  # Órdenes confirmadas aparecen en cocina
                fecha_creacion=fecha_creacion,
                total=0  # Se calculará después
            )
            
            # Agregar productos a la orden
            total_orden = 0
            num_items = random.randint(1, 3)  # 1-3 productos por orden
            productos_seleccionados = random.sample(productos, min(num_items, len(productos)))
            
            for producto in productos_seleccionados:
                cantidad = random.randint(1, 2)
                item = OrdenItem.objects.create(
                    orden=orden,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio
                )
                total_orden += producto.precio * cantidad
            
            # Actualizar total de la orden
            orden.total = total_orden
            orden.save()
            
            ordenes_creadas.append(orden)
            print(f"✅ Creada orden #{orden.numero_orden} - Mesa {orden.mesa.numero} - "
                  f"hace {abs(orden_data['offset_seconds'])} segundos")
        
        print(f"\n🎉 ¡Proceso completado!")
        print(f"📊 Resumen:")
        print(f"   • {len(ordenes_creadas)} órdenes creadas con tiempos en segundos")
        print(f"   • Tiempos: 5s, 15s, 30s, 45s, 55s atrás")
        print(f"   • Estado: Confirmadas (aparecen en cocina)")
        print(f"   • Mesero: {mesero.get_full_name()}")
        print(f"   • Sucursal: {sucursal.nombre}")
        
        print(f"\n🚀 Ve al dashboard de cocina para ver los timers en tiempo real:")
        print(f"   http://127.0.0.1:8000/cocina/")
        print(f"   Los timers mostrarán segundos para órdenes de menos de 1 minuto")
        print(f"   Y cambiarán automáticamente a minutos después de 1 minuto")
        
        return ordenes_creadas
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    ordenes = crear_ordenes_segundos_test()
    print(f"\n✨ Órdenes creadas: {len(ordenes)}")
