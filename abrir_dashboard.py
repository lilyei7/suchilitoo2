"""
Script para abrir el dashboard en el navegador
"""
import webbrowser
import time

def abrir_dashboard():
    # URL base
    base_url = "http://127.0.0.1:8000/mesero/"
    
    # Agregar timestamp para forzar recarga sin caché
    timestamp = int(time.time())
    url = f"{base_url}?t={timestamp}"
    
    print(f"Abriendo dashboard en: {url}")
    webbrowser.open(url)
    
    print("Dashboard abierto en el navegador.")

if __name__ == "__main__":
    abrir_dashboard()
