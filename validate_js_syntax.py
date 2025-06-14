#!/usr/bin/env python3
"""
Script para extraer y validar el JavaScript del archivo de proveedores
"""
import re

def extract_javascript(file_path):
    """Extrae solo el contenido JavaScript del archivo HTML"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar el bloque de script
        script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
        if script_match:
            return script_match.group(1).strip()
        else:
            return None
    except Exception as e:
        print(f"Error leyendo archivo: {e}")
        return None

def validate_javascript_syntax(js_content):
    """Valida la sintaxis básica del JavaScript"""
    issues = []
    lines = js_content.split('\n')
    
    # Contadores para verificar balance de llaves y paréntesis
    brace_count = 0
    paren_count = 0
    bracket_count = 0
    
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        # Ignorar comentarios
        if line_stripped.startswith('//') or line_stripped.startswith('/*'):
            continue
            
        # Contar llaves, paréntesis y corchetes
        for char in line:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            elif char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1        # Verificar problemas específicos
        if '};}' in line:
            issues.append("Línea " + str(i) + ": Posible problema con '};}' - cierre doble de función")
        
        if line_stripped.endswith('};};'):
            issues.append("Línea " + str(i) + ": Problema definitivo con '};};' - cierre doble")
            
        # Buscar declaraciones de variables duplicadas
        if 'const submitBtn' in line or 'let submitBtn' in line or 'var submitBtn' in line:
            issues.append(f"Línea {i}: Posible declaración duplicada de 'submitBtn'")
    
    # Verificar balance final
    if brace_count != 0:
        issues.append(f"Balance de llaves incorrecto: {brace_count} llaves sin cerrar")
    if paren_count != 0:
        issues.append(f"Balance de paréntesis incorrecto: {paren_count} paréntesis sin cerrar")
    if bracket_count != 0:
        issues.append(f"Balance de corchetes incorrecto: {bracket_count} corchetes sin cerrar")
    
    return issues

def main():
    file_path = r"c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\proveedores.html"
    
    print("🔍 Extrayendo JavaScript del archivo de proveedores...")
    js_content = extract_javascript(file_path)
    
    if not js_content:
        print("❌ No se pudo extraer el contenido JavaScript")
        return
    
    print(f"📝 JavaScript extraído: {len(js_content)} caracteres")
    print("🔍 Validando sintaxis...")
    
    issues = validate_javascript_syntax(js_content)
    
    if issues:
        print("❌ Problemas encontrados:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ No se encontraron problemas obvios de sintaxis")
    
    # Mostrar las últimas líneas para depuración
    lines = js_content.split('\n')
    print(f"\n📄 Últimas 10 líneas del JavaScript:")
    for i, line in enumerate(lines[-10:], len(lines) - 9):
        print(f"{i:4d}: {line}")

if __name__ == "__main__":
    main()
