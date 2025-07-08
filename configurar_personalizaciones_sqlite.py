import django
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

import sqlite3
from restaurant.models import ProductoVenta

def insertar_opciones_personalizacion():
    """Insertar opciones de personalización usando SQLite directamente"""
    print("=== INSERTANDO OPCIONES DE PERSONALIZACIÓN ===")
    
    # Conectar directamente a SQLite
    db_path = "db.sqlite3"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Limpiar tabla
        cursor.execute("DELETE FROM mesero_opcionpersonalizacion")
        
        # Opciones básicas
        opciones = [
            ("Sin cebolla", "quitar", 0.00),
            ("Sin picante", "quitar", 0.00), 
            ("Sin wasabi", "quitar", 0.00),
            ("Sin jengibre", "quitar", 0.00),
            ("Sin salsa de soya", "quitar", 0.00),
            ("Sin ajonjolí", "quitar", 0.00),
            ("Sin aguacate", "quitar", 0.00),
            ("Sin pepino", "quitar", 0.00),
            ("Sin alga nori", "quitar", 0.00),
            ("Sin salsa teriyaki", "quitar", 0.00),
            ("Extra aguacate", "agregar", 15.00),
            ("Extra salmón", "agregar", 25.00),
            ("Extra atún", "agregar", 30.00),
            ("Extra queso crema", "agregar", 10.00),
            ("Extra ajonjolí", "agregar", 5.00),
            ("Extra salsa spicy", "agregar", 8.00),
            ("Extra wasabi", "agregar", 5.00),
            ("Nota especial", "nota", 0.00),
        ]
        
        for nombre, tipo, precio in opciones:
            cursor.execute("""
                INSERT INTO mesero_opcionpersonalizacion 
                (nombre, tipo, precio_extra, activa)
                VALUES (?, ?, ?, ?)
            """, (nombre, tipo, precio, 1))
            print(f"✓ {nombre} ({tipo}) - ${precio}")
        
        conn.commit()
        
        # Verificar inserción
        cursor.execute("SELECT COUNT(*) FROM mesero_opcionpersonalizacion")
        total = cursor.fetchone()[0]
        print(f"\n✅ {total} opciones insertadas")
        
    finally:
        conn.close()

