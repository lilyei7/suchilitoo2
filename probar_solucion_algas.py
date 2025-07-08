#!/usr/bin/env python
"""
Script para probar que "algas alas algas con algas" ahora puede ordenarse
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

from restaurant.models import ProductoVenta, Receta, Insumo, RecetaInsumo, Inventario
from accounts.models import Sucursal

def verificar_producto_puede_ordenarse():
    """Verificar que el producto ahora puede ordenarse"""
    print("🧪 PRUEBA: ¿Puede ordenarse 'algas alas algas con algas'?")
    print("=" * 60)
    
    # 1. Buscar el producto
    try:
        producto = ProductoVenta.objects.get(nombre="algas alas algas con algas")
        print(f"✅ Producto: {producto.nombre} (ID: {producto.id})")
    except ProductoVenta.DoesNotExist:
        print("❌ Producto no encontrado")
        return False
    
    # 2. Verificar que tiene receta
    try:
        receta = producto.receta
        print(f"✅ Receta: ID {receta.id}")
    except Receta.DoesNotExist:
        print("❌ El producto NO tiene receta")
        return False
    
    # 3. Obtener insumos de la receta
    receta_insumos = RecetaInsumo.objects.filter(receta=receta)
    print(f"✅ Insumos en receta: {receta_insumos.count()}")
    
    if not receta_insumos.exists():
        print("❌ La receta no tiene insumos")
        return False
    
    # 4. Verificar inventario
    sucursal = Sucursal.objects.first()
    if not sucursal:
        print("❌ No hay sucursales")
        return False
    
    print(f"\n📍 Verificando inventario en: {sucursal.nombre}")
    
    puede_preparar = True
    
    for ri in receta_insumos:
        insumo = ri.insumo
        cantidad_necesaria = ri.cantidad
        
        print(f"\n🥗 Insumo: {insumo.nombre}")
        print(f"   Cantidad necesaria: {cantidad_necesaria} {insumo.unidad_medida}")
        
        # Buscar inventario
        try:
            inventario = Inventario.objects.get(
                sucursal=sucursal,
                insumo=insumo
            )
            
            cantidad_disponible = inventario.cantidad_actual
            print(f"   Cantidad disponible: {cantidad_disponible} {insumo.unidad_medida}")
            
            if cantidad_disponible >= cantidad_necesaria:
                print(f"   ✅ Suficiente stock")
            else:
                print(f"   ❌ Stock insuficiente (falta {cantidad_necesaria - cantidad_disponible})")
                puede_preparar = False
                
        except Inventario.DoesNotExist:
            print(f"   ❌ No hay inventario para este insumo")
            puede_preparar = False
    
    # 5. Resultado final
    print(f"\n" + "=" * 60)
    if puede_preparar:
        print("🎉 ¡EL PRODUCTO PUEDE ORDENARSE!")
        print("• Tiene receta válida")
        print("• Todos los insumos tienen stock suficiente")
        
        # Simular deducción
        print(f"\n🧮 SIMULANDO DEDUCCIÓN DE INVENTARIO (1 porción)")
        for ri in receta_insumos:
            cantidad_a_deducir = ri.cantidad
            print(f"   • {ri.insumo.nombre}: -{cantidad_a_deducir} {ri.insumo.unidad_medida}")
        
        return True
    else:
        print("⚠️ EL PRODUCTO TIENE RECETA PERO HAY PROBLEMAS DE STOCK")
        print("• La receta existe")
        print("• Pero algunos insumos no tienen stock suficiente")
        return False

def comparar_con_algas_con_nalgas():
    """Comparar con el producto que sí funcionaba"""
    print("\n\n🔍 COMPARACIÓN CON 'algas con nalgas'")
    print("=" * 60)
    
    productos = [
        "algas con nalgas",
        "algas alas algas con algas"
    ]
    
    for nombre_producto in productos:
        print(f"\n📋 {nombre_producto}:")
        
        try:
            producto = ProductoVenta.objects.get(nombre=nombre_producto)
            receta = producto.receta
            receta_insumos = RecetaInsumo.objects.filter(receta=receta)
            
            print(f"   ✅ Receta: ID {receta.id}")
            print(f"   📝 Insumos: {receta_insumos.count()}")
            
            for ri in receta_insumos:
                print(f"      • {ri.cantidad} {ri.insumo.unidad_medida} de {ri.insumo.nombre}")
                
        except (ProductoVenta.DoesNotExist, Receta.DoesNotExist):
            print(f"   ❌ Error: producto o receta no encontrados")

def main():
    # Verificar que el producto puede ordenarse
    resultado = verificar_producto_puede_ordenarse()
    
    # Comparar con el producto que ya funcionaba
    comparar_con_algas_con_nalgas()
    
    print(f"\n" + "=" * 80)
    print("🎯 RESUMEN:")
    if resultado:
        print("✅ PROBLEMA RESUELTO")
        print("• 'algas alas algas con algas' ahora tiene receta")
        print("• Puede verificar inventario y deducir stock")
        print("• Debería funcionar igual que 'algas con nalgas'")
    else:
        print("⚠️ PROBLEMA PARCIALMENTE RESUELTO")
        print("• 'algas alas algas con algas' ahora tiene receta")
        print("• Pero hay problemas de inventario")
        print("• Verificar stock de alga nori")

if __name__ == "__main__":
    main()
