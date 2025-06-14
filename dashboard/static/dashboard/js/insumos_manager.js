/**
 * Insumos Manager - Functions for handling the creation and management of insumos
 * This is a dedicated file for cleaner organization of insumo-related functionality
 */

// Variable global para control de creación
let creandoInsumo = false;

/**
 * Create an insumo (ingredient) via AJAX
 * @returns {void}
 */
function crearInsumo() {
    console.log("Iniciando función crearInsumo()");
    // Verificar si ya se está procesando una petición
    if (creandoInsumo) {
        console.log("Ya se está procesando una petición, se ignora esta llamada");
        return;
    }
    
    // Marcar como procesando
    creandoInsumo = true;
    console.log("Estado creandoInsumo cambiado a:", creandoInsumo);
    
    const form = document.getElementById('nuevoInsumoForm');
    if (!form) {
        alert('Error: No se encontró el formulario');
        console.error("No se encontró el formulario con ID nuevoInsumoForm");
        
        // Rehabilitar botón (aunque no debería estar habilitado aún en este punto)
        const btnGuardar = document.getElementById('btnGuardarInsumo');
        if (btnGuardar) {
            btnGuardar.disabled = false;
            btnGuardar.innerHTML = '<i class="fas fa-save me-1"></i>Guardar Insumo';
        }
        
        creandoInsumo = false; // Liberar variable de control
        return;
    }
    
    const formData = new FormData(form);
    
    // Validar campos obligatorios
    const nombre = formData.get('nombre');
    const categoria = formData.get('categoria');
    const unidad_medida = formData.get('unidad_medida');
    
    console.log("Datos del formulario:", {
        nombre,
        categoria,
        unidad_medida
    });
    
    // Validación de datos del formulario
    if (!nombre || !categoria || !unidad_medida) {
        // Campos obligatorios faltantes
        console.warn("Faltan campos obligatorios", { nombre, categoria, unidad_medida });
        
        mostrarNotificacionElegante(
            'Campos Incompletos',
            'Por favor completa todos los campos obligatorios: Nombre, Categoría y Unidad de Medida.',
            'warning'
        );
        
        // Rehabilitar botón
        const btnGuardar = document.getElementById('btnGuardarInsumo');
        if (btnGuardar) {
            btnGuardar.disabled = false;
            btnGuardar.innerHTML = '<i class="fas fa-save me-1"></i>Guardar Insumo';
        }
        
        creandoInsumo = false; // Liberar variable de control
        return;
    }
    
    // Forzar tipo a "basico" ya que este formulario es solo para insumos básicos
    formData.set('tipo', 'basico');
    
    // Generar código si no existe
    if (!formData.get('codigo') || formData.get('codigo').trim() === '') {
        const timestamp = Date.now().toString().slice(-3);
        const codigo = nombre.toUpperCase().replace(/\s+/g, '').substring(0, 6) + timestamp;
        formData.set('codigo', codigo);
        console.log("Código generado automáticamente:", codigo);
    }
    
    // Verificar CSRF token
    let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    
    // Si no está en el DOM, intentar obtenerlo de las cookies
    if (!csrfToken) {
        console.log("CSRF token no encontrado en el DOM, buscando en cookies...");
        
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        
        const csrfCookie = getCookie('csrftoken');
        if (csrfCookie) {
            console.log("CSRF token encontrado en cookies:", csrfCookie.substring(0, 5) + "...");
            
            // Crear un objeto para simular el input con el token
            csrfToken = {value: csrfCookie};
            
            // También agregar el token a los datos del formulario
            formData.append('csrfmiddlewaretoken', csrfCookie);
        }
    } else {
        console.log("CSRF token encontrado en el DOM:", csrfToken.value.substring(0, 5) + "...");
    }
    
    if (!csrfToken) {
        alert('Error: Token de seguridad no encontrado');
        console.error("No se pudo obtener el CSRF token ni del DOM ni de las cookies");
        
        // Rehabilitar botón
        const btnGuardar = document.getElementById('btnGuardarInsumo');
        if (btnGuardar) {
            btnGuardar.disabled = false;
            btnGuardar.innerHTML = '<i class="fas fa-save me-1"></i>Guardar Insumo';
        }
        
        creandoInsumo = false; // Liberar variable de control
        return;
    }
    
    // Debug para verificar los datos que se están enviando
    console.log("Datos del formulario que se enviarán:");
    for (let [key, value] of formData.entries()) {
        console.log(`${key}: ${value}`);
    }
    
    // URL del endpoint
    const url = '/dashboard/insumos/crear/';
    console.log("URL para crear insumo:", url);
    
    // Deshabilitar botón durante el proceso
    const btnGuardar = document.getElementById('btnGuardarInsumo');
    if (btnGuardar) {
        btnGuardar.disabled = true;
        btnGuardar.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Guardando...';
    }
    
    // Mostrar notificación de carga
    mostrarCargando('Guardando insumo en el sistema...');
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken.value,
            'X-Requested-With': 'XMLHttpRequest' // Agregar el header para identificar solicitudes AJAX
        },
        credentials: 'same-origin' // Asegurar que las cookies se envían con la solicitud
    })
    .then(response => {
        console.log("Respuesta del servidor:", response.status, response.statusText);
        if (!response.ok) {
            if (response.status === 403) {
                throw new Error(`Error de permisos! CSRF token inválido o faltante`);
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json().catch(error => {
            console.error("Error al parsear JSON:", error);
            throw new Error("Error en el formato de la respuesta del servidor");
        });
    })
    .then(data => {
        console.log("Datos recibidos del servidor:", data);
        // Ocultar notificación de carga
        ocultarCargando();
        
        if (data.success) {
            // Mostrar notificación elegante principal
            mostrarNotificacionElegante(
                '¡Insumo Creado!', 
                `El insumo "${formData.get('nombre')}" se ha guardado exitosamente en el sistema.`,
                'success'
            );
            
            // Limpiar formulario
            form.reset();
            
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('nuevoInsumoModal'));
            if (modal) {
                modal.hide();
            }
            
            // Liberar variable de control
            creandoInsumo = false;
            
            // Esperar un momento y luego recargar para mostrar los cambios
            console.log("Esperando 500ms antes de recargar la página...");
            setTimeout(() => {
                console.log("Recargando página...");
                window.location.href = '/dashboard/inventario/';
            }, 500);
        } else {
            // Ocultar notificación de carga
            ocultarCargando();
            
            // Rehabilitar botón
            if (btnGuardar) {
                btnGuardar.disabled = false;
                btnGuardar.innerHTML = '<i class="fas fa-save me-1"></i>Guardar Insumo';
            }
            
            // Liberar variable de control
            creandoInsumo = false;
            
            mostrarNotificacionElegante(
                'Error al Guardar',
                data.error || 'No se pudo guardar el insumo. Intenta nuevamente.',
                'error'
            );
        }
    })
    .catch(error => {
        console.error("Error en la petición:", error);
        
        // Ocultar notificación de carga
        ocultarCargando();
        
        // Rehabilitar botón
        if (btnGuardar) {
            btnGuardar.disabled = false;
            btnGuardar.innerHTML = '<i class="fas fa-save me-1"></i>Guardar Insumo';
        }
        
        // Liberar variable de control
        creandoInsumo = false;
        
        mostrarNotificacionElegante(
            'Error de Conexión',
            'No se pudo conectar con el servidor. Verifica tu conexión e intenta nuevamente.',
            'error'
        );
    });
}

