from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from accounts.models import Usuario, Sucursal
from restaurant.models import Inventario, MovimientoInventario, ProductoVenta
from django.db.models import F
from datetime import datetime

def get_sidebar_context(view_name):
    """
    Función auxiliar para obtener el contexto del sidebar activo
    """
    sidebar_context = {
        'current_view': view_name,
        'sidebar_active': view_name,
        'inventario_section_active': view_name in [
            'inventario', 'entradas_salidas', 'insumos_compuestos', 
            'insumos_elaborados', 'proveedores', 'recetas', 'reportes'
        ],
        'cajero_section_active': view_name in [
            'cajero_dashboard', 'punto_venta', 'ordenes_activas', 'historial_ventas',
            'apertura_caja', 'cierre_caja', 'admin_mesas'
        ],
        'checklist_section_active': view_name in [
            # Standard names
            'checklist_dashboard', 'checklist_incidents', 'checklist_notifications', 
            'manage_categories', 'manage_tasks', 'task_history',
            # Alternative names
            'categorias_checklist', 'tareas_checklist', 'historial_checklist', 'notificaciones_checklist',
            'checklist_categories', 'checklist_tasks', 'checklist_history',
            # Generic checklist name
            'checklist'
        ]
    }
    return sidebar_context

def is_admin_or_manager(user):
    """Verifica si el usuario es admin o gerente"""
    return user.is_superuser or (user.rol and user.rol.nombre in ['admin', 'gerente'])

def is_admin(user):
    """Verifica si el usuario es admin o superusuario"""
    return user.is_superuser or (user.rol and user.rol.nombre == 'admin')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:principal')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard:principal')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'dashboard/login.html')

def logout_view(request):
    logout(request)
    return redirect('dashboard:login')

@login_required
def principal_view(request):
    # Estadísticas generales
    total_sucursales = Sucursal.objects.filter(activa=True).count()
    total_usuarios = Usuario.objects.filter(activo=True).count()
    total_productos = ProductoVenta.objects.filter(disponible=True).count()
    
    # Insumos con stock bajo
    insumos_stock_bajo = Inventario.objects.filter(
        cantidad_actual__lte=F('insumo__stock_minimo')
    ).count()
    
    # Movimientos recientes
    movimientos_hoy = MovimientoInventario.objects.filter(
        created_at__date=datetime.now().date()
    ).count()
    
    context = {
        'total_sucursales': total_sucursales,
        'total_usuarios': total_usuarios,
        'total_productos': total_productos,
        'insumos_stock_bajo': insumos_stock_bajo,
        'movimientos_hoy': movimientos_hoy,
        'usuario': request.user,
        **get_sidebar_context('principal')
    }
    
    return render(request, 'dashboard/principal.html', context)

@login_required
def checklist_redirect_view(request):
    """
    Redirecciona a la vista mejorada de checklist
    """
    return redirect('dashboard:checklist_dashboard')
