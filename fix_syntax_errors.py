#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corregir errores de sintaxis JavaScript específicos en inventario.html
"""

import re
import os

def fix_javascript_syntax_errors():
    file_path = r'c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\inventario.html'
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Lista de correcciones específicas
    corrections = [
        # Corregir funciones con doble cierre
        (r'(\s+})(\s+})', r'\1'),
        
        # Corregir .then data => { que debe ser .then(data => {
        (r'\.then\s+data\s+=>\s+{', r'.then(data => {'),
        
        # Corregir catch que no está cerrado correctamente
        (r'}\)\s*\.catch\(error\s+=>\s+{\s*(?!\s*mostrarNotificacionElegante)', 
         r'}).catch(error => {\n        '),
         
        # Corregir console.log mal cerrado
        (r'console\.log\([^)]+\);\s+}', r'},'),
        
        # Corregir espacios extra en promise chains
        (r'}\)\s+\.then', r'}).then'),
        (r'}\)\s+\.catch', r'}).catch'),
        
        # Corregir funciones que terminan con doble }
        (r'function\s+\w+\([^)]*\)\s*{\s*[^}]*}\s*}', 
         lambda m: m.group().replace('}}', '}')),
    ]
    
    changes_made = 0
    
    for pattern, replacement in corrections:
        if callable(replacement):
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        else:
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        
        if new_content != content:
            changes_made += 1
            content = new_content
            print(f"✅ Aplicada corrección {changes_made}: {pattern[:50]}...")
    
    # Correcciones específicas por línea (más precisas)
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Corregir líneas específicas problemáticas
        if '.then data => {' in line:
            lines[i] = line.replace('.then data => {', '.then(data => {')
            changes_made += 1
            print(f"✅ Corregida línea {i+1}: .then data => {{ -> .then(data => {{")
        
        # Corregir funciones que terminan con doble }
        if line.strip() == '}' and i > 0 and lines[i-1].strip() == '}':
            # Verificar si el contexto es una función
            context_start = max(0, i-10)
            context = '\n'.join(lines[context_start:i+1])
            if 'function' in context:
                lines[i] = ''  # Remover la línea extra
                changes_made += 1
                print(f"✅ Removida línea extra {i+1}: }}")
    
    content = '\n'.join(lines)
    
    # Verificar si se hicieron cambios
    if content != original_content:
        # Crear backup
        backup_path = file_path + '.backup.' + str(int(os.path.getmtime(file_path)))
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"📁 Backup creado: {backup_path}")
        
        # Escribir archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n🎉 CORRECCIÓN COMPLETADA")
        print(f"📊 Total de cambios aplicados: {changes_made}")
        print(f"📁 Archivo corregido: {file_path}")
        
        return True
    else:
        print("ℹ️  No se encontraron errores de sintaxis para corregir")
        return False

if __name__ == "__main__":
    print("🔧 Iniciando corrección de errores de sintaxis JavaScript...")
    print("=" * 60)
    
    success = fix_javascript_syntax_errors()
    
    print("=" * 60)
    if success:
        print("✅ Script ejecutado exitosamente")
    else:
        print("ℹ️  Script completado sin cambios")
