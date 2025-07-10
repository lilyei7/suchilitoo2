from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.db.models import Q
from django.utils import timezone
import json

from accounts.models import Usuario, Sucursal, Rol
from .base_views import get_sidebar_context, is_admin_or_manager
from ..utils.permissions import (
    require_module_access, require_permission, 
    has_module_access, has_permission, invalidate_user_permissions
)

@login_required
@require_module_access('usuarios')
def usuarios_view(request):
    """Vista principal para gestión de usuarios con filtros"""
    user = request.user
    # Filtros desde GET
    filtro_sucursal = request.GET.get('filtroSucursal')
    filtro_rol = request.GET.get('filtroRol')
    filtro_estado = request.GET.get('filtroEstado')
    filtro_busqueda = request.GET.get('filtroBusqueda')

    # Base queryset
    usuarios = Usuario.objects.select_related('sucursal', 'rol').all()

    # Si no es superuser ni admin, filtrar por sucursal asignada
    if not user.is_superuser and (not hasattr(user, 'rol') or user.rol is None or user.rol.nombre != 'admin'):
        if hasattr(user, 'sucursal') and user.sucursal:
            usuarios = usuarios.filter(sucursal=user.sucursal)

    # Filtro por sucursal (solo si el admin o gerente quiere filtrar)
    if filtro_sucursal:
        usuarios = usuarios.filter(sucursal_id=filtro_sucursal)

    # Filtro por rol
    if filtro_rol and filtro_rol != '':
        usuarios = usuarios.filter(rol__nombre=filtro_rol)

    # Filtro por estado
    if filtro_estado == 'activo':
        usuarios = usuarios.filter(is_active=True)
    elif filtro_estado == 'inactivo':
        usuarios = usuarios.filter(is_active=False)

    # Filtro por búsqueda
    if filtro_busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=filtro_busqueda) |
            Q(first_name__icontains=filtro_busqueda) |
            Q(last_name__icontains=filtro_busqueda) |
            Q(email__icontains=filtro_busqueda)
        )

    usuarios = usuarios.order_by('-date_joined')

    # Calcular estadísticas
    total_usuarios = usuarios.count()
    usuarios_activos = usuarios.filter(is_active=True).count()
    usuarios_admin = usuarios.filter(
        Q(is_superuser=True) | Q(rol__nombre__in=['admin', 'gerente'])
    ).count()
    usuarios_recientes = usuarios.filter(
        date_joined__gte=timezone.now() - timezone.timedelta(days=30)
    ).count()

    # Obtener roles y sucursales para los formularios
    roles = Rol.objects.filter(activo=True)
    sucursales = Sucursal.objects.filter(activa=True)

    context = {
        'usuarios': usuarios,
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'usuarios_admin': usuarios_admin,
        'usuarios_recientes': usuarios_recientes,
        'roles': roles,
        'sucursales': sucursales,
        'filtro_sucursal': filtro_sucursal or '',
        'filtro_rol': filtro_rol or '',
        'filtro_estado': filtro_estado or '',
        'filtro_busqueda': filtro_busqueda or '',
        **get_sidebar_context('usuarios')
    }
    return render(request, 'dashboard/usuarios.html', context)

