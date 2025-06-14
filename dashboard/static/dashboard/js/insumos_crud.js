console.log('Archivo insumos_manager.js cargado correctamente');

/**
 * Edit an insumo via AJAX
 * @param {number} insumoId - The ID of the insumo to edit
 */
function editarInsumo(insumoId) {
    console.log('=== INICIANDO EDICION DE INSUMO ===');
    console.log('ID del insumo:', insumoId);
    
    // First get the insumo data
    fetch(`/dashboard/insumos/editar/${insumoId}/`)
        .then(response => {
            console.log('Respuesta GET recibida, status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })        .then(data => {
            console.log('Datos del insumo recibidos:', data);
            
            // Populate the form with all available data
            const fields = {
                'editInsumoId': data.id,
                'editNombre': data.nombre,
                'editCategoria': data.categoria,
                'editUnidadMedida': data.unidad_medida,
                'editStockMinimo': data.stock_minimo,
                'editPrecioUnitario': data.precio_unitario
            };
            
            // Llenar los campos del formulario
            Object.entries(fields).forEach(([fieldId, value]) => {
                const field = document.getElementById(fieldId);
                if (field) {
                    field.value = value;
                    console.log(`Campo ${fieldId} poblado con:`, value);
                } else {
                    console.warn(`Campo ${fieldId} no encontrado`);
                }
            });
              // Mostrar los nombres actuales en las etiquetas de ayuda
            const categoriaLabel = document.getElementById('editCategoriaLabel');
            if (categoriaLabel && data.categoria_nombre) {
                categoriaLabel.textContent = `Categoría actual: ${data.categoria_nombre}`;
                console.log('Categoría nombre mostrado:', data.categoria_nombre);
            }
            
            const unidadLabel = document.getElementById('editUnidadMedidaLabel');
            if (unidadLabel && data.unidad_medida_nombre) {
                unidadLabel.textContent = `Unidad actual: ${data.unidad_medida_nombre}`;
                console.log('Unidad nombre mostrado:', data.unidad_medida_nombre);
            }
            
            // Handle checkbox for perecedero
            const perecederoField = document.getElementById('editPerecedero');
            if (perecederoField) {
                perecederoField.checked = data.perecedero || false;
                console.log('Campo perecedero:', data.perecedero);
                
                // Show/hide días vencimiento based on perecedero
                const diasContainer = document.getElementById('editDiasVencimientoContainer');
                if (diasContainer) {
                    diasContainer.style.display = data.perecedero ? 'block' : 'none';
                }
                
                // Set días vencimiento if exists
                const diasField = document.getElementById('editDiasVencimiento');
                if (diasField && data.dias_vencimiento) {
                    diasField.value = data.dias_vencimiento;
                }
            }
            
            // Show the modal using Bootstrap 5
            const modalElement = document.getElementById('modalEditarInsumo');
            if (modalElement) {
                const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
                modal.show();
                console.log('✅ Modal de edición mostrado');
            } else {
                console.error('❌ Modal de edición no encontrado');
                mostrarAlerta('Error: Modal de edición no encontrado', 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error al cargar datos del insumo:', error);
            mostrarAlerta('Error al cargar los datos del insumo: ' + error.message, 'error');
        });
}

/**
 * Save edited insumo
 */
function guardarEdicionInsumo() {
    console.log('=== INICIANDO GUARDADO DE EDICION ===');
    
    const insumoId = document.getElementById('editInsumoId').value;
    console.log('ID del insumo:', insumoId);
    
    if (!insumoId) {
        console.error('ID del insumo no encontrado');
        mostrarAlerta('Error: ID del insumo no encontrado', 'error');
        return;
    }
    
    const formData = new FormData();
    
    // Collect all form data
    const campos = ['editNombre', 'editCategoria', 'editUnidadMedida', 'editStockMinimo', 'editPrecioUnitario'];
    const nombres = ['nombre', 'categoria', 'unidad_medida', 'stock_minimo', 'precio_unitario'];
    
    for (let i = 0; i < campos.length; i++) {
        const campo = document.getElementById(campos[i]);
        if (campo) {
            const valor = campo.value;
            console.log(`${nombres[i]}: ${valor}`);
            formData.append(nombres[i], valor);
        } else {
            console.error(`Campo ${campos[i]} no encontrado`);
            mostrarAlerta(`Error: Campo ${campos[i]} no encontrado`, 'error');
            return;
        }
    }
    
    // Handle perecedero checkbox
    const perecederoField = document.getElementById('editPerecedero');
    if (perecederoField) {
        const perecederoValue = perecederoField.checked;
        console.log('perecedero:', perecederoValue);
        formData.append('perecedero', perecederoValue);
        
        if (perecederoValue) {
            const diasField = document.getElementById('editDiasVencimiento');
            if (diasField && diasField.value) {
                console.log('dias_vencimiento:', diasField.value);
                formData.append('dias_vencimiento', diasField.value);
            }
        }
    }
    
    // Get CSRF token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    console.log('CSRF Token encontrado:', csrftoken ? 'SI' : 'NO');
    
    if (!csrftoken) {
        mostrarAlerta('Error: Token CSRF no encontrado', 'error');
        return;
    }
    
    // Disable the form while submitting
    const submitButton = document.getElementById('btnGuardarEdicion');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
        console.log('Botón deshabilitado');
    }
    
    const url = `/dashboard/insumos/editar/${insumoId}/`;
    console.log('URL de destino:', url);
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => {
        console.log('Respuesta recibida, status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Datos de respuesta:', data);
        
        if (data.success) {
            console.log('✅ Actualización exitosa');
            mostrarAlerta('Insumo actualizado exitosamente', 'success');
            
            // Hide the modal
            const modalElement = document.getElementById('modalEditarInsumo');
            if (modalElement) {
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                }
            }
            
            // Reload page after a short delay
            setTimeout(() => {
                console.log('Recargando página...');
                window.location.reload();
            }, 1500);
        } else {
            console.log('❌ Error en la respuesta:', data.error);
            mostrarAlerta(data.error, 'error');
        }
    })
    .catch(error => {
        console.error('❌ Error durante el fetch:', error);
        mostrarAlerta('Error al actualizar el insumo: ' + error.message, 'error');
    })
    .finally(() => {
        // Re-enable the submit button
        const submitButton = document.getElementById('btnGuardarEdicion');
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="fas fa-save me-1"></i>Guardar Cambios';
            console.log('Botón rehabilitado');
        }
        console.log('=== FIN DEL PROCESO DE GUARDADO ===');
    });
}

