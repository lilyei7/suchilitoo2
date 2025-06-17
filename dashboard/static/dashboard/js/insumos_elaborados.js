// Funciones principales para insumos elaborados
let contadorComponentesElaborado = 0;
let insumosDisponibles = []; // Lista de insumos disponibles para usar en elaborados
let contadorComponentesEdicion = 0;

// FUNCIONES PARA CREAR INSUMOS ELABORADOS
// -----------------------------------------------

// Abrir modal para crear insumo elaborado
function abrirModalCrearElaborado() {
    contadorComponentesElaborado = 0;
    const container = document.getElementById('componentesElaboradoContainer');
    if (container) {
        container.innerHTML = '';
    }
    
    const form = document.getElementById('formCrearElaborado');
    if (form) {
        form.reset();
    }
    
    // Cargar datos iniciales
    cargarCategorias();
    cargarUnidades();
    cargarInsumosDisponibles();
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalCrearElaborado'));
    modal.show();
}

// Cargar insumos disponibles (básicos + compuestos)
function cargarInsumosDisponibles() {
    fetch('/dashboard/insumos-elaborados/insumos-disponibles/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            insumosDisponibles = data.insumos;
            console.log(`✅ Insumos cargados: ${data.total_basicos} básicos, ${data.total_compuestos} compuestos`);
        } else {
            console.error('❌ Error al cargar insumos:', data.message);
            showToast('Error al cargar insumos: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('❌ Error de conexión:', error);
        showToast('Error de conexión al cargar insumos', 'error');
    });
}

// FUNCIONES PARA VER DETALLES
// -----------------------------------------------

// Ver detalles de un insumo elaborado
function verDetalleElaborado(insumoId) {
    console.log(`🔍 Viendo detalle de insumo ID: ${insumoId}`);
    
    // Mostrar modal con spinner mientras carga
    const modal = new bootstrap.Modal(document.getElementById('modalDetalleElaborado'));
    const content = document.getElementById('detalleElaboradoContent');
    
    content.innerHTML = `
        <div class="d-flex justify-content-center my-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
        </div>
    `;
    
    modal.show();
    
    // Cargar datos del insumo
    fetch(`/dashboard/insumos-elaborados/detalle/${insumoId}/`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarDetalleElaborado(data.insumo, data.componentes);
        } else {
            content.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
            console.error("Error cargando datos:", data.message);
        }
    })
    .catch(error => {
        content.innerHTML = `<div class="alert alert-danger">Error de conexión. Intente nuevamente.</div>`;
        console.error("Error de conexión:", error);
    });
}

// Mostrar detalles del insumo elaborado en el modal
function mostrarDetalleElaborado(insumo, componentes) {
    const content = document.getElementById('detalleElaboradoContent');
    
    // Crear contenido HTML para el detalle
    let componentesHTML = '';
    let costoTotal = 0;
    
    componentes.forEach(componente => {
        costoTotal += componente.costo_total;
        componentesHTML += `
            <div class="componente-item border rounded p-3 mb-3">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="mb-0">${componente.nombre}</h6>
                    <span class="badge bg-info">${componente.tipo}</span>
                </div>
                <div class="row g-2">
                    <div class="col-md-4">
                        <small class="text-muted d-block">Cantidad:</small>
                        <strong>${componente.cantidad} ${componente.unidad_medida}</strong>
                    </div>
                    <div class="col-md-4">
                        <small class="text-muted d-block">Precio unitario:</small>
                        <strong>$${componente.precio_unitario.toFixed(2)}</strong>
                    </div>
                    <div class="col-md-4">
                        <small class="text-muted d-block">Costo total:</small>
                        <strong>$${componente.costo_total.toFixed(2)}</strong>
                    </div>
                    <div class="col-12">
                        <small class="text-muted d-block">Instrucciones:</small>
                        <p class="mb-0 small">${componente.notas || 'Sin instrucciones'}</p>
                    </div>
                </div>
            </div>
        `;
    });
    
    if (componentesHTML === '') {
        componentesHTML = '<div class="alert alert-info">Este insumo elaborado no tiene componentes registrados.</div>';
    }
    
    // Montar la estructura completa
    content.innerHTML = `
        <div class="row g-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-light">
                        <h6 class="mb-0"><i class="fas fa-info-circle me-2"></i>Información Básica</h6>
                    </div>
                    <div class="card-body">
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item d-flex justify-content-between">
                                <span class="text-muted">Código:</span>
                                <span class="fw-medium">${insumo.codigo}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between">
                                <span class="text-muted">Nombre:</span>
                                <span class="fw-medium">${insumo.nombre}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between">
                                <span class="text-muted">Categoría:</span>
                                <span class="fw-medium">${insumo.categoria}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between">
                                <span class="text-muted">Unidad de medida:</span>
                                <span class="fw-medium">${insumo.unidad_medida}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between">
                                <span class="text-muted">Cantidad producida:</span>
                                <span class="fw-medium">${insumo.cantidad_producida}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between">
                                <span class="text-muted">Tiempo preparación:</span>
                                <span class="fw-medium">${insumo.tiempo_preparacion} min</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between">
                                <span class="text-muted">Precio unitario:</span>
                                <span class="fw-medium text-success">$${insumo.precio_unitario.toFixed(2)}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between">
                                <span class="text-muted">Costo total:</span>
                                <span class="fw-medium text-primary">$${insumo.total_costo.toFixed(2)}</span>
                            </li>
                        </ul>
                        
                        <div class="mt-3">
                            <h6 class="mb-2">Descripción:</h6>
                            <p class="mb-0">${insumo.descripcion || 'Sin descripción'}</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-light">
                        <h6 class="mb-0"><i class="fas fa-puzzle-piece me-2"></i>Componentes (${componentes.length})</h6>
                    </div>
                    <div class="card-body">
                        ${componentesHTML}
                    </div>
                </div>
            </div>
        </div>
    `;
}

// FUNCIONES PARA EDITAR INSUMOS ELABORADOS
// -----------------------------------------------

// Editar insumo elaborado
function editarInsumoElaborado(insumoId) {
    console.log(`🔄 Cargando datos para editar insumo ID: ${insumoId}`);
    
    const modal = new bootstrap.Modal(document.getElementById('modalEditarElaborado'));
    const content = document.getElementById('editarElaboradoContent');
    
    content.innerHTML = `
        <div class="d-flex justify-content-center my-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
        </div>
    `;
    
    modal.show();
    
    fetch(`/dashboard/insumos-elaborados/editar/${insumoId}/`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            cargarFormularioEdicion(data.insumo, data.componentes);
        } else {
            content.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
            console.error("Error cargando datos:", data.message);
        }
    })
    .catch(error => {
        content.innerHTML = `<div class="alert alert-danger">Error de conexión. Intente nuevamente.</div>`;
        console.error("Error de conexión:", error);
    });
}

