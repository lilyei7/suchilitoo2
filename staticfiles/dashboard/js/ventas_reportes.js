/**
 * Funciones para la página de reportes de ventas
 */
document.addEventListener('DOMContentLoaded', function() {
    // Manejar cambios en los filtros para actualizaciones en tiempo real
    const filtroSucursal = document.getElementById('sucursal');
    const filtroTipoReporte = document.getElementById('tipo_reporte');
    const filtroFechaInicio = document.getElementById('fecha_inicio');
    const filtroFechaFin = document.getElementById('fecha_fin');
    
    // Función para formatear números como moneda
    function formatCurrency(number) {
        return new Intl.NumberFormat('es-MX', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(number);
    }
    
    // Manejar clics en filas de detalles para mostrar información adicional
    document.querySelectorAll('.detalle-row').forEach(function(row) {
        row.addEventListener('click', function() {
            const periodo = this.getAttribute('data-periodo');
            
            // Si hay un detalle expandido para este periodo, lo elimina
            const existingDetail = document.querySelector(`.detalle-expandido[data-periodo="${periodo}"]`);
            if (existingDetail) {
                existingDetail.remove();
                return;
            }
            
            // Cerrar cualquier otro detalle abierto
            document.querySelectorAll('.detalle-expandido').forEach(function(el) {
                el.remove();
            });
            
            // Mostrar indicador de carga
            const loadingRow = document.createElement('tr');
            loadingRow.className = 'detalle-expandido';
            loadingRow.setAttribute('data-periodo', periodo);
            loadingRow.innerHTML = `
                <td colspan="5" class="text-center py-3">
                    <div class="spinner-border spinner-border-sm text-primary" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    <span class="ms-2">Cargando detalles del periodo ${periodo}...</span>
                </td>
            `;
            
            // Insertar después de la fila actual
            this.parentNode.insertBefore(loadingRow, this.nextSibling);
            
            // TODO: En una implementación real, aquí se haría una petición AJAX
            // para obtener los detalles de ventas del periodo específico
            
            // Simulación de carga de datos
            setTimeout(function() {
                loadingRow.innerHTML = `
                    <td colspan="5" class="p-0">
                        <div class="p-3 bg-light">
                            <h6 class="mb-3">Detalles del periodo: ${periodo}</h6>
                            
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <div class="card border-left-info shadow h-100 py-2">
                                        <div class="card-body">
                                            <div class="row no-gutters align-items-center">
                                                <div class="col mr-2">
                                                    <div class="text-xs font-weight-bold text-info text-uppercase mb-1">
                                                        Ventas más populares
                                                    </div>
                                                    <div class="h5 mb-0 font-weight-bold text-gray-800">3 productos</div>
                                                </div>
                                                <div class="col-auto">
                                                    <i class="fas fa-utensils fa-2x text-gray-300"></i>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="col-md-6">
                                    <div class="card border-left-warning shadow h-100 py-2">
                                        <div class="card-body">
                                            <div class="row no-gutters align-items-center">
                                                <div class="col mr-2">
                                                    <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
                                                        Hora pico
                                                    </div>
                                                    <div class="h5 mb-0 font-weight-bold text-gray-800">18:00 - 19:00</div>
                                                </div>
                                                <div class="col-auto">
                                                    <i class="fas fa-clock fa-2x text-gray-300"></i>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <h6 class="mb-2">Ventas populares del periodo</h6>
                            <table class="table table-sm table-bordered mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th>Producto</th>
                                        <th class="text-center">Cantidad</th>
                                        <th class="text-end">Ingresos</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Sushi California</td>
                                        <td class="text-center">15</td>
                                        <td class="text-end">$2,250.00</td>
                                    </tr>
                                    <tr>
                                        <td>Ramen Tradicional</td>
                                        <td class="text-center">12</td>
                                        <td class="text-end">$1,800.00</td>
                                    </tr>
                                    <tr>
                                        <td>Tempura Mixta</td>
                                        <td class="text-center">8</td>
                                        <td class="text-end">$960.00</td>
                                    </tr>
                                </tbody>
                            </table>
                            
                            <div class="text-center mt-3">
                                <button class="btn btn-sm btn-outline-primary ver-detalle-completo" data-periodo="${periodo}">
                                    <i class="fas fa-search-plus me-1"></i> Ver Reporte Completo
                                </button>
                                <button class="btn btn-sm btn-outline-secondary cerrar-detalle" data-periodo="${periodo}">
                                    <i class="fas fa-times me-1"></i> Cerrar
                                </button>
                            </div>
                        </div>
                    </td>
                `;
                
                // Añadir evento al botón de cerrar
                loadingRow.querySelector('.cerrar-detalle').addEventListener('click', function(e) {
                    e.stopPropagation();
                    loadingRow.remove();
                });
                
                // Añadir evento al botón de ver detalle completo
                loadingRow.querySelector('.ver-detalle-completo').addEventListener('click', function(e) {
                    e.stopPropagation();
                    alert('Esta funcionalidad estará disponible próximamente.\n\nSe mostrará un informe detallado de las ventas del periodo ' + periodo);
                });
            }, 1000);
        });
    });
    
    // Inicializar tooltips de Bootstrap si están disponibles
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
});
