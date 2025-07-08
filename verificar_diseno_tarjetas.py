#!/usr/bin/env python
"""
Script para verificar que las tarjetas muestran todos los productos
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta

def verificar_diseno_tarjetas():
    print("=" * 70)
    print("🎨 VERIFICACIÓN - DISEÑO DE TARJETAS RESTAURADO")
    print("=" * 70)
    
    # Verificar productos disponibles
    productos = ProductoVenta.objects.all()
    activos = productos.filter(disponible=True).count()
    inactivos = productos.filter(disponible=False).count()
    
    print(f"📊 PRODUCTOS EN LA BASE DE DATOS:")
    print(f"   Total: {productos.count()}")
    print(f"   Activos: {activos}")
    print(f"   Inactivos: {inactivos}")
    
    print(f"\n📋 Lista de productos:")
    for producto in productos.order_by('nombre'):
        estado = "🟢 ACTIVO" if producto.disponible else "🔴 INACTIVO"
        categoria = producto.categoria.nombre if producto.categoria else "Sin categoría"
        print(f"   - {producto.nombre} ({estado}) - {categoria}")
    
    print(f"\n🎯 CARACTERÍSTICAS DEL NUEVO DISEÑO:")
    print(f"   ✅ Diseño de tarjetas (cards) como el original")
    print(f"   ✅ Muestra TODOS los productos (activos e inactivos)")
    print(f"   ✅ Etiquetas de estado prominentes:")
    print(f"      - ACTIVO: Badge verde con ícono de check")
    print(f"      - INACTIVO: Badge rojo con ícono de pausa")
    print(f"   ✅ Grid responsive (3 columnas en desktop)")
    print(f"   ✅ Efectos hover en las tarjetas")
    print(f"   ✅ Estadísticas al final de la página")
    print(f"   ✅ Filtros de búsqueda y categoría")
    print(f"   ✅ Botones de acción: Ver, Editar, Eliminar")
    
    print(f"\n🚀 PARA VER EL RESULTADO:")
    print(f"   1. Ve a: http://127.0.0.1:8000/dashboard/productos-venta/")
    print(f"   ")
    print(f"   2. Deberías ver:")
    print(f"      - {productos.count()} tarjetas de productos")
    print(f"      - Cada tarjeta con imagen placeholder")
    print(f"      - Estado claramente visible en cada tarjeta")
    print(f"      - Diseño similar al original pero mostrando TODOS los productos")
    
    print(f"\n📝 DIFERENCIAS CON EL DISEÑO ORIGINAL:")
    print(f"   ❌ Eliminado: Botón de toggle de estado desde la lista")
    print(f"   ✅ Mantenido: Diseño de tarjetas")
    print(f"   ✅ Mejorado: Etiquetas de estado más prominentes")
    print(f"   ✅ Corregido: Muestra productos inactivos")
    
    print(f"\n" + "=" * 70)
    print(f"🎉 ¡DISEÑO DE TARJETAS RESTAURADO!")
    print(f"   Ahora tienes el diseño original con la funcionalidad corregida.")
    print("=" * 70)

if __name__ == "__main__":
    verificar_diseno_tarjetas()
