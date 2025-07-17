from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Count, Q, Sum
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.files.storage import default_storage
from django.conf import settings
import os
import json
import csv
from datetime import datetime, timedelta, time
import logging

from .models import (
    Empleado, Rol, DocumentoEmpleado, Turno, AsignacionTurno,
    Asistencia, Capacitacion, EmpleadoCapacitacion,
    Evaluacion, Vacacion, Nomina, Notificacion
)
from accounts.models import Sucursal
from .forms import (
    EmpleadoForm, DocumentoEmpleadoForm, TurnoForm,
    AsignacionTurnoForm, AsistenciaForm, CapacitacionForm,
    EvaluacionForm, VacacionForm, NominaForm
)

logger = logging.getLogger(__name__)

# Funciones auxiliares
def calcular_estado_asistencia(asistencia):
    """Calcula el estado de una asistencia basado en horarios"""
    if not asistencia.hora_entrada:
        return 'ausente'
    
    # Por ahora retornamos 'presente' si hay hora de entrada
    # En el futuro se puede agregar lógica más compleja con turnos
    return 'presente'

# Funciones auxiliares simplificadas
def require_module_access(module_name):
    """Decorador simplificado para verificar acceso a módulos"""
    def decorator(view_func):
        @login_required
        def wrapped_view(request, *args, **kwargs):
            # Para simplificar, permitir acceso a superusuarios y staff
            if request.user.is_superuser or request.user.is_staff:
                return view_func(request, *args, **kwargs)
            
            # Verificar si el usuario es empleado
            try:
                empleado = Empleado.objects.get(email=request.user.email)
                return view_func(request, *args, **kwargs)
            except Empleado.DoesNotExist:
                messages.error(request, "No tienes acceso a este módulo.")
                return redirect('dashboard:index')
        
        return wrapped_view
    return decorator

@login_required
def recursos_humanos_index(request):
    """Vista principal del módulo de RRHH"""
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    # Estadísticas para el dashboard
    total_empleados = Empleado.objects.count()
    empleados_activos = Empleado.objects.filter(estado='activo').count()
    
    # Empleados nuevos este mes
    hoy = timezone.now().date()
    primer_dia_mes = hoy.replace(day=1)
    empleados_nuevos = Empleado.objects.filter(fecha_ingreso__gte=primer_dia_mes).count()
    
    # Asistencia de hoy - corregido para no usar campo estado inexistente
    asistencias_hoy = Asistencia.objects.filter(fecha=hoy)
    presentes_hoy = asistencias_hoy.count()  # Simplificado por ahora
    ausentes_hoy = 0  # Calculado dinámicamente en el futuro
    tardanzas_hoy = 0  # Calculado dinámicamente en el futuro
    
    # Distribución por sucursal
    sucursales = Sucursal.objects.annotate(
        num_empleados=Count('empleados_sucursal', distinct=True)
    ).values('nombre', 'num_empleados')
    
    # Distribución por rol
    roles = Rol.objects.annotate(
        num_empleados=Count('empleados_rol', distinct=True)
    ).values('nombre', 'num_empleados')
    
    # Empleados sin roles definidos
    empleados_sin_roles = Empleado.objects.filter(roles__isnull=True).count()
    
    # Datos para gráficos
    sucursales_data = list(sucursales)
    roles_data = list(roles)
    
    context = {
        'total_empleados': total_empleados,
        'empleados_activos': empleados_activos,
        'empleados_nuevos': empleados_nuevos,
        'empleados_sin_roles': empleados_sin_roles,
        'presentes_hoy': presentes_hoy,
        'ausentes_hoy': ausentes_hoy,
        'tardanzas_hoy': tardanzas_hoy,
        'sucursales_data': sucursales_data,
        'roles_data': roles_data,
        'fecha_actual': hoy,
        'hora_actual': timezone.now(),
    }
    
    return render(request, 'dashboard/recursos_humanos/index.html', context)

@login_required
def empleados_listado(request):
    """Vista para listar empleados con filtros"""
    
    # Obtener parámetros de filtro
    query = request.GET.get('q', '')
    estado_filtro = request.GET.get('estado', 'todos')
    rol_filtro = request.GET.get('rol', '')
    sucursal_filtro = request.GET.get('sucursal', '')
    
    # Consulta base
    empleados = Empleado.objects.all().select_related().prefetch_related('roles', 'sucursales')
    
    # Aplicar filtros
    if query:
        empleados = empleados.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(rut__icontains=query) |
            Q(email__icontains=query)
        )
    
    if estado_filtro != 'todos':
        empleados = empleados.filter(estado=estado_filtro)
    
    if rol_filtro:
        empleados = empleados.filter(roles__id=rol_filtro)
    
    if sucursal_filtro:
        empleados = empleados.filter(sucursales__id=sucursal_filtro)
    
    # Paginación
    paginator = Paginator(empleados, 12)  # 12 empleados por página
    page_number = request.GET.get('page')
    empleados = paginator.get_page(page_number)
    
    # Datos para filtros
    roles = Rol.objects.all()
    sucursales = Sucursal.objects.all()
    
    context = {
        'empleados': empleados,
        'roles': roles,
        'sucursales': sucursales,
        'query': query,
        'estado_filtro': estado_filtro,
        'rol_filtro': rol_filtro,
        'sucursal_filtro': sucursal_filtro,
    }
    
    return render(request, 'dashboard/recursos_humanos/empleados_listado.html', context)

@login_required
def empleado_crear(request):
    """Vista para crear un nuevo empleado"""
    
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                empleado = form.save()
                messages.success(request, f'Empleado {empleado.nombre} {empleado.apellido} creado exitosamente.')
                return redirect('dashboard:rrhh_empleados_listado')  # Corregido: redirigir al listado
            except Exception as e:
                messages.error(request, f'Error al crear empleado: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = EmpleadoForm()
    
    context = {
        'form': form,
        'accion': 'crear',  # Agregado para la plantilla
        'title': 'Crear Nuevo Empleado'
    }
    
    return render(request, 'dashboard/recursos_humanos/empleado_form.html', context)  # Corregido: plantilla correcta

@login_required
def empleado_detalle(request, empleado_id):
    """Vista para mostrar detalles de un empleado"""
    
    empleado = get_object_or_404(Empleado, id=empleado_id)
    
    # Asistencias del empleado (últimos 30 días)
    fecha_limite = timezone.now().date() - timedelta(days=30)
    asistencias = Asistencia.objects.filter(
        empleado=empleado,
        fecha__gte=fecha_limite
    ).order_by('-fecha')[:10]  # Últimas 10 asistencias
    
    # Documentos del empleado
    documentos = DocumentoEmpleado.objects.filter(empleado=empleado).order_by('-fecha_subida')
    
    # Capacitaciones del empleado
    capacitaciones = EmpleadoCapacitacion.objects.filter(empleado=empleado).order_by('-fecha_inicio')
    
    # Nóminas del empleado (últimas 6)
    nominas = Nomina.objects.filter(empleado=empleado).order_by('-año', '-mes')[:6]
    
    # Estadísticas de asistencia - corregido para no usar campo estado inexistente
    total_asistencias = asistencias.count()
    presentes = total_asistencias  # Simplificado por ahora
    ausentes = 0  # Para calcular dinámicamente en el futuro
    tardanzas = 0  # Para calcular dinámicamente en el futuro  
    justificados = 0  # Para calcular dinámicamente en el futuro
    
    asistencia_mensual = (presentes / total_asistencias * 100) if total_asistencias > 0 else 0
    puntualidad = ((presentes + justificados) / total_asistencias * 100) if total_asistencias > 0 else 0
    
    # Calcular horas trabajadas
    horas_trabajadas = 0
    for asistencia in asistencias:
        if asistencia.hora_entrada and asistencia.hora_salida:
            delta = datetime.combine(timezone.now().date(), asistencia.hora_salida) - \
                   datetime.combine(timezone.now().date(), asistencia.hora_entrada)
            horas_trabajadas += delta.total_seconds() / 3600
    
    # Datos para calendario de asistencia
    asistencia_calendario = {}
    for asistencia in asistencias:
        fecha_str = asistencia.fecha.strftime('%Y-%m-%d')
        asistencia_calendario[fecha_str] = {
            'estado': calcular_estado_asistencia(asistencia),
            'hora_entrada': asistencia.hora_entrada.strftime('%H:%M') if asistencia.hora_entrada else None,
            'hora_salida': asistencia.hora_salida.strftime('%H:%M') if asistencia.hora_salida else None,
        }
    
    context = {
        'empleado': empleado,
        'asistencias': asistencias,
        'documentos': documentos,
        'capacitaciones': capacitaciones,
        'nominas': nominas,
        'asistencia_mensual': round(asistencia_mensual, 1),
        'puntualidad': round(puntualidad, 1),
        'horas_trabajadas': round(horas_trabajadas, 1),
        'llegadas_tarde': tardanzas,
        'presentes': presentes,
        'ausentes': ausentes,
        'tardanzas': tardanzas,
        'justificados': justificados,
        'asistencia_calendario': json.dumps(asistencia_calendario),
        'mes_actual': timezone.now().date(),
        'meses': json.dumps(['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']),
        'asistencia_mensual_historico': json.dumps([95, 92, 88, 94, 96, 93]),
    }
    
    return render(request, 'dashboard/recursos_humanos/empleado_detalle.html', context)
    evaluaciones_pendientes = []
    # Aquí iría lógica para determinar evaluaciones pendientes
    
    # Notificaciones recientes para el usuario
    notificaciones = Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).order_by('-fecha_creacion')[:5]
    
    context = {
        'total_empleados': total_empleados,
        'empleados_activos': empleados_activos,
        'empleados_nuevos': empleados_nuevos,
        'sucursales': sucursales,
        'roles': roles,
        'contratos_por_vencer': contratos_por_vencer,
        'evaluaciones_pendientes': evaluaciones_pendientes,
        'notificaciones': notificaciones,
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'dashboard'
    }
    
    return render(request, 'dashboard/recursos_humanos/index.html', context)

