import os
import django
import sys
import requests
import json
from decimal import Decimal

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from restaurant.models import CategoriaProducto, Receta, ProductoVenta, RecetaInsumo, Insumo, UnidadMedida, CategoriaInsumo

User = get_user_model()

def verificar_funcionalidad_recetas():
    """
    Verifica que la funcionalidad de recetas esté trabajando correctamente
    """
    print("Verificando funcionalidad de recetas...")
    
    # Verificar categorías de productos
    categorias = CategoriaProducto.objects.all()
    print(f"Categorías disponibles: {categorias.count()}")
    for cat in categorias:
        print(f"  - {cat.nombre}")
    
    # Verificar recetas
    recetas = Receta.objects.select_related('producto').all()
    print(f"\nRecetas disponibles: {recetas.count()}")
    for receta in recetas:
        print(f"  - {receta.producto.nombre} (ID: {receta.id})")
        ingredientes = RecetaInsumo.objects.filter(receta=receta)
        print(f"    Ingredientes: {ingredientes.count()}")
        
        # Mostrar detalles detallados de la receta
        print(f"    Categoría: {receta.producto.categoria.nombre if receta.producto.categoria else 'Sin categoría'}")
        print(f"    Porciones: {receta.porciones}")
        print(f"    Tiempo de preparación: {receta.tiempo_preparacion} minutos")
        print(f"    Precio de venta: ${float(receta.producto.precio):.2f}")
        
        # Calcular y mostrar costo total
        costo_total = Decimal('0.00')
        for ingrediente in ingredientes:
            precio_unitario = ingrediente.insumo.precio_unitario or Decimal('0.00')
            cantidad = ingrediente.cantidad or Decimal('0.00')
            costo_ingrediente = precio_unitario * cantidad
            costo_total += costo_ingrediente
            
            print(f"      - {ingrediente.insumo.nombre}: {cantidad} {ingrediente.insumo.unidad_medida.nombre if ingrediente.insumo.unidad_medida else 'unidad'}, Costo: ${float(costo_ingrediente):.2f}")
        
        print(f"    Costo Total: ${float(costo_total):.2f}")
        
        # Actualizar el costo del producto si es diferente
        if receta.producto.costo != costo_total:
            receta.producto.costo = costo_total
            receta.producto.save()
            print(f"    ✓ Costo actualizado en el producto")
    
    print("\nVerificación de funcionalidad de recetas completada.")
    
def agregar_ingredientes_prueba():
    """
    Agrega ingredientes de prueba a las recetas existentes
    """
    print("\nAgregando ingredientes de prueba a las recetas...")
    
    # Obtener todas las recetas
    recetas = Receta.objects.all()
    
    if not recetas.exists():
        print("No hay recetas disponibles para agregar ingredientes.")
        return
      # Obtener unidades de medida existentes o crear nuevas
    try:
        unidad_gramos = UnidadMedida.objects.get(nombre="Gramos")
        print("  - Unidad 'Gramos' ya existe")
    except UnidadMedida.DoesNotExist:
        unidad_gramos = UnidadMedida.objects.create(
            nombre="Gramos",
            abreviacion="gr"
        )
        print("  ✓ Unidad 'Gramos' creada")
    
    try:
        unidad_unidades = UnidadMedida.objects.get(nombre="Unidad")
        print("  - Unidad 'Unidad' ya existe")
    except UnidadMedida.DoesNotExist:
        unidad_unidades = UnidadMedida.objects.create(
            nombre="Unidad",
            abreviacion="un"
        )
        print("  ✓ Unidad 'Unidad' creada")
    
    # Crear insumos de prueba si no existen
    insumo1, created = Insumo.objects.get_or_create(
        nombre="Arroz para sushi",
        defaults={
            'codigo': 'INS001',
            'descripcion': 'Arroz especial para sushi',
            'tipo': 'basico',
            'unidad_medida': unidad_gramos,
            'precio_unitario': Decimal('0.02'),  # precio por gramo
            'stock_minimo': 1000,
            'stock_actual': 5000
        }
    )
    if created:
        print(f"  ✓ Insumo creado: {insumo1.nombre}")
    
    insumo2, created = Insumo.objects.get_or_create(
        nombre="Alga Nori",
        defaults={
            'codigo': 'INS002',
            'descripcion': 'Alga para envolver sushi',
            'tipo': 'basico',
            'unidad_medida': unidad_unidades,
            'precio_unitario': Decimal('0.50'),  # precio por unidad
            'stock_minimo': 50,
            'stock_actual': 200
        }
    )
    if created:
        print(f"  ✓ Insumo creado: {insumo2.nombre}")
    
    insumo3, created = Insumo.objects.get_or_create(
        nombre="Salmón fresco",
        defaults={
            'codigo': 'INS003',
            'descripcion': 'Salmón de alta calidad para sushi',
            'tipo': 'basico',
            'unidad_medida': unidad_gramos,
            'precio_unitario': Decimal('0.05'),  # precio por gramo
            'stock_minimo': 500,
            'stock_actual': 2000
        }
    )
    if created:
        print(f"  ✓ Insumo creado: {insumo3.nombre}")
    
    # Para cada receta, agregar ingredientes si no tiene ninguno
    for receta in recetas:
        ingredientes = RecetaInsumo.objects.filter(receta=receta)
        
        if ingredientes.count() == 0:
            print(f"  Agregando ingredientes a: {receta.producto.nombre}")
            
            # Agregar arroz
            RecetaInsumo.objects.create(
                receta=receta,
                insumo=insumo1,
                cantidad=Decimal('200'),  # 200 gramos
                opcional=False
            )
            
            # Agregar alga nori
            RecetaInsumo.objects.create(
                receta=receta,
                insumo=insumo2,
                cantidad=Decimal('2'),  # 2 unidades
                opcional=False
            )
            
            # Agregar salmón
            RecetaInsumo.objects.create(
                receta=receta,
                insumo=insumo3,
                cantidad=Decimal('100'),  # 100 gramos
                opcional=False
            )
            
            print(f"    ✓ 3 ingredientes añadidos")
        else:
            print(f"  La receta {receta.producto.nombre} ya tiene ingredientes ({ingredientes.count()})")
    
    print("Ingredientes de prueba agregados correctamente.")

if __name__ == "__main__":
    agregar_ingredientes_prueba()  # Primero agregamos ingredientes de prueba si faltan
    verificar_funcionalidad_recetas()  # Luego verificamos el estado
