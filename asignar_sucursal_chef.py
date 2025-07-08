#!/usr/bin/env python
"""
Script para asignar una sucursal a un usuario de cocina
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Sucursal, Rol

User = get_user_model()

def asignar_sucursal_chef():
    """Asignar sucursal a un usuario de cocina"""
    print("=== ASIGNACIÓN DE SUCURSAL AL CHEF ===")
    
    # Listar usuarios activos
    usuarios = User.objects.filter(is_active=True)
    
    if not usuarios.exists():
        print("❌ No hay usuarios activos")
        return
    
    print("\nUsuarios disponibles:")
    for i, user in enumerate(usuarios, 1):
        sucursal_info = f" - Sucursal: {user.sucursal.nombre}" if user.sucursal else " - Sin sucursal"
        rol_info = f" - Rol: {user.rol}" if user.rol else " - Sin rol"
        print(f"{i}. {user.username} ({user.first_name or 'Sin nombre'}){sucursal_info}{rol_info}")
    
    # Seleccionar usuario
    try:
        opcion = int(input(f"\nSelecciona un usuario (1-{len(usuarios)}): "))
        if opcion < 1 or opcion > len(usuarios):
            print("❌ Opción inválida")
            return
        
        usuario_seleccionado = usuarios[opcion - 1]
        
    except ValueError:
        print("❌ Debe ingresar un número")
        return
    
    # Listar sucursales disponibles
    sucursales = Sucursal.objects.filter(activa=True)
    
    if not sucursales.exists():
        print("❌ No hay sucursales activas. Creando sucursal por defecto...")
        sucursal = Sucursal.objects.create(
            nombre="Sucursal Centro",
            direccion="Av. Principal 123",
            telefono="555-1234",
            email="centro@sushi.com",
            fecha_apertura="2025-01-01"
        )
        print(f"✅ Sucursal '{sucursal.nombre}' creada")
        sucursales = [sucursal]
    
    print("\nSucursales disponibles:")
    for i, sucursal in enumerate(sucursales, 1):
        print(f"{i}. {sucursal.nombre} - {sucursal.direccion}")
    
    # Seleccionar sucursal
    try:
        opcion_sucursal = int(input(f"\nSelecciona una sucursal (1-{len(sucursales)}): "))
        if opcion_sucursal < 1 or opcion_sucursal > len(sucursales):
            print("❌ Opción inválida")
            return
        
        sucursal_seleccionada = sucursales[opcion_sucursal - 1]
        
    except ValueError:
        print("❌ Debe ingresar un número")
        return
    
    # Asignar sucursal y rol si no lo tiene
    usuario_seleccionado.sucursal = sucursal_seleccionada
    
    # Asignar rol de cocinero si no tiene rol
    if not usuario_seleccionado.rol:
        rol_cocinero, created = Rol.objects.get_or_create(
            nombre='cocinero',
            defaults={
                'descripcion': 'Personal de cocina encargado de preparar órdenes',
                'activo': True
            }
        )
        usuario_seleccionado.rol = rol_cocinero
        if created:
            print(f"✅ Rol 'Cocinero' creado")
    
    usuario_seleccionado.save()
    
    print(f"\n✅ ASIGNACIÓN COMPLETADA")
    print(f"Usuario: {usuario_seleccionado.first_name or usuario_seleccionado.username}")
    print(f"Sucursal: {usuario_seleccionado.sucursal.nombre}")
    print(f"Rol: {usuario_seleccionado.rol}")
    
    print(f"\n🌐 Ahora cuando accedas al dashboard de cocina verás:")
    print(f"   - Nombre: {usuario_seleccionado.first_name or usuario_seleccionado.username}")
    print(f"   - Sucursal: {usuario_seleccionado.sucursal.nombre}")
    print(f"   - En la esquina superior derecha de la navegación")

if __name__ == '__main__':
    try:
        asignar_sucursal_chef()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
