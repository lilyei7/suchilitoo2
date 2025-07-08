#!/usr/bin/env python
"""
Script para probar la verificación de stock del mesero
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

try:
    django.setup()
except Exception as e:
    print(f"Error al configurar Django: {e}")
    sys.exit(1)

from restaurant.models import ProductoVenta
from accounts.models import Sucursal
from inventario_automatico import InventarioAutomatico

def main():
    print("🧪 PROBANDO VERIFICACIÓN DE STOCK DEL MESERO")
    print("=" * 60)
    
    # Buscar la sucursal centro
    sucursal_centro = Sucursal.objects.filter(nombre__icontains='centro').first()
    print(f"🏢 Sucursal: {sucursal_centro.nombre}")
    
    # Buscar el producto de algas
    producto = ProductoVenta.objects.filter(nombre__icontains='algas').first()
    print(f"🍱 Producto: {producto.nombre}")
    
    # Inicializar el inventario automático
    inventario_automatico = InventarioAutomatico(sucursal_centro)
    
    # Probar verificación con diferentes cantidades
    cantidades = [1, 2]
    
    for cantidad in cantidades:
        print(f"\n🔍 Verificando stock para {cantidad} unidad(es)")
        print("-" * 40)
        
        try:
            stock_ok, faltantes = inventario_automatico.verificar_stock_disponible(producto, cantidad)
            
            print(f"✅ Resultado: {stock_ok}")
            
            if not stock_ok:
                print("❌ Faltantes:")
                for faltante in faltantes:
                    print(f"   • {faltante['insumo']}: necesita {faltante['necesario']} {faltante['unidad']}, disponible {faltante['disponible']} {faltante['unidad']}")
            else:
                print("✅ Stock suficiente para todos los insumos")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
