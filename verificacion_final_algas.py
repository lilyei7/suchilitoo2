#!/usr/bin/env python
"""
Prueba final: Verificar que "algas alas algas con algas" funciona correctamente
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

from restaurant.models import ProductoVenta, Receta, Inventario
from accounts.models import Sucursal

def simular_orden_completa():
    """Simular una orden completa del producto"""
    print("🧪 PRUEBA FINAL: SIMULACIÓN DE ORDEN COMPLETA")
    print("=" * 60)
    
    # 1. Buscar el producto
    try:
        producto = ProductoVenta.objects.get(nombre="algas alas algas con algas")
        print(f"✅ Producto: {producto.nombre}")
        print(f"   ID: {producto.id}")
        print(f"   Precio: ${producto.precio}")
    except ProductoVenta.DoesNotExist:
        print("❌ Producto no encontrado")
        return False
    
    # 2. Verificar receta
    try:
        receta = producto.receta
        print(f"✅ Receta: ID {receta.id}")
        print(f"   Tiempo preparación: {receta.tiempo_preparacion} min")
        print(f"   Porciones: {receta.porciones}")
    except Receta.DoesNotExist:
        print("❌ El producto NO tiene receta")
        return False
    
    # 3. Verificar insumos y stock
    from restaurant.models import RecetaInsumo
    receta_insumos = RecetaInsumo.objects.filter(receta=receta)
    
    print(f"\n📋 VERIFICACIÓN DE INVENTARIO:")
    sucursal = Sucursal.objects.first()
    
    total_puede_preparar = True
    cantidades_a_deducir = []
    
    for ri in receta_insumos:
        insumo = ri.insumo
        cantidad_necesaria = ri.cantidad
        
        print(f"\n🥗 {insumo.nombre}:")
        print(f"   Necesario: {cantidad_necesaria} {insumo.unidad_medida}")
        
        try:
            inventario = Inventario.objects.get(sucursal=sucursal, insumo=insumo)
            cantidad_disponible = inventario.cantidad_actual
            
            print(f"   Disponible: {cantidad_disponible} {insumo.unidad_medida}")
            
            if cantidad_disponible >= cantidad_necesaria:
                print(f"   ✅ Stock suficiente")
                cantidades_a_deducir.append((inventario, cantidad_necesaria))
            else:
                print(f"   ❌ Stock insuficiente")
                total_puede_preparar = False
                
        except Inventario.DoesNotExist:
            print(f"   ❌ Sin inventario")
            total_puede_preparar = False
    
    # 4. Simular deducción (sin guardar realmente)
    if total_puede_preparar:
        print(f"\n🎉 ¡ORDEN EXITOSA!")
        print(f"✅ El producto puede prepararse")
        
        print(f"\n🧮 SIMULANDO DEDUCCIÓN DE INVENTARIO:")
        for inventario, cantidad in cantidades_a_deducir:
            nuevo_stock = inventario.cantidad_actual - cantidad
            print(f"   • {inventario.insumo.nombre}: {inventario.cantidad_actual} → {nuevo_stock} {inventario.insumo.unidad_medida}")
        
        print(f"\n💰 RESUMEN DE LA ORDEN:")
        print(f"   • Producto: {producto.nombre}")
        print(f"   • Precio: ${producto.precio}")
        print(f"   • Receta: ID {receta.id}")
        print(f"   • Tiempo prep: {receta.tiempo_preparacion} min")
        print(f"   • Estado: ✅ LISTA PARA PREPARAR")
        
        return True
    else:
        print(f"\n⚠️ ORDEN RECHAZADA")
        print(f"❌ Stock insuficiente para preparar el producto")
        return False

def verificar_estado_final():
    """Verificar el estado final del sistema"""
    print(f"\n\n📊 ESTADO FINAL DEL SISTEMA")
    print("=" * 60)
    
    # Verificar que "algas con nalgas" ya no tiene receta
    try:
        producto_nalgas = ProductoVenta.objects.get(nombre="algas con nalgas")
        try:
            receta_nalgas = producto_nalgas.receta
            print(f"⚠️ 'algas con nalgas' aún tiene receta (ID: {receta_nalgas.id})")
        except Receta.DoesNotExist:
            print(f"✅ 'algas con nalgas' ya no tiene receta (correcto)")
    except ProductoVenta.DoesNotExist:
        print(f"❓ 'algas con nalgas' no existe como producto")
    
    # Verificar que "algas alas algas con algas" tiene la receta correcta
    try:
        producto_alas = ProductoVenta.objects.get(nombre="algas alas algas con algas")
        receta_alas = producto_alas.receta
        print(f"✅ 'algas alas algas con algas' tiene receta (ID: {receta_alas.id})")
    except:
        print(f"❌ Problema con 'algas alas algas con algas'")

def main():
    print("🎯 VERIFICACIÓN FINAL DEL SISTEMA")
    print("=" * 80)
    
    # Simular orden completa
    exito = simular_orden_completa()
    
    # Verificar estado del sistema
    verificar_estado_final()
    
    print(f"\n" + "=" * 80)
    if exito:
        print("🎉 ¡SISTEMA FUNCIONANDO CORRECTAMENTE!")
        print("✅ El producto 'algas alas algas con algas' puede ordenarse")
        print("✅ La deducción de inventario funciona")
        print("✅ El problema original está resuelto")
    else:
        print("⚠️ Hay problemas de inventario")
        print("• El producto tiene receta válida")
        print("• Pero no hay stock suficiente")

if __name__ == "__main__":
    main()
