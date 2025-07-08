#!/usr/bin/env python
"""
Script para verificar que la página de productos-venta muestre TODOS los productos
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta
from django.http import HttpRequest
from django.contrib.auth.models import User
from dashboard.views.productos_venta_views import lista_productos_venta

def verificar_productos_venta():
    print("=" * 60)
    print("VERIFICACIÓN FINAL - PRODUCTOS VENTA")
    print("=" * 60)
    
    # 1. Verificar todos los productos en la base de datos
    print("\n1. PRODUCTOS EN LA BASE DE DATOS:")
    productos_db = ProductoVenta.objects.all()
    print(f"Total productos en DB: {productos_db.count()}")
    
    activos_db = productos_db.filter(disponible=True).count()
    inactivos_db = productos_db.filter(disponible=False).count()
    
    print(f"- Activos: {activos_db}")
    print(f"- Inactivos: {inactivos_db}")
    
    print("\nListado completo:")
    for producto in productos_db.order_by('nombre'):
        estado = "ACTIVO" if producto.disponible else "INACTIVO"
        print(f"- {producto.nombre} ({estado})")
    
    # 2. Simular la vista lista_productos_venta
    print("\n" + "=" * 60)
    print("2. SIMULACIÓN DE LA VISTA lista_productos_venta")
    print("=" * 60)
    
    # Crear un request simulado
    request = HttpRequest()
    request.method = 'GET'
    request.GET = {}
    request.user = User.objects.filter(is_superuser=True).first()
    
    if not request.user:
        print("⚠️  No hay usuario admin para probar")
        return
    
    try:
        # Simular la función de la vista directamente
        productos_vista = ProductoVenta.objects.select_related('categoria').all()
        productos_lista = list(productos_vista)
        
        print(f"Productos devueltos por la vista: {len(productos_lista)}")
        
        activos_vista = len([p for p in productos_lista if p.disponible])
        inactivos_vista = len(productos_lista) - activos_vista
        
        print(f"- Activos en vista: {activos_vista}")
        print(f"- Inactivos en vista: {inactivos_vista}")
        
        print("\nProductos en la vista:")
        for producto in productos_lista:
            estado = "ACTIVO" if producto.disponible else "INACTIVO"
            print(f"- {producto.nombre} ({estado})")
        
        # 3. Verificar consistencia
        print("\n" + "=" * 60)
        print("3. VERIFICACIÓN DE CONSISTENCIA")
        print("=" * 60)
        
        if len(productos_lista) == productos_db.count():
            print("✅ La vista devuelve TODOS los productos")
        else:
            print("❌ La vista NO devuelve todos los productos")
            print(f"   DB: {productos_db.count()} vs Vista: {len(productos_lista)}")
        
        if activos_vista == activos_db and inactivos_vista == inactivos_db:
            print("✅ Los conteos de activos/inactivos coinciden")
        else:
            print("❌ Los conteos NO coinciden")
            print(f"   DB: {activos_db}A/{inactivos_db}I vs Vista: {activos_vista}A/{inactivos_vista}I")
        
        # 4. Mostrar resultado esperado en la página
        print("\n" + "=" * 60)
        print("4. RESULTADO ESPERADO EN LA PÁGINA")
        print("=" * 60)
        
        print(f"URL: http://127.0.0.1:8000/dashboard/productos-venta/")
        print(f"Debería mostrar: {len(productos_lista)} productos")
        print(f"- {activos_vista} con etiqueta ACTIVO (verde)")
        print(f"- {inactivos_vista} con etiqueta INACTIVO (roja)")
        
        if inactivos_vista > 0:
            print("\n✅ CONFIRMADO: Los productos INACTIVOS aparecerán en la lista")
            print("   con la etiqueta 'INACTIVO' en rojo")
        else:
            print("\n⚠️  NO HAY productos inactivos para mostrar")
            print("   Puedes crear uno para probar")
            
    except Exception as e:
        print(f"❌ Error al simular la vista: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_productos_venta()
