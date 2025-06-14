#!/usr/bin/env python
"""
Script para crear un usuario admin para probar el sistema
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Sucursal, Rol

User = get_user_model()

def crear_usuario_admin():
    """Crear usuario admin para probar el sistema"""
    print("👤 Creando usuario admin para pruebas...")
    
    # Crear rol admin si no existe
    rol_admin, created = Rol.objects.get_or_create(
        nombre='admin',
        defaults={
            'descripcion': 'Administrador del sistema',
            'permisos': ['all']
        }
    )
    
    if created:
        print("   ✅ Rol admin creado")
    else:
        print("   ⏩ Rol admin ya existe")
    
    # Crear sucursal principal si no existe
    sucursal_principal, created = Sucursal.objects.get_or_create(
        nombre='Principal',
        defaults={
            'direccion': 'Dirección Principal',
            'telefono': '123-456-7890',
            'activa': True
        }
    )
    
    if created:
        print("   ✅ Sucursal principal creada")
    else:
        print("   ⏩ Sucursal principal ya existe")
    
    # Crear usuario admin
    username = 'admin'
    password = 'admin123'
    email = 'admin@sushi.com'
    
    try:
        # Verificar si ya existe
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            print(f"   ⏩ Usuario '{username}' ya existe")
        else:
            # Crear nuevo usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='Admin',
                last_name='Sistema',
                sucursal=sucursal_principal,
                rol=rol_admin,
                activo=True
            )
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print(f"   ✅ Usuario '{username}' creado exitosamente")
        
        print(f"\n🎯 Credenciales de acceso:")
        print(f"   👤 Usuario: {username}")
        print(f"   🔑 Contraseña: {password}")
        print(f"   🌐 URL: http://127.0.0.1:8000/dashboard/login/")
        print(f"   🍣 Insumos elaborados: http://127.0.0.1:8000/dashboard/insumos-elaborados/")
        
        print(f"\n📋 Instrucciones:")
        print(f"   1. Ve a http://127.0.0.1:8000/dashboard/login/")
        print(f"   2. Inicia sesión con las credenciales de arriba")
        print(f"   3. Navega a 'Insumos Elaborados'")
        print(f"   4. Prueba crear un nuevo insumo elaborado")
        
        return user
        
    except Exception as e:
        print(f"   ❌ Error creando usuario: {e}")
        return None

if __name__ == '__main__':
    crear_usuario_admin()
