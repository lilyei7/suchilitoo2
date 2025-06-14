#!/usr/bin/env python3
"""
Script para limpiar el archivo de proveedores eliminando código duplicado
"""

def clean_proveedores_file():
    file_path = r"c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\proveedores.html"
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar la línea donde termina el contenido bueno (antes del JavaScript duplicado)
    # Buscamos la línea que contiene el cierre del bloque extra_js limpio
    end_good_content = None
    for i, line in enumerate(lines):
        if '{% endblock %}' in line and i > 1600:  # El endblock del JavaScript limpio
            end_good_content = i + 1
            break
    
    if end_good_content:
        # Mantener solo las líneas hasta el final del JavaScript limpio
        clean_lines = lines[:end_good_content]
        
        # Escribir el archivo limpio
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(clean_lines)
        
        print(f"✅ Archivo limpiado. Líneas mantenidas: {len(clean_lines)}")
        print(f"📝 Líneas eliminadas: {len(lines) - len(clean_lines)}")
    else:
        print("❌ No se pudo encontrar el final del JavaScript limpio")

if __name__ == "__main__":
    clean_proveedores_file()
