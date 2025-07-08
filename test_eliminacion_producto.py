"""
Utilidad para probar explícitamente la funcionalidad del botón de eliminar
"""
import requests
import json
from bs4 import BeautifulSoup
import re
import time
import os

def test_eliminacion_producto():
    """
    Prueba completa del flujo de eliminación de productos
    """
    print("=== PRUEBA COMPLETA DEL FLUJO DE ELIMINACIÓN DE PRODUCTOS ===")
    
    # Verificar que el servidor Django esté en ejecución
    try:
        response = requests.get("http://127.0.0.1:8000/dashboard/productos-venta/")
        if response.status_code != 200:
            print(f"❌ Error al conectar con el servidor Django: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error al conectar con el servidor Django: {str(e)}")
        print("Asegúrate de que el servidor esté en ejecución con 'python manage.py runserver'")
        return
    
    print("✅ Servidor Django en ejecución")
    
    # Paso 1: Obtener un producto existente
    print("\n1. Obteniendo lista de productos...")
    try:
        response = requests.get("http://127.0.0.1:8000/dashboard/productos-venta/")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar botones de eliminar para obtener IDs de productos
        delete_buttons = soup.find_all('button', {'data-bs-toggle': 'modal', 'data-bs-target': '#deleteModal'})
        
        if not delete_buttons:
            print("❌ No se encontraron productos en la página")
            return
        
        print(f"✅ Se encontraron {len(delete_buttons)} productos")
        
        # Obtener IDs de los primeros 3 productos o menos si no hay suficientes
        producto_ids = []
        for button in delete_buttons[:3]:
            producto_id = button.get('data-id')
            producto_nombre = button.get('data-nombre')
            if producto_id:
                producto_ids.append((producto_id, producto_nombre))
        
        if not producto_ids:
            print("❌ No se pudieron obtener IDs de productos")
            return
        
        print(f"✅ IDs de productos obtenidos: {[pid for pid, _ in producto_ids]}")
        
        # Obtener CSRF token
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        if not csrf_token:
            print("❌ No se pudo obtener el token CSRF")
            return
        
        csrf_value = csrf_token.get('value')
        print(f"✅ Token CSRF obtenido: {csrf_value[:10]}...")
        
        # Paso 2: Intentar eliminar el primer producto
        producto_id, producto_nombre = producto_ids[0]
        print(f"\n2. Intentando eliminar producto {producto_id} ({producto_nombre})...")
        
        # Simular el envío del formulario
        delete_url = f"http://127.0.0.1:8000/dashboard/productos-venta/{producto_id}/eliminar/"
        headers = {
            'X-CSRFToken': csrf_value,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': "http://127.0.0.1:8000/dashboard/productos-venta/"
        }
        data = {
            'csrfmiddlewaretoken': csrf_value,
            'producto_id': producto_id
        }
        
        response = requests.post(delete_url, headers=headers, data=data)
        
        print(f"✅ Respuesta recibida: {response.status_code}")
        try:
            response_data = response.json()
            print(f"✅ Respuesta JSON: {json.dumps(response_data, indent=2)}")
        except:
            print(f"⚠️ Respuesta no es JSON: {response.text[:100]}...")
        
        # Paso 3: Verificar si el producto fue eliminado
        print("\n3. Verificando si el producto fue eliminado...")
        verify_url = f"http://127.0.0.1:8000/dashboard/api/verificar-producto/{producto_id}/"
        response = requests.get(verify_url, headers={'X-Requested-With': 'XMLHttpRequest'})
        
        if response.status_code == 200:
            try:
                verify_data = response.json()
                if 'exists' in verify_data:
                    if verify_data['exists'] == False:
                        print(f"✅ El producto {producto_id} fue eliminado correctamente")
                    else:
                        print(f"⚠️ El producto {producto_id} NO fue eliminado")
                        if 'dependencias' in verify_data and verify_data['dependencias']:
                            print(f"⚠️ El producto tiene dependencias: {verify_data['dependencias']}")
                else:
                    print(f"⚠️ Respuesta de verificación no contiene campo 'exists': {verify_data}")
            except:
                print(f"⚠️ Respuesta de verificación no es JSON: {response.text[:100]}...")
        else:
            print(f"❌ Error al verificar producto: {response.status_code}")
        
        # Paso 4: Intentar eliminación forzada si el producto aún existe
        force_delete = False
        if force_delete:
            print("\n4. Intentando eliminación forzada...")
            force_url = f"http://127.0.0.1:8000/dashboard/productos-venta/{producto_id}/eliminar-forzado/"
            headers = {
                'X-CSRFToken': csrf_value,
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
                'Referer': "http://127.0.0.1:8000/dashboard/productos-venta/"
            }
            data = {
                'force': True,
                'csrftoken': csrf_value,
                'timestamp': time.time(),
                'usuario': 'test-script'
            }
            
            response = requests.post(force_url, headers=headers, data=json.dumps(data))
            
            print(f"✅ Respuesta recibida: {response.status_code}")
            try:
                response_data = response.json()
                print(f"✅ Respuesta JSON: {json.dumps(response_data, indent=2)}")
            except:
                print(f"⚠️ Respuesta no es JSON: {response.text[:100]}...")
            
            # Verificar nuevamente
            print("\nVerificando después de eliminación forzada...")
            response = requests.get(verify_url, headers={'X-Requested-With': 'XMLHttpRequest'})
            
            if response.status_code == 200:
                try:
                    verify_data = response.json()
                    if 'exists' in verify_data:
                        if verify_data['exists'] == False:
                            print(f"✅ El producto {producto_id} fue eliminado correctamente con eliminación forzada")
                        else:
                            print(f"⚠️ El producto {producto_id} NO fue eliminado incluso con eliminación forzada")
                    else:
                        print(f"⚠️ Respuesta de verificación no contiene campo 'exists': {verify_data}")
                except:
                    print(f"⚠️ Respuesta de verificación no es JSON: {response.text[:100]}...")
            else:
                print(f"❌ Error al verificar producto después de eliminación forzada: {response.status_code}")
        
        print("\n=== PRUEBA COMPLETA ===")
        print("La eliminación de productos ha sido probada.")
        print("Consulta los logs para más detalles.")
        print("Para probar la eliminación en la interfaz de usuario:")
        print("1. Visita http://127.0.0.1:8000/dashboard/productos-venta/")
        print("2. Haz clic en el botón de eliminar de un producto")
        print("3. Confirma la eliminación")
        print("4. Verifica que el producto se haya eliminado")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_eliminacion_producto()
