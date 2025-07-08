import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

import json
from django.test import Client
from restaurant.models import ProductoVenta

print("🧪 PRUEBA DE VISTA AJAX DETALLE PRODUCTO")
print("=" * 50)

# Crear cliente de prueba
client = Client()

# Obtener un producto para probar
producto = ProductoVenta.objects.filter(disponible=True).first()

if producto:
    print(f"Probando con producto: {producto.nombre} (ID: {producto.id})")
    
    # Hacer la petición AJAX
    response = client.get(f'/mesero/producto-detalle/{producto.id}/')
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.get('Content-Type', 'N/A')}")
    
    if response.status_code == 200:
        try:
            data = json.loads(response.content)
            print("✅ Respuesta JSON válida")
            print(f"Success: {data.get('success')}")
            
            if data.get('success'):
                producto_data = data.get('producto', {})
                print("\n📋 DETALLES DEL PRODUCTO:")
                print(f"  - Nombre: {producto_data.get('nombre')}")
                print(f"  - Precio: ${producto_data.get('precio')}")
                print(f"  - Descripción: {producto_data.get('descripcion')}")
                print(f"  - Imagen: {'✓' if producto_data.get('imagen') else '✗'}")
                print(f"  - Disponible: {'✓' if producto_data.get('disponible') else '✗'}")
                print(f"  - Tiempo prep: {producto_data.get('tiempo_preparacion')} min")
                print(f"  - Calorías: {producto_data.get('calorias')}")
                print(f"  - Tipo: {producto_data.get('tipo')}")
                print(f"  - Categoría: {producto_data.get('categoria')}")
                print("\n✅ LA VISTA AJAX FUNCIONA CORRECTAMENTE")
            else:
                print(f"❌ Error en la respuesta: {data.get('error')}")
        except json.JSONDecodeError as e:
            print(f"❌ Error al decodificar JSON: {e}")
            print(f"Contenido de la respuesta: {response.content}")
    else:
        print(f"❌ Error en la petición: {response.status_code}")
        print(f"Contenido: {response.content}")
else:
    print("❌ No hay productos disponibles para probar")

print("\n" + "=" * 50)
print("🌐 INSTRUCCIONES PARA PROBAR EN EL NAVEGADOR:")
print("1. Ve a: http://127.0.0.1:8000/mesero/menu/")
print("2. Haz clic en cualquier imagen de producto")
print("3. El modal debería abrirse mostrando todos los detalles")
print("4. Verifica que puedas cerrar el modal")
print("5. Verifica que puedas agregar productos al pedido desde el modal")
