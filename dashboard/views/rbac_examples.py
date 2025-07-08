"""
Ejemplos de vistas usando el nuevo sistema RBAC
"""
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django import forms
from accounts.models import Usuario, Rol
from dashboard.utils.mixins import (
    PermissionRequiredMixin, ModuleAccessMixin, FeatureAccessMixin,
    UsuariosAccessMixin, PermissionContextMixin, ManagerRequiredMixin,
    ConditionalPermissionMixin
)
from dashboard.utils.permissions import require_module_access, require_permission


# ============================================================================
# EJEMPLOS CON DECORADORES (Function-Based Views)
# ============================================================================

@login_required
@require_module_access('reportes')
def reportes_view(request):
    """Vista de reportes que requiere acceso al módulo de reportes"""
    return render(request, 'dashboard/reportes.html', {
        'title': 'Reportes del Sistema'
    })


@login_required
@require_permission('inventario', 'create')
def crear_insumo_view(request):
    """Vista para crear insumo que requiere permiso específico"""
    if request.method == 'POST':
        # Lógica para crear insumo
        return JsonResponse({'success': True, 'message': 'Insumo creado'})
    
    return render(request, 'inventario/crear_insumo.html')


# ============================================================================
# EJEMPLOS CON MIXINS (Class-Based Views)
# ============================================================================

class UsuariosListView(UsuariosAccessMixin, PermissionContextMixin, ListView):
    """
    Vista para listar usuarios que requiere acceso al módulo de usuarios
    También inyecta información de permisos en el contexto
    """
    model = Usuario
    template_name = 'dashboard/usuarios_list.html'
    context_object_name = 'usuarios'
    paginate_by = 20
    
    def get_queryset(self):
        """Personalizar queryset según permisos del usuario"""
        queryset = super().get_queryset()
        
        # Si no es admin, solo mostrar usuarios de su sucursal
        if not self.request.user.is_superuser:
            if hasattr(self.request.user, 'sucursal') and self.request.user.sucursal:
                queryset = queryset.filter(sucursal=self.request.user.sucursal)
        
        return queryset.select_related('rol', 'sucursal')


class UsuarioDetailView(UsuariosAccessMixin, PermissionContextMixin, DetailView):
    """
    Vista de detalle de usuario con control de acceso
    """
    model = Usuario
    template_name = 'dashboard/usuario_detail.html'
    context_object_name = 'usuario'


class UsuarioCreateView(PermissionRequiredMixin, PermissionContextMixin, CreateView):
    """
    Vista para crear usuario que requiere permiso específico de creación
    """
    model = Usuario
    template_name = 'dashboard/usuario_create.html'
    required_permission = ('usuarios', 'create')
    fields = ['username', 'email', 'first_name', 'last_name', 'rol', 'sucursal']
    
    def form_valid(self, form):
        """Personalizar guardado según rol del usuario"""
        response = super().form_valid(form)
        
        # Si no es admin, asignar automáticamente su sucursal
        if not self.request.user.is_superuser:
            if hasattr(self.request.user, 'sucursal') and self.request.user.sucursal:
                self.object.sucursal = self.request.user.sucursal
                self.object.save()
        
        return response


class UsuarioUpdateView(PermissionRequiredMixin, PermissionContextMixin, UpdateView):
    """
    Vista para actualizar usuario con permisos específicos
    """
    model = Usuario
    template_name = 'dashboard/usuario_update.html'
    required_permission = ('usuarios', 'update')
    fields = ['username', 'email', 'first_name', 'last_name', 'is_active']
    
    def get_form_class(self):
        """Personalizar campos del formulario según permisos"""
        form_class = super().get_form_class()
        
        # Solo administradores pueden cambiar roles
        if self.request.user.is_superuser or (
            hasattr(self.request.user, 'rol') and 
            self.request.user.rol and 
            self.request.user.rol.nombre == 'admin'
        ):
            form_class.base_fields['rol'] = forms.ModelChoiceField(
                queryset=Rol.objects.filter(activo=True)
            )
        
        return form_class


class UsuarioDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Vista para eliminar usuario (solo administradores)
    """
    model = Usuario
    template_name = 'dashboard/usuario_delete.html'
    required_permission = ('usuarios', 'delete')
    success_url = '/dashboard/usuarios/'
    
    def delete(self, request, *args, **kwargs):
        """Prevenir auto-eliminación"""
        if self.get_object() == request.user:
            return JsonResponse({
                'success': False,
                'message': 'No puedes eliminar tu propio usuario'
            }, status=400)
        
        return super().delete(request, *args, **kwargs)


class ReportesCostosView(FeatureAccessMixin, PermissionContextMixin, ListView):
    """
    Vista de reportes de costos que requiere característica específica
    """
    required_feature = 'ver_costos'
    template_name = 'reportes/costos.html'
    context_object_name = 'reportes'
    
    def get_queryset(self):
        """Generar datos de reportes de costos"""
        # Aquí iría la lógica para generar reportes de costos
        return []


class ConfiguracionView(ManagerRequiredMixin, PermissionContextMixin, ListView):
    """
    Vista de configuración solo para gerentes o superiores
    """
    template_name = 'dashboard/configuracion.html'
    
    def get_queryset(self):
        return []  # No necesita queryset real


class UsuarioAPIView(ConditionalPermissionMixin, DetailView):
    """
    API REST para usuarios con permisos condicionales por método HTTP
    """
    model = Usuario
    permission_map = {
        'GET': ('usuarios', 'read'),
        'POST': ('usuarios', 'create'),
        'PUT': ('usuarios', 'update'),
        'DELETE': ('usuarios', 'delete'),
    }
    
    def get(self, request, *args, **kwargs):
        """GET: Obtener datos del usuario"""
        usuario = self.get_object()
        return JsonResponse({
            'id': usuario.id,
            'username': usuario.username,
            'email': usuario.email,
            'full_name': usuario.get_full_name(),
            'rol': usuario.rol.nombre if usuario.rol else None,
            'sucursal': usuario.sucursal.nombre if usuario.sucursal else None,
            'is_active': usuario.is_active,
        })
    
    def post(self, request, *args, **kwargs):
        """POST: Crear nuevo usuario"""
        # Lógica para crear usuario via API
        return JsonResponse({'success': True, 'message': 'Usuario creado'})
    
    def put(self, request, *args, **kwargs):
        """PUT: Actualizar usuario"""
        # Lógica para actualizar usuario via API
        return JsonResponse({'success': True, 'message': 'Usuario actualizado'})
    
    def delete(self, request, *args, **kwargs):
        """DELETE: Eliminar usuario"""
        usuario = self.get_object()
        
        # Prevenir auto-eliminación
        if usuario == request.user:
            return JsonResponse({
                'success': False,
                'message': 'No puedes eliminar tu propio usuario'
            }, status=400)
        
        usuario.delete()
        return JsonResponse({'success': True, 'message': 'Usuario eliminado'})


# ============================================================================
# VISTA COMBINADA CON MÚLTIPLES MIXINS
# ============================================================================

class DashboardComplexView(
    ModuleAccessMixin,
    PermissionContextMixin,
    ManagerRequiredMixin,
    ListView
):
    """
    Vista compleja que combina múltiples tipos de control de acceso:
    - Requiere acceso al módulo dashboard
    - Requiere ser gerente o superior 
    - Inyecta contexto de permisos
    """
    required_module = 'dashboard'
    template_name = 'dashboard/complex_view.html'
    
    def get_queryset(self):
        return Usuario.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar datos específicos según permisos
        user = self.request.user
        
        if user.is_superuser:
            context['show_admin_panel'] = True
            context['sensitive_data'] = "Datos muy sensibles"
        
        # Usando los helpers de permisos inyectados por PermissionContextMixin
        if context.get('feature_access', {}).get('ver_costos'):
            context['cost_data'] = "Información de costos"
        
        if context.get('feature_access', {}).get('ver_reportes_completos'):
            context['full_reports'] = "Reportes completos"
        
        return context


# ============================================================================
# TEMPLATE PARA USAR EN URLS.PY
# ============================================================================

"""
# En dashboard/urls.py se pueden usar así:

from django.urls import path
from . import views_rbac_examples

urlpatterns = [
    # Function-based views
    path('reportes/', views_rbac_examples.reportes_view, name='reportes'),
    path('crear-insumo/', views_rbac_examples.crear_insumo_view, name='crear_insumo'),
    
    # Class-based views
    path('usuarios/', views_rbac_examples.UsuariosListView.as_view(), name='usuarios_list'),
    path('usuarios/<int:pk>/', views_rbac_examples.UsuarioDetailView.as_view(), name='usuario_detail'),
    path('usuarios/crear/', views_rbac_examples.UsuarioCreateView.as_view(), name='usuario_create'),
    path('usuarios/<int:pk>/editar/', views_rbac_examples.UsuarioUpdateView.as_view(), name='usuario_update'),
    path('usuarios/<int:pk>/eliminar/', views_rbac_examples.UsuarioDeleteView.as_view(), name='usuario_delete'),
    
    # Vistas con características específicas
    path('reportes/costos/', views_rbac_examples.ReportesCostosView.as_view(), name='reportes_costos'),
    path('configuracion/', views_rbac_examples.ConfiguracionView.as_view(), name='configuracion'),
    
    # API con permisos condicionales
    path('api/usuarios/<int:pk>/', views_rbac_examples.UsuarioAPIView.as_view(), name='usuario_api'),
    
    # Vista compleja
    path('dashboard-complex/', views_rbac_examples.DashboardComplexView.as_view(), name='dashboard_complex'),
]
"""
