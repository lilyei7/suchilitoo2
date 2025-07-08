import django
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.db import connection
from restaurant.models import ProductoVenta

def insertar_opciones_personalizacion():
    """Insertar opciones de personalización directamente en la base de datos"""
    print("=== INSERTANDO OPCIONES DE PERSONALIZACIÓN ===")
    
    with connection.cursor() as cursor:
        # Limpiar tablas existentes
        cursor.execute("DELETE FROM mesero_productopersonalizacion")
        cursor.execute("DELETE FROM mesero_opcionpersonalizacion")
        
        # Opciones para quitar ingredientes
        opciones_quitar = [
            "Sin cebolla",
            "Sin ajonjolí", 
            "Sin aguacate",
            "Sin pepino",
            "Sin zanahoria",
            "Sin salsa de soya",
            "Sin wasabi",
            "Sin jengibre",
            "Sin alga nori",
            "Sin picante",
            "Sin salsa teriyaki",
            "Sin salsa de anguila",
        ]
        
        # Opciones para agregar extras
        opciones_agregar = [
            ("Extra aguacate", 15.00),
            ("Extra salmón", 25.00),
            ("Extra atún", 30.00),
            ("Extra queso crema", 10.00),
            ("Extra tempura", 20.00),
            ("Extra ajonjolí", 5.00),
            ("Extra salsa spicy", 8.00),
            ("Extra wasabi", 5.00),
            ("Extra jengibre", 5.00),
            ("Porción extra de arroz", 12.00),
        ]
        
        # Insertar opciones de quitar
        for opcion in opciones_quitar:
            cursor.execute("""
                INSERT INTO mesero_opcionpersonalizacion 
                (nombre, tipo, precio_extra, activa, categoria_id)
                VALUES (?, ?, ?, ?, ?)
            """, [opcion, 'quitar', 0.00, 1, None])
            print(f"✓ Insertada opción: {opcion}")
        
        # Insertar opciones de agregar
        for opcion, precio in opciones_agregar:
            cursor.execute("""
                INSERT INTO mesero_opcionpersonalizacion 
                (nombre, tipo, precio_extra, activa, categoria_id)
                VALUES (?, ?, ?, ?, ?)
            """, [opcion, 'agregar', precio, 1, None])
            print(f"✓ Insertada opción: {opcion} (+${precio})")
        
        # Insertar opción de nota especial
        cursor.execute("""
            INSERT INTO mesero_opcionpersonalizacion 
            (nombre, tipo, precio_extra, activa, categoria_id)
            VALUES (?, ?, ?, ?, ?)
        """, ["Nota especial", 'nota', 0.00, 1, None])
        print("✓ Insertada opción: Nota especial")
        
        # Verificar inserción
        cursor.execute("SELECT COUNT(*) FROM mesero_opcionpersonalizacion")
        total_opciones = cursor.fetchone()[0]
        print(f"\n✅ Total opciones insertadas: {total_opciones}")

def asignar_opciones_a_productos():
    """Asignar opciones básicas a todos los productos"""
    print("\n=== ASIGNANDO OPCIONES A PRODUCTOS ===")
    
    with connection.cursor() as cursor:
        # Obtener todos los productos disponibles
        productos = ProductoVenta.objects.filter(disponible=True)
        
        # Opciones básicas que se asignarán a todos los productos
        opciones_basicas = [
            "Sin cebolla",
            "Sin picante", 
            "Sin wasabi",
            "Sin jengibre",
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
                """, [opcion_nombre])
                
                result = cursor.fetchone()
                if result:
                    opcion_id = result[0]
                    
                    # Verificar si ya existe la asignación
                    cursor.execute("""
                        SELECT COUNT(*) FROM mesero_productopersonalizacion 
                        WHERE producto_id = %s AND opcion_id = %s
                    """, [producto.id, opcion_id])
                    
                    if cursor.fetchone()[0] == 0:
                        # Insertar asignación
                        cursor.execute("""
                            INSERT INTO mesero_productopersonalizacion 
                            (producto_id, opcion_id, activa)
                            VALUES (%s, %s, %s)
                        """, [producto.id, opcion_id, 1])
                        print(f"  ✓ {opcion_nombre}")
        
        # Verificar asignaciones
        cursor.execute("SELECT COUNT(*) FROM mesero_productopersonalizacion")
        total_asignaciones = cursor.fetchone()[0]
        print(f"\n✅ Total asignaciones: {total_asignaciones}")

def mostrar_resumen():
    """Mostrar resumen de configuración"""
    print("\n=== RESUMEN DE CONFIGURACIÓN ===")
    
    with connection.cursor() as cursor:
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
        
        print("\n✅ Sistema de personalización configurado exitosamente")

def main():
    """Función principal"""
    try:
        insertar_opciones_personalizacion()
        asignar_opciones_a_productos()
        mostrar_resumen()
        
        print("\n🎯 PERSONALIZACIÓN LISTA PARA USAR")
        print("Ahora puedes actualizar la interfaz del mesero")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
