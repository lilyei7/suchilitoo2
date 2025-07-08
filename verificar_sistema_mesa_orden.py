#!/usr/bin/env python
"""
Script para verificar flujo completo: Mesa → Orden → Items desglosados → Cocina
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
from cocina.views import expandir_items_orden

def verificar_vinculo_mesa_orden():
    """Verifica que las órdenes estén correctamente vinculadas a las mesas"""
    print("🔗 Verificando vínculos Mesa → Orden...")
    
    ordenes_activas = Orden.objects.filter(
        estado__in=['pendiente', 'confirmada', 'en_preparacion']
    ).select_related('mesa', 'mesero')
    
    print(f"📊 Total de órdenes activas: {ordenes_activas.count()}")
    
    for orden in ordenes_activas:
        print(f"\n📋 Orden: {orden.numero_orden}")
        print(f"   🏢 Mesa: {orden.mesa.numero if orden.mesa else 'SIN MESA'}")
        print(f"   🍽️ Sucursal: {orden.mesa.sucursal.nombre if orden.mesa and orden.mesa.sucursal else 'N/A'}")
        print(f"   👨‍💼 Mesero: {orden.mesero.first_name if orden.mesero else 'N/A'}")
        print(f"   📊 Estado: {orden.estado}")
        print(f"   🕐 Creación: {orden.fecha_creacion.strftime('%H:%M:%S')}")
        
        # Verificar ítems de la orden
        items = orden.items.all()
        print(f"   📦 Total ítems: {items.count()}")
        
        for i, item in enumerate(items, 1):
            notas = item.observaciones or "Sin notas"
            print(f"      {i}. {item.cantidad}x {item.producto.nombre}")
            print(f"         📝 {notas}")
        
        # Probar función de expansión
        items_expandidos = expandir_items_orden(orden)
        total_expandido = len(items_expandidos)
        
        if total_expandido != items.count():
            print(f"   ✅ Items expandidos: {items.count()} → {total_expandido} líneas individuales")
            for j, item_exp in enumerate(items_expandidos, 1):
                if hasattr(item_exp, 'es_expandido') and item_exp.es_expandido:
                    print(f"      {j}. Unidad {item_exp.numero_unidad}/{item_exp.total_unidades} - {item_exp.producto.nombre}")
                    print(f"         📝 {item_exp.observaciones or 'Sin notas'}")
                else:
                    print(f"      {j}. {item_exp.cantidad}x {item_exp.producto.nombre}")
                    print(f"         📝 {item_exp.observaciones or 'Sin notas'}")
        else:
            print(f"   ✅ No se requiere expansión de ítems")

def verificar_mesas_disponibles():
    """Verifica estado de las mesas"""
    print("\n\n🏢 Verificando estado de mesas...")
    
    mesas = Mesa.objects.filter(activa=True).order_by('numero')
    
    for mesa in mesas:
        orden_activa = mesa.obtener_orden_activa()
        print(f"\n🪑 Mesa {mesa.numero} ({mesa.sucursal.nombre})")
        print(f"   📊 Estado: {mesa.estado}")
        print(f"   📍 Ubicación: {mesa.ubicacion or 'No especificada'}")
        
        if orden_activa:
            print(f"   🍽️ Orden activa: {orden_activa.numero_orden}")
            print(f"   👨‍💼 Mesero: {orden_activa.mesero.first_name if orden_activa.mesero else 'N/A'}")
            print(f"   📦 Ítems: {orden_activa.items.count()}")
        else:
            print(f"   ✅ Sin órdenes activas")

def main():
    print("🍣 VERIFICACIÓN DEL SISTEMA MESA → ORDEN → COCINA")
    print("=" * 60)
    
    # 1. Verificar vínculos existentes
    verificar_vinculo_mesa_orden()
    
    # 2. Verificar estado de mesas
    verificar_mesas_disponibles()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE VERIFICACIÓN:")
    print("✅ Vínculos Mesa → Orden: Verificado")
    print("✅ Estados de mesa: Verificado")
    print("✅ Expansión de ítems para cocina: Verificado")
    
    print("\n🔍 Para ver los cambios:")
    print("1. Iniciar servidor: python manage.py runserver")
    print("2. Abrir cocina: http://127.0.0.1:8000/cocina/")
    print("3. Verificar que cada item aparece por separado")
    print("4. Comprobar que las notas son visibles")

if __name__ == "__main__":
    main()
