/**
 * Sistema POS - Cajero App
 * Tablet-optimized Point of Sale System
 */

document.addEventListener('DOMContentLoaded', function() {
    // Estado de la orden actual
    let ordenActual = {
        items: [],
        subtotal: 0,
        descuento: 0,
        iva: 0,
        total: 0
    };

    // Referencias DOM
    const orderItems = document.querySelector('.order-items');
    const subtotalEl = document.getElementById('subtotal');
    const descuentoEl = document.getElementById('descuento');
    const ivaEl = document.getElementById('iva');
    const totalEl = document.getElementById('total');

    // Estado para ingredientes personalizados
    window.ingredientesSeleccionados = {};

    // Ingredientes por producto de ejemplo
    const ingredientesPorProducto = {
        bebida1: ['Agua', 'Hielo', 'Azúcar', 'Limón'], // Té Helado
        bebida2: ['Agua', 'Azúcar', 'Limón', 'Miel'],  // Té Caliente
        bebida3: ['Café', 'Agua', 'Azúcar', 'Leche'],  // Café
        bebida4: ['Agua', 'Limón', 'Azúcar', 'Hielo'], // Limonada
        sushi1: ['Arroz', 'Salmón', 'Alga', 'Aguacate', 'Queso Crema'], // Sushi Salmón
        sushi2: ['Arroz', 'Atún', 'Alga', 'Pepino', 'Ajonjolí'], // Sushi Atún
        ceviche1: ['Camarón', 'Jitomate', 'Cilantro', 'Cebolla', 'Limón', 'Aguacate'], // Ceviche Camarón
        ceviche2: ['Camarón', 'Pescado', 'Jitomate', 'Cilantro', 'Cebolla', 'Limón', 'Aguacate'], // Ceviche Mixto
        tostada1: ['Tostada', 'Atún', 'Mayonesa', 'Aguacate', 'Cebolla'], // Tostada Atún
        tostada2: ['Tostada', 'Camarón', 'Mayonesa', 'Aguacate', 'Cebolla'] // Tostada Camarón
    };

    // Iconos para ingredientes
    const iconosIngredientes = {
        Agua: '💧', Hielo: '🧊', Azúcar: '🍬', Limón: '🍋', Miel: '🍯',
        Café: '☕', Leche: '🥛', Salmón: '🐟', Atún: '🐟', Alga: '🌿',
        Arroz: '🍚', Aguacate: '🥑', Queso: '🧀', QuesoCrema: '🧀',
        Pepino: '🥒', Ajonjolí: '🌰', Camarón: '🦐', Jitomate: '🍅',
        Cilantro: '🌱', Cebolla: '🧅', Pescado: '🐟', Tostada: '🥙',
        Mayonesa: '🥄'
    };

    // === EVENT LISTENERS ===

    // Botones de cantidad (+ y -)
    document.querySelectorAll('.modern-qty-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const action = this.getAttribute('data-action');
            const input = this.parentElement.querySelector('.modern-qty-input');
            let value = parseInt(input.value) || 1;
            
            if (action === 'increase') {
                value = Math.min(value + 1, 99); // Máximo 99
            } else if (action === 'decrease') {
                value = Math.max(value - 1, 1); // Mínimo 1
            }
            
            input.value = value;
            
            // Haptic feedback
            hapticFeedback();
        });
    });

    // Checkboxes de productos
    document.querySelectorAll('.modern-product-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const card = this.closest('.modern-product-card');
            
            if (this.checked) {
                card.classList.add('selected');
                // Auto-focus en cantidad si está seleccionado
                const qtyInput = card.querySelector('.modern-qty-input');
                if (qtyInput) qtyInput.focus();
            } else {
                card.classList.remove('selected');
            }
            
            hapticFeedback();
        });
    });

    // Botones "Agregar"
    document.querySelectorAll('.btn-agregar-producto').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const productoId = this.getAttribute('data-producto-id');
            const card = this.closest('.modern-product-card');
            const checkbox = card.querySelector('.modern-product-checkbox');
            
            if (!checkbox.checked) {
                // Auto-seleccionar si no está marcado
                checkbox.checked = true;
                checkbox.dispatchEvent(new Event('change'));
            }
            
            const nombre = card.querySelector('.modern-product-name').textContent;
            const precio = parseFloat(card.querySelector('.modern-product-price').textContent.replace(/[^\d.]/g, ''));
            const qtyInput = card.querySelector('.modern-qty-input');
            let cantidad = parseInt(qtyInput.value) || 1;
            
            // Ingredientes seleccionados (por defecto todos)
            let ingredientes = (window.ingredientesSeleccionados && window.ingredientesSeleccionados[productoId])
                ? window.ingredientesSeleccionados[productoId].slice()
                : (ingredientesPorProducto[productoId] || []).slice();
            
            // Agregar producto
            agregarProductoAOrden(productoId, nombre, precio, cantidad, ingredientes);
            
            // Reset checkbox y cantidad
            checkbox.checked = false;
            card.classList.remove('selected');
            qtyInput.value = 1;
            
            // Feedback visual
            this.classList.add('loading');
            setTimeout(() => {
                this.classList.remove('loading');
            }, 500);
            
            hapticFeedback();
        });
    });

    // Botones de ingredientes
    document.querySelectorAll('.btn-ingredientes').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const productoId = this.getAttribute('data-producto-id');
            abrirModalIngredientes(productoId);
        });
    });

    // Botón nueva orden
    const btnNewOrder = document.querySelector('.btn-new-order');
    if (btnNewOrder) {
        btnNewOrder.addEventListener('click', function() {
            if (ordenActual.items.length > 0) {
                if (confirm('¿Está seguro que desea crear una nueva orden? La orden actual se perderá.')) {
                    limpiarOrden();
                }
            } else {
                limpiarOrden();
            }
        });
    }

    // Botón guardar orden
    const btnSaveOrder = document.querySelector('.btn-save-order');
    if (btnSaveOrder) {
        btnSaveOrder.addEventListener('click', guardarOrden);
    }

    // === FUNCIONES PRINCIPALES ===

    function agregarProductoAOrden(productoId, nombre, precio, cantidad, ingredientes) {
        // Buscar si ya existe el mismo producto con los mismos ingredientes
        let itemExistente = ordenActual.items.find(item => 
            item.productoId === productoId && 
            JSON.stringify(item.ingredientes) === JSON.stringify(ingredientes)
        );
        
        if (itemExistente) {
            itemExistente.cantidad += cantidad;
            itemExistente.total = itemExistente.cantidad * itemExistente.precio;
        } else {
            ordenActual.items.push({
                id: Date.now() + Math.random(), // ID único
                productoId,
                nombre,
                precio,
                cantidad,
                total: precio * cantidad,
                ingredientes
            });
        }
        
        actualizarOrden();
    }

    function actualizarOrden() {
        // Calcular totales
        ordenActual.subtotal = ordenActual.items.reduce((sum, item) => sum + item.total, 0);
        ordenActual.iva = ordenActual.subtotal * 0.12;
        ordenActual.total = ordenActual.subtotal + ordenActual.iva - ordenActual.descuento;

        // Actualizar UI
        if (subtotalEl) subtotalEl.textContent = '$' + ordenActual.subtotal.toFixed(2);
        if (descuentoEl) descuentoEl.textContent = '$' + ordenActual.descuento.toFixed(2);
        if (ivaEl) ivaEl.textContent = '$' + ordenActual.iva.toFixed(2);
        if (totalEl) totalEl.textContent = '$' + ordenActual.total.toFixed(2);

        // Actualizar lista de items
        actualizarListaItems();
    }

    function actualizarListaItems() {
        if (!orderItems) return;

        if (ordenActual.items.length === 0) {
            orderItems.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="fas fa-shopping-cart fa-3x mb-3 opacity-50"></i>
                    <p>No hay productos agregados</p>
                    <small>Selecciona productos para empezar</small>
                </div>
            `;
            return;
        }

        let html = '';
        ordenActual.items.forEach(item => {
            const ingredientesTexto = item.ingredientes.length < (ingredientesPorProducto[item.productoId] || []).length
                ? 'Sin: ' + (ingredientesPorProducto[item.productoId] || [])
                    .filter(ing => !item.ingredientes.includes(ing))
                    .join(', ')
                : 'Completo';

            html += `
                <div class="order-item" data-item-id="${item.id}">
                    <div class="flex-grow-1">
                        <div class="fw-bold">${item.nombre}</div>
                        <small class="text-muted">${ingredientesTexto}</small>
                        <div class="text-success fw-bold">$${item.precio.toFixed(2)} c/u</div>
                    </div>
                    <div class="item-quantity">
                        <button class="quantity-btn" onclick="cambiarCantidadItem('${item.id}', -1)">-</button>
                        <input type="text" class="quantity-input" value="${item.cantidad}" readonly>
                        <button class="quantity-btn" onclick="cambiarCantidadItem('${item.id}', 1)">+</button>
                    </div>
                    <div class="text-end">
                        <div class="fw-bold">$${item.total.toFixed(2)}</div>
                        <button class="btn btn-sm btn-outline-danger" onclick="eliminarItem('${item.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        });

        orderItems.innerHTML = html;
    }

    function abrirModalIngredientes(productoId) {
        const form = document.getElementById('form-ingredientes');
        if (!form) return;

        form.innerHTML = '';
        
        // Agregar ingredientes como switches
        (ingredientesPorProducto[productoId] || []).forEach((ing, idx) => {
            const ingId = `ing-${productoId}-${idx}`;
            const icon = iconosIngredientes[ing.replace(/\s/g, '')] || '🥗';
            const checked = !window.ingredientesSeleccionados[productoId] || 
                           window.ingredientesSeleccionados[productoId].includes(ing);
            
            form.innerHTML += `
                <div class='form-check form-switch mb-3'>
                    <input class='form-check-input' type='checkbox' value='${ing}' id='${ingId}' ${checked ? 'checked' : ''}>
                    <label class='form-check-label' for='${ingId}'>
                        <span style="font-size: 1.2rem; margin-right: 8px;">${icon}</span>
                        ${ing}
                    </label>
                </div>
            `;
        });

        // Configurar botón guardar
        const btnGuardar = document.getElementById('guardarIngredientes');
        if (btnGuardar) {
            btnGuardar.onclick = function() {
                const checkboxes = form.querySelectorAll('input[type="checkbox"]');
                const seleccionados = [];
                
                checkboxes.forEach(cb => {
                    if (cb.checked) {
                        seleccionados.push(cb.value);
                    }
                });
                
                window.ingredientesSeleccionados[productoId] = seleccionados;
                
                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('ingredientesModal'));
                if (modal) modal.hide();
                
                hapticFeedback();
            };
        }

        // Abrir modal
        const modal = new bootstrap.Modal(document.getElementById('ingredientesModal'));
        modal.show();
    }

    function limpiarOrden() {
        ordenActual = {
            items: [],
            subtotal: 0,
            descuento: 0,
            iva: 0,
            total: 0
        };
        
        // Limpiar ingredientes seleccionados
        window.ingredientesSeleccionados = {};
        
        // Limpiar checkboxes
        document.querySelectorAll('.modern-product-checkbox').forEach(cb => {
            cb.checked = false;
            cb.closest('.modern-product-card').classList.remove('selected');
        });
        
        // Reset cantidades
        document.querySelectorAll('.modern-qty-input').forEach(input => {
            input.value = 1;
        });
        
        actualizarOrden();
        hapticFeedback();
    }

    function guardarOrden() {
        if (ordenActual.items.length === 0) {
            mostrarAlerta('No hay productos en la orden', 'warning');
            return;
        }

        const data = {
            items: ordenActual.items.map(item => ({
                producto_id: item.productoId,
                cantidad: item.cantidad,
                ingredientes_removidos: (ingredientesPorProducto[item.productoId] || [])
                    .filter(ing => !item.ingredientes.includes(ing))
            }))
        };

        // Mostrar loading
        const btn = document.querySelector('.btn-save-order');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Guardando...';
        btn.disabled = true;

        // Simular guardado (reemplazar con llamada real a la API)
        setTimeout(() => {
            mostrarAlerta('Orden guardada exitosamente', 'success');
            btn.innerHTML = originalText;
            btn.disabled = false;
        }, 1000);
    }

    // === FUNCIONES GLOBALES ===

    window.cambiarCantidadItem = function(itemId, delta) {
        const item = ordenActual.items.find(i => i.id == itemId);
        if (!item) return;

        item.cantidad = Math.max(1, item.cantidad + delta);
        item.total = item.cantidad * item.precio;
        
        actualizarOrden();
        hapticFeedback();
    };

    window.eliminarItem = function(itemId) {
        ordenActual.items = ordenActual.items.filter(i => i.id != itemId);
        actualizarOrden();
        hapticFeedback();
    };

    // === PAYMENT HANDLING ===

    // Mostrar campos según método de pago
    const metodoPagoSelect = document.getElementById('metodoPago');
    if (metodoPagoSelect) {
        metodoPagoSelect.addEventListener('change', function() {
            const metodo = this.value;
            const efectivoFields = document.getElementById('efectivoFields');
            const tarjetaFields = document.getElementById('tarjetaFields');
            const montoCobrarBox = document.getElementById('montoCobrarBox');
            const montoCobrarEl = document.getElementById('montoCobrar');
            
            if (efectivoFields) efectivoFields.style.display = metodo === 'efectivo' ? '' : 'none';
            if (tarjetaFields) tarjetaFields.style.display = metodo === 'tarjeta' ? '' : 'none';
            if (montoCobrarBox) montoCobrarBox.style.display = metodo === 'tarjeta' ? '' : 'none';
            
            if (metodo === 'tarjeta' && montoCobrarEl && totalEl) {
                montoCobrarEl.textContent = totalEl.textContent;
            }
        });
        
        // Inicializar
        metodoPagoSelect.dispatchEvent(new Event('change'));
    }

    // Cálculo automático de cambio
    const montoRecibidoInput = document.getElementById('montoRecibido');
    const cambioInput = document.getElementById('cambio');
    
    if (montoRecibidoInput && cambioInput) {
        montoRecibidoInput.addEventListener('input', function() {
            let recibido = parseFloat(this.value) || 0;
            let total = parseFloat(totalEl.textContent.replace(/[^\d.]/g, '')) || 0;
            let cambio = Math.max(0, recibido - total);
            
            cambioInput.value = '$' + cambio.toFixed(2);
            
            // Colorear según el cambio
            if (recibido < total) {
                cambioInput.classList.add('is-invalid');
                cambioInput.classList.remove('is-valid');
            } else {
                cambioInput.classList.remove('is-invalid');
                cambioInput.classList.add('is-valid');
            }
        });
    }

    window.finalizarPago = function() {
        if (ordenActual.items.length === 0) {
            mostrarAlerta('No hay productos en la orden', 'error');
            return;
        }

        const metodo = metodoPagoSelect.value;
        let isValid = true;

        if (metodo === 'efectivo') {
            const montoRecibido = parseFloat(montoRecibidoInput.value) || 0;
            const total = parseFloat(totalEl.textContent.replace(/[^\d.]/g, '')) || 0;
            
            if (montoRecibido < total) {
                mostrarAlerta('El monto recibido es insuficiente', 'error');
                isValid = false;
            }
        }

        if (!isValid) return;

        // Simular procesamiento de pago
        const btn = document.querySelector('button[onclick="finalizarPago()"]');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';
        btn.disabled = true;

        setTimeout(() => {
            mostrarAlerta('¡Pago procesado exitosamente!', 'success');
            limpiarOrden();
            
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('pagoModal'));
            if (modal) modal.hide();
            
            btn.innerHTML = originalText;
            btn.disabled = false;
            
            // Reset formulario de pago
            document.getElementById('formPago').reset();
            if (cambioInput) cambioInput.value = '';
            metodoPagoSelect.dispatchEvent(new Event('change'));
        }, 2000);
    };

    window.imprimirTicket = function() {
        if (ordenActual.items.length === 0) {
            mostrarAlerta('No hay productos para imprimir', 'warning');
            return;
        }

        let ticket = '═══ SUSHI RESTAURANT ═══\n';
        ticket += `Fecha: ${new Date().toLocaleString('es-ES')}\n`;
        ticket += `Cajero: ${document.querySelector('.navbar-brand + .navbar-nav .nav-link').textContent.trim()}\n`;
        ticket += '═════════════════════════\n\n';
        
        ordenActual.items.forEach(item => {
            ticket += `${item.cantidad}x ${item.nombre}\n`;
            if (item.ingredientes.length < (ingredientesPorProducto[item.productoId] || []).length) {
                const sinIngredientes = (ingredientesPorProducto[item.productoId] || [])
                    .filter(ing => !item.ingredientes.includes(ing));
                ticket += `   Sin: ${sinIngredientes.join(', ')}\n`;
            }
            ticket += `   $${item.precio.toFixed(2)} c/u = $${item.total.toFixed(2)}\n\n`;
        });
        
        ticket += '─────────────────────────\n';
        ticket += `Subtotal: $${ordenActual.subtotal.toFixed(2)}\n`;
        ticket += `IVA (12%): $${ordenActual.iva.toFixed(2)}\n`;
        ticket += `TOTAL: $${ordenActual.total.toFixed(2)}\n`;
        ticket += '═════════════════════════\n';
        ticket += '¡Gracias por su preferencia!\n';
        ticket += 'Vuelva pronto\n';

        // Imprimir usando ventana emergente
        const win = window.open('', '', 'width=400,height=700');
        win.document.write(`
            <html>
                <head>
                    <title>Ticket de Venta</title>
                    <style>
                        body { font-family: 'Courier New', monospace; font-size: 12px; margin: 20px; }
                        pre { white-space: pre-wrap; }
                    </style>
                </head>
                <body onload="window.print(); window.close();">
                    <pre>${ticket}</pre>
                </body>
            </html>
        `);
        win.document.close();
    };

    // === UTILIDADES ===

    function mostrarAlerta(mensaje, tipo = 'info') {
        // Crear y mostrar alerta toast
        const toastContainer = document.querySelector('.toast-container') || createToastContainer();
        
        const toastId = 'toast-' + Date.now();
        const iconClass = {
            'success': 'fa-check-circle text-success',
            'error': 'fa-exclamation-triangle text-danger',
            'warning': 'fa-exclamation-circle text-warning',
            'info': 'fa-info-circle text-info'
        }[tipo] || 'fa-info-circle text-info';

        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas ${iconClass} me-2"></i>
                        ${mensaje}
                    </div>
                    <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
        toast.show();

        // Eliminar después de que se oculte
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    function createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    function hapticFeedback() {
        if ('vibrate' in navigator) {
            navigator.vibrate(50);
        }
    }

    // === KEYBOARD SHORTCUTS ===
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + N = Nueva orden
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            document.querySelector('.btn-new-order').click();
        }
        
        // Ctrl/Cmd + S = Guardar orden
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            document.querySelector('.btn-save-order').click();
        }
        
        // Ctrl/Cmd + P = Procesar pago
        if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
            e.preventDefault();
            document.querySelector('button[data-bs-target="#pagoModal"]').click();
        }
    });

    // Inicialización completa
    console.log('🎯 Sistema POS Cajero inicializado correctamente');
    mostrarAlerta('Sistema POS listo para usar', 'success');
});