// Cargar formulario de edición
function cargarFormularioEdicion(insumo, componentes) {
    console.log(`📝 Cargando formulario de edición para: ${insumo.nombre}`, insumo);
    
    const content = document.getElementById('editarElaboradoContent');
    
    // Crear el HTML del formulario
    content.innerHTML = `
        <form id="formEditarElaborado" data-insumo-id="${insumo.id}">
            <input type="hidden" name="csrfmiddlewaretoken" value="${document.querySelector('[name=csrfmiddlewaretoken]').value}">
            
            <div class="row g-4">
                <!-- Información básica -->
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header bg-light">
                            <h6 class="mb-0"><i class="fas fa-info-circle me-2"></i>Información Básica</h6>
                        </div>
                        <div class="card-body">
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <label class="form-label">Código</label>
                                    <input type="text" class="form-control" readonly value="${insumo.codigo || ''}">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Nombre <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" name="nombre" required value="${insumo.nombre || ''}">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Categoría <span class="text-danger">*</span></label>
                                    <select class="form-select" name="categoria_id" id="editCategoriaSelect" required>
                                        <option value="">Cargando...</option>
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Unidad de medida <span class="text-danger">*</span></label>
                                    <select class="form-select" name="unidad_medida_id" id="editUnidadSelect" required>
                                        <option value="">Cargando...</option>
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Cantidad producida <span class="text-danger">*</span></label>
                                    <input type="number" class="form-control" name="cantidad_producida" min="0.01" step="0.01" 
                                           required value="${insumo.cantidad_producida || 1}" onchange="actualizarResumenEdicion()">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Tiempo preparación (min)</label>
                                    <input type="number" class="form-control" name="tiempo_preparacion" min="0"
                                           value="${insumo.tiempo_preparacion || 0}" onchange="actualizarResumenEdicion()">
                                </div>
                                <div class="col-12">
                                    <label class="form-label">Descripción</label>
                                    <textarea class="form-control" name="descripcion" rows="3">${insumo.descripcion || ''}</textarea>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Componentes -->
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header bg-light d-flex justify-content-between align-items-center">
                            <h6 class="mb-0"><i class="fas fa-puzzle-piece me-2"></i>Componentes</h6>
                            <button type="button" class="btn btn-sm btn-primary" onclick="agregarComponenteEdicion()">
                                <i class="fas fa-plus me-1"></i>Agregar
                            </button>
                        </div>
                        <div class="card-body">
                            <div id="componentesEdicionContainer">
                                <!-- Componentes cargados dinámicamente -->
                                <div class="alert alert-info" id="alertNoComponentesEdicion">
                                    <i class="fas fa-info-circle me-2"></i>
                                    Agregue al menos un componente para este insumo elaborado
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Resumen -->
                <div class="col-12">
                    <div class="card">
                        <div class="card-header bg-light">
                            <h6 class="mb-0"><i class="fas fa-calculator me-2"></i>Resumen</h6>
                        </div>
                        <div class="card-body">
                            <div class="row text-center">
                                <div class="col-md-3">
                                    <div class="metric">
                                        <div class="metric-value" id="costoTotalEdicion">$0.00</div>
                                        <div class="metric-label">Costo Total</div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="metric">
                                        <div class="metric-value" id="precioUnitarioEdicion">$0.00</div>
                                        <div class="metric-label">Precio Unitario</div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="metric">
                                        <div class="metric-value" id="totalComponentesEdicion">0</div>
                                        <div class="metric-label">Componentes</div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="metric">
                                        <div class="metric-value" id="tiempoTotalEdicion">0 min</div>
                                        <div class="metric-label">Tiempo Total</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                    <i class="fas fa-times me-2"></i>Cancelar
                </button>
                <button type="submit" class="btn btn-success">
                    <i class="fas fa-save me-2"></i>Guardar Cambios
                </button>
            </div>
        </form>
    `;
    
    // Cargar categorías y unidades
    cargarCategoriasEdicion(insumo.categoria_id);
    cargarUnidadesEdicion(insumo.unidad_medida_id);
    
    // Cargar insumos disponibles y luego cargar componentes
    cargarInsumosParaEdicion().then(() => {
        console.log(`✅ Insumos cargados, procediendo a cargar ${componentes.length} componentes`);
        cargarComponentesEdicion(componentes);
    });
    
    // Configurar el formulario de edición
    configurarFormularioEdicion();
}

// Configurar event listener del formulario de edición
function configurarFormularioEdicion() {
    console.log('🔄 Configurando formulario de edición...');
    
    const form = document.getElementById('formEditarElaborado');
    if (!form) {
        console.error('❌ No se encontró el formulario de edición');
        return;
    }
    
    // Eliminar listeners previos si existen para evitar duplicados
    const newForm = form.cloneNode(true);
    form.parentNode.replaceChild(newForm, form);
    
    // Configurar nuevo event listener
    newForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        console.log('🔄 Enviando formulario de edición...');
        
        // Validar que haya al menos un componente
        const componentes = document.querySelectorAll('#componentesEdicionContainer .componente-item');
        if (componentes.length === 0) {
            showToast('Debe agregar al menos un componente para este insumo elaborado', 'error');
            return false;
        }
        
        // Obtener ID del insumo
        const insumoId = this.dataset.insumoId;
        if (!insumoId) {
            console.error('❌ No se encontró el ID del insumo a editar');
            showToast('Error al identificar el insumo. Por favor, intente nuevamente', 'error');
            return false;
        }
        
        // Deshabilitar botón de submit para prevenir doble envío
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Guardando...`;
        
        // Crear objeto FormData con los datos del formulario
        const formData = new FormData(this);
        
        // Realizar la petición para actualizar el insumo
        fetch(`/dashboard/insumos-elaborados/editar/${insumoId}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Mostrar mensaje de éxito
                showToast(data.message || 'Insumo elaborado actualizado correctamente', 'success');
                
                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalEditarElaborado'));
                modal.hide();
                
                // Recargar tabla o página
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                // Mostrar mensaje de error
                showToast(data.message || 'Error al actualizar el insumo elaborado', 'error');
                console.error('❌ Error al actualizar:', data.message);
            }
        })
        .catch(error => {
            console.error('❌ Error en la petición:', error);
            showToast('Error al comunicarse con el servidor. Por favor, intente nuevamente', 'error');
        })
        .finally(() => {
            // Restaurar botón de submit
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        });
    });
    
    console.log('✅ Formulario de edición configurado correctamente');
}

// Actualizar resumen de edición
function actualizarResumenEdicion() {
    console.log('🔄 Actualizando resumen de edición...');
    
    // Obtener elementos del resumen
    const costoTotalElement = document.getElementById('costoTotalEdicion');
    const precioUnitarioElement = document.getElementById('precioUnitarioEdicion');
    const totalComponentesElement = document.getElementById('totalComponentesEdicion');
    const tiempoTotalElement = document.getElementById('tiempoTotalEdicion');
    
    if (!costoTotalElement || !precioUnitarioElement || !totalComponentesElement || !tiempoTotalElement) {
        console.error('❌ No se encontraron todos los elementos del resumen');
        return;
    }
    
    // Obtener componentes
    const componentes = document.querySelectorAll('#componentesEdicionContainer .componente-item');
    let costoTotal = 0;
    let tiempoTotal = 0;
    
    // Calcular costo total sumando el costo de cada componente
    componentes.forEach(componente => {
        // Extraer costo del componente
        const costoInput = componente.querySelector('input[id^="costoComponenteEdicion"]');
        if (costoInput) {
            const costoTexto = costoInput.value.replace('$', '').trim();
            const costo = parseFloat(costoTexto) || 0;
            costoTotal += costo;
        }
        
        // Extraer tiempo del componente
        const tiempoInput = componente.querySelector('input[name="componente_tiempo[]"]');
        if (tiempoInput) {
            const tiempo = parseFloat(tiempoInput.value) || 0;
            tiempoTotal += tiempo;
        }
    });
    
    // Obtener cantidad producida
    const cantidadProducidaInput = document.querySelector('input[name="cantidad_producida"]');
    const cantidadProducida = cantidadProducidaInput ? parseFloat(cantidadProducidaInput.value) || 1 : 1;
    
    // Calcular precio unitario
    const precioUnitario = cantidadProducida > 0 ? costoTotal / cantidadProducida : 0;
    
    // Actualizar elementos del resumen
    costoTotalElement.textContent = `$${costoTotal.toFixed(2)}`;
    precioUnitarioElement.textContent = `$${precioUnitario.toFixed(2)}`;
    totalComponentesElement.textContent = componentes.length;
    
    // Actualizar tiempo total (sumar tiempo de componentes + tiempo de preparación)
    const tiempoPreparacionInput = document.querySelector('input[name="tiempo_preparacion"]');
    const tiempoPreparacion = tiempoPreparacionInput ? parseFloat(tiempoPreparacionInput.value) || 0 : 0;
    tiempoTotal += tiempoPreparacion;
    
    tiempoTotalElement.textContent = `${tiempoTotal} min`;
    
    console.log(`💰 Resumen actualizado: $${costoTotal.toFixed(2)} total, $${precioUnitario.toFixed(2)} unitario, ${componentes.length} componentes, ${tiempoTotal} min`);
}

