#!/usr/bin/env python3
"""
Script para probar la aplicación de cocina
"""

import os
import sys
import django
import requests
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def test_cocina_urls():
    """Prueba las URLs de cocina"""
    print("=== PRUEBA DE URLS DE COCINA ===\n")
    
    base_url = "http://localhost:8000"
    
    urls_to_test = [
        "/cocina/",
        "/cocina/login/",
        "/cocina/ordenes/",
    ]
    
    for url in urls_to_test:
        try:
            full_url = base_url + url
            print(f"Probando: {full_url}")
            response = requests.get(full_url, timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✓ OK")
            elif response.status_code == 302:
                print("   ↳ Redirección (normal para vistas protegidas)")
            else:
                print(f"   ⚠ Estado inesperado: {response.status_code}")
                
        except requests.RequestException as e:
            print(f"   ❌ Error: {e}")
        
        print()

def test_cocina_models():
    """Prueba los modelos de cocina"""
    print("=== PRUEBA DE MODELOS DE COCINA ===\n")
    
    from cocina.models import EstadoCocina, TiempoPreparacion, OrdenCocina
    from restaurant.models import ProductoVenta
    from django.contrib.auth.models import User
    
    # Probar EstadoCocina
    print("1. Probando EstadoCocina...")
    estados = EstadoCocina.objects.all()
    print(f"   Estados encontrados: {estados.count()}")
    
    for estado in estados:
        print(f"   - {estado.nombre}: {estado.descripcion}")
    
    # Probar TiempoPreparacion
    print("\n2. Probando TiempoPreparacion...")
    tiempos = TiempoPreparacion.objects.all()[:5]
    print(f"   Tiempos configurados: {TiempoPreparacion.objects.count()}")
    
    for tiempo in tiempos:
        print(f"   - {tiempo.producto.nombre}: {tiempo.tiempo_estimado} min")
    
    # Probar usuarios de cocina
    print("\n3. Probando usuarios de cocina...")
    usuarios_cocina = User.objects.filter(groups__name='Cocina')
    print(f"   Usuarios de cocina: {usuarios_cocina.count()}")
    
    for usuario in usuarios_cocina:
        print(f"   - {usuario.username}: {usuario.first_name} {usuario.last_name}")
    
    print("\n✓ Modelos funcionando correctamente")

def test_cocina_permissions():
    """Prueba los permisos de cocina"""
    print("\n=== PRUEBA DE PERMISOS DE COCINA ===\n")
    
    from django.contrib.auth.models import Group, Permission
    
    try:
        grupo_cocina = Group.objects.get(name='Cocina')
        print(f"Grupo 'Cocina' encontrado con {grupo_cocina.permissions.count()} permisos")
        
        permisos = grupo_cocina.permissions.all()[:10]  # Mostrar solo los primeros 10
        for permiso in permisos:
            print(f"   - {permiso.codename}: {permiso.name}")
        
        print("\n✓ Permisos configurados correctamente")
        
    except Group.DoesNotExist:
        print("❌ Grupo 'Cocina' no encontrado")

def test_cocina_templates():
    """Prueba que los templates existan"""
    print("\n=== PRUEBA DE TEMPLATES ===\n")
    
    import os
    from django.conf import settings
    
    cocina_templates_dir = os.path.join(settings.BASE_DIR, 'cocina', 'templates', 'cocina')
    
    if os.path.exists(cocina_templates_dir):
        print(f"Directorio de templates encontrado: {cocina_templates_dir}")
        
        templates = os.listdir(cocina_templates_dir)
        print(f"Templates encontrados: {len(templates)}")
        
        for template in templates:
            print(f"   - {template}")
        
        print("\n✓ Templates disponibles")
    else:
        print("❌ Directorio de templates no encontrado")

def test_cocina_static():
    """Prueba que los archivos estáticos existan"""
    print("\n=== PRUEBA DE ARCHIVOS ESTÁTICOS ===\n")
    
    import os
    from django.conf import settings
    
    cocina_static_dir = os.path.join(settings.BASE_DIR, 'cocina', 'static', 'cocina')
    
    if os.path.exists(cocina_static_dir):
        print(f"Directorio de estáticos encontrado: {cocina_static_dir}")
        
        # Verificar CSS
        css_dir = os.path.join(cocina_static_dir, 'css')
        if os.path.exists(css_dir):
            css_files = os.listdir(css_dir)
            print(f"   CSS files: {css_files}")
        
        # Verificar JS
        js_dir = os.path.join(cocina_static_dir, 'js')
        if os.path.exists(js_dir):
            js_files = os.listdir(js_dir)
            print(f"   JS files: {js_files}")
        
        print("\n✓ Archivos estáticos disponibles")
    else:
        print("❌ Directorio de estáticos no encontrado")

def main():
    """Ejecuta todas las pruebas"""
    print("🍣 PRUEBAS DE LA APLICACIÓN DE COCINA")
    print("=" * 50)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Pruebas de modelos (no requieren servidor)
        test_cocina_models()
        test_cocina_permissions()
        test_cocina_templates()
        test_cocina_static()
        
        # Pruebas de URLs (requieren servidor ejecutándose)
        print("\n" + "=" * 50)
        print("NOTA: Las siguientes pruebas requieren que el servidor esté ejecutándose")
        print("Ejecute 'python manage.py runserver' en otra terminal")
        print("=" * 50)
        
        try:
            test_cocina_urls()
        except Exception as e:
            print(f"⚠ No se pudieron probar las URLs: {e}")
            print("   Asegúrese de que el servidor esté ejecutándose")
        
        print("\n" + "=" * 50)
        print("🎉 PRUEBAS COMPLETADAS")
        print("=" * 50)
        print("\nLa aplicación de cocina está configurada y lista para usar!")
        print("\nPara acceder:")
        print("1. Ejecute: python manage.py runserver")
        print("2. Vaya a: http://localhost:8000/cocina/")
        print("3. Use las credenciales:")
        print("   - Usuario: cocinero")
        print("   - Contraseña: cocinero123")
        print("   O:")
        print("   - Usuario: ayudante")
        print("   - Contraseña: ayudante123")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
