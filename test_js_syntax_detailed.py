#!/usr/bin/env python3
"""
Script para detectar problemas de sintaxis JavaScript específicos
"""

import os
import re

def find_js_syntax_issues():
    """Encuentra problemas específicos de sintaxis JavaScript"""
    template_path = 'dashboard/templates/dashboard/croquis_editor.html'
    
    if not os.path.exists(template_path):
        print(f"❌ No se encontró el template: {template_path}")
        return False
    
    print(f"🔍 Buscando problemas de sintaxis JavaScript en: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Extraer solo la sección JavaScript
    js_lines = []
    in_script = False
    for i, line in enumerate(lines):
        if '<script>' in line:
            in_script = True
            continue
        if '</script>' in line:
            break
        if in_script:
            js_lines.append((i+1, line.rstrip()))
    
    print(f"📝 Analizando {len(js_lines)} líneas de JavaScript...")
    
    issues_found = []
    
    # Verificar funciones sin cuerpo o llaves problemáticas
    for line_num, line in js_lines:
        # Buscar funciones mal definidas
        if 'function ' in line and '{' not in line:
            # Verificar si la siguiente línea tiene llave
            next_line_found = False
            for next_num, next_line in js_lines:
                if next_num == line_num + 1:
                    if '{' not in next_line:
                        issues_found.append(f"Línea {line_num}: Función sin llave de apertura")
                    next_line_found = True
                    break
            if not next_line_found:
                issues_found.append(f"Línea {line_num}: Función al final del archivo sin llave")
        
        # Buscar llaves sueltas
        if line.strip() == '}':
            # Verificar contexto de la llave
            if line_num > 1:
                prev_line = None
                for prev_num, prev_line_content in js_lines:
                    if prev_num == line_num - 1:
                        prev_line = prev_line_content.strip()
                        break
                if prev_line and prev_line.endswith(','):
                    issues_found.append(f"Línea {line_num}: Llave de cierre después de coma")
        
        # Buscar caracteres problemáticos
        if '{{ ' in line and ' }}' in line and 'SUCURSAL_ID' not in line:
            issues_found.append(f"Línea {line_num}: Template syntax en JavaScript: {line.strip()}")
        
        # Buscar llaves desbalanceadas en líneas individuales
        open_braces = line.count('{')
        close_braces = line.count('}')
        if close_braces > open_braces and not line.strip().startswith('}'):
            issues_found.append(f"Línea {line_num}: Más llaves de cierre que de apertura: {line.strip()}")
    
    # Verificar balance general de llaves
    total_open = sum(line[1].count('{') for line in js_lines)
    total_close = sum(line[1].count('}') for line in js_lines)
    if total_open != total_close:
        issues_found.append(f"Balance general: {total_open} llaves abiertas, {total_close} llaves cerradas")
    
    # Verificar balance de paréntesis
    total_open_paren = sum(line[1].count('(') for line in js_lines)
    total_close_paren = sum(line[1].count(')') for line in js_lines)
    if total_open_paren != total_close_paren:
        issues_found.append(f"Balance general: {total_open_paren} paréntesis abiertos, {total_close_paren} paréntesis cerrados")
    
    if issues_found:
        print("❌ Problemas encontrados:")
        for issue in issues_found:
            print(f"   - {issue}")
        return False
    else:
        print("✅ No se encontraron problemas de sintaxis JavaScript")
        return True

if __name__ == '__main__':
    find_js_syntax_issues()
