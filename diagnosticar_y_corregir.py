#!/usr/bin/env python
"""
Script para diagnosticar y corregir problemas de sucursales e inventarios
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario, Sucursal
from restaurant.models import Insumo, Inventario

def main():
    print("🔍 === DIAGNÓSTICO COMPLETO DE SUCURSALES E INVENTARIOS ===\n")
    
    # 1. Verificar usuario actual (jhayco)
    print("1️⃣ VERIFICANDO USUARIO ACTUAL:")
    try:
        usuario = Usuario.objects.get(username='jhayco')
        print(f"   👤 Usuario encontrado: {usuario.username}")
        print(f"   📧 Email: {usuario.email}")
        print(f"   🏢 Sucursal asignada: {usuario.sucursal.nombre if usuario.sucursal else 'SIN ASIGNAR'}")
        print(f"   👑 Es superusuario: {usuario.is_superuser}")
        print(f"   🔧 Rol: {usuario.rol.nombre if usuario.rol else 'Sin rol'}")
    except Usuario.DoesNotExist:
        print("   ❌ Usuario 'jhayco' no encontrado")
        return
    
    print()
    
    # 2. Verificar sucursales existentes
    print("2️⃣ VERIFICANDO SUCURSALES:")
    sucursales = Sucursal.objects.all()
    print(f"   📊 Total de sucursales: {sucursales.count()}")
    
    for sucursal in sucursales:
        inventarios_en_sucursal = Inventario.objects.filter(sucursal=sucursal).count()
        usuarios_en_sucursal = Usuario.objects.filter(sucursal=sucursal).count()
        print(f"   🏢 {sucursal.nombre:20s} | Activa: {sucursal.activa} | Inventarios: {inventarios_en_sucursal:2d} | Usuarios: {usuarios_en_sucursal}")
    
    print()
    
    # 3. Verificar insumos sin inventario
    print("3️⃣ VERIFICANDO INSUMOS SIN INVENTARIO:")
    total_insumos = Insumo.objects.count()
    total_inventarios = Inventario.objects.count()
    total_sucursales = Sucursal.objects.filter(activa=True).count()
    
    print(f"   📊 Total insumos: {total_insumos}")
    print(f"   📊 Total inventarios: {total_inventarios}")
    print(f"   📊 Total sucursales activas: {total_sucursales}")
    print(f"   📊 Inventarios esperados: {total_insumos * total_sucursales}")
    
    # Encontrar insumos sin inventario
    insumos_sin_inventario = []
    for insumo in Insumo.objects.all():
        inventarios_del_insumo = Inventario.objects.filter(insumo=insumo).count()
        if inventarios_del_insumo < total_sucursales:
            insumos_sin_inventario.append({
                'insumo': insumo,
                'inventarios_actuales': inventarios_del_insumo,
                'inventarios_faltantes': total_sucursales - inventarios_del_insumo
            })
    
    if insumos_sin_inventario:
        print(f"   ⚠️  INSUMOS CON INVENTARIOS INCOMPLETOS: {len(insumos_sin_inventario)}")
        for item in insumos_sin_inventario[:10]:  # Mostrar solo los primeros 10
            insumo = item['insumo']
            print(f"      - {insumo.nombre} ({insumo.codigo}): {item['inventarios_actuales']}/{total_sucursales} inventarios")
    else:
        print("   ✅ Todos los insumos tienen inventarios completos")
    
    print()
    
    # 4. Verificar qué ve el usuario actual
    print("4️⃣ SIMULANDO LO QUE VE EL USUARIO EN LA PÁGINA:")
    if usuario.sucursal:
        inventarios_visibles = Inventario.objects.filter(sucursal=usuario.sucursal)
        print(f"   👤 Usuario con sucursal '{usuario.sucursal.nombre}' ve: {inventarios_visibles.count()} inventarios")
    else:
        inventarios_visibles = Inventario.objects.all()
        print(f"   👤 Usuario SIN sucursal ve: {inventarios_visibles.count()} inventarios (TODOS)")
    
    # Mostrar algunos ejemplos
    if inventarios_visibles.exists():
        print("   📋 Primeros 5 inventarios visibles:")
        for i, inv in enumerate(inventarios_visibles[:5], 1):
            print(f"      {i}. {inv.insumo.nombre} en {inv.sucursal.nombre}: {inv.cantidad_actual}")
    
    print()
    
    # 5. Verificar últimos insumos creados
    print("5️⃣ VERIFICANDO ÚLTIMOS INSUMOS CREADOS:")
    ultimos_insumos = Insumo.objects.order_by('-id')[:5]
    
    for insumo in ultimos_insumos:
        inventarios_del_insumo = Inventario.objects.filter(insumo=insumo)
        print(f"   📦 {insumo.nombre} ({insumo.codigo}):")
        if inventarios_del_insumo.exists():
            for inv in inventarios_del_insumo:
                print(f"      └─ {inv.sucursal.nombre}: {inv.cantidad_actual}")
        else:
            print(f"      └─ ❌ SIN INVENTARIOS")
    
    print()
    
    # 6. Proponer correcciones
    print("6️⃣ CORRECCIONES SUGERIDAS:")
    
    if insumos_sin_inventario:
        print("   🔧 CORRECCIÓN AUTOMÁTICA: Crear inventarios faltantes")
        print(f"      Se crearán {sum(item['inventarios_faltantes'] for item in insumos_sin_inventario)} registros de inventario")
        
        respuesta = input("   ❓ ¿Deseas crear los inventarios faltantes? (s/n): ").lower().strip()
        
        if respuesta == 's':
            print("   🔄 Creando inventarios faltantes...")
            inventarios_creados = 0
            
            for item in insumos_sin_inventario:
                insumo = item['insumo']
                sucursales_con_inventario = Inventario.objects.filter(insumo=insumo).values_list('sucursal_id', flat=True)
                
                for sucursal in Sucursal.objects.filter(activa=True).exclude(id__in=sucursales_con_inventario):
                    Inventario.objects.create(
                        sucursal=sucursal,
                        insumo=insumo,
                        cantidad_actual=0
                    )
                    inventarios_creados += 1
                    print(f"      ✅ Creado inventario: {insumo.nombre} en {sucursal.nombre}")
            
            print(f"   🎉 ¡Inventarios creados exitosamente! Total: {inventarios_creados}")
        else:
            print("   ℹ️  Corrección cancelada por el usuario")
    
    # 7. Verificar asignación de sucursal al usuario
    if not usuario.sucursal:
        print("   🔧 CORRECCIÓN DE USUARIO: Asignar sucursal")
        print("      El usuario 'jhayco' no tiene sucursal asignada")
        print("      Opciones disponibles:")
        
        for i, sucursal in enumerate(sucursales, 1):
            print(f"         {i}. {sucursal.nombre}")
        print(f"         {len(sucursales) + 1}. Mantener sin sucursal (ve todos los inventarios)")
        
        try:
            opcion = input("   ❓ Selecciona una opción (número): ").strip()
            opcion_num = int(opcion)
            
            if 1 <= opcion_num <= len(sucursales):
                sucursal_elegida = list(sucursales)[opcion_num - 1]
                usuario.sucursal = sucursal_elegida
                usuario.save()
                print(f"   ✅ Usuario asignado a sucursal: {sucursal_elegida.nombre}")
            elif opcion_num == len(sucursales) + 1:
                print("   ℹ️  Usuario mantenido sin sucursal (verá todos los inventarios)")
            else:
                print("   ❌ Opción inválida")
        except ValueError:
            print("   ❌ Opción inválida")
    else:
        print(f"   ✅ Usuario ya tiene sucursal asignada: {usuario.sucursal.nombre}")
    
    print()
    
    # 8. Resumen final
    print("8️⃣ RESUMEN FINAL:")
    inventarios_finales = Inventario.objects.count()
    if usuario.sucursal:
        inventarios_visibles_finales = Inventario.objects.filter(sucursal=usuario.sucursal).count()
        print(f"   📊 Total inventarios en el sistema: {inventarios_finales}")
        print(f"   👁️  Inventarios visibles para usuario '{usuario.username}': {inventarios_visibles_finales}")
    else:
        print(f"   📊 Total inventarios en el sistema: {inventarios_finales}")
        print(f"   👁️  Inventarios visibles para usuario '{usuario.username}': {inventarios_finales} (TODOS)")
    
    print("\n🔍 === FIN DEL DIAGNÓSTICO ===")

if __name__ == "__main__":
    main()
