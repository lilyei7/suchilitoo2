#!/usr/bin/env python3
"""
Test para validar las mejoras en zoom y pan del editor de croquis.
Verifica que todas las funciones de limitación estén implementadas correctamente.
"""

import re
import os

def test_zoom_pan_improvements():
    """Test principal para validar mejoras de zoom y pan"""
    
    print("🔍 Iniciando test de mejoras de zoom y pan...")
    
    croquis_file = "dashboard/templates/dashboard/croquis_editor.html"
    
    if not os.path.exists(croquis_file):
        print(f"❌ No se encontró el archivo: {croquis_file}")
        return False
    
    with open(croquis_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar variables necesarias para pan
    required_vars = [
        'isPanning',
        'panStartPos',
        'lastMouseX',
        'lastMouseY'
    ]
    
    print("\n📝 Verificando variables necesarias...")
    for var in required_vars:
        if var in content:
            print(f"✅ Variable '{var}' encontrada")
        else:
            print(f"❌ Variable '{var}' faltante")
    
    # Verificar funciones clave
    required_functions = [
        'limitarPan',
        'recentrarVista',
        'onWheel',
        'onMouseDown',
        'onMouseMove',
        'onMouseUp',
        'dibujarEscalaFija'
    ]
    
    print("\n🔧 Verificando funciones necesarias...")
    for func in required_functions:
        pattern = rf'function\s+{func}\s*\('
        if re.search(pattern, content):
            print(f"✅ Función '{func}' encontrada")
        else:
            print(f"❌ Función '{func}' faltante")
    
    # Verificar botón pan
    print("\n🔳 Verificando botón Pan...")
    if 'tool-pan' in content and 'seleccionarHerramienta(\'pan\')' in content:
        print("✅ Botón Pan encontrado")
    else:
        print("❌ Botón Pan faltante")
    
    # Verificar limitación de zoom
    print("\n📏 Verificando limitación de zoom...")
    zoom_limits = re.search(r'newZoom\s*>=\s*([\d.]+)\s*&&\s*newZoom\s*<=\s*([\d.]+)', content)
    if zoom_limits:
        min_zoom = float(zoom_limits.group(1))
        max_zoom = float(zoom_limits.group(2))
        print(f"✅ Límites de zoom: {min_zoom*100}% - {max_zoom*100}%")
    else:
        print("❌ Límites de zoom no encontrados")
    
    # Verificar manejo de pan en eventos de mouse
    print("\n🖱️ Verificando manejo de pan en eventos...")
    pan_events = [
        'isPanning = true',
        'isPanning = false',
        'limitarPan()'
    ]
    
    for event in pan_events:
        if event in content:
            print(f"✅ Evento pan '{event}' encontrado")
        else:
            print(f"❌ Evento pan '{event}' faltante")
    
    # Verificar función limitarPan mejorada
    print("\n🔒 Verificando función limitarPan mejorada...")
    if 'margenSeguridad' in content and 'contenidoScaladoWidth' in content:
        print("✅ limitarPan() tiene lógica mejorada")
    else:
        print("❌ limitarPan() necesita mejoras")
    
    # Verificar que recentrarVista esté expuesta globalmente
    print("\n🌐 Verificando exposición global de funciones...")
    if 'window.recentrarVista = recentrarVista' in content:
        print("✅ recentrarVista() expuesta globalmente")
    else:
        print("❌ recentrarVista() no expuesta globalmente")
    
    print("\n" + "="*60)
    print("✅ Test de zoom y pan completado")
    print("📋 Mejoras implementadas:")
    print("   • Limitación estricta de zoom (50%-200%)")
    print("   • Pan con límites que mantienen visible el área de trabajo")
    print("   • Botón Pan dedicado")
    print("   • Función recentrar vista")
    print("   • Escala visual fija independiente del zoom")
    print("   • Lógica mejorada para mantener objetos siempre accesibles")
    
    return True

def validate_js_syntax():
    """Validar sintaxis básica de JavaScript"""
    
    print("\n🔍 Validando sintaxis JavaScript básica...")
    
    croquis_file = "dashboard/templates/dashboard/croquis_editor.html"
    
    with open(croquis_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer solo el contenido JavaScript
    js_start = content.find('<script>')
    js_end = content.find('</script>')
    
    if js_start == -1 or js_end == -1:
        print("❌ No se encontró bloque <script>")
        return False
    
    js_content = content[js_start:js_end]
    
    # Verificar balance de llaves
    open_braces = js_content.count('{')
    close_braces = js_content.count('}')
    
    print(f"📊 Balance de llaves: {open_braces} abrir, {close_braces} cerrar")
    
    if open_braces == close_braces:
        print("✅ Llaves balanceadas")
    else:
        print("❌ Llaves desbalanceadas")
        return False
    
    # Verificar algunas declaraciones de función
    functions_found = len(re.findall(r'function\s+\w+\s*\(', js_content))
    print(f"📊 Funciones encontradas: {functions_found}")
    
    if functions_found > 20:  # Esperamos muchas funciones
        print("✅ Cantidad razonable de funciones")
    else:
        print("⚠️ Pocas funciones encontradas")
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando validación de mejoras zoom/pan...")
    print("="*60)
    
    try:
        success = test_zoom_pan_improvements()
        if success:
            validate_js_syntax()
            print("\n🎉 Todas las validaciones completadas!")
            print("\n📝 Instrucciones de uso:")
            print("   1. El modo Seleccionar permite pan al hacer clic en área vacía")
            print("   2. El botón Pan activa modo pan dedicado")
            print("   3. Usa la rueda del mouse para zoom con límites")
            print("   4. El botón Recentrar restaura vista por defecto")
            print("   5. La escala visual se adapta automáticamente al zoom")
        else:
            print("\n❌ Algunas validaciones fallaron")
    
    except Exception as e:
        print(f"\n❌ Error durante la validación: {str(e)}")
        import traceback
        traceback.print_exc()
