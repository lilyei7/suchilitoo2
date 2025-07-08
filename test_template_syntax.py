#!/usr/bin/env python3
"""
Script para validar la sintaxis JavaScript en el template croquis_editor.html
"""

import os
import re
import sys

def validate_croquis_template():
    """Valida la sintaxis del template croquis_editor.html"""
    template_path = 'dashboard/templates/dashboard/croquis_editor.html'
    
    if not os.path.exists(template_path):
        print(f"❌ No se encontró el template: {template_path}")
        return False
    
    print(f"🔍 Validando template: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar que las funciones críticas estén presentes
    critical_functions = [
        'function cargarLayout(',
        'function guardarLayout(',
        'function seleccionarHerramienta(',
        'function limpiarPiso(',
        'function eliminarSeleccionado(',
        'function duplicarSeleccionado(',
        'function zoomIn(',
        'function zoomOut(',
        'function centrarVista(',
        'function ajustarTamaño(',
        'function actualizarPropiedad('
    ]
    
    missing_functions = []
    for func in critical_functions:
        if func not in content:
            missing_functions.append(func)
    
    if missing_functions:
        print("❌ Funciones faltantes:")
        for func in missing_functions:
            print(f"   - {func}")
        return False
    else:
        print("✅ Todas las funciones críticas están presentes")
    
    # Verificar declaraciones globales
    global_declarations = [
        'window.cargarLayout',
        'window.guardarLayout',
        'window.seleccionarHerramienta',
        'window.limpiarPiso',
        'window.eliminarSeleccionado',
        'window.duplicarSeleccionado',
        'window.zoomIn',
        'window.zoomOut',
        'window.centrarVista',
        'window.ajustarTamaño'
    ]
    
    missing_globals = []
    for decl in global_declarations:
        if decl not in content:
            missing_globals.append(decl)
    
    if missing_globals:
        print("❌ Declaraciones globales faltantes:")
        for decl in missing_globals:
            print(f"   - {decl}")
        return False
    else:
        print("✅ Todas las declaraciones globales están presentes")
    
    # Verificar que no haya template syntax en JavaScript
    js_section = content.split('<script>')[1].split('</script>')[0] if '<script>' in content else ""
    if '{{ sucursal.id }}' in js_section:
        print("❌ Hay sintaxis de template Django en JavaScript")
        return False
    else:
        print("✅ No hay sintaxis de template Django en la sección JavaScript")
    
    # Verificar balanceado de llaves básico
    brace_count = js_section.count('{') - js_section.count('}')
    if brace_count != 0:
        print(f"⚠️  Llaves posiblemente desbalanceadas: diferencia de {brace_count}")
    else:
        print("✅ Llaves balanceadas")
    
    # Verificar paréntesis básico
    paren_count = js_section.count('(') - js_section.count(')')
    if paren_count != 0:
        print(f"⚠️  Paréntesis posiblemente desbalanceados: diferencia de {paren_count}")
    else:
        print("✅ Paréntesis balanceados")
    
    print("✅ Validación del template completada")
    return True

if __name__ == '__main__':
    success = validate_croquis_template()
    sys.exit(0 if success else 1)