// FUNCIONES PARA CARGAR DATOS AUXILIARES
// -----------------------------------------------

// Función para cargar categorías en el modal de creación
function cargarCategorias() {
    console.log('🔄 Cargando categorías para formulario...');
    
    fetch('/dashboard/api/categorias/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const select = document.getElementById('categoriaElaborado');
            if (select) {
                select.innerHTML = '<option value="">-- Seleccione una categoría --</option>';
                
                data.categorias.forEach(categoria => {
                    select.innerHTML += `<option value="${categoria.id}">${categoria.nombre}</option>`;
                });
                
                console.log(`✅ ${data.categorias.length} categorías cargadas`);
            }
        } else {
            console.error('❌ Error al cargar categorías:', data.message);
            showToast('Error al cargar categorías', 'error');
        }
    })
    .catch(error => {
        console.error('❌ Error de conexión:', error);
        showToast('Error de conexión al cargar categorías', 'error');
    });
}

// Función para cargar unidades en el modal de creación
function cargarUnidades() {
    console.log('🔄 Cargando unidades para formulario...');
    
    fetch('/dashboard/api/unidades-medida/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const select = document.getElementById('unidadElaborado');
            if (select) {
                select.innerHTML = '<option value="">-- Seleccione una unidad --</option>';
                
                data.unidades.forEach(unidad => {
                    select.innerHTML += `<option value="${unidad.id}">${unidad.nombre} (${unidad.abreviacion})</option>`;
                });
                
                console.log(`✅ ${data.unidades.length} unidades cargadas`);
            }
        } else {
            console.error('❌ Error al cargar unidades:', data.message);
            showToast('Error al cargar unidades', 'error');
        }
    })
    .catch(error => {
        console.error('❌ Error de conexión:', error);
        showToast('Error de conexión al cargar unidades', 'error');
    });
}

// Funciones para edición
function cargarCategoriasEdicion(categoriaId) {
    console.log(`🔄 Cargando categorías para edición (seleccionada: ${categoriaId})...`);
    
    fetch('/dashboard/api/categorias/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const select = document.getElementById('editCategoriaSelect');
            if (select) {
                select.innerHTML = '<option value="">-- Seleccione una categoría --</option>';
                
                data.categorias.forEach(categoria => {
                    const selected = categoria.id == categoriaId ? 'selected' : '';
                    select.innerHTML += `<option value="${categoria.id}" ${selected}>${categoria.nombre}</option>`;
                });
                
                console.log(`✅ Categoría seleccionada: ${select.options[select.selectedIndex].text} (${categoriaId})`);
                console.log(`✅ ${data.categorias.length} categorías cargadas para edición`);
            }
        } else {
            console.error('❌ Error al cargar categorías para edición:', data.message);
        }
    })
    .catch(error => {
        console.error('❌ Error de conexión:', error);
    });
}

function cargarUnidadesEdicion(unidadId) {
    console.log(`🔄 Cargando unidades para edición (seleccionada: ${unidadId})...`);
    
    fetch('/dashboard/api/unidades-medida/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const select = document.getElementById('editUnidadSelect');
            if (select) {
                select.innerHTML = '<option value="">-- Seleccione una unidad --</option>';
                
                data.unidades.forEach(unidad => {
                    const selected = unidad.id == unidadId ? 'selected' : '';
                    select.innerHTML += `<option value="${unidad.id}" ${selected}>${unidad.nombre} (${unidad.abreviacion})</option>`;
                });
                
                console.log(`✅ Unidad seleccionada: ${select.options[select.selectedIndex].text} (${unidadId})`);
                console.log(`✅ ${data.unidades.length} unidades cargadas para edición`);
            }
        } else {
            console.error('❌ Error al cargar unidades para edición:', data.message);
        }
    })
    .catch(error => {
        console.error('❌ Error de conexión:', error);
    });
}

// Función para cargar insumos disponibles para edición
function cargarInsumosParaEdicion() {
    console.log('🔄 Cargando insumos disponibles para edición...');
    
    return fetch('/dashboard/insumos-elaborados/insumos-disponibles/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            insumosDisponibles = data.insumos;
            console.log(`✅ Cargados ${data.total} insumos para edición (${data.total_basicos} básicos, ${data.total_compuestos} compuestos)`);
            return data;
        } else {
            console.error('❌ Error al cargar insumos para edición:', data.message);
            throw new Error(data.message);
        }
    })
    .catch(error => {
        console.error('❌ Error de conexión:', error);
        throw error;
    });
}

// Función para cargar los componentes existentes en el formulario de edición
function cargarComponentesEdicion(componentes) {
    console.log(`🔄 Cargando ${componentes.length} componentes para edición`, componentes);
    
    // Limpiar contenedor existente
    const container = document.getElementById('componentesEdicionContainer');
    if (!container) {
        console.error('❌ No se encontró el contenedor de componentes');
        return;
    }
    
    // Asegurarnos que insumos disponibles esté cargado
    if (!insumosDisponibles || insumosDisponibles.length === 0) {
        console.error('❌ No hay insumos disponibles cargados');
        return;
    }
    
    // Eliminar cualquier componente existente
    const componentesExistentes = container.querySelectorAll('.componente-item');
    componentesExistentes.forEach(comp => comp.remove());
    
    // Ocultar alerta si hay componentes
    const alerta = document.getElementById('alertNoComponentesEdicion');
    if (alerta && componentes.length > 0) {
        alerta.style.display = 'none';
    } else if (alerta) {
        alerta.style.display = 'block';
    }
    
    // Si no hay componentes, no hacer nada más
    if (!componentes || componentes.length === 0) {
        console.log('⚠️ No hay componentes para cargar');
        return;
    }
    
    // Resetear contador de componentes
    contadorComponentesEdicion = 0;
    
    // Cargar cada componente existente
    componentes.forEach(componente => {
        agregarComponenteExistenteEdicion(componente);
    });
    
    // Actualizar el resumen después de cargar todos los componentes
    setTimeout(() => {
        actualizarResumenEdicion();
        console.log('✅ Componentes para edición cargados y resumen actualizado');
    }, 100);
}

