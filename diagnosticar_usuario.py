#!/usr/bin/env python
"""
Script para diagnosticar el usuario actual y su sucursal asignada
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario, Sucursal
from restaurant.models import Inventario

def main():
    print("👤 === DIAGNÓSTICO DEL USUARIO Y SUCURSALES ===\n")
      # 1. Verificar usuarios existentes
    print("1️⃣ USUARIOS EXISTENTES:")
    usuarios = Usuario.objects.all()
    print(f"   📊 Total de usuarios: {usuarios.count()}")
    
    for usuario in usuarios:
        sucursal = getattr(usuario, 'sucursal', None)
        print(f"   👤 {usuario.username:15s} | Superuser: {str(usuario.is_superuser):5s} | Sucursal: {sucursal.nombre if sucursal else 'Sin asignar'}")
    
    print()
    
    # 2. Verificar sucursales
    print("2️⃣ SUCURSALES EXISTENTES:")
    sucursales = Sucursal.objects.all()
    print(f"   📊 Total de sucursales: {sucursales.count()}")
    
    for sucursal in sucursales:
        inventarios_en_sucursal = Inventario.objects.filter(sucursal=sucursal).count()
        usuarios_en_sucursal = Usuario.objects.filter(sucursal=sucursal).count()
        print(f"   🏢 {sucursal.nombre:20s} | Activa: {str(sucursal.activa):5s} | Inventarios: {inventarios_en_sucursal:2d} | Usuarios: {usuarios_en_sucursal}")
    
    print()
    
    # 3. Simular la vista del inventario para cada usuario
    print("3️⃣ SIMULACIÓN DE LA VISTA DEL INVENTARIO:")
    for usuario in usuarios:
        sucursal = getattr(usuario, 'sucursal', None)
        
        if sucursal:
            inventarios = Inventario.objects.filter(sucursal=sucursal)
            print(f"   👤 Usuario '{usuario.username}' (Sucursal: {sucursal.nombre}) ve: {inventarios.count()} inventarios")
        else:
            inventarios = Inventario.objects.all()
            print(f"   👤 Usuario '{usuario.username}' (Sin sucursal) ve: {inventarios.count()} inventarios")
        
        # Mostrar algunos inventarios para este usuario
        if inventarios.exists():
            print(f"      📋 Primeros 3 inventarios que ve:")
            for i, inv in enumerate(inventarios[:3], 1):
                print(f"         {i}. {inv.insumo.nombre} en {inv.sucursal.nombre}: {inv.cantidad_actual}")
        else:
            print(f"      ❌ No ve ningún inventario")
    
    print()
      # 4. Recomendaciones
    print("4️⃣ RECOMENDACIONES:")
    usuarios_sin_sucursal = Usuario.objects.filter(sucursal__isnull=True)
    if usuarios_sin_sucursal.exists():
        print("   ✅ Usuarios sin sucursal asignada (ven TODOS los inventarios):")
        for usuario in usuarios_sin_sucursal:
            print(f"      - {usuario.username}")
        print("   💡 Usa uno de estos usuarios para ver todos los inventarios")
    else:
        print("   ⚠️  Todos los usuarios tienen sucursal asignada")
        print("   💡 Recomendación: Crear un usuario administrador sin sucursal")
    
    print("\n👤 === FIN DEL DIAGNÓSTICO ===")

if __name__ == "__main__":
    main()
