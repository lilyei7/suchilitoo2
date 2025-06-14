#!/usr/bin/env python
"""
Script para crear una sucursal y asignarla al usuario
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Sucursal, Usuario
from datetime import date

def crear_sucursal():
    """Crear sucursal principal y asignarla al usuario"""
    print("🏢 Creando sucursal principal...")
    
    # Crear o obtener sucursal principal
    sucursal, created = Sucursal.objects.get_or_create(
        nombre='Sucursal Principal',
        defaults={
            'direccion': 'Calle Principal #123',
            'telefono': '123-456-7890',
            'email': 'principal@sushirestaurant.com',
            'fecha_apertura': date.today(),
            'activa': True
        }
    )
    
    if created:
        print(f"✅ Sucursal creada: {sucursal.nombre}")
    else:
        print(f"ℹ️ Sucursal ya existe: {sucursal.nombre}")
    
    # Asignar sucursal al usuario principal
    try:
        usuario = Usuario.objects.get(username='jhayco')
        usuario.sucursal = sucursal
        usuario.save()
        print(f"✅ Usuario {usuario.username} asignado a sucursal {sucursal.nombre}")
    except Usuario.DoesNotExist:
        print("❌ Usuario 'jhayco' no encontrado")
    
    return sucursal

if __name__ == '__main__':
    crear_sucursal()
