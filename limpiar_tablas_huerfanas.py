#!/usr/bin/env python
"""
Script para limpiar tablas huérfanas en la base de datos.
Estas son tablas que no tienen modelos Django correspondientes pero pueden tener
referencias a modelos existentes que impiden operaciones de eliminación.

Uso: python limpiar_tablas_huerfanas.py

ADVERTENCIA: Este script elimina datos. Úselo solo si está seguro de que
los datos en las tablas huérfanas no son necesarios.
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.db import connection
from restaurant.models import ProductoVenta


def encontrar_tablas_huerfanas():
    """Encuentra tablas que no tienen modelos Django pero referencian ProductoVenta"""
    
    from django.apps import apps
    
    # Obtener todas las tablas de la base de datos
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        db_tables = [row[0] for row in cursor.fetchall()]
    
    # Obtener todas las tablas que tienen modelos Django
    django_tables = set()
    for model in apps.get_models():
        django_tables.add(model._meta.db_table)
    
    # Encontrar tablas huérfanas
    tablas_huerfanas = []
    for tabla in db_tables:
        if tabla not in django_tables:
            # Verificar si la tabla tiene una columna producto_id
            with connection.cursor() as cursor:
                try:
                    cursor.execute(f"PRAGMA table_info({tabla})")
                    columns = cursor.fetchall()
                    column_names = [col[1] for col in columns]
                    
                    if 'producto_id' in column_names:
                        tablas_huerfanas.append(tabla)
                except Exception as e:
                    print(f"Error verificando tabla {tabla}: {e}")
    
    return tablas_huerfanas


def verificar_referencias_productos(tablas_huerfanas):
    """Verifica qué productos tienen referencias en tablas huérfanas"""
    
    referencias = {}
    
    for tabla in tablas_huerfanas:
        with connection.cursor() as cursor:
            try:
                cursor.execute(f"SELECT producto_id, COUNT(*) as count FROM {tabla} GROUP BY producto_id")
                resultados = cursor.fetchall()
                
                if resultados:
                    referencias[tabla] = resultados
                    print(f"\nTabla huérfana: {tabla}")
                    for producto_id, count in resultados:
                        try:
                            producto = ProductoVenta.objects.get(id=producto_id)
                            print(f"  - Producto ID {producto_id} ({producto.nombre}): {count} referencias")
                        except ProductoVenta.DoesNotExist:
                            print(f"  - Producto ID {producto_id} (NO EXISTE): {count} referencias")
                            
            except Exception as e:
                print(f"Error verificando referencias en {tabla}: {e}")
    
    return referencias


def limpiar_tabla_huerfana(tabla, producto_id=None):
    """Limpia una tabla huérfana completamente o solo para un producto específico"""
    
    with connection.cursor() as cursor:
        try:
            if producto_id:
                cursor.execute(f"DELETE FROM {tabla} WHERE producto_id = ?", [producto_id])
                count = cursor.rowcount
                print(f"Eliminados {count} registros de {tabla} para producto ID {producto_id}")
            else:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                total = cursor.fetchone()[0]
                
                cursor.execute(f"DELETE FROM {tabla}")
                count = cursor.rowcount
                print(f"Eliminados {count} de {total} registros de {tabla}")
                
        except Exception as e:
            print(f"Error limpiando tabla {tabla}: {e}")


def main():
    print("=== LIMPIADOR DE TABLAS HUÉRFANAS ===")
    print("Buscando tablas huérfanas...")
    
    tablas_huerfanas = encontrar_tablas_huerfanas()
    
    if not tablas_huerfanas:
        print("No se encontraron tablas huérfanas con referencias a productos.")
        return
    
    print(f"Encontradas {len(tablas_huerfanas)} tablas huérfanas:")
    for tabla in tablas_huerfanas:
        print(f"  - {tabla}")
    
    print("\nVerificando referencias...")
    referencias = verificar_referencias_productos(tablas_huerfanas)
    
    if not referencias:
        print("No se encontraron referencias a productos en las tablas huérfanas.")
        return
    
    print(f"\n=== RESUMEN ===")
    total_referencias = 0
    for tabla, refs in referencias.items():
        count = sum(ref[1] for ref in refs)
        total_referencias += count
        print(f"{tabla}: {count} referencias")
    
    print(f"Total de referencias huérfanas: {total_referencias}")
    
    if total_referencias > 0:
        respuesta = input("\n¿Desea eliminar TODAS las referencias huérfanas? (sí/no): ")
        
        if respuesta.lower() in ['sí', 'si', 'yes', 'y']:
            print("\nLimpiando tablas huérfanas...")
            
            for tabla in referencias.keys():
                limpiar_tabla_huerfana(tabla)
            
            print("\n=== LIMPIEZA COMPLETADA ===")
            print("Las tablas huérfanas han sido limpiadas.")
            print("Ahora debería poder eliminar productos sin errores de integridad.")
        else:
            print("Operación cancelada.")
    

if __name__ == '__main__':
    main()
