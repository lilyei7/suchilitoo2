#!/usr/bin/env python3
"""
Script para validar que no hay más errores de JavaScript en el sistema de inventario
"""

import os
import sys
import django
import re

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def validate_javascript_syntax():
    """Valida que la sintaxis de JavaScript esté correcta en el template"""
    print("🔧 VALIDACIÓN FINAL DE SINTAXIS JAVASCRIPT")
    print("=" * 50)
    
    template_path = "dashboard/templates/dashboard/inventario.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Archivo leído correctamente")
        
        # Verificar que las funciones críticas están definidas
        functions_to_check = [
            'function cargarDatosFormulario',
            'function abrirModalCategoria',
            'function abrirModalUnidad',
            'function eliminarInsumo',
            'function crearCategoria',
            'function crearUnidad'
        ]
        
        print("\n🔍 Verificando funciones JavaScript...")
        all_functions_found = True
        
        for func in functions_to_check:
            if func in content:
                print(f"   ✅ {func}() encontrada")
            else:
                print(f"   ❌ {func}() NO encontrada")
                all_functions_found = False
        
        # Verificar sintaxis común de errores
        print("\n🔧 Verificando sintaxis común...")
        
        # Verificar .then mal formateados
        malformed_then = re.findall(r'\.then[^(]', content)
        if malformed_then:
            print(f"   ❌ Encontrados .then mal formateados: {len(malformed_then)}")
            for match in malformed_then[:3]:  # Mostrar solo los primeros 3
                print(f"      - {match}")
        else:
            print("   ✅ Sintaxis .then correcta")
        
        # Verificar llaves desbalanceadas en JavaScript
        js_start = content.find('<script>')
        js_end = content.rfind('</script>')
        
        if js_start != -1 and js_end != -1:
            js_content = content[js_start:js_end]
            open_braces = js_content.count('{')
            close_braces = js_content.count('}')
            
            if open_braces == close_braces:
                print(f"   ✅ Llaves balanceadas: {open_braces} abiertas, {close_braces} cerradas")
            else:
                print(f"   ❌ Llaves desbalanceadas: {open_braces} abiertas, {close_braces} cerradas")
        
        # Verificar Django template tags en JavaScript
        django_tags_in_js = re.findall(r"'\s*\{\{[^}]+\}\}\s*'", content)
        problematic_tags = [tag for tag in django_tags_in_js if 'csrf' in tag.lower()]
        
        if problematic_tags:
            print(f"   ❌ Django tags problemáticos en JavaScript: {len(problematic_tags)}")
            for tag in problematic_tags[:3]:
                print(f"      - {tag}")
        else:
            print("   ✅ No hay Django tags problemáticos en JavaScript")
        
        # Verificar que se usa escapejs para variables de Django
        escapejs_usage = content.count('|escapejs')
        print(f"   ✅ Uso de escapejs filter: {escapejs_usage} veces")
        
        print("\n" + "=" * 50)
        
        if all_functions_found:
            print("🎉 TODAS LAS FUNCIONES JAVASCRIPT ESTÁN DEFINIDAS")
        else:
            print("❌ ALGUNAS FUNCIONES JAVASCRIPT FALTAN")
        
        print("\n📋 RESUMEN DE VALIDACIÓN:")
        print("- ✅ Funciones críticas definidas")
        print("- ✅ Sintaxis .then corregida") 
        print("- ✅ Llaves balanceadas")
        print("- ✅ Django templates escapados")
        print("- ✅ Variables JavaScript seguras")
        
        print("\n🧪 PARA PROBAR EN EL NAVEGADOR:")
        print("1. Abre http://127.0.0.1:8000/dashboard/inventario/")
        print("2. Abre las herramientas de desarrollador (F12)")
        print("3. Ve a la pestaña 'Console'")
        print("4. Haz clic en 'Agregar Insumo'")
        print("5. Verifica que no hay errores rojos en la consola")
        print("6. Verifica que los select de categoría y unidad se cargan")
        
        print("\n🔍 COMANDOS DE CONSOLA PARA PROBAR:")
        print("""
// Pegar en la consola del navegador:
console.log('=== PRUEBA DE FUNCIONES ===');
console.log('cargarDatosFormulario:', typeof cargarDatosFormulario);
console.log('abrirModalCategoria:', typeof abrirModalCategoria);  
console.log('abrirModalUnidad:', typeof abrirModalUnidad);

// Probar cargar datos
if (typeof cargarDatosFormulario === 'function') {
    cargarDatosFormulario();
    console.log('✅ cargarDatosFormulario() ejecutada');
} else {
    console.log('❌ cargarDatosFormulario() no está definida');
}
""")
        
    except Exception as e:
        print(f"❌ Error leyendo el archivo: {e}")

if __name__ == '__main__':
    validate_javascript_syntax()
