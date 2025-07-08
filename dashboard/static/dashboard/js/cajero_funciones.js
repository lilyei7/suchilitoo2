/**
 * Funciones del Punto de Venta (POS)
 * Sistema de Restaurant Sushi
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

    // Event Listeners
    // Eliminar el listener de click en toda la tarjeta
    // document.querySelectorAll('.product-item').forEach(product => {
    //     product.addEventListener('click', () => agregarProducto(product));
    // });

    // Nuevo: Listener solo en el botón "Agregar"
    document.querySelectorAll('.btn-agregar-producto').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const productoId = this.getAttribute('data-producto-id');
            const card = this.closest('.modern-product-card');
            const checkbox = card.querySelector('.modern-product-checkbox');
            if (!checkbox.checked) return; // Solo si está activo
            const nombre = card.querySelector('.modern-product-name').textContent;
            const precio = parseFloat(card.querySelector('.modern-product-price').textContent.replace(/[^\d.]/g, ''));
            const qtyInput = card.querySelector('.modern-qty-input');
            let cantidad = parseInt(qtyInput.value) || 1;
            // Ingredientes seleccionados (por defecto todos)
            let ingredientes = (window.ingredientesSeleccionados && window.ingredientesSeleccionados[productoId])
                ? window.ingredientesSeleccionados[productoId].slice()
                : (ingredientesPorProducto[productoId] || []).slice();
            // Buscar si ya existe el mismo producto con los mismos ingredientes
            let itemExistente = ordenActual.items.find(item => item.productoId === productoId && JSON.stringify(item.ingredientes) === JSON.stringify(ingredientes));
            if (itemExistente) {
                itemExistente.cantidad += cantidad;
                itemExistente.total = itemExistente.cantidad * itemExistente.precio;
            } else {
                ordenActual.items.push({
                    productoId,
                    nombre,
                    precio,
                    cantidad,
                    total: precio * cantidad,
                    ingredientes
                });
            }
            actualizarOrden();
        });
    });

    const btnSaveOrder = document.querySelector('.btn-save-order');
    if (btnSaveOrder) btnSaveOrder.addEventListener('click', guardarOrden);
    const btnProcessPayment = document.querySelector('.btn-process-payment');
    if (btnProcessPayment) btnProcessPayment.addEventListener('click', procesarPago);
    const btnNewOrder = document.querySelector('.btn-new-order');
    if (btnNewOrder) btnNewOrder.addEventListener('click', () => {
        if (confirm('¿Está seguro que desea crear una nueva orden? La orden actual se perderá.')) {
            limpiarOrden();
        }
    });

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

    // Iconos para algunos ingredientes (puedes expandir este objeto)
    const iconosIngredientes = {
        Agua: '💧', Hielo: '🧊', Azúcar: '🍬', Limón: '🍋', Miel: '🍯',
        Café: '☕', Leche: '🥛', Salmón: '🐟', Atún: '🐟', Alga: '🌿',
        Arroz: '🍚', Aguacate: '🥑', Queso: '🧀', QuesoCrema: '🧀',
        Pepino: '🥒', Ajonjolí: '🌰', Camarón: '🦐', Jitomate: '🍅',
        Cilantro: '🌱', Cebolla: '🧅', Pescado: '🐟', Tostada: '🥙',
        Mayonesa: '🥄', Limón: '🍋'
    };

    document.querySelectorAll('.btn-ingredientes').forEach(btn => {
        btn.addEventListener('click', function() {
            const productoId = this.getAttribute('data-producto-id');
            // Limpiar el formulario de ingredientes
            const form = document.getElementById('form-ingredientes');
            form.innerHTML = '';
            // Agregar ingredientes correspondientes como switches con iconos
            (ingredientesPorProducto[productoId] || []).forEach((ing, idx) => {
                const ingId = `ing-${productoId}-${idx}`;
                const icon = iconosIngredientes[ing.replace(/\s/g, '')] || '';
                form.innerHTML += `
                  <div class='form-check form-switch mb-2'>
                    <input class='form-check-input' type='checkbox' value='${ing}' id='${ingId}' checked>
                    <label class='form-check-label' for='${ingId}'>${icon} ${ing}</label>
                  </div>
                `;
            });
            // Marcar el checkbox relacionado (opcional, para referencia)
            document.querySelectorAll('.modern-product-checkbox').forEach(cb => cb.classList.remove('ingrediente-pendiente'));
            const checkbox = document.getElementById(productoId);
            if (checkbox) checkbox.classList.add('ingrediente-pendiente');
            const modal = new bootstrap.Modal(document.getElementById('ingredientesModal'));
            modal.show();
        });
    });

    // Guardar ingredientes personalizados temporalmente por producto
    window.ingredientesSeleccionados = {};
    document.getElementById('guardarIngredientes').addEventListener('click', function() {
        const checkbox = document.querySelector('.modern-product-checkbox.ingrediente-pendiente');
        if (!checkbox) return;
        const productoId = checkbox.id;
        const ingredientes = Array.from(document.querySelectorAll('#form-ingredientes .form-check-input:checked')).map(e => e.value);
        window.ingredientesSeleccionados[productoId] = ingredientes;
        // Asociar los ingredientes seleccionados al producto en la orden si ya existe
        const item = ordenActual.items.find(item => item.productoId === productoId);
        if (item) {
            item.ingredientes = ingredientes;
        }
        actualizarOrden();
        checkbox.classList.remove('ingrediente-pendiente');
        bootstrap.Modal.getInstance(document.getElementById('ingredientesModal')).hide();
    });

    /**
     * Agrega un producto a la orden actual
     */
    function agregarProducto(productElement) {
        const productoId = productElement.dataset.productoId;
        const nombre = productElement.querySelector('.product-name').textContent;
        const precio = parseFloat(productElement.querySelector('.product-price').textContent.replace('Q', ''));

        // Buscar si el producto ya existe en la orden
        const itemExistente = ordenActual.items.find(item => item.productoId === productoId);

        if (itemExistente) {
            itemExistente.cantidad++;
            itemExistente.total = itemExistente.cantidad * itemExistente.precio;
        } else {
            // Por defecto, todos los ingredientes seleccionados
            const ingredientes = (ingredientesPorProducto[productoId] || []).slice();
            ordenActual.items.push({
                productoId,
                nombre,
                precio,
                cantidad: 1,
                total: precio,
                ingredientes
            });
        }

        actualizarOrden();
    }

    /**
     * Actualiza la cantidad de un item en la orden
     */
    function actualizarCantidad(productoId, nuevaCantidad) {
        const item = ordenActual.items.find(item => item.productoId === productoId);
        if (item) {
            if (nuevaCantidad <= 0) {
                ordenActual.items = ordenActual.items.filter(i => i.productoId !== productoId);
            } else {
                item.cantidad = nuevaCantidad;
                item.total = item.cantidad * item.precio;
            }
            actualizarOrden();
        }
    }

    /**
     * Actualiza la visualización de la orden
     */
    function actualizarOrden() {
        // Limpiar lista de items
        orderItems.innerHTML = '';
        // Agregar cada item
        ordenActual.items.forEach(item => {
            const ingredientesFaltantes = (ingredientesPorProducto[item.productoId] || []).filter(ing => !(item.ingredientes || []).includes(ing));
            const ingredientesHtml = ingredientesFaltantes.length
                ? `<div class='ingredientes-list text-danger small'>Sin: ${ingredientesFaltantes.map(ing => `<span class='badge bg-light text-danger border me-1'>${ing}</span>`).join('')}</div>`
                : `<div class='ingredientes-list text-secondary small'>Sin: ninguno</div>`;
            const itemElement = document.createElement('div');
            itemElement.className = 'order-item d-flex align-items-center py-2 border-bottom';
            itemElement.innerHTML = `
                <div class="flex-grow-1">
                    <div class="fw-bold">${item.nombre}</div>
                    <div class="text-muted">$${item.precio.toFixed(2)}</div>
                    ${ingredientesHtml}
                </div>
                <div class="item-quantity ms-2">
                    <button class="quantity-btn btn btn-outline-secondary btn-sm" onclick="actualizarCantidad('${item.productoId}', ${item.cantidad - 1})">-</button>
                    <input type="text" class="quantity-input form-control d-inline-block text-center mx-1" style="width:40px;" value="${item.cantidad}" onchange="actualizarCantidad('${item.productoId}', this.value)">
                    <button class="quantity-btn btn btn-outline-secondary btn-sm" onclick="actualizarCantidad('${item.productoId}', ${item.cantidad + 1})">+</button>
                </div>
                <div class="ms-3 fw-bold">$${item.total.toFixed(2)}</div>
            `;
            orderItems.appendChild(itemElement);
        });
        // Calcular totales
        calcularTotales();
    }

    /**
     * Calcula los totales de la orden
     */
    function calcularTotales() {
        ordenActual.subtotal = ordenActual.items.reduce((sum, item) => sum + item.total, 0);
        ordenActual.iva = ordenActual.subtotal * 0.12;
        ordenActual.total = ordenActual.subtotal + ordenActual.iva - ordenActual.descuento;

        // Actualizar elementos en el DOM
        subtotalEl.textContent = `$${ordenActual.subtotal.toFixed(2)}`;
        descuentoEl.textContent = `$${ordenActual.descuento.toFixed(2)}`;
        ivaEl.textContent = `$${ordenActual.iva.toFixed(2)}`;
        totalEl.textContent = `$${ordenActual.total.toFixed(2)}`;
    }

    /**
     * Guarda la orden actual
     */
    async function guardarOrden() {
        if (ordenActual.items.length === 0) {
            alert('No hay items en la orden');
            return;
        }

        try {
            const response = await fetch('/api/cajero/guardar-orden', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    items: ordenActual.items.map(item => ({
                        ...item,
                        ingredientes: item.ingredientes || []
                    })),
                    tipo: 'mesa',
                    mesa_id: getMesaActual(),
                    notas: ''
                })
            });

            const data = await response.json();
            if (data.success) {
                alert('Orden guardada exitosamente');
                limpiarOrden();
            } else {
                alert(data.message || 'Error al guardar la orden');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al guardar la orden');
        }
    }

    /**
     * Procesa el pago de la orden actual
     */
    function procesarPago() {
        if (ordenActual.items.length === 0) {
            alert('No hay items en la orden');
            return;
        }

        // Abrir modal de pago
        const modal = new bootstrap.Modal(document.getElementById('pagoModal'));
        modal.show();
    }

    // --- FINALIZAR PAGO ---
    window.finalizarPago = function() {
        // Aquí puedes poner la lógica real de pago
        alert('Pago procesado (demo).');
        // Cierra el modal si quieres
        const modal = bootstrap.Modal.getInstance(document.getElementById('pagoModal'));
        if (modal) modal.hide();
    }

    // Mostrar campos según método de pago y monto grande
    document.getElementById('metodoPago').addEventListener('change', function() {
        const metodo = this.value;
        document.getElementById('efectivoFields').style.display = metodo === 'efectivo' ? '' : 'none';
        document.getElementById('tarjetaFields').style.display = metodo === 'tarjeta' ? '' : 'none';
        document.getElementById('montoCobrarBox').style.display = metodo === 'tarjeta' ? '' : 'none';
        var montoCobrarEl = document.getElementById('montoCobrar');
        if (metodo === 'tarjeta' && montoCobrarEl) {
            montoCobrarEl.textContent = subtotalEl.textContent;
        }
    });
    // Inicializar al cargar
    document.getElementById('metodoPago').dispatchEvent(new Event('change'));

    // --- CÁLCULO AUTOMÁTICO DE CAMBIO (EFECTIVO) ---
    const montoRecibidoInput = document.getElementById('montoRecibido');
    const cambioInput = document.getElementById('cambio');
    if (montoRecibidoInput && cambioInput) {
        montoRecibidoInput.addEventListener('input', function() {
            let recibido = parseFloat(this.value);
            let total = parseFloat(totalEl.textContent.replace(/[^\d.]/g, ''));
            let cambio = 0;
            if (!isNaN(recibido) && !isNaN(total)) {
                cambio = recibido - total;
            }
            cambioInput.value = cambio > 0 ? cambio.toFixed(2) : '0.00';
        });
    }

    // --- IMPRESIÓN DE TICKET ---
    window.imprimirTicket = function() {
        // Puedes personalizar el contenido del ticket aquí
        let ticket = '--- Sushi POS ---\n';
        ticket += 'Fecha: ' + new Date().toLocaleString() + '\n';
        ticket += '-------------------\n';
        ordenActual.items.forEach(item => {
            ticket += `${item.cantidad} x ${item.nombre}\n`;
            if (item.ingredientes && item.ingredientes.length < (ingredientesPorProducto[item.productoId]||[]).length) {
                ticket += '  Sin: ' + (ingredientesPorProducto[item.productoId]||[]).filter(ing => !item.ingredientes.includes(ing)).join(', ') + '\n';
            }
            ticket += `  $${item.total.toFixed(2)}\n`;
        });
        ticket += '-------------------\n';
        ticket += 'Subtotal: ' + subtotalEl.textContent + '\n';
        ticket += 'IVA: ' + ivaEl.textContent + '\n';
        ticket += 'Total: ' + totalEl.textContent + '\n';
        ticket += 'Pago: ' + document.getElementById('metodoPago').value + '\n';
        if(document.getElementById('ultimos4') && document.getElementById('ultimos4').value) {
            ticket += 'Tarjeta: **** ' + document.getElementById('ultimos4').value + '\n';
        }
        ticket += '\n¡Gracias por su compra!\n';
        // Imprime usando print (básico)
        const win = window.open('', '', 'width=350,height=600');
        win.document.write('<pre style="font-size:16px">'+ticket+'</pre>');
        win.print();
        win.close();
        // Para integración avanzada con impresora térmica, usar QZ Tray o similar
    }

    /**
     * Limpia la orden actual
     */
    function limpiarOrden() {
        ordenActual = {
            items: [],
            subtotal: 0,
            descuento: 0,
            iva: 0,
            total: 0
        };
        actualizarOrden();
    }

    /**
     * Obtiene el token CSRF
     */
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    /**
     * Obtiene el ID de la mesa actual
     */
    function getMesaActual() {
        // Implementar lógica para obtener la mesa seleccionada
        return null;
    }
});
