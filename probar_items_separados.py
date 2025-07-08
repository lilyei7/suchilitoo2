#!/usr/bin/env python
"""
Script para probar que cada ítem aparezca como línea separada en cocina,
especialmente cuando hay notas diferentes en el mismo producto.
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

try:
    django.setup()
except Exception as e:
    print(f"Error al configurar Django: {e}")
    sys.exit(1)

from django.utils import timezone
from mesero.models import Mesa, Orden, OrdenItem
from restaurant.models import ProductoVenta
from accounts.models import Usuario, Rol

def crear_orden_con_items_separados():
    """Crea una orden con múltiples ítems del mismo producto pero con notas diferentes"""
    try:
        # Buscar o crear mesa
        mesa = Mesa.objects.filter(activa=True).first()
        if not mesa:
            print("No hay mesas disponibles")
            return
        
        # Buscar mesero
        rol_mesero = Rol.objects.filter(nombre='mesero').first()
        mesero = Usuario.objects.filter(rol=rol_mesero).first() if rol_mesero else Usuario.objects.filter(is_staff=True).first()
        if not mesero:
            print("No hay meseros disponibles")
            return
        
        # Buscar producto popular (ejemplo: California Roll)
        producto = ProductoVenta.objects.filter(disponible=True).first()
        if not producto:
            print("No hay productos disponibles")
            return
        
        print(f"Creando orden con {producto.nombre} en Mesa {mesa.numero}")
        
        # Crear la orden
        orden = Orden.objects.create(
            mesa=mesa,
            mesero=mesero,
            tipo_servicio='mesa',
            estado='en_preparacion',
            fecha_creacion=timezone.now(),
            fecha_preparacion=timezone.now()
        )
        
        # Crear múltiples ítems del mismo producto con notas diferentes
        items_data = [
            {"cantidad": 1, "notas": "Sin aguacate"},
            {"cantidad": 1, "notas": "Extra picante"},
            {"cantidad": 1, "notas": "Sin pepino, con extra salmón"},
            {"cantidad": 2, "notas": ""},  # Sin notas
            {"cantidad": 1, "notas": "Sin arroz, base de quinoa"},
        ]
        
        for item_data in items_data:
            OrdenItem.objects.create(
                orden=orden,
                producto=producto,
                cantidad=item_data["cantidad"],
                precio_unitario=producto.precio,
                observaciones=item_data["notas"] if item_data["notas"] else None
            )
        
        orden.calcular_totales()
        
        print(f"✅ Orden creada: {orden.numero_orden}")
        print(f"   Mesa: {mesa.numero}")
        print(f"   Estado: {orden.estado}")
        print(f"   Total de ítems: {orden.items.count()}")
        
        print("\n📋 Desglose de ítems:")
        for i, item in enumerate(orden.items.all(), 1):
            notas = item.observaciones or "Sin notas especiales"
            print(f"   {i}. {item.cantidad}x {item.producto.nombre}")
            print(f"      📝 {notas}")
        
        return orden
        
    except Exception as e:
        print(f"❌ Error al crear orden: {e}")
        import traceback
        traceback.print_exc()
        return None

def crear_orden_productos_mixtos():
    """Crea una orden con productos diferentes, algunos con notas"""
    try:
        # Buscar mesa diferente
        mesa = Mesa.objects.filter(activa=True).exclude(
            ordenes_mesero__estado__in=['pendiente', 'en_preparacion', 'lista']
        ).first()
        
        if not mesa:
            print("No hay mesas libres para la segunda orden")
            return
        
        # Buscar mesero
        rol_mesero = Rol.objects.filter(nombre='mesero').first()
        mesero = Usuario.objects.filter(rol=rol_mesero).first() if rol_mesero else Usuario.objects.filter(is_staff=True).first()
        if not mesero:
            print("No hay meseros disponibles")
            return
        
        # Buscar varios productos
        productos = ProductoVenta.objects.filter(disponible=True)[:3]
        if len(productos) < 2:
            print("No hay suficientes productos para la prueba mixta")
            return
        
        print(f"\nCreando orden mixta en Mesa {mesa.numero}")
        
        # Crear la orden
        orden = Orden.objects.create(
            mesa=mesa,
            mesero=mesero,
            tipo_servicio='mesa',
            estado='en_preparacion',
            fecha_creacion=timezone.now(),
            fecha_preparacion=timezone.now()
        )
        
        # Agregar diferentes productos
        items_mixtos = [
            {"producto": productos[0], "cantidad": 2, "notas": "Bien cocido"},
            {"producto": productos[1], "cantidad": 1, "notas": "Sin wasabi"},
            {"producto": productos[0], "cantidad": 1, "notas": "Extra salsa"},  # Mismo producto, nota diferente
            {"producto": productos[1], "cantidad": 1, "notas": ""},  # Mismo producto, sin notas
        ]
        
        if len(productos) > 2:
            items_mixtos.append({"producto": productos[2], "cantidad": 3, "notas": "Temperatura ambiente"})
        
        for item_data in items_mixtos:
            OrdenItem.objects.create(
                orden=orden,
                producto=item_data["producto"],
                cantidad=item_data["cantidad"],
                precio_unitario=item_data["producto"].precio,
                observaciones=item_data["notas"] if item_data["notas"] else None
            )
        
        orden.calcular_totales()
        
        print(f"✅ Orden mixta creada: {orden.numero_orden}")
        print(f"   Mesa: {mesa.numero}")
        print(f"   Estado: {orden.estado}")
        print(f"   Total de ítems: {orden.items.count()}")
        
        print("\n📋 Desglose de ítems mixtos:")
        for i, item in enumerate(orden.items.all(), 1):
            notas = item.observaciones or "Sin notas especiales"
            print(f"   {i}. {item.cantidad}x {item.producto.nombre}")
            print(f"      📝 {notas}")
        
        return orden
        
    except Exception as e:
        print(f"❌ Error al crear orden mixta: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("🍣 Probando visualización de ítems separados en cocina")
    print("=" * 60)
    
    # Crear orden con mismo producto, notas diferentes
    orden1 = crear_orden_con_items_separados()
    
    # Crear orden con productos mixtos
    orden2 = crear_orden_productos_mixtos()
    
    if orden1 or orden2:
        print("\n" + "=" * 60)
        print("✅ Órdenes de prueba creadas exitosamente")
        print("\n🔍 Ve al dashboard de cocina para verificar que:")
        print("   1. Cada ítem aparece en una línea separada")
        print("   2. Las notas se muestran debajo de cada ítem")
        print("   3. Los ítems del mismo producto con diferentes notas no se agrupan")
        print("   4. El vínculo mesa-orden es correcto")
        
        if orden1:
            print(f"\n📝 Orden 1: {orden1.numero_orden} (Mesa {orden1.mesa.numero})")
            print(f"    {orden1.items.count()} ítems del mismo producto con notas diferentes")
        
        if orden2:
            print(f"\n📝 Orden 2: {orden2.numero_orden} (Mesa {orden2.mesa.numero})")
            print(f"    {orden2.items.count()} ítems de productos mixtos")
    else:
        print("\n❌ No se pudieron crear las órdenes de prueba")

if __name__ == "__main__":
    main()
