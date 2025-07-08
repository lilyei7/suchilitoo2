#!/usr/bin/env python3
"""
Script para probar el sistema de descuento automático de inventario.
Simula la creación de una orden y verifica que los insumos se descuenten correctamente.
"""

import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.db import transaction
from django.utils import timezone
from restaurant.models import (
    ProductoVenta, Receta, RecetaInsumo, Insumo, InsumoCompuesto, 
    InsumoElaborado, Inventario, MovimientoInventario, CategoriaProducto
)
from mesero.models import Orden, OrdenItem, Mesa
from accounts.models import Sucursal, Usuario
from inventario_automatico import InventarioAutomatico

def mostrar_estado_inventario():
    """Muestra el estado actual del inventario"""
    print("📊 ESTADO ACTUAL DEL INVENTARIO")
    print("=" * 60)
    
    # Obtener inventarios con stock > 0
    inventarios = Inventario.objects.filter(cantidad_actual__gt=0).order_by('insumo__nombre')
    
    if not inventarios.exists():
        print("⚠️  No hay inventarios con stock disponible")
        return
    
    for inventario in inventarios:
        print(f"📦 {inventario.insumo.nombre} ({inventario.insumo.codigo})")
        print(f"   📊 Stock actual: {inventario.cantidad_actual} {inventario.insumo.unidad_medida.abreviacion}")
        print(f"   🏢 Sucursal: {inventario.sucursal.nombre}")
        print(f"   🏷️  Tipo: {inventario.insumo.tipo}")
        
        # Mostrar componentes si es compuesto o elaborado
        if inventario.insumo.tipo in ['compuesto', 'elaborado']:
            componentes = InsumoCompuesto.objects.filter(insumo_compuesto=inventario.insumo)
            if componentes.exists():
                print(f"   📋 Componentes:")
                for comp in componentes:
                    print(f"      - {comp.cantidad} {comp.insumo_componente.unidad_medida.abreviacion} de {comp.insumo_componente.nombre}")
        print()

def mostrar_recetas_disponibles():
    """Muestra las recetas disponibles para productos"""
    print("🍣 RECETAS DISPONIBLES")
    print("=" * 60)
    
    productos = ProductoVenta.objects.filter(disponible=True)
    
    for producto in productos:
        print(f"🍱 {producto.nombre} (${producto.precio})")
        try:
            receta = producto.receta
            if receta:
                print(f"   📋 Receta: {receta.nombre}")
                print(f"   ⏱️  Tiempo: {receta.tiempo_preparacion} min")
                print(f"   🍽️  Porciones: {receta.porciones}")
                print(f"   📝 Ingredientes:")
                
                for ingrediente in receta.insumos.all():
                    print(f"      - {ingrediente.cantidad} {ingrediente.insumo.unidad_medida.abreviacion} de {ingrediente.insumo.nombre}")
            else:
                print(f"   ⚠️  Sin receta definida")
        except Exception as e:
            print(f"   ❌ Error al obtener receta: {e}")
        print()

def verificar_stock_producto(producto, cantidad):
    """Verifica si hay suficiente stock para un producto"""
    print(f"🔍 VERIFICANDO STOCK PARA {cantidad}x {producto.nombre}")
    print("-" * 40)
    
    sucursal = Sucursal.objects.first()
    if not sucursal:
        print("❌ No hay sucursales disponibles")
        return False
    
    inventario = InventarioAutomatico(sucursal)
    stock_ok, faltantes = inventario.verificar_stock_disponible(producto, cantidad)
    
    if stock_ok:
        print(f"✅ Stock suficiente para {cantidad}x {producto.nombre}")
        return True
    else:
        print(f"❌ Stock insuficiente para {cantidad}x {producto.nombre}")
        print("📋 Faltantes:")
        for faltante in faltantes:
            if 'error' in faltante:
                print(f"   ❌ Error: {faltante['error']}")
            else:
                print(f"   - {faltante['insumo']}: necesario {faltante['necesario']} {faltante['unidad']}, disponible {faltante['disponible']} {faltante['unidad']}")
        return False

