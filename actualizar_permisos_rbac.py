#!/usr/bin/env python
"""
Script para actualizar los permisos por defecto de los roles existentes
Este script actualiza el campo 'permisos' de cada rol con la estructura definida en RBAC
"""
import os
import sys
import django
import json

# Configurar el entorno de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Rol, Usuario
from django.db import transaction
from dashboard.utils.permissions import DEFAULT_ROLE_PERMISSIONS, invalidate_user_permissions

def actualizar_permisos_roles():
    """
    Actualiza los permisos de todos los roles existentes con la estructura RBAC
    """
    print("=" * 60)
    print("🔧 ACTUALIZANDO PERMISOS DE ROLES CON ESTRUCTURA RBAC")
    print("=" * 60)
    
    # Obtener todos los roles activos
    roles = Rol.objects.filter(activo=True)
    
    if not roles.exists():
        print("❌ No se encontraron roles activos en el sistema")
        return False
    
    print(f"📋 Roles encontrados: {roles.count()}")
    for rol in roles:
        print(f"   - {rol.get_nombre_display()} ({rol.nombre})")
    
    # Confirmar actualización
    print("\n⚠️  ADVERTENCIA: Este proceso actualizará los permisos de todos los roles.")
    print("⚠️  Los permisos personalizados se perderán y se usarán los por defecto.")
    
    respuesta = input("\n¿Desea continuar? (escriba 'SI' para confirmar): ")
    
    if respuesta != "SI":
        print("❌ Operación cancelada por el usuario")
        return False
    
    # Procesar cada rol
    roles_actualizados = 0
    usuarios_afectados = []
    
    try:
        with transaction.atomic():
            for rol in roles:
                # Obtener permisos por defecto para este rol
                permisos_default = DEFAULT_ROLE_PERMISSIONS.get(rol.nombre)
                
                if permisos_default:
                    # Guardar estado anterior para comparación
                    permisos_anteriores = rol.permisos
                    
                    # Actualizar permisos
                    rol.permisos = permisos_default
                    rol.save()
                    
                    print(f"\n✅ Rol '{rol.get_nombre_display()}' actualizado:")
                    print(f"   📁 Módulos: {len([m for m, access in permisos_default.get('modules', {}).items() if access])}")
                    print(f"   🔧 Acciones: {list(permisos_default.get('actions', {}).keys())}")
                    print(f"   ⭐ Características: {len([f for f, enabled in permisos_default.get('features', {}).items() if enabled])}")
                    
                    roles_actualizados += 1
                    
                    # Obtener usuarios con este rol
                    usuarios_con_rol = Usuario.objects.filter(rol=rol, is_active=True)
                    usuarios_afectados.extend(usuarios_con_rol)
                    
                    if usuarios_con_rol.exists():
                        print(f"   👥 Usuarios afectados: {usuarios_con_rol.count()}")
                        for usuario in usuarios_con_rol:
                            print(f"      - {usuario.username} ({usuario.get_full_name() or 'Sin nombre'})")
                    
                else:
                    print(f"\n⚠️  Rol '{rol.get_nombre_display()}' no tiene permisos definidos en DEFAULT_ROLE_PERMISSIONS")
                    print(f"    Se mantienen los permisos actuales: {rol.permisos}")
            
            # Invalidar cache de permisos para todos los usuarios afectados
            print(f"\n🔄 Invalidando cache de permisos para {len(usuarios_afectados)} usuarios...")
            for usuario in usuarios_afectados:
                invalidate_user_permissions(usuario)
            
            print(f"\n✅ ACTUALIZACIÓN COMPLETADA")
            print(f"   📊 Roles actualizados: {roles_actualizados}")
            print(f"   👥 Usuarios afectados: {len(usuarios_afectados)}")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Error durante la actualización: {e}")
        return False