// Función para agregar un componente existente al formulario de edición
function agregarComponenteExistenteEdicion(componente) {
    contadorComponentesEdicion++;
    
    // Crear opciones para select de insumos
    let opcionesInsumos = '<option value="">-- Seleccione un insumo --</option>';
    
    // Agrupar insumos por tipo
    const insumosPorTipo = {
        'basico': insumosDisponibles.filter(i => i.tipo === 'basico'),
        'compuesto': insumosDisponibles.filter(i => i.tipo === 'compuesto')
    };
    
    // Agregar insumos básicos
    if (insumosPorTipo.basico && insumosPorTipo.basico.length > 0) {
        opcionesInsumos += '<optgroup label="📦 Insumos Básicos">';
        insumosPorTipo.basico.forEach(insumo => {
            const selected = componente.insumo_id == insumo.id ? 'selected' : '';
            opcionesInsumos += `<option value="${insumo.id}" 
                data-precio="${insumo.precio_unitario}" 
                data-unidad="${insumo.unidad_medida_nombre || ''}"
                data-tipo="basico" ${selected}>
                ${insumo.nombre} (${insumo.categoria_nombre || 'Sin categoría'})
            </option>`;
        });
        opcionesInsumos += '</optgroup>';
    }
    
    // Agregar insumos compuestos
    if (insumosPorTipo.compuesto && insumosPorTipo.compuesto.length > 0) {
        opcionesInsumos += '<optgroup label="🔧 Insumos Compuestos">';
        insumosPorTipo.compuesto.forEach(insumo => {
            const selected = componente.insumo_id == insumo.id ? 'selected' : '';
            opcionesInsumos += `<option value="${insumo.id}" 
                data-precio="${insumo.precio_unitario}" 
                data-unidad="${insumo.unidad_medida_nombre || ''}"
                data-tipo="compuesto" ${selected}>
                ${insumo.nombre} (${insumo.categoria_nombre || 'Sin categoría'})
            </option>`;
        });
        opcionesInsumos += '</optgroup>';
    }
    
    const componenteHtml = `
        <div class="componente-item border rounded p-3 mb-3" id="componenteEdicion${contadorComponentesEdicion}">
            <div class="d-flex justify-content-between align-items-start mb-3">
                <h6 class="mb-0">Componente ${contadorComponentesEdicion}</h6>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="eliminarComponenteEdicion(${contadorComponentesEdicion})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            <div class="row g-3">
                <div class="col-md-12">
                    <label class="form-label">Insumo (Básico o Compuesto) <span class="text-danger">*</span></label>
                    <select class="form-select" name="componente_insumo[]" onchange="actualizarInfoComponenteEdicion(this, ${contadorComponentesEdicion})" required>
                        ${opcionesInsumos}
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Cantidad <span class="text-danger">*</span></label>
                    <input type="number" class="form-control" name="componente_cantidad[]" step="0.01" min="0.01" 
                           value="${componente.cantidad || 1}" 
                           onchange="actualizarCostoComponenteEdicion(this, ${contadorComponentesEdicion});" required>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Tiempo (min)</label>
                    <input type="number" class="form-control" name="componente_tiempo[]" min="0" 
                           value="0"
                           onchange="actualizarResumenEdicion()">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Costo</label>
                    <input type="text" class="form-control" readonly id="costoComponenteEdicion${contadorComponentesEdicion}" value="$${componente.costo_total ? componente.costo_total.toFixed(2) : '0.00'}">
                </div>
                <div class="col-12">
                    <label class="form-label">Instrucciones especiales</label>
                    <textarea class="form-control" name="componente_instrucciones[]" rows="2" placeholder="Instrucciones específicas para este componente...">${componente.notas || ''}</textarea>
                </div>
            </div>
        </div>
    `;
    
    const container = document.getElementById('componentesEdicionContainer');
    if (container) {
        container.insertAdjacentHTML('beforeend', componenteHtml);
    }
}

