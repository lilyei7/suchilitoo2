// Variables globales para el módulo de recetas
let todosLosInsumos = [];
let contadorIngredientes = 0;
let contadorIngredientesEditar = 0;
let currentRecetaId = null;

// Función para abrir el modal de crear receta
function abrirModalCrearReceta() {
    console.log('🔍 Abriendo modal de nueva receta');
    
    // Asegurar que tenemos los insumos cargados
    cargarInsumos().then(() => {
        // Limpiar el formulario
        const form = document.getElementById('formCrearReceta');
        if (form) {
            form.reset();
        }
        
        // Limpiar contenedor de ingredientes
        const container = document.getElementById('ingredientesContainer');
        if (container) {
            container.innerHTML = `
                <div id="alertaIngredientes" class="alert alert-info">
                    <i class="fas fa-info-circle me-1"></i> Agrega ingredientes para tu receta
                </div>
            `;
        }
        
        // Reiniciar contador de ingredientes
        contadorIngredientes = 0;
          // Actualizar costos
        const costoPorcion = document.getElementById('costoPorcion');
        if (costoPorcion) {
            costoPorcion.value = '0.00';
        }
        
        const costoTotal = document.getElementById('costoTotal');
        if (costoTotal) {
            costoTotal.value = '0.00';
        }
        
        // Actualizar selectores de categorías
        actualizarSelectoresCategorias().then(() => {
            console.log('✅ Selectores de categorías actualizados para creación');
        }).catch(error => {
            console.error('Error actualizando categorías:', error);
        });
        
        // Abrir el modal
        const modal = new bootstrap.Modal(document.getElementById('modalCrearReceta'));
        modal.show();    }).catch(error => {
        console.error('Error al cargar insumos:', error);
        showToast('Error al cargar insumos. Intente de nuevo.', 'error');
    });
}

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Módulo de recetas inicializado');
    // Cargar insumos y esperar a que terminen antes de continuar
    cargarInsumos().then(() => {
        console.log('✅ Insumos cargados correctamente, continuando con inicialización');
        cargarCategoriasEnSelectores(); // Cargar categorías de recetas en los selectores
    }).catch(error => {
        console.error('❌ Error cargando insumos:', error);
        showToast('Error cargando insumos. Algunas funciones pueden no estar disponibles.', 'error');
    });
    
    // Evento para el formulario de creación - Usando try-catch para evitar errores si el elemento no existe
    try {
        const formCrearReceta = document.getElementById('formCrearReceta');
        if (formCrearReceta) {
            formCrearReceta.addEventListener('submit', function(e) {
                e.preventDefault(); // Prevenir el envío normal del formulario
                guardarReceta();
            });
            console.log('✅ Evento submit configurado para formCrearReceta');
        } else {
            console.warn('⚠️ No se encontró el formulario formCrearReceta');
        }
    } catch (error) {
        console.error('Error al configurar evento para formCrearReceta:', error);
    }
      // Evento para el formulario de edición - Usando try-catch para evitar errores
    try {
        const formEditarReceta = document.getElementById('formEditarReceta');
        if (formEditarReceta) {
            formEditarReceta.addEventListener('submit', function(e) {
                e.preventDefault(); // Prevenir el envío normal del formulario
                actualizarReceta();
            });
            console.log('✅ Evento submit configurado para formEditarReceta');
        } else {
            console.warn('⚠️ No se encontró el formulario formEditarReceta');
        }
    } catch (error) {
        console.error('Error al configurar evento para formEditarReceta:', error);
    }
    
    // Evento para el formulario de crear categoría
    try {
        const formCrearCategoria = document.getElementById('formCrearCategoria');
        if (formCrearCategoria) {
            formCrearCategoria.addEventListener('submit', function(e) {
                e.preventDefault();
                crearCategoriaReceta();
            });
            console.log('✅ Evento submit configurado para formCrearCategoria');
        } else {
            console.warn('⚠️ No se encontró el formulario formCrearCategoria');
        }
    } catch (error) {
        console.error('Error al configurar evento para formCrearCategoria:', error);
    }
      // Actualizar costo por porción cuando cambie el número de porciones en creación
    document.getElementById('porciones').addEventListener('change', function() {
        actualizarResumenCostos();
    });
    
    // Exposición de funciones al ámbito global al final de la inicialización 
    window.verDetalleReceta = verDetalleReceta;
    window.editarReceta = editarReceta;
    window.duplicarReceta = duplicarReceta;
    window.eliminarReceta = eliminarReceta;
    window.abrirModalCrearReceta = abrirModalCrearReceta;
    window.abrirModalCategorias = abrirModalCategorias;
});

