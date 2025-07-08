#!/usr/bin/env python3
"""
Script para verificar funciones JavaScript del editor de croquis
"""
import re

def verificar_funciones_croquis():
    print("🔍 VERIFICANDO FUNCIONES JAVASCRIPT DEL CROQUIS")
    print("=" * 55)
    
    # Leer el archivo del template
    template_path = "dashboard/templates/dashboard/croquis_editor.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ No se pudo encontrar el archivo: {template_path}")
        return
    
    # Funciones que se están llamando en DOMContentLoaded
    funciones_llamadas = [
        'inicializarCanvas',
        'inicializarDragAndDrop', 
        'cargarMesasDisponibles',
        'seleccionarHerramienta',
        'cambiarPiso'
    ]
    
    # Funciones de eventos del canvas referenciadas
    funciones_eventos = [
        'onMouseDown',
        'onMouseMove', 
        'onMouseUp',
        'onWheel'
    ]
    
    # Verificar funciones llamadas
    print("\n✅ FUNCIONES LLAMADAS EN INICIALIZACIÓN:")
    for func in funciones_llamadas:
        patron = rf'function {func}\s*\('
        if re.search(patron, content):
            print(f"   ✅ {func} - DEFINIDA")
        else:
            print(f"   ❌ {func} - NO ENCONTRADA")
    
    # Verificar funciones de eventos
    print("\n✅ FUNCIONES DE EVENTOS DEL CANVAS:")
    for func in funciones_eventos:
        patron = rf'function {func}\s*\('
        if re.search(patron, content):
            print(f"   ✅ {func} - DEFINIDA")
        else:
            print(f"   ❌ {func} - NO ENCONTRADA")
    
    # Verificar variables globales
    print("\n✅ VARIABLES GLOBALES:")
    variables_importantes = ['canvas', 'ctx', 'objetos', 'mesasDisponibles']
    for var in variables_importantes:
        patron = rf'let {var}[,;]'
        if re.search(patron, content):
            print(f"   ✅ {var} - DECLARADA")
        else:
            print(f"   ❌ {var} - NO ENCONTRADA")
    
    # Verificar llamada de inicialización
    print("\n✅ INICIALIZACIÓN:")
    if "DOMContentLoaded" in content and "inicializarCanvas()" in content:
        print("   ✅ DOMContentLoaded configurado")
        print("   ✅ inicializarCanvas() llamado en DOMContentLoaded")
    else:
        print("   ❌ Problemas con la inicialización")
    
    # Verificar elemento canvas en HTML
    if 'id="croquiCanvas"' in content:
        print("   ✅ Elemento canvas con ID correcto")
    else:
        print("   ❌ Elemento canvas no encontrado")
    
    print("\n" + "=" * 55)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("\nSi todas las funciones están marcadas como ✅, el editor debería funcionar correctamente.")

if __name__ == '__main__':
    verificar_funciones_croquis()
