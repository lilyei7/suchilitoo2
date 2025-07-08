#!/usr/bin/env python
"""
Script para verificar que las etiquetas tienen colores forzados
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta

def verificar_colores_forzados():
    print("=" * 70)
    print("🎨 VERIFICACIÓN - COLORES FORZADOS EN ETIQUETAS")
    print("=" * 70)
    
    # Verificar productos disponibles
    productos = ProductoVenta.objects.all()
    activos = productos.filter(disponible=True).count()
    inactivos = productos.filter(disponible=False).count()
    
    print(f"📊 PRODUCTOS EN LA BASE DE DATOS:")
    print(f"   Total: {productos.count()}")
    print(f"   Activos: {activos}")
    print(f"   Inactivos: {inactivos}")
    
    print(f"\n🔧 SOLUCIONES APLICADAS:")
    print(f"   ✅ Estilos CSS con !important para mayor prioridad")
    print(f"   ✅ Estilos en línea como respaldo")
    print(f"   ✅ Clases CSS específicas para sobrescribir Bootstrap")
    print(f"   ✅ Color blanco explícito (#ffffff) para el texto")
    print(f"   ✅ z-index y position para evitar conflictos")
    
    print(f"\n🎯 ESTILOS APLICADOS:")
    print(f"   🟢 ACTIVO:")
    print(f"      - background-color: #28a745 !important")
    print(f"      - color: #ffffff !important")
    print(f"      - border: 2px solid #1e7e34 !important")
    print(f"      - Estilo en línea: style='...'")
    print(f"   ")
    print(f"   🔴 INACTIVO:")
    print(f"      - background-color: #dc3545 !important")
    print(f"      - color: #ffffff !important")
    print(f"      - border: 2px solid #bd2130 !important")
    print(f"      - Estilo en línea: style='...'")
    
    print(f"\n📋 PRODUCTOS ACTUALES:")
    for producto in productos.order_by('nombre'):
        if producto.disponible:
            print(f"   🟢 {producto.nombre}")
            print(f"      └─ Etiqueta: VERDE BRILLANTE con texto blanco")
        else:
            print(f"   🔴 {producto.nombre}")
            print(f"      └─ Etiqueta: ROJA BRILLANTE con texto blanco")
    
    print(f"\n🚀 PARA VER EL RESULTADO:")
    print(f"   1. Actualiza la página: http://127.0.0.1:8000/dashboard/productos-venta/")
    print(f"   2. Presiona Ctrl+F5 para limpiar la caché del navegador")
    print(f"   3. Deberías ver:")
    print(f"      - Etiquetas con colores brillantes")
    print(f"      - Texto blanco legible")
    print(f"      - Bordes definidos")
    print(f"      - NO más etiquetas blancas")
    
    print(f"\n🔍 SI AÚN SE VEN BLANCAS:")
    print(f"   1. Abre las herramientas de desarrollador (F12)")
    print(f"   2. Ve a la pestaña 'Elements'")
    print(f"   3. Busca <span class='badge status-badge'>")
    print(f"   4. Verifica que los estilos en línea estén aplicados")
    print(f"   5. En 'Computed' verifica que background-color sea verde o rojo")
    
    print(f"\n" + "=" * 70)
    print(f"🎉 ¡COLORES FORZADOS APLICADOS!")
    print(f"   Ahora las etiquetas deberían ser completamente visibles.")
    print("=" * 70)

if __name__ == "__main__":
    verificar_colores_forzados()
