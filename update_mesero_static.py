import os
import sys

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

import django
django.setup()

import time
from django.contrib.staticfiles import finders
from django.core.management import call_command
from pathlib import Path

# Mensaje informativo
print("===== ACTUALIZANDO ARCHIVOS ESTÁTICOS DEL SISTEMA MESERO =====")

# Verificar directorio de estáticos
css_path = Path('mesero/static/mesero/css/mesero-style.css')
if not css_path.exists():
    print(f"❌ Error: No se encuentra el archivo CSS en {css_path}")
    sys.exit(1)

# Ejecutar collectstatic
print("\n📦 Ejecutando collectstatic para actualizar archivos estáticos...")
call_command('collectstatic', interactive=False, verbosity=0)

# Verificar que los archivos estén disponibles
css_file = finders.find('mesero/css/mesero-style.css')
if css_file:
    print(f"✅ CSS encontrado en: {css_file}")
else:
    print("❌ Error: CSS no encontrado después de collectstatic")

# Instrucciones para el usuario
print("\n✅ Archivos estáticos actualizados correctamente.")
print("\n📌 Instrucciones para verificar el sistema:")
print("1. Asegúrate de que el servidor esté ejecutándose (python manage.py runserver)")
print("2. Accede a http://127.0.0.1:8000/mesero/login/")
print("3. Inicia sesión con las credenciales (mesero1/mesero123)")
print("4. Navega a http://127.0.0.1:8000/mesero/menu/ para ver el menú moderno")
print("5. Navega a http://127.0.0.1:8000/mesero/mesas/ y selecciona una mesa")
print("6. Haz clic en 'Nueva Orden' para ver el diseño moderno de la vista de nuevas órdenes")
