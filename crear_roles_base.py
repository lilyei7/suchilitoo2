#!/usr/bin/env python
"""
Script para crear roles básicos en el sistema
"""
import os
import sys
import django

# Configurar el entorno de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Rol
from django.db import transaction

def crear_roles_base():
    """Crear roles básicos si no existen"""
    roles_base = [
        {
            'nombre': 'admin',
            'descripcion': 'Administrador del sistema con acceso completo a todas las funcionalidades',
            'permisos': {'admin': True, 'dashboard': True, 'inventario': True, 'usuarios': True}
        },
        {
            'nombre': 'gerente',
            'descripcion': 'Gerente con acceso a la mayoría de funcionalidades, excepto configuraciones críticas',
            'permisos': {'dashboard': True, 'inventario': True, 'usuarios': True}
        },
        {
            'nombre': 'supervisor',
            'descripcion': 'Supervisor con acceso a inventario y operaciones diarias',
            'permisos': {'dashboard': True, 'inventario': True}
        },
        {
            'nombre': 'cajero',
            'descripcion': 'Cajero con acceso a ventas y operaciones de caja',
            'permisos': {'dashboard': True, 'ventas': True}
        },
        {
            'nombre': 'cocinero',
            'descripcion': 'Cocinero con acceso a recetas e inventario básico',
            'permisos': {'dashboard': True, 'recetas': True}
        },
        {
            'nombre': 'mesero',
            'descripcion': 'Mesero con acceso a toma de pedidos',
            'permisos': {'dashboard': True, 'pedidos': True}
        },
        {
            'nombre': 'inventario',
            'descripcion': 'Encargado de inventario con acceso a gestión de stock',
            'permisos': {'dashboard': True, 'inventario': True}
        },
        {
            'nombre': 'rrhh',
            'descripcion': 'Recursos Humanos con acceso a gestión de personal',
            'permisos': {'dashboard': True, 'usuarios': True}
        }
    ]
    
    created = 0
    updated = 0
    
    with transaction.atomic():
        for rol_data in roles_base:
            rol, created_now = Rol.objects.update_or_create(
                nombre=rol_data['nombre'],
                defaults={
                    'descripcion': rol_data['descripcion'],
                    'permisos': rol_data['permisos'],
                    'activo': True
                }
            )
            
            if created_now:
                created += 1
                print(f"✅ Rol creado: {rol.get_nombre_display()}")
            else:
                updated += 1
                print(f"🔄 Rol actualizado: {rol.get_nombre_display()}")
    
    return created, updated

if __name__ == "__main__":
    print("Creando roles básicos del sistema...")
    created, updated = crear_roles_base()
    print(f"\nProceso completado: {created} roles creados, {updated} roles actualizados")
    
    # Mostrar todos los roles activos
    print("\nRoles disponibles en el sistema:")
    roles = Rol.objects.filter(activo=True)
    for rol in roles:
        print(f"- {rol.get_nombre_display()} (ID: {rol.id})")
