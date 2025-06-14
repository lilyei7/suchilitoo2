from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count, Sum, Q, F, Avg
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from decimal import Decimal
from datetime import datetime, timedelta
from restaurant.models import (
    Inventario, MovimientoInventario, ProductoVenta, 
    CheckListEjecucion, Insumo as RestaurantInsumo, CategoriaInsumo,
    UnidadMedida, Receta, CategoriaProducto, CheckListItem,
    InsumoCompuesto, InsumoElaborado, RecetaInsumo
)
from dashboard.models import Proveedor, ProveedorInsumo
from accounts.models import Usuario, Sucursal, Rol
from django.db import models

# Usamos el Insumo de restaurant para tener consistencia
Insumo = RestaurantInsumo
Categoria = CategoriaInsumo

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
    total_productos = ProductoVenta.objects.filter(disponible=True).count()    # Insumos con stock bajo
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
def inventario_view(request):
    # En lugar de mostrar inventarios por sucursal, mostrar insumos únicos
    # Ya que los insumos son globales y se dan de alta una sola vez
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
        'insumos': insumos,  # Cambiar de 'inventarios' a 'insumos'
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
    sucursales = Sucursal.objects.filter(activa=True)
    
    context = {
        'movimientos': movimientos,
        'sucursales': sucursales,
        **get_sidebar_context('entradas_salidas')
    }
    
    return render(request, 'dashboard/entradas_salidas.html', context)

@login_required
def insumos_elaborados_view(request):
    """Vista principal de insumos elaborados con funcionalidad completa"""
    # Filtrar insumos elaborados con sus componentes
    insumos_elaborados = Insumo.objects.filter(
        tipo='elaborado'
    ).select_related(
        'categoria', 'unidad_medida'
    ).prefetch_related(
        'componentes_elaborados__insumo_componente__categoria',
        'componentes_elaborados__insumo_componente__unidad_medida'
    ).order_by('nombre')
    
    # Estadísticas
    total_elaborados = insumos_elaborados.count()
    elaborados_activos = insumos_elaborados.filter(activo=True).count()
    
    context = {
        'insumos_elaborados': insumos_elaborados,
        'total_elaborados': total_elaborados,
        'elaborados_activos': elaborados_activos,
        **get_sidebar_context('insumos_elaborados')
    }
    
    return render(request, 'dashboard/insumos_elaborados.html', context)

@login_required
def productos_venta_view(request):
    productos = ProductoVenta.objects.filter(disponible=True)
    
    context = {
        'productos': productos,
        **get_sidebar_context('productos_venta')
    }
    
    return render(request, 'dashboard/productos_venta.html', context)

@login_required
def sucursales_view(request):
    # Obtener todas las sucursales (activas e inactivas para vista completa)
    sucursales = Sucursal.objects.all()
    sucursales_activas = sucursales.filter(activa=True).count()
    
    context = {
        'sucursales': sucursales,
        'sucursales_activas': sucursales_activas,
        **get_sidebar_context('sucursales')
    }
    
    return render(request, 'dashboard/sucursales.html', context)

@login_required
def ventas_view(request):
    # Aquí agregarás la lógica de ventas más adelante
    context = {
        'mensaje': 'Módulo de ventas en desarrollo',
        **get_sidebar_context('ventas')
    }
    
    return render(request, 'dashboard/ventas.html', context)

@login_required
def checklist_view(request):    # Obtener checklist del día
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
    usuarios = Usuario.objects.filter(activo=True)
    
    context = {
        'usuarios': usuarios,
        **get_sidebar_context('recursos_humanos')
    }
    
    return render(request, 'dashboard/recursos_humanos.html', context)

@login_required
def usuarios_view(request):
    usuarios = Usuario.objects.all()
      # Estadísticas para la vista
    usuarios_activos = usuarios.filter(is_active=True).count()
    usuarios_admin = usuarios.filter(
        Q(is_superuser=True) | Q(rol__nombre__in=['admin', 'gerente'])
    ).count()
    
    context = {
        'usuarios': usuarios,
        'usuarios_activos': usuarios_activos,
        'usuarios_admin': usuarios_admin,
        **get_sidebar_context('usuarios')
    }
    
    return render(request, 'dashboard/usuarios.html', context)

# ========================================================================================
# FUNCIONES CRUD PARA INSUMOS ELABORADOS
# ========================================================================================

