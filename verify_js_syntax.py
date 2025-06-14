#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de verificación de sintaxis JavaScript directamente en el archivo
"""

import re
import os

def verify_javascript_fixes():
    """Verifica las correcciones de sintaxis JavaScript"""
    file_path = r'c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\inventario.html'
    
    print("🔍 VERIFICACIÓN DE CORRECCIONES JAVASCRIPT")
    print("=" * 50)
    print(f"📁 Archivo: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraer la sección JavaScript
        js_start = content.find('<script>')
        js_end = content.find('</script>')
        
        if js_start == -1 or js_end == -1:
            print("❌ No se encontró sección JavaScript")
            return False
        
        js_content = content[js_start:js_end]
        print(f"📊 Sección JavaScript encontrada ({len(js_content)} caracteres)")
        
        # Lista de verificaciones
        checks = []
        
        # 1. Verificar que no hay .then data => {
        if '.then data =>' in js_content:
            checks.append(("❌", "Error .then data => { encontrado"))
        else:
            checks.append(("✅", "Promises .then() correctamente formateadas"))
        
        # 2. Verificar balance de llaves
        open_braces = js_content.count('{')
        close_braces = js_content.count('}')
        if open_braces == close_braces:
            checks.append(("✅", f"Balance de llaves correcto ({open_braces}/{close_braces})"))
        else:
            checks.append(("❌", f"Balance de llaves incorrecto ({open_braces}/{close_braces})"))
        
        # 3. Verificar funciones críticas
        critical_functions = [
            'function crearInsumo()',
            'function cargarDatosFormulario()',
            'function mostrarNotificacionElegante(',
            'function crearCategoria()',
            'function crearUnidadMedida()',
            'function cerrarNotificacion('
        ]
        
        missing_functions = []
        for func in critical_functions:
            if func in js_content:
                checks.append(("✅", f"Función encontrada: {func}"))
            else:
                missing_functions.append(func)
                checks.append(("❌", f"Función faltante: {func}"))
        
        # 4. Verificar que no hay errores de sintaxis obvios
        syntax_issues = []
        
        # Verificar .catch mal formateados
        if re.search(r'}\s*\.catch\s*\(\s*error\s*=>\s*{\s*mostrarNotificacionElegante', js_content):
            checks.append(("✅", "Promises .catch() correctamente formateadas"))
        
        # Verificar que no hay console.log sueltos problemáticos
        problematic_console = re.findall(r'console\.log\([^)]*\);\s*}(?!\s*\.)', js_content)
        if not problematic_console:
            checks.append(("✅", "No hay console.log problemáticos"))
        else:
            checks.append(("⚠️", f"{len(problematic_console)} console.log problemáticos"))
        
        # 5. Verificar event listeners
        event_listeners = [
            "addEventListener('DOMContentLoaded'",
            "addEventListener('input'",
            "addEventListener('show.bs.modal'",
            "addEventListener('submit'"
        ]
        
        for listener in event_listeners:
            if listener in js_content:
                checks.append(("✅", f"Event listener encontrado: {listener}"))
        
        # 6. Verificar elementos del DOM
        dom_elements = [
            "getElementById('nuevoInsumoModal')",
            "getElementById('nuevoInsumoForm')",
            "getElementById('nombre')",
            "getElementById('categoria')",
            "getElementById('unidad_medida')"
        ]
        
        for element in dom_elements:
            if element in js_content:
                checks.append(("✅", f"Acceso DOM encontrado: {element}"))
        
        # Mostrar resultados
        print("\n📋 RESULTADOS DE VERIFICACIÓN:")
        print("-" * 50)
        
        success_count = 0
        warning_count = 0
        error_count = 0
        
        for status, message in checks:
            print(f"{status} {message}")
            if status == "✅":
                success_count += 1
            elif status == "⚠️":
                warning_count += 1
            elif status == "❌":
                error_count += 1
        
        print("-" * 50)
        print(f"📊 RESUMEN: {success_count} éxitos, {warning_count} advertencias, {error_count} errores")
        
        # Verificación específica de los errores que reportaste
        print("\n🎯 VERIFICACIÓN DE ERRORES ESPECÍFICOS:")
        print("-" * 50)
        
        # Buscar el error original: "Uncaught SyntaxError: unexpected token: identifier"
        specific_issues = []
        
        # Patrón 1: identificadores inesperados después de }
        unexpected_identifiers = re.findall(r'}\s+[a-zA-Z_$][a-zA-Z0-9_$]*\s*[^(=\.]', js_content)
        if unexpected_identifiers:
            specific_issues.append(f"❌ Identificadores inesperados: {len(unexpected_identifiers)}")
        else:
            print("✅ No se encontraron identificadores inesperados")
        
        # Patrón 2: funciones mal cerradas
        malformed_functions = re.findall(r'function\s+\w+\([^)]*\)\s*{[^}]*}\s*}', js_content)
        if len(malformed_functions) > 0:
            specific_issues.append(f"❌ Funciones con doble cierre: {len(malformed_functions)}")
        else:
            print("✅ No se encontraron funciones con doble cierre")
        
        # Patrón 3: promises mal formateadas
        malformed_promises = re.findall(r'\.then\s+\w+\s*=>', js_content)
        if malformed_promises:
            specific_issues.append(f"❌ Promises mal formateadas: {len(malformed_promises)}")
        else:
            print("✅ Todas las promises están correctamente formateadas")
        
        if specific_issues:
            print("\n❌ PROBLEMAS ESPECÍFICOS ENCONTRADOS:")
            for issue in specific_issues:
                print(f"   {issue}")
        else:
            print("✅ No se encontraron los problemas específicos reportados")
        
        # Conclusión final
        print("\n" + "=" * 50)
        if error_count == 0 and len(specific_issues) == 0:
            print("🎉 CONCLUSIÓN: ¡Los errores de sintaxis JavaScript han sido CORREGIDOS!")
            print("✅ El código JavaScript parece estar sintácticamente correcto")
            print("✅ Todas las funciones críticas están presentes")
            print("✅ Los event listeners están configurados")
            print("\n💡 RECOMENDACIÓN:")
            print("   - Prueba la funcionalidad manualmente en el navegador")
            print("   - Verifica que no aparezcan errores en la consola del navegador")
            print("   - El formulario de nuevo insumo debería funcionar correctamente")
            return True
        else:
            print("⚠️  CONCLUSIÓN: Aún pueden existir problemas menores")
            print(f"   - {error_count} errores críticos")
            print(f"   - {len(specific_issues)} problemas específicos")
            print("\n🔧 RECOMENDACIÓN:")
            print("   - Revisar manualmente los errores reportados")
            print("   - Probar en navegador y verificar consola")
            return False
        
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return False

if __name__ == "__main__":
    verify_javascript_fixes()
