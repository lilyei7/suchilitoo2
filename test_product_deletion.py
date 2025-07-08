"""
Script para probar la eliminación de productos via AJAX

Este script ayuda a verificar que la funcionalidad de eliminación 
de productos está trabajando correctamente, enfocándose en la respuesta
del servidor y manejo de errores.
"""

import requests
import json
import sys
import os
import django

# Configurar el entorno Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushitoo.settings')
django.setup()

# Importar los modelos necesarios
from restaurant.models import ProductoVenta
from django.contrib.auth.models import User

def get_csrf_token():
    """Obtener un CSRF token del servidor"""
    session = requests.Session()
    response = session.get('http://localhost:8000/accounts/login/')
    csrf_token = None
    
    # Intentar extraer el CSRF token de la respuesta
    if response.status_code == 200:
        # Buscar en cookies
        if 'csrftoken' in session.cookies:
            csrf_token = session.cookies['csrftoken']
        # Buscar en el HTML
        elif 'csrfmiddlewaretoken' in response.text:
            import re
            match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
            if match:
                csrf_token = match.group(1)
    
    return session, csrf_token

def test_delete_product(product_id):
    """Probar eliminar un producto via AJAX"""
    print(f"\n🔍 Probando eliminación del producto ID: {product_id}")
    
    # Verificar si el producto existe
    try:
        producto = ProductoVenta.objects.get(id=product_id)
        print(f"✓ Producto encontrado: {producto.nombre}")
    except ProductoVenta.DoesNotExist:
        print(f"✗ Error: Producto con ID {product_id} no existe")
        return False
    
    # Obtener CSRF token
    session, csrf_token = get_csrf_token()
    if not csrf_token:
        print("✗ Error: No se pudo obtener CSRF token")
        return False
    
    # Iniciar sesión como admin
    try:
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            print("✗ Error: No hay usuarios admin en la base de datos")
            return False
        
        login_data = {
            'username': admin.username,
            'password': 'admin',  # Asumiendo que esta es la contraseña
            'csrfmiddlewaretoken': csrf_token
        }
        
        login_response = session.post('http://localhost:8000/accounts/login/', 
                                     data=login_data, 
                                     headers={'Referer': 'http://localhost:8000/accounts/login/'})
        
        if login_response.status_code != 200 or "Iniciar sesión" in login_response.text:
            print("✗ Error: No se pudo iniciar sesión")
            return False
            
        print(f"✓ Sesión iniciada como {admin.username}")
    except Exception as e:
        print(f"✗ Error al iniciar sesión: {str(e)}")
        return False
    
    # Eliminar el producto via AJAX
    delete_url = f'http://localhost:8000/dashboard/productos-venta/{product_id}/eliminar/'
    
    headers = {
        'X-CSRFToken': csrf_token,
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'http://localhost:8000/dashboard/productos-venta/'
    }
    
    try:
        delete_response = session.post(delete_url, headers=headers)
        
        print(f"✓ Respuesta del servidor: {delete_response.status_code}")
        
        if delete_response.status_code == 200:
            try:
                response_data = delete_response.json()
                print(f"✓ Respuesta JSON: {json.dumps(response_data, indent=2)}")
                
                if response_data.get('success'):
                    print("✅ Producto eliminado exitosamente")
                    return True
                else:
                    print(f"✗ Error del servidor: {response_data.get('message', 'Error desconocido')}")
                    return False
            except ValueError:
                print("✗ Error: Respuesta no es JSON válido")
                print(f"Contenido: {delete_response.text[:200]}...")
                return False
        else:
            print(f"✗ Error HTTP: {delete_response.status_code}")
            print(f"Contenido: {delete_response.text[:200]}...")
            return False
    except Exception as e:
        print(f"✗ Error al eliminar producto: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🧪 Test de eliminación de productos")
    print("=" * 50)
    
    # Mostrar productos disponibles
    productos = ProductoVenta.objects.all()
    print(f"Productos disponibles: {productos.count()}")
    
    for p in productos[:10]:  # Mostrar solo los primeros 10
        print(f"ID: {p.id} - {p.nombre}")
    
    if productos.count() > 10:
        print(f"... y {productos.count() - 10} más")
    
    # Solicitar ID para eliminar
    try:
        product_id = input("\nIngrese ID del producto a eliminar (o 'q' para salir): ")
        
        if product_id.lower() == 'q':
            print("Operación cancelada.")
            return
            
        product_id = int(product_id)
        test_delete_product(product_id)
    except ValueError:
        print("ID inválido. Debe ser un número.")
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.")

if __name__ == "__main__":
    main()