@login_required
@user_passes_test(is_admin_or_manager)
def crear_insumo_elaborado(request):
    """Vista para crear un nuevo insumo elaborado"""
    if request.method == 'POST':
        try:
            # Importar el modelo aquí para evitar problemas de importación circular
            from restaurant.models import InsumoElaborado
            
            # Datos básicos del insumo elaborado
            codigo = request.POST.get('codigo')
            nombre = request.POST.get('nombre')
            categoria_id = request.POST.get('categoria_id')
            unidad_medida_id = request.POST.get('unidad_medida_id')
            cantidad_producida = request.POST.get('cantidad_producida')
            descripcion = request.POST.get('descripcion', '')
            tiempo_total_preparacion = request.POST.get('tiempo_total_preparacion', 0)
            
            # Validaciones
            if not all([nombre, categoria_id, unidad_medida_id, cantidad_producida]):
                return JsonResponse({
                    'success': False,
                    'message': 'Todos los campos obligatorios deben ser completados'
                })
            
            # Generar código automáticamente si no se proporciona
            if not codigo:
                numero = 1
                while True:
                    codigo = f'ELAB-{numero:03d}'
                    if not Insumo.objects.filter(codigo=codigo).exists():
                        break
                    numero += 1
                    if numero > 9999:
                        return JsonResponse({
                            'success': False,
                            'message': 'No se pudo generar un código único'
                        })
            else:
                # Verificar que el código proporcionado no exista
                if Insumo.objects.filter(codigo=codigo).exists():
                    return JsonResponse({
                        'success': False,
                        'message': f'Ya existe un insumo con el código "{codigo}"'
                    })
              # Obtener componentes del POST
            componentes_data = []
            insumo_ids = request.POST.getlist('componente_insumo[]')
            cantidades = request.POST.getlist('componente_cantidad[]')
            tiempos = request.POST.getlist('componente_tiempo[]')
            instrucciones_list = request.POST.getlist('componente_instrucciones[]')
            
            if len(insumo_ids) != len(cantidades):
                return JsonResponse({
                    'success': False,
                    'message': 'Error en los datos de componentes'
                })
              # Validar componentes
            total_costo = 0
            for i, (insumo_id, cantidad) in enumerate(zip(insumo_ids, cantidades)):
                if not insumo_id or not cantidad:
                    continue
                
                try:
                    # Permitir tanto insumos básicos como compuestos para elaborados
                    insumo_componente = Insumo.objects.get(
                        id=insumo_id, 
                        tipo__in=['basico', 'compuesto'],
                        activo=True
                    )
                    cantidad_decimal = Decimal(str(cantidad))
                    tiempo_prep = int(tiempos[i]) if i < len(tiempos) and tiempos[i] else 0
                    instrucciones = instrucciones_list[i] if i < len(instrucciones_list) else ''
                    
                    if cantidad_decimal <= 0:
                        return JsonResponse({
                            'success': False,
                            'message': f'La cantidad para {insumo_componente.nombre} debe ser mayor a 0'
                        })
                    
                    # Calcular costo usando Decimal para evitar errores de tipo
                    costo_componente = cantidad_decimal * insumo_componente.precio_unitario
                    
                    componentes_data.append({
                        'insumo': insumo_componente,
                        'cantidad': cantidad_decimal,
                        'tiempo_preparacion': tiempo_prep,
                        'instrucciones': instrucciones,
                        'costo': costo_componente
                    })
                    
                    total_costo += costo_componente
                
                except Insumo.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': f'El insumo con ID {insumo_id} no existe o no está activo'
                    })
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'message': f'Cantidad inválida para el componente {i+1}'
                    })
            
            if not componentes_data:
                return JsonResponse({
                    'success': False,
                    'message': 'Debe agregar al menos un componente'
                })
              # Crear el insumo elaborado
            categoria = CategoriaInsumo.objects.get(id=categoria_id)
            unidad_medida = UnidadMedida.objects.get(id=unidad_medida_id)
            
            # Calcular precio unitario por unidad producida usando Decimal
            cantidad_producida_decimal = Decimal(str(cantidad_producida))
            precio_unitario = total_costo / cantidad_producida_decimal
            
            insumo_elaborado = Insumo.objects.create(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                categoria=categoria,
                unidad_medida=unidad_medida,
                tipo='elaborado',
                precio_unitario=precio_unitario,
                stock_minimo=Decimal('0'),  # Se iniciará en 0
                activo=True
            )
            
            # Crear los componentes
            for i, componente_data in enumerate(componentes_data):
                InsumoElaborado.objects.create(
                    insumo_elaborado=insumo_elaborado,
                    insumo_componente=componente_data['insumo'],
                    cantidad=componente_data['cantidad'],
                    orden=i + 1,
                    tiempo_preparacion_minutos=componente_data['tiempo_preparacion'],
                    instrucciones=componente_data['instrucciones']
                )
            
            return JsonResponse({
                'success': True,
                'message': f'Insumo elaborado "{nombre}" creado exitosamente',
                'insumo_id': insumo_elaborado.id,
                'codigo': codigo,
                'costo_total': float(total_costo),
                'precio_unitario': float(precio_unitario),
                'cantidad_producida': float(cantidad_producida)
            })
            
        except Exception as e:
            print(f"Error creando insumo elaborado: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })

@login_required
def obtener_insumos_compuestos(request):
    """Vista para obtener insumos compuestos disponibles para elaborados"""
    try:
        insumos_compuestos = Insumo.objects.filter(
            tipo='compuesto', 
            activo=True
        ).select_related('categoria', 'unidad_medida').order_by('nombre')
        
        insumos_data = []
        for insumo in insumos_compuestos:
            insumos_data.append({
                'id': insumo.id,
                'codigo': insumo.codigo,
                'nombre': insumo.nombre,
                'categoria_nombre': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
                'unidad_medida_nombre': str(insumo.unidad_medida) if insumo.unidad_medida else 'Sin unidad',
                'precio_unitario': float(insumo.precio_unitario),
                'cantidad_stock': float(insumo.cantidad_stock)
            })
        
        return JsonResponse({
            'success': True,
            'insumos': insumos_data
        })
        
    except Exception as e:
        print(f"Error obteniendo insumos compuestos: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
def detalle_insumo_elaborado(request, insumo_id):
    """Vista para ver detalles de un insumo elaborado"""
    try:
        from restaurant.models import InsumoElaborado
        
        insumo = get_object_or_404(Insumo, id=insumo_id, tipo='elaborado')
        componentes = InsumoElaborado.objects.filter(
            insumo_elaborado=insumo
        ).select_related(
            'insumo_componente__categoria', 
            'insumo_componente__unidad_medida'
        ).order_by('orden')
        
        # Calcular estadísticas
        total_costo = sum(c.costo_total() for c in componentes)
        tiempo_total = sum(c.tiempo_preparacion_minutos for c in componentes)
        
        componentes_data = []
        for componente in componentes:
            componentes_data.append({
                'id': componente.id,
                'insumo_nombre': componente.insumo_componente.nombre,
                'insumo_codigo': componente.insumo_componente.codigo,
                'categoria': componente.insumo_componente.categoria.nombre if componente.insumo_componente.categoria else 'Sin categoría',
                'cantidad': float(componente.cantidad),
                'unidad_medida': str(componente.insumo_componente.unidad_medida),
                'precio_unitario': float(componente.insumo_componente.precio_unitario),
                'costo_total': float(componente.costo_total()),
                'tiempo_preparacion': componente.tiempo_preparacion_minutos,
                'instrucciones': componente.instrucciones,
                'orden': componente.orden
            })
        
        insumo_data = {
            'id': insumo.id,
            'codigo': insumo.codigo,
            'nombre': insumo.nombre,
            'descripcion': insumo.descripcion,
            'categoria': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
            'unidad_medida': str(insumo.unidad_medida),
            'precio_unitario': float(insumo.precio_unitario),
            'cantidad_stock': float(insumo.cantidad_stock),
            'activo': insumo.activo,
            'total_costo': float(total_costo),
            'tiempo_total_preparacion': tiempo_total,
            'cantidad_componentes': len(componentes_data)
        }
        
        return JsonResponse({
            'success': True,
            'insumo': insumo_data,
            'componentes': componentes_data
        })
        
    except Exception as e:
        print(f"Error obteniendo detalle de insumo elaborado: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
def editar_insumo_elaborado(request, insumo_id):
    """Vista para editar un insumo elaborado"""
    if request.method == 'POST':
        try:
            from restaurant.models import InsumoElaborado
            
            insumo = get_object_or_404(Insumo, id=insumo_id, tipo='elaborado')
            
            # Actualizar datos básicos
            insumo.nombre = request.POST.get('nombre', insumo.nombre)
            insumo.descripcion = request.POST.get('descripcion', insumo.descripcion)
            
            categoria_id = request.POST.get('categoria_id')
            if categoria_id:
                insumo.categoria = CategoriaInsumo.objects.get(id=categoria_id)
            
            unidad_medida_id = request.POST.get('unidad_medida_id')
            if unidad_medida_id:
                insumo.unidad_medida = UnidadMedida.objects.get(id=unidad_medida_id)
            
            # Obtener nuevos componentes
            insumo_ids = request.POST.getlist('componente_insumo[]')
            cantidades = request.POST.getlist('componente_cantidad[]')
            tiempos = request.POST.getlist('componente_tiempo[]')
            instrucciones_list = request.POST.getlist('componente_instrucciones[]')
            
            # Eliminar componentes existentes
            InsumoElaborado.objects.filter(insumo_elaborado=insumo).delete()
            
            # Crear nuevos componentes
            total_costo = 0
            cantidad_producida = float(request.POST.get('cantidad_producida', 1));
            
            for i, (insumo_id_comp, cantidad) in enumerate(zip(insumo_ids, cantidades)):
                if not insumo_id_comp or not cantidad:
                    continue
                
                insumo_componente = Insumo.objects.get(id=insumo_id_comp, tipo='compuesto')
                cantidad_decimal = float(cantidad)
                tiempo_prep = int(tiempos[i]) if i < len(tiempos) and tiempos[i] else 0
                instrucciones = instrucciones_list[i] if i < len(instrucciones_list) else ''
                
                InsumoElaborado.objects.create(
                    insumo_elaborado=insumo,
                    insumo_componente=insumo_componente,
                    cantidad=cantidad_decimal,
                    orden=i + 1,
                    tiempo_preparacion_minutos=tiempo_prep,
                    instrucciones=instrucciones
                )
                
                total_costo += cantidad_decimal * insumo_componente.precio_unitario
            
            # Actualizar precio unitario
            insumo.precio_unitario = total_costo / cantidad_producida
            insumo.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Insumo elaborado "{insumo.nombre}" actualizado exitosamente'
            })
            
        except Exception as e:
            print(f"Error editando insumo elaborado: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            })
    
    # Si es GET, devolver datos para edición
    try:
        return detalle_insumo_elaborado(request, insumo_id)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error cargando datos: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
def eliminar_insumo_elaborado(request, insumo_id):
    """Vista para eliminar un insumo elaborado"""
    if request.method == 'POST':
        try:
            from restaurant.models import InsumoElaborado
            
            insumo = get_object_or_404(Insumo, id=insumo_id, tipo='elaborado')
            nombre = insumo.nombre
            
            # Eliminar componentes primero
            InsumoElaborado.objects.filter(insumo_elaborado=insumo).delete()
            
            # Eliminar el insumo
            insumo.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Insumo elaborado "{nombre}" eliminado exitosamente'
            })
            
        except Exception as e:
            print(f"Error eliminando insumo elaborado: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })

def get_form_data(request):
    """Vista para obtener datos para los formularios"""
    # Comprobar si el usuario está autenticado
    if not request.user.is_authenticated:
        print("Usuario no autenticado accediendo a get_form_data")
        # Para depuración - permitir acceso incluso sin autenticación
        # pass  # Descomentar esta línea para permitir acceso sin autenticación
        
    # Obtener datos
    categorias = CategoriaInsumo.objects.all().values('id', 'nombre')
    unidades = UnidadMedida.objects.all().values('id', 'nombre', 'abreviacion')
    
    data = {
        'categorias': list(categorias),
        'unidades': list(unidades)
    }
      # Para depuración
    print(f"Devolviendo datos: {len(data['categorias'])} categorías y {len(data['unidades'])} unidades")
    
    return JsonResponse(data)

@login_required
def crear_categoria(request):
    """Vista para crear una nueva categoría"""
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            
            if not nombre:
                return JsonResponse({
                    'success': False,
                    'error': 'El nombre de la categoría es obligatorio'
                })
            
            # Verificar si ya existe
            if Categoria.objects.filter(nombre=nombre).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Ya existe una categoría con el nombre "{nombre}"'
                })
            
            categoria = Categoria.objects.create(
                nombre=nombre,
                descripcion=descripcion
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Categoría "{nombre}" creada exitosamente',
                'categoria': {
                    'id': categoria.id,
                    'nombre': categoria.nombre,
                    'descripcion': categoria.descripcion if hasattr(categoria, 'descripcion') else ''
                }
            })
            
        except Exception as e:
            print(f"Error creando categoría: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Error al crear la categoría: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })

@login_required
def eliminar_categoria(request, categoria_id):
    """Vista para eliminar una categoría"""
    if request.method == 'POST':
        try:
            categoria = get_object_or_404(Categoria, id=categoria_id)
            
            # Verificar si tiene insumos asociados
            if Insumo.objects.filter(categoria=categoria).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'No se puede eliminar la categoría porque tiene insumos asociados'
                })
            
            nombre = categoria.nombre
            categoria.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Categoría "{nombre}" eliminada exitosamente'
            })
            
        except Exception as e:
            print(f"Error eliminando categoría: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Error al eliminar la categoría: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })

@login_required
def crear_unidad(request):
    """Vista para crear una nueva unidad de medida"""
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre', '').strip()
            abreviacion = request.POST.get('abreviacion', '').strip()
            tipo = request.POST.get('tipo', '').strip()
            
            if not all([nombre, abreviacion]):
                return JsonResponse({
                    'success': False,
                    'error': 'El nombre y abreviación son obligatorios'
                })
            
            # Verificar si ya existe
            if UnidadMedida.objects.filter(nombre=nombre).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Ya existe una unidad con el nombre "{nombre}"'
                })
            
            if UnidadMedida.objects.filter(abreviacion=abreviacion).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Ya existe una unidad con la abreviación "{abreviacion}"'
                })
            
            # Crear la unidad
            unidad_data = {
                'nombre': nombre,
                'abreviacion': abreviacion
            }
            
            # Solo agregar tipo si el modelo lo soporta
            if hasattr(UnidadMedida, 'tipo') and tipo:
                unidad_data['tipo'] = tipo
            
            unidad = UnidadMedida.objects.create(**unidad_data)
            
            return JsonResponse({
                'success': True,
                'message': f'Unidad de medida "{nombre}" creada exitosamente',
                'unidad': {
                    'id': unidad.id,
                    'nombre': unidad.nombre,
                    'abreviacion': unidad.abreviacion,
                    'tipo': getattr(unidad, 'tipo', '') if hasattr(unidad, 'tipo') else ''
                }
            })
            
        except Exception as e:
            print(f"Error creando unidad: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Error al crear la unidad: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })

@login_required
def eliminar_unidad(request, unidad_id):
    """Vista para eliminar una unidad de medida"""
    if request.method == 'POST':
        try:
            unidad = get_object_or_404(UnidadMedida, id=unidad_id)
            
            # Verificar si tiene insumos asociados
            if Insumo.objects.filter(unidad_medida=unidad).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'No se puede eliminar la unidad porque tiene insumos asociados'
                })
            
            nombre = unidad.nombre
            unidad.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Unidad de medida "{nombre}" eliminada exitosamente'
            })
            
        except Exception as e:
            print(f"Error eliminando unidad: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Error al eliminar la unidad: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })

@login_required
def detalle_proveedor(request, proveedor_id):
    """Vista para ver detalles completos de un proveedor"""
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    
    # Obtener insumos del proveedor
    insumos_proveedor = ProveedorInsumo.objects.filter(
        proveedor=proveedor, 
        activo=True
    ).select_related('insumo', 'insumo__categoria', 'insumo__unidad_medida')
    
    # Estadísticas del proveedor
    total_insumos = insumos_proveedor.count()
    precio_promedio = insumos_proveedor.aggregate(
        promedio=Avg('precio_unitario')
    )['promedio'] or 0
    
    # Preparar datos de insumos con serialización segura
    insumos_data = []
    for pi in insumos_proveedor:
        # Usar valores escalares en vez de objetos para evitar errores de serialización
        insumo_data = {
            'id': pi.id,
            'insumo_id': pi.insumo.id,
            'nombre': pi.insumo.nombre,
            'categoria_nombre': pi.insumo.categoria.nombre if pi.insumo.categoria else None,
            'categoria_id': pi.insumo.categoria_id,
            'unidad_medida_nombre': str(pi.insumo.unidad_medida) if pi.insumo.unidad_medida else None,
            'unidad_medida_id': pi.insumo.unidad_medida_id,
            'precio_unitario': float(pi.precio_unitario),
            'precio_descuento': float(pi.precio_descuento) if pi.precio_descuento else None,
            'precio_final': float(pi.precio_final()),
            'descuento_porcentaje': pi.descuento_porcentaje(),
            'cantidad_minima': float(pi.cantidad_minima),
            'tiempo_entrega_dias': pi.tiempo_entrega_dias,
            'notas': pi.notas,
        }
        insumos_data.append(insumo_data)
    
    # Datos del proveedor para AJAX
    proveedor_ajax = {
        'id': proveedor.id,
        'nombre_comercial': proveedor.nombre_comercial,
        'razon_social': proveedor.razon_social,
        'rfc': proveedor.rfc,
        'persona_contacto': proveedor.persona_contacto,
        'telefono': proveedor.telefono,
        'email': proveedor.email,
        'direccion': proveedor.direccion,
        'ciudad_estado': proveedor.ciudad_estado,
        'categoria_productos': proveedor.categoria_productos,
        'forma_pago_preferida': proveedor.forma_pago_preferida,
        'dias_credito': proveedor.dias_credito,
        'estado': proveedor.estado,
        'fecha_registro': proveedor.fecha_registro.strftime('%d/%m/%Y'),
        'notas_adicionales': proveedor.notas_adicionales,
        'total_insumos': total_insumos,
        'precio_promedio': float(precio_promedio),
    }
    
    # Datos del proveedor para non-AJAX (versión simplificada)
    proveedor_simple = {
        'id': proveedor.id,
        'nombre_comercial': proveedor.nombre_comercial,
        'razon_social': proveedor.razon_social,
        'rfc': proveedor.rfc,
        'telefono': proveedor.telefono,
        'email': proveedor.email,
        'direccion': proveedor.direccion,
        'contacto_principal': proveedor.persona_contacto,
        'estado': proveedor.estado,
        'fecha_registro': proveedor.fecha_registro.strftime('%d/%m/%Y'),
        'precio_promedio': float(precio_promedio),
    }
    
    # Responder según el tipo de solicitud
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'proveedor': proveedor_ajax,
            'insumos': insumos_data
        })
    else:
        # Para solicitudes no-AJAX
        return JsonResponse({
            'success': True,
            'proveedor': proveedor_simple,
            'insumos': insumos_data
        })


