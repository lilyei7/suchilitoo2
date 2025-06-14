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
