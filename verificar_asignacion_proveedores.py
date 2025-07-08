#!/usr/bin/env python
"""
Script para verificar asignación de proveedores a insumos
"""
import os
import sys

# Agregar el directorio del proyecto al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

import django
django.setup()

from restaurant.models import Insumo, Proveedor

def verificar_asignacion_proveedores():
    print("🔍 VERIFICACIÓN DE ASIGNACIÓN DE PROVEEDORES")
    print("=" * 60)
    
    # Estadísticas básicas
    total_insumos = Insumo.objects.count()
    insumos_con_proveedor = Insumo.objects.filter(proveedor_principal__isnull=False).count()
    insumos_sin_proveedor = total_insumos - insumos_con_proveedor
    
    print(f"📦 ESTADÍSTICAS DE INSUMOS:")
    print(f"   Total de insumos: {total_insumos}")
    print(f"   Con proveedor: {insumos_con_proveedor}")
    print(f"   Sin proveedor: {insumos_sin_proveedor}")
    print()
    
    # Mostrar insumos con proveedor
    print("✅ INSUMOS CON PROVEEDOR ASIGNADO:")
    insumos_con_prov = Insumo.objects.filter(proveedor_principal__isnull=False).select_related('proveedor_principal')[:10]
    
    if insumos_con_prov:
        for insumo in insumos_con_prov:
            print(f"   {insumo.codigo} - {insumo.nombre}")
            print(f"      Proveedor: {insumo.proveedor_principal.nombre}")
            if insumo.proveedor_principal.contacto:
                print(f"      Contacto: {insumo.proveedor_principal.contacto}")
            if insumo.proveedor_principal.telefono:
                print(f"      Teléfono: {insumo.proveedor_principal.telefono}")
            if insumo.proveedor_principal.email:
                print(f"      Email: {insumo.proveedor_principal.email}")
            print()
    else:
        print("   ❌ No hay insumos con proveedor asignado")
    
    # Mostrar algunos insumos sin proveedor
    print("❌ ALGUNOS INSUMOS SIN PROVEEDOR:")
    insumos_sin_prov = Insumo.objects.filter(proveedor_principal__isnull=True)[:5]
    
    if insumos_sin_prov:
        for insumo in insumos_sin_prov:
            print(f"   {insumo.codigo} - {insumo.nombre}")
        if insumos_sin_proveedor > 5:
            print(f"   ... y {insumos_sin_proveedor - 5} más")
    else:
        print("   ✅ Todos los insumos tienen proveedor asignado")
    
    print()

def asignar_proveedores_automaticamente():
    """Asignar proveedores a insumos que no tienen"""
    print("🔗 ASIGNANDO PROVEEDORES AUTOMÁTICAMENTE...")
    
    # Obtener proveedores disponibles
    proveedores = list(Proveedor.objects.filter(activo=True))
    if not proveedores:
        print("❌ No hay proveedores activos disponibles")
        return
    
    # Obtener insumos sin proveedor
    insumos_sin_proveedor = Insumo.objects.filter(proveedor_principal__isnull=True)
    total = insumos_sin_proveedor.count()
    
    if total == 0:
        print("✅ Todos los insumos ya tienen proveedor asignado")
        return
    
    print(f"📝 Asignando proveedor a {total} insumos...")
    
    # Asignar proveedores de forma cíclica
    asignados = 0
    for i, insumo in enumerate(insumos_sin_proveedor):
        proveedor = proveedores[i % len(proveedores)]
        insumo.proveedor_principal = proveedor
        insumo.save()
        asignados += 1
        print(f"   ✅ {insumo.codigo} -> {proveedor.nombre}")
    
    print(f"🎉 Se asignaron proveedores a {asignados} insumos")

if __name__ == "__main__":
    print("🚀 INICIANDO VERIFICACIÓN DE ASIGNACIÓN DE PROVEEDORES\n")
    
    # Verificar estado actual
    verificar_asignacion_proveedores()
    
    # Preguntar si asignar proveedores
    print("¿Desea asignar proveedores automáticamente a los insumos sin proveedor? (y/n)")
    respuesta = input().lower().strip()
    
    if respuesta in ['y', 'yes', 'sí', 'si', '1']:
        asignar_proveedores_automaticamente()
        print("\n" + "=" * 60)
        print("🔍 ESTADO FINAL:")
        verificar_asignacion_proveedores()
    
    print("\n✅ Verificación completada")
