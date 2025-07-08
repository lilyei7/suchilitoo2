#!/usr/bin/env python3
"""
Script para probar la funcionalidad completa de órdenes en el sistema mesero
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from mesero.models import Mesa, Orden, OrdenItem
from restaurant.models import ProductoVenta, CategoriaProducto
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

def main():
    print("=== PROBANDO SISTEMA COMPLETO DE ÓRDENES ===\n")
    
    # 1. Verificar mesas existentes
    print("1. VERIFICANDO MESAS...")
    mesas = Mesa.objects.all()
    print(f"   Mesas encontradas: {mesas.count()}")
    
    for mesa in mesas[:5]:  # Mostrar solo las primeras 5
        print(f"   - Mesa {mesa.numero}: {mesa.capacidad} personas, Estado: {mesa.estado}")
    
    if mesas.count() == 0:
        print("   ⚠️  No hay mesas. Creando mesas de ejemplo...")
        for i in range(1, 9):
            capacidad = 4 if i % 2 == 0 else 2 if i % 3 == 0 else 6
            Mesa.objects.create(
                numero=i,
                capacidad=capacidad,
                estado='disponible',
                descripcion=f'Mesa {i} para {capacidad} personas'
            )
        print(f"   ✅ Creadas {Mesa.objects.count()} mesas")
    
    # 2. Verificar productos
    print("\n2. VERIFICANDO PRODUCTOS...")
    productos = ProductoVenta.objects.filter(disponible=True)
    print(f"   Productos disponibles: {productos.count()}")
    
    if productos.count() == 0:
        print("   ⚠️  No hay productos disponibles")
        return
    
    for producto in productos[:3]:  # Mostrar solo los primeros 3
        print(f"   - {producto.nombre}: ${producto.precio}")
    
    # 3. Verificar usuarios meseros
    print("\n3. VERIFICANDO USUARIOS MESEROS...")
    meseros = User.objects.filter(is_staff=False)  # Buscar usuarios no admin
    
    if not meseros.exists():
        print("   ⚠️  No hay usuarios meseros. Creando usuario de prueba...")
        from accounts.models import Sucursal
        # Obtener la primera sucursal disponible
        sucursal = Sucursal.objects.first()
        if not sucursal:
            sucursal = Sucursal.objects.create(
                nombre='Sucursal Principal',
                direccion='Av. Principal 123',
                telefono='555-0123'
            )
        
        mesero = User.objects.create_user(
            username='mesero_test',
            password='test123',
            first_name='Juan',
            last_name='Pérez',
            email='mesero@test.com',
            sucursal=sucursal
        )
        print(f"   ✅ Usuario creado: {mesero.username}")
    else:
        mesero = meseros.first()
        print(f"   Mesero encontrado: {mesero.get_full_name() or mesero.username}")
    
    # 4. Verificar sucursales para las mesas
    print("\n4. VERIFICANDO SUCURSALES...")
    from accounts.models import Sucursal
    sucursales = Sucursal.objects.all()
    
    if not sucursales.exists():
        print("   ⚠️  No hay sucursales. Creando sucursal principal...")
        sucursal = Sucursal.objects.create(
            nombre='Sucursal Principal',
            direccion='Av. Principal 123',
            telefono='555-0123'
        )
        print(f"   ✅ Sucursal creada: {sucursal.nombre}")
    else:
        sucursal = sucursales.first()
        print(f"   Sucursal encontrada: {sucursal.nombre}")
    
    # Asignar sucursal a las mesas que no la tengan
    mesas_sin_sucursal = Mesa.objects.filter(sucursal__isnull=True)
    if mesas_sin_sucursal.exists():
        print(f"   Asignando sucursal a {mesas_sin_sucursal.count()} mesas...")
        mesas_sin_sucursal.update(sucursal=sucursal)
    
    # 5. Crear orden de prueba
    print("\n5. CREANDO ORDEN DE PRUEBA...")
    
    mesa_disponible = Mesa.objects.filter(estado='disponible').first()
    if not mesa_disponible:
        mesa_disponible = Mesa.objects.first()
        mesa_disponible.estado = 'disponible'
        mesa_disponible.save()
    
    # Crear la orden
    orden = Orden.objects.create(
        mesa=mesa_disponible,
        mesero=mesero,
        estado='pendiente',
        observaciones='Orden de prueba del sistema'
    )
    
    print(f"   ✅ Orden creada: #{orden.id} para Mesa {mesa_disponible.numero}")
    
    # Agregar items a la orden
    total = Decimal('0.00')
    for i, producto in enumerate(productos[:3]):  # Agregar los primeros 3 productos
        cantidad = i + 1  # 1, 2, 3
        precio_unitario = producto.precio
        subtotal = precio_unitario * cantidad
        
        OrdenItem.objects.create(
            orden=orden,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            subtotal=subtotal
        )
        
        total += subtotal
        print(f"   - {cantidad}x {producto.nombre}: ${subtotal}")
    
    # Actualizar total de la orden
    orden.total = total
    orden.save()
    
    # Actualizar estado de la mesa
    mesa_disponible.estado = 'ocupada'
    mesa_disponible.save()
    
    print(f"   💰 Total de la orden: ${total}")
    print(f"   🍽️  Mesa {mesa_disponible.numero} ahora está: {mesa_disponible.estado}")
    
    # 6. Verificar el estado del sistema
    print("\n6. ESTADO ACTUAL DEL SISTEMA...")
    
    ordenes_activas = Orden.objects.filter(estado__in=['pendiente', 'en_preparacion', 'listo'])
    mesas_ocupadas = Mesa.objects.filter(estado='ocupada')
    
    print(f"   📋 Órdenes activas: {ordenes_activas.count()}")
    print(f"   🔒 Mesas ocupadas: {mesas_ocupadas.count()}")
    print(f"   🆓 Mesas disponibles: {Mesa.objects.filter(estado='disponible').count()}")
    
    # Mostrar detalles de órdenes activas
    for orden in ordenes_activas:
        items_count = orden.items.count()
        print(f"   - Orden #{orden.id}: Mesa {orden.mesa.numero}, {items_count} items, ${orden.total}")
    
    print("\n✅ SISTEMA LISTO PARA USAR")
    print("\nPuedes probar:")
    print("1. Ir a /mesero/menu/ para ver el menú")
    print("2. Agregar productos al carrito")
    print("3. Seleccionar una mesa")
    print("4. Confirmar la orden")
    print("5. Ver órdenes en /mesero/orders/")

if __name__ == '__main__':
    main()
