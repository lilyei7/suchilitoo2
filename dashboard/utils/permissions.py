"""
Utilidades centralizadas para el manejo de permisos basados en roles (RBAC)
"""
from functools import wraps
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================================

# Módulos disponibles en el sistema
AVAILABLE_MODULES = [
    'dashboard', 'inventario', 'usuarios', 'ventas', 
    'recetas', 'reportes', 'proveedores', 'configuracion'
]

# Sub-módulos dentro de inventario para control granular
INVENTARIO_SUBMODULES = [
    'inventario.insumos',           # Insumos básicos
    'inventario.entradas_salidas',  # Entradas y salidas de inventario
    'inventario.insumos_compuestos', # Insumos compuestos
    'inventario.insumos_elaborados', # Insumos elaborados  
    'inventario.recetas',           # Recetas (dentro de inventario)
    'inventario.proveedores',       # Proveedores (dentro de inventario)
]

# Acciones CRUD disponibles
AVAILABLE_ACTIONS = ['create', 'read', 'update', 'delete']

# Características especiales disponibles
AVAILABLE_FEATURES = [
    'ver_precios', 'ver_costos', 'ver_reportes_completos',
    'gestionar_usuarios', 'cambiar_configuracion', 'ver_datos_sensibles',
    'ver_todos_proveedores'  # Nueva característica para ver todos los proveedores
]

# Permisos por defecto para cada rol
DEFAULT_ROLE_PERMISSIONS = {
    'admin': {
        'modules': {module: True for module in AVAILABLE_MODULES},
        'actions': {action: ['*'] for action in AVAILABLE_ACTIONS},
        'features': {feature: True for feature in AVAILABLE_FEATURES}
    },    'gerente': {
        'modules': {
            'dashboard': True, 
            'inventario': True,  # Acceso general al inventario
            'usuarios': False,   # ❌ Sin acceso a gestión de usuarios
            'ventas': True, 
            'recetas': False,    # Sin acceso directo a recetas (solo las del inventario)
            'reportes': True, 
            'proveedores': False, # Sin acceso directo a proveedores (solo los del inventario)
            'configuracion': False,
            'sucursales': False  # ❌ Sin acceso a sucursales
        },'submodules': {
            # Control granular dentro de inventario
            'inventario.insumos': True,           # ✅ SÍ puede ver insumos básicos
            'inventario.entradas_salidas': True,  # ✅ SÍ puede ver entradas y salidas
            'inventario.insumos_compuestos': False, # ❌ NO puede ver insumos compuestos
            'inventario.insumos_elaborados': False, # ❌ NO puede ver insumos elaborados
            'inventario.recetas': False,          # ❌ NO puede ver recetas desde inventario
            'inventario.proveedores': True,       # ✅ SÍ puede ver proveedores desde inventario
        },        'actions': {
            'create': ['inventario.insumos', 'inventario.entradas_salidas', 'ventas', 'inventario.proveedores'],
            'read': ['*'],
            'update': ['inventario.insumos', 'inventario.entradas_salidas', 'ventas', 'inventario.proveedores'],
            'delete': ['inventario.insumos', 'inventario.entradas_salidas', 'ventas']
        },
        'features': {
            'ver_precios': True, 
            'ver_costos': True, 
            'ver_reportes_completos': True,
            'gestionar_usuarios': False, 
            'cambiar_configuracion': False, 
            'ver_datos_sensibles': False,    # ❌ NO puede ver datos sensibles
            'filtrar_por_sucursal': True,    # ✅ Solo ve datos de su sucursal
        }
    },    'supervisor': {
        'modules': {
            'dashboard': True, 'inventario': True, 'usuarios': False,
            'ventas': True, 'recetas': True, 'reportes': False,
            'proveedores': False, 'configuracion': False, 'sucursales': False
        },
        'actions': {
            'create': ['inventario', 'ventas'],
            'read': ['dashboard', 'inventario', 'ventas', 'recetas'],
            'update': ['inventario'],
            'delete': []
        },
        'features': {
            'ver_precios': True, 'ver_costos': False, 'ver_reportes_completos': False,
            'gestionar_usuarios': False, 'cambiar_configuracion': False, 'ver_datos_sensibles': False
        }
    },    'cajero': {
        'modules': {
            'dashboard': True, 'inventario': False, 'usuarios': False,
            'ventas': True, 'recetas': False, 'reportes': False,
            'proveedores': False, 'configuracion': False, 'sucursales': False
        },
        'actions': {
            'create': ['ventas'],
            'read': ['dashboard', 'ventas'],
            'update': ['ventas'],
            'delete': []
        },
        'features': {
            'ver_precios': True, 'ver_costos': False, 'ver_reportes_completos': False,
            'gestionar_usuarios': False, 'cambiar_configuracion': False, 'ver_datos_sensibles': False
        }
    },    'cocinero': {
        'modules': {
            'dashboard': True, 'inventario': True, 'usuarios': False,
            'ventas': False, 'recetas': True, 'reportes': False,
            'proveedores': False, 'configuracion': False, 'sucursales': False
        },
        'actions': {
            'create': ['recetas'],
            'read': ['dashboard', 'inventario', 'recetas'],
            'update': ['recetas'],
            'delete': []
        },
        'features': {
            'ver_precios': False, 'ver_costos': True, 'ver_reportes_completos': False,
            'gestionar_usuarios': False, 'cambiar_configuracion': False, 'ver_datos_sensibles': False
        }
    },
    'mesero': {
        'modules': {
            'dashboard': True, 'inventario': False, 'usuarios': False,
            'ventas': True, 'recetas': True, 'reportes': False,
            'proveedores': False, 'configuracion': False
        },
        'actions': {
            'create': ['ventas'],
            'read': ['dashboard', 'ventas', 'recetas'],
            'update': [],
            'delete': []
        },
        'features': {
            'ver_precios': True, 'ver_costos': False, 'ver_reportes_completos': False,
            'gestionar_usuarios': False, 'cambiar_configuracion': False, 'ver_datos_sensibles': False
        }
    },
    'inventario': {
        'modules': {
            'dashboard': True, 'inventario': True, 'usuarios': False,
            'ventas': False, 'recetas': True, 'reportes': False,
            'proveedores': True, 'configuracion': False
        },
        'actions': {
            'create': ['inventario', 'proveedores'],
            'read': ['dashboard', 'inventario', 'recetas', 'proveedores'],
            'update': ['inventario', 'proveedores'],
            'delete': ['inventario']
        },
        'features': {
            'ver_precios': True, 'ver_costos': True, 'ver_reportes_completos': False,
            'gestionar_usuarios': False, 'cambiar_configuracion': False, 'ver_datos_sensibles': False
        }
    },
    'rrhh': {
        'modules': {
            'dashboard': True, 'inventario': False, 'usuarios': True,
            'ventas': False, 'recetas': False, 'reportes': True,
            'proveedores': False, 'configuracion': False
        },
        'actions': {
            'create': ['usuarios'],
            'read': ['dashboard', 'usuarios', 'reportes'],
            'update': ['usuarios'],
            'delete': []
        },
        'features': {
            'ver_precios': False, 'ver_costos': False, 'ver_reportes_completos': False,
            'gestionar_usuarios': True, 'cambiar_configuracion': False, 'ver_datos_sensibles': True
        }
    }
}

