#!/usr/bin/env python
"""
Script para investigar el problema con el inventario de alga nori
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

from restaurant.models import ProductoVenta, Receta, RecetaInsumo, Insumo, Inventario
from accounts.models import Sucursal

def main():
    print("🔍 INVESTIGANDO PROBLEMA CON ALGA NORI")
    print("=" * 60)
    
    # 1. Buscar el producto 'algas con algas'
    productos = ProductoVenta.objects.filter(nombre__icontains='algas')
    print(f"🍱 Productos encontrados con 'algas':")
    for producto in productos:
        print(f"   ID: {producto.id} - {producto.nombre} - Disponible: {producto.disponible}")
    
    # 2. Buscar la receta correspondiente
    if productos.exists():
        producto = productos.first()
        print(f"\n📋 Buscando receta para: {producto.nombre}")
        try:
            receta = producto.receta
            print(f"   ✅ Receta encontrada: ID {receta.id}")
            
            # 3. Ver los insumos de la receta
            insumos_receta = RecetaInsumo.objects.filter(receta=receta)
            print(f"   📦 Insumos en la receta:")
            for item in insumos_receta:
                print(f"      • {item.insumo.nombre}: {item.cantidad} {item.insumo.unidad_medida.abreviacion}")
                
        except Exception as e:
            print(f"   ❌ No se encontró receta para este producto: {e}")
    
    # 4. Verificar inventario de alga nori
    print(f"\n🏪 INVENTARIO DE ALGA NORI:")
    alga_nori = Insumo.objects.filter(nombre__icontains='alga nori').first()
    if alga_nori:
        print(f"   📦 Insumo: {alga_nori.nombre} (ID: {alga_nori.id})")
        print(f"   📊 Stock general: {alga_nori.stock_actual} {alga_nori.unidad_medida.abreviacion}")
        
        # Ver inventario por sucursal
        inventarios = Inventario.objects.filter(insumo=alga_nori)
        print(f"   🏢 Inventario por sucursal:")
        for inv in inventarios:
            print(f"      • {inv.sucursal.nombre}: {inv.cantidad_actual} {alga_nori.unidad_medida.abreviacion}")
    else:
        print("   ❌ No se encontró insumo alga nori")
    
    # 5. Verificar sucursal centro
    sucursal_centro = Sucursal.objects.filter(nombre__icontains='centro').first()
    if sucursal_centro:
        print(f"\n🏢 Sucursal Centro: {sucursal_centro.nombre} (ID: {sucursal_centro.id})")
        
        # 6. Probar verificación de stock específicamente
        if productos.exists() and alga_nori:
            producto = productos.first()
            print(f"\n🧪 PROBANDO VERIFICACIÓN DE STOCK:")
            print(f"   Producto: {producto.nombre}")
            print(f"   Sucursal: {sucursal_centro.nombre}")
            
            try:
                # Verificar stock manualmente
                print(f"   🔍 Verificando stock manualmente...")
                
                # Obtener detalles de la verificación
                if hasattr(producto, 'receta'):
                    receta = producto.receta
                    insumos_receta = RecetaInsumo.objects.filter(receta=receta)
                    print(f"   📋 Detalle de verificación:")
                    
                    puede_producir = True
                    for item in insumos_receta:
                        inventario = Inventario.objects.filter(
                            insumo=item.insumo,
                            sucursal=sucursal_centro
                        ).first()
                        
                        cantidad_necesaria = item.cantidad * 1  # cantidad del producto
                        
                        if inventario:
                            disponible = inventario.cantidad_disponible
                            suficiente = disponible >= cantidad_necesaria
                            print(f"      • {item.insumo.nombre}:")
                            print(f"        Necesario: {cantidad_necesaria} {item.insumo.unidad_medida.abreviacion}")
                            print(f"        Disponible: {disponible} {item.insumo.unidad_medida.abreviacion}")
                            print(f"        ¿Suficiente? {'✅' if suficiente else '❌'}")
                            
                            if not suficiente:
                                puede_producir = False
                        else:
                            print(f"      • {item.insumo.nombre}: ❌ Sin inventario en esta sucursal")
                            puede_producir = False
                    
                    print(f"   🎯 RESULTADO: ¿Puede producir 1 unidad? {'✅ SÍ' if puede_producir else '❌ NO'}")
                else:
                    print("   ❌ El producto no tiene receta asociada")
                            
            except Exception as e:
                print(f"   ❌ Error en verificación: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 ANÁLISIS COMPLETADO")

if __name__ == "__main__":
    main()
