// Función para cargar categorías y unidades en los selects
function cargarDatosFormulario() {
    console.log('📋 Cargando datos del formulario...');
    
    // Usar datos del servidor en lugar de AJAX
    if (window.categoriasData && window.unidadesData) {
        console.log('✅ Usando datos del servidor');
        
        // Cargar categorías
        const categoriaSelect = document.getElementById('categoria');
        if (categoriaSelect) {
            categoriaSelect.innerHTML = '<option value="">Seleccionar categoría</option>';
            window.categoriasData.forEach(categoria => {
                const option = document.createElement('option');
                option.value = categoria.id;
                option.textContent = categoria.nombre;
                categoriaSelect.appendChild(option);
            });
            console.log(`✅ Cargadas ${window.categoriasData.length} categorías`);
        }
        
        // Cargar unidades de medida
        const unidadSelect = document.getElementById('unidad_medida');
        if (unidadSelect) {
            unidadSelect.innerHTML = '<option value="">Seleccionar unidad</option>';
            window.unidadesData.forEach(unidad => {
                const option = document.createElement('option');
                option.value = unidad.id;
                option.textContent = `${unidad.nombre} (${unidad.abreviacion})`;
                unidadSelect.appendChild(option);
            });
            console.log(`✅ Cargadas ${window.unidadesData.length} unidades`);
        }
        
        return;
    }
    
    // Fallback: usar AJAX si los datos del servidor no están disponibles
    console.log('⚠️ Datos del servidor no disponibles, usando AJAX...');
    const url = document.querySelector('meta[name="form-data-url"]')?.getAttribute('content');
    
    if (!url) {
        console.error('❌ URL de form-data no encontrada');
        alert('Error: No se pudo obtener la URL para cargar datos.');
        return;
    }
    
    fetch(url, {
        method: 'GET',
        credentials: 'same-origin', // Incluir cookies de sesión
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Cargar categorías
            const categoriaSelect = document.getElementById('categoria');
            if (categoriaSelect) {
                categoriaSelect.innerHTML = '<option value="">Seleccionar categoría</option>';
                data.categorias.forEach(categoria => {
                    const option = document.createElement('option');
                    option.value = categoria.id;
                    option.textContent = categoria.nombre;
                    categoriaSelect.appendChild(option);
                });
            }
            
            // Cargar unidades de medida
            const unidadSelect = document.getElementById('unidad_medida');
            if (unidadSelect) {
                unidadSelect.innerHTML = '<option value="">Seleccionar unidad</option>';
                data.unidades.forEach(unidad => {
                    const option = document.createElement('option');
                    option.value = unidad.id;
                    option.textContent = `${unidad.nombre} (${unidad.abreviacion})`;
                    unidadSelect.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('Error cargando datos del formulario:', error);
            alert('Error al cargar categorías y unidades. Por favor, recarga la página.');
        });
}

// Función para abrir modal de nueva categoría
function abrirModalCategoria() {
    const modal = new bootstrap.Modal(document.getElementById('nuevaCategoriaModal'));
    modal.show();
}

// Función para abrir modal de nueva unidad
function abrirModalUnidad() {
    const modal = new bootstrap.Modal(document.getElementById('nuevaUnidadModal'));
    modal.show();
}

// Función para mostrar notificaciones elegantes
function mostrarNotificacionElegante(titulo, mensaje, tipo) {
    Swal.fire({
        title: titulo,
        text: mensaje,
        icon: tipo,
        confirmButtonText: 'Entendido',
        confirmButtonColor: '#10b981'
    });
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Cargar datos iniciales
    cargarDatosFormulario();
    
    // Configurar event listeners para botones
    const btnCategoria = document.querySelector('button[onclick="abrirModalCategoria()"]');
    const btnUnidad = document.querySelector('button[onclick="abrirModalUnidad()"]');
    
    if (btnCategoria) {
        btnCategoria.addEventListener('click', function(e) {
            e.preventDefault();
            abrirModalCategoria();
        });
    }
    
    if (btnUnidad) {
        btnUnidad.addEventListener('click', function(e) {
            e.preventDefault();
            abrirModalUnidad();
        });
    }
});
