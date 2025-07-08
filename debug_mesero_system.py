import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.management import call_command
from django.conf import settings

def setup_test_data():
    print("\n=== Configurando datos de prueba ===")
    User = get_user_model()
    
    # Crear usuario de prueba
    username = "test_mesero"
    email = "test@mesero.com"
    password = "test12345"
    
    try:
        user = User.objects.get(username=username)
        print(f"Usuario de prueba ya existe: {username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        print(f"Usuario de prueba creado: {username}")
    
    return user, password

def test_static_files():
    print("\n=== Verificando archivos estáticos ===")
    
    static_files = [
        'mesero/css/base.css',
        'mesero/css/mesero-style.css',
    ]
    
    print("\nBuscando en:")
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
    
    for file_path in static_files:
        full_path = os.path.join(settings.STATIC_ROOT, file_path)
        if os.path.exists(full_path):
            print(f"✓ {file_path} existe")
            # Mostrar primeras líneas del archivo
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()[:200]
                print(f"   Primeras líneas:\n   {content.replace(chr(10), chr(10)+'   ')}\n")
        else:
            print(f"✗ {file_path} NO existe")

def test_urls():
    print("\n=== Probando URLs ===")
    client = Client()
    
    urls_to_test = [
        ('mesero:dashboard', []),
        ('mesero:menu', []),
        ('mesero:mesas', []),
        ('mesero:login', []),
    ]
    
    for url_name, args in urls_to_test:
        url = reverse(url_name, args=args)
        print(f"\nProbando {url_name} ({url})")
        
        response = client.get(url)
        print(f"Código de respuesta: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'No Content-Type')}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            print(f"Longitud del contenido: {len(content)} caracteres")
            if len(content) < 200:
                print("ADVERTENCIA: Contenido muy corto")
            if 'mesero-container' not in content:
                print("ADVERTENCIA: No se encontró la clase 'mesero-container'")
            if '{% extends' in content:
                print("ADVERTENCIA: Template no está siendo renderizado correctamente")

def test_template_inheritance():
    print("\n=== Verificando herencia de templates ===")
    template_files = [
        'mesero/templates/mesero/base.html',
        'mesero/templates/mesero/menu.html',
        'mesero/templates/mesero/dashboard.html',
    ]
    
    base_dir = settings.BASE_DIR
    for template_file in template_files:
        full_path = os.path.join(base_dir, template_file)
        if os.path.exists(full_path):
            print(f"✓ {template_file} existe")
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'extends' in content:
                    print(f"  Template extiende: {content.split('extends')[1].split('%}')[0].strip()}")
        else:
            print(f"✗ {template_file} NO existe")

def main():
    print("=== Iniciando diagnóstico del sistema mesero ===")
    
    # 1. Configurar datos de prueba
    user, password = setup_test_data()
    
    # 2. Verificar archivos estáticos
    test_static_files()
    
    # 3. Probar URLs
    test_urls()
    
    # 4. Verificar herencia de templates
    test_template_inheritance()

if __name__ == '__main__':
    main()
