from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, F, Value, DecimalField, Avg, Count
from django.urls import reverse
from restaurant.models import ProductoVenta, CategoriaProducto, Receta, ProductoReceta
from decimal import Decimal
import json

@login_required
def lista_productos_venta_moderna(request):
    """Vista moderna que muestra la lista de productos de venta en un grid con tarjetas"""
    productos = ProductoVenta.objects.all().order_by('categoria__nombre', 'nombre')
    categorias = CategoriaProducto.objects.filter(activo=True).order_by('nombre')
    
    # Filtros por categoría, estado o búsqueda
    categoria_id = request.GET.get('categoria')
    estado = request.GET.get('estado')
    query = request.GET.get('q')
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if estado:
        if estado == 'disponible':
            productos = productos.filter(disponible=True)
        elif estado == 'no-disponible':
            productos = productos.filter(disponible=False)
        elif estado == 'promocion':
            productos = productos.filter(es_promocion=True)
    
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | 
            Q(codigo__icontains=query) | 
            Q(descripcion__icontains=query)
        )
    
    # Estadísticas para el dashboard
    productos_disponibles = productos.filter(disponible=True).count()
    productos_promocion = productos.filter(es_promocion=True).count()
    precio_promedio = productos.aggregate(promedio=Avg('precio'))['promedio'] or 0
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_id,
        'estado': estado,
        'query': query,
        'productos_disponibles': productos_disponibles,
        'productos_promocion': productos_promocion,
        'precio_promedio': precio_promedio,
    }
    
    return render(request, 'dashboard/productos_venta.html', context)

# Las demás funciones (crear_producto_venta, editar_producto_venta, etc.) se mantienen igual
