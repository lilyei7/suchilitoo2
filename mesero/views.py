from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from restaurant.models import ProductoVenta, CategoriaProducto
# Usar el modelo Mesa de mesero, no el de dashboard
from .models import Orden, OrdenItem, HistorialMesa, HistorialOrden, Mesa
from collections import defaultdict
import json
from inventario_automatico import InventarioAutomatico

def obtener_productos_menu():
    """
    Función helper para obtener productos activos organizados por categoría
    Reutilizable en todas las vistas que necesiten mostrar el menú
    """
    from django.db import connection
    
    # Obtener productos activos de la base de datos organizados por categoría
    productos_activos = ProductoVenta.objects.filter(
        disponible=True  # Solo productos disponibles/activos
    ).select_related('categoria').order_by('categoria__orden', 'categoria__nombre', 'nombre')
    
    # Organizar productos por categoría
    productos_por_categoria = defaultdict(list)
    
    for producto in productos_activos:
        categoria_nombre = producto.categoria.nombre if producto.categoria else 'Sin Categoría'
        
        # Obtener personalizaciones disponibles para este producto
        personalizaciones = []
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT o.id, o.nombre, o.tipo, o.precio_extra
                FROM mesero_opcionpersonalizacion o
                JOIN mesero_productopersonalizacion pp ON o.id = pp.opcion_id
                WHERE pp.producto_id = %s AND pp.activa = 1 AND o.activa = 1
                ORDER BY o.tipo, o.nombre
            """, [producto.id])
            
            rows = cursor.fetchall()
            for row in rows:
                personalizaciones.append({
                    'id': row[0],
                    'nombre': row[1],
                    'tipo': row[2],
                    'precio_extra': float(row[3])
                })
        
        # Convertir el producto a un diccionario para el template
        producto_data = {
            'id': producto.id,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion or 'Sin descripción disponible',
            'precio': float(producto.precio),
            'imagen': producto.imagen.url if producto.imagen else None,
            'disponible': producto.disponible,
            'tiempo_preparacion': getattr(producto, 'tiempo_preparacion', 15),  # Default 15 min
            'calorias': producto.calorias or 0,
            'tipo': producto.get_tipo_display(),
            'es_promocion': producto.es_promocion,
            'destacado': producto.destacado,
            'personalizaciones': personalizaciones,  # Añadir personalizaciones
        }
        
        productos_por_categoria[categoria_nombre].append(producto_data)
    
    # Convertir defaultdict a dict regular para el template
    productos_por_categoria = dict(productos_por_categoria)
    
    # Si no hay productos, mostrar un mensaje de ejemplo
    if not productos_por_categoria:
        productos_por_categoria = {
            'Información': [
                {
                    'id': 0,
                    'nombre': 'Sin productos disponibles',
                    'descripcion': 'No hay productos activos en el menú. Contacta al administrador.',
                    'precio': 0.00,
                    'imagen': None,
                    'disponible': False,
                    'tiempo_preparacion': 0,
                    'calorias': 0
                }
            ]
        }
    
    return productos_por_categoria

def login_view(request):
    """Vista de login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Inicio de sesión exitoso')
            return redirect('mesero:menu')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'mesero/login.html')

@login_required
def menu(request):
    """Vista del menú usando productos reales de la base de datos"""
    debug_info = {
        'view': 'menu_moderno',
        'path': request.path,
        'user': request.user.username,
        'authenticated': request.user.is_authenticated,
        'session': request.session.session_key,
    }
    
    productos_por_categoria = obtener_productos_menu()
    
    # Obtener estadísticas para debug
    total_productos = sum(len(productos) for productos in productos_por_categoria.values())
    total_categorias = len(productos_por_categoria)
    
    context = {
        'debug_info': debug_info,
        'productos_por_categoria': productos_por_categoria,
        'total_productos': total_productos,
        'total_categorias': total_categorias,
    }
    
    print(f"DEBUG - Menú mesero: {total_categorias} categorías, {total_productos} productos")
    for categoria, productos in productos_por_categoria.items():
        print(f"  - {categoria}: {len(productos)} productos")
    
    return render(request, 'mesero/menu_moderno.html', context)

