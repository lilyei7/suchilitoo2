import os
import re

def corregir_bloque_styles():
    # Define la ruta del archivo
    file_path = r'c:\Users\olcha\Desktop\sushi_restaurant - Copy (2)\suchilitoo2\dashboard\templates\dashboard\productos_venta\lista.html'
    
    # Lee el contenido del archivo
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Buscar si existe un bloque styles que no está en base.html
    if '{% block styles %}' in content:
        print("Encontrado bloque 'styles' que no está en base.html.")
        
        # Extraer el contenido del bloque styles
        styles_match = re.search(r'{% block styles %}(.*?){% endblock %}', content, re.DOTALL)
        
        if styles_match:
            styles_content = styles_match.group(1)
            
            # Crear una copia de seguridad del archivo original
            backup_path = file_path + '.styles_backup'
            with open(backup_path, 'w', encoding='utf-8') as backup_file:
                backup_file.write(content)
            print(f"Copia de seguridad creada en: {backup_path}")
            
            # Mover el contenido de styles al bloque extra_css
            if '{% block extra_css %}' in content:
                # Reemplazar el bloque extra_css existente
                extra_css_match = re.search(r'{% block extra_css %}(.*?){% endblock %}', content, re.DOTALL)
                if extra_css_match:
                    extra_css_content = extra_css_match.group(1)
                    new_extra_css_content = extra_css_content + styles_content
                    modified_content = content.replace(extra_css_match.group(0), 
                                                     f"{{% block extra_css %}}{new_extra_css_content}{{% endblock %}}")
                else:
                    print("No se pudo encontrar el contenido del bloque extra_css.")
                    return False
            else:
                # Añadir un nuevo bloque extra_css
                modified_content = content.replace('{% extends', 
                                                 f"{{% block extra_css %}}{styles_content}{{% endblock %}}\n\n{{% extends")
            
            # Eliminar el bloque styles
            modified_content = modified_content.replace(styles_match.group(0), '')
            
            # Guardar el contenido modificado
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)
            print(f"Archivo actualizado: {file_path}")
            print("Contenido de 'styles' movido a 'extra_css' y bloque 'styles' eliminado.")
            return True
        else:
            print("No se pudo extraer el contenido del bloque styles.")
            return False
    else:
        print("No se encontró el bloque 'styles'.")
        return False

# Ejecuta la función principal
if __name__ == "__main__":
    corregir_bloque_styles()
