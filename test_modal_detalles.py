#!/usr/bin/env python
"""
Script para probar la funcionalidad del modal de detalles de producto
"""
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta
import requests

def test_vista_detalle_producto():
    """Probar la vista de detalles de producto"""
    print("=== TEST VISTA DETALLE PRODUCTO ===")
    
    # Obtener un producto de prueba
    producto = ProductoVenta.objects.filter(disponible=True).first()
    
    if not producto:
        print("✗ No hay productos disponibles para probar")
        return
    
    print(f"Probando con producto: {producto.nombre} (ID: {producto.id})")
    
    # Probar la URL
    url = f"http://127.0.0.1:8000/mesero/producto-detalle/{producto.id}/"
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("✓ Vista funciona correctamente")
                producto_data = data['producto']
                print(f"  - Nombre: {producto_data['nombre']}")
                print(f"  - Precio: ${producto_data['precio']}")
                print(f"  - Descripción: {producto_data['descripcion']}")
                print(f"  - Tiempo preparación: {producto_data['tiempo_preparacion']} min")
                print(f"  - Disponible: {producto_data['disponible']}")
                print(f"  - Imagen: {producto_data['imagen']}")
            else:
                print(f"✗ Error en respuesta: {data.get('error', 'Error desconocido')}")
        else:
            print(f"✗ Error HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error de conexión: {e}")

def verificar_productos_con_datos():
    """Verificar que los productos tienen datos completos"""
    print("\n=== VERIFICACIÓN PRODUCTOS ===")
    
    productos = ProductoVenta.objects.filter(disponible=True)[:5]
    
    for producto in productos:
        print(f"\nProducto: {producto.nombre}")
        print(f"  - ID: {producto.id}")
        print(f"  - Código: {producto.codigo}")
        print(f"  - Precio: ${producto.precio}")
        print(f"  - Imagen: {'✓' if producto.imagen else '✗'}")
        print(f"  - Descripción: {'✓' if producto.descripcion else '✗'}")
        print(f"  - Categoría: {producto.categoria.nombre if producto.categoria else 'Sin categoría'}")
        print(f"  - Tipo: {producto.get_tipo_display()}")
        print(f"  - Calorías: {producto.calorias or 'No especificado'}")

def main():
    print("PRUEBA DE MODAL DE DETALLES DE PRODUCTO")
    print("=" * 50)
    
    verificar_productos_con_datos()
    test_vista_detalle_producto()
    
    print("\n=== INSTRUCCIONES DE PRUEBA ===")
    print("1. Abre el navegador en: http://127.0.0.1:8000/mesero/menu/")
    print("2. Haz click en cualquier imagen de producto")
    print("3. Debería abrirse un modal con los detalles del producto")
    print("4. Verifica que muestre:")
    print("   - Imagen grande del producto")
    print("   - Nombre y precio")
    print("   - Descripción completa")
    print("   - Tiempo de preparación")
    print("   - Calorías (si está disponible)")
    print("   - Estado de disponibilidad")
    print("   - Botón para agregar al pedido")
    print("\n🎉 ¡Funcionalidad implementada!")

if __name__ == "__main__":
    main()
