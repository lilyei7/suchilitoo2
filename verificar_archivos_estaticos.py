import os
import django
from django.conf import settings
from django.core.management import execute_from_command_line
from django.contrib.staticfiles.finders import find

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

print("=== VERIFICACIÓN DE ARCHIVOS ESTÁTICOS ===")
print(f"DEBUG = {settings.DEBUG}")
print(f"STATIC_URL = {settings.STATIC_URL}")
print(f"STATIC_ROOT = {getattr(settings, 'STATIC_ROOT', 'No configurado')}")

print("\n=== STATICFILES_DIRS ===")
staticfiles_dirs = getattr(settings, 'STATICFILES_DIRS', [])
for i, dir_path in enumerate(staticfiles_dirs):
    print(f"{i+1}. {dir_path}")
    if os.path.exists(dir_path):
        print(f"   ✓ Existe")
        files = os.listdir(dir_path)[:10]  # Primeros 10 archivos
        for f in files:
            print(f"     - {f}")
    else:
        print(f"   ✗ No existe")

print("\n=== VERIFICANDO ARCHIVOS CSS/JS ESPECÍFICOS ===")
archivos_criticos = [
    'css/bootstrap.min.css',
    'css/style.css',
    'js/bootstrap.min.js',
    'js/jquery.min.js',
    'css/mesero.css',
    'js/mesero.js'
]

for archivo in archivos_criticos:
    resultado = find(archivo)
    if resultado:
        print(f"✓ {archivo} encontrado en: {resultado}")
    else:
        print(f"✗ {archivo} NO encontrado")

print("\n=== VERIFICANDO DIRECTORIOS STATIC EN APPS ===")
apps_dirs = [
    'mesero/static',
    'static',
    'staticfiles'
]

for dir_path in apps_dirs:
    full_path = os.path.join(os.getcwd(), dir_path)
    if os.path.exists(full_path):
        print(f"✓ {dir_path} existe")
        # Listar contenido
        try:
            for root, dirs, files in os.walk(full_path):
                if files:
                    rel_root = os.path.relpath(root, full_path)
                    print(f"  {rel_root}:")
                    for f in files[:5]:  # Primeros 5 archivos
                        print(f"    - {f}")
        except Exception as e:
            print(f"  Error listando: {e}")
    else:
        print(f"✗ {dir_path} no existe")
