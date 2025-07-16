#!/usr/bin/env python3
"""
Script para probar que la corrección de decimales funciona correctamente
"""

import os
import django
import sys

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from decimal import Decimal
from restaurant.models import Receta, RecetaInsumo, Insumo

def probar_precision_decimales():
    """
    Prueba que los decimales se guarden y muestren correctamente
    """
    print("=== PRUEBA DE PRECISIÓN DE DECIMALES ===")
    
    # Obtener la primera receta disponible
    receta = Receta.objects.first()
    if not receta:
        print("❌ No hay recetas disponibles para probar")
        return
        
    print(f"✅ Probando con la receta: {receta.nombre}")
    
    # Obtener el primer ingrediente de la receta
    ingrediente = RecetaInsumo.objects.filter(receta=receta).first()
    if not ingrediente:
        print("❌ La receta no tiene ingredientes")
        return
        
    print(f"✅ Probando con el ingrediente: {ingrediente.insumo.nombre}")
    
    # Probar diferentes valores con hasta 4 decimales
    valores_prueba = [
        Decimal('0.0001'),  # 4 decimales
        Decimal('0.025'),   # 3 decimales
        Decimal('0.33'),    # 2 decimales  
        Decimal('1.2345'),  # 4 decimales
        Decimal('10.5678'), # 4 decimales
    ]
    
    for valor in valores_prueba:
        print(f"\n🔍 Probando cantidad: {valor}")
        
        # Guardar el valor original
        cantidad_original = ingrediente.cantidad
        
        try:
            # Asignar nuevo valor
            ingrediente.cantidad = valor
            ingrediente.save()
            
            # Recargar desde la base de datos
            ingrediente.refresh_from_db()
            
            # Verificar que se guardó correctamente
            if ingrediente.cantidad == valor:
                print(f"  ✅ ÉXITO: Se guardó y recuperó correctamente: {ingrediente.cantidad}")
            else:
                print(f"  ❌ ERROR: Se guardó {valor} pero se recuperó {ingrediente.cantidad}")
                
        except Exception as e:
            print(f"  ❌ ERROR al guardar {valor}: {e}")
        
        # Restaurar valor original
        ingrediente.cantidad = cantidad_original
        ingrediente.save()
    
    print("\n=== PRUEBA COMPLETADA ===")

def mostrar_recetas_actuales():
    """
    Muestra las recetas actuales con sus nombres actualizados
    """
    print("\n=== RECETAS ACTUALES ===")
    
    recetas = Receta.objects.all()
    if not recetas:
        print("❌ No hay recetas en el sistema")
        return
    
    for receta in recetas:
        ingredientes_count = RecetaInsumo.objects.filter(receta=receta).count()
        print(f"ID: {receta.id:2d} | Nombre: {receta.nombre:30s} | Ingredientes: {ingredientes_count}")
        
        # Mostrar algunos ingredientes con sus cantidades
        ingredientes = RecetaInsumo.objects.filter(receta=receta)[:3]
        for ing in ingredientes:
            print(f"    - {ing.insumo.nombre}: {ing.cantidad} {ing.insumo.unidad_medida.abreviacion if ing.insumo.unidad_medida else 'Un'}")
    
    print(f"\nTotal: {recetas.count()} recetas")

if __name__ == "__main__":
    try:
        mostrar_recetas_actuales()
        probar_precision_decimales()
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
