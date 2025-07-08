"""
Mixins para vistas basadas en clase con control de acceso por roles
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import View
from .permissions import (
    has_module_access, has_permission, has_feature, 
    get_user_permissions, get_accessible_modules
)


class PermissionRequiredMixin(LoginRequiredMixin):
    """
    Mixin que requiere permisos específicos para acceder a la vista
    """
    required_permission = None  # Tupla (module, action)
    permission_denied_message = "No tienes permisos para acceder a esta funcionalidad"
    
    def dispatch(self, request, *args, **kwargs):
        if not self.has_required_permission():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    
    def has_required_permission(self):
        """
        Verifica si el usuario tiene los permisos requeridos
        """
        if not self.required_permission:
            return True
        
        if isinstance(self.required_permission, tuple) and len(self.required_permission) == 2:
            module, action = self.required_permission
            return has_permission(self.request.user, module, action)
        
        return False
    
    def handle_no_permission(self):
        """
        Maneja el caso cuando el usuario no tiene permisos
        """
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': self.permission_denied_message,
                'redirect': '/dashboard/'
            }, status=403)
        else:
            messages.error(self.request, self.permission_denied_message)
            return redirect('dashboard:principal')


class ModuleAccessMixin(LoginRequiredMixin):
    """
    Mixin que requiere acceso a un módulo específico
    """
    required_module = None
    module_denied_message = "No tienes acceso a este módulo"
    
    def dispatch(self, request, *args, **kwargs):
        if not self.has_module_access():
            return self.handle_no_module_access()
        return super().dispatch(request, *args, **kwargs)
    
    def has_module_access(self):
        """
        Verifica si el usuario tiene acceso al módulo requerido
        """
        if not self.required_module:
            return True
        
        return has_module_access(self.request.user, self.required_module)
    
    def handle_no_module_access(self):
        """
        Maneja el caso cuando el usuario no tiene acceso al módulo
        """
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': self.module_denied_message,
                'redirect': '/dashboard/'
            }, status=403)
        else:
            messages.error(self.request, self.module_denied_message)
            return redirect('dashboard:principal')


class FeatureAccessMixin(LoginRequiredMixin):
    """
    Mixin que requiere acceso a una característica específica
    """
    required_feature = None
    feature_denied_message = "No tienes acceso a esta característica"
    
    def dispatch(self, request, *args, **kwargs):
        if not self.has_feature_access():
            return self.handle_no_feature_access()
        return super().dispatch(request, *args, **kwargs)
    
    def has_feature_access(self):
        """
        Verifica si el usuario tiene acceso a la característica requerida
        """
        if not self.required_feature:
            return True
        
        return has_feature(self.request.user, self.required_feature)
    
    def handle_no_feature_access(self):
        """
        Maneja el caso cuando el usuario no tiene acceso a la característica
        """
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': self.feature_denied_message,
                'redirect': '/dashboard/'
            }, status=403)
        else:
            messages.error(self.request, self.feature_denied_message)
            return redirect('dashboard:principal')


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin que requiere uno de los roles específicos
    """
    required_roles = []  # Lista de roles permitidos
    role_denied_message = "No tienes el rol necesario para acceder a esta funcionalidad"
    
    def dispatch(self, request, *args, **kwargs):
        if not self.has_required_role():
            return self.handle_no_role()
        return super().dispatch(request, *args, **kwargs)
    
    def has_required_role(self):
        """
        Verifica si el usuario tiene uno de los roles requeridos
        """
        if not self.required_roles:
            return True
        
        if self.request.user.is_superuser:
            return True
        
        user_role = self.request.user.rol.nombre if self.request.user.rol else None
        return user_role in self.required_roles
    
    def handle_no_role(self):
        """
        Maneja el caso cuando el usuario no tiene el rol requerido
        """
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': self.role_denied_message,
                'redirect': '/dashboard/'
            }, status=403)
        else:
            messages.error(self.request, self.role_denied_message)
            return redirect('dashboard:principal')


class AdminRequiredMixin(RoleRequiredMixin):
    """
    Mixin que requiere rol de administrador
    """
    required_roles = ['admin']
    role_denied_message = "Requiere permisos de administrador"


class ManagerRequiredMixin(RoleRequiredMixin):
    """
    Mixin que requiere rol de gerente o superior
    """
    required_roles = ['admin', 'gerente']
    role_denied_message = "Requiere permisos de gerente o superior"


class SupervisorRequiredMixin(RoleRequiredMixin):
    """
    Mixin que requiere rol de supervisor o superior
    """
    required_roles = ['admin', 'gerente', 'supervisor']
    role_denied_message = "Requiere permisos de supervisor o superior"


