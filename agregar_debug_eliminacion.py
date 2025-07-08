import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_separator(message=""):
    logger.info("=" * 80)
    if message:
        logger.info(f"= {message}")
        logger.info("=" * 80)

def añadir_debug_eliminacion():
    log_separator("AÑADIENDO DEBUGGING AL FLUJO DE ELIMINACIÓN")
    
    # Ruta al template
    template_path = os.path.join('dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html')
    
    if not os.path.exists(template_path):
        logger.error(f"No se encontró el archivo de template en: {template_path}")
        return False
    
    logger.info(f"Agregando debugging al template: {template_path}")
    
    # Hacer backup
    backup_path = f"{template_path}.bak.debug.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            original_content = file.read()
        
        with open(backup_path, 'w', encoding='utf-8') as file:
            file.write(original_content)
        logger.info(f"Backup creado en: {backup_path}")
    except Exception as e:
        logger.error(f"Error creando backup: {str(e)}")
        return False
    
    # Vamos a agregar código de debugging específico para la eliminación
    try:
        # Buscar la sección del modal para eliminar
        if '<!-- Modal para eliminar -->' in original_content:
            logger.info("Encontrada sección del modal para eliminar, mejorando el código...")
            
            # 1. Mejorar el formulario en el modal
            improved_modal = '''<!-- Modal para eliminar -->
<div class="modal fade" id="deleteModal" tabindex="-1" aria-labelledby="deleteModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header bg-danger text-white">
                <h5 class="modal-title" id="deleteModalLabel">Confirmar eliminación</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <p>¿Estás seguro de que deseas eliminar el producto <strong id="productoNombre"></strong>?</p>
                <p class="text-danger">Esta acción no se puede deshacer.</p>
                <div id="debug-info" class="small text-muted mb-2">
                    <p class="mb-1"><strong>Debug Info:</strong></p>
                    <p class="mb-1">Producto ID: <span id="debug-producto-id">-</span></p>
                    <p class="mb-1">Nombre: <span id="debug-producto-nombre">-</span></p>
                    <p class="mb-1">URL: <span id="debug-action-url">-</span></p>
                </div>
            </div>
            <div class="modal-footer">
                <form id="deleteForm" method="post">
                    {% csrf_token %}
                    <input type="hidden" id="producto_id_input" name="producto_id" value="">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="submit" class="btn btn-danger">Eliminar</button>
                </form>
            </div>
        </div>
    </div>
</div>'''
            
            new_content = original_content.replace(
                original_content[original_content.find('<!-- Modal para eliminar -->'):original_content.find('{% endblock %}')],
                improved_modal
            )
            
            # 2. Mejorar el manejo del evento cuando se abre el modal
            modal_event_code = '''
        // Manejo del modal de eliminar
        const deleteModal = document.getElementById('deleteModal');
        const deleteForm = document.getElementById('deleteForm');
        
        if (deleteModal) {
            console.log('✅ [MODAL] Modal de eliminación encontrado');
            
            // Evento cuando se abre el modal
            deleteModal.addEventListener('show.bs.modal', function (event) {
                console.log('📖 [MODAL] Modal de eliminación abriéndose...');
                console.log('🕐 [TIME] Timestamp modal opening:', new Date().toISOString());
                
                const button = event.relatedTarget;
                const productoId = button.getAttribute('data-id');
                const productoNombre = button.getAttribute('data-nombre');
                
                console.log(`🎯 [MODAL] Producto seleccionado para eliminar:`, {
                    id: productoId,
                    nombre: productoNombre,
                    button: button,
                    buttonTagName: button.tagName,
                    buttonClasses: button.className
                });
                
                // Actualizar el texto y los campos de debug
                document.getElementById('productoNombre').textContent = productoNombre;
                document.getElementById('debug-producto-id').textContent = productoId;
                document.getElementById('debug-producto-nombre').textContent = productoNombre;
                
                // Actualizar el valor del input oculto
                document.getElementById('producto_id_input').value = productoId;
                
                // Construir y actualizar la URL de acción
                const actionUrl = "{% url 'dashboard:eliminar_producto_venta' 0 %}".replace('0', productoId);
                document.getElementById('deleteForm').action = actionUrl;
                document.getElementById('debug-action-url').textContent = actionUrl;
                
                console.log(`🔗 [MODAL] URL de eliminación configurada: ${actionUrl}`);
                console.log(`📋 [FORM] Formulario action actualizado a: ${document.getElementById('deleteForm').action}`);
                console.log(`📋 [FORM] Input oculto producto_id actualizado a: ${document.getElementById('producto_id_input').value}`);
            });'''
            
            if '// Manejo del modal de eliminar' in new_content:
                start_idx = new_content.find('// Manejo del modal de eliminar')
                end_idx = new_content.find('// Evento cuando se confirma el modal', start_idx)
                if end_idx > start_idx:
                    new_content = new_content[:start_idx] + modal_event_code + new_content[end_idx:]
            
            # 3. Mejorar el manejo de envío del formulario
            form_submit_code = '''
        // Manejo del formulario de eliminación
        if (deleteForm) {
            console.log('✅ [FORM] Formulario de eliminación encontrado');
            console.log('📋 [FORM] Action inicial del formulario:', deleteForm.action);
            console.log('📋 [FORM] Método del formulario:', deleteForm.method);
            
            deleteForm.addEventListener('submit', function(event) {
                console.log('🚀 [FORM] ¡¡¡FORMULARIO DE ELIMINACIÓN ENVIADO!!!');
                console.log('🕐 [TIME] Timestamp form submit:', new Date().toISOString());
                
                // Log de todos los inputs del formulario
                const formInputs = this.querySelectorAll('input');
                console.log(`📝 [FORM] Número de inputs: ${formInputs.length}`);
                formInputs.forEach((input, index) => {
                    console.log(`📝 [FORM] Input #${index}:`, {
                        name: input.name,
                        value: input.value,
                        type: input.type,
                        id: input.id
                    });
                });
                
                console.log('📋 [FORM] Datos del formulario al enviar:', {
                    action: this.action,
                    method: this.method,
                    elements: this.elements.length,
                });
                
                // Verificar producto_id
                const productoIdInput = this.querySelector('input[name="producto_id"]');
                const productoId = productoIdInput ? productoIdInput.value : null;
                console.log(`🔑 [FORM] ID del producto a eliminar: ${productoId || 'NO ENCONTRADO'}`);
                
                if (!productoId) {
                    console.error('❌ [ERROR] ¡No se encontró el ID del producto! Agregando manualmente...');
                    // Extraer el ID de la URL
                    const actionUrl = this.action;
                    const urlParts = actionUrl.split('/');
                    const extractedId = urlParts[urlParts.length - 2];
                    console.log(`🔍 [RECUPERACIÓN] ID extraído de la URL: ${extractedId}`);
                    
                    // Crear input si no existe
                    if (!productoIdInput) {
                        const newInput = document.createElement('input');
                        newInput.type = 'hidden';
                        newInput.name = 'producto_id';
                        newInput.value = extractedId;
                        this.appendChild(newInput);
                        console.log(`✅ [RECUPERACIÓN] Input creado con ID: ${extractedId}`);
                    } else {
                        productoIdInput.value = extractedId;
                        console.log(`✅ [RECUPERACIÓN] Input actualizado con ID: ${extractedId}`);
                    }
                }
                
                // PREVENIR EL ENVÍO NORMAL DEL FORMULARIO
                event.preventDefault();
                console.log('🛑 [FORM] Envío normal PREVENIDO - usando AJAX...');
                
                // Obtener CSRF token
                const csrfToken = this.querySelector('[name=csrfmiddlewaretoken]');
                console.log('🔐 [CSRF] Token encontrado:', csrfToken ? 'SÍ' : 'NO');
                if (csrfToken) {
                    console.log('🔐 [CSRF] Valor del token:', csrfToken.value.substring(0, 10) + '...');
                }
                
                // Log de todos los datos del formulario
                const formData = new FormData(this);
                console.log('📊 [FORM] Todos los datos del formulario:');
                for (let [key, value] of formData.entries()) {
                    console.log(`   ${key}: ${value}`);
                }
                
                // Asegurar que el producto_id está en el FormData
                if (!formData.has('producto_id')) {
                    const actionUrl = this.action;
                    const urlParts = actionUrl.split('/');
                    const extractedId = urlParts[urlParts.length - 2];
                    formData.append('producto_id', extractedId);
                    console.log(`✅ [RECUPERACIÓN] Agregado producto_id=${extractedId} al FormData`);
                }
                
                // Log antes de enviar AJAX
                console.log('⏳ [AJAX] ¡¡¡ENVIANDO PETICIÓN AJAX DE ELIMINACIÓN AHORA!!!');
                console.log('🎯 [AJAX] URL destino:', this.action);
                console.log('📡 [AJAX] Método HTTP:', this.method.toUpperCase());'''
            
            if '// Manejo del formulario de eliminación' in new_content:
                start_idx = new_content.find('// Manejo del formulario de eliminación')
                end_idx = new_content.find('// Deshabilitar el botón de eliminar mientras se procesa', start_idx)
                if end_idx > start_idx:
                    new_content = new_content[:start_idx] + form_submit_code + new_content[end_idx:]
            
            # 4. Mejorar el fetch AJAX
            fetch_code = '''
                // Enviar via AJAX con más instrumentación
                console.log(`🚀 [AJAX] Iniciando fetch a ${this.action}...`);
                
                // Asegurar que tenemos el producto_id para el cuerpo de la petición
                let productoIdParaEnviar = formData.get('producto_id');
                if (!productoIdParaEnviar) {
                    const actionUrl = this.action;
                    const urlParts = actionUrl.split('/');
                    productoIdParaEnviar = urlParts[urlParts.length - 2];
                    formData.append('producto_id', productoIdParaEnviar);
                    console.log(`⚠️ [AJAX] No se encontró producto_id en formData. Usando ${productoIdParaEnviar} de la URL.`);
                }
                
                fetch(this.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-Debug-Delete': 'true',
                        'X-Debug-Timestamp': new Date().toISOString(),
                        'X-Producto-ID': productoIdParaEnviar,
                    },
                    credentials: 'same-origin' // Asegura envío de cookies
                })'''
            
            if 'fetch(this.action, {' in new_content:
                start_idx = new_content.find('// Enviar via AJAX con más instrumentación')
                end_idx = new_content.find('.then(response => {', start_idx)
                if end_idx > start_idx:
                    new_content = new_content[:start_idx] + fetch_code + new_content[end_idx:]
        
            # Guardar los cambios
            with open(template_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            
            logger.info("Template actualizado exitosamente con código de debugging")
            return True
        else:
            logger.error("No se encontró la sección del modal para eliminar en el template")
            return False
    
    except Exception as e:
        logger.error(f"Error actualizando el template: {str(e)}")
        return False

if __name__ == "__main__":
    if añadir_debug_eliminacion():
        print("\n✅ Debugging agregado exitosamente al flujo de eliminación.")
        print("   Por favor, reinicia el servidor Django para aplicar los cambios.")
        print("   Luego limpia la caché del navegador (Ctrl+F5 o Cmd+Shift+R).")
    else:
        print("\n❌ Error agregando debugging al flujo de eliminación.")
        print("   Revisa los logs para más detalles.")