@login_required
def orders(request):
    """Vista de pedidos del mesero"""
    # Obtener órdenes del mesero ordenadas por fecha más reciente
    ordenes = Orden.objects.filter(
        mesero=request.user
    ).select_related('mesa').prefetch_related('items__producto').order_by('-fecha_creacion')
    
    # Procesar las órdenes para el template
    pedidos = []
    for orden in ordenes:
        items = []
        for item in orden.items.all():
            items.append({
                'nombre': item.producto.nombre,
                'cantidad': item.cantidad,
                'precio_unitario': float(item.precio_unitario),
                'subtotal': float(item.subtotal)
            })
        
        pedidos.append({
            'id': orden.id,
            'mesa': orden.mesa.numero,
            'estado': orden.get_estado_display(),
            'estado_code': orden.estado,
            'hora': orden.fecha_creacion.strftime('%H:%M'),
            'fecha': orden.fecha_creacion.strftime('%d/%m/%Y'),
            'total': float(orden.total),
            'items': items,
            'notas': orden.observaciones or '',
        })
    
    return render(request, 'mesero/orders.html', {'pedidos': pedidos})

@login_required
@csrf_exempt
def liberar_mesa(request, orden_id):
    """Liberar mesa desde interface del mesero"""
    try:
        orden = get_object_or_404(Orden, id=orden_id, mesero=request.user)
        
        # Verificar que la orden esté en un estado que permita liberación
        if orden.estado not in ['lista', 'entregada']:
            return JsonResponse({
                'success': False,
                'message': f'La orden debe estar lista o entregada para liberar la mesa. Estado actual: {orden.get_estado_display()}'
            })
        
        mesa_numero = orden.mesa.numero if orden.mesa else 'Sin mesa'
        
        # Cambiar estado a cerrada para liberar mesa
        orden.cambiar_estado('cerrada', request.user, 'Mesa liberada por mesero')
        
        return JsonResponse({
            'success': True,
            'message': f'Mesa {mesa_numero} liberada exitosamente',
            'mesa_numero': mesa_numero
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al liberar mesa: {str(e)}'
        })

@login_required
@csrf_exempt
def cancelar_orden(request, orden_id):
    """Cancelar orden desde interface del mesero"""
    try:
        orden = get_object_or_404(Orden, id=orden_id, mesero=request.user)
        
        # Verificar que la orden esté en un estado que permita cancelación
        if orden.estado not in ['pendiente', 'confirmada']:
            return JsonResponse({
                'success': False,
                'message': f'No se puede cancelar una orden en estado: {orden.get_estado_display()}'
            })
        
        # Cambiar estado a cancelada
        orden.cambiar_estado('cancelada', request.user, 'Orden cancelada por mesero')
        
        return JsonResponse({
            'success': True,
            'message': 'Orden cancelada exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al cancelar orden: {str(e)}'
        })

