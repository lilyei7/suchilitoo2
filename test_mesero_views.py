import requests
import sys
import time
import webbrowser
from urllib.parse import urljoin

def test_views(view_name):
    print(f"Verificando acceso a la vista '{view_name}' del módulo mesero...")
    
    # URL base
    base_url = "http://127.0.0.1:8000"
    
    # URL de la vista
    view_url = urljoin(base_url, f"/mesero/{view_name}/")
    
    try:
        # Intentar acceder a la vista
        response = requests.get(view_url, timeout=5)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            print(f"✅ La vista '{view_name}' está disponible (Código: {response.status_code})")
            print(f"✅ Tamaño de la respuesta: {len(response.content)} bytes")
            
            # Abrir en navegador con timestamp para evitar caché
            timestamp = int(time.time())
            url_with_param = f"{view_url}?t={timestamp}"
            webbrowser.open(url_with_param)
            
            return True
        else:
            print(f"❌ Error al acceder a la vista '{view_name}' (Código: {response.status_code})")
            if len(response.text) > 500:
                print(f"Respuesta: {response.text[:500]}...")
            else:
                print(f"Respuesta: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        print("Asegúrate de que el servidor Django esté en ejecución.")
        return False

if __name__ == "__main__":
    views_to_test = [
        "menu_moderno"
    ]
    
    # Vistas que requieren parámetros
    views_with_params = {
        "mesa/1/nueva-orden-moderna": "nueva_orden_moderna con mesa_id=1"
    }
    
    for view in views_to_test:
        print("\n" + "="*50)
        test_views(view)
        print("="*50 + "\n")
    
    for view_path, view_name in views_with_params.items():
        print("\n" + "="*50)
        test_views(view_path)
        print("="*50 + "\n")
