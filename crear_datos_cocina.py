#!/usr/bin/env python3
"""
Script para crear datos de prueba para la aplicación de cocina
"""

import os
import sys
import django
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario
from mesero.models import Orden, OrdenItem, Mesa
from restaurant.models import ProductoVenta, CategoriaProducto
from cocina.models import TiempoPreparacion, EstadoCocina, OrdenCocina, ItemCocina, LogCocina
from django.contrib.auth.models import Group

def crear_datos_cocina():
    """Crear datos básicos para la aplicación de cocina"""
    
    print("🍣 CREANDO DATOS DE PRUEBA PARA COCINA")
    print("=" * 50)
    
    # 1. Crear grupo de cocina si no existe
    print("1. Creando grupo de Cocina...")
    cocina_group, created = Group.objects.get_or_create(name='Cocina')
    if created:
        print("   ✅ Grupo 'Cocina' creado")
    else:
        print("   ℹ️  Grupo 'Cocina' ya existe")
    
    # 2. Crear usuario de cocina si no existe
    print("2. Creando usuario de cocina...")
    try:
        usuario_cocina = Usuario.objects.get(username='cocinero1')
        print("   ℹ️  Usuario 'cocinero1' ya existe")
    except Usuario.DoesNotExist:
        usuario_cocina = Usuario.objects.create_user(
            username='cocinero1',
            password='cocina123',
            email='cocinero1@sushi.com',
            first_name='Juan',
            last_name='Cocinero',
            is_staff=True,
            is_active=True
        )
        usuario_cocina.groups.add(cocina_group)
        print("   ✅ Usuario 'cocinero1' creado y agregado al grupo Cocina")
    
    # 3. Crear productos de ejemplo si no existen
    print("3. Creando productos de ejemplo...")
    productos_ejemplo = [
        ('Sushi Salmón', 'Sushi de salmón fresco', 12.50, 8),
        ('Sushi Atún', 'Sushi de atún rojo', 15.00, 10),
        ('Maki Philadelphia', 'Maki con salmón y queso crema', 18.50, 12),
        ('Nigiri Ebi', 'Nigiri de camarón cocido', 8.00, 5),
        ('Temaki Spicy', 'Temaki picante mixto', 14.00, 15),
        ('Sashimi Salmón', 'Sashimi de salmón fresco', 22.00, 7),
        ('Uramaki California', 'Uramaki con cangrejo y aguacate', 16.50, 10),
        ('Onigiri Tradicional', 'Onigiri con relleno de atún', 6.50, 5),
    ]
    
    for nombre, descripcion, precio, tiempo_est in productos_ejemplo:
        producto, created = ProductoVenta.objects.get_or_create(
            nombre=nombre,
            defaults={
                'codigo': f'PROD{len(ProductoVenta.objects.all()) + 1:03d}',
                'descripcion': descripcion,
                'precio': Decimal(str(precio)),
                'disponible': True,
                'tipo': 'plato'
            }
        )
        if created:
            print(f"   ✅ Producto '{nombre}' creado")
            
            # Crear tiempo de preparación
            tiempo_prep, tp_created = TiempoPreparacion.objects.get_or_create(
                producto=producto,
                defaults={
                    'tiempo_estimado': tiempo_est,
                    'tiempo_promedio': tiempo_est,
                    'cantidad_preparaciones': 0
                }
            )
            if tp_created:
                print(f"     ➡️  Tiempo de preparación: {tiempo_est} minutos")
        else:
            print(f"   ℹ️  Producto '{nombre}' ya existe")
    
    # 4. Crear estados de cocina
    print("4. Creando estados de cocina...")
    estados = [
        ('pendiente', 'Pendiente de preparación'),
        ('en_preparacion', 'En preparación'),
        ('lista', 'Lista para servir'),
        ('entregada', 'Entregada al mesero'),
        ('cancelada', 'Cancelada')
    ]
    
    for nombre, descripcion in estados:
        estado, created = EstadoCocina.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': descripcion}
        )
        if created:
            print(f"   ✅ Estado '{nombre}' creado")
        else:
            print(f"   ℹ️  Estado '{nombre}' ya existe")
    
    # 5. Crear mesas de ejemplo
    print("5. Creando mesas de ejemplo...")
    
    # Necesitamos una sucursal para las mesas
    from accounts.models import Sucursal
    
    # Obtener la primera sucursal o crear una
    sucursal = Sucursal.objects.first()
    if not sucursal:
        sucursal = Sucursal.objects.create(
            nombre='Sucursal Principal',
            direccion='Dirección Principal',
            telefono='123456789',
            activa=True
        )
        print(f"   ✅ Sucursal creada: {sucursal.nombre}")
    
    for i in range(1, 11):
        mesa, created = Mesa.objects.get_or_create(
            numero=str(i),
            defaults={
                'capacidad': 4,
                'sucursal': sucursal,
                'estado': 'disponible',
                'ubicacion': f'Zona A',
                'activa': True
            }
        )
        if created:
            print(f"   ✅ Mesa {i} creada")
        else:
            print(f"   ℹ️  Mesa {i} ya existe")
    
    # 6. Crear órdenes de ejemplo
    print("6. Creando órdenes de ejemplo...")
    mesas = Mesa.objects.all()[:5]  # Usar las primeras 5 mesas
    productos = ProductoVenta.objects.all()[:4]  # Usar los primeros 4 productos
    
    for i, mesa in enumerate(mesas, 1):
        # Crear orden
        orden = Orden.objects.create(
            mesa=mesa,
            mesero=usuario_cocina,
            estado='confirmada',
            total=Decimal('0.00'),
            fecha_creacion=timezone.now() - timedelta(minutes=i*10)
        )
        
        total_orden = Decimal('0.00')
        
        # Agregar items a la orden
        for j, producto in enumerate(productos[:2+i%3], 1):
            cantidad = j
            subtotal = producto.precio * cantidad
            total_orden += subtotal
            
            orden_item = OrdenItem.objects.create(
                orden=orden,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio,
                subtotal=subtotal,
                estado='pendiente'
            )
            
            # Crear entrada en cocina
            orden_cocina, oc_created = OrdenCocina.objects.get_or_create(
                orden=orden,
                defaults={
                    'cocinero_asignado': usuario_cocina,
                    'prioridad': 1,
                    'tiempo_estimado_total': 30,
                    'notas_cocina': f'Orden para mesa {mesa.numero}'
                }
            )
            
            if oc_created:
                # Crear item de cocina
                ItemCocina.objects.create(
                    orden_item=orden_item,
                    estado_cocina='recibida',
                    cocinero_responsable=usuario_cocina,
                    notas_preparacion=f'Item {j} de la orden {orden.numero_orden}'
                )
        
        orden.total = total_orden
        orden.save()
        
        print(f"   ✅ Orden {orden.id} creada para mesa {mesa.numero} (${total_orden})")
    
    # 7. Crear algunos logs de ejemplo
    print("7. Creando logs de ejemplo...")
    ordenes_cocina = OrdenCocina.objects.all()
    
    for orden_cocina in ordenes_cocina[:3]:
        LogCocina.objects.create(
            orden=orden_cocina.orden,
            accion='orden_recibida',
            usuario=usuario_cocina,
            descripcion=f'Orden recibida de mesa {orden_cocina.orden.mesa.numero}'
        )
        
        LogCocina.objects.create(
            orden=orden_cocina.orden,
            accion='preparacion_iniciada',
            usuario=usuario_cocina,
            descripcion=f'Iniciada preparación de orden {orden_cocina.orden.numero_orden}'
        )
    
    print("   ✅ Logs de ejemplo creados")
    
    print("\n" + "=" * 50)
    print("✅ DATOS DE COCINA CREADOS EXITOSAMENTE")
    print("\n📊 RESUMEN:")
    print(f"   • Productos: {ProductoVenta.objects.count()}")
    print(f"   • Tiempos de preparación: {TiempoPreparacion.objects.count()}")
    print(f"   • Estados de cocina: {EstadoCocina.objects.count()}")
    print(f"   • Mesas: {Mesa.objects.count()}")
    print(f"   • Órdenes: {Orden.objects.count()}")
    print(f"   • Órdenes en cocina: {OrdenCocina.objects.count()}")
    print(f"   • Items de cocina: {ItemCocina.objects.count()}")
    print(f"   • Logs de cocina: {LogCocina.objects.count()}")
    print(f"   • Usuarios de cocina: {Usuario.objects.filter(groups__name='Cocina').count()}")
    
    print("\n🔑 CREDENCIALES DE ACCESO:")
    print("   Usuario: cocinero1")
    print("   Contraseña: cocina123")
    print("\n🌐 URL de acceso: http://localhost:8000/cocina/")

if __name__ == "__main__":
    crear_datos_cocina()
