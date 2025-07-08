#!/usr/bin/env python3
"""
Test script to check JavaScript syntax and console errors in croquis editor
"""

import os
import re

def check_croquis_syntax():
    print("🔍 Verificando sintaxis JavaScript del editor de croquis...")
    
    croquis_file = "dashboard/templates/dashboard/croquis_editor.html"
    
    if not os.path.exists(croquis_file):
        print(f"❌ Archivo no encontrado: {croquis_file}")
        return
    
    with open(croquis_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer solo la sección JavaScript
    js_start = content.find('<script>')
    js_end = content.find('</script>', js_start)
    
    if js_start == -1 or js_end == -1:
        print("❌ No se encontró sección JavaScript")
        return
    
    js_content = content[js_start + 8:js_end]
    
    print("📋 Verificando sintaxis JavaScript...")
    
    # Problemas comunes de sintaxis
    issues = []
    
    # 1. Verificar llaves balanceadas
    brace_count = js_content.count('{') - js_content.count('}')
    if brace_count != 0:
        issues.append(f"Llaves desbalanceadas: {brace_count}")
    
    # 2. Verificar paréntesis balanceados
    paren_count = js_content.count('(') - js_content.count(')')
    if paren_count != 0:
        issues.append(f"Paréntesis desbalanceados: {paren_count}")
    
    # 3. Verificar puntos y comas faltantes en líneas importantes
    lines = js_content.split('\n')
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if line and not line.startswith('//') and not line.startswith('/*'):
            # Líneas que deberían terminar en punto y coma
            if (line.endswith('return') or 
                (line.startswith('let ') or line.startswith('const ') or line.startswith('var ')) and 
                '=' in line and not line.endswith(';') and not line.endswith('{') and not line.endswith(',')):
                issues.append(f"Línea {i}: Posible punto y coma faltante - {line[:50]}...")
    
    # 4. Verificar llamadas de función malformadas
    function_calls = re.findall(r'(\w+)\s*\(\s*\)', js_content)
    for call in function_calls:
        if call in ['if', 'for', 'while', 'switch', 'catch']:
            continue
        # Verificar si la función está definida
        if f'function {call}' not in js_content:
            # Podría ser una función integrada o de jQuery/DOM
            if call not in ['console', 'alert', 'confirm', 'parseInt', 'parseFloat', 'Math', 'Date', 'Object', 'Array', 'String', 'document', 'window', 'setTimeout', 'clearTimeout']:
                issues.append(f"Posible función no definida: {call}()")
    
    # 5. Verificar variables no declaradas (básico)
    # Buscar asignaciones sin declaración
    assignments = re.findall(r'^(\w+)\s*=', js_content, re.MULTILINE)
    declared_vars = re.findall(r'(?:let|const|var)\s+(\w+)', js_content)
    
    for var in assignments:
        if var not in declared_vars and var not in ['canvas', 'ctx', 'herramientaActual', 'objetoSeleccionado', 'objetos', 'mesasDisponibles', 'isDragging', 'dragOffset', 'zoom', 'panOffset', 'pisoActual', 'objetosPorPiso', 'elementoDragActual', 'dragStartPos']:
            # Estas son variables globales conocidas
            if var not in ['window', 'document', 'console']:
                issues.append(f"Posible variable no declarada: {var}")
    
    print(f"\n📊 Resultados del análisis:")
    if issues:
        print(f"⚠️  Problemas encontrados: {len(issues)}")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ No se encontraron problemas evidentes de sintaxis")
    
    # Verificar funciones clave para ReferenceError
    print(f"\n🔧 Verificando funciones críticas:")
    critical_functions = ['onMouseDown', 'seleccionarHerramienta', 'actualizarPanelPropiedades', 'guardarLayout', 'cargarLayout', 'eliminarSeleccionado']
    
    for func in critical_functions:
        # Verificar que la función esté completamente definida (con cierre de llaves)
        pattern = rf'function\s+{func}\s*\([^)]*\)\s*\{{.*?\}}'
        match = re.search(pattern, js_content, re.DOTALL)
        if match:
            print(f"✅ {func} - Definición completa encontrada")
        else:
            # Verificar definición parcial
            partial_pattern = rf'function\s+{func}\s*\('
            if re.search(partial_pattern, js_content):
                print(f"⚠️  {func} - Definición encontrada pero posiblemente incompleta")
            else:
                print(f"❌ {func} - No encontrada")
    
    return len(issues) == 0

if __name__ == "__main__":
    check_croquis_syntax()
