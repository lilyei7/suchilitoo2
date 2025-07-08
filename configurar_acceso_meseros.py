import django
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mesero.models import Mesa
from accounts.models import Sucursal

User = get_user_model()

def crear_grupo_meseros():
    """Crear el grupo Meseros si no existe"""
    print("=== CREANDO GRUPO MESEROS ===")
    
    # Crear grupo
    grupo, created = Group.objects.get_or_create(name='Meseros')
    if created:
        print("✓ Grupo 'Meseros' creado")
    else:
        print("✓ Grupo 'Meseros' ya existe")
    
    # Añadir permisos básicos
    content_type = ContentType.objects.get_for_model(Mesa)
    permisos = [
        Permission.objects.get_or_create(
            codename='view_mesa',
            name='Can view mesa',
            content_type=content_type,
        )[0],
        Permission.objects.get_or_create(
            codename='change_mesa',
            name='Can change mesa',
            content_type=content_type,
        )[0],
    ]
    
    grupo.permissions.set(permisos)
    print(f"✓ Permisos añadidos al grupo: {[p.name for p in permisos]}")
    
    return grupo

def asignar_usuarios_a_grupo():
    """Asignar usuarios meseros al grupo"""
    print("\n=== ASIGNANDO USUARIOS AL GRUPO MESEROS ===")
    
    grupo = Group.objects.get(name='Meseros')
    usuarios = ['mesero_test', 'mesero1', 'mesero2', 'mesero3']
    
    for username in usuarios:
        try:
            user = User.objects.get(username=username)
            user.groups.add(grupo)
            print(f"✓ Usuario {username} añadido al grupo Meseros")
        except User.DoesNotExist:
            print(f"✗ Usuario {username} no existe")

def verificar_acceso():
    """Verificar que los usuarios pueden acceder a las mesas"""
    print("\n=== VERIFICANDO ACCESO A MESAS ===")
    
    usuarios = ['mesero_test', 'mesero1', 'mesero2', 'mesero3']
    
    for username in usuarios:
        try:
            user = User.objects.get(username=username)
            print(f"\nUsuario: {username}")
            print(f"  - Grupos: {[g.name for g in user.groups.all()]}")
            print(f"  - Sucursal: {getattr(user, 'sucursal', 'SIN SUCURSAL')}")
            print(f"  - Activo: {user.is_active}")
            print(f"  - Staff: {user.is_staff}")
            
            # Verificar permisos
            permisos = user.get_all_permissions()
            print(f"  - Permisos: {list(permisos)}")
            
            # Verificar mesas accesibles
            if hasattr(user, 'sucursal') and user.sucursal:
                mesas = Mesa.objects.filter(sucursal=user.sucursal, activa=True)
                print(f"  - Mesas accesibles: {mesas.count()}")
            else:
                print("  - Sin sucursal asignada")
                
        except User.DoesNotExist:
            print(f"✗ Usuario {username} no existe")

def crear_usuario_test():
    """Crear un usuario de prueba específico"""
    print("\n=== CREANDO USUARIO DE PRUEBA ===")
    
    # Obtener sucursal
    sucursal = Sucursal.objects.get(nombre="Sucursal Centro")
    
    # Crear usuario
    username = "mesero_demo"
    password = "demo123"
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f'{username}@sushi.com',
            'first_name': 'Demo',
            'last_name': 'Mesero',
            'is_active': True,
            'sucursal': sucursal
        }
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"✓ Usuario {username} creado con contraseña: {password}")
    else:
        print(f"✓ Usuario {username} ya existe")
    
    # Añadir al grupo
    grupo = Group.objects.get(name='Meseros')
    user.groups.add(grupo)
    user.sucursal = sucursal
    user.save()
    
    print(f"✓ Usuario {username} configurado:")
    print(f"  - Sucursal: {user.sucursal.nombre}")
    print(f"  - Grupos: {[g.name for g in user.groups.all()]}")
    print(f"  - Credenciales: {username} / {password}")

def main():
    """Función principal"""
    try:
        crear_grupo_meseros()
        asignar_usuarios_a_grupo()
        verificar_acceso()
        crear_usuario_test()
        
        print("\n=== INSTRUCCIONES PARA PROBAR ===")
        print("1. Accede a: http://127.0.0.1:8000/accounts/login/")
        print("2. Usa las credenciales: mesero_demo / demo123")
        print("3. Después del login, ve a: http://127.0.0.1:8000/mesero/seleccionar-mesa/")
        print("4. Deberías ver 8 mesas disponibles de 'Sucursal Centro'")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
