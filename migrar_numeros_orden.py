#!/usr/bin/env python
"""
Script para migrar todas las órdenes a un formato estándar: ORD-YYYYMMDD-NNNN
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from mesero.models import Orden

def migrar_numeros_orden():
    """Migrar todas las órdenes a formato estándar ORD-YYYYMMDD-NNNN"""
    print("=== MIGRACIÓN DE NÚMEROS DE ORDEN ===")
    
    # Obtener todas las órdenes ordenadas por fecha
    ordenes = Orden.objects.all().order_by('fecha_creacion')
    
    print(f"Total órdenes a migrar: {ordenes.count()}")
    
    # Diccionario para llevar cuenta de números por fecha
    contadores_por_fecha = {}
    ordenes_migradas = 0
    
    for orden in ordenes:
        fecha_str = orden.fecha_creacion.strftime('%Y%m%d')
        
        # Inicializar contador para esta fecha si no existe
        if fecha_str not in contadores_por_fecha:
            contadores_por_fecha[fecha_str] = 0
        
        # Incrementar contador
        contadores_por_fecha[fecha_str] += 1
        
        # Generar nuevo número
        nuevo_numero = f"ORD-{fecha_str}-{contadores_por_fecha[fecha_str]:04d}"
        
        # Solo actualizar si es diferente
        if orden.numero_orden != nuevo_numero:
            numero_anterior = orden.numero_orden
            orden.numero_orden = nuevo_numero
            orden.save()
            ordenes_migradas += 1
            print(f"Migrada: {numero_anterior} → {nuevo_numero}")
    
    print(f"\n=== MIGRACIÓN COMPLETADA ===")
    print(f"Órdenes migradas: {ordenes_migradas}")
    print(f"Órdenes sin cambios: {ordenes.count() - ordenes_migradas}")
    
    # Mostrar estadísticas finales
    print("\n=== ESTADÍSTICAS FINALES ===")
    for fecha, count in contadores_por_fecha.items():
        fecha_format = datetime.strptime(fecha, '%Y%m%d').strftime('%d/%m/%Y')
        print(f"{fecha_format}: {count} órdenes")
    
    # Verificar que no hay duplicados
    print("\n=== VERIFICACIÓN DE DUPLICADOS ===")
    from django.db.models import Count
    duplicados = Orden.objects.values('numero_orden').annotate(count=Count('numero_orden')).filter(count__gt=1)
    
    if duplicados:
        print("⚠️  ADVERTENCIA: Se encontraron números duplicados:")
        for dup in duplicados:
            print(f"  - {dup['numero_orden']}: {dup['count']} veces")
    else:
        print("✅ No se encontraron duplicados")

if __name__ == '__main__':
    migrar_numeros_orden()
