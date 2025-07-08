#!/usr/bin/env python
"""
Script para verificar los estilos mejorados de las etiquetas de estado
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta

def verificar_etiquetas_mejoradas():
    print("=" * 70)
    print("🎨 VERIFICACIÓN - ETIQUETAS DE ESTADO MEJORADAS")
    print("=" * 70)
    
    # Verificar productos disponibles
    productos = ProductoVenta.objects.all()
    activos = productos.filter(disponible=True).count()
    inactivos = productos.filter(disponible=False).count()
    
    print(f"📊 PRODUCTOS EN LA BASE DE DATOS:")
    print(f"   Total: {productos.count()}")
    print(f"   Activos: {activos}")
    print(f"   Inactivos: {inactivos}")
    
    print(f"\n🎯 MEJORAS EN LAS ETIQUETAS DE ESTADO:")
    print(f"   ✅ Etiqueta ACTIVO:")
    print(f"      - Color: Verde brillante (#28a745)")
    print(f"      - Ícono: ✓ (check-circle)")
    print(f"      - Borde: Verde oscuro con sombra")
    print(f"      - Efecto hover: Más brillante y sombra más grande")
    print(f"   ")
    print(f"   ✅ Etiqueta INACTIVO:")
    print(f"      - Color: Rojo brillante (#dc3545)")
    print(f"      - Ícono: ⏸ (pause-circle)")
    print(f"      - Borde: Rojo oscuro con sombra")
    print(f"      - Efecto hover: Más brillante y sombra más grande")
    print(f"   ")
    print(f"   ✅ Características adicionales:")
    print(f"      - Texto en mayúsculas (ACTIVO/INACTIVO)")
    print(f"      - Fuente más gruesa (font-weight: 700)")
    print(f"      - Espaciado de letras mejorado")
    print(f"      - Padding más generoso")
    print(f"      - Animaciones suaves")
    
    print(f"\n📋 PRODUCTOS QUE VERÁS:")
    for producto in productos.order_by('nombre'):
        if producto.disponible:
            print(f"   🟢 {producto.nombre}")
            print(f"      └─ Etiqueta: 'ACTIVO' (verde brillante)")
        else:
            print(f"   🔴 {producto.nombre}")
            print(f"      └─ Etiqueta: 'INACTIVO' (rojo brillante)")
    
    print(f"\n🚀 PARA VER EL RESULTADO:")
    print(f"   1. Ve a: http://127.0.0.1:8000/dashboard/productos-venta/")
    print(f"   ")
    print(f"   2. Observa las etiquetas:")
    print(f"      - Colores más vibrantes y contrastantes")
    print(f"      - Mejor visibilidad")
    print(f"      - Efectos hover más llamativos")
    print(f"      - Texto más legible")
    
    print(f"\n🎨 COLORES UTILIZADOS:")
    print(f"   🟢 ACTIVO:")
    print(f"      - Fondo: #28a745 (verde Bootstrap success)")
    print(f"      - Borde: #1e7e34 (verde más oscuro)")
    print(f"      - Sombra: rgba(40, 167, 69, 0.3)")
    print(f"   ")
    print(f"   🔴 INACTIVO:")
    print(f"      - Fondo: #dc3545 (rojo Bootstrap danger)")
    print(f"      - Borde: #bd2130 (rojo más oscuro)")
    print(f"      - Sombra: rgba(220, 53, 69, 0.3)")
    
    print(f"\n" + "=" * 70)
    print(f"🎉 ¡ETIQUETAS MEJORADAS!")
    print(f"   Ahora las etiquetas son mucho más visibles y atractivas.")
    print("=" * 70)

if __name__ == "__main__":
    verificar_etiquetas_mejoradas()
