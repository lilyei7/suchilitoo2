#!/usr/bin/env python3
"""
Script para crear las tablas faltantes y corregir la estructura de mesero
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
    print("=== CREANDO TABLAS FALTANTES DE MESERO ===\n")
    
    cursor = connection.cursor()
    
    # 1. Recrear tabla mesero_orden con la estructura correcta
    print("1. Recreando tabla mesero_orden...")
    try:
        # Eliminar tabla existente si existe
        cursor.execute("DROP TABLE IF EXISTS mesero_orden_old")
        cursor.execute("ALTER TABLE mesero_orden RENAME TO mesero_orden_old")
        
        # Crear nueva tabla con estructura correcta
        cursor.execute("""
            CREATE TABLE mesero_orden (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_orden VARCHAR(20) UNIQUE NOT NULL,
                mesa_id INTEGER,
                mesero_id INTEGER,
                cliente_nombre VARCHAR(200),
                cliente_telefono VARCHAR(20),
                tipo_servicio VARCHAR(20) DEFAULT 'mesa',
                estado VARCHAR(20) DEFAULT 'pendiente',
                subtotal DECIMAL(10,2) DEFAULT 0,
                impuesto DECIMAL(10,2) DEFAULT 0,
                descuento DECIMAL(10,2) DEFAULT 0,
                total DECIMAL(10,2) DEFAULT 0,
                observaciones TEXT,
                notas_cocina TEXT,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_confirmacion DATETIME,
                fecha_preparacion DATETIME,
                fecha_lista DATETIME,
                fecha_entrega DATETIME,
                fecha_cierre DATETIME,
                FOREIGN KEY (mesa_id) REFERENCES mesero_mesa (id),
                FOREIGN KEY (mesero_id) REFERENCES accounts_usuario (id)
            )
        """)
        
        # Migrar datos de la tabla anterior si había alguno
        cursor.execute("""
            INSERT INTO mesero_orden 
            (id, numero_orden, mesa_id, mesero_id, estado, total, observaciones, fecha_creacion)
            SELECT id, 
                   '20250702-' || PRINTF('%04d', id) as numero_orden,
                   mesa_id, 
                   mesero_id, 
                   estado, 
                   total, 
                   notas,
                   created_at
            FROM mesero_orden_old
        """)
        
        cursor.execute("DROP TABLE mesero_orden_old")
        print("   ✅ Tabla mesero_orden recreada")
        
    except Exception as e:
        print(f"   ❌ Error recreando mesero_orden: {e}")
    
    # 2. Recrear tabla mesero_ordenitem con la estructura correcta
    print("\n2. Recreando tabla mesero_ordenitem...")
    try:
        cursor.execute("DROP TABLE IF EXISTS mesero_ordenitem_old")
        cursor.execute("ALTER TABLE mesero_ordenitem RENAME TO mesero_ordenitem_old")
        
        cursor.execute("""
            CREATE TABLE mesero_ordenitem (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orden_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL DEFAULT 1,
                precio_unitario DECIMAL(10,2) NOT NULL,
                subtotal DECIMAL(10,2) NOT NULL,
                notas_especiales TEXT,
                estado VARCHAR(20) DEFAULT 'pendiente',
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (orden_id) REFERENCES mesero_orden (id),
                FOREIGN KEY (producto_id) REFERENCES restaurant_productoventa (id)
            )
        """)
        
        # Migrar datos
        cursor.execute("""
            INSERT INTO mesero_ordenitem 
            (id, orden_id, producto_id, cantidad, precio_unitario, subtotal, notas_especiales, fecha_creacion)
            SELECT id, 
                   orden_id, 
                   producto_id, 
                   cantidad, 
                   precio_unitario,
                   precio_unitario * cantidad as subtotal,
                   notas,
                   created_at
            FROM mesero_ordenitem_old
        """)
        
        cursor.execute("DROP TABLE mesero_ordenitem_old")
        print("   ✅ Tabla mesero_ordenitem recreada")
        
    except Exception as e:
        print(f"   ❌ Error recreando mesero_ordenitem: {e}")
    
    # 3. Crear tabla mesero_historialorden
    print("\n3. Creando tabla mesero_historialorden...")
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mesero_historialorden (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orden_id INTEGER NOT NULL,
                estado_anterior VARCHAR(20) NOT NULL,
                estado_nuevo VARCHAR(20) NOT NULL,
                usuario_id INTEGER,
                observaciones TEXT,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (orden_id) REFERENCES mesero_orden (id),
                FOREIGN KEY (usuario_id) REFERENCES accounts_usuario (id)
            )
        """)
        print("   ✅ Tabla mesero_historialorden creada")
        
    except Exception as e:
        print(f"   ❌ Error creando mesero_historialorden: {e}")
    
    # 4. Crear tabla mesero_historialmesa
    print("\n4. Creando tabla mesero_historialmesa...")
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mesero_historialmesa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mesa_id INTEGER NOT NULL,
                estado_anterior VARCHAR(20) NOT NULL,
                estado_nuevo VARCHAR(20) NOT NULL,
                usuario_id INTEGER,
                motivo TEXT,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mesa_id) REFERENCES mesero_mesa (id),
                FOREIGN KEY (usuario_id) REFERENCES accounts_usuario (id)
            )
        """)
        print("   ✅ Tabla mesero_historialmesa creada")
        
    except Exception as e:
        print(f"   ❌ Error creando mesero_historialmesa: {e}")
    
    # 5. Verificar estructura final
    print("\n5. Verificando estructura final...")
    
    tablas_necesarias = [
        'mesero_mesa',
        'mesero_orden', 
        'mesero_ordenitem',
        'mesero_historialorden',
        'mesero_historialmesa'
    ]
    
    for tabla in tablas_necesarias:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabla}'")
        if cursor.fetchone():
            print(f"   ✅ {tabla}")
            
            # Mostrar algunas columnas importantes
            cursor.execute(f"PRAGMA table_info({tabla});")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]
            print(f"      Columnas principales: {', '.join(col_names[:8])}")
            if len(col_names) > 8:
                print(f"      ... y {len(col_names) - 8} más")
        else:
            print(f"   ❌ {tabla}")
    
    print("\n✅ CORRECCIÓN DE TABLAS COMPLETADA")

if __name__ == '__main__':
    main()
