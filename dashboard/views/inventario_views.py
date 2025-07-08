from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.core.paginator import Paginator
from datetime import datetime
from django.http import JsonResponse

from restaurant.models import Inventario, MovimientoInventario, CategoriaInsumo, UnidadMedida, Insumo as RestaurantInsumo
from dashboard.views.base_views import get_sidebar_context
from dashboard.utils.permissions import require_module_access, require_submodule_access

# Usamos el Insumo de restaurant para tener consistencia
Insumo = RestaurantInsumo

@login_required
@require_submodule_access('inventario', 'insumos')
def inventario_view(request):
    """Vista principal del inventario con filtrado por sucursal según permisos"""
    
    user = request.user
    
    # Determinar qué sucursales puede ver el usuario
    if user.is_superuser or (user.rol and user.rol.nombre == 'admin'):
        # Admin puede ver todas las sucursales
        from accounts.models import Sucursal
        sucursales_disponibles = Sucursal.objects.filter(activa=True)
        sucursal_filtro = None
        es_admin = True
    elif user.rol and user.rol.nombre == 'gerente' and user.sucursal:
        # Gerente solo ve su sucursal asignada
        from accounts.models import Sucursal
        sucursales_disponibles = Sucursal.objects.filter(id=user.sucursal.id, activa=True)
        sucursal_filtro = user.sucursal
        es_admin = False
    else:
        # Otros usuarios: pueden ver su sucursal si la tienen asignada
        if user.sucursal:
            from accounts.models import Sucursal
            sucursales_disponibles = Sucursal.objects.filter(id=user.sucursal.id, activa=True)
            sucursal_filtro = user.sucursal
            es_admin = False
        else:
            # Sin sucursal asignada, no pueden ver inventario
            from accounts.models import Sucursal
            sucursales_disponibles = Sucursal.objects.none()
            sucursal_filtro = None
            es_admin = False
    
    # Filtro por sucursal desde la URL (solo para admin)
    sucursal_seleccionada_id = request.GET.get('sucursal')
    if es_admin and sucursal_seleccionada_id and sucursal_seleccionada_id != 'todas':
        try:
            from accounts.models import Sucursal
            sucursal_filtro = Sucursal.objects.get(id=sucursal_seleccionada_id, activa=True)
        except Sucursal.DoesNotExist:
            sucursal_filtro = None
    
    # Obtener insumos basados en los inventarios de las sucursales que puede ver
    if sucursal_filtro:
        # Filtro específico por sucursal
        inventarios_base = Inventario.objects.filter(sucursal=sucursal_filtro)
        insumos_ids = inventarios_base.values_list('insumo_id', flat=True).distinct()
        insumos = Insumo.objects.filter(id__in=insumos_ids, activo=True)
    elif es_admin:
        # Admin sin filtro: mostrar todos los insumos que tienen inventario en alguna sucursal
        insumos_con_inventario = Inventario.objects.values_list('insumo_id', flat=True).distinct()
        insumos = Insumo.objects.filter(id__in=insumos_con_inventario, activo=True)
    else:
        # Sin permisos o sin sucursal
        insumos = Insumo.objects.none()
      
    # Aplicar filtros adicionales
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
        # Mostrar insumos que tienen stock bajo
        if sucursal_filtro:
            # En la sucursal específica
            insumos_con_stock_bajo = Inventario.objects.filter(
                cantidad_actual__lte=F('insumo__stock_minimo'),
                sucursal=sucursal_filtro
            ).values_list('insumo_id', flat=True).distinct()
        elif es_admin:
            # En cualquier sucursal (para admin sin filtro)
            insumos_con_stock_bajo = Inventario.objects.filter(
                cantidad_actual__lte=F('insumo__stock_minimo')
            ).values_list('insumo_id', flat=True).distinct()
        else:
            insumos_con_stock_bajo = []
        insumos = insumos.filter(id__in=insumos_con_stock_bajo)
    elif estado == 'normal':
        # Mostrar insumos que tienen stock normal
        if sucursal_filtro:
            # En la sucursal específica
            insumos_con_stock_bajo = Inventario.objects.filter(
                cantidad_actual__lte=F('insumo__stock_minimo'),
                sucursal=sucursal_filtro
            ).values_list('insumo_id', flat=True).distinct()
        elif es_admin:
            # En cualquier sucursal (para admin sin filtro)
            insumos_con_stock_bajo = Inventario.objects.filter(
                cantidad_actual__lte=F('insumo__stock_minimo')
            ).values_list('insumo_id', flat=True).distinct()
        else:
            insumos_con_stock_bajo = []
        insumos = insumos.exclude(id__in=insumos_con_stock_bajo)
    
    # Obtener datos de inventario para cada insumo
    insumos_con_inventario = []
    for insumo in insumos:
        # Obtener inventario según el filtro de sucursal
        if sucursal_filtro:
            inventario = Inventario.objects.filter(sucursal=sucursal_filtro, insumo=insumo).first()
            inventarios_sucursal = [inventario] if inventario else []
        elif es_admin:
            inventarios_sucursal = Inventario.objects.filter(insumo=insumo)
        else:
            inventarios_sucursal = []
          # Calcular datos agregados
        stock_total = sum(inv.cantidad_actual for inv in inventarios_sucursal if inv.cantidad_actual)
        stock_disponible = sum(inv.cantidad_disponible for inv in inventarios_sucursal if inv.cantidad_disponible)
        
        # Determinar estado del stock
        from decimal import Decimal
        if stock_total <= insumo.stock_minimo:
            estado_stock = 'bajo'
        elif stock_total <= (insumo.stock_minimo * Decimal('1.5')):
            estado_stock = 'medio'
        else:
            estado_stock = 'alto'
          # Obtener información de TODOS los proveedores para este insumo
        from dashboard.models import ProveedorInsumo
        
        proveedores_insumo = []
        
        # Agregar proveedor principal si existe
        if insumo.proveedor_principal:
            proveedores_insumo.append({
                'nombre': insumo.proveedor_principal.nombre,
                'contacto': insumo.proveedor_principal.contacto,
                'telefono': insumo.proveedor_principal.telefono,
                'tipo': 'principal'
            })
        
        # Agregar proveedores asignados
        relaciones_proveedor = ProveedorInsumo.objects.filter(
            insumo=insumo, 
            activo=True
        ).select_related('proveedor')
        
        for relacion in relaciones_proveedor:
            proveedores_insumo.append({
                'nombre': relacion.proveedor.nombre_comercial,
                'contacto': relacion.proveedor.persona_contacto,
                'telefono': relacion.proveedor.telefono,
                'tipo': 'asignado'
            })
        
        # Información del proveedor principal para mostrar en tabla (compatibilidad)
        proveedor_principal_info = None
        if proveedores_insumo:
            proveedor_principal_info = proveedores_insumo[0]  # Usar el primer proveedor disponible
        
        insumos_con_inventario.append({
            'insumo': insumo,
            'stock_actual': stock_total,  # Cambiado de stock_total a stock_actual
            'stock_disponible': stock_disponible,
            'stock_minimo': insumo.stock_minimo,
            'estado': estado_stock,  # Cambiado de estado_stock a estado
            'sucursal': sucursal_filtro,  # Agregado para facilitar el template
            'inventarios': inventarios_sucursal,
            'sucursales_con_stock': len([inv for inv in inventarios_sucursal if inv.cantidad_actual > 0]),
            # NUEVO: Información de proveedores
            'proveedores': proveedores_insumo,
            'proveedor_principal_info': proveedor_principal_info
        })
      
    # Obtener categorías para el filtro
    categorias = CategoriaInsumo.objects.all()
    
    # Obtener unidades de medida para los modales
    unidades = UnidadMedida.objects.all()
      # Calcular estadísticas
    total_insumos = len(insumos_con_inventario)
    insumos_stock_bajo = len([item for item in insumos_con_inventario if item['estado'] == 'bajo'])
    insumos_stock_alto = len([item for item in insumos_con_inventario if item['estado'] == 'alto'])
    valor_total_inventario = sum(
        item['stock_actual'] * (item['insumo'].precio_unitario or 0) 
        for item in insumos_con_inventario
    )
    
    context = {
        'insumos_con_inventario': insumos_con_inventario,
        'insumos': [item['insumo'] for item in insumos_con_inventario],  # Para compatibilidad
        'categorias': categorias,
        'unidades': unidades,
        'sucursales_disponibles': sucursales_disponibles,
        'sucursal_seleccionada': sucursal_filtro,
        'es_admin': es_admin,
        'user_sucursal': user.sucursal,
        # Estadísticas
        'total_insumos': total_insumos,
        'insumos_stock_bajo': insumos_stock_bajo,
        'insumos_stock_alto': insumos_stock_alto,
        'valor_total_inventario': valor_total_inventario,
        # Filtros actuales (para mantener en el formulario)
        'filtro_categoria': categoria,
        'filtro_buscar': buscar,
        'filtro_estado': estado,
        'filtro_sucursal': sucursal_seleccionada_id,
        **get_sidebar_context('inventario')
    }
    
    return render(request, 'dashboard/inventario.html', context)

