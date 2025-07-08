"""
Template tags personalizados para manejo de permisos
"""
from django import template
from django.template.context import RequestContext
from ..utils.permissions import (
    has_module_access, has_permission, has_feature,
    get_user_capabilities, get_accessible_modules
)

register = template.Library()


@register.filter
def has_module_access_filter(user, module_name):
    """
    Template filter para verificar acceso a módulo
    Uso: {% if user|has_module_access:'inventario' %}
    """
    return has_module_access(user, module_name)


@register.filter
def has_permission_filter(user, permission_string):
    """
    Template filter para verificar permisos específicos
    Uso: {% if user|has_permission:'inventario:create' %}
    """
    try:
        module, action = permission_string.split(':')
        return has_permission(user, module, action)
    except ValueError:
        return False


@register.filter
def has_feature_filter(user, feature_name):
    """
    Template filter para verificar características
    Uso: {% if user|has_feature:'ver_costos' %}
    """
    return has_feature(user, feature_name)


@register.filter
def can_create(user, module_name):
    """
    Template filter para verificar permiso de creación
    Uso: {% if user|can_create:'inventario' %}
    """
    return has_permission(user, module_name, 'create')


@register.filter
def can_update(user, module_name):
    """
    Template filter para verificar permiso de actualización
    Uso: {% if user|can_update:'inventario' %}
    """
    return has_permission(user, module_name, 'update')


@register.filter
def can_delete(user, module_name):
    """
    Template filter para verificar permiso de eliminación
    Uso: {% if user|can_delete:'inventario' %}
    """
    return has_permission(user, module_name, 'delete')


@register.filter
def can_read(user, module_name):
    """
    Template filter para verificar permiso de lectura
    Uso: {% if user|can_read:'inventario' %}
    """
    return has_permission(user, module_name, 'read')


@register.simple_tag
def user_capabilities(user):
    """
    Template tag para obtener capacidades completas del usuario
    Uso: {% user_capabilities user as capabilities %}
    """
    return get_user_capabilities(user)


@register.simple_tag
def accessible_modules(user):
    """
    Template tag para obtener módulos accesibles
    Uso: {% accessible_modules user as modules %}
    """
    return get_accessible_modules(user)


@register.inclusion_tag('dashboard/components/permission_required_button.html')
def permission_button(user, module, action, button_text, button_class="btn btn-primary", icon="", **kwargs):
    """
    Template tag de inclusión para mostrar botones condicionalmente
    Uso: {% permission_button user 'inventario' 'create' 'Crear Insumo' 'btn btn-success' 'fas fa-plus' %}
    """
    has_perm = has_permission(user, module, action)
    
    return {
        'show_button': has_perm,
        'button_text': button_text,
        'button_class': button_class,
        'icon': icon,
        'module': module,
        'action': action,
        'extra_attrs': kwargs
    }


@register.inclusion_tag('dashboard/components/module_access_section.html')
def module_section(user, module_name, title, content):
    """
    Template tag de inclusión para mostrar secciones completas condicionalmente
    Uso: {% module_section user 'inventario' 'Gestión de Inventario' %}...{% endmodule_section %}
    """
    has_access = has_module_access(user, module_name)
    
    return {
        'show_section': has_access,
        'module_name': module_name,
        'title': title,
        'content': content
    }


@register.inclusion_tag('dashboard/components/feature_content.html')
def feature_content(user, feature_name, content=""):
    """
    Template tag de inclusión para mostrar contenido basado en características
    Uso: {% feature_content user 'ver_costos' %}Contenido sensible{% endfeature_content %}
    """
    has_feat = has_feature(user, feature_name)
    
    return {
        'show_content': has_feat,
        'feature_name': feature_name,
        'content': content
    }


@register.simple_tag
def role_badge_class(role_name):
    """
    Template tag para obtener la clase CSS del badge de rol
    Uso: {% role_badge_class user.rol.nombre %}
    """
    role_classes = {
        'admin': 'badge bg-danger',
        'gerente': 'badge bg-primary',
        'supervisor': 'badge bg-success',
        'cajero': 'badge bg-warning',
        'cocinero': 'badge bg-danger',
        'mesero': 'badge bg-info',
        'inventario': 'badge bg-secondary',
        'rrhh': 'badge bg-dark',
    }
    
    return role_classes.get(role_name, 'badge bg-light')


@register.simple_tag
def role_icon(role_name):
    """
    Template tag para obtener el ícono del rol
    Uso: {% role_icon user.rol.nombre %}
    """
    role_icons = {
        'admin': 'fas fa-crown',
        'gerente': 'fas fa-user-tie',
        'supervisor': 'fas fa-user-cog',
        'cajero': 'fas fa-cash-register',
        'cocinero': 'fas fa-utensils',
        'mesero': 'fas fa-concierge-bell',
        'inventario': 'fas fa-boxes',
        'rrhh': 'fas fa-users',
    }
    
    return role_icons.get(role_name, 'fas fa-user')


@register.filter
def permission_debug(user):
    """
    Template filter para debugging de permisos (solo en desarrollo)
    Uso: {{ user|permission_debug }}
    """
    from django.conf import settings
    
    if not settings.DEBUG:
        return ""
    
    capabilities = get_user_capabilities(user)
    return f"Debug: {capabilities}"


@register.simple_tag(takes_context=True)
def can_access_url(context, url_name, *args, **kwargs):
    """
    Template tag para verificar si el usuario puede acceder a una URL específica
    Requiere mapeo de URLs a permisos (se puede extender)
    Uso: {% can_access_url 'dashboard:crear_usuario' as can_access %}
    """
    # Mapeo básico de URLs a permisos (se puede extender)
    url_permissions = {
        'dashboard:usuarios': ('usuarios', 'read'),
        'dashboard:crear_usuario': ('usuarios', 'create'),
        'dashboard:inventario': ('inventario', 'read'),
        'dashboard:crear_insumo': ('inventario', 'create'),
        'dashboard:reportes': ('reportes', 'read'),
        'dashboard:configuracion': ('configuracion', 'read'),
    }
    
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return False
    
    permission = url_permissions.get(url_name)
    if permission:
        module, action = permission
        return has_permission(request.user, module, action)
    
    return True  # Por defecto permitir si no hay restricción definida


@register.simple_tag
def permission_message(module, action):
    """
    Template tag para generar mensajes de permisos
    Uso: {% permission_message 'inventario' 'create' %}
    """
    action_names = {
        'create': 'crear',
        'read': 'ver',
        'update': 'editar',
        'delete': 'eliminar'
    }
    
    module_names = {
        'inventario': 'inventario',
        'usuarios': 'usuarios',
        'ventas': 'ventas',
        'recetas': 'recetas',
        'reportes': 'reportes',
        'proveedores': 'proveedores',
        'configuracion': 'configuración'
    }
    
    action_name = action_names.get(action, action)
    module_name = module_names.get(module, module)
    
    return f"No tienes permisos para {action_name} en {module_name}"

# Alias para compatibilidad con templates existentes
register.filter('has_feature', has_feature_filter)
register.filter('has_module_access', has_module_access_filter)
register.filter('has_permission', has_permission_filter)
