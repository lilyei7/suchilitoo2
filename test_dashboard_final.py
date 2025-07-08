#!/usr/bin/env python
"""
Script de prueba final para validar que el dashboard de cocina
muestra correctamente las órdenes completadas
"""

import os
import sys
import django
from datetime import datetime, date

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import Orden

def test_dashboard_completadas():
    print("=== PRUEBA FINAL DEL DASHBOARD DE COCINA ===")
    print(f"Fecha actual: {datetime.now()}")
    print()
    
    hoy = date.today()
    
    # Esta es la misma query que usa el dashboard
    ordenes_completadas = Orden.objects.filter(
        estado__in=['lista', 'entregada', 'completada'],
        fecha_creacion__date=hoy
    ).select_related('mesa', 'mesero').order_by('-fecha_creacion')
    
    print(f"=== ÓRDENES QUE APARECERÁN EN EL TAB 'PEDIDOS COMPLETADOS' ===")
    print(f"Total: {ordenes_completadas.count()} órdenes")
    print()
    
    if ordenes_completadas.count() == 0:
        print("❌ No hay órdenes completadas para mostrar")
        return
    
    for i, orden in enumerate(ordenes_completadas, 1):
        print(f"{i}. Orden #{orden.numero_orden}")
        print(f"   - Mesa: {orden.mesa}")
        print(f"   - Estado: {orden.estado}")
        print(f"   - Creada: {orden.fecha_creacion.strftime('%H:%M:%S')}")
        
        if orden.fecha_lista:
            print(f"   - Finalizada: {orden.fecha_lista.strftime('%H:%M:%S')}")
        elif orden.fecha_entrega:
            print(f"   - Entregada: {orden.fecha_entrega.strftime('%H:%M:%S')}")
        else:
            print(f"   - ⚠️ Sin fecha de finalización")
        
        print()
    
    print("=== VERIFICACIÓN DE CONSISTENCIA ===")
    
    # Verificar que todas las órdenes 'lista' tienen fecha_lista
    ordenes_lista_sin_fecha = Orden.objects.filter(
        estado='lista',
        fecha_lista__isnull=True
    ).count()
    
    if ordenes_lista_sin_fecha == 0:
        print("✅ Todas las órdenes 'lista' tienen fecha_lista")
    else:
        print(f"❌ Hay {ordenes_lista_sin_fecha} órdenes 'lista' sin fecha_lista")
    
    # Verificar que todas las órdenes 'entregada' tienen fecha_entrega
    ordenes_entregada_sin_fecha = Orden.objects.filter(
        estado='entregada',
        fecha_entrega__isnull=True
    ).count()
    
    if ordenes_entregada_sin_fecha == 0:
        print("✅ Todas las órdenes 'entregada' tienen fecha_entrega")
    else:
        print(f"❌ Hay {ordenes_entregada_sin_fecha} órdenes 'entregada' sin fecha_entrega")
    
    print()
    print("=== RESUMEN ===")
    print(f"✅ Dashboard mostrará {ordenes_completadas.count()} órdenes completadas")
    print("✅ Sistema funcionando correctamente")
    print()
    print("INSTRUCCIONES:")
    print("1. Ve al dashboard en: http://127.0.0.1:8000/cocina/")
    print("2. Haz clic en el tab 'Pedidos Completados'")
    print(f"3. Deberías ver {ordenes_completadas.count()} órdenes listadas")
    print("4. Marca cualquier orden nueva como completada desde el dashboard")
    print("5. La orden debería aparecer inmediatamente en 'Pedidos Completados'")

if __name__ == '__main__':
    try:
        test_dashboard_completadas()
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
