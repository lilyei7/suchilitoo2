import os
import sys
import django
import inspect

# Configurar entorno Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sushi_core.settings")
django.setup()

from django.urls import get_resolver
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.conf import settings
from mesero import views
from mesero.models import Mesa, Orden, OrdenItem

def separador(titulo):
    print(f"\n{'='*10} {titulo} {'='*10}")

def check_static_files():
    separador("ARCHIVOS ESTÁTICOS")
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    
    mesero_css_path = os.path.join('mesero', 'static', 'mesero', 'css', 'mesero-style.css')
    
    # Verificar en STATICFILES_DIRS
    for static_dir in settings.STATICFILES_DIRS:
        full_path = os.path.join(static_dir, mesero_css_path)
        print(f"Buscando en: {full_path}")
        if os.path.exists(full_path):
            print(f"✅ CSS encontrado en STATICFILES_DIRS")
        else:
            print(f"❌ CSS NO encontrado en {full_path}")
    
    # Verificar en STATIC_ROOT
    if hasattr(settings, 'STATIC_ROOT'):
        full_path = os.path.join(settings.STATIC_ROOT, 'mesero', 'css', 'mesero-style.css')
        print(f"Buscando en: {full_path}")
        if os.path.exists(full_path):
            print(f"✅ CSS encontrado en STATIC_ROOT")
        else:
            print(f"❌ CSS NO encontrado en {full_path}")

    # Verificar en app
    app_static_path = os.path.join(settings.BASE_DIR, 'mesero', 'static', 'mesero', 'css', 'mesero-style.css')
    print(f"Buscando en app: {app_static_path}")
    if os.path.exists(app_static_path):
        print(f"✅ CSS encontrado en app/static")
    else:
        print(f"❌ CSS NO encontrado en app/static")

def check_templates():
    separador("TEMPLATES")
    print(f"TEMPLATE DIRS: {settings.TEMPLATES[0]['DIRS']}")
    print(f"APP_DIRS: {settings.TEMPLATES[0]['APP_DIRS']}")
    
    templates_to_check = [
        'mesero/base.html',
        'mesero/dashboard.html',
        'mesero/login.html',
        'mesero/mesas.html',
    ]
    
    for template_name in templates_to_check:
        try:
            template = get_template(template_name)
            print(f"✅ Template {template_name} encontrado en: {template.origin.name}")
        except TemplateDoesNotExist:
            print(f"❌ Template {template_name} NO encontrado")

def check_views():
    separador("VISTAS")
    view_funcs = [func for name, func in inspect.getmembers(views, inspect.isfunction)]
    
    print(f"Total de vistas definidas: {len(view_funcs)}")
    for view in view_funcs[:5]:  # Mostrar solo las primeras 5 para no saturar
        print(f"Vista: {view.__name__}")
        doc = view.__doc__ or "Sin documentación"
        print(f"  Descripción: {doc.strip()}")

def check_urls():
    separador("URLS")
    resolver = get_resolver()
    all_urls = []
    
    def extract_views_from_resolver(resolver, prefix=''):
        for pattern in resolver.url_patterns:
            if hasattr(pattern, 'url_patterns'):
                # Es un include, procesar recursivamente
                namespace = getattr(pattern, 'namespace', '')
                app_name = getattr(pattern, 'app_name', '')
                ns = namespace or app_name
                if ns:
                    new_prefix = f"{prefix}:{ns}" if prefix else ns
                else:
                    new_prefix = prefix
                extract_views_from_resolver(pattern, new_prefix)
            else:
                # Es una URL regular
                view_name = pattern.callback.__name__ if pattern.callback else "Unknown"
                pattern_name = pattern.name or "sin nombre"
                if prefix:
                    pattern_name = f"{prefix}:{pattern_name}"
                
                if hasattr(pattern, 'pattern'):
                    route = str(pattern.pattern)
                else:
                    route = "Unknown"
                
                all_urls.append((route, view_name, pattern_name))
    
    extract_views_from_resolver(resolver)
    
    print(f"Total de URLs: {len(all_urls)}")
    
    # Filtrar solo las URLs del sistema mesero
    mesero_urls = [url for url in all_urls if 'mesero' in url[2].lower()]
    print(f"\nURLs de mesero: {len(mesero_urls)}")
    
    for route, view_name, pattern_name in mesero_urls:
        print(f"URL: {pattern_name}")
        print(f"  Ruta: {route}")
        print(f"  Vista: {view_name}")

def check_models():
    separador("MODELOS")
    print(f"Mesa: {Mesa.objects.count()} registros")
    print(f"Orden: {Orden.objects.count()} registros")
    print(f"OrdenItem: {OrdenItem.objects.count()} registros")

def check_server():
    separador("SERVIDOR")
    print(f"Debug: {settings.DEBUG}")
    print(f"Allowed Hosts: {settings.ALLOWED_HOSTS}")

if __name__ == "__main__":
    print("=== DIAGNÓSTICO DEL SISTEMA MESERO ===\n")
    try:
        check_static_files()
        check_templates()
        check_urls()
        check_views()
        check_models()
        check_server()
    except Exception as e:
        print(f"Error en diagnóstico: {str(e)}")
