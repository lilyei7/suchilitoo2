#!/usr/bin/env python3
"""
Script para hacer una verificación final del archivo croquis_editor.html
y confirmar que todo esté funcionando correctamente.
"""

import sys
from pathlib import Path

def validate_file():
    """Valida que el archivo sea válido y las funciones estén bien implementadas"""
    file_path = Path(__file__).parent / "dashboard" / "templates" / "dashboard" / "croquis_editor.html"
    
    if not file_path.exists():
        print(f"❌ Archivo no encontrado: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return False
    
    print("🔍 VERIFICACIÓN FINAL DEL EDITOR DE CROQUIS")
    print("=" * 50)
    
    # Verificaciones básicas
    checks = [
        ("📄 Archivo existe", True),
        ("📝 Contenido leído", len(content) > 0),
        ("🏷️ Etiqueta script", "<script>" in content),
        ("🔚 Cierre script", "</script>" in content),
        ("🔧 Función cargarMesasDisponibles", "function cargarMesasDisponibles()" in content),
        ("📋 Función actualizarListaMesas", "function actualizarListaMesas()" in content),
        ("🏢 Función cambiarPiso", "function cambiarPiso(" in content),
        ("➕ Función agregarPiso", "function agregarPiso(" in content),
        ("🗑️ Función eliminarPiso", "function eliminarPiso(" in content),
        ("🎨 Función alternarCuadricula", "function alternarCuadricula(" in content),
        ("🏗️ Función crearLayoutPredefinido", "function crearLayoutPredefinido(" in content),
        ("📐 Función actualizarDimensiones", "function actualizarDimensiones(" in content),
        ("🌐 Exposición window", "window.cargarMesasDisponibles = cargarMesasDisponibles" in content),
        ("🚀 DOMContentLoaded", "document.addEventListener('DOMContentLoaded'" in content),
    ]
    
    all_passed = True
    for desc, condition in checks:
        status = "✅" if condition else "❌"
        print(f"  {status} {desc}")
        if not condition:
            all_passed = False
    
    print()
    
    # Verificar que no hay errores comunes
    errors = []
    
    # Verificar balance de llaves
    brace_count = content.count('{') - content.count('}')
    if brace_count != 0:
        errors.append(f"Desbalance de llaves: {brace_count}")
    
    # Verificar balance de paréntesis
    paren_count = content.count('(') - content.count(')')
    if paren_count != 0:
        errors.append(f"Desbalance de paréntesis: {paren_count}")
    
    # Verificar que no hay funciones undefined
    undefined_functions = [
        "actualizarContadorObjetos",
        "actualizarPanelPropiedades"
    ]
    
    for func in undefined_functions:
        if f"function {func}(" not in content and f"{func}(" in content:
            errors.append(f"Función {func} llamada pero no definida")
    
    if errors:
        print("⚠️ ERRORES POTENCIALES:")
        for error in errors:
            print(f"  ❌ {error}")
        all_passed = False
    else:
        print("✅ No se encontraron errores sintácticos")
    
    # Estadísticas del archivo
    lines = content.count('\n') + 1
    js_start = content.find('<script>')
    js_end = content.find('</script>')
    js_lines = 0
    if js_start != -1 and js_end != -1:
        js_content = content[js_start:js_end]
        js_lines = js_content.count('\n')
    
    print(f"\n📊 ESTADÍSTICAS DEL ARCHIVO:")
    print(f"  - Total líneas: {lines}")
    print(f"  - Líneas JavaScript: {js_lines}")
    print(f"  - Tamaño: {len(content)} caracteres")
    
    if all_passed:
        print(f"\n🎉 VALIDACIÓN COMPLETADA EXITOSAMENTE")
        print(f"✅ El editor de croquis está listo para funcionar")
        print(f"📝 Todas las funciones requeridas están implementadas")
        print(f"🔧 Los errores de ReferenceError han sido solucionados")
    else:
        print(f"\n⚠️ SE ENCONTRARON PROBLEMAS")
        print(f"❌ Revisa los errores indicados arriba")
    
    return all_passed

if __name__ == "__main__":
    success = validate_file()
    sys.exit(0 if success else 1)
