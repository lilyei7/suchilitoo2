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
    usuarios = Usuario.objects.filter(activo=True)
    
    context = {
        'usuarios': usuarios,
        **get_sidebar_context('recursos_humanos')
    }
    
    return render(request, 'dashboard/recursos_humanos.html', context)
