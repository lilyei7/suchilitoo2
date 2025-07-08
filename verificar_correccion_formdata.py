"""
Verifica que se han corregido todos los problemas de JavaScript en la eliminación de productos.
"""

import os
import sys
import time
import webbrowser
import re

def print_title(title):
    """Imprime un título formateado."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "*"))
    print("=" * 80)

def print_section(section):
    """Imprime una sección formateada."""
    print("\n" + "-" * 80)
    print(f" {section} ".center(80, "-"))
    print("-" * 80)

def check_js_errors():
    """Verifica errores comunes de JavaScript en el archivo lista.html."""
    print_section("Verificando errores de JavaScript")
    
    file_path = "dashboard/templates/dashboard/productos_venta/lista.html"
    
    if not os.path.exists(file_path):
        print(f"❌ Error: No se encontró el archivo {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar declaraciones duplicadas
    js_vars = {
        'productoId': 0,
        'formData': 0,
    }
    
    # Buscar declaraciones de variables
    lines = content.split('\n')
    for i, line in enumerate(lines):
        for var in js_vars:
            if re.search(rf'const\s+{var}\s*=', line):
                js_vars[var] += 1
                print(f"   Variable '{var}' declarada en línea {i+1}: {line.strip()}")
    
    # Verificar si hay duplicados
    errors_found = False
    for var, count in js_vars.items():
        if count > 1:
            print(f"❌ Error: La variable '{var}' está declarada {count} veces")
            errors_found = True
        else:
            print(f"✅ La variable '{var}' está declarada correctamente ({count} vez)")
    
    # Buscar errores de sintaxis comunes
    syntax_errors = [
        (r',[^}"\'\n]*},', "Coma incorrecta en objeto JavaScript"),
        (r'{\s*[^}"\'\n]*,,', "Doble coma en objeto JavaScript"),
        (r'{\s*,', "Coma al inicio de objeto JavaScript"),
        (r'headers:\s*{[^}]*},\s*}', "Problema con las comas en los headers"),
        (r'const [a-zA-Z_$][a-zA-Z0-9_$]*\s*=.*;\s*const \1\s*=', "Redeclaración de variable"),
    ]
    
    for pattern, description in syntax_errors:
        matches = re.findall(pattern, content)
        if matches:
            print(f"❌ Error de sintaxis: {description}")
            for match in matches[:3]:  # Mostrar hasta 3 ejemplos
                print(f"   Ejemplo: {match}")
            errors_found = True
    
    return not errors_found

def main():
    """Función principal del script."""
    print_title("VERIFICACIÓN FINAL DE CORRECCIÓN DE JAVASCRIPT")
    
    # Verificar errores de JavaScript
    js_ok = check_js_errors()
    
    if js_ok:
        print("\n✅ No se encontraron errores de JavaScript en el código")
        print("✅ La corrección de las declaraciones duplicadas de 'formData' parece exitosa")
        
        # Preguntar si se desea abrir el navegador
        print("\n¿Deseas abrir el navegador para probar la funcionalidad? (s/n)")
        choice = input().lower()
        
        if choice == 's':
            url = "http://localhost:8000/dashboard/productos-venta/"
            print(f"\nAbriendo {url} en el navegador...")
            webbrowser.open(url)
            
            print("\nInstrucciones para probar la eliminación:")
            print("1. Inicia sesión si es necesario")
            print("2. Abre la consola del navegador (F12)")
            print("3. Localiza un producto en la lista")
            print("4. Haz clic en el botón 'Eliminar'")
            print("5. Confirma la eliminación en el modal")
            print("6. Verifica que no aparezcan errores en la consola del navegador")
            print("7. Verifica que el producto se elimine correctamente")
    else:
        print("\n❌ Se encontraron errores en el código JavaScript que deben corregirse")

if __name__ == "__main__":
    main()
