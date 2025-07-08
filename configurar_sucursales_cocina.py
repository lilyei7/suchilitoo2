#!/usr/bin/env python
"""
Script para configurar el sistema de sucursales y datos de prueba para cocina
Este script es seguro y no afectará datos existentes
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
from django.contrib.auth.models import Group
from accounts.models import Sucursal, Usuario
from mesero.models import Mesa, Orden, OrdenItem
from restaurant.models import ProductoVenta
from decimal import Decimal

def verificar_estado_actual():
    """Verifica el estado actual del sistema"""
    print("=== VERIFICANDO ESTADO ACTUAL ===")
    
    # Verificar sucursales
    sucursales = Sucursal.objects.all()
    print(f"📍 Sucursales existentes: {sucursales.count()}")
    for s in sucursales:
        print(f"   - {s.nombre} (ID: {s.id}) - Activa: {s.activa}")
    
    # Verificar usuario chef
    try:
        chef = Usuario.objects.get(username='chef')
        print(f"👨‍🍳 Chef existe - Sucursal asignada: {chef.sucursal.nombre if chef.sucursal else 'Sin asignar'}")
    except Usuario.DoesNotExist:
        print("👨‍🍳 Chef no existe")
    
    # Verificar mesas
    mesas = Mesa.objects.all()
    print(f"🪑 Mesas totales: {mesas.count()}")
    mesas_por_sucursal = {}
    for mesa in mesas:
        sucursal_nombre = mesa.sucursal.nombre
        if sucursal_nombre not in mesas_por_sucursal:
            mesas_por_sucursal[sucursal_nombre] = 0
        mesas_por_sucursal[sucursal_nombre] += 1
    
    for sucursal, cantidad in mesas_por_sucursal.items():
        print(f"   - {sucursal}: {cantidad} mesas")
    
    # Verificar productos
    productos = ProductoVenta.objects.all()
    print(f"🍱 Productos disponibles: {productos.count()}")
    
    # Verificar órdenes existentes
    ordenes = Orden.objects.all()
    print(f"📝 Órdenes existentes: {ordenes.count()}")
    
    print("\n" + "="*50)
    return sucursales, chef if 'chef' in locals() else None, mesas, productos

def configurar_sucursal_y_chef():
    """Configura la sucursal y usuario chef de forma segura"""
    print("=== CONFIGURANDO SUCURSAL Y CHEF ===")
    
    # Obtener o crear grupo Cocina
    cocina_group, created = Group.objects.get_or_create(name='Cocina')
    if created:
        print("✅ Grupo 'Cocina' creado")
    else:
        print("ℹ️  Grupo 'Cocina' ya existe")
    
    # Verificar sucursales existentes
    sucursales = Sucursal.objects.all()
    
    if not sucursales.exists():
        print("🏢 No hay sucursales, creando Sucursal Central...")
        sucursal_central = Sucursal.objects.create(
            nombre='Sucursal Central',
            direccion='Av. Principal 123, Centro',
            telefono='555-0123',
            email='central@restaurant.com',
            activa=True
        )
        print(f"✅ Sucursal creada: {sucursal_central.nombre}")
    else:
        sucursal_central = sucursales.first()
        print(f"ℹ️  Usando sucursal existente: {sucursal_central.nombre}")
    
    # Verificar y configurar usuario chef
    try:
        chef_user = Usuario.objects.get(username='chef')
        if not chef_user.sucursal:
            chef_user.sucursal = sucursal_central
            chef_user.save()
            print(f"✅ Sucursal asignada al chef: {chef_user.sucursal.nombre}")
        else:
            print(f"ℹ️  Chef ya tiene sucursal: {chef_user.sucursal.nombre}")
            sucursal_central = chef_user.sucursal  # Usar la sucursal del chef
        
        # Asegurar que el chef esté en el grupo Cocina
        if not chef_user.groups.filter(name='Cocina').exists():
            chef_user.groups.add(cocina_group)
            print("✅ Chef agregado al grupo Cocina")
            
    except Usuario.DoesNotExist:
        print("👨‍🍳 Creando usuario chef...")
        chef_user = Usuario.objects.create_user(
            username='chef',
            password='chef123',
            first_name='Chef',
            last_name='Principal',
            email='chef@restaurant.com',
            is_staff=True,
            sucursal=sucursal_central
        )
        chef_user.groups.add(cocina_group)
        print(f"✅ Usuario chef creado en sucursal: {chef_user.sucursal.nombre}")
    
    return sucursal_central, chef_user

def configurar_mesas(sucursal):
    """Configura las mesas para la sucursal"""
    print(f"=== CONFIGURANDO MESAS PARA {sucursal.nombre.upper()} ===")
    
    mesas_existentes = Mesa.objects.filter(sucursal=sucursal)
    mesas_creadas = 0
    
    for i in range(1, 6):  # Crear mesas 1-5
        mesa, created = Mesa.objects.get_or_create(
            numero=str(i),
            sucursal=sucursal,
            defaults={
                'capacidad': 4,
                'estado': 'disponible',
                'activa': True,
                'ubicacion': f'Salón principal' if i <= 3 else 'Terraza'
            }
        )
        if created:
            mesas_creadas += 1
            print(f"✅ Mesa {i} creada")
    
    if mesas_creadas == 0:
        print(f"ℹ️  Todas las mesas ya existen ({mesas_existentes.count()} mesas)")
    else:
        print(f"✅ {mesas_creadas} mesas creadas")
    
    return Mesa.objects.filter(sucursal=sucursal)

def configurar_productos():
    """Configura productos de prueba"""
    print("=== CONFIGURANDO PRODUCTOS ===")
    
    productos_data = [
        {'nombre': 'Sushi Salmón', 'precio': 15.99, 'codigo': 'SUSHI-001'},
        {'nombre': 'Ramen Tonkotsu', 'precio': 12.50, 'codigo': 'RAMEN-001'},
        {'nombre': 'Tempura Mixta', 'precio': 18.00, 'codigo': 'TEMPURA-001'},
        {'nombre': 'Sashimi Variado', 'precio': 22.00, 'codigo': 'SASHIMI-001'},
        {'nombre': 'Udon Vegetal', 'precio': 10.50, 'codigo': 'UDON-001'},
        {'nombre': 'Maki California', 'precio': 8.99, 'codigo': 'MAKI-001'},
        {'nombre': 'Teriyaki Chicken', 'precio': 14.50, 'codigo': 'TERIYAKI-001'},
        {'nombre': 'Gyoza (6 piezas)', 'precio': 7.99, 'codigo': 'GYOZA-001'}
    ]
    
    productos = []
    productos_creados = 0
    
    for prod_data in productos_data:
        producto, created = ProductoVenta.objects.get_or_create(
            codigo=prod_data['codigo'],
            defaults={
                'nombre': prod_data['nombre'],
                'precio': Decimal(str(prod_data['precio'])),
                'disponible': True,
                'descripcion': f'Delicioso {prod_data["nombre"]} preparado con ingredientes frescos'
            }
        )
        productos.append(producto)
        if created:
            productos_creados += 1
            print(f"✅ Producto creado: {producto.nombre}")
    
    if productos_creados == 0:
        print("ℹ️  Todos los productos ya existen")
    else:
        print(f"✅ {productos_creados} productos creados")
    
    return productos

def crear_ordenes_prueba(sucursal, chef_user, mesas, productos):
    """Crea órdenes de prueba para mostrar el dashboard"""
    print("=== CREANDO ÓRDENES DE PRUEBA ===")
    
    if not productos:
        print("❌ No hay productos disponibles para crear órdenes")
        return
    
    ahora = timezone.now()
    ordenes_creadas = 0
    
    # 1. Órdenes retrasadas (más de 25 minutos)
    print("📋 Creando órdenes retrasadas...")
    for i in range(2):
        minutos_atraso = random.randint(30, 45)
        fecha_orden = ahora - timedelta(minutes=minutos_atraso)
        
        orden = Orden.objects.create(
            numero_orden=f"OR{1000 + i}",
            mesa=random.choice(mesas),
            mesero=chef_user,
            estado='confirmada',
            fecha_creacion=fecha_orden,
            subtotal=Decimal('25.00'),
            total=Decimal('28.00'),
            tipo_servicio='mesa'
        )
        
        # Agregar items
        for j in range(random.randint(2, 3)):
            producto = random.choice(productos)
            OrdenItem.objects.create(
                orden=orden,
                producto=producto,
                cantidad=random.randint(1, 2),
                precio_unitario=producto.precio,
                estado='pendiente'
            )
        
        ordenes_creadas += 1
        print(f"   ⏰ Orden retrasada {orden.numero_orden} - Mesa {orden.mesa.numero}")
    
    # 2. Órdenes en proceso
    print("📋 Creando órdenes en proceso...")
    for i in range(3):
        minutos_proceso = random.randint(10, 20)
        fecha_orden = ahora - timedelta(minutes=minutos_proceso)
        
        orden = Orden.objects.create(
            numero_orden=f"OR{2000 + i}",
            mesa=random.choice(mesas),
            mesero=chef_user,
            estado='en_preparacion',
            fecha_creacion=fecha_orden,
            fecha_preparacion=fecha_orden + timedelta(minutes=2),
            subtotal=Decimal('32.50'),
            total=Decimal('36.40'),
            tipo_servicio='mesa'
        )
        
        # Agregar items
        for j in range(random.randint(2, 4)):
            producto = random.choice(productos)
            OrdenItem.objects.create(
                orden=orden,
                producto=producto,
                cantidad=random.randint(1, 2),
                precio_unitario=producto.precio,
                estado='en_preparacion'
            )
        
        ordenes_creadas += 1
        print(f"   🔄 Orden en proceso {orden.numero_orden} - Mesa {orden.mesa.numero}")
    
    # 3. Nuevos pedidos
    print("📋 Creando nuevos pedidos...")
    for i in range(4):
        minutos_nuevo = random.randint(5, 15)
        fecha_orden = ahora - timedelta(minutes=minutos_nuevo)
        
        orden = Orden.objects.create(
            numero_orden=f"OR{3000 + i}",
            mesa=random.choice(mesas),
            mesero=chef_user,
            estado='confirmada',
            fecha_creacion=fecha_orden,
            fecha_confirmacion=fecha_orden + timedelta(minutes=1),
            subtotal=Decimal('18.75'),
            total=Decimal('21.00'),
            tipo_servicio='mesa'
        )
        
        # Agregar items
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
        print(f"   🆕 Nuevo pedido {orden.numero_orden} - Mesa {orden.mesa.numero}")
    
    # 4. Órdenes completadas
    print("📋 Creando órdenes completadas...")
    for i in range(2):
        minutos_completada = random.randint(30, 90)
        fecha_orden = ahora - timedelta(minutes=minutos_completada + 20)
        fecha_entrega = ahora - timedelta(minutes=minutos_completada)
        
        orden = Orden.objects.create(
            numero_orden=f"OR{4000 + i}",
            mesa=random.choice(mesas),
            mesero=chef_user,
            estado='entregada',
            fecha_creacion=fecha_orden,
            fecha_confirmacion=fecha_orden + timedelta(minutes=1),
            fecha_preparacion=fecha_orden + timedelta(minutes=3),
            fecha_lista=fecha_orden + timedelta(minutes=15),
            fecha_entrega=fecha_entrega,
            subtotal=Decimal('42.50'),
            total=Decimal('47.60'),
            tipo_servicio='mesa'
        )
        
        # Agregar items
        for j in range(random.randint(3, 5)):
            producto = random.choice(productos)
            OrdenItem.objects.create(
                orden=orden,
                producto=producto,
                cantidad=random.randint(1, 2),
                precio_unitario=producto.precio,
                estado='entregado'
            )
        
        ordenes_creadas += 1
        print(f"   ✅ Orden completada {orden.numero_orden} - Mesa {orden.mesa.numero}")
    
    print(f"✅ {ordenes_creadas} órdenes de prueba creadas")

def main():
    """Función principal del script"""
    print("🚀 INICIANDO CONFIGURACIÓN DE SISTEMA DE COCINA")
    print("="*60)
    
    try:
        # 1. Verificar estado actual
        sucursales, chef, mesas, productos = verificar_estado_actual()
        
        # 2. Configurar sucursal y chef
        sucursal_central, chef_user = configurar_sucursal_y_chef()
        
        # 3. Configurar mesas
        mesas = configurar_mesas(sucursal_central)
        
        # 4. Configurar productos
        productos = configurar_productos()
        
        # 5. Crear órdenes de prueba
        crear_ordenes_prueba(sucursal_central, chef_user, mesas, productos)
        
        print("\n" + "="*60)
        print("🎉 CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
        print("="*60)
        print(f"📍 Sucursal configurada: {sucursal_central.nombre}")
        print(f"👨‍🍳 Usuario chef: {chef_user.username} (contraseña: chef123)")
        print(f"🪑 Mesas disponibles: {mesas.count()}")
        print(f"🍱 Productos disponibles: {len(productos)}")
        print(f"📝 Órdenes de prueba: {Orden.objects.filter(mesa__sucursal=sucursal_central).count()}")
        print("\n🌐 Ahora puedes acceder a: http://127.0.0.1:8000/cocina/")
        print("   Usuario: chef")
        print("   Contraseña: chef123")
        
    except Exception as e:
        print(f"❌ Error durante la configuración: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
