import os
import re

def fix_scripts_block():
    # Define la ruta del archivo
    file_path = r'c:\Users\olcha\Desktop\sushi_restaurant - Copy (2)\suchilitoo2\dashboard\templates\dashboard\productos_venta\lista.html'
    
    # Lee el contenido del archivo
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Verifica si el archivo usa {% block scripts %} en lugar de {% block extra_js %}
    if '{% block scripts %}' in content and '{% endblock %}' in content:
        print("Encontrado bloque 'scripts' en lugar de 'extra_js'.")
        
        # Reemplaza el bloque scripts por extra_js
        modified_content = content.replace('{% block scripts %}', '{% block extra_js %}')
        
        # Crea una copia de seguridad del archivo original
        backup_path = file_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as backup_file:
            backup_file.write(content)
        print(f"Copia de seguridad creada en: {backup_path}")
        
        # Guarda el contenido modificado
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        print(f"Archivo actualizado: {file_path}")
        print("Bloque de scripts cambiado de 'scripts' a 'extra_js'.")
        return True
    else:
        print("No se encontró el bloque 'scripts' o ya está usando 'extra_js'.")
        return False

# Ejecuta la función principal
if __name__ == "__main__":
    fix_scripts_block()
