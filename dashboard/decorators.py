from django.http import JsonResponse
from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages

def role_required(allowed_roles):
    """
    Decorator to check if the user has the required role.
    Usage: @role_required(['admin', 'gerente', 'supervisor'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Verificar si el usuario está autenticado
            if not request.user.is_authenticated:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Acceso denegado. Debes iniciar sesión.'
                    })
                return redirect('dashboard:login')
            
            # Siempre permitir a superusers
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verificar si el usuario tiene uno de los roles permitidos
            if not hasattr(request.user, 'rol') or not request.user.rol:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'No tienes permisos para acceder a esta función.'
                    })
                messages.error(request, 'No tienes permisos para acceder a esta página.')
                return redirect('dashboard:principal')
            
            if request.user.rol.nombre in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            # Si el usuario no tiene un rol permitido
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes permisos para acceder a esta función.'
                })
            messages.error(request, 'No tienes permisos para acceder a esta página.')
            return redirect('dashboard:principal')
        return _wrapped_view
    return decorator

def branch_required(view_func):
    """
    Decorator to check if the user has a branch assigned.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Verificar si el usuario está autenticado
        if not request.user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Acceso denegado. Debes iniciar sesión.'
                })
            return redirect('dashboard:login')
        
        # Siempre permitir a superusers y staff
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        
        # Verificar si el usuario tiene una sucursal asignada
        if not hasattr(request.user, 'sucursal') or not request.user.sucursal:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes una sucursal asignada. Contacta a un administrador.'
                })
            messages.error(request, 'No tienes una sucursal asignada. Contacta a un administrador.')
            return redirect('dashboard:principal')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view
