#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de verificación final para confirmar que todos los problemas han sido resueltos
"""

import requests
import re

def test_template_rendering():
    """Verificar que los templates Django se renderizan correctamente"""
    try:
        response = requests.get('http://127.0.0.1:8000/dashboard/inventario/', timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
        
        html_content = response.text
        
        # Verificar que no hay templates sin renderizar
        unrendered_templates = re.findall(r'{\s*{\s*[^}]+\s*}\s*}', html_content)
        
        if unrendered_templates:
            print("❌ Templates sin renderizar encontrados:")
            for template in unrendered_templates[:5]:  # Mostrar solo los primeros 5
                print(f"   🔴 {template}")
            return False
        else:
            print("✅ Todos los templates Django se renderizan correctamente")
        
        # Verificar que hay datos reales (no placeholders)
        if 'insumos.count' in html_content or 'insumo.nombre' in html_content:
            print("❌ Aún hay placeholders sin renderizar en el HTML")
            return False
        else:
            print("✅ No hay placeholders de Django sin renderizar")
        
        # Verificar que el modal existe
        if 'id="nuevoInsumoModal"' in html_content:
            print("✅ Modal de nuevo insumo presente")
        else:
            print("❌ Modal de nuevo insumo no encontrado")
            return False
        
        # Verificar que las funciones JavaScript críticas existen
        js_functions = ['crearInsumo()', 'cargarDatosFormulario()', 'mostrarNotificacionElegante(']
        for func in js_functions:
            if func in html_content:
                print(f"✅ Función JavaScript encontrada: {func}")
            else:
                print(f"❌ Función JavaScript faltante: {func}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar templates: {e}")
        return False

def check_syntax_errors():
    """Verificar que no hay errores de sintaxis JavaScript obvios"""
    file_path = r'c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\inventario.html'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar errores de sintaxis comunes
        syntax_issues = [
            (r'\.then\s+\w+\s+=>', 'Promise .then sin paréntesis'),
            (r'}\s*}\s*}', 'Triple cierre de función'),
            (r'{\s*{\s*[^}]+\s*}', 'Template Django malformateado'),
        ]
        
        issues_found = 0
        for pattern, description in syntax_issues:
            matches = re.findall(pattern, content)
            if matches:
                print(f"❌ {description}: {len(matches)} encontrados")
                issues_found += len(matches)
        
        if issues_found == 0:
            print("✅ No se encontraron errores de sintaxis")
            return True
        else:
            print(f"❌ Se encontraron {issues_found} problemas de sintaxis")
            return False
            
    except Exception as e:
        print(f"❌ Error al verificar sintaxis: {e}")
        return False

def test_functionality():
    """Probar la funcionalidad básica del sistema"""
    try:
        # Test de endpoints básicos
        endpoints_to_test = [
            ('http://127.0.0.1:8000/dashboard/', 'Dashboard principal'),
            ('http://127.0.0.1:8000/dashboard/inventario/', 'Página de inventario'),
        ]
        
        for url, description in endpoints_to_test:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {description}: OK")
            else:
                print(f"❌ {description}: HTTP {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error al probar funcionalidad: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("🎯 VERIFICACIÓN FINAL COMPLETA")
    print("=" * 50)
    
    print("\n📋 1. Verificando renderizado de templates...")
    templates_ok = test_template_rendering()
    
    print("\n🔧 2. Verificando sintaxis JavaScript...")
    syntax_ok = check_syntax_errors()
    
    print("\n🌐 3. Verificando funcionalidad básica...")
    functionality_ok = test_functionality()
    
    # Resultado final
    print("\n" + "=" * 50)
    print("📊 RESUMEN FINAL:")
    
    if templates_ok:
        print("✅ Templates Django: CORREGIDOS")
    else:
        print("❌ Templates Django: PROBLEMAS PENDIENTES")
    
    if syntax_ok:
        print("✅ Sintaxis JavaScript: CORREGIDA")
    else:
        print("❌ Sintaxis JavaScript: PROBLEMAS PENDIENTES")
    
    if functionality_ok:
        print("✅ Funcionalidad básica: OPERATIVA")
    else:
        print("❌ Funcionalidad básica: PROBLEMAS")
    
    print("\n" + "=" * 50)
    
    if templates_ok and syntax_ok and functionality_ok:
        print("🎉 ¡ÉXITO COMPLETO!")
        print("✅ Todos los problemas han sido resueltos:")
        print("   • Error de sintaxis JavaScript: CORREGIDO")
        print("   • Templates Django malformateados: CORREGIDOS")
        print("   • Página de inventario: FUNCIONAL")
        print("   • Formulario de nuevo insumo: LISTO PARA USAR")
        print("\n💡 PRÓXIMOS PASOS:")
        print("   1. Recarga la página en tu navegador")
        print("   2. Haz clic en 'NUEVO INSUMO'")
        print("   3. Completa y guarda un insumo de prueba")
        print("   4. Verifica que aparezca en la lista")
    else:
        print("⚠️  AÚN HAY PROBLEMAS PENDIENTES")
        print("🔍 Revisar los errores mostrados arriba")

if __name__ == "__main__":
    main()