// Agregar nuevo componente para edición
function agregarComponenteEdicion() {
    if (insumosDisponibles.length === 0) {
        showToast('No hay insumos disponibles para agregar como componentes', 'error');
        return;
    }
    
    contadorComponentesEdicion++;
    const container = document.getElementById('componentesEdicionContainer');
    
    if (!container) {
        console.error('❌ No se encontró el contenedor para componentes');
        return;
    }
    
    // Crear opciones para el select
    let opcionesInsumos = '<option value="">-- Seleccione un insumo --</option>';
    
    // Agrupar insumos por tipo
    const insumosPorTipo = {
        'basico': insumosDisponibles.filter(i => i.tipo === 'basico'),
        'compuesto': insumosDisponibles.filter(i => i.tipo === 'compuesto')
    };
    
    // Mostrar conteos en la consola para debuggear
    console.log(`🔍 Filtrando insumos para select:`); 
    console.log(`   - Básicos: ${insumosPorTipo.basico ? insumosPorTipo.basico.length : 0}`);
    console.log(`   - Compuestos: ${insumosPorTipo.compuesto ? insumosPorTipo.compuesto.length : 0}`);
    
    // Agregar insumos básicos
    if (insumosPorTipo.basico && insumosPorTipo.basico.length > 0) {
        opcionesInsumos += '<optgroup label="📦 Insumos Básicos">';
        insumosPorTipo.basico.forEach(insumo => {
            opcionesInsumos += `<option value="${insumo.id}" 
                data-precio="${insumo.precio_unitario}" 
                data-unidad="${insumo.unidad_medida_nombre || ''}"
                data-tipo="basico">
                ${insumo.nombre} (${insumo.categoria_nombre || 'Sin categoría'})
            </option>`;
        });
        opcionesInsumos += '</optgroup>';
    }
    
    // Agregar insumos compuestos
    if (insumosPorTipo.compuesto && insumosPorTipo.compuesto.length > 0) {
        opcionesInsumos += '<optgroup label="🔧 Insumos Compuestos">';
        insumosPorTipo.compuesto.forEach(insumo => {
            opcionesInsumos += `<option value="${insumo.id}" 
                data-precio="${insumo.precio_unitario}" 
                data-unidad="${insumo.unidad_medida_nombre || ''}"
                data-tipo="compuesto">
                ${insumo.nombre} (${insumo.categoria_nombre || 'Sin categoría'})
            </option>`;
        });
        opcionesInsumos += '</optgroup>';
    }
    
    const componenteHtml = `
        <div class="componente-item border rounded p-3 mb-3" id="componenteEdicion${contadorComponentesEdicion}">
            <div class="d-flex justify-content-between align-items-start mb-3">
                <h6 class="mb-0">Componente ${contadorComponentesEdicion}</h6>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="eliminarComponenteEdicion(${contadorComponentesEdicion})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            <div class="row g-3">
                <div class="col-md-12">
                    <label class="form-label">Insumo (Básico o Compuesto) <span class="text-danger">*</span></label>
                    <select class="form-select" name="componente_insumo[]" onchange="actualizarInfoComponenteEdicion(this, ${contadorComponentesEdicion})" required>
                        ${opcionesInsumos}
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Cantidad <span class="text-danger">*</span></label>
                    <input type="number" class="form-control" name="componente_cantidad[]" step="0.01" min="0.01" 
                           value="1" 
                           onchange="actualizarCostoComponenteEdicion(this, ${contadorComponentesEdicion});" required>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Tiempo (min)</label>
                    <input type="number" class="form-control" name="componente_tiempo[]" min="0" 
                           value="0"
                           onchange="actualizarResumenEdicion()">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Costo</label>
                    <input type="text" class="form-control" readonly id="costoComponenteEdicion${contadorComponentesEdicion}" value="$0.00">
                </div>
                <div class="col-12">
                    <label class="form-label">Instrucciones especiales</label>
                    <textarea class="form-control" name="componente_instrucciones[]" rows="2" placeholder="Instrucciones específicas para este componente..."></textarea>
                </div>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', componenteHtml);
    
    // Ocultar alerta de no componentes
    const alerta = document.getElementById('alertNoComponentesEdicion');
    if (alerta) {
        alerta.style.display = 'none';
    }
    
    // Actualizar resumen
    actualizarResumenEdicion();
}

// Eliminar componente en edición
function eliminarComponenteEdicion(id) {
    const componente = document.getElementById(`componenteEdicion${id}`);
    if (componente) {
        componente.remove();
        
        // Mostrar alerta si no hay componentes
        const container = document.getElementById('componentesEdicionContainer');
        if (container && container.querySelectorAll('.componente-item').length === 0) {
            const alerta = document.getElementById('alertNoComponentesEdicion');
            if (alerta) {
                alerta.style.display = 'block';
            }
        }
        
        // Actualizar resumen
        actualizarResumenEdicion();
    }
}

// Actualizar información de un componente en edición
function actualizarInfoComponenteEdicion(select, id) {
    const option = select.selectedOptions[0];
    const componenteItem = select.closest('.componente-item');
    
    if (option && option.value && componenteItem) {
        const cantidadInput = componenteItem.querySelector('input[name="componente_cantidad[]"]');
        if (cantidadInput) {
            actualizarCostoComponenteEdicion(cantidadInput, id);
        }
    }
    
    actualizarResumenEdicion();
}

// Actualizar costo de componente en edición
function actualizarCostoComponenteEdicion(cantidadInput, id) {
    const componenteItem = cantidadInput.closest('.componente-item');
    const select = componenteItem.querySelector('select[name="componente_insumo[]"]');
    const costoInput = document.getElementById(`costoComponenteEdicion${id}`);
    
    if (select.value && cantidadInput.value) {
        const option = select.selectedOptions[0];
        const precio = parseFloat(option.dataset.precio) || 0;
        const cantidad = parseFloat(cantidadInput.value) || 0;
        const costo = precio * cantidad;
        
        costoInput.value = `$${costo.toFixed(2)}`;
        
        console.log(`💰 Componente edición ${id}: ${cantidad} × $${precio} = $${costo.toFixed(2)}`);
    } else {
        costoInput.value = '$0.00';
    }
    
    // Actualizar resumen total
    actualizarResumenEdicion();
}

// FUNCIONES PARA CREAR INSUMOS ELABORADOS
// -----------------------------------------------

// Función para agregar un componente al crear un insumo elaborado
function agregarComponenteElaborado() {
    console.log('🔄 Agregando componente para elaborado...');
    
    if (insumosDisponibles.length === 0) {
        showToast('No hay insumos disponibles para agregar como componentes', 'error');
        return;
    }
    
    contadorComponentesElaborado++;
    const container = document.getElementById('componentesElaboradoContainer');
    
    if (!container) {
        console.error('❌ No se encontró el contenedor para componentes');
        return;
    }
    
    // Crear opciones para el select
    let opcionesInsumos = '<option value="">-- Seleccione un insumo --</option>';
    
    // Agrupar insumos por tipo
    const insumosPorTipo = {
        'basico': insumosDisponibles.filter(i => i.tipo === 'basico'),
        'compuesto': insumosDisponibles.filter(i => i.tipo === 'compuesto')
    };
    
    // Mostrar conteos en la consola para debuggear
    console.log(`🔍 Filtrando insumos para select:`); 
    console.log(`   - Básicos: ${insumosPorTipo.basico ? insumosPorTipo.basico.length : 0}`);
    console.log(`   - Compuestos: ${insumosPorTipo.compuesto ? insumosPorTipo.compuesto.length : 0}`);
    
    // Agregar insumos básicos
    if (insumosPorTipo.basico && insumosPorTipo.basico.length > 0) {
        opcionesInsumos += '<optgroup label="📦 Insumos Básicos">';
        insumosPorTipo.basico.forEach(insumo => {
            opcionesInsumos += `<option value="${insumo.id}" 
                data-precio="${insumo.precio_unitario}" 
                data-unidad="${insumo.unidad_medida_nombre || ''}"
                data-tipo="basico">
                ${insumo.nombre} (${insumo.categoria_nombre || 'Sin categoría'})
            </option>`;
        });
        opcionesInsumos += '</optgroup>';
    }
    
    // Agregar insumos compuestos
    if (insumosPorTipo.compuesto && insumosPorTipo.compuesto.length > 0) {
        opcionesInsumos += '<optgroup label="🔧 Insumos Compuestos">';
        insumosPorTipo.compuesto.forEach(insumo => {
            opcionesInsumos += `<option value="${insumo.id}" 
                data-precio="${insumo.precio_unitario}" 
                data-unidad="${insumo.unidad_medida_nombre || ''}"
                data-tipo="compuesto">
                ${insumo.nombre} (${insumo.categoria_nombre || 'Sin categoría'})
            </option>`;
        });
        opcionesInsumos += '</optgroup>';
    }
    
    const componenteHtml = `
        <div class="componente-item border rounded p-3 mb-3" id="componente${contadorComponentesElaborado}">
            <div class="d-flex justify-content-between align-items-start mb-3">
                <h6 class="mb-0">Componente ${contadorComponentesElaborado}</h6>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="eliminarComponenteElaborado(${contadorComponentesElaborado})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            <div class="row g-3">
                <div class="col-md-12">
                    <label class="form-label">Insumo (Básico o Compuesto) <span class="text-danger">*</span></label>
                    <select class="form-select" name="componente_insumo[]" onchange="actualizarInfoComponenteElaborado(this, ${contadorComponentesElaborado})" required>
                        ${opcionesInsumos}
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Cantidad <span class="text-danger">*</span></label>
                    <input type="number" class="form-control" name="componente_cantidad[]" step="0.01" min="0.01" 
                           value="1" 
                           onchange="actualizarCostoComponenteElaborado(this, ${contadorComponentesElaborado});" required>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Tiempo (min)</label>
                    <input type="number" class="form-control" name="componente_tiempo[]" min="0" 
                           value="0"
                           onchange="actualizarResumenElaborado()">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Costo</label>
                    <input type="text" class="form-control" readonly id="costoComponente${contadorComponentesElaborado}" value="$0.00">
                </div>
                <div class="col-12">
                    <label class="form-label">Instrucciones especiales</label>
                    <textarea class="form-control" name="componente_instrucciones[]" rows="2" placeholder="Instrucciones específicas para este componente..."></textarea>
                </div>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', componenteHtml);
    
    // Ocultar alerta de no componentes
    const alerta = document.getElementById('alertNoComponentes');
    if (alerta) {
        alerta.classList.add('d-none');
    }
    
    // Actualizar resumen
    actualizarResumenElaborado();
}

