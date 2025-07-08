#!/usr/bin/env python
"""
Script para crear/resetear un usuario mesero con credenciales conocidas
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

def crear_usuario_mesero_test():
    """Crear un usuario mesero de prueba con credenciales conocidas"""
    print("=" * 60)
    print("CREANDO USUARIO MESERO DE PRUEBA")
    print("=" * 60)
    
    username = "mesero_test"
    password = "123456"
    
    try:
        with transaction.atomic():
            # Eliminar usuario si ya existe
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                print(f"Usuario '{username}' ya existe. Actualizando contraseña...")
                user.set_password(password)
                user.is_active = True
                user.save()
            else:
                # Crear nuevo usuario
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    is_active=True
                )
                print(f"Usuario '{username}' creado exitosamente")
            
            print(f"\n✅ CREDENCIALES DEL MESERO:")
            print(f"   Usuario: {username}")
            print(f"   Contraseña: {password}")
            print(f"   Activo: {user.is_active}")
            
            print(f"\n🔗 PASOS PARA ACCEDER AL MENÚ:")
            print(f"   1. Ve a: http://127.0.0.1:8000/mesero/login/")
            print(f"   2. Ingresa usuario: {username}")
            print(f"   3. Ingresa contraseña: {password}")
            print(f"   4. Serás redirigido al menú automáticamente")
            
            print(f"\n📱 URL DIRECTA DEL MENÚ (después del login):")
            print(f"   http://127.0.0.1:8000/mesero/menu/")
            
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")

if __name__ == '__main__':
    crear_usuario_mesero_test()
