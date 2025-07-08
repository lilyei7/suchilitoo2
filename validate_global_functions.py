#!/usr/bin/env python3
"""
Script para validar que todas las funciones requeridas en onclick handlers
estén expuestas globalmente en el archivo croquis_editor.html
"""

import re
import sys
from pathlib import Path

def extract_onclick_functions(html_content):
    """Extrae todas las funciones llamadas en onclick handlers"""
    onclick_pattern = r'onclick="([^"]*)"'
    onclick_matches = re.findall(onclick_pattern, html_content)
    
    functions = set()
    for onclick in onclick_matches:
        # Buscar llamadas a funciones: functionName() o functionName(params)
        func_pattern = r'(\w+)\s*\('
        func_matches = re.findall(func_pattern, onclick)
        functions.update(func_matches)
    
    return functions

def extract_exposed_functions(html_content):
    """Extrae todas las funciones expuestas en window."""
    window_pattern = r'window\.(\w+)\s*='
    return set(re.findall(window_pattern, html_content))

def extract_defined_functions(html_content):
    """Extrae todas las funciones definidas en el JavaScript"""
    func_pattern = r'function\s+(\w+)\s*\('
    return set(re.findall(func_pattern, html_content))

def main():
    file_path = Path(__file__).parent / "dashboard" / "templates" / "dashboard" / "croquis_editor.html"
    
    if not file_path.exists():
        print(f"❌ Archivo no encontrado: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 VALIDACIÓN DE FUNCIONES GLOBALES EN CROQUIS EDITOR")
    print("=" * 60)
    
    # Extraer funciones
    onclick_functions = extract_onclick_functions(content)
    exposed_functions = extract_exposed_functions(content)
    defined_functions = extract_defined_functions(content)
    
    print(f"\n📋 Funciones llamadas en onclick handlers ({len(onclick_functions)}):")
    for func in sorted(onclick_functions):
        print(f"  - {func}")
    
    print(f"\n🌐 Funciones expuestas en window ({len(exposed_functions)}):")
    for func in sorted(exposed_functions):
        print(f"  - {func}")
    
    print(f"\n⚙️ Funciones definidas en JavaScript ({len(defined_functions)}):")
    for func in sorted(defined_functions):
        print(f"  - {func}")
    
    # Validación
    print("\n🔍 RESULTADOS DE VALIDACIÓN:")
    print("-" * 30)
    
    missing_exposures = onclick_functions - exposed_functions
    missing_definitions = onclick_functions - defined_functions
    
    all_valid = True
    
    if missing_exposures:
        print(f"\n❌ Funciones onclick NO EXPUESTAS en window ({len(missing_exposures)}):")
        for func in sorted(missing_exposures):
            print(f"  - {func}")
        all_valid = False
    
    if missing_definitions:
        print(f"\n❌ Funciones onclick NO DEFINIDAS ({len(missing_definitions)}):")
        for func in sorted(missing_definitions):
            print(f"  - {func}")
        all_valid = False
    
    if all_valid:
        print("\n✅ TODAS las funciones onclick están correctamente expuestas y definidas")
        print("🎉 Los onclick handlers funcionarán correctamente")
    else:
        print(f"\n⚠️ Se encontraron {len(missing_exposures | missing_definitions)} problemas")
        print("❌ Algunos onclick handlers NO funcionarán")
    
    # Estadísticas adicionales
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"  - Total funciones onclick: {len(onclick_functions)}")
    print(f"  - Total funciones expuestas: {len(exposed_functions)}")
    print(f"  - Total funciones definidas: {len(defined_functions)}")
    print(f"  - Cobertura exposición: {(len(onclick_functions - missing_exposures) / len(onclick_functions) * 100):.1f}%")
    print(f"  - Cobertura definición: {(len(onclick_functions - missing_definitions) / len(onclick_functions) * 100):.1f}%")
    
    return all_valid

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
