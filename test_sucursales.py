#!/usr/bin/env python
"""
Script simple para crear datos de prueba de sucursales
"""
import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Sucursal

def main():
    print("🏢 Creando sucursales de prueba...")
    
    # Datos de ejemplo
    sucursales = [
        {
            'nombre': 'Sushi Central',
            'direccion': 'Av. Principal #123, Centro, CDMX',
            'telefono': '555-0001',
            'email': 'central@sushi.com',
            'fecha_apertura': date.today() - timedelta(days=100),
            'activa': True
        },
        {
            'nombre': 'Sushi Plaza',
            'direccion': 'Plaza Comercial #456, Norte, CDMX',
            'telefono': '555-0002',
            'email': 'plaza@sushi.com',
            'fecha_apertura': date.today() - timedelta(days=50),
            'activa': True
        },
        {
            'nombre': 'Sushi Express',
            'direccion': 'Mall Sur #789, Sur, CDMX',
            'telefono': '555-0003',
            'email': 'express@sushi.com',
            'fecha_apertura': date.today() - timedelta(days=20),
            'activa': False
        }
    ]
    
    for data in sucursales:
        sucursal, created = Sucursal.objects.get_or_create(
            nombre=data['nombre'],
            defaults=data
        )
        status = "✅ Creada" if created else "ℹ️ Ya existe"
        print(f"{status}: {sucursal.nombre}")
    
    total = Sucursal.objects.count()
    activas = Sucursal.objects.filter(activa=True).count()
    print(f"\n📊 Total: {total} sucursales ({activas} activas)")
    print("🌐 Ve a: http://127.0.0.1:8000/dashboard/sucursales/")

if __name__ == '__main__':
    main()
