#!/usr/bin/env python
"""
Script para diagnosticar y solucionar problemas con usuarios y roles.
Verifica:
1. Que existan todos los roles necesarios
2. Que los roles estén activos
3. Que exista al menos un superusuario
4. Que existan sucursales activas
"""
import os
import sys
import django
import json

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.db import transaction
from accounts.models import Usuario, Rol, Sucursal
from django.contrib.auth.hashers import make_password

def verificar_roles():
    """Verifica que existan todos los roles necesarios y estén activos"""
    print("\n🔍 VERIFICANDO ROLES")
    print("-" * 40)
    
    roles_requeridos = [
        'admin', 'gerente', 'supervisor', 'cajero', 
        'cocinero', 'mesero', 'inventario', 'rrhh'
    ]
    
    roles_existentes = {rol.nombre: rol for rol in Rol.objects.all()}
    roles_faltantes = [nombre for nombre in roles_requeridos if nombre not in roles_existentes]
    roles_inactivos = [rol for rol in Rol.objects.filter(activo=False)]
    
    # Mostrar estado actual
    print(f"Total de roles en BD: {len(roles_existentes)}")
    if roles_faltantes:
        print(f"Roles faltantes: {', '.join(roles_faltantes)}")
    else:
        print("✅ Todos los roles requeridos existen")
    
    if roles_inactivos:
        print(f"Roles inactivos: {', '.join([rol.nombre for rol in roles_inactivos])}")
    else:
        print("✅ Todos los roles están activos")
    
    # Preguntar si arreglar problemas
    if roles_faltantes or roles_inactivos:
        respuesta = input("\n¿Desea crear los roles faltantes y activar los inactivos? (s/n): ")
        if respuesta.lower() == 's':
            with transaction.atomic():
                # Crear roles faltantes
                for nombre in roles_faltantes:
                    descripcion = f"Rol de {nombre}"
                    rol = Rol.objects.create(
                        nombre=nombre, 
                        descripcion=descripcion,
                        activo=True
                    )
                    print(f"✅ Rol '{nombre}' creado")
                
                # Activar roles inactivos
                for rol in roles_inactivos:
                    rol.activo = True
                    rol.save()
                    print(f"✅ Rol '{rol.nombre}' activado")
            
            print("\n✅ Correcciones aplicadas")
    
    return roles_faltantes, roles_inactivos

def verificar_superusuario():
    """Verifica que exista al menos un superusuario"""
    print("\n🔍 VERIFICANDO SUPERUSUARIOS")
    print("-" * 40)
    
    superusers = Usuario.objects.filter(is_superuser=True)
    print(f"Superusuarios encontrados: {superusers.count()}")
    
    if superusers.exists():
        for user in superusers:
            print(f"- {user.username} ({user.email})")
        print("✅ Existe al menos un superusuario")
    else:
        print("❌ No hay superusuarios en el sistema")
        respuesta = input("\n¿Desea crear un superusuario? (s/n): ")
        if respuesta.lower() == 's':
            username = input("Nombre de usuario: ") or 'admin'
            email = input("Email: ") or 'admin@sushirestaurant.com'
            password = input("Contraseña: ") or 'admin123456'
            
            try:
                Usuario.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                    first_name='Administrador',
                    last_name='Sistema'
                )
                print(f"✅ Superusuario '{username}' creado exitosamente")
            except Exception as e:
                print(f"❌ Error al crear superusuario: {e}")
    
    return superusers.exists()

def verificar_sucursales():
    """Verifica que existan sucursales activas"""
    print("\n🔍 VERIFICANDO SUCURSALES")
    print("-" * 40)
    
    sucursales = Sucursal.objects.all()
    sucursales_activas = Sucursal.objects.filter(activa=True)
    
    print(f"Sucursales totales: {sucursales.count()}")
    print(f"Sucursales activas: {sucursales_activas.count()}")
    
    if sucursales.exists():
        for sucursal in sucursales:
            estado = "✓ Activa" if sucursal.activa else "✗ Inactiva"
            print(f"- {sucursal.nombre}: {estado}")
    else:
        print("❌ No hay sucursales en el sistema")
    
    if not sucursales_activas.exists():
        respuesta = input("\n¿Desea crear una sucursal? (s/n): ")
        if respuesta.lower() == 's':
            nombre = input("Nombre de la sucursal: ") or 'Sucursal Principal'
            direccion = input("Dirección: ") or 'Av. Principal #123, Ciudad'
            telefono = input("Teléfono: ") or '555-123-4567'
            email = input("Email: ") or 'sucursal@sushirestaurant.com'
            
            try:
                from datetime import date
                sucursal = Sucursal.objects.create(
                    nombre=nombre,
                    direccion=direccion,
                    telefono=telefono,
                    email=email,
                    activa=True,
                    fecha_apertura=date.today()
                )
                print(f"✅ Sucursal '{nombre}' creada exitosamente")
            except Exception as e:
                print(f"❌ Error al crear sucursal: {e}")
        elif sucursales.exists():
            respuesta = input("\n¿Desea activar todas las sucursales existentes? (s/n): ")
            if respuesta.lower() == 's':
                with transaction.atomic():
                    for sucursal in sucursales:
                        sucursal.activa = True
                        sucursal.save()
                    print(f"✅ {sucursales.count()} sucursales activadas")
    
    return sucursales_activas.exists()

