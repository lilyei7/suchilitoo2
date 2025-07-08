#!/usr/bin/env python
"""
Script para crear escenarios de prueba para verificar la visualización de proveedores.
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Insumo
from dashboard.models import Proveedor, ProveedorInsumo
from accounts.models import Usuario

def main():
    print("🧪 CREANDO ESCENARIOS DE PRUEBA PARA PROVEEDORES")
    print("=" * 60)
    
    try:
        # Buscar un usuario admin
        admin_user = Usuario.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = Usuario.objects.filter(rol__nombre='admin').first()
        
        if not admin_user:
            print("❌ No se encontró un usuario administrador")
            return
        
        print(f"✅ Usuario admin: {admin_user.username}")
        
        # Escenario 1: Insumo con solo proveedor principal
        print(f"\n🔧 ESCENARIO 1: Insumo con solo proveedor principal")
        insumo1 = Insumo.objects.filter(proveedor_principal__isnull=False).first()
        if insumo1:
            # Remover relaciones ProveedorInsumo si existen
            ProveedorInsumo.objects.filter(insumo=insumo1).delete()
            print(f"   ✅ {insumo1.nombre} - Solo proveedor principal: {insumo1.proveedor_principal.nombre}")
        else:
            print("   ⚠️ No se encontró insumo con proveedor principal")
        
        # Escenario 2: Insumo con solo proveedores asignados (sin principal)
        print(f"\n🔧 ESCENARIO 2: Insumo con solo proveedores asignados")
        insumo2 = Insumo.objects.filter(proveedor_principal__isnull=True).first()
        if not insumo2:
            # Crear un insumo sin proveedor principal
            from restaurant.models import CategoriaInsumo, UnidadMedida
            categoria = CategoriaInsumo.objects.first()
            unidad = UnidadMedida.objects.first()
            
            insumo2 = Insumo.objects.create(
                codigo="TEST-002",
                nombre="Insumo Test Solo Asignados",
                categoria=categoria,
                unidad_medida=unidad,
                precio_unitario=10.00,
                stock_minimo=5,
                proveedor_principal=None  # Sin proveedor principal
            )
            print(f"   ✅ Creado: {insumo2.nombre}")
        
        # Asignar 2 proveedores al insumo2
        proveedores = Proveedor.objects.all()[:2]
        ProveedorInsumo.objects.filter(insumo=insumo2).delete()  # Limpiar primero
        
        for i, proveedor in enumerate(proveedores):
            relacion = ProveedorInsumo.objects.create(
                proveedor=proveedor,
                insumo=insumo2,
                precio_unitario=15.0 + i * 5,
                cantidad_minima=10 + i * 5,
                tiempo_entrega_dias=2 + i,
                notas=f"Notas para {proveedor.nombre_comercial}"
            )
            print(f"   ✅ Asignado: {proveedor.nombre_comercial} - ${relacion.precio_unitario}")
        
        # Escenario 3: Insumo con proveedor principal + proveedores asignados
        print(f"\n🔧 ESCENARIO 3: Insumo con proveedor principal Y proveedores asignados")
        insumo3 = Insumo.objects.filter(proveedor_principal__isnull=False).exclude(id=insumo1.id if insumo1 else None).first()
        if insumo3:
            # Asignar un proveedor adicional
            proveedor_extra = proveedores[0] if proveedores else None
            if proveedor_extra:
                # Limpiar relaciones existentes para evitar duplicados
                ProveedorInsumo.objects.filter(insumo=insumo3, proveedor=proveedor_extra).delete()
                
                relacion_extra = ProveedorInsumo.objects.create(
                    proveedor=proveedor_extra,
                    insumo=insumo3,
                    precio_unitario=12.50,
                    cantidad_minima=20,
                    tiempo_entrega_dias=3,
                    notas="Proveedor alternativo con mejor precio"
                )
                print(f"   ✅ {insumo3.nombre}")
                print(f"      - Principal: {insumo3.proveedor_principal.nombre}")
                print(f"      - Asignado: {proveedor_extra.nombre_comercial} - ${relacion_extra.precio_unitario}")
          # Escenario 4: Insumo sin proveedores
        print(f"\n🔧 ESCENARIO 4: Insumo sin proveedores")
        
        # Obtener categoría y unidad para crear insumo
        from restaurant.models import CategoriaInsumo, UnidadMedida
        categoria = CategoriaInsumo.objects.first()
        unidad = UnidadMedida.objects.first()
        
        insumo4 = Insumo.objects.filter(proveedor_principal__isnull=True).exclude(id=insumo2.id if insumo2 else None).first()
        if not insumo4:
            insumo4 = Insumo.objects.create(
                codigo="TEST-004",
                nombre="Insumo Sin Proveedores",
                categoria=categoria,
                unidad_medida=unidad,
                precio_unitario=5.00,
                stock_minimo=10
            )
        
        # Asegurar que no tiene proveedores
        ProveedorInsumo.objects.filter(insumo=insumo4).delete()
        insumo4.proveedor_principal = None
        insumo4.save()
        print(f"   ✅ {insumo4.nombre} - Sin proveedores")
        
        print(f"\n📋 RESUMEN DE ESCENARIOS CREADOS:")
        print(f"   1. Solo principal: {insumo1.nombre if insumo1 else 'N/A'} (ID: {insumo1.id if insumo1 else 'N/A'})")
        print(f"   2. Solo asignados: {insumo2.nombre if insumo2 else 'N/A'} (ID: {insumo2.id if insumo2 else 'N/A'})")
        print(f"   3. Principal + asignados: {insumo3.nombre if insumo3 else 'N/A'} (ID: {insumo3.id if insumo3 else 'N/A'})")
        print(f"   4. Sin proveedores: {insumo4.nombre if insumo4 else 'N/A'} (ID: {insumo4.id if insumo4 else 'N/A'})")
        
        print(f"\n🌐 URLs PARA PROBAR EN EL NAVEGADOR:")
        print(f"   Inventario: http://127.0.0.1:8000/dashboard/inventario/")
        print(f"   Proveedores: http://127.0.0.1:8000/dashboard/proveedores/")
        
        print(f"\n✅ ESCENARIOS CREADOS. Puedes probar los modales de detalles en el navegador.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
