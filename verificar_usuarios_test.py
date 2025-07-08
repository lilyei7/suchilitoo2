#!/usr/bin/env python3
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario

def listar_usuarios_test():
    """List test users"""
    print("Usuarios de prueba disponibles:")
    
    usuarios = Usuario.objects.filter(
        username__in=['mesero_demo', 'admin_test', 'gerente_test']
    ).select_related('sucursal', 'rol')
    
    for usuario in usuarios:
        print(f"\nUsuario: {usuario.username}")
        print(f"  Email: {usuario.email}")
        print(f"  Nombre: {usuario.first_name} {usuario.last_name}")
        print(f"  Rol: {usuario.rol.nombre if usuario.rol else 'Sin rol'}")
        print(f"  Sucursal: {usuario.sucursal.nombre if usuario.sucursal else 'Sin sucursal'}")
        print(f"  Activo: {usuario.is_active}")
        print(f"  Contraseña: test123 (por defecto)")

if __name__ == "__main__":
    listar_usuarios_test()