@login_required
def editar_proveedor(request, proveedor_id):
    """Vista para editar un proveedor existente"""
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            proveedor.nombre_comercial = request.POST.get('nombre_comercial', '').strip()
            proveedor.razon_social = request.POST.get('razon_social', '').strip()
            proveedor.rfc = request.POST.get('rfc', '').strip()
            proveedor.persona_contacto = request.POST.get('persona_contacto', '').strip()
            proveedor.telefono = request.POST.get('telefono', '').strip()
            proveedor.email = request.POST.get('email', '').strip()
            proveedor.forma_pago_preferida = request.POST.get('forma_pago_preferida', 'transferencia')
            proveedor.dias_credito = int(request.POST.get('dias_credito', '0'))
            proveedor.direccion = request.POST.get('direccion', '').strip()
            proveedor.ciudad_estado = request.POST.get('ciudad_estado', '').strip()
            proveedor.categoria_productos = request.POST.get('categoria_productos', 'ingredientes')
            proveedor.notas_adicionales = request.POST.get('notas_adicionales', '').strip()
            proveedor.estado = request.POST.get('estado', 'activo')
            
            proveedor.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Proveedor "{proveedor.nombre_comercial}" actualizado exitosamente'
                })
            else:
                messages.success(request, f'Proveedor "{proveedor.nombre_comercial}" actualizado exitosamente')
                return redirect('dashboard:proveedores')
                
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error al actualizar el proveedor: {str(e)}'
                })
            else:
                messages.error(request, f'Error al actualizar el proveedor: {str(e)}')
    
    # Para GET requests o si hay error en POST
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'proveedor': {
                'id': proveedor.id,
                'nombre_comercial': proveedor.nombre_comercial,
                'razon_social': proveedor.razon_social,
                'rfc': proveedor.rfc,
                'persona_contacto': proveedor.persona_contacto,
                'telefono': proveedor.telefono,
                'email': proveedor.email,
                'direccion': proveedor.direccion,
                'ciudad_estado': proveedor.ciudad_estado,
                'categoria_productos': proveedor.categoria_productos,
                'forma_pago_preferida': proveedor.forma_pago_preferida,
                'dias_credito': proveedor.dias_credito,
                'estado': proveedor.estado,
                'notas_adicionales': proveedor.notas_adicionales,
            }
        })


