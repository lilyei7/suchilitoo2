#!/usr/bin/env python3
"""
Script para encontrar la línea problemática en el template
"""

import re

def find_problematic_lines():
    try:
        with open('dashboard/templates/dashboard/inventario.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Buscar líneas que contengan la sintaxis problemática
        problematic_patterns = [
            r"proveedor\.tipo\s*==\s*['\"]principal['\"]",
            r"and\s+['\"]star['\"]",
            r"or\s+['\"]handshake['\"]",
            r"proveedor\.tipo.*and.*or"
        ]
        
        print("🔍 Buscando líneas problemáticas...")
        print("=" * 60)
        
        found_issues = []
        
        for i, line in enumerate(lines, 1):
            # Buscar sintaxis de template Django incorrecta
            if 'proveedor.tipo' in line and ('and' in line or 'or' in line):
                # Si no está dentro de {% %} o es JavaScript
                if not (line.strip().startswith('{% ') or line.strip().startswith('{{') or '//' in line or 'function' in line or 'const' in line or 'var' in line):
                    found_issues.append((i, line.strip()))
                    print(f"⚠️  Línea {i}: {line.strip()}")
            
            # Buscar específicamente la sintaxis del error
            if "== 'principal' and 'star' or 'handshake'" in line:
                found_issues.append((i, line.strip()))
                print(f"🚨 ENCONTRADO - Línea {i}: {line.strip()}")
        
        if not found_issues:
            print("❌ No se encontraron líneas problemáticas obvias.")
            print("\n🔍 Buscando todas las líneas que contengan 'proveedor.tipo':")
            
            for i, line in enumerate(lines, 1):
                if 'proveedor.tipo' in line:
                    print(f"   Línea {i}: {line.strip()}")
        else:
            print(f"\n✅ Se encontraron {len(found_issues)} líneas problemáticas.")
            
            # Mostrar sugerencias de corrección
            print("\n💡 Sugerencias de corrección:")
            for line_num, line_content in found_issues:
                print(f"\nLínea {line_num}:")
                print(f"   Actual: {line_content}")
                if "== 'principal' and 'star' or 'handshake'" in line_content:
                    corrected = line_content.replace("== 'principal' and 'star' or 'handshake'", "== 'principal' %}star{% else %}handshake{% endif")
                    print(f"   Corregir a: {corrected}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    find_problematic_lines()
