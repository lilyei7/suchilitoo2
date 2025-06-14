#!/usr/bin/env python3
"""
Script para añadir automáticamente las llaves de cierre faltantes
"""

import re

def fix_missing_braces():
    """Añade las llaves de cierre faltantes"""
    
    template_path = "dashboard/templates/dashboard/inventario.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔧 AÑADIENDO LLAVES DE CIERRE FALTANTES...")
        print("=" * 50)
        
        # Patrones de funciones que sabemos que necesitan cierre
        functions_needing_closure = [
            'function crearInsumo() {',
            'function cerrarNotificacion(notification) {',
            'function agregarStock(insumoId) {',
            'function reducirStock(insumoId) {',
            'function crearCategoria() {',
            'function crearUnidadMedida() {',
            'function mostrarTip(mensaje, duracion = 7000) {',
            'function ocultarCargando() {',
            'function cargarCategorias() {',
            'function cargarUnidades() {',
            'function configurarFormularioCategoria() {',
            'function configurarFormularioUnidad() {'
        ]
        
        # Añadir llaves de cierre antes del final del script
        script_end_pattern = r'(\}\);\s*</script>\s*{%\s*endblock\s*%})'
        
        # Contar cuántas llaves faltan
        js_start = content.find('<script>')
        js_end = content.find('</script>')
        
        if js_start != -1 and js_end != -1:
            js_content = content[js_start:js_end]
            open_braces = js_content.count('{')
            close_braces = js_content.count('}')
            missing_braces = open_braces - close_braces
            
            print(f"📊 Llaves abiertas: {open_braces}")
            print(f"📊 Llaves cerradas: {close_braces}")
            print(f"📊 Faltan: {missing_braces} llaves de cierre")
            
            if missing_braces > 0:
                # Añadir las llaves faltantes antes del cierre del script
                closing_braces = '\n' + '}\n' * missing_braces
                
                # Buscar el patrón de cierre y añadir las llaves antes
                replacement = closing_braces + r'\1'
                new_content = re.sub(script_end_pattern, replacement, content)
                
                # Escribir el archivo corregido
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ Añadidas {missing_braces} llaves de cierre")
                print("✅ Archivo guardado")
                
                return True
            else:
                print("✅ No se necesitan correcciones")
                return False
        else:
            print("❌ No se encontró sección de JavaScript")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = fix_missing_braces()
    if success:
        print("\n🎉 CORRECCIÓN COMPLETADA")
        print("Ejecuta el servidor y prueba la página de inventario")
    else:
        print("\n⚠️  No se pudo completar la corrección")