# ============================================================================
# FUNCIONES PRINCIPALES DE VERIFICACIÓN DE PERMISOS
# ============================================================================

def get_user_permissions(user):
    """
    Obtiene los permisos de un usuario desde cache o base de datos
    
    Args:
        user: Instancia del usuario
        
    Returns:
        dict: Diccionario con los permisos del usuario
    """
    if not user.is_authenticated:
        return {}
    
    # Verificar si es superusuario
    if user.is_superuser:
        return DEFAULT_ROLE_PERMISSIONS['admin']
    
    # Cache key única por usuario
    cache_key = f"user_permissions_{user.id}"
    permissions = cache.get(cache_key)
    
    if permissions is None:
        # Obtener permisos del rol del usuario
        if user.rol and user.rol.activo:
            # Si el rol tiene permisos configurados, usarlos
            if user.rol.permisos:
                permissions = user.rol.permisos
            else:
                # Si no tiene permisos configurados, usar los por defecto
                permissions = DEFAULT_ROLE_PERMISSIONS.get(user.rol.nombre, {})
        else:
            # Usuario sin rol activo
            permissions = {}
        
        # Guardar en cache por 5 minutos
        cache.set(cache_key, permissions, 300)
        logger.info(f"Permisos cargados para usuario {user.username}: {permissions}")
    
    return permissions

def invalidate_user_permissions(user):
    """
    Invalida el cache de permisos de un usuario
    
    Args:
        user: Instancia del usuario
    """
    cache_key = f"user_permissions_{user.id}"
    cache.delete(cache_key)
    logger.info(f"Cache de permisos invalidado para usuario {user.username}")

