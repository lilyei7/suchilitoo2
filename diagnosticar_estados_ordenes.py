#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import Orden
from django.utils import timezone

def verificar_estados_ordenes():
    """Verificar los estados actuales de las órdenes en la base de datos"""
    print("=== DIAGNÓSTICO DE ESTADOS DE ÓRDENES ===")
    
    # Contar órdenes por estado
    estados_count = {}
    for estado, _ in Orden.ESTADO_CHOICES:
        count = Orden.objects.filter(estado=estado).count()
        estados_count[estado] = count
        print(f"Estado '{estado}': {count} órdenes")
    
    print("\n=== ÓRDENES RECIENTES (ÚLTIMAS 20) ===")
    ordenes_recientes = Orden.objects.all().order_by('-fecha_creacion')[:20]
    
    for orden in ordenes_recientes:
        print(f"Orden {orden.numero_orden}:")
        print(f"  - Estado: {orden.estado}")
        print(f"  - Mesa: {orden.mesa.numero if orden.mesa else 'N/A'}")
        print(f"  - Fecha creación: {orden.fecha_creacion}")
        print(f"  - Fecha lista: {orden.fecha_lista}")
        print(f"  - Fecha entrega: {orden.fecha_entrega}")
        print(f"  - Fecha cierre: {orden.fecha_cierre}")
        print("  ---")
    
    print("\n=== ÓRDENES DEL DÍA ACTUAL ===")
    hoy = timezone.now().date()
    ordenes_hoy = Orden.objects.filter(fecha_creacion__date=hoy).order_by('-fecha_creacion')
    
    print(f"Total órdenes creadas hoy: {ordenes_hoy.count()}")
    
    for orden in ordenes_hoy:
        print(f"Orden {orden.numero_orden}: Estado={orden.estado}, Creada={orden.fecha_creacion.strftime('%H:%M')}")
    
    print("\n=== ÓRDENES QUE DEBERÍAN ESTAR EN TAB COMPLETADOS ===")
    # Estados que deberían aparecer en completados
    ordenes_completadas = Orden.objects.filter(
        estado__in=['lista', 'entregada', 'completada', 'cerrada'],
        fecha_creacion__date=hoy
    ).order_by('-fecha_creacion')
    
    print(f"Órdenes completadas del día: {ordenes_completadas.count()}")
    for orden in ordenes_completadas:
        fecha_final = orden.fecha_lista or orden.fecha_entrega or orden.fecha_cierre
        print(f"  - {orden.numero_orden}: {orden.estado} (Mesa {orden.mesa.numero if orden.mesa else 'N/A'}) - Finalizada: {fecha_final}")

if __name__ == "__main__":
    verificar_estados_ordenes()
