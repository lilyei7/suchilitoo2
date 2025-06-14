#!/usr/bin/env python
"""
Script para analizar el contenido específico de la página de insumos elaborados
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client

def analyze_insumos_elaborados():
    print("🔍 ANALIZANDO PÁGINA DE INSUMOS ELABORADOS")
    print("=" * 60)
    
    client = Client()
    client.login(username='admin', password='admin123')
    
    response = client.get('/dashboard/insumos-elaborados/')
    content = response.content.decode('utf-8')
    
    print(f"📄 Tamaño del contenido: {len(content)} caracteres")
    print(f"📊 Status code: {response.status_code}")
    
    # Buscar palabras clave específicas
    keywords = [
        'gestionar_categorias',
        'gestionar_unidades', 
        'nuevaCategoriaModal',
        'nuevaUnidadModal',
        'include',
        'dashboard/modals/',
    ]
    
    print("\n🔍 BÚSQUEDA DE PALABRAS CLAVE:")
    for keyword in keywords:
        count = content.count(keyword)
        print(f"   {keyword}: {count} ocurrencias")
        if count > 0:
            # Mostrar contexto
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if keyword in line:
                    print(f"      Línea {i+1}: {line.strip()}")
                    break
    
    # Buscar includes específicamente
    print("\n📋 ANÁLISIS DE INCLUDES:")
    import re
    include_pattern = r'{%\s*include\s+[\'"]([^\'"]*)[\'"].*?%}'
    includes = re.findall(include_pattern, content)
    
    if includes:
        for include in includes:
            print(f"   ✅ Include encontrado: {include}")
    else:
        print("   ❌ No se encontraron includes")
    
    # Buscar los modales específicos en el HTML renderizado
    modal_patterns = [
        (r'id=[\'"]nuevaCategoriaModal[\'"]', 'Modal Categorías'),
        (r'id=[\'"]nuevaUnidadModal[\'"]', 'Modal Unidades'),
    ]
    
    print("\n🏗️  ANÁLISIS DE MODALES EN HTML RENDERIZADO:")
    for pattern, name in modal_patterns:
        matches = re.findall(pattern, content)
        print(f"   {name}: {len(matches)} ocurrencias")
    
    # Verificar si hay errores de template en el contenido
    error_indicators = [
        'TemplateDoesNotExist',
        'TemplateSyntaxError',
        'Could not parse',
        'Invalid template',
    ]
    
    print("\n⚠️  VERIFICACIÓN DE ERRORES:")
    has_errors = False
    for error in error_indicators:
        if error in content:
            print(f"   ❌ Error detectado: {error}")
            has_errors = True
    
    if not has_errors:
        print("   ✅ No se detectaron errores obvios")
    
    # Guardar el contenido para análisis manual
    with open('debug_insumos_elaborados.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n💾 Contenido guardado en: debug_insumos_elaborados.html")

if __name__ == "__main__":
    analyze_insumos_elaborados()
