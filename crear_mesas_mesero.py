#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import Mesa
from accounts.models import Sucursal

def crear_mesas_mesero():
    """Crear mesas para el modelo mesero basadas en las existentes"""
    
    # Obtener sucursales
    sucursales = Sucursal.objects.all()
    if not sucursales.exists():
        print("❌ No hay sucursales en el sistema")
        return
    
    # Crear mesas para la sucursal del mesero_test (Sucursal Centro)
    sucursal_centro = Sucursal.objects.get(nombre="Sucursal Centro")
    print(f"📍 Creando mesas de mesero para: {sucursal_centro.nombre}")
    
    # Mesas para crear
    mesas_config = [
        {'numero': 'M01', 'capacidad': 2, 'ubicacion': 'Ventana'},
        {'numero': 'M02', 'capacidad': 4, 'ubicacion': 'Ventana'},
        {'numero': 'M03', 'capacidad': 4, 'ubicacion': 'Ventana'},
        {'numero': 'M04', 'capacidad': 6, 'ubicacion': 'Centro'},
        {'numero': 'M05', 'capacidad': 4, 'ubicacion': 'Centro'},
        {'numero': 'M06', 'capacidad': 4, 'ubicacion': 'Centro'},
        {'numero': 'M07', 'capacidad': 2, 'ubicacion': 'Barra'},
        {'numero': 'M08', 'capacidad': 2, 'ubicacion': 'Barra'},
        {'numero': 'M09', 'capacidad': 8, 'ubicacion': 'Terraza'},
        {'numero': 'M10', 'capacidad': 6, 'ubicacion': 'Terraza'},
        {'numero': 'VIP1', 'capacidad': 4, 'ubicacion': 'Sala VIP'},
        {'numero': 'VIP2', 'capacidad': 6, 'ubicacion': 'Sala VIP'},
    ]
    
    mesas_creadas = 0
    
    for mesa_data in mesas_config:
        mesa, created = Mesa.objects.get_or_create(
            numero=mesa_data['numero'],
            sucursal=sucursal_centro,
            defaults={
                'capacidad': mesa_data['capacidad'],
                'ubicacion': mesa_data['ubicacion'],
                'estado': 'disponible',
                'activa': True
            }
        )
        
        if created:
            print(f"✅ Mesa {mesa.numero} creada - {mesa.capacidad} personas - {mesa.ubicacion}")
            mesas_creadas += 1
        else:
            print(f"ℹ️ Mesa {mesa.numero} ya existía")
    
    print(f"\n🎉 Resumen: {mesas_creadas} mesas nuevas creadas")
    
    # Mostrar estado actual
    print(f"\n📊 Estado actual de mesas (modelo mesero):")
    for estado, nombre in Mesa.ESTADO_CHOICES:
        count = Mesa.objects.filter(estado=estado, sucursal=sucursal_centro).count()
        print(f"   {nombre}: {count} mesas")
    
    total_mesas = Mesa.objects.filter(sucursal=sucursal_centro).count()
    capacidad_total = sum(Mesa.objects.filter(sucursal=sucursal_centro).values_list('capacidad', flat=True))
    print(f"\n📈 Total: {total_mesas} mesas con capacidad para {capacidad_total} personas")

if __name__ == "__main__":
    print("=== CREACIÓN DE MESAS MESERO ===")
    crear_mesas_mesero()
