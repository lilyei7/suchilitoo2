import requests
import re
import time
import os
import sys
from urllib.parse import urljoin

def test_js_errors():
    print("🔍 VERIFICANDO CORRECCIONES DE JAVASCRIPT...")
    print("==================================================")
    
    # URL del servidor local
    base_url = "http://127.0.0.1:8000"
    inventario_url = urljoin(base_url, "/dashboard/inventario/")
    
    try:
        # Primero verificamos si el servidor está corriendo
        response = requests.get(base_url)
        if response.status_code != 200:
            print("❌ El servidor no está corriendo en http://127.0.0.1:8000")
            print("Asegúrate de iniciar el servidor con: python manage.py runserver")
            return
        
        print("✅ Servidor Django funcionando correctamente")
        
        # Intenta acceder a la página de inventario
        response = requests.get(inventario_url)
        if response.status_code != 200:
            print(f"❌ No se pudo acceder a {inventario_url}")
            print(f"Código de estado: {response.status_code}")
            return
        
        print(f"✅ Página de inventario accesible")
        
        # Buscar en el contenido HTML para verificar funciones JavaScript
        content = response.text
        
        # Verificar la presencia de las funciones clave
        js_functions = [
            ('function cargarDatosFormulario()', 'Función de carga de datos del formulario'),
            ('function abrirModalCategoria()', 'Función para abrir modal de categoría'),
            ('function abrirModalUnidad()', 'Función para abrir modal de unidad'),
        ]
        
        for function_pattern, description in js_functions:
            if function_pattern in content:
                print(f"✅ {description}: ENCONTRADA")
            else:
                print(f"❌ {description}: NO ENCONTRADA")
        
        # Verificar balanceo de llaves
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        print(f"📊 Llaves abiertas: {open_braces}")
        print(f"📊 Llaves cerradas: {close_braces}")
        
        if open_braces == close_braces:
            print("✅ Llaves correctamente balanceadas")
        else:
            print(f"❌ Llaves desbalanceadas: faltan {abs(open_braces - close_braces)} llaves")
          # Verificar etiquetas de script
        script_open = content.count('<script>')
        script_close = content.count('</script>')
        
        print(f"📊 Etiquetas <script>: {script_open}")
        print(f"📊 Etiquetas </script>: {script_close}")
        
        if script_open == script_close:
            print("✅ Etiquetas de script correctamente balanceadas")
        else:
            print(f"❌ Etiquetas de script desbalanceadas")
            
        # Print the first 100 lines to see if there's any <script> tag we're missing
        print("\nPrimeras líneas del documento:")
        lines = content.split("\n")[:100]
        for i, line in enumerate(lines):
            if "<script" in line:
                print(f"Línea {i+1}: {line}")
        
        # Print the last 20 lines to see if there's any </script> tag we're missing
        print("\nÚltimas líneas del documento:")
        lines = content.split("\n")[-20:]
        for i, line in enumerate(lines):
            if "</script>" in line:
                print(f"Línea {len(content.split('\n'))-20+i+1}: {line}")
        
        print("==================================================")
        print("✅ VERIFICACIÓN COMPLETADA")
        print("Abre http://127.0.0.1:8000/dashboard/inventario/ en tu navegador")
        print("y verifica que no haya errores en la consola del navegador.")
    
    except Exception as e:
        print(f"❌ Error durante la verificación: {str(e)}")

if __name__ == "__main__":
    # Esperar a que el servidor esté listo
    print("Esperando a que el servidor Django esté listo...")
    time.sleep(3)
    test_js_errors()
