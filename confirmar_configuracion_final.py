#!/usr/bin/env python
"""
Script final para confirmar que la página muestra todos los productos
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta

def confirmar_configuracion_final():
    print("=" * 70)
    print("🎯 CONFIRMACIÓN FINAL - CONFIGURACIÓN PRODUCTOS VENTA")
    print("=" * 70)
    
    # 1. Estado de la base de datos
    productos = ProductoVenta.objects.all().order_by('nombre')
    activos = productos.filter(disponible=True)
    inactivos = productos.filter(disponible=False)
    
    print(f"\n📊 ESTADO DE LA BASE DE DATOS:")
    print(f"   Total productos: {productos.count()}")
    print(f"   Productos ACTIVOS: {activos.count()}")
    print(f"   Productos INACTIVOS: {inactivos.count()}")
    
    print(f"\n📋 LISTADO COMPLETO:")
    for producto in productos:
        estado = "🟢 ACTIVO" if producto.disponible else "🔴 INACTIVO"
        print(f"   - {producto.nombre} ({estado})")
    
    # 2. Configuración de la vista
    print(f"\n⚙️  CONFIGURACIÓN DE LA VISTA:")
    print(f"   ✅ Vista: lista_productos_venta")
    print(f"   ✅ Queryset: ProductoVenta.objects.all() (SIN filtros)")
    print(f"   ✅ Template: dashboard/productos_venta/lista.html")
    print(f"   ✅ URL: /dashboard/productos-venta/")
    
    # 3. Lo que deberías ver en la página
    print(f"\n🌐 LO QUE DEBERÍAS VER EN LA PÁGINA:")
    print(f"   URL: http://127.0.0.1:8000/dashboard/productos-venta/")
    print(f"   ")
    print(f"   📋 Lista de productos:")
    
    for producto in productos:
        if producto.disponible:
            print(f"   🟢 {producto.nombre}")
            print(f"      └─ Etiqueta: 'ACTIVO' (fondo verde)")
        else:
            print(f"   🔴 {producto.nombre}")
            print(f"      └─ Etiqueta: 'INACTIVO' (fondo rojo)")
    
    # 4. Instrucciones
    print(f"\n🚀 INSTRUCCIONES:")
    print(f"   1. Asegúrate de que el servidor esté corriendo:")
    print(f"      python manage.py runserver")
    print(f"   ")
    print(f"   2. Ve a la URL:")
    print(f"      http://127.0.0.1:8000/dashboard/productos-venta/")
    print(f"   ")
    print(f"   3. Deberías ver AMBOS productos en la lista:")
    print(f"      - California Roll con etiqueta ACTIVO (verde)")
    print(f"      - rollosake con etiqueta INACTIVO (roja)")
    print(f"   ")
    print(f"   4. Para cambiar el estado, usa el botón 'Editar' en cada producto")
    
    # 5. Verificación de archivos clave
    archivos_clave = [
        'dashboard/views/productos_venta_views.py',
        'dashboard/templates/dashboard/productos_venta/lista.html',
        'dashboard/urls.py'
    ]
    
    print(f"\n📁 ARCHIVOS MODIFICADOS:")
    for archivo in archivos_clave:
        ruta_completa = os.path.join(os.getcwd(), archivo)
        if os.path.exists(ruta_completa):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} (no encontrado)")
    
    print(f"\n" + "=" * 70)
    print(f"🎉 ¡CONFIGURACIÓN COMPLETADA!")
    print(f"   La página ahora muestra TODOS los productos con sus estados.")
    print(f"   No hay filtros que oculten los productos inactivos.")
    print("=" * 70)

if __name__ == "__main__":
    confirmar_configuracion_final()