/**
 * Edit an insumo via AJAX
 * @param {number} insumoId - The ID of the insumo to edit
 */
function editarInsumo(insumoId) {
    // First get the insumo data
    fetch(`/dashboard/insumos/editar/${insumoId}/`)
        .then(response => response.json())
        .then(data => {
            // Populate the form with all available data
            document.getElementById('editInsumoId').value = data.id;
            document.getElementById('editNombre').value = data.nombre;
            document.getElementById('editCategoria').value = data.categoria;
            document.getElementById('editUnidadMedida').value = data.unidad_medida;
            document.getElementById('editStockMinimo').value = data.stock_minimo;
            document.getElementById('editPrecioUnitario').value = data.precio_unitario;
            document.getElementById('editPerecedero').checked = data.perecedero;
            
            // Handle optional fields
            if (document.getElementById('editDiasVencimiento')) {
                document.getElementById('editDiasVencimiento').value = data.dias_vencimiento || '';
                // Show/hide días vencimiento based on perecedero
                document.getElementById('editDiasVencimientoContainer').style.display = 
                    data.perecedero ? 'block' : 'none';
            }
            
            // Update any display labels
            const categoriaLabel = document.getElementById('editCategoriaLabel');
            if (categoriaLabel) {
                categoriaLabel.textContent = data.categoria_nombre;
            }
            
            const unidadMedidaLabel = document.getElementById('editUnidadMedidaLabel');
            if (unidadMedidaLabel) {
                unidadMedidaLabel.textContent = data.unidad_medida_nombre;
            }
              // Show the modal using Bootstrap 5
            const modalElement = document.getElementById('modalEditarInsumo');
            const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
            modal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('Error al cargar los datos del insumo', 'error');
        });
}

