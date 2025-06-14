#!/usr/bin/env python
"""
Script para recrear solo los datos básicos del sistema.
Este script crea:
1. Superusuario administrador
2. Roles básicos
3. Sucursales de ejemplo
4. Usuarios de ejemplo

Útil cuando se han borrado los datos pero no la estructura de la base de datos.
"""
import os
import sys
import django
from datetime import date

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.db import transaction
from accounts.models import Usuario, Rol, Sucursal

def main():
    """Función principal que ejecuta todo el proceso"""
    print("\n\n🔄 RECREANDO DATOS BÁSICOS DEL SISTEMA...")
    
    try:
        # Crear superusuario
        if not Usuario.objects.filter(is_superuser=True).exists():
            Usuario.objects.create_superuser(
                username='admin',
                email='admin@sushirestaurant.com',
                password='admin123456',
                first_name='Administrador',
                last_name='Sistema'
            )
            print("✅ Superusuario 'admin' creado (contraseña: admin123456)")
        else:
            print("ℹ️ Ya existe un superusuario")
        
        # Crear roles básicos
        roles_creados = 0
        for nombre, desc in [
            ('admin', 'Administrador del sistema'),
            ('gerente', 'Gerente de sucursal'),
            ('supervisor', 'Supervisor de operaciones'),
            ('cajero', 'Cajero/a'),
            ('cocinero', 'Cocinero/Chef'),
            ('mesero', 'Mesero/a'),
            ('inventario', 'Encargado de inventario'),
            ('rrhh', 'Recursos Humanos')
        ]:
            if not Rol.objects.filter(nombre=nombre).exists():
                Rol.objects.create(
                    nombre=nombre,
                    descripcion=desc,
                    permisos={'admin': True} if nombre == 'admin' else {},
                    activo=True
                )
                roles_creados += 1
        
        print(f"✅ {roles_creados} roles creados")
        
        # Crear sucursales básicas
        sucursales_creadas = 0
        if not Sucursal.objects.exists():
            Sucursal.objects.create(
                nombre="Sucursal Principal",
                direccion="Av. Principal #123, Ciudad",
                telefono="555-123-4567",
                email="principal@sushirestaurant.com",
                fecha_apertura=date.today(),
                activa=True
            )
            sucursales_creadas += 1
        
        print(f"✅ {sucursales_creadas} sucursales creadas")
        
        print("\n✅ DATOS BÁSICOS RECREADOS EXITOSAMENTE")
        print("✅ Ahora puedes iniciar sesión con: admin / admin123456")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False
    
    return True

if __name__ == "__main__":
    with transaction.atomic():
        success = main()
    
    sys.exit(0 if success else 1)