def simular_creacion_orden():
    """Simula la creación de una orden completa"""
    print("🍽️  SIMULANDO CREACIÓN DE ORDEN")
    print("=" * 60)
    
    # Obtener datos necesarios
    sucursal = Sucursal.objects.first()
    if not sucursal:
        print("❌ No hay sucursales disponibles")
        return
    
    mesero = Usuario.objects.filter(rol__nombre='mesero').first()
    if not mesero:
        print("❌ No hay meseros disponibles")
        return
    
    mesa = Mesa.objects.filter(activa=True).first()
    if not mesa:
        print("❌ No hay mesas disponibles")
        return
    
    producto = ProductoVenta.objects.filter(disponible=True).first()
    if not producto:
        print("❌ No hay productos disponibles")
        return
    
    print(f"🏢 Sucursal: {sucursal.nombre}")
    print(f"👨‍💼 Mesero: {mesero.first_name} {mesero.last_name}")
    print(f"🪑 Mesa: {mesa.numero}")
    print(f"🍱 Producto: {producto.nombre}")
    
    # Mostrar estado inicial del inventario
    print("\n📊 ESTADO INICIAL DEL INVENTARIO:")
    inventarios_iniciales = {}
    for inventario in Inventario.objects.filter(sucursal=sucursal):
        inventarios_iniciales[inventario.insumo.id] = inventario.cantidad_actual
        print(f"   {inventario.insumo.nombre}: {inventario.cantidad_actual} {inventario.insumo.unidad_medida.abreviacion}")
    
    # Verificar stock antes de crear la orden
    cantidad = 1
    print(f"\n🔍 Verificando stock para {cantidad}x {producto.nombre}...")
    
    inventario = InventarioAutomatico(sucursal)
    stock_ok, faltantes = inventario.verificar_stock_disponible(producto, cantidad)
    
    if not stock_ok:
        print("❌ No hay suficiente stock para crear la orden")
        return
    
    print("✅ Stock suficiente, creando orden...")
    
    try:
        with transaction.atomic():
            # Crear la orden
            orden = Orden.objects.create(
                mesero=mesero,
                mesa=mesa,
                estado='pendiente',
                numero_orden=f"TEST-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            )
            
            # Crear item de la orden
            orden_item = OrdenItem.objects.create(
                orden=orden,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )
            
            print(f"✅ Orden creada: #{orden.numero_orden}")
            print(f"   Item: {cantidad}x {producto.nombre} - ${orden_item.subtotal}")
            
            # Procesar descuento automático
            print("\n🔄 Procesando descuento automático de inventario...")
            
            success, messages = inventario.procesar_orden(orden)
            
            print(f"\n{'='*50}")
            print(f"RESULTADO: {'✅ ÉXITO' if success else '❌ ERROR'}")
            print(f"{'='*50}")
            
            # Mostrar mensajes del procesamiento
            for message in messages:
                print(message)
            
            # Mostrar estado final del inventario
            print("\n📊 ESTADO FINAL DEL INVENTARIO:")
            cambios = False
            for inventario in Inventario.objects.filter(sucursal=sucursal):
                inicial = inventarios_iniciales.get(inventario.insumo.id, 0)
                actual = inventario.cantidad_actual
                
                if inicial != actual:
                    cambios = True
                    diferencia = actual - inicial
                    print(f"   {inventario.insumo.nombre}: {inicial} → {actual} ({diferencia:+}) {inventario.insumo.unidad_medida.abreviacion}")
                else:
                    print(f"   {inventario.insumo.nombre}: {actual} {inventario.insumo.unidad_medida.abreviacion} (sin cambios)")
            
            if not cambios:
                print("   ℹ️  No se detectaron cambios en el inventario")
            
            # Mostrar movimientos generados
            print("\n📋 MOVIMIENTOS DE INVENTARIO GENERADOS:")
            movimientos = MovimientoInventario.objects.filter(
                documento_referencia=orden.numero_orden
            ).order_by('-created_at')
            
            if movimientos.exists():
                for movimiento in movimientos:
                    print(f"   📤 {movimiento.insumo.nombre}: -{movimiento.cantidad} {movimiento.insumo.unidad_medida.abreviacion}")
                    print(f"      Motivo: {movimiento.motivo}")
                    print(f"      Usuario: {movimiento.usuario.nombre}")
                    print(f"      Fecha: {movimiento.fecha}")
                    print()
            else:
                print("   ℹ️  No se generaron movimientos de inventario")
            
            if success:
                print("🎉 ¡Prueba completada exitosamente!")
                return orden
            else:
                print("❌ La prueba falló")
                return None
                
    except Exception as e:
        print(f"❌ Error durante la simulación: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Función principal del script"""
    print("🧪 SISTEMA DE DESCUENTO AUTOMÁTICO DE INVENTARIO")
    print("=" * 80)
    
    # Mostrar estado inicial
    mostrar_estado_inventario()
    print()
    
    # Mostrar recetas disponibles
    mostrar_recetas_disponibles()
    print()
    
    # Preguntar al usuario qué quiere hacer
    print("¿Qué deseas hacer?")
    print("1. Verificar stock de un producto")
    print("2. Simular creación de orden completa")
    print("3. Mostrar estado del inventario")
    print("4. Salir")
    
    try:
        opcion = input("\nSelecciona una opción (1-4): ").strip()
        
        if opcion == "1":
            productos = ProductoVenta.objects.filter(disponible=True)[:5]
            if not productos.exists():
                print("❌ No hay productos disponibles")
                return
            
            print("\nProductos disponibles:")
            for i, producto in enumerate(productos, 1):
                print(f"{i}. {producto.nombre} (${producto.precio})")
            
            try:
                prod_index = int(input("\nSelecciona un producto: ")) - 1
                if 0 <= prod_index < len(productos):
                    producto = productos[prod_index]
                    cantidad = int(input(f"¿Cuántas unidades de {producto.nombre}? "))
                    verificar_stock_producto(producto, cantidad)
                else:
                    print("❌ Producto no válido")
            except ValueError:
                print("❌ Entrada no válida")
        
        elif opcion == "2":
            simular_creacion_orden()
        
        elif opcion == "3":
            mostrar_estado_inventario()
        
        elif opcion == "4":
            print("👋 ¡Hasta luego!")
        
        else:
            print("❌ Opción no válida")
            
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
