/**
 * Critical Functions for Inventory Management
 * This file contains essential JavaScript functions for the inventory management system.
 */

// Asegurarse de que estas funciones están globalmente disponibles
window.abrirModalCategoria = function() {
    console.log("Abriendo modal de categoría");
    const modal = new bootstrap.Modal(document.getElementById('nuevaCategoriaModal'));
    modal.show();
};

window.abrirModalUnidad = function() {
    console.log("Abriendo modal de unidad");
    const modal = new bootstrap.Modal(document.getElementById('nuevaUnidadModal'));
    modal.show();
};

window.cargarDatosFormulario = function() {
    console.log("%c[DEBUG] Cargando datos del formulario...", "background: #4CAF50; color: white; padding: 2px 5px; border-radius: 3px;");
    const url = '/dashboard/insumos/form-data/';
    console.log("[DEBUG] URL a consultar:", url);
    
    // Verificar si los elementos select existen antes de hacer la petición
    const categoriaSelect = document.getElementById('categoria');
    const unidadSelect = document.getElementById('unidad_medida');
    
    console.log("[DEBUG] Elemento select categoría existe:", categoriaSelect ? "SÍ" : "NO");
    console.log("[DEBUG] Elemento select unidad existe:", unidadSelect ? "SÍ" : "NO");
    
    if (!categoriaSelect && !unidadSelect) {
        console.error("[ERROR] No se encontraron los elementos select. Abortando carga.");
        return;
    }
    
    fetch(url)
        .then(response => {
            console.log("[DEBUG] Respuesta recibida. Status:", response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("%c[DEBUG] Datos recibidos:", "background: #2196F3; color: white; padding: 2px 5px; border-radius: 3px;", data);
            console.log("[DEBUG] Categorías recibidas:", data.categorias ? data.categorias.length : 0);
            console.log("[DEBUG] Unidades recibidas:", data.unidades ? data.unidades.length : 0);
            
            // Cargar categorías
            const categoriaSelect = document.getElementById('categoria');
            if (categoriaSelect) {
                categoriaSelect.innerHTML = '<option value="">Seleccionar categoría</option>';
                if (data.categorias && data.categorias.length > 0) {
                    data.categorias.forEach((categoria, index) => {
                        console.log(`[DEBUG] Procesando categoría ${index}: ID=${categoria.id}, Nombre=${categoria.nombre}`);
                        const option = document.createElement('option');
                        option.value = categoria.id;
                        option.textContent = categoria.nombre;
                        categoriaSelect.appendChild(option);
                    });
                    console.log("%c[DEBUG] Categorías cargadas exitosamente:", "background: #4CAF50; color: white;", data.categorias.length);
                } else {
                    console.warn("[WARN] No hay categorías para cargar");
                }
            } else {
                console.error("[ERROR] No se encontró el select de categoría");
            }
              // Cargar unidades de medida
            const unidadSelect = document.getElementById('unidad_medida');
            if (unidadSelect) {
                unidadSelect.innerHTML = '<option value="">Seleccionar unidad</option>';
                if (data.unidades && data.unidades.length > 0) {
                    data.unidades.forEach((unidad, index) => {
                        console.log(`[DEBUG] Procesando unidad ${index}: ID=${unidad.id}, Nombre=${unidad.nombre}, Abrev=${unidad.abreviacion}`);
                        const option = document.createElement('option');
                        option.value = unidad.id;
                        option.textContent = `${unidad.nombre} (${unidad.abreviacion})`;
                        unidadSelect.appendChild(option);
                    });
                    console.log("%c[DEBUG] Unidades cargadas exitosamente:", "background: #4CAF50; color: white;", data.unidades.length);
                } else {
                    console.warn("[WARN] No hay unidades para cargar");
                }
            } else {
                console.error("[ERROR] No se encontró el select de unidad");
            }
            
            // Verificar el contenido de los selects después de cargar
            setTimeout(() => {
                console.log("[DEBUG] Verificación final:");
                const catSelect = document.getElementById('categoria');
                const unitSelect = document.getElementById('unidad_medida');
                console.log("- Select categoría tiene opciones:", catSelect ? catSelect.options.length : 0);
                console.log("- Select unidad tiene opciones:", unitSelect ? unitSelect.options.length : 0);
            }, 200);
        })
        .catch(error => {
            console.error('[ERROR] Error cargando datos del formulario:', error);
            console.trace("Stack trace del error:");
            alert('Error al cargar categorías y unidades. Por favor, revisa la consola para más detalles.');
        });
};

// Script para ejecución automática
document.addEventListener('DOMContentLoaded', function() {
    console.log("%c[INICIO] Inicialización del sistema de inventario", "background: #FF9800; color: white; padding: 5px; font-size: 14px;");
    
    // Verificar que las funciones existan en el ámbito global
    console.log("[DEBUG] Verificando funciones críticas:");
    console.log("- función abrirModalCategoria:", typeof window.abrirModalCategoria === 'function' ? "✅ DISPONIBLE" : "❌ NO DISPONIBLE");
    console.log("- función abrirModalUnidad:", typeof window.abrirModalUnidad === 'function' ? "✅ DISPONIBLE" : "❌ NO DISPONIBLE");
    console.log("- función cargarDatosFormulario:", typeof window.cargarDatosFormulario === 'function' ? "✅ DISPONIBLE" : "❌ NO DISPONIBLE");
    
    // Registrar los modales disponibles
    const modalCategoria = document.getElementById('nuevaCategoriaModal');
    const modalUnidad = document.getElementById('nuevaUnidadModal');
    const modalInsumo = document.getElementById('nuevoInsumoModal');
    
    console.log("[DEBUG] Verificando modales:");
    console.log("- Modal categoría:", modalCategoria ? "✅ ENCONTRADO" : "❌ NO ENCONTRADO");
    console.log("- Modal unidad:", modalUnidad ? "✅ ENCONTRADO" : "❌ NO ENCONTRADO");
    console.log("- Modal insumo:", modalInsumo ? "✅ ENCONTRADO" : "❌ NO ENCONTRADO");
      // Verificar si el botón de nuevo insumo existe y configurar su evento
    const btnNuevoInsumo = document.querySelector('button[data-bs-target="#nuevoInsumoModal"]');
    if (btnNuevoInsumo) {
        console.log("[DEBUG] Configurando evento para btnNuevoInsumo");
        btnNuevoInsumo.addEventListener('click', function() {
            console.log("%c[EVENTO] Botón Nuevo Insumo clickeado - Cargando datos del formulario", "background: #9C27B0; color: white;");
            setTimeout(function() {
                window.cargarDatosFormulario();
            }, 300);
        });
    } else {
        console.warn("[WARN] No se encontró el botón de nuevo insumo");
    }
    
    // También asociar la función a los botones que abren los modales
    const btnCategoria = document.querySelector('button[onclick="abrirModalCategoria()"]');
    const btnUnidad = document.querySelector('button[onclick="abrirModalUnidad()"]');
    
    console.log("[DEBUG] Botones de modales:");
    console.log("- Botón categoría:", btnCategoria ? "✅ ENCONTRADO" : "❌ NO ENCONTRADO");
    console.log("- Botón unidad:", btnUnidad ? "✅ ENCONTRADO" : "❌ NO ENCONTRADO");
    
    if (btnCategoria) {
        console.log("[DEBUG] Configurando eventos adicionales para botón de categoría");
        btnCategoria.addEventListener('click', function() {
            console.log("[EVENTO] Botón categoría clickeado - Ejecutando abrirModalCategoria");
            // Primero verificar si la función existe para evitar errores
            if (typeof window.abrirModalCategoria === 'function') {
                try {
                    window.abrirModalCategoria();
                    console.log("[DEBUG] Función abrirModalCategoria ejecutada con éxito");
                } catch (error) {
                    console.error("[ERROR] Error al ejecutar abrirModalCategoria:", error);
                }
            }
        });
    }
    
    // Ejecutar cargarDatosFormulario cuando el DOM esté listo
    console.log("[DEBUG] Programando carga automática de datos en 500ms");
    setTimeout(function() {
        console.log("%c[EVENTO] Ejecutando cargarDatosFormulario automáticamente", "background: #FF5722; color: white;");
        
        // Verificar que la función existe antes de llamarla
        if (typeof window.cargarDatosFormulario === 'function') {
            try {
                window.cargarDatosFormulario();
            } catch (error) {
                console.error("[ERROR] Error al ejecutar cargarDatosFormulario:", error);
            }
        } else {
            console.error("[ERROR] La función cargarDatosFormulario no está definida");
        }
    }, 500);
    
    // Verificación adicional después de un tiempo
    setTimeout(function() {
        console.log("%c[VERIFICACIÓN FINAL]", "background: #607D8B; color: white; padding: 5px;");
        
        // Verificar nuevamente el estado de los elementos críticos
        const catSelect = document.getElementById('categoria');
        const unitSelect = document.getElementById('unidad_medida');
        
        if (catSelect) {
            console.log("- Select categoría encontrado con", catSelect.options.length, "opciones");
        } else {
            console.error("- ❌ Select categoría NO ENCONTRADO");
        }
        
        if (unitSelect) {
            console.log("- Select unidad encontrado con", unitSelect.options.length, "opciones");
        } else {
            console.error("- ❌ Select unidad NO ENCONTRADO");
        }
    }, 2000);
});
