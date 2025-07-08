#!/usr/bin/env python
"""
Script para crear usuarios de prueba con diferentes roles
Ejecutar: python crear_usuarios_roles.py
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario, Sucursal, Rol

def crear_usuarios_roles():
    print("Creando usuarios con diferentes roles...")
    
    # Obtener sucursal
    try:
        sucursal = Sucursal.objects.get(nombre="Sucursal Principal")
    except Sucursal.DoesNotExist:
        print("❌ No se encontró la Sucursal Principal")
        return
    
    # Crear roles si no existen
    roles_data = [
        {'nombre': 'admin', 'descripcion': 'Administrador del sistema'},
        {'nombre': 'gerente', 'descripcion': 'Gerente del restaurante'},
        {'nombre': 'cajero', 'descripcion': 'Cajero del restaurante'},
    ]
    
    roles = {}
    for rol_data in roles_data:
        rol, created = Rol.objects.get_or_create(
            nombre=rol_data['nombre'],
            defaults={'descripcion': rol_data['descripcion']}
        )
        roles[rol_data['nombre']] = rol
        if created:
            print(f"✓ Rol creado: {rol.get_nombre_display()}")
        else:
            print(f"✓ Rol existente: {rol.get_nombre_display()}")
    
    # Crear usuarios de prueba
    usuarios_data = [
        {
            'username': 'admin1',
            'password': '123456',
            'first_name': 'Carlos',
            'last_name': 'Administrador',
            'email': 'admin@sushi.com',
            'rol': 'admin'
        },
        {
            'username': 'gerente1',
            'password': '123456',
            'first_name': 'María',
            'last_name': 'Gerente',
            'email': 'gerente@sushi.com',
            'rol': 'gerente'
        },
        {
            'username': 'cajero2',
            'password': '123456',
            'first_name': 'Luis',
            'last_name': 'Cajero',
            'email': 'cajero2@sushi.com',
            'rol': 'cajero'
        }
    ]
    
    for user_data in usuarios_data:
        try:
            usuario = Usuario.objects.get(username=user_data['username'])
            print(f"✓ Usuario existente: {usuario.username} ({usuario.rol.get_nombre_display() if usuario.rol else 'Sin rol'})")
        except Usuario.DoesNotExist:
            usuario = Usuario.objects.create_user(
                username=user_data['username'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email'],
                sucursal=sucursal,
                rol=roles[user_data['rol']]
            )
            print(f"✓ Usuario creado: {usuario.username} ({usuario.rol.get_nombre_display()})")
    
    print("\n" + "="*60)
    print("USUARIOS CON ROLES CREADOS EXITOSAMENTE")
    print("="*60)
    print("Todos pueden acceder al app de cajero:")
    print("")
    print("🔑 ADMINISTRADOR:")
    print("   Username: admin1")
    print("   Password: 123456")
    print("   Permisos: Acceso completo + Dashboard admin")
    print("")
    print("👨‍💼 GERENTE:")
    print("   Username: gerente1") 
    print("   Password: 123456")
    print("   Permisos: Acceso completo (excepto admin)")
    print("")
    print("💰 CAJERO ORIGINAL:")
    print("   Username: cajero1")
    print("   Password: 123456")
    print("   Permisos: POS y ventas básicas")
    print("")
    print("💰 CAJERO ADICIONAL:")
    print("   Username: cajero2")
    print("   Password: 123456")
    print("   Permisos: POS y ventas básicas")
    print("")
    print("URL: http://127.0.0.1:8000/cajero/")
    print("="*60)

if __name__ == "__main__":
    crear_usuarios_roles()