@login_required
@require_module_access('recursos_humanos')
def empleados_listado(request):
    """Vista para listar empleados con filtros"""
    
    # Obtener parámetros de filtrado
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', 'todos')
    rol_id = request.GET.get('rol', '')
    sucursal_id = request.GET.get('sucursal', '')
    
    # Iniciar queryset base
    empleados = Empleado.objects.all().order_by('apellido', 'nombre')
    
    # Aplicar filtros
    if query:
        empleados = empleados.filter(
            Q(nombre__icontains=query) | 
            Q(apellido__icontains=query) |
            Q(rut__icontains=query) |
            Q(email__icontains=query)
        )
    
    if estado != 'todos':
        empleados = empleados.filter(estado=estado)
    
    if rol_id:
        empleados = empleados.filter(roles__id=rol_id)
    
    if sucursal_id:
        empleados = empleados.filter(sucursales__id=sucursal_id)
    
    # Paginación
    paginator = Paginator(empleados, 10)
    page_number = request.GET.get('page', 1)
    empleados_paginados = paginator.get_page(page_number)
    
    # Datos para los filtros selectores
    roles = Rol.objects.all().order_by('nombre')
    sucursales = Sucursal.objects.all().order_by('nombre')
    
    context = {
        'empleados': empleados_paginados,
        'roles': roles,
        'sucursales': sucursales,
        'query': query,
        'estado_filtro': estado,
        'rol_filtro': rol_id,
        'sucursal_filtro': sucursal_id,
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'empleados'
    }
    
    return render(request, 'dashboard/recursos_humanos/empleados_listado.html', context)

@login_required
@require_module_access('recursos_humanos')
def empleado_crear(request):
    """Vista para crear un nuevo empleado"""
    
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES)
        if form.is_valid():
            empleado = form.save()
            
            # Manejar múltiples sucursales
            sucursales_ids = request.POST.getlist('sucursales')
            empleado.sucursales.set(sucursales_ids)
            
            # Manejar múltiples roles
            roles_ids = request.POST.getlist('roles')
            empleado.roles.set(roles_ids)
            
            messages.success(request, f"Empleado {empleado.nombre} {empleado.apellido} creado correctamente.")
            return redirect('dashboard:rrhh_empleado_detalle', empleado_id=empleado.id)
        else:
            messages.error(request, "Error al crear el empleado. Revisa los datos ingresados.")
    else:
        form = EmpleadoForm()
    
    # Datos para los selectores
    roles = Rol.objects.all().order_by('nombre')
    sucursales = Sucursal.objects.all().order_by('nombre')
    empleados = Empleado.objects.filter(estado='activo').order_by('apellido', 'nombre')
    
    context = {
        'form': form,
        'roles': roles,
        'sucursales': sucursales,
        'empleados': empleados,
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'empleados',
        'accion': 'crear'
    }
    
    return render(request, 'dashboard/recursos_humanos/empleado_form.html', context)

@login_required
@require_module_access('recursos_humanos')
def empleado_editar(request, empleado_id):
    """Vista para editar un empleado existente"""
    
    empleado = get_object_or_404(Empleado, id=empleado_id)
    
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES, instance=empleado)
        if form.is_valid():
            empleado = form.save()
            
            # Manejar múltiples sucursales
            sucursales_ids = request.POST.getlist('sucursales')
            empleado.sucursales.set(sucursales_ids)
            
            # Manejar múltiples roles
            roles_ids = request.POST.getlist('roles')
            empleado.roles.set(roles_ids)
            
            messages.success(request, f"Empleado {empleado.nombre} {empleado.apellido} actualizado correctamente.")
            return redirect('dashboard:rrhh_empleado_detalle', empleado_id=empleado.id)
        else:
            messages.error(request, "Error al actualizar el empleado. Revisa los datos ingresados.")
    else:
        form = EmpleadoForm(instance=empleado)
    
    # Datos para los selectores
    roles = Rol.objects.all().order_by('nombre')
    sucursales = Sucursal.objects.all().order_by('nombre')
    empleados = Empleado.objects.filter(estado='activo').exclude(id=empleado_id).order_by('apellido', 'nombre')
    
    # Valores preseleccionados
    roles_seleccionados = empleado.roles.all().values_list('id', flat=True)
    sucursales_seleccionadas = empleado.sucursales.all().values_list('id', flat=True)
    
    context = {
        'form': form,
        'empleado': empleado,
        'roles': roles,
        'sucursales': sucursales,
        'empleados': empleados,
        'roles_seleccionados': list(roles_seleccionados),
        'sucursales_seleccionadas': list(sucursales_seleccionadas),
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'empleados',
        'accion': 'editar'
    }
    
    return render(request, 'dashboard/recursos_humanos/empleado_form.html', context)

