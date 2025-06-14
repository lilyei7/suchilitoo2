#!/usr/bin/env python
"""
Script para verificar exactamente qué template se está cargando
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.template.loader import get_template

def debug_template_rendering():
    print("🔍 DEBUGGING TEMPLATE RENDERING")
    print("=" * 50)
    
    # Primero verificar qué template está realmente cargando Django
    template = get_template('dashboard/insumos_elaborados.html')
    print(f"📁 Template encontrado en: {template.origin.name}")
    
    # Leer el contenido del archivo directamente
    with open(template.origin.name, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    print(f"📄 Tamaño del template: {len(template_content)} caracteres")
    
    # Buscar los includes en el archivo del template
    import re
    include_pattern = r'{%\s*include\s+[\'"]([^\'"]*)[\'"].*?%}'
    includes = re.findall(include_pattern, template_content)
    
    print(f"\n📋 INCLUDES ENCONTRADOS EN EL TEMPLATE:")
    if includes:
        for include in includes:
            print(f"   ✅ {include}")
    else:
        print("   ❌ No se encontraron includes")
    
    # Buscar líneas específicas alrededor de los includes
    lines = template_content.split('\n')
    for i, line in enumerate(lines):
        if 'gestionar_categorias' in line or 'gestionar_unidades' in line:
            print(f"\n📍 Línea {i+1}: {line.strip()}")
            # Mostrar contexto
            start = max(0, i-2)
            end = min(len(lines), i+3)
            for j in range(start, end):
                marker = ">>> " if j == i else "    "
                print(f"{marker}{j+1}: {lines[j]}")
    
    # Ahora probar la renderización completa
    print(f"\n🔧 PROBANDO RENDERIZACIÓN COMPLETA:")
    
    client = Client()
    client.login(username='admin', password='admin123')
    
    response = client.get('/dashboard/insumos-elaborados/')
    rendered_content = response.content.decode('utf-8')
    
    # Verificar si los includes se procesaron
    includes_in_rendered = [
        ('nuevaCategoriaModal', 'Modal Categorías'),
        ('nuevaUnidadModal', 'Modal Unidades'),
        ('gestionar_categorias', 'Include Categorías'),
        ('gestionar_unidades', 'Include Unidades'),
    ]
    
    for search_term, description in includes_in_rendered:
        count = rendered_content.count(search_term)
        print(f"   {description}: {count} ocurrencias")
    
    # Verificar si hay algo que esté interrumpiendo el procesamiento del template
    error_patterns = [
        (r'{% include.*gestionar_categorias.*%}', 'Include directo categorías'),
        (r'{% include.*gestionar_unidades.*%}', 'Include directo unidades'),
    ]
    
    print(f"\n🔍 VERIFICANDO INCLUDES NO PROCESADOS:")
    for pattern, description in error_patterns:
        matches = re.findall(pattern, rendered_content)
        if matches:
            print(f"   ❌ {description}: {len(matches)} includes sin procesar")
            for match in matches:
                print(f"      {match}")
        else:
            print(f"   ✅ {description}: Include procesado correctamente")

if __name__ == "__main__":
    debug_template_rendering()
