#!/usr/bin/env python
"""
Script para actualizar los nombres de las recetas en la base de datos.

Este script actualiza los nombres de las recetas basándose en los productos asociados.
Si una receta tiene un producto, su nombre será "Receta de [nombre del producto]".
Si una receta no tiene producto, se le asignará un nombre genérico con su ID.

Uso:
    python actualizar_nombres_recetas.py         # Actualizar nombres y mostrar listado
    python actualizar_nombres_recetas.py --listar # Solo mostrar listado sin actualizar
"""
import os
import django
import sys
import logging

# Desactivar completamente los logs de SQL
import django.db.backends.utils
django.db.backends.utils.CursorDebugWrapper = django.db.backends.utils.CursorWrapper

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

# Importar modelos después de configurar Django
from restaurant.models import Receta

def actualizar_nombres_recetas():
    """Actualiza los nombres de las recetas según sus productos asociados"""
    print("\n=== ACTUALIZACIÓN DE NOMBRES DE RECETAS ===")
    print("Iniciando actualización de nombres de recetas...")
    
    # Obtener todas las recetas
    recetas = Receta.objects.all()
    total = recetas.count()
    print(f"Se encontraron {total} recetas en total")
    
    # Actualizar nombres de recetas
    recetas_actualizadas = 0
    recetas_con_producto = 0
    recetas_sin_producto = 0
    
    for receta in recetas:
        nombre_original = receta.nombre
        
        # Si la receta tiene un producto asociado, usar el nombre del producto
        if receta.producto:
            nuevo_nombre = f"Receta de {receta.producto.nombre}"
            recetas_con_producto += 1
        else:
            # Si no tiene producto asociado, asignar un nombre personalizado
            if nombre_original == "Receta" or not nombre_original:
                nuevo_nombre = f"Receta sin producto #{receta.id}"
            else:
                # Si ya tiene un nombre personalizado que no es "Receta", mantenerlo
                nuevo_nombre = nombre_original
                print(f"Manteniendo nombre personalizado existente: '{nombre_original}' (ID: {receta.id})")
                continue
            recetas_sin_producto += 1
        
        # Si el nombre actual es diferente al nuevo nombre, actualizar
        if nombre_original != nuevo_nombre:
            receta.nombre = nuevo_nombre
            receta.save()
            recetas_actualizadas += 1
            print(f'Actualizado nombre de receta ID {receta.id}: "{nombre_original}" → "{nuevo_nombre}"')
    
    # Resumen de las actualizaciones
    print("\n=== RESUMEN DE ACTUALIZACIÓN ===")
    print(f"Total de recetas procesadas: {total}")
    print(f"Recetas con producto asociado: {recetas_con_producto}")
    print(f"Recetas sin producto asociado: {recetas_sin_producto}")
    print(f"Recetas con nombres actualizados: {recetas_actualizadas}")
    
    if recetas_actualizadas == 0:
        print('No se actualizó ninguna receta. Todas tienen nombres apropiados.')
    else:
        print(f'Se actualizaron {recetas_actualizadas} recetas correctamente.')

def mostrar_recetas():
    """Muestra todas las recetas en la base de datos con sus nombres actuales"""
    print("\n=== LISTADO DE RECETAS ACTUALES ===")
    recetas = Receta.objects.all().order_by('id')
    
    if not recetas:
        print("No hay recetas en la base de datos.")
        return
    
    print(f"{'ID':<5} {'NOMBRE':<50} {'PRODUCTO':<30} {'ACTIVO':<10}")
    print("-" * 95)
    
    for receta in recetas:
        producto_nombre = receta.producto.nombre if receta.producto else "Sin producto"
        activo = "Sí" if receta.activo else "No"
        print(f"{receta.id:<5} {receta.nombre[:50]:<50} {producto_nombre[:30]:<30} {activo:<10}")
    
    print(f"\nTotal: {recetas.count()} recetas")

if __name__ == "__main__":
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1 and sys.argv[1] == '--listar':
        mostrar_recetas()
    else:
        actualizar_nombres_recetas()
        # Mostrar listado después de la actualización
        mostrar_recetas()

if __name__ == "__main__":
    actualizar_nombres_recetas()
