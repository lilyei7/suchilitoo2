#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test final específico para verificar que los selects de categorías y unidades funcionen
"""

def create_browser_test_script():
    """Crear script de test para ejecutar en el navegador"""
    
    test_script = """
// ===== TEST COMPLETO DE SELECTS =====
console.log('🚀 Iniciando test completo de selects...');

// 1. Verificar elementos del DOM
const categoriaSelect = document.getElementById('categoria');
const unidadSelect = document.getElementById('unidad_medida');
const nuevoInsumoBtn = document.querySelector('[data-bs-target="#nuevoInsumoModal"]');
const modal = document.getElementById('nuevoInsumoModal');

console.log('📋 Verificación de elementos:');
console.log('✅ Select categoría:', categoriaSelect ? 'ENCONTRADO' : '❌ NO ENCONTRADO');
console.log('✅ Select unidad:', unidadSelect ? 'ENCONTRADO' : '❌ NO ENCONTRADO');
console.log('✅ Botón nuevo insumo:', nuevoInsumoBtn ? 'ENCONTRADO' : '❌ NO ENCONTRADO');
console.log('✅ Modal:', modal ? 'ENCONTRADO' : '❌ NO ENCONTRADO');

// 2. Verificar funciones JavaScript
const functionsToCheck = [
    'cargarDatosFormulario',
    'abrirModalCategoria', 
    'abrirModalUnidad',
    'cargarCategorias',
    'cargarUnidades',
    'crearInsumo'
];

console.log('\\n🔧 Verificación de funciones:');
functionsToCheck.forEach(funcName => {
    const exists = typeof window[funcName] === 'function';
    console.log(`${exists ? '✅' : '❌'} ${funcName}:`, exists ? 'DEFINIDA' : 'NO DEFINIDA');
});

// 3. Test del endpoint directamente
console.log('\\n🌐 Probando endpoint de datos...');
fetch('/dashboard/insumos/form-data/')
    .then(response => {
        console.log('📊 Status del endpoint:', response.status);
        if (response.ok) {
            return response.json();
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    })
    .then(data => {
        console.log('✅ Datos recibidos del endpoint:');
        console.log(`📦 Categorías: ${data.categorias?.length || 0}`);
        console.log(`📏 Unidades: ${data.unidades?.length || 0}`);
        
        if (data.categorias && data.categorias.length > 0) {
            console.log('✅ Ejemplos de categorías:');
            data.categorias.slice(0, 3).forEach(cat => {
                console.log(`   • ${cat.nombre} (ID: ${cat.id})`);
            });
        }
        
        if (data.unidades && data.unidades.length > 0) {
            console.log('✅ Ejemplos de unidades:');
            data.unidades.slice(0, 3).forEach(unidad => {
                console.log(`   • ${unidad.nombre} (${unidad.abreviacion}) (ID: ${unidad.id})`);
            });
        }
    })
    .catch(error => {
        console.log('❌ Error en endpoint:', error);
    });

// 4. Test de carga en los selects
if (typeof cargarDatosFormulario === 'function') {
    console.log('\\n🔄 Ejecutando cargarDatosFormulario...');
    cargarDatosFormulario();
    
    // Verificar después de 3 segundos
    setTimeout(() => {
        console.log('\\n📊 Verificando selects después de la carga:');
        
        if (categoriaSelect) {
            const catOptions = categoriaSelect.options.length - 1; // -1 por la opción placeholder
            console.log(`📦 Opciones en select categoría: ${catOptions}`);
            
            if (catOptions > 0) {
                console.log('✅ ¡Categorías cargadas exitosamente!');
                for (let i = 1; i <= Math.min(3, catOptions); i++) {
                    console.log(`   • ${categoriaSelect.options[i].text}`);
                }
            } else {
                console.log('❌ No se cargaron categorías en el select');
            }
        }
        
        if (unidadSelect) {
            const unidadOptions = unidadSelect.options.length - 1; // -1 por la opción placeholder
            console.log(`📏 Opciones en select unidad: ${unidadOptions}`);
            
            if (unidadOptions > 0) {
                console.log('✅ ¡Unidades cargadas exitosamente!');
                for (let i = 1; i <= Math.min(3, unidadOptions); i++) {
                    console.log(`   • ${unidadSelect.options[i].text}`);
                }
            } else {
                console.log('❌ No se cargaron unidades en el select');
            }
        }
        
        // Resultado final
        const categoriasOk = categoriaSelect && categoriaSelect.options.length > 1;
        const unidadesOk = unidadSelect && unidadSelect.options.length > 1;
        
        console.log('\\n🎯 RESULTADO FINAL:');
        if (categoriasOk && unidadesOk) {
            console.log('🎉 ¡ÉXITO COMPLETO! Los selects funcionan correctamente');
            console.log('✅ Categorías: CARGADAS');
            console.log('✅ Unidades: CARGADAS');
            console.log('💡 Ahora puedes crear insumos sin problemas');
        } else {
            console.log('⚠️ PROBLEMAS DETECTADOS:');
            if (!categoriasOk) console.log('❌ Categorías no se cargan');
            if (!unidadesOk) console.log('❌ Unidades no se cargan');
            console.log('🔍 Revisar errores en la consola del navegador');
        }
        
    }, 3000);
} else {
    console.log('❌ La función cargarDatosFormulario no está disponible');
}

console.log('\\n📝 Para ver todos los resultados, espera 3 segundos...');
"""
    
    return test_script

def main():
    """Función principal"""
    print("🔍 TEST FINAL DE FUNCIONALIDAD DE SELECTS")
    print("=" * 60)
    
    # Generar script de test
    test_script = create_browser_test_script()
    
    print("📋 INSTRUCCIONES PARA VERIFICAR:")
    print("1. 🌐 Abre http://127.0.0.1:8000/dashboard/inventario/")
    print("2. 🔐 Haz login con admin/admin123") 
    print("3. 🖱️  Haz clic en 'NUEVO INSUMO' (botón verde)")
    print("4. 🛠️  Abre DevTools (F12) → pestaña Console")
    print("5. 📋 Copia y pega el siguiente código:")
    
    print("\n" + "=" * 60)
    print("// CÓDIGO PARA EJECUTAR EN LA CONSOLA DEL NAVEGADOR")
    print(test_script)
    print("=" * 60)
    
    print("\n💡 RESULTADOS ESPERADOS:")
    print("✅ Todos los elementos del DOM encontrados")
    print("✅ Todas las funciones JavaScript definidas")
    print("✅ Endpoint devuelve datos correctos")
    print("✅ Selects se llenan con opciones")
    print("✅ Mensaje final: '¡ÉXITO COMPLETO!'")
    
    print("\n🎯 VERIFICACIÓN VISUAL:")
    print("• El select 'Categoría' debe tener opciones como:")
    print("  - Proteínas")
    print("  - Vegetales") 
    print("  - Lácteos")
    print("  - etc.")
    
    print("\n• El select 'Unidad de Medida' debe tener opciones como:")
    print("  - Kilogramo (kg)")
    print("  - Litro (L)")
    print("  - Unidad (und)")
    print("  - etc.")
    
    print(f"\n🔧 Si hay problemas:")
    print("• Revisar errores en rojo en la consola")
    print("• Verificar que el servidor Django esté corriendo")
    print("• Asegurar que estás logueado correctamente")

if __name__ == "__main__":
    main()
