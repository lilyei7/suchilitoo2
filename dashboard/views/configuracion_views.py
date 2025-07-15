from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import logging
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from dashboard.utils.permissions import require_module_access
from restaurant.models import ConfiguracionSistema
from datetime import datetime

logger = logging.getLogger(__name__)

@login_required
def configuracion_temas(request):
    """Vista para la configuración de temas y colores del sistema"""
    try:
        # Obtener o crear la configuración actual de tema
        config, created = ConfiguracionSistema.objects.get_or_create(
            nombre="tema_colores",
            defaults={
                'valor': json.dumps({
                    'sidebar_bg': '#343a40',
                    'sidebar_text': '#ffffff',
                    'navbar_bg': '#f8f9fa',
                    'navbar_text': '#212529',
                    'primary_color': '#0d6efd',
                    'secondary_color': '#6c757d',
                    'accent_color': '#fd7e14'
                })
            }
        )
        
        # Obtener o crear la configuración actual de logo
        logo_config, logo_created = ConfiguracionSistema.objects.get_or_create(
            nombre="logo_sistema",
            defaults={
                'valor': json.dumps({
                    'logo_path': 'dashboard/img/logos/original.png',
                    'usar_logo_personalizado': False
                })
            }
        )
        
        # Cargar los colores actuales
        colores_actuales = json.loads(config.valor)
        
        # Cargar la configuración del logo
        logo_config_data = json.loads(logo_config.valor)
        logo_path = logo_config_data.get('logo_path', 'dashboard/img/logos/original.png')
        usar_logo_personalizado = logo_config_data.get('usar_logo_personalizado', False)
        
        # Si es una solicitud POST, actualizar los colores y/o logo
        if request.method == 'POST':
            try:
                # Verificar si se está actualizando el logo
                if 'logo_file' in request.FILES:
                    logo_file = request.FILES['logo_file']
                    # Create directories if they don't exist
                    logos_dir = os.path.join('dashboard', 'static', 'dashboard', 'img', 'logos')
                    os.makedirs(logos_dir, exist_ok=True)
                    
                    # Save the file to the static directory, not STATIC_ROOT
                    fs = FileSystemStorage(location=logos_dir)
                    filename = fs.save(logo_file.name, logo_file)
                    logo_path = f'dashboard/img/logos/{filename}'
                    usar_logo_personalizado = True
                    
                    # Run collectstatic to copy the file to STATIC_ROOT
                    from django.core.management import call_command
                    call_command('collectstatic', '--noinput')
                
                # Obtener datos del formulario para el tema
                nuevo_tema = {
                    'sidebar_bg': request.POST.get('sidebar_bg', '#343a40'),
                    'sidebar_text': request.POST.get('sidebar_text', '#ffffff'),
                    'navbar_bg': request.POST.get('navbar_bg', '#f8f9fa'),
                    'navbar_text': request.POST.get('navbar_text', '#212529'),
                    'primary_color': request.POST.get('primary_color', '#0d6efd'),
                    'secondary_color': request.POST.get('secondary_color', '#6c757d'),
                    'accent_color': request.POST.get('accent_color', '#fd7e14')
                }
                
                # Actualizar en la base de datos el tema
                config.valor = json.dumps(nuevo_tema)
                config.save()
                
                # Actualizar en la base de datos el logo
                logo_config_data = {
                    'logo_path': logo_path,
                    'usar_logo_personalizado': usar_logo_personalizado
                }
                logo_config.valor = json.dumps(logo_config_data)
                logo_config.save()
                
                # Actualizar la variable colores_actuales para la vista
                colores_actuales = nuevo_tema
                
                messages.success(request, 'Configuración actualizada correctamente')
                
                # Si es AJAX, devolver una respuesta JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Configuración actualizada correctamente',
                        'tema': nuevo_tema,
                        'logo': logo_config_data
                    })
                
            except Exception as e:
                logger.error(f"Error al actualizar configuración: {e}")
                messages.error(request, f"Error al actualizar configuración: {str(e)}")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f"Error al actualizar configuración: {str(e)}"
                    })
        
        # Preparar temas predefinidos
        temas_predefinidos = {
            'azul_oscuro': {
                'nombre': 'Azul Oscuro',
                'sidebar_bg': '#1a2942',
                'sidebar_text': '#ffffff',
                'navbar_bg': '#f8f9fa',
                'navbar_text': '#212529',
                'primary_color': '#3c6cde',
                'secondary_color': '#6c757d',
                'accent_color': '#fd7e14'
            },
            'verde_claro': {
                'nombre': 'Verde Claro',
                'sidebar_bg': '#2d572c',
                'sidebar_text': '#ffffff',
                'navbar_bg': '#f8f9fa',
                'navbar_text': '#212529',
                'primary_color': '#4caf50',
                'secondary_color': '#6c757d',
                'accent_color': '#ff9800'
            },
            'morado_elegante': {
                'nombre': 'Morado Elegante',
                'sidebar_bg': '#4a235a',
                'sidebar_text': '#ffffff',
                'navbar_bg': '#f8f9fa',
                'navbar_text': '#212529',
                'primary_color': '#8e44ad',
                'secondary_color': '#6c757d',
                'accent_color': '#f39c12'
            },
            'rojo_clasico': {
                'nombre': 'Rojo Clásico',
                'sidebar_bg': '#7d1a1a',
                'sidebar_text': '#ffffff',
                'navbar_bg': '#f8f9fa',
                'navbar_text': '#212529',
                'primary_color': '#dc3545',
                'secondary_color': '#6c757d',
                'accent_color': '#ffc107'
            },
            'oscuro_elegante': {
                'nombre': 'Oscuro Elegante',
                'sidebar_bg': '#121212',
                'sidebar_text': '#e0e0e0',
                'navbar_bg': '#1e1e1e',
                'navbar_text': '#e0e0e0',
                'primary_color': '#bb86fc',
                'secondary_color': '#4a4a4a',
                'accent_color': '#03dac6'
            },
            'marino_fresco': {
                'nombre': 'Marino Fresco',
                'sidebar_bg': '#00334e',
                'sidebar_text': '#ffffff',
                'navbar_bg': '#f8f9fa',
                'navbar_text': '#212529',
                'primary_color': '#0077b6',
                'secondary_color': '#6c757d',
                'accent_color': '#00b4d8'
            },
            'amanecer': {
                'nombre': 'Amanecer',
                'sidebar_bg': '#ff7b00',
                'sidebar_text': '#ffffff',
                'navbar_bg': '#ffecd1',
                'navbar_text': '#4f4f4f',
                'primary_color': '#ff4800',
                'secondary_color': '#6c757d',
                'accent_color': '#ffd000'
            },
            'verde_azulado': {
                'nombre': 'Verde Azulado',
                'sidebar_bg': '#1b4332',
                'sidebar_text': '#ffffff',
                'navbar_bg': '#f8f9fa',
                'navbar_text': '#212529',
                'primary_color': '#2d6a4f',
                'secondary_color': '#6c757d',
                'accent_color': '#40916c'
            }
        }
        
        # Obtener todos los logos disponibles en la carpeta logos
        logos_dir_static = os.path.join('dashboard', 'static', 'dashboard', 'img', 'logos')
        logos_dir_staticfiles = os.path.join(settings.STATIC_ROOT, 'dashboard', 'img', 'logos')
        logos_disponibles = []
        
        # Check both directories for logos
        for dir_path in [logos_dir_static, logos_dir_staticfiles]:
            if os.path.exists(dir_path):
                for file in os.listdir(dir_path):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.gif')):
                        logo_info = {
                            'nombre': file,
                            'path': f'dashboard/img/logos/{file}'
                        }
                        # Avoid duplicates
                        if not any(logo['nombre'] == file for logo in logos_disponibles):
                            logos_disponibles.append(logo_info)
        
        return render(request, 'dashboard/configuracion/temas.html', {
            'colores': colores_actuales,
            'temas_predefinidos': temas_predefinidos,
            'sidebar_active': 'configuracion_temas',
            'configuracion_section_active': True,
            'logo_actual': logo_path,
            'logos_disponibles': logos_disponibles,
            'usar_logo_personalizado': usar_logo_personalizado
        })
        
    except Exception as e:
        logger.error(f"Error en configuración de temas: {e}")
        messages.error(request, f"Error en configuración de temas: {str(e)}")
        return render(request, 'dashboard/configuracion/temas.html', {
            'colores': {
                'sidebar_bg': '#343a40',
                'sidebar_text': '#ffffff',
                'navbar_bg': '#f8f9fa',
                'navbar_text': '#212529',
                'primary_color': '#0d6efd',
                'secondary_color': '#6c757d',
                'accent_color': '#fd7e14'
            },
            'sidebar_active': 'configuracion_temas',
            'configuracion_section_active': True,
            'logo_actual': 'dashboard/img/logos/original.png',
            'logos_disponibles': []
        })

