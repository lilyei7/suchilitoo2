from django.urls import path
from dashboard.views import checklist_views

urlpatterns = [
    # Rutas del dashboard de checklist
    path('', checklist_views.checklist_dashboard, name='checklist_dashboard'),
    path('generate-tasks/', checklist_views.generate_task_instances, name='generate_task_instances'),
    path('task/<int:instance_id>/complete/', checklist_views.complete_task, name='complete_task'),
    path('task/<int:instance_id>/evidence/', checklist_views.upload_evidence, name='upload_evidence'),
    path('bulk-complete/', checklist_views.bulk_complete_tasks, name='bulk_complete_tasks'),
    
    # Rutas de incidentes
    path('incidents/', checklist_views.incident_list, name='checklist_incidents'),
    path('incidents/report/', checklist_views.report_incident, name='report_incident'),
    path('incidents/<int:incident_id>/', checklist_views.incident_detail, name='incident_detail'),
    path('incidents/<int:incident_id>/status/', checklist_views.update_incident_status, name='update_incident_status'),
    path('incidents/<int:incident_id>/evidence/', checklist_views.upload_incident_evidence, name='upload_incident_evidence'),
    
    # Rutas de notificaciones
    path('notifications/', checklist_views.notifications_list, name='checklist_notifications'),
    path('notifications/<int:notification_id>/read/', checklist_views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', checklist_views.mark_all_notifications_read, name='mark_all_notifications_read'),
]
