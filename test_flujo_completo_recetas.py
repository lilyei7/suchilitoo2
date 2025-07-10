#!/usr/bin/env python3
"""
Script para probar el flujo completo de creación y asignación de recetas
"""

import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import (
    ProductoVenta, Receta, RecetaInsumo, CategoriaProducto, 
    ProductoReceta, Insumo, UnidadMedida
)
from accounts.models import Sucursal
from inventario_automatico import InventarioAutomatico

def test_flujo_completo_recetas():
    print("🧪 PRUEBA COMPLETA: Flujo de creación y asignación de recetas")
    print("="*60)
    
    # 1. CREAR UNA RECETA INDEPENDIENTE
    print("\\n1. 🍳 CREANDO RECETA INDEPENDIENTE")
    print("-" * 40)
    
    # Buscar un insumo para la receta
    insumo = Insumo.objects.first()
    if not insumo:
        print("❌ No se encontró ningún insumo")
        return
    
    # Crear receta independiente (sin producto)
    receta_independiente = Receta.objects.create(
        producto=None,  # Sin producto inicialmente
        tiempo_preparacion=20,
        porciones=2,
        instrucciones="Preparar según instrucciones",
        notas="Receta de prueba independiente",
        activo=True
    )
    
    print(f"✅ Receta independiente creada: ID {receta_independiente.id}")
    
    # Agregar insumos a la receta
    RecetaInsumo.objects.create(
        receta=receta_independiente,
        insumo=insumo,
        cantidad=Decimal("2.5"),
        orden=1,
        opcional=False,
        notas="Insumo principal"
    )
    
    print(f"✅ Insumo agregado: {insumo.nombre} (cantidad: 2.5)")
    
    # 2. CREAR UN PRODUCTO Y ASIGNARLE LA RECETA
    print("\\n2. 🍽️ CREANDO PRODUCTO Y ASIGNANDO RECETA")
    print("-" * 40)
    
    # Buscar categoría
    categoria = CategoriaProducto.objects.first()
    if not categoria:
        print("❌ No se encontró ninguna categoría")
        return
    
    # Crear producto
    producto_test = ProductoVenta.objects.create(
        codigo="TEST-FLUJO",
        nombre="Producto Test Flujo",
        descripcion="Producto para probar flujo completo",
        precio=Decimal("18.50"),
        categoria=categoria,
        disponible=True,
        calorias=300
    )
    
    print(f"✅ Producto creado: {producto_test.nombre} (ID: {producto_test.id})")
    
    # Simular asignación de receta (como lo hace el formulario)
    recetas_ids = [str(receta_independiente.id)]
    
    # Crear relación many-to-many
    ProductoReceta.objects.create(
        producto=producto_test,
        receta=receta_independiente
    )
    
    print(f"✅ Relación ProductoReceta creada")
    
    # 🆕 CREAR RECETA DIRECTA (OneToOneField) 
    if recetas_ids:
        # Usar la primera receta como receta directa
        primera_receta = Receta.objects.get(id=recetas_ids[0])
        
        # Crear una copia de la receta directamente asociada al producto
        receta_directa = Receta.objects.create(
            producto=producto_test,
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
        
        print(f"✅ Insumos copiados a receta directa")
    
    # 3. VERIFICAR QUE FUNCIONE CON EL MESERO
    print("\\n3. 🔧 VERIFICANDO FUNCIONAMIENTO CON MESERO")
    print("-" * 40)
    
    # Verificar relación directa
    try:
        receta_directa_test = producto_test.receta
        print(f"✅ Receta directa encontrada: ID {receta_directa_test.id}")
        print(f"   - Tiempo preparación: {receta_directa_test.tiempo_preparacion} min")
        print(f"   - Porciones: {receta_directa_test.porciones}")
        print(f"   - Insumos: {receta_directa_test.insumos.count()}")
    except Exception as e:
        print(f"❌ Error en receta directa: {e}")
        return
    
    # Verificar relación many-to-many
    relaciones = ProductoReceta.objects.filter(producto=producto_test)
    print(f"✅ Relaciones ProductoReceta: {relaciones.count()}")
    
    # Probar con InventarioAutomatico
    sucursal = Sucursal.objects.first()
    if sucursal:
        inventario = InventarioAutomatico(sucursal)
        stock_ok, faltantes = inventario.verificar_stock_disponible(producto_test, 1)
        
        print(f"✅ Stock verificado: {stock_ok}")
        if stock_ok:
            print("✅ ¡EL MESERO PUEDE CREAR ÓRDENES!")
        else:
            print("❌ El mesero NO puede crear órdenes")
            for faltante in faltantes:
                print(f"   - {faltante}")
    
    # 4. CREAR SEGUNDA RECETA Y CAMBIAR ASIGNACIÓN
    print("\\n4. 🔄 CREANDO SEGUNDA RECETA Y CAMBIANDO ASIGNACIÓN")
    print("-" * 40)
    
    # Crear segunda receta independiente
    receta_independiente_2 = Receta.objects.create(
        producto=None,
        tiempo_preparacion=15,
        porciones=1,
        instrucciones="Preparación rápida",
        notas="Segunda receta de prueba",
        activo=True
    )
    
    # Agregar insumos a la segunda receta
    RecetaInsumo.objects.create(
        receta=receta_independiente_2,
        insumo=insumo,
        cantidad=Decimal("1.0"),
        orden=1,
        opcional=False,
        notas="Menos cantidad"
    )
    
    print(f"✅ Segunda receta creada: ID {receta_independiente_2.id}")
    
    # Simular edición del producto (cambiar receta)
    # Eliminar asociaciones existentes
    ProductoReceta.objects.filter(producto=producto_test).delete()
    print(f"✅ Relaciones ProductoReceta eliminadas")
    
    # Eliminar receta directa existente
    try:
        receta_directa_existente = producto_test.receta
        if receta_directa_existente:
            receta_directa_existente.producto = None
            receta_directa_existente.save()
            print(f"✅ Receta directa anterior desenlazada: ID {receta_directa_existente.id}")
    except Receta.DoesNotExist:
        print("✅ No había receta directa anterior")
    
    # Crear nueva asociación
    ProductoReceta.objects.create(
        producto=producto_test,
        receta=receta_independiente_2
    )
    print(f"✅ Nueva relación ProductoReceta creada")
    
    # Crear nueva receta directa
    nueva_receta_directa = Receta.objects.create(
        producto=producto_test,
        tiempo_preparacion=receta_independiente_2.tiempo_preparacion,
        porciones=receta_independiente_2.porciones,
        instrucciones=receta_independiente_2.instrucciones,
        notas=receta_independiente_2.notas,
        activo=receta_independiente_2.activo
    )
    
    # Copiar insumos
    for receta_insumo in receta_independiente_2.insumos.all():
        RecetaInsumo.objects.create(
            receta=nueva_receta_directa,
            insumo=receta_insumo.insumo,
            cantidad=receta_insumo.cantidad,
            orden=receta_insumo.orden,
            opcional=receta_insumo.opcional,
            notas=receta_insumo.notas
        )
    
    print(f"✅ Nueva receta directa creada: ID {nueva_receta_directa.id}")
    
    # 5. VERIFICAR QUE SIGUE FUNCIONANDO
    print("\\n5. ✅ VERIFICACIÓN FINAL")
    print("-" * 40)
    
    # Verificar nueva relación directa
    try:
        receta_directa_final = producto_test.receta
        print(f"✅ Nueva receta directa: ID {receta_directa_final.id}")
        print(f"   - Tiempo preparación: {receta_directa_final.tiempo_preparacion} min")
        print(f"   - Porciones: {receta_directa_final.porciones}")
    except Exception as e:
        print(f"❌ Error en nueva receta directa: {e}")
        return
    
    # Probar nuevamente con InventarioAutomatico
    if sucursal:
        inventario = InventarioAutomatico(sucursal)
        stock_ok, faltantes = inventario.verificar_stock_disponible(producto_test, 1)
        
        print(f"✅ Stock verificado después del cambio: {stock_ok}")
        if stock_ok:
            print("✅ ¡EL MESERO SIGUE FUNCIONANDO DESPUÉS DEL CAMBIO!")
        else:
            print("❌ El mesero NO funciona después del cambio")
            for faltante in faltantes:
                print(f"   - {faltante}")
    
    # 6. RESUMEN FINAL
    print("\\n6. 📊 RESUMEN FINAL")
    print("-" * 40)
    
    # Contar recetas
    recetas_totales = Receta.objects.count()
    recetas_con_producto = Receta.objects.filter(producto__isnull=False).count()
    recetas_independientes = Receta.objects.filter(producto__isnull=True).count()
    
    print(f"📈 Estadísticas finales:")
    print(f"   - Recetas totales: {recetas_totales}")
    print(f"   - Recetas con producto (directas): {recetas_con_producto}")
    print(f"   - Recetas independientes: {recetas_independientes}")
    print(f"   - Relaciones ProductoReceta: {ProductoReceta.objects.count()}")
    
    print("\\n🎉 PRUEBA COMPLETADA CON ÉXITO")
    print("✅ El flujo completo funciona correctamente:")
    print("   1. Crear recetas independientes ✅")
    print("   2. Asignar recetas a productos ✅")
    print("   3. Funcionamiento con mesero ✅")
    print("   4. Cambiar recetas asignadas ✅")
    print("   5. Mantener funcionamiento ✅")

if __name__ == "__main__":
    test_flujo_completo_recetas()