/**
 * Save edited insumo
 */
function guardarEdicionInsumo() {
    const insumoId = document.getElementById('editInsumoId').value;
    const formData = new FormData();
    
    // Collect all form data
    formData.append('nombre', document.getElementById('editNombre').value);
    formData.append('categoria', document.getElementById('editCategoria').value);
    formData.append('unidad_medida', document.getElementById('editUnidadMedida').value);
    formData.append('stock_minimo', document.getElementById('editStockMinimo').value);
    formData.append('precio_unitario', document.getElementById('editPrecioUnitario').value);
    formData.append('perecedero', document.getElementById('editPerecedero').checked);
    
    if (document.getElementById('editPerecedero').checked) {
        formData.append('dias_vencimiento', document.getElementById('editDiasVencimiento').value);
    }
      // Get CSRF token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      // Disable the form while submitting
    const submitButton = document.getElementById('btnGuardarEdicion');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    }
    
    fetch(`/dashboard/insumos/editar/${insumoId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {            // Update the row in the table without reloading
            actualizarFilaInsumo(data.insumo);
            mostrarAlerta('Insumo actualizado exitosamente', 'success');
            
            // Hide the modal
            const modalElement = document.getElementById('modalEditarInsumo');
            const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
            modal.hide();
        } else {
            mostrarAlerta(data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarAlerta('Error al actualizar el insumo', 'error');
    })    .finally(() => {
        // Re-enable the submit button
        const submitButton = document.getElementById('btnGuardarEdicion');
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="fas fa-save me-1"></i>Guardar Cambios';
        }
    });
}

/**
 * Delete an insumo
 * @param {number} insumoId - The ID of the insumo to delete
 */
function eliminarInsumo(insumoId) {
    // Use SweetAlert2 for better confirmation dialog
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
            // Get CSRF token
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch(`/dashboard/insumos/eliminar/${insumoId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove the row from the table without reloading
                    const row = document.querySelector(`tr[data-id="${insumoId}"]`);
                    if (row) {
                        row.remove();
                    }
                    mostrarAlerta('Insumo eliminado exitosamente', 'success');
                } else {
                    mostrarAlerta(data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarAlerta('Error al eliminar el insumo', 'error');
            });
        }
    });
}

/**
 * Update a table row with new insumo data
 * @param {Object} insumo - The updated insumo data
 */
function actualizarFilaInsumo(insumo) {
    const row = document.querySelector(`tr[data-id="${insumo.id}"]`);
    if (!row) return;
    
    // Update the nombre column
    const nombreCell = row.querySelector('td:nth-child(2)');
    if (nombreCell) {
        nombreCell.querySelector('h6').textContent = insumo.nombre;
    }
    
    // Update categoría
    const categoriaCell = row.querySelector('td:nth-child(7)');
    if (categoriaCell) {
        categoriaCell.textContent = insumo.categoria_nombre;
    }
    
    // Update stock mínimo
    const stockMinimoCell = row.querySelector('td:nth-child(5)');
    if (stockMinimoCell) {
        stockMinimoCell.textContent = insumo.stock_minimo;
    }
    
    // Update precio
    const precioCell = row.querySelector('td:nth-child(8)');
    if (precioCell) {
        precioCell.textContent = `$${insumo.precio_unitario.toFixed(2)}`;
    }
}

