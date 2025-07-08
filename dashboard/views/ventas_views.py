from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
import json
from decimal import Decimal

from restaurant.models import ProductoVenta, Receta, RecetaInsumo
from dashboard.models import HistorialPrecios
from accounts.models import Sucursal
from dashboard.views.base_views import get_sidebar_context

@login_required
def ventas_view(request):
    """Vista principal del módulo de ventas con integración de costos"""
    
    # Determinar qué sucursales puede ver el usuario
    user = request.user
    
    if user.is_superuser or (user.rol and user.rol.nombre == 'admin'):
        sucursales = Sucursal.objects.filter(activa=True)
        sucursal_filtro = None
    elif user.rol and user.rol.nombre == 'gerente' and user.sucursal:
        sucursales = Sucursal.objects.filter(id=user.sucursal.id, activa=True)
        sucursal_filtro = user.sucursal
    else:
        if user.sucursal:
            sucursales = Sucursal.objects.filter(id=user.sucursal.id, activa=True)
            sucursal_filtro = user.sucursal
        else:
            sucursales = Sucursal.objects.none()
            sucursal_filtro = None
    
    # Obtener productos disponibles para venta
    productos = ProductoVenta.objects.filter(disponible=True)
    
    # Productos con receta (para calcular costos)
    productos_con_receta = ProductoVenta.objects.filter(
        disponible=True, 
        receta__isnull=False
    ).select_related('receta')
    
    context = {
        'productos': productos,
        'productos_con_receta': productos_con_receta,
        'sucursales': sucursales,
        'sucursal_filtro': sucursal_filtro,
        'current_view': 'ventas',
        'sidebar_active': 'ventas',
        **get_sidebar_context('ventas')
    }
    
    return render(request, 'dashboard/ventas.html', context)

@login_required
def venta_producto_api(request):
    """API para registrar venta de un producto y descontar inventario"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        producto_id = data.get('producto_id')
        cantidad = Decimal(str(data.get('cantidad', 1)))
        sucursal_id = data.get('sucursal_id')
        metodo_costeo = data.get('metodo_costeo', 'peps')  # 'peps' o 'promedio'
        
        if not producto_id or not sucursal_id or cantidad <= 0:
            return JsonResponse({'success': False, 'message': 'Parámetros inválidos'}, status=400)
        
        # Obtener producto y verificar que tenga receta
        producto = get_object_or_404(ProductoVenta, id=producto_id, disponible=True)
        sucursal = get_object_or_404(Sucursal, id=sucursal_id, activa=True)
        
        try:
            receta = Receta.objects.get(producto=producto)
        except Receta.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': f'El producto {producto.nombre} no tiene una receta asociada para descontar inventario'
            }, status=400)
        
        # Obtener insumos de la receta
        insumos_receta = RecetaInsumo.objects.filter(receta=receta)
        
        if not insumos_receta:
            return JsonResponse({
                'success': False, 
                'message': f'La receta de {producto.nombre} no tiene insumos asociados'
            }, status=400)
        
        # Realizar la operación en una transacción
        with transaction.atomic():
            costo_total = Decimal('0')
            detalles = []
            
            # Procesar cada insumo de la receta
            for item in insumos_receta:
                insumo = item.insumo
                cantidad_insumo = item.cantidad * cantidad  # Cantidad por número de productos
                
                # Descontar stock según el método elegido
                if metodo_costeo == 'peps':
                    # Usar PEPS para descontar stock y calcular costo
                    costo_item, movimiento = HistorialPrecios.descontar_stock_peps(
                        insumo,
                        cantidad_insumo,
                        sucursal,
                        f"Venta de {producto.nombre} - {cantidad} unidad(es)"
                    )
                else:
                    # Implementar método promedio si se requiere
                    # Por ahora usamos PEPS
                    costo_item, movimiento = HistorialPrecios.descontar_stock_peps(
                        insumo,
                        cantidad_insumo,
                        sucursal,
                        f"Venta de {producto.nombre} - {cantidad} unidad(es)"
                    )
                
                costo_total += costo_item
                
                detalles.append({
                    'insumo_id': insumo.id,
                    'insumo_nombre': insumo.nombre,
                    'cantidad_utilizada': float(cantidad_insumo),
                    'costo': float(costo_item),
                    'unidad': insumo.unidad_medida.abreviacion
                })
            
            # Aquí se podría registrar la venta en un modelo de Ventas si existiera
            
            # Calcular margen de ganancia
            precio_venta_total = producto.precio * cantidad
            margen = (precio_venta_total - costo_total) / costo_total * 100 if costo_total > 0 else 0
            
            return JsonResponse({
                'success': True,
                'message': f'Se ha registrado la venta de {cantidad} {producto.nombre} y descontado el inventario',
                'producto': {
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'codigo': producto.codigo
                },
                'cantidad': float(cantidad),
                'precio_unitario': float(producto.precio),
                'precio_total': float(precio_venta_total),
                'costo_total': float(costo_total),
                'margen': float(margen),
                'fecha': timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
                'detalles': detalles
            })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
