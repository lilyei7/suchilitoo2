#!/usr/bin/env python3
"""
Herramienta para encontrar llaves desbalanceadas en JavaScript
"""

import re

def find_brace_imbalance():
    """Encuentra dónde están las llaves desbalanceadas"""
    
    html_file = r'c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\recetas.html'
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraer solo el contenido JavaScript
        script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
        
        if not script_match:
            print("❌ No se encontró bloque de JavaScript")
            return
        
        js_code = script_match.group(1)
        lines = js_code.split('\n')
        
        # Contar llaves por línea
        brace_count = 0
        line_number = 0
        
        print("🔍 Analizando balance de llaves línea por línea:")
        print("=" * 60)
        
        for i, line in enumerate(lines):
            line_number = i + 1
            open_braces = line.count('{')
            close_braces = line.count('}')
            brace_count += open_braces - close_braces
            
            if open_braces > 0 or close_braces > 0:
                status = "✅" if brace_count >= 0 else "❌"
                print(f"{status} Línea {line_number:4d}: +{open_braces} -{close_braces} = {brace_count:3d} | {line.strip()[:70]}")
        
        print("=" * 60)
        print(f"Balance final: {brace_count}")
        
        if brace_count != 0:
            print(f"❌ ERROR: Balance de llaves incorrecto ({brace_count})")
            
            # Buscar las últimas líneas donde hay problemas
            print("\n🔍 Últimas 20 líneas con llaves:")
            brace_lines = []
            for i, line in enumerate(lines):
                if '{' in line or '}' in line:
                    brace_lines.append((i+1, line.strip()))
            
            for line_num, line_content in brace_lines[-20:]:
                print(f"Línea {line_num:4d}: {line_content}")
                
        else:
            print("✅ Balance de llaves correcto")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    find_brace_imbalance()