/**
 * Delete an insumo
 * @param {number} insumoId - The ID of the insumo to delete
 */
function eliminarInsumo(insumoId) {
    console.log('=== INICIANDO ELIMINACION DE INSUMO ===');
    console.log('ID del insumo:', insumoId);
    
    // Use SweetAlert2 for better confirmation dialog
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: '¿Estás seguro?',
            text: 'Esta acción no se puede deshacer',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                ejecutarEliminacion(insumoId);
            }
        });
    } else {
        // Fallback a confirm básico
        if (confirm('¿Estás seguro de que deseas eliminar este insumo?')) {
            ejecutarEliminacion(insumoId);
        }
    }
}

function ejecutarEliminacion(insumoId) {
    // Get CSRF token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    console.log('Enviando petición de eliminación...');
    
    fetch(`/dashboard/insumos/eliminar/${insumoId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => {
        console.log('Respuesta de eliminación, status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Datos de respuesta de eliminación:', data);
        
        if (data.success) {
            console.log('✅ Eliminación exitosa');
            mostrarAlerta('Insumo eliminado exitosamente', 'success');
            
            // Remove the row from the table
            const row = document.querySelector(`tr[data-id="${insumoId}"]`);
            if (row) {
                row.remove();
                console.log('Fila eliminada de la tabla');
            }
            
            // Reload page after a short delay
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            console.log('❌ Error en la eliminación:', data.error);
            mostrarAlerta(data.error, 'error');
        }
    })
    .catch(error => {
        console.error('❌ Error durante la eliminación:', error);
        mostrarAlerta('Error al eliminar el insumo: ' + error.message, 'error');
    });
}

/**
 * Show an alert message
 * @param {string} message - The message to show
 * @param {string} type - The type of alert (success, error, warning, info)
 */
function mostrarAlerta(message, type = 'info') {
    console.log(`Mostrando alerta: ${type} - ${message}`);
    
    // Usar SweetAlert2 si está disponible, sino usar alert básico
    if (typeof Swal !== 'undefined') {
        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true
        });
        
        Toast.fire({
            icon: type === 'error' ? 'error' : type === 'success' ? 'success' : 'info',
            title: message
        });
    } else {
        // Fallback a alert básico
        alert(message);
    }
}

// Función para script en el template
function toggleDiasVencimiento() {
    const container = document.getElementById('editDiasVencimientoContainer');
    const checkbox = document.getElementById('editPerecedero');
    const input = document.getElementById('editDiasVencimiento');
    
    if (container && checkbox) {
        container.style.display = checkbox.checked ? 'block' : 'none';
        if (!checkbox.checked && input) {
            input.value = '';
        }
    }
}

// Asegurar que las funciones estén disponibles globalmente
window.editarInsumo = editarInsumo;
window.eliminarInsumo = eliminarInsumo;
window.guardarEdicionInsumo = guardarEdicionInsumo;
window.mostrarAlerta = mostrarAlerta;
window.toggleDiasVencimiento = toggleDiasVencimiento;

console.log('Funciones de insumos definidas correctamente: editarInsumo, guardarEdicionInsumo, eliminarInsumo, mostrarAlerta');
console.log('✅ Funciones disponibles globalmente:', {
    editarInsumo: typeof window.editarInsumo,
    eliminarInsumo: typeof window.eliminarInsumo,
    guardarEdicionInsumo: typeof window.guardarEdicionInsumo,
    mostrarAlerta: typeof window.mostrarAlerta,
    toggleDiasVencimiento: typeof window.toggleDiasVencimiento
});
