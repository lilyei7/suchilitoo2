import os
import sys
import django
import logging
from datetime import datetime

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi.settings')
django.setup()

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

def corregir_envio_id_producto():
    log_separator("CORRIGIENDO ENVÍO DE ID DE PRODUCTO EN LA ELIMINACIÓN")
    logger.info(f"Iniciando corrección: {datetime.now().isoformat()}")
    
    # Ruta al template
    template_path = os.path.join('dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html')
    
    if not os.path.exists(template_path):
        logger.error(f"No se encontró el archivo de template en: {template_path}")
        return False
    
    logger.info(f"Corrigiendo template: {template_path}")
    
    # Hacer backup
    backup_path = f"{template_path}.bak.fix_id.{datetime.now().strftime('%Y%m%d%H%M%S')}"
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
        new_content = original_content
        
        # 1. Asegurarnos que el formulario del modal tiene un input oculto para el ID
        if '<form id="deleteForm" method="post">' in new_content and '<input type="hidden" id="producto_id_input" name="producto_id" value="">' not in new_content:
            logger.info("Agregando input oculto para producto_id en el formulario")
            new_content = new_content.replace(
                '<form id="deleteForm" method="post">',
                '<form id="deleteForm" method="post">\n                    <input type="hidden" id="producto_id_input" name="producto_id" value="">'
            )
        
        # 2. Asegurarnos que se actualiza el input oculto cuando se abre el modal
        if 'document.getElementById(\'productoNombre\').textContent = productoNombre;' in new_content and 'document.getElementById(\'producto_id_input\').value = productoId;' not in new_content:
            logger.info("Agregando código para actualizar el input oculto cuando se abre el modal")
            new_content = new_content.replace(
                'document.getElementById(\'productoNombre\').textContent = productoNombre;',
                'document.getElementById(\'productoNombre\').textContent = productoNombre;\n                document.getElementById(\'producto_id_input\').value = productoId;'
            )
        
        # 3. Mejorar la sección de envío del formulario
        if 'deleteForm.addEventListener(\'submit\', function(event) {' in new_content:
            logger.info("Mejorando la gestión del envío del formulario")
            
            # Verificar que se hace un log del producto_id
            log_form_data_code = '''
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
                }'''
            
            if 'const productoIdInput = this.querySelector(\'input[name="producto_id"]\');' not in new_content:
                # Buscar un lugar adecuado para insertar el código
                form_data_logs_pos = new_content.find('// Log de todos los datos del formulario', new_content.find('deleteForm.addEventListener(\'submit\''))
                if form_data_logs_pos > 0:
                    new_content = new_content[:form_data_logs_pos] + log_form_data_code + new_content[form_data_logs_pos:]
        
        # 4. Asegurar que se incluye el producto_id en los headers de la petición AJAX
        if 'fetch(this.action, {' in new_content and '\'X-Producto-ID\': productoIdParaEnviar' not in new_content:
            logger.info("Mejorando la petición AJAX para incluir el producto_id en los headers")
            
            ajax_headers_code = '''
                // Asegurar que tenemos el producto_id para el cuerpo de la petición
                let productoIdParaEnviar = formData.get('producto_id');
                if (!productoIdParaEnviar) {
                    const actionUrl = this.action;
                    const urlParts = actionUrl.split('/');
                    productoIdParaEnviar = urlParts[urlParts.length - 2];
                    formData.append('producto_id', productoIdParaEnviar);
                    console.log(`⚠️ [AJAX] No se encontró producto_id en formData. Usando ${productoIdParaEnviar} de la URL.`);
                }'''
            
            fetch_pos = new_content.find('fetch(this.action, {')
            if fetch_pos > 0:
                headers_pos = new_content.find('headers: {', fetch_pos)
                if headers_pos > 0:
                    headers_end_pos = new_content.find('},', headers_pos)
                    if headers_end_pos > 0:
                        # Insertar el código antes del fetch
                        pre_fetch_pos = new_content.rfind('\n', 0, fetch_pos)
                        if pre_fetch_pos > 0:
                            new_content = new_content[:pre_fetch_pos] + ajax_headers_code + new_content[pre_fetch_pos:]
                        
                        # Agregar el header X-Producto-ID
                        headers_content = new_content[headers_pos:headers_end_pos]
                        if '\'X-Producto-ID\'' not in headers_content:
                            new_headers = headers_content + '\n                        \'X-Producto-ID\': productoIdParaEnviar,'
                            new_content = new_content[:headers_pos] + new_headers + new_content[headers_end_pos:]
        
        # 5. Actualizar la respuesta del backend
        # Ahora vamos a modificar la vista para que acepte el producto_id tanto de la URL como del body
        view_path = os.path.join('dashboard', 'views', 'productos_venta_views.py')
        if os.path.exists(view_path):
            logger.info(f"Modificando vista: {view_path}")
            
            with open(view_path, 'r', encoding='utf-8') as file:
                view_content = file.read()
            
            # Hacer backup
            view_backup_path = f"{view_path}.bak.fix_id.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            with open(view_backup_path, 'w', encoding='utf-8') as file:
                file.write(view_content)
            logger.info(f"Backup de vista creado en: {view_backup_path}")
            
            # Buscar el inicio de la función eliminar_producto_venta
            if 'def eliminar_producto_venta(request, producto_id, force=False):' in view_content:
                logger.info("Encontrada función eliminar_producto_venta, mejorando manejo de producto_id")
                
                # Agregar código para obtener producto_id del body si no viene en la URL
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
                
                # Buscar el lugar adecuado para insertar el código
                after_logs_pos = view_content.find('logger.info(f"")', view_content.find('def eliminar_producto_venta'))
                if after_logs_pos > 0:
                    view_content = view_content[:after_logs_pos + 20] + producto_id_check_code + view_content[after_logs_pos + 20:]
                
                # Guardar los cambios
                with open(view_path, 'w', encoding='utf-8') as file:
                    file.write(view_content)
                logger.info("Vista actualizada exitosamente")
        else:
            logger.warning(f"No se encontró el archivo de vista en: {view_path}")
        
        # Guardar los cambios al template
        with open(template_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        logger.info("Template actualizado exitosamente")
        return True
    
    except Exception as e:
        logger.error(f"Error actualizando archivos: {str(e)}")
        return False

if __name__ == "__main__":
    if corregir_envio_id_producto():
        print("\n✅ Correcciones aplicadas exitosamente al flujo de eliminación.")
        print("   Por favor, reinicia el servidor Django para aplicar los cambios.")
        print("   Luego limpia la caché del navegador (Ctrl+F5 o Cmd+Shift+R).")
    else:
        print("\n❌ Error aplicando correcciones al flujo de eliminación.")
        print("   Revisa los logs para más detalles.")
