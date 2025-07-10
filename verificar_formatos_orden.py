#!/usr/bin/env python
"""
Script para verificar el formato de números de orden
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from mesero.models import Orden

def verificar_formatos_orden():
    """Verificar los formatos de números de orden"""
    print("=== VERIFICANDO FORMATOS DE NÚMEROS DE ORDEN ===")
    
    # Obtener todas las órdenes
    ordenes = Orden.objects.all().order_by('-fecha_creacion')[:20]
    
    print(f"Total de órdenes: {Orden.objects.count()}")
    print(f"Mostrando las últimas 20 órdenes:")
    print("-" * 60)
    
    for orden in ordenes:
        print(f"ID: {orden.id:3d} | Número: {orden.numero_orden:15s} | Mesa: {orden.mesa.numero if orden.mesa else 'Sin mesa':3s} | Estado: {orden.estado:10s} | Fecha: {orden.fecha_creacion.strftime('%d/%m/%Y %H:%M')}")
    
    # Contar diferentes formatos
    print("\n=== ANÁLISIS DE FORMATOS ===")
    
    formatos = {}
    for orden in Orden.objects.all():
        if orden.numero_orden:
            if orden.numero_orden.startswith('NOR'):
                formato = 'NOR'
            elif '-' in orden.numero_orden:
                formato = 'FECHA-NUMERO'
            else:
                formato = 'OTRO'
            
            if formato not in formatos:
                formatos[formato] = 0
            formatos[formato] += 1
    
    for formato, count in formatos.items():
        print(f"{formato}: {count} órdenes")
    
    # Verificar si hay órdenes sin numero_orden
    sin_numero = Orden.objects.filter(numero_orden__isnull=True).count()
    vacio = Orden.objects.filter(numero_orden='').count()
    
    print(f"\nÓrdenes sin número_orden: {sin_numero}")
    print(f"Órdenes con número_orden vacío: {vacio}")

if __name__ == '__main__':
    verificar_formatos_orden()