@login_required
@require_permission('usuarios', 'create')
def crear_usuario(request):
    """Vista para crear un nuevo usuario"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            password = request.POST.get('password', '').strip()
            telefono = request.POST.get('telefono', '').strip()
            cedula = request.POST.get('cedula', '').strip()
            sucursal_id = request.POST.get('sucursal')
            rol_id = request.POST.get('rol')
            is_active = request.POST.get('is_active') == 'true'
            
            # Validaciones básicas
            if not all([username, email, first_name, last_name, password]):
                return JsonResponse({
                    'success': False,
                    'message': 'Los campos username, email, nombre, apellido y contraseña son obligatorios'
                })
            
            # Verificar que no exista usuario con el mismo username o email
            if Usuario.objects.filter(Q(username=username) | Q(email=email)).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Ya existe un usuario con ese username o email'
                })
            
            # Verificar cédula única si se proporciona
            if cedula and Usuario.objects.filter(cedula=cedula).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Ya existe un usuario con esa cédula'
                })
            
            with transaction.atomic():
                # Obtener sucursal y rol si se proporcionan
                sucursal = None
                if sucursal_id:
                    try:
                        sucursal = Sucursal.objects.get(id=sucursal_id)
                    except Sucursal.DoesNotExist:
                        return JsonResponse({
                            'success': False,
                            'message': 'La sucursal seleccionada no existe'
                        })
                
                rol = None
                if rol_id:
                    try:
                        rol = Rol.objects.get(id=rol_id)
                    except Rol.DoesNotExist:
                        return JsonResponse({
                            'success': False,
                            'message': 'El rol seleccionado no existe'
                        })
                
                # Crear el usuario
                usuario = Usuario.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=make_password(password),
                    telefono=telefono if telefono else '',
                    cedula=cedula if cedula else None,
                    sucursal=sucursal,
                    rol=rol,
                    is_active=is_active
                )
            
            return JsonResponse({
                'success': True,
                'message': f'Usuario "{username}" creado exitosamente'
            })
            
        except Exception as e:
            print(f"Error creando usuario: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
@require_permission('usuarios', 'read')
def detalle_usuario(request, usuario_id):
    """Vista para ver detalles de un usuario"""
    try:
        usuario = get_object_or_404(Usuario, id=usuario_id)
        
        # Preparar datos del usuario
        usuario_data = {
            'id': usuario.id,
            'username': usuario.username,
            'email': usuario.email,
            'first_name': usuario.first_name,
            'last_name': usuario.last_name,
            'telefono': usuario.telefono,
            'cedula': usuario.cedula,
            'is_active': usuario.is_active,
            'is_superuser': usuario.is_superuser,
            'sucursal': {
                'id': usuario.sucursal.id,
                'nombre': usuario.sucursal.nombre,
                'direccion': usuario.sucursal.direccion
            } if usuario.sucursal else None,            'rol': {
                'id': usuario.rol.id,
                'nombre': usuario.rol.get_nombre_display(),
                'descripcion': usuario.rol.descripcion
            } if usuario.rol else None,
            'date_joined': usuario.date_joined.strftime('%d/%m/%Y %H:%M'),
            'last_login': usuario.last_login.strftime('%d/%m/%Y %H:%M') if usuario.last_login else 'Nunca'
        }
        
        return JsonResponse({
            'success': True,
            'usuario': usuario_data
        })
        
    except Exception as e:
        print(f"Error obteniendo detalle de usuario: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@require_permission('usuarios', 'update')
def editar_usuario(request, usuario_id):
    """Vista para editar un usuario existente"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        usuario = get_object_or_404(Usuario, id=usuario_id)
        
        # Obtener datos del formulario
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        cedula = request.POST.get('cedula', '').strip()
        sucursal_id = request.POST.get('sucursal')
        rol_id = request.POST.get('rol')
        is_active = request.POST.get('is_active') == 'true'
        password = request.POST.get('password', '').strip()
        
        # Validaciones básicas
        if not all([username, email, first_name, last_name]):
            return JsonResponse({
                'success': False, 
                'message': 'Los campos username, email, nombre y apellido son obligatorios'
            })
        
        # Verificar username único (excluyendo el usuario actual)
        if Usuario.objects.filter(username=username).exclude(id=usuario_id).exists():
            return JsonResponse({
                'success': False,
                'message': 'Ya existe otro usuario con ese username'
            })
        
        # Verificar email único (excluyendo el usuario actual)
        if Usuario.objects.filter(email=email).exclude(id=usuario_id).exists():
            return JsonResponse({
                'success': False,
                'message': 'Ya existe otro usuario con ese email'
            })
        
        # Verificar cédula única si se proporciona (excluyendo el usuario actual)
        if cedula and Usuario.objects.filter(cedula=cedula).exclude(id=usuario_id).exists():
            return JsonResponse({
                'success': False,
                'message': 'Ya existe otro usuario con esa cédula'
            })
        
        with transaction.atomic():
            # Obtener sucursal y rol si se proporcionan
            sucursal = None
            if sucursal_id:
                try:
                    sucursal = Sucursal.objects.get(id=sucursal_id)
                except Sucursal.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': 'La sucursal seleccionada no existe'
                    })
            
            rol = None
            if rol_id:
                try:
                    rol = Rol.objects.get(id=rol_id)
                except Rol.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': 'El rol seleccionado no existe'
                    })
            
            # Actualizar datos del usuario
            usuario.username = username
            usuario.email = email
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.telefono = telefono if telefono else ''
            usuario.cedula = cedula if cedula else None
            usuario.sucursal = sucursal
            usuario.rol = rol
            usuario.is_active = is_active
              # Actualizar contraseña si se proporciona
            if password:
                usuario.password = make_password(password)
            
            usuario.save()
            
            # Invalidar cache de permisos si se cambió el rol
            if rol_id:
                invalidate_user_permissions(usuario)
        
        return JsonResponse({
            'success': True,
            'message': f'Usuario "{username}" actualizado exitosamente'
        })
        
    except Exception as e:
        print(f"Error editando usuario: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@require_permission('usuarios', 'delete')
def eliminar_usuario(request, usuario_id):
    """Vista para eliminar un usuario"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        usuario = get_object_or_404(Usuario, id=usuario_id)
        
        # Verificar que no sea el usuario actual
        if usuario.id == request.user.id:
            return JsonResponse({
                'success': False,
                'message': 'No puedes eliminar tu propio usuario'
            })
        
        # Verificar si es superusuario (solo otro superusuario puede eliminarlo)
        if usuario.is_superuser and not request.user.is_superuser:
            return JsonResponse({
                'success': False,
                'message': 'Solo un superusuario puede eliminar a otro superusuario'
            })
        
        username = usuario.username
        usuario.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Usuario "{username}" eliminado exitosamente'
        })
        
    except Exception as e:
        print(f"Error eliminando usuario: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@require_permission('usuarios', 'update')
def toggle_estado_usuario(request, usuario_id):
    """Vista para activar/desactivar un usuario"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        usuario = get_object_or_404(Usuario, id=usuario_id)
        
        # Verificar que no sea el usuario actual
        if usuario.id == request.user.id:
            return JsonResponse({
                'success': False,
                'message': 'No puedes cambiar el estado de tu propio usuario'
            })
        
        # Cambiar el estado
        usuario.is_active = not usuario.is_active
        usuario.save()
        
        estado = "activado" if usuario.is_active else "desactivado"
        
        return JsonResponse({
            'success': True,
            'message': f'Usuario "{usuario.username}" {estado} exitosamente',
            'nuevo_estado': usuario.is_active
        })
        
    except Exception as e:
        print(f"Error cambiando estado de usuario: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
def obtener_sucursales_roles(request):
    """API para obtener sucursales y roles para formularios"""
    try:
        sucursales = Sucursal.objects.filter(activa=True).values('id', 'nombre')
        roles = Rol.objects.filter(activo=True).values('id', 'nombre')
        
        # Para depuración
        print(f"Roles encontrados para API: {list(roles)}")
        
        # Si no hay roles activos, incluir al menos el rol de admin como respaldo
        if not roles:
            print("⚠️ No hay roles activos. Proporcionando roles de respaldo.")
            # Intentar obtener roles incluso si no están activos
            roles_respaldo = Rol.objects.all().values('id', 'nombre')
            
            if roles_respaldo:
                roles = roles_respaldo
                print(f"✅ Usando {roles_respaldo.count()} roles de respaldo")
            else:
                # Si aún no hay roles, crear un rol admin temporal solo para la respuesta
                print("⚠️ No hay roles en absoluto. Creando rol admin temporal.")
                roles = [{'id': 1, 'nombre': 'admin'}]
        
        return JsonResponse({
            'success': True,
            'sucursales': list(sucursales),
            'roles': list(roles)
        })
        
    except Exception as e:
        print(f"Error obteniendo sucursales y roles: {e}")
        # Proporcionar datos mínimos de respaldo en caso de error
        return JsonResponse({
            'success': True,  # Devolvemos True para evitar errores en el cliente
            'sucursales': [],
            'roles': [{'id': 1, 'nombre': 'admin'}],
            'error_info': str(e)
        })

@login_required
@require_permission('usuarios', 'update')
def cambiar_contrasena_usuario(request, usuario_id):
    """Vista para cambiar la contraseña de un usuario"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        usuario = get_object_or_404(Usuario, id=usuario_id)
        
        # Obtener nueva contraseña
        password = request.POST.get('password', '').strip()
        
        # Validar que se haya proporcionado una contraseña
        if not password:
            return JsonResponse({
                'success': False,
                'message': 'La contraseña no puede estar vacía'
            })
        
        # Validar longitud mínima
        if len(password) < 8:
            return JsonResponse({
                'success': False,
                'message': 'La contraseña debe tener al menos 8 caracteres'
            })
        
        # Actualizar contraseña
        usuario.password = make_password(password)
        usuario.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Contraseña de "{usuario.username}" actualizada exitosamente'
        })
        
    except Exception as e:
        print(f"Error cambiando contraseña: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })
