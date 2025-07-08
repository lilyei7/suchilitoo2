"""
Utilidad para verificar la sintaxis del JavaScript en el template
"""
from bs4 import BeautifulSoup
import os
import re
import sys
import json

def verificar_sintaxis_js():
    """Verifica la sintaxis del JavaScript en el template de lista.html"""
    template_path = os.path.join('dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html')
    
    if not os.path.exists(template_path):
        print(f"❌ Error: No se encontró el archivo {template_path}")
        return
    
    print(f"Analizando {template_path}...")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer bloques de script
    soup = BeautifulSoup(content, 'html.parser')
    scripts = soup.find_all('script')
    
    print(f"Se encontraron {len(scripts)} bloques de script")
    
    # Verificar cada bloque de script
    for i, script in enumerate(scripts):
        script_content = script.string
        if not script_content:
            print(f"Script #{i+1}: vacío o solo tiene etiquetas externas")
            continue
        
        print(f"\nAnalizando Script #{i+1}:")
        
        # Buscar problemas comunes
        problemas = []
        
        # 1. Llaves desbalanceadas
        open_braces = script_content.count('{')
        close_braces = script_content.count('}')
        if open_braces != close_braces:
            problemas.append(f"⚠️ Llaves desbalanceadas: {open_braces} abiertas, {close_braces} cerradas")
        
        # 2. Paréntesis desbalanceados
        open_parens = script_content.count('(')
        close_parens = script_content.count(')')
        if open_parens != close_parens:
            problemas.append(f"⚠️ Paréntesis desbalanceados: {open_parens} abiertos, {close_parens} cerrados")
        
        # 3. Corchetes desbalanceados
        open_brackets = script_content.count('[')
        close_brackets = script_content.count(']')
        if open_brackets != close_brackets:
            problemas.append(f"⚠️ Corchetes desbalanceados: {open_brackets} abiertos, {close_brackets} cerrados")
        
        # 4. Comillas invertidas (template literals) desbalanceadas
        backticks = script_content.count('`')
        if backticks % 2 != 0:
            problemas.append(f"⚠️ Comillas invertidas desbalanceadas: {backticks} (debe ser par)")
        
        # 5. Puntos y coma faltantes
        lines = script_content.split('\n')
        for j, line in enumerate(lines):
            line = line.strip()
            if line and not line.endswith('{') and not line.endswith('}') and not line.endswith(';') and not line.endswith(',') and not line.endswith(':') and not line.endswith('(') and not line.endswith(')') and not line.endswith('[') and not line.endswith(']') and not line.endswith('`') and not line.endswith('*/') and not line.startswith('//') and not line.startswith('/*'):
                if j < len(lines) - 1 and not lines[j+1].strip().startswith(('.', '?', ':', '}')):
                    problemas.append(f"⚠️ Posible punto y coma faltante en línea {j+1}: {line}")
        
        # 6. Errores comunes de sintaxis
        errores_comunes = [
            (r'console\.log\([^)]*\)\s*\{', "Console.log seguido de { sin punto y coma"),
            (r'for\s*\([^)]*\)\s*\{', "for sin { de apertura"),
            (r'if\s*\([^)]*\)\s*\{', "if sin { de apertura"),
            (r'else\s*\{', "else sin { de apertura"),
            (r'function\s*\([^)]*\)\s*\{', "function sin { de apertura"),
            (r'\}\s*else\s*\{', "} else { mal formateado"),
            (r'\}\s*catch\s*\([^)]*\)\s*\{', "} catch() { mal formateado"),
            (r'\}\s*finally\s*\{', "} finally { mal formateado"),
            (r'=\s*>\s*\{', "=> { mal formateado para arrow function"),
            (r'=\s*>\s*\(', "=> ( mal formateado para arrow function"),
        ]
        
        for pattern, desc in errores_comunes:
            if re.search(pattern, script_content):
                problemas.append(f"⚠️ Posible error de sintaxis: {desc}")
        
        # 7. Buscar líneas problemáticas
        lineas_problematicas = []
        for j, line in enumerate(lines):
            line = line.strip()
            if line:
                # Buscar patrones específicos de error
                if '}:' in line or '};' in line and not '"};' in line and not "'};'" in line:
                    lineas_problematicas.append((j+1, line, "Posible error de sintaxis con }"))
                
                if '{:' in line or '{;' in line:
                    lineas_problematicas.append((j+1, line, "Posible error de sintaxis con {"))
                
                if ':}' in line or ';{' in line:
                    lineas_problematicas.append((j+1, line, "Posible error de sintaxis con : o ; seguido de {"))
                
                if re.search(r'console\.log\([^)]*$', line):
                    lineas_problematicas.append((j+1, line, "console.log sin cerrar"))
                
                if '${' in line and '`' not in line:
                    lineas_problematicas.append((j+1, line, "Template literal ${} sin comillas invertidas"))
                
                # Buscar específicamente errores relacionados con los campos de entrada
                if 'console.log(`   ${key}' in line:
                    lineas_problematicas.append((j+1, line, "Posible template literal mal formado"))
                
                # Verificar líneas que terminan con operadores
                operators = ['+', '-', '*', '/', '=', '&&', '||', '??', '?', ':']
                for op in operators:
                    if line.endswith(op):
                        lineas_problematicas.append((j+1, line, f"Línea termina con operador {op}"))
        
        # Mostrar problemas encontrados
        if problemas:
            print("Problemas encontrados:")
            for problema in problemas:
                print(f"  {problema}")
        else:
            print("✅ No se encontraron problemas estructurales en el script")
        
        # Mostrar líneas problemáticas
        if lineas_problematicas:
            print("\nLíneas potencialmente problemáticas:")
            for linea, contenido, desc in lineas_problematicas:
                print(f"  Línea {linea}: {contenido}")
                print(f"    - {desc}")
        else:
            print("✅ No se encontraron líneas potencialmente problemáticas")

    print("\n=== CONCLUSIÓN ===")
    print("La verificación de sintaxis básica está completa.")
    print("Se recomienda también verificar el JavaScript en un navegador.")
    print("Para una verificación más exhaustiva, se recomienda usar una herramienta como ESLint.")

if __name__ == "__main__":
    verificar_sintaxis_js()
