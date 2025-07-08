#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import Orden
from django.utils import timezone

def corregir_ordenes_completadas():
    """Corregir órdenes con estado 'lista' que no tienen fecha_lista"""
    print("=== CORRECCIÓN DE ÓRDENES COMPLETADAS ===")
    
    # Encontrar órdenes con estado lista sin fecha_lista
    ordenes_sin_fecha = Orden.objects.filter(
        estado='lista',
        fecha_lista__isnull=True
    )
    
    print(f"Órdenes encontradas sin fecha_lista: {ordenes_sin_fecha.count()}")
    
    for orden in ordenes_sin_fecha:
        print(f"Corrigiendo orden {orden.numero_orden}...")
        
        # Usar fecha de preparación si existe, si no usar fecha de creación + tiempo estimado
        if orden.fecha_preparacion:
            # Estimar que estuvo lista 15 minutos después de comenzar preparación
            orden.fecha_lista = orden.fecha_preparacion + timezone.timedelta(minutes=15)
        else:
            # Estimar que estuvo lista 20 minutos después de creada
            orden.fecha_lista = orden.fecha_creacion + timezone.timedelta(minutes=20)
        
        orden.save()
        print(f"  ✅ Orden {orden.numero_orden} actualizada con fecha_lista: {orden.fecha_lista}")
    
    print("\n=== ACTUALIZAR ÓRDENES ENTREGADAS SIN FECHA_ENTREGA ===")
    
    # Encontrar órdenes entregadas sin fecha_entrega
    ordenes_entregadas_sin_fecha = Orden.objects.filter(
        estado='entregada',
        fecha_entrega__isnull=True
    )
    
    print(f"Órdenes entregadas sin fecha_entrega: {ordenes_entregadas_sin_fecha.count()}")
    
    for orden in ordenes_entregadas_sin_fecha:
        print(f"Corrigiendo orden entregada {orden.numero_orden}...")
        
        # Usar fecha_lista + 5 minutos si existe, si no usar fecha de creación + 25 minutos
        if orden.fecha_lista:
            orden.fecha_entrega = orden.fecha_lista + timezone.timedelta(minutes=5)
        else:
            orden.fecha_entrega = orden.fecha_creacion + timezone.timedelta(minutes=25)
            # También establecer fecha_lista si no existe
            if not orden.fecha_lista:
                orden.fecha_lista = orden.fecha_creacion + timezone.timedelta(minutes=20)
        
        orden.save()
        print(f"  ✅ Orden {orden.numero_orden} actualizada con fecha_entrega: {orden.fecha_entrega}")
    
    print("\n=== RESUMEN FINAL ===")
    
    # Verificar estado actual
    ordenes_hoy = Orden.objects.filter(fecha_creacion__date=timezone.now().date())
    ordenes_completadas_hoy = ordenes_hoy.filter(estado__in=['lista', 'entregada', 'completada', 'cerrada'])
    
    print(f"Total órdenes del día: {ordenes_hoy.count()}")
    print(f"Órdenes completadas del día: {ordenes_completadas_hoy.count()}")
    
    for orden in ordenes_completadas_hoy:
        fecha_final = orden.fecha_lista or orden.fecha_entrega or orden.fecha_cierre
        print(f"  - {orden.numero_orden}: {orden.estado} - Finalizada: {fecha_final}")

if __name__ == "__main__":
    corregir_ordenes_completadas()
