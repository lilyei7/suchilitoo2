// Función de utilidad para manejar respuestas AJAX de forma segura
function handleAjaxResponse(response) {
    // Primero verificamos el estado de la respuesta
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    // Obtenemos la respuesta como texto primero
    return response.text().then(text => {
        // Nos aseguramos de tener texto válido antes de intentar parsearlo
        if (!text || text.trim() === '') {
            throw new Error('Respuesta vacía del servidor');
        }
        
        // Intentamos parsear como JSON
        try {
            return JSON.parse(text);
        } catch (e) {
            console.error('Error al parsear JSON:', e);
            console.error('Respuesta cruda:', text);
            throw new Error(`Error al parsear la respuesta: ${e.message}`);
        }
    });
}

// Sobrescribimos window.verDetalleProveedor para usar la nueva función de utilidad
window.verDetalleProveedor = function(proveedorId) {
    console.log('Ver detalles del proveedor:', proveedorId);
    const modal = new bootstrap.Modal(document.getElementById('detalleProveedorModal'));
    const content = document.getElementById('detalleProveedorContent');
    
    // Mostrar loading
    content.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="mt-2 text-muted">Cargando información del proveedor...</p>
        </div>
    `;
    
    modal.show();
    
    // Cargar datos del proveedor
    fetch(`/dashboard/proveedor/${proveedorId}/detalle/`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(handleAjaxResponse)
    .then(data => {
        if (data.success) {
            // Guardar referencia global al proveedor actual
            window.proveedorActual = data.proveedor;
            
            // Mostrar detalles (HTML o datos JSON)
            if (data.html) {
                content.innerHTML = data.html;
            } else {
                // Función personalizada para mostrar datos
                mostrarDetalleProveedor(data.proveedor, data.insumos);
            }
        } else {
            content.innerHTML = `
                <div class="alert alert-danger mx-3">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error: ${data.message || 'No se pudieron cargar los detalles del proveedor'}
                </div>
            `;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        content.innerHTML = `
            <div class="alert alert-danger mx-3">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error de conexión: ${error.message}. Intenta nuevamente.
            </div>
        `;
    });
};
