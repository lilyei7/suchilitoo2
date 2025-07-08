#!/usr/bin/env python
"""
Script para verificar que los insumos aparecen en el inventario
"""
import os
import sys

# Agregar el directorio del proyecto al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

import django
django.setup()

from restaurant.models import Insumo, Inventario
from accounts.models import Sucursal

def verificar_inventario():
    print("🔍 VERIFICANDO INVENTARIO ACTUAL")
    print("=" * 50)
    
    # Obtener insumos con inventario (usando la misma lógica que la vista)
    insumos_con_inventario = Inventario.objects.values_list('insumo_id', flat=True).distinct()
    insumos = Insumo.objects.filter(id__in=insumos_con_inventario, activo=True)
    
    print(f"📦 Insumos que aparecen en inventario: {insumos.count()}")
    print()
    
    for insumo in insumos:
        print(f"✅ {insumo.codigo} - {insumo.nombre}")
        print(f"   Categoría: {insumo.categoria.nombre if insumo.categoria else 'Sin categoría'}")
        print(f"   Tipo: {insumo.tipo}")
        
        # Mostrar inventarios por sucursal
        inventarios = Inventario.objects.filter(insumo=insumo)
        for inv in inventarios:
            print(f"   📍 {inv.sucursal.nombre}: {inv.cantidad_actual} {insumo.unidad_medida.abreviacion if insumo.unidad_medida else 'unidades'}")
        
        # Mostrar proveedor si existe
        if insumo.proveedor_principal:
            print(f"   🏭 Proveedor: {insumo.proveedor_principal.nombre}")
            if insumo.proveedor_principal.contacto:
                print(f"      Contacto: {insumo.proveedor_principal.contacto}")
            if insumo.proveedor_principal.telefono:
                print(f"      Teléfono: {insumo.proveedor_principal.telefono}")
            if insumo.proveedor_principal.email:
                print(f"      Email: {insumo.proveedor_principal.email}")
        else:
            print(f"   ⚠️ Sin proveedor asignado")
        
        print()

if __name__ == "__main__":
    verificar_inventario()
