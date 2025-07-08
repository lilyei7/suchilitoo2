import os
import sys
import subprocess
import shutil
from pathlib import Path

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

import django
django.setup()

from django.conf import settings

print("===== FORZANDO RECARGA DE ARCHIVOS ESTÁTICOS =====")

# 1. Borrar archivos estáticos recolectados
staticfiles_dir = settings.STATIC_ROOT
print(f"\n1) Limpiando directorio de archivos estáticos: {staticfiles_dir}")

if os.path.exists(staticfiles_dir):
    for item in os.listdir(staticfiles_dir):
        item_path = os.path.join(staticfiles_dir, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
            print(f"   Eliminado directorio: {item}")
        else:
            os.remove(item_path)
            print(f"   Eliminado archivo: {item}")
else:
    os.makedirs(staticfiles_dir, exist_ok=True)
    print(f"   Creado directorio: {staticfiles_dir}")

# 2. Ejecutar collectstatic
print("\n2) Recolectando archivos estáticos...")
subprocess.run([sys.executable, "manage.py", "collectstatic", "--noinput"])

# 3. Detener todos los servidores Django en el puerto 8000
print("\n3) Deteniendo servidores Django existentes...")
try:
    if os.name == 'nt':  # Windows
        os.system("taskkill /F /IM python.exe /T")
    else:
        os.system("pkill -f runserver")
except Exception as e:
    print(f"   Error al detener servidores: {e}")

# 4. Iniciar un nuevo servidor Django
print("\n4) Iniciando nuevo servidor Django...")
subprocess.Popen([sys.executable, "manage.py", "runserver"])

print("\n✅ Proceso completado! Los archivos estáticos han sido actualizados.")
print("   Por favor, recarga la página en tu navegador con Ctrl+F5 para borrar la caché.")
print("   URL del menú: http://127.0.0.1:8000/mesero/menu/")
