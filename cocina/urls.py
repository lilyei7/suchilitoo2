from django.urls import path
from . import views

app_name = 'cocina'

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard principal de cocina
    path('', views.dashboard, name='dashboard'),
    
    # Gestión de órdenes
    path('ordenes/', views.ordenes_pendientes, name='ordenes_pendientes'),
    path('ordenes/ajax/', views.ordenes_ajax, name='ordenes_ajax'),
    path('orden/<int:orden_id>/', views.detalle_orden, name='detalle_orden'),
    path('orden/<int:orden_id>/item/<int:item_id>/cambiar-estado/', views.cambiar_estado_item, name='cambiar_estado_item'),
    path('orden/<int:orden_id>/cambiar-estado/', views.cambiar_estado_orden, name='cambiar_estado_orden'),
    path('orden/<int:orden_id>/detalles/', views.orden_detalles_ajax, name='orden_detalles_ajax'),
    path('orden/<int:orden_id>/cambiar-estado-ajax/', views.cambiar_estado_orden_ajax, name='cambiar_estado_orden_ajax'),
    path('finalizar-orden/<int:orden_id>/', views.finalizar_orden, name='finalizar_orden'),
    path('finalizar-servicio/<int:orden_id>/', views.finalizar_servicio, name='finalizar_servicio'),
    
    # Reportes y estadísticas
    path('reportes/', views.reportes, name='reportes'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
    
    # API endpoints
    path('api/ordenes/', views.api_ordenes, name='api_ordenes'),
    path('api/tiempos/', views.api_tiempos_preparacion, name='api_tiempos'),
]
