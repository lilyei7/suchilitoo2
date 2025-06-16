from django.urls import path
from . import views
from .views import categorias_unidades_views

app_name = 'dashboard'

urlpatterns = [
    # Rutas básicas que funcionan
    path('', views.principal_view, name='principal'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Inventario
    path('inventario/', views.inventario_view, name='inventario'),
    path('entradas-salidas/', views.entradas_salidas_view, name='entradas_salidas'),
    
    # Insumos básicos CRUD
    path('insumos/crear/', views.crear_insumo, name='crear_insumo'),
    path('insumos/editar/<int:insumo_id>/', views.editar_insumo, name='editar_insumo'),
    path('insumos/eliminar/<int:insumo_id>/', views.eliminar_insumo, name='eliminar_insumo'),
    path('insumos/detalle/<int:insumo_id>/', views.detalle_insumo, name='detalle_insumo'),
    
    # Insumos Elaborados
    path('insumos-elaborados/', views.insumos_elaborados_view, name='insumos_elaborados'),
    path('insumos-elaborados/crear/', views.crear_insumo_elaborado, name='crear_insumo_elaborado'),
    path('insumos-elaborados/editar/<int:insumo_id>/', views.editar_insumo_elaborado, name='editar_insumo_elaborado'),
    path('insumos-elaborados/eliminar/<int:insumo_id>/', views.eliminar_insumo_elaborado, name='eliminar_insumo_elaborado'),
    path('insumos-elaborados/detalle/<int:insumo_id>/', views.detalle_insumo_elaborado, name='detalle_insumo_elaborado'),
    path('insumos-elaborados/insumos-disponibles/', views.obtener_insumos_para_elaborados, name='obtener_insumos_para_elaborados'),
    
    # APIs para formularios
    path('api/form-data/', views.get_form_data, name='get_form_data'),
    path('api/categorias/', views.obtener_categorias, name='obtener_categorias'),
    path('api/unidades-medida/', views.obtener_unidades_medida, name='obtener_unidades_medida'),
    path('api/insumos-basicos/', views.obtener_insumos_basicos, name='api_obtener_insumos_basicos'),
    
    # Gestión de categorías y unidades
    path('categorias/crear/', categorias_unidades_views.crear_categoria, name='crear_categoria'),
    path('categorias/eliminar/<int:categoria_id>/', views.eliminar_categoria, name='eliminar_categoria'),
    path('categorias/listar/', categorias_unidades_views.listar_categorias, name='listar_categorias'),
    path('unidades/crear/', categorias_unidades_views.crear_unidad, name='crear_unidad_medida'),
    path('unidades/listar/', categorias_unidades_views.listar_unidades, name='listar_unidades'),
    path('unidades/eliminar/<int:unidad_id>/', views.eliminar_unidad, name='eliminar_unidad_medida'),
    
    # Proveedores
    path('proveedores/', views.proveedores_view, name='proveedores'),
    path('proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedor/<int:proveedor_id>/detalle/', views.detalle_proveedor, name='detalle_proveedor'),
    path('proveedor/<int:proveedor_id>/editar/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedor/<int:proveedor_id>/eliminar/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('proveedor/<int:proveedor_id>/asignar-insumo/', views.asignar_insumo_proveedor, name='asignar_insumo_proveedor'),
    path('proveedor-insumo/<int:proveedor_insumo_id>/remover/', views.remover_insumo_proveedor, name='remover_insumo_proveedor'),
    path('api/insumos-disponibles/', views.obtener_insumos_disponibles, name='obtener_insumos_disponibles'),
    
    # Insumos compuestos
    path('insumos-compuestos/', views.insumos_compuestos_view, name='insumos_compuestos'),
    path('insumos-compuestos/crear/', views.crear_insumo_compuesto, name='crear_insumo_compuesto'),
    path('insumos-compuestos/detalle/<int:insumo_id>/', views.detalle_insumo_compuesto, name='detalle_insumo_compuesto'),
    path('insumos-compuestos/editar/<int:insumo_id>/', views.editar_insumo_compuesto, name='editar_insumo_compuesto'),
    path('insumos-compuestos/eliminar/<int:insumo_id>/', views.eliminar_insumo_compuesto, name='eliminar_insumo_compuesto'),
    
    # Recetas
    path('recetas/', views.recetas_view, name='recetas'),
    path('recetas/crear/', views.crear_receta, name='crear_receta'),
    path('recetas/detalle/<int:receta_id>/', views.detalle_receta, name='detalle_receta'),
    path('recetas/editar/<int:receta_id>/', views.editar_receta, name='editar_receta'),
    path('recetas/eliminar/<int:receta_id>/', views.eliminar_receta, name='eliminar_receta'),
    path('recetas/duplicar/<int:receta_id>/', views.duplicar_receta, name='duplicar_receta'),
    path('recetas/insumos/todos/', views.obtener_todos_los_insumos, name='obtener_todos_los_insumos'),
    path('recetas/categorias/', views.obtener_categorias_recetas, name='obtener_categorias_recetas'),
    path('recetas/categorias/crear/', views.crear_categoria_receta, name='crear_categoria_receta'),
    path('recetas/categorias/editar/<int:categoria_id>/', views.editar_categoria_receta, name='editar_categoria_receta'),
    path('recetas/categorias/eliminar/<int:categoria_id>/', views.eliminar_categoria_receta, name='eliminar_categoria_receta'),
    
    # Reportes
    path('reportes/', views.reportes_view, name='reportes'),
    
    # Productos de venta
    path('productos-venta/', views.productos_venta_view, name='productos_venta'),
    
    # Ventas
    path('ventas/', views.ventas_view, name='ventas'),
    
    # Recursos Humanos
    path('recursos-humanos/', views.recursos_humanos_view, name='recursos_humanos'),
    
    # Checklist
    path('checklist/', views.checklist_view, name='checklist'),
    
    # Sucursales
    path('sucursales/', views.sucursales_view, name='sucursales'),
    path('sucursales/crear/', views.crear_sucursal, name='crear_sucursal'),
    path('sucursales/detalle/<int:sucursal_id>/', views.detalle_sucursal, name='detalle_sucursal'),
    path('sucursales/editar/<int:sucursal_id>/', views.editar_sucursal, name='editar_sucursal'),
    path('sucursales/eliminar/<int:sucursal_id>/', views.eliminar_sucursal, name='eliminar_sucursal'),
    path('sucursales/toggle-estado/<int:sucursal_id>/', views.toggle_estado_sucursal, name='toggle_estado_sucursal'),
    
    # Usuarios
    path('usuarios/', views.usuarios_view, name='usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/detalle/<int:usuario_id>/', views.detalle_usuario, name='detalle_usuario'),
    path('usuarios/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/toggle-estado/<int:usuario_id>/', views.toggle_estado_usuario, name='toggle_estado_usuario'),
    path('usuarios/cambiar-contrasena/<int:usuario_id>/', views.cambiar_contrasena_usuario, name='cambiar_contrasena_usuario'),
    path('usuarios/sucursales-roles/', views.obtener_sucursales_roles, name='obtener_sucursales_roles'),
]
