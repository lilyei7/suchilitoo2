#!/usr/bin/env python
"""
Script para actualizar la URL de ngrok en la configuración de Django
"""

import os
import re

def actualizar_ngrok_url():
    """Actualizar la URL de ngrok en settings.py"""
    print("=== ACTUALIZACIÓN DE URL DE NGROK ===")
    
    nueva_url = input("Ingresa tu nueva URL de ngrok (ej: https://abc123.ngrok-free.app): ").strip()
    
    if not nueva_url:
        print("❌ No se ingresó ninguna URL")
        return
    
    if not nueva_url.startswith('https://') or not 'ngrok-free.app' in nueva_url:
        print("❌ La URL debe ser de formato https://xxxxx.ngrok-free.app")
        return
    
    settings_file = 'sushi_core/settings.py'
    
    if not os.path.exists(settings_file):
        print(f"❌ No se encontró el archivo {settings_file}")
        return
    
    try:
        # Leer el archivo
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar y reemplazar la URL de ngrok
        pattern = r"'https://[a-z0-9]+\.ngrok-free\.app'"
        replacement = f"'{nueva_url}'"
        
        new_content = re.sub(pattern, replacement, content)
        
        if new_content == content:
            # Si no encontró el patrón, agregar la nueva URL
            csrf_pattern = r"(CSRF_TRUSTED_ORIGINS = \[)"
            csrf_replacement = f"\\1\n    '{nueva_url}',"
            new_content = re.sub(csrf_pattern, csrf_replacement, content)
        
        # Escribir el archivo actualizado
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ URL de ngrok actualizada a: {nueva_url}")
        print("✅ Reinicia el servidor Django para aplicar los cambios")
        print("\nComandos para reiniciar:")
        print("1. Ctrl+C en la terminal donde corre Django")
        print("2. python manage.py runserver")
        
    except Exception as e:
        print(f"❌ Error al actualizar: {e}")

if __name__ == '__main__':
    actualizar_ngrok_url()