@login_required
def seleccionar_mesa(request):
    """Vista para seleccionar la mesa a atender"""
    # Depuración: Mostrar información del usuario y su sucursal
    print(f"DEBUG: Usuario actual: {request.user.username}")
    print(f"DEBUG: Sucursal del usuario: {request.user.sucursal}")
    
    # Verificar que el usuario tenga sucursal asignada
    if not request.user.sucursal:
        messages.error(request, 'Tu usuario no tiene una sucursal asignada. Contacta al administrador.')
        return redirect('mesero:login')

    # Obtener mesas solo de la sucursal del mesero logueado
    mesas = Mesa.objects.filter(
        sucursal=request.user.sucursal,
        activa=True  # Usando 'activa' en lugar de 'activo'
    ).order_by('numero')
    
    # Depuración: Mostrar información de la consulta
    print(f"DEBUG: Consultando mesas para sucursal: {request.user.sucursal}")
    print(f"DEBUG: Total mesas encontradas: {mesas.count()}")
    print(f"DEBUG: Mesas: {list(mesas.values_list('id', 'numero', 'sucursal__nombre'))}")

    # Actualizar estados basados en órdenes activas
    for mesa in mesas:
        ordenes_activas = Orden.objects.filter(
            mesa=mesa,
            estado__in=['pendiente', 'en_preparacion', 'lista']  # Usando 'lista' en lugar de 'listo'
        ).exists()
        
        if ordenes_activas and mesa.estado == 'disponible':
            mesa.estado = 'ocupada'
            mesa.save()
        elif not ordenes_activas and mesa.estado == 'ocupada':
            mesa.estado = 'disponible'
            mesa.save()

    # Preparar datos para el template
    mesas_info = [{
        'id': mesa.id,
        'numero': mesa.numero,
        'capacidad': mesa.capacidad,
        'estado': mesa.get_estado_display()
    } for mesa in mesas]
    
    # Depuración: Datos que se pasan al template
    print(f"DEBUG: Datos enviados al template: {mesas_info}")

    context = {
        'mesas': mesas_info,
        'sucursal': request.user.sucursal,
        'mesero': request.user
    }

    return render(request, 'mesero/seleccionar_mesa.html', context)

@login_required
def nueva_orden(request, mesa_id=None):
    """Vista para crear una nueva orden usando productos reales de la base de datos"""
    if mesa_id is None:
        # Si no se especificó una mesa, redirigir a la selección de mesa
        messages.info(request, 'Selecciona una mesa para crear una nueva orden')
        return redirect('mesero:seleccionar_mesa')
    
    # Verificar que el usuario tenga sucursal asignada
    if not request.user.sucursal:
        messages.error(request, 'Tu usuario no tiene una sucursal asignada. Contacta al administrador.')
        return redirect('mesero:login')
    
    # Obtener y validar la mesa
    try:
        mesa = Mesa.objects.get(
            id=mesa_id,
            sucursal=request.user.sucursal,
            activa=True  # Usando 'activa' en lugar de 'activo'
        )
    except Mesa.DoesNotExist:
        messages.error(request, 'Mesa no encontrada o no pertenece a tu sucursal.')
        return redirect('mesero:seleccionar_mesa')
        
    if request.method == 'POST':
        # Procesar el formulario de la orden
        # Esto en producción guardaría la orden en la base de datos
        items_seleccionados = request.POST.getlist('items')
        messages.success(request, f'Orden creada correctamente para Mesa #{mesa.numero}')
        return redirect('mesero:orders')
    
    productos_por_categoria = obtener_productos_menu()
    
    context = {
        'mesa': mesa,
        'mesa_id': mesa_id,
        'productos_por_categoria': productos_por_categoria,
    }
    
    return render(request, 'mesero/nueva_orden.html', context)

def logout_view(request):
    """Cerrar sesión del usuario mesero"""
    logout(request)
    messages.info(request, 'Sesión finalizada correctamente')
    return redirect('mesero:login')

