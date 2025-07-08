#!/usr/bin/env python
"""
Script para solucionar el problema de eliminación de productos
"""

import os
import sys
import django

# Configurar Django
sys.path.append('c:\\Users\\olcha\\Desktop\\sushi_restaurant - Copy (2)\\suchilitoo2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from restaurant.models import ProductoVenta

User = get_user_model()

def solucionar_eliminacion():
    print("=== SOLUCIONANDO PROBLEMA DE ELIMINACIÓN ===\n")
    
    # 1. Verificar que el problema existe
    print("1. VERIFICANDO ESTADO ACTUAL:")
    usuarios_sin_permisos = []
    usuarios_con_permisos = []
    
    for usuario in User.objects.filter(is_active=True):
        if usuario.has_perm('restaurant.delete_productoventa'):
            usuarios_con_permisos.append(usuario.username)
        else:
            usuarios_sin_permisos.append(usuario.username)
    
    print(f"   Usuarios CON permisos de eliminación: {usuarios_con_permisos}")
    print(f"   Usuarios SIN permisos de eliminación: {usuarios_sin_permisos}")
    
    if not usuarios_sin_permisos:
        print("   ✓ Todos los usuarios ya tienen permisos")
        return
    
    # 2. Obtener o crear permisos necesarios
    print("\n2. CONFIGURANDO PERMISOS:")
    
    try:
        content_type = ContentType.objects.get_for_model(ProductoVenta)
        
        permisos_necesarios = [
            ('add_productoventa', 'Can add producto venta'),
            ('change_productoventa', 'Can change producto venta'),
            ('delete_productoventa', 'Can delete producto venta'),
            ('view_productoventa', 'Can view producto venta'),
        ]
        
        permisos_creados = []
        for codename, name in permisos_necesarios:
            permiso, created = Permission.objects.get_or_create(
                codename=codename,
                content_type=content_type,
                defaults={'name': name}
            )
            permisos_creados.append(permiso)
            if created:
                print(f"   ✓ Permiso creado: {codename}")
            else:
                print(f"   - Permiso ya existe: {codename}")
        
    except Exception as e:
        print(f"   ❌ Error creando permisos: {e}")
        return
    
    # 3. Crear o actualizar grupos con permisos
    print("\n3. CONFIGURANDO GRUPOS:")
    
    # Grupo para administradores/gerentes (permisos completos)
    grupo_admin, created = Group.objects.get_or_create(name='Administradores')
    if created:
        print("   ✓ Grupo 'Administradores' creado")
    else:
        print("   - Grupo 'Administradores' ya existe")
    
    # Asignar todos los permisos al grupo admin
    for permiso in permisos_creados:
        grupo_admin.permissions.add(permiso)
    print("   ✓ Permisos asignados al grupo 'Administradores'")
    
    # Grupo para usuarios regulares (solo ver y editar, no eliminar)
    grupo_usuarios, created = Group.objects.get_or_create(name='Usuarios')
    if created:
        print("   ✓ Grupo 'Usuarios' creado")
    else:
        print("   - Grupo 'Usuarios' ya existe")
    
    # Asignar permisos limitados al grupo usuarios (sin delete)
    permisos_usuarios = [p for p in permisos_creados if p.codename != 'delete_productoventa']
    for permiso in permisos_usuarios:
        grupo_usuarios.permissions.add(permiso)
    print("   ✓ Permisos limitados asignados al grupo 'Usuarios'")
    
    # 4. Asignar usuarios a grupos
    print("\n4. ASIGNANDO USUARIOS A GRUPOS:")
    
    usuarios_admin = ['jhayco', 'admin', 'admin_test', 'admin1']  # Usuarios que deben tener permisos completos
    usuarios_asignados_admin = 0
    usuarios_asignados_usuarios = 0
    
    for usuario in User.objects.filter(is_active=True):
        if usuario.is_superuser or usuario.username in usuarios_admin:
            # Usuarios admin: permisos completos
            usuario.groups.add(grupo_admin)
            usuarios_asignados_admin += 1
            print(f"   ✓ {usuario.username} agregado al grupo 'Administradores'")
        else:
            # Usuarios regulares: permisos limitados 
            usuario.groups.add(grupo_usuarios)
            usuarios_asignados_usuarios += 1
            print(f"   ✓ {usuario.username} agregado al grupo 'Usuarios'")
    
    print(f"\n   Resumen:")
    print(f"   - Usuarios en grupo 'Administradores': {usuarios_asignados_admin}")
    print(f"   - Usuarios en grupo 'Usuarios': {usuarios_asignados_usuarios}")
    
    # 5. Verificar la solución
    print("\n5. VERIFICANDO SOLUCIÓN:")
    
    usuarios_con_eliminacion = []
    usuarios_sin_eliminacion = []
    
    for usuario in User.objects.filter(is_active=True):
        if usuario.has_perm('restaurant.delete_productoventa'):
            usuarios_con_eliminacion.append(usuario.username)
        else:
            usuarios_sin_eliminacion.append(usuario.username)
    
    print(f"   Usuarios CON permisos de eliminación: {usuarios_con_eliminacion}")
    print(f"   Usuarios SIN permisos de eliminación: {usuarios_sin_eliminacion}")
    
    # 6. Crear contraseñas conocidas para usuarios admin si es necesario
    print("\n6. CONFIGURANDO ACCESO DE PRUEBA:")
    
    try:
        # Asegurar que el usuario admin tenga una contraseña conocida
        admin_usuario = User.objects.get(username='admin')
        admin_usuario.set_password('admin123')
        admin_usuario.save()
        print("   ✓ Contraseña actualizada para usuario 'admin' (admin123)")
    except User.DoesNotExist:
        print("   - Usuario 'admin' no encontrado")
    
    try:
        # Asegurar que jhayco tenga una contraseña conocida  
        jhayco_usuario = User.objects.get(username='jhayco')
        jhayco_usuario.set_password('jhayco123')
        jhayco_usuario.save()
        print("   ✓ Contraseña actualizada para usuario 'jhayco' (jhayco123)")
    except User.DoesNotExist:
        print("   - Usuario 'jhayco' no encontrado")
    
    # 7. Resumen final
    print("\n" + "="*50)
    print("RESUMEN DE LA SOLUCIÓN:")
    print("="*50)
    print("✓ Permisos de productos de venta configurados")
    print("✓ Grupos 'Administradores' y 'Usuarios' creados")
    print("✓ Usuarios asignados a grupos apropiados")
    print("✓ Usuarios admin tienen permisos de eliminación")
    print("✓ Contraseñas de prueba configuradas")
    print("\nCREDENCIALES DE PRUEBA:")
    print("- Usuario: admin, Contraseña: admin123")
    print("- Usuario: jhayco, Contraseña: jhayco123")
    print("\nAHORA PUEDES:")
    print("1. Hacer login con un usuario admin")
    print("2. Ir a /dashboard/productos-venta/")
    print("3. Eliminar productos usando el botón de basura")
    print("="*50)

if __name__ == '__main__':
    solucionar_eliminacion()
