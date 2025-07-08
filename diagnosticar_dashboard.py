#!/usr/bin/env python
"""
Script para diagnosticar por qué el dashboard no refleja los cambios correctos
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

from restaurant.models import ProductoVenta, Receta, RecetaInsumo

def diagnosticar_problema_dashboard():
    """Diagnosticar por qué el dashboard no muestra la información correcta"""
    print("🔍 DIAGNÓSTICO: PROBLEMA EN DASHBOARD")
    print("=" * 60)
    
    # 1. Verificar el producto "algas alas algas con algas"
    try:
        producto = ProductoVenta.objects.get(nombre="algas alas algas con algas")
        print(f"✅ Producto encontrado: {producto.nombre}")
        print(f"   ID: {producto.id}")
        print(f"   Código: {producto.codigo}")
        print(f"   Precio: ${producto.precio}")
    except ProductoVenta.DoesNotExist:
        print("❌ Producto no encontrado")
        return
    
    # 2. Verificar la receta asociada
    try:
        receta = producto.receta
        print(f"\n✅ Receta asociada encontrada:")
        print(f"   ID: {receta.id}")
        print(f"   Tiempo preparación: {receta.tiempo_preparacion} min")
        print(f"   Porciones: {receta.porciones}")
        
        # Verificar insumos
        insumos = RecetaInsumo.objects.filter(receta=receta)
        print(f"   Insumos: {insumos.count()}")
        for ri in insumos:
            print(f"      • {ri.cantidad} {ri.insumo.unidad_medida} de {ri.insumo.nombre}")
            
    except Receta.DoesNotExist:
        print(f"\n❌ EL PRODUCTO NO TIENE RECETA ASOCIADA")
        print(f"   Esto explica por qué el dashboard muestra problemas")
        return
    
    # 3. Verificar si hay alguna confusión con nombres o IDs
    print(f"\n🔍 VERIFICANDO POSIBLES CONFUSIONES:")
    
    # Buscar si existe "algas con nalgas" como ProductoVenta
    try:
        producto_nalgas = ProductoVenta.objects.get(nombre="algas con nalgas")
        print(f"   ⚠️ Existe producto 'algas con nalgas' (ID: {producto_nalgas.id})")
        
        try:
            receta_nalgas = producto_nalgas.receta
            print(f"      Tiene receta (ID: {receta_nalgas.id})")
        except Receta.DoesNotExist:
            print(f"      No tiene receta")
            
    except ProductoVenta.DoesNotExist:
        print(f"   ✅ No existe producto 'algas con nalgas' (correcto)")
    
    # 4. Buscar todas las recetas y ver a qué productos están asociadas
    print(f"\n📋 TODAS LAS RECETAS EN EL SISTEMA:")
    recetas = Receta.objects.all()
    
    for receta in recetas:
        if receta.producto:
            print(f"   Receta ID {receta.id} → Producto: {receta.producto.nombre} (ID: {receta.producto.id})")
        else:
            print(f"   Receta ID {receta.id} → SIN PRODUCTO ASOCIADO")
    
    # 5. Verificar cómo se muestra en el dashboard
    print(f"\n🖥️ DATOS PARA EL DASHBOARD:")
    print(f"   URL: http://127.0.0.1:8000/dashboard/productos-venta/{producto.id}/detalle/")
    print(f"   Producto ID: {producto.id}")
    print(f"   Receta ID: {receta.id if 'receta' in locals() else 'N/A'}")

def verificar_vista_dashboard():
    """Verificar cómo la vista del dashboard obtiene los datos"""
    print(f"\n🔍 VERIFICANDO VISTA DEL DASHBOARD")
    print("=" * 60)
    
    # Simular lo que hace la vista del dashboard
    try:
        producto = ProductoVenta.objects.get(id=116)  # ID del producto en la URL
        
        print(f"Dashboard ve:")
        print(f"   Producto: {producto.nombre}")
        print(f"   Código: {producto.codigo}")
        print(f"   Precio: ${producto.precio}")
        
        # Ver si tiene receta
        try:
            receta = producto.receta
            print(f"   Receta: SÍ (ID: {receta.id})")
            
            # Buscar insumos
            insumos = RecetaInsumo.objects.filter(receta=receta)
            print(f"   Tabla de recetas muestra:")
            print(f"   ┌─────────────────┬───────────────────┬──────────┬─────────┐")
            print(f"   │ RECETA          │ TIEMPO PREPARACIÓN│ PORCIONES│ COSTO   │")
            print(f"   ├─────────────────┼───────────────────┼──────────┼─────────┤")
            
            # Aquí está el problema probable: ¿qué nombre se muestra?
            nombre_mostrado = receta.producto.nombre if receta.producto else "Sin nombre"
            print(f"   │ {nombre_mostrado:<15} │ {receta.tiempo_preparacion} minutos{' ' * 8} │ {receta.porciones:<8} │ $8000.00│")
            print(f"   └─────────────────┴───────────────────┴──────────┴─────────┘")
            
        except Receta.DoesNotExist:
            print(f"   Receta: NO")
            
    except ProductoVenta.DoesNotExist:
        print("❌ Error: Producto con ID 116 no encontrado")

def posibles_problemas():
    """Identificar posibles problemas"""
    print(f"\n🤔 POSIBLES PROBLEMAS:")
    print("=" * 60)
    
    print("1. 🔄 Cache del navegador")
    print("   • El navegador puede estar mostrando datos antiguos")
    print("   • Solución: Ctrl+F5 para refrescar sin cache")
    
    print("\n2. 🐛 La vista del dashboard no está actualizada")
    print("   • Puede estar usando datos cached de Django")
    print("   • Solución: Reiniciar el servidor Django")
    
    print("\n3. 📊 Lógica incorrecta en la vista")
    print("   • La vista puede estar buscando datos incorrectamente")
    print("   • Solución: Revisar el código de la vista")
    
    print("\n4. 🔀 Problema en la relación OneToOne")
    print("   • Django puede no estar reflejando los cambios correctamente")
    print("   • Solución: Verificar que no hay conflictos en la BD")

def main():
    diagnosticar_problema_dashboard()
    verificar_vista_dashboard()
    posibles_problemas()
    
    print(f"\n" + "=" * 80)
    print("🎯 PRÓXIMOS PASOS:")
    print("1. Refrescar el navegador (Ctrl+F5)")
    print("2. Reiniciar el servidor Django")
    print("3. Verificar la vista del dashboard")
    print("4. Si persiste, revisar la base de datos directamente")

if __name__ == "__main__":
    main()
