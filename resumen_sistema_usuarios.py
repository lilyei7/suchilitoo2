#!/usr/bin/env python
"""
Script para generar un resumen del sistema de usuarios
"""
import os
import sys
import django
from datetime import datetime

# Configurar el entorno de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario, Sucursal, Rol

def generar_resumen():
    """Generar un resumen del sistema de usuarios"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("=" * 60)
    print(f"RESUMEN DEL SISTEMA DE USUARIOS - {now}")
    print("=" * 60)
    
    # Resumen de usuarios
    total_usuarios = Usuario.objects.count()
    usuarios_activos = Usuario.objects.filter(is_active=True).count()
    usuarios_inactivos = total_usuarios - usuarios_activos
    superusers = Usuario.objects.filter(is_superuser=True).count()
    
    print(f"\n📊 USUARIOS:")
    print(f"  Total de usuarios: {total_usuarios}")
    print(f"  Usuarios activos: {usuarios_activos}")
    print(f"  Usuarios inactivos: {usuarios_inactivos}")
    print(f"  Superusuarios: {superusers}")
    
    # Distribución por roles
    print("\n📊 DISTRIBUCIÓN POR ROLES:")
    roles = Rol.objects.all()
    for rol in roles:
        usuarios_rol = Usuario.objects.filter(rol=rol).count()
        print(f"  {rol.get_nombre_display()}: {usuarios_rol} usuarios")
    
    # Usuarios sin rol
    usuarios_sin_rol = Usuario.objects.filter(rol__isnull=True).count()
    print(f"  Sin rol asignado: {usuarios_sin_rol} usuarios")
    
    # Distribución por sucursales
    print("\n📊 DISTRIBUCIÓN POR SUCURSALES:")
    sucursales = Sucursal.objects.all()
    for sucursal in sucursales:
        usuarios_sucursal = Usuario.objects.filter(sucursal=sucursal).count()
        print(f"  {sucursal.nombre}: {usuarios_sucursal} usuarios")
    
    # Usuarios sin sucursal
    usuarios_sin_sucursal = Usuario.objects.filter(sucursal__isnull=True).count()
    print(f"  Sin sucursal asignada: {usuarios_sin_sucursal} usuarios")
    
    # Resumen de roles
    print("\n📊 ROLES DEL SISTEMA:")
    roles_total = Rol.objects.count()
    roles_activos = Rol.objects.filter(activo=True).count()
    print(f"  Total de roles: {roles_total}")
    print(f"  Roles activos: {roles_activos}")
    
    for rol in roles:
        print(f"  - {rol.get_nombre_display()} (ID: {rol.id}): {'✓ Activo' if rol.activo else '✗ Inactivo'}")
    
    # Resumen de sucursales
    print("\n📊 SUCURSALES DEL SISTEMA:")
    sucursales_total = Sucursal.objects.count()
    sucursales_activas = Sucursal.objects.filter(activa=True).count()
    print(f"  Total de sucursales: {sucursales_total}")
    print(f"  Sucursales activas: {sucursales_activas}")
    
    for sucursal in sucursales:
        print(f"  - {sucursal.nombre} (ID: {sucursal.id}): {'✓ Activa' if sucursal.activa else '✗ Inactiva'}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    generar_resumen()
