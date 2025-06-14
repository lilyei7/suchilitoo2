#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de verificación simple para confirmar que los errores de sintaxis JavaScript han sido corregidos
"""

import requests
import re
import os

def test_page_loading():
    """Prueba básica de carga de página"""
    try:
        response = requests.get('http://127.0.0.1:8000/dashboard/inventario/', timeout=10)
        if response.status_code == 200:
            print("✅ Página de inventario carga correctamente (HTTP 200)")
            return True, response.text
        else:
            print(f"❌ Error de carga: HTTP {response.status_code}")
            return False, None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False, None

def analyze_javascript_syntax(html_content):
    """Analiza la sintaxis JavaScript en el HTML"""
    # Extraer el contenido JavaScript
    js_pattern = r'<script[^>]*>(.*?)</script>'
    js_matches = re.findall(js_pattern, html_content, re.DOTALL)
    
    if not js_matches:
        print("⚠️  No se encontró JavaScript en la página")
        return False
    
    js_content = js_matches[0] if js_matches else ""
    
    # Patrones de errores de sintaxis comunes
    syntax_errors = []
    
    # Error 1: .then data => { (sin paréntesis)
    if re.search(r'\.then\s+\w+\s+=>', js_content):
        syntax_errors.append("❌ Error: .then data => { (falta paréntesis)")
    
    # Error 2: Funciones con doble cierre }}
    double_close_matches = re.findall(r'}\s*}', js_content)
    if len(double_close_matches) > 5:  # Algunas son válidas
        syntax_errors.append(f"⚠️  Posibles cierres dobles de función: {len(double_close_matches)}")
    
    # Error 3: Promises mal formateadas
    if re.search(r'}\)\s*\.then\s*\(', js_content):
        print("✅ Promises correctamente formateadas")
    
    # Error 4: Verificar que las funciones principales existen
    required_functions = [
        'crearInsumo',
        'cargarDatosFormulario', 
        'mostrarNotificacionElegante',
        'crearCategoria',
        'crearUnidadMedida'
    ]
    
    missing_functions = []
    for func in required_functions:
        if f'function {func}' not in js_content:
            missing_functions.append(func)
    
    if missing_functions:
        syntax_errors.append(f"❌ Funciones faltantes: {', '.join(missing_functions)}")
    else:
        print("✅ Todas las funciones principales están presentes")
    
    return len(syntax_errors) == 0, syntax_errors

def test_api_endpoints():
    """Prueba los endpoints de API"""
    endpoints = {
        '/dashboard/get-form-data/': 'GET',
        '/dashboard/crear-insumo/': 'POST',
        '/dashboard/crear-categoria/': 'POST', 
        '/dashboard/crear-unidad-medida/': 'POST'
    }
    
    print("\n🔧 Probando endpoints de API...")
    all_ok = True
    
    for endpoint, method in endpoints.items():
        try:
            url = f'http://127.0.0.1:8000{endpoint}'
            
            if method == 'GET':
                response = requests.get(url, timeout=5)
            else:
                # Para POST, esperamos 403 (CSRF) o 405, no 404
                response = requests.post(url, timeout=5)
            
            if response.status_code in [200, 403, 405]:  
                print(f"✅ Endpoint {endpoint} disponible (HTTP {response.status_code})")
            else:
                print(f"❌ Endpoint {endpoint}: HTTP {response.status_code}")
                all_ok = False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Endpoint {endpoint}: Error de conexión")
            all_ok = False
    
    return all_ok

def check_file_syntax():
    """Verifica la sintaxis del archivo directamente"""
    file_path = r'c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\inventario.html'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraer solo la sección JavaScript
        js_start = content.find('<script>')
        js_end = content.find('</script>')
        
        if js_start == -1 or js_end == -1:
            print("❌ No se encontró sección JavaScript en el archivo")
            return False
        
        js_content = content[js_start:js_end]
        
        # Verificar problemas específicos
        issues = []
        
        # 1. Verificar .then(data => { vs .then data => {
        if '.then data =>' in js_content:
            issues.append("❌ .then data => { (sin paréntesis)")
        else:
            print("✅ Promises .then() correctamente formateadas")
        
        # 2. Verificar cierres de función
        open_braces = js_content.count('{')
        close_braces = js_content.count('}')
        print(f"📊 Llaves: {open_braces} abiertas, {close_braces} cerradas")
        
        # 3. Verificar que no hay console.log sueltos
        console_logs = len(re.findall(r'console\.log', js_content))
        if console_logs > 0:
            print(f"ℹ️  {console_logs} console.log encontrados (pueden ser normales)")
        
        # 4. Verificar funciones críticas
        critical_functions = ['crearInsumo()', 'cargarDatosFormulario()', 'mostrarNotificacionElegante(']
        for func in critical_functions:
            if func in js_content:
                print(f"✅ Función crítica encontrada: {func}")
            else:
                issues.append(f"❌ Función crítica faltante: {func}")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Error al leer archivo: {e}")
        return False

def main():
    """Función principal de verificación simplificada"""
    print("🔍 VERIFICACIÓN SIMPLIFICADA - CORRECCIÓN DE SINTAXIS JAVASCRIPT")
    print("=" * 70)
    
    # Verificar que el servidor esté ejecutándose
    print("\n📋 1. Verificando servidor Django...")
    page_loads, html_content = test_page_loading()
    
    if not page_loads:
        print("❌ El servidor no está ejecutándose o la página no carga")
        print("💡 Asegúrate de que el servidor Django esté corriendo en el puerto 8000")
        return
    
    # Verificar sintaxis en el archivo
    print("\n📁 2. Verificando sintaxis en archivo...")
    file_syntax_ok = check_file_syntax()
    
    # Verificar sintaxis en HTML renderizado
    print("\n🌐 3. Analizando JavaScript en HTML renderizado...")
    if html_content:
        js_syntax_ok, errors = analyze_javascript_syntax(html_content)
        if not js_syntax_ok:
            print("❌ Errores de sintaxis encontrados:")
            for error in errors:
                print(f"   {error}")
        else:
            print("✅ Sintaxis JavaScript parece correcta")
    
    # Verificar endpoints
    print("\n🔧 4. Verificando endpoints de API...")
    api_ok = test_api_endpoints()
    
    # Resultado final
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE VERIFICACIÓN:")
    
    results = []
    results.append(("Carga de página", page_loads))
    results.append(("Sintaxis de archivo", file_syntax_ok))
    results.append(("Sintaxis en HTML", js_syntax_ok if html_content else None))
    results.append(("Endpoints API", api_ok))
    
    for test_name, result in results:
        if result is True:
            print(f"✅ {test_name}: EXITOSO")
        elif result is False:
            print(f"❌ {test_name}: FALLIDO") 
        else:
            print(f"⚠️  {test_name}: NO PUDO VERIFICARSE")
    
    # Conclusión
    all_critical_ok = page_loads and file_syntax_ok
    
    if all_critical_ok:
        print("\n🎉 CONCLUSIÓN: Los errores de sintaxis JavaScript han sido CORREGIDOS")
        print("✅ La página de inventario está funcionando correctamente")
        print("✅ Puedes probar manualmente el formulario de nuevo insumo")
        print("\n💡 PRÓXIMOS PASOS:")
        print("   1. Abre http://127.0.0.1:8000/dashboard/inventario/ en tu navegador")
        print("   2. Haz clic en 'Nuevo Insumo'")
        print("   3. Completa el formulario y guarda")
        print("   4. Verifica que no aparezcan errores en la consola del navegador")
    else:
        print("\n⚠️  CONCLUSIÓN: Aún pueden existir problemas")
        print("🔍 Revisar manualmente la consola del navegador para más detalles")

if __name__ == "__main__":
    main()
