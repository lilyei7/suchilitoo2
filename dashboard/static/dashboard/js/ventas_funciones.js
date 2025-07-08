/**
 * Módulo de Ventas - Integración con sistema de costos
 * Permite vender productos y descontar automáticamente el inventario
 * Calcula costos reales usando historial de precios (PEPS o Promedio)
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Iniciando módulo de Ventas con integración de costos');
    
    // Referencias a elementos del DOM
    const btnVenderProducto = document.getElementById('btnVenderProducto');
    const productoSelect = document.getElementById('producto');
    const cantidadInput = document.getElementById('cantidad');
    const sucursalSelect = document.getElementById('sucursal');
    const metodoCosteoSelect = document.getElementById('metodoCosteo');
    const btnSimularCosto = document.getElementById('btnSimularCosto');
    const btnConfirmarVenta = document.getElementById('btnConfirmarVenta');
    
    // Elementos de resultados
    const resultadoSimulacion = document.getElementById('resultadoSimulacion');
    const resultadoVenta = document.getElementById('resultadoVenta');
    const alertaStock = document.getElementById('alertaStock');
    
    // Eventos
    if (btnSimularCosto) {
        btnSimularCosto.addEventListener('click', simularCostoProducto);
    }
    
    if (btnConfirmarVenta) {
        btnConfirmarVenta.addEventListener('click', registrarVenta);
    }
    
    if (productoSelect) {
        productoSelect.addEventListener('change', actualizarInfoProducto);
    }
    
    /**
     * Actualiza información del producto seleccionado
     */
    function actualizarInfoProducto() {
        const productoId = productoSelect.value;
        if (!productoId) return;
        
        // Actualizar información del producto (precio, descripción, etc.)
        const productoSeleccionado = productoSelect.options[productoSelect.selectedIndex];
        const precio = productoSeleccionado.dataset.precio;
        const descripcion = productoSeleccionado.dataset.descripcion;
        
        const infoProducto = document.getElementById('infoProducto');
        if (infoProducto) {
            infoProducto.innerHTML = `
                <div class="alert alert-info">
                    <h5>${productoSeleccionado.text}</h5>
                    <p>${descripcion || 'Sin descripción'}</p>
                    <strong>Precio: $${precio || '0.00'}</strong>
                </div>
            `;
        }
    }
    
    /**
     * Simula el costo de un producto sin registrar la venta
     */
    function simularCostoProducto(e) {
        e.preventDefault();
        
        // Validar campos
        const productoId = productoSelect.value;
        const cantidad = parseFloat(cantidadInput.value);
        const sucursalId = sucursalSelect.value;
        const metodoCosteo = metodoCosteoSelect.value;
        
        if (!productoId || !cantidad || !sucursalId) {
            mostrarAlerta('error', 'Debe completar todos los campos');
            return;
        }
        
        // Mostrar indicador de carga
        resultadoSimulacion.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"></div><p>Calculando costos...</p></div>';
        
        // Hacer petición a la API de cálculo de costos
        fetch('/dashboard/api/calcular-costo/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            params: {
                producto_id: productoId,
                cantidad: cantidad,
                sucursal_id: sucursalId,
                metodo_costeo: metodoCosteo
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Mostrar resultado de la simulación
                mostrarResultadoSimulacion(data);
            } else {
                throw new Error(data.message || 'Error al calcular costos');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultadoSimulacion.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    ${error.message || 'Error al calcular costos'}
                </div>
            `;
        });
    }
    
    /**
     * Registra la venta y descuenta el inventario
     */
    function registrarVenta(e) {
        e.preventDefault();
        
        // Validar campos
        const productoId = productoSelect.value;
        const cantidad = parseFloat(cantidadInput.value);
        const sucursalId = sucursalSelect.value;
        const metodoCosteo = metodoCosteoSelect.value;
        
        if (!productoId || !cantidad || !sucursalId) {
            mostrarAlerta('error', 'Debe completar todos los campos');
            return;
        }
        
        // Confirmar la venta
        if (!confirm('¿Está seguro de realizar esta venta? Se descontará el inventario.')) {
            return;
        }
        
        // Mostrar indicador de carga
        resultadoVenta.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"></div><p>Procesando venta...</p></div>';
        
        // Hacer petición a la API para registrar la venta
        fetch('/dashboard/api/venta-producto/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                producto_id: productoId,
                cantidad: cantidad,
                sucursal_id: sucursalId,
                metodo_costeo: metodoCosteo
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Mostrar resultado de la venta
                mostrarResultadoVenta(data);
                // Limpiar formulario
                limpiarFormulario();
            } else {
                throw new Error(data.message || 'Error al registrar la venta');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultadoVenta.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    ${error.message || 'Error al registrar la venta'}
                </div>
            `;
        });
    }
    
    /**
     * Muestra el resultado de la simulación de costos
     */
    function mostrarResultadoSimulacion(data) {
        const productoNombre = productoSelect.options[productoSelect.selectedIndex].text;
        const cantidad = parseFloat(cantidadInput.value);
        
        resultadoSimulacion.innerHTML = `
            <div class="card border-info mb-3">
                <div class="card-header bg-info text-white">
                    <i class="fas fa-calculator me-2"></i>
                    Simulación de Costos
                </div>
                <div class="card-body">
                    <h5 class="card-title">${productoNombre} x ${cantidad}</h5>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Costo Total:</strong> $${data.costo_total.toFixed(2)}</p>
                            <p><strong>Costo Unitario:</strong> $${(data.costo_total / cantidad).toFixed(2)}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Precio Venta:</strong> $${data.precio_venta.toFixed(2)}</p>
                            <p><strong>Margen:</strong> ${data.margen.toFixed(2)}%</p>
                        </div>
                    </div>
                    
                    <h6>Desglose de Insumos:</h6>
                    <table class="table table-sm table-striped">
                        <thead>
                            <tr>
                                <th>Insumo</th>
                                <th>Cantidad</th>
                                <th>Costo</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.detalles.map(detalle => `
                                <tr>
                                    <td>${detalle.insumo_nombre}</td>
                                    <td>${detalle.cantidad} ${detalle.unidad}</td>
                                    <td>$${detalle.costo.toFixed(2)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        // Mostrar alertas de stock si existen
        if (data.alertas && data.alertas.length > 0) {
            alertaStock.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Advertencia de Stock:</strong>
                    <ul>
                        ${data.alertas.map(alerta => `
                            <li>${alerta.insumo}: Faltante de ${alerta.faltante} ${alerta.unidad}</li>
                        `).join('')}
                    </ul>
                </div>
            `;
        } else {
            alertaStock.innerHTML = '';
        }
    }
    
    /**
     * Muestra el resultado de la venta
     */
    function mostrarResultadoVenta(data) {
        resultadoVenta.innerHTML = `
            <div class="card border-success mb-3">
                <div class="card-header bg-success text-white">
                    <i class="fas fa-check-circle me-2"></i>
                    Venta Registrada Exitosamente
                </div>
                <div class="card-body">
                    <h5 class="card-title">${data.producto.nombre} x ${data.cantidad}</h5>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Fecha:</strong> ${data.fecha}</p>
                            <p><strong>Precio Unitario:</strong> $${data.precio_unitario.toFixed(2)}</p>
                            <p><strong>Precio Total:</strong> $${data.precio_total.toFixed(2)}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Costo Total:</strong> $${data.costo_total.toFixed(2)}</p>
                            <p><strong>Margen:</strong> ${data.margen.toFixed(2)}%</p>
                            <p><strong>Utilidad:</strong> $${(data.precio_total - data.costo_total).toFixed(2)}</p>
                        </div>
                    </div>
                    
                    <h6>Insumos Descontados:</h6>
                    <table class="table table-sm table-striped">
                        <thead>
                            <tr>
                                <th>Insumo</th>
                                <th>Cantidad</th>
                                <th>Costo</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.detalles.map(detalle => `
                                <tr>
                                    <td>${detalle.insumo_nombre}</td>
                                    <td>${detalle.cantidad_utilizada} ${detalle.unidad}</td>
                                    <td>$${detalle.costo.toFixed(2)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                <div class="card-footer">
                    <button type="button" class="btn btn-outline-success" onclick="window.print()">
                        <i class="fas fa-print me-2"></i> Imprimir
                    </button>
                </div>
            </div>
        `;
        
        // Mostrar mensaje de éxito
        mostrarAlerta('success', 'Venta registrada y stock descontado exitosamente');
    }
    
    /**
     * Limpia el formulario después de una venta
     */
    function limpiarFormulario() {
        productoSelect.value = '';
        cantidadInput.value = '1';
        
        // Limpiar información del producto
        const infoProducto = document.getElementById('infoProducto');
        if (infoProducto) {
            infoProducto.innerHTML = '';
        }
        
        // Limpiar simulación
        resultadoSimulacion.innerHTML = '';
    }
    
    /**
     * Muestra una alerta al usuario
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
            alertaDiv.remove();
        }, 5000);
    }
    
    /**
     * Obtiene el token CSRF de las cookies
     */
    function getCsrfToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        
        return cookieValue || '';
    }
});
