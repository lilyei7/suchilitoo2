import requests
import os
import time

def save_html_source():
    # URL del servidor local
    inventario_url = "http://127.0.0.1:8000/dashboard/inventario/"
    
    try:
        # Intenta acceder a la página de inventario
        response = requests.get(inventario_url)
        if response.status_code != 200:
            print(f"❌ No se pudo acceder a {inventario_url}")
            print(f"Código de estado: {response.status_code}")
            return
        
        # Guardar el contenido HTML completo en un archivo
        html_file_path = os.path.join(os.path.dirname(__file__), "inventario_page_source.html")
        with open(html_file_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print(f"✅ HTML completo guardado en: {html_file_path}")
        print("Examina este archivo para diagnosticar problemas con los scripts")
        
    except Exception as e:
        print(f"❌ Error al guardar HTML: {str(e)}")

if __name__ == "__main__":
    # Esperar a que el servidor esté listo
    print("Esperando a que el servidor Django esté listo...")
    time.sleep(2)
    save_html_source()
