from django.urls import path
from . import views

app_name = 'cajero'

urlpatterns = [
    # Login y logout
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard principal
    path('', views.dashboard, name='dashboard'),
    
    # Punto de venta
    path('pos/', views.punto_venta, name='pos'),
    
    # Crear pedidos (nueva funcionalidad)
    path('crear-pedido/', views.crear_pedido, name='crear_pedido'),
    
    # Notificaciones y procesamiento de cuentas
    path('notificaciones/', views.notificaciones_cuenta, name='notificaciones_cuenta'),
    path('procesar-cuenta/<int:notificacion_id>/', views.procesar_cuenta, name='procesar_cuenta'),
    
    # Historial de ventas
    path('ventas/', views.historial_ventas, name='ventas'),
    
    # APIs para el POS
    path('api/productos/', views.api_productos, name='api_productos'),
    path('api/procesar-pago/', views.api_procesar_pago, name='api_procesar_pago'),
    path('api/guardar-orden/', views.api_guardar_orden, name='api_guardar_orden'),
    path('api/cancelar-venta/<int:venta_id>/', views.api_cancelar_venta, name='api_cancelar_venta'),
    
    # APIs para crear pedidos y procesar cuentas
    path('api/crear-pedido/', views.api_crear_pedido, name='api_crear_pedido'),
    path('api/procesar-cuenta/<int:notificacion_id>/', views.api_procesar_cuenta, name='api_procesar_cuenta'),
]
