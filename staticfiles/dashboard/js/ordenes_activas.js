/**
 * Ordenes Activas - Funciones
 * Sistema de Restaurant Sushi
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Sistema de Órdenes Activas cargado correctamente');
    
    // Referencias a elementos del DOM
    const listaOrdenes = document.getElementById('listaOrdenes');
    const ordenNoSeleccionada = document.getElementById('ordenNoSeleccionada');
    const ordenDetalle = document.getElementById('ordenDetalle');
    const ordenTitulo = document.getElementById('ordenTitulo');
    const ordenNumeroDetalle = document.getElementById('ordenNumeroDetalle');
    const ordenEstadoDetalle = document.getElementById('ordenEstadoDetalle');
    const ordenFechaHora = document.getElementById('ordenFechaHora');
    const ordenTipo = document.getElementById('ordenTipo');
    const ordenMesa = document.getElementById('ordenMesa');
    const ordenCliente = document.getElementById('ordenCliente');
    const ordenCajero = document.getElementById('ordenCajero');
    const ordenPagada = document.getElementById('ordenPagada');
    const ordenNotas = document.getElementById('ordenNotas');
    const ordenItems = document.getElementById('ordenItems');
    const ordenSubtotal = document.getElementById('ordenSubtotal');
    const ordenDescuento = document.getElementById('ordenDescuento');
    const ordenImpuestos = document.getElementById('ordenImpuestos');
    const ordenTotal = document.getElementById('ordenTotal');
    
    // Botones
    const btnActualizarEstado = document.getElementById('btnActualizarEstado');
    const btnCancelarOrdenDetalle = document.getElementById('btnCancelarOrdenDetalle');
    const btnImprimirComanda = document.getElementById('btnImprimirComanda');
    const btnProcesarPago = document.getElementById('btnProcesarPago');
    const btnCompletarPago = document.getElementById('btnCompletarPago');
    
    // Orden seleccionada actualmente
    let ordenSeleccionada = null;
    
    // Eventos
    
    // Filtrar órdenes
    document.querySelectorAll('[data-filter]').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const filtro = this.dataset.filter;
            filtrarOrdenes(filtro);
        });
    });
    
    // Seleccionar orden
    if (listaOrdenes) {
        listaOrdenes.addEventListener('click', function(e) {
            const ordenItem = e.target.closest('.orden-item');
            if (ordenItem) {
                const ordenId = ordenItem.dataset.id;
                seleccionarOrden(ordenId);
                
                // Marcar como activa
                document.querySelectorAll('.orden-item').forEach(item => {
                    item.classList.remove('active');
                });
                ordenItem.classList.add('active');
            }
        });
    }
    
    // Cambiar estado de la orden
    if (btnActualizarEstado) {
        btnActualizarEstado.addEventListener('click', actualizarEstadoOrden);
    }
    
    // Cancelar orden
    if (btnCancelarOrdenDetalle) {
        btnCancelarOrdenDetalle.addEventListener('click', cancelarOrden);
    }
    
    // Imprimir comanda
    if (btnImprimirComanda) {
        btnImprimirComanda.addEventListener('click', imprimirComanda);
    }
    
    // Procesar pago
    if (btnProcesarPago) {
        btnProcesarPago.addEventListener('click', mostrarProcesarPago);
    }
    
    // Completar pago
    if (btnCompletarPago) {
        btnCompletarPago.addEventListener('click', completarPago);
    }
    
    // Calcular cambio al ingresar monto recibido
    const montoRecibido = document.getElementById('montoRecibido');
    if (montoRecibido) {
        montoRecibido.addEventListener('input', calcularCambio);
    }
    
    // Cambiar método de pago
    const metodoPago = document.getElementById('metodoPago');
    if (metodoPago) {
        metodoPago.addEventListener('change', function() {
            const efectivoContainer = document.getElementById('efectivoContainer');
            const tarjetaContainer = document.getElementById('tarjetaContainer');
            
            if (this.value === 'efectivo') {
                efectivoContainer.style.display = 'block';
                tarjetaContainer.style.display = 'none';
            } else if (this.value === 'tarjeta') {
                efectivoContainer.style.display = 'none';
                tarjetaContainer.style.display = 'block';
            } else {
                efectivoContainer.style.display = 'block';
                tarjetaContainer.style.display = 'block';
            }
        });
    }
    
    // Inicialización
    inicializar();
    
    /**
     * Inicializa la página
     */
    function inicializar() {
        // Ocultar detalles de orden
        if (ordenNoSeleccionada && ordenDetalle) {
            ordenNoSeleccionada.style.display = 'block';
            ordenDetalle.style.display = 'none';
        }
        
        // Si hay una orden en la URL, seleccionarla
        const urlParams = new URLSearchParams(window.location.search);
        const ordenId = urlParams.get('orden');
        if (ordenId) {
            seleccionarOrden(ordenId);
            
            // Marcar como activa en la lista
            const ordenItem = document.querySelector(`.orden-item[data-id="${ordenId}"]`);
            if (ordenItem) {
                ordenItem.classList.add('active');
            }
        }
    }
    
    /**
     * Filtra las órdenes según criterio
     * @param {string} filtro - Criterio de filtrado
     */
    function filtrarOrdenes(filtro) {
        const items = document.querySelectorAll('.orden-item');
        
        items.forEach(item => {
            if (filtro === 'todas') {
                item.style.display = 'block';
            } else if (item.dataset.estado === filtro || item.dataset.tipo === filtro) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }
    
    /**
     * Selecciona una orden y muestra sus detalles
     * @param {string} ordenId - ID de la orden
     */
    function seleccionarOrden(ordenId) {
        // Mostrar spinner de carga
        if (ordenDetalle) {
            ordenDetalle.innerHTML = `
                <div class="text-center py-5">
                    <div class="spinner-border text-primary" role="status"></div>
                    <p class="mt-3">Cargando detalles de la orden...</p>
                </div>
            `;
            ordenDetalle.style.display = 'block';
        }
        if (ordenNoSeleccionada) {
            ordenNoSeleccionada.style.display = 'none';
        }
        
        // Obtener detalles de la orden
        fetch(`/api/cajero/orden/${ordenId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    ordenSeleccionada = data.orden;
                    mostrarDetallesOrden(data.orden);
                } else {
                    throw new Error(data.message || 'Error al cargar detalles de la orden');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (ordenDetalle) {
                    ordenDetalle.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            ${error.message || 'Error al cargar detalles de la orden'}
                        </div>
                    `;
                }
            });
    }
    
    /**
     * Muestra los detalles de la orden
     * @param {Object} orden - Datos de la orden
     */
    function mostrarDetallesOrden(orden) {
        if (!ordenDetalle) return;
        
        // Mostrar contenedor de detalles
        ordenNoSeleccionada.style.display = 'none';
        ordenDetalle.style.display = 'block';
        
        // Actualizar información básica
        if (ordenTitulo) ordenTitulo.textContent = `Orden #${orden.numero}`;
        if (ordenNumeroDetalle) ordenNumeroDetalle.textContent = `#${orden.numero}`;
        if (ordenEstadoDetalle) {
            ordenEstadoDetalle.textContent = orden.estado_display;
            ordenEstadoDetalle.className = `badge ${getEstadoClass(orden.estado)}`;
        }
        
        // Actualizar detalles
        if (ordenFechaHora) ordenFechaHora.textContent = orden.fecha_hora;
        if (ordenTipo) ordenTipo.textContent = orden.tipo_display;
        if (ordenMesa) ordenMesa.textContent = orden.mesa ? `Mesa ${orden.mesa.numero}` : 'N/A';
        if (ordenCliente) ordenCliente.textContent = orden.cliente ? orden.cliente.nombre : 'Cliente General';
        if (ordenCajero) ordenCajero.textContent = orden.cajero ? orden.cajero.nombre : 'N/A';
        if (ordenPagada) {
            ordenPagada.textContent = orden.pagada ? 'Pagado' : 'Pendiente de pago';
            ordenPagada.className = orden.pagada ? 'text-success' : 'text-danger';
        }
        if (ordenNotas) ordenNotas.textContent = orden.notas || 'Sin notas';
        
        // Actualizar items
        if (ordenItems) {
            ordenItems.innerHTML = '';
            
            if (orden.items && orden.items.length > 0) {
                orden.items.forEach(item => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${item.producto.nombre}</td>
                        <td>$${item.precio_unitario.toFixed(2)}</td>
                        <td>${item.cantidad}</td>
                        <td>$${item.precio_total.toFixed(2)}</td>
                        <td>
                            <span class="badge ${getItemEstadoClass(item.estado)}">
                                ${item.estado_display || item.estado}
                            </span>
                        </td>
                    `;
                    
                    ordenItems.appendChild(row);
                });
            } else {
                ordenItems.innerHTML = `
                    <tr>
                        <td colspan="5" class="text-center py-3 text-muted">
                            No hay productos en esta orden
                        </td>
                    </tr>
                `;
            }
        }
        
        // Actualizar totales
        if (ordenSubtotal) ordenSubtotal.textContent = `$${orden.subtotal.toFixed(2)}`;
        if (ordenDescuento) ordenDescuento.textContent = `$${orden.descuento.toFixed(2)}`;
        if (ordenImpuestos) ordenImpuestos.textContent = `$${orden.impuestos.toFixed(2)}`;
        if (ordenTotal) ordenTotal.textContent = `$${orden.total.toFixed(2)}`;
        
        // Actualizar selector de estado
        const cambiarEstado = document.getElementById('cambiarEstado');
        if (cambiarEstado) {
            cambiarEstado.value = orden.estado;
        }
        
        // Actualizar botones según estado
        if (btnProcesarPago) {
            btnProcesarPago.disabled = orden.pagada || orden.estado === 'cancelada';
        }
        
        if (btnCancelarOrdenDetalle) {
            btnCancelarOrdenDetalle.disabled = orden.pagada || orden.estado === 'cancelada' || orden.estado === 'entregada';
        }
    }
    
    /**
     * Actualiza el estado de la orden
     */
    function actualizarEstadoOrden() {
        if (!ordenSeleccionada) {
            mostrarAlerta('error', 'No hay una orden seleccionada');
            return;
        }
        
        const cambiarEstado = document.getElementById('cambiarEstado');
        if (!cambiarEstado) return;
        
        const nuevoEstado = cambiarEstado.value;
        
        // Validar cambio de estado
        if (ordenSeleccionada.estado === 'cancelada') {
            mostrarAlerta('error', 'No se puede cambiar el estado de una orden cancelada');
            return;
        }
        
        if (ordenSeleccionada.estado === 'entregada' && nuevoEstado !== 'cerrada') {
            mostrarAlerta('error', 'Una orden entregada solo puede cambiar a estado cerrada');
            return;
        }
        
        if (ordenSeleccionada.pagada && ['abierta', 'en_proceso'].includes(nuevoEstado)) {
            mostrarAlerta('error', 'No se puede cambiar a un estado anterior una orden ya pagada');
            return;
        }
        
        // Confirmar cambio
        if (!confirm(`¿Está seguro de cambiar el estado de la orden a "${getEstadoNombre(nuevoEstado)}"?`)) {
            return;
        }
        
        // Mostrar spinner de carga
        const btnOriginalText = btnActualizarEstado.innerHTML;
        btnActualizarEstado.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Actualizando...';
        btnActualizarEstado.disabled = true;
        
        // Enviar al servidor
        fetch(`/api/cajero/orden/${ordenSeleccionada.id}/estado/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                estado: nuevoEstado
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Actualizar UI
                ordenSeleccionada.estado = nuevoEstado;
                ordenSeleccionada.estado_display = getEstadoNombre(nuevoEstado);
                
                if (ordenEstadoDetalle) {
                    ordenEstadoDetalle.textContent = ordenSeleccionada.estado_display;
                    ordenEstadoDetalle.className = `badge ${getEstadoClass(nuevoEstado)}`;
                }
                
                // Actualizar orden en la lista
                const ordenItem = document.querySelector(`.orden-item[data-id="${ordenSeleccionada.id}"]`);
                if (ordenItem) {
                    ordenItem.dataset.estado = nuevoEstado;
                    const estadoBadge = ordenItem.querySelector('[class*="bg-"]');
                    if (estadoBadge) {
                        estadoBadge.className = `badge ${getEstadoClass(nuevoEstado)}`;
                        estadoBadge.textContent = getEstadoNombre(nuevoEstado);
                    }
                }
                
                mostrarAlerta('success', 'Estado de la orden actualizado');
            } else {
                throw new Error(data.message || 'Error al actualizar estado');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('error', error.message || 'Error al actualizar estado');
        })
        .finally(() => {
            // Restaurar botón
            btnActualizarEstado.innerHTML = btnOriginalText;
            btnActualizarEstado.disabled = false;
        });
    }
    
    /**
     * Cancela la orden seleccionada
     */
    function cancelarOrden() {
        if (!ordenSeleccionada) {
            mostrarAlerta('error', 'No hay una orden seleccionada');
            return;
        }
        
        // Validar cancelación
        if (ordenSeleccionada.pagada) {
            mostrarAlerta('error', 'No se puede cancelar una orden ya pagada');
            return;
        }
        
        if (ordenSeleccionada.estado === 'cancelada') {
            mostrarAlerta('error', 'Esta orden ya está cancelada');
            return;
        }
        
        if (ordenSeleccionada.estado === 'entregada') {
            mostrarAlerta('error', 'No se puede cancelar una orden ya entregada');
            return;
        }
        
        // Confirmar cancelación
        if (!confirm('¿Está seguro de cancelar esta orden? Esta acción no se puede deshacer.')) {
            return;
        }
        
        // Mostrar spinner de carga
        const btnOriginalText = btnCancelarOrdenDetalle.innerHTML;
        btnCancelarOrdenDetalle.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Cancelando...';
        btnCancelarOrdenDetalle.disabled = true;
        
        // Enviar al servidor
        fetch(`/api/cajero/orden/${ordenSeleccionada.id}/cancelar/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Actualizar UI
                ordenSeleccionada.estado = 'cancelada';
                ordenSeleccionada.estado_display = 'Cancelada';
                
                if (ordenEstadoDetalle) {
                    ordenEstadoDetalle.textContent = 'Cancelada';
                    ordenEstadoDetalle.className = 'badge bg-danger';
                }
                
                // Actualizar orden en la lista
                const ordenItem = document.querySelector(`.orden-item[data-id="${ordenSeleccionada.id}"]`);
                if (ordenItem) {
                    ordenItem.dataset.estado = 'cancelada';
                    const estadoBadge = ordenItem.querySelector('[class*="bg-"]');
                    if (estadoBadge) {
                        estadoBadge.className = 'badge bg-danger';
                        estadoBadge.textContent = 'Cancelada';
                    }
                }
                
                // Deshabilitar botones
                if (btnProcesarPago) btnProcesarPago.disabled = true;
                if (btnCancelarOrdenDetalle) btnCancelarOrdenDetalle.disabled = true;
                
                mostrarAlerta('success', 'Orden cancelada correctamente');
            } else {
                throw new Error(data.message || 'Error al cancelar orden');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('error', error.message || 'Error al cancelar orden');
        })
        .finally(() => {
            // Restaurar botón
            btnCancelarOrdenDetalle.innerHTML = btnOriginalText;
            btnCancelarOrdenDetalle.disabled = false;
        });
    }
    
    /**
     * Imprime la comanda de la orden
     */
    function imprimirComanda() {
        if (!ordenSeleccionada) {
            mostrarAlerta('error', 'No hay una orden seleccionada');
            return;
        }
        
        // Generar HTML de la comanda
        let comandaHTML = `
            <html>
                <head>
                    <title>Comanda #${ordenSeleccionada.numero}</title>
                    <style>
                        body {
                            font-family: 'Courier New', Courier, monospace;
                            font-size: 12px;
                            line-height: 1.2;
                            width: 80mm;
                            margin: 0 auto;
                        }
                        .comanda-header {
                            text-align: center;
                            margin-bottom: 10px;
                        }
                        .comanda-info {
                            margin-bottom: 10px;
                        }
                        .comanda-items {
                            width: 100%;
                            border-top: 1px dashed #000;
                            border-bottom: 1px dashed #000;
                            margin: 10px 0;
                            padding: 10px 0;
                        }
                        .comanda-footer {
                            text-align: center;
                            margin-top: 10px;
                            font-size: 10px;
                        }
                    </style>
                </head>
                <body>
                    <div class="comanda-header">
                        <h3>COMANDA - COCINA</h3>
                        <p>Orden: #${ordenSeleccionada.numero}</p>
                        <p>Fecha: ${ordenSeleccionada.fecha_hora}</p>
                    </div>
                    
                    <div class="comanda-info">
                        <p><strong>Tipo:</strong> ${ordenSeleccionada.tipo_display}</p>
                        ${ordenSeleccionada.mesa ? `<p><strong>Mesa:</strong> ${ordenSeleccionada.mesa.numero}</p>` : ''}
                        <p><strong>Cajero:</strong> ${ordenSeleccionada.cajero ? ordenSeleccionada.cajero.nombre : 'N/A'}</p>
                    </div>
                    
                    <div class="comanda-items">
                        <table style="width: 100%;">
                            <thead>
                                <tr>
                                    <th style="text-align: left;">Producto</th>
                                    <th style="text-align: right;">Cant.</th>
                                </tr>
                            </thead>
                            <tbody>
        `;
        
        ordenSeleccionada.items.forEach(item => {
            comandaHTML += `
                <tr>
                    <td style="text-align: left;">${item.producto.nombre}</td>
                    <td style="text-align: right;">${item.cantidad}</td>
                </tr>
            `;
        });
        
        comandaHTML += `
                            </tbody>
                        </table>
                    </div>
                    
                    ${ordenSeleccionada.notas ? `
                        <div class="comanda-info">
                            <p><strong>Notas:</strong> ${ordenSeleccionada.notas}</p>
                        </div>
                    ` : ''}
                    
                    <div class="comanda-footer">
                        <p>PREPARAR INMEDIATAMENTE</p>
                        <p>SUSHI RESTAURANT</p>
                    </div>
                </body>
            </html>
        `;
        
        // Crear ventana de impresión
        const ventanaImpresion = window.open('', '_blank');
        ventanaImpresion.document.write(comandaHTML);
        ventanaImpresion.document.close();
        ventanaImpresion.focus();
        ventanaImpresion.print();
        ventanaImpresion.close();
    }
    
    /**
     * Muestra el modal para procesar pago
     */
    function mostrarProcesarPago() {
        if (!ordenSeleccionada) {
            mostrarAlerta('error', 'No hay una orden seleccionada');
            return;
        }
        
        // Validar estado
        if (ordenSeleccionada.pagada) {
            mostrarAlerta('error', 'Esta orden ya está pagada');
            return;
        }
        
        if (ordenSeleccionada.estado === 'cancelada') {
            mostrarAlerta('error', 'No se puede procesar el pago de una orden cancelada');
            return;
        }
        
        // Establecer total a pagar
        const totalAPagar = document.getElementById('totalAPagar');
        if (totalAPagar) {
            totalAPagar.value = ordenSeleccionada.total.toFixed(2);
        }
        
        // Mostrar modal
        const pagoModal = new bootstrap.Modal(document.getElementById('pagoModal'));
        pagoModal.show();
    }
    
    /**
     * Calcula el cambio a devolver
     */
    function calcularCambio() {
        const montoRecibido = document.getElementById('montoRecibido');
        const cambio = document.getElementById('cambio');
        const totalAPagar = document.getElementById('totalAPagar');
        
        if (!montoRecibido || !cambio || !totalAPagar) return;
        
        const monto = parseFloat(montoRecibido.value) || 0;
        const total = parseFloat(totalAPagar.value) || 0;
        
        const cambioCalculado = monto - total;
        cambio.value = cambioCalculado > 0 ? cambioCalculado.toFixed(2) : '0.00';
    }
    
    /**
     * Completa el pago de la orden
     */
    function completarPago() {
        if (!ordenSeleccionada) {
            mostrarAlerta('error', 'No hay una orden seleccionada');
            return;
        }
        
        // Obtener datos del formulario
        const metodoPago = document.getElementById('metodoPago').value;
        const montoRecibidoValue = parseFloat(document.getElementById('montoRecibido').value) || 0;
        const cambioValue = parseFloat(document.getElementById('cambio').value) || 0;
        const referencia = document.getElementById('referenciaPago') ? document.getElementById('referenciaPago').value : '';
        const imprimirTicket = document.getElementById('imprimirTicket') ? document.getElementById('imprimirTicket').checked : true;
        
        // Validar datos según método de pago
        if (metodoPago === 'efectivo' && montoRecibidoValue < ordenSeleccionada.total) {
            alert('El monto recibido debe ser mayor o igual al total a pagar.');
            return;
        }
        
        if (metodoPago === 'tarjeta' && !referencia) {
            alert('Debe ingresar una referencia para el pago con tarjeta.');
            return;
        }
        
        // Preparar datos para enviar al servidor
        const pagoData = {
            orden_id: ordenSeleccionada.id,
            metodo_pago: metodoPago,
            monto_recibido: montoRecibidoValue,
            cambio: cambioValue,
            referencia_pago: referencia
        };
        
        // Mostrar spinner de carga
        const btnOriginalText = btnCompletarPago.innerHTML;
        btnCompletarPago.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Procesando...';
        btnCompletarPago.disabled = true;
        
        // Enviar al servidor
        fetch('/api/cajero/procesar-pago/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(pagoData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Cerrar modal
                const pagoModal = bootstrap.Modal.getInstance(document.getElementById('pagoModal'));
                pagoModal.hide();
                
                // Actualizar UI
                ordenSeleccionada.pagada = true;
                ordenSeleccionada.estado = 'cerrada';
                ordenSeleccionada.estado_display = 'Cerrada';
                
                if (ordenEstadoDetalle) {
                    ordenEstadoDetalle.textContent = 'Cerrada';
                    ordenEstadoDetalle.className = 'badge bg-secondary';
                }
                
                if (ordenPagada) {
                    ordenPagada.textContent = 'Pagado';
                    ordenPagada.className = 'text-success';
                }
                
                // Actualizar orden en la lista
                const ordenItem = document.querySelector(`.orden-item[data-id="${ordenSeleccionada.id}"]`);
                if (ordenItem) {
                    ordenItem.dataset.estado = 'cerrada';
                    const estadoBadge = ordenItem.querySelector('[class*="bg-"]');
                    if (estadoBadge) {
                        estadoBadge.className = 'badge bg-secondary';
                        estadoBadge.textContent = 'Cerrada';
                    }
                    
                    // Quitar badge de pendiente de pago
                    const pagoBadge = ordenItem.querySelector('.bg-danger');
                    if (pagoBadge) {
                        pagoBadge.remove();
                    }
                }
                
                // Deshabilitar botones
                if (btnProcesarPago) btnProcesarPago.disabled = true;
                if (btnCancelarOrdenDetalle) btnCancelarOrdenDetalle.disabled = true;
                
                // Mostrar ticket si está habilitado
                if (imprimirTicket) {
                    mostrarTicket(data.venta);
                }
                
                mostrarAlerta('success', 'Pago procesado correctamente');
            } else {
                throw new Error(data.message || 'Error al procesar pago');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('error', error.message || 'Error al procesar pago');
        })
        .finally(() => {
            // Restaurar botón
            btnCompletarPago.innerHTML = btnOriginalText;
            btnCompletarPago.disabled = false;
        });
    }
    
    /**
     * Muestra el ticket de venta
     */
    function mostrarTicket(venta) {
        const ticketContainer = document.getElementById('ticketContainer');
        if (!ticketContainer) return;
        
        // Generar HTML del ticket
        ticketContainer.innerHTML = `
            <div class="ticket-header">
                <h5>SUSHI RESTAURANT</h5>
                <p>Sucursal: ${venta.sucursal}</p>
                <p>Ticket: ${venta.numero_factura || venta.id}</p>
                <p>Fecha: ${venta.fecha_hora}</p>
            </div>
            
            <div class="ticket-info">
                <p>Cajero: ${venta.cajero.nombre}</p>
                <p>Cliente: ${venta.cliente ? venta.cliente.nombre : 'Cliente General'}</p>
                <p>Método de pago: ${venta.metodo_pago_display}</p>
            </div>
            
            <div class="ticket-items">
                <table style="width: 100%;">
                    <thead>
                        <tr>
                            <th style="text-align: left;">Producto</th>
                            <th style="text-align: right;">Cant.</th>
                            <th style="text-align: right;">Precio</th>
                            <th style="text-align: right;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${venta.detalles.map(detalle => `
                            <tr>
                                <td style="text-align: left;">${detalle.producto.nombre}</td>
                                <td style="text-align: right;">${detalle.cantidad}</td>
                                <td style="text-align: right;">$${detalle.precio_unitario.toFixed(2)}</td>
                                <td style="text-align: right;">$${detalle.precio_total.toFixed(2)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            
            <div class="ticket-total">
                <p>Subtotal: $${venta.subtotal.toFixed(2)}</p>
                ${venta.descuento > 0 ? `<p>Descuento: $${venta.descuento.toFixed(2)}</p>` : ''}
                ${venta.impuestos > 0 ? `<p>Impuestos: $${venta.impuestos.toFixed(2)}</p>` : ''}
                <p>TOTAL: $${venta.total.toFixed(2)}</p>
                
                ${venta.metodo_pago === 'efectivo' ? `
                    <p>Efectivo: $${venta.monto_recibido.toFixed(2)}</p>
                    <p>Cambio: $${venta.cambio.toFixed(2)}</p>
                ` : ''}
            </div>
            
            <div class="ticket-footer">
                <p>¡Gracias por su compra!</p>
                <p>www.sushirestaurant.com</p>
            </div>
        `;
        
        // Mostrar modal
        const ticketModal = new bootstrap.Modal(document.getElementById('ticketModal'));
        ticketModal.show();
    }
    
    /**
     * Obtiene la clase CSS para el estado de la orden
     * @param {string} estado - Estado de la orden
     * @returns {string} Clase CSS
     */
    function getEstadoClass(estado) {
        switch (estado) {
            case 'abierta':
                return 'bg-info';
            case 'en_proceso':
                return 'bg-warning';
            case 'lista':
                return 'bg-success';
            case 'entregada':
                return 'bg-primary';
            case 'cancelada':
                return 'bg-danger';
            case 'cerrada':
                return 'bg-secondary';
            default:
                return 'bg-secondary';
        }
    }
    
    /**
     * Obtiene la clase CSS para el estado de un item
     * @param {string} estado - Estado del item
     * @returns {string} Clase CSS
     */
    function getItemEstadoClass(estado) {
        switch (estado) {
            case 'pendiente':
                return 'bg-warning';
            case 'en_preparacion':
                return 'bg-info';
            case 'listo':
                return 'bg-success';
            case 'cancelado':
                return 'bg-danger';
            default:
                return 'bg-secondary';
        }
    }
    
    /**
     * Obtiene el nombre del estado
     * @param {string} estado - Estado de la orden
     * @returns {string} Nombre del estado
     */
    function getEstadoNombre(estado) {
        switch (estado) {
            case 'abierta':
                return 'Abierta';
            case 'en_proceso':
                return 'En Proceso';
            case 'lista':
                return 'Lista para Entrega';
            case 'entregada':
                return 'Entregada';
            case 'cancelada':
                return 'Cancelada';
            case 'cerrada':
                return 'Cerrada';
            default:
                return estado;
        }
    }
    
    /**
     * Muestra una alerta
     * @param {string} tipo - Tipo de alerta (success, error, info, warning)
     * @param {string} mensaje - Mensaje a mostrar
     */
    function mostrarAlerta(tipo, mensaje) {
        const alertaContainer = document.createElement('div');
        alertaContainer.className = `alert alert-${tipo === 'error' ? 'danger' : tipo} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
        alertaContainer.style.zIndex = '9999';
        alertaContainer.innerHTML = `
            <i class="fas fa-${tipo === 'success' ? 'check-circle' : tipo === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.body.appendChild(alertaContainer);
        
        // Remover después de 5 segundos
        setTimeout(() => {
            if (alertaContainer.parentNode) {
                alertaContainer.parentNode.removeChild(alertaContainer);
            }
        }, 5000);
    }
    
    /**
     * Obtiene el token CSRF
     * @returns {string} Token CSRF
     */
    function getCsrfToken() {
        const csrfCookie = document.cookie.split(';').find(cookie => cookie.trim().startsWith('csrftoken='));
        return csrfCookie ? csrfCookie.split('=')[1] : '';
    }
});
