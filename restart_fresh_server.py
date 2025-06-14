"""
Script para forzar actualización y limpiar caché
Reinicia el servidor con parámetros que eviten problemas de caché
"""

import os
import time
import subprocess
import signal

def kill_existing_servers():
    """Matar procesos de Django existentes"""
    try:
        # Para Windows
        subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                      capture_output=True, check=False)
        time.sleep(2)
    except:
        pass

def clear_cache():
    """Limpiar archivos de caché de Django"""
    cache_dirs = [
        "__pycache__",
        "dashboard/__pycache__", 
        "sushi_core/__pycache__",
        "restaurant/__pycache__"
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                import shutil
                shutil.rmtree(cache_dir)
                print(f"✅ Eliminado cache: {cache_dir}")
            except:
                print(f"⚠️ No se pudo eliminar: {cache_dir}")

def start_fresh_server():
    """Iniciar servidor fresco"""
    print("🚀 Iniciando servidor con configuración anti-caché...")
    
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'sushi_core.settings'
    env['PYTHONDONTWRITEBYTECODE'] = '1'  # No crear .pyc
    
    # Comando con parámetros anti-caché
    cmd = [
        "python", "manage.py", "runserver",
        "--settings=sushi_core.settings",
        "--noreload"  # Evitar recarga automática
    ]
    
    process = subprocess.Popen(cmd, env=env)
    return process

def main():
    print("🔄 REINICIO COMPLETO DE SERVIDOR")
    print("=" * 40)
    
    print("1. Matando procesos existentes...")
    kill_existing_servers()
    
    print("2. Limpiando caché...")
    clear_cache()
    
    print("3. Iniciando servidor fresco...")
    process = start_fresh_server()
    
    print("✅ Servidor iniciado")
    print("\n📌 INSTRUCCIONES:")
    print("1. Ve a http://127.0.0.1:8000/dashboard/proveedores/")
    print("2. Presiona Ctrl+F5 para forzar recarga del navegador")
    print("3. Abre las herramientas de desarrollador (F12)")
    print("4. Ve a la pestaña Network/Red") 
    print("5. Marca 'Disable cache' si está disponible")
    print("6. Prueba los botones Ver, Editar, Eliminar")
    print("7. Observa las llamadas en la pestaña Network")
    print("\n💡 Para detener el servidor: Ctrl+C")
    
    try:
        # Mantener el script corriendo hasta que el usuario lo detenga
        process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servidor...")
        process.terminate()
        print("✅ Servidor detenido")

if __name__ == "__main__":
    main()
