#!/usr/bin/env python
"""
Script para reconstruir la base de datos del sistema desde cero.
Este script crea:
1. Migraciones iniciales
2. Superusuario administrador
3. Roles básicos
4. Sucursales de ejemplo
5. Usuarios de ejemplo
6. Otros datos básicos necesarios para el funcionamiento

Ejecutar después de borrar la base de datos sqlite.
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
from django.db import transaction
from django.core.management import call_command
from accounts.models import Usuario, Rol, Sucursal

def ejecutar_migraciones():
    """Ejecuta las migraciones de Django para crear las tablas en la DB"""
    print("\n\n🔄 EJECUTANDO MIGRACIONES...")
    call_command('makemigrations')
    call_command('migrate')
    print("✅ Migraciones completadas.\n")

def crear_superusuario():
    """Crea un superusuario administrador"""
    print("\n\n🔐 CREANDO SUPERUSUARIO...")
    try:
        if not Usuario.objects.filter(username='admin').exists():
            superuser = Usuario.objects.create_superuser(
                username='admin',
                email='admin@sushirestaurant.com',
                password='admin123456',
                first_name='Administrador',
                last_name='Sistema',
                is_active=True
            )
            print(f"✅ Superusuario creado: {superuser.username} (contraseña: admin123456)")
        else:
            print("ℹ️ El superusuario 'admin' ya existe.")
    except Exception as e:
        print(f"❌ Error al crear superusuario: {e}")

def crear_roles_basicos():
    """Crea los roles básicos del sistema"""
    print("\n\n👥 CREANDO ROLES BÁSICOS...")
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
    
    roles_creados = 0
    for rol_data in roles_base:
        try:
            rol, created = Rol.objects.get_or_create(
                nombre=rol_data['nombre'],
                defaults={
                    'descripcion': rol_data['descripcion'],
                    'permisos': rol_data['permisos'],
                    'activo': True
                }
            )
            if created:
                roles_creados += 1
                print(f"✅ Rol creado: {rol.get_nombre_display()}")
            else:
                print(f"ℹ️ El rol '{rol.get_nombre_display()}' ya existe.")
        except Exception as e:
            print(f"❌ Error al crear rol '{rol_data['nombre']}': {e}")
    
    print(f"✅ {roles_creados} roles creados.")

def crear_sucursales_ejemplo():
    """Crea sucursales de ejemplo"""
    print("\n\n🏢 CREANDO SUCURSALES DE EJEMPLO...")
    sucursales_ejemplo = [
        {
            'nombre': 'Sushi Central',
            'direccion': 'Av. Principal #123, Centro Comercial Plaza Mayor',
            'telefono': '555-123-4567',
            'email': 'central@sushirestaurant.com',
            'fecha_apertura': date.today() - timedelta(days=365*2)
        },
        {
            'nombre': 'Sushi Plaza',
            'direccion': 'Calle Comercio #456, Zona Norte',
            'telefono': '555-234-5678',
            'email': 'plaza@sushirestaurant.com',
            'fecha_apertura': date.today() - timedelta(days=365)
        },
        {
            'nombre': 'Sushi Express',
            'direccion': 'Av. Libertad #789, Centro Comercial Express',
            'telefono': '555-345-6789',
            'email': 'express@sushirestaurant.com',
            'fecha_apertura': date.today() - timedelta(days=180)
        }
    ]
    
    sucursales_creadas = 0
    for sucursal_data in sucursales_ejemplo:
        try:
            sucursal, created = Sucursal.objects.get_or_create(
                nombre=sucursal_data['nombre'],
                defaults={
                    'direccion': sucursal_data['direccion'],
                    'telefono': sucursal_data['telefono'],
                    'email': sucursal_data['email'],
                    'fecha_apertura': sucursal_data['fecha_apertura'],
                    'activa': True
                }
            )
            if created:
                sucursales_creadas += 1
                print(f"✅ Sucursal creada: {sucursal.nombre}")
            else:
                print(f"ℹ️ La sucursal '{sucursal.nombre}' ya existe.")
        except Exception as e:
            print(f"❌ Error al crear sucursal '{sucursal_data['nombre']}': {e}")
    
    print(f"✅ {sucursales_creadas} sucursales creadas.")

def crear_usuarios_ejemplo():
    """Crea usuarios de ejemplo con diferentes roles"""
    print("\n\n👤 CREANDO USUARIOS DE EJEMPLO...")
    
    # Verificar que existan roles y sucursales
    if Rol.objects.count() == 0:
        print("❌ No hay roles disponibles. Ejecutando creación de roles...")
        crear_roles_basicos()
    
    if Sucursal.objects.count() == 0:
        print("❌ No hay sucursales disponibles. Ejecutando creación de sucursales...")
        crear_sucursales_ejemplo()
    
    # Obtener roles y sucursales
    roles = list(Rol.objects.all())
    sucursales = list(Sucursal.objects.all())
    
    # Datos de ejemplo
    usuarios_ejemplo = [
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
        },
        {
            'username': 'mesero',
            'email': 'mesero@sushirestaurant.com',
            'first_name': 'Mesero',
            'last_name': 'Servicio',
            'password': 'mesero123',
            'rol': next((r for r in roles if r.nombre == 'mesero'), None),
            'telefono': '555-555-5555',
            'cedula': '0000000006'
        }
    ]
    
    usuarios_creados = 0
    for datos in usuarios_ejemplo:
        try:
            # Asignar sucursal aleatoria
            datos['sucursal'] = random.choice(sucursales)
            
            # Verificar si ya existe
            if Usuario.objects.filter(username=datos['username']).exists():
                print(f"ℹ️ El usuario '{datos['username']}' ya existe.")
                continue
            
            # Crear usuario
            password = datos.pop('password')
            usuario = Usuario(
                **datos,
                password=make_password(password),
                fecha_ingreso=date.today() - timedelta(days=random.randint(1, 365)),
                is_active=True
            )
            usuario.save()
            usuarios_creados += 1
            print(f"✅ Usuario creado: {usuario.username} ({usuario.get_full_name()})")
        except Exception as e:
            print(f"❌ Error al crear usuario '{datos['username']}': {e}")
    
    print(f"✅ {usuarios_creados} usuarios creados.")

def verificar_instalacion():
    """Verifica que la instalación esté completa y funcional"""
    print("\n\n🔍 VERIFICANDO INSTALACIÓN...")
    
    # Verificar superusuario
    superusers = Usuario.objects.filter(is_superuser=True).count()
    print(f"✅ Superusuarios: {superusers}")
    
    # Verificar roles
    roles = Rol.objects.filter(activo=True).count()
    print(f"✅ Roles activos: {roles}")
    
    # Verificar sucursales
    sucursales = Sucursal.objects.filter(activa=True).count()
    print(f"✅ Sucursales activas: {sucursales}")
    
    # Verificar usuarios
    usuarios = Usuario.objects.filter(is_active=True).count()
    print(f"✅ Usuarios activos: {usuarios}")
    
    # Mostrar credenciales
    print("\n🔐 CREDENCIALES DE ACCESO:")
    print("┌───────────────┬─────────────────────┬───────────────┐")
    print("│ Usuario       │ Contraseña          │ Rol           │")
    print("├───────────────┼─────────────────────┼───────────────┤")
    print("│ admin         │ admin123456         │ Superusuario  │")
    print("│ gerente       │ gerente123          │ Gerente       │")
    print("│ supervisor    │ supervisor123       │ Supervisor    │")
    print("│ cajero        │ cajero123           │ Cajero        │")
    print("│ cocinero      │ cocinero123         │ Cocinero      │")
    print("│ mesero        │ mesero123           │ Mesero        │")
    print("└───────────────┴─────────────────────┴───────────────┘")

def importar_datos_adicionales():
    """
    Importa datos adicionales necesarios para el sistema
    (categorías, unidades de medida, etc.)
    """
    # Esta función puede llamar a otros scripts que necesites
    pass

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 INICIALIZANDO SISTEMA SUSHI RESTAURANT")
    print("=" * 80)
    
    try:
        # Ejecutar todos los pasos en orden
        with transaction.atomic():
            ejecutar_migraciones()
            crear_superusuario()
            crear_roles_basicos()
            crear_sucursales_ejemplo()
            crear_usuarios_ejemplo()
            importar_datos_adicionales()  # Si hay más datos básicos necesarios
        
        # Verificar la instalación
        verificar_instalacion()
        
        print("\n" + "=" * 80)
        print("✅ SISTEMA INICIALIZADO CORRECTAMENTE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA INICIALIZACIÓN: {e}")
        print("\nPor favor, verifica los mensajes de error e intenta nuevamente.")
        sys.exit(1)
