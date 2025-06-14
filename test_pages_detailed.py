#!/usr/bin/env python
"""
Script detallado para probar todas las páginas del sistema y detectar problemas
"""
import os
import sys
import django
from django.test import Client
from django.urls import reverse

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def test_all_pages():
    client = Client()
    
    # Primero hacer login
    from accounts.models import Usuario
    
    # Crear usuario de prueba si no existe
    try:
        admin_user = Usuario.objects.get(username='admin')
    except Usuario.DoesNotExist:
        admin_user = Usuario.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123',
            nombre='Admin',
            apellido='Test'
        )
        print("✅ Usuario admin creado")
    
    # Login
    login_success = client.login(username='admin', password='admin123')
    print(f"🔐 Login exitoso: {login_success}")
    
    if not login_success:
        print("❌ No se pudo hacer login. Deteniendo pruebas.")
        return
    
    # URLs a probar
    test_urls = [
        ('dashboard:principal', 'Principal'),
        ('dashboard:inventario', 'Inventario'),
        ('dashboard:insumos_elaborados', 'Insumos Elaborados'),
        ('dashboard:insumos_compuestos', 'Insumos Compuestos'),
        ('dashboard:proveedores', 'Proveedores'),
        ('dashboard:entradas_salidas', 'Entradas/Salidas'),
    ]
    
    for url_name, description in test_urls:
        try:
            print(f"\n🔍 Probando {description}...")
            url = reverse(url_name)
            print(f"   URL: {url}")
            
            response = client.get(url)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                # Buscar indicadores de errores
                if 'TemplateDoesNotExist' in content:
                    print("   ❌ Error: TemplateDoesNotExist detectado")
                    # Extraer el nombre del template que falta
                    import re
                    template_match = re.search(r"TemplateDoesNotExist at [^\n]*\n([^\n]*)", content)
                    if template_match:
                        print(f"   📁 Template faltante: {template_match.group(1)}")
                elif 'NoReverseMatch' in content:
                    print("   ❌ Error: NoReverseMatch detectado")
                elif 'Exception' in content or 'Error' in content:
                    print("   ⚠️  Posible error detectado en el contenido")
                else:
                    print("   ✅ Página carga correctamente")
                    
                # Verificar si contiene los elementos esperados
                if 'gestionar_categorias' in content.lower():
                    print("   ✅ Modal de categorías detectado")
                if 'gestionar_unidades' in content.lower():
                    print("   ✅ Modal de unidades detectado")
                    
            elif response.status_code == 404:
                print("   ❌ Error 404: URL no encontrada")
            elif response.status_code == 500:
                print("   ❌ Error 500: Error interno del servidor")
            else:
                print(f"   ⚠️  Código de respuesta inesperado: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Excepción: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas detalladas del sistema...")
    test_all_pages()
    print("\n✅ Pruebas completadas")
