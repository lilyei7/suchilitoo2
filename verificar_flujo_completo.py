#!/usr/bin/env python
"""
Script para verificar el flujo completo del sistema de inventario
"""
import os
import sys

# Agregar el directorio del proyecto al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

import django
django.setup()

from restaurant.models import Insumo, Proveedor, Inventario
from accounts.models import Sucursal

def verificar_flujo_completo():
    print("🔍 VERIFICACIÓN DEL FLUJO COMPLETO DEL SISTEMA")
    print("=" * 70)
    
    # 1. Verificar insumos existentes
    print("1️⃣ VERIFICANDO INSUMOS:")
    insumos = Insumo.objects.filter(activo=True)
    print(f"   📦 Total de insumos activos: {insumos.count()}")
    
    for insumo in insumos:
        print(f"\n   📋 {insumo.codigo} - {insumo.nombre}")
        print(f"      Categoría: {insumo.categoria.nombre if insumo.categoria else 'Sin categoría'}")
        print(f"      Proveedor: {insumo.proveedor_principal.nombre if insumo.proveedor_principal else '❌ Sin proveedor'}")
        
        # Verificar inventarios
        inventarios = Inventario.objects.filter(insumo=insumo)
        print(f"      Inventarios: {inventarios.count()} sucursal(es)")
        
        for inv in inventarios:
            print(f"         🏢 {inv.sucursal.nombre}: {inv.cantidad_actual} {insumo.unidad_medida.abreviacion if insumo.unidad_medida else ''}")
    
    # 2. Verificar proveedores
    print(f"\n2️⃣ VERIFICANDO PROVEEDORES:")
    proveedores = Proveedor.objects.filter(activo=True)
    print(f"   🏭 Total de proveedores activos: {proveedores.count()}")
    
    for proveedor in proveedores:
        insumos_proveidos = Insumo.objects.filter(proveedor_principal=proveedor, activo=True)
        print(f"\n   🏭 {proveedor.nombre}")
        print(f"      Contacto: {proveedor.contacto or 'Sin contacto'}")
        print(f"      Teléfono: {proveedor.telefono or 'Sin teléfono'}")
        print(f"      Email: {proveedor.email or 'Sin email'}")
        print(f"      Insumos proveídos: {insumos_proveidos.count()}")
        
        for insumo in insumos_proveidos:
            print(f"         📦 {insumo.codigo} - {insumo.nombre}")
    
    # 3. Verificar sucursales
    print(f"\n3️⃣ VERIFICANDO SUCURSALES:")
    sucursales = Sucursal.objects.filter(activa=True)
    print(f"   🏢 Total de sucursales activas: {sucursales.count()}")
    
    for sucursal in sucursales:
        inventarios_sucursal = Inventario.objects.filter(sucursal=sucursal)
        print(f"\n   🏢 {sucursal.nombre}")
        print(f"      Inventarios: {inventarios_sucursal.count()} insumo(s)")
        
        for inv in inventarios_sucursal:
            print(f"         📦 {inv.insumo.codigo}: {inv.cantidad_actual} {inv.insumo.unidad_medida.abreviacion if inv.insumo.unidad_medida else ''}")

def mostrar_resumen_api():
    """Mostrar información que se envía a través del API de detalles"""
    print("\n4️⃣ VERIFICANDO API DE DETALLES:")
    
    insumos = Insumo.objects.filter(activo=True)
    
    for insumo in insumos:
        print(f"\n   📡 API para {insumo.codigo} - {insumo.nombre}:")
        print(f"      ID: {insumo.id}")
        print(f"      Proveedor: {insumo.proveedor_principal.nombre if insumo.proveedor_principal else 'Sin proveedor'}")
        
        if insumo.proveedor_principal:
            print(f"      Contacto proveedor: {insumo.proveedor_principal.contacto or 'Sin contacto'}")
            print(f"      Teléfono proveedor: {insumo.proveedor_principal.telefono or 'Sin teléfono'}")
            print(f"      Email proveedor: {insumo.proveedor_principal.email or 'Sin email'}")
        
        # Simular cálculo de stock total
        inventarios = Inventario.objects.filter(insumo=insumo)
        stock_total = sum(inv.cantidad_actual for inv in inventarios if inv.cantidad_actual)
        print(f"      Stock total: {stock_total} {insumo.unidad_medida.abreviacion if insumo.unidad_medida else ''}")
        
        # Estado del stock
        from decimal import Decimal
        if stock_total <= insumo.stock_minimo:
            estado = '🔴 BAJO'
        elif stock_total <= (insumo.stock_minimo * Decimal('1.5')):
            estado = '🟡 MEDIO'
        else:
            estado = '🟢 ALTO'
        print(f"      Estado: {estado}")

def mostrar_recomendaciones():
    """Mostrar recomendaciones para completar el flujo"""
    print("\n5️⃣ RECOMENDACIONES PARA COMPLETAR EL FLUJO:")
    
    # Insumos sin proveedor
    insumos_sin_proveedor = Insumo.objects.filter(activo=True, proveedor_principal__isnull=True)
    if insumos_sin_proveedor.count() > 0:
        print(f"\n   ⚠️ {insumos_sin_proveedor.count()} insumo(s) sin proveedor asignado:")
        for insumo in insumos_sin_proveedor:
            print(f"      📦 {insumo.codigo} - {insumo.nombre}")
        print("      💡 Ir a /dashboard/proveedores/ para asignar proveedores")
    
    # Inventarios con stock 0
    inventarios_sin_stock = Inventario.objects.filter(cantidad_actual=0)
    if inventarios_sin_stock.count() > 0:
        print(f"\n   📊 {inventarios_sin_stock.count()} inventario(s) con stock 0:")
        for inv in inventarios_sin_stock:
            print(f"      📦 {inv.insumo.codigo} en {inv.sucursal.nombre}")
        print("      💡 Ir a /dashboard/entradas-salidas/ para dar stock inicial")
    
    # Si todo está bien
    if insumos_sin_proveedor.count() == 0 and inventarios_sin_stock.count() == 0:
        print("\n   ✅ ¡Todo el flujo está completo!")
        print("      - Todos los insumos tienen proveedores asignados")
        print("      - Todos los inventarios tienen stock")
        print("      - El modal de detalles mostrará información completa del proveedor")

if __name__ == "__main__":
    print("🚀 INICIANDO VERIFICACIÓN DEL FLUJO COMPLETO\n")
    
    verificar_flujo_completo()
    mostrar_resumen_api()
    mostrar_recomendaciones()
    
    print("\n" + "=" * 70)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("\n📋 FLUJO DEL SISTEMA:")
    print("1. Crear insumo → /dashboard/inventario/ (botón 'Nuevo Insumo')")
    print("2. Asignar proveedor → /dashboard/proveedores/ (gestionar proveedores)")
    print("3. Dar stock → /dashboard/entradas-salidas/ (crear movimiento de entrada)")
    print("4. Ver detalles → /dashboard/inventario/ (botón 'Ver detalles' en la tabla)")
