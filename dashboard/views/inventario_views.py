from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.core.paginator import Paginator
from datetime import datetime

from restaurant.models import Inventario, MovimientoInventario, CategoriaInsumo, UnidadMedida, Insumo as RestaurantInsumo
from dashboard.views.base_views import get_sidebar_context

# Usamos el Insumo de restaurant para tener consistencia
Insumo = RestaurantInsumo

@login_required
def inventario_view(request):
    # En lugar de mostrar inventarios por sucursal, mostrar insumos únicos
    insumos = Insumo.objects.all()
    
    # Filtros
    categoria = request.GET.get('categoria')
    if categoria:
        insumos = insumos.filter(categoria__id=categoria)
    
    buscar = request.GET.get('buscar')
    if buscar:
        insumos = insumos.filter(
            Q(nombre__icontains=buscar) |
            Q(codigo__icontains=buscar)
        )
    
    estado = request.GET.get('estado')
    if estado == 'bajo':
        # Mostrar insumos que tienen stock bajo en cualquier sucursal
        insumos_con_stock_bajo = Inventario.objects.filter(
            cantidad_actual__lte=F('insumo__stock_minimo')
        ).values_list('insumo_id', flat=True).distinct()
        insumos = insumos.filter(id__in=insumos_con_stock_bajo)
    elif estado == 'normal':
        # Mostrar insumos que tienen stock normal en todas las sucursales
        insumos_con_stock_bajo = Inventario.objects.filter(
            cantidad_actual__lte=F('insumo__stock_minimo')
        ).values_list('insumo_id', flat=True).distinct()
        insumos = insumos.exclude(id__in=insumos_con_stock_bajo)
    
    # Obtener categorías para el filtro
    categorias = CategoriaInsumo.objects.all()
    
    # Obtener unidades de medida para los modales
    unidades = UnidadMedida.objects.all()
    
    # Obtener sucursal del usuario para contexto (opcional)
    sucursal = request.user.sucursal
    
    context = {
        'insumos': insumos,
        'categorias': categorias,
        'unidades': unidades,
        'sucursal': sucursal,
        **get_sidebar_context('inventario')
    }
    
    return render(request, 'dashboard/inventario.html', context)

@login_required
def entradas_salidas_view(request):
    """Vista para gestionar entradas y salidas de inventario"""
    # Obtener movimientos de inventario
    movimientos = MovimientoInventario.objects.all().order_by('-created_at')
    
    # Filtrar por sucursal del usuario si no es admin
    if request.user.sucursal and not request.user.is_superuser:
        movimientos = movimientos.filter(sucursal=request.user.sucursal)
    
    # Filtros de búsqueda
    buscar = request.GET.get('buscar')
    if buscar:
        movimientos = movimientos.filter(
            Q(insumo__nombre__icontains=buscar) |
            Q(usuario__first_name__icontains=buscar) |
            Q(usuario__last_name__icontains=buscar) |
            Q(motivo__icontains=buscar)
        )
    
    tipo = request.GET.get('tipo')
    if tipo and tipo != 'todos':
        movimientos = movimientos.filter(tipo_movimiento=tipo)
    
    sucursal_id = request.GET.get('sucursal')
    if sucursal_id and sucursal_id != 'todas':
        movimientos = movimientos.filter(sucursal_id=sucursal_id)
    
    fecha = request.GET.get('fecha')
    if fecha:
        movimientos = movimientos.filter(created_at__date=fecha)
    
    # Paginación
    paginator = Paginator(movimientos, 25)
    page_number = request.GET.get('page')
    movimientos = paginator.get_page(page_number)
    
    # Obtener sucursales para el filtro
    from accounts.models import Sucursal
    sucursales = Sucursal.objects.filter(activa=True)
    
    context = {
        'movimientos': movimientos,
        'sucursales': sucursales,
        **get_sidebar_context('entradas_salidas')
    }
    
    return render(request, 'dashboard/entradas_salidas.html', context)
