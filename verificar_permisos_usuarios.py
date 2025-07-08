#!/usr/bin/env python
"""
Script para verificar y asignar permisos de eliminación de productos
"""

import os
import django
import sys
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

# Importar modelos necesarios
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from restaurant.models import ProductoVenta

# Obtener el modelo de usuario personalizado
User = get_user_model()

def print_separator(title=None):
    """Imprime un separador con título opcional"""
    if title:
        print("\n" + "="*20 + f" {title} " + "="*20)
    else:
        print("\n" + "="*50)

def listar_usuarios():
    """Lista todos los usuarios y sus permisos"""
    print_separator("USUARIOS Y PERMISOS")
    
    usuarios = User.objects.all().order_by('username')
    print(f"Total de usuarios: {usuarios.count()}")
    
    for usuario in usuarios:
        print(f"\nUsuario: {usuario.username}")
        print(f"Superusuario: {'Sí' if usuario.is_superuser else 'No'}")
        print(f"Staff: {'Sí' if usuario.is_staff else 'No'}")
        print(f"Activo: {'Sí' if usuario.is_active else 'No'}")
        
        print("Permisos:")
        permisos = usuario.get_all_permissions()
        
        if 'restaurant.delete_productoventa' in permisos:
            print(f"   ✓ Puede eliminar productos (restaurant.delete_productoventa)")
        else:
            print(f"   ✗ NO puede eliminar productos (restaurant.delete_productoventa)")
        
        if 'restaurant.view_productoventa' in permisos:
            print(f"   ✓ Puede ver productos (restaurant.view_productoventa)")
        else:
            print(f"   ✗ NO puede ver productos (restaurant.view_productoventa)")
        
        if 'restaurant.change_productoventa' in permisos:
            print(f"   ✓ Puede editar productos (restaurant.change_productoventa)")
        else:
            print(f"   ✗ NO puede editar productos (restaurant.change_productoventa)")
        
        if 'restaurant.add_productoventa' in permisos:
            print(f"   ✓ Puede crear productos (restaurant.add_productoventa)")
        else:
            print(f"   ✗ NO puede crear productos (restaurant.add_productoventa)")
        
        # Listar grupos
        grupos = usuario.groups.all()
        if grupos:
            print(f"Grupos: {', '.join([g.name for g in grupos])}")
        else:
            print("Grupos: Ninguno")

def asignar_permiso_eliminar(username):
    """Asigna el permiso de eliminación de productos a un usuario"""
    print_separator(f"ASIGNANDO PERMISO A {username}")
    
    try:
        usuario = User.objects.get(username=username)
        
        # Verificar si ya tiene el permiso
        if usuario.has_perm('restaurant.delete_productoventa'):
            print(f"El usuario {username} ya tiene el permiso para eliminar productos.")
            return True
        
        # Obtener el permiso
        content_type = ContentType.objects.get_for_model(ProductoVenta)
        permiso = Permission.objects.get(
            codename='delete_productoventa',
            content_type=content_type
        )
        
        # Asignar el permiso
        usuario.user_permissions.add(permiso)
        print(f"Permiso 'delete_productoventa' asignado exitosamente a {username}.")
        
        # Verificar que se haya asignado correctamente
        usuario = User.objects.get(username=username)  # Recargar el usuario
        if usuario.has_perm('restaurant.delete_productoventa'):
            print(f"✓ Verificación exitosa: El usuario {username} ahora puede eliminar productos.")
            return True
        else:
            print(f"✗ Error: El permiso no se asignó correctamente.")
            return False
    
    except User.DoesNotExist:
        print(f"Error: El usuario {username} no existe.")
        return False
    
    except Permission.DoesNotExist:
        print(f"Error: El permiso 'delete_productoventa' no existe.")
        return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def asignar_permisos_a_grupo(grupo_nombre):
    """Asigna permisos de ProductoVenta a un grupo"""
    print_separator(f"ASIGNANDO PERMISOS AL GRUPO {grupo_nombre}")
    
    try:
        # Obtener o crear el grupo
        grupo, creado = Group.objects.get_or_create(name=grupo_nombre)
        if creado:
            print(f"Grupo '{grupo_nombre}' creado exitosamente.")
        else:
            print(f"Grupo '{grupo_nombre}' ya existe.")
        
        # Obtener los permisos de ProductoVenta
        content_type = ContentType.objects.get_for_model(ProductoVenta)
        permisos = Permission.objects.filter(
            content_type=content_type,
            codename__in=['add_productoventa', 'change_productoventa', 'delete_productoventa', 'view_productoventa']
        )
        
        # Asignar permisos al grupo
        for permiso in permisos:
            grupo.permissions.add(permiso)
            print(f"Permiso '{permiso.codename}' asignado al grupo '{grupo_nombre}'.")
        
        print(f"Todos los permisos de ProductoVenta asignados al grupo '{grupo_nombre}'.")
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def hacer_superusuario(username):
    """Convierte a un usuario en superusuario"""
    print_separator(f"HACIENDO SUPERUSUARIO A {username}")
    
    try:
        usuario = User.objects.get(username=username)
        
        if usuario.is_superuser:
            print(f"El usuario {username} ya es superusuario.")
            return True
        
        usuario.is_superuser = True
        usuario.is_staff = True
        usuario.save()
        
        print(f"El usuario {username} ahora es superusuario.")
        return True
    
    except User.DoesNotExist:
        print(f"Error: El usuario {username} no existe.")
        return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def crear_usuario_admin():
    """Crea un usuario administrador con todos los permisos"""
    print_separator("CREANDO USUARIO ADMIN")
    
    try:
        # Verificar si ya existe
        if User.objects.filter(username='admin').exists():
            print("El usuario 'admin' ya existe.")
            admin = User.objects.get(username='admin')
        else:
            # Crear el usuario
            admin = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            print("Usuario 'admin' creado exitosamente.")
        
        # Hacerlo superusuario
        admin.is_superuser = True
        admin.is_staff = True
        admin.save()
        
        print("El usuario 'admin' ahora es superusuario.")
        print("Credenciales: username='admin', password='admin123'")
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Función principal"""
    print_separator("ADMINISTRACIÓN DE PERMISOS DE PRODUCTOS")
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Django version: {django.get_version()}")
    print(f"Python version: {sys.version}")
    
    # Listar usuarios actuales
    listar_usuarios()
    
    # Menú de opciones
    print_separator("OPCIONES")
    print("1. Asignar permiso de eliminación a un usuario existente")
    print("2. Asignar todos los permisos de productos a un grupo")
    print("3. Hacer superusuario a un usuario existente")
    print("4. Crear usuario admin (superusuario)")
    print("5. Verificar permisos de usuarios")
    
    try:
        opcion = int(input("\nSeleccione una opción (1-5): "))
    except ValueError:
        opcion = 5
    
    if opcion == 1:
        username = input("Ingrese el nombre de usuario: ")
        asignar_permiso_eliminar(username)
    elif opcion == 2:
        grupo_nombre = input("Ingrese el nombre del grupo: ")
        asignar_permisos_a_grupo(grupo_nombre)
    elif opcion == 3:
        username = input("Ingrese el nombre de usuario: ")
        hacer_superusuario(username)
    elif opcion == 4:
        crear_usuario_admin()
    elif opcion == 5:
        listar_usuarios()
    else:
        print("Opción no válida.")
    
    print_separator("FIN")

if __name__ == "__main__":
    main()