@login_required
def configuracion_general(request):
    """Vista para la configuración general del sistema"""
    return render(request, 'dashboard/configuracion/general.html', {
        'sidebar_active': 'configuracion_general',
        'configuracion_section_active': True
    })

@require_POST
@login_required
def guardar_tema(request):
    """Endpoint AJAX para guardar un tema personalizado"""
    try:
        # Obtener datos del formulario
        tema_data = json.loads(request.body)
        
        # Validar datos mínimos
        campos_requeridos = ['sidebar_bg', 'sidebar_text', 'primary_color']
        for campo in campos_requeridos:
            if campo not in tema_data:
                return JsonResponse({
                    'success': False,
                    'message': f'Falta el campo requerido: {campo}'
                })
        
        # Obtener o crear la configuración
        config, created = ConfiguracionSistema.objects.get_or_create(
            nombre="tema_colores",
            defaults={'valor': '{}'}
        )
        
        # Guardar en la base de datos
        config.valor = json.dumps(tema_data)
        config.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Tema guardado correctamente'
        })
        
    except Exception as e:
        logger.error(f"Error al guardar tema: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al guardar tema: {str(e)}'
        })

@login_required
def obtener_tema_actual(request):
    """Endpoint AJAX para obtener el tema actual"""
    try:
        config = ConfiguracionSistema.objects.filter(nombre="tema_colores").first()
        
        if config:
            tema = json.loads(config.valor)
            return JsonResponse({
                'success': True,
                'tema': tema
            })
        else:
            # Valores por defecto
            return JsonResponse({
                'success': True,
                'tema': {
                    'sidebar_bg': '#343a40',
                    'sidebar_text': '#ffffff',
                    'navbar_bg': '#f8f9fa',
                    'navbar_text': '#212529',
                    'primary_color': '#0d6efd',
                    'secondary_color': '#6c757d',
                    'accent_color': '#fd7e14'
                }
            })
            
    except Exception as e:
        logger.error(f"Error al obtener tema: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener tema: {str(e)}'
        })

