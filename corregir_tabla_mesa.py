#!/usr/bin/env python3
"""
Script para corregir la estructura de la tabla Mesa y hacer que coincida con el modelo actual
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.db import connection

def main():
    print("=== CORRIGIENDO ESTRUCTURA DE TABLA MESA ===\n")
    
    cursor = connection.cursor()
    
    # 1. Agregar campos faltantes uno por uno
    print("1. Agregando campos faltantes...")
    
    try:
        # Campo estado
        cursor.execute("""
            ALTER TABLE mesero_mesa 
            ADD COLUMN estado VARCHAR(20) DEFAULT 'disponible'
        """)
        print("   ✅ Campo 'estado' agregado")
    except Exception as e:
        if "duplicate column name" in str(e).lower():
            print("   ⚠️  Campo 'estado' ya existe")
        else:
            print(f"   ❌ Error agregando campo 'estado': {e}")
    
    try:
        # Campo ubicacion
        cursor.execute("""
            ALTER TABLE mesero_mesa 
            ADD COLUMN ubicacion VARCHAR(100)
        """)
        print("   ✅ Campo 'ubicacion' agregado")
    except Exception as e:
        if "duplicate column name" in str(e).lower():
            print("   ⚠️  Campo 'ubicacion' ya existe")
        else:
            print(f"   ❌ Error agregando campo 'ubicacion': {e}")
    
    try:
        # Campo notas
        cursor.execute("""
            ALTER TABLE mesero_mesa 
            ADD COLUMN notas TEXT
        """)
        print("   ✅ Campo 'notas' agregado")
    except Exception as e:
        if "duplicate column name" in str(e).lower():
            print("   ⚠️  Campo 'notas' ya existe")
        else:
            print(f"   ❌ Error agregando campo 'notas': {e}")
    
    try:
        # Campo fecha_creacion
        cursor.execute("""
            ALTER TABLE mesero_mesa 
            ADD COLUMN fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        """)
        print("   ✅ Campo 'fecha_creacion' agregado")
    except Exception as e:
        if "duplicate column name" in str(e).lower():
            print("   ⚠️  Campo 'fecha_creacion' ya existe")
        else:
            print(f"   ❌ Error agregando campo 'fecha_creacion': {e}")
    
    try:
        # Campo fecha_actualizacion
        cursor.execute("""
            ALTER TABLE mesero_mesa 
            ADD COLUMN fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
        """)
        print("   ✅ Campo 'fecha_actualizacion' agregado")
    except Exception as e:
        if "duplicate column name" in str(e).lower():
            print("   ⚠️  Campo 'fecha_actualizacion' ya existe")
        else:
            print(f"   ❌ Error agregando campo 'fecha_actualizacion': {e}")
    
    # 2. Actualizar estructura de número de mesa para que sea VARCHAR
    print("\n2. Actualizando estructura del campo 'numero'...")
    try:
        # Crear tabla temporal con la estructura correcta
        cursor.execute("""
            CREATE TABLE mesero_mesa_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero VARCHAR(10) UNIQUE NOT NULL,
                capacidad INTEGER NOT NULL DEFAULT 4,
                sucursal_id BIGINT NOT NULL,
                estado VARCHAR(20) DEFAULT 'disponible',
                ubicacion VARCHAR(100),
                activa BOOLEAN NOT NULL DEFAULT 1,
                notas TEXT,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sucursal_id) REFERENCES accounts_sucursal (id)
            )
        """)
        
        # Copiar datos de la tabla original
        cursor.execute("""
            INSERT INTO mesero_mesa_new 
            (id, numero, capacidad, sucursal_id, activa)
            SELECT id, CAST(numero AS VARCHAR), capacidad, sucursal_id, activa
            FROM mesero_mesa
        """)
        
        # Eliminar tabla original
        cursor.execute("DROP TABLE mesero_mesa")
        
        # Renombrar tabla nueva
        cursor.execute("ALTER TABLE mesero_mesa_new RENAME TO mesero_mesa")
        
        print("   ✅ Estructura de tabla actualizada correctamente")
        
    except Exception as e:
        print(f"   ❌ Error actualizando estructura: {e}")
        print("   Intentando método alternativo...")
        
        # Si falla, solo agregar los campos que faltan sin cambiar estructura
        try:
            cursor.execute("UPDATE mesero_mesa SET estado = 'disponible' WHERE estado IS NULL")
            print("   ✅ Estados por defecto establecidos")
        except Exception as e2:
            print(f"   ❌ Error estableciendo estados: {e2}")
    
    # 3. Verificar la estructura final
    print("\n3. Verificando estructura final...")
    cursor.execute("PRAGMA table_info(mesero_mesa);")
    columns = cursor.fetchall()
    
    print("   📋 COLUMNAS FINALES:")
    for col in columns:
        print(f"     - {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
    
    # 4. Verificar que el campo estado existe y está disponible
    column_names = [col[1] for col in columns]
    if 'estado' in column_names:
        print("\n   ✅ Campo 'estado' está disponible")
        
        # Contar registros por estado
        cursor.execute("SELECT estado, COUNT(*) FROM mesero_mesa GROUP BY estado")
        estados = cursor.fetchall()
        
        if estados:
            print("   📊 Distribución de estados:")
            for estado, count in estados:
                print(f"     - {estado or 'NULL'}: {count} mesas")
        else:
            print("   ⚠️  No hay mesas en la tabla")
    else:
        print("\n   ❌ Campo 'estado' aún no está disponible")
    
    print("\n✅ CORRECCIÓN COMPLETADA")

if __name__ == '__main__':
    main()
