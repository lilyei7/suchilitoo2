#!/usr/bin/env python3
"""
Herramienta para validar la sintaxis del JavaScript en el archivo de recetas
"""

import re
import os

def test_javascript_syntax():
    """Valida la sintaxis del JavaScript"""
    
    html_file = r'c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\recetas.html'
    
    print(f"🔍 Validando sintaxis JavaScript en: {html_file}")
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraer solo el contenido JavaScript
        script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
        
        if not script_match:
            print("❌ No se encontró bloque de JavaScript")
            return False
        
        js_code = script_match.group(1)
        
        # Escribir el código JavaScript a un archivo temporal
        temp_js_file = 'temp_recetas.js'
        with open(temp_js_file, 'w', encoding='utf-8') as f:
            f.write(js_code)
        
        print(f"✅ Código JavaScript extraído ({len(js_code)} caracteres)")
        print(f"📝 Guardado en archivo temporal: {temp_js_file}")
        
        # Verificar balance de llaves
        open_braces = js_code.count('{')
        close_braces = js_code.count('}')
        
        print(f"🔧 Llaves abiertas: {open_braces}")
        print(f"🔧 Llaves cerradas: {close_braces}")
        
        if open_braces != close_braces:
            print(f"❌ ERROR: Las llaves no están balanceadas!")
            print(f"   Diferencia: {open_braces - close_braces}")
            return False
        
        # Verificar paréntesis
        open_parens = js_code.count('(')
        close_parens = js_code.count(')')
        
        print(f"🔧 Paréntesis abiertos: {open_parens}")
        print(f"🔧 Paréntesis cerrados: {close_parens}")
        
        if open_parens != close_parens:
            print(f"❌ ERROR: Los paréntesis no están balanceados!")
            return False
        
        # Verificar corchetes
        open_brackets = js_code.count('[')
        close_brackets = js_code.count(']')
        
        print(f"🔧 Corchetes abiertos: {open_brackets}")
        print(f"🔧 Corchetes cerrados: {close_brackets}")
        
        if open_brackets != close_brackets:
            print(f"❌ ERROR: Los corchetes no están balanceados!")
            return False
        
        # Buscar funciones definidas
        function_pattern = r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\('
        functions = re.findall(function_pattern, js_code)
        
        print(f"\n📋 Funciones encontradas ({len(functions)}):")
        for func in functions:
            print(f"   - {func}()")
        
        # Verificar si todas las funciones críticas están definidas
        required_functions = [
            'abrirModalCrearReceta',
            'abrirModalCategorias', 
            'verDetalleReceta',
            'editarReceta',
            'duplicarReceta',
            'eliminarReceta'
        ]
        
        missing_functions = []
        for func in required_functions:
            if func not in functions:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"\n❌ Funciones faltantes:")
            for func in missing_functions:
                print(f"   - {func}()")
            return False
        
        print(f"\n✅ Todas las funciones requeridas están definidas")
        
        # Limpiar archivo temporal
        if os.path.exists(temp_js_file):
            os.remove(temp_js_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Error al validar sintaxis: {e}")
        return False

if __name__ == "__main__":
    test_javascript_syntax()
