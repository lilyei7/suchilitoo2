import os
import re

def clean_inventario_html():
    """
    Clean the inventario.html file by:
    1. Removing duplicate JavaScript function definitions
    2. Ensuring proper script structure
    3. Adding external JS file reference
    """
    # Define file paths
    inventario_path = os.path.join('dashboard', 'templates', 'dashboard', 'inventario.html')
    backup_path = inventario_path + '.full_backup'

    # Make a backup of the original file
    if os.path.exists(inventario_path):
        with open(inventario_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"✅ Backup created at {backup_path}")
      # HTML template to use (keeps the existing structure but fixes the scripts)
    clean_html_template = r"""{% extends 'dashboard/base.html' %}
{% load static %}
{% block title %}Inventario - Sushi Restaurant{% endblock %}
{% block content %}
<!-- Original content here -->
{}
{% endblock %}

{% block styles %}
<!-- Original styles here -->
{}
{% endblock %}

{% block extra_js %}
<!-- External script for critical functions -->
<script src="{% static 'dashboard/js/funciones_inventario.js' %}"></script>

<!-- Main script -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    console.log("Inventario: DOM cargado");
    
    // Verificar elementos críticos
    const elementos = {
        'nuevoInsumoModal': document.getElementById('nuevoInsumoModal'),
        'nuevoInsumoForm': document.getElementById('nuevoInsumoForm'),
        'nombre': document.getElementById('nombre'),
        'codigo': document.getElementById('codigo'),
        'categoria': document.getElementById('categoria'),
        'unidad_medida': document.getElementById('unidad_medida'),
        'tipo': document.getElementById('tipo'),
        'precio': document.getElementById('precio'),
        'stock_minimo': document.getElementById('stock_minimo')
    };
    
    // Verificar que todos los elementos existen
    let elementosFaltantes = [];
    for (let [clave, elemento] of Object.entries(elementos)) {
        if (!elemento) {
            elementosFaltantes.push(clave);
        }
    }
    
    if (elementosFaltantes.length > 0) {
        console.warn("Advertencia: No se encontraron todos los elementos necesarios:", elementosFaltantes);
    } else {
        console.log("✅ Todos los elementos críticos encontrados");
    }
    
    // Configurar event listeners para el botón de nuevo insumo
    const btnNuevoInsumo = document.getElementById('btnNuevoInsumo');
    if (btnNuevoInsumo) {
        btnNuevoInsumo.addEventListener('click', function() {
            console.log("Botón Nuevo Insumo clickeado");
            // Cargar datos del formulario cuando se abre el modal
            cargarDatosFormulario();
        });
    }
    
    // Event listener para el formulario de insumo
    const nuevoInsumoForm = document.getElementById('nuevoInsumoForm');
    if (nuevoInsumoForm) {
        nuevoInsumoForm.addEventListener('submit', function(e) {
            e.preventDefault();
            crearInsumo();
        });
    }
});

// Variable global para prevenir envíos duplicados
let creandoInsumo = false;

function crearInsumo() {
    // Verificar si ya se está procesando una petición
    if (creandoInsumo) {
        console.log("Ya se está procesando una petición. Ignorando click...");
        return;
    }
    
    // Marcar como procesando
    creandoInsumo = true;
    
    const form = document.getElementById('nuevoInsumoForm');
    if (!form) {
        console.error("Error: No se encontró el formulario");
        creandoInsumo = false; // Liberar variable de control
        return;
    }
    
    const formData = new FormData(form);
    
    // Validar campos obligatorios
    const nombre = formData.get('nombre');
    const categoria = formData.get('categoria');
    const unidad_medida = formData.get('unidad_medida');
    
    if (!nombre || !categoria || !unidad_medida) {
        mostrarNotificacionElegante(
            'Formulario Incompleto',
            'Por favor completa todos los campos obligatorios.',
            'warning'
        );
        creandoInsumo = false; // Liberar variable de control
        return;
    }
    
    // Forzar tipo a "basico" ya que este formulario es solo para insumos básicos
    formData.set('tipo', 'basico');
    
    // Generar código si no existe
    if (!formData.get('codigo')) {
        const timestamp = Date.now().toString().slice(-3);
        const codigo = nombre.toUpperCase().replace(/\\s+/g, '').substring(0, 6) + timestamp;
        formData.set('codigo', codigo);
    }
    
    // Verificar CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    
    if (!csrfToken) {
        mostrarNotificacionElegante(
            'Error',
            'Token de seguridad no encontrado. Por favor, recarga la página.',
            'error'
        );
        
        creandoInsumo = false; // Liberar variable de control
        return;
    }
    
    // Mostrar qué datos se van a enviar
    console.log("Enviando datos del formulario:");
    for (let [key, value] of formData.entries()) {
        console.log(`${key}: ${value}`);
    }
    
    const url = '{% url "dashboard:crear_insumo" %}';
    
    // Deshabilitar botón durante el proceso
    const btnGuardar = document.getElementById('btnGuardarInsumo');
    if (btnGuardar) {
        btnGuardar.disabled = true;
        btnGuardar.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Guardando...';
    }
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken.value
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Respuesta del servidor:", data);
        
        if (data.success) {
            // Mostrar notificación de éxito
            mostrarNotificacionElegante(
                '¡Insumo Creado!', 
                `El insumo "${formData.get('nombre')}" se ha guardado exitosamente en el sistema.`,
                'success'
            );
            
            // Limpiar formulario
            form.reset();
            
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('nuevoInsumoModal'));
            if (modal) {
                modal.hide();
            }
            
            // Liberar variable de control
            creandoInsumo = false;
            
            // Recargar página inmediatamente para mostrar el nuevo insumo
            window.location.reload();
        } else {
            // Mostrar errores
            let mensajeError = 'No se pudo guardar el insumo. ';
            if (data.errors) {
                mensajeError += Object.values(data.errors).join(' ');
            }
            
            mostrarNotificacionElegante(
                'Error al Guardar',
                mensajeError,
                'error'
            );
            
            // Rehabilitar botón
            const btnGuardar = document.getElementById('btnGuardarInsumo');
            if (btnGuardar) {
                btnGuardar.disabled = false;
                btnGuardar.innerHTML = '<i class="fas fa-save me-1"></i>Guardar Insumo';
            }
            
            // Liberar variable de control
            creandoInsumo = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        
        // Rehabilitar botón
        const btnGuardar = document.getElementById('btnGuardarInsumo');
        if (btnGuardar) {
            btnGuardar.disabled = false;
            btnGuardar.innerHTML = '<i class="fas fa-save me-1"></i>Guardar Insumo';
        }
        
        // Liberar variable de control
        creandoInsumo = false;
        
        mostrarNotificacionElegante(
            'Error de Conexión',
            'No se pudo conectar con el servidor. Verifica tu conexión e intenta nuevamente.',
            'error'
        );
    });
}

// Función para eliminar insumo
function eliminarInsumo(insumoId, nombre) {
    if (confirm(`¿Estás seguro de que quieres eliminar el insumo "${nombre}"?`)) {
        fetch(`{% url 'dashboard:eliminar_insumo' 0 %}`.replace('0', insumoId), {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remover fila o tarjeta
                const elemento = document.getElementById(`insumo-${insumoId}`);
                if (elemento) {
                    elemento.remove();
                }
                
                mostrarNotificacionElegante(
                    'Insumo Eliminado', 
                    `El insumo "${nombre}" ha sido eliminado correctamente.`,
                    'success'
                );
                
                // Recargar para actualizar datos
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                mostrarNotificacionElegante(
                    'Error', 
                    data.message || 'No se pudo eliminar el insumo.',
                    'error'
                );
            }
        })
        .catch(error => {
            mostrarAlerta('Error al eliminar el insumo', 'danger');
        });
    }
}

// Función para mostrar notificaciones elegantes
function mostrarNotificacionElegante(titulo, mensaje, tipo = 'success') {
    const container = document.getElementById('notification-container');
    if (!container) {
        console.warn("Contenedor de notificaciones no encontrado. Usando alert convencional.");
        alert(`${titulo}: ${mensaje}`);
        return;
    }
    
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification ${tipo}`;
    
    // Iconos por tipo
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    // HTML de la notificación
    notification.innerHTML = `
        <div class="notification-content">
            <div class="notification-icon">
                <i class="${icons[tipo] || icons.info}"></i>
            </div>
            <div class="notification-text">
                <div class="notification-title">${titulo}</div>
                <div class="notification-message">${mensaje}</div>
            </div>
        </div>
        <button class="notification-close" onclick="cerrarNotificacion(this.parentElement)">
            <i class="fas fa-times"></i>
        </button>
        <div class="notification-progress"></div>
    `;
    
    // Agregar al contenedor
    container.appendChild(notification);
    
    // Mostrar con animación
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Auto-cerrar después de 5 segundos
    setTimeout(() => {
        cerrarNotificacion(notification);
    }, 5000);
    
    return notification;
}

function cerrarNotificacion(notification) {
    if (notification && notification.parentNode) {
        notification.classList.remove('show');
        notification.classList.add('hide');
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }
}

function mostrarAlerta(mensaje, tipo) {
    let titulo = 'Notificación';
    switch(tipo) {
        case 'success':
            titulo = 'Éxito';
            break;
        case 'danger':
        case 'error':
            titulo = 'Error';
            tipo = 'error';
            break;
        case 'warning':
            titulo = 'Advertencia';
            break;
        case 'info':
            titulo = 'Información';
            break;
    }
    
    mostrarNotificacionElegante(titulo, mensaje, tipo);
}

// Funciones para acciones de la lista
function verDetalles(insumoId) {
    mostrarNotificacionElegante(
        'Ver Detalles',
        'Función de detalles en desarrollo. Se mostrará información completa del insumo.',
        'info'
    );
}

function agregarStock(insumoId) {
    const cantidad = prompt('¿Cuántas unidades deseas agregar al stock?');
    if (cantidad && !isNaN(cantidad) && parseFloat(cantidad) > 0) {
        mostrarNotificacionElegante(
            'Stock Agregado',
            `Se agregaron ${cantidad} unidades al inventario. Función en desarrollo.`,
            'success'
        );
    } else if (cantidad !== null) {
        mostrarNotificacionElegante(
            'Error',
            'La cantidad debe ser un número positivo.',
            'error'
        );
    }
}

function reducirStock(insumoId) {
    const cantidad = prompt('¿Cuántas unidades deseas reducir del stock?');
    if (cantidad && !isNaN(cantidad) && parseFloat(cantidad) > 0) {
        mostrarNotificacionElegante(
            'Stock Reducido',
            `Se redujeron ${cantidad} unidades del inventario. Función en desarrollo.`,
            'success'
        );
    } else if (cantidad !== null) {
        mostrarNotificacionElegante(
            'Error',
            'La cantidad debe ser un número positivo.',
            'error'
        );
    }
}

function verHistorial(insumoId) {
    mostrarNotificacionElegante(
        'Historial de Movimientos',
        'Se mostrará el historial completo de movimientos del insumo. Función en desarrollo.',
        'info'
    );
}
</script>
{% endblock %}"""

    # Extract the content and styles from the original file
    try:
        with open(inventario_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract main content (between block content and endblock)
        content_match = re.search(r'{%\s*block\s+content\s*%}(.*?){%\s*endblock\s*%}', content, re.DOTALL)
        main_content = content_match.group(1) if content_match else ""
        
        # Extract styles (between block styles and endblock)
        styles_match = re.search(r'{%\s*block\s+styles\s*%}(.*?){%\s*endblock\s*%}', content, re.DOTALL)
        styles_content = styles_match.group(1) if styles_match else ""
        
        # Create new file content
        new_content = clean_html_template.format(main_content, styles_content)
        
        # Write the clean content back to the file
        with open(inventario_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print(f"✅ {inventario_path} ha sido limpiado y corregido")
        return True
        
    except Exception as e:
        print(f"❌ Error al procesar el archivo: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 LIMPIEZA Y CORRECCIÓN DE INVENTARIO.HTML")
    print("===========================================")
    clean_inventario_html()
