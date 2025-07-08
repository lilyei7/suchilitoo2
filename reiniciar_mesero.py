import os
import sys
import shutil
import subprocess
import webbrowser
from time import sleep

def limpiar_cache():
    """Limpia la caché de Python y Django"""
    print("Limpiando caché...")
    
    # Limpiar archivos .pyc
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
                print(f"Eliminado: {os.path.join(root, file)}")
        for dir in dirs:
            if dir == '__pycache__':
                shutil.rmtree(os.path.join(root, dir))
                print(f"Eliminado: {os.path.join(root, dir)}")

def recolectar_estaticos():
    """Recolecta archivos estáticos"""
    print("\nRecolectando archivos estáticos...")
    static_root = os.path.join('.', 'static')
    if os.path.exists(static_root):
        shutil.rmtree(static_root)
    subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'])

def abrir_navegador():
    """Abre el navegador en la página de login"""
    print("\nAbriendo navegador...")
    sleep(2)  # Esperar a que el servidor esté listo
    webbrowser.open('http://localhost:8000/mesero/login/')

def main():
    """Función principal"""
    print("=== REINICIANDO SISTEMA DE MESERO ===")
    
    # 1. Limpiar caché
    limpiar_cache()
    
    # 2. Recolectar estáticos
    recolectar_estaticos()
    
    # 3. Abrir navegador
    abrir_navegador()
    
    # 4. Iniciar servidor
    print("\nIniciando servidor...")
    subprocess.run([sys.executable, 'manage.py', 'runserver'])

if __name__ == '__main__':
    main()