// Función para eliminar un componente al crear un insumo elaborado
function eliminarComponenteElaborado(id) {
    const componente = document.getElementById(`componente${id}`);
    if (componente) {
        componente.remove();
        
        // Mostrar alerta si no hay componentes
        const container = document.getElementById('componentesElaboradoContainer');
        if (container && container.querySelectorAll('.componente-item').length === 0) {
            const alerta = document.getElementById('alertNoComponentes');
            if (alerta) {
                alerta.classList.remove('d-none');
            }
        }
        
        // Actualizar resumen
        actualizarResumenElaborado();
    }
}

// Actualizar información de un componente al crear insumo elaborado
function actualizarInfoComponenteElaborado(select, id) {
    const option = select.selectedOptions[0];
    const componenteItem = select.closest('.componente-item');
    
    if (option && option.value && componenteItem) {
        const cantidadInput = componenteItem.querySelector('input[name="componente_cantidad[]"]');
        if (cantidadInput) {
            actualizarCostoComponenteElaborado(cantidadInput, id);
        }
    }
    
    actualizarResumenElaborado();
}

// Actualizar costo de componente al crear insumo elaborado
function actualizarCostoComponenteElaborado(cantidadInput, id) {
    const componenteItem = cantidadInput.closest('.componente-item');
    const select = componenteItem.querySelector('select[name="componente_insumo[]"]');
    const costoInput = document.getElementById(`costoComponente${id}`);
    
    if (select.value && cantidadInput.value) {
        const option = select.selectedOptions[0];
        const precio = parseFloat(option.dataset.precio) || 0;
        const cantidad = parseFloat(cantidadInput.value) || 0;
        const costo = precio * cantidad;
        
        costoInput.value = `$${costo.toFixed(2)}`;
        
        console.log(`💰 Componente ${id}: ${cantidad} × $${precio} = $${costo.toFixed(2)}`);
    } else {
        costoInput.value = '$0.00';
    }
    
    // Actualizar resumen total
    actualizarResumenElaborado();
}

// Actualizar resumen al crear insumo elaborado
function actualizarResumenElaborado() {
    console.log('🔄 Actualizando resumen de elaborado...');
    
    // Obtener elementos del resumen
    const costoTotalElement = document.getElementById('costoTotalElaborado');
    const precioUnitarioElement = document.getElementById('precioUnitarioElaborado');
    const totalComponentesElement = document.getElementById('totalComponentesElaborado');
    const tiempoTotalElement = document.getElementById('tiempoTotalElaborado');
    
    if (!costoTotalElement || !precioUnitarioElement || !totalComponentesElement || !tiempoTotalElement) {
        console.error('❌ No se encontraron todos los elementos del resumen');
        return;
    }
    
    // Obtener componentes
    const componentes = document.querySelectorAll('#componentesElaboradoContainer .componente-item');
    let costoTotal = 0;
    let tiempoTotal = 0;
    
    // Calcular costo total sumando el costo de cada componente
    componentes.forEach(componente => {
        // Extraer costo del componente
        const costoInput = componente.querySelector('input[id^="costoComponente"]');
        if (costoInput) {
            const costoTexto = costoInput.value.replace('$', '').trim();
            const costo = parseFloat(costoTexto) || 0;
            costoTotal += costo;
        }
        
        // Extraer tiempo del componente
        const tiempoInput = componente.querySelector('input[name="componente_tiempo[]"]');
        if (tiempoInput) {
            const tiempo = parseFloat(tiempoInput.value) || 0;
            tiempoTotal += tiempo;
        }
    });
    
    // Obtener cantidad producida
    const cantidadProducidaInput = document.querySelector('input[name="cantidad_producida"]');
    const cantidadProducida = cantidadProducidaInput ? parseFloat(cantidadProducidaInput.value) || 1 : 1;
    
    // Calcular precio unitario
    const precioUnitario = cantidadProducida > 0 ? costoTotal / cantidadProducida : 0;
    
    // Actualizar elementos del resumen
    costoTotalElement.textContent = `$${costoTotal.toFixed(2)}`;
    precioUnitarioElement.textContent = `$${precioUnitario.toFixed(2)}`;
    totalComponentesElement.textContent = componentes.length;
    
    // Actualizar tiempo total (sumar tiempo de componentes + tiempo de preparación)
    const tiempoPreparacionInput = document.querySelector('input[name="tiempo_total_preparacion"]');
    const tiempoPreparacion = tiempoPreparacionInput ? parseFloat(tiempoPreparacionInput.value) || 0 : 0;
    tiempoTotal += tiempoPreparacion;
    
    tiempoTotalElement.textContent = `${tiempoTotal} min`;
    
    console.log(`💰 Resumen actualizado: $${costoTotal.toFixed(2)} total, $${precioUnitario.toFixed(2)} unitario, ${componentes.length} componentes, ${tiempoTotal} min`);
}

// GESTIÓN DE CATEGORÍAS Y UNIDADES DE MEDIDA
// =============================================

// Variables globales para categorías y unidades
let categoriasActuales = [];
let unidadesActuales = [];

// FUNCIONES PARA GESTIÓN DE CATEGORÍAS
// -------------------------------------

// Mostrar modal de gestión de categorías
function mostrarGestionCategorias() {
    cargarListaCategorias();
    const modal = new bootstrap.Modal(document.getElementById('nuevaCategoriaModal'));
    modal.show();
}

// Cargar lista de categorías en el modal
function cargarListaCategorias() {
    console.log('🔄 Cargando lista de categorías...');
    
    fetch('/dashboard/api/categorias/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            categoriasActuales = data.categorias;
            mostrarListaCategorias(data.categorias);
            console.log(`✅ ${data.categorias.length} categorías cargadas`);
        } else {
            console.error('❌ Error al cargar categorías:', data.message);
            showToast('Error al cargar categorías', 'error');
        }
    })
    .catch(error => {
        console.error('❌ Error de conexión:', error);
        showToast('Error de conexión al cargar categorías', 'error');
    });
}

