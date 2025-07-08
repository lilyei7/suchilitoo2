import os
import django
import webbrowser
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Configurar entorno Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sushi_core.settings")
django.setup()

# Verificar URL base
HOST = "http://127.0.0.1:8000"
MESERO_BASE = f"{HOST}/mesero"

# URLs a verificar
urls = [
    f"{MESERO_BASE}/test/",    # Vista de prueba
    f"{MESERO_BASE}/",         # Dashboard
    f"{MESERO_BASE}/login/",   # Login
    f"{MESERO_BASE}/mesas/"    # Mesas
]

print("=== Verificación de URLs del Sistema Mesero ===")
print(f"URL base: {HOST}")

for i, url in enumerate(urls, 1):
    print(f"\nAbriendo URL {i}/{len(urls)}: {url}")
    webbrowser.open(url)
    
    # Esperar para que el usuario pueda ver la página
    if i < len(urls):
        time.sleep(2)  # Esperar 2 segundos entre cada URL

print("\n¡Verificación de URLs completada!")
print("Verifica si las páginas se están cargando correctamente en tu navegador.")
