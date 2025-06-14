#!/usr/bin/env python
"""
Script para verificar y asegurar que los roles básicos existan en el sistema.
Este script debe ejecutarse cuando se inicia el sistema por primera vez o
cuando se restaura la base de datos.
"""

import os
import sys
import django

# Configurar el entorno de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Rol

def verificar_y_crear_roles_basicos():
    """Verifica que existan los roles básicos y los crea si no existen"""
    
    # Definir roles básicos que deben existir
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
    
    roles_creados = 0
    roles_existentes = 0
    roles_activados = 0
    
    for rol_info in roles_basicos:
        rol, created = Rol.objects.get_or_create(
            nombre=rol_info['nombre'],
            defaults={
                'descripcion': rol_info['descripcion'],
                'activo': True
            }
        )
        
        if created:
            print(f"✅ Rol '{rol.nombre}' creado exitosamente")
            roles_creados += 1
        else:
            print(f"ℹ️ Rol '{rol.nombre}' ya existe")
            roles_existentes += 1
            
            # Si el rol existe pero está inactivo, activarlo
            if not rol.activo:
                rol.activo = True
                rol.save()
                print(f"🔄 Rol '{rol.nombre}' reactivado")
                roles_activados += 1
    
    # Resumen
    print("\n=== RESUMEN DE ROLES ===")
    print(f"✅ Roles creados: {roles_creados}")
    print(f"ℹ️ Roles existentes: {roles_existentes}")
    print(f"🔄 Roles reactivados: {roles_activados}")
    print(f"📊 Total roles básicos: {len(roles_basicos)}")
    
    # Verificar roles activos en el sistema
    roles_activos = Rol.objects.filter(activo=True).count()
    print(f"🟢 Roles activos en el sistema: {roles_activos}")
    
    return roles_creados + roles_activados > 0

if __name__ == "__main__":
    print("=== VERIFICACIÓN DE ROLES BÁSICOS ===")
    cambios = verificar_y_crear_roles_basicos()
    
    if cambios:
        print("\n✅ Se realizaron cambios en los roles del sistema")
    else:
        print("\n✅ Todos los roles básicos están correctamente configurados")