def has_module_access(user, module_name):
    """
    Verifica si el usuario tiene acceso a un módulo específico
    
    Args:
        user: Instancia del usuario
        module_name: Nombre del módulo
        
    Returns:
        bool: True si tiene acceso, False en caso contrario
    """
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    permissions = get_user_permissions(user)
    modules = permissions.get('modules', {})
    
    return modules.get(module_name, False)

def has_submodule_access(user, module_name, submodule_name):
    """
    Verifica si un usuario tiene acceso a un submódulo específico
    
    Args:
        user: Usuario a verificar
        module_name (str): Nombre del módulo principal
        submodule_name (str): Nombre del submódulo
        
    Returns:
        bool: True si el usuario tiene acceso al submódulo
    """
    try:
        # Verificar si el usuario está autenticado
        if not user or not user.is_authenticated:
            return False
        
        # Super usuarios tienen acceso a todo
        if user.is_superuser:
            return True
        
        # Obtener permisos del usuario
        permissions = get_user_permissions(user)
        
        # Construir la clave del submódulo
        submodule_key = f"{module_name}.{submodule_name}"
        
        # Verificar acceso al submódulo específico
        if 'submodules' in permissions:
            return permissions['submodules'].get(submodule_key, False)
        
        # Si no hay submódulos definidos, verificar acceso al módulo principal
        return has_module_access(user, module_name)
        
    except Exception as e:
        logger.error(f"Error verificando acceso a submódulo {module_name}.{submodule_name} para usuario {user}: {e}")
        return False

def has_permission(user, module_name, action):
    """
    Verifica si el usuario tiene un permiso específico en un módulo
    
    Args:
        user: Instancia del usuario
        module_name: Nombre del módulo
        action: Acción a verificar (create, read, update, delete)
        
    Returns:
        bool: True si tiene el permiso, False en caso contrario
    """
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    permissions = get_user_permissions(user)
    actions = permissions.get('actions', {})
    allowed_modules = actions.get(action, [])
    
    # Si tiene acceso a todos los módulos para esta acción
    if '*' in allowed_modules:
        return True
    
    # Verificar si el módulo específico está permitido
    return module_name in allowed_modules

def has_feature(user, feature_name):
    """
    Verifica si el usuario tiene acceso a una característica específica
    
    Args:
        user: Instancia del usuario
        feature_name: Nombre de la característica
        
    Returns:
        bool: True si tiene acceso, False en caso contrario
    """
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    permissions = get_user_permissions(user)
    features = permissions.get('features', {})
    
    return features.get(feature_name, False)

def get_accessible_modules(user):
    """
    Obtiene la lista de módulos accesibles para un usuario
    
    Args:
        user: Instancia del usuario
        
    Returns:
        list: Lista de nombres de módulos accesibles
    """
    if not user.is_authenticated:
        return []
    
    if user.is_superuser:
        return AVAILABLE_MODULES
    
    permissions = get_user_permissions(user)
    modules = permissions.get('modules', {})
    
    return [module for module, access in modules.items() if access]

def get_user_capabilities(user):
    """
    Obtiene un resumen completo de las capacidades del usuario
    
    Args:
        user: Instancia del usuario
        
    Returns:
        dict: Diccionario con resumen de capacidades
    """
    if not user.is_authenticated:
        return {
            'modules': [],
            'can_create': [],
            'can_update': [],
            'can_delete': [],
            'features': [],
            'role': None,
            'is_admin': False
        }
    
    permissions = get_user_permissions(user)
    
    return {
        'modules': get_accessible_modules(user),
        'can_create': permissions.get('actions', {}).get('create', []),
        'can_update': permissions.get('actions', {}).get('update', []),
        'can_delete': permissions.get('actions', {}).get('delete', []),
        'features': [f for f, enabled in permissions.get('features', {}).items() if enabled],
        'role': user.rol.nombre if user.rol else None,
        'is_admin': user.is_superuser or (user.rol and user.rol.nombre == 'admin')
    }

# ============================================================================
# DECORADORES AVANZADOS DE PERMISOS
# ============================================================================

