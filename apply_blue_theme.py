import os
import sys
import shutil
import subprocess
from pathlib import Path
import webbrowser
import time

print("===== APLICANDO TEMA AZUL Y BLANCO AL SISTEMA MESERO =====")

# Configurar rutas
base_dir = Path.cwd()
templates_dir = base_dir / 'mesero' / 'templates' / 'mesero'
static_dir = base_dir / 'mesero' / 'static' / 'mesero' / 'css'

# 1. Modificar base_simple.html para incluir el tema global
print("\n1. Actualizando template base para incluir tema azul...")

base_path = templates_dir / 'base_simple.html'
if base_path.exists():
    content = base_path.read_text(encoding='utf-8')
    
    # Verificar si ya tiene la inclusión del tema
    if 'global-blue-theme.css' not in content:
        # Insertar referencia al CSS de tema azul justo después del Font Awesome
        insert_point = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">'
        theme_link = f'{insert_point}\n    \n    <!-- Tema Azul y Blanco -->\n    <link rel="stylesheet" href="{{% static \'mesero/css/global-blue-theme.css\' %}}?v={{% now \'U\' %}}">'
        content = content.replace(insert_point, theme_link)
        
        # Agregar variables CSS inline para forzar los colores
        insert_point = '<style>'
        blue_vars = f'{insert_point}\n        /* Paleta Azul y Blanco */\n        :root {{\n            --primary: #2b6cb0 !important;\n            --primary-light: #4299e1 !important;\n            --primary-dark: #2c5282 !important;\n            --primary-pale: #ebf8ff !important;\n        }}\n'
        content = content.replace(insert_point, blue_vars)
        
        # Guardar el archivo modificado
        base_path.write_text(content, encoding='utf-8')
        print("✅ Template base actualizado con tema azul y blanco")
    else:
        print("✅ Template base ya contiene el tema azul y blanco")
else:
    print("❌ No se encontró el archivo base_simple.html")

# 2. Collectstatic
print("\n2. Recolectando archivos estáticos...")
subprocess.run([sys.executable, "manage.py", "collectstatic", "--noinput"])

# 3. Reiniciar servidor
print("\n3. Reiniciando servidor Django...")
subprocess.run([sys.executable, "restart_server.py"])
time.sleep(3)  # Esperar a que el servidor se inicie

# 4. Abrir navegador
print("\n4. Abriendo navegador...")
url = "http://127.0.0.1:8000/mesero/login/"
webbrowser.open(url)

print("\n✅ Sistema preparado con tema azul y blanco.")
print("   Por favor, inicia sesión con: mesero1 / mesero123")
print("   Luego, navega al menú para ver el nuevo diseño.")
