#!/usr/bin/env python
"""
Script para crear un usuario gerente y configurar el rol gerente correctamente.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario, Rol, Sucursal
from dashboard.utils.permissions import DEFAULT_ROLE_PERMISSIONS

def crear_gerente_test():
    """Crea un usuario gerente para pruebas"""
    print("=" * 60)
    print("CREANDO USUARIO GERENTE DE PRUEBA")
    print("=" * 60)
    
    try:
        # Crear o obtener el rol gerente
        rol_gerente, created = Rol.objects.get_or_create(
            nombre='gerente',
            defaults={
                'descripcion': 'Gerente de sucursal con acceso limitado al inventario',
                'permisos': DEFAULT_ROLE_PERMISSIONS['gerente'],
                'activo': True
            }
        )
        
        if created:
            print("✅ Rol 'gerente' creado exitosamente")
        else:
            print("✅ Rol 'gerente' ya existe")
            # Actualizar permisos si es necesario
            rol_gerente.permisos = DEFAULT_ROLE_PERMISSIONS['gerente']
            rol_gerente.save()
            print("✅ Permisos del rol gerente actualizados")
        
        # Buscar o crear una sucursal de prueba
        sucursal, created = Sucursal.objects.get_or_create(
            nombre='Sucursal Centro',
            defaults={
                'direccion': 'Calle Principal 123',
                'telefono': '555-0123',
                'email': 'centro@sushirestaurant.com',
                'fecha_apertura': '2024-01-01',
                'activa': True
            }
        )
        
        if created:
            print("✅ Sucursal 'Sucursal Centro' creada")
        else:
            print("✅ Sucursal 'Sucursal Centro' ya existe")
        
        # Crear usuario gerente
        username = 'gerente_test'
        
        # Verificar si ya existe
        if Usuario.objects.filter(username=username).exists():
            print(f"⚠️  Usuario '{username}' ya existe")
            gerente = Usuario.objects.get(username=username)
        else:
            gerente = Usuario.objects.create_user(
                username=username,
                email='gerente@test.com',
                password='test123',
                first_name='Gerente',
                last_name='Test',
                sucursal=sucursal,
                rol=rol_gerente,
                activo=True
            )
            print(f"✅ Usuario gerente '{username}' creado exitosamente")
        
        # Asegurar que tiene la configuración correcta
        gerente.rol = rol_gerente
        gerente.sucursal = sucursal
        gerente.activo = True
        gerente.save()
        
        print(f"\n📋 INFORMACIÓN DEL GERENTE:")
        print(f"   Username: {gerente.username}")
        print(f"   Email: {gerente.email}")
        print(f"   Rol: {gerente.rol.nombre}")
        print(f"   Sucursal: {gerente.sucursal.nombre}")
        print(f"   Activo: {gerente.activo}")
        
        print(f"\n📋 PERMISOS DEL ROL GERENTE:")
        permisos = rol_gerente.permisos
        print(f"   Módulos: {permisos.get('modules', {})}")
        print(f"   Submódulos: {permisos.get('submodules', {})}")
        print(f"   Características: {permisos.get('features', {})}")
        
        print("\n" + "=" * 60)
        print("GERENTE DE PRUEBA LISTO PARA USAR")
        print("Credenciales:")
        print(f"  Username: {username}")
        print(f"  Password: test123")
        print("=" * 60)
        
        return gerente
        
    except Exception as e:
        print(f"❌ Error creando gerente: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    crear_gerente_test()
