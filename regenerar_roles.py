#!/usr/bin/env python
"""
Script para regenerar todos los roles del sistema.
ADVERTENCIA: Este script eliminará los roles existentes y creará nuevos roles básicos.
Solo debe usarse en caso de problemas graves con los roles.
"""

import os
import sys
import django

# Configurar el entorno de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Rol, Usuario
from django.db import transaction

def regenerar_roles():
    """Elimina todos los roles y crea los roles básicos de nuevo"""
    
    # Roles básicos que se crearán
    roles_basicos = [
        {'nombre': 'admin', 'descripcion': 'Administrador del sistema con acceso completo'},
        {'nombre': 'gerente', 'descripcion': 'Gerente con acceso a gestión y reportes'},
        {'nombre': 'supervisor', 'descripcion': 'Supervisor de operaciones'},
        {'nombre': 'cajero', 'descripcion': 'Cajero para manejo de ventas'},
        {'nombre': 'cocinero', 'descripcion': 'Cocinero para preparación de alimentos'},
        {'nombre': 'mesero', 'descripcion': 'Mesero para atención al cliente'},
        {'nombre': 'inventario', 'descripcion': 'Encargado de inventario'},
        {'nombre': 'rrhh', 'descripcion': 'Recursos Humanos'},
    ]
    
    # Advertencia y confirmación
    print("⚠️ ADVERTENCIA: Este script eliminará TODOS los roles existentes y creará nuevos roles básicos.")
    print("⚠️ Los usuarios perderán su asignación de rol actual.")
    confirmacion = input("¿Está seguro de continuar? (escriba 'SI' para confirmar): ")
    
    if confirmacion != "SI":
        print("❌ Operación cancelada")
        return False
    
    try:
        with transaction.atomic():
            # Contar usuarios actuales con roles
            usuarios_con_rol = Usuario.objects.exclude(rol=None).count()
            print(f"ℹ️ Usuarios con rol asignado actualmente: {usuarios_con_rol}")
            
            # Guardar los roles existentes de los superusuarios para restaurarlos después
            superusuarios = Usuario.objects.filter(is_superuser=True)
            superusuarios_roles = {}
            for user in superusuarios:
                if user.rol:
                    superusuarios_roles[user.id] = user.rol.nombre
            
            # Eliminar todos los roles (esto desvinculará los roles de los usuarios)
            roles_eliminados = Rol.objects.all().delete()
            print(f"🗑️ Roles eliminados: {roles_eliminados}")
            
            # Crear nuevos roles básicos
            roles_creados = []
            for rol_info in roles_basicos:
                rol = Rol.objects.create(
                    nombre=rol_info['nombre'],
                    descripcion=rol_info['descripcion'],
                    activo=True
                )
                roles_creados.append(rol)
                print(f"✅ Rol '{rol.nombre}' creado exitosamente")
            
            # Restaurar el rol 'admin' a los superusuarios
            rol_admin = Rol.objects.get(nombre='admin')
            for user in superusuarios:
                user.rol = rol_admin
                user.save()
                print(f"🔄 Restaurado rol 'admin' al superusuario: {user.username}")
            
            print(f"\n✅ Regeneración completada. {len(roles_creados)} roles básicos creados.")
            return True
            
    except Exception as e:
        print(f"❌ Error durante la regeneración de roles: {e}")
        return False

if __name__ == "__main__":
    print("=== REGENERACIÓN DE ROLES DEL SISTEMA ===")
    resultado = regenerar_roles()
    
    if resultado:
        print("\n✅ Los roles se han regenerado exitosamente.")
        print("ℹ️ Recuerde asignar los roles apropiados a los usuarios del sistema.")
    else:
        print("\n❌ La regeneración de roles fue cancelada o falló.")
