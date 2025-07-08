"""
Verifica que se han corregido los problemas de JavaScript en la eliminación de productos.
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

def check_js_syntax():
    """Verifica la sintaxis JavaScript en el archivo lista.html."""
    print_section("Verificando sintaxis JavaScript")
    
    file_path = "dashboard/templates/dashboard/productos_venta/lista.html"
    
    if not os.path.exists(file_path):
        print(f"❌ Error: No se encontró el archivo {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar declaraciones duplicadas de productoId
    productoId_declarations = re.findall(r'const\s+productoId\s*=', content)
    if len(productoId_declarations) > 1:
        print(f"❌ Se encontraron {len(productoId_declarations)} declaraciones de 'productoId'")
        
        # Mostrar las líneas donde se encuentran las declaraciones
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if re.search(r'const\s+productoId\s*=', line):
                print(f"   Línea {i+1}: {line.strip()}")
        
        return False
    else:
        print("✅ No se encontraron declaraciones duplicadas de 'productoId'")
    
    # Verificar errores de sintaxis comunes en JavaScript
    js_errors = [
        (r',[^}"\'\n]*},', "Coma incorrecta en objeto JavaScript"),
        (r'{\s*[^}"\'\n]*,,', "Doble coma en objeto JavaScript"),
        (r'{\s*,', "Coma al inicio de objeto JavaScript"),
        (r'headers:\s*{[^}]*},\s*}', "Problema con las comas en los headers"),
    ]
    
    for pattern, description in js_errors:
        matches = re.findall(pattern, content)
        if matches:
            print(f"❌ Error de sintaxis: {description}")
            for match in matches[:3]:  # Mostrar hasta 3 ejemplos
                print(f"   Ejemplo: {match}")
            return False
    
    print("✅ No se encontraron errores comunes de sintaxis JavaScript")
    return True

def analyze_fetch_request():
    """Analiza la estructura de la petición fetch en lista.html."""
    print_section("Analizando estructura de la petición AJAX")
    
    file_path = "dashboard/templates/dashboard/productos_venta/lista.html"
    
    if not os.path.exists(file_path):
        print(f"❌ Error: No se encontró el archivo {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar estructura básica de fetch
    if not re.search(r'fetch\s*\(\s*this\.action\s*,\s*{', content):
        print("❌ Error: No se encontró la estructura básica de fetch")
        return False
    
    print("✅ Estructura básica de fetch encontrada")
    
    # Verificar headers correctos
    if not re.search(r'headers\s*:\s*{[^}]*\'X-Requested-With\'\s*:\s*\'XMLHttpRequest\'', content):
        print("❌ Error: Falta header 'X-Requested-With: XMLHttpRequest'")
        return False
    
    print("✅ Headers básicos correctos")
    
    # Verificar manejadores de respuesta
    if not re.search(r'\.then\s*\(\s*response\s*=>\s*{', content):
        print("❌ Error: No se encontró el manejador de respuesta (.then)")
        return False
    
    print("✅ Manejadores de respuesta correctos")
    
    return True

def verify_modal_structure():
    """Verifica la estructura del modal de eliminación."""
    print_section("Verificando estructura del modal de eliminación")
    
    file_path = "dashboard/templates/dashboard/productos_venta/lista.html"
    
    if not os.path.exists(file_path):
        print(f"❌ Error: No se encontró el archivo {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar presencia del modal
    if not re.search(r'<div[^>]*id\s*=\s*["\']deleteModal["\']', content):
        print("❌ Error: No se encontró el modal con id 'deleteModal'")
        return False
    
    print("✅ Modal de eliminación encontrado")
    
    # Verificar formulario dentro del modal
    if not re.search(r'<form[^>]*id\s*=\s*["\']deleteForm["\']', content):
        print("❌ Error: No se encontró el formulario con id 'deleteForm'")
        return False
    
    print("✅ Formulario de eliminación encontrado")
    
    # Verificar campo hidden para producto_id
    if not re.search(r'<input[^>]*type\s*=\s*["\']hidden["\'][^>]*name\s*=\s*["\']producto_id["\']', content):
        print("❌ Error: No se encontró el campo hidden para producto_id")
        return False
    
    print("✅ Campo hidden para producto_id encontrado")
    
    return True

def open_browser_for_testing():
    """Abre el navegador para probar la funcionalidad de eliminación."""
    print_section("Abriendo navegador para pruebas")
    
    # URL de la lista de productos
    url = "http://localhost:8000/dashboard/productos-venta/"
    
    print(f"Abriendo {url} en el navegador...")
    webbrowser.open(url)
    
    print("\nInstrucciones para probar la eliminación:")
    print("1. Inicia sesión si es necesario")
    print("2. Localiza un producto en la lista")
    print("3. Haz clic en el botón 'Eliminar'")
    print("4. Confirma la eliminación en el modal")
    print("5. Verifica que no aparezcan errores en la consola del navegador (F12)")
    print("6. Verifica que el producto se elimine correctamente")

def main():
    """Función principal del script."""
    print_title("VERIFICACIÓN DE CORRECCIÓN DE JAVASCRIPT")
    
    # Verificar sintaxis JS
    if not check_js_syntax():
        print("\n❌ Se encontraron problemas de sintaxis JavaScript que deben corregirse.")
        return
    
    # Analizar estructura de fetch
    if not analyze_fetch_request():
        print("\n❌ Se encontraron problemas en la estructura de la petición AJAX.")
        return
    
    # Verificar estructura del modal
    if not verify_modal_structure():
        print("\n❌ Se encontraron problemas en la estructura del modal de eliminación.")
        return
    
    # Todo parece estar bien, abrir el navegador para pruebas
    print("\n✅ Todas las verificaciones estáticas pasaron correctamente!")
    print("✅ La corrección de las declaraciones duplicadas de 'productoId' parece exitosa.")
    print("✅ La sintaxis JavaScript parece correcta.")
    
    # Preguntar si se desea abrir el navegador
    print("\n¿Deseas abrir el navegador para probar la funcionalidad? (s/n)")
    choice = input().lower()
    
    if choice == 's':
        open_browser_for_testing()
    else:
        print("\nPuedes probar la funcionalidad manualmente accediendo a:")
        print("http://localhost:8000/dashboard/productos-venta/")

if __name__ == "__main__":
    main()
