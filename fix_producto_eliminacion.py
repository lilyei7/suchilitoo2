import os
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

def corregir_problema_eliminacion():
    log_separator("CORRIGIENDO PROBLEMA DE ELIMINACIÓN DE PRODUCTOS")
    
    # Ruta al template
    template_path = os.path.join('dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html')
    
    if not os.path.exists(template_path):
        logger.error(f"No se encontró el archivo de template en: {template_path}")
        return False
    
    logger.info(f"Modificando template: {template_path}")
    
    # Hacer backup
    backup_path = f"{template_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            original_content = file.read()
        
        with open(backup_path, 'w', encoding='utf-8') as file:
            file.write(original_content)
        logger.info(f"Backup creado en: {backup_path}")
    except Exception as e:
        logger.error(f"Error creando backup: {str(e)}")
        return False
    
    try:
        # Modificar el template
        new_content = original_content
        
        # 1. Agregar input oculto al formulario del modal
        if '<form id="deleteForm" method="post">' in new_content:
            logger.info("Agregando input oculto para producto_id en el formulario")
            new_content = new_content.replace(
                '<form id="deleteForm" method="post">',
                '<form id="deleteForm" method="post">\n                    {% csrf_token %}\n                    <input type="hidden" id="producto_id_input" name="producto_id" value="">'
            )
        
        # 2. Actualizar el input oculto cuando se abre el modal
        if 'deleteModal.addEventListener(\'show.bs.modal\', function (event) {' in new_content:
            # Buscar donde se actualiza el productoNombre
            productoNombre_update_pos = new_content.find('document.getElementById(\'productoNombre\').textContent = productoNombre;', 
                                                        new_content.find('deleteModal.addEventListener(\'show.bs.modal\''))
            
            if productoNombre_update_pos > 0:
                # Verificar si ya existe la actualización del input
                if 'document.getElementById(\'producto_id_input\').value = productoId;' not in new_content[productoNombre_update_pos:productoNombre_update_pos+200]:
                    logger.info("Agregando código para actualizar el input oculto cuando se abre el modal")
                    
                    # Encontrar el final de la línea
                    line_end_pos = new_content.find('\n', productoNombre_update_pos)
                    if line_end_pos > 0:
                        update_code = '\n                document.getElementById(\'producto_id_input\').value = productoId;'
                        new_content = new_content[:line_end_pos] + update_code + new_content[line_end_pos:]
        
        # 3. Mejorar el evento submit para asegurar que se envía el ID
        if 'deleteForm.addEventListener(\'submit\', function(event) {' in new_content:
            submit_pos = new_content.find('deleteForm.addEventListener(\'submit\', function(event) {')
            
            # Verificar que se hace preventDefault
            prevent_default_pos = new_content.find('event.preventDefault();', submit_pos)
            if prevent_default_pos < 0 or prevent_default_pos > submit_pos + 500:
                logger.info("Agregando event.preventDefault() al submit")
                
                # Encontrar el lugar adecuado para insertar
                open_brace_pos = new_content.find('{', submit_pos)
                if open_brace_pos > 0:
                    line_end_pos = new_content.find('\n', open_brace_pos)
                    if line_end_pos > 0:
                        prevent_code = '\n                event.preventDefault();'
                        new_content = new_content[:line_end_pos] + prevent_code + new_content[line_end_pos:]
            
            # Agregar código para verificar y asegurar que el producto_id está presente
            form_data_pos = new_content.find('const formData = new FormData(this);', submit_pos)
            if form_data_pos > 0:
                verify_id_code = '''
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
                '''
                
                # Verificar si ya existe este código
                if 'const productoIdInput = this.querySelector(\'input[name="producto_id"]\');' not in new_content[submit_pos:form_data_pos]:
                    logger.info("Agregando código para verificar y asegurar producto_id")
                    new_content = new_content[:form_data_pos] + verify_id_code + new_content[form_data_pos:]
            
            # Agregar código para asegurar que producto_id está en formData
            formdata_entries_pos = new_content.find('for (let [key, value] of formData.entries()) {', form_data_pos if form_data_pos > 0 else submit_pos)
            if formdata_entries_pos > 0:
                formdata_end_pos = new_content.find('}', formdata_entries_pos)
                if formdata_end_pos > 0:
                    ensure_id_code = '''
                
                // Asegurar que el producto_id está en el FormData
                if (!formData.has('producto_id')) {
                    const actionUrl = this.action;
                    const urlParts = actionUrl.split('/');
                    const extractedId = urlParts[urlParts.length - 2];
                    formData.append('producto_id', extractedId);
                    console.log(`✅ [RECUPERACIÓN] Agregado producto_id=${extractedId} al FormData`);
                }
                '''
                    
                    # Verificar si ya existe este código
                    if 'if (!formData.has(\'producto_id\'))' not in new_content[formdata_entries_pos:formdata_entries_pos+500]:
                        logger.info("Agregando código para asegurar producto_id en formData")
                        new_content = new_content[:formdata_end_pos + 1] + ensure_id_code + new_content[formdata_end_pos + 1:]
        
        # 4. Agregar header con producto_id en fetch
        if 'fetch(this.action, {' in new_content:
            fetch_pos = new_content.find('fetch(this.action, {')
            headers_pos = new_content.find('headers: {', fetch_pos)
            
            if headers_pos > 0:
                # Verificar si ya existe el header
                if '\'X-Producto-ID\'' not in new_content[headers_pos:headers_pos+500]:
                    logger.info("Agregando header X-Producto-ID a la petición fetch")
                    
                    # Encontrar donde termina el bloque de headers
                    headers_end_pos = new_content.find('},', headers_pos)
                    if headers_end_pos > 0:
                        # Agregar el header justo antes del cierre
                        header_code = '\n                        \'X-Producto-ID\': formData.get(\'producto_id\'),'
                        new_content = new_content[:headers_end_pos] + header_code + new_content[headers_end_pos:]
        
        # Guardar los cambios
        with open(template_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        logger.info("✅ Template actualizado exitosamente")
        
        # Ahora modificar la vista
        view_path = os.path.join('dashboard', 'views', 'productos_venta_views.py')
        if os.path.exists(view_path):
            logger.info(f"Modificando vista: {view_path}")
            
            with open(view_path, 'r', encoding='utf-8') as file:
                view_content = file.read()
            
            # Hacer backup
            view_backup_path = f"{view_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            with open(view_backup_path, 'w', encoding='utf-8') as file:
                file.write(view_content)
            logger.info(f"Backup de vista creado en: {view_backup_path}")
            
            # Buscar el inicio de la función eliminar_producto_venta
            if 'def eliminar_producto_venta(request, producto_id, force=False):' in view_content:
                # Buscar después de los logs iniciales
                logs_section_end = view_content.find('try:', view_content.find('def eliminar_producto_venta'))
                
                if logs_section_end > 0:
                    # Código para verificar producto_id desde diferentes fuentes
                    producto_id_check_code = '''
    # Verificar si el producto_id viene del body en caso de que la URL no tenga el ID correcto
    if not producto_id or producto_id == '0':
        logger.warning(f"Producto ID en URL es inválido: {producto_id}")
        # Intentar obtener del body
        producto_id_body = request.POST.get('producto_id')
        if producto_id_body:
            logger.info(f"Producto ID encontrado en el body: {producto_id_body}")
            producto_id = producto_id_body
        else:
            # Intentar obtener de los headers
            producto_id_header = request.headers.get('X-Producto-ID')
            if producto_id_header:
                logger.info(f"Producto ID encontrado en los headers: {producto_id_header}")
                producto_id = producto_id_header
            else:
                logger.error(f"No se pudo encontrar un ID de producto válido ni en URL, ni en body, ni en headers")
    
    logger.info(f"Producto ID final utilizado: {producto_id}")
    
    '''
                    
                    # Verificar si ya existe este código
                    if 'Producto ID final utilizado' not in view_content[logs_section_end-500:logs_section_end]:
                        logger.info("Agregando código para verificar producto_id desde diferentes fuentes")
                        view_content = view_content[:logs_section_end] + producto_id_check_code + view_content[logs_section_end:]
                
                # Guardar los cambios
                with open(view_path, 'w', encoding='utf-8') as file:
                    file.write(view_content)
                
                logger.info("✅ Vista actualizada exitosamente")
            else:
                logger.warning("No se encontró la función eliminar_producto_venta en la vista")
        else:
            logger.warning(f"No se encontró el archivo de vista en: {view_path}")
        
        # Todo completado
        return True
    
    except Exception as e:
        logger.error(f"Error actualizando archivos: {str(e)}")
        return False

if __name__ == "__main__":
    if corregir_problema_eliminacion():
        print("\n✅ Correcciones aplicadas exitosamente.")
        print("   1. Se ha agregado un input oculto para el ID del producto.")
        print("   2. Se ha mejorado el código para actualizar y verificar el ID.")
        print("   3. Se ha agregado un header con el ID en la petición AJAX.")
        print("   4. Se ha modificado la vista para aceptar el ID desde diferentes fuentes.")
        print("\n   Por favor:")
        print("   - Reinicia el servidor Django para aplicar los cambios.")
        print("   - Limpia la caché del navegador (Ctrl+F5 o Cmd+Shift+R).")
        print("   - Prueba nuevamente la eliminación de productos.")
    else:
        print("\n❌ Error aplicando correcciones.")
        print("   Revisa los logs para más detalles.")
