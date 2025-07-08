"""
Decoradores personalizados para manejo de permisos en el app de cajero
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse

def cajero_required(view_func):
    """
    Decorador que permite acceso a usuarios con roles de:
    - cajero (rol principal)
    - gerente (puede supervisar)
    - admin (acceso total)
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.is_ajax() or request.content_type == 'application/json':
                return JsonResponse({'error': 'No autenticado'}, status=401)
            return redirect('cajero:login')
        
        # El superuser siempre tiene acceso
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verificar permisos por rol
        user_role = getattr(request.user.rol, 'nombre', None) if hasattr(request.user, 'rol') and request.user.rol else None
        
        # Roles permitidos para el app de cajero
        allowed_roles = ['cajero', 'gerente', 'admin']
        
        # Verificar si el usuario tiene un rol permitido
        if user_role and user_role in allowed_roles:
            return view_func(request, *args, **kwargs)
        
        # Verificar por grupos de Django (fallback)
        if request.user.groups.filter(name__in=allowed_roles).exists():
            return view_func(request, *args, **kwargs)
        
        # Si el usuario tiene staff status, permitir acceso (para admins sin rol específico)
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        
        # Acceso denegado
        if request.is_ajax() or request.content_type == 'application/json':
            return JsonResponse({'error': 'Permisos insuficientes'}, status=403)
        
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard:principal')
    
    return _wrapped_view

def admin_or_gerente_required(view_func):
    """
    Decorador que permite acceso solo a admin y gerente
    Para funciones sensibles como cancelar ventas, reportes, etc.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.is_ajax() or request.content_type == 'application/json':
                return JsonResponse({'error': 'No autenticado'}, status=401)
            return redirect('cajero:login')
        
        # Verificar permisos por rol
        user_role = getattr(request.user.rol, 'nombre', None) if request.user.rol else None
        
        # Roles con permisos elevados
        elevated_roles = ['gerente', 'admin']
        
        # El superuser siempre tiene acceso
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verificar si el usuario tiene un rol elevado
        if user_role in elevated_roles:
            return view_func(request, *args, **kwargs)
        
        # Verificar por grupos de Django (fallback)
        if request.user.groups.filter(name__in=elevated_roles).exists():
            return view_func(request, *args, **kwargs)
        
        # Acceso denegado
        if request.is_ajax() or request.content_type == 'application/json':
            return JsonResponse({'error': 'Permisos insuficientes - se requiere rol de gerente o admin'}, status=403)
        
        messages.error(request, 'Esta acción requiere permisos de gerente o administrador.')
        return redirect('cajero:dashboard')
    
    return _wrapped_view

def get_user_permissions(user):
    """
    Función helper para obtener los permisos del usuario
    Retorna un diccionario con los permisos disponibles
    """
    if not user.is_authenticated:
        return {}
    
    # Obtener rol del usuario de forma segura
    user_role = None
    if hasattr(user, 'rol') and user.rol:
        user_role = getattr(user.rol, 'nombre', None)
    
    permissions = {
        'can_access_pos': False,
        'can_view_sales': False,
        'can_cancel_sales': False,
        'can_view_reports': False,
        'can_manage_inventory': False,
        'is_admin': False,
        'is_gerente': False,
        'is_cajero': False,
        'role_display': 'Sin rol'
    }
    
    # Superuser tiene todos los permisos
    if user.is_superuser:
        permissions.update({
            'can_access_pos': True,
            'can_view_sales': True,
            'can_cancel_sales': True,
            'can_view_reports': True,
            'can_manage_inventory': True,
            'is_admin': True,
            'role_display': 'Super Administrador'
        })
        return permissions
    
    # Permisos por rol
    if user_role == 'admin':
        permissions.update({
            'can_access_pos': True,
            'can_view_sales': True,
            'can_cancel_sales': True,
            'can_view_reports': True,
            'can_manage_inventory': True,
            'is_admin': True,
            'role_display': 'Administrador'
        })
    elif user_role == 'gerente':
        permissions.update({
            'can_access_pos': True,
            'can_view_sales': True,
            'can_cancel_sales': True,
            'can_view_reports': True,
            'can_manage_inventory': True,
            'is_gerente': True,
            'role_display': 'Gerente'
        })
    elif user_role == 'cajero':
        permissions.update({
            'can_access_pos': True,
            'can_view_sales': True,
            'can_cancel_sales': False,  # Cajeros no pueden cancelar ventas
            'can_view_reports': False,   # Cajeros no ven reportes completos
            'can_manage_inventory': False,
            'is_cajero': True,
            'role_display': 'Cajero'
        })
    
    # Fallback: verificar por grupos de Django si no hay rol definido
    if not any([permissions['is_admin'], permissions['is_gerente'], permissions['is_cajero']]):
        groups = list(user.groups.values_list('name', flat=True))
        if 'admin' in groups:
            permissions.update({
                'can_access_pos': True,
                'can_view_sales': True,
                'can_cancel_sales': True,
                'can_view_reports': True,
                'can_manage_inventory': True,
                'is_admin': True,
                'role_display': 'Administrador'
            })
        elif 'gerente' in groups:
            permissions.update({
                'can_access_pos': True,
                'can_view_sales': True,
                'can_cancel_sales': True,
                'can_view_reports': True,
                'can_manage_inventory': True,
                'is_gerente': True,
                'role_display': 'Gerente'
            })
        elif 'cajero' in groups:
            permissions.update({
                'can_access_pos': True,
                'can_view_sales': True,
                'is_cajero': True,
                'role_display': 'Cajero'
            })
        # Si tiene staff status pero no rol específico, tratarlo como admin
        elif user.is_staff:
            permissions.update({
                'can_access_pos': True,
                'can_view_sales': True,
                'can_cancel_sales': True,
                'can_view_reports': True,
                'can_manage_inventory': True,
                'is_admin': True,
                'role_display': 'Staff'
            })
    
    return permissions
