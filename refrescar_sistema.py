#!/usr/bin/env python
"""
Script para refrescar y verificar el estado del sistema
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suchilitoo.settings')
django.setup()

from restaurant.models import ProductoVenta, Receta
from django.core.cache import cache

def limpiar_cache():
    """Limpiar todo el cache de Django"""
    print("🧹 LIMPIANDO CACHE DE DJANGO")
    print("=" * 50)
    try:
        cache.clear()
        print("✅ Cache limpiado exitosamente")
    except Exception as e:
        print(f"⚠️ Error limpiando cache: {e}")

def verificar_estado_final():
    """Verificación final del estado del sistema"""
    print("\n🔍 VERIFICACIÓN FINAL DEL ESTADO")
    print("=" * 50)
    
    # Buscar el producto
    try:
        producto = ProductoVenta.objects.get(nombre='algas alas algas con algas')
        print(f"✅ Producto encontrado:")
        print(f"   ID: {producto.id}")
        print(f"   Nombre: {producto.nombre}")
        print(f"   Código: {producto.codigo}")
        print(f"   Precio: ${producto.precio:,.2f}")
        
        # Verificar receta
        try:
            receta = producto.receta
            print(f"✅ Receta asociada:")
            print(f"   ID: {receta.id}")
            print(f"   Tiempo: {receta.tiempo_preparacion} min")
            print(f"   Porciones: {receta.porciones}")
            
            # Verificar insumos
            insumos = receta.recetainsumo_set.all()
            print(f"✅ Insumos ({insumos.count()}):")
            for ri in insumos:
                print(f"   • {ri.insumo.nombre}: {ri.cantidad} {ri.insumo.unidad_medida.abreviacion}")
                
        except Receta.DoesNotExist:
            print("❌ No tiene receta asociada")
            
    except ProductoVenta.DoesNotExist:
        print("❌ Producto no encontrado")

def mostrar_info_servidor():
    """Mostrar información para reiniciar el servidor"""
    print("\n🚀 INSTRUCCIONES PARA REINICIAR SERVIDOR")
    print("=" * 50)
    print("1. Presiona Ctrl+C en la terminal donde está corriendo Django")
    print("2. Ejecuta nuevamente: python manage.py runserver")
    print("3. Abre el navegador y presiona Ctrl+F5 para refrescar sin cache")
    print("4. Ve a: http://127.0.0.1:8000/dashboard/productos-venta/")
    print("\n📱 URL directa del producto:")
    try:
        producto = ProductoVenta.objects.get(nombre='algas alas algas con algas')
        print(f"   http://127.0.0.1:8000/dashboard/productos-venta/{producto.id}/detalle/")
    except:
        print("   No se pudo obtener la URL")

if __name__ == "__main__":
    print("🔄 REFRESCANDO SISTEMA COMPLETO")
    print("=" * 60)
    
    limpiar_cache()
    verificar_estado_final()
    mostrar_info_servidor()
    
    print("\n" + "=" * 60)
    print("🎉 ¡SISTEMA VERIFICADO Y CACHE LIMPIADO!")
    print("✅ El problema debería estar resuelto después de reiniciar el servidor")
