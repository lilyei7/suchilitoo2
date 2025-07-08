#!/usr/bin/env python
"""
Script para crear un producto inactivo y ver la diferencia de colores
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta

def activar_desactivar_producto():
    print("=" * 70)
    print("🔄 CAMBIAR ESTADO DE PRODUCTO PARA VER DIFERENCIAS")
    print("=" * 70)
    
    # Buscar el producto rollosake para ponerlo inactivo
    try:
        producto = ProductoVenta.objects.get(nombre="rollosake")
        estado_anterior = "ACTIVO" if producto.disponible else "INACTIVO"
        
        # Cambiar el estado
        producto.disponible = False  # Ponerlo inactivo
        producto.save()
        
        print(f"✅ Producto '{producto.nombre}' cambiado:")
        print(f"   Estado anterior: {estado_anterior}")
        print(f"   Estado nuevo: INACTIVO")
        
    except ProductoVenta.DoesNotExist:
        print("❌ No se encontró el producto 'rollosake'")
        return
    
    # Mostrar estado actual de todos los productos
    productos = ProductoVenta.objects.all()
    activos = productos.filter(disponible=True).count()
    inactivos = productos.filter(disponible=False).count()
    
    print(f"\n📊 ESTADO ACTUAL:")
    print(f"   Total productos: {productos.count()}")
    print(f"   Activos: {activos}")
    print(f"   Inactivos: {inactivos}")
    
    print(f"\n📋 LISTA COMPLETA:")
    for producto in productos.order_by('nombre'):
        if producto.disponible:
            print(f"   🟢 {producto.nombre} - ACTIVO (etiqueta verde)")
        else:
            print(f"   🔴 {producto.nombre} - INACTIVO (etiqueta roja)")
    
    print(f"\n🎨 AHORA PODRÁS VER LA DIFERENCIA:")
    print(f"   📍 Ve a: http://127.0.0.1:8000/dashboard/productos-venta/")
    print(f"   ")
    print(f"   👀 Observa:")
    print(f"   🟢 California Roll - Etiqueta VERDE con ícono ✓")
    print(f"   🔴 rollosake - Etiqueta ROJA con ícono ⏸")
    print(f"   ")
    print(f"   ✨ Efectos que verás:")
    print(f"   - Verde: Brillante, sombra verde, hover más intenso")
    print(f"   - Rojo: Brillante, sombra roja, hover más intenso")
    print(f"   - Texto en mayúsculas y fuente más gruesa")
    print(f"   - Animaciones suaves al pasar el mouse")
    
    print(f"\n" + "=" * 70)
    print(f"🎉 ¡LISTO PARA PROBAR!")
    print(f"   Ahora tienes un producto de cada estado para ver la diferencia.")
    print("=" * 70)

if __name__ == "__main__":
    activar_desactivar_producto()