// Mostrar lista de categorías en el modal
function mostrarListaCategorias(categorias) {
    const modalBody = document.querySelector('#nuevaCategoriaModal .modal-body');
    
    let listaHTML = '';
    if (categorias.length > 0) {
        listaHTML = `
            <div class="mb-4">
                <h6 class="mb-3"><i class="fas fa-list me-2"></i>Categorías existentes (${categorias.length})</h6>
                <div class="list-group" style="max-height: 200px; overflow-y: auto;">
        `;
        
        categorias.forEach(categoria => {
            listaHTML += `
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${categoria.nombre}</strong>
                        ${categoria.descripcion ? `<br><small class="text-muted">${categoria.descripcion}</small>` : ''}
                    </div>
                    <div class="btn-group btn-group-sm">
                        <button type="button" class="btn btn-outline-primary btn-sm" onclick="editarCategoria(${categoria.id}, '${categoria.nombre}', '${categoria.descripcion || ''}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button type="button" class="btn btn-outline-danger btn-sm" onclick="eliminarCategoria(${categoria.id}, '${categoria.nombre}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        });
        
        listaHTML += `
                </div>
                <hr>
            </div>
        `;
    }
    
    modalBody.innerHTML = listaHTML + `
        <div>
            <h6 class="mb-3"><i class="fas fa-plus me-2"></i>Crear nueva categoría</h6>
            <div class="mb-3">
                <label class="form-label">Nombre de la categoría</label>
                <input type="text" class="form-control" id="nombreCategoria" name="nombre" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Descripción</label>
                <textarea class="form-control" id="descripcionCategoria" name="descripcion" rows="3"></textarea>
            </div>
        </div>
    `;
}

// Crear nueva categoría
function crearCategoria() {
    const nombre = document.getElementById('nombreCategoria').value.trim();
    const descripcion = document.getElementById('descripcionCategoria').value.trim();
    
    if (!nombre) {
        showToast('El nombre de la categoría es obligatorio', 'warning');
        return;
    }
    
    console.log('🔄 Creando nueva categoría:', nombre);
    
    const formData = new FormData();
    formData.append('nombre', nombre);
    formData.append('descripcion', descripcion);
    
    fetch('/dashboard/categorias/crear/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            
            // Limpiar formulario
            document.getElementById('nombreCategoria').value = '';
            document.getElementById('descripcionCategoria').value = '';
            
            // Recargar lista
            cargarListaCategorias();
            
            // Actualizar selects en formularios
            cargarCategorias();
            cargarCategoriasEdicion();
            
            console.log('✅ Categoría creada exitosamente');
        } else {
            showToast(data.error || 'Error al crear la categoría', 'error');
            console.error('❌ Error:', data.error);
        }
    })
    .catch(error => {
        console.error('❌ Error de conexión:', error);
        showToast('Error de conexión', 'error');
    });
}

// Editar categoría (simplificado - solo cambiar nombre)
function editarCategoria(id, nombre, descripcion) {
    const nuevoNombre = prompt('Nuevo nombre para la categoría:', nombre);
    const nuevaDescripcion = prompt('Nueva descripción:', descripcion);
    
    if (nuevoNombre && nuevoNombre.trim() !== '') {
        // Como no tenemos endpoint de edición, creamos uno nuevo si es diferente
        if (nuevoNombre.trim() !== nombre) {
            const formData = new FormData();
            formData.append('nombre', nuevoNombre.trim());
            formData.append('descripcion', nuevaDescripcion || '');
            
            fetch('/dashboard/categorias/crear/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Nueva categoría creada (edición no soportada)', 'info');
                    cargarListaCategorias();
                } else {
                    showToast(data.error || 'Error al crear la categoría', 'error');
                }
            });
        }
    }
}

// Eliminar categoría
function eliminarCategoria(id, nombre) {
    if (confirm(`¿Está seguro de que desea eliminar la categoría "${nombre}"?\n\nEsta acción no se puede deshacer.`)) {
        console.log('🗑️ Eliminando categoría:', nombre);
        
        fetch(`/dashboard/categorias/eliminar/${id}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, 'success');
                cargarListaCategorias();
                
                // Actualizar selects en formularios
                cargarCategorias();
                cargarCategoriasEdicion();
                
                console.log('✅ Categoría eliminada exitosamente');
            } else {
                showToast(data.error || 'Error al eliminar la categoría', 'error');
                console.error('❌ Error:', data.error);
            }
        })
        .catch(error => {
            console.error('❌ Error de conexión:', error);
            showToast('Error de conexión', 'error');
        });
    }
}

// FUNCIONES PARA GESTIÓN DE UNIDADES DE MEDIDA
// ---------------------------------------------

// Mostrar modal de gestión de unidades
function mostrarGestionUnidades() {
    cargarListaUnidades();
    const modal = new bootstrap.Modal(document.getElementById('nuevaUnidadModal'));
    modal.show();
}

// Cargar lista de unidades en el modal
function cargarListaUnidades() {
    console.log('🔄 Cargando lista de unidades...');
    
    fetch('/dashboard/api/unidades-medida/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            unidadesActuales = data.unidades;
            mostrarListaUnidades(data.unidades);
            console.log(`✅ ${data.unidades.length} unidades cargadas`);
        } else {
            console.error('❌ Error al cargar unidades:', data.message);
            showToast('Error al cargar unidades', 'error');
        }
    })
    .catch(error => {
        console.error('❌ Error de conexión:', error);
        showToast('Error de conexión al cargar unidades', 'error');
    });
}

// Mostrar lista de unidades en el modal
function mostrarListaUnidades(unidades) {
    const modalBody = document.querySelector('#nuevaUnidadModal .modal-body');
    
    let listaHTML = '';
    if (unidades.length > 0) {
        listaHTML = `
            <div class="mb-4">
                <h6 class="mb-3"><i class="fas fa-list me-2"></i>Unidades existentes (${unidades.length})</h6>
                <div class="list-group" style="max-height: 200px; overflow-y: auto;">
        `;
        
        unidades.forEach(unidad => {
            listaHTML += `
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${unidad.nombre}</strong> <span class="text-muted">(${unidad.abreviacion})</span>
                    </div>
                    <div class="btn-group btn-group-sm">
                        <button type="button" class="btn btn-outline-primary btn-sm" onclick="editarUnidad(${unidad.id}, '${unidad.nombre}', '${unidad.abreviacion}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button type="button" class="btn btn-outline-danger btn-sm" onclick="eliminarUnidad(${unidad.id}, '${unidad.nombre}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        });
        
        listaHTML += `
                </div>
                <hr>
            </div>
        `;
    }
    
    modalBody.innerHTML = listaHTML + `
        <div>
            <h6 class="mb-3"><i class="fas fa-plus me-2"></i>Crear nueva unidad</h6>
            <div class="mb-3">
                <label class="form-label">Nombre de la unidad</label>
                <input type="text" class="form-control" id="nombreUnidad" name="nombre" placeholder="Kilogramos" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Abreviación</label>
                <input type="text" class="form-control" id="abreviacionUnidad" name="abreviacion" placeholder="kg" required>
            </div>
        </div>
    `;
}

// Crear nueva unidad
function crearUnidad() {
    const nombre = document.getElementById('nombreUnidad').value.trim();
    const abreviacion = document.getElementById('abreviacionUnidad').value.trim();
    
    if (!nombre || !abreviacion) {
        showToast('El nombre y la abreviación son obligatorios', 'warning');
        return;
    }
    
    console.log('🔄 Creando nueva unidad:', nombre, abreviacion);
    
    const formData = new FormData();
    formData.append('nombre', nombre);
    formData.append('abreviacion', abreviacion);
    
    fetch('/dashboard/unidades/crear/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            
            // Limpiar formulario
            document.getElementById('nombreUnidad').value = '';
            document.getElementById('abreviacionUnidad').value = '';
            
            // Recargar lista
            cargarListaUnidades();
            
            // Actualizar selects en formularios
            cargarUnidades();
            cargarUnidadesEdicion();
            
            console.log('✅ Unidad creada exitosamente');
        } else {
            showToast(data.error || 'Error al crear la unidad', 'error');
            console.error('❌ Error:', data.error);
        }
    })
    .catch(error => {
        console.error('❌ Error de conexión:', error);
        showToast('Error de conexión', 'error');
    });
}

// Editar unidad (simplificado - solo cambiar nombre y abreviación)
function editarUnidad(id, nombre, abreviacion) {
    const nuevoNombre = prompt('Nuevo nombre para la unidad:', nombre);
    const nuevaAbreviacion = prompt('Nueva abreviación:', abreviacion);
    
    if (nuevoNombre && nuevaAbreviacion && (nuevoNombre.trim() !== nombre || nuevaAbreviacion.trim() !== abreviacion)) {
        const formData = new FormData();
        formData.append('nombre', nuevoNombre.trim());
        formData.append('abreviacion', nuevaAbreviacion.trim());
        
        fetch('/dashboard/unidades/crear/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Nueva unidad creada (edición no soportada)', 'info');
                cargarListaUnidades();
            } else {
                showToast(data.error || 'Error al crear la unidad', 'error');
            }
        });
    }
}

// Eliminar unidad
function eliminarUnidad(id, nombre) {
    if (confirm(`¿Está seguro de que desea eliminar la unidad "${nombre}"?\n\nEsta acción no se puede deshacer.`)) {
        console.log('🗑️ Eliminando unidad:', nombre);
        
        fetch(`/dashboard/unidades/eliminar/${id}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, 'success');
                cargarListaUnidades();
                
                // Actualizar selects en formularios
                cargarUnidades();
                cargarUnidadesEdicion();
                
                console.log('✅ Unidad eliminada exitosamente');
            } else {
                showToast(data.error || 'Error al eliminar la unidad', 'error');
                console.error('❌ Error:', data.error);
            }
        })
        .catch(error => {
            console.error('❌ Error de conexión:', error);
            showToast('Error de conexión', 'error');
        });
    }
}

