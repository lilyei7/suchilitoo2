import os
import sys
import shutil
import subprocess

def limpiar_cache():
    """Limpia la caché de Python y Django"""
    # Limpiar archivos .pyc
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
        for dir in dirs:
            if dir == '__pycache__':
                shutil.rmtree(os.path.join(root, dir))
    
    # Limpiar directorio de estáticos si existe
    static_root = os.path.join('.', 'static')
    if os.path.exists(static_root):
        shutil.rmtree(static_root)

def main():
    print("Limpiando caché...")
    limpiar_cache()
    
    print("Recolectando archivos estáticos...")
    subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'])
    
    print("\nIniciando servidor de desarrollo...")
    subprocess.run([sys.executable, 'manage.py', 'runserver'])

if __name__ == '__main__':
    main()
