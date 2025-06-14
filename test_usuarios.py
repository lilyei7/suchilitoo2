#!/usr/bin/env python
"""
Script para probar la funcionalidad CRUD de usuarios.
Crea usuarios de prueba con diferentes roles y sucursales.
"""

import os
import sys
import django
import random
from datetime import date, timedelta

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from accounts.models import Usuario, Rol, Sucursal

def crear_usuarios_prueba():
    print("🧪 Iniciando creación de usuarios de prueba...")
    
    # Verificar que existan roles
    if Rol.objects.count() == 0:
        print("❌ No hay roles creados. Creando roles por defecto...")
        crear_roles_defecto()
    
    # Verificar que existan sucursales
    if Sucursal.objects.count() == 0:
        print("❌ No hay sucursales creadas. Creando sucursal por defecto...")
        crear_sucursal_defecto()
    
    # Obtener roles y sucursales
    roles = list(Rol.objects.all())
    sucursales = list(Sucursal.objects.all())
    
    # Datos de prueba
    usuarios_prueba = [
        {
            'username': 'admin',
            'email': 'admin@sushirestaurant.com',
            'first_name': 'Administrador',
            'last_name': 'Sistema',
            'password': 'admin123',
            'is_superuser': True,
            'is_staff': True,
            'telefono': '555-000-0000',
            'cedula': '0000000001'
        },
        {
            'username': 'gerente',
            'email': 'gerente@sushirestaurant.com',
            'first_name': 'Gerente',
            'last_name': 'Principal',
            'password': 'gerente123',
            'rol': next((r for r in roles if r.nombre == 'gerente'), None),
            'telefono': '555-111-1111',
            'cedula': '0000000002'
        },
        {
            'username': 'supervisor',
            'email': 'supervisor@sushirestaurant.com',
            'first_name': 'Supervisor',
            'last_name': 'Control',
            'password': 'supervisor123',
            'rol': next((r for r in roles if r.nombre == 'supervisor'), None),
            'telefono': '555-222-2222',
            'cedula': '0000000003'
        },
        {
            'username': 'cajero',
            'email': 'cajero@sushirestaurant.com',
            'first_name': 'Cajero',
            'last_name': 'Ventas',
            'password': 'cajero123',
            'rol': next((r for r in roles if r.nombre == 'cajero'), None),
            'telefono': '555-333-3333',
            'cedula': '0000000004'
        },
        {
            'username': 'cocinero',
            'email': 'cocinero@sushirestaurant.com',
            'first_name': 'Cocinero',
            'last_name': 'Chef',
            'password': 'cocinero123',
            'rol': next((r for r in roles if r.nombre == 'cocinero'), None),
            'telefono': '555-444-4444',
            'cedula': '0000000005'
        }
    ]
    
    # Crear usuarios
    usuarios_creados = 0
    for datos in usuarios_prueba:
        # Asignar sucursal aleatoria excepto para admin
        if 'is_superuser' not in datos or not datos['is_superuser']:
            datos['sucursal'] = random.choice(sucursales)
        
        # Verificar si ya existe
        if Usuario.objects.filter(username=datos['username']).exists():
            print(f"ℹ️ El usuario '{datos['username']}' ya existe.")
            continue
        
        # Crear usuario
        try:
            password = datos.pop('password')
            usuario = Usuario(
                **datos,
                password=make_password(password),
                fecha_ingreso=date.today() - timedelta(days=random.randint(1, 365)),
                salario=random.randint(50, 150) * 100
            )
            usuario.save()
            usuarios_creados += 1
            print(f"✅ Usuario '{usuario.username}' creado exitosamente.")
        except Exception as e:
            print(f"❌ Error al crear usuario '{datos['username']}': {e}")
    
    return usuarios_creados

def crear_roles_defecto():
    """Crea los roles básicos del sistema si no existen"""
    roles_default = [
        ('admin', 'Administrador del sistema'),
        ('gerente', 'Gerente de sucursal'),
        ('supervisor', 'Supervisor de operaciones'),
        ('cajero', 'Cajero/a'),
        ('cocinero', 'Cocinero/Chef'),
        ('mesero', 'Mesero/a'),
        ('inventario', 'Encargado de inventario'),
        ('rrhh', 'Recursos Humanos')
    ]
    
    roles_creados = 0
    for nombre, descripcion in roles_default:
        if not Rol.objects.filter(nombre=nombre).exists():
            Rol.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                permisos={'admin': True} if nombre == 'admin' else {}
            )
            roles_creados += 1
            print(f"✅ Rol '{nombre}' creado.")
    
    return roles_creados

def crear_sucursal_defecto():
    """Crea una sucursal de prueba si no existe ninguna"""
    if not Sucursal.objects.exists():
        Sucursal.objects.create(
            nombre="Sucursal Principal",
            direccion="Av. Principal #123, Ciudad",
            telefono="555-123-4567",
            email="sucursal@sushirestaurant.com",
            fecha_apertura=date.today() - timedelta(days=365)
        )
        print("✅ Sucursal Principal creada.")
        return 1
    return 0

if __name__ == "__main__":
    try:
        # Ejecutar función principal
        total_usuarios = crear_usuarios_prueba()
        
        # Mostrar resumen
        print(f"\n✅ Proceso completado. {total_usuarios} usuarios creados.")
        print(f"📊 Total de usuarios en el sistema: {Usuario.objects.count()}")
        print(f"📊 Total de roles en el sistema: {Rol.objects.count()}")
        print(f"📊 Total de sucursales en el sistema: {Sucursal.objects.count()}")
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        sys.exit(1)