@login_required
@require_module_access('recursos_humanos')
def empleado_detalle(request, empleado_id):
    """Vista para ver detalles de un empleado"""
    
    empleado = get_object_or_404(Empleado, id=empleado_id)
    
    # Obtener documentos asociados
    documentos = DocumentoEmpleado.objects.filter(empleado=empleado).order_by('-fecha_subida')
    
    # Obtener asignaciones de turno actuales
    ahora = timezone.now().date()
    asignaciones_turno = AsignacionTurno.objects.filter(
        empleado=empleado,
        fecha_inicio__lte=ahora
    ).filter(
        Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=ahora)
    ).order_by('turno__hora_inicio')
    
    # Obtener capacitaciones
    capacitaciones = EmpleadoCapacitacion.objects.filter(
        empleado=empleado
    ).order_by('-fecha_inicio')
    
    # Obtener evaluaciones recientes
    evaluaciones = Evaluacion.objects.filter(
        empleado=empleado
    ).order_by('-fecha')[:5]
    
    # Obtener registros de asistencia recientes
    asistencias = Asistencia.objects.filter(
        empleado=empleado
    ).order_by('-fecha')[:10]
    
    # Obtener vacaciones y permisos
    vacaciones = Vacacion.objects.filter(
        empleado=empleado
    ).order_by('-fecha_inicio')[:5]
    
    # Obtener nóminas recientes
    nominas = Nomina.objects.filter(
        empleado=empleado
    ).order_by('-fecha_calculo')[:5]
    
    context = {
        'empleado': empleado,
        'documentos': documentos,
        'asignaciones_turno': asignaciones_turno,
        'capacitaciones': capacitaciones,
        'evaluaciones': evaluaciones,
        'asistencias': asistencias,
        'vacaciones': vacaciones,
        'nominas': nominas,
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'empleados'
    }
    
    return render(request, 'dashboard/recursos_humanos/empleado_detalle.html', context)

@login_required
@require_module_access('recursos_humanos')
@require_POST
def empleado_cambiar_estado(request, empleado_id):
    """Vista para cambiar el estado de un empleado (activar/desactivar)"""
    
    empleado = get_object_or_404(Empleado, id=empleado_id)
    nuevo_estado = request.POST.get('estado')
    
    if nuevo_estado in dict(Empleado.ESTADO_CHOICES).keys():
        empleado.estado = nuevo_estado
        empleado.save()
        
        estado_display = dict(Empleado.ESTADO_CHOICES)[nuevo_estado]
        messages.success(request, f"Estado del empleado cambiado a {estado_display}.")
        
        # Si está inactivando, registrar fecha de término si no existe
        if nuevo_estado == 'inactivo' and not empleado.fecha_termino:
            empleado.fecha_termino = timezone.now().date()
            empleado.save()
    else:
        messages.error(request, "Estado no válido.")
    
    return redirect('dashboard:rrhh_empleado_detalle', empleado_id=empleado.id)

@login_required
@require_module_access('recursos_humanos')
def documento_subir(request, empleado_id):
    """Vista para subir un documento asociado a un empleado"""
    
    empleado = get_object_or_404(Empleado, id=empleado_id)
    
    if request.method == 'POST':
        form = DocumentoEmpleadoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.empleado = empleado
            documento.save()
            
            messages.success(request, "Documento subido correctamente.")
            return redirect('dashboard:rrhh_empleado_detalle', empleado_id=empleado.id)
        else:
            messages.error(request, "Error al subir el documento. Revisa los datos ingresados.")
    else:
        form = DocumentoEmpleadoForm()
    
    context = {
        'form': form,
        'empleado': empleado,
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'empleados'
    }
    
    return render(request, 'dashboard/recursos_humanos/documento_form.html', context)

@login_required
@require_module_access('recursos_humanos')
def turnos_listado(request):
    """Vista para listar los turnos definidos"""
    
    turnos = Turno.objects.all().order_by('hora_inicio')
    
    context = {
        'turnos': turnos,
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'turnos'
    }
    
    return render(request, 'dashboard/recursos_humanos/turnos_listado.html', context)

@login_required
@require_module_access('recursos_humanos')
def turno_crear(request):
    """Vista para crear un nuevo turno"""
    
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            turno = form.save()
            messages.success(request, f"Turno {turno.nombre} creado correctamente.")
            return redirect('dashboard:rrhh_turnos_listado')
        else:
            messages.error(request, "Error al crear el turno. Revisa los datos ingresados.")
    else:
        form = TurnoForm()
    
    context = {
        'form': form,
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'turnos',
        'accion': 'crear'
    }
    
    return render(request, 'dashboard/recursos_humanos/turno_form.html', context)

@login_required
@require_module_access('recursos_humanos')
def asignacion_turno_crear(request, empleado_id=None):
    """Vista para asignar un turno a un empleado"""
    
    empleado_inicial = None
    if empleado_id:
        empleado_inicial = get_object_or_404(Empleado, id=empleado_id)
    
    if request.method == 'POST':
        form = AsignacionTurnoForm(request.POST)
        if form.is_valid():
            asignacion = form.save()
            messages.success(request, "Turno asignado correctamente.")
            
            # Redireccionar según contexto
            if 'volver_empleado' in request.POST and empleado_id:
                return redirect('dashboard:rrhh_empleado_detalle', empleado_id=empleado_id)
            else:
                return redirect('dashboard:rrhh_asignaciones_turno_listado')
        else:
            messages.error(request, "Error al asignar el turno. Revisa los datos ingresados.")
    else:
        form = AsignacionTurnoForm(initial={'empleado': empleado_inicial})
    
    # Datos para los selectores
    empleados = Empleado.objects.filter(estado='activo').order_by('apellido', 'nombre')
    turnos = Turno.objects.all().order_by('hora_inicio')
    sucursales = Sucursal.objects.all().order_by('nombre')
    
    context = {
        'form': form,
        'empleados': empleados,
        'turnos': turnos,
        'sucursales': sucursales,
        'empleado_seleccionado': empleado_inicial,
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'turnos',
        'accion': 'asignar'
    }
    
    return render(request, 'dashboard/recursos_humanos/asignacion_turno_form.html', context)

@login_required
@require_module_access('recursos_humanos')
def asignaciones_turno_listado(request):
    """Vista para listar todas las asignaciones de turno actuales"""
    
    # Filtros
    empleado_id = request.GET.get('empleado', '')
    sucursal_id = request.GET.get('sucursal', '')
    turno_id = request.GET.get('turno', '')
    
    # Fecha actual para mostrar solo asignaciones vigentes
    ahora = timezone.now().date()
    
    # Iniciar queryset base
    asignaciones = AsignacionTurno.objects.filter(
        fecha_inicio__lte=ahora
    ).filter(
        Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=ahora)
    ).order_by('empleado__apellido', 'empleado__nombre', 'turno__hora_inicio')
    
    # Aplicar filtros
    if empleado_id:
        asignaciones = asignaciones.filter(empleado_id=empleado_id)
    
    if sucursal_id:
        asignaciones = asignaciones.filter(sucursal_id=sucursal_id)
    
    if turno_id:
        asignaciones = asignaciones.filter(turno_id=turno_id)
    
    # Paginación
    paginator = Paginator(asignaciones, 15)
    page_number = request.GET.get('page', 1)
    asignaciones_paginadas = paginator.get_page(page_number)
    
    # Datos para los filtros selectores
    empleados = Empleado.objects.filter(estado='activo').order_by('apellido', 'nombre')
    turnos = Turno.objects.all().order_by('hora_inicio')
    sucursales = Sucursal.objects.all().order_by('nombre')
    
    context = {
        'asignaciones': asignaciones_paginadas,
        'empleados': empleados,
        'turnos': turnos,
        'sucursales': sucursales,
        'empleado_filtro': empleado_id,
        'turno_filtro': turno_id,
        'sucursal_filtro': sucursal_id,
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'turnos'
    }
    
    return render(request, 'dashboard/recursos_humanos/asignaciones_turno_listado.html', context)

