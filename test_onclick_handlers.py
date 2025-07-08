#!/usr/bin/env python3
"""
Script para probar específicamente los onclick handlers del croquis editor
"""

import os
import re

def test_onclick_handlers():
    """Prueba que todos los onclick handlers tengan sus funciones correspondientes"""
    template_path = 'dashboard/templates/dashboard/croquis_editor.html'
    
    if not os.path.exists(template_path):
        print(f"❌ No se encontró el template: {template_path}")
        return False
    
    print(f"🔍 Probando onclick handlers en: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer todos los onclick handlers
    onclick_pattern = r'onclick="([^"]+)"'
    onclick_matches = re.findall(onclick_pattern, content)
    
    print(f"📋 Se encontraron {len(onclick_matches)} onclick handlers:")
    
    # Mapear función a declaración esperada
    function_mapping = {
        'cargarLayout()': 'window.cargarLayout',
        'guardarLayout()': 'window.guardarLayout',
        "seleccionarHerramienta('seleccionar')": 'window.seleccionarHerramienta',
        "seleccionarHerramienta('mesa')": 'window.seleccionarHerramienta',
        "seleccionarHerramienta('silla')": 'window.seleccionarHerramienta',
        "seleccionarHerramienta('pared')": 'window.seleccionarHerramienta',
        "seleccionarHerramienta('puerta')": 'window.seleccionarHerramienta',
        "seleccionarHerramienta('barra')": 'window.seleccionarHerramienta',
        'limpiarPiso()': 'window.limpiarPiso',
        'zoomOut()': 'window.zoomOut',
        'zoomIn()': 'window.zoomIn',
        'ajustarTamaño()': 'window.ajustarTamaño',
        'centrarVista()': 'window.centrarVista',
        'eliminarSeleccionado()': 'window.eliminarSeleccionado',
        'duplicarSeleccionado()': 'window.duplicarSeleccionado'
    }
    
    missing_declarations = []
    for onclick in onclick_matches:
        print(f"   - {onclick}")
        
        # Extraer nombre de función base
        func_name = onclick.split('(')[0]
        expected_declaration = f'window.{func_name}'
        
        # Verificar si la declaración global existe
        if expected_declaration not in content:
            missing_declarations.append(expected_declaration)
    
    if missing_declarations:
        print("❌ Declaraciones globales faltantes:")
        for decl in set(missing_declarations):
            print(f"   - {decl}")
        return False
    else:
        print("✅ Todas las declaraciones globales para onclick handlers están presentes")
    
    # Verificar que las funciones base estén definidas
    base_functions = {
        'cargarLayout': 'function cargarLayout(',
        'guardarLayout': 'function guardarLayout(',
        'seleccionarHerramienta': 'function seleccionarHerramienta(',
        'limpiarPiso': 'function limpiarPiso(',
        'zoomOut': 'function zoomOut(',
        'zoomIn': 'function zoomIn(',
        'ajustarTamaño': 'function ajustarTamaño(',
        'centrarVista': 'function centrarVista(',
        'eliminarSeleccionado': 'function eliminarSeleccionado(',
        'duplicarSeleccionado': 'function duplicarSeleccionado('
    }
    
    missing_functions = []
    for func_name, func_definition in base_functions.items():
        if func_definition not in content:
            missing_functions.append(func_name)
    
    if missing_functions:
        print("❌ Funciones base faltantes:")
        for func in missing_functions:
            print(f"   - {func}")
        return False
    else:
        print("✅ Todas las funciones base están definidas")
    
    print("✅ Todas las pruebas de onclick handlers pasaron")
    return True

if __name__ == '__main__':
    test_onclick_handlers()
