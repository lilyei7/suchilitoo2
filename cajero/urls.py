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
    
    # Historial de ventas
    path('ventas/', views.historial_ventas, name='ventas'),
    
    # APIs para el POS
    path('api/productos/', views.api_productos, name='api_productos'),
    path('api/procesar-pago/', views.api_procesar_pago, name='api_procesar_pago'),
    path('api/guardar-orden/', views.api_guardar_orden, name='api_guardar_orden'),
    path('api/cancelar-venta/<int:venta_id>/', views.api_cancelar_venta, name='api_cancelar_venta'),
]
