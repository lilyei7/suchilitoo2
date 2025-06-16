#!/usr/bin/env python3
"""
Script para arreglar errores de JavaScript en recetas.html
"""

def fix_javascript_errors():
    file_path = r"c:\Users\olcha\Desktop\sushi_restaurant\suchilitoo2\dashboard\templates\dashboard\recetas.html"
    
    try:
        # Leer el archivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Archivo leído correctamente")
        print(f"Total de líneas: {len(content.splitlines())}")
        
        lines = content.splitlines()
        
        # Buscar problemas específicos
        print("\n🔍 Buscando problemas...")
        
        # Verificar el final del archivo
        last_10_lines = lines[-10:]
        print("Últimas 10 líneas:")
        for i, line in enumerate(last_10_lines, start=len(lines)-9):
            print(f"{i}: {line}")
        
        # Buscar líneas duplicadas o problemáticas
        problematic_patterns = [
            "showToast('Error al actualizar selectores de categorías', 'error');",
            "throw error;  // Re-lanzar el error para manejo superior",
            "}}"  # Dobles llaves de cierre
        ]
        
        found_issues = []
        for i, line in enumerate(lines):
            for pattern in problematic_patterns:
                if pattern in line:
                    found_issues.append((i+1, line, pattern))
        
        if found_issues:
            print(f"\n⚠️  Encontrados {len(found_issues)} problemas potenciales:")
            for line_num, line, pattern in found_issues:
                print(f"Línea {line_num}: {line.strip()}")
                print(f"  Patrón: {pattern}")
        
        # Buscar la función actualizarSelectoresCategorias para verificar su sintaxis
        in_function = False
        function_lines = []
        brace_count = 0
        
        for i, line in enumerate(lines):
            if "async function actualizarSelectoresCategorias()" in line:
                in_function = True
                brace_count = 0
                function_lines = [(i+1, line)]
            elif in_function:
                function_lines.append((i+1, line))
                # Contar llaves
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0 and '}' in line:
                    # Fin de la función
                    break
        
        if function_lines:
            print(f"\n📋 Función actualizarSelectoresCategorias ({len(function_lines)} líneas):")
            for line_num, line in function_lines[-5:]:  # Últimas 5 líneas
                print(f"{line_num}: {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    fix_javascript_errors()