def mostrar_resumen_permisos():
    """
    Muestra un resumen de los permisos configurados por rol
    """
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PERMISOS POR ROL")
    print("=" * 60)
    
    for rol_nombre, permisos in DEFAULT_ROLE_PERMISSIONS.items():
        print(f"\n🔹 ROL: {rol_nombre.upper()}")
        print("-" * 40)
        
        # Módulos
        modulos = permisos.get('modules', {})
        modulos_activos = [m for m, access in modulos.items() if access]
        print(f"📁 Módulos ({len(modulos_activos)}): {', '.join(modulos_activos)}")
        
        # Acciones
        acciones = permisos.get('actions', {})
        print("🔧 Acciones:")
        for accion, modulos_permitidos in acciones.items():
            if modulos_permitidos:
                if '*' in modulos_permitidos:
                    print(f"   {accion}: Todos los módulos")
                else:
                    print(f"   {accion}: {', '.join(modulos_permitidos)}")
        
        # Características
        caracteristicas = permisos.get('features', {})
        caracteristicas_activas = [f for f, enabled in caracteristicas.items() if enabled]
        print(f"⭐ Características ({len(caracteristicas_activas)}): {', '.join(caracteristicas_activas)}")

def verificar_estructura_permisos():
    """
    Verifica que todos los roles en la BD tengan la estructura de permisos correcta
    """
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO ESTRUCTURA DE PERMISOS")
    print("=" * 60)
    
    roles = Rol.objects.filter(activo=True)
    problemas_encontrados = []
    
    for rol in roles:
        print(f"\n🔹 Verificando rol: {rol.get_nombre_display()}")
        
        if not rol.permisos:
            print("   ❌ Sin permisos configurados")
            problemas_encontrados.append(f"Rol {rol.nombre} sin permisos")
            continue
        
        # Verificar estructura
        estructura_esperada = ['modules', 'actions', 'features']
        estructura_actual = list(rol.permisos.keys())
        
        for seccion in estructura_esperada:
            if seccion not in estructura_actual:
                print(f"   ❌ Falta sección: {seccion}")
                problemas_encontrados.append(f"Rol {rol.nombre} falta sección {seccion}")
            else:
                print(f"   ✅ Sección {seccion}: OK")
        
        # Verificar que tenga al menos acceso al dashboard
        if rol.permisos.get('modules', {}).get('dashboard', False):
            print("   ✅ Acceso al dashboard: OK")
        else:
            print("   ⚠️  Sin acceso al dashboard")
            problemas_encontrados.append(f"Rol {rol.nombre} sin acceso al dashboard")
    
    if problemas_encontrados:
        print(f"\n⚠️  PROBLEMAS ENCONTRADOS ({len(problemas_encontrados)}):")
        for problema in problemas_encontrados:
            print(f"   - {problema}")
        return False
    else:
        print(f"\n✅ Todos los roles tienen estructura correcta")
        return True

def menu_principal():
    """
    Menú principal del script
    """
    while True:
        print("\n" + "=" * 60)
        print("🔧 GESTIÓN DE PERMISOS DE ROLES")
        print("=" * 60)
        print("1. 📊 Mostrar resumen de permisos por defecto")
        print("2. 🔍 Verificar estructura de permisos actuales")
        print("3. 🔄 Actualizar permisos de roles existentes")
        print("4. 🚪 Salir")
        print("-" * 60)
        
        opcion = input("Seleccione una opción (1-4): ").strip()
        
        if opcion == "1":
            mostrar_resumen_permisos()
        elif opcion == "2":
            verificar_estructura_permisos()
        elif opcion == "3":
            if actualizar_permisos_roles():
                print("\n🎉 ¡Permisos actualizados exitosamente!")
                print("💡 Los usuarios necesitarán volver a iniciar sesión para ver los cambios.")
            else:
                print("\n❌ La actualización no se completó correctamente.")
        elif opcion == "4":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("\n❌ Opción no válida. Por favor seleccione 1-4.")
        
        input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    print("🚀 Iniciando gestión de permisos de roles...")
    menu_principal()
