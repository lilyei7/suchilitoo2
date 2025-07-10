#!/usr/bin/env python3
"""
Script para reproducir el error exacto que está viendo el mesero
"""

import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta, Receta, RecetaInsumo, Insumo
from mesero.models import Orden, OrdenItem
from accounts.models import Sucursal
from inventario_automatico import InventarioAutomatico

def test_producto_xxx2():
    print("🔍 Probando verificación de stock para producto xxx2")
    
    # Buscar el producto xxx2
    try:
        producto = ProductoVenta.objects.get(nombre="xxx2")
        print(f"✅ Producto encontrado: {producto.nombre} (ID: {producto.id})")
    except ProductoVenta.DoesNotExist:
        print("❌ Producto xxx2 no encontrado")
        return
    
    # Verificar las relaciones de receta
    print("\n📋 Verificando relaciones de receta:")
    
    # 1. Verificar relación directa OneToOne
    try:
        receta_directa = producto.receta
        print(f"✅ Receta directa (OneToOne): {receta_directa.nombre} (ID: {receta_directa.id})")
    except Exception as e:
        print(f"❌ Error en receta directa: {e}")
        receta_directa = None
    
    # 2. Verificar relación many-to-many ProductoReceta
    try:
        from restaurant.models_producto_receta import ProductoReceta
        relaciones = ProductoReceta.objects.filter(producto=producto)
        print(f"📊 Relaciones ProductoReceta encontradas: {relaciones.count()}")
        for rel in relaciones:
            print(f"  - Receta: {rel.receta.nombre} (ID: {rel.receta.id})")
    except Exception as e:
        print(f"❌ Error verificando ProductoReceta: {e}")
    
    # 3. Probar con InventarioAutomatico
    print("\n🔧 Probando con InventarioAutomatico:")
    
    try:
        sucursal = Sucursal.objects.first()
        if not sucursal:
            print("❌ No se encontró sucursal")
            return
        
        inventario = InventarioAutomatico(sucursal)
        stock_ok, faltantes = inventario.verificar_stock_disponible(producto, 1)
        
        print(f"Stock OK: {stock_ok}")
        print(f"Faltantes: {faltantes}")
        
        if not stock_ok and faltantes:
            for faltante in faltantes:
                print(f"  Faltante: {faltante}")
                
    except Exception as e:
        print(f"❌ Error en InventarioAutomatico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_producto_xxx2()
