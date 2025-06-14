#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corregir los templates de Django malformateados en inventario.html
"""

import re
import os

def fix_django_templates():
    file_path = r'c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\inventario.html'
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Patrones para corregir templates Django malformateados
    corrections = [
        # Corregir { { variable } } -> {{ variable }}
        (r'{\s*{\s*([^}]+)\s*}\s*}', r'{{ \1 }}'),
        
        # Corregir casos específicos encontrados
        (r'{\s+{\s*insumos\.count\s*}\s*}', r'{{ insumos.count }}'),
        (r'{\s+{\s*insumos\|length\s*}\s*}', r'{{ insumos|length }}'),
        (r'{\s+{\s*insumo\.[^}]+\s*}\s*}', lambda m: '{{ ' + m.group().strip('{ }').strip() + ' }}'),
        
        # Casos con saltos de línea
        (r'{\s*\n\s*{\s*([^}]+)\s*}\s*\n\s*}', r'{{ \1 }}'),
        (r'{\s*\n\s*{\s*([^}]+)\s*}', r'{{ \1 }}'),
        
        # Múltiples espacios entre llaves
        (r'{\s+{', r'{{'),
        (r'}\s+}', r'}}'),
    ]
    
    changes_made = 0
    
    print("🔧 Buscando y corrigiendo templates Django malformateados...")
    
    for i, (pattern, replacement) in enumerate(corrections, 1):
        if callable(replacement):
            matches = re.findall(pattern, content)
            if matches:
                print(f"  📝 Patrón {i}: Encontradas {len(matches)} coincidencias")
                new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
            else:
                new_content = content
        else:
            matches = re.findall(pattern, content)
            if matches:
                print(f"  📝 Patrón {i}: Encontradas {len(matches)} coincidencias - {matches[:3]}...")
                new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
            else:
                new_content = content
        
        if new_content != content:
            changes_made += 1
            content = new_content
    
    # Correcciones específicas línea por línea para casos complejos
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Corregir líneas específicas con patrones complejos
        if '{ insumos.count }' in line:
            lines[i] = line.replace('{ insumos.count }', '{{ insumos.count }}')
            changes_made += 1
            print(f"  ✅ Línea {i+1}: Corregido '{ insumos.count }' -> '{{ insumos.count }}'")
        
        if '{ { csrf_token }' in line:
            lines[i] = line.replace('{ { csrf_token }', '{{ csrf_token }}')
            changes_made += 1
            print(f"  ✅ Línea {i+1}: Corregido CSRF token")
        
        # Buscar patrones como { { variable.something }
        pattern_match = re.search(r'{\s*{\s*([^}]+)\s*}', line)
        if pattern_match:
            variable = pattern_match.group(1).strip()
            lines[i] = re.sub(r'{\s*{\s*' + re.escape(variable) + r'\s*}', f'{{{{ {variable} }}}}', line)
            changes_made += 1
            print(f"  ✅ Línea {i+1}: Corregido template variable: {variable}")
    
    content = '\n'.join(lines)
    
    # Verificar si se hicieron cambios
    if content != original_content:
        # Crear backup
        backup_path = file_path + '.template_backup.' + str(int(os.path.getmtime(file_path)))
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"📁 Backup creado: {backup_path}")
        
        # Escribir archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n🎉 CORRECCIÓN DE TEMPLATES COMPLETADA")
        print(f"📊 Total de cambios aplicados: {changes_made}")
        print(f"📁 Archivo corregido: {file_path}")
        
        return True
    else:
        print("ℹ️  No se encontraron templates malformateados para corregir")
        return False

def verify_templates():
    """Verificar que los templates estén correctamente formateados"""
    file_path = r'c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\inventario.html'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar patrones problemáticos
    problematic_patterns = [
        r'{\s+{',  # Espacios después de {
        r'}\s+}',  # Espacios antes de }
        r'{\s*\n\s*{',  # Saltos de línea entre llaves
    ]
    
    issues_found = 0
    for pattern in problematic_patterns:
        matches = re.findall(pattern, content)
        if matches:
            issues_found += len(matches)
            print(f"❌ Encontrados {len(matches)} templates malformateados: {pattern}")
    
    if issues_found == 0:
        print("✅ Todos los templates Django están correctamente formateados")
        return True
    else:
        print(f"❌ Se encontraron {issues_found} problemas de formato en templates")
        return False

if __name__ == "__main__":
    print("🔧 Iniciando corrección de templates Django...")
    print("=" * 60)
    
    success = fix_django_templates()
    
    print("\n" + "=" * 60)
    print("🔍 Verificando resultado...")
    verify_templates()
    
    print("=" * 60)
    if success:
        print("✅ Script ejecutado exitosamente")
        print("💡 Recarga la página del navegador para ver los datos reales")
    else:
        print("ℹ️  Script completado sin cambios")
