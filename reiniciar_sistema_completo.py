#!/usr/bin/env python
"""
Script para limpiar completamente la base de datos y reiniciar el sistema.
¡ADVERTENCIA! Este script eliminará TODOS los datos del sistema.
"""
import os
import sys
import django
import shutil
from pathlib import Path
import subprocess

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

def confirmar_accion():
    """Solicita confirmación del usuario"""
    print("\n" + "!" * 60)
    print("⚠️  ADVERTENCIA: ESTA ACCIÓN ELIMINARÁ TODOS LOS DATOS DEL SISTEMA ⚠️")
    print("!" * 60)
    print("\nEste script realizará las siguientes acciones:")
    print("1. Eliminar la base de datos actual (db.sqlite3)")
    print("2. Eliminar todas las migraciones de Django")
    print("3. Crear una nueva base de datos")
    print("4. Ejecutar migraciones iniciales")
    print("5. Crear datos básicos (superusuario, roles, sucursales)")
    
    confirmacion = input("\n¿Está COMPLETAMENTE SEGURO de que desea continuar? (escriba 'SI' para confirmar): ")
    
    if confirmacion.upper() != "SI":
        print("\n❌ Operación cancelada por el usuario.")
        sys.exit(0)
    
    print("\n⚠️ Comenzando proceso de limpieza total...\n")

def eliminar_base_datos():
    """Elimina el archivo de base de datos SQLite"""
    try:
        db_path = Path("db.sqlite3")
        if db_path.exists():
            db_path.unlink()
            print("✅ Base de datos eliminada")
        else:
            print("ℹ️ No se encontró archivo de base de datos")
    except Exception as e:
        print(f"❌ Error al eliminar base de datos: {e}")
        sys.exit(1)

def eliminar_migraciones():
    """Elimina todas las carpetas de migraciones"""
    try:
        apps = ['accounts', 'dashboard', 'restaurant']
        for app in apps:
            migrations_dir = Path(app) / 'migrations'
            if migrations_dir.exists() and migrations_dir.is_dir():
                # Preservar __init__.py
                init_file = migrations_dir / '__init__.py'
                has_init = init_file.exists()
                
                # Eliminar todos los archivos de migración
                for file in migrations_dir.glob('*.py'):
                    if file.name != '__init__.py':
                        file.unlink()
                
                # Eliminar carpeta __pycache__ si existe
                pycache = migrations_dir / '__pycache__'
                if pycache.exists() and pycache.is_dir():
                    shutil.rmtree(pycache)
                
                # Recrear __init__.py si existía
                if has_init and not init_file.exists():
                    init_file.touch()
                
                print(f"✅ Migraciones de '{app}' eliminadas")
            else:
                print(f"ℹ️ No se encontró carpeta de migraciones para '{app}'")
    except Exception as e:
        print(f"❌ Error al eliminar migraciones: {e}")
        sys.exit(1)

def ejecutar_comando(comando, descripcion):
    """Ejecuta un comando de shell y muestra su salida"""
    print(f"\n🔄 {descripcion}...")
    try:
        proceso = subprocess.run(comando, shell=True, check=True, 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 text=True)
        print(f"✅ {descripcion} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {descripcion}:")
        print(f"Código de salida: {e.returncode}")
        print(f"Salida de error:")
        print(e.stderr)
        return False

def main():
    """Función principal que ejecuta todo el proceso"""
    print("\n" + "=" * 60)
    print("🧹 LIMPIEZA TOTAL DEL SISTEMA Y REINICIO")
    print("=" * 60)
    
    # Confirmar acción
    confirmar_accion()
    
    # Eliminar base de datos y migraciones
    eliminar_base_datos()
    eliminar_migraciones()
    
    # Crear nuevas migraciones
    if not ejecutar_comando("python manage.py makemigrations accounts dashboard restaurant", 
                         "Creación de nuevas migraciones"):
        sys.exit(1)
    
    # Aplicar migraciones
    if not ejecutar_comando("python manage.py migrate", 
                         "Aplicación de migraciones"):
        sys.exit(1)
    
    # Inicializar sistema
    if not ejecutar_comando("python inicializar_sistema.py", 
                         "Inicialización del sistema"):
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ SISTEMA REINICIADO CORRECTAMENTE")
    print("=" * 60)
    print("\nPuede acceder al sistema con las siguientes credenciales:")
    print("Usuario: admin")
    print("Contraseña: admin123456")

if __name__ == "__main__":
    main()