// Ver detalle de receta
function verDetalleReceta(recetaId) {
    console.log(`👀 Mostrando detalle de receta ID: ${recetaId}`);
    
    const modal = new bootstrap.Modal(document.getElementById('modalDetalleReceta'));
    const content = document.getElementById('detalleRecetaContent');
    
    // Mostrar cargando
    content.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="mt-2 text-muted">Cargando detalles...</p>
        </div>
    `;
    
    modal.show();
    
    // Cargar datos
    fetch(`/dashboard/recetas/detalle/${recetaId}/`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('✅ Datos recibidos:', data);
            renderizarDetalleReceta(data.receta, data.ingredientes);
        } else {
            console.error('❌ Error:', data.message);
            content.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-1"></i> ${data.message}
                </div>
            `;
        }
    })
    .catch(error => {
        console.error('❌ Error:', error);
        content.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-1"></i> Error al cargar los datos
            </div>
        `;
    });
}

// Editar receta
function editarReceta(recetaId) {
    // Guardar el ID para referencias futuras
    currentRecetaId = recetaId;
    
    console.log(`🔧 Iniciando edición de receta ID: ${recetaId}`);
    
    // Verificar que el modal y sus elementos existen
    const modalElement = document.getElementById('modalEditarReceta');
    if (!modalElement) {
        console.error('Error: No se encontró el modal de edición');
        showToast('Error al cargar el formulario de edición', 'error');
        return;
    }
    
    const modal = new bootstrap.Modal(modalElement);
    const form = document.getElementById('formEditarReceta');
    if (!form) {
        console.error('Error: No se encontró el formulario de edición');
        showToast('Error al cargar el formulario de edición', 'error');
        return;
    }
    
    // Verificar que existe el contenedor de ingredientes
    const content = document.getElementById('editarIngredientesContainer');
    if (!content) {
        console.error('Error: No se encontró el contenedor de ingredientes en el modal de edición');
        // Intentar crear el contenedor si no existe
        try {
            const ingredientesSection = document.querySelector('#formEditarReceta .ingredientes-section');
            if (ingredientesSection) {
                const newContainer = document.createElement('div');
                newContainer.id = 'editarIngredientesContainer';
                ingredientesSection.appendChild(newContainer);
                console.log('Se creó un nuevo contenedor de ingredientes');
            } else {
                showToast('Error al cargar el formulario de edición', 'error');
                return;
            }
        } catch (e) {
            console.error('No se pudo crear el contenedor de ingredientes:', e);
            showToast('Error al cargar el formulario de edición', 'error');
            return;
        }
    }
    
    // Obtener el contenedor de ingredientes (recién creado o existente)
    const ingredientesContainer = document.getElementById('editarIngredientesContainer');
    
    // Mostrar cargando
    ingredientesContainer.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="mt-2 text-muted">Cargando ingredientes...</p>
        </div>
    `;
    
    // Asegurarse de que el botón de guardar cambios tenga el onclick correcto
    const saveButton = document.querySelector('#modalEditarReceta .modal-footer button.btn-primary');
    if (saveButton) {
        saveButton.setAttribute('onclick', 'actualizarReceta()');
        console.log('Botón de guardar cambios configurado correctamente');
    } else {
        console.error('No se encontró el botón de guardar cambios en el modal de edición');
    }
    
    modal.show();
    
    // Reiniciar el contador de ingredientes para edición
    contadorIngredientesEditar = 0;
    
    // Asegurar que las categorías estén cargadas en el selector y luego los insumos
    Promise.all([
        actualizarSelectoresCategorias(), 
        cargarInsumos()
    ]).then(() => {
        console.log('✅ Categorías e insumos cargados antes de editar receta');
        
        // Ahora cargar datos de la receta
        return fetch(`/dashboard/recetas/detalle/${recetaId}/`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
    })
    .then(response => {
        console.log('Status:', response.status);
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('✅ Datos de receta recibidos para edición:', data);
            console.log(`- Receta: ${data.receta.nombre}`);
            console.log(`- Ingredientes: ${data.ingredientes ? data.ingredientes.length : 0}`);
            return cargarDatosEdicion(data.receta, data.ingredientes);
        } else {
            console.error('❌ Error:', data.message);
            const container = document.getElementById('editarIngredientesContainer');
            if (container) {
                container.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle me-1"></i> ${data.message}
                    </div>
                `;
            }
            throw new Error(data.message);
        }
    })
    .catch(error => {
        console.error('❌ Error durante la edición de receta:', error);
        const container = document.getElementById('editarIngredientesContainer');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-1"></i> Error al cargar los datos: ${error.message}
                </div>
            `;
        }
    });
}

// Duplicar receta
function duplicarReceta(recetaId) {
    if (confirm('¿Estás seguro de duplicar esta receta?')) {
        fetch(`/dashboard/recetas/duplicar/${recetaId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {  // Fix: Changed "then data =>" to "then(data =>"
            if (data.success) {
                showToast(data.message, 'success');
                // Redirigir a la edición de la nueva receta
                setTimeout(() => {
                    editarReceta(data.receta.id);
                    // Recargar la página después de un tiempo para mostrar la nueva receta en la lista
                    setTimeout(() => window.location.reload(), 1000);
                }, 500);
            } else {
                showToast(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error al duplicar la receta', 'error');
        });
    }
}

// Toast para mensajes
function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast show align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : type === 'warning' ? 'warning' : 'info'}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 500);
    }, 5000);
}

// Crear contenedor para toasts si no existe
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '5000';
    document.body.appendChild(container);
    return container;
}

// Renderizar detalle de receta
function renderizarDetalleReceta(receta, ingredientes) {
    console.log(`Renderizando detalle de receta:`, receta);
    console.log(`Ingredientes:`, ingredientes);
    
    // Siempre establecer el ID de la receta actual, incluso si hay error
    currentRecetaId = receta.id;
    
    // Actualizar botones de acciones con el ID correcto
    const btnEditar = document.querySelector('#modalDetalleReceta .modal-footer button[onclick*="editarReceta"]');
    if (btnEditar) {
        btnEditar.setAttribute('onclick', `editarReceta(${receta.id})`);
    }
    
    const btnDuplicar = document.querySelector('#modalDetalleReceta .modal-footer button[onclick*="duplicarReceta"]');
    if (btnDuplicar) {
        btnDuplicar.setAttribute('onclick', `duplicarReceta(${receta.id})`);
    }
    
    // Obtener el contenedor
    const content = document.getElementById('detalleRecetaContent');
    
    // Si la receta tiene "Error en datos", mostrar un mensaje amigable pero mantener la funcionalidad
    if (receta.nombre === 'Error en datos') {
        // Mostrar mensaje de error pero mantener la posibilidad de editar
        content.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Algunos datos de esta receta están incompletos o tienen errores. 
                Puedes editarla para corregir la información.
            </div>
            <div class="card mb-3">
                <div class="card-header bg-light">
                    <h5 class="mb-0">Receta #${receta.id}</h5>
                </div>
                <div class="card-body">
                    <p class="text-muted">Los detalles no están disponibles debido a errores en los datos. 
                    Por favor, usa el botón "Editar" para corregir esta receta.</p>
                </div>
            </div>
            <h6 class="mb-2">Ingredientes:</h6>
            <div class="list-group mb-3">
                ${ingredientes && ingredientes.length ? ingredientes.map(ing => `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>${ing.insumo?.nombre || 'Ingrediente desconocido'}</strong>
                                <div class="text-muted small">
                                    ${ing.cantidad || 0} ${ing.insumo?.unidad_medida?.nombre || 'unidad'}
                                </div>
                            </div>
                            <span class="badge bg-primary rounded-pill">
                                $${(ing.costo_total || 0).toFixed(2)}
                            </span>
                        </div>
                    </div>
                `).join('') : '<div class="list-group-item">No hay ingredientes disponibles</div>'}
            </div>
        `;
        return;
    }
    
    // Calcular los costos de manera segura
    const costoTotal = parseFloat(receta.costo_total || 0);
    const precioVenta = parseFloat(receta.precio_venta || 0);
    const porciones = parseInt(receta.porciones || 1);
    const costoPorcion = porciones > 0 ? (costoTotal / porciones) : 0;
    
    console.log(`Costo total: $${costoTotal.toFixed(2)}`);
    console.log(`Precio de venta: $${precioVenta.toFixed(2)}`);
    console.log(`Costo por porción: $${costoPorcion.toFixed(2)}`);
    
    // Construir el HTML para mostrar la receta
    let html = `
        <div class="mb-4">
            <h5 class="border-bottom pb-2 mb-3">${receta.nombre || `Receta #${receta.id}`}</h5>
            
            <div class="row mb-3">
                <div class="col-md-6">
                    <div class="mb-2">
                        <span class="text-muted">Categoría:</span>
                        <span class="fw-medium">${receta.categoria?.nombre || 'Sin categoría'}</span>
                    </div>
                    <div class="mb-2">
                        <span class="text-muted">Tiempo de preparación:</span>
                        <span class="fw-medium">${receta.tiempo_preparacion || 0} min</span>
                    </div>
                    <div class="mb-2">
                        <span class="text-muted">Porciones:</span>
                        <span class="fw-medium">${porciones}</span>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-2">
                        <span class="text-muted">Costo total:</span>
                        <span class="fw-medium text-success">$${costoTotal.toFixed(2)}</span>
                    </div>
                    <div class="mb-2">
                        <span class="text-muted">Costo por porción:</span>
                        <span class="fw-medium text-success">$${costoPorcion.toFixed(2)}</span>
                    </div>
                    <div class="mb-2">
                        <span class="text-muted">Precio de venta:</span>
                        <span class="fw-medium text-primary">$${precioVenta.toFixed(2)}</span>
                    </div>
                </div>
            </div>
            
            ${receta.descripcion ? `
            <div class="mb-3">
                <p class="text-muted mb-1">Descripción:</p>
                <p>${receta.descripcion}</p>
            </div>
            ` : ''}
        </div>
    `;    
    
    // Listado de ingredientes
    html += `
        <div class="mb-4">
            <h6 class="border-bottom pb-2 mb-3">Ingredientes (${ingredientes ? ingredientes.length : 0})</h6>
            
            <div class="table-responsive">
                <table class="table table-sm table-hover">
                    <thead class="table-light">
                        <tr>
                            <th>Ingrediente</th>
                            <th>Tipo</th>
                            <th>Cantidad</th>
                            <th class="text-end">Costo</th>
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    let totalCostoIngredientes = 0;
    
    if (ingredientes && ingredientes.length > 0) {
        ingredientes.forEach(ingrediente => {
            try {
                console.log("Procesando ingrediente:", ingrediente);
                
                // Asegurarnos de que insumo existe y tiene todas las propiedades necesarias
                const insumo = ingrediente.insumo || {};
                const nombreInsumo = insumo.nombre || 'Sin nombre';
                const tipo = insumo.tipo || 'basico';
                
                // Determinar el nombre del tipo para mostrar
                let tipoNombre = 'Básico';
                let tipoBadgeColor = 'bg-primary';
                
                if (tipo === 'compuesto') {
                    tipoNombre = 'Compuesto';
                    tipoBadgeColor = 'bg-success';
                } else if (tipo === 'elaborado') {
                    tipoNombre = 'Elaborado';
                    tipoBadgeColor = 'bg-info';
                }
                
                // Asegurarnos de que la unidad de medida existe
                const unidadMedida = insumo.unidad_medida || { nombre: 'Unidad', abreviacion: 'Un' };
                const unidadNombre = unidadMedida.nombre || 'Unidad';
                const unidadAbrev = insumo.unidad_abrev || 'Un';
                
                // Parsear cantidad y costos
                const cantidad = parseFloat(ingrediente.cantidad || 0);
                const costoUnitario = parseFloat(ingrediente.costo_unitario || insumo.precio_unitario || 0);
                const costoTotal = parseFloat(ingrediente.costo_total || (cantidad * costoUnitario) || 0);
                
                totalCostoIngredientes += costoTotal;
                
                // Opcional
                const opcional = ingrediente.opcional || false;
                const claseFila = opcional ? 'table-warning' : '';
                const marcaOpcional = opcional ? '<span class="badge bg-warning text-dark ms-2">Opcional</span>' : '';
                
                html += `
                    <tr class="${claseFila}">
                        <td>
                            <div class="d-flex align-items-center">
                                ${nombreInsumo}
                                ${marcaOpcional}
                            </div>
                            ${ingrediente.notas ? `<small class="text-muted">${ingrediente.notas}</small>` : ''}
                        </td>
                        <td><span class="badge ${tipoBadgeColor}">${tipoNombre}</span></td>
                        <td>${cantidad.toFixed(2)} ${unidadAbrev}</td>
                        <td class="text-end">$${costoTotal.toFixed(2)}</td>
                    </tr>
                `;
            } catch (e) {
                console.error("Error procesando ingrediente:", e);
                // Agregar una fila de ingrediente con error
                html += `
                    <tr class="table-danger">
                        <td>
                            <div class="d-flex align-items-center">
                                Error en ingrediente
                                <span class="badge bg-danger ms-2">Error</span>
                            </div>
                        </td>
                        <td>-</td>
                        <td>-</td>
                        <td class="text-end">$0.00</td>
                    </tr>
                `;
            }
        });
    } else {
        html += `
            <tr>
                <td colspan="4" class="text-center text-muted py-3">
                    No hay ingredientes registrados para esta receta
                </td>
            </tr>
        `;
    }
    
    // Instrucciones
    if (receta.instrucciones) {
        html += `
            <div class="mb-4">
                <h6 class="border-bottom pb-2 mb-3">Instrucciones</h6>
                <div class="card">
                    <div class="card-body">
                        ${receta.instrucciones.replace(/\n/g, '<br>')}
                    </div>
                </div>
            </div>
        `;
    }
    
    content.innerHTML = html;
}

// Agregar ingrediente en el modal de edición
function agregarIngredienteEditar(ingredienteExistente = null) {
    console.log("Agregando ingrediente para edición:", ingredienteExistente);
    
    if (todosLosInsumos.length === 0) {
        console.error("Error: No hay insumos disponibles");
        showToast('No hay insumos disponibles', 'error');
        return;
    }
    
    contadorIngredientesEditar++;
    const container = document.getElementById('editarIngredientesContainer');
    
    // Ocultar alerta si es el primer ingrediente
    const alerta = document.getElementById('alertaIngredientesEditar');
    if (alerta) {
        alerta.style.display = 'none';
    }
    
    const id = `editar_ingrediente_${contadorIngredientesEditar}`;
    
    // Crear opciones agrupadas por tipo
    let opcionesInsumos = '<option value="">Seleccionar insumo</option>';
    
    // Extraer información del insumo si existe
    let insumoId = null;
    let cantidad = '1';
    let costoIngrediente = '0.00';
    let esOpcional = false;
    let notas = '';
    let unidadMedida = 'Und';
      if (ingredienteExistente) {
        // Si tenemos el objeto completo del ingrediente (de la API)
        if (ingredienteExistente.insumo && ingredienteExistente.insumo.id) {
            insumoId = ingredienteExistente.insumo.id;
            console.log(`Ingrediente existente con insumo ID: ${insumoId}`);
        } else if (ingredienteExistente.insumo_id) {
            // Si solo tenemos el ID del insumo
            insumoId = ingredienteExistente.insumo_id;
            console.log(`Ingrediente existente con insumo_id: ${insumoId}`);
        }
        
        // Obtener otros datos del ingrediente
        cantidad = ingredienteExistente.cantidad || cantidad;
        costoIngrediente = parseFloat(ingredienteExistente.costo || 0).toFixed(2);
        esOpcional = ingredienteExistente.opcional || false;
        notas = ingredienteExistente.notas || '';
        unidadMedida = ingredienteExistente.unidad || 'Und';
    }
    
    // Agrupar insumos por tipo
    const insumosPorTipo = {
        basico: todosLosInsumos.filter(i => i.tipo === 'basico'),
        compuesto: todosLosInsumos.filter(i => i.tipo === 'compuesto'),
        elaborado: todosLosInsumos.filter(i => i.tipo === 'elaborado')
    };
    
    // Crear grupos de opciones
    if (insumosPorTipo.basico.length > 0) {
        opcionesInsumos += '<optgroup label="Insumos Básicos">';
        insumosPorTipo.basico.forEach(insumo => {
            const selected = insumoId && insumoId == insumo.id ? 'selected' : '';
            opcionesInsumos += `<option value="${insumo.id}" data-tipo="${insumo.tipo}" data-precio="${insumo.precio_unitario}" data-unidad="${insumo.unidad_medida_nombre}" data-unidad-abrev="${insumo.unidad_abrev}" ${selected}>${insumo.nombre} (${insumo.codigo})</option>`;
        });
        opcionesInsumos += '</optgroup>';
    }
    
    if (insumosPorTipo.compuesto.length > 0) {
        opcionesInsumos += '<optgroup label="Insumos Compuestos">';
        insumosPorTipo.compuesto.forEach(insumo => {
            const selected = insumoId && insumoId == insumo.id ? 'selected' : '';
            opcionesInsumos += `<option value="${insumo.id}" data-tipo="${insumo.tipo}" data-precio="${insumo.precio_unitario}" data-unidad="${insumo.unidad_medida_nombre}" data-unidad-abrev="${insumo.unidad_abrev}" ${selected}>${insumo.nombre} (${insumo.codigo})</option>`;
        });
        opcionesInsumos += '</optgroup>';
    }
    
    if (insumosPorTipo.elaborado.length > 0) {
        opcionesInsumos += '<optgroup label="Insumos Elaborados">';
        insumosPorTipo.elaborado.forEach(insumo => {
            const selected = insumoId && insumoId == insumo.id ? 'selected' : '';
            opcionesInsumos += `<option value="${insumo.id}" data-tipo="${insumo.tipo}" data-precio="${insumo.precio_unitario}" data-unidad="${insumo.unidad_medida_nombre}" data-unidad-abrev="${insumo.unidad_abrev}" ${selected}>${insumo.nombre} (${insumo.codigo})</option>`;
        });
        opcionesInsumos += '</optgroup>';
    }
    
    // Crear fila de ingrediente
    const html = `
    <div id="${id}" class="row mb-2 align-items-end border-bottom pb-2">
        <div class="col-md-4">
            <label class="form-label small">Insumo</label>
            <select class="form-select form-select-sm" name="editar_ingrediente_insumo[]" onchange="actualizarInfoIngredienteEditar(this, '${id}')">
                ${opcionesInsumos}
            </select>
        </div>
        <div class="col-md-2">
            <label class="form-label small">Cantidad</label>
            <div class="input-group input-group-sm">
                <input type="number" class="form-control" name="editar_ingrediente_cantidad[]" step="0.01" min="0.01" value="${cantidad}" onchange="actualizarCostoIngredienteEditar(this, '${id}')">
                <span class="input-group-text unidad-medida">${unidadMedida}</span>
            </div>
        </div>
        <div class="col-md-2">
            <label class="form-label small">Costo</label>
            <div class="input-group input-group-sm">
                <span class="input-group-text">$</span>
                <input type="text" class="form-control costo-ingrediente" name="editar_ingrediente_costo[]" readonly value="${costoIngrediente}">
            </div>
        </div>
        <div class="col-md-2">
            <div class="form-check form-switch mt-4">
                <input class="form-check-input" type="checkbox" name="editar_ingrediente_opcional[]" ${esOpcional ? 'checked' : ''}>
                <label class="form-check-label small">Opcional</label>
            </div>
        </div>
        <div class="col-md-1">
            <label class="form-label small">Notas</label>
            <input type="text" class="form-control form-control-sm" name="editar_ingrediente_notas[]" value="${notas}" placeholder="Notas">
        </div>
        <div class="col-md-1">
            <button type="button" class="btn btn-sm btn-outline-danger mt-4" onclick="eliminarIngredienteEditar('${id}')">
                <i class="fas fa-trash-alt"></i>
            </button>
        </div>
    </div>
    `;
    
    // Agregar al container
    container.innerHTML += html;
    
    // Si tenemos un insumo ya seleccionado, actualizar su información
    if (insumoId) {
        setTimeout(() => {
            const select = document.querySelector(`#${id} select[name="editar_ingrediente_insumo[]"]`);
            if (select) {
                actualizarInfoIngredienteEditar(select, id);
                console.log(`Insumo ${insumoId} seleccionado y actualizado automáticamente`);
            }
        }, 100);
    }
      // Actualizar resumen de costos
    setTimeout(actualizarResumenCostosEditar, 200);
      console.log(`✅ Ingrediente ${id} agregado al formulario de edición`);
    return id;
}

// Cargar datos de edición
function cargarDatosEdicion(receta, ingredientes) {
    try {
        console.log('Iniciando carga de datos para edición', receta);
        console.log('Ingredientes a cargar:', ingredientes);
        
        // Cargar datos básicos de forma segura
        document.getElementById('editar_receta_id').value = receta.id;
        document.getElementById('editar_nombre').value = receta.nombre || '';
        
        // Establecer la categoría correcta si existe
        try {
            if (receta.categoria && receta.categoria.id) {
                document.getElementById('editar_categoria_id').value = receta.categoria.id;
            } else {
                document.getElementById('editar_categoria_id').value = '';
            }
        } catch (e) {
            console.error('Error al establecer categoría:', e);
            document.getElementById('editar_categoria_id').value = '';
        }
        
        // Establecer otros campos con manejo de errores
        try {
            document.getElementById('editar_descripcion').value = receta.descripcion || '';
        } catch (e) {
            console.error('Error al establecer descripción:', e);
            document.getElementById('editar_descripcion').value = '';
        }
        
        try {
            document.getElementById('editar_tiempo_preparacion').value = receta.tiempo_preparacion || 0;
        } catch (e) {
            console.error('Error al establecer tiempo de preparación:', e);
            document.getElementById('editar_tiempo_preparacion').value = 0;
        }
        
        try {
            document.getElementById('editar_porciones').value = receta.porciones || 1;
        } catch (e) {
            console.error('Error al establecer porciones:', e);
            document.getElementById('editar_porciones').value = 1;
        }
        
        try {
            // Precio de venta: asegurar que es un número válido o vacío
            const precio = parseFloat(receta.precio_venta);
            document.getElementById('editar_precio_venta').value = isNaN(precio) ? '' : precio.toFixed(2);
        } catch (e) {
            console.error('Error al establecer precio de venta:', e);
            document.getElementById('editar_precio_venta').value = '';
        }
        
        try {
            // Establecer instrucciones
            const instruccionesEditor = document.getElementById('editar_instrucciones');
            if (instruccionesEditor) {
                instruccionesEditor.value = receta.instrucciones || '';
            }
        } catch (e) {
            console.error('Error al establecer instrucciones:', e);
        }
        
        // Limpiar container de ingredientes
        const container = document.getElementById('editarIngredientesContainer');
        if (!container) {
            console.error('No se encontró el contenedor de ingredientes');
            showToast('Error al preparar el formulario de edición', 'error');
            return Promise.reject(new Error('Contenedor de ingredientes no encontrado'));
        }
        
        container.innerHTML = '';
        contadorIngredientesEditar = 0;
        
        // Verificar si hay ingredientes válidos
        if (!ingredientes || !Array.isArray(ingredientes) || ingredientes.length === 0) {
            console.log("No hay ingredientes para cargar");
            // Mostrar alerta de no ingredientes
            container.innerHTML = `
                <div id="alertaIngredientesEditar" class="alert alert-info">
                    <i class="fas fa-info-circle me-1"></i> Agrega ingredientes para tu receta
                </div>
            `;
            actualizarResumenCostosEditar();
            return Promise.resolve(false);
        }
        
        // Cargar ingredientes existentes
        console.log(`Cargando ${ingredientes.length} ingredientes existentes`);
        
        // Primero asegurémonos de que todos los insumos están cargados
        return cargarInsumos().then(() => {
            console.log("Insumos cargados correctamente, procediendo a agregar ingredientes");
            try {
                procesarIngredientesEdicion(ingredientes);
                // Actualizar costos una vez que todo está cargado
                setTimeout(actualizarResumenCostosEditar, 500);
                return true;
            } catch (e) {
                console.error('Error al procesar ingredientes:', e);
                showToast('Error al cargar algunos ingredientes', 'warning');
                
                // Asegurar que el contenedor no quede vacío
                if (container.innerHTML === '') {
                    container.innerHTML = `
                        <div id="alertaIngredientesEditar" class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle me-1"></i> Hubo un error al cargar los ingredientes. Puedes agregar nuevos ingredientes.
                        </div>
                    `;
                }
                
                return false;
            }
        }).catch(error => {
            console.error('Error al cargar insumos:', error);
            showToast('Error al cargar lista de insumos', 'error');
            return false;
        });
    } catch (error) {
        console.error('Error al cargar datos de edición:', error);
        showToast('Error al cargar datos de edición', 'error');
        return Promise.reject(error);
    }
}

// Función auxiliar para procesar ingredientes en la edición
function procesarIngredientesEdicion(ingredientes) {
    console.log("Procesando ingredientes para edición:", ingredientes);
    
    // Filtrar ingredientes nulos o inválidos
    const ingredientesValidos = ingredientes.filter(ing => ing && ing.insumo && ing.insumo.id);
    
    if (ingredientesValidos.length === 0) {
        console.warn("No hay ingredientes válidos para procesar");
        throw new Error("No hay ingredientes válidos");
    }
    
    ingredientesValidos.forEach(ingrediente => {
        try {
            // Obtener datos del ingrediente
            const insumo = ingrediente.insumo || {};
            const insumoId = insumo.id;
            
            if (!insumoId) {
                console.warn("Ingrediente sin ID de insumo, omitiendo:", ingrediente);
                return; // Saltar este ingrediente
            }
            
            // Parsear valores numéricos de forma segura
            const cantidad = parseFloat(ingrediente.cantidad || 0);
            const opcional = Boolean(ingrediente.opcional);
            const notas = ingrediente.notas || '';
            
            // Parsear costos de forma segura
            let costoUnitario = 0;
            try {
                costoUnitario = parseFloat(insumo.precio_unitario || ingrediente.costo_unitario || 0);
            } catch (e) {
                console.warn("Error al parsear costo unitario:", e);
                costoUnitario = 0;
            }
            
            let costoTotal = 0;
            try {
                costoTotal = parseFloat(ingrediente.costo_total || 0);
                if (costoTotal === 0 && cantidad > 0 && costoUnitario > 0) {
                    costoTotal = cantidad * costoUnitario;
                }
            } catch (e) {
                console.warn("Error al parsear costo total:", e);
                costoTotal = 0;
            }
            
            console.log(`Agregando ingrediente: ${insumo.nombre}, ID: ${insumoId}, Cantidad: ${cantidad}, Costo: ${costoTotal}`);
            
            // Obtener unidad de medida de forma segura
            let unidad = 'Und';
            if (insumo.unidad_abrev) {
                unidad = insumo.unidad_abrev;
            } else if (insumo.unidad_medida && insumo.unidad_medida.nombre) {
                unidad = insumo.unidad_medida.nombre;
            }
            
            // Preparar información completa del ingrediente para agregarIngredienteEditar
            const ingredienteCompleto = {
                insumo_id: insumoId,
                insumo: insumo,
                cantidad: cantidad,
                opcional: opcional,
                notas: notas,
                costo: costoTotal,
                unidad: unidad
            };
            
            // Agregar el ingrediente con toda su información
            agregarIngredienteEditar(ingredienteCompleto);
        } catch (e) {
            console.error("Error procesando ingrediente individual:", e);
            // Continuar con el siguiente ingrediente
        }
    });
    
    // Actualizar resumen de costos después de agregar todos los ingredientes
    setTimeout(actualizarResumenCostosEditar, 300);
}

// Cargar insumos
function cargarInsumos() {
    // Devolver una Promise para poder encadenar acciones
    return new Promise((resolve, reject) => {
        // Si ya tenemos insumos cargados, resolvemos inmediatamente
        if (todosLosInsumos.length > 0) {
            console.log(`✅ Usando insumos ya cargados: ${todosLosInsumos.length} insumos`);
            resolve(todosLosInsumos);
            return;
        }
        
        // Mostrar spinner de carga
        console.log('🔄 Cargando insumos desde el servidor...');
        
        // Realizar petición para obtener todos los insumos
        fetch('/dashboard/recetas/insumos/todos/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success && data.insumos) {
                // Guardar insumos en variable global
                todosLosInsumos = data.insumos;
                console.log(`✅ Insumos cargados: ${todosLosInsumos.length} insumos disponibles`);
                
                // Mostrar estadísticas por tipo
                const stats = {
                    basico: data.insumos.filter(i => i.tipo === 'basico').length,
                    compuesto: data.insumos.filter(i => i.tipo === 'compuesto').length,
                    elaborado: data.insumos.filter(i => i.tipo === 'elaborado').length
                };
                console.log(`📊 Básicos: ${stats.basico}, Compuestos: ${stats.compuesto}, Elaborados: ${stats.elaborado}`);
                
                // Resolver la promesa con los insumos
                resolve(todosLosInsumos);
            } else {
                console.error('❌ Error cargando insumos:', data.message);
                showToast('Error cargando insumos: ' + (data.message || 'Error desconocido'), 'error');
                reject(new Error(data.message || 'Error desconocido'));
            }
        })
        .catch(error => {
            console.error('❌ Error:', error);
            showToast('Error de conexión al cargar insumos', 'error');
            reject(error);
        });
    });
}

// Agregar ingrediente en creación
function agregarIngrediente() {
    if (todosLosInsumos.length === 0) {
        showToast('No hay insumos disponibles', 'error');
        return;
    }
    
    contadorIngredientes++;
    const container = document.getElementById('ingredientesContainer');
    
    // Ocultar alerta si es el primer ingrediente
    const alerta = document.getElementById('alertaIngredientes');
    if (alerta) {
        alerta.style.display = 'none';
    }
    
    const id = `ingrediente_${contadorIngredientes}`;
    
    // Crear opciones agrupadas por tipo
    let opcionesInsumos = '<option value="">Seleccionar insumo</option>';
    
    // Agrupar insumos por tipo
    const insumosPorTipo = {
        basico: todosLosInsumos.filter(i => i.tipo === 'basico'),
        compuesto: todosLosInsumos.filter(i => i.tipo === 'compuesto'),
        elaborado: todosLosInsumos.filter(i => i.tipo === 'elaborado')
    };
    
    // Crear grupos de opciones
    if (insumosPorTipo.basico.length > 0) {
        opcionesInsumos += '<optgroup label="Insumos Básicos">';
        insumosPorTipo.basico.forEach(insumo => {
            opcionesInsumos += `<option value="${insumo.id}" data-tipo="${insumo.tipo}" data-precio="${insumo.precio_unitario}" data-unidad="${insumo.unidad_medida_nombre}" data-unidad-abrev="${insumo.unidad_abrev}">${insumo.nombre} (${insumo.codigo})</option>`;
        });
        opcionesInsumos += '</optgroup>';
    }
    
    if (insumosPorTipo.compuesto.length > 0) {
        opcionesInsumos += '<optgroup label="Insumos Compuestos">';
        insumosPorTipo.compuesto.forEach(insumo => {
            opcionesInsumos += `<option value="${insumo.id}" data-tipo="${insumo.tipo}" data-precio="${insumo.precio_unitario}" data-unidad="${insumo.unidad_medida_nombre}" data-unidad-abrev="${insumo.unidad_abrev}">${insumo.nombre} (${insumo.codigo})</option>`;
        });
        opcionesInsumos += '</optgroup>';
    }
    
    if (insumosPorTipo.elaborado.length > 0) {
        opcionesInsumos += '<optgroup label="Insumos Elaborados">';
        insumosPorTipo.elaborado.forEach(insumo => {
            opcionesInsumos += `<option value="${insumo.id}" data-tipo="${insumo.tipo}" data-precio="${insumo.precio_unitario}" data-unidad="${insumo.unidad_medida_nombre}" data-unidad-abrev="${insumo.unidad_abrev}">${insumo.nombre} (${insumo.codigo})</option>`;
        });
        opcionesInsumos += '</optgroup>';
    }
    
    // Crear fila de ingrediente
    const html = `
    <div id="${id}" class="row mb-2 align-items-end border-bottom pb-2">
        <div class="col-md-5">
            <label class="form-label small">Insumo</label>
            <select class="form-select form-select-sm" name="ingrediente_insumo[]" onchange="actualizarInfoIngrediente(this, '${id}')">
                ${opcionesInsumos}
            </select>
        </div>
        <div class="col-md-3">
            <label class="form-label small">Cantidad</label>
            <div class="input-group input-group-sm">
                <input type="number" class="form-control" name="ingrediente_cantidad[]" step="0.01" min="0.01" value="1" onchange="actualizarCostoIngrediente(this, '${id}')">
                <span class="input-group-text unidad-medida">Und</span>
            </div>
        </div>
        <div class="col-md-3">
            <label class="form-label small">Costo</label>
            <div class="input-group input-group-sm">
                <span class="input-group-text">$</span>
                <input type="text" class="form-control costo-ingrediente" name="ingrediente_costo[]" readonly value="0.00">
            </div>
        </div>
        <div class="col-md-1">
            <button type="button" class="btn btn-sm btn-outline-danger" onclick="eliminarIngrediente('${id}')">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    </div>
    `;
    
    // Agregar al container
    container.insertAdjacentHTML('beforeend', html);
}

// Actualizar información del ingrediente
function actualizarInfoIngrediente(select, id) {
    const row = document.getElementById(id);
    const option = select.options[select.selectedIndex];
    const unidadSpan = row.querySelector('.unidad-medida');
    const inputCantidad = row.querySelector('input[name="ingrediente_cantidad[]"]');
    
    if (option.value) {
        // Verificar si el ingrediente ya está seleccionado en otro campo
        const insumosSeleccionados = Array.from(document.querySelectorAll('select[name="ingrediente_insumo[]"]'))
            .filter(s => s !== select && s.value === option.value);
        
        if (insumosSeleccionados.length > 0) {
            showToast('Este ingrediente ya está agregado a la receta', 'warning');
            select.value = '';
            unidadSpan.textContent = 'Und';
            row.querySelector('.costo-ingrediente').value = '0.00';
            actualizarResumenCostos();
            return;
        }
        
        // Obtener insumo seleccionado de la lista global para asegurar que tenemos todos los datos
        const insumoSeleccionado = todosLosInsumos.find(i => i.id.toString() === option.value);
        
        // Usar la abreviación de la unidad si está disponible
        if (insumoSeleccionado) {
            unidadSpan.textContent = insumoSeleccionado.unidad_abrev || 'Und';
        } else {
            // Usar el dataset como fallback
            const unidadAbrev = option.dataset.unidadAbrev || option.dataset.unidad || 'Und';
            unidadSpan.textContent = unidadAbrev;
        }
        
        // Actualizar el costo del ingrediente
        actualizarCostoIngrediente(inputCantidad, id);
    } else {
        unidadSpan.textContent = 'Und';
        row.querySelector('.costo-ingrediente').value = '0.00';
        actualizarResumenCostos();
    }
}

// Actualizar información del ingrediente en el formulario de edición
function actualizarInfoIngredienteEditar(select, id) {
    const row = document.getElementById(id);
    const option = select.options[select.selectedIndex];
    const unidadSpan = row.querySelector('.unidad-medida');
    const inputCantidad = row.querySelector('input[name="editar_ingrediente_cantidad[]"]');
    
    if (option.value) {
        // Verificar si el ingrediente ya está seleccionado en otro campo
        const insumosSeleccionados = Array.from(document.querySelectorAll('select[name="editar_ingrediente_insumo[]"]'))
            .filter(s => s !== select && s.value === option.value);
        
        if (insumosSeleccionados.length > 0) {
            showToast('Este ingrediente ya está agregado a la receta', 'warning');
            select.value = '';
            unidadSpan.textContent = 'Und';
            row.querySelector('.costo-ingrediente').value = '0.00';
            actualizarResumenCostosEditar();
            return;
        }
        
        // Obtener insumo seleccionado de la lista global para asegurar que tenemos todos los datos
        const insumoSeleccionado = todosLosInsumos.find(i => i.id.toString() === option.value);
        
        // Usar la abreviación de la unidad si está disponible
        if (insumoSeleccionado) {
            unidadSpan.textContent = insumoSeleccionado.unidad_abrev || 'Und';
        } else {
            // Usar el dataset como fallback
            const unidadAbrev = option.dataset.unidadAbrev || option.dataset.unidad || 'Und';
            unidadSpan.textContent = unidadAbrev;
        }
        
        // Actualizar el costo del ingrediente
        actualizarCostoIngredienteEditar(inputCantidad, id);
    } else {
        unidadSpan.textContent = 'Und';
        row.querySelector('.costo-ingrediente').value = '0.00';
        actualizarResumenCostosEditar();
    }
}

// Actualizar costo del ingrediente
function actualizarCostoIngrediente(input, id) {
    const row = document.getElementById(id);
    const select = row.querySelector('select[name="ingrediente_insumo[]"]');
    const option = select.options[select.selectedIndex];
    const costoInput = row.querySelector('.costo-ingrediente');
    
    if (option.value && input.value > 0) {
        const precioUnitario = parseFloat(option.dataset.precio);
        const cantidad = parseFloat(input.value);
        const costo = precioUnitario * cantidad;
        costoInput.value = costo.toFixed(2);
    } else {
        costoInput.value = '0.00';
    }
    
    actualizarResumenCostos();
}

// Actualizar costo del ingrediente en edición
function actualizarCostoIngredienteEditar(input, id) {
    try {
        const row = document.getElementById(id);
        const select = row.querySelector('select[name="editar_ingrediente_insumo[]"]');
        const option = select.options[select.selectedIndex];
        const costoInput = row.querySelector('.costo-ingrediente');
        
        if (option.value && input.value > 0) {
            const precioUnitario = parseFloat(option.dataset.precio);
            const cantidad = parseFloat(input.value);
            const costo = precioUnitario * cantidad;
            costoInput.value = costo.toFixed(2);
        } else {
            costoInput.value = '0.00';
        }
        
        // Llamar a la función para actualizar el resumen
        actualizarResumenCostosEditar();
    } catch (error) {
        console.error('Error al actualizar costo del ingrediente en edición:', error);
    }
}

// Función para actualizar el resumen de costos en el formulario de edición
function actualizarResumenCostosEditar() {
    try {
        console.log('Actualizando resumen de costos para edición...');
        
        // Obtener todos los ingredientes
        const ingredientes = document.querySelectorAll('#editarIngredientesContainer .row');
        let costoTotal = 0;
        
        // Sumar los costos de todos los ingredientes
        ingredientes.forEach(ingrediente => {
            const costoInput = ingrediente.querySelector('.costo-ingrediente');
            if (costoInput && costoInput.value) {
                costoTotal += parseFloat(costoInput.value);
            }
        });
        
        // Actualizar el costo de ingredientes
        const costoIngredientesElement = document.getElementById('editarCostoIngredientes');
        if (costoIngredientesElement) {
            costoIngredientesElement.textContent = `$${costoTotal.toFixed(2)}`;
        }
          // Actualizar el costo total
        const costoTotalElement = document.getElementById('editar_costoTotal');
        if (costoTotalElement) {
            costoTotalElement.value = costoTotal.toFixed(2);
        }
        
        // Actualizar el costo por porción
        const costoPorcionElement = document.getElementById('editar_costoPorcion');
        const porcionesInput = document.getElementById('editar_porciones');
        if (costoPorcionElement && porcionesInput && porcionesInput.value > 0) {
            const porciones = parseInt(porcionesInput.value);
            const costoPorcion = costoTotal / porciones;
            costoPorcionElement.value = costoPorcion.toFixed(2);
        } else if (costoPorcionElement) {
            costoPorcionElement.value = '0.00';
        }
        
        console.log(`Resumen actualizado: Costo total $${costoTotal.toFixed(2)}`);
    } catch (error) {
        console.error('Error al actualizar resumen de costos para edición:', error);
    }
}

// También parece que falta la función actualizarResumenCostos para creación
// Vamos a implementarla para asegurar consistencia:
function actualizarResumenCostos() {
    try {
        console.log('Actualizando resumen de costos para creación...');
        
        // Obtener todos los ingredientes
        const ingredientes = document.querySelectorAll('#ingredientesContainer .row');
        let costoTotal = 0;
        
        // Sumar los costos de todos los ingredientes
        ingredientes.forEach(ingrediente => {
            const costoInput = ingrediente.querySelector('.costo-ingrediente');
            if (costoInput && costoInput.value) {
                costoTotal += parseFloat(costoInput.value);
            }
        });
        
        // Actualizar el costo de ingredientes
        const costoIngredientesElement = document.getElementById('costoIngredientes');
        if (costoIngredientesElement) {
            costoIngredientesElement.textContent = `$${costoTotal.toFixed(2)}`;
        }
          // Actualizar el costo total
        const costoTotalElement = document.getElementById('costoTotal');
        if (costoTotalElement) {
            costoTotalElement.value = costoTotal.toFixed(2);
        }
        
        // Actualizar el costo por porción
        const costoPorcionElement = document.getElementById('costoPorcion');
        const porcionesInput = document.getElementById('porciones');
        if (costoPorcionElement && porcionesInput && porcionesInput.value > 0) {
            const porciones = parseInt(porcionesInput.value);
            const costoPorcion = costoTotal / porciones;
            costoPorcionElement.value = costoPorcion.toFixed(2);
        } else if (costoPorcionElement) {
            costoPorcionElement.value = '0.00';
        }
        
        console.log(`Resumen actualizado: Costo total $${costoTotal.toFixed(2)}`);
    } catch (error) {
        console.error('Error al actualizar resumen de costos para creación:', error);
    }
}

// Función para actualizar una receta existente
function actualizarReceta() {
    console.log('🔄 Actualizando receta...');
    
    // Verificar que haya ingredientes
    const ingredientesContainer = document.getElementById('editarIngredientesContainer');
    const ingredientes = ingredientesContainer.querySelectorAll('.row');
    
    if (ingredientes.length === 0) {
        showToast('⚠️ Debe agregar al menos un ingrediente', 'warning');
        return;
    }
    // Verificar que todos los ingredientes tengan insumo seleccionado
    let todosValidos = true;
    ingredientes.forEach(ing => {
        const selectInsumo = ing.querySelector('select[name="editar_ingrediente_insumo[]"]');
        if (selectInsumo && !selectInsumo.value) {
            todosValidos = false;
            selectInsumo.classList.add('is-invalid');
        } else if (selectInsumo) {
            selectInsumo.classList.remove('is-invalid');
        }
    });
    
    if (!todosValidos) {
        showToast('⚠️ Todos los ingredientes deben tener un insumo seleccionado', 'warning');
        return;
    }
    
    // Obtener datos del formulario
    const form = document.getElementById('formEditarReceta');
    if (!form) {
        console.error('No se encontró el formulario formEditarReceta');
        showToast('❌ Error: No se encontró el formulario', 'error');
        return;
    }
    
    const formData = new FormData(form);
    
    // Obtener ID de la receta
    const recetaIdElement = document.getElementById('editar_receta_id');
    if (!recetaIdElement || !recetaIdElement.value) {
        showToast('❌ Error: No se encontró el ID de la receta', 'error');
        return;
    }
    const recetaId = recetaIdElement.value;    // Añadir el costo total calculado al formData - Con verificación para evitar errores
    const costoTotalElement = document.getElementById('editar_costoTotal');
    let costoTotal = 0;
    
    if (costoTotalElement && costoTotalElement.value) {
        costoTotal = parseFloat(costoTotalElement.value) || 0;
    } else {
        console.warn('No se encontró el elemento editar_costoTotal, usando costo 0');
    }
    
    formData.append('costo_total', costoTotal);
    
    // Deshabilitar el botón de envío - Con verificación para evitar errores
    const submitBtn = form.querySelector('button[type="submit"]');
    let originalBtnText = 'Actualizar Receta';
    
    if (submitBtn) {
        originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Actualizando...';
    } else {
        console.warn('No se encontró el botón de envío en el formulario');
    }
    
    // Enviar datos
    fetch(`/dashboard/recetas/editar/${recetaId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('✅ ' + data.message, 'success');
            
            // Cerrar el modal de edición
            const modalElement = document.getElementById('modalEditarReceta');
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();

            // Recargar la página para actualizar la lista de recetas
            window.location.reload();
        } else {
            showToast('❌ ' + data.message, 'error');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('❌ Error de conexión', 'error');
    });
}

// Función para guardar receta nueva
function guardarReceta(event) {
    if (event) {
        event.preventDefault();
    }
    
    console.log('💾 Guardando nueva receta...');
    
    // Verificar que haya ingredientes
    const ingredientesContainer = document.getElementById('ingredientesContainer');
    const ingredientes = ingredientesContainer.querySelectorAll('.row');
    
    if (ingredientes.length === 0) {
        showToast('⚠️ Debe agregar al menos un ingrediente', 'warning');
        return;
    }
    
    // Verificar que todos los ingredientes tengan insumo seleccionado
    let todosValidos = true;
    ingredientes.forEach(ing => {
        const selectInsumo = ing.querySelector('select[name="ingrediente_insumo[]"]');
        if (selectInsumo && !selectInsumo.value) {
            todosValidos = false;
            selectInsumo.classList.add('is-invalid');
        } else if (selectInsumo) {
            selectInsumo.classList.remove('is-invalid');
        }
    });
    
    if (!todosValidos) {
        showToast('⚠️ Todos los ingredientes deben tener un insumo seleccionado', 'warning');
        return;
    }
    
    try {
        // Obtener datos del formulario
        const form = document.getElementById('formCrearReceta');
        const formData = new FormData(form);
        
        // Verificar campos obligatorios
        const nombre = formData.get('nombre');
        const categoriaId = formData.get('categoria_id');
        const tiempoPreparacion = formData.get('tiempo_preparacion');
        const porciones = formData.get('porciones');
        const precioVenta = formData.get('precio_venta');
        
        if (!nombre) {
            showToast('⚠️ El nombre de la receta es obligatorio', 'warning');
            return;
        }
        
        if (!categoriaId) {
            showToast('⚠️ Debe seleccionar una categoría', 'warning');
            return;
        }
        
        if (!tiempoPreparacion || tiempoPreparacion < 1) {
            showToast('⚠️ El tiempo de preparación debe ser mayor a 0', 'warning');
            return;
        }
        
        if (!porciones || porciones < 1) {
            showToast('⚠️ El número de porciones debe ser mayor a 0', 'warning');
            return;
        }
        
        if (!precioVenta || precioVenta <= 0) {
            showToast('⚠️ Debe ingresar un precio de venta válido', 'warning');
            return;
        }
        
        // Añadir el costo total calculado al formData
        const costoTotalInput = document.getElementById('costoTotal');
        const costoTotal = costoTotalInput ? parseFloat(costoTotalInput.value || '0') : 0;
        formData.append('costo_total', costoTotal);
        
        // Verificar que se hayan añadido los ingredientes correctamente
        const insumoIds = formData.getAll('ingrediente_insumo[]');
        const cantidades = formData.getAll('ingrediente_cantidad[]');
        
        if (insumoIds.length === 0 || cantidades.length === 0) {
            showToast('⚠️ Error al procesar los ingredientes', 'warning');
            console.error('Error: No se encontraron ingredientes en el FormData');
            return;
        }
        
        console.log(`Procesando ${insumoIds.length} ingredientes`);
        
        // Deshabilitar el botón de envío
        const submitBtn = document.querySelector('button[onclick="guardarReceta(event)"]');
        let originalBtnText = submitBtn ? submitBtn.innerHTML : 'Guardar Receta';
        
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Guardando...';
            console.log('Botón de guardar encontrado y deshabilitado');
        }

        // Enviar datos
        fetch('/dashboard/recetas/crear/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showToast('✅ ' + data.message, 'success');
                
                // Cerrar el modal de creación
                const modalElement = document.getElementById('modalCrearReceta');
                const modal = bootstrap.Modal.getInstance(modalElement);
                modal.hide();

                console.log("Receta guardada con éxito, actualizando lista...");
                
                // Retrasar un poco la actualización para dar tiempo a la BD
                setTimeout(() => {
                    // Actualizar la lista en lugar de recargar la página
                    actualizarListaRecetas();
                }, 500);
            }else {
                console.error('Error del servidor:', data.message);
                showToast('❌ ' + (data.message || 'Error al guardar la receta'), 'error');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnText;
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('❌ ' + (error.message || 'Error de conexión'), 'error');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        });
    } catch (error) {
        console.error('Error inesperado:', error);
        showToast('❌ Error inesperado', 'error');
        const submitBtn = document.querySelector('button[onclick="guardarReceta(event)"]');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Guardar Receta';
        }
    }
}

// Función para actualizar la lista de recetas
function actualizarListaRecetas() {
    console.log('🔄 Actualizando lista de recetas...');
    
    // Mostrar indicador de carga
    const tableContainer = document.querySelector('.table-responsive');
    if (tableContainer) {
        tableContainer.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Actualizando lista...</span>
                </div>
                <p class="mt-2 text-muted">Actualizando lista de recetas...</p>
            </div>
        `;
    }
    
    fetch('/dashboard/recetas/?ajax=1', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Cache-Control': 'no-cache, no-store, must-revalidate'
        }
    })
    .then(response => response.text())
    .then(html => {
        console.log('Respuesta HTML recibida, procesando...');
        
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // Actualizar la tabla de recetas
        const nuevaTabla = doc.querySelector('.table-responsive');
        const tablaActual = document.querySelector('.table-responsive');
        
        if (nuevaTabla && tablaActual) {
            tablaActual.innerHTML = nuevaTabla.innerHTML;
            console.log('✅ Tabla de recetas actualizada');
        } else {
            console.error('No se pudo encontrar la tabla para actualizar');
            // Intentar recargar la página como fallback
            location.reload();
            return;
        }
        
        // Actualizar las estadísticas
        const nuevasEstadisticas = doc.querySelectorAll('.stats-card');
        const estadisticasActuales = document.querySelectorAll('.stats-card');
        
        if (nuevasEstadisticas.length > 0 && estadisticasActuales.length > 0) {
            nuevasEstadisticas.forEach((nueva, index) => {
                if (estadisticasActuales[index]) {
                    estadisticasActuales[index].innerHTML = nueva.innerHTML;
                }
            });
            console.log('✅ Estadísticas actualizadas');
        } else {
            console.warn('No se encontraron estadísticas para actualizar');
        }
        
        console.log('✅ Lista de recetas actualizada completamente');
    })
    .catch(error => {
        console.error('Error al actualizar la lista:', error);
        showToast('❌ Error al actualizar la lista de recetas. La página se recargará.', 'error');
        
        // Recargar la página como último recurso
        setTimeout(() => {
            location.reload();
        }, 1500);
    });
}

