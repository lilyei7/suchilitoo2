import os
import sys
import django
from django.template.loader import get_template
from django.conf import settings
from django.urls import reverse, resolve, URLPattern, URLResolver
from django.core.wsgi import get_wsgi_application

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def check_template_exists(template_name):
    """Verifica si un template existe y puede ser cargado"""
    try:
        template = get_template(template_name)
        return True, None
    except Exception as e:
        return False, str(e)

def check_url_pattern(urlpattern, parent_pattern=""):
    """Analiza recursivamente los patrones de URL"""
    patterns = []
    if isinstance(urlpattern, URLPattern):
        patterns.append({
            'pattern': str(parent_pattern) + str(urlpattern.pattern),
            'name': urlpattern.name,
            'callback': urlpattern.callback.__name__ if hasattr(urlpattern.callback, '__name__') else str(urlpattern.callback)
        })
    elif isinstance(urlpattern, URLResolver):
        for pattern in urlpattern.url_patterns:
            patterns.extend(check_url_pattern(pattern, str(parent_pattern) + str(urlpattern.pattern)))
    return patterns

def run_diagnostics():
    """Ejecuta diagnósticos completos del sistema mesero"""
    print("\n=== DIAGNÓSTICO DEL SISTEMA MESERO ===\n")

    # 1. Verificar configuración
    print("1. CONFIGURACIÓN BÁSICA:")
    print(f"DEBUG = {settings.DEBUG}")
    print(f"BASE_DIR = {settings.BASE_DIR}")
    print(f"INSTALLED_APPS = {', '.join(settings.INSTALLED_APPS)}")
    
    # 2. Verificar directorios de templates
    print("\n2. DIRECTORIOS DE TEMPLATES:")
    for template_dir in settings.TEMPLATES[0]['DIRS']:
        print(f"Directorio: {template_dir}")
        if os.path.exists(template_dir):
            print(f"  ✅ Existe")
            # Listar contenido
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if file.endswith('.html'):
                        print(f"    - {os.path.join(os.path.relpath(root, template_dir), file)}")
        else:
            print(f"  ❌ No existe")

    # 3. Verificar templates específicos
    print("\n3. VERIFICACIÓN DE TEMPLATES:")
    templates_to_check = [
        'base.html',
        'mesero/menu.html',
        'mesero/login_simple.html'
    ]
    for template_name in templates_to_check:
        exists, error = check_template_exists(template_name)
        if exists:
            print(f"✅ {template_name} - OK")
        else:
            print(f"❌ {template_name} - Error: {error}")

    # 4. Analizar URLs
    print("\n4. ANÁLISIS DE URLs:")
    from sushi_core.urls import urlpatterns
    
    def print_url_patterns(patterns, level=0):
        for pattern in patterns:
            print("  " * level + f"- {pattern['pattern']} → {pattern['callback']}")
            if hasattr(pattern, 'url_patterns'):
                print_url_patterns(pattern.url_patterns, level + 1)

    all_patterns = []
    for urlpattern in urlpatterns:
        all_patterns.extend(check_url_pattern(urlpattern))
    
    for pattern in all_patterns:
        print(f"URL: {pattern['pattern']}")
        print(f"  Nombre: {pattern['name']}")
        print(f"  Vista: {pattern['callback']}")
        print()

    print("\n5. VERIFICACIÓN DE ARCHIVOS ESTÁTICOS:")
    static_dirs = settings.STATICFILES_DIRS if hasattr(settings, 'STATICFILES_DIRS') else []
    print(f"STATIC_URL = {settings.STATIC_URL}")
    print(f"STATIC_ROOT = {settings.STATIC_ROOT}")
    print("Directorios estáticos adicionales:")
    for static_dir in static_dirs:
        print(f"  - {static_dir}")

    # 6. Verificar permisos de archivos
    print("\n6. PERMISOS DE ARCHIVOS:")
    template_dirs = settings.TEMPLATES[0]['DIRS']
    for dir_path in template_dirs:
        if os.path.exists(dir_path):
            try:
                test_file = os.path.join(dir_path, 'test_permissions.tmp')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print(f"✅ {dir_path} - Permisos de escritura OK")
            except Exception as e:
                print(f"❌ {dir_path} - Error de permisos: {e}")
        else:
            print(f"❌ {dir_path} - Directorio no existe")

if __name__ == '__main__':
    run_diagnostics()
