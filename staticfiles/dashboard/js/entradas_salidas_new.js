/**
 * Entradas y Salidas - Movimientos de Inventario
 * Script para manejar todas las interacciones del usuario con la página de entradas y salidas
 */

/**
 * Muestra una alerta con un mensaje
 * @param {string} tipo - El tipo de alerta (success, error, warning, info)
 * @param {string} mensaje - El mensaje a mostrar
 */
function mostrarAlerta(tipo, mensaje) {
    const alertaDiv = document.createElement('div');
    alertaDiv.className = `alert alert-${tipo} alert-dismissible fade show`;
    alertaDiv.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insertar al inicio del contenedor principal
    const contenedor = document.querySelector('.container-fluid');
    contenedor.insertBefore(alertaDiv, contenedor.firstChild);
    
    // Eliminar después de 5 segundos
    setTimeout(() => {
        alertaDiv.classList.remove('show');
        setTimeout(() => alertaDiv.remove(), 300);
    }, 5000);
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Iniciando módulo Entradas y Salidas');
    
    // Referencias a elementos del DOM
    const modalMovimiento = document.getElementById('modalMovimiento');
    const formMovimiento = document.getElementById('formMovimiento');
    
    // Entradas de radio para tipo de movimiento
    const tipoEntradaRadio = document.getElementById('tipoEntrada');
    const tipoSalidaRadio = document.getElementById('tipoSalida');
    
    const sucursalSelect = document.getElementById('sucursal');
    const proveedorSelect = document.getElementById('proveedor');
    const insumoSelect = document.getElementById('insumo');
    const motivoSelect = document.getElementById('motivo');
    const cantidadInput = document.getElementById('cantidad');
    const costoUnitarioInput = document.getElementById('costoUnitario');
    const btnGuardarMovimiento = document.getElementById('btnGuardarMovimiento');
    const formFiltro = document.getElementById('formFiltro');
    
    // Elementos de información
    const stockActualSpan = document.getElementById('stockActual');
    const unidadMedidaSpan = document.getElementById('unidadMedida');
    const unidadMedidaText = document.getElementById('unidadMedidaText');
    const insumoInfo = document.getElementById('insumoInfo');
    
    // Contenedores condicionales
    const contenedorProveedor = document.getElementById('contenedorProveedor');
    const contenedorCostoUnitario = document.getElementById('contenedorCostoUnitario');
    const contenedorOtroMotivo = document.getElementById('contenedorOtroMotivo');
    const contenedorSucursalDestino = document.getElementById('contenedorSucursalDestino');
    
    // Elementos para detalles de movimiento
    const modalDetalleMovimiento = document.getElementById('modalDetalleMovimiento');
    const modalConfirmDelete = document.getElementById('modalConfirmDelete');
    
    // Variables globales
    let insumosData = [];
    let movimientoId = null;
    
    // ===== Event Listeners =====
    
    // Mostrar/ocultar campos según el tipo de movimiento
    if (tipoEntradaRadio && tipoSalidaRadio) {
        tipoEntradaRadio.addEventListener('change', function() {
            if (this.checked) {
                actualizarFormularioPorTipo('entrada');
                cargarInsumosPorSucursalYProveedor();
            }
        });
        
        tipoSalidaRadio.addEventListener('change', function() {
            if (this.checked) {
                actualizarFormularioPorTipo('salida');
                // Limpiar selección de proveedor y recargar insumos
                if (proveedorSelect) {
                    proveedorSelect.value = '';
                }
                cargarInsumosPorSucursalYProveedor();
            }
        });
        
        // Inicializar el formulario según el tipo seleccionado por defecto
        if (tipoEntradaRadio.checked) {
            actualizarFormularioPorTipo('entrada');
        }
    }
    
    // Cambiar opciones de insumo cuando cambia la sucursal
    if (sucursalSelect) {
        sucursalSelect.addEventListener('change', function() {
            cargarInsumosPorSucursalYProveedor();
        });
    }
    
    // Cambiar opciones de insumo cuando cambia el proveedor
    if (proveedorSelect) {
        proveedorSelect.addEventListener('change', function() {
            cargarInsumosPorSucursalYProveedor();
        });
    }
    
    // Actualizar información cuando se selecciona un insumo
    if (insumoSelect) {
        insumoSelect.addEventListener('change', function() {
            actualizarInformacionInsumo();
        });
    }
    
    // Mostrar campo otro motivo cuando se selecciona "otro"
    if (motivoSelect) {
        motivoSelect.addEventListener('change', function() {
            const mostrarOtroMotivo = this.value === 'otro';
            if (contenedorOtroMotivo) {
                contenedorOtroMotivo.style.display = mostrarOtroMotivo ? 'block' : 'none';
            }
            
            // Si es traspaso, mostrar selección de sucursal destino
            const esTraspaso = this.value === 'traspaso';
            if (contenedorSucursalDestino) {
                contenedorSucursalDestino.style.display = esTraspaso ? 'block' : 'none';
            }
        });
    }
    
    // Manejo del formulario de movimiento
    if (formMovimiento) {
        formMovimiento.addEventListener('submit', function(e) {
            e.preventDefault();
            guardarMovimiento();
        });
    }
    
    // Manejo del formulario de filtro
    if (formFiltro) {
        formFiltro.addEventListener('submit', function(e) {
            e.preventDefault();
            filtrarMovimientos();
        });
    }
    
    // Botón para crear nuevo movimiento
    const btnNuevoMovimiento = document.getElementById('btnNuevoMovimiento');
    if (btnNuevoMovimiento) {
        btnNuevoMovimiento.addEventListener('click', function() {
            abrirModalNuevoMovimiento();
        });
    }
    
    // Botón para crear primer movimiento (estado vacío)
    const btnVacio = document.getElementById('btnNuevoMovimientoVacio');
    if (btnVacio) {
        btnVacio.addEventListener('click', function() {
            abrirModalNuevoMovimiento();
        });
    }
    
    // Cerrar modales con botones de cerrar
    document.querySelectorAll('.close, .btn-cerrar').forEach(btn => {
        btn.addEventListener('click', function() {
            cerrarTodosLosModales();
        });
    });
    
    // Cerrar modales al hacer clic fuera
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            cerrarTodosLosModales();
        }
    });
    
    // ===== Funciones =====
    
    /**
     * Actualiza la visibilidad de campos según el tipo de movimiento
     */
    function actualizarFormularioPorTipo(tipoMovimiento) {
        if (!tipoMovimiento) {
            // Si no se especifica tipo, obtenemos del formulario
            const tipoSeleccionado = document.querySelector('input[name="tipo_movimiento"]:checked');
            tipoMovimiento = tipoSeleccionado ? tipoSeleccionado.value : 'entrada';
        }
        
        if (tipoMovimiento === 'entrada') {
            // Para entradas: mostrar proveedor y costo
            if (contenedorProveedor) contenedorProveedor.style.display = 'block';
            if (contenedorCostoUnitario) contenedorCostoUnitario.style.display = 'block';
            
            // Actualizar opciones de motivo para entradas
            actualizarOpcionesMotivo([
                {value: 'compra', text: 'Compra'},
                {value: 'devolucion', text: 'Devolución'},
                {value: 'ajuste_inventario', text: 'Ajuste de inventario'},
                {value: 'traspaso', text: 'Traspaso entre sucursales'},
                {value: 'otro', text: 'Otro'}
            ]);
        } else if (tipoMovimiento === 'salida') {
            // Para salidas: ocultar proveedor y costo
            if (contenedorProveedor) contenedorProveedor.style.display = 'none';
            if (contenedorCostoUnitario) contenedorCostoUnitario.style.display = 'none';
            
            // Actualizar opciones de motivo para salidas
            actualizarOpcionesMotivo([
                {value: 'venta', text: 'Venta'},
                {value: 'consumo_interno', text: 'Consumo interno'},
                {value: 'merma', text: 'Merma'},
                {value: 'caducidad', text: 'Caducidad'},
                {value: 'traspaso', text: 'Traspaso entre sucursales'},
                {value: 'ajuste_inventario', text: 'Ajuste de inventario'},
                {value: 'otro', text: 'Otro'}
            ]);
        }
        
        // Ocultar contenedores condicionales
        if (contenedorOtroMotivo) contenedorOtroMotivo.style.display = 'none';
        if (contenedorSucursalDestino) contenedorSucursalDestino.style.display = 'none';
    }
    
    /**
     * Actualiza las opciones del select de motivo
     */
    function actualizarOpcionesMotivo(opciones) {
        if (!motivoSelect) return;
        
        // Limpiar opciones actuales
        motivoSelect.innerHTML = '<option value="">Seleccionar motivo</option>';
        
        // Agregar nuevas opciones
        opciones.forEach(opcion => {
            const option = document.createElement('option');
            option.value = opcion.value;
            option.textContent = opcion.text;
            motivoSelect.appendChild(option);
        });
    }
    
    /**
     * Carga los insumos disponibles para la sucursal y proveedor seleccionados
     */
    function cargarInsumosPorSucursalYProveedor() {
        if (!sucursalSelect || !insumoSelect) return;
        
        const sucursalId = sucursalSelect.value;
        const proveedorId = proveedorSelect ? proveedorSelect.value : '';
        
        if (!sucursalId) {
            limpiarInformacionInsumo();
            return;
        }
        
        // Construir URL con parámetros
        let url = `/dashboard/entradas-salidas/obtener-insumos?sucursal_id=${sucursalId}`;
        if (proveedorId) {
            url += `&proveedor_id=${proveedorId}`;
        }
        
        // Mostrar loading
        insumoSelect.innerHTML = '<option value="">Cargando insumos...</option>';
        insumoSelect.disabled = true;
        
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                insumosData = data.insumos;
                
                // Limpiar y llenar el select de insumos
                insumoSelect.innerHTML = '<option value="">Seleccionar insumo</option>';
                
                if (insumosData.length > 0) {
                    insumosData.forEach(insumo => {
                        const option = document.createElement('option');
                        option.value = insumo.id;
                        option.textContent = `${insumo.codigo} - ${insumo.nombre}`;
                        option.dataset.insumo = JSON.stringify(insumo);
                        insumoSelect.appendChild(option);
                    });
                    insumoSelect.disabled = false;
                } else {
                    insumoSelect.innerHTML = '<option value="">No hay insumos disponibles</option>';
                    if (proveedorId) {
                        mostrarAlerta('warning', 'Este proveedor no tiene insumos asignados.');
                    }
                }
            } else {
                console.error('Error cargando insumos:', data.message);
                insumoSelect.innerHTML = '<option value="">Error cargando insumos</option>';
                mostrarAlerta('error', 'Error al cargar insumos: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error en petición:', error);
            insumoSelect.innerHTML = '<option value="">Error de conexión</option>';
            mostrarAlerta('error', 'Error de conexión al cargar insumos');
        })
        .finally(() => {
            limpiarInformacionInsumo();
        });
    }
    
    /**
     * Limpia la información mostrada del insumo
     */
    function limpiarInformacionInsumo() {
        if (stockActualSpan) stockActualSpan.textContent = '0';
        if (unidadMedidaSpan) unidadMedidaSpan.textContent = '-';
        if (unidadMedidaText) unidadMedidaText.textContent = '-';
        if (insumoInfo) {
            insumoInfo.classList.add('d-none');
            insumoInfo.textContent = '';
        }
    }
    
    /**
     * Actualiza la información mostrada del insumo seleccionado
     */
    function actualizarInformacionInsumo() {
        if (!insumoSelect) return;
        
        const option = insumoSelect.options[insumoSelect.selectedIndex];
        if (!option || !option.dataset.insumo) {
            limpiarInformacionInsumo();
            return;
        }
        
        try {
            const insumo = JSON.parse(option.dataset.insumo);
            
            if (stockActualSpan) stockActualSpan.textContent = insumo.stock_actual;
            if (unidadMedidaSpan) unidadMedidaSpan.textContent = insumo.unidad_abrev;
            if (unidadMedidaText) unidadMedidaText.textContent = insumo.unidad_abrev;
            
            // Mostrar información adicional
            if (insumoInfo) {
                insumoInfo.textContent = `Categoría: ${insumo.categoria} | Precio: $${insumo.precio_unitario}`;
                insumoInfo.classList.remove('d-none');
            }
            
            // Si es entrada y hay costo unitario, prellenarlo
            if (costoUnitarioInput && tipoEntradaRadio && tipoEntradaRadio.checked) {
                costoUnitarioInput.value = insumo.precio_unitario;
            }
        } catch (error) {
            console.error('Error parseando datos del insumo:', error);
            limpiarInformacionInsumo();
        }
    }
    
    /**
     * Guarda un nuevo movimiento de inventario
     */
    function guardarMovimiento() {
        if (!validarFormularioMovimiento()) {
            return;
        }
        
        // Deshabilitar botón para evitar doble envío
        if (btnGuardarMovimiento) {
            btnGuardarMovimiento.disabled = true;
            btnGuardarMovimiento.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Guardando...';
        }
        
        const formData = new FormData(formMovimiento);
        
        fetch('/dashboard/entradas-salidas/crear-movimiento', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCsrfToken()
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarAlerta('success', data.message);
                cerrarTodosLosModales();
                resetearFormulario();
                // Recargar la tabla de movimientos
                filtrarMovimientos();
            } else {
                mostrarAlerta('error', data.message);
            }
        })
        .catch(error => {
            console.error('Error guardando movimiento:', error);
            mostrarAlerta('error', 'Error de conexión al guardar el movimiento');
        })
        .finally(() => {
            // Rehabilitar botón
            if (btnGuardarMovimiento) {
                btnGuardarMovimiento.disabled = false;
                btnGuardarMovimiento.innerHTML = '<i class="fas fa-save me-2"></i>Guardar Movimiento';
            }
        });
    }
    
    /**
     * Valida el formulario antes de enviar
     */
    function validarFormularioMovimiento() {
        const requiredFields = [
            {element: sucursalSelect, name: 'sucursal'},
            {element: motivoSelect, name: 'motivo'},
            {element: insumoSelect, name: 'insumo'},
            {element: cantidadInput, name: 'cantidad'}
        ];
        
        for (let field of requiredFields) {
            if (!field.element || !field.element.value) {
                mostrarAlerta('error', `El campo ${field.name} es obligatorio`);
                if (field.element) field.element.focus();
                return false;
            }
        }
        
        // Validar cantidad
        const cantidad = parseFloat(cantidadInput.value);
        if (isNaN(cantidad) || cantidad <= 0) {
            mostrarAlerta('error', 'La cantidad debe ser mayor que cero');
            cantidadInput.focus();
            return false;
        }
        
        // Validar stock suficiente para salidas
        if (tipoSalidaRadio && tipoSalidaRadio.checked) {
            const stockActual = parseFloat(stockActualSpan.textContent) || 0;
            if (cantidad > stockActual) {
                mostrarAlerta('error', `Stock insuficiente. Stock actual: ${stockActual}`);
                cantidadInput.focus();
                return false;
            }
        }
        
        // Validar motivo "otro"
        if (motivoSelect.value === 'otro') {
            const otroMotivoInput = document.getElementById('otroMotivo');
            if (!otroMotivoInput || !otroMotivoInput.value.trim()) {
                mostrarAlerta('error', 'Debe especificar el motivo');
                if (otroMotivoInput) otroMotivoInput.focus();
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * Filtra los movimientos según los criterios seleccionados
     */
    function filtrarMovimientos() {
        const container = document.getElementById('movimientosTableContainer');
        if (!container) return;
        
        // Construir parámetros de filtro
        const params = new URLSearchParams();
        
        if (formFiltro) {
            const formData = new FormData(formFiltro);
            for (let [key, value] of formData.entries()) {
                if (value) params.append(key, value);
            }
        }
        
        // Mostrar loading
        container.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"></div></div>';
        
        fetch(`/dashboard/entradas-salidas/filtrar?${params.toString()}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderizarTablaMovimientos(data.movimientos);
            } else {
                container.innerHTML = `<div class="alert alert-danger">Error: ${data.message}</div>`;
            }
        })
        .catch(error => {
            console.error('Error filtrando movimientos:', error);
            container.innerHTML = '<div class="alert alert-danger">Error de conexión</div>';
        });
    }
    
    /**
     * Renderiza la tabla de movimientos con los datos recibidos
     */    function renderizarTablaMovimientos(movimientos) {
        const container = document.getElementById('movimientosTableContainer');
        if (!container) return;
        
        if (movimientos.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <div class="mb-4">
                        <i class="fas fa-box-open text-muted" style="font-size: 4rem; opacity: 0.3;"></i>
                    </div>
                    <h5 class="text-muted mb-2">No hay movimientos</h5>
                    <p class="text-muted mb-4">No se encontraron movimientos con los filtros aplicados</p>
                </div>
            `;
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-hover" id="tablaMovimientos">
                    <thead>
                        <tr>
                            <th>FECHA</th>
                            <th>TIPO</th>
                            <th>INSUMO</th>
                            <th>CANTIDAD</th>
                            <th>USUARIO</th>
                            <th>SUCURSAL</th>
                            <th>MOTIVO</th>
                            <th>ACCIONES</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        movimientos.forEach(mov => {
            const badgeClass = mov.tipo_movimiento === 'entrada' ? 'bg-success' : 'bg-danger';
            const badgeText = mov.tipo_movimiento === 'entrada' ? 'Entrada' : 'Salida';
            
            // Asegurar que todos los campos tengan valores válidos
            const fecha = mov.fecha || mov.fecha_creacion || 'N/A';
            const insumo = mov.insumo || 'N/A';
            const cantidad = mov.cantidad || 0;
            const unidadMedida = mov.unidad_medida || '';
            const usuario = mov.usuario || 'Sistema';
            const sucursal = mov.sucursal || 'N/A';
            const motivo = mov.motivo || 'Sin motivo';
            
            html += `
                <tr>
                    <td><span class="text-muted">${fecha}</span></td>
                    <td><span class="badge ${badgeClass}">${badgeText}</span></td>
                    <td>
                        <div>
                            <h6 class="mb-0">${insumo}</h6>
                        </div>
                    </td>
                    <td><span class="fw-bold">${cantidad} ${unidadMedida}</span></td>
                    <td><span class="text-muted">${usuario}</span></td>
                    <td><span class="text-muted">${sucursal}</span></td>
                    <td><span class="text-muted">${motivo}</span></td>
                    <td>
                        <button class="btn btn-link text-muted btn-sm" onclick="verDetalleMovimiento(${mov.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    /**
     * Abre el modal para crear un nuevo movimiento
     */
    function abrirModalNuevoMovimiento() {
        resetearFormulario();
        
        // Configurar el modal para nuevo movimiento
        document.getElementById('movimientoModalTitle').innerHTML = 
            '<i class="fas fa-exchange-alt me-2"></i>Nuevo Movimiento';
        
        // Mostrar el modal
        mostrarModal(modalMovimiento);
        
        // Configurar formulario inicial
        actualizarFormularioPorTipo('entrada');
        
        // Si el usuario tiene una sucursal asignada, cargar sus insumos
        const sucursalSelect = document.getElementById('sucursal');
        if (sucursalSelect && sucursalSelect.value && sucursalSelect.disabled) {
            cargarInsumosPorSucursalYProveedor();
        }
    }

    /**
     * Resetea el formulario de movimiento
     */
    function resetearFormulario() {
        if (formMovimiento) {
            formMovimiento.reset();
        }
        
        // Limpiar campos específicos
        limpiarInformacionInsumo();
        
        // Resetear radio buttons al valor por defecto
        const tipoEntradaRadio = document.getElementById('tipoEntrada');
        if (tipoEntradaRadio) {
            tipoEntradaRadio.checked = true;
        }
        
        // Limpiar insumos
        const insumoSelect = document.getElementById('insumo');
        if (insumoSelect) {
            insumoSelect.innerHTML = '<option value="">Seleccione datos adicionales primero</option>';
        }
        
        // Ocultar contenedores condicionales
        if (contenedorProveedor) contenedorProveedor.style.display = 'none';
        if (contenedorCostoUnitario) contenedorCostoUnitario.style.display = 'none';
        if (contenedorOtroMotivo) contenedorOtroMotivo.style.display = 'none';
        if (contenedorSucursalDestino) contenedorSucursalDestino.style.display = 'none';
    }

    /**
     * Muestra un modal
     */
    function mostrarModal(modal) {
        if (modal) {
            modal.style.display = 'block';
            setTimeout(() => {
                modal.classList.add('show');
            }, 10);
        }
    }

    /**
     * Cierra todos los modales
     */
    function cerrarTodosLosModales() {
        const modales = document.querySelectorAll('.modal');
        modales.forEach(modal => {
            modal.classList.remove('show');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
        });
    }    /**
     * Muestra el detalle de un movimiento específico
     */
    function verDetalleMovimiento(movimientoId) {
        const modal = document.getElementById('modalDetalleMovimiento');
        const modalContent = document.getElementById('detalleMovimientoContent');
        
        if (!modal || !modalContent) {
            console.error('Modal de detalle no encontrado');
            return;
        }
        
        // Mostrar loading
        modalContent.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"></div><p class="mt-2 text-muted">Cargando detalles...</p></div>';
        mostrarModal(modal);
        
        // Hacer petición al backend
        fetch(`/dashboard/entradas-salidas/detalle/${movimientoId}/`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderizarDetalleMovimiento(data.movimiento);
            } else {
                modalContent.innerHTML = `<div class="alert alert-danger">Error: ${data.message}</div>`;
            }
        })
        .catch(error => {
            console.error('Error obteniendo detalle:', error);
            modalContent.innerHTML = '<div class="alert alert-danger">Error de conexión</div>';
        });
    }

    /**
     * Renderiza los detalles de un movimiento en el modal
     */
    function renderizarDetalleMovimiento(movimiento) {
        const modalContent = document.getElementById('detalleMovimientoContent');
        if (!modalContent) return;
        
        const tipoIcon = movimiento.tipo_movimiento === 'entrada' ? 'fa-arrow-down text-success' : 'fa-arrow-up text-danger';
        const tipoBadge = movimiento.tipo_movimiento === 'entrada' ? 'bg-success' : 'bg-danger';
        const tipoTexto = movimiento.tipo_movimiento === 'entrada' ? 'Entrada' : 'Salida';
        
        const html = `
            <div class="row">
                <div class="col-md-6">
                    <h6 class="text-muted mb-2">Información General</h6>
                    <div class="mb-3">
                        <label class="form-label small text-muted">ID del Movimiento</label>
                        <div class="fw-bold">#${movimiento.id}</div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label small text-muted">Tipo de Movimiento</label>
                        <div>
                            <span class="badge ${tipoBadge}">
                                <i class="fas ${tipoIcon} me-1"></i>${tipoTexto}
                            </span>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label small text-muted">Sucursal</label>
                        <div class="fw-bold">${movimiento.sucursal}</div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label small text-muted">Usuario</label>
                        <div>${movimiento.usuario}</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <h6 class="text-muted mb-2">Detalles del Insumo</h6>
                    <div class="mb-3">
                        <label class="form-label small text-muted">Insumo</label>
                        <div class="fw-bold">${movimiento.insumo.nombre}</div>
                        <small class="text-muted">Código: ${movimiento.insumo.codigo}</small>
                    </div>
                    <div class="mb-3">
                        <label class="form-label small text-muted">Cantidad</label>
                        <div class="fw-bold fs-4 text-primary">${movimiento.cantidad} ${movimiento.insumo.unidad_medida}</div>
                    </div>
                    <div class="row">
                        <div class="col-6">
                            <label class="form-label small text-muted">Stock Anterior</label>
                            <div>${movimiento.cantidad_anterior} ${movimiento.insumo.unidad_medida}</div>
                        </div>
                        <div class="col-6">
                            <label class="form-label small text-muted">Stock Nuevo</label>
                            <div class="fw-bold">${movimiento.cantidad_nueva} ${movimiento.insumo.unidad_medida}</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <hr>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label small text-muted">Motivo</label>
                        <div>${movimiento.motivo || 'Sin motivo especificado'}</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label small text-muted">Fecha y Hora</label>
                        <div>${movimiento.fecha_creacion}</div>
                    </div>
                </div>
            </div>
            
            ${movimiento.documento_referencia ? `
            <div class="mb-3">
                <label class="form-label small text-muted">Documento de Referencia</label>
                <div><code>${movimiento.documento_referencia}</code></div>
            </div>
            ` : ''}
        `;
        
        modalContent.innerHTML = html;
    }

    /**
     * Obtiene el token CSRF para peticiones AJAX
     */
    function getCsrfToken() {
        const csrf = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrf ? csrf.value : '';
    }
    
    // Exponer funciones globales
    window.verDetalleMovimiento = verDetalleMovimiento;
    
    // Cargar datos iniciales
    filtrarMovimientos();
    
    // Si hay una sucursal pre-seleccionada (usuario no admin), cargar sus insumos
    if (sucursalSelect && sucursalSelect.value && sucursalSelect.disabled) {
        cargarInsumosPorSucursalYProveedor();
    }
    
    console.log('✅ Módulo Entradas y Salidas inicializado correctamente');
});