def require_module_access(module_name):
    """
    Decorador que requiere acceso a un módulo específico
    
    Args:
        module_name: Nombre del módulo requerido
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not has_module_access(request.user, module_name):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'No tienes acceso al módulo {module_name}',
                        'redirect': '/dashboard/'
                    }, status=403)
                else:
                    messages.error(request, f'No tienes acceso al módulo {module_name}')
                    return redirect('dashboard:principal')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def require_permission(module_name, action):
    """
    Decorador que requiere un permiso específico
    
    Args:
        module_name: Nombre del módulo
        action: Acción requerida (create, read, update, delete)
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not has_permission(request.user, module_name, action):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'No tienes permisos para {action} en {module_name}',
                        'redirect': '/dashboard/'
                    }, status=403)
                else:
                    messages.error(request, f'No tienes permisos para {action} en {module_name}')
                    return redirect('dashboard:principal')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def require_feature(feature_name):
    """
    Decorador que requiere una característica específica
    
    Args:
        feature_name: Nombre de la característica requerida
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not has_feature(request.user, feature_name):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'No tienes acceso a la característica {feature_name}',
                        'redirect': '/dashboard/'
                    }, status=403)
                else:
                    messages.error(request, f'No tienes acceso a la característica {feature_name}')
                    return redirect('dashboard:principal')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def require_role(*role_names):
    """
    Decorador que requiere uno de los roles especificados
    
    Args:
        role_names: Nombres de roles permitidos
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user_role = request.user.rol.nombre if request.user.rol else None
            
            if not request.user.is_superuser and user_role not in role_names:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Requiere uno de los siguientes roles: {", ".join(role_names)}',
                        'redirect': '/dashboard/'
                    }, status=403)
                else:
                    messages.error(request, f'Requiere uno de los siguientes roles: {", ".join(role_names)}')
                    return redirect('dashboard:principal')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def require_submodule_access(module_name, submodule_name):
    """
    Decorador que requiere acceso a un submódulo específico
    
    Args:
        module_name (str): Nombre del módulo principal
        submodule_name (str): Nombre del submódulo
        
    Returns:
        decorator: Decorador que verifica el acceso al submódulo
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Verificar autenticación
            if not request.user.is_authenticated:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Debes iniciar sesión para acceder a esta función',
                        'redirect': '/dashboard/login/'
                    }, status=401)
                return redirect('/dashboard/login/')
            
            # Verificar acceso al submódulo
            if not has_submodule_access(request.user, module_name, submodule_name):
                error_message = f'No tienes permisos para acceder a {module_name}.{submodule_name}'
                logger.warning(f"Acceso denegado a {module_name}.{submodule_name} para usuario {request.user.username}")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': error_message
                    }, status=403)
                
                messages.error(request, error_message)
                return redirect('/dashboard/')
            
            # Log del acceso exitoso
            logger.info(f"Acceso concedido a {module_name}.{submodule_name} para usuario {request.user.username}")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# ============================================================================
# FUNCIONES DE COMPATIBILIDAD CON SISTEMA ANTERIOR
# ============================================================================

def is_admin_or_manager(user):
    """Función de compatibilidad con el sistema anterior"""
    return user.is_superuser or has_permission(user, 'usuarios', 'create') or (user.rol and user.rol.nombre in ['admin', 'gerente'])

def is_admin(user):
    """Función de compatibilidad con el sistema anterior"""
    return user.is_superuser or (user.rol and user.rol.nombre == 'admin')

# ============================================================================
# UTILIDADES ADICIONALES
# ============================================================================

def get_permission_summary_for_role(role_name):
    """
    Obtiene un resumen de permisos para un rol específico
    
    Args:
        role_name: Nombre del rol
        
    Returns:
        dict: Resumen de permisos del rol
    """
    permissions = DEFAULT_ROLE_PERMISSIONS.get(role_name, {})
    
    if not permissions:
        return {
            'modules': [],
            'actions': {},
            'features': [],
            'summary': f'Rol {role_name} no encontrado'
        }
    
    modules = [m for m, access in permissions.get('modules', {}).items() if access]
    features = [f for f, enabled in permissions.get('features', {}).items() if enabled]
    
    return {
        'modules': modules,
        'actions': permissions.get('actions', {}),
        'features': features,
        'summary': f'Acceso a {len(modules)} módulos, {len(features)} características especiales'
    }

def log_permission_check(user, module_name, action, result):
    """
    Registra verificaciones de permisos para auditoría
    
    Args:
        user: Usuario que realiza la acción
        module_name: Módulo verificado
        action: Acción verificada
        result: Resultado de la verificación
    """
    logger.info(f"Permission check - User: {user.username}, Module: {module_name}, Action: {action}, Result: {result}")
