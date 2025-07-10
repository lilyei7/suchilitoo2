#!/usr/bin/env python3
"""
Script para probar el flujo completo de creación de productos con recetas
"""

import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta, Receta, RecetaInsumo, CategoriaProducto, ProductoReceta
from accounts.models import Sucursal
from inventario_automatico import InventarioAutomatico

def test_crear_producto_con_receta():
    print("🧪 Probando creación de producto con receta automática")
    
    # 1. Buscar una receta existente para usar como template
    receta_template = Receta.objects.first()
    if not receta_template:
        print("❌ No se encontró ninguna receta template")
        return
    
    print(f"✅ Usando receta template: {receta_template.id}")
    
    # 2. Buscar una categoría
    categoria = CategoriaProducto.objects.first()
    if not categoria:
        print("❌ No se encontró ninguna categoría")
        return
    
    print(f"✅ Usando categoría: {categoria.nombre}")
    
    # 3. Crear producto de prueba
    nombre_producto = "Test Producto Auto"
    
    try:
        # Simular lo que hace el formulario
        producto = ProductoVenta.objects.create(
            codigo="TEST001",
            nombre=nombre_producto,
            descripcion="Producto de prueba con receta automática",
            precio=Decimal("15.00"),
            categoria=categoria,
            disponible=True,
            calorias=250
        )
        
        print(f"✅ Producto creado: {producto.nombre} (ID: {producto.id})")
        
        # 4. Asociar receta (simulando el código modificado)
        recetas_ids = [str(receta_template.id)]
        
        # Crear relación many-to-many
        ProductoReceta.objects.create(
            producto=producto,
            receta=receta_template
        )
        
        # 🆕 CREAR RECETA DIRECTA (OneToOneField) 
        if recetas_ids:
            # Usar la primera receta como receta directa
            primera_receta = Receta.objects.get(id=recetas_ids[0])
            
            # Crear una copia de la receta directamente asociada al producto
            receta_directa = Receta.objects.create(
                producto=producto,
                tiempo_preparacion=primera_receta.tiempo_preparacion,
                porciones=primera_receta.porciones,
                instrucciones=primera_receta.instrucciones,
                notas=primera_receta.notas,
                activo=primera_receta.activo
            )
            
            print(f"✅ Receta directa creada: ID {receta_directa.id}")
            
            # Copiar los insumos de la primera receta a la receta directa
            for receta_insumo in primera_receta.insumos.all():
                RecetaInsumo.objects.create(
                    receta=receta_directa,
                    insumo=receta_insumo.insumo,
                    cantidad=receta_insumo.cantidad,
                    orden=receta_insumo.orden,
                    opcional=receta_insumo.opcional,
                    notas=receta_insumo.notas
                )
            
            print(f"✅ Insumos copiados: {primera_receta.insumos.count()} insumos")
        
        # 5. Verificar que el producto ahora tiene ambas relaciones
        print("\\n🔍 Verificando relaciones creadas:")
        
        # Verificar relación directa
        try:
            receta_directa = producto.receta
            print(f"✅ Receta directa encontrada: ID {receta_directa.id}")
        except Exception as e:
            print(f"❌ Error en receta directa: {e}")
        
        # Verificar relación many-to-many
        relaciones = ProductoReceta.objects.filter(producto=producto)
        print(f"✅ Relaciones ProductoReceta: {relaciones.count()}")
        
        # 6. Probar con InventarioAutomatico
        print("\\n🔧 Probando con InventarioAutomatico:")
        
        sucursal = Sucursal.objects.first()
        if sucursal:
            inventario = InventarioAutomatico(sucursal)
            stock_ok, faltantes = inventario.verificar_stock_disponible(producto, 1)
            
            print(f"Stock OK: {stock_ok}")
            print(f"Faltantes: {faltantes}")
            
            if stock_ok:
                print("✅ El mesero PUEDE crear órdenes con este producto")
            else:
                print("❌ El mesero NO puede crear órdenes con este producto")
                for faltante in faltantes:
                    print(f"  - {faltante}")
        
        print("\\n🎉 Prueba completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_crear_producto_con_receta()
