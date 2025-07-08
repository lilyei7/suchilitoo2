#!/usr/bin/env python
"""
Script para crear órdenes de prueba en el sistema de mesero
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import Mesa, Orden, OrdenItem
from restaurant.models import ProductoVenta
from accounts.models import Usuario
from decimal import Decimal

def crear_ordenes_prueba():
    print("🍣 Creando órdenes de prueba...")
    
    # Obtener datos necesarios
    mesas = Mesa.objects.all()[:4]  # Primeras 4 mesas
    productos = ProductoVenta.objects.all()[:8]  # Primeros 8 productos
    mesero = Usuario.objects.filter(rol__nombre='mesero').first()
    
    if not mesero:
        print("❌ No se encontró un usuario mesero. Ejecuta primero crear_datos_mesero.py")
        return
    
    if not mesas.exists():
        print("❌ No se encontraron mesas. Ejecuta primero crear_datos_mesero.py")
        return
    
    if not productos.exists():
        print("❌ No se encontraron productos. Ejecuta primero crear_datos_mesero.py")
        return
    
    # Crear órdenes en diferentes estados
    estados_ordenes = [
        ('pendiente', 'Orden recién creada'),
        ('preparando', 'Orden en cocina'),
        ('listo', 'Orden lista para entregar'),
    ]
    
    for i, (estado, descripcion) in enumerate(estados_ordenes):
        if i < len(mesas):
            mesa = mesas[i]
            
            # Verificar que la mesa no tenga orden activa
            if not mesa.esta_ocupada:
                orden = Orden.objects.create(
                    mesa=mesa,
                    mesero=mesero,
                    estado=estado,
                    notas=f"Orden de prueba - {descripcion}"
                )
                
                # Agregar algunos items a la orden
                total = Decimal('0.00')
                for j, producto in enumerate(productos[:3]):  # 3 productos por orden
                    cantidad = j + 1  # 1, 2, 3
                    item = OrdenItem.objects.create(
                        orden=orden,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=producto.precio,
                        notas=f"Sin {['cebolla', 'picante', 'salsa'][j]}" if j < 3 else ""
                    )
                    total += item.subtotal
                
                # Actualizar total de la orden
                orden.total = total
                orden.save()
                
                print(f"✓ Orden #{orden.id} creada para Mesa {mesa.numero} - Estado: {estado} - Total: ${total}")
            else:
                print(f"⚠️ Mesa {mesa.numero} ya tiene una orden activa")
    
    print("\n🎉 ¡Órdenes de prueba creadas!")
    print("\n📋 Resumen de órdenes:")
    for orden in Orden.objects.all():
        print(f"   • Orden #{orden.id} - Mesa {orden.mesa.numero} - {orden.get_estado_display()} - ${orden.total}")
    
    print("\n🌐 Ahora puedes probar:")
    print("   • Estado de Cocina: http://127.0.0.1:8000/mesero/cocina/")
    print("   • Gestión de Mesas: http://127.0.0.1:8000/mesero/mesas/")
    print("   • Dashboard: http://127.0.0.1:8000/mesero/")

if __name__ == '__main__':
    crear_ordenes_prueba()
