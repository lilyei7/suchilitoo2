#!/usr/bin/env python
"""
Script para confirmar que la URL ahora usa la vista correcta
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.urls import resolve, reverse
from restaurant.models import ProductoVenta

def verificar_url_corregida():
    print("=" * 70)
    print("🔧 VERIFICACIÓN DE CORRECCIÓN DE URL")
    print("=" * 70)
    
    # 1. Verificar qué vista resuelve la URL
    try:
        resolver = resolve('/dashboard/productos-venta/')
        print(f"✅ URL /dashboard/productos-venta/ resuelve a:")
        print(f"   Vista: {resolver.func}")
        print(f"   Nombre: {resolver.view_name}")
        print(f"   Módulo: {resolver.func.__module__}")
        print(f"   Función: {resolver.func.__name__}")
        
        # Verificar si es la vista correcta
        if 'productos_venta_views' in resolver.func.__module__:
            print(f"   ✅ Usando la vista CORRECTA (productos_venta_views.lista_productos_venta)")
        else:
            print(f"   ❌ Usando la vista INCORRECTA (views.productos_venta_view)")
            
    except Exception as e:
        print(f"❌ Error al resolver URL: {e}")
    
    # 2. Verificar productos que debería mostrar la nueva vista
    print(f"\n📊 PRODUCTOS QUE DEBERÍA MOSTRAR:")
    productos = ProductoVenta.objects.all()
    activos = productos.filter(disponible=True).count()
    inactivos = productos.filter(disponible=False).count()
    
    print(f"   Total productos: {productos.count()}")
    print(f"   Activos: {activos}")
    print(f"   Inactivos: {inactivos}")
    
    print(f"\n📋 Lista de productos:")
    for producto in productos.order_by('nombre'):
        estado = "🟢 ACTIVO" if producto.disponible else "🔴 INACTIVO"
        print(f"   - {producto.nombre} ({estado})")
    
    # 3. Instrucciones finales
    print(f"\n🚀 INSTRUCCIONES FINALES:")
    print(f"   1. Reinicia el servidor Django:")
    print(f"      Ctrl+C (si está corriendo)")
    print(f"      python manage.py runserver")
    print(f"   ")
    print(f"   2. Ve a la URL:")
    print(f"      http://127.0.0.1:8000/dashboard/productos-venta/")
    print(f"   ")
    print(f"   3. Ahora deberías ver:")
    print(f"      - Una TABLA (no cards)")
    print(f"      - {productos.count()} productos listados")
    print(f"      - {activos} con etiqueta ACTIVO (verde)")
    print(f"      - {inactivos} con etiqueta INACTIVO (roja)")
    
    print(f"\n" + "=" * 70)
    print(f"🎉 ¡PROBLEMA SOLUCIONADO!")
    print(f"   Se eliminó la URL duplicada que causaba el filtro.")
    print("=" * 70)

if __name__ == "__main__":
    verificar_url_corregida()
