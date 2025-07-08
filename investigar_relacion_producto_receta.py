#!/usr/bin/env python
"""
Script para investigar la relación entre productos y recetas
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

try:
    django.setup()
except Exception as e:
    print(f"Error al configurar Django: {e}")
    sys.exit(1)

from restaurant.models import ProductoVenta, Receta
from django.db import connection

def main():
    print("🔍 INVESTIGANDO RELACIÓN PRODUCTO-RECETA")
    print("=" * 60)
    
    # 1. Ver la estructura de las tablas
    print("📋 ESTRUCTURA DE LA RELACIÓN:")
    
    # Verificar si hay campo receta_id en ProductoVenta
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(restaurant_productoventa)")
        columns = cursor.fetchall()
        
        print("\n🍱 Campos en ProductoVenta:")
        for col in columns:
            if 'receta' in col[1].lower():
                print(f"   ✅ {col[1]} ({col[2]})")
    
    # Verificar campos en Receta
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(restaurant_receta)")
        columns = cursor.fetchall()
        
        print("\n📋 Campos en Receta:")
        for col in columns:
            if 'producto' in col[1].lower():
                print(f"   ✅ {col[1]} ({col[2]})")
    
    # 2. Investigar los productos con algas específicamente
    print("\n" + "=" * 60)
    print("🔍 ANÁLISIS DE PRODUCTOS CON ALGAS:")
    
    productos = ProductoVenta.objects.filter(nombre__icontains='algas').order_by('id')
    
    for producto in productos:
        print(f"\n🍱 Producto ID {producto.id}: '{producto.nombre}'")
        
        # Buscar todas las recetas relacionadas con este producto
        recetas = Receta.objects.filter(producto=producto)
        print(f"   📋 Recetas encontradas: {recetas.count()}")
        
        if recetas.exists():
            for i, receta in enumerate(recetas, 1):
                print(f"      {i}. Receta ID {receta.id}")
                print(f"         Tiempo: {receta.tiempo_preparacion} min")
                print(f"         Porciones: {receta.porciones}")
                print(f"         Activa: {receta.activo}")
                
                # Ver insumos de esta receta
                try:
                    from restaurant.models import RecetaInsumo
                    insumos = RecetaInsumo.objects.filter(receta=receta)
                    print(f"         Insumos: {insumos.count()}")
                    for insumo_receta in insumos:
                        print(f"           • {insumo_receta.insumo.nombre}: {insumo_receta.cantidad} {insumo_receta.insumo.unidad_medida.abreviacion}")
                except Exception as e:
                    print(f"         ❌ Error obteniendo insumos: {e}")
        else:
            print("   ❌ Sin recetas asociadas")
    
    # 3. Verificar si hay relación inversa (recetas sin producto)
    print("\n" + "=" * 60)
    print("🔍 RECETAS SIN PRODUCTO ASOCIADO:")
    
    recetas_sin_producto = Receta.objects.filter(producto__isnull=True)
    print(f"📋 Recetas huérfanas: {recetas_sin_producto.count()}")
    
    for receta in recetas_sin_producto:
        print(f"   • Receta ID {receta.id} - Sin producto")

if __name__ == "__main__":
    main()