@login_required
@csrf_exempt
def crear_orden(request):
    """Vista AJAX para crear una nueva orden desde el menú con descuento automático de inventario"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mesa_id = data.get('mesa_id')
            items = data.get('items', [])
            notas = data.get('notas', '')
            
            if not mesa_id:
                return JsonResponse({
                    'success': False, 
                    'error': 'Debe seleccionar una mesa'
                })
            
            if not items:
                return JsonResponse({
                    'success': False, 
                    'error': 'Debe agregar al menos un producto'
                })
            
            # Verificar que el usuario tenga sucursal asignada
            if not request.user.sucursal:
                return JsonResponse({
                    'success': False, 
                    'error': 'Usuario sin sucursal asignada'
                })
            
            # Obtener y validar la mesa
            try:
                mesa = Mesa.objects.get(
                    id=mesa_id,
                    sucursal=request.user.sucursal,
                    activa=True
                )
            except Mesa.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'error': 'Mesa no encontrada o no pertenece a tu sucursal'
                })
            
            # 🆕 VERIFICAR STOCK DISPONIBLE ANTES DE CREAR LA ORDEN
            inventario_automatico = InventarioAutomatico(request.user.sucursal)
            
            # Verificar stock para cada item
            stock_faltante = []
            for item_data in items:
                producto = get_object_or_404(ProductoVenta, id=item_data['id'])
                cantidad = int(item_data['cantidad'])
                
                # Verificar stock disponible
                stock_ok, faltantes = inventario_automatico.verificar_stock_disponible(producto, cantidad)
                
                if not stock_ok:
                    stock_faltante.extend([
                        {
                            'producto': producto.nombre,
                            'cantidad_solicitada': cantidad,
                            'faltantes': faltantes
                        }
                    ])
            
            # Si hay stock faltante, retornar error
            if stock_faltante:
                error_msg = "Stock insuficiente para los siguientes productos:\n"
                for faltante in stock_faltante:
                    error_msg += f"• {faltante['producto']} (cantidad: {faltante['cantidad_solicitada']})\n"
                    for item in faltante['faltantes']:
                        if 'error' in item:
                            error_msg += f"  - Error: {item['error']}\n"
                        else:
                            error_msg += f"  - {item['insumo']}: necesario {item['necesario']} {item['unidad']}, disponible {item['disponible']} {item['unidad']}\n"
                
                return JsonResponse({
                    'success': False,
                    'error': error_msg,
                    'stock_faltante': stock_faltante
                })
            
            # Crear la orden
            orden = Orden.objects.create(
                mesa=mesa,
                mesero=request.user,
                estado='pendiente',
                observaciones=notas
            )
            
            # Agregar los items a la orden
            total = 0
            for item_data in items:
                producto = get_object_or_404(ProductoVenta, id=item_data['id'])
                cantidad = int(item_data['cantidad'])
                precio_unitario = producto.precio
                
                # Calcular precio extra por personalizaciones
                precio_extra_personalizaciones = 0
                personalizaciones = item_data.get('personalizaciones', [])
                
                if personalizaciones:
                    from .models import OpcionPersonalizacion
                    for personalizacion_id in personalizaciones:
                        try:
                            opcion = OpcionPersonalizacion.objects.get(id=personalizacion_id, activa=True)
                            precio_extra_personalizaciones += opcion.precio_extra
                        except OpcionPersonalizacion.DoesNotExist:
                            continue
                
                # Precio final por unidad incluyendo personalizaciones
                precio_final_unitario = precio_unitario + precio_extra_personalizaciones
                
                # Crear el item de orden
                orden_item = OrdenItem.objects.create(
                    orden=orden,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_final_unitario,
                    observaciones=item_data.get('observaciones', '')  # Agregar las observaciones del producto
                )
                
                # Guardar las personalizaciones del item
                if personalizaciones:
                    from .models import OpcionPersonalizacion, OrdenItemPersonalizacion
                    for personalizacion_id in personalizaciones:
                        try:
                            opcion = OpcionPersonalizacion.objects.get(id=personalizacion_id, activa=True)
                            OrdenItemPersonalizacion.objects.create(
                                orden_item=orden_item,
                                opcion=opcion,
                                precio_aplicado=opcion.precio_extra
                            )
                        except OpcionPersonalizacion.DoesNotExist:
                            continue
                
                total += orden_item.calcular_subtotal()
            
            # Actualizar el total de la orden
            orden.total = total
            orden.save()
            
            # 🆕 DESCONTAR INVENTARIO AUTOMÁTICAMENTE
            try:
                inventario_success, inventario_messages = inventario_automatico.procesar_orden(orden)
                
                if not inventario_success:
                    # Si falla el descuento de inventario, eliminar la orden
                    orden.delete()
                    return JsonResponse({
                        'success': False,
                        'error': 'Error al descontar inventario: ' + '\n'.join(inventario_messages[-3:])
                    })
                
                # Log del inventario para debugging
                print(f"📦 Inventario descontado para orden #{orden.numero_orden}")
                for msg in inventario_messages:
                    print(f"  {msg}")
                    
            except Exception as e:
                # Si falla el descuento de inventario, eliminar la orden
                orden.delete()
                return JsonResponse({
                    'success': False,
                    'error': f'Error al procesar inventario: {str(e)}'
                })
            
            # Actualizar el estado de la mesa
            mesa.estado = 'ocupada'
            mesa.save()
            
            # Crear historial
            HistorialOrden.objects.create(
                orden=orden,
                estado_anterior='',
                estado_nuevo='pendiente',
                usuario=request.user,
                observaciones=f'Orden creada con {len(items)} items - Inventario descontado automáticamente'
            )
            
            return JsonResponse({
                'success': True,
                'orden_id': orden.id,
                'mesa_numero': mesa.numero,
                'total': float(total),
                'message': f'Orden creada exitosamente para Mesa #{mesa.numero}\nInventario actualizado automáticamente',
                'inventario_info': inventario_messages[-5:] if len(inventario_messages) > 5 else inventario_messages
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f'Error al crear la orden: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def actualizar_estado_orden(request, orden_id):
    """Vista para actualizar el estado de una orden"""
    if request.method == 'POST':
        orden = get_object_or_404(Orden, id=orden_id, mesero=request.user)
        nuevo_estado = request.POST.get('estado')
        
        if nuevo_estado in ['pendiente', 'en_preparacion', 'listo', 'entregado', 'cancelado']:
            estado_anterior = orden.estado
            orden.estado = nuevo_estado
            orden.save()
            
            # Si la orden se marca como entregada o cancelada, liberar la mesa
            if nuevo_estado in ['entregado', 'cancelado']:
                # Verificar si hay otras órdenes activas en la mesa
                otras_ordenes = Orden.objects.filter(
                    mesa=orden.mesa,
                    estado__in=['pendiente', 'en_preparacion', 'listo']
                ).exclude(id=orden.id).exists()
                
                if not otras_ordenes:
                    orden.mesa.estado = 'disponible'
                    orden.mesa.save()
            
            # Crear historial
            HistorialOrden.objects.create(
                orden=orden,
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado,
                usuario=request.user
            )
            
            messages.success(request, f'Estado de la orden #{orden.id} actualizado a {orden.get_estado_display()}')
        else:
            messages.error(request, 'Estado no válido')
    
    return redirect('mesero:orders')

@login_required
def seleccionar_mesa_modal(request):
    """Vista AJAX para mostrar las mesas disponibles en un modal"""
    # Verificar que el usuario tenga sucursal asignada
    if not request.user.sucursal:
        return JsonResponse({
            'error': 'Usuario sin sucursal asignada',
            'mesas': []
        }, status=400)
    
    # Obtener mesas solo de la sucursal del mesero logueado
    mesas = Mesa.objects.filter(
        sucursal=request.user.sucursal,
        activa=True  # Usando 'activa' en lugar de 'activo'
    ).order_by('numero')
    
    # Actualizar estados basado en órdenes activas
    for mesa in mesas:
        ordenes_activas = Orden.objects.filter(
            mesa=mesa, 
            estado__in=['pendiente', 'en_preparacion', 'lista']  # Usando 'lista' en lugar de 'listo'
        ).exists()
        mesa.tiene_ordenes_activas = ordenes_activas
    
    return JsonResponse({
        'success': True,
        'sucursal': request.user.sucursal.nombre,
        'mesas': [
            {
                'id': mesa.id,
                'numero': mesa.numero,
                'capacidad': mesa.capacidad,
                'estado': mesa.estado,
                'tiene_ordenes_activas': mesa.tiene_ordenes_activas,
                'disponible': not mesa.tiene_ordenes_activas
            }
            for mesa in mesas
        ]
    })

@login_required
def detalle_producto(request, producto_id):
    """Vista AJAX para obtener detalles de un producto"""
    try:
        producto = get_object_or_404(ProductoVenta, id=producto_id)
        
        # Construir los datos del producto
        producto_data = {
            'id': producto.id,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion or 'Sin descripción disponible',
            'precio': float(producto.precio),
            'imagen': producto.imagen.url if producto.imagen else None,
            'disponible': producto.disponible,
            'tiempo_preparacion': getattr(producto, 'tiempo_preparacion', 15),
            'calorias': producto.calorias or 0,
            'tipo': producto.get_tipo_display(),
            'es_promocion': producto.es_promocion,
            'destacado': producto.destacado,
            'categoria': producto.categoria.nombre if producto.categoria else 'Sin categoría',
        }
        
        return JsonResponse({
            'success': True,
            'producto': producto_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener detalles del producto: {str(e)}'
        })

@login_required
def inventario_status(request):
    """Vista para mostrar el estado del inventario"""
    if not request.user.sucursal:
        messages.error(request, 'Usuario sin sucursal asignada')
        return redirect('mesero:dashboard')
    
    # Obtener inventario con stock bajo
    from restaurant.models import Inventario, Insumo
    
    inventarios = Inventario.objects.filter(
        sucursal=request.user.sucursal
    ).select_related('insumo').order_by('insumo__nombre')
    
    # Identificar productos con stock bajo
    stock_bajo = []
    stock_critico = []
    
    for inventario in inventarios:
        porcentaje_stock = 0
        if inventario.insumo.stock_minimo > 0:
            porcentaje_stock = (inventario.cantidad_disponible / inventario.insumo.stock_minimo) * 100
        
        if inventario.cantidad_disponible <= inventario.insumo.stock_minimo:
            if inventario.cantidad_disponible <= (inventario.insumo.stock_minimo * 0.5):
                stock_critico.append({
                    'inventario': inventario,
                    'porcentaje': porcentaje_stock
                })
            else:
                stock_bajo.append({
                    'inventario': inventario,
                    'porcentaje': porcentaje_stock
                })
    
    # Obtener movimientos recientes
    from restaurant.models import MovimientoInventario
    
    movimientos_recientes = MovimientoInventario.objects.filter(
        sucursal=request.user.sucursal
    ).select_related('insumo').order_by('-created_at')[:10]
    
    context = {
        'inventarios': inventarios,
        'stock_bajo': stock_bajo,
        'stock_critico': stock_critico,
        'movimientos_recientes': movimientos_recientes,
        'total_inventarios': inventarios.count(),
        'total_stock_bajo': len(stock_bajo),
        'total_stock_critico': len(stock_critico),
    }
    
    return render(request, 'mesero/inventario_status.html', context)

@login_required
def verificar_stock_producto(request, producto_id):
    """Vista AJAX para verificar stock de un producto específico"""
    if not request.user.sucursal:
        return JsonResponse({
            'success': False,
            'error': 'Usuario sin sucursal asignada'
        })
    
    try:
        from inventario_automatico import InventarioAutomatico
        
        producto = get_object_or_404(ProductoVenta, id=producto_id)
        cantidad = int(request.GET.get('cantidad', 1))
        
        inventario_automatico = InventarioAutomatico(request.user.sucursal)
        stock_ok, faltantes = inventario_automatico.verificar_stock_disponible(producto, cantidad)
        
        return JsonResponse({
            'success': True,
            'stock_ok': stock_ok,
            'faltantes': faltantes,
            'producto': producto.nombre,
            'cantidad': cantidad
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })