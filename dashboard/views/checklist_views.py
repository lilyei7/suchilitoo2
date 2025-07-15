from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import transaction

from accounts.models import Usuario, Sucursal, Rol
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
                            message=f'Se ha creado una nueva tarea "{task.title}" para {branch.nombre}, turno {shift}, fecha {task_date}.',
                            alert_type='info',
                            icon='clipboard-check'
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
                    related_task=instance,
                    alert_type='success',
                    icon='check-circle'
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
                    related_task=instance,
                    alert_type='info',
                    icon='camera'
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
def report_incident(request):
    """
    Reporta un nuevo incidente o muestra el formulario de reporte
    """
    # Si es GET, mostrar el formulario
    if request.method == 'GET':
        # Obtener sucursales para el selector
        if request.user.is_staff:
            branches = Sucursal.objects.filter(activa=True).order_by('nombre')
        else:
            branches = Sucursal.objects.filter(id=request.user.sucursal.id) if request.user.sucursal else Sucursal.objects.none()
        
        context = {
            'branches': branches,
            'category_choices': IncidentReport.CATEGORY_CHOICES,
            **get_sidebar_context('checklist_incidents')
        }
        return render(request, 'dashboard/checklist/report_incident.html', context)
    
    # Si es POST, procesar el formulario
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
        except (Sucursal.DoesNotExist, ValueError):
            return JsonResponse({
                'success': False,
                'message': 'Sucursal no encontrada o inválida.'
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
                related_incident=incident,
                alert_type='warning',
                icon='exclamation-triangle',
                link=f'/dashboard/checklist/incidente/{incident.id}/'
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
                    related_incident=incident,
                    alert_type='info',
                    icon='user-check',
                    link=f'/dashboard/checklist/incidente/{incident.id}/'
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
                related_incident=incident,
                alert_type='success',
                icon='check-circle',
                link=f'/dashboard/checklist/incidente/{incident.id}/'
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
    # Obtener todas las notificaciones del usuario
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')
    
    # Marcar como leídas si se solicita
    mark_read = request.GET.get('mark_read')
    if mark_read == 'all':
        Notification.objects.filter(recipient=request.user, read=False).update(read=True)
        messages.success(request, "Todas las notificaciones han sido marcadas como leídas.")
        return redirect('dashboard:notificaciones')
    
    # Filtrar por estado de lectura si se especifica
    read_filter = request.GET.get('read')
    if read_filter == 'unread':
        notifications = notifications.filter(read=False)
    elif read_filter == 'read':
        notifications = notifications.filter(read=True)
    
    # Filtrar por tipo si se especifica
    tipo_filter = request.GET.get('tipo')
    if tipo_filter and tipo_filter in dict(Notification.TYPE_CHOICES):
        notifications = notifications.filter(type=tipo_filter)
    
    context = {
        'notifications': notifications,
        'read_filter': read_filter,
        'tipo_filter': tipo_filter,
        'tipos_notificacion': Notification.TYPE_CHOICES,
        **get_sidebar_context('checklist')
    }
    
    return render(request, 'dashboard/checklist/notifications.html', context)


@login_required
@require_POST
def mark_notification_read(request):
    """
    Marca una notificación como leída (AJAX)
    """
    try:
        notification_id = request.POST.get('notification_id')
        if not notification_id:
            return JsonResponse({'success': False, 'message': 'ID de notificación no proporcionado'})
        
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.marcar_como_leida()
        
        return JsonResponse({
            'success': True, 
            'message': 'Notificación marcada como leída',
            'unread_count': Notification.objects.filter(recipient=request.user, read=False).count()
        })
    
    except Exception as e:
        logger.error(f"Error al marcar notificación como leída: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


@login_required
@require_POST
def delete_notification(request):
    """
    Elimina una notificación (AJAX)
    """
    try:
        notification_id = request.POST.get('notification_id')
        if not notification_id:
            return JsonResponse({'success': False, 'message': 'ID de notificación no proporcionado'})
        
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.delete()
        
        return JsonResponse({
            'success': True, 
            'message': 'Notificación eliminada',
            'unread_count': Notification.objects.filter(recipient=request.user, read=False).count()
        })
    
    except Exception as e:
        logger.error(f"Error al eliminar notificación: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


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
        
        # Verificar que se haya subido al menos un archivo
        if 'evidence_files' not in request.FILES:
            return JsonResponse({
                'success': False,
                'message': 'No se ha proporcionado ningún archivo.'
            })
        
        # Obtener datos del formulario
        files = request.FILES.getlist('evidence_files')
        
        # Verificar que la lista de archivos no esté vacía
        if not files:
            return JsonResponse({
                'success': False,
                'message': 'No se ha proporcionado ningún archivo válido.'
            })
            
        comment = request.POST.get('comment', '')
        
        # Limitar a un máximo de 3 archivos
        if len(files) > 3:
            return JsonResponse({
                'success': False,
                'message': 'Solo se permiten un máximo de 3 archivos por subida.'
            })
        
        # Validar cada archivo
        for file in files:
            # Validar que el archivo sea una imagen o un PDF
            if not (file.content_type.startswith('image/') or file.content_type == 'application/pdf'):
                return JsonResponse({
                    'success': False,
                    'message': 'Los archivos deben ser imágenes (JPEG, PNG) o PDF.'
                })
            
            # Verificar tamaño máximo (5 MB)
            if file.size > 5 * 1024 * 1024:
                return JsonResponse({
                    'success': False,
                    'message': 'Cada archivo no debe superar los 5 MB.'
                })
        
        # Procesar y guardar cada archivo
        from dashboard.utils.image_utils import compress_image
        
        evidence_files = []
        for file in files:
            # Comprimir la imagen si es necesario
            processed_file = file
            if file and file.content_type and file.content_type.startswith('image/'):
                processed_file = compress_image(file)
                # Si la compresión falló, usar el archivo original
                if processed_file is None:
                    processed_file = file
            
            # Crear la evidencia
            evidence = IncidentEvidence.objects.create(
                incident=incident,
                uploaded_by=request.user,
                file=processed_file,
                comment=comment
            )
            evidence_files.append(evidence)
        
        # Crear notificación para los administradores y supervisores
        managers = Usuario.objects.filter(
            Q(sucursal=incident.branch) | Q(is_staff=True),
            Q(rol__nombre__in=['admin', 'gerente', 'supervisor']) | Q(is_staff=True),
            is_active=True
        ).distinct()
        
        for manager in managers:
            if manager != request.user:  # No notificar a quien subió la evidencia
                Notification.objects.create(
                    type='evidence_uploaded',
                    recipient=manager,
                    title='Nueva evidencia de incidente',
                    message=f'{request.user.get_full_name()} ha subido {len(files)} evidencia(s) para el incidente "{incident.title}" en {incident.branch.nombre}.',
                    related_incident=incident,
                    alert_type='info',
                    icon='camera',
                    link=f'/dashboard/checklist/incidente/{incident.id}/'
                )
        
        return JsonResponse({
            'success': True,
            'message': f'Se han subido {len(files) if files else 0} evidencia(s) correctamente.',
            'evidence_count': len(files) if files else 0
        })
        
    except Exception as e:
        logger.error(f"Error al subir evidencia de incidente: {str(e)}")
        import traceback
        traceback.print_exc()
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
    user_is_admin = request.user.is_staff
    if hasattr(request.user, 'rol') and request.user.rol:
        user_is_admin = user_is_admin or request.user.rol.nombre in ['admin', 'gerente']
        user_is_supervisor = request.user.rol.nombre == 'supervisor'
    else:
        user_is_supervisor = False
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


@login_required
def mark_all_notifications_read(request):
    """
    Marca todas las notificaciones como leídas y redirecciona
    """
    Notification.objects.filter(recipient=request.user, read=False).update(read=True)
    messages.success(request, "Todas las notificaciones han sido marcadas como leídas.")
    
    # Redireccionar a la URL de referencia o a la lista de notificaciones
    redirect_url = request.META.get('HTTP_REFERER', 'dashboard:notificaciones')
    return redirect(redirect_url)


@login_required
@role_required(['admin', 'gerente'])
def manage_categories(request):
    """
    Vista para gestionar las categorías de checklist
    """
    categories = ChecklistCategory.objects.all().order_by('order', 'name')
    
    context = {
        'categories': categories,
        **get_sidebar_context('checklist_categories')
    }
    
    return render(request, 'dashboard/checklist/manage_categories.html', context)


@login_required
@role_required(['admin', 'gerente'])
def create_category(request):
    """
    Crea una nueva categoría de checklist
    """
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            name = request.POST.get('name')
            order = request.POST.get('order', 0)
            
            # Validar datos
            if not name:
                return JsonResponse({
                    'success': False,
                    'message': 'El nombre de la categoría es requerido.'
                })
            
            try:
                order = int(order)
            except ValueError:
                order = 0
            
            # Crear la categoría
            category = ChecklistCategory.objects.create(
                name=name,
                order=order,
                active=True
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Categoría creada exitosamente.',
                'category_id': category.id,
                'category_name': category.name
            })
            
        except Exception as e:
            logger.error(f"Error al crear categoría: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    # Si no es POST, redirigir a la página de gestión
    return redirect('dashboard:manage_categories')


@login_required
@role_required(['admin', 'gerente'])
def edit_category(request, category_id):
    """
    Edita una categoría existente
    """
    # Obtener la categoría
    category = get_object_or_404(ChecklistCategory, id=category_id)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            name = request.POST.get('name')
            order = request.POST.get('order', category.order)
            active = request.POST.get('active') == 'on'
            
            # Validar datos
            if not name:
                return JsonResponse({
                    'success': False,
                    'message': 'El nombre de la categoría es requerido.'
                })
            
            try:
                order = int(order)
            except ValueError:
                order = category.order
            
            # Actualizar la categoría
            category.name = name
            category.order = order
            category.active = active
            category.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Categoría actualizada exitosamente.',
                'category_id': category.id,
                'category_name': category.name,
                'category_order': category.order,
                'category_active': category.active
            })
            
        except Exception as e:
            logger.error(f"Error al actualizar categoría: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    # Si es GET, mostrar formulario
    context = {
        'category': category,
        **get_sidebar_context('checklist_categories')
    }
    
    return render(request, 'dashboard/checklist/edit_category.html', context)


@login_required
@role_required(['admin', 'gerente'])
@require_POST
def delete_category(request, category_id):
    """
    Elimina una categoría (solo si no tiene tareas asociadas)
    """
    try:
        category = get_object_or_404(ChecklistCategory, id=category_id)
        
        # Verificar si tiene tareas
        if category.tasks.exists():
            return JsonResponse({
                'success': False,
                'message': 'No se puede eliminar la categoría porque tiene tareas asociadas. Desactívela en su lugar.'
            })
        
        # Eliminar la categoría
        category_name = category.name
        category.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Categoría "{category_name}" eliminada exitosamente.'
        })
        
    except Exception as e:
        logger.error(f"Error al eliminar categoría: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@role_required(['admin', 'gerente'])
def manage_tasks(request):
    """
    Vista para gestionar las tareas de checklist
    """
    # Obtener parámetros de filtro
    category_id = request.GET.get('category')
    active_only = request.GET.get('active', 'true') == 'true'
    
    # Base de consulta
    tasks = ChecklistTask.objects.select_related('category', 'default_role')
    
    # Aplicar filtros
    if category_id:
        try:
            category = ChecklistCategory.objects.get(id=category_id)
            tasks = tasks.filter(category=category)
        except ChecklistCategory.DoesNotExist:
            pass
    
    if active_only:
        tasks = tasks.filter(active=True)
    
    # Ordenar tareas
    tasks = tasks.order_by('category__order', 'category__name', 'title')
    
    # Obtener categorías para el filtro
    categories = ChecklistCategory.objects.filter(active=True).order_by('order', 'name')
    
    # Obtener roles para el selector
    roles = Rol.objects.all().order_by('nombre')
    
    context = {
        'tasks': tasks,
        'categories': categories,
        'roles': roles,
        'selected_category': category_id,
        'active_only': active_only,
        **get_sidebar_context('checklist_tasks')
    }
    
    return render(request, 'dashboard/checklist/manage_tasks.html', context)


@login_required
@role_required(['admin', 'gerente'])
def create_task(request):
    """
    Crea una nueva tarea de checklist
    """
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            title = request.POST.get('title')
            description = request.POST.get('description', '')
            category_id = request.POST.get('category')
            requires_evidence = request.POST.get('requires_evidence') == 'on'
            default_role_id = request.POST.get('default_role')
            
            # Validar datos
            if not title or not category_id:
                return JsonResponse({
                    'success': False,
                    'message': 'El título y la categoría son requeridos.'
                })
            
            # Obtener categoría
            try:
                category = ChecklistCategory.objects.get(id=category_id)
            except ChecklistCategory.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'La categoría seleccionada no existe.'
                })
            
            # Obtener rol predeterminado (opcional)
            default_role = None
            if default_role_id:
                try:
                    default_role = Rol.objects.get(id=default_role_id)
                except Rol.DoesNotExist:
                    pass
            
            # Crear la tarea
            task = ChecklistTask.objects.create(
                title=title,
                description=description,
                category=category,
                requires_evidence=requires_evidence,
                default_role=default_role,
                active=True
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Tarea creada exitosamente.',
                'task_id': task.id,
                'task_title': task.title
            })
            
        except Exception as e:
            logger.error(f"Error al crear tarea: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    # Si no es POST, redirigir a la página de gestión
    return redirect('dashboard:manage_tasks')


@login_required
@role_required(['admin', 'gerente'])
def edit_task(request, task_id):
    """
    Edita una tarea existente
    """
    # Obtener la tarea
    task = get_object_or_404(ChecklistTask, id=task_id)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            title = request.POST.get('title')
            description = request.POST.get('description', '')
            category_id = request.POST.get('category')
            requires_evidence = request.POST.get('requires_evidence') == 'on'
            default_role_id = request.POST.get('default_role')
            active = request.POST.get('active') == 'on'
            
            # Validar datos
            if not title or not category_id:
                return JsonResponse({
                    'success': False,
                    'message': 'El título y la categoría son requeridos.'
                })
            
            # Obtener categoría
            try:
                category = ChecklistCategory.objects.get(id=category_id)
            except ChecklistCategory.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'La categoría seleccionada no existe.'
                })
            
            # Obtener rol predeterminado (opcional)
            default_role = None
            if default_role_id:
                try:
                    default_role = Rol.objects.get(id=default_role_id)
                except Rol.DoesNotExist:
                    pass
            
            # Actualizar la tarea
            task.title = title
            task.description = description
            task.category = category
            task.requires_evidence = requires_evidence
            task.default_role = default_role
            task.active = active
            task.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Tarea actualizada exitosamente.',
                'task_id': task.id,
                'task_title': task.title
            })
            
        except Exception as e:
            logger.error(f"Error al actualizar tarea: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    # Si es GET, mostrar formulario
    categories = ChecklistCategory.objects.filter(active=True).order_by('order', 'name')
    roles = Rol.objects.all().order_by('nombre')
    
    context = {
        'task': task,
        'categories': categories,
        'roles': roles,
        **get_sidebar_context('checklist_tasks')
    }
    
    return render(request, 'dashboard/checklist/edit_task.html', context)


@login_required
@role_required(['admin', 'gerente'])
@require_POST
def delete_task(request, task_id):
    """
    Elimina una tarea (solo si no tiene instancias asociadas)
    """
    try:
        task = get_object_or_404(ChecklistTask, id=task_id)
        
        # Verificar si tiene instancias
        if task.instances.exists():
            return JsonResponse({
                'success': False,
                'message': 'No se puede eliminar la tarea porque tiene instancias asociadas. Desactívela en su lugar.'
            })
        
        # Eliminar la tarea
        task_title = task.title
        task.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Tarea "{task_title}" eliminada exitosamente.'
        })
        
    except Exception as e:
        logger.error(f"Error al eliminar tarea: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@role_required(['admin', 'gerente', 'supervisor'])
def task_history(request):
    """
    Historial de tareas completadas con posibilidad de filtrado
    """
    # Obtener parámetros de filtro
    branch_id = request.GET.get('branch')
    category_id = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')
    
    # Base de consulta con joins optimizados
    task_instances = TaskInstance.objects.select_related(
        'task', 'task__category', 'branch', 'performed_by'
    ).prefetch_related('evidence_files')
    
    # Aplicar filtros
    if branch_id:
        try:
            branch = Sucursal.objects.get(id=branch_id)
            task_instances = task_instances.filter(branch=branch)
        except Sucursal.DoesNotExist:
            messages.warning(request, "Sucursal no encontrada.")
    
    if category_id:
        try:
            category = ChecklistCategory.objects.get(id=category_id)
            task_instances = task_instances.filter(task__category=category)
        except ChecklistCategory.DoesNotExist:
            messages.warning(request, "Categoría no encontrada.")
    
    # Filtro por fecha
    if start_date:
        try:
            start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            task_instances = task_instances.filter(date__gte=start)
        except ValueError:
            messages.warning(request, "Formato de fecha inicial inválido.")
    
    if end_date:
        try:
            end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            task_instances = task_instances.filter(date__lte=end)
        except ValueError:
            messages.warning(request, "Formato de fecha final inválido.")
    
    # Filtro por estado
    if status in ['pendiente', 'completado']:
        task_instances = task_instances.filter(status=status)
    
    # Limitar según permisos del usuario
    if not request.user.is_staff and request.user.rol.nombre not in ['admin', 'gerente']:
        # Si no es admin o gerente, solo puede ver su sucursal
        if request.user.sucursal:
            task_instances = task_instances.filter(branch=request.user.sucursal)
        else:
            task_instances = TaskInstance.objects.none()
    
    # Ordenar por fecha (más recientes primero) y otros campos
    task_instances = task_instances.order_by('-date', '-performed_at', 'shift', 'task__category__order', 'task__title')
    
    # Obtener sucursales para el filtro
    if request.user.is_staff or request.user.rol.nombre in ['admin', 'gerente']:
        branches = Sucursal.objects.filter(activa=True).order_by('nombre')
    else:
        if request.user.sucursal:
            branches = Sucursal.objects.filter(id=request.user.sucursal.id)
        else:
            branches = Sucursal.objects.none()
    
    # Obtener categorías para el filtro
    categories = ChecklistCategory.objects.filter(active=True).order_by('order', 'name')
    
    context = {
        'task_instances': task_instances,
        'branches': branches,
        'categories': categories,
        'selected_branch': branch_id,
        'selected_category': category_id,
        'start_date': start_date,
        'end_date': end_date,
        'selected_status': status,
        **get_sidebar_context('checklist_history')
    }
    
    return render(request, 'dashboard/checklist/task_history.html', context)


@login_required
@role_required(['admin', 'gerente', 'supervisor'])
def task_instance_detail(request, instance_id):
    """
    Detalles de una instancia de tarea específica
    """
    # Obtener la instancia con sus relaciones
    instance = get_object_or_404(
        TaskInstance.objects.select_related(
            'task', 'task__category', 'branch', 'performed_by'
        ).prefetch_related('evidence_files'),
        id=instance_id
    )
    
    # Verificar permisos
    if not request.user.is_staff and request.user.rol.nombre not in ['admin', 'gerente', 'supervisor']:
        if request.user.sucursal != instance.branch:
            messages.error(request, "No tienes permiso para ver esta tarea.")
            return redirect('dashboard:checklist_dashboard')
    
    # Obtener evidencias
    evidences = instance.evidence_files.all().order_by('-uploaded_at')
    
    context = {
        'instance': instance,
        'evidences': evidences,
        **get_sidebar_context('checklist_history')
    }
    
    return render(request, 'dashboard/checklist/task_instance_detail.html', context)


@login_required
@role_required(['admin', 'gerente', 'supervisor'])
@require_POST
def verify_task_instance(request, instance_id):
    """
    Verifica y aprueba o rechaza una instancia de tarea completada
    """
    try:
        # Obtener la instancia
        instance = get_object_or_404(TaskInstance, id=instance_id)
        
        # Verificar permisos
        if not request.user.is_staff and request.user.rol.nombre not in ['admin', 'gerente', 'supervisor']:
            if request.user.sucursal != instance.branch:
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes permiso para verificar esta tarea.'
                })
        
        # Solo se pueden verificar tareas completadas
        if instance.status != 'completado':
            return JsonResponse({
                'success': False,
                'message': 'Solo se pueden verificar tareas que ya hayan sido completadas.'
            })
        
        # Obtener acción (aprobar o rechazar)
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')
        
        if action == 'approve':
            # Marcar como verificada
            instance.verified = True
            instance.verified_by = request.user
            instance.verified_at = timezone.now()
            instance.verification_notes = comments
            instance.save()
            
            # Notificar al usuario que completó la tarea
            if instance.performed_by:
                Notification.objects.create(
                    type='task_approved',
                    recipient=instance.performed_by,
                    title='Tarea aprobada',
                    message=f'Tu tarea "{instance.task.title}" del {instance.date} ha sido aprobada por {request.user.get_full_name()}.',
                    related_task=instance,
                    alert_type='success',
                    icon='check-double'
                )
            
            return JsonResponse({
                'success': True,
                'message': 'Tarea aprobada exitosamente.'
            })
            
        elif action == 'reject':
            # Rechazar la tarea (volver a estado pendiente)
            instance.status = 'pendiente'
            instance.performed_by = None
            instance.performed_at = None
            instance.verified = False
            instance.verification_notes = comments
            instance.save()
            
            # Notificar a los usuarios responsables
            if instance.task.default_role:
                users_to_notify = Usuario.objects.filter(
                    sucursal=instance.branch,
                    rol=instance.task.default_role,
                    is_active=True
                )
                
                for user in users_to_notify:
                    Notification.objects.create(
                        type='task_rejected',
                        recipient=user,
                        title='Tarea rechazada',
                        message=f'La tarea "{instance.task.title}" del {instance.date} ha sido rechazada y debe ser completada nuevamente. Comentario: {comments}',
                        related_task=instance,
                        alert_type='warning',
                        icon='exclamation-circle'
                    )
            
            return JsonResponse({
                'success': True,
                'message': 'Tarea rechazada y vuelta a estado pendiente.'
            })
            
        else:
            return JsonResponse({
                'success': False,
                'message': 'Acción no válida.'
            })
        
    except Exception as e:
        logger.error(f"Error al verificar tarea: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })
