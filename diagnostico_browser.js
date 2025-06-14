// Script de diagnóstico para la consola del navegador
// Ejecutar en la página de proveedores con F12 abierto

console.clear();
console.log("🧪 DIAGNÓSTICO DE ERRORES JAVASCRIPT");

// Función para probar un endpoint
async function testEndpoint(url, options = {}) {
    console.log(`\n🔍 Probando: ${url}`);
    console.log(`   Options:`, options);
    
    try {
        const response = await fetch(url, options);
        console.log(`   ✅ Status: ${response.status}`);
        console.log(`   ✅ Content-Type: ${response.headers.get('content-type')}`);
        
        const text = await response.text();
        console.log(`   📄 Response length: ${text.length} chars`);
        console.log(`   📄 First 100 chars: ${text.substring(0, 100)}`);
        
        if (response.headers.get('content-type')?.includes('application/json')) {
            try {
                const json = JSON.parse(text);
                console.log(`   ✅ Valid JSON`);
                console.log(`   📊 Data:`, json);
                return json;
            } catch (e) {
                console.log(`   ❌ Invalid JSON: ${e.message}`);
                return null;
            }
        } else {
            console.log(`   ⚠️ Not JSON response`);
            return null;
        }
    } catch (error) {
        console.log(`   ❌ Fetch error: ${error.message}`);
        return null;
    }
}

// Obtener ID de un proveedor de la página actual
function getProveedorId() {
    const button = document.querySelector('[onclick*="verDetalleProveedor"]');
    if (button) {
        const match = button.getAttribute('onclick').match(/verDetalleProveedor\((\d+)\)/);
        return match ? match[1] : null;
    }
    return null;
}

// Ejecutar diagnóstico
async function runDiagnostic() {
    const proveedorId = getProveedorId();
    if (!proveedorId) {
        console.log("❌ No se encontró ID de proveedor en la página");
        return;
    }
    
    console.log(`📌 Usando proveedor ID: ${proveedorId}`);
    
    // Test 1: Sin headers (como estaba antes)
    await testEndpoint(`/dashboard/proveedor/${proveedorId}/detalle/`);
    
    // Test 2: Con headers (como debería ser)
    await testEndpoint(`/dashboard/proveedor/${proveedorId}/detalle/`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    });
    
    // Test 3: Editar
    await testEndpoint(`/dashboard/proveedor/${proveedorId}/editar/`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    });
    
    // Test 4: Eliminar (GET)
    await testEndpoint(`/dashboard/proveedor/${proveedorId}/eliminar/`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    });
    
    console.log("\n✅ Diagnóstico completado");
}

// Ejecutar
runDiagnostic();
