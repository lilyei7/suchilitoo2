/**
 * Este script complementa el archivo insumos_crud.js con las funciones
 * que faltan para la creación de categorías y unidades de medida.
 */

// Para crear categoría
function crearCategoria() {
    console.log('Iniciando creación de categoría...');
    
    const form = document.getElementById('nuevaCategoriaForm');
    const formData = new FormData(form);
    
    // Obtener token CSRF
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Verificar datos antes de enviar
    const nombre = formData.get('nombre');
    if (!nombre || nombre.trim() === '') {
        mostrarAlerta('El nombre de la categoría es obligatorio', 'error');
        return;
    }
    
    // Deshabilitar botón para evitar múltiples envíos
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    
    // Enviar datos al servidor
    fetch('/dashboard/categorias/crear/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la petición');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Mostrar notificación de éxito
            mostrarAlerta('Categoría creada con éxito', 'success');
            
            // Limpiar formulario
            form.reset();
            
            // Cerrar el modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('nuevaCategoriaModal'));
            if (modal) {
                modal.hide();
            }
            
            // Actualizar lista de categorías en la interfaz
            cargarDatosFormulario();
            
            // Recargar página después de un breve retraso
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            mostrarAlerta(data.error || 'Error al crear la categoría', 'error');
        }
    })
    .catch(error => {
        console.error('Error al crear categoría:', error);
        mostrarAlerta('Error al crear la categoría: ' + error.message, 'error');
    })
    .finally(() => {
        // Restaurar el botón
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    });
}

// Para crear unidad de medida
function crearUnidadMedida() {
    console.log('Iniciando creación de unidad de medida...');
    
    const form = document.getElementById('nuevaUnidadForm');
    const formData = new FormData(form);
    
    // Obtener token CSRF
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Verificar datos antes de enviar
    const nombre = formData.get('nombre');
    const abreviacion = formData.get('abreviacion');
    if (!nombre || nombre.trim() === '') {
        mostrarAlerta('El nombre de la unidad es obligatorio', 'error');
        return;
    }
    if (!abreviacion || abreviacion.trim() === '') {
        mostrarAlerta('La abreviación es obligatoria', 'error');
        return;
    }
    
    // Deshabilitar botón para evitar múltiples envíos
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    
    // Enviar datos al servidor
    fetch('/dashboard/unidades/crear/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la petición');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Mostrar notificación de éxito
            mostrarAlerta('Unidad de medida creada con éxito', 'success');
            
            // Limpiar formulario
            form.reset();
            
            // Cerrar el modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('nuevaUnidadModal'));
            if (modal) {
                modal.hide();
            }
            
            // Actualizar lista de unidades en la interfaz
            cargarDatosFormulario();
            
            // Recargar página después de un breve retraso
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            mostrarAlerta(data.error || 'Error al crear la unidad de medida', 'error');
        }
    })
    .catch(error => {
        console.error('Error al crear unidad de medida:', error);
        mostrarAlerta('Error al crear la unidad de medida: ' + error.message, 'error');
    })
    .finally(() => {
        // Restaurar el botón
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    });
}

// Función para mostrar alertas utilizando SweetAlert2
function mostrarAlerta(mensaje, tipo) {
    Swal.fire({
        title: tipo === 'success' ? '¡Éxito!' : 'Error',
        text: mensaje,
        icon: tipo,
        confirmButtonText: 'Entendido',
        confirmButtonColor: tipo === 'success' ? '#10b981' : '#ef4444'
    });
}

// Configurar eventos para los formularios cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('Configurando eventos para categorías y unidades...');
    
    // Configurar evento para formulario de categoría
    const formCategoria = document.getElementById('nuevaCategoriaForm');
    if (formCategoria) {
        formCategoria.addEventListener('submit', function(e) {
            e.preventDefault();
            crearCategoria();
        });
        console.log('✅ Evento configurado para formulario de categoría');
    } else {
        console.warn('⚠️ Formulario de categoría no encontrado');
    }
    
    // Configurar evento para formulario de unidad
    const formUnidad = document.getElementById('nuevaUnidadForm');
    if (formUnidad) {
        formUnidad.addEventListener('submit', function(e) {
            e.preventDefault();
            crearUnidadMedida();
        });
        console.log('✅ Evento configurado para formulario de unidad');
    } else {
        console.warn('⚠️ Formulario de unidad no encontrado');
    }
    
    // Cargar datos existentes
    cargarCategorias();
    cargarUnidades();
});

// Cargar categorías existentes
function cargarCategorias() {
    console.log('Cargando categorías existentes...');
    const listaCategorias = document.getElementById('listaCategorias');
    
    if (!listaCategorias) {
        console.warn('Contenedor de lista de categorías no encontrado');
        return;
    }
    
    fetch('/dashboard/categorias/listar/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la petición');
            }
            return response.json();
        })
        .then(data => {
            if (data.categorias && data.categorias.length > 0) {
                let html = '<div class="list-group">';
                data.categorias.forEach(cat => {
                    html += `
                        <div class="list-group-item d-flex justify-content-between align-items-center">
                            <div>
                                <span class="fw-medium">${cat.nombre}</span>
                                ${cat.descripcion ? `<small class="text-muted d-block">${cat.descripcion}</small>` : ''}
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                listaCategorias.innerHTML = html;
            } else {
                listaCategorias.innerHTML = '<div class="text-center text-muted">No hay categorías registradas</div>';
            }
        })
        .catch(error => {
            console.error('Error al cargar categorías:', error);
            listaCategorias.innerHTML = '<div class="text-center text-danger">Error al cargar categorías</div>';
        });
}

// Cargar unidades existentes
function cargarUnidades() {
    console.log('Cargando unidades existentes...');
    const listaUnidades = document.getElementById('listaUnidades');
    
    if (!listaUnidades) {
        console.warn('Contenedor de lista de unidades no encontrado');
        return;
    }
    
    fetch('/dashboard/unidades/listar/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la petición');
            }
            return response.json();
        })
        .then(data => {
            if (data.unidades && data.unidades.length > 0) {
                let html = '<div class="list-group">';
                data.unidades.forEach(unidad => {
                    html += `
                        <div class="list-group-item d-flex justify-content-between align-items-center">
                            <div>
                                <span class="fw-medium">${unidad.nombre}</span>
                                <small class="text-muted ms-2">(${unidad.abreviacion})</small>
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                listaUnidades.innerHTML = html;
            } else {
                listaUnidades.innerHTML = '<div class="text-center text-muted">No hay unidades registradas</div>';
            }
        })
        .catch(error => {
            console.error('Error al cargar unidades:', error);
            listaUnidades.innerHTML = '<div class="text-center text-danger">Error al cargar unidades</div>';
        });
}
