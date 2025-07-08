#!/usr/bin/env python3
"""
Script para verificar las tablas de cocina en la base de datos
"""

import os
import sys
import django
import sqlite3

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def verificar_tablas_cocina():
    """Verificar si las tablas de cocina existen"""
    print("=== VERIFICACIÓN DE TABLAS DE COCINA ===\n")
    
    # Conectar a la base de datos SQLite
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    try:
        # Buscar todas las tablas de cocina
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'cocina_%'")
        tablas_cocina = cursor.fetchall()
        
        print(f"Tablas de cocina encontradas: {len(tablas_cocina)}")
        for tabla in tablas_cocina:
            print(f"  - {tabla[0]}")
        
        if not tablas_cocina:
            print("❌ No se encontraron tablas de cocina")
            return False
        
        # Verificar tablas específicas esperadas
        tablas_esperadas = [
            'cocina_estadococina',
            'cocina_tiempopreparacion', 
            'cocina_ordencocina',
            'cocina_itemcocina',
            'cocina_logcocina'
        ]
        
        print(f"\nVerificando tablas esperadas:")
        todas_existen = True
        
        for tabla_esperada in tablas_esperadas:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabla_esperada,))
            existe = cursor.fetchone()
            
            if existe:
                print(f"  ✓ {tabla_esperada}")
                
                # Mostrar estructura de la tabla
                cursor.execute(f"PRAGMA table_info({tabla_esperada})")
                columnas = cursor.fetchall()
                print(f"    Columnas: {len(columnas)}")
                for col in columnas:
                    print(f"      - {col[1]} ({col[2]})")
                
            else:
                print(f"  ❌ {tabla_esperada} - NO EXISTE")
                todas_existen = False
        
        return todas_existen
        
    except Exception as e:
        print(f"Error verificando tablas: {e}")
        return False
    finally:
        conn.close()

def verificar_migraciones():
    """Verificar el estado de las migraciones"""
    print("\n=== VERIFICACIÓN DE MIGRACIONES ===\n")
    
    from django.db import connection
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT app, name, applied FROM django_migrations WHERE app = 'cocina'"
            )
            migraciones = cursor.fetchall()
            
            print(f"Migraciones de cocina: {len(migraciones)}")
            for app, name, applied in migraciones:
                estado = "APLICADA" if applied else "PENDIENTE"
                print(f"  - {name}: {estado}")
            
            return len(migraciones) > 0
            
    except Exception as e:
        print(f"Error verificando migraciones: {e}")
        return False

def recrear_tablas():
    """Intentar recrear las tablas de cocina"""
    print("\n=== RECREANDO TABLAS DE COCINA ===\n")
    
    try:
        from django.core.management import execute_from_command_line
        
        print("1. Eliminando migraciones de cocina...")
        # Marcar migraciones como no aplicadas
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM django_migrations WHERE app = 'cocina'")
        
        print("2. Recreando migraciones...")
        os.system("python manage.py makemigrations cocina")
        
        print("3. Aplicando migraciones...")
        os.system("python manage.py migrate cocina")
        
        print("✅ Tablas recreadas exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error recreando tablas: {e}")
        return False

def main():
    print("🔍 DIAGNÓSTICO DE TABLAS DE COCINA")
    print("=" * 50)
    
    # Verificar tablas
    tablas_ok = verificar_tablas_cocina()
    
    # Verificar migraciones
    migraciones_ok = verificar_migraciones()
    
    # Si las tablas no existen, intentar recrearlas
    if not tablas_ok:
        print("\n🔧 Las tablas no existen. Intentando recrearlas...")
        if recrear_tablas():
            # Verificar nuevamente
            tablas_ok = verificar_tablas_cocina()
    
    print("\n" + "=" * 50)
    if tablas_ok:
        print("✅ VERIFICACIÓN COMPLETADA: Tablas de cocina OK")
    else:
        print("❌ VERIFICACIÓN FALLÓ: Problemas con tablas de cocina")
        print("\n🔧 SOLUCIONES RECOMENDADAS:")
        print("1. python manage.py makemigrations cocina")
        print("2. python manage.py migrate")
        print("3. python configurar_cocina.py")

if __name__ == '__main__':
    main()
