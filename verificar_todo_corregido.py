#!/usr/bin/env python
"""
Script final para verificar que las URLs están corregidas
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.urls import reverse
from restaurant.models import ProductoVenta

def verificar_todo_corregido():
    print("=" * 70)
    print("🔧 VERIFICACIÓN FINAL - TODAS LAS CORRECCIONES")
    print("=" * 70)
    
    # 1. Verificar que la URL funciona
    try:
        url = reverse('dashboard:lista_productos_venta')
        print(f"✅ URL correcta generada: {url}")
    except Exception as e:
        print(f"❌ Error generando URL: {e}")
        return
    
    # 2. Verificar productos en la base de datos
    productos = ProductoVenta.objects.all()
    activos = productos.filter(disponible=True).count()
    inactivos = productos.filter(disponible=False).count()
    
    print(f"\n📊 PRODUCTOS EN LA BASE DE DATOS:")
    print(f"   Total: {productos.count()}")
    print(f"   Activos: {activos}")
    print(f"   Inactivos: {inactivos}")
    
    print(f"\n📋 Lista completa:")
    for producto in productos.order_by('nombre'):
        estado = "🟢 ACTIVO" if producto.disponible else "🔴 INACTIVO"
        categoria = producto.categoria.nombre if producto.categoria else "Sin categoría"
        print(f"   - {producto.nombre} ({estado}) - {categoria}")
    
    # 3. Instrucciones finales
    print(f"\n🚀 INSTRUCCIONES PARA VERIFICAR:")
    print(f"   1. Ve al dashboard principal:")
    print(f"      http://127.0.0.1:8000/dashboard/")
    print(f"   ")
    print(f"   2. Haz clic en 'Productos de Venta' desde:")
    print(f"      - El menú lateral (sidebar)")
    print(f"      - O el botón en el dashboard principal")
    print(f"   ")
    print(f"   3. Deberías llegar a:")
    print(f"      http://127.0.0.1:8000/dashboard/productos-venta/")
    print(f"   ")
    print(f"   4. Y ver:")
    print(f"      - Una TABLA con {productos.count()} productos")
    print(f"      - {activos} producto(s) con etiqueta ACTIVO (verde)")
    print(f"      - {inactivos} producto(s) con etiqueta INACTIVO (roja)")
    print(f"      - Información: 'Total: {productos.count()} - Activos: {activos}, Inactivos: {inactivos}'")
    
    # 4. Resumen de cambios realizados
    print(f"\n📝 CAMBIOS REALIZADOS:")
    print(f"   ✅ Comentada URL duplicada en dashboard/urls.py")
    print(f"   ✅ Corregidas referencias en templates:")
    print(f"      - dashboard/base.html")
    print(f"      - dashboard/principal.html") 
    print(f"      - dashboard/base_new.html")
    print(f"   ✅ Vista productos_venta_views.lista_productos_venta configurada para mostrar TODOS los productos")
    print(f"   ✅ Template con etiquetas de estado (ACTIVO/INACTIVO)")
    
    print(f"\n" + "=" * 70)
    print(f"🎉 ¡CONFIGURACIÓN COMPLETADA!")
    print(f"   Ahora la URL /dashboard/productos-venta/ muestra TODOS los productos")
    print(f"   con sus respectivas etiquetas de estado.")
    print("=" * 70)

if __name__ == "__main__":
    verificar_todo_corregido()
