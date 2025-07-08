/**
 * Script para probar la eliminación de productos en la web
 * Usar en la consola del navegador
 */

function testProductCardSelection() {
    console.log('🔍 Iniciando diagnóstico de estructura de productos...');
    
    const deleteButtons = document.querySelectorAll('.delete-product-btn');
    console.log(`ℹ️ Se encontraron ${deleteButtons.length} botones de eliminación`);
    
    deleteButtons.forEach((button, index) => {
        const productId = button.dataset.productId;
        const productName = button.dataset.nombre;
        
        // Probar diferentes selectores para encontrar la tarjeta del producto
        const directParent = button.parentElement;
        const cardBody = button.closest('.card-body');
        const card = button.closest('.card');
        const col12 = button.closest('.col-12');
        const colAny = button.closest('[class*="col-"]');
        
        console.group(`🔎 Producto #${index + 1}: "${productName}" (ID: ${productId})`);
        console.log('Button:', button);
        console.log('Direct parent:', directParent);
        console.log('Card body:', cardBody);
        console.log('Card:', card);
        console.log('Col-12:', col12);
        console.log('Any column:', colAny);
        
        // Mostrar la ruta DOM completa
        let element = button;
        let path = [];
        while (element && element !== document.body) {
            let classes = Array.from(element.classList).join('.');
            if (classes) classes = '.' + classes;
            path.unshift(`${element.tagName.toLowerCase()}${classes}`);
            element = element.parentElement;
        }
        
        console.log('DOM Path:', path.join(' > '));
        console.groupEnd();
    });
    
    console.log('✅ Diagnóstico completado');
    return 'Script ejecutado con éxito. Revise la consola para ver los resultados.';
}

// Ejecutar diagnóstico
testProductCardSelection();
