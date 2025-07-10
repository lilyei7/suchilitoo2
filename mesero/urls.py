from django.urls import path
from . import views
from . import debug_views

app_name = 'mesero'

urlpatterns = [
    # URLs para inventario
    path('inventario/status/', views.inventario_status, name='inventario_status'),
    path('inventario/verificar-stock/<int:producto_id>/', views.verificar_stock_producto, name='verificar_stock_producto'),

    path('login/', views.login_view, name='login'),
    path('menu/', views.menu, name='menu'),
    path('orders/', views.orders, name='orders'),
    path('logout/', views.logout_view, name='logout'),
    path('seleccionar-mesa/', views.seleccionar_mesa, name='seleccionar_mesa'),
    path('nueva-orden/<int:mesa_id>/', views.nueva_orden, name='nueva_orden_mesa'),
    path('nueva-orden/', views.nueva_orden, name='nueva_orden'),  # Ruta para nueva orden sin mesa específica
    path('crear-orden/', views.crear_orden, name='crear_orden'),  # Nueva ruta AJAX para crear órdenes
    path('mesas-modal/', views.seleccionar_mesa_modal, name='seleccionar_mesa_modal'),  # AJAX para modal de mesas
    path('producto-detalle/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),  # AJAX para detalles de producto
    path('orden/<int:orden_id>/actualizar/', views.actualizar_estado_orden, name='actualizar_estado_orden'),  # Actualizar estado
    path('liberar-mesa/<int:orden_id>/', views.liberar_mesa, name='liberar_mesa'),
    path('cancelar-orden/<int:orden_id>/', views.cancelar_orden, name='cancelar_orden'),
    
    # URLs para sistema de cuentas
    path('solicitar-cuenta/<int:orden_id>/', views.solicitar_cuenta, name='solicitar_cuenta'),
    path('estado-cuenta/<int:orden_id>/', views.estado_cuenta, name='estado_cuenta'),
    
    # APIs para sistema de cuentas
    path('api/solicitar-cuenta/', views.api_solicitar_cuenta, name='api_solicitar_cuenta'),
    path('api/estado-cuenta/<int:orden_id>/', views.api_estado_cuenta, name='api_estado_cuenta'),
    
    # Debug endpoints
    path('debug/', debug_views.debug_endpoint, name='debug_endpoint'),
    path('debug-auth/', debug_views.debug_auth_endpoint, name='debug_auth_endpoint'),
    
    path('', views.seleccionar_mesa, name='index'),  # Ahora la ruta raíz va a selección de mesa
]