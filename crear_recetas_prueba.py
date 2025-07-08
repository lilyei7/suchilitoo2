#!/usr/bin/env python3
"""
Script para crear recetas de prueba para los productos existentes
"""

import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.db import transaction
from restaurant.models import (
    ProductoVenta, Receta, RecetaInsumo, Insumo, CategoriaProducto
)

def crear_recetas_prueba():
    """Crea recetas de prueba para productos existentes"""
    print("🍣 CREANDO RECETAS DE PRUEBA")
    print("=" * 60)
    
    # Buscar productos disponibles
    productos = ProductoVenta.objects.filter(disponible=True)[:5]
    insumos = Insumo.objects.filter(activo=True)
    
    if not productos.exists():
        print("❌ No hay productos disponibles")
        return
    
    if not insumos.exists():
        print("❌ No hay insumos disponibles")
        return
    
    print(f"📋 Productos encontrados: {productos.count()}")
    print(f"🧪 Insumos disponibles: {insumos.count()}")
    
    # Mapear algunos insumos básicos
    insumos_map = {}
    for insumo in insumos:
        insumos_map[insumo.nombre.lower()] = insumo
    
    # Crear recetas para productos específicos
    recetas_creadas = 0
    
    try:
        with transaction.atomic():
            for producto in productos:
                # Verificar si ya tiene receta
                if hasattr(producto, 'receta'):
                    print(f"⚠️  {producto.nombre} ya tiene receta")
                    continue
                
                print(f"\n🍱 Creando receta para: {producto.nombre}")
                
                # Crear receta básica
                receta = Receta.objects.create(
                    producto=producto,
                    tiempo_preparacion=15,
                    porciones=1,
                    instrucciones="Preparar según receta estándar",
                    notas="Receta de prueba generada automáticamente",
                    activo=True
                )
                
                # Agregar ingredientes según el tipo de producto
                ingredientes_agregados = 0
                
                if 'california' in producto.nombre.lower():
                    # California Roll
                    ingredientes = [
                        ('arroz para sushi', 200),  # 200g
                        ('alga nori', 1),          # 1 hoja
                        ('salmón fresco', 100),    # 100g
                        ('palta', 50),             # 50g
                        ('pepino', 30),            # 30g
                        ('semillas de sésamo', 10) # 10g
                    ]
                    
                elif 'ramen' in producto.nombre.lower():
                    # Ramen
                    ingredientes = [
                        ('arroz para sushi', 150),  # 150g (como fideos)
                        ('salmón fresco', 80),      # 80g
                        ('pepino', 20),             # 20g
                        ('salsa de soja', 30),      # 30ml
                        ('alga nori', 1),           # 1 hoja
                    ]
                    
                elif 'sushi' in producto.nombre.lower():
                    # Sushi genérico
                    ingredientes = [
                        ('arroz para sushi', 120),  # 120g
                        ('alga nori', 1),           # 1 hoja
                        ('salmón fresco', 80),      # 80g
                        ('wasabi', 5),              # 5g
                        ('salsa de soja', 20),      # 20ml
                    ]
                    
                elif 'gyoza' in producto.nombre.lower():
                    # Gyozas
                    ingredientes = [
                        ('arroz para sushi', 50),   # 50g (como masa)
                        ('pepino', 40),             # 40g
                        ('salsa de soja', 20),      # 20ml
                        ('sesamo', 5),              # 5g
                    ]
                    
                elif 'tempura' in producto.nombre.lower():
                    # Tempura
                    ingredientes = [
                        ('arroz para sushi', 100),  # 100g (como harina)
                        ('pepino', 80),             # 80g
                        ('palta', 60),              # 60g
                        ('salsa de soja', 25),      # 25ml
                    ]
                    
                else:
                    # Receta genérica
                    ingredientes = [
                        ('arroz para sushi', 100),  # 100g
                        ('alga nori', 1),           # 1 hoja
                        ('salmón fresco', 60),      # 60g
                        ('pepino', 30),             # 30g
                        ('salsa de soja', 15),      # 15ml
                    ]
                
                # Agregar ingredientes a la receta
                for nombre_ingrediente, cantidad in ingredientes:
                    # Buscar el insumo correspondiente
                    insumo = None
                    for insumo_disponible in insumos:
                        if nombre_ingrediente.lower() in insumo_disponible.nombre.lower():
                            insumo = insumo_disponible
                            break
                    
                    if insumo:
                        RecetaInsumo.objects.create(
                            receta=receta,
                            insumo=insumo,
                            cantidad=Decimal(str(cantidad)),
                            opcional=False
                        )
                        print(f"   ✅ Agregado: {cantidad} {insumo.unidad_medida.abreviacion} de {insumo.nombre}")
                        ingredientes_agregados += 1
                    else:
                        print(f"   ⚠️  No encontrado: {nombre_ingrediente}")
                
                if ingredientes_agregados > 0:
                    print(f"   🎯 Receta creada con {ingredientes_agregados} ingredientes")
                    recetas_creadas += 1
                else:
                    print(f"   ❌ No se pudieron agregar ingredientes")
                    receta.delete()
    
    except Exception as e:
        print(f"❌ Error creando recetas: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎉 Proceso completado: {recetas_creadas} recetas creadas")
    return recetas_creadas

def mostrar_recetas_creadas():
    """Muestra las recetas creadas"""
    print("\n📋 RECETAS CREADAS")
    print("=" * 60)
    
    recetas = Receta.objects.filter(activo=True).select_related('producto')
    
    for receta in recetas:
        print(f"🍱 {receta.producto.nombre}")
        print(f"   ⏱️  Tiempo: {receta.tiempo_preparacion} min")
        print(f"   🍽️  Porciones: {receta.porciones}")
        
        ingredientes = RecetaInsumo.objects.filter(receta=receta).select_related('insumo')
        if ingredientes.exists():
            print(f"   📋 Ingredientes:")
            for ing in ingredientes:
                print(f"      - {ing.cantidad} {ing.insumo.unidad_medida.abreviacion} de {ing.insumo.nombre}")
        else:
            print(f"   ⚠️  Sin ingredientes")
        print()

if __name__ == "__main__":
    recetas_creadas = crear_recetas_prueba()
    if recetas_creadas > 0:
        mostrar_recetas_creadas()