class PermissionContextMixin:
    """
    Mixin que agrega información de permisos al contexto de la vista
    """
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            user_permissions = get_user_permissions(self.request.user)
            accessible_modules = get_accessible_modules(self.request.user)
            
            context.update({
                'user_permissions': user_permissions,
                'accessible_modules': accessible_modules,
                'user_role': self.request.user.rol.nombre if self.request.user.rol else None,
                'is_admin': self.request.user.is_superuser or (
                    self.request.user.rol and self.request.user.rol.nombre == 'admin'
                ),
                'is_manager': self.request.user.is_superuser or (
                    self.request.user.rol and self.request.user.rol.nombre in ['admin', 'gerente']
                ),
            })
        
        return context


class ConditionalPermissionMixin:
    """
    Mixin para vistas que requieren diferentes permisos según el método HTTP
    """
    permission_map = {
        'GET': None,      # (module, action) para GET
        'POST': None,     # (module, action) para POST
        'PUT': None,      # (module, action) para PUT
        'DELETE': None,   # (module, action) para DELETE
    }
    
    def dispatch(self, request, *args, **kwargs):
        required_permission = self.permission_map.get(request.method.upper())
        
        if required_permission:
            module, action = required_permission
            if not has_permission(request.user, module, action):
                return self.handle_no_permission(module, action)
        
        return super().dispatch(request, *args, **kwargs)
    
    def handle_no_permission(self, module, action):
        """
        Maneja el caso cuando el usuario no tiene el permiso requerido
        """
        message = f"No tienes permisos para {action} en {module}"
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': message,
                'redirect': '/dashboard/'
            }, status=403)
        else:
            messages.error(self.request, message)
            return redirect('dashboard:principal')


# ============================================================================
# MIXINS COMBINADOS PARA CASOS COMUNES
# ============================================================================

class InventarioAccessMixin(ModuleAccessMixin):
    """Mixin para vistas que requieren acceso al módulo de inventario"""
    required_module = 'inventario'
    module_denied_message = "No tienes acceso al módulo de inventario"


class UsuariosAccessMixin(ModuleAccessMixin):
    """Mixin para vistas que requieren acceso al módulo de usuarios"""
    required_module = 'usuarios'
    module_denied_message = "No tienes acceso al módulo de usuarios"


class VentasAccessMixin(ModuleAccessMixin):
    """Mixin para vistas que requieren acceso al módulo de ventas"""
    required_module = 'ventas'
    module_denied_message = "No tienes acceso al módulo de ventas"


class RecetasAccessMixin(ModuleAccessMixin):
    """Mixin para vistas que requieren acceso al módulo de recetas"""
    required_module = 'recetas'
    module_denied_message = "No tienes acceso al módulo de recetas"


class ReportesAccessMixin(ModuleAccessMixin):
    """Mixin para vistas que requieren acceso al módulo de reportes"""
    required_module = 'reportes'
    module_denied_message = "No tienes acceso al módulo de reportes"


class ProveedoresAccessMixin(ModuleAccessMixin):
    """Mixin para vistas que requieren acceso al módulo de proveedores"""
    required_module = 'proveedores'
    module_denied_message = "No tienes acceso al módulo de proveedores"


class ConfiguracionAccessMixin(ModuleAccessMixin):
    """Mixin para vistas que requieren acceso al módulo de configuración"""
    required_module = 'configuracion'
    module_denied_message = "No tienes acceso al módulo de configuración"


# ============================================================================
# EJEMPLOS DE USO
# ============================================================================

"""
Ejemplos de cómo usar estos mixins en vistas basadas en clase:

# Ejemplo 1: Vista que requiere acceso al módulo de inventario
class InventarioListView(InventarioAccessMixin, PermissionContextMixin, ListView):
    model = Inventario
    template_name = 'inventario/lista.html'

# Ejemplo 2: Vista que requiere permisos específicos
class CrearInsumoView(PermissionRequiredMixin, CreateView):
    required_permission = ('inventario', 'create')
    model = Insumo
    template_name = 'inventario/crear_insumo.html'

# Ejemplo 3: Vista que requiere una característica específica
class ReportesCostosView(FeatureAccessMixin, TemplateView):
    required_feature = 'ver_costos'
    template_name = 'reportes/costos.html'

# Ejemplo 4: Vista con permisos condicionales por método
class UsuarioAPIView(ConditionalPermissionMixin, View):
    permission_map = {
        'GET': ('usuarios', 'read'),
        'POST': ('usuarios', 'create'),
        'PUT': ('usuarios', 'update'),
        'DELETE': ('usuarios', 'delete'),
    }

# Ejemplo 5: Vista que combina múltiples mixins
class UsuarioDetailView(
    UsuariosAccessMixin, 
    PermissionContextMixin, 
    ManagerRequiredMixin, 
    DetailView
):
    model = Usuario
    template_name = 'usuarios/detalle.html'
"""
