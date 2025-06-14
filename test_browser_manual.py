#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para crear un test directo que puedes ejecutar en la consola del navegador
"""

def create_browser_test():
    """Crear test para ejecutar en la consola del navegador"""
    
    test_js = """
// TEST DIRECTO DE CARGA DE CATEGORÍAS Y UNIDADES
// Ejecuta este código en la consola del navegador en la página de inventario

console.log('🚀 Iniciando test de carga de categorías y unidades...');

// 1. Verificar que los elementos existen
const categoriaSelect = document.getElementById('categoria');
const unidadSelect = document.getElementById('unidad_medida');
const modal = document.getElementById('nuevoInsumoModal');

console.log('📋 Verificando elementos del DOM:');
console.log('✅ Select categoría:', categoriaSelect ? 'Encontrado' : '❌ NO encontrado');
console.log('✅ Select unidad:', unidadSelect ? 'Encontrado' : '❌ NO encontrado');
console.log('✅ Modal:', modal ? 'Encontrado' : '❌ NO encontrado');

// 2. Verificar función cargarDatosFormulario
if (typeof cargarDatosFormulario === 'function') {
    console.log('✅ Función cargarDatosFormulario: Encontrada');
    
    // 3. Probar la función directamente
    console.log('🔄 Ejecutando cargarDatosFormulario...');
    cargarDatosFormulario();
    
    // 4. Verificar resultados después de un breve delay
    setTimeout(() => {
        console.log('📊 Verificando resultados:');
        
        if (categoriaSelect) {
            console.log(`📦 Opciones en categoría: ${categoriaSelect.options.length}`);
            if (categoriaSelect.options.length > 1) {
                console.log('✅ Categorías cargadas correctamente');
                for (let i = 1; i < Math.min(4, categoriaSelect.options.length); i++) {
                    console.log(`   • ${categoriaSelect.options[i].text}`);
                }
            } else {
                console.log('❌ No se cargaron categorías');
            }
        }
        
        if (unidadSelect) {
            console.log(`📏 Opciones en unidad: ${unidadSelect.options.length}`);
            if (unidadSelect.options.length > 1) {
                console.log('✅ Unidades cargadas correctamente');
                for (let i = 1; i < Math.min(4, unidadSelect.options.length); i++) {
                    console.log(`   • ${unidadSelect.options[i].text}`);
                }
            } else {
                console.log('❌ No se cargaron unidades');
            }
        }
        
        console.log('🎯 Test completado. Si ves opciones arriba, todo funciona correctamente.');
    }, 2000);
    
} else {
    console.log('❌ Función cargarDatosFormulario: NO encontrada');
}

// 5. Test adicional: probar endpoint directamente
console.log('🌐 Probando endpoint directamente...');
fetch('/dashboard/insumos/form-data/')
    .then(response => {
        console.log('📊 Status del endpoint:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('✅ Datos del endpoint:', data);
        console.log(`📦 Categorías en endpoint: ${data.categorias?.length || 0}`);
        console.log(`📏 Unidades en endpoint: ${data.unidades?.length || 0}`);
    })
    .catch(error => {
        console.log('❌ Error en endpoint:', error);
    });
"""
    
    print("🌐 TEST DIRECTO PARA CONSOLA DEL NAVEGADOR")
    print("=" * 50)
    print("\n📋 INSTRUCCIONES:")
    print("1. Abre http://127.0.0.1:8000/dashboard/inventario/ en tu navegador")
    print("2. Haz login con admin/admin123")
    print("3. Haz clic en 'NUEVO INSUMO' para abrir el modal")
    print("4. Abre las herramientas de desarrollador (F12)")
    print("5. Ve a la pestaña 'Console'")
    print("6. Copia y pega el siguiente código:")
    print("\n" + "=" * 50)
    print(test_js)
    print("=" * 50)
    print("\n💡 RESULTADOS ESPERADOS:")
    print("   ✅ Elementos del DOM encontrados")
    print("   ✅ Función cargarDatosFormulario encontrada")
    print("   ✅ Categorías y unidades cargadas en los selects")
    print("   ✅ Endpoint devuelve datos JSON válidos")

def create_manual_verification_steps():
    """Crear pasos de verificación manual"""
    
    print("\n📝 VERIFICACIÓN MANUAL PASO A PASO")
    print("=" * 50)
    
    steps = [
        "1. 🌐 Abre http://127.0.0.1:8000/dashboard/inventario/",
        "2. 🔐 Haz login con admin/admin123",
        "3. ✅ Verifica que aparezca 'NUEVO INSUMO' (botón verde)",
        "4. 🖱️  Haz clic en el botón 'NUEVO INSUMO'",
        "5. 👁️  Verifica que se abra el modal",
        "6. 📋 Busca el campo 'Categoría' (select dropdown)",
        "7. 🔍 Haz clic en el select de categoría",
        "8. ✅ Verifica que aparezcan opciones (Proteínas, Vegetales, etc.)",
        "9. 📋 Busca el campo 'Unidad de Medida' (select dropdown)",
        "10. 🔍 Haz clic en el select de unidad de medida",
        "11. ✅ Verifica que aparezcan opciones (Kilogramo, Litro, etc.)",
        "12. 🎯 Si ambos selects tienen opciones: ¡ÉXITO COMPLETO!"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print("\n🚨 SI LOS SELECTS ESTÁN VACÍOS:")
    print("   • Abre F12 → Console")
    print("   • Busca errores en rojo")
    print("   • Ejecuta el test JavaScript de arriba")

def main():
    """Función principal"""
    print("🔧 HERRAMIENTAS DE DIAGNÓSTICO PARA SELECTS")
    print("=" * 60)
    
    create_browser_test()
    create_manual_verification_steps()
    
    print("\n" + "=" * 60)
    print("📌 RESUMEN:")
    print("✅ Se han corregido los errores de sintaxis JavaScript")
    print("✅ Se han creado categorías y unidades en la base de datos")
    print("✅ El endpoint get_form_data está configurado")
    print("✅ La función cargarDatosFormulario está implementada")
    print("\n💡 AHORA PROCEDE CON LA VERIFICACIÓN MANUAL")

if __name__ == "__main__":
    main()
