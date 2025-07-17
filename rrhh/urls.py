from django.urls import path
from . import views

urlpatterns = [
    # Dashboard principal de RRHH
    path('', views.recursos_humanos_index, name='rrhh_index'),
    
    # Empleados
    path('empleados/', views.empleados_listado, name='rrhh_empleados_listado'),
    path('empleados/crear/', views.empleado_crear, name='rrhh_empleado_crear'),
    path('empleados/<int:empleado_id>/', views.empleado_detalle, name='rrhh_empleado_detalle'),
    path('empleados/<int:empleado_id>/editar/', views.empleado_editar, name='rrhh_empleado_editar'),
    path('empleados/<int:empleado_id>/cambiar-estado/', views.empleado_cambiar_estado, name='rrhh_empleado_cambiar_estado'),
    
    # Documentos
    path('empleados/<int:empleado_id>/documentos/subir/', views.documento_subir, name='rrhh_documento_subir'),
    # path('documentos/<int:documento_id>/editar/', views.documento_editar, name='rrhh_documento_editar'),
    # path('documentos/<int:documento_id>/eliminar/', views.documento_eliminar, name='rrhh_documento_eliminar'),
    
    # Turnos
    path('turnos/', views.turnos_listado, name='rrhh_turnos_listado'),
    path('turnos/crear/', views.turno_crear, name='rrhh_turno_crear'),
    path('turnos/asignaciones/', views.asignaciones_turno_listado, name='rrhh_asignaciones_turno_listado'),
    path('turnos/asignar/', views.asignacion_turno_crear, name='rrhh_asignacion_turno_crear'),
    path('turnos/asignar/<int:empleado_id>/', views.asignacion_turno_crear, name='rrhh_asignacion_turno_crear_empleado'),
    
    # Asistencias
    path('asistencias/', views.asistencias_listado, name='rrhh_asistencias_listado'),
    path('asistencias/registro/', views.asistencia_registro_rapido, name='rrhh_asistencia_registrar'),
    path('asistencias/registrar/', views.asistencia_registrar, name='rrhh_asistencia_registrar_manual'),
    path('asistencias/registrar/<int:empleado_id>/', views.asistencia_registrar, name='rrhh_asistencia_registrar_empleado'),
    # path('asistencias/<int:asistencia_id>/editar/', views.asistencia_editar, name='rrhh_asistencia_editar'),
    # path('asistencias/<int:asistencia_id>/justificar/', views.asistencia_justificar, name='rrhh_asistencia_justificar'),
    
    # Capacitaciones
    path('capacitaciones/', views.capacitaciones_listado, name='rrhh_capacitaciones_listado'),
    path('capacitaciones/crear/', views.capacitacion_crear, name='rrhh_capacitacion_crear'),
    path('capacitaciones/asignadas/', views.capacitaciones_asignadas, name='rrhh_capacitaciones_asignadas'),
    path('capacitaciones/asignar/', views.capacitacion_asignar, name='rrhh_capacitacion_asignar'),
    path('capacitaciones/asignar/<int:empleado_id>/', views.capacitacion_asignar, name='rrhh_capacitacion_asignar_empleado'),
    # path('capacitaciones/<int:capacitacion_id>/', views.capacitacion_detalle, name='rrhh_capacitacion_detalle'),
    # path('capacitaciones/<int:capacitacion_id>/editar/', views.capacitacion_editar, name='rrhh_capacitacion_editar'),
    # path('capacitaciones/<int:capacitacion_id>/completar/', views.capacitacion_completar, name='rrhh_capacitacion_completar'),
    
    # Evaluaciones
    path('evaluaciones/', views.evaluaciones_listado, name='rrhh_evaluaciones_listado'),
    path('evaluaciones/crear/', views.evaluacion_crear, name='rrhh_evaluacion_crear'),
    path('evaluaciones/crear/<int:empleado_id>/', views.evaluacion_crear, name='rrhh_evaluacion_crear_empleado'),
    
    # Vacaciones y permisos
    path('vacaciones/', views.vacaciones_listado, name='rrhh_vacaciones_listado'),
    path('vacaciones/solicitar/', views.vacaciones_solicitar, name='rrhh_vacaciones_solicitar'),
    path('vacaciones/solicitar/<int:empleado_id>/', views.vacaciones_solicitar, name='rrhh_vacaciones_solicitar_empleado'),
    path('vacaciones/<int:vacacion_id>/aprobar/', views.vacacion_aprobar, name='rrhh_vacacion_aprobar'),
    path('vacaciones/<int:vacacion_id>/rechazar/', views.vacacion_rechazar, name='rrhh_vacacion_rechazar'),
    
    # Nóminas
    path('nominas/', views.nominas_listado, name='rrhh_nominas_listado'),
    path('nominas/generar/', views.nomina_generar, name='rrhh_nomina_generar'),
    path('nominas/generar/<int:empleado_id>/', views.nomina_generar, name='rrhh_nomina_generar_empleado'),
    # path('nominas/<int:nomina_id>/', views.nomina_detalle, name='rrhh_nomina_detalle'),
    # path('nominas/<int:nomina_id>/editar/', views.nomina_editar, name='rrhh_nomina_editar'),
    path('nominas/<int:nomina_id>/aprobar/', views.nomina_aprobar, name='rrhh_nomina_aprobar'),
    path('nominas/<int:nomina_id>/pagar/', views.nomina_pagar, name='rrhh_nomina_pagar'),
    # path('nominas/<int:nomina_id>/pdf/', views.nomina_pdf, name='rrhh_nomina_pdf'),
    
    # Estadísticas
    path('estadisticas/', views.estadisticas, name='rrhh_estadisticas'),
    
    # Exportar datos
    path('exportar/empleados/', views.exportar_empleados_csv, name='rrhh_exportar_empleados'),
    path('exportar/asistencias/', views.exportar_asistencias_csv, name='rrhh_exportar_asistencias'),
    
    # API para AJAX
    path('api/empleados/<int:empleado_id>/info/', views.api_empleado_info, name='api_empleado_info'),
    path('api/empleados/<int:empleado_id>/turnos/', views.api_obtener_turnos_empleado, name='api_obtener_turnos_empleado'),
    path('api/notificaciones/<int:notificacion_id>/leida/', views.api_marcar_notificacion_leida, name='api_marcar_notificacion_leida'),
]