@login_required  
def eliminar_proveedor(request, proveedor_id):
    """Vista para eliminar un proveedor"""
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    
    if request.method == 'POST':
        try:
            nombre = proveedor.nombre_comercial
            proveedor.delete()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Proveedor "{nombre}" eliminado exitosamente'
                })
            else:
                messages.success(request, f'Proveedor "{nombre}" eliminado exitosamente')
                return redirect('dashboard:proveedores')
                
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error al eliminar el proveedor: {str(e)}'
                })
            else:
                messages.error(request, f'Error al eliminar el proveedor: {str(e)}')
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })


@login_required
def asignar_insumo_proveedor(request, proveedor_id):
    """Vista para asignar un insumo a un proveedor con precio"""
    if request.method == 'POST':
        try:
            # Log de datos recibidos para debug
            print(f"🔍 DEBUG - Datos recibidos:")
            print(f"   proveedor_id: {proveedor_id} (tipo: {type(proveedor_id)})")
            print(f"   POST data: {dict(request.POST)}")
            
            # El proveedor_id viene del URL, no del POST
            insumo_id = request.POST.get('insumo_id')
            precio_unitario = request.POST.get('precio_unitario')
            precio_descuento = request.POST.get('precio_descuento') or None
            cantidad_minima = request.POST.get('cantidad_minima', 1)
            tiempo_entrega_dias = request.POST.get('tiempo_entrega_dias', 1)
            notas = request.POST.get('observaciones', '')
            
            print(f"   insumo_id: {insumo_id} (tipo: {type(insumo_id)})")
            print(f"   precio_unitario: {precio_unitario}")
            
            # Validaciones
            if not insumo_id or not precio_unitario:
                return JsonResponse({
                    'success': False,
                    'message': 'Faltan campos requeridos: insumo_id y precio_unitario son obligatorios'
                })
            
            # Validar que insumo_id sea un número válido
            try:
                insumo_id = int(insumo_id)
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'message': f'ID de insumo inválido: {insumo_id}'
                })
            
            # Validar que proveedor_id sea un número válido
            try:
                proveedor_id = int(proveedor_id)
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'message': f'ID de proveedor inválido: {proveedor_id}'
                })
            
            # Validar precio
            try:
                precio_unitario = float(precio_unitario)
                if precio_unitario <= 0:
                    raise ValueError("Precio debe ser mayor a cero")
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'message': f'Precio unitario inválido: {precio_unitario}'
                })
            
            # Buscar proveedor
            try:
                proveedor = Proveedor.objects.get(id=proveedor_id)
                print(f"   ✅ Proveedor encontrado: {proveedor.id} - {proveedor.nombre_comercial}")
            except Proveedor.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': f'No se encontró el proveedor con ID {proveedor_id}'
                })
            
            # Buscar insumo
            try:
                insumo = Insumo.objects.get(id=insumo_id)
                print(f"   ✅ Insumo encontrado: {insumo.id} - {insumo.nombre}")
            except Insumo.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': f'No se encontró el insumo con ID {insumo_id}'
                })
                
            # Verificar si ya existe la relación
            existing = ProveedorInsumo.objects.filter(proveedor=proveedor, insumo=insumo).first()
            if existing:
                print(f"   ⚠️ Relación ya existe, actualizando: {existing.id}")
                # Actualizar la relación existente
                existing.precio_unitario = precio_unitario
                if precio_descuento:
                    try:
                        existing.precio_descuento = float(precio_descuento)
                    except (ValueError, TypeError):
                        existing.precio_descuento = None
                else:
                    existing.precio_descuento = None
                    
                existing.cantidad_minima = float(cantidad_minima) if cantidad_minima else 1
                existing.tiempo_entrega_dias = int(tiempo_entrega_dias) if tiempo_entrega_dias else 1
                existing.notas = notas
                existing.activo = True
                existing.save()
                proveedor_insumo = existing
                mensaje = f'Precio de "{insumo.nombre}" actualizado para el proveedor "{proveedor.nombre_comercial}"'
            else:
                print(f"   ✅ Creando nueva relación...")
                # Crear una nueva relación
                proveedor_insumo = ProveedorInsumo.objects.create(
                    proveedor=proveedor,
                    insumo=insumo,
                    precio_unitario=precio_unitario,
                    precio_descuento=float(precio_descuento) if precio_descuento else None,
                    cantidad_minima=float(cantidad_minima) if cantidad_minima else 1,
                    tiempo_entrega_dias=int(tiempo_entrega_dias) if tiempo_entrega_dias else 1,
                    notas=notas,
                    activo=True
                )
                print(f"   ✅ Relación creada exitosamente: {proveedor_insumo.id}")
                mensaje = f'Insumo "{insumo.nombre}" asignado al proveedor "{proveedor.nombre_comercial}" exitosamente'
            
            return JsonResponse({
                'success': True,
                'message': mensaje,
                'proveedor_insumo': {
                    'id': proveedor_insumo.id,
                    'insumo_nombre': insumo.nombre,
                    'precio_unitario': float(proveedor_insumo.precio_unitario),
                    'precio_final': float(proveedor_insumo.precio_final()),
                }
            })
            
        except Exception as e:
            print(f"❌ Error en asignar_insumo_proveedor: {e}")
            print(f"   Tipo de error: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Error al asignar el insumo: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })


@login_required
def remover_insumo_proveedor(request, proveedor_insumo_id):
    """Vista para remover un insumo de un proveedor"""
    if request.method == 'POST':
        try:
            proveedor_insumo = get_object_or_404(ProveedorInsumo, id=proveedor_insumo_id)
            insumo_nombre = proveedor_insumo.insumo.nombre
            proveedor_nombre = proveedor_insumo.proveedor.nombre_comercial
            
            proveedor_insumo.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Insumo "{insumo_nombre}" removido del proveedor "{proveedor_nombre}"'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al remover el insumo: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })


@login_required
def obtener_insumos_disponibles(request):
    """Vista para obtener insumos disponibles para asignar a proveedores"""
    proveedor_id = request.GET.get('proveedor_id')
    
    if not proveedor_id:
        return JsonResponse({
            'success': False,
            'message': 'ID de proveedor requerido'
        })
    
    try:
        proveedor = get_object_or_404(Proveedor, id=proveedor_id)
        
        # Obtener insumos que no están asignados a este proveedor
        insumos_asignados = ProveedorInsumo.objects.filter(
            proveedor=proveedor,
            activo=True
        ).values_list('insumo_id', flat=True)
        
        insumos_disponibles = Insumo.objects.filter(
            activo=True
        ).exclude(
            id__in=insumos_asignados
        ).select_related('categoria', 'unidad_medida').order_by('categoria__nombre', 'nombre')
        
        insumos_data = [{
            'id': insumo.id,
            'nombre': insumo.nombre,
            'categoria': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
            'unidad_medida': f"{insumo.unidad_medida.nombre} ({insumo.unidad_medida.abreviacion})" if insumo.unidad_medida else 'Sin unidad',
            'descripcion': '',  # El modelo de Restaurant.Insumo no tiene descripcion
        } for insumo in insumos_disponibles]
        
        return JsonResponse({
            'success': True,
            'insumos': insumos_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener insumos: {str(e)}'
        })

@login_required
def obtener_insumos_basicos(request):
    """API para obtener insumos básicos disponibles"""
    try:
        insumos = Insumo.objects.filter(
            tipo='basico', 
            activo=True
        ).select_related('categoria', 'unidad_medida').order_by('nombre')
        
        insumos_data = []
        for insumo in insumos:
            insumos_data.append({
                'id': insumo.id,
                'codigo': insumo.codigo,
                'nombre': insumo.nombre,
                'tipo': 'basico',
                'categoria_nombre': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
                'unidad_medida_nombre': str(insumo.unidad_medida) if insumo.unidad_medida else 'Sin unidad',
                'unidad_abrev': insumo.unidad_medida.abreviacion if insumo.unidad_medida else '',
                'precio_unitario': float(insumo.precio_unitario)
            })
        
        return JsonResponse({
            'success': True,
            'insumos': insumos_data,
            'count': len(insumos_data)
        })
    except Exception as e:
        print(f"Error obteniendo insumos básicos: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
def obtener_insumos_compuestos(request):
    """API para obtener insumos compuestos disponibles"""
    try:
        insumos = Insumo.objects.filter(
            tipo='compuesto', 
            activo=True
        ).select_related('categoria', 'unidad_medida').order_by('nombre')
        
        insumos_data = []
        for insumo in insumos:
            insumos_data.append({
                'id': insumo.id,
                'codigo': insumo.codigo,
                'nombre': insumo.nombre,
                'tipo': 'compuesto',
                'categoria_nombre': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
                'unidad_medida_nombre': str(insumo.unidad_medida) if insumo.unidad_medida else 'Sin unidad',
                'unidad_abrev': insumo.unidad_medida.abreviacion if insumo.unidad_medida else '',
                'precio_unitario': float(insumo.precio_unitario)
            })
        
        return JsonResponse({
            'success': True,
            'insumos': insumos_data,
            'count': len(insumos_data)
        })
    except Exception as e:
        print(f"Error obteniendo insumos compuestos: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
def obtener_insumos_elaborados(request):
    """API para obtener insumos elaborados disponibles"""
    try:
        insumos = Insumo.objects.filter(
            tipo='elaborado', 
            activo=True
        ).select_related('categoria', 'unidad_medida').order_by('nombre')
        
        insumos_data = []
        for insumo in insumos:
            insumos_data.append({
                'id': insumo.id,
                'codigo': insumo.codigo,
                'nombre': insumo.nombre,
                'tipo': 'elaborado',
                'categoria_nombre': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
                'unidad_medida_nombre': str(insumo.unidad_medida) if insumo.unidad_medida else 'Sin unidad',
                'unidad_abrev': insumo.unidad_medida.abreviacion if insumo.unidad_medida else '',
                'precio_unitario': float(insumo.precio_unitario)
            })
        
        return JsonResponse({
            'success': True,
            'insumos': insumos_data,
            'count': len(insumos_data)
        })
    except Exception as e:
        print(f"Error obteniendo insumos elaborados: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
def crear_receta(request):
    """Vista para crear una nueva receta"""
    if request.method == 'POST':
        try:
            # Datos básicos de la receta
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            categoria_id = request.POST.get('categoria_id')
            tiempo_preparacion = request.POST.get('tiempo_preparacion')
            porciones = request.POST.get('porciones', 1)
            precio_venta = request.POST.get('precio_venta')
            
            # Validaciones básicas
            if not all([nombre, tiempo_preparacion, porciones]):
                return JsonResponse({
                    'success': False,
                    'message': 'Los campos nombre, tiempo de preparación y porciones son obligatorios'
                })
            
            # Convertir datos a tipos correctos
            tiempo_preparacion = int(tiempo_preparacion)
            porciones = int(porciones)
            precio_venta = Decimal(str(precio_venta)) if precio_venta else None
            
            # Obtener ingredientes (insumos básicos)
            ingredientes_data = []
            insumo_ids = request.POST.getlist('ingrediente_insumo[]')
            cantidades = request.POST.getlist('ingrediente_cantidad[]')
            
            if len(insumo_ids) != len(cantidades):
                return JsonResponse({
                    'success': False,
                    'message': 'Error en los datos de ingredientes'
                })
            
            # Obtener pre-preparados (insumos compuestos o elaborados)
            prepreparados_data = []
            prepreparado_ids = request.POST.getlist('prepreparado_insumo[]')
            prepreparado_cantidades = request.POST.getlist('prepreparado_cantidad[]')
            
            if len(prepreparado_ids) != len(prepreparado_cantidades):
                return JsonResponse({
                    'success': False,
                    'message': 'Error en los datos de insumos pre-preparados'
                })
            
            # Procesar ingredientes básicos
            total_costo_ingredientes = Decimal('0')
            for i, (insumo_id, cantidad) in enumerate(zip(insumo_ids, cantidades)):
                if not insumo_id or not cantidad:
                    continue
                
                try:
                    insumo = Insumo.objects.get(id=insumo_id, tipo='basico', activo=True)
                    cantidad_decimal = Decimal(str(cantidad))
                    
                    if cantidad_decimal <= 0:
                        return JsonResponse({
                            'success': False,
                            'message': f'La cantidad para {insumo.nombre} debe ser mayor a 0'
                        })
                    
                    costo = cantidad_decimal * insumo.precio_unitario
                    total_costo_ingredientes += costo
                    
                    ingredientes_data.append({
                        'insumo': insumo,
                        'cantidad': cantidad_decimal,
                        'costo': costo
                    })
                except Insumo.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': f'El insumo básico con ID {insumo_id} no existe o no está activo'
                    })
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'message': f'Cantidad inválida para el ingrediente {i+1}'
                    })
            
            # Procesar pre-preparados (compuestos o elaborados)
            total_costo_prepreparados = Decimal('0')
            for i, (insumo_id, cantidad) in enumerate(zip(prepreparado_ids, prepreparado_cantidades)):
                if not insumo_id or not cantidad:
                    continue
                
                try:
                    insumo = Insumo.objects.get(
                        id=insumo_id, 
                        tipo__in=['compuesto', 'elaborado'],
                        activo=True
                    )
                    cantidad_decimal = Decimal(str(cantidad))
                    
                    if cantidad_decimal <= 0:
                        return JsonResponse({
                            'success': False,
                            'message': f'La cantidad para {insumo.nombre} debe ser mayor a 0'
                        })
                    
                    costo = cantidad_decimal * insumo.precio_unitario
                    total_costo_prepreparados += costo
                    
                    prepreparados_data.append({
                        'insumo': insumo,
                        'cantidad': cantidad_decimal,
                        'costo': costo
                    })
                except Insumo.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': f'El insumo pre-preparado con ID {insumo_id} no existe o no está activo'
                    })
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'message': f'Cantidad inválida para el pre-preparado {i+1}'
                    })
            
            # Verificar que haya al menos un ingrediente o pre-preparado
            if not ingredientes_data and not prepreparados_data:
                return JsonResponse({
                    'success': False,
                    'message': 'Debe agregar al menos un ingrediente o insumo pre-preparado'
                })
            
            # Calcular costo total
            costo_total = total_costo_ingredientes + total_costo_prepreparados
            
            # Crear la receta
            categoria = None
            if categoria_id:
                try:
                    categoria = CategoriaProducto.objects.get(id=categoria_id)
                except CategoriaProducto.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': f'La categoría con ID {categoria_id} no existe'
                    })
            
            # Crear la receta en la base de datos
            with transaction.atomic():
                # Crear la receta
                receta = Receta.objects.create(
                    nombre=nombre,
                    descripcion=descripcion,
                    instrucciones='',  # Por ahora sin instrucciones detalladas
                    tiempo_preparacion=tiempo_preparacion,
                    porciones=porciones,
                    costo_total=costo_total,
                    activa=True
                )
                
                # Agregar ingredientes (insumos básicos)
                for item in ingredientes_data:
                    RecetaInsumo.objects.create(
                        receta=receta,
                        insumo=item['insumo'],
                        cantidad=item['cantidad']
                    )
                
                # Agregar pre-preparados (insumos compuestos o elaborados)
                for item in prepreparados_data:
                    RecetaInsumo.objects.create(
                        receta=receta,
                        insumo=item['insumo'],
                        cantidad=item['cantidad']
                    )
                
                # Si hay precio de venta, crear un producto asociado
                if precio_venta and categoria:
                    codigo = f"PROD-{receta.id}"
                    ProductoVenta.objects.create(
                        codigo=codigo,
                        nombre=nombre,
                        descripcion=descripcion,
                        categoria=categoria,
                        precio=precio_venta,
                        costo=costo_total,
                        receta=receta,
                        disponible=True
                    )
            
            return JsonResponse({
                'success': True,
                'message': f'Receta "{nombre}" creada exitosamente',
                'receta_id': receta.id,
                'costo_total': float(costo_total),
                'ingredientes': len(ingredientes_data),
                'prepreparados': len(prepreparados_data)
            })
            
        except Exception as e:
            print(f"Error creando receta: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })

@login_required
def detalle_receta(request, receta_id):
    """Vista para ver detalles de una receta"""
    try:
        receta = get_object_or_404(Receta, id=receta_id, activa=True)
        
        # Obtener ingredientes
        ingredientes = RecetaInsumo.objects.filter(receta=receta).select_related('insumo', 'insumo__unidad_medida')
        
        # Obtener producto asociado si existe
        try:
            producto = ProductoVenta.objects.get(receta=receta)
            precio_venta = float(producto.precio)
        except ProductoVenta.DoesNotExist:
            precio_venta = None
        
        # Preparar datos de la receta
        receta_data = {
            'id': receta.id,
            'nombre': receta.nombre,
            'descripcion': receta.descripcion,
            'tiempo_preparacion': receta.tiempo_preparacion,
            'porciones': receta.porciones,
            'costo_total': float(receta.costo_total),
            'precio_venta': precio_venta,
            'categoria': receta.categoria.nombre if hasattr(receta, 'categoria') and receta.categoria else None,
            'fecha_creacion': receta.created_at.strftime('%d/%m/%Y')
        }
        
        # Preparar datos de ingredientes
        ingredientes_data = []
        for ingrediente in ingredientes:
            ingredientes_data.append({
                'id': ingrediente.insumo.id,
                'nombre': ingrediente.insumo.nombre,
                'codigo': ingrediente.insumo.codigo,
                'tipo': ingrediente.insumo.tipo,
                'cantidad': float(ingrediente.cantidad),
                'unidad': ingrediente.insumo.unidad_medida.abreviacion if ingrediente.insumo.unidad_medida else '',
                'precio_unitario': float(ingrediente.insumo.precio_unitario),
                'costo': float(ingrediente.cantidad * ingrediente.insumo.precio_unitario)
            })
        
        return JsonResponse({
            'success': True,
            'receta': receta_data,
            'ingredientes': ingredientes_data
        })
        
    except Exception as e:
        print(f"Error obteniendo detalle de receta: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
def eliminar_receta(request, receta_id):
    """Vista para eliminar una receta"""
    if request.method == 'POST':
        try:
            receta = get_object_or_404(Receta, id=receta_id)
            
            # Verificar si hay productos asociados
            productos = ProductoVenta.objects.filter(receta=receta)
            
            with transaction.atomic():
                # Desactivar la receta en lugar de eliminarla
                receta.activa = False
                receta.save()
                
                # Desactivar productos asociados
                for producto in productos:
                    producto.disponible = False
                    producto.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Receta "{receta.nombre}" eliminada exitosamente'
            })
            
        except Exception as e:
            print(f"Error eliminando receta: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })

@login_required
def recetas_view(request):
    """Vista principal para gestión de recetas"""
    # Obtener todas las recetas activas
    recetas = Receta.objects.filter(activa=True).order_by('nombre')
    
    # Estadísticas
    total_recetas = recetas.count()
    costo_promedio = recetas.aggregate(promedio=Avg('costo_total'))['promedio'] or 0
    
    # Obtener categorías de productos para el formulario
    categorias_productos = CategoriaProducto.objects.all().order_by('nombre')
    
    context = {
        'recetas': recetas,
        'total_recetas': total_recetas,
        'costo_promedio': costo_promedio,
        'categorias_productos': categorias_productos,
        **get_sidebar_context('recetas')
    }
    
    return render(request, 'dashboard/recetas.html', context)


