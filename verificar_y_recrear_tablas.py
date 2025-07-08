import django
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.db import connection

def verificar_tablas():
    """Verificar la estructura de las tablas de personalización"""
    print("=== VERIFICANDO ESTRUCTURA DE TABLAS ===")
    
    with connection.cursor() as cursor:
        # Verificar si existen las tablas
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'mesero_%personalizacion'
        """)
        tablas = cursor.fetchall()
        
        print(f"Tablas encontradas: {[t[0] for t in tablas]}")
        
        for tabla in tablas:
            tabla_nombre = tabla[0]
            print(f"\n--- Estructura de {tabla_nombre} ---")
            
            cursor.execute(f"PRAGMA table_info({tabla_nombre})")
            columnas = cursor.fetchall()
            
            for columna in columnas:
                print(f"  {columna[1]} ({columna[2]}) - NOT NULL: {columna[3]} - DEFAULT: {columna[4]}")

def recrear_tablas():
    """Recrear las tablas con la estructura correcta"""
    print("\n=== RECREANDO TABLAS ===")
    
    with connection.cursor() as cursor:
        # Eliminar tablas existentes
        cursor.execute("DROP TABLE IF EXISTS mesero_ordenitempersonalizacion")
        cursor.execute("DROP TABLE IF EXISTS mesero_productopersonalizacion") 
        cursor.execute("DROP TABLE IF EXISTS mesero_opcionpersonalizacion")
        cursor.execute("DROP TABLE IF EXISTS mesero_tipopersonalizacion")
        
        print("✓ Tablas eliminadas")
        
        # Crear tabla OpcionPersonalizacion
        cursor.execute("""
            CREATE TABLE mesero_opcionpersonalizacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(100) NOT NULL,
                tipo VARCHAR(20) NOT NULL DEFAULT 'quitar',
                precio_extra DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                activa BOOLEAN NOT NULL DEFAULT 1,
                categoria_id INTEGER NULL,
                FOREIGN KEY (categoria_id) REFERENCES restaurant_categoriaproducto(id)
            )
        """)
        print("✓ Tabla mesero_opcionpersonalizacion creada")
        
        # Crear tabla ProductoPersonalizacion
        cursor.execute("""
            CREATE TABLE mesero_productopersonalizacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER NOT NULL,
                opcion_id INTEGER NOT NULL,
                activa BOOLEAN NOT NULL DEFAULT 1,
                FOREIGN KEY (producto_id) REFERENCES restaurant_productoventa(id),
                FOREIGN KEY (opcion_id) REFERENCES mesero_opcionpersonalizacion(id),
                UNIQUE(producto_id, opcion_id)
            )
        """)
        print("✓ Tabla mesero_productopersonalizacion creada")
        
        # Crear tabla OrdenItemPersonalizacion
        cursor.execute("""
            CREATE TABLE mesero_ordenitempersonalizacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orden_item_id INTEGER NOT NULL,
                opcion_id INTEGER NOT NULL,
                valor TEXT NULL,
                precio_aplicado DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                FOREIGN KEY (orden_item_id) REFERENCES mesero_ordenitem(id),
                FOREIGN KEY (opcion_id) REFERENCES mesero_opcionpersonalizacion(id)
            )
        """)
        print("✓ Tabla mesero_ordenitempersonalizacion creada")

def insertar_datos_ejemplo():
    """Insertar algunos datos de ejemplo"""
    print("\n=== INSERTANDO DATOS DE EJEMPLO ===")
    
    with connection.cursor() as cursor:
        # Opciones básicas
        opciones = [
            ("Sin cebolla", "quitar", 0.00),
            ("Sin picante", "quitar", 0.00), 
            ("Sin wasabi", "quitar", 0.00),
            ("Extra aguacate", "agregar", 15.00),
            ("Extra salmón", "agregar", 25.00),
            ("Nota especial", "nota", 0.00),
        ]
        
        for nombre, tipo, precio in opciones:
            cursor.execute("""
                INSERT INTO mesero_opcionpersonalizacion 
                (nombre, tipo, precio_extra, activa)
                VALUES (?, ?, ?, ?)
            """, [nombre, tipo, precio, 1])
            print(f"✓ {nombre} ({tipo}) - ${precio}")
        
        cursor.execute("SELECT COUNT(*) FROM mesero_opcionpersonalizacion")
        total = cursor.fetchone()[0]
        print(f"\n✅ {total} opciones insertadas")

def main():
    """Función principal"""
    try:
        verificar_tablas()
        recrear_tablas()
        verificar_tablas()
        insertar_datos_ejemplo()
        
        print("\n🎯 TABLAS CONFIGURADAS CORRECTAMENTE")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
