#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import Orden
from django.utils import timezone

def test_dashboard_query():
    """Test the dashboard query to find the issue"""
    print("Testing dashboard query...")
    
    ahora = timezone.now()
    
    try:
        # Query base
        ordenes_base = Orden.objects.all()
        print("✅ Base query works")
        
        # Test active orders query
        ordenes_activas = ordenes_base.filter(
            estado__in=['pendiente', 'confirmada', 'en_preparacion']
        ).select_related('mesa', 'mesero').prefetch_related('items__producto').order_by('fecha_creacion')
        
        print(f"✅ Active orders query works, found {ordenes_activas.count()} orders")
        
        # Test completed orders query - this is likely where the error occurs
        ordenes_completadas = ordenes_base.filter(
            estado__in=['lista', 'entregada', 'completada'],
            fecha_creacion__date=ahora.date()
        ).select_related('mesa', 'mesero').prefetch_related('items__producto').order_by('-fecha_lista')
        
        print(f"✅ Completed orders query works, found {ordenes_completadas.count()} orders")
        
        # Check if there are orders without fecha_lista
        orders_without_fecha_lista = ordenes_base.filter(
            estado__in=['lista', 'entregada', 'completada'],
            fecha_lista__isnull=True
        )
        
        print(f"⚠️  Found {orders_without_fecha_lista.count()} completed orders without fecha_lista")
        
        for orden in orders_without_fecha_lista:
            print(f"   - Order {orden.numero_orden}: estado={orden.estado}, fecha_lista={orden.fecha_lista}")
            
    except Exception as e:
        print(f"❌ Error in query: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dashboard_query()
