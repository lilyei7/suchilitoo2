import os
import sys
import django
import logging
from datetime import datetime

# Configurar entorno para Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi.settings')
sys.path.append('.')
try:
    django.setup()
    django_loaded = True
except Exception as e:
    django_loaded = False
    print(f"No se pudo cargar Django: {e}")

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

def verificar_cambios_y_permisos():
    log_separator("VERIFICANDO CAMBIOS Y PERMISOS")
    
    # Verificar archivos modificados
    template_path = os.path.join('dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html')
    view_path = os.path.join('dashboard', 'views', 'productos_venta_views.py')
    
    files_status = {}
    
    # Verificar template
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Verificar cambios específicos
        checks = {
            'input_oculto': '<input type="hidden" id="producto_id_input" name="producto_id" value="">' in content,
            'actualizar_input': 'document.getElementById(\'producto_id_input\').value = productoId;' in content,
            'prevent_default': 'event.preventDefault();' in content,
            'verificar_producto_id': 'const productoIdInput = this.querySelector(\'input[name="producto_id"]\');' in content,
            'header_producto_id': '\'X-Producto-ID\'' in content
        }
        
        files_status['template'] = {
            'exists': True,
            'checks': checks,
            'all_ok': all(checks.values())
        }
    else:
        files_status['template'] = {
            'exists': False
        }
    
    # Verificar vista
    if os.path.exists(view_path):
        with open(view_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Verificar cambios específicos
        checks = {
            'get_from_body': 'producto_id_body = request.POST.get(\'producto_id\')' in content,
            'get_from_header': 'producto_id_header = request.headers.get(\'X-Producto-ID\')' in content,
            'log_final_id': 'Producto ID final utilizado' in content
        }
        
        files_status['view'] = {
            'exists': True,
            'checks': checks,
            'all_ok': all(checks.values())
        }
    else:
        files_status['view'] = {
            'exists': False
        }
    
    # Verificar permisos si Django está cargado
    permisos_status = {}
    
    if django_loaded:
        try:
            from django.contrib.auth.models import Group, Permission
            from django.contrib.auth import get_user_model
            from django.contrib.contenttypes.models import ContentType
            
            User = get_user_model()
            
            # Verificar si existe el permiso delete_productoventa
            try:
                content_type = ContentType.objects.get(app_label='restaurant', model='productoventa')
                delete_perm = Permission.objects.get(content_type=content_type, codename='delete_productoventa')
                
                permisos_status['permiso_existe'] = True
                
                # Verificar usuarios con permiso
                users_with_perm = []
                for user in User.objects.all():
                    if user.has_perm('restaurant.delete_productoventa'):
                        users_with_perm.append(user.username)
                
                permisos_status['usuarios_con_permiso'] = users_with_perm
                permisos_status['todos_usuarios_tienen_permiso'] = len(users_with_perm) == User.objects.count()
                
                # Verificar grupos con permiso
                groups_with_perm = []
                for group in Group.objects.all():
                    if delete_perm in group.permissions.all():
                        groups_with_perm.append(group.name)
                
                permisos_status['grupos_con_permiso'] = groups_with_perm
                
                # Verificar grupo "Usuarios"
                try:
                    usuarios_group = Group.objects.get(name='Usuarios')
                    permisos_status['grupo_usuarios_existe'] = True
                    permisos_status['grupo_usuarios_tiene_permiso'] = delete_perm in usuarios_group.permissions.all()
                except Group.DoesNotExist:
                    permisos_status['grupo_usuarios_existe'] = False
            
            except Exception as e:
                permisos_status['error'] = str(e)
        
        except Exception as e:
            permisos_status['error_general'] = str(e)
    else:
        permisos_status['django_cargado'] = False
    
    # Mostrar resultados
    log_separator("RESULTADOS DE LA VERIFICACIÓN")
    
    # Template
    logger.info("VERIFICACIÓN DEL TEMPLATE:")
    if files_status['template']['exists']:
        logger.info(f"✅ Template encontrado: {template_path}")
        
        checks = files_status['template']['checks']
        for check_name, check_result in checks.items():
            if check_result:
                logger.info(f"  ✅ {check_name}: OK")
            else:
                logger.info(f"  ❌ {check_name}: FALLO")
        
        if files_status['template']['all_ok']:
            logger.info("  ✅ Todos los cambios en el template están correctos")
        else:
            logger.info("  ❌ Algunos cambios en el template no se aplicaron correctamente")
    else:
        logger.info(f"❌ Template no encontrado: {template_path}")
    
    # Vista
    logger.info("\nVERIFICACIÓN DE LA VISTA:")
    if files_status['view']['exists']:
        logger.info(f"✅ Vista encontrada: {view_path}")
        
        checks = files_status['view']['checks']
        for check_name, check_result in checks.items():
            if check_result:
                logger.info(f"  ✅ {check_name}: OK")
            else:
                logger.info(f"  ❌ {check_name}: FALLO")
        
        if files_status['view']['all_ok']:
            logger.info("  ✅ Todos los cambios en la vista están correctos")
        else:
            logger.info("  ❌ Algunos cambios en la vista no se aplicaron correctamente")
    else:
        logger.info(f"❌ Vista no encontrada: {view_path}")
    
    # Permisos
    logger.info("\nVERIFICACIÓN DE PERMISOS:")
    if django_loaded:
        if 'error_general' in permisos_status:
            logger.info(f"❌ Error general: {permisos_status['error_general']}")
        elif 'error' in permisos_status:
            logger.info(f"❌ Error verificando permisos: {permisos_status['error']}")
        else:
            if permisos_status['permiso_existe']:
                logger.info("✅ Permiso 'delete_productoventa' existe")
                
                # Usuarios con permiso
                usuarios = permisos_status['usuarios_con_permiso']
                if usuarios:
                    logger.info(f"✅ Usuarios con permiso ({len(usuarios)}): {', '.join(usuarios)}")
                else:
                    logger.info("❌ Ningún usuario tiene el permiso")
                
                # Grupos con permiso
                grupos = permisos_status['grupos_con_permiso']
                if grupos:
                    logger.info(f"✅ Grupos con permiso ({len(grupos)}): {', '.join(grupos)}")
                else:
                    logger.info("❌ Ningún grupo tiene el permiso")
                
                # Grupo Usuarios
                if permisos_status.get('grupo_usuarios_existe', False):
                    if permisos_status.get('grupo_usuarios_tiene_permiso', False):
                        logger.info("✅ El grupo 'Usuarios' tiene el permiso")
                    else:
                        logger.info("❌ El grupo 'Usuarios' NO tiene el permiso")
                else:
                    logger.info("ℹ️ El grupo 'Usuarios' no existe")
            else:
                logger.info("❌ Permiso 'delete_productoventa' NO existe")
    else:
        logger.info("❌ Django no pudo ser cargado, no se pueden verificar permisos")
    
    # Mostrar recomendaciones
    log_separator("RECOMENDACIONES")
    
    # Template
    if not files_status['template'].get('exists', False) or not files_status['template'].get('all_ok', False):
        logger.info("1. Revisa y corrige el template manualmente:")
        if not files_status['template'].get('exists', False):
            logger.info("   - Asegúrate de que el archivo existe en la ruta correcta")
        else:
            for check_name, check_result in files_status['template'].get('checks', {}).items():
                if not check_result:
                    logger.info(f"   - Agrega manualmente el cambio: {check_name}")
    
    # Vista
    if not files_status['view'].get('exists', False) or not files_status['view'].get('all_ok', False):
        logger.info("2. Revisa y corrige la vista manualmente:")
        if not files_status['view'].get('exists', False):
            logger.info("   - Asegúrate de que el archivo existe en la ruta correcta")
        else:
            for check_name, check_result in files_status['view'].get('checks', {}).items():
                if not check_result:
                    logger.info(f"   - Agrega manualmente el cambio: {check_name}")
    
    # Permisos
    if django_loaded:
        if 'error_general' in permisos_status or 'error' in permisos_status:
            logger.info("3. Corrige los errores al verificar permisos")
        elif not permisos_status.get('permiso_existe', False):
            logger.info("3. El permiso 'delete_productoventa' no existe, verifica la configuración de Django")
        elif not permisos_status.get('todos_usuarios_tienen_permiso', False):
            logger.info("3. Asigna el permiso 'delete_productoventa' a todos los usuarios relevantes")
        
        if permisos_status.get('grupo_usuarios_existe', False) and not permisos_status.get('grupo_usuarios_tiene_permiso', False):
            logger.info("4. Asigna el permiso 'delete_productoventa' al grupo 'Usuarios'")
    
    # General
    logger.info("\nPASOS FINALES:")
    logger.info("1. Reinicia el servidor Django para aplicar todos los cambios")
    logger.info("2. Limpia la caché del navegador (Ctrl+F5 o Cmd+Shift+R)")
    logger.info("3. Prueba la eliminación de productos nuevamente")
    logger.info("4. Si persisten los problemas, verifica los logs del servidor y la consola del navegador")

if __name__ == "__main__":
    verificar_cambios_y_permisos()
