#!/usr/bin/env python
"""
Script para crear órdenes de prueba en el dashboard de cocina
"""
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import Orden, OrdenItem, Mesa
from restaurant.models import ProductoVenta
from django.contrib.auth.models import User
from django.utils import timezone

def crear_orden_prueba():
    """Crear una orden de prueba para el dashboard de cocina"""
    
    # Buscar o crear una mesa
    try:
        mesa = Mesa.objects.first()  # Usar la primera mesa disponible
    except Mesa.DoesNotExist:
        mesa = Mesa.objects.create(
            numero="TEST-1",
            capacidad=4,
            sucursal_id=1  # Asumiendo que existe una sucursal con ID 1
        )
    
    # Buscar un mesero (cualquier usuario)
    try:
        mesero = User.objects.first()
    except:
        mesero = None
    
    # Crear la orden
    orden = Orden.objects.create(
        mesa=mesa,
        mesero=mesero,
        cliente_nombre="Cliente Prueba",
        cliente_telefono="123456789",
        tipo_servicio="mesa",
        estado="confirmada",
        subtotal=25.50,
        total=28.60,
        observaciones="Sin cebolla, extra salsa"
    )
    
    # Buscar algunos productos para agregar a la orden
    productos = ProductoVenta.objects.all()[:3]
    
    for i, producto in enumerate(productos):
        OrdenItem.objects.create(
            orden=orden,
            producto=producto,
            cantidad=i + 1,
            precio_unitario=producto.precio if hasattr(producto, 'precio') else 10.00,
            subtotal=(i + 1) * (producto.precio if hasattr(producto, 'precio') else 10.00)
        )
    
    print(f"✅ Orden de prueba creada: {orden.numero_orden}")
    print(f"   Mesa: {orden.mesa.numero}")
    print(f"   Items: {orden.items.count()}")
    print(f"   Estado: {orden.estado}")
    
    return orden

if __name__ == "__main__":
    try:
        orden = crear_orden_prueba()
        print("\n🎉 ¡Orden de prueba creada exitosamente!")
        print(f"Puedes verla en: http://127.0.0.1:8000/cocina/")
    except Exception as e:
        print(f"❌ Error al crear orden de prueba: {e}")