@login_required
@require_module_access('recursos_humanos')
def asistencia_registrar(request, empleado_id=None):
    """Vista para registrar la asistencia de un empleado"""
    
    empleado_inicial = None
    if empleado_id:
        empleado_inicial = get_object_or_404(Empleado, id=empleado_id)
    
    if request.method == 'POST':
        form = AsistenciaForm(request.POST)
        if form.is_valid():
            asistencia = form.save(commit=False)
            
            # Verificar si ya existe registro para este empleado y fecha
            fecha = form.cleaned_data.get('fecha')
            empleado = form.cleaned_data.get('empleado')
            
            try:
                existente = Asistencia.objects.get(empleado=empleado, fecha=fecha)
                # Si solo hay entrada y está registrando salida
                if not existente.hora_salida and 'hora_salida' in request.POST and request.POST['hora_salida']:
                    existente.hora_salida = form.cleaned_data.get('hora_salida')
                    existente.observaciones = form.cleaned_data.get('observaciones')
                    existente.save()
                    messages.success(request, f"Hora de salida registrada para {empleado}.")
                else:
                    messages.warning(request, f"Ya existe un registro para {empleado} en la fecha {fecha}.")
            except Asistencia.DoesNotExist:
                asistencia.save()
                messages.success(request, f"Asistencia registrada para {empleado}.")
            
            if 'volver_empleado' in request.POST and empleado_id:
                return redirect('dashboard:rrhh_empleado_detalle', empleado_id=empleado_id)
            else:
                return redirect('dashboard:rrhh_asistencias_listado')
        else:
            messages.error(request, "Error al registrar la asistencia. Revisa los datos ingresados.")
    else:
        initial_data = {
            'empleado': empleado_inicial,
            'fecha': timezone.now().date(),
            'hora_entrada': timezone.now(),
        }
        form = AsistenciaForm(initial=initial_data)
    
    # Datos para los selectores
    empleados = Empleado.objects.filter(estado='activo').order_by('apellido', 'nombre')
    turnos = Turno.objects.all().order_by('hora_inicio')
    sucursales = Sucursal.objects.all().order_by('nombre')
    
    context = {
        'form': form,
        'empleados': empleados,
        'turnos': turnos,
        'sucursales': sucursales,
        'empleado_seleccionado': empleado_inicial,
        'fecha_actual': timezone.now().date(),
        'hora_actual': timezone.now().time(),
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'asistencias',
        'accion': 'registrar'
    }
    
    return render(request, 'dashboard/recursos_humanos/asistencia_form.html', context)

