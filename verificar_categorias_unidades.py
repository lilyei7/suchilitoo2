#!/usr/bin/env python3
"""
Script para verificar que hay categorías y unidades en la base de datos
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import CategoriaInsumo, UnidadMedida

def main():
    print("🔍 Verificando datos de categorías y unidades...")
    
    # Verificar categorías
    categorias = CategoriaInsumo.objects.all()
    print(f"📁 Total de categorías: {categorias.count()}")
    for cat in categorias:
        print(f"  - ID: {cat.id}, Nombre: {cat.nombre}")
    
    # Verificar unidades
    unidades = UnidadMedida.objects.all()
    print(f"📏 Total de unidades: {unidades.count()}")
    for unidad in unidades:
        print(f"  - ID: {unidad.id}, Nombre: {unidad.nombre}, Abrev: {unidad.abreviacion}")
    
    if categorias.count() == 0:
        print("\n⚠️ No hay categorías. Creando algunas de ejemplo...")
        CategoriaInsumo.objects.create(nombre="Vegetales", descripcion="Verduras y hortalizas")
        CategoriaInsumo.objects.create(nombre="Proteínas", descripcion="Carnes y pescados")
        CategoriaInsumo.objects.create(nombre="Condimentos", descripcion="Especias y condimentos")
        print("✅ Categorías de ejemplo creadas")
    
    if unidades.count() == 0:
        print("\n⚠️ No hay unidades. Creando algunas de ejemplo...")
        UnidadMedida.objects.create(nombre="Kilogramo", abreviacion="kg", tipo="peso")
        UnidadMedida.objects.create(nombre="Litro", abreviacion="l", tipo="volumen")
        UnidadMedida.objects.create(nombre="Unidad", abreviacion="ud", tipo="cantidad")
        UnidadMedida.objects.create(nombre="Gramo", abreviacion="g", tipo="peso")
        print("✅ Unidades de ejemplo creadas")
    
    print(f"\n📊 Estado final:")
    print(f"  - Total categorías: {CategoriaInsumo.objects.count()}")
    print(f"  - Total unidades: {UnidadMedida.objects.count()}")

if __name__ == '__main__':
    main()
