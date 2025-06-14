#!/usr/bin/env python
"""
Script para hacer login y probar la funcionalidad
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario

def main():
    print("🔐 === VERIFICACIÓN DE USUARIO PARA LOGIN ===\n")
    
    usuarios = Usuario.objects.all()
    print(f"👥 Total usuarios en el sistema: {usuarios.count()}")
    
    if usuarios.exists():
        print("\n📋 Usuarios disponibles:")
        for i, user in enumerate(usuarios, 1):
            print(f"   {i}. {user.username} ({user.email}) - Activo: {user.is_active}")
            if user.sucursal:
                print(f"      Sucursal: {user.sucursal.nombre}")
            if user.rol:
                print(f"      Rol: {user.rol.nombre}")
        
        # Mostrar instrucciones de login
        primer_usuario = usuarios.first()
        print(f"\n🌐 INSTRUCCIONES PARA LOGIN:")
        print(f"   1. Ve a: http://127.0.0.1:8000/dashboard/login/")
        print(f"   2. Usuario: {primer_usuario.username}")
        print(f"   3. Contraseña: (la contraseña que configuraste)")
        print(f"   4. Después ve a: http://127.0.0.1:8000/dashboard/inventario/")
        
    else:
        print("❌ No hay usuarios en el sistema")
        print("🔧 Ejecuta el script de datos iniciales primero")
    
    print("\n🔐 === VERIFICACIÓN COMPLETADA ===")

if __name__ == '__main__':
    main()
