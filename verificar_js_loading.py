"""
Utilidad para verificar que el JavaScript se está cargando en las páginas
"""
import requests
from bs4 import BeautifulSoup
import re

def verificar_js_loading():
    """
    Verifica que el JavaScript se está cargando correctamente en diferentes páginas
    """
    print("=== VERIFICANDO CARGA DE JAVASCRIPT ===")
    
    # URLs para probar
    urls = [
        "http://127.0.0.1:8000/dashboard/productos-venta/",
        "http://127.0.0.1:8000/dashboard/productos-venta/diagnostico/"
    ]
    
    for url in urls:
        print(f"\nProbando URL: {url}")
        try:
            response = requests.get(url)
            
            if response.status_code != 200:
                print(f"❌ Error al cargar la página: {response.status_code}")
                continue
            
            # Analizar la página con BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Verificar que la página tenga scripts
            scripts = soup.find_all('script')
            if not scripts:
                print("❌ No se encontraron scripts en la página")
                continue
            
            print(f"✅ Se encontraron {len(scripts)} scripts en la página")
            
            # Verificar que haya scripts dentro del bloque extra_js
            js_logs_found = False
            js_debug_lines = []
            
            for script in scripts:
                if script.string and "console.log(" in script.string:
                    js_logs_found = True
                    for line in script.string.split('\n'):
                        if "console.log(" in line:
                            js_debug_lines.append(line.strip())
            
            if js_logs_found:
                print("✅ Se encontraron logs de depuración en la página")
                print(f"   Primeros logs encontrados: {len(js_debug_lines)} logs")
                for i, line in enumerate(js_debug_lines[:3]):
                    print(f"   {i+1}. {line[:80]}...")
            else:
                print("❌ No se encontraron logs de depuración en la página")
            
            # Verificar si la página tiene el bloque extra_js
            page_source = response.text
            if "{% block extra_js %}" in page_source and "{% endblock %}" in page_source:
                print("✅ La página utiliza el bloque extra_js")
            else:
                print("❌ No se encontró el bloque extra_js en la página")
            
            # Buscar específicamente scripts de eliminación
            deletion_js_found = False
            for script in scripts:
                if script.string and ('deleteForm' in script.string or 'deleteModal' in script.string):
                    deletion_js_found = True
                    break
            
            if deletion_js_found:
                print("✅ Se encontró JavaScript relacionado con la eliminación")
            else:
                print("❌ No se encontró JavaScript relacionado con la eliminación")
                
        except Exception as e:
            print(f"❌ Error al verificar la página: {str(e)}")
    
    print("\n=== RECOMENDACIONES ===")
    print("1. Verifica en el navegador que los logs aparecen en la consola (F12 -> Console)")
    print("2. Asegúrate de que el bloque extra_js contiene el JavaScript necesario")
    print("3. Verifica que no hay errores de sintaxis en el JavaScript")
    print("4. Prueba los botones de eliminación para verificar el funcionamiento")

if __name__ == "__main__":
    verificar_js_loading()
