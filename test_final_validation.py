#!/usr/bin/env python3
"""
Script de validación final para el editor de croquis
"""

import os
import re

def final_validation():
    """Validación final completa del editor de croquis"""
    template_path = 'dashboard/templates/dashboard/croquis_editor.html'
    
    if not os.path.exists(template_path):
        print(f"❌ No se encontró el template: {template_path}")
        return False
    
    print("🔍 VALIDACIÓN FINAL DEL EDITOR DE CROQUIS")
    print("=" * 50)
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Funciones críticas presentes
    print("\n1. ✅ VERIFICANDO FUNCIONES CRÍTICAS...")
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
        'function ajustarTamaño('
    ]
    
    for func in critical_functions:
        if func in content:
            print(f"   ✅ {func}")
        else:
            print(f"   ❌ {func}")
            return False
    
    # Test 2: Declaraciones globales
    print("\n2. ✅ VERIFICANDO DECLARACIONES GLOBALES...")
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
    
    for decl in global_declarations:
        if decl in content:
            print(f"   ✅ {decl}")
        else:
            print(f"   ❌ {decl}")
            return False
    
    # Test 3: Template syntax en JavaScript
    print("\n3. ✅ VERIFICANDO SINTAXIS DE TEMPLATE...")
    js_section = content.split('<script>')[1].split('</script>')[0] if '<script>' in content else ""
    
    # Verificar que solo exista {{ sucursal.id }} en la línea de SUCURSAL_ID
    sucursal_id_lines = [line for line in js_section.split('\n') if '{{ sucursal.id }}' in line]
    problematic_lines = [line for line in sucursal_id_lines if 'SUCURSAL_ID' not in line]
    
    if problematic_lines:
        print(f"   ❌ Sintaxis problemática encontrada en líneas: {problematic_lines}")
        return False
    else:
        print("   ✅ No hay sintaxis de template problemática en JavaScript")
    
    # Test 4: Balance de llaves y paréntesis
    print("\n4. ✅ VERIFICANDO BALANCE DE CARACTERES...")
    open_braces = js_section.count('{')
    close_braces = js_section.count('}')
    open_parens = js_section.count('(')
    close_parens = js_section.count(')')
    
    if open_braces == close_braces:
        print(f"   ✅ Llaves balanceadas: {open_braces} / {close_braces}")
    else:
        print(f"   ❌ Llaves desbalanceadas: {open_braces} / {close_braces}")
        return False
    
    if open_parens == close_parens:
        print(f"   ✅ Paréntesis balanceados: {open_parens} / {close_parens}")
    else:
        print(f"   ❌ Paréntesis desbalanceados: {open_parens} / {close_parens}")
        return False
    
    # Test 5: Onclick handlers
    print("\n5. ✅ VERIFICANDO ONCLICK HANDLERS...")
    onclick_pattern = r'onclick="([^"]+)"'
    onclick_matches = re.findall(onclick_pattern, content)
    print(f"   📋 Se encontraron {len(onclick_matches)} onclick handlers")
    
    for onclick in onclick_matches:
        func_name = onclick.split('(')[0]
        if f'window.{func_name}' in content or func_name == 'actualizarPropiedadEspecifica':
            print(f"   ✅ {onclick}")
        else:
            print(f"   ❌ {onclick} - No tiene declaración global")
            return False
    
    # Test 6: Sucursal ID variable
    print("\n6. ✅ VERIFICANDO VARIABLE SUCURSAL_ID...")
    if 'const SUCURSAL_ID = {{ sucursal.id }};' in content:
        print("   ✅ Variable SUCURSAL_ID correctamente definida")
    else:
        print("   ❌ Variable SUCURSAL_ID no encontrada")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 TODAS LAS VALIDACIONES PASARON EXITOSAMENTE")
    print("✅ El editor de croquis está listo para usar")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    final_validation()
