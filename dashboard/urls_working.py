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
    
    # Categorías y Unidades
    path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('unidades/crear/', views.crear_unidad_medida, name='crear_unidad_medida'),
    path('api/categorias/', views.obtener_categorias, name='obtener_categorias'),
    path('api/unidades-medida/', views.obtener_unidades_medida, name='obtener_unidades_medida'),
    
    # Insumos Compuestos - FUNCIONALIDAD PRINCIPAL
    path('insumos-compuestos/', views.insumos_compuestos_view, name='insumos_compuestos'),
    path('insumos-compuestos/crear/', views.crear_insumo_compuesto, name='crear_insumo_compuesto'),
    path('insumos-compuestos/editar/<int:insumo_id>/', views.editar_insumo_compuesto, name='editar_insumo_compuesto'),
    path('insumos-compuestos/eliminar/<int:insumo_id>/', views.eliminar_insumo_compuesto, name='eliminar_insumo_compuesto'),
    path('insumos-compuestos/detalle/<int:insumo_id>/', views.detalle_insumo_compuesto, name='detalle_insumo_compuesto'),
    path('insumos-compuestos/insumos-basicos/', views.obtener_insumos_basicos, name='obtener_insumos_basicos'),
    
    # Insumos Elaborados
    path('insumos-elaborados/', views.insumos_elaborados_view, name='insumos_elaborados'),
    path('insumos-elaborados/crear/', views.crear_insumo_elaborado, name='crear_insumo_elaborado'),
]
