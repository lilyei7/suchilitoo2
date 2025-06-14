#!/usr/bin/env python3
"""
Script para limpiar todos los console.log statements del archivo de inventario
"""

import re

def clean_console_logs():
    """Eliminar todos los console.log del archivo de inventario"""
    print("🧹 === LIMPIANDO CONSOLE.LOG STATEMENTS ===")
    
    # Leer el archivo actual
    file_path = r'c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\inventario.html'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Contar console.log antes
    console_logs_before = len(re.findall(r'console\.(log|error|warn|info)', content))
    print(f"📊 Console statements encontrados: {console_logs_before}")
    
    if console_logs_before == 0:
        print("✅ El archivo ya está limpio de console statements")
        return
    
    # Patrones para eliminar console statements
    patterns_to_remove = [
        r'\s*console\.log\([^)]*\);\s*\n',
        r'\s*console\.error\([^)]*\);\s*\n', 
        r'\s*console\.warn\([^)]*\);\s*\n',
        r'\s*console\.info\([^)]*\);\s*\n',
        # Para console.log multilinea con strings template
        r'\s*console\.log\([^;]*`[^`]*`[^;]*\);\s*\n',
        # Para console.log con concatenación compleja
        r'\s*console\.log\([^;]*\+[^;]*\);\s*\n',
    ]
    
    # Aplicar limpieza
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
    
    # Patrones más complejos (console.log con múltiples líneas)
    content = re.sub(r'\s*console\.log\(\s*\'[^\']*===.*?===.*?\'\s*\);\s*\n', '', content, flags=re.MULTILINE | re.DOTALL)
    content = re.sub(r'\s*console\.log\(\s*\"[^\"]*===.*?===.*?\"\s*\);\s*\n', '', content, flags=re.MULTILINE | re.DOTALL)
    
    # Remover líneas específicas problemáticas que pueden quedar
    lines_to_remove = [
        'console.log(\'🚀 === INICIANDO CREACIÓN DE INSUMO ===\');',
        'console.log(\'📋 === DATOS RECIBIDOS DEL SERVIDOR ===\');',
        'console.log(\'🚀 === PÁGINA CARGADA - INICIALIZANDO SISTEMA ===\');',
        'console.log(\'📅 Timestamp:\', new Date().toISOString());',
        'console.log(\'🔍 === VERIFICANDO ELEMENTOS DEL DOM ===\');',
        'console.log(\'🚪 === MODAL ABRIÉNDOSE ===\');',
        'console.log(\'🚪 === MODAL CERRÁNDOSE ===\');',
        'console.log(\'📋 === CARGANDO DATOS DEL FORMULARIO ===\');',
        'console.log(\'💥 === ERROR AL CARGAR DATOS DEL FORMULARIO ===\');',
        'console.log(\'💥 === ERROR EN LA PETICIÓN ===\');',
        'console.log(\'🚀 === ENVIANDO PETICIÓN FETCH ===\');',
        'console.log(\'📨 === EVENT SUBMIT DISPARADO ===\');',
        'console.log(\'🔧 === CONFIGURANDO EVENT LISTENERS ===\');'
    ]
    
    for line in lines_to_remove:
        content = content.replace(line + '\n', '')
        content = content.replace('    ' + line + '\n', '')
        content = content.replace('        ' + line + '\n', '')
        content = content.replace('            ' + line + '\n', '')
    
    # Eliminar comentarios de debug también
    content = re.sub(r'\s*\/\/ console\.log.*\n', '', content)
    
    # Contar después de la limpieza
    console_logs_after = len(re.findall(r'console\.(log|error|warn|info)', content))
    
    # Escribir el archivo limpio
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Limpieza completada:")
    print(f"   - Console statements antes: {console_logs_before}")
    print(f"   - Console statements después: {console_logs_after}")
    print(f"   - Eliminados: {console_logs_before - console_logs_after}")
    
    if console_logs_after == 0:
        print("🎉 ¡Archivo completamente limpio!")
    else:
        print(f"⚠️ Quedan {console_logs_after} console statements que requieren revisión manual")

if __name__ == "__main__":
    clean_console_logs()
