import os
import shutil
import django
from django.core.management import call_command
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def limpiar_cache():
    """Limpia todos los archivos de caché"""
    print("Limpiando caché...")
    
    # Limpiar __pycache__
    for root, dirs, files in os.walk('.'):
        for dir in dirs:
            if dir == '__pycache__':
                shutil.rmtree(os.path.join(root, dir))
                print(f"Eliminado: {os.path.join(root, dir)}")
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
                print(f"Eliminado: {os.path.join(root, file)}")

def verificar_templates():
    """Verifica la estructura de templates"""
    print("\nVerificando templates...")
    
    template_dirs = settings.TEMPLATES[0]['DIRS']
    for dir in template_dirs:
        print(f"\nRevisando: {dir}")
        if os.path.exists(dir):
            print("✓ Directorio existe")
            for root, dirs, files in os.walk(dir):
                for file in files:
                    if file.endswith('.html'):
                        print(f"  - {os.path.join(os.path.relpath(root, dir), file)}")
        else:
            print("✗ Directorio no existe")
            try:
                os.makedirs(dir)
                print(f"  ✓ Directorio creado: {dir}")
            except Exception as e:
                print(f"  ✗ Error creando directorio: {e}")

def main():
    """Función principal de limpieza"""
    print("=== LIMPIEZA DEL SISTEMA ===")
    
    # 1. Limpiar caché
    limpiar_cache()
    
    # 2. Verificar templates
    verificar_templates()
    
    # 3. Recolectar estáticos
    print("\nRecolectando archivos estáticos...")
    try:
        if os.path.exists(settings.STATIC_ROOT):
            shutil.rmtree(settings.STATIC_ROOT)
        call_command('collectstatic', '--noinput')
    except Exception as e:
        print(f"Error recolectando estáticos: {e}")
    
    print("\n=== LIMPIEZA COMPLETADA ===")
    print("Ahora puedes reiniciar el servidor Django")

if __name__ == '__main__':
    main()
