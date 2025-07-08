#!/usr/bin/env python3
"""
Test simple para verificar mesas disponibles
"""
import os
import django
import sys

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Sucursal
from dashboard.models_ventas import Mesa

def test_mesas_simple():
    print("🔍 TEST SIMPLE DE MESAS")
    print("=" * 40)
    
    # Verificar mesas existentes
    sucursales = Sucursal.objects.all()
    for sucursal in sucursales:
        mesas = Mesa.objects.filter(sucursal=sucursal, activo=True).order_by('numero')
        print(f"\n📍 Sucursal: {sucursal.nombre} (ID: {sucursal.id})")
        print(f"   Total mesas activas: {mesas.count()}")
        
        if mesas.exists():
            print("   Mesas:")
            for mesa in mesas:
                print(f"     • Mesa {mesa.numero} (ID: {mesa.id}) - {mesa.capacidad} personas - {mesa.estado}")
        else:
            print("   ❌ No hay mesas activas")
    
    print("\n✅ Test completado")

if __name__ == '__main__':
    test_mesas_simple()