/**
 * Show an alert message
 * @param {string} message - The message to show
 * @param {string} type - The type of alert (success, error, warning, info)
 */
function mostrarAlerta(message, type = 'info') {
    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true    });
    
    Toast.fire({
        icon: type,
        title: message
    });
}

/**
 * Setup event listeners for insumo form and buttons
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log("Iniciando configuración de eventos para insumos_manager.js");
    
    // Configurar el botón para guardar insumo
    const btnGuardarInsumo = document.getElementById('btnGuardarInsumo');
    if (btnGuardarInsumo) {
        console.log("Botón de guardar insumo encontrado, configurando evento click");
        btnGuardarInsumo.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("Botón Guardar Insumo clickeado");
            crearInsumo();
        });
    } else {
        console.error("No se encontró el botón btnGuardarInsumo");
    }

    // Prevenir el envío directo del formulario
    const nuevoInsumoForm = document.getElementById('nuevoInsumoForm');
    if (nuevoInsumoForm) {
        console.log("Formulario de nuevo insumo encontrado, configurando evento submit");
        nuevoInsumoForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log("Formulario de nuevo insumo enviado");
            crearInsumo();
        });
    } else {
        console.error("No se encontró el formulario nuevoInsumoForm");
    }
    
    console.log("Configuración de eventos completada en insumos_manager.js");
});

// Función auxiliar para mostrar notificación de carga
function mostrarCargando(mensaje) {
    // Si ya existe una notificación de carga, la removemos
    const existingLoading = document.querySelector('.loading-overlay');
    if (existingLoading) {
        existingLoading.remove();
    }
    
    // Crear overlay de carga
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 9999; display: flex; justify-content: center; align-items: center;';
    
    const loadingBox = document.createElement('div');
    loadingBox.style.cssText = 'background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); text-align: center; max-width: 300px;';
    
    const spinner = document.createElement('div');
    spinner.className = 'spinner-border text-primary mb-3';
    spinner.setAttribute('role', 'status');
    
    const spinnerText = document.createElement('span');
    spinnerText.className = 'visually-hidden';
    spinnerText.textContent = 'Cargando...';
    
    const loadingText = document.createElement('p');
    loadingText.className = 'mb-0';
    loadingText.textContent = mensaje || 'Procesando...';
    
    spinner.appendChild(spinnerText);
    loadingBox.appendChild(spinner);
    loadingBox.appendChild(loadingText);
    overlay.appendChild(loadingBox);
    document.body.appendChild(overlay);
    
    return overlay;
}

// Función auxiliar para ocultar notificación de carga
function ocultarCargando() {
    const existingLoading = document.querySelector('.loading-overlay');
    if (existingLoading) {
        existingLoading.remove();
    }
}

// Función auxiliar para mostrar notificaciones elegantes
function mostrarNotificacionElegante(titulo, mensaje, tipo) {
    const icono = tipo === 'success' ? 'check-circle' 
               : tipo === 'warning' ? 'exclamation-triangle'
               : tipo === 'info' ? 'info-circle'
               : 'times-circle';
    
    const colorClase = tipo === 'success' ? 'bg-success'
                    : tipo === 'warning' ? 'bg-warning'
                    : tipo === 'info' ? 'bg-info'
                    : 'bg-danger';
    
    // Crea la notificación
    const toast = document.createElement('div');
    toast.className = `toast ${colorClase} text-white`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.innerHTML = `
        <div class="toast-header ${colorClase} text-white">
            <i class="fas fa-${icono} me-2"></i>
            <strong class="me-auto">${titulo}</strong>
            <small>Ahora</small>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${mensaje}
        </div>
    `;
    
    // Asegurarse de que exista el contenedor de toasts
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Agregar la notificación al contenedor
    toastContainer.appendChild(toast);
    
    // Inicializar y mostrar la notificación
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 5000
    });
    bsToast.show();
    
    // Eliminar la notificación después de ocultarse
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}