@login_required
@require_submodule_access('inventario', 'entradas_salidas')
def entradas_salidas_view(request):
    """Vista para gestionar entradas y salidas de inventario"""
    # Obtener movimientos de inventario
    movimientos = MovimientoInventario.objects.all().order_by('-created_at')
    
    # Filtrar por sucursal del usuario si no es admin o si tiene la característica de filtrar por sucursal
    if request.user.sucursal and (
        not request.user.is_superuser or 
        (hasattr(request.user, 'has_feature') and request.user.has_feature('filtrar_por_sucursal'))
    ):
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

@login_required
@require_submodule_access('inventario', 'insumos')
def insumo_detalle_api(request, insumo_id):
    """API para obtener detalles completos de un insumo"""
    try:
        # Cargar el insumo con todas las relaciones necesarias
        insumo = Insumo.objects.select_related(
            'categoria', 
            'unidad_medida', 
            'proveedor_principal'
        ).get(id=insumo_id)
        
        # Obtener inventarios relacionados según permisos del usuario
        user = request.user
        if user.is_superuser or (user.rol and user.rol.nombre == 'admin'):
            # Admin puede ver inventarios de todas las sucursales
            inventarios = Inventario.objects.filter(insumo=insumo).select_related('sucursal')
        elif user.sucursal:
            # Otros usuarios solo ven inventario de su sucursal
            inventarios = Inventario.objects.filter(insumo=insumo, sucursal=user.sucursal).select_related('sucursal')
        else:
            # Sin sucursal, no puede ver inventarios
            inventarios = Inventario.objects.none()
        
        # Calcular stock total y estado
        stock_total = sum(inv.cantidad_actual for inv in inventarios if inv.cantidad_actual)
        
        from decimal import Decimal
        if stock_total <= insumo.stock_minimo:
            estado_stock = 'bajo'
        elif stock_total <= (insumo.stock_minimo * Decimal('1.5')):
            estado_stock = 'medio'
        else:
            estado_stock = 'alto'
          # Obtener TODOS los proveedores asignados al insumo
        from dashboard.models import ProveedorInsumo
        
        proveedores_asignados = []
        
        # 1. Agregar proveedor principal si existe
        if insumo.proveedor_principal:
            proveedores_asignados.append({
                'nombre': insumo.proveedor_principal.nombre,
                'contacto': insumo.proveedor_principal.contacto,
                'telefono': insumo.proveedor_principal.telefono,
                'email': insumo.proveedor_principal.email,
                'tipo': 'principal',
                'precio_unitario': str(insumo.precio_unitario) if insumo.precio_unitario else '',
                'tiempo_entrega': None,
                'cantidad_minima': None,
                'notas': ''
            })
        
        # 2. Agregar proveedores de las relaciones ProveedorInsumo
        relaciones_proveedor = ProveedorInsumo.objects.filter(
            insumo=insumo, 
            activo=True
        ).select_related('proveedor')
        
        for relacion in relaciones_proveedor:
            proveedores_asignados.append({
                'nombre': relacion.proveedor.nombre_comercial,
                'contacto': relacion.proveedor.persona_contacto,
                'telefono': relacion.proveedor.telefono,
                'email': relacion.proveedor.email,
                'tipo': 'asignado',
                'precio_unitario': str(relacion.precio_final()),
                'tiempo_entrega': relacion.tiempo_entrega_dias,
                'cantidad_minima': str(relacion.cantidad_minima),
                'notas': relacion.notas
            })
        
        # Información del proveedor principal para compatibilidad
        proveedor_principal_info = {
            'nombre': 'Sin proveedor asignado',
            'contacto': '',
            'telefono': '',
            'email': ''
        }
        
        if proveedores_asignados:
            # Usar el primer proveedor disponible como "principal" para compatibilidad
            primer_proveedor = proveedores_asignados[0]
            proveedor_principal_info = {
                'nombre': primer_proveedor['nombre'],
                'contacto': primer_proveedor['contacto'],
                'telefono': primer_proveedor['telefono'],
                'email': primer_proveedor['email']
            }

        # Preparar datos del insumo
        insumo_data = {
            'id': insumo.id,
            'codigo': insumo.codigo,
            'nombre': insumo.nombre,
            'descripcion': insumo.descripcion or '',
            'tipo': insumo.tipo,
            'categoria': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
            'unidad_medida': insumo.unidad_medida.nombre if insumo.unidad_medida else 'Sin unidad',
            'unidad_abreviacion': insumo.unidad_medida.abreviacion if insumo.unidad_medida else '',
            'precio_unitario': str(insumo.precio_unitario),
            'stock_actual': str(stock_total),
            'stock_minimo': str(insumo.stock_minimo),
            'estado_stock': estado_stock,
            'perecedero': insumo.perecedero,
            'dias_vencimiento': insumo.dias_vencimiento,
            # Campos de proveedor para compatibilidad (primer proveedor disponible)
            'proveedor': proveedor_principal_info['nombre'],
            'proveedor_contacto': proveedor_principal_info['contacto'],
            'proveedor_telefono': proveedor_principal_info['telefono'],
            'proveedor_email': proveedor_principal_info['email'],
            # NUEVO: Lista completa de proveedores
            'proveedores': proveedores_asignados,
            'costo_produccion': str(insumo.costo_produccion) if insumo.costo_produccion else None,
            'tiempo_preparacion': insumo.tiempo_preparacion,
            'activo': insumo.activo,
            'fecha_creacion': insumo.fecha_creacion.isoformat() if insumo.fecha_creacion else None,
            'fecha_actualizacion': insumo.fecha_actualizacion.isoformat() if insumo.fecha_actualizacion else None,
            'inventarios': [
                {
                    'sucursal': inv.sucursal.nombre,
                    'cantidad_actual': str(inv.cantidad_actual),
                    'cantidad_disponible': str(inv.cantidad_disponible or 0),
                }
                for inv in inventarios
            ]
        }
        
        return JsonResponse(insumo_data)
        
    except Insumo.DoesNotExist:
        return JsonResponse({'error': 'Insumo no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
