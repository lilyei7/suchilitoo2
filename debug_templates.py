import os
from django.conf import settings
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def debug_template(template_name):
    """Intenta cargar un template y muestra información de debug"""
    print(f"\nDebug para template: {template_name}")
    print("-" * 50)
    
    # 1. Verificar directorios de búsqueda
    print("Directorios de búsqueda:")
    for dir in settings.TEMPLATES[0]['DIRS']:
        print(f"- {dir}")
        # Verificar si el directorio existe
        if os.path.exists(dir):
            print("  ✓ Directorio existe")
            # Listar contenido
            for root, dirs, files in os.walk(dir):
                for file in files:
                    if file.endswith('.html'):
                        print(f"    - {os.path.join(os.path.relpath(root, dir), file)}")
        else:
            print("  ✗ Directorio no existe")
    
    # 2. Verificar APP_DIRS
    print(f"\nAPP_DIRS habilitado: {settings.TEMPLATES[0]['APP_DIRS']}")
    
    # 3. Intentar cargar el template
    try:
        template = get_template(template_name)
        print(f"\n✓ Template encontrado: {template.origin.name}")
    except TemplateDoesNotExist as e:
        print(f"\n✗ Template no encontrado: {str(e)}")
        # Buscar manualmente el archivo
        for app in settings.INSTALLED_APPS:
            if '.' in app:
                app = app.split('.')[-1]
            template_dir = os.path.join(settings.BASE_DIR, app, 'templates')
            if os.path.exists(template_dir):
                print(f"\nBuscando en {template_dir}:")
                for root, dirs, files in os.walk(template_dir):
                    for file in files:
                        if file.endswith('.html'):
                            print(f"- {os.path.join(os.path.relpath(root, template_dir), file)}")

if __name__ == '__main__':
    templates_to_check = [
        'base.html',
        'mesero/menu.html',
        'mesero/login_simple.html'
    ]
    
    for template in templates_to_check:
        debug_template(template)
