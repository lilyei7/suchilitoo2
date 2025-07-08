"""
Script para verificar y aplicar cambios en archivos estáticos
"""
import os
import django
import sys
import webbrowser
from pathlib import Path
import time

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def verificar_archivos_estaticos():
    """Verifica y aplica cambios en archivos estáticos"""
    
    print("=== Verificando archivos estáticos ===")
    
    # Verificar directorio static
    static_dir = Path("mesero/static/mesero/css")
    if not static_dir.exists():
        print(f"Creando directorio: {static_dir}")
        static_dir.mkdir(parents=True, exist_ok=True)
    
    # Ejecutar collectstatic
    print("\nEjecutando collectstatic...")
    os.system('python manage.py collectstatic --noinput')
    
    # Reiniciar servidor
    print("\nReiniciando servidor...")
    os.system('python restart_server.py')
    
    # Esperar un momento para que el servidor se reinicie
    print("\nEsperando a que el servidor esté listo...")
    time.sleep(3)
    
    # Abrir el navegador con timestamp para forzar recarga
    url = f"http://127.0.0.1:8000/mesero/?t={int(time.time())}"
    print(f"\nAbriendo {url}")
    webbrowser.open(url)
    
    print("\n=== Proceso completado ===")

if __name__ == "__main__":
    verificar_archivos_estaticos()