@login_required
@require_module_access('recursos_humanos')
def asistencias_listado(request):
    """Vista para listar los registros de asistencia"""
    
    # Filtros
    empleado_id = request.GET.get('empleado', '')
    sucursal_id = request.GET.get('sucursal', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    # Iniciar queryset base
    asistencias = Asistencia.objects.all().order_by('-fecha', '-hora_entrada')
    
    # Aplicar filtros
    if empleado_id:
        asistencias = asistencias.filter(empleado_id=empleado_id)
    
    if sucursal_id:
        asistencias = asistencias.filter(sucursal_id=sucursal_id)
    
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            asistencias = asistencias.filter(fecha__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            asistencias = asistencias.filter(fecha__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    # Paginación
    paginator = Paginator(asistencias, 20)
    page_number = request.GET.get('page', 1)
    asistencias_paginadas = paginator.get_page(page_number)
    
    # Datos para los filtros selectores
    empleados = Empleado.objects.filter(estado='activo').order_by('apellido', 'nombre')
    sucursales = Sucursal.objects.all().order_by('nombre')
    
    # Estadísticas para hoy - corregido para no usar campo estado inexistente
    hoy = timezone.now().date()
    asistencias_hoy = Asistencia.objects.filter(fecha=hoy)
    presentes_hoy = asistencias_hoy.count()  # Simplificado por ahora
    ausentes_hoy = 0  # Para calcular dinámicamente en el futuro
    tardanzas_hoy = 0  # Para calcular dinámicamente en el futuro
    total_asistencias = asistencias.count()
    
    context = {
        'asistencias': asistencias_paginadas,
        'empleados': empleados,
        'sucursales': sucursales,
        'empleado_filtro': empleado_id,
        'sucursal_filtro': sucursal_id,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'presentes_hoy': presentes_hoy,
        'ausentes_hoy': ausentes_hoy,
        'tardanzas_hoy': tardanzas_hoy,
        'total_asistencias': total_asistencias,
        'is_paginated': asistencias_paginadas.has_other_pages(),
        'page_obj': asistencias_paginadas,
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'asistencias'
    }
    
    return render(request, 'dashboard/recursos_humanos/asistencias_listado.html', context)

@login_required
@require_module_access('recursos_humanos')
def capacitaciones_listado(request):
    """Vista para listar capacitaciones disponibles"""
    
    capacitaciones = Capacitacion.objects.all().order_by('nombre')
    
    context = {
        'capacitaciones': capacitaciones,
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'capacitaciones'
    }
    
    return render(request, 'dashboard/recursos_humanos/capacitaciones_listado.html', context)

@login_required
@require_module_access('recursos_humanos')
def capacitacion_crear(request):
    """Vista para crear una nueva capacitación"""
    
    if request.method == 'POST':
        form = CapacitacionForm(request.POST, request.FILES)
        if form.is_valid():
            capacitacion = form.save()
            messages.success(request, f"Capacitación '{capacitacion.nombre}' creada correctamente.")
            return redirect('dashboard:rrhh_capacitaciones_listado')
        else:
            messages.error(request, "Error al crear la capacitación. Revisa los datos ingresados.")
    else:
        form = CapacitacionForm()
    
    context = {
        'form': form,
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'capacitaciones',
        'accion': 'crear'
    }
    
    return render(request, 'dashboard/recursos_humanos/capacitacion_form.html', context)

@login_required
@require_module_access('recursos_humanos')
def capacitacion_asignar(request, empleado_id=None):
    """Vista para asignar una capacitación a un empleado"""
    
    empleado_inicial = None
    if empleado_id:
        empleado_inicial = get_object_or_404(Empleado, id=empleado_id)
    
    if request.method == 'POST':
        # Procesar formulario para asignar capacitación
        empleado_id = request.POST.get('empleado')
        capacitacion_id = request.POST.get('capacitacion')
        fecha_inicio = request.POST.get('fecha_inicio')
        
        try:
            empleado = Empleado.objects.get(id=empleado_id)
            capacitacion = Capacitacion.objects.get(id=capacitacion_id)
            
            # Crear la asignación
            asignacion = EmpleadoCapacitacion(
                empleado=empleado,
                capacitacion=capacitacion,
                fecha_inicio=fecha_inicio,
                estado='pendiente'
            )
            asignacion.save()
            
            messages.success(request, f"Capacitación asignada a {empleado}.")
            
            if 'volver_empleado' in request.POST and empleado_id:
                return redirect('dashboard:rrhh_empleado_detalle', empleado_id=empleado_id)
            else:
                return redirect('dashboard:rrhh_capacitaciones_asignadas')
                
        except (Empleado.DoesNotExist, Capacitacion.DoesNotExist) as e:
            messages.error(request, f"Error al asignar capacitación: {str(e)}")
    
    # Datos para los selectores
    empleados = Empleado.objects.filter(estado='activo').order_by('apellido', 'nombre')
    capacitaciones = Capacitacion.objects.all().order_by('nombre')
    
    context = {
        'empleados': empleados,
        'capacitaciones': capacitaciones,
        'empleado_seleccionado': empleado_inicial,
        'fecha_actual': timezone.now().date(),
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'capacitaciones'
    }
    
    return render(request, 'dashboard/recursos_humanos/capacitacion_asignar_form.html', context)

@login_required
@require_module_access('recursos_humanos')
def capacitaciones_asignadas(request):
    """Vista para listar todas las capacitaciones asignadas"""
    
    # Filtros
    empleado_id = request.GET.get('empleado', '')
    capacitacion_id = request.GET.get('capacitacion', '')
    estado = request.GET.get('estado', '')
    
    # Iniciar queryset base
    asignaciones = EmpleadoCapacitacion.objects.all().order_by('-fecha_asignacion')
    
    # Aplicar filtros
    if empleado_id:
        asignaciones = asignaciones.filter(empleado_id=empleado_id)
    
    if capacitacion_id:
        asignaciones = asignaciones.filter(capacitacion_id=capacitacion_id)
    
    if estado:
        asignaciones = asignaciones.filter(estado=estado)
    
    # Paginación
    paginator = Paginator(asignaciones, 15)
    page_number = request.GET.get('page', 1)
    asignaciones_paginadas = paginator.get_page(page_number)
    
    # Datos para los filtros selectores
    empleados = Empleado.objects.filter(estado='activo').order_by('apellido', 'nombre')
    capacitaciones = Capacitacion.objects.all().order_by('nombre')
    
    context = {
        'asignaciones': asignaciones_paginadas,
        'empleados': empleados,
        'capacitaciones': capacitaciones,
        'estados': EmpleadoCapacitacion.ESTADO_CHOICES,
        'empleado_filtro': empleado_id,
        'capacitacion_filtro': capacitacion_id,
        'estado_filtro': estado,
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'capacitaciones'
    }
    
    return render(request, 'dashboard/recursos_humanos/capacitaciones_asignadas_listado.html', context)

@login_required
@require_module_access('recursos_humanos')
def evaluacion_crear(request, empleado_id=None):
    """Vista para crear una evaluación para un empleado"""
    
    empleado_inicial = None
    if empleado_id:
        empleado_inicial = get_object_or_404(Empleado, id=empleado_id)
    
    if request.method == 'POST':
        form = EvaluacionForm(request.POST)
        if form.is_valid():
            evaluacion = form.save()
            messages.success(request, f"Evaluación registrada para {evaluacion.empleado}.")
            
            if 'volver_empleado' in request.POST and empleado_id:
                return redirect('dashboard:rrhh_empleado_detalle', empleado_id=empleado_id)
            else:
                return redirect('dashboard:rrhh_evaluaciones_listado')
        else:
            messages.error(request, "Error al registrar la evaluación. Revisa los datos ingresados.")
    else:
        # Buscar quién es el evaluador (usuario actual)
        evaluador = None
        try:
            evaluador = Empleado.objects.get(usuario=request.user)
        except Empleado.DoesNotExist:
            pass
        
        initial_data = {
            'empleado': empleado_inicial,
            'evaluador': evaluador,
            'fecha': timezone.now().date(),
        }
        form = EvaluacionForm(initial=initial_data)
    
    # Datos para los selectores
    empleados = Empleado.objects.filter(estado='activo').order_by('apellido', 'nombre')
    evaluadores = Empleado.objects.filter(
        estado='activo',
        roles__permisos__contains={'recursos_humanos': {'acceso': True}}
    ).order_by('apellido', 'nombre').distinct()
    
    context = {
        'form': form,
        'empleados': empleados,
        'evaluadores': evaluadores,
        'empleado_seleccionado': empleado_inicial,
        'fecha_actual': timezone.now().date(),
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'evaluaciones',
        'accion': 'crear'
    }
    
    return render(request, 'dashboard/recursos_humanos/evaluacion_form.html', context)

@login_required
@require_module_access('recursos_humanos')
def evaluaciones_listado(request):
    """Vista para listar todas las evaluaciones"""
    
    # Filtros
    empleado_id = request.GET.get('empleado', '')
    evaluador_id = request.GET.get('evaluador', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    # Iniciar queryset base
    evaluaciones = Evaluacion.objects.all().order_by('-fecha')
    
    # Aplicar filtros
    if empleado_id:
        evaluaciones = evaluaciones.filter(empleado_id=empleado_id)
    
    if evaluador_id:
        evaluaciones = evaluaciones.filter(evaluador_id=evaluador_id)
    
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            evaluaciones = evaluaciones.filter(fecha__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            evaluaciones = evaluaciones.filter(fecha__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    # Paginación
    paginator = Paginator(evaluaciones, 15)
    page_number = request.GET.get('page', 1)
    evaluaciones_paginadas = paginator.get_page(page_number)
    
    # Datos para los filtros selectores
    empleados = Empleado.objects.filter(estado='activo').order_by('apellido', 'nombre')
    evaluadores = Empleado.objects.filter(evaluaciones_realizadas__isnull=False).distinct().order_by('apellido', 'nombre')
    
    context = {
        'evaluaciones': evaluaciones_paginadas,
        'empleados': empleados,
        'evaluadores': evaluadores,
        'empleado_filtro': empleado_id,
        'evaluador_filtro': evaluador_id,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'evaluaciones'
    }
    
    return render(request, 'dashboard/recursos_humanos/evaluaciones_listado.html', context)

@login_required
@require_module_access('recursos_humanos')
def vacaciones_solicitar(request, empleado_id=None):
    """Vista para solicitar vacaciones o permisos"""
    
    empleado_inicial = None
    if empleado_id:
        empleado_inicial = get_object_or_404(Empleado, id=empleado_id)
    
    if request.method == 'POST':
        form = VacacionForm(request.POST)
        if form.is_valid():
            vacacion = form.save()
            messages.success(request, f"Solicitud de {vacacion.get_tipo_display()} registrada para {vacacion.empleado}.")
            
            if 'volver_empleado' in request.POST and empleado_id:
                return redirect('dashboard:rrhh_empleado_detalle', empleado_id=empleado_id)
            else:
                return redirect('dashboard:rrhh_vacaciones_listado')
        else:
            messages.error(request, "Error al registrar la solicitud. Revisa los datos ingresados.")
    else:
        initial_data = {
            'empleado': empleado_inicial,
            'fecha_solicitud': timezone.now().date(),
        }
        form = VacacionForm(initial=initial_data)
    
    # Datos para los selectores
    empleados = Empleado.objects.filter(estado='activo').order_by('apellido', 'nombre')
    aprobadores = Empleado.objects.filter(
        estado='activo',
        roles__permisos__contains={'recursos_humanos': {'acceso': True}}
    ).order_by('apellido', 'nombre').distinct()
    
    context = {
        'form': form,
        'empleados': empleados,
        'aprobadores': aprobadores,
        'empleado_seleccionado': empleado_inicial,
        'fecha_actual': timezone.now().date(),
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'vacaciones',
        'accion': 'solicitar'
    }
    
    return render(request, 'dashboard/recursos_humanos/vacacion_form.html', context)

@login_required
@require_module_access('recursos_humanos')
def vacaciones_listado(request):
    """Vista para listar todas las solicitudes de vacaciones y permisos"""
    
    # Filtros
    empleado_id = request.GET.get('empleado', '')
    tipo = request.GET.get('tipo', '')
    estado = request.GET.get('estado', '')
    
    # Iniciar queryset base
    vacaciones = Vacacion.objects.all().order_by('-fecha_solicitud')
    
    # Aplicar filtros
    if empleado_id:
        vacaciones = vacaciones.filter(empleado_id=empleado_id)
    
    if tipo:
        vacaciones = vacaciones.filter(tipo=tipo)
    
    if estado:
        vacaciones = vacaciones.filter(estado=estado)
    
    # Paginación
    paginator = Paginator(vacaciones, 15)
    page_number = request.GET.get('page', 1)
    vacaciones_paginadas = paginator.get_page(page_number)
    
    # Datos para los filtros selectores
    empleados = Empleado.objects.filter(estado='activo').order_by('apellido', 'nombre')
    
    context = {
        'vacaciones': vacaciones_paginadas,
        'empleados': empleados,
        'tipos_vacacion': Vacacion.TIPO_CHOICES,
        'estados_vacacion': Vacacion.ESTADO_CHOICES,
        'empleado_filtro': empleado_id,
        'tipo_filtro': tipo,
        'estado_filtro': estado,
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'vacaciones'
    }
    
    return render(request, 'dashboard/recursos_humanos/vacaciones_listado.html', context)

@login_required
@require_module_access('recursos_humanos')
@require_POST
def vacacion_aprobar(request, vacacion_id):
    """Vista para aprobar una solicitud de vacaciones"""
    
    vacacion = get_object_or_404(Vacacion, id=vacacion_id)
    
    # Verificar si el usuario actual puede aprobar
    try:
        aprobador = Empleado.objects.get(usuario=request.user)
        vacacion.estado = 'aprobada'
        vacacion.aprobada_por = aprobador
        vacacion.fecha_aprobacion = timezone.now().date()
        vacacion.save()
        
        # Actualizar estado del empleado si es vacación y empieza hoy o antes
        if vacacion.tipo == 'vacaciones' and vacacion.fecha_inicio <= timezone.now().date():
            empleado = vacacion.empleado
            empleado.estado = 'vacaciones'
            empleado.save()
        
        messages.success(request, f"Solicitud de {vacacion.get_tipo_display()} aprobada.")
    except Empleado.DoesNotExist:
        messages.error(request, "No tienes permisos para aprobar esta solicitud.")
    
    return redirect('dashboard:rrhh_vacaciones_listado')

@login_required
@require_module_access('recursos_humanos')
@require_POST
def vacacion_rechazar(request, vacacion_id):
    """Vista para rechazar una solicitud de vacaciones"""
    
    vacacion = get_object_or_404(Vacacion, id=vacacion_id)
    
    try:
        aprobador = Empleado.objects.get(usuario=request.user)
        vacacion.estado = 'rechazada'
        vacacion.aprobada_por = aprobador  # Usar el mismo campo para registrar quién rechazó
        vacacion.fecha_aprobacion = timezone.now().date()
        vacacion.save()
        
        messages.success(request, f"Solicitud de {vacacion.get_tipo_display()} rechazada.")
    except Empleado.DoesNotExist:
        messages.error(request, "No tienes permisos para rechazar esta solicitud.")
    
    return redirect('dashboard:rrhh_vacaciones_listado')

@login_required
@require_module_access('recursos_humanos')
def nomina_generar(request, empleado_id=None):
    """Vista para generar una nómina de pago"""
    
    empleado_inicial = None
    if empleado_id:
        empleado_inicial = get_object_or_404(Empleado, id=empleado_id)
    
    if request.method == 'POST':
        form = NominaForm(request.POST)
        if form.is_valid():
            nomina = form.save()
            messages.success(request, f"Nómina generada para {nomina.empleado}.")
            
            if 'volver_empleado' in request.POST and empleado_id:
                return redirect('dashboard:rrhh_empleado_detalle', empleado_id=empleado_id)
            else:
                return redirect('dashboard:rrhh_nominas_listado')
        else:
            messages.error(request, "Error al generar la nómina. Revisa los datos ingresados.")
    else:
        # Si hay empleado preseleccionado, cargar su salario base
        salario_base = None
        if empleado_inicial:
            salario_base = empleado_inicial.salario_base
        
        # Determinar el período actual (mes y año)
        ahora = timezone.now()
        periodo = f"{ahora.strftime('%B')} {ahora.year}"
        
        initial_data = {
            'empleado': empleado_inicial,
            'periodo': periodo,
            'salario_base': salario_base,
            'fecha_calculo': ahora.date(),
        }
        form = NominaForm(initial=initial_data)
    
    # Datos para los selectores
    empleados = Empleado.objects.filter(estado='activo').order_by('apellido', 'nombre')
    
    context = {
        'form': form,
        'empleados': empleados,
        'empleado_seleccionado': empleado_inicial,
        'fecha_actual': timezone.now().date(),
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'nominas',
        'accion': 'generar'
    }
    
    return render(request, 'dashboard/recursos_humanos/nomina_form.html', context)

@login_required
@require_module_access('recursos_humanos')
def nominas_listado(request):
    """Vista para listar todas las nóminas generadas"""
    
    # Filtros
    empleado_id = request.GET.get('empleado', '')
    periodo = request.GET.get('periodo', '')
    estado = request.GET.get('estado', '')
    
    # Iniciar queryset base
    nominas = Nomina.objects.all().order_by('-fecha_calculo')
    
    # Aplicar filtros
    if empleado_id:
        nominas = nominas.filter(empleado_id=empleado_id)
    
    if periodo:
        nominas = nominas.filter(periodo__icontains=periodo)
    
    if estado:
        nominas = nominas.filter(estado=estado)
    
    # Paginación
    paginator = Paginator(nominas, 15)
    page_number = request.GET.get('page', 1)
    nominas_paginadas = paginator.get_page(page_number)
    
    # Datos para los filtros selectores
    empleados = Empleado.objects.filter(estado='activo').order_by('apellido', 'nombre')
    
    # Obtener períodos únicos
    periodos = Nomina.objects.values_list('periodo', flat=True).distinct().order_by('-periodo')
    
    # Estadísticas del mes actual
    from datetime import datetime
    mes_actual = datetime.now().month
    ano_actual = datetime.now().year
    
    nominas_mes_actual = Nomina.objects.filter(
        fecha_calculo__month=mes_actual,
        fecha_calculo__year=ano_actual
    )
    
    nominas_pagadas = nominas_mes_actual.filter(estado='pagada').count()
    nominas_pendientes = nominas_mes_actual.filter(estado='pendiente').count()
    total_pagado = nominas_mes_actual.filter(estado='pagada').aggregate(
        total=Sum('total_neto')
    )['total'] or 0
    
    # Promedio de salario - corregido para usar salario_base
    from django.db.models import Avg
    promedio_salario = Empleado.objects.filter(estado='activo').aggregate(
        promedio=Avg('salario_base')
    )['promedio'] or 0
    
    # Generar datos para selects
    import calendar
    meses = [(i, calendar.month_name[i]) for i in range(1, 13)]
    anos = list(range(ano_actual - 2, ano_actual + 2))
    
    context = {
        'nominas': nominas_paginadas,
        'empleados': empleados,
        'periodos': periodos,
        'estados_nomina': Nomina.ESTADO_CHOICES if hasattr(Nomina, 'ESTADO_CHOICES') else [('pendiente', 'Pendiente'), ('pagada', 'Pagada'), ('cancelada', 'Cancelada')],
        'empleado_filtro': empleado_id,
        'periodo_filtro': periodo,
        'estado_filtro': estado,
        'nominas_pagadas': nominas_pagadas,
        'nominas_pendientes': nominas_pendientes,
        'total_pagado': total_pagado,
        'promedio_salario': promedio_salario,
        'meses': meses,
        'anos': anos,
        'sucursales': Sucursal.objects.all(),
        'is_paginated': nominas_paginadas.has_other_pages(),
        'page_obj': nominas_paginadas,
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'nominas'
    }
    
    return render(request, 'dashboard/recursos_humanos/nominas_listado.html', context)

@login_required
@require_module_access('recursos_humanos')
@require_POST
def nomina_aprobar(request, nomina_id):
    """Vista para aprobar una nómina"""
    
    nomina = get_object_or_404(Nomina, id=nomina_id)
    
    if nomina.estado != 'borrador' and nomina.estado != 'pendiente':
        messages.error(request, f"No se puede aprobar una nómina en estado {nomina.get_estado_display()}")
        return redirect('dashboard:rrhh_nominas_listado')
    
    nomina.estado = 'aprobada'
    nomina.aprobada_por = request.user
    nomina.save()
    
    messages.success(request, f"Nómina de {nomina.empleado} aprobada correctamente.")
    return redirect('dashboard:rrhh_nominas_listado')

@login_required
@require_module_access('recursos_humanos')
@require_POST
def nomina_pagar(request, nomina_id):
    """Vista para marcar una nómina como pagada"""
    
    nomina = get_object_or_404(Nomina, id=nomina_id)
    
    if nomina.estado != 'aprobada':
        messages.error(request, "Solo se pueden pagar nóminas que estén aprobadas.")
        return redirect('dashboard:rrhh_nominas_listado')
    
    nomina.estado = 'pagada'
    nomina.fecha_pago = timezone.now().date()
    nomina.save()
    
    messages.success(request, f"Nómina de {nomina.empleado} marcada como pagada.")
    return redirect('dashboard:rrhh_nominas_listado')

@login_required
@require_module_access('recursos_humanos')
def estadisticas(request):
    """Vista para mostrar estadísticas de RRHH"""
    
    # Total de empleados por estado
    empleados_por_estado = Empleado.objects.values('estado').annotate(
        total=Count('id')
    ).order_by('estado')
    
    # Total de empleados por sucursal
    empleados_por_sucursal = Sucursal.objects.annotate(
        total_empleados=Count('empleado')
    ).values('nombre', 'total_empleados').order_by('-total_empleados')
    
    # Total de empleados por rol
    empleados_por_rol = Rol.objects.annotate(
        total_empleados=Count('empleado')
    ).values('nombre', 'total_empleados').order_by('-total_empleados')
    
    # Empleados con más capacitaciones
    empleados_capacitados = Empleado.objects.annotate(
        total_capacitaciones=Count('capacitaciones')
    ).filter(total_capacitaciones__gt=0).order_by('-total_capacitaciones')[:10]
    
    # Obtener datos para gráfica de asistencia mensual
    ahora = timezone.now()
    primer_dia_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # Asistencias del mes actual, agrupadas por día
    asistencias_mes = Asistencia.objects.filter(
        fecha__gte=primer_dia_mes
    ).values('fecha').annotate(
        total=Count('id')
    ).order_by('fecha')
    
    # Convertir a formato para gráficas
    fechas = [a['fecha'].strftime('%d-%m') for a in asistencias_mes]
    totales = [a['total'] for a in asistencias_mes]
    
    context = {
        'empleados_por_estado': empleados_por_estado,
        'empleados_por_sucursal': empleados_por_sucursal,
        'empleados_por_rol': empleados_por_rol,
        'empleados_capacitados': empleados_capacitados,
        'fechas_asistencia': json.dumps(fechas),
        'totales_asistencia': json.dumps(totales),
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'estadisticas'
    }
    
    return render(request, 'dashboard/recursos_humanos/estadisticas.html', context)

@login_required
@require_module_access('recursos_humanos')
def exportar_empleados_csv(request):
    """Exportar lista de empleados a CSV"""
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="empleados.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Nombre', 'Apellido', 'RUT', 'Email', 'Teléfono',
        'Fecha Ingreso', 'Estado', 'Cargo', 'Salario Base',
        'Roles', 'Sucursales'
    ])
    
    empleados = Empleado.objects.all().order_by('apellido', 'nombre')
    
    for empleado in empleados:
        roles = ', '.join([rol.nombre for rol in empleado.roles.all()])
        sucursales = ', '.join([suc.nombre for suc in empleado.sucursales.all()])
        
        writer.writerow([
            empleado.id,
            empleado.nombre,
            empleado.apellido,
            empleado.rut,
            empleado.email,
            empleado.telefono,
            empleado.fecha_ingreso,
            empleado.get_estado_display(),
            empleado.cargo,
            empleado.salario_base,
            roles,
            sucursales
        ])
    
    return response

@login_required
@require_module_access('recursos_humanos')
def exportar_asistencias_csv(request):
    """Exportar registros de asistencia a CSV"""
    
    # Filtros opcionales
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="asistencias.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Empleado', 'RUT', 'Fecha', 'Hora Entrada', 'Hora Salida',
        'Horas Trabajadas', 'Turno', 'Sucursal', 'Observaciones'
    ])
    
    # Iniciar queryset base
    asistencias = Asistencia.objects.all().order_by('-fecha', 'empleado__apellido')
    
    # Aplicar filtros
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            asistencias = asistencias.filter(fecha__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            asistencias = asistencias.filter(fecha__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    for asistencia in asistencias:
        # Calcular horas trabajadas
        horas_trabajadas = ''
        if asistencia.hora_salida:
            diferencia = asistencia.hora_salida - asistencia.hora_entrada
            horas_trabajadas = f"{diferencia.total_seconds() / 3600:.2f}"
        
        writer.writerow([
            asistencia.id,
            f"{asistencia.empleado.nombre} {asistencia.empleado.apellido}",
            asistencia.empleado.rut,
            asistencia.fecha,
            asistencia.hora_entrada.strftime('%H:%M'),
            asistencia.hora_salida.strftime('%H:%M') if asistencia.hora_salida else '',
            horas_trabajadas,
            asistencia.turno.nombre if asistencia.turno else '',
            asistencia.sucursal.nombre,
            asistencia.observaciones or ''
        ])
    
    return response

# API endpoints para usar con AJAX

@login_required
@require_module_access('recursos_humanos')
@require_GET
def api_empleado_info(request, empleado_id):
    """API para obtener información de un empleado"""
    
    try:
        empleado = Empleado.objects.get(id=empleado_id)
        data = {
            'id': empleado.id,
            'nombre': empleado.nombre,
            'apellido': empleado.apellido,
            'nombre_completo': f"{empleado.nombre} {empleado.apellido}",
            'rut': empleado.rut,
            'email': empleado.email,
            'telefono': empleado.telefono,
            'cargo': empleado.cargo,
            'salario_base': float(empleado.salario_base),
            'estado': empleado.estado,
            'fecha_ingreso': empleado.fecha_ingreso.strftime('%Y-%m-%d'),
            'sucursales': [{'id': s.id, 'nombre': s.nombre} for s in empleado.sucursales.all()],
            'roles': [{'id': r.id, 'nombre': r.nombre} for r in empleado.roles.all()],
        }
        return JsonResponse({'success': True, 'empleado': data})
    except Empleado.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Empleado no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_module_access('recursos_humanos')
@require_GET
def api_obtener_turnos_empleado(request, empleado_id):
    """API para obtener los turnos asignados a un empleado"""
    
    try:
        # Obtener fecha actual
        ahora = timezone.now().date()
        
        # Buscar asignaciones de turno vigentes
        asignaciones = AsignacionTurno.objects.filter(
            empleado_id=empleado_id,
            fecha_inicio__lte=ahora
        ).filter(
            Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=ahora)
        ).select_related('turno', 'sucursal')
        
        data = []
        for asignacion in asignaciones:
            turno_data = {
                'id': asignacion.id,
                'turno_id': asignacion.turno.id,
                'turno_nombre': asignacion.turno.nombre,
                'hora_inicio': asignacion.turno.hora_inicio.strftime('%H:%M'),
                'hora_fin': asignacion.turno.hora_fin.strftime('%H:%M'),
                'dias': {
                    'lunes': asignacion.turno.lunes,
                    'martes': asignacion.turno.martes,
                    'miercoles': asignacion.turno.miercoles,
                    'jueves': asignacion.turno.jueves,
                    'viernes': asignacion.turno.viernes,
                    'sabado': asignacion.turno.sabado,
                    'domingo': asignacion.turno.domingo,
                },
                'sucursal_id': asignacion.sucursal.id,
                'sucursal_nombre': asignacion.sucursal.nombre,
                'fecha_inicio': asignacion.fecha_inicio.strftime('%Y-%m-%d'),
                'fecha_fin': asignacion.fecha_fin.strftime('%Y-%m-%d') if asignacion.fecha_fin else None,
            }
            data.append(turno_data)
        
        return JsonResponse({'success': True, 'turnos': data})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_module_access('recursos_humanos')
@require_POST
def api_marcar_notificacion_leida(request, notificacion_id):
    """API para marcar una notificación como leída"""
    
    try:
        notificacion = Notificacion.objects.get(id=notificacion_id, usuario=request.user)
        notificacion.marcar_como_leida()
        return JsonResponse({'success': True})
    except Notificacion.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Notificación no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def asistencia_listado(request):
    """Vista para listar asistencias con filtros"""
    
    # Obtener parámetros
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    empleado_filtro = request.GET.get('empleado', '')
    estado_filtro = request.GET.get('estado', 'todos')
    sucursal_filtro = request.GET.get('sucursal', '')
    
    # Si no hay fechas, usar el mes actual
    if not fecha_desde:
        fecha_desde = timezone.now().date().replace(day=1)
    else:
        fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
    
    if not fecha_hasta:
        fecha_hasta = timezone.now().date()
    else:
        fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    
    # Consulta base
    asistencias = Asistencia.objects.filter(
        fecha__gte=fecha_desde,
        fecha__lte=fecha_hasta
    ).select_related('empleado').order_by('-fecha', 'empleado__apellido')
    
    # Aplicar filtros
    if empleado_filtro:
        asistencias = asistencias.filter(empleado__id=empleado_filtro)
    
    if estado_filtro != 'todos':
        asistencias = asistencias.filter(estado=estado_filtro)
    
    if sucursal_filtro:
        asistencias = asistencias.filter(empleado__sucursales__id=sucursal_filtro)
    
    # Paginación
    paginator = Paginator(asistencias, 20)
    page_number = request.GET.get('page')
    asistencias = paginator.get_page(page_number)
    
    # Estadísticas del período
    total_registros = asistencias.paginator.count
    presentes = Asistencia.objects.filter(
        fecha__gte=fecha_desde,
        fecha__lte=fecha_hasta,
        estado='presente'
    ).count()
    ausentes = Asistencia.objects.filter(
        fecha__gte=fecha_desde,
        fecha__lte=fecha_hasta,
        estado='ausente'
    ).count()
    tardanzas = Asistencia.objects.filter(
        fecha__gte=fecha_desde,
        fecha__lte=fecha_hasta,
        estado='tarde'
    ).count()
    
    # Datos para filtros
    empleados = Empleado.objects.filter(estado='activo').order_by('apellido', 'nombre')
    sucursales = Sucursal.objects.all()
    
    # Generar datos para el calendario
    calendario_data = {}
    asistencias_all = Asistencia.objects.filter(
        fecha__gte=fecha_desde,
        fecha__lte=fecha_hasta
    ).values('fecha', 'estado').annotate(total=Count('id'))
    
    for item in asistencias_all:
        fecha_str = item['fecha'].strftime('%Y-%m-%d')
        if fecha_str not in calendario_data:
            calendario_data[fecha_str] = {'presente': 0, 'ausente': 0, 'tarde': 0, 'justificado': 0}
        calendario_data[fecha_str][item['estado']] = item['total']
    
    context = {
        'asistencias': asistencias,
        'empleados': empleados,
        'sucursales': sucursales,
        'fecha_desde': fecha_desde.strftime('%Y-%m-%d'),
        'fecha_hasta': fecha_hasta.strftime('%Y-%m-%d'),
        'empleado_filtro': empleado_filtro,
        'estado_filtro': estado_filtro,
        'sucursal_filtro': sucursal_filtro,
        'total_registros': total_registros,
        'presentes': presentes,
        'ausentes': ausentes,
        'tardanzas': tardanzas,
        'calendario_data': json.dumps(calendario_data),
    }
    
    return render(request, 'dashboard/recursos_humanos/asistencia_listado.html', context)

@login_required
def asistencia_registro_rapido(request):
    """Vista para registro rápido de asistencia"""
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            empleado_id = data.get('empleado_id')
            tipo_accion = data.get('accion', 'entrada')  # entrada, salida
            
            empleado = get_object_or_404(Empleado, id=empleado_id)
            fecha_actual = timezone.now().date()
            hora_actual = timezone.now().time()
            
            # Buscar registro de asistencia del día
            asistencia, created = Asistencia.objects.get_or_create(
                empleado=empleado,
                fecha=fecha_actual,
                defaults={
                    'estado': 'presente',
                    'hora_entrada': hora_actual if tipo_accion == 'entrada' else None,
                    'hora_salida': hora_actual if tipo_accion == 'salida' else None,
                }
            )
            
            if not created:
                # Actualizar registro existente
                if tipo_accion == 'entrada' and not asistencia.hora_entrada:
                    asistencia.hora_entrada = hora_actual
                elif tipo_accion == 'salida' and not asistencia.hora_salida:
                    asistencia.hora_salida = hora_actual
                
                # Determinar estado basado en la hora de entrada
                # Nota: El campo estado no existe en el modelo, pero mantenemos la lógica para el futuro
                
                asistencia.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Registro de {tipo_accion} exitoso para {empleado.nombre}',
                'hora': hora_actual.strftime('%H:%M'),
                'estado': calcular_estado_asistencia(asistencia)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    # GET request: mostrar formulario
    empleados_activos = Empleado.objects.filter(estado='activo').order_by('apellido', 'nombre')
    
    # Asistencias de hoy
    fecha_hoy = timezone.now().date()
    asistencias_hoy = Asistencia.objects.filter(fecha=fecha_hoy).select_related('empleado')
    
    # Organizar datos para el template
    empleados_con_asistencia = {}
    for asistencia in asistencias_hoy:
        empleados_con_asistencia[asistencia.empleado.id] = {
            'entrada': asistencia.hora_entrada,
            'salida': asistencia.hora_salida,
            'estado': calcular_estado_asistencia(asistencia),
        }
    
    context = {
        'empleados': empleados_activos,
        'asistencias_hoy': empleados_con_asistencia,
        'fecha_actual': fecha_hoy,
        'hora_actual': timezone.now().time(),
    }
    
    return render(request, 'dashboard/recursos_humanos/asistencia_registro.html', context)

@login_required
def turnos_listado_alternativo(request):
    """Vista alternativa para listar turnos de trabajo"""
    
    # Obtener parámetros de filtro
    sucursal_filtro = request.GET.get('sucursal', '')
    
    # Obtener turnos básicos
    turnos = Turno.objects.all().order_by('hora_inicio')
    
    # Obtener asignaciones de turnos para la semana actual
    hoy = timezone.now().date()
    dias_desde_lunes = hoy.weekday()
    semana_inicio = hoy - timedelta(days=dias_desde_lunes)
    semana_fin = semana_inicio + timedelta(days=6)
    
    asignaciones = AsignacionTurno.objects.filter(
        fecha_inicio__lte=semana_fin,
        fecha_fin__gte=semana_inicio
    ).select_related('empleado', 'turno').order_by('fecha_inicio')
    
    if sucursal_filtro:
        asignaciones = asignaciones.filter(empleado__sucursales__id=sucursal_filtro)
    
    # Sucursales para filtro
    sucursales = Sucursal.objects.all()
    
    # Datos para navegación de semanas
    semana_anterior = semana_inicio - timedelta(days=7)
    semana_siguiente = semana_inicio + timedelta(days=7)
    
    context = {
        'turnos': turnos,
        'asignaciones': asignaciones,
        'semana_inicio': semana_inicio,
        'semana_fin': semana_fin,
        'semana_anterior': semana_anterior,
        'semana_siguiente': semana_siguiente,
        'sucursales': sucursales,
        'sucursal_filtro': sucursal_filtro,
        'seccion_activa': 'recursos-humanos',
        'subseccion': 'turnos'
    }
    
    return render(request, 'dashboard/recursos_humanos/turnos_listado.html', context)
