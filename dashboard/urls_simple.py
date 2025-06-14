from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Rutas básicas que funcionan
    path('', views.principal_view, name='principal'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Inventario
    path('inventario/', views.inventario_view, name='inventario'),
    
    # Insumos Elaborados - FUNCIONALIDAD PRINCIPAL
    path('insumos-elaborados/', views.insumos_elaborados_view, name='insumos_elaborados'),
    path('insumos-elaborados/crear/', views.crear_insumo_elaborado, name='crear_insumo_elaborado'),
    path('insumos-elaborados/editar/<int:insumo_id>/', views.editar_insumo_elaborado, name='editar_insumo_elaborado'),
    path('insumos-elaborados/eliminar/<int:insumo_id>/', views.eliminar_insumo_elaborado, name='eliminar_insumo_elaborado'),
    path('insumos-elaborados/detalle/<int:insumo_id>/', views.detalle_insumo_elaborado, name='detalle_insumo_elaborado'),
    path('insumos-elaborados/insumos-compuestos/', views.obtener_insumos_compuestos, name='obtener_insumos_compuestos'),
    
    # URLs adicionales necesarias para el dashboard principal
    path('entradas-salidas/', views.entradas_salidas_view, name='entradas_salidas'),
    path('productos-venta/', views.productos_venta_view, name='productos_venta'),
    path('checklist/', views.checklist_view, name='checklist'),
    path('ventas/', views.ventas_view, name='ventas'),
    path('recursos-humanos/', views.recursos_humanos_view, name='recursos_humanos'),
    path('sucursales/', views.sucursales_view, name='sucursales'),
    path('usuarios/', views.usuarios_view, name='usuarios'),
]
