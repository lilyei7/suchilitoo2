from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import transaction

from accounts.models import Usuario, Sucursal
from dashboard.models_checklist import (
    ChecklistCategory, ChecklistTask, TaskInstance, 
    Evidence, IncidentReport, Notification, IncidentEvidence
)
from dashboard.views.base_views import get_sidebar_context
from dashboard.utils.image_utils import compress_image
from dashboard.decorators import role_required, branch_required

import logging
import datetime

logger = logging.getLogger(__name__)

@login_required
def checklist_dashboard(request):
    """
    Vista principal del dashboard de checklist
    """
    # Obtener fecha actual o la especificada en el filtro
    date_str = request.GET.get('date')
    try:
        if date_str:
            selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            selected_date = timezone.now().date()
    except ValueError:
        selected_date = timezone.now().date()
        messages.warning(request, "Formato de fecha inválido. Mostrando la fecha actual.")
    
    # Obtener sucursal del usuario o la especificada en el filtro
    branch_id = request.GET.get('branch')
    if branch_id and request.user.is_staff:
        try:
            selected_branch = Sucursal.objects.get(id=branch_id, activa=True)
        except Sucursal.DoesNotExist:
            selected_branch = request.user.sucursal
            messages.warning(request, "Sucursal no encontrada. Mostrando tu sucursal asignada.")
    else:
        selected_branch = request.user.sucursal
    
    # Obtener turno seleccionado o predeterminado
    shift = request.GET.get('shift', '')
    if shift not in ['mañana', 'tarde', 'noche']:
        # Determinar turno actual según la hora
        current_hour = timezone.now().hour
        if current_hour < 12:
            shift = 'mañana'
        elif current_hour < 18:
            shift = 'tarde'
        else:
            shift = 'noche'
    
    # Obtener categorías y tareas
    categories = ChecklistCategory.objects.filter(active=True).prefetch_related(
        'tasks'
    ).order_by('order', 'name')
    
    # Obtener instancias de tareas para la fecha, sucursal y turno seleccionados
    task_instances = TaskInstance.objects.filter(
        branch=selected_branch,
        date=selected_date,
        shift=shift
    ).select_related('task', 'task__category', 'performed_by')
    
    # Convertir a diccionario para fácil acceso en la plantilla
    instances_dict = {instance.task_id: instance for instance in task_instances}
    
    # Calcular progreso
    total_tasks = task_instances.count()
    completed_tasks = task_instances.filter(status='completado').count()
    
    if total_tasks > 0:
        progress_percentage = int((completed_tasks / total_tasks) * 100)
    else:
        progress_percentage = 0
    
    # Verificar si hay instancias para esta combinación
    if not task_instances.exists():
        # No hay instancias, mostrar botón para generarlas
        has_instances = False
    else:
        has_instances = True
    
    # Obtener lista de sucursales para el selector (solo para staff)
    branches = Sucursal.objects.filter(activa=True) if request.user.is_staff else []
    
    # Obtener incidentes recientes para esta sucursal
    recent_incidents = IncidentReport.objects.filter(
        branch=selected_branch
    ).order_by('-reported_at')[:5]
    
    # Obtener notificaciones no leídas para el usuario
    unread_notifications = Notification.objects.filter(
        recipient=request.user,
        read=False
    ).order_by('-created_at')[:5]
    
    context = {
        'categories': categories,
        'instances_dict': instances_dict,
        'selected_date': selected_date,
        'selected_branch': selected_branch,
        'shift': shift,
        'has_instances': has_instances,
        'progress_percentage': progress_percentage,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'branches': branches,
        'recent_incidents': recent_incidents,
        'unread_notifications': unread_notifications,
        **get_sidebar_context('checklist_dashboard')
    }
    
    return render(request, 'dashboard/checklist/dashboard.html', context)