@login_required
def obtener_logo_actual(request):
    """Endpoint AJAX para obtener el logo actual"""
    try:
        config = ConfiguracionSistema.objects.filter(nombre="logo_sistema").first()
        
        if config:
            logo_data = json.loads(config.valor)
            return JsonResponse({
                'success': True,
                'logo': logo_data
            })
        else:
            # Valores por defecto
            return JsonResponse({
                'success': True,
                'logo': {
                    'logo_path': 'dashboard/img/logos/original.png',
                    'usar_logo_personalizado': False
                }
            })
            
    except Exception as e:
        logger.error(f"Error al obtener logo: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener logo: {str(e)}'
        })

@login_required
def backup_database(request):
    """Vista para la gestión de copias de seguridad de la base de datos"""
    try:
        # Obtener la lista de copias de seguridad existentes
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        
        # Crear el directorio de backups si no existe
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        # Listar archivos de backup (solo .sql o .dump)
        backups = []
        if os.path.exists(backup_dir):
            for file in os.listdir(backup_dir):
                if file.endswith(('.sql', '.dump', '.gz', '.bak')):
                    file_path = os.path.join(backup_dir, file)
                    backups.append({
                        'name': file,
                        'size': os.path.getsize(file_path) / (1024 * 1024),  # Tamaño en MB
                        'date': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        # Ordenar por fecha, más reciente primero
        backups.sort(key=lambda x: x['date'], reverse=True)
        
        return render(request, 'dashboard/configuracion/backup.html', {
            'backups': backups,
            'sidebar_active': 'configuracion_backup',
            'configuracion_section_active': True
        })
    except Exception as e:
        logger.error(f"Error en gestión de copias de seguridad: {e}")
        messages.error(request, f"Error en gestión de copias de seguridad: {str(e)}")
        return render(request, 'dashboard/configuracion/backup.html', {
            'backups': [],
            'sidebar_active': 'configuracion_backup',
            'configuracion_section_active': True
        })

@login_required
@require_POST
def crear_backup_api(request):
    """Endpoint AJAX para crear una copia de seguridad de la base de datos"""
    try:
        import subprocess
        from django.db import connections
        
        # Obtener información de la base de datos
        db_settings = settings.DATABASES['default']
        db_type = db_settings['ENGINE'].split('.')[-1]
        
        # Nombre del archivo basado en la fecha actual
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        
        # Crear directorio si no existe
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Crear el backup según el tipo de base de datos
        if db_type == 'sqlite3':
            # Para SQLite, simplemente copiamos el archivo
            db_path = db_settings['NAME']
            backup_path = os.path.join(backup_dir, f'backup_{timestamp}.sqlite3')
            import shutil
            shutil.copy2(db_path, backup_path)
            
        elif db_type == 'postgresql':
            # Para PostgreSQL, usamos pg_dump
            db_name = db_settings['NAME']
            db_user = db_settings['USER']
            db_password = db_settings['PASSWORD']
            db_host = db_settings['HOST'] or 'localhost'
            
            backup_path = os.path.join(backup_dir, f'backup_{db_name}_{timestamp}.sql')
            
            # Configurar variables de entorno para la contraseña
            env = os.environ.copy()
            env['PGPASSWORD'] = db_password
            
            # Ejecutar pg_dump
            command = [
                'pg_dump',
                '--dbname=' + db_name,
                '--username=' + db_user,
                '--host=' + db_host,
                '--file=' + backup_path,
                '--format=custom'
            ]
            
            result = subprocess.run(command, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Error en pg_dump: {result.stderr}")
                return JsonResponse({
                    'success': False,
                    'message': f'Error al crear backup: {result.stderr}'
                })
                
        elif db_type == 'mysql':
            # Para MySQL, usamos mysqldump
            db_name = db_settings['NAME']
            db_user = db_settings['USER']
            db_password = db_settings['PASSWORD']
            db_host = db_settings['HOST'] or 'localhost'
            
            backup_path = os.path.join(backup_dir, f'backup_{db_name}_{timestamp}.sql')
            
            # Ejecutar mysqldump
            command = [
                'mysqldump',
                '--user=' + db_user,
                '--password=' + db_password,
                '--host=' + db_host,
                db_name,
                '--result-file=' + backup_path
            ]
            
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Error en mysqldump: {result.stderr}")
                return JsonResponse({
                    'success': False,
                    'message': f'Error al crear backup: {result.stderr}'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': f'Motor de base de datos no soportado: {db_type}'
            })
        
        # Verificar que el backup se creó correctamente
        if not os.path.exists(backup_path):
            return JsonResponse({
                'success': False,
                'message': 'No se pudo crear el archivo de backup'
            })
        
        # Obtener tamaño del archivo
        file_size = os.path.getsize(backup_path) / (1024 * 1024)  # Tamaño en MB
        
        return JsonResponse({
            'success': True,
            'message': 'Copia de seguridad creada correctamente',
            'backup': {
                'name': os.path.basename(backup_path),
                'path': backup_path,
                'size': round(file_size, 2),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        logger.error(f"Error al crear copia de seguridad: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al crear copia de seguridad: {str(e)}'
        })

@login_required
@require_POST
def restaurar_backup_api(request):
    """Endpoint AJAX para restaurar una copia de seguridad de la base de datos"""
    try:
        import subprocess
        from django.db import connections
        
        # Obtener el nombre del archivo a restaurar
        backup_file = request.POST.get('backup_file')
        if not backup_file:
            return JsonResponse({
                'success': False,
                'message': 'No se especificó archivo de backup'
            })
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        backup_path = os.path.join(backup_dir, backup_file)
        
        # Verificar que el archivo existe
        if not os.path.exists(backup_path):
            return JsonResponse({
                'success': False,
                'message': 'El archivo de backup no existe'
            })
        
        # Obtener información de la base de datos
        db_settings = settings.DATABASES['default']
        db_type = db_settings['ENGINE'].split('.')[-1]
        
        # Restaurar según el tipo de base de datos
        if db_type == 'sqlite3':
            # Para SQLite, cerramos todas las conexiones y reemplazamos el archivo
            db_path = db_settings['NAME']
            connections.close_all()
            
            # Hacer copia de seguridad antes de restaurar
            import shutil
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            current_backup = os.path.join(backup_dir, f'pre_restore_{timestamp}.sqlite3')
            shutil.copy2(db_path, current_backup)
            
            # Restaurar desde el backup
            shutil.copy2(backup_path, db_path)
            
        elif db_type == 'postgresql':
            # Para PostgreSQL, usamos pg_restore
            db_name = db_settings['NAME']
            db_user = db_settings['USER']
            db_password = db_settings['PASSWORD']
            db_host = db_settings['HOST'] or 'localhost'
            
            # Configurar variables de entorno para la contraseña
            env = os.environ.copy()
            env['PGPASSWORD'] = db_password
            
            # Primero, hacer un backup de la situación actual
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            current_backup = os.path.join(backup_dir, f'pre_restore_{db_name}_{timestamp}.sql')
            
            # Backup antes de restaurar
            backup_command = [
                'pg_dump',
                '--dbname=' + db_name,
                '--username=' + db_user,
                '--host=' + db_host,
                '--file=' + current_backup,
                '--format=custom'
            ]
            
            subprocess.run(backup_command, env=env, capture_output=True, text=True)
            
            # Cerrar conexiones
            connections.close_all()
            
            # Restaurar desde backup
            # Primero recreamos la base de datos
            drop_command = [
                'dropdb',
                '--username=' + db_user,
                '--host=' + db_host,
                '--if-exists',
                db_name
            ]
            
            create_command = [
                'createdb',
                '--username=' + db_user,
                '--host=' + db_host,
                db_name
            ]
            
            restore_command = [
                'pg_restore',
                '--dbname=' + db_name,
                '--username=' + db_user,
                '--host=' + db_host,
                '--clean',
                backup_path
            ]
            
            # Ejecutar los comandos en secuencia
            subprocess.run(drop_command, env=env, capture_output=True, text=True)
            subprocess.run(create_command, env=env, capture_output=True, text=True)
            result = subprocess.run(restore_command, env=env, capture_output=True, text=True)
            
            if result.returncode != 0 and "not found" in result.stderr:
                logger.error(f"Error en pg_restore: {result.stderr}")
                return JsonResponse({
                    'success': False,
                    'message': f'Error al restaurar backup: {result.stderr}'
                })
                
        elif db_type == 'mysql':
            # Para MySQL, usamos mysql
            db_name = db_settings['NAME']
            db_user = db_settings['USER']
            db_password = db_settings['PASSWORD']
            db_host = db_settings['HOST'] or 'localhost'
            
            # Backup antes de restaurar
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            current_backup = os.path.join(backup_dir, f'pre_restore_{db_name}_{timestamp}.sql')
            
            backup_command = [
                'mysqldump',
                '--user=' + db_user,
                '--password=' + db_password,
                '--host=' + db_host,
                db_name,
                '--result-file=' + current_backup
            ]
            
            subprocess.run(backup_command, capture_output=True, text=True)
            
            # Cerrar conexiones
            connections.close_all()
            
            # Restaurar desde backup
            restore_command = [
                'mysql',
                '--user=' + db_user,
                '--password=' + db_password,
                '--host=' + db_host,
                db_name,
                '--execute=source ' + backup_path
            ]
            
            result = subprocess.run(restore_command, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Error en mysql restore: {result.stderr}")
                return JsonResponse({
                    'success': False,
                    'message': f'Error al restaurar backup: {result.stderr}'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': f'Motor de base de datos no soportado: {db_type}'
            })
        
        return JsonResponse({
            'success': True,
            'message': 'Base de datos restaurada correctamente. Se recomienda reiniciar la aplicación.'
        })
        
    except Exception as e:
        logger.error(f"Error al restaurar copia de seguridad: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al restaurar copia de seguridad: {str(e)}'
        })
