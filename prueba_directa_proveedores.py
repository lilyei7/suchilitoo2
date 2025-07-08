#!/usr/bin/env python
"""
Script simple para probar directamente las APIs y verificar que los proveedores funcionan.
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Insumo
from dashboard.models import ProveedorInsumo

def main():
    print("🧪 PRUEBA DIRECTA DE PROVEEDORES")
    print("=" * 50)
    
    # Verificar varios insumos
    insumos = Insumo.objects.all()[:5]
    
    for insumo in insumos:
        print(f"\n📦 {insumo.nombre} (ID: {insumo.id})")
        
        # Proveedor principal
        if insumo.proveedor_principal:
            print(f"   🏷️ Principal: {insumo.proveedor_principal.nombre}")
        else:
            print(f"   🏷️ Principal: Ninguno")
        
        # Proveedores asignados
        relaciones = ProveedorInsumo.objects.filter(insumo=insumo, activo=True)
        print(f"   📋 Asignados: {relaciones.count()}")
        
        for relacion in relaciones:
            print(f"      - {relacion.proveedor.nombre_comercial}: ${relacion.precio_final()}")
        
        # Total de proveedores
        total_proveedores = (1 if insumo.proveedor_principal else 0) + relaciones.count()
        print(f"   📊 Total proveedores: {total_proveedores}")
    
    print(f"\n✅ Prueba completada")
    print(f"\n🌐 Para probar en navegador:")
    print(f"   1. Ve a http://127.0.0.1:8000/dashboard/login/")
    print(f"   2. Logueate con cualquier usuario admin")
    print(f"   3. Ve a http://127.0.0.1:8000/dashboard/inventario/")
    print(f"   4. Busca insumos con múltiples proveedores y haz clic en 'Ver detalles'")

if __name__ == "__main__":
    main()
