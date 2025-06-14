#!/usr/bin/env python3
"""
Script para encontrar y corregir llaves desbalanceadas en JavaScript
"""

import re

def find_brace_issues():
    """Encuentra problemas con llaves en el archivo"""
    
    template_path = "dashboard/templates/dashboard/inventario.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("🔍 BUSCANDO PROBLEMAS DE LLAVES...")
        print("=" * 50)
        
        # Buscar bloques de JavaScript
        in_script = False
        script_lines = []
        
        for i, line in enumerate(lines, 1):
            if '<script>' in line:
                in_script = True
                print(f"📍 Inicio de script en línea {i}")
            elif '</script>' in line:
                in_script = False
                print(f"📍 Fin de script en línea {i}")
            elif in_script:
                script_lines.append((i, line))
        
        # Contar llaves en contexto
        open_count = 0
        close_count = 0
        issues = []
        
        for line_num, line in script_lines:
            line_open = line.count('{')
            line_close = line.count('}')
            
            open_count += line_open
            close_count += line_close
            
            # Identificar líneas problemáticas
            if line_open > 0 or line_close > 0:
                balance = open_count - close_count
                if line.strip().endswith('{') and not line.strip().endswith('});'):
                    # Línea que abre bloque
                    pass
                elif line_close > line_open and balance < 0:
                    issues.append((line_num, line.strip(), f"Posible llave de cierre extra"))
                elif line_open > line_close and balance > 3:
                    issues.append((line_num, line.strip(), f"Posibles llaves de apertura extra"))
        
        print(f"\n📊 RESUMEN:")
        print(f"   Llaves abiertas total: {open_count}")
        print(f"   Llaves cerradas total: {close_count}")
        print(f"   Diferencia: {open_count - close_count}")
        
        if issues:
            print(f"\n⚠️  POSIBLES PROBLEMAS ENCONTRADOS:")
            for line_num, line_content, issue in issues[:10]:  # Mostrar solo los primeros 10
                print(f"   Línea {line_num}: {issue}")
                print(f"      {line_content}")
        
        # Buscar patrones específicos problemáticos
        print(f"\n🔍 BUSCANDO PATRONES PROBLEMÁTICOS...")
        
        full_content = ''.join([line for _, line in script_lines])
        
        # Buscar funciones sin cierre
        function_pattern = r'function\s+\w+\s*\([^)]*\)\s*\{'
        functions = re.finditer(function_pattern, full_content)
        
        for match in functions:
            func_start = match.start()
            # Buscar el cierre correspondiente
            brace_count = 0
            found_close = False
            
            for i, char in enumerate(full_content[func_start:], func_start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        found_close = True
                        break
            
            if not found_close:
                print(f"   ❌ Función sin cierre encontrada: {match.group()}")
        
        return open_count - close_count
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == '__main__':
    difference = find_brace_issues()
    if difference is not None:
        if difference == 0:
            print("\n✅ LLAVES BALANCEADAS CORRECTAMENTE")
        else:
            print(f"\n⚠️  NECESITA CORRECCIÓN: Faltan {abs(difference)} llaves {'de cierre' if difference > 0 else 'de apertura'}")
