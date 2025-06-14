#!/usr/bin/env python
"""
Script para verificar y corregir problemas en los selects de roles de usuario
"""
import os
import sys
import django

# Configurar el entorno de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Rol
from django.utils.translation import gettext as _

def verificar_roles():
    """Verificar el estado de los roles en el sistema"""
    print("=== Verificación de Roles ===")
    
    # Contar roles
    total_roles = Rol.objects.count()
    roles_activos = Rol.objects.filter(activo=True).count()
    
    print(f"Total de roles en la base de datos: {total_roles}")
    print(f"Roles activos: {roles_activos}")
    
    # Listar todos los roles
    print("\nListado completo de roles:")
    print(f"{'ID':<5} {'Nombre':<15} {'Nombre mostrado':<20} {'Activo':<10}")
    print("-" * 50)
    
    for rol in Rol.objects.all().order_by('id'):
        nombre_mostrado = rol.get_nombre_display()
        print(f"{rol.id:<5} {rol.nombre:<15} {nombre_mostrado:<20} {'✓' if rol.activo else '✗'}")
    
    # Verificar si hay algún problema
    if total_roles == 0:
        print("\n❌ No hay roles definidos en el sistema.")
    elif roles_activos == 0:
        print("\n❌ No hay roles activos en el sistema.")
    
    return total_roles, roles_activos

def corregir_roles_inactivos():
    """Activar roles inactivos"""
    roles_inactivos = Rol.objects.filter(activo=False)
    
    if roles_inactivos.exists():
        print(f"\nActivando {roles_inactivos.count()} roles inactivos...")
        for rol in roles_inactivos:
            rol.activo = True
            rol.save()
            print(f"✅ Rol activado: {rol.get_nombre_display()}")
        return True
    else:
        print("\nNo hay roles inactivos que corregir.")
        return False

if __name__ == "__main__":
    print("Verificando roles del sistema...")
    total_roles, roles_activos = verificar_roles()
    
    if roles_activos < total_roles:
        respuesta = input("\n¿Desea activar los roles inactivos? (s/n): ")
        if respuesta.lower() == 's':
            corregir_roles_inactivos()
            print("\nVerificación después de la corrección:")
            verificar_roles()
    
    print("\n=== Verificación completada ===")
