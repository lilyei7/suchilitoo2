from django.urls import path
from dashboard.views import checklist_views

urlpatterns = [
    # Rutas del dashboard de checklist
    path('', checklist_views.checklist_dashboard, name='checklist_dashboard'),
    path('generate-tasks/', checklist_views.generate_task_instances, name='generate_task_instances'),
    path('task/<int:instance_id>/complete/', checklist_views.complete_task, name='complete_task'),
    path('task/<int:instance_id>/evidence/', checklist_views.upload_evidence, name='upload_evidence'),
    path('bulk-complete/', checklist_views.bulk_complete_tasks, name='bulk_complete_tasks'),
    
    # Gestión de categorías
    path('categorias/', checklist_views.manage_categories, name='manage_categories'),
    path('categoria/crear/', checklist_views.create_category, name='create_category'),
    path('categoria/<int:category_id>/editar/', checklist_views.edit_category, name='edit_category'),
    path('categoria/<int:category_id>/eliminar/', checklist_views.delete_category, name='delete_category'),
    
    # Gestión de tareas
    path('tareas/', checklist_views.manage_tasks, name='manage_tasks'),
    path('tarea/crear/', checklist_views.create_task, name='create_task'),
    path('tarea/<int:task_id>/editar/', checklist_views.edit_task, name='edit_task'),
    path('tarea/<int:task_id>/eliminar/', checklist_views.delete_task, name='delete_task'),
    
    # Historial y verificación de tareas
    path('historial/', checklist_views.task_history, name='task_history'),
    path('historial/tarea/<int:instance_id>/', checklist_views.task_instance_detail, name='task_instance_detail'),
    path('historial/tarea/<int:instance_id>/verificar/', checklist_views.verify_task_instance, name='verify_task_instance'),
    
    # Rutas de incidentes
    path('incidentes/', checklist_views.incident_list, name='checklist_incidents'),
    path('incidente/reportar/', checklist_views.report_incident, name='report_incident'),
    path('incidente/<int:incident_id>/', checklist_views.incident_detail, name='incident_detail'),
    path('incidente/<int:incident_id>/status/', checklist_views.update_incident_status, name='update_incident_status'),
    path('incidente/<int:incident_id>/evidencia/', checklist_views.upload_incident_evidence, name='upload_incident_evidence'),
    
    # Rutas de notificaciones
    path('notificaciones/', checklist_views.notifications_list, name='notificaciones'),
    path('notificacion/leer/', checklist_views.mark_notification_read, name='marcar_notificacion_leida'),
    path('notificacion/eliminar/', checklist_views.delete_notification, name='eliminar_notificacion'),
    path('notificaciones/marcar-todas-leidas/', checklist_views.mark_all_notifications_read, name='marcar_todas_notificaciones_leidas'),
]
