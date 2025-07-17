from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from accounts.models import Usuario, Sucursal
from restaurant.models import ProductoVenta, CheckListEjecucion
from datetime import datetime
from .base_views import get_sidebar_context

@login_required
def productos_venta_view(request):
    """Vista para gestionar productos de venta"""
    productos = ProductoVenta.objects.filter(disponible=True)
    
    context = {
        'productos': productos,
        **get_sidebar_context('productos_venta')
    }
    
    return render(request, 'dashboard/productos_venta.html', context)

@login_required
def reportes_view(request):
    """Vista para reportes"""
    context = {
        'titulo': 'Reportes',
        **get_sidebar_context('reportes')
    }
    
    return render(request, 'dashboard/reportes.html', context)

@login_required
def ventas_view(request):
    """Vista para gestionar ventas"""
    # Aquí agregarás la lógica de ventas más adelante
    context = {
        'mensaje': 'Módulo de ventas en desarrollo',
        **get_sidebar_context('ventas')
    }
    
    return render(request, 'dashboard/ventas.html', context)

@login_required
def checklist_view(request):
    """Vista para gestionar checklists"""
    # Obtener checklist del día
    hoy = datetime.now().date()
    ejecuciones_hoy = CheckListEjecucion.objects.filter(
        fecha=hoy,
        sucursal=request.user.sucursal
    ) if request.user.sucursal else CheckListEjecucion.objects.filter(fecha=hoy)
    
    context = {
        'ejecuciones_hoy': ejecuciones_hoy,
        'fecha': hoy,
        **get_sidebar_context('checklist')
    }
    
    return render(request, 'dashboard/checklist.html', context)

@login_required
def recursos_humanos_view(request):
    """Vista para gestionar recursos humanos"""
    from rrhh.models import Empleado, Rol
    from accounts.models import Sucursal
    from django.utils import timezone
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    # Obtener datos para estadísticas
    total_empleados = Empleado.objects.count()
    empleados_activos = Empleado.objects.filter(estado='activo').count()
    empleados_nuevos = Empleado.objects.filter(
        fecha_ingreso__month=timezone.now().month,
        fecha_ingreso__year=timezone.now().year
    ).count()
    
    # Datos para gráficos - usar las relaciones ManyToMany correctas
    try:
        # Para sucursales: relación ManyToMany a través de la tabla intermedia
        sucursales = Sucursal.objects.annotate(
            num_empleados=Count('empleado', filter=Q(empleado__estado='activo'))
        ).filter(num_empleados__gt=0)
    except:
        # Si hay error, obtener todas las sucursales activas
        sucursales = Sucursal.objects.filter(activa=True)
    
    try:
        # Para roles: relación ManyToMany a través de la tabla intermedia
        roles = Rol.objects.annotate(
            num_empleados=Count('empleado', filter=Q(empleado__estado='activo'))
        ).filter(num_empleados__gt=0)
    except:
        # Si hay error, obtener todos los roles
        roles = Rol.objects.all()
    
    # Empleados con contratos próximos a vencer
    contratos_por_vencer = Empleado.objects.filter(
        fecha_termino__isnull=False,
        fecha_termino__lte=timezone.now().date() + timedelta(days=30),
        estado='activo'
    )[:5]  # Solo los primeros 5
    
    # Notificaciones (ejemplo)
    notificaciones = []
    
    context = {
        'total_empleados': total_empleados,
        'empleados_activos': empleados_activos,
        'empleados_nuevos': empleados_nuevos,
        'sucursales': sucursales,
        'roles': roles,
        'contratos_por_vencer': contratos_por_vencer,
        'notificaciones': notificaciones,
        'fecha_actual': timezone.now(),
        'hora_actual': timezone.now(),
        **get_sidebar_context('recursos_humanos')
    }
    
    return render(request, 'dashboard/recursos_humanos/index.html', context)
