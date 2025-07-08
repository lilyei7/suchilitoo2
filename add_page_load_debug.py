import os
import re

def add_page_load_debug():
    # Define la ruta del archivo
    file_path = r'c:\Users\olcha\Desktop\sushi_restaurant - Copy (2)\suchilitoo2\dashboard\templates\dashboard\productos_venta\lista.html'
    
    # Lee el contenido del archivo
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Busca la posición después de la apertura del tag script dentro del bloque extra_js
    script_start = content.find('<script>', content.find('{% block extra_js %}'))
    
    if script_start != -1:
        # Posición para insertar nuestro código de debug
        insert_pos = script_start + len('<script>')
        
        # Código de debug para insertar
        debug_code = """
    // Código de prueba para verificar que el JavaScript se está cargando
    console.log('🔍 [DEBUG] JavaScript cargado en productos_venta/lista.html', {
        time: new Date().toISOString(),
        page: 'productos_venta/lista.html',
        url: window.location.href
    });
    
    // Mostrar un indicador visual de que el JS está cargado
    window.addEventListener('DOMContentLoaded', function() {
        // Crear un elemento de notificación
        const debugNotification = document.createElement('div');
        debugNotification.style.position = 'fixed';
        debugNotification.style.bottom = '20px';
        debugNotification.style.right = '20px';
        debugNotification.style.backgroundColor = 'rgba(0, 128, 255, 0.9)';
        debugNotification.style.color = 'white';
        debugNotification.style.padding = '10px 15px';
        debugNotification.style.borderRadius = '5px';
        debugNotification.style.zIndex = '9999';
        debugNotification.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
        debugNotification.textContent = '✓ JavaScript cargado correctamente';
        
        // Añadir al DOM
        document.body.appendChild(debugNotification);
        
        // Remover después de 5 segundos
        setTimeout(function() {
            debugNotification.style.transition = 'opacity 0.5s ease-out';
            debugNotification.style.opacity = '0';
            setTimeout(function() {
                debugNotification.remove();
            }, 500);
        }, 5000);
    });
"""
        
        # Insertar el código de debug
        modified_content = content[:insert_pos] + debug_code + content[insert_pos:]
        
        # Crea una copia de seguridad del archivo original
        backup_path = file_path + '.debug_backup'
        with open(backup_path, 'w', encoding='utf-8') as backup_file:
            backup_file.write(content)
        print(f"Copia de seguridad creada en: {backup_path}")
        
        # Guarda el contenido modificado
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        print(f"Archivo actualizado con código de debug: {file_path}")
        return True
    else:
        print("No se pudo encontrar la etiqueta script dentro del bloque extra_js.")
        return False

# Ejecuta la función principal
if __name__ == "__main__":
    add_page_load_debug()
