#!/usr/bin/env python3
"""
Verificar si hay referencias de puerto en los archivos JavaScript
"""

import os
import re

def buscar_puertos_en_archivos():
    """Buscar referencias de puertos en archivos"""
    print("=== BUSCANDO REFERENCIAS DE PUERTOS ===\n")
    
    # Buscar en templates
    template_dir = "dashboard/templates"
    
    puertos_encontrados = []
    
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Buscar patrones de puerto
                        patterns = [
                            r':8000',
                            r':8001',
                            r'127\.0\.0\.1:(\d+)',
                            r'localhost:(\d+)',
                            r'http://[^/]*:(\d+)'
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, content)
                            if matches:
                                puertos_encontrados.append({
                                    'archivo': file_path,
                                    'patron': pattern,
                                    'coincidencias': matches
                                })
                                
                except Exception as e:
                    print(f"Error leyendo {file_path}: {e}")
    
    if puertos_encontrados:
        print("🔍 REFERENCIAS DE PUERTOS ENCONTRADAS:")
        for item in puertos_encontrados:
            print(f"\nArchivo: {item['archivo']}")
            print(f"Patrón: {item['patron']}")
            print(f"Coincidencias: {item['coincidencias']}")
    else:
        print("✓ No se encontraron referencias de puertos hardcodeadas")
    
    # Verificar URLs relativas en el template principal
    print("\n=== VERIFICANDO URLS EN TEMPLATE PRINCIPAL ===")
    
    try:
        with open("dashboard/templates/dashboard/insumos_compuestos.html", 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Buscar referencias a fetch con URLs
            fetch_patterns = re.findall(r'fetch\([\'"`]([^\'"`]+)[\'"`]', content)
            if fetch_patterns:
                print("🔍 URLs en fetch() encontradas:")
                for url in fetch_patterns:
                    print(f"  - {url}")
            
            # Buscar template tags de URL
            url_patterns = re.findall(r'{%\s*url\s+[\'"]([^\'\"]+)[\'"]', content)
            if url_patterns:
                print("✓ Template tags de URL encontrados:")
                for url_tag in url_patterns:
                    print(f"  - {{% url '{url_tag}' %}}")
                    
    except Exception as e:
        print(f"Error: {e}")

def generar_solucion():
    """Generar solución para el problema de puerto"""
    print("\n=== SOLUCIÓN RECOMENDADA ===\n")
    
    print("🔧 PASOS PARA SOLUCIONAR EL ERROR DE PUERTO:")
    print("1. Asegúrate de acceder a la URL correcta:")
    print("   ✅ http://127.0.0.1:8001/dashboard/login/")
    print("   ❌ http://127.0.0.1:8000/dashboard/login/")
    print()
    print("2. Limpia la caché del navegador:")
    print("   - Ctrl+Shift+R (recarga forzada)")
    print("   - O abre en ventana privada/incógnito")
    print()
    print("3. Verifica que el servidor esté corriendo en el puerto correcto:")
    print("   - python manage.py runserver 8001")
    print()
    print("4. Si el problema persiste, verifica la consola de desarrollador:")
    print("   - F12 -> Console -> Verificar errores de red")
    print()
    
    print("🎯 CREDENCIALES PARA TESTING:")
    print("   Usuario: admin_test")
    print("   Contraseña: 123456")
    print("   URL completa: http://127.0.0.1:8001/dashboard/insumos-compuestos/")

if __name__ == '__main__':
    buscar_puertos_en_archivos()
    generar_solucion()
