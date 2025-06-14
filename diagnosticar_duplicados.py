#!/usr/bin/env python
"""
Script para diagnosticar el problema de duplicación de insumos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Insumo, Inventario
from accounts.models import Sucursal

def main():
    print("🔍 === DIAGNÓSTICO DE DUPLICACIÓN DE INSUMOS ===\n")
    
    # 1. Verificar insumos únicos vs duplicados
    print("1️⃣ VERIFICANDO INSUMOS EN LA BASE DE DATOS:")
    insumos = Insumo.objects.all().order_by('nombre', 'id')
    print(f"   📊 Total insumos en BD: {insumos.count()}")
    
    # Agrupar por nombre para detectar duplicados
    nombres_insumos = {}
    for insumo in insumos:
        if insumo.nombre in nombres_insumos:
            nombres_insumos[insumo.nombre].append(insumo)
        else:
            nombres_insumos[insumo.nombre] = [insumo]
    
    print("   📋 Insumos por nombre:")
    duplicados_encontrados = False
    for nombre, lista_insumos in nombres_insumos.items():
        if len(lista_insumos) > 1:
            duplicados_encontrados = True
            print(f"      🔴 DUPLICADO: '{nombre}' aparece {len(lista_insumos)} veces")
            for insumo in lista_insumos:
                print(f"         - ID: {insumo.id} | Código: {insumo.codigo} | Tipo: {insumo.tipo}")
        else:
            print(f"      ✅ ÚNICO: '{nombre}' (ID: {lista_insumos[0].id})")
    
    if not duplicados_encontrados:
        print("   ✅ No hay insumos duplicados en la base de datos")
    
    print()
    
    # 2. Verificar inventarios
    print("2️⃣ VERIFICANDO INVENTARIOS:")
    inventarios = Inventario.objects.all().order_by('insumo__nombre', 'sucursal__nombre')
    print(f"   📊 Total inventarios en BD: {inventarios.count()}")
    
    # Agrupar inventarios por insumo
    inventarios_por_insumo = {}
    for inv in inventarios:
        key = f"{inv.insumo.nombre} ({inv.insumo.id})"
        if key not in inventarios_por_insumo:
            inventarios_por_insumo[key] = []
        inventarios_por_insumo[key].append(inv)
    
    print("   📋 Inventarios por insumo:")
    for insumo_key, lista_inv in inventarios_por_insumo.items():
        print(f"      📦 {insumo_key}: {len(lista_inv)} inventarios")
        for inv in lista_inv:
            print(f"         - {inv.sucursal.nombre}: {inv.cantidad_actual}")
    
    print()
    
    # 3. Verificar códigos duplicados
    print("3️⃣ VERIFICANDO CÓDIGOS DUPLICADOS:")
    codigos = {}
    for insumo in insumos:
        if insumo.codigo in codigos:
            codigos[insumo.codigo].append(insumo)
        else:
            codigos[insumo.codigo] = [insumo]
    
    codigos_duplicados = False
    for codigo, lista_insumos in codigos.items():
        if len(lista_insumos) > 1:
            codigos_duplicados = True
            print(f"      🔴 CÓDIGO DUPLICADO: '{codigo}' usado por {len(lista_insumos)} insumos")
            for insumo in lista_insumos:
                print(f"         - ID: {insumo.id} | Nombre: '{insumo.nombre}'")
        else:
            print(f"      ✅ CÓDIGO ÚNICO: '{codigo}' → '{lista_insumos[0].nombre}'")
    
    if not codigos_duplicados:
        print("   ✅ No hay códigos duplicados")
    
    print()
      # 4. Simular exactamente lo que ve la vista
    print("4️⃣ SIMULANDO LA VISTA INVENTARIO_VIEW:")
    
    # Simular la lógica de la vista NUEVA (mostrar insumos únicos en lugar de inventarios por sucursal)
    print("   📋 Consulta de la vista (NUEVA LÓGICA):")
    insumos_vista = Insumo.objects.all()
    print(f"   📊 Total registros que devuelve la vista: {insumos_vista.count()}")
    
    print("   📋 Registros que ve el usuario:")
    for i, insumo in enumerate(insumos_vista, 1):
        print(f"      {i:2d}. {insumo.nombre:15s} | {insumo.codigo:10s} | Maestro Global    | registrado")
    
    print()
      # 5. Detectar el problema
    print("5️⃣ ANÁLISIS DEL PROBLEMA:")
    
    if duplicados_encontrados:
        print("   🔴 PROBLEMA: Hay insumos duplicados en la base de datos")
        print("   💡 CAUSA: El formulario está insertando múltiples veces el mismo insumo")
        print("   🔧 SOLUCIÓN: Eliminar insumos duplicados y corregir lógica de inserción")
    elif insumos_vista.count() != len(nombres_insumos):
        print("   🟡 POSIBLE PROBLEMA: Discrepancia en el conteo")
        print(f"   📊 Insumos únicos por nombre: {len(nombres_insumos)}")
        print(f"   📊 Insumos en la vista: {insumos_vista.count()}")
    else:
        print("   ✅ PERFECTO: La vista ahora muestra insumos únicos sin duplicación")
        print("   💡 EXPLICACIÓN: Los insumos son registros maestros globales")
        print("   🔧 SOLUCIÓN IMPLEMENTADA: Vista modificada para mostrar Insumo.objects.all()")
    
    print()
    
    # 6. Proponer solución automática
    print("6️⃣ PROPUESTA DE SOLUCIÓN AUTOMÁTICA:")
    
    if duplicados_encontrados:
        print("   🔧 LIMPIEZA AUTOMÁTICA DE DUPLICADOS:")
        print("   ⚠️  Se mantendrá el insumo con ID más bajo y se eliminarán los demás")
        
        respuesta = input("   ❓ ¿Deseas eliminar los insumos duplicados automáticamente? (s/n): ").lower().strip()
        
        if respuesta == 's':
            eliminados = 0
            for nombre, lista_insumos in nombres_insumos.items():
                if len(lista_insumos) > 1:
                    # Mantener el primero (ID más bajo) y eliminar el resto
                    insumo_a_mantener = lista_insumos[0]
                    for insumo_duplicado in lista_insumos[1:]:
                        print(f"      🗑️  Eliminando: '{insumo_duplicado.nombre}' (ID: {insumo_duplicado.id})")
                        # Primero eliminar inventarios relacionados
                        Inventario.objects.filter(insumo=insumo_duplicado).delete()
                        # Luego eliminar el insumo
                        insumo_duplicado.delete()
                        eliminados += 1
            
            print(f"   ✅ Eliminados {eliminados} insumos duplicados")
            
            # Verificar resultado
            insumos_finales = Insumo.objects.count()
            inventarios_finales = Inventario.objects.count()
            sucursales_activas = Sucursal.objects.filter(activa=True).count()
            
            print(f"   📊 Estado final:")
            print(f"      - Insumos únicos: {insumos_finales}")
            print(f"      - Inventarios: {inventarios_finales}")
            print(f"      - Esperados: {insumos_finales * sucursales_activas}")
            
            # Recrear inventarios si es necesario
            if inventarios_finales < insumos_finales * sucursales_activas:
                print("   🔄 Recreando inventarios faltantes...")
                for insumo in Insumo.objects.all():
                    for sucursal in Sucursal.objects.filter(activa=True):
                        Inventario.objects.get_or_create(
                            insumo=insumo,
                            sucursal=sucursal,
                            defaults={'cantidad_actual': 0}
                        )
                print("   ✅ Inventarios recreados")
        else:
            print("   ℹ️  Limpieza cancelada por el usuario")
    
    print("\n🔍 === FIN DEL DIAGNÓSTICO ===")

if __name__ == "__main__":
    main()
