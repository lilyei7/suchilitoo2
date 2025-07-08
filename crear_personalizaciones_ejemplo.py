#!/usr/bin/env python3
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import OpcionPersonalizacion, ProductoPersonalizacion
from restaurant.models import ProductoVenta

def crear_personalizaciones_ejemplo():
    """Crear opciones de personalización de ejemplo"""
    print("Creando opciones de personalización de ejemplo...")    # Crear opciones de personalización
    opciones = [
        # Opciones generales
        {"nombre": "Sin cebolla", "tipo": "omitir", "categoria": "vegetales", "precio_extra": 0.00},
        {"nombre": "Sin pimiento", "tipo": "omitir", "categoria": "vegetales", "precio_extra": 0.00},
        {"nombre": "Sin pepino", "tipo": "omitir", "categoria": "vegetales", "precio_extra": 0.00},
        {"nombre": "Sin cilantro", "tipo": "omitir", "categoria": "vegetales", "precio_extra": 0.00},
        {"nombre": "Sin jengibre", "tipo": "omitir", "categoria": "condimentos", "precio_extra": 0.00},
        
        # Opciones de adición
        {"nombre": "Extra aguacate", "tipo": "agregar", "categoria": "extras", "precio_extra": 2.00},
        {"nombre": "Extra queso", "tipo": "agregar", "categoria": "extras", "precio_extra": 1.50},
        {"nombre": "Extra salmón", "tipo": "agregar", "categoria": "proteinas", "precio_extra": 4.00},
        {"nombre": "Extra atún", "tipo": "agregar", "categoria": "proteinas", "precio_extra": 3.50},
        {"nombre": "Extra salsa teriyaki", "tipo": "agregar", "categoria": "salsas", "precio_extra": 0.50},
        {"nombre": "Extra salsa picante", "tipo": "agregar", "categoria": "salsas", "precio_extra": 0.50},
        {"nombre": "Extra wasabi", "tipo": "agregar", "categoria": "condimentos", "precio_extra": 0.30},
        
        # Opciones de sustitución
        {"nombre": "Arroz integral", "tipo": "cambiar", "categoria": "base", "precio_extra": 1.00},
        {"nombre": "Sin arroz", "tipo": "omitir", "categoria": "base", "precio_extra": 0.00},
        {"nombre": "Con quinoa", "tipo": "cambiar", "categoria": "base", "precio_extra": 2.00},
        
        # Opciones de preparación
        {"nombre": "Menos picante", "tipo": "modificar", "categoria": "preparacion", "precio_extra": 0.00},
        {"nombre": "Más picante", "tipo": "modificar", "categoria": "preparacion", "precio_extra": 0.00},
        {"nombre": "Sin sal", "tipo": "omitir", "categoria": "condimentos", "precio_extra": 0.00},
        {"nombre": "Poca sal", "tipo": "modificar", "categoria": "condimentos", "precio_extra": 0.00},
        {"nombre": "Templado", "tipo": "modificar", "categoria": "preparacion", "precio_extra": 0.00},
    ]
    
    opciones_creadas = []
    for opcion_data in opciones:
        try:
            opcion, created = OpcionPersonalizacion.objects.get_or_create(
                nombre=opcion_data["nombre"],
                defaults={
                    "tipo": opcion_data["tipo"],
                    "categoria": opcion_data["categoria"],
                    "precio_extra": opcion_data["precio_extra"],
                    "activa": True
                }
            )
            opciones_creadas.append(opcion)
            if created:
                print(f"✓ Creada: {opcion.nombre}")
            else:
                print(f"- Ya existe: {opcion.nombre}")
        except Exception as e:
            print(f"Error creating option {opcion_data['nombre']}: {e}")
            # Try to create with direct SQL instead
            import sqlite3
            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO mesero_opcionpersonalizacion 
                    (nombre, tipo, categoria, precio_extra, activa) 
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    opcion_data["nombre"],
                    opcion_data["tipo"],
                    opcion_data["categoria"],
                    opcion_data["precio_extra"],
                    True
                ))
                conn.commit()
                print(f"✓ Creada (SQL): {opcion_data['nombre']}")
            except Exception as sql_error:
                print(f"SQL Error: {sql_error}")
            finally:
                conn.close()
    
    print(f"\nTotal opciones disponibles: {len(opciones_creadas)}")
    
    # Asignar opciones a productos
    print("\nAsignando opciones a productos...")
    
    productos = ProductoVenta.objects.filter(disponible=True)[:10]  # Primeros 10 productos
    
    for producto in productos:
        print(f"\nAsignando opciones a: {producto.nombre}")
        
        # Asignar opciones básicas a todos los productos
        opciones_basicas = OpcionPersonalizacion.objects.filter(
            tipo__in=["omitir", "modificar"],
            categoria__in=["vegetales", "condimentos", "preparacion"]
        )
        
        for opcion in opciones_basicas:
            ProductoPersonalizacion.objects.get_or_create(
                producto=producto,
                opcion=opcion,
                defaults={"activa": True}
            )
        
        # Asignar opciones de extras seleccionadas según el tipo de producto
        if any(palabra in producto.nombre.lower() for palabra in ["roll", "sushi", "maki"]):
            # Para rolls y sushi, agregar opciones de proteínas y extras
            opciones_sushi = OpcionPersonalizacion.objects.filter(
                categoria__in=["proteinas", "extras", "salsas"]
            )
            
            for opcion in opciones_sushi:
                ProductoPersonalizacion.objects.get_or_create(
                    producto=producto,
                    opcion=opcion,
                    defaults={"activa": True}
                )
        
        if any(palabra in producto.nombre.lower() for palabra in ["bowl", "poke", "ensalada"]):
            # Para bowls y pokes, agregar opciones de base y extras
            opciones_bowl = OpcionPersonalizacion.objects.filter(
                categoria__in=["base", "extras", "salsas"]
            )
            
            for opcion in opciones_bowl:
                ProductoPersonalizacion.objects.get_or_create(
                    producto=producto,
                    opcion=opcion,
                    defaults={"activa": True}
                )
        
        # Contar opciones asignadas
        opciones_asignadas = ProductoPersonalizacion.objects.filter(
            producto=producto,
            activa=True
        ).count()
        
        print(f"  → {opciones_asignadas} opciones asignadas")
    
    print("\n✓ Personalización de ejemplo creada exitosamente!")
    print("\nOpciones disponibles por categoría:")
    
    categorias = OpcionPersonalizacion.objects.values_list('categoria', flat=True).distinct()
    for categoria in categorias:
        count = OpcionPersonalizacion.objects.filter(categoria=categoria, activa=True).count()
        print(f"  - {categoria.title()}: {count} opciones")

if __name__ == "__main__":
    crear_personalizaciones_ejemplo()
