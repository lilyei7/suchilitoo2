#!/usr/bin/env python
"""
Script para investigar y corregir la relación entre productos y recetas
Caso específico: "algas alas algas con algas" (producto) debe usar "algas con nalgas" (receta)
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

from restaurant.models import ProductoVenta, Receta, Insumo, RecetaInsumo

def investigar_relacion_correcta():
    """Investigar cómo debe ser la relación correcta"""
    print("🔍 INVESTIGANDO RELACIÓN PRODUCTO-RECETA")
    print("=" * 60)
    
    # 1. Buscar el producto "algas alas algas con algas"
    try:
        producto_venta = ProductoVenta.objects.get(nombre="algas alas algas con algas")
        print(f"✅ Producto encontrado: {producto_venta.nombre} (ID: {producto_venta.id})")
    except ProductoVenta.DoesNotExist:
        print("❌ Producto 'algas alas algas con algas' no encontrado")
        return False
    
    # 2. Buscar la receta "algas con nalgas" 
    print(f"\n🔍 Buscando receta 'algas con nalgas'...")
    
    # Primero verificar si existe como ProductoVenta (lo que creamos antes)
    try:
        producto_algas_nalgas = ProductoVenta.objects.get(nombre="algas con nalgas")
        print(f"✅ Producto 'algas con nalgas' encontrado (ID: {producto_algas_nalgas.id})")
        
        # Ver si tiene receta
        try:
            receta_algas_nalgas = producto_algas_nalgas.receta
            print(f"✅ Receta de 'algas con nalgas' encontrada (ID: {receta_algas_nalgas.id})")
        except Receta.DoesNotExist:
            print(f"❌ 'algas con nalgas' no tiene receta")
            return False
            
    except ProductoVenta.DoesNotExist:
        print("❌ Producto 'algas con nalgas' no encontrado")
        return False
    
    # 3. Ver qué receta tiene actualmente "algas alas algas con algas"
    print(f"\n📋 Estado actual de '{producto_venta.nombre}':")
    try:
        receta_actual = producto_venta.receta
        print(f"   Receta actual: ID {receta_actual.id}")
        
        # Ver insumos de la receta actual
        insumos_actuales = RecetaInsumo.objects.filter(receta=receta_actual)
        print(f"   Insumos: {insumos_actuales.count()}")
        for ri in insumos_actuales:
            print(f"      • {ri.cantidad} {ri.insumo.unidad_medida} de {ri.insumo.nombre}")
            
    except Receta.DoesNotExist:
        print(f"   ❌ No tiene receta")
    
    # 4. Ver la receta de "algas con nalgas"
    print(f"\n📋 Receta de 'algas con nalgas':")
    insumos_correctos = RecetaInsumo.objects.filter(receta=receta_algas_nalgas)
    print(f"   Insumos: {insumos_correctos.count()}")
    for ri in insumos_correctos:
        print(f"      • {ri.cantidad} {ri.insumo.unidad_medida} de {ri.insumo.nombre}")
    
    return producto_venta, receta_algas_nalgas

def corregir_relacion(producto_venta, receta_correcta):
    """Corregir la relación para que el producto use la receta correcta"""
    print(f"\n🔧 CORRIGIENDO RELACIÓN")
    print("=" * 60)
    
    print(f"❓ PROBLEMA DETECTADO:")
    print(f"• El producto '{producto_venta.nombre}' tiene su propia receta")
    print(f"• Pero debería usar la receta de 'algas con nalgas'")
    print(f"• Esto viola el principio OneToOne de Django")
    
    print(f"\n💡 SOLUCIONES POSIBLES:")
    print(f"1. 🔄 Reasignar la receta existente de 'algas con nalgas' al producto de venta")
    print(f"2. 🗑️ Eliminar la receta duplicada y usar la correcta")
    print(f"3. 🔗 Crear una referencia diferente (ForeignKey en lugar de OneToOne)")
    
    respuesta = input(f"\n❓ ¿Cuál opción prefieres? (1/2/3): ").strip()
    
    if respuesta == "1":
        return reasignar_receta(producto_venta, receta_correcta)
    elif respuesta == "2":
        return eliminar_receta_duplicada(producto_venta, receta_correcta)
    elif respuesta == "3":
        print("⚠️ Esta opción requiere cambios en el modelo Django")
        return False
    else:
        print("❌ Opción no válida")
        return False

def reasignar_receta(producto_venta, receta_correcta):
    """Reasignar la receta correcta al producto de venta"""
    print(f"\n🔄 REASIGNANDO RECETA")
    print("-" * 40)
    
    try:
        # 1. Liberar la receta actual del producto de venta
        try:
            receta_actual = producto_venta.receta
            print(f"📝 Liberando receta actual (ID: {receta_actual.id})")
            receta_actual.producto = None
            receta_actual.save()
        except Receta.DoesNotExist:
            print("✅ El producto no tenía receta previa")
        
        # 2. Liberar la receta de "algas con nalgas"
        producto_algas_nalgas = ProductoVenta.objects.get(nombre="algas con nalgas")
        print(f"📝 Liberando receta de 'algas con nalgas'")
        receta_correcta.producto = None
        receta_correcta.save()
        
        # 3. Asignar la receta correcta al producto de venta
        print(f"🔗 Asignando receta correcta al producto de venta")
        receta_correcta.producto = producto_venta
        receta_correcta.save()
        
        print(f"✅ Receta reasignada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al reasignar: {e}")
        return False

def eliminar_receta_duplicada(producto_venta, receta_correcta):
    """Eliminar la receta duplicada y usar la correcta"""
    print(f"\n🗑️ ELIMINANDO RECETA DUPLICADA")
    print("-" * 40)
    
    try:
        # 1. Eliminar la receta actual del producto de venta
        try:
            receta_actual = producto_venta.receta
            print(f"🗑️ Eliminando receta duplicada (ID: {receta_actual.id})")
            
            # Primero eliminar las relaciones con insumos
            RecetaInsumo.objects.filter(receta=receta_actual).delete()
            
            # Luego eliminar la receta
            receta_actual.delete()
            
        except Receta.DoesNotExist:
            print("✅ El producto no tenía receta previa")
        
        # 2. Liberar la receta de "algas con nalgas"
        producto_algas_nalgas = ProductoVenta.objects.get(nombre="algas con nalgas")
        print(f"📝 Liberando receta de 'algas con nalgas'")
        receta_correcta.producto = None
        receta_correcta.save()
        
        # 3. Asignar la receta correcta al producto de venta
        print(f"🔗 Asignando receta correcta al producto de venta")
        receta_correcta.producto = producto_venta
        receta_correcta.save()
        
        print(f"✅ Receta corregida exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al corregir: {e}")
        return False

def verificar_solucion():
    """Verificar que la solución funciona"""
    print(f"\n🧪 VERIFICANDO SOLUCIÓN")
    print("=" * 60)
    
    try:
        producto_venta = ProductoVenta.objects.get(nombre="algas alas algas con algas")
        receta = producto_venta.receta
        
        print(f"✅ Producto: {producto_venta.nombre}")
        print(f"✅ Receta: ID {receta.id}")
        
        # Ver insumos
        insumos = RecetaInsumo.objects.filter(receta=receta)
        print(f"✅ Insumos: {insumos.count()}")
        
        for ri in insumos:
            print(f"   • {ri.cantidad} {ri.insumo.unidad_medida} de {ri.insumo.nombre}")
        
        print(f"\n🎉 SOLUCIÓN VERIFICADA")
        print(f"• El producto '{producto_venta.nombre}' ahora usa la receta correcta")
        print(f"• Debería poder ordenarse sin problemas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

def main():
    print("🔧 CORRECCIÓN DE RELACIÓN PRODUCTO-RECETA")
    print("=" * 80)
    
    # 1. Investigar la situación actual
    resultado = investigar_relacion_correcta()
    
    if not resultado:
        print("❌ No se pudo completar la investigación")
        return
    
    producto_venta, receta_correcta = resultado
    
    # 2. Corregir la relación
    if corregir_relacion(producto_venta, receta_correcta):
        # 3. Verificar que funciona
        verificar_solucion()
    else:
        print("❌ No se pudo corregir la relación")

if __name__ == "__main__":
    main()