// Función para eliminar ingrediente
function eliminarIngrediente(id) {
    const elemento = document.getElementById(id);
    if (elemento) {
        elemento.remove();
        actualizarResumenCostos();
          // Mostrar alerta si no quedan ingredientes
        const container = document.getElementById('ingredientesContainer');
        const ingredientes = container.querySelectorAll('.row');
        if (ingredientes.length === 0) {
            container.innerHTML = `
                <div id="alertaIngredientes" class="alert alert-info">
                    <i class="fas fa-info-circle me-1"></i> Agrega ingredientes para tu receta
                </div>
            `;
        }
    }
}

// Función para eliminar ingrediente en edición
function eliminarIngredienteEditar(id) {
    const elemento = document.getElementById(id);
    if (elemento) {
        elemento.remove();
        actualizarResumenCostosEditar();
        
        // Mostrar alerta si no quedan ingredientes
        const container = document.getElementById('editarIngredientesContainer');
        const ingredientes = container.querySelectorAll('.row');
        if (ingredientes.length === 0) {
            container.innerHTML = `
                <div id="alertaIngredientesEditar" class="alert alert-info">
                    <i class="fas fa-info-circle me-1"></i> Agrega ingredientes para tu receta
                </div>
            `;
        }
    }
}

// Función para eliminar receta
function eliminarReceta(recetaId, nombre) {
    if (confirm(`¿Estás seguro de que quieres eliminar la receta "${nombre}"?`)) {
        // Obtener el token CSRF
        let csrfToken = '';
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput) {
            csrfToken = csrfInput.value;
        } else {
            console.error('No se encontró el token CSRF');
            showToast('❌ Error: No se encontró el token CSRF. Por favor recarga la página.', 'error');
            return;
        }

        console.log(`🗑️ Eliminando receta ID: ${recetaId} - "${nombre}"`);
        
        // Mostrar indicador de carga
        showToast('⏳ Eliminando receta...', 'info');
        
        fetch(`/dashboard/recetas/eliminar/${recetaId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin',
            body: JSON.stringify({}) // Enviar un objeto vacío para asegurar que es un POST válido
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('Receta no encontrada');
                } else if (response.status === 403) {
                    throw new Error('No tienes permiso para eliminar esta receta');
                } else {
                    throw new Error(`Error en el servidor (${response.status})`);
                }
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showToast('✅ ' + data.message, 'success');
                // Recargar la página después de un breve retraso
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showToast('❌ ' + (data.message || 'Error al eliminar la receta'), 'error');
                console.error('Error al eliminar receta:', data);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('❌ Error al eliminar la receta: ' + error.message, 'error');
        });
    }
}

// Función para cargar categorías de recetas
function cargarCategoriasRecetas() {
    const container = document.getElementById('listaCategorias');
    
    // Mostrar cargando
    container.innerHTML = `
        <div class="text-center py-3">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="mt-2 text-muted">Cargando categorías...</p>
        </div>
    `;
    
    fetch('/dashboard/recetas/categorias/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            let html = '';
            
            if (data.categorias.length === 0) {
                html = `
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle"></i> No hay categorías creadas aún.
                    </div>
                `;            } else {
                data.categorias.forEach((categoria, index) => {
                    html += `
                        <div class="list-group-item d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="mb-1">${categoria.nombre}</h6>
                                <small class="text-muted">Código: ${categoria.codigo}</small>
                                ${categoria.descripcion ? `<p class="mb-1">${categoria.descripcion}</p>` : ''}
                                <small class="text-success">Estado: ${categoria.activa ? 'Activa' : 'Inactiva'}</small>
                            </div>
                            <div class="btn-group">
                                <button class="btn btn-outline-primary btn-sm" onclick="editarCategoriaReceta(${categoria.id}, '${categoria.codigo}', '${categoria.nombre}', '${categoria.descripcion || ''}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-outline-danger btn-sm" onclick="eliminarCategoriaReceta(${categoria.id}, '${categoria.nombre}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        ${index < data.categorias.length - 1 ? '<hr class="my-2 mx-3 border-secondary-subtle opacity-50">' : ''}
                    `;
                });
            }
            
            container.innerHTML = html;
        } else {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i> Error: ${data.message}
                </div>
            `;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        container.innerHTML = `

            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i> Error de conexión
            </div>
        `;
    });
}

