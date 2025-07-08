"""
Context processor para inyectar información de permisos en todos los templates
"""
from .permissions import (
    get_user_permissions, get_accessible_modules, 
    has_module_access, has_permission, has_feature,
    get_user_capabilities
)


def permissions_context(request):
    """
    Context processor que agrega información de permisos del usuario a todos los templates
    
    Args:
        request: HttpRequest object
        
    Returns:
        dict: Diccionario con información de permisos
    """
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return {
            'user_permissions': {},
            'accessible_modules': [],
            'user_capabilities': {},
            'permission_helpers': {}
        }
    
    user = request.user
    
    # Obtener permisos completos del usuario
    user_permissions = get_user_permissions(user)
    accessible_modules = get_accessible_modules(user)
    user_capabilities = get_user_capabilities(user)
    
    # Crear helpers de permisos para usar en templates
    permission_helpers = {
        'has_module_access': lambda module: has_module_access(user, module),
        'has_permission': lambda module, action: has_permission(user, module, action),
        'has_feature': lambda feature: has_feature(user, feature),
        'can_create': lambda module: has_permission(user, module, 'create'),
        'can_read': lambda module: has_permission(user, module, 'read'),
        'can_update': lambda module: has_permission(user, module, 'update'),
        'can_delete': lambda module: has_permission(user, module, 'delete'),
    }
    
    # Información específica de rol
    role_info = {
        'name': user.rol.nombre if user.rol else None,
        'display_name': user.rol.get_nombre_display() if user.rol else 'Sin rol',
        'is_admin': user.is_superuser or (user.rol and user.rol.nombre == 'admin'),
        'is_manager': user.is_superuser or (user.rol and user.rol.nombre in ['admin', 'gerente']),
        'is_supervisor': user.is_superuser or (user.rol and user.rol.nombre in ['admin', 'gerente', 'supervisor']),
    }
    
    # Accesos rápidos por módulo (para optimizar templates)
    module_access = {
        'dashboard': has_module_access(user, 'dashboard'),
        'inventario': has_module_access(user, 'inventario'),
        'usuarios': has_module_access(user, 'usuarios'),
        'ventas': has_module_access(user, 'ventas'),
        'recetas': has_module_access(user, 'recetas'),
        'reportes': has_module_access(user, 'reportes'),
        'proveedores': has_module_access(user, 'proveedores'),
        'configuracion': has_module_access(user, 'configuracion'),
    }
    
    # Características específicas (para mostrar/ocultar elementos)
    feature_access = {
        'ver_precios': has_feature(user, 'ver_precios'),
        'ver_costos': has_feature(user, 'ver_costos'),
        'ver_reportes_completos': has_feature(user, 'ver_reportes_completos'),
        'gestionar_usuarios': has_feature(user, 'gestionar_usuarios'),
        'cambiar_configuracion': has_feature(user, 'cambiar_configuracion'),
        'ver_datos_sensibles': has_feature(user, 'ver_datos_sensibles'),
    }
    
    # Permisos CRUD por módulo (para botones de acción)
    crud_permissions = {}
    for module in accessible_modules:
        crud_permissions[module] = {
            'create': has_permission(user, module, 'create'),
            'read': has_permission(user, module, 'read'),
            'update': has_permission(user, module, 'update'),
            'delete': has_permission(user, module, 'delete'),
        }
    
    return {
        'user_permissions': user_permissions,
        'accessible_modules': accessible_modules,
        'user_capabilities': user_capabilities,
        'permission_helpers': permission_helpers,
        'user_role': role_info,
        'module_access': module_access,
        'feature_access': feature_access,
        'crud_permissions': crud_permissions,
    }
