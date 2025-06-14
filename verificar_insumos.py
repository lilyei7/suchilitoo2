#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Insumo

def verificar_insumos():
    print("=== ÚLTIMOS INSUMOS CREADOS ===")
    insumos = Insumo.objects.order_by('-created_at')[:5]
    
    for insumo in insumos:
        print(f"{insumo.codigo} - {insumo.nombre} - {insumo.created_at}")
    
    print(f"\nTotal de insumos: {Insumo.objects.count()}")

if __name__ == "__main__":
    verificar_insumos()
