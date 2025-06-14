#!/usr/bin/env python3
"""
Script para regenerar el JavaScript de proveedores sin errores
"""

def create_clean_js():
    js_content = """
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando sistema de proveedores...');
    
    // Referencias del DOM
    const modalNuevoProveedor = document.getElementById('nuevoProveedorModal');
    const formNuevoProveedor = document.getElementById('formNuevoProveedor');
    const submitBtnNuevo = formNuevoProveedor.querySelector('button[type="submit"]');
    const originalBtnText = submitBtnNuevo.innerHTML;

    // Función para mostrar notificaciones toast
    function showToast(message, type = 'success') {
        const toastContainer = document.querySelector('.toast-container') || createToastContainer();
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        const toastBootstrap = new bootstrap.Toast(toast);
        toastBootstrap.show();
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }

    function createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    // Variable global para el proveedor actual
    let proveedorActual = null;

    // Ver detalles del proveedor
    window.verDetalleProveedor = function(proveedorId) {
        const modal = new bootstrap.Modal(document.getElementById('detalleProveedorModal'));
        const content = document.getElementById('detalleProveedorContent');
        
        // Mostrar loading
        content.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-2 text-muted">Cargando información del proveedor...</p>
            </div>
        `;
        
        modal.show();
        
        // Cargar datos del proveedor
        fetch(`/dashboard/proveedor/${proveedorId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    proveedorActual = data.proveedor;
                    content.innerHTML = data.html;
                } else {
                    content.innerHTML = `
                        <div class="text-center py-4">
                            <i class="fas fa-exclamation-triangle text-warning fa-3x mb-3"></i>
                            <p class="text-muted">Error al cargar los datos del proveedor</p>
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                content.innerHTML = `
                    <div class="text-center py-4">
                        <i class="fas fa-exclamation-triangle text-danger fa-3x mb-3"></i>
                        <p class="text-muted">Error de conexión</p>
                    </div>
                `;
            });
    };

    // Editar proveedor
    window.editarProveedor = function(proveedorId) {
        const modal = new bootstrap.Modal(document.getElementById('editarProveedorModal'));
        const content = document.getElementById('editarProveedorContent');
        const form = document.getElementById('formEditarProveedor');
        
        // Mostrar loading
        content.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-2 text-muted">Cargando formulario de edición...</p>
            </div>
        `;
        
        modal.show();
        
        // Cargar formulario de edición
        fetch(`/dashboard/proveedor/${proveedorId}/editar/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    proveedorActual = data.proveedor;
                    content.innerHTML = data.html;
                    form.action = `/dashboard/proveedor/${proveedorId}/editar/`;
                } else {
                    content.innerHTML = `
                        <div class="text-center py-4">
                            <i class="fas fa-exclamation-triangle text-warning fa-3x mb-3"></i>
                            <p class="text-muted">Error al cargar el formulario</p>
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                content.innerHTML = `
                    <div class="text-center py-4">
                        <i class="fas fa-exclamation-triangle text-danger fa-3x mb-3"></i>
                        <p class="text-muted">Error de conexión</p>
                    </div>
                `;
            });
    };

    // Eliminar proveedor
    window.eliminarProveedor = function(proveedorId, nombreProveedor) {
        document.getElementById('eliminarProveedorNombre').textContent = nombreProveedor;
        
        const modal = new bootstrap.Modal(document.getElementById('eliminarProveedorModal'));
        modal.show();
        
        // Configurar el botón de confirmación
        document.getElementById('confirmarEliminar').onclick = function() {
            const btn = this;
            const originalText = btn.innerHTML;
            
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Eliminando...';
            
            fetch(`/dashboard/proveedor/${proveedorId}/eliminar/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    modal.hide();
                    showToast(`✅ Proveedor "${nombreProveedor}" eliminado correctamente`, 'success');
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    showToast(`❌ Error: ${data.message || 'No se pudo eliminar el proveedor'}`, 'error');
                    btn.disabled = false;
                    btn.innerHTML = originalText;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('❌ Error de conexión. Intenta nuevamente.', 'error');
                btn.disabled = false;
                btn.innerHTML = originalText;
            });
        };
    };

    // Manejar formulario de nuevo proveedor
    formNuevoProveedor.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        
        submitBtnNuevo.disabled = true;
        submitBtnNuevo.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Guardando...';
        
        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const modal = bootstrap.Modal.getInstance(modalNuevoProveedor);
                modal.hide();
                showToast('✅ Proveedor creado correctamente', 'success');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                let errorMessage = '❌ ';
                if (data.errors) {
                    const errorList = Object.values(data.errors).flat();
                    errorMessage += errorList.join(', ');
                } else {
                    errorMessage += data.message || 'Error al crear el proveedor';
                }
                showToast(errorMessage, 'error');
                
                submitBtnNuevo.disabled = false;
                submitBtnNuevo.innerHTML = originalBtnText;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('❌ Error de conexión. Intenta nuevamente.', 'error');
            submitBtnNuevo.disabled = false;
            submitBtnNuevo.innerHTML = originalBtnText;
        });
    });

    // Manejar formulario de edición
    document.getElementById('formEditarProveedor').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const form = this;
        const submitBtnEditar = form.querySelector('button[type="submit"]');
        const originalText = submitBtnEditar.innerHTML;
        
        submitBtnEditar.disabled = true;
        submitBtnEditar.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Guardando...';
        
        const formData = new FormData(form);
        
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const modal = bootstrap.Modal.getInstance(document.getElementById('editarProveedorModal'));
                modal.hide();
                showToast('✅ Proveedor actualizado correctamente', 'success');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showToast(`❌ Error: ${data.message || 'No se pudo actualizar el proveedor'}`, 'error');
                submitBtnEditar.disabled = false;
                submitBtnEditar.innerHTML = originalText;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('❌ Error de conexión. Intenta nuevamente.', 'error');
            submitBtnEditar.disabled = false;
            submitBtnEditar.innerHTML = originalText;
        });
    });

    console.log('✅ Sistema de proveedores inicializado correctamente');
});
"""
    return js_content.strip()

if __name__ == "__main__":
    print("🔧 Generando JavaScript limpio para proveedores...")
    js_content = create_clean_js()
    print(f"📝 JavaScript generado: {len(js_content)} caracteres")
    print("✅ JavaScript listo para usar")
