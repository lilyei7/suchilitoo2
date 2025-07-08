#!/usr/bin/env python
"""
Script para verificar el comportamiento del inventario para usuarios gerente
"""
import os
import sys

# Agregar el directorio del proyecto al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Sucursal
from restaurant.models import Insumo, Inventario, Proveedor
from decimal import Decimal

User = get_user_model()

def simular_vista_inventario_gerente():
    """Simular lo que ve un gerente en la vista de inventario"""
    print("🎯 SIMULANDO VISTA DE INVENTARIO PARA GERENTE")
    print("=" * 60)
    
    # Obtener usuario gerente
    try:
        gerente = User.objects.get(username="gerente_test")
        print(f"👤 Usuario: {gerente.username} ({gerente.first_name} {gerente.last_name})")
        print(f"🏢 Sucursal asignada: {gerente.sucursal.nombre}")
        print(f"🔒 Rol: {gerente.rol.nombre}")
        print()
        
        # Lógica similar a la vista inventario_view para gerente
        if gerente.rol and gerente.rol.nombre == 'gerente' and gerente.sucursal:
            # Gerente solo ve su sucursal asignada
            sucursales_disponibles = Sucursal.objects.filter(id=gerente.sucursal.id, activa=True)
            sucursal_filtro = gerente.sucursal
            es_admin = False
            
            print(f"✅ PERMISOS DE GERENTE:")
            print(f"   - Puede ver sucursal: {sucursal_filtro.nombre}")
            print(f"   - Es admin: {es_admin}")
            print(f"   - Sucursales disponibles: {[s.nombre for s in sucursales_disponibles]}")
            print()
            
            # Obtener insumos de su sucursal
            inventarios_base = Inventario.objects.filter(sucursal=sucursal_filtro)
            insumos_ids = inventarios_base.values_list('insumo_id', flat=True).distinct()
            insumos = Insumo.objects.filter(id__in=insumos_ids, activo=True)
            
            print(f"📦 INSUMOS EN SU SUCURSAL ({sucursal_filtro.nombre}):")
            print(f"   Total de insumos: {insumos.count()}")
            print()
            
            # Mostrar detalles de cada insumo
            for insumo in insumos:
                inventario = Inventario.objects.filter(sucursal=sucursal_filtro, insumo=insumo).first()
                
                # Determinar estado del stock
                if inventario.cantidad_actual <= insumo.stock_minimo:
                    estado_stock = 'bajo'
                elif inventario.cantidad_actual <= (insumo.stock_minimo * Decimal('1.5')):
                    estado_stock = 'medio'
                else:
                    estado_stock = 'alto'
                
                print(f"   📋 {insumo.codigo} - {insumo.nombre}")
                print(f"      Categoría: {insumo.categoria.nombre if insumo.categoria else 'Sin categoría'}")
                print(f"      Stock actual: {inventario.cantidad_actual} {insumo.unidad_medida.abreviacion}")
                print(f"      Stock mínimo: {insumo.stock_minimo} {insumo.unidad_medida.abreviacion}")
                print(f"      Estado: {estado_stock}")
                print(f"      Precio unitario: ${insumo.precio_unitario}")
                if insumo.proveedor_principal:
                    print(f"      Proveedor: {insumo.proveedor_principal.nombre}")
                    print(f"      Contacto proveedor: {insumo.proveedor_principal.contacto or 'Sin contacto'}")
                else:
                    print(f"      Proveedor: Sin asignar")
                print()
        
        else:
            print("❌ El usuario no tiene permisos de gerente o no tiene sucursal asignada")
            
    except User.DoesNotExist:
        print("❌ No se encontró el usuario gerente_test")

def verificar_inventarios_todas_sucursales():
    """Mostrar inventarios de todas las sucursales para comparar"""
    print("🌐 INVENTARIOS EN TODAS LAS SUCURSALES (Vista de admin)")
    print("=" * 60)
    
    sucursales = Sucursal.objects.filter(activa=True)
    
    for sucursal in sucursales:
        print(f"\n🏢 {sucursal.nombre}:")
        inventarios = Inventario.objects.filter(sucursal=sucursal)
        
        if inventarios.exists():
            for inv in inventarios:
                proveedor = inv.insumo.proveedor_principal.nombre if inv.insumo.proveedor_principal else "Sin proveedor"
                print(f"   - {inv.insumo.codigo}: {inv.insumo.nombre}")
                print(f"     Stock: {inv.cantidad_actual} | Min: {inv.insumo.stock_minimo}")
                print(f"     Precio: ${inv.insumo.precio_unitario} | Proveedor: {proveedor}")
        else:
            print("   (Sin inventarios)")

def configurar_insumo_pepinos():
    """Configurar el insumo Pepinos como lo haría un gerente"""
    print("🥒 CONFIGURANDO INSUMO PEPINOS COMO GERENTE")
    print("=" * 60)
    
    try:
        insumo = Insumo.objects.get(nombre="Pepinos")
        proveedor = Proveedor.objects.first()
        
        if not proveedor:
            # Crear proveedor si no existe
            proveedor = Proveedor.objects.create(
                nombre="Verduras Frescas SAC",
                ruc="20555666777",
                direccion="Mercado Central, Puesto 15",
                contacto="Ana Rodríguez",
                telefono="+51 999 888 777",
                email="ventas@verdurasfrescas.com",
                activo=True
            )
            print(f"✅ Proveedor creado: {proveedor.nombre}")
        
        # Asignar proveedor y configurar precios
        insumo.proveedor_principal = proveedor
        insumo.precio_unitario = Decimal('3.20')  # S/ 3.20 por kg
        insumo.stock_minimo = Decimal('15.00')    # 15 kg mínimo
        insumo.save()
        
        print(f"✅ Insumo configurado: {insumo.nombre}")
        print(f"   Código: {insumo.codigo}")
        print(f"   Proveedor: {proveedor.nombre}")
        print(f"   Contacto: {proveedor.contacto}")
        print(f"   Teléfono: {proveedor.telefono}")
        print(f"   Precio unitario: S/ {insumo.precio_unitario}")
        print(f"   Stock mínimo: {insumo.stock_minimo} kg")
        
    except Insumo.DoesNotExist:
        print("❌ No se encontró el insumo 'Pepinos'")

if __name__ == "__main__":
    print("🚀 INICIANDO VERIFICACIÓN DEL FLUJO DE GERENTE\n")
    
    # Configurar insumo como lo haría un gerente
    configurar_insumo_pepinos()
    
    print("\n" + "=" * 60)
    
    # Simular vista de inventario para gerente
    simular_vista_inventario_gerente()
    
    print("\n" + "=" * 60)
    
    # Mostrar vista completa para comparar
    verificar_inventarios_todas_sucursales()
    
    print(f"\n✅ VERIFICACIÓN COMPLETADA")
    print(f"\n📝 NOTAS IMPORTANTES:")
    print(f"   - El gerente solo ve insumos de SU sucursal asignada")
    print(f"   - Puede asignar proveedores y establecer precios")
    print(f"   - El stock inicial se gestiona en Entradas y Salidas")
    print(f"   - Cada sucursal tiene inventarios independientes")
