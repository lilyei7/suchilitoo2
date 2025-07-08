import requests
import sys
import time
import webbrowser
from urllib.parse import urljoin

def test_dashboard():
    print("Verificando acceso a la vista de dashboard del mesero...")
    
    # URL base
    base_url = "http://127.0.0.1:8000"
    
    # URL de la vista del dashboard del mesero
    dashboard_url = urljoin(base_url, "/mesero/")
    
    try:
        # Intentar acceder a la vista
        response = requests.get(dashboard_url, timeout=5)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            print(f"✅ La vista de dashboard del mesero está disponible (Código: {response.status_code})")
            print(f"✅ Tamaño de la respuesta: {len(response.content)} bytes")
            
            # Abrir en navegador con timestamp para evitar caché
            timestamp = int(time.time())
            url_with_param = f"{dashboard_url}?t={timestamp}"
            webbrowser.open(url_with_param)
            
            return True
        else:
            print(f"❌ Error al acceder a la vista del dashboard del mesero (Código: {response.status_code})")
            print(f"Respuesta: {response.text[:500]}...")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        print("Asegúrate de que el servidor Django esté en ejecución.")
        return False

if __name__ == "__main__":
    test_dashboard()
