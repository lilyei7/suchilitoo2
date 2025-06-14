#!/usr/bin/env python3
"""
Script para diagnosticar el problema de FOREIGN KEY constraint failed
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from dashboard.models import Proveedor, ProveedorInsumo
from restaurant.models import Insumo

def diagnosticar_foreign_key_problem():
    print("🔍 Diagnosticando problema de Foreign Key constraint...")
    
    # Verificar que hay proveedores
    proveedores = Proveedor.objects.all()
    print(f"📊 Total de proveedores: {proveedores.count()}")
    
    if proveedores.exists():
        primer_proveedor = proveedores.first()
        print(f"   - Primer proveedor: {primer_proveedor.id} - {primer_proveedor.nombre_comercial}")
    
    # Verificar que hay insumos
    insumos = Insumo.objects.all()
    print(f"📦 Total de insumos: {insumos.count()}")
    
    if insumos.exists():
        primer_insumo = insumos.first()
        print(f"   - Primer insumo: {primer_insumo.id} - {primer_insumo.nombre}")
    
    # Verificar relaciones existentes
    relaciones = ProveedorInsumo.objects.all()
    print(f"🔗 Total de relaciones proveedor-insumo: {relaciones.count()}")
    
    if relaciones.exists():
        print("   Relaciones existentes:")
        for rel in relaciones[:5]:  # Mostrar las primeras 5
            print(f"      - Proveedor {rel.proveedor.id} -> Insumo {rel.insumo.id}")
    
    # Intentar simular la creación de una relación
    if proveedores.exists() and insumos.exists():
        print("\n🧪 Simulando creación de relación...")
        
        proveedor = proveedores.first()
        insumo = insumos.first()
        
        print(f"   Proveedor seleccionado: {proveedor.id} - {proveedor.nombre_comercial}")
        print(f"   Insumo seleccionado: {insumo.id} - {insumo.nombre}")
        
        # Verificar si ya existe
        existing = ProveedorInsumo.objects.filter(proveedor=proveedor, insumo=insumo).first()
        if existing:
            print(f"   ⚠️ Ya existe la relación: {existing.id}")
        else:
            print("   ✅ No existe la relación, se puede crear")
            
            # Intentar crear
            try:
                nueva_relacion = ProveedorInsumo.objects.create(
                    proveedor=proveedor,
                    insumo=insumo,
                    precio_unitario=100.00,
                    cantidad_minima=1,
                    tiempo_entrega_dias=3
                )
                print(f"   ✅ Relación creada exitosamente: {nueva_relacion.id}")
                
                # Eliminar la relación de prueba
                nueva_relacion.delete()
                print("   🗑️ Relación de prueba eliminada")
                
            except Exception as e:
                print(f"   ❌ Error al crear relación: {e}")
                print(f"   📝 Tipo de error: {type(e).__name__}")
                
                # Diagnosticar más a fondo
                print(f"\n🔍 Diagnóstico adicional:")
                print(f"   - Proveedor existe: {Proveedor.objects.filter(id=proveedor.id).exists()}")
                print(f"   - Insumo existe: {Insumo.objects.filter(id=insumo.id).exists()}")
                print(f"   - Tipo de proveedor.id: {type(proveedor.id)}")
                print(f"   - Tipo de insumo.id: {type(insumo.id)}")
    
    else:
        print("❌ No hay suficientes datos para probar")
    
    # Verificar estructura de las tablas
    print(f"\n📋 Verificando estructura de tablas...")
    
    # Verificar campos del modelo Proveedor
    proveedor_fields = [f.name for f in Proveedor._meta.get_fields()]
    print(f"   Campos de Proveedor: {proveedor_fields}")
    
    # Verificar campos del modelo Insumo
    insumo_fields = [f.name for f in Insumo._meta.get_fields()]
    print(f"   Campos de Insumo: {insumo_fields}")
    
    # Verificar campos del modelo ProveedorInsumo
    proveedor_insumo_fields = [f.name for f in ProveedorInsumo._meta.get_fields()]
    print(f"   Campos de ProveedorInsumo: {proveedor_insumo_fields}")

if __name__ == "__main__":
    diagnosticar_foreign_key_problem()
