#!/usr/bin/env python
"""
Script para generar más datos de prueba en el dashboard de comandas
"""

import os
import sys
import django
from datetime import timedelta
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.utils import timezone
from mesero.models import Orden, OrdenItem, Mesa
from restaurant.models import ProductoVenta
from accounts.models import Usuario
from decimal import Decimal

def crear_mas_ordenes():
    """Crear más órdenes de prueba para el dashboard"""
    print("=== CREANDO MÁS ÓRDENES DE PRUEBA ===")
    
    # Obtener datos necesarios
    try:
        chef = Usuario.objects.get(username='chef')
        mesas = Mesa.objects.all()
        productos = ProductoVenta.objects.all()
        
        if not mesas.exists():
            print("❌ No hay mesas disponibles")
            return
        
        if not productos.exists():
            print("❌ No hay productos disponibles")
            return
        
        ahora = timezone.now()
        ordenes_creadas = 0
        
        # 1. Crear más órdenes retrasadas (35-50 minutos)
        print("📋 Creando órdenes muy retrasadas...")
        for i in range(3):
            minutos_atraso = random.randint(35, 50)
            fecha_orden = ahora - timedelta(minutes=minutos_atraso)
            
            orden = Orden.objects.create(
                numero_orden=f"RET{5000 + i}",
                mesa=random.choice(mesas),
                mesero=chef,
                estado='confirmada',
                fecha_creacion=fecha_orden,
                subtotal=Decimal(str(random.uniform(20.0, 35.0))),
                total=Decimal(str(random.uniform(22.0, 39.0))),
                tipo_servicio='mesa'
            )
            
            # Agregar 2-4 items
            for j in range(random.randint(2, 4)):
                producto = random.choice(productos)
                OrdenItem.objects.create(
                    orden=orden,
                    producto=producto,
                    cantidad=random.randint(1, 2),
                    precio_unitario=producto.precio,
                    estado='pendiente'
                )
            
            ordenes_creadas += 1
            print(f"   ⏰ Orden muy retrasada {orden.numero_orden} - Mesa {orden.mesa.numero} ({minutos_atraso} min)")
        
        # 2. Crear órdenes en tolerancia (16-18 minutos)
        print("📋 Creando órdenes en tolerancia...")
        for i in range(4):
            minutos_tolerancia = random.randint(16, 18)
            fecha_orden = ahora - timedelta(minutes=minutos_tolerancia)
            
            orden = Orden.objects.create(
                numero_orden=f"TOL{6000 + i}",
                mesa=random.choice(mesas),
                mesero=chef,
                estado='en_preparacion',
                fecha_creacion=fecha_orden,
                fecha_preparacion=fecha_orden + timedelta(minutes=2),
                subtotal=Decimal(str(random.uniform(15.0, 28.0))),
                total=Decimal(str(random.uniform(17.0, 31.0))),
                tipo_servicio='mesa'
            )
            
            # Agregar 1-3 items
            for j in range(random.randint(1, 3)):
                producto = random.choice(productos)
                OrdenItem.objects.create(
                    orden=orden,
                    producto=producto,
                    cantidad=random.randint(1, 2),
                    precio_unitario=producto.precio,
                    estado='en_preparacion'
                )
            
            ordenes_creadas += 1
            print(f"   ⚠️ Orden en tolerancia {orden.numero_orden} - Mesa {orden.mesa.numero} ({minutos_tolerancia} min)")
        
        # 3. Crear órdenes normales (5-14 minutos)
        print("📋 Creando órdenes normales...")
        for i in range(6):
            minutos_normal = random.randint(5, 14)
            fecha_orden = ahora - timedelta(minutes=minutos_normal)
            
            orden = Orden.objects.create(
                numero_orden=f"NOR{7000 + i}",
                mesa=random.choice(mesas),
                mesero=chef,
                estado='confirmada',
                fecha_creacion=fecha_orden,
                fecha_confirmacion=fecha_orden + timedelta(minutes=1),
                subtotal=Decimal(str(random.uniform(12.0, 25.0))),
                total=Decimal(str(random.uniform(14.0, 28.0))),
                tipo_servicio='mesa'
            )
            
            # Agregar 1-3 items
            for j in range(random.randint(1, 3)):
                producto = random.choice(productos)
                OrdenItem.objects.create(
                    orden=orden,
                    producto=producto,
                    cantidad=random.randint(1, 2),
                    precio_unitario=producto.precio,
                    estado='pendiente'
                )
            
            ordenes_creadas += 1
            print(f"   ✅ Orden normal {orden.numero_orden} - Mesa {orden.mesa.numero} ({minutos_normal} min)")
        
        # 4. Crear órdenes muy nuevas (1-4 minutos)
        print("📋 Creando órdenes muy nuevas...")
        for i in range(3):
            minutos_nuevo = random.randint(1, 4)
            fecha_orden = ahora - timedelta(minutes=minutos_nuevo)
            
            orden = Orden.objects.create(
                numero_orden=f"NEW{8000 + i}",
                mesa=random.choice(mesas),
                mesero=chef,
                estado='pendiente',
                fecha_creacion=fecha_orden,
                subtotal=Decimal(str(random.uniform(8.0, 20.0))),
                total=Decimal(str(random.uniform(9.0, 22.0))),
                tipo_servicio='mesa'
            )
            
            # Agregar 1-2 items
            for j in range(random.randint(1, 2)):
                producto = random.choice(productos)
                OrdenItem.objects.create(
                    orden=orden,
                    producto=producto,
                    cantidad=random.randint(1, 2),
                    precio_unitario=producto.precio,
                    estado='pendiente'
                )
            
            ordenes_creadas += 1
            print(f"   🆕 Orden nueva {orden.numero_orden} - Mesa {orden.mesa.numero} ({minutos_nuevo} min)")
        
        print(f"\n✅ {ordenes_creadas} nuevas órdenes de prueba creadas")
        
        # Mostrar resumen
        total_ordenes = Orden.objects.filter(
            estado__in=['pendiente', 'confirmada', 'en_preparacion']
        ).count()
        print(f"📊 Total de órdenes activas: {total_ordenes}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def mostrar_estado_dashboard():
    """Mostrar el estado actual del dashboard"""
    print("\n=== ESTADO ACTUAL DEL DASHBOARD ===")
    
    from django.utils import timezone
    ahora = timezone.now()
    
    ordenes_activas = Orden.objects.filter(
        estado__in=['pendiente', 'confirmada', 'en_preparacion']
    ).order_by('fecha_creacion')
    
    retrasadas = 0
    tolerancia = 0
    normales = 0
    
    for orden in ordenes_activas:
        tiempo_transcurrido = int((ahora - orden.fecha_creacion).total_seconds() / 60)
        
        if tiempo_transcurrido > 16.5:  # 15 + 1.5 tolerancia
            categoria = "RETRASADA"
            retrasadas += 1
        elif tiempo_transcurrido > 15:
            categoria = "TOLERANCIA"
            tolerancia += 1
        else:
            categoria = "NORMAL"
            normales += 1
        
        print(f"📋 {orden.numero_orden} - Mesa {orden.mesa.numero} - {tiempo_transcurrido}m - {categoria}")
    
    print(f"\n📊 RESUMEN:")
    print(f"🔴 Retrasadas: {retrasadas}")
    print(f"🟡 En tolerancia: {tolerancia}")
    print(f"🟢 Normales: {normales}")
    print(f"📝 Total: {len(ordenes_activas)}")

if __name__ == "__main__":
    crear_mas_ordenes()
    mostrar_estado_dashboard()
    print("\n🌐 Actualiza http://127.0.0.1:8000/cocina/ para ver los cambios")