@login_required
@require_POST
def generate_task_instances(request):
    """
    Genera instancias de tareas para una fecha, sucursal y turno específicos
    """
    try:
        # Obtener parámetros
        date_str = request.POST.get('date')
        branch_id = request.POST.get('branch')
        shift = request.POST.get('shift')
        
        # Validar parámetros
        if not all([date_str, branch_id, shift]):
            return JsonResponse({
                'success': False,
                'message': 'Todos los campos son requeridos.'
            })
        
        # Convertir fecha
        try:
            task_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Formato de fecha inválido.'
            })
        
        # Obtener sucursal
        try:
            branch = Sucursal.objects.get(id=branch_id)
        except Sucursal.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Sucursal no encontrada.'
            })
        
        # Validar turno
        if shift not in ['mañana', 'tarde', 'noche']:
            return JsonResponse({
                'success': False,
                'message': 'Turno inválido.'
            })
        
        # Verificar si ya existen instancias para esta combinación
        existing_instances = TaskInstance.objects.filter(
            branch=branch,
            date=task_date,
            shift=shift
        )
        
        if existing_instances.exists():
            return JsonResponse({
                'success': False,
                'message': f'Ya existen tareas para esta sucursal, fecha y turno. ({existing_instances.count()} tareas)'
            })
        
        # Obtener todas las tareas activas
        active_tasks = ChecklistTask.objects.filter(active=True)
        
        # Crear instancias de tareas
        with transaction.atomic():
            instances_created = 0
            for task in active_tasks:
                TaskInstance.objects.create(
                    task=task,
                    branch=branch,
                    date=task_date,
                    shift=shift,
                    status='pendiente'
                )
                instances_created += 1
            
            # Crear notificaciones para usuarios según roles
            for task in active_tasks:
                if task.default_role:
                    users_to_notify = Usuario.objects.filter(
                        sucursal=branch,
                        rol=task.default_role,
                        is_active=True
                    )
                    
                    for user in users_to_notify:
                        Notification.objects.create(
                            type='task_created',
                            recipient=user,
                            title='Nueva tarea asignada',
                            message=f'Se ha creado una nueva tarea "{task.title}" para {branch.nombre}, turno {shift}, fecha {task_date}.'
                        )
        
        return JsonResponse({
            'success': True,
            'message': f'Se han generado {instances_created} tareas exitosamente.',
            'redirect': f'/dashboard/checklist/?date={date_str}&branch={branch_id}&shift={shift}'
        })
        
    except Exception as e:
        logger.error(f"Error al generar instancias de tareas: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@require_POST
def complete_task(request, instance_id):
    """
    Marca una instancia de tarea como completada
    """
    try:
        instance = get_object_or_404(TaskInstance, id=instance_id)
        
        # Verificar si la tarea ya está completada
        if instance.status == 'completado':
            return JsonResponse({
                'success': False,
                'message': 'Esta tarea ya ha sido completada.'
            })
        
        # Verificar si la tarea requiere evidencia
        if instance.task.requires_evidence and not instance.evidence_files.exists():
            return JsonResponse({
                'success': False,
                'message': 'Esta tarea requiere evidencia antes de ser completada.'
            })
        
        # Actualizar la instancia
        instance.status = 'completado'
        instance.performed_by = request.user
        instance.performed_at = timezone.now()
        instance.save()
        
        # Crear notificación para supervisores
        supervisors = Usuario.objects.filter(
            sucursal=instance.branch,
            rol__nombre__in=['admin', 'gerente', 'supervisor'],
            is_active=True
        )
        
        for supervisor in supervisors:
            if supervisor != request.user:  # No notificar a quien completó la tarea
                Notification.objects.create(
                    type='task_completed',
                    recipient=supervisor,
                    title='Tarea completada',
                    message=f'{request.user.get_full_name()} ha completado la tarea "{instance.task.title}" en {instance.branch.nombre}.',
                    related_task=instance
                )
        
        # Recalcular progreso
        total_tasks = TaskInstance.objects.filter(
            branch=instance.branch,
            date=instance.date,
            shift=instance.shift
        ).count()
        
        completed_tasks = TaskInstance.objects.filter(
            branch=instance.branch,
            date=instance.date,
            shift=instance.shift,
            status='completado'
        ).count()
        
        if total_tasks > 0:
            progress_percentage = int((completed_tasks / total_tasks) * 100)
        else:
            progress_percentage = 0
        
        return JsonResponse({
            'success': True,
            'message': 'Tarea completada exitosamente.',
            'progress': progress_percentage,
            'completed': completed_tasks,
            'total': total_tasks
        })
        
    except Exception as e:
        logger.error(f"Error al completar tarea: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@require_POST
def upload_evidence(request, instance_id):
    """
    Sube una evidencia para una instancia de tarea
    """
    try:
        logger.info(f"Upload evidence request for instance {instance_id}")
        logger.info(f"Files in request: {request.FILES}")
        logger.info(f"POST data: {request.POST}")
        
        instance = get_object_or_404(TaskInstance, id=instance_id)
        
        # Verificar si hay un archivo en la solicitud
        if 'evidence_file' not in request.FILES:
            logger.error("No file found in request")
            return JsonResponse({
                'success': False,
                'message': 'No se ha proporcionado ningún archivo.'
            })
        
        file = request.FILES['evidence_file']
        
        # Validar tamaño del archivo (5MB máximo)
        if file.size > 5 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'message': 'El archivo excede el tamaño máximo permitido (5MB).'
            })
        
        # Validar tipo de archivo
        allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
        if file.content_type not in allowed_types:
            return JsonResponse({
                'success': False,
                'message': 'Tipo de archivo no permitido. Se permiten jpg, png y pdf.'
            })
        
        comment = request.POST.get('comment', '')
        
        # Comprimir la imagen si es un tipo de imagen
        if file.content_type in ['image/jpeg', 'image/png']:
            file = compress_image(file)
            
        # Crear la evidencia
        evidence = Evidence.objects.create(
            instance=instance,
            uploaded_by=request.user,
            file=file,
            comment=comment
        )
        
        # Crear notificación para supervisores
        supervisors = Usuario.objects.filter(
            sucursal=instance.branch,
            rol__nombre__in=['admin', 'gerente', 'supervisor'],
            is_active=True
        )
        
        for supervisor in supervisors:
            if supervisor != request.user:  # No notificar a quien subió la evidencia
                Notification.objects.create(
                    type='evidence_uploaded',
                    recipient=supervisor,
                    title='Nueva evidencia subida',
                    message=f'{request.user.get_full_name()} ha subido evidencia para la tarea "{instance.task.title}" en {instance.branch.nombre}.',
                    related_task=instance
                )
        
        return JsonResponse({
            'success': True,
            'message': 'Evidencia subida exitosamente.',
            'evidence_id': evidence.id,
            'can_complete': True
        })
        
    except Exception as e:
        logger.error(f"Error al subir evidencia: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@require_POST
def bulk_complete_tasks(request):
    """
    Marca múltiples tareas como completadas en una sola operación
    """
    try:
        # Obtener parámetros
        date_str = request.POST.get('date')
        branch_id = request.POST.get('branch')
        shift = request.POST.get('shift')
        
        # Validar parámetros
        if not all([date_str, branch_id, shift]):
            return JsonResponse({
                'success': False,
                'message': 'Todos los campos son requeridos.'
            })
        
        # Convertir fecha
        try:
            task_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Formato de fecha inválido.'
            })
        
        # Obtener sucursal
        try:
            branch = Sucursal.objects.get(id=branch_id)
        except Sucursal.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Sucursal no encontrada.'
            })
        
        # Validar turno
        if shift not in ['mañana', 'tarde', 'noche']:
            return JsonResponse({
                'success': False,
                'message': 'Turno inválido.'
            })
        
        # Obtener tareas pendientes que no requieren evidencia
        pending_tasks = TaskInstance.objects.filter(
            branch=branch,
            date=task_date,
            shift=shift,
            status='pendiente',
            task__requires_evidence=False  # Solo las que no requieren evidencia
        )
        
        if not pending_tasks.exists():
            return JsonResponse({
                'success': False,
                'message': 'No hay tareas pendientes que puedan ser completadas automáticamente.'
            })
        
        # Marcar todas como completadas
        with transaction.atomic():
            for instance in pending_tasks:
                instance.status = 'completado'
                instance.performed_by = request.user
                instance.performed_at = timezone.now()
                instance.save()
        
        # Recalcular progreso
        total_tasks = TaskInstance.objects.filter(
            branch=branch,
            date=task_date,
            shift=shift
        ).count()
        
        completed_tasks = TaskInstance.objects.filter(
            branch=branch,
            date=task_date,
            shift=shift,
            status='completado'
        ).count()
        
        if total_tasks > 0:
            progress_percentage = int((completed_tasks / total_tasks) * 100)
        else:
            progress_percentage = 0
        
        return JsonResponse({
            'success': True,
            'message': f'Se han completado {pending_tasks.count()} tareas exitosamente.',
            'progress': progress_percentage,
            'completed': completed_tasks,
            'total': total_tasks
        })
        
    except Exception as e:
        logger.error(f"Error al completar tareas en masa: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@login_required
@branch_required
def incident_list(request):
    """
    Lista de incidentes reportados
    """
    # Filtros
    branch_id = request.GET.get('branch')
    status = request.GET.get('status')
    category = request.GET.get('category')
    date_range = request.GET.get('date_range')
    
    # Base de consulta
    incidents = IncidentReport.objects.all()
    
    # Aplicar filtros
    if branch_id:
        try:
            branch = Sucursal.objects.get(id=branch_id)
            incidents = incidents.filter(branch=branch)
        except Sucursal.DoesNotExist:
            messages.warning(request, "Sucursal no encontrada. Mostrando todos los incidentes.")
    
    if status and status in dict(IncidentReport.STATUS_CHOICES):
        incidents = incidents.filter(status=status)
    
    if category and category in dict(IncidentReport.CATEGORY_CHOICES):
        incidents = incidents.filter(category=category)
    
    # Filtro por fecha
    if date_range:
        today = timezone.now().date()
        if date_range == 'today':
            incidents = incidents.filter(reported_at__date=today)
        elif date_range == 'week':
            start_of_week = today - datetime.timedelta(days=today.weekday())
            end_of_week = start_of_week + datetime.timedelta(days=6)
            incidents = incidents.filter(reported_at__date__range=[start_of_week, end_of_week])
        elif date_range == 'month':
            start_of_month = today.replace(day=1)
            next_month = (today.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
            end_of_month = next_month - datetime.timedelta(days=1)
            incidents = incidents.filter(reported_at__date__range=[start_of_month, end_of_month])
    
    # Restringir a la sucursal del usuario si no es staff
    if not request.user.is_staff and not request.user.rol.nombre in ['admin', 'gerente']:
        incidents = incidents.filter(branch=request.user.sucursal)
    
    # Ordenar por fecha de reporte (más recientes primero)
    incidents = incidents.order_by('-reported_at')
    
    # Obtener sucursales para el filtro (solo staff y roles administrativos)
    user_is_admin = request.user.is_staff or request.user.rol.nombre in ['admin', 'gerente']
    branches = Sucursal.objects.filter(activa=True) if user_is_admin else []
    
    # Filtrar incidentes por estado para las pestañas
    open_incidents = incidents.filter(status='abierto')
    in_process_incidents = incidents.filter(status='en_proceso')
    closed_incidents = incidents.filter(status='cerrado')
    assigned_to_me = incidents.filter(assigned_to=request.user)
    
    # Contadores
    open_count = open_incidents.count()
    in_process_count = in_process_incidents.count()
    closed_count = closed_incidents.count()
    assigned_to_me_count = assigned_to_me.count()
    
    # Datos para los filtros seleccionados
    selected_filters = {
        'branch': branch_id,
        'status': status,
        'category': category,
        'date_range': date_range
    }
    
    context = {
        'incidents': incidents,
        'open_incidents': open_incidents,
        'in_process_incidents': in_process_incidents,
        'closed_incidents': closed_incidents,
        'assigned_to_me': assigned_to_me,
        'branches': branches,
        'status_choices': IncidentReport.STATUS_CHOICES,
        'category_choices': IncidentReport.CATEGORY_CHOICES,
        'open_count': open_count,
        'in_process_count': in_process_count,
        'closed_count': closed_count,
        'assigned_to_me_count': assigned_to_me_count,
        'selected_filters': selected_filters,
        'user_is_admin': user_is_admin,
        'closed_incidents': closed_incidents,
        'selected_branch': branch_id,
        'selected_status': status,
        'selected_category': category,
        **get_sidebar_context('checklist_incidents')
    }
    
    return render(request, 'dashboard/checklist/incident_list.html', context)


@login_required
@require_POST
def report_incident(request):
    """
    Reporta un nuevo incidente
    """
    try:
        # Obtener datos del formulario
        branch_id = request.POST.get('branch')
        category = request.POST.get('category')
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        # Validar datos
        if not all([branch_id, category, title, description]):
            return JsonResponse({
                'success': False,
                'message': 'Todos los campos son requeridos.'
            })
        
        # Validar categoría
        if category not in dict(IncidentReport.CATEGORY_CHOICES):
            return JsonResponse({
                'success': False,
                'message': 'Categoría no válida.'
            })
        
        # Obtener sucursal
        try:
            branch = Sucursal.objects.get(id=branch_id)
        except Sucursal.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Sucursal no encontrada.'
            })
        
        # Crear el incidente
        incident = IncidentReport.objects.create(
            branch=branch,
            category=category,
            title=title,
            description=description,
            reported_by=request.user,
            status='abierto'
        )
        
        # Notificar a los usuarios de mantenimiento y gerentes
        maintenance_staff = Usuario.objects.filter(
            Q(rol__nombre='mantenimiento') | Q(rol__nombre='gerente'),
            is_active=True
        )
        
        for user in maintenance_staff:
            Notification.objects.create(
                type='incident_reported',
                recipient=user,
                title='Nuevo incidente reportado',
                message=f'{request.user.get_full_name()} ha reportado un incidente en {branch.nombre}: {title}',
                related_incident=incident
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Incidente reportado exitosamente.',
            'incident_id': incident.id
        })
        
    except Exception as e:
        logger.error(f"Error al reportar incidente: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@branch_required
@require_POST
def update_incident_status(request, incident_id):
    """
    Actualiza el estado de un incidente
    """
    try:
        incident = get_object_or_404(IncidentReport, id=incident_id)
        
        # Verificar permisos: solo el asignado, mantenimiento, supervisores o gerentes pueden cambiar el estado
        is_authorized = (
            request.user.is_staff or
            request.user == incident.assigned_to or
            incident.branch == request.user.sucursal and
            request.user.rol and request.user.rol.nombre in ['admin', 'mantenimiento', 'gerente', 'supervisor']
        )
        
        if not is_authorized:
            return JsonResponse({
                'success': False,
                'message': 'No tienes permiso para cambiar el estado de este incidente.'
            })
        
        # Obtener nuevo estado
        new_status = request.POST.get('status')
        resolution_note = request.POST.get('resolution_note', '')
        
        # Validar estado
        if new_status not in dict(IncidentReport.STATUS_CHOICES):
            return JsonResponse({
                'success': False,
                'message': 'Estado no válido.'
            })
        
        # Validar nota de resolución para incidentes cerrados
        if new_status == 'cerrado' and not resolution_note:
            return JsonResponse({
                'success': False,
                'message': 'Se requiere una nota de resolución para cerrar el incidente.'
            })
        
        # Actualizar el incidente
        old_status = incident.status
        incident.status = new_status
        
        # Si se está cerrando, registrar fecha de resolución
        if new_status == 'cerrado' and old_status != 'cerrado':
            incident.resolved_at = timezone.now()
            incident.resolution_note = resolution_note
        
        # Si se está asignando a alguien
        assigned_to_id = request.POST.get('assigned_to')
        if assigned_to_id:
            try:
                assigned_to = Usuario.objects.get(id=assigned_to_id)
                incident.assigned_to = assigned_to
                
                # Notificar al asignado
                Notification.objects.create(
                    type='incident_updated',
                    recipient=assigned_to,
                    title='Incidente asignado',
                    message=f'{request.user.get_full_name()} te ha asignado un incidente: {incident.title}',
                    related_incident=incident
                )
            except Usuario.DoesNotExist:
                pass
        
        incident.save()
        
        # Notificar al reportante si el incidente se cerró
        if new_status == 'cerrado' and old_status != 'cerrado' and incident.reported_by:
            Notification.objects.create(
                type='incident_resolved',
                recipient=incident.reported_by,
                title='Incidente resuelto',
                message=f'Tu incidente "{incident.title}" ha sido resuelto.',
                related_incident=incident
            )
        
        return JsonResponse({
            'success': True,
            'message': f'Estado actualizado a {dict(IncidentReport.STATUS_CHOICES)[new_status]}.'
        })
        
    except Exception as e:
        logger.error(f"Error al actualizar estado de incidente: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
def notifications_list(request):
    """
    Lista de notificaciones del usuario
    """
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')
    
    context = {
        'notifications': notifications,
        **get_sidebar_context('checklist')
    }
    
    return render(request, 'dashboard/checklist/notifications.html', context)


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """
    Marca una notificación como leída
    """
    try:
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.read = True
        notification.save()
        
        return JsonResponse({
            'success': True
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
@require_POST
def mark_all_notifications_read(request):
    """
    Marca todas las notificaciones del usuario como leídas
    """
    try:
        Notification.objects.filter(recipient=request.user, read=False).update(read=True)
        
        return JsonResponse({
            'success': True,
            'message': 'Todas las notificaciones marcadas como leídas.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
@require_POST
def upload_incident_evidence(request, incident_id):
    """
    Sube una evidencia para un incidente
    """
    try:
        # Obtener el incidente
        try:
            incident = IncidentReport.objects.get(id=incident_id)
        except IncidentReport.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Incidente no encontrado.'
            })
        
        # Verificar permisos
        if not request.user.is_staff and request.user.sucursal != incident.branch:
            return JsonResponse({
                'success': False,
                'message': 'No tienes permiso para agregar evidencia a este incidente.'
            })
        
        # Verificar que se haya subido un archivo
        if 'evidence_file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'message': 'No se ha proporcionado ningún archivo.'
            })
        
        # Obtener datos del formulario
        file = request.FILES['evidence_file']
        comment = request.POST.get('comment', '')
        
        # Validar que el archivo sea una imagen o un PDF
        if not (file.content_type.startswith('image/') or file.content_type == 'application/pdf'):
            return JsonResponse({
                'success': False,
                'message': 'El archivo debe ser una imagen (JPEG, PNG) o un PDF.'
            })
        
        # Verificar tamaño máximo (5 MB)
        if file.size > 5 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'message': 'El archivo no debe superar los 5 MB.'
            })
        
        # Comprimir la imagen si es necesario
        if file.content_type.startswith('image/'):
            file = compress_image(file)
        
        # Crear la evidencia
        evidence = IncidentEvidence.objects.create(
            incident=incident,
            uploaded_by=request.user,
            file=file,
            comment=comment
        )
        
        # Actualizar flag de evidencia en el incidente
        if not incident.has_evidence:
            incident.has_evidence = True
            incident.save(update_fields=['has_evidence'])
        
        # Crear notificación para los administradores y supervisores
        managers = Usuario.objects.filter(
            Q(sucursal=incident.branch) | Q(is_staff=True),
            rol__nombre__in=['admin', 'gerente', 'supervisor'],
            is_active=True
        ).distinct()
        
        for manager in managers:
            if manager != request.user:  # No notificar a quien subió la evidencia
                Notification.objects.create(
                    type='evidence_uploaded',
                    recipient=manager,
                    title='Nueva evidencia de incidente',
                    message=f'{request.user.get_full_name()} ha subido evidencia para el incidente "{incident.title}" en {incident.branch.nombre}.',
                    related_incident=incident
                )
        
        return JsonResponse({
            'success': True,
            'message': 'Evidencia subida correctamente.',
            'evidence_id': evidence.id,
            'file_url': evidence.file.url
        })
        
    except Exception as e:
        logger.error(f"Error al subir evidencia de incidente: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@branch_required
def incident_detail(request, incident_id):
    """
    Vista detallada de un incidente específico
    """
    # Obtener el incidente con sus relaciones
    incident = get_object_or_404(IncidentReport, id=incident_id)
    
    # Verificar permisos según el rol y la sucursal
    user_is_admin = request.user.is_staff or request.user.rol.nombre in ['admin', 'gerente']
    user_is_supervisor = request.user.rol.nombre == 'supervisor'
    user_is_reporter = request.user == incident.reported_by
    user_is_assigned = request.user == incident.assigned_to
    user_in_same_branch = request.user.sucursal == incident.branch
    
    # Si no es admin y no pertenece a la sucursal, no tiene acceso
    if not user_is_admin and not user_in_same_branch and not user_is_assigned:
        messages.error(request, "No tienes permiso para ver este incidente.")
        return redirect('dashboard:checklist_incidents')
    
    # Si es supervisor pero no es el que reportó ni está asignado, no tiene acceso
    if user_is_supervisor and not user_is_reporter and not user_is_assigned and not user_is_admin:
        messages.error(request, "No tienes permiso para ver este incidente.")
        return redirect('dashboard:checklist_incidents')
    
    # Obtener lista de usuarios para asignación (sólo roles relevantes)
    if user_is_admin or user_is_supervisor:
        users = Usuario.objects.filter(
            Q(sucursal=incident.branch) | Q(is_staff=True),
            Q(rol__nombre__in=['admin', 'gerente', 'supervisor', 'jefe_cocina']) | Q(is_staff=True),
            is_active=True
        ).distinct().order_by('first_name', 'last_name')
    else:
        users = []
    
    context = {
        'incident': incident,
        'users': users,
        **get_sidebar_context('checklist_incidents')
    }
    
    return render(request, 'dashboard/checklist/incident_detail.html', context)
