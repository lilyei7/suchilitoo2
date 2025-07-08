import os
import django
import requests
from django.contrib.auth import authenticate
from django.test import Client
from django.urls import reverse

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

print("=== SIMULACIÓN DE NAVEGADOR COMPLETA ===")

# Crear cliente de prueba
client = Client()

# 1. Intentar acceder al menú sin login
print("\n1. Acceso sin login:")
response = client.get('/mesero/menu/')
print(f"Status: {response.status_code}")
print(f"Redirect: {response.get('Location', 'No redirect')}")

# 2. Login
print("\n2. Login:")
login_response = client.post('/dashboard/login/', {
    'username': 'mesero_test',
    'password': '123456'
})
print(f"Login status: {login_response.status_code}")
print(f"Login redirect: {login_response.get('Location', 'No redirect')}")

# 3. Acceder al menú después del login
print("\n3. Acceso al menú con login:")
menu_response = client.get('/mesero/menu/')
print(f"Menu status: {menu_response.status_code}")

if menu_response.status_code == 200:
    content = menu_response.content.decode('utf-8')
    
    # Verificar elementos críticos en el HTML
    print("\n=== ANÁLISIS DEL HTML ===")
    print(f"Tamaño del HTML: {len(content)} caracteres")
    
    # Buscar elementos específicos
    elementos_buscar = [
        '<title>',
        'productos_por_categoria',
        'card-producto',
        'producto-nombre',
        'producto-precio',
        'class="categoria-seccion"',
        'btn-agregar-producto',
        'background-logo',
        '<script',
        '<link',
        'static/',
        'csrf_token'
    ]
    
    for elemento in elementos_buscar:
        count = content.count(elemento)
        print(f"'{elemento}': {count} ocurrencias")
        if count > 0 and elemento in ['card-producto', 'producto-nombre']:
            # Mostrar un ejemplo
            start = content.find(elemento)
            if start != -1:
                sample = content[start:start+200]
                print(f"  Ejemplo: {sample[:100]}...")
    
    # Verificar si hay productos en el contexto
    print("\n=== BÚSQUEDA DE CONTENIDO DE PRODUCTOS ===")
    productos_encontrados = []
    
    # Buscar patrones que indiquen productos
    if 'class="producto-nombre"' in content:
        import re
        pattern = r'class="producto-nombre"[^>]*>([^<]+)<'
        productos = re.findall(pattern, content)
        productos_encontrados.extend(productos)
    
    if productos_encontrados:
        print(f"Productos encontrados en HTML: {len(productos_encontrados)}")
        for i, producto in enumerate(productos_encontrados[:5]):
            print(f"  {i+1}. {producto.strip()}")
    else:
        print("No se encontraron productos en el HTML renderizado")
    
    # Buscar errores JavaScript o CSS
    print("\n=== BÚSQUEDA DE POSIBLES ERRORES ===")
    errores_buscar = [
        'error',
        'undefined',
        'null',
        'Error:',
        'console.log',
        'display: none',
        'visibility: hidden',
        'opacity: 0'
    ]
    
    for error in errores_buscar:
        count = content.lower().count(error.lower())
        if count > 0:
            print(f"'{error}': {count} ocurrencias")
    
    # Guardar una muestra del HTML para inspección manual
    with open('menu_debug_completo.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✓ HTML completo guardado en 'menu_debug_completo.html'")
    
    # Verificar si hay estilos que oculten elementos
    print("\n=== ANÁLISIS DE ESTILOS QUE OCULTAN ===")
    if 'display: none' in content.lower():
        print("⚠️  Encontrados estilos 'display: none'")
    if 'visibility: hidden' in content.lower():
        print("⚠️  Encontrados estilos 'visibility: hidden'")
    if 'opacity: 0' in content.lower():
        print("⚠️  Encontrados estilos 'opacity: 0'")

else:
    print(f"Error accediendo al menú: {menu_response.status_code}")

print("\n=== VERIFICACIÓN DE URLS ESTÁTICAS ===")
# Verificar que las URLs estáticas respondan
try:
    static_test = client.get('/static/mesero/css/mesero-style.css')
    print(f"CSS mesero-style.css: {static_test.status_code}")
except Exception as e:
    print(f"Error accediendo a CSS: {e}")

print("\n=== FIN DEL DIAGNÓSTICO ===")