def verificar_usuarios_con_rol():
    """Verifica que los usuarios tengan roles asignados"""
    print("\n🔍 VERIFICANDO USUARIOS CON ROL")
    print("-" * 40)
    
    usuarios = Usuario.objects.all()
    usuarios_sin_rol = Usuario.objects.filter(rol__isnull=True)
    
    print(f"Total de usuarios: {usuarios.count()}")
    print(f"Usuarios sin rol: {usuarios_sin_rol.count()}")
    
    if usuarios_sin_rol.exists():
        print("\nUsuarios sin rol asignado:")
        for user in usuarios_sin_rol:
            print(f"- {user.username} ({user.get_full_name() or 'Sin nombre'})")
        
        respuesta = input("\n¿Desea asignar el rol 'admin' a estos usuarios? (s/n): ")
        if respuesta.lower() == 's':
            try:
                rol_admin = Rol.objects.get(nombre='admin')
                with transaction.atomic():
                    for user in usuarios_sin_rol:
                        user.rol = rol_admin
                        user.save()
                    print(f"✅ {usuarios_sin_rol.count()} usuarios ahora tienen rol 'admin'")
            except Rol.DoesNotExist:
                print("❌ No existe el rol 'admin'. Ejecute primero la verificación de roles.")
            except Exception as e:
                print(f"❌ Error al asignar roles: {e}")
    else:
        print("✅ Todos los usuarios tienen un rol asignado")
    
    return usuarios_sin_rol.count()

def verificar_usuarios_con_sucursal():
    """Verifica que los usuarios tengan sucursal asignada"""
    print("\n🔍 VERIFICANDO USUARIOS CON SUCURSAL")
    print("-" * 40)
    
    usuarios = Usuario.objects.all()
    usuarios_sin_sucursal = Usuario.objects.filter(sucursal__isnull=True)
    
    print(f"Total de usuarios: {usuarios.count()}")
    print(f"Usuarios sin sucursal: {usuarios_sin_sucursal.count()}")
    
    if usuarios_sin_sucursal.exists() and Sucursal.objects.filter(activa=True).exists():
        print("\nUsuarios sin sucursal asignada:")
        for user in usuarios_sin_sucursal:
            print(f"- {user.username} ({user.get_full_name() or 'Sin nombre'})")
        
        respuesta = input("\n¿Desea asignar una sucursal a estos usuarios? (s/n): ")
        if respuesta.lower() == 's':
            try:
                sucursal = Sucursal.objects.filter(activa=True).first()
                with transaction.atomic():
                    for user in usuarios_sin_sucursal:
                        user.sucursal = sucursal
                        user.save()
                    print(f"✅ {usuarios_sin_sucursal.count()} usuarios ahora tienen asignada la sucursal '{sucursal.nombre}'")
            except Exception as e:
                print(f"❌ Error al asignar sucursales: {e}")
    elif not Sucursal.objects.filter(activa=True).exists():
        print("❌ No hay sucursales activas para asignar")
    else:
        print("✅ Todos los usuarios tienen una sucursal asignada")
    
    return usuarios_sin_sucursal.count()

def main():
    """Función principal que ejecuta todas las verificaciones"""
    print("\n" + "=" * 50)
    print("🔧 DIAGNÓSTICO DE USUARIOS Y ROLES")
    print("=" * 50)
    
    # Verificar componentes
    roles_faltantes, roles_inactivos = verificar_roles()
    hay_superusuario = verificar_superusuario()
    hay_sucursales = verificar_sucursales()
    usuarios_sin_rol = verificar_usuarios_con_rol()
    usuarios_sin_sucursal = verificar_usuarios_con_sucursal()
    
    # Mostrar resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 50)
    
    estado_roles = "✅ OK" if not roles_faltantes and not roles_inactivos else "❌ Requiere atención"
    estado_superusuario = "✅ OK" if hay_superusuario else "❌ Requiere atención"
    estado_sucursales = "✅ OK" if hay_sucursales else "❌ Requiere atención"
    estado_usuarios_rol = "✅ OK" if not usuarios_sin_rol else "❌ Requiere atención"
    estado_usuarios_sucursal = "✅ OK" if not usuarios_sin_sucursal else "❌ Requiere atención"
    
    print(f"Roles: {estado_roles}")
    print(f"Superusuario: {estado_superusuario}")
    print(f"Sucursales: {estado_sucursales}")
    print(f"Usuarios con rol: {estado_usuarios_rol}")
    print(f"Usuarios con sucursal: {estado_usuarios_sucursal}")
    
    # Recomendaciones finales
    if not hay_superusuario or not hay_sucursales or roles_faltantes or roles_inactivos:
        print("\n⚠️ RECOMENDACIÓN: Ejecute 'python inicializar_sistema.py' para crear todos los datos básicos")
    
    print("\n¡Diagnóstico completado!")

if __name__ == "__main__":
    main()
