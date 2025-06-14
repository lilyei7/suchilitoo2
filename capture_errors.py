#!/usr/bin/env python
"""
Script para capturar errores específicos en las páginas
"""
import os
import sys
import django
from django.test import Client
from django.urls import reverse
import re

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def capture_page_errors():
    client = Client()
    
    # Login
    from accounts.models import Usuario
    admin_user = Usuario.objects.filter(username='admin').first()
    if admin_user:
        login_success = client.login(username='admin', password='admin123')
        print(f"🔐 Login exitoso: {login_success}")
    
    # Probar páginas específicas con problemas
    problematic_pages = [
        ('dashboard:inventario', 'Inventario'),
        ('dashboard:insumos_elaborados', 'Insumos Elaborados'),
    ]
    
    for url_name, description in problematic_pages:
        try:
            print(f"\n{'='*50}")
            print(f"🔍 Analizando {description}")
            print(f"{'='*50}")
            
            url = reverse(url_name)
            response = client.get(url)
            content = response.content.decode('utf-8')
            
            # Buscar errores específicos de Django
            error_patterns = [
                (r'TemplateDoesNotExist at [^\n]*\n([^\n]*)', 'Template faltante'),
                (r'NoReverseMatch[^\n]*\n([^\n]*)', 'Reverse match error'),
                (r'(Exception|Error) at [^\n]*\n([^\n]*)', 'Error general'),
                (r'<pre class="exception_value">([^<]*)</pre>', 'Valor de excepción'),
                (r'<h1>([^<]*Error[^<]*)</h1>', 'Título de error'),
            ]
            
            for pattern, error_type in error_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    print(f"❌ {error_type}: {match.group(1).strip()}")
            
            # Buscar includes problemáticos
            include_pattern = r'{% include [\'"]([^\'"]*)[\'"] %}'
            includes = re.findall(include_pattern, content)
            if includes:
                print(f"\n📁 Templates incluidos encontrados:")
                for include in includes:
                    print(f"   - {include}")
            
            # Buscar referencias a gestionar_categorias
            if 'gestionar_categorias' in content:
                print(f"\n✅ Referencia a gestionar_categorias encontrada")
            if 'gestionar_unidades' in content:
                print(f"✅ Referencia a gestionar_unidades encontrada")
                
            # Si hay errores, mostrar más contexto
            if 'exception' in content.lower() or 'error' in content.lower():
                # Extraer el traceback
                traceback_pattern = r'<div id="traceback">(.*?)</div>'
                traceback_match = re.search(traceback_pattern, content, re.DOTALL)
                if traceback_match:
                    print(f"\n📋 Traceback detectado (primeras líneas):")
                    traceback = traceback_match.group(1)
                    # Limpiar HTML y mostrar solo las primeras líneas
                    import html
                    clean_traceback = html.unescape(re.sub(r'<[^>]*>', '', traceback))
                    lines = clean_traceback.split('\n')[:10]
                    for line in lines:
                        if line.strip():
                            print(f"   {line.strip()}")
                            
        except Exception as e:
            print(f"❌ Excepción al analizar {description}: {str(e)}")

if __name__ == "__main__":
    print("🔍 Capturando errores específicos...")
    capture_page_errors()
