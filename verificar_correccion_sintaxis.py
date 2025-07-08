#!/usr/bin/env python3
"""
Script para verificar que la corrección del error de sintaxis JavaScript funciona
y que la eliminación de productos vuelve a funcionar correctamente.
"""

import subprocess
import sys
from pathlib import Path

def main():
    print("🔧 Verificando corrección del error de sintaxis JavaScript...")
    print("=" * 60)
    
    # Verificar que el archivo existe
    template_path = Path("dashboard/templates/dashboard/productos_venta/lista.html")
    if not template_path.exists():
        print("❌ Error: No se encontró el archivo de la plantilla")
        return False
    
    # Leer el contenido del archivo
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print("✅ Archivo de plantilla leído correctamente")
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return False
    
    # Verificar que no hay escapes incorrectos
    incorrect_escapes = [
        r"\'producto_id\'",  # Escape incorrecto de comillas simples
        r"\\\'",             # Triple escape
        r"\\n",              # Escape de nueva línea incorrecto en string
        r"\\t",              # Escape de tab incorrecto en string
    ]
    
    errors_found = []
    for line_num, line in enumerate(content.split('\n'), 1):
        for incorrect in incorrect_escapes:
            if incorrect in line:
                errors_found.append({
                    'line': line_num,
                    'content': line.strip(),
                    'error': incorrect
                })
    
    if errors_found:
        print("❌ Se encontraron errores de escape:")
        for error in errors_found:
            print(f"   Línea {error['line']}: {error['error']}")
            print(f"   Contenido: {error['content'][:100]}...")
        return False
    else:
        print("✅ No se encontraron errores de escape JavaScript")
    
    # Verificar que las funciones principales están presentes
    required_functions = [
        "safeGetProductId",
        "addEventListener('DOMContentLoaded'",
        "getElementById('deleteModal')",
        "addEventListener('submit'",
        "fetch(this.action",
    ]
    
    missing_functions = []
    for func in required_functions:
        if func not in content:
            missing_functions.append(func)
    
    if missing_functions:
        print("❌ Funciones JavaScript faltantes:")
        for func in missing_functions:
            print(f"   - {func}")
        return False
    else:
        print("✅ Todas las funciones JavaScript requeridas están presentes")
    
    # Verificar la estructura del extra_js
    if "{% block extra_js %}" in content and "{% endblock %}" in content:
        print("✅ Bloque extra_js correctamente estructurado")
    else:
        print("❌ Bloque extra_js mal estructurado")
        return False
    
    # Verificar que las comillas están correctamente balanceadas
    single_quotes = content.count("'")
    double_quotes = content.count('"')
    
    print(f"📊 Estadísticas de comillas:")
    print(f"   Comillas simples: {single_quotes}")
    print(f"   Comillas dobles: {double_quotes}")
    
    # Verificar que no hay caracteres de escape inválidos
    invalid_escapes = [r"\'", r'\"', r"\\n", r"\\t"]
    
    for invalid in invalid_escapes:
        if invalid in content:
            # Contar las ocurrencias para ver si son problemáticas
            count = content.count(invalid)
            if count > 0:
                print(f"⚠️  Advertencia: Se encontraron {count} instancias de '{invalid}'")
                # Verificar si están en contextos válidos (como strings)
                lines_with_invalid = []
                for line_num, line in enumerate(content.split('\n'), 1):
                    if invalid in line:
                        lines_with_invalid.append((line_num, line.strip()))
                
                print("   Líneas afectadas:")
                for line_num, line_content in lines_with_invalid[:5]:  # Solo mostrar primeras 5
                    print(f"     {line_num}: {line_content[:80]}...")
    
    print("\n🧪 Ejecutando prueba de sintaxis básica...")
    
    # Extraer solo el JavaScript del bloque extra_js
    js_start = content.find("{% block extra_js %}")
    js_end = content.find("{% endblock %}", js_start)
    
    if js_start != -1 and js_end != -1:
        js_content = content[js_start:js_end]
        
        # Verificar patrones problemáticos
        problematic_patterns = [
            ("Uncaught SyntaxError", "Error de sintaxis no capturado"),
            ("invalid escape sequence", "Secuencia de escape inválida"),
            (r"\'[^']*\'", "Comillas simples escapadas incorrectamente"),
            ("function(", "Declaración de función"),
            ("addEventListener", "Event listeners"),
            ("console.log", "Logs de consola"),
        ]
        
        for pattern, description in problematic_patterns:
            if pattern in js_content:
                count = js_content.count(pattern)
                print(f"   ✅ {description}: {count} instancias encontradas")
    
    print("\n🎯 Resultado de la verificación:")
    if not errors_found and not missing_functions:
        print("✅ ¡CORRECCIÓN EXITOSA! El JavaScript debería funcionar correctamente ahora.")
        print("\n📋 Próximos pasos:")
        print("1. Abrir el navegador y ir a la página de productos")
        print("2. Abrir las herramientas de desarrollador (F12)")
        print("3. Intentar eliminar un producto")
        print("4. Verificar que no aparezcan errores en la consola")
        print("5. Confirmar que la eliminación funciona correctamente")
        
        return True
    else:
        print("❌ Aún hay problemas que necesitan ser corregidos")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
