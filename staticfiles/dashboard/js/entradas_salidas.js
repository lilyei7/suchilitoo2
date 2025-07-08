/**
 * Entradas y Salidas - Movimientos de Inventario
 * Script para manejar todas las interacciones del usuario con la página de entradas y salidas
 */

document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos del DOM
    const modalMovimiento = document.getElementById('modalMovimiento');
    const formMovimiento = document.getElementById('formMovimiento');
    
    // Entradas de radio para tipo de movimiento (en lugar de un select)
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
    const tablaMovimientos = document.getElementById('tablaMovimientos');    const stockActualSpan = document.getElementById('stockActual');
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
    
    // Inicialización del estado
    let insumosData = [];
    let movimientoId = null;
      // ===== Event Listeners =====
      // Mostrar/ocultar campos según el tipo de movimiento
    if (tipoEntradaRadio && tipoSalidaRadio) {
        tipoEntradaRadio.addEventListener('change', function() {
            if (this.checked) {
                actualizarFormularioPorTipo('entrada');
                // Recargar insumos para mostrar todos o los del proveedor si está seleccionado
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
        } else if (tipoSalidaRadio.checked) {
            actualizarFormularioPorTipo('salida');
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
            resetearFormulario();
            mostrarModal(modalMovimiento);
        });
    }
    
    // Botón para crear primer movimiento (estado vacío)
    const btnVacio = document.getElementById('btnNuevoMovimientoVacio');
    if (btnVacio) {
        btnVacio.addEventListener('click', function() {
            resetearFormulario();
            mostrarModal(modalMovimiento);
        });
    }
    
    // Cerrar modales con botones de cerrar
    document.querySelectorAll('.close, .btn-cerrar').forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            cerrarModal(modal);
        });
    });
    
    // Cerrar modales al hacer clic fuera
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            cerrarModal(event.target);
        }
    });
    
    // ===== Funciones =====
      /**
     * Actualiza la visibilidad de campos según el tipo de movimiento
     */
    function actualizarFormularioPorTipo(tipoMovimiento) {
        // Si no se especifica tipo, obtenemos del formulario
        if (!tipoMovimiento) {
            if (tipoEntradaRadio && tipoEntradaRadio.checked) {
                tipoMovimiento = 'entrada';
            } else if (tipoSalidaRadio && tipoSalidaRadio.checked) {
                tipoMovimiento = 'salida';
            }
        }
        
        if (tipoMovimiento === 'entrada') {
            if (contenedorProveedor) contenedorProveedor.style.display = 'block';
            if (contenedorCostoUnitario) contenedorCostoUnitario.style.display = 'block';
            
            // Actualizar opciones de motivo para entradas
            actualizarOpcionesMotivo([
                { value: 'compra', text: 'Compra' },
                { value: 'devolucion', text: 'Devolución de salida' },
                { value: 'ajuste', text: 'Ajuste de inventario' },
                { value: 'otro', text: 'Otro' }
            ]);
            
        } else if (tipoMovimiento === 'salida') {
            if (contenedorProveedor) contenedorProveedor.style.display = 'none';
            if (contenedorCostoUnitario) contenedorCostoUnitario.style.display = 'none';
            
            // Actualizar opciones de motivo para salidas
            actualizarOpcionesMotivo([
                { value: 'consumo', text: 'Consumo' },
                { value: 'merma', text: 'Merma/Caducidad' },
                { value: 'traspaso', text: 'Traspaso entre sucursales' },
                { value: 'ajuste', text: 'Ajuste de inventario' },
                { value: 'otro', text: 'Otro' }
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
    }    /**
     * Carga los insumos disponibles para la sucursal y proveedor seleccionados
     */    function cargarInsumosPorSucursalYProveedor() {
        if (!insumoSelect) return;
        
        // Obtener sucursal (desde select habilitado o campo oculto)
        let sucursalId = '';
        if (sucursalSelect) {
            if (sucursalSelect.disabled) {
                // Si está deshabilitado, buscar el campo oculto
                const hiddenSucursal = document.querySelector('input[name="sucursalMovimiento"]');
                sucursalId = hiddenSucursal ? hiddenSucursal.value : '';
            } else {
                sucursalId = sucursalSelect.value;
            }
        }
        
        const proveedorId = proveedorSelect ? proveedorSelect.value : '';
        
        if (!sucursalId) {
            // Limpiar select de insumos
            insumoSelect.innerHTML = '<option value="">Seleccionar insumo</option>';
            limpiarInformacionInsumo();
            return;
        }
        
        // Mostrar loader
        insumoSelect.innerHTML = '<option value="">Cargando insumos...</option>';
        
        // Limpiar información previa del insumo
        limpiarInformacionInsumo();
        
        // Construir URL con parámetros
        let url = `/dashboard/entradas-salidas/obtener-insumos?sucursal_id=${sucursalId}`;
        if (proveedorId) {
            url += `&proveedor_id=${proveedorId}`;
        }
        
        // Realizar petición AJAX
        fetch(url)
            .then(response => response.json())            .then(data => {
                if (data.success) {
                    insumosData = data.insumos;
                    
                    // Llenar select de insumos
                    insumoSelect.innerHTML = '<option value="">Seleccionar insumo</option>';
                    
                    if (data.insumos.length === 0) {
                        const option = document.createElement('option');
                        option.value = '';
                        option.textContent = proveedorId ? 
                            'No hay insumos para este proveedor' : 
                            'No hay insumos disponibles';
                        option.disabled = true;
                        insumoSelect.appendChild(option);
                        
                        // Mostrar información
                        if (insumoInfo) {
                            insumoInfo.textContent = proveedorId ? 
                                'Este proveedor no tiene insumos asignados.' : 
                                'No hay insumos disponibles para esta sucursal.';
                            insumoInfo.className = 'text-warning';
                            insumoInfo.classList.remove('d-none');
                        }
                    } else {
                        data.insumos.forEach(insumo => {
                            const option = document.createElement('option');
                            option.value = insumo.id;
                            option.textContent = `${insumo.codigo} - ${insumo.nombre}`;
                            insumoSelect.appendChild(option);
                        });
                        
                        // Mostrar información
                        if (insumoInfo) {
                            const mensaje = proveedorId ? 
                                `${data.insumos.length} insumo(s) disponible(s) del proveedor seleccionado.` :
                                `${data.insumos.length} insumo(s) disponible(s) en esta sucursal.`;
                            insumoInfo.textContent = mensaje;
                            insumoInfo.className = 'text-muted';
                            insumoInfo.classList.remove('d-none');
                        }
                    }
                } else {
                    mostrarAlerta('error', data.error || 'Error al cargar insumos');
                    insumoSelect.innerHTML = '<option value="">Error al cargar insumos</option>';
                    
                    if (insumoInfo) {
                        insumoInfo.textContent = 'Error al cargar los insumos.';
                        insumoInfo.className = 'text-danger';
                        insumoInfo.classList.remove('d-none');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarAlerta('error', 'Error de conexión al cargar insumos');
                insumoSelect.innerHTML = '<option value="">Error de conexión</option>';
            });
    }
      /**
     * Limpia la información mostrada del insumo
     */
    function limpiarInformacionInsumo() {
        if (stockActualSpan) stockActualSpan.textContent = '0';
        if (unidadMedidaSpan) unidadMedidaSpan.textContent = '';
        if (unidadMedidaText) unidadMedidaText.textContent = '-';
        if (costoUnitarioInput) costoUnitarioInput.value = '';
        if (insumoInfo) insumoInfo.classList.add('d-none');
    }
    
    /**
     * Carga los insumos disponibles para la sucursal seleccionada (mantenido para compatibilidad)
     */
    function cargarInsumosPorSucursal() {
        cargarInsumosPorSucursalYProveedor();
    }    /**
     * Actualiza la información mostrada del insumo seleccionado
     */
    function actualizarInformacionInsumo() {
        if (!insumoSelect) return;
        
        const insumoId = insumoSelect.value;
        
        if (!insumoId) {
            limpiarInformacionInsumo();
            return;
        }
        
        // Buscar datos del insumo seleccionado
        const insumoSeleccionado = insumosData.find(i => i.id === parseInt(insumoId));
        
        if (insumoSeleccionado) {
            // Actualizar información mostrada
            if (stockActualSpan) stockActualSpan.textContent = insumoSeleccionado.stock_actual.toFixed(2);
            if (unidadMedidaSpan) unidadMedidaSpan.textContent = insumoSeleccionado.unidad_abrev;
            if (unidadMedidaText) unidadMedidaText.textContent = insumoSeleccionado.unidad_abrev;
            
            // Si es entrada, establecer costo unitario por defecto
            const tipoMovimiento = tipoEntradaRadio && tipoEntradaRadio.checked ? 'entrada' : 'salida';
            if (tipoMovimiento === 'entrada' && costoUnitarioInput) {
                // Si viene precio del proveedor específico, usarlo; sino el precio general
                const precioUnitario = insumoSeleccionado.precio_proveedor || insumoSeleccionado.precio_unitario;
                costoUnitarioInput.value = precioUnitario.toFixed(2);
            }
        }
    }
    
    /**
     * Guarda un nuevo movimiento de inventario
     */
    function guardarMovimiento() {
        // Validar formulario
        if (!validarFormularioMovimiento()) {
            return;
        }
        
        // Deshabilitar botón para evitar múltiples envíos
        btnGuardarMovimiento.disabled = true;
        btnGuardarMovimiento.textContent = 'Guardando...';
        
        // Obtener datos del formulario
        const formData = new FormData(formMovimiento);
        
        // Enviar petición AJAX
        fetch('/dashboard/entradas-salidas/crear-movimiento', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarAlerta('success', data.message || 'Movimiento guardado correctamente');
                cerrarModal(modalMovimiento);
                
                // Recargar lista de movimientos
                filtrarMovimientos();
                  // Si cambiamos la sucursal actual, recargar insumos
                if (formFiltro.querySelector('#filtroSucursal').value === formData.get('sucursal')) {
                    cargarInsumosPorSucursalYProveedor();
                }
            } else {
                mostrarAlerta('error', data.error || 'Error al guardar el movimiento');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('error', 'Error de conexión al guardar el movimiento');
        })
        .finally(() => {
            // Restaurar botón
            btnGuardarMovimiento.disabled = false;
            btnGuardarMovimiento.textContent = 'Guardar';
        });
    }
      /**
     * Valida el formulario antes de enviar
     */    function validarFormularioMovimiento() {
        // Obtener tipo de movimiento de los radio buttons
        let tipoMovimiento = '';
        if (tipoEntradaRadio && tipoEntradaRadio.checked) {
            tipoMovimiento = 'entrada';
        } else if (tipoSalidaRadio && tipoSalidaRadio.checked) {
            tipoMovimiento = 'salida';
        }
        
        // Verificar sucursal (puede estar en el select o en el campo oculto)
        let sucursal = '';
        if (sucursalSelect) {
            if (sucursalSelect.disabled) {
                // Si está deshabilitado, buscar el campo oculto
                const hiddenSucursal = document.querySelector('input[name="sucursalMovimiento"]');
                sucursal = hiddenSucursal ? hiddenSucursal.value : '';
            } else {
                sucursal = sucursalSelect.value;
            }
        }
        
        const insumo = insumoSelect ? insumoSelect.value : '';
        const motivo = motivoSelect ? motivoSelect.value : '';
        const cantidad = cantidadInput ? parseFloat(cantidadInput.value) : 0;
        
        if (!tipoMovimiento) {
            mostrarAlerta('error', 'Debe seleccionar un tipo de movimiento');
            return false;
        }
        
        if (!sucursal) {
            mostrarAlerta('error', 'Debe seleccionar una sucursal');
            return false;
        }
        
        if (!insumo) {
            mostrarAlerta('error', 'Debe seleccionar un insumo');
            return false;
        }
        
        if (!motivo) {
            mostrarAlerta('error', 'Debe seleccionar un motivo');
            return false;
        }
        
        if (isNaN(cantidad) || cantidad <= 0) {
            mostrarAlerta('error', 'La cantidad debe ser un número mayor a cero');
            return false;
        }
        
        // Validar otro motivo si está seleccionado
        if (motivo === 'otro') {
            const otroMotivo = document.getElementById('otroMotivo');
            if (!otroMotivo || !otroMotivo.value.trim()) {
                mostrarAlerta('error', 'Debe especificar el motivo');
                return false;
            }
        }
        
        // Validar sucursal destino si es traspaso
        if (motivo === 'traspaso') {
            const sucursalDestino = document.getElementById('sucursalDestino');
            if (!sucursalDestino || !sucursalDestino.value) {
                mostrarAlerta('error', 'Debe seleccionar una sucursal de destino');
                return false;
            }
            
            if (sucursalDestino.value === sucursal) {
                mostrarAlerta('error', 'La sucursal de destino debe ser diferente a la de origen');
                return false;
            }
        }
        
        // Validar costo unitario si es entrada
        if (tipoMovimiento === 'entrada' && costoUnitarioInput) {
            const costoUnitario = parseFloat(costoUnitarioInput.value);
            if (isNaN(costoUnitario) || costoUnitario < 0) {
                mostrarAlerta('error', 'El costo unitario debe ser un número no negativo');
                return false;
            }
        }
        
        // Validar que hay suficiente stock si es salida
        if (tipoMovimiento === 'salida' && stockActualSpan) {
            const stockActual = parseFloat(stockActualSpan.textContent);
            if (cantidad > stockActual) {
                const unidad = unidadMedidaSpan ? unidadMedidaSpan.textContent : '';
                mostrarAlerta('error', `Stock insuficiente. Disponible: ${stockActual} ${unidad}`);
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * Filtra los movimientos según los criterios seleccionados
     */
    function filtrarMovimientos() {
        // Obtener parámetros de filtro
        const tipo = formFiltro.querySelector('#filtroTipo').value;
        const sucursal = formFiltro.querySelector('#filtroSucursal').value;
        const fecha = formFiltro.querySelector('#filtroFecha').value;
        const busqueda = formFiltro.querySelector('#filtroBusqueda').value;
        
        // Construir URL con parámetros
        let url = '/dashboard/entradas-salidas/filtrar?';
        url += `tipo=${encodeURIComponent(tipo)}`;
        url += `&sucursal=${encodeURIComponent(sucursal)}`;
        url += `&fecha=${encodeURIComponent(fecha)}`;
        url += `&busqueda=${encodeURIComponent(busqueda)}`;
        
        // Mostrar indicador de carga
        tablaMovimientos.querySelector('tbody').innerHTML = '<tr><td colspan="8" class="text-center">Cargando movimientos...</td></tr>';
        
        // Realizar petición AJAX
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    renderizarTablaMovimientos(data.movimientos);
                    
                    // Actualizar contador de resultados
                    const contadorResultados = document.getElementById('contadorResultados');
                    if (contadorResultados) {
                        contadorResultados.textContent = data.total;
                    }
                } else {
                    mostrarAlerta('error', data.error || 'Error al filtrar movimientos');
                    tablaMovimientos.querySelector('tbody').innerHTML = '<tr><td colspan="8" class="text-center">Error al cargar datos</td></tr>';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarAlerta('error', 'Error de conexión al filtrar movimientos');
                tablaMovimientos.querySelector('tbody').innerHTML = '<tr><td colspan="8" class="text-center">Error de conexión</td></tr>';
            });
    }
    
    /**
     * Renderiza la tabla de movimientos con los datos recibidos
     */
    function renderizarTablaMovimientos(movimientos) {
        const tbody = tablaMovimientos.querySelector('tbody');
        tbody.innerHTML = '';
        
        if (movimientos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center">No se encontraron movimientos</td></tr>';
            return;
        }
        
        movimientos.forEach(m => {
            const tr = document.createElement('tr');
            
            // Clase según el tipo de movimiento
            tr.classList.add(m.tipo_movimiento === 'entrada' ? 'entrada-row' : 'salida-row');
            
            tr.innerHTML = `
                <td>${m.fecha}</td>
                <td>
                    <span class="badge ${m.tipo_movimiento === 'entrada' ? 'badge-success' : 'badge-danger'}">
                        ${m.tipo_movimiento === 'entrada' ? 'Entrada' : 'Salida'}
                    </span>
                </td>
                <td>${m.insumo.codigo} - ${m.insumo.nombre}</td>
                <td>${m.cantidad} ${m.unidad}</td>
                <td>${m.sucursal}</td>
                <td>${m.usuario}</td>
                <td>${m.motivo}</td>
                <td>
                    <button type="button" class="btn-sm btn-info" onclick="verDetalleMovimiento(${m.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            `;
            
            tbody.appendChild(tr);
        });
    }
    
    /**
     * Muestra el detalle de un movimiento específico
     */
    function verDetalleMovimiento(id) {
        // Mostrar loader en el modal
        document.getElementById('detalleMovimientoContent').innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin fa-2x"></i><p>Cargando detalles...</p></div>';
        
        // Mostrar modal
        mostrarModal(modalDetalleMovimiento);
        
        // Realizar petición AJAX
        fetch(`/dashboard/entradas-salidas/detalle/${id}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    renderizarDetalleMovimiento(data.movimiento);
                } else {
                    document.getElementById('detalleMovimientoContent').innerHTML = `<div class="alert alert-danger">${data.error || 'Error al cargar los detalles'}</div>`;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('detalleMovimientoContent').innerHTML = '<div class="alert alert-danger">Error de conexión al cargar los detalles</div>';
            });
    }
    
    /**
     * Renderiza los detalles de un movimiento en el modal
     */
    function renderizarDetalleMovimiento(movimiento) {
        const content = document.getElementById('detalleMovimientoContent');
        
        // Guardar ID para posibles acciones
        movimientoId = movimiento.id;
        
        // Construir HTML con los detalles
        let html = `
            <div class="detalle-movimiento">
                <h4 class="${movimiento.tipo_movimiento === 'entrada' ? 'text-success' : 'text-danger'}">
                    ${movimiento.tipo_movimiento === 'entrada' ? 'Entrada' : 'Salida'} #${movimiento.id}
                </h4>
                
                <div class="detalle-section">
                    <h5>Información básica</h5>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Fecha:</strong> ${movimiento.fecha}</p>
                            <p><strong>Insumo:</strong> ${movimiento.insumo.codigo} - ${movimiento.insumo.nombre}</p>
                            <p><strong>Cantidad:</strong> ${movimiento.cantidad} ${movimiento.insumo.abreviacion}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Sucursal:</strong> ${movimiento.sucursal.nombre}</p>
                            <p><strong>Usuario:</strong> ${movimiento.usuario}</p>
                            <p><strong>Motivo:</strong> ${movimiento.motivo}</p>
                        </div>
                    </div>
                </div>`;
        
        // Mostrar proveedor y costo unitario para entradas
        if (movimiento.tipo_movimiento === 'entrada') {
            html += `
                <div class="detalle-section">
                    <h5>Detalles de entrada</h5>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Costo unitario:</strong> $${movimiento.costo_unitario ? movimiento.costo_unitario.toFixed(2) : 'No especificado'}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Proveedor:</strong> ${movimiento.proveedor ? movimiento.proveedor.nombre : 'No especificado'}</p>
                        </div>
                    </div>
                </div>`;
        }
        
        // Mostrar sucursal destino para traspasos
        if (movimiento.sucursal_destino) {
            html += `
                <div class="detalle-section">
                    <h5>Traspaso</h5>
                    <p><strong>Sucursal destino:</strong> ${movimiento.sucursal_destino.nombre}</p>
                </div>`;
        }
        
        // Mostrar observaciones si existen
        if (movimiento.observaciones) {
            html += `
                <div class="detalle-section">
                    <h5>Observaciones</h5>
                    <p>${movimiento.observaciones}</p>
                </div>`;
        }
        
        // Cerrar div principal
        html += '</div>';
        
        // Actualizar contenido
        content.innerHTML = html;
    }
      /**
     * Resetea el formulario de movimiento
     */
    function resetearFormulario() {
        if (formMovimiento) {
            formMovimiento.reset();
        }
        
        // Resetear campos y visibilidad
        if (contenedorProveedor) contenedorProveedor.style.display = 'none';
        if (contenedorCostoUnitario) contenedorCostoUnitario.style.display = 'none';
        if (contenedorOtroMotivo) contenedorOtroMotivo.style.display = 'none';
        if (contenedorSucursalDestino) contenedorSucursalDestino.style.display = 'none';
        
        // Limpiar select de insumos
        if (insumoSelect) {
            insumoSelect.innerHTML = '<option value="">Seleccionar insumo</option>';
        }
        
        // Resetear información de insumo
        if (stockActualSpan) stockActualSpan.textContent = '0';
        if (unidadMedidaSpan) unidadMedidaSpan.textContent = '';
        if (unidadMedidaText) unidadMedidaText.textContent = '-';
        
        // Resetear motivo
        if (motivoSelect) {
            motivoSelect.innerHTML = '<option value="">Seleccione primero un tipo de movimiento</option>';
        }
        
        // Resetear a entrada por defecto
        if (tipoEntradaRadio) {
            tipoEntradaRadio.checked = true;
            actualizarFormularioPorTipo('entrada');
        }
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
     * Cierra un modal
     */
    function cerrarModal(modal) {
        if (modal) {
            modal.classList.remove('show');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
        }
    }
    
    /**
     * Muestra una alerta con un mensaje
     */
    function mostrarAlerta(tipo, mensaje) {
        const alertaDiv = document.createElement('div');
        alertaDiv.className = `alert alert-${tipo} alert-dismissible fade show`;
        alertaDiv.innerHTML = `
            ${mensaje}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
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
    
    // Exponer funciones globales
    window.verDetalleMovimiento = verDetalleMovimiento;
      // Cargar datos iniciales
    filtrarMovimientos();
    
    // Si hay una sucursal pre-seleccionada (usuario no admin), cargar sus insumos
    if (sucursalSelect && sucursalSelect.value && sucursalSelect.disabled) {
        cargarInsumosPorSucursalYProveedor();
    }
});