def asignar_a_productos():
    """Asignar opciones básicas a productos"""
    print("\n=== ASIGNANDO OPCIONES A PRODUCTOS ===")
    
    # Conectar directamente a SQLite
    db_path = "db.sqlite3"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Limpiar asignaciones
        cursor.execute("DELETE FROM mesero_productopersonalizacion")
        
        # Obtener productos disponibles
        productos = ProductoVenta.objects.filter(disponible=True)
        
        # Opciones básicas para todos los productos
        opciones_basicas = [
            "Sin cebolla",
            "Sin picante", 
            "Sin wasabi",
            "Sin salsa de soya",
            "Nota especial"
        ]
        
        for producto in productos:
            print(f"\nConfigurando: {producto.nombre}")
            
            for opcion_nombre in opciones_basicas:
                # Obtener ID de la opción
                cursor.execute("""
                    SELECT id FROM mesero_opcionpersonalizacion 
                    WHERE nombre = ?
                """, (opcion_nombre,))
                
                result = cursor.fetchone()
                if result:
                    opcion_id = result[0]
                    
                    # Insertar asignación
                    cursor.execute("""
                        INSERT OR IGNORE INTO mesero_productopersonalizacion 
                        (producto_id, opcion_id, activa)
                        VALUES (?, ?, ?)
                    """, (producto.id, opcion_id, 1))
                    print(f"  ✓ {opcion_nombre}")
            
            # Opciones específicas para sushi/rolls
            nombre_lower = producto.nombre.lower()
            if any(palabra in nombre_lower for palabra in ['roll', 'maki', 'sushi']):
                opciones_sushi = ["Sin ajonjolí", "Sin aguacate", "Sin alga nori"]
                for opcion_nombre in opciones_sushi:
                    cursor.execute("""
                        SELECT id FROM mesero_opcionpersonalizacion 
                        WHERE nombre = ?
                    """, (opcion_nombre,))
                    
                    result = cursor.fetchone()
                    if result:
                        opcion_id = result[0]
                        cursor.execute("""
                            INSERT OR IGNORE INTO mesero_productopersonalizacion 
                            (producto_id, opcion_id, activa)
                            VALUES (?, ?, ?)
                        """, (producto.id, opcion_id, 1))
                        print(f"  ✓ {opcion_nombre}")
                
                # Extras para sushi
                if 'salmón' in nombre_lower or 'salmon' in nombre_lower:
                    cursor.execute("""
                        SELECT id FROM mesero_opcionpersonalizacion 
                        WHERE nombre = 'Extra salmón'
                    """)
                    result = cursor.fetchone()
                    if result:
                        cursor.execute("""
                            INSERT OR IGNORE INTO mesero_productopersonalizacion 
                            (producto_id, opcion_id, activa)
                            VALUES (?, ?, ?)
                        """, (producto.id, result[0], 1))
                        print(f"  ✓ Extra salmón")
                
                if 'queso' in nombre_lower:
                    cursor.execute("""
                        SELECT id FROM mesero_opcionpersonalizacion 
                        WHERE nombre = 'Extra queso crema'
                    """)
                    result = cursor.fetchone()
                    if result:
                        cursor.execute("""
                            INSERT OR IGNORE INTO mesero_productopersonalizacion 
                            (producto_id, opcion_id, activa)
                            VALUES (?, ?, ?)
                        """, (producto.id, result[0], 1))
                        print(f"  ✓ Extra queso crema")
        
        conn.commit()
        
        # Verificar asignaciones
        cursor.execute("SELECT COUNT(*) FROM mesero_productopersonalizacion")
        total = cursor.fetchone()[0]
        print(f"\n✅ Total asignaciones: {total}")
        
    finally:
        conn.close()

def mostrar_resumen():
    """Mostrar resumen de configuración"""
    print("\n=== RESUMEN DE CONFIGURACIÓN ===")
    
    db_path = "db.sqlite3"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Contar por tipo
        cursor.execute("""
            SELECT tipo, COUNT(*) 
            FROM mesero_opcionpersonalizacion 
            GROUP BY tipo
        """)
        
        tipos = cursor.fetchall()
        for tipo, count in tipos:
            print(f"{tipo}: {count} opciones")
        
        # Total productos con personalizaciones
        cursor.execute("""
            SELECT COUNT(DISTINCT producto_id) 
            FROM mesero_productopersonalizacion
        """)
        productos_con_personalizacion = cursor.fetchone()[0]
        print(f"\nProductos con personalizaciones: {productos_con_personalizacion}")
        
        # Mostrar algunos ejemplos
        cursor.execute("""
            SELECT p.nombre, o.nombre, o.tipo, o.precio_extra
            FROM mesero_productopersonalizacion pp
            JOIN restaurant_productoventa p ON pp.producto_id = p.id
            JOIN mesero_opcionpersonalizacion o ON pp.opcion_id = o.id
            WHERE p.nombre LIKE '%roll%' OR p.nombre LIKE '%maki%'
            LIMIT 10
        """)
        
        ejemplos = cursor.fetchall()
        if ejemplos:
            print("\nEjemplos de personalización:")
            for producto, opcion, tipo, precio in ejemplos:
                print(f"  {producto} - {opcion} ({tipo}) +${precio}")
        
        print("\n✅ Sistema de personalización configurado exitosamente")
        
    finally:
        conn.close()

def main():
    """Función principal"""
    try:
        insertar_opciones_personalizacion()
        asignar_a_productos()
        mostrar_resumen()
        
        print("\n🎯 PERSONALIZACIÓN LISTA PARA USAR")
        print("Ahora puedes actualizar la interfaz del mesero")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