// UTILIDADES
// -----------------------------------------------

// Función para mostrar notificaciones Toast
function showToast(message, type = 'info') {
    // Comprobar si ya existe un contenedor de toasts
    let toastContainer = document.querySelector('.toast-container');
    
    // Si no existe, crearlo
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Crear el toast
    const toastId = 'toast-' + Date.now();
    const bgClass = type === 'success' ? 'bg-success' : 
                   type === 'error' ? 'bg-danger' : 
                   type === 'warning' ? 'bg-warning' : 'bg-info';
    
    const toast = document.createElement('div');
    toast.className = `toast ${bgClass} text-white`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="toast-header">
            <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    // Agregar el toast al contenedor
    toastContainer.appendChild(toast);
    
    // Inicializar y mostrar el toast
    const bsToast = new bootstrap.Toast(toast, { autohide: true, delay: 5000 });
    bsToast.show();
    
    // Eliminar el toast del DOM después de ocultarse
    toast.addEventListener('hidden.bs.toast', function () {
        toast.remove();
    });
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando módulo de insumos elaborados...');
    
    // Inicializar tooltips y popovers de Bootstrap
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));
    
    const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
    popovers.forEach(popover => new bootstrap.Popover(popover));    
    
    // Configurar event listeners para los botones de acción
    configurarBotonesAccion();
    
    // Configurar event listeners para gestión de categorías
    configurarFormularioCategorias();
    
    // Configurar event listeners para gestión de unidades
    configurarFormularioUnidades();
    
    // Configurar formulario de creación
    const formCrearElaborado = document.getElementById('formCrearElaborado');
    if (formCrearElaborado) {
        formCrearElaborado.addEventListener('submit', function(e) {
            e.preventDefault();
            
            console.log('🔄 Enviando formulario de creación...');
            
            // Validar que haya al menos un componente
            const componentes = document.querySelectorAll('#componentesElaboradoContainer .componente-item');
            if (componentes.length === 0) {
                showToast('Debe agregar al menos un componente para este insumo elaborado', 'error');
                return false;
            }
            
            // Deshabilitar botón de submit para prevenir doble envío
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Guardando...`;
            
            // Crear objeto FormData con los datos del formulario
            const formData = new FormData(this);
            
            // Agregar token CSRF
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            formData.append('csrfmiddlewaretoken', csrfToken);
            
            // Realizar la petición para crear el insumo
            fetch('/dashboard/insumos-elaborados/crear/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Mostrar mensaje de éxito
                    showToast(data.message || 'Insumo elaborado creado correctamente', 'success');
                    
                    // Cerrar modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('modalCrearElaborado'));
                    modal.hide();
                    
                    // Recargar página
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    // Mostrar mensaje de error
                    showToast(data.message || 'Error al crear el insumo elaborado', 'error');
                    console.error('❌ Error al crear:', data.message);
                }
            })
            .catch(error => {
                console.error('❌ Error en la petición:', error);
                showToast('Error al comunicarse con el servidor. Por favor, intente nuevamente', 'error');
            })
            .finally(() => {
                // Restaurar botón de submit
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
        });
        console.log('✅ Formulario de creación configurado correctamente');
    } else {
        console.log('⚠️ No se encontró el formulario de creación de insumo elaborado');
    }
});

// Función para configurar los event listeners de los botones de acción
function configurarBotonesAccion() {
    console.log('🔄 Configurando botones de acción para insumos elaborados...');
    
    // Botones de ver detalle
    document.querySelectorAll('.btn-detalle').forEach(btn => {
        btn.addEventListener('click', function() {
            const insumoId = this.getAttribute('data-id');
            if (insumoId) {
                verDetalleElaborado(insumoId);
            }
        });
    });
    
    // Botones de editar
    document.querySelectorAll('.btn-editar').forEach(btn => {
        btn.addEventListener('click', function() {
            const insumoId = this.getAttribute('data-id');
            if (insumoId) {
                editarInsumoElaborado(insumoId);
            }
        });
    });
    
    // Botones de eliminar
    document.querySelectorAll('.btn-eliminar').forEach(btn => {
        btn.addEventListener('click', function() {
            const insumoId = this.getAttribute('data-id');
            const nombre = this.getAttribute('data-nombre');
            if (insumoId && nombre) {
                eliminarInsumoElaborado(insumoId, nombre);
            }
        });
    });
    
    console.log('✅ Botones de acción configurados correctamente');
}

// CONFIGURACIÓN DE FORMULARIOS PARA CATEGORÍAS Y UNIDADES
// ========================================================

// Configurar formulario de categorías
function configurarFormularioCategorias() {
    console.log('🔄 Configurando formulario de categorías...');
    
    // Event listener para abrir modal de categorías
    const btnGestionarCategorias = document.querySelector('[data-bs-toggle="modal"][data-bs-target="#nuevaCategoriaModal"]');
    if (btnGestionarCategorias) {
        btnGestionarCategorias.addEventListener('click', function() {
            cargarListaCategorias();
        });
    }
    
    // Event listener para el formulario dentro del modal
    const modalCategorias = document.getElementById('nuevaCategoriaModal');
    if (modalCategorias) {
        // Event listener para el botón de crear categoría
        const btnCrearCategoria = document.getElementById('btnCrearCategoria');
        if (btnCrearCategoria) {
            btnCrearCategoria.addEventListener('click', function(e) {
                e.preventDefault();
                crearCategoria();
            });
        }
    }
    
    console.log('✅ Formulario de categorías configurado');
}

// Configurar formulario de unidades
function configurarFormularioUnidades() {
    console.log('🔄 Configurando formulario de unidades...');
    
    // Event listener para abrir modal de unidades
    const btnGestionarUnidades = document.querySelector('[data-bs-toggle="modal"][data-bs-target="#nuevaUnidadModal"]');
    if (btnGestionarUnidades) {
        btnGestionarUnidades.addEventListener('click', function() {
            cargarListaUnidades();
        });
    }
    
    // Event listener para el formulario dentro del modal
    const modalUnidades = document.getElementById('nuevaUnidadModal');
    if (modalUnidades) {
        // Event listener para el botón de crear unidad
        const btnCrearUnidad = document.getElementById('btnCrearUnidad');
        if (btnCrearUnidad) {
            btnCrearUnidad.addEventListener('click', function(e) {
                e.preventDefault();
                crearUnidad();
            });
        }
    }
    
    console.log('✅ Formulario de unidades configurado');
}
