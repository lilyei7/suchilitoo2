#!/usr/bin/env python
"""
Script para verificar qué datos tenemos en la base de datos para insumos
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Insumo

def verificar_datos():
    """Verificar qué insumos tenemos en la base de datos"""
    
    print("=" * 60)
    print("VERIFICACIÓN DE DATOS DE INSUMOS")
    print("=" * 60)
    
    # Contar insumos por tipo
    total_insumos = Insumo.objects.count()
    basicos = Insumo.objects.filter(tipo='basico').count()
    compuestos = Insumo.objects.filter(tipo='compuesto').count()
    elaborados = Insumo.objects.filter(tipo='elaborado').count()
    
    print(f"\n📊 RESUMEN GENERAL:")
    print(f"   Total de insumos: {total_insumos}")
    print(f"   🔹 Básicos: {basicos}")
    print(f"   🔹 Compuestos: {compuestos}")
    print(f"   🔹 Elaborados: {elaborados}")
    
    # Mostrar algunos ejemplos de cada tipo
    print(f"\n📦 INSUMOS BÁSICOS (primeros 5):")
    insumos_basicos = Insumo.objects.filter(tipo='basico', activo=True)[:5]
    if insumos_basicos:
        for insumo in insumos_basicos:
            print(f"   ID {insumo.id}: {insumo.codigo} - {insumo.nombre} (${insumo.precio_unitario})")
    else:
        print("   ❌ No hay insumos básicos")
    
    print(f"\n🔧 INSUMOS COMPUESTOS (primeros 5):")
    insumos_compuestos = Insumo.objects.filter(tipo='compuesto', activo=True)[:5]
    if insumos_compuestos:
        for insumo in insumos_compuestos:
            print(f"   ID {insumo.id}: {insumo.codigo} - {insumo.nombre} (${insumo.precio_unitario})")
    else:
        print("   ❌ No hay insumos compuestos")
    
    print(f"\n🍣 INSUMOS ELABORADOS (primeros 5):")
    insumos_elaborados = Insumo.objects.filter(tipo='elaborado', activo=True)[:5]
    if insumos_elaborados:
        for insumo in insumos_elaborados:
            print(f"   ID {insumo.id}: {insumo.codigo} - {insumo.nombre} (${insumo.precio_unitario})")
    else:
        print("   ❌ No hay insumos elaborados")
    
    # Verificar disponibilidad para elaborados
    disponibles_para_elaborados = Insumo.objects.filter(
        tipo__in=['basico', 'compuesto'], 
        activo=True
    ).count()
    
    print(f"\n🎯 DISPONIBLES PARA ELABORADOS:")
    print(f"   Total disponibles: {disponibles_para_elaborados}")
    
    if disponibles_para_elaborados == 0:
        print("   ⚠️ PROBLEMA: No hay insumos disponibles para crear elaborados")
        print("   💡 SOLUCIÓN: Necesitas crear algunos insumos básicos y/o compuestos primero")
    else:
        print("   ✅ Hay insumos disponibles para crear elaborados")
    
    print("=" * 60)

if __name__ == '__main__':
    verificar_datos()
