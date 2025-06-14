#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corregir llaves extra en los templates Django
"""

import re
import os

def fix_extra_braces():
    file_path = r'c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\inventario.html'
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Correcciones específicas para llaves extra
    corrections = [
        # Corregir {{ variable }}} -> {{ variable }}
        (r'({{\s*[^}]+\s*}})}', r'\1'),
        
        # Corregir casos específicos
        (r'(\{\{\s*insumo\.[^}]+\s*\}\})\}', r'\1'),
        (r'(\{\{\s*[^}]+\s*\}\})\}', r'\1'),
    ]
    
    changes_made = 0
    
    print("🔧 Corrigiendo llaves extra en templates Django...")
    
    # Aplicar correcciones con regex
    for i, (pattern, replacement) in enumerate(corrections, 1):
        matches = re.findall(pattern, content)
        if matches:
            print(f"  📝 Patrón {i}: Encontradas {len(matches)} coincidencias")
            content = re.sub(pattern, replacement, content)
            changes_made += len(matches)
    
    # Corrección línea por línea más específica
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Buscar y corregir patrones específicos como {{ variable }}}
        pattern = r'(\{\{\s*[^}]+\s*\}\})\}'
        if re.search(pattern, line):
            lines[i] = re.sub(pattern, r'\1', line)
            print(f"  ✅ Línea {i+1}: Removida llave extra")
            changes_made += 1
    
    content = '\n'.join(lines)
    
    # Verificar si se hicieron cambios
    if content != original_content:
        # Crear backup
        backup_path = file_path + '.braces_backup.' + str(int(os.path.getmtime(file_path)))
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"📁 Backup creado: {backup_path}")
        
        # Escribir archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n🎉 CORRECCIÓN DE LLAVES COMPLETADA")
        print(f"📊 Total de cambios aplicados: {changes_made}")
        print(f"📁 Archivo corregido: {file_path}")
        
        return True
    else:
        print("ℹ️  No se encontraron llaves extra para corregir")
        return False

if __name__ == "__main__":
    print("🔧 Iniciando corrección de llaves extra...")
    print("=" * 50)
    
    success = fix_extra_braces()
    
    print("=" * 50)
    if success:
        print("✅ Script ejecutado exitosamente")
    else:
        print("ℹ️  Script completado sin cambios")