// Función para crear categoría de receta
function crearCategoriaReceta() {
    const form = document.getElementById('formCrearCategoria');
    const formData = new FormData(form);
    
    fetch('/dashboard/recetas/categorias/crear/', {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('✅ ' + data.message, 'success');
            form.reset();
            cargarCategoriasRecetas();
            // Actualizar selectores en modales de recetas
            actualizarSelectoresCategorias();
        } else {
            showToast('❌ ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('❌ Error de conexión', 'error');
    });
}

// Función para editar categoría de receta
function editarCategoriaReceta(id, codigo, nombre, descripcion) {
    const modal = new bootstrap.Modal(document.getElementById('modalEditarCategoria'));
    
    // Llenar formulario
    document.getElementById('editar_categoria_id').value = id;
    document.getElementById('editar_categoria_codigo').value = codigo;
    document.getElementById('editar_categoria_nombre').value = nombre;
    document.getElementById('editar_categoria_descripcion').value = descripcion;
    
    modal.show();
}

// Función para actualizar categoría de receta
function actualizarCategoriaReceta() {
    const form = document.getElementById('formEditarCategoria');
    const formData = new FormData(form);
    const categoriaId = document.getElementById('editar_categoria_id').value;
    
    fetch(`/dashboard/recetas/categorias/editar/${categoriaId}/`, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('✅ ' + data.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('modalEditarCategoria')).hide();
            cargarCategoriasRecetas();
            // Actualizar selectores en modales de recetas
            actualizarSelectoresCategorias();
        } else {
            showToast('❌ ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('❌ Error de conexión', 'error');
    });
}

// Función para eliminar categoría de receta
function eliminarCategoriaReceta(id, nombre) {
    if (confirm(`¿Estás seguro de eliminar la categoría "${nombre}"?\n\nEsta acción no se puede deshacer.`)) {
        fetch(`/dashboard/recetas/categorias/eliminar/${id}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('✅ ' + data.message, 'success');
                cargarCategoriasRecetas();
                // Actualizar selectores en modales de recetas
                actualizarSelectoresCategorias();
            } else {
                showToast('❌ ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('❌ Error de conexión', 'error');
        });
    }
}

// Función para cargar categorías en los selectores al inicializar
function cargarCategoriasEnSelectores() {
    actualizarSelectoresCategorias();
}

// Función para actualizar los selectores de categorías en los formularios de recetas
async function actualizarSelectoresCategorias() {
    try {
        console.log('🔄 Actualizando selectores de categorías...');
        
        const response = await fetch('/dashboard/recetas/categorias/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success && data.categorias) {
            // Actualizar selector de crear receta
            const selectorCrear = document.getElementById('categoria_id');
            
            if (selectorCrear) {
                selectorCrear.innerHTML = '<option value="">Seleccionar categoría...</option>';
                data.categorias.forEach(categoria => {
                    selectorCrear.innerHTML += `<option value="${categoria.id}">${categoria.nombre}</option>`;
                });
            }
            
            // Actualizar selector de editar receta
            const selectorEditar = document.getElementById('editar_categoria_id');
            
            if (selectorEditar) {
                selectorEditar.innerHTML = '<option value="">Seleccionar categoría...</option>';
                data.categorias.forEach(categoria => {
                    selectorEditar.innerHTML += `<option value="${categoria.id}">${categoria.nombre}</option>`;
                });
            }
            
            console.log('✅ Selectores de categorías actualizados');
            return data.categorias;
        } else {
            console.error('Error al cargar categorías:', data.message);
            showToast(data.message || 'Error al cargar categorías', 'error');
            throw new Error(data.message || 'Error al cargar categorías');
        }
    } catch (error) {
        console.error('Error actualizando selectores:', error);
        showToast('Error al actualizar selectores de categorías', 'error');
        throw error;      }
}

// Función para abrir el modal de gestión de categorías
function abrirModalCategorias() {
    console.log('🔍 Abriendo modal para gestionar categorías de recetas');
    
    // Cargar las categorías actuales
    cargarCategoriasRecetas();
    
    // Abrir el modal
    const modal = new bootstrap.Modal(document.getElementById('modalCategorias'));
    modal.show();
}
