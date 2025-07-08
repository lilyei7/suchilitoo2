import django
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.db import connection

def crear_tablas_personalizacion():
    """Crear las tablas de personalización directamente en la base de datos"""
    print("=== CREANDO TABLAS DE PERSONALIZACIÓN ===")
    
    with connection.cursor() as cursor:
        # Crear tabla OpcionPersonalizacion
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mesero_opcionpersonalizacion (
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
            CREATE TABLE IF NOT EXISTS mesero_productopersonalizacion (
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
            CREATE TABLE IF NOT EXISTS mesero_ordenitempersonalizacion (
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
        
        # Verificar que las tablas se crearon correctamente
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'mesero_%personalizacion'")
        tablas = cursor.fetchall()
        
        print(f"\n✅ Tablas creadas exitosamente:")
        for tabla in tablas:
            print(f"  - {tabla[0]}")

def main():
    """Función principal"""
    try:
        crear_tablas_personalizacion()
        print("\n🎯 Las tablas están listas para usar")
        print("Ahora puedes ejecutar configurar_personalizaciones.py")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
