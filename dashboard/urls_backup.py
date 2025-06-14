from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.principal_view, name='principal'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),      # Inventario
    path('inventario/', views.inventario_view, name='inventario'),
    path('entradas-salidas/', views.entradas_salidas_view, name='entradas_salidas'),
    
    # Proveedores
    path('proveedores/', views.proveedores_view, name='proveedores'),
    path('crear-proveedor/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedor/<int:proveedor_id>/detalle/', views.detalle_proveedor, name='detalle_proveedor'),
    path('proveedor/<int:proveedor_id>/editar/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedor/<int:proveedor_id>/eliminar/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('proveedor/<int:proveedor_id>/asignar-insumo/', views.asignar_insumo_proveedor, name='asignar_insumo_proveedor'),
    path('proveedor-insumo/<int:proveedor_insumo_id>/remover/', views.remover_insumo_proveedor, name='remover_insumo_proveedor'),
    path('proveedores/insumos-disponibles/', views.obtener_insumos_disponibles, name='obtener_insumos_disponibles'),
      # Insumos Básicos (comentadas temporalmente - no implementadas)
    # path('insumos/crear/', views.crear_insumo, name='crear_insumo'),
    # path('insumos/editar/<int:insumo_id>/', views.editar_insumo, name='editar_insumo'),
    # path('insumos/eliminar/<int:insumo_id>/', views.eliminar_insumo, name='eliminar_insumo'),
    # path('insumos/form-data/', views.get_form_data, name='get_form_data'),
    
    # Categorías y Unidades
    path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('unidades/crear/', views.crear_unidad_medida, name='crear_unidad_medida'),      # Insumos Compuestos
    path('insumos-compuestos/', views.insumos_compuestos_view, name='insumos_compuestos'),
    path('insumos-compuestos/crear/', views.crear_insumo_compuesto, name='crear_insumo_compuesto'),
    path('insumos-compuestos/editar/<int:insumo_id>/', views.editar_insumo_compuesto, name='editar_insumo_compuesto'),
    path('insumos-compuestos/eliminar/<int:insumo_id>/', views.eliminar_insumo_compuesto, name='eliminar_insumo_compuesto'),
    path('insumos-compuestos/detalle/<int:insumo_id>/', views.detalle_insumo_compuesto, name='detalle_insumo_compuesto'),
    path('insumos-compuestos/insumos-basicos/', views.obtener_insumos_basicos, name='obtener_insumos_basicos'),
    path('api/categorias/', views.obtener_categorias, name='obtener_categorias'),
    path('api/unidades-medida/', views.obtener_unidades_medida, name='obtener_unidades_medida'),
    
    # Insumos Elaborados
    path('insumos-elaborados/', views.insumos_elaborados_view, name='insumos_elaborados'),
    path('insumos-elaborados/crear/', views.crear_insumo_elaborado, name='crear_insumo_elaborado'),
    path('insumos-elaborados/editar/<int:insumo_id>/', views.editar_insumo_elaborado, name='editar_insumo_elaborado'),
    path('insumos-elaborados/eliminar/<int:insumo_id>/', views.eliminar_insumo_elaborado, name='eliminar_insumo_elaborado'),
    
    # Productos de Venta
    path('productos-venta/', views.productos_venta_view, name='productos_venta'),
    path('productos-venta/crear/', views.crear_producto_venta, name='crear_producto_venta'),
    
    # Usuarios
    path('usuarios/', views.usuarios_view, name='usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    
    # Otros módulos
    path('sucursales/', views.sucursales_view, name='sucursales'),
    path('ventas/', views.ventas_view, name='ventas'),
    path('checklist/', views.checklist_view, name='checklist'),
    path('recursos-humanos/', views.recursos_humanos_view, name='recursos_humanos'),
]
