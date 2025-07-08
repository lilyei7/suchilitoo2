#!/usr/bin/env python3
"""
Script para probar la funcionalidad de notas especiales en los productos.
Crea una orden de prueba con notas especiales para validar que el sistema funciona.
"""

import os
import django
import sys
from datetime import datetime
from django.utils import timezone

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import Orden, OrdenItem, Mesa
from restaurant.models import ProductoVenta
from accounts.models import Usuario, Sucursal

def probar_notas_especiales():
    """Crear una orden de prueba con notas especiales"""
    
    print("🍣 Probando funcionalidad de notas especiales...")
    
    try:
        # Obtener datos necesarios
        sucursal = Sucursal.objects.first()
        if not sucursal:
            print("❌ No hay sucursales en la base de datos")
            return
        
        # Obtener una mesa
        mesa = Mesa.objects.filter(sucursal=sucursal).first()
        if not mesa:
            print("❌ No hay mesas en la base de datos")
            return
        
        # Obtener un mesero
        mesero = Usuario.objects.filter(
            groups__name__in=['Mesero', 'Meseros']
        ).first()
        
        if not mesero:
            print("❌ No hay meseros en la base de datos")
            return
        
        # Obtener algunos productos
        productos = list(ProductoVenta.objects.filter(disponible=True)[:3])
        if not productos:
            print("❌ No hay productos disponibles")
            return
        
        print(f"✅ Usando mesa: {mesa.numero}")
        print(f"✅ Mesero: {mesero.get_full_name()}")
        print(f"✅ Productos disponibles: {len(productos)}")
        
        # Crear una orden con notas especiales
        orden = Orden.objects.create(
            mesa=mesa,
            mesero=mesero,
            estado='confirmada',
            observaciones='Orden de prueba para validar notas especiales',
            total=0
        )
        
        print(f"✅ Orden creada: #{orden.numero_orden}")
        
        # Notas especiales de ejemplo
        notas_especiales = [
            "Sin tomate, extra picante",
            "Cocción media, sin cebolla",
            "Sin salsa, extra queso"
        ]
        
        total_orden = 0
        
        # Agregar productos con notas especiales
        for i, producto in enumerate(productos):
            notas = notas_especiales[i] if i < len(notas_especiales) else ""
            
            orden_item = OrdenItem.objects.create(
                orden=orden,
                producto=producto,
                cantidad=1,
                precio_unitario=producto.precio,
                observaciones=notas  # ¡AQUÍ están las notas especiales!
            )
            
            total_orden += producto.precio
            
            print(f"   📝 {producto.nombre}: \"{notas}\"")
        
        # Actualizar total de la orden
        orden.total = total_orden
        orden.save()
        
        print(f"✅ Total de la orden: ${total_orden}")
        print(f"📊 Items con notas especiales: {orden.items.filter(observaciones__isnull=False).exclude(observaciones='').count()}")
        
        # Mostrar detalles de los items
        print("\n🔍 Detalles de la orden:")
        for item in orden.items.all():
            notas_display = f" - NOTAS: {item.observaciones}" if item.observaciones else " - Sin notas especiales"
            print(f"   • {item.cantidad}x {item.producto.nombre}{notas_display}")
        
        print(f"\n🎉 ¡Orden de prueba creada exitosamente!")
        print(f"📌 Ve al dashboard de cocina para ver las notas especiales:")
        print(f"   http://127.0.0.1:8000/cocina/")
        print(f"   La orden #{orden.numero_orden} debe mostrar las notas especiales de cada producto")
        
        return orden
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    orden = probar_notas_especiales()
    if orden:
        print(f"\n✨ ¡Funcionalidad probada exitosamente!")
        print(f"   Orden ID: {orden.id}")
        print(f"   Número: {orden.numero_orden}")
        print(f"   Items con notas: {orden.items.filter(observaciones__isnull=False).exclude(observaciones='').count()}")
