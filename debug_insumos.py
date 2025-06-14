#!/usr/bin/env python
"""
Script para verificar los insumos existentes y debuggear el error
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def verificar_insumos():
    from restaurant.models import Insumo
    
    print("🔍 Verificando insumos existentes...")
    
    # Todos los insumos
    todos_insumos = Insumo.objects.all().order_by('id')
    print(f"\n📊 Total de insumos: {todos_insumos.count()}")
    
    # Por tipo
    basicos = Insumo.objects.filter(tipo='basico').count()
    compuestos = Insumo.objects.filter(tipo='compuesto').count()
    elaborados = Insumo.objects.filter(tipo='elaborado').count()
    
    print(f"   - Básicos: {basicos}")
    print(f"   - Compuestos: {compuestos}")
    print(f"   - Elaborados: {elaborados}")
    
    # Verificar si existe ID 47
    print(f"\n🔍 Verificando ID 47...")
    try:
        insumo_47 = Insumo.objects.get(id=47)
        print(f"✅ ID 47 SÍ existe: {insumo_47.nombre} (tipo: {insumo_47.tipo})")
    except Insumo.DoesNotExist:
        print("❌ ID 47 NO existe")
    
    # Mostrar últimos 10 insumos
    print(f"\n📋 Últimos 10 insumos:")
    for insumo in todos_insumos.order_by('-id')[:10]:
        print(f"   ID {insumo.id}: {insumo.nombre} (tipo: {insumo.tipo})")
    
    # Buscar IDs alrededor de 47
    print(f"\n🔍 IDs alrededor de 47:")
    for i in range(45, 50):
        try:
            insumo = Insumo.objects.get(id=i)
            print(f"   ID {i}: ✅ {insumo.nombre} (tipo: {insumo.tipo})")
        except Insumo.DoesNotExist:
            print(f"   ID {i}: ❌ No existe")

if __name__ == "__main__":
    verificar_insumos()
