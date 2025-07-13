from django.urls import path
from . import views
from .views import categorias_unidades_views
from .views import entradas_salidas_views
from .views import historial_precios_views
from .views import ventas_views
from .views import cajero_views
from .views import productos_venta_views
from .views import sucursales_views
from .views import croquis_views
from .views import productos_venta_moderna_views
from .views import api_views
from .views import usuarios_views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'dashboard'

urlpatterns = [
    # Rutas básicas que funcionan
    path('', views.principal_view, name='principal'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Inventario
    path('inventario/', views.inventario_view, name='inventario'),
    
    # Entradas y Salidas (Movimientos de inventario)
    path('entradas-salidas/', entradas_salidas_views.entradas_salidas_view, name='entradas_salidas'),
    path('entradas-salidas/crear-movimiento', entradas_salidas_views.crear_movimiento, name='crear_movimiento'),
    path('entradas-salidas/obtener-insumos', entradas_salidas_views.obtener_insumos, name='obtener_insumos'),
    path('entradas-salidas/detalle/<int:movimiento_id>/', entradas_salidas_views.obtener_detalle_movimiento, name='obtener_detalle_movimiento'),
    path('entradas-salidas/filtrar', entradas_salidas_views.filtrar_movimientos, name='filtrar_movimientos'),
      # Insumos básicos CRUD
    path('insumos/crear/', views.crear_insumo, name='crear_insumo'),
    path('insumos/editar/<int:insumo_id>/', views.editar_insumo, name='editar_insumo'),
    path('insumos/eliminar/<int:insumo_id>/', views.eliminar_insumo, name='eliminar_insumo'),
    path('insumos/detalle/<int:insumo_id>/', views.detalle_insumo, name='detalle_insumo'),
    path('insumos/<int:insumo_id>/detalle/', views.insumo_detalle_api, name='insumo_detalle_api'),
    
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
      # Productos de venta - COMENTADO: usar la vista de productos_venta_views.lista_productos_venta
    # path('productos-venta/', views.productos_venta_view, name='productos_venta'),
    
    # Ventas
    path('ventas/', ventas_views.ventas_view, name='ventas'),
    path('api/venta-producto/', ventas_views.venta_producto_api, name='venta_producto_api'),
    
    # Recursos Humanos
    path('recursos-humanos/', views.recursos_humanos_view, name='recursos_humanos'),
    
    # Checklist
    path('checklist/', views.checklist_view, name='checklist'),
    
    # Sucursales
    path('sucursales/', sucursales_views.sucursales_view, name='sucursales'),
    path('sucursales/crear/', sucursales_views.crear_sucursal, name='crear_sucursal'),
    path('sucursales/detalle/<int:sucursal_id>/', sucursales_views.detalle_sucursal, name='detalle_sucursal'),
    path('sucursales/<int:sucursal_id>/editar/', sucursales_views.editar_sucursal, name='editar_sucursal'),
    path('sucursales/<int:sucursal_id>/eliminar/', sucursales_views.eliminar_sucursal, name='eliminar_sucursal'),
    path('sucursales/<int:sucursal_id>/toggle-estado/', sucursales_views.toggle_estado_sucursal, name='toggle_estado_sucursal'),
    
    # APIs para gestión de mesas
    path('api/sucursales/<int:sucursal_id>/mesas/', sucursales_views.listar_mesas_sucursal, name='listar_mesas_sucursal'),
    path('api/mesas/crear/', sucursales_views.crear_mesa, name='crear_mesa'),
    path('api/mesas/<int:mesa_id>/', sucursales_views.obtener_mesa, name='obtener_mesa'),
    path('api/mesas/<int:mesa_id>/editar/', sucursales_views.editar_mesa, name='editar_mesa'),
    path('api/mesas/<int:mesa_id>/estado/', sucursales_views.cambiar_estado_mesa, name='cambiar_estado_mesa'),
    path('api/mesas/<int:mesa_id>/eliminar/', sucursales_views.eliminar_mesa, name='eliminar_mesa'),
    path('api/mesas/<int:mesa_id>/toggle-activa/', sucursales_views.toggle_activa_mesa, name='toggle_activa_mesa'),

    # Croquis Editor
    path('sucursales/<int:sucursal_id>/croquis/', croquis_views.croquis_editor_view, name='croquis_editor'),
    path('sucursales/<int:sucursal_id>/croquis/preview/', croquis_views.preview_croquis, name='preview_croquis'),
    path('api/croquis/guardar/', croquis_views.guardar_layout_croquis, name='guardar_layout_croquis'),
    path('api/croquis/cargar/<int:sucursal_id>/', croquis_views.cargar_layout_croquis, name='cargar_layout_croquis'),
    path('api/croquis/eliminar/<int:sucursal_id>/', croquis_views.eliminar_layout_croquis, name='eliminar_layout_croquis'),
    path('api/croquis/estadisticas/<int:sucursal_id>/', croquis_views.estadisticas_croquis, name='estadisticas_croquis'),
    path('api/croquis/mesas/<int:sucursal_id>/', croquis_views.obtener_mesas_croquis, name='obtener_mesas_croquis'),

    # Usuarios
    path('usuarios/', views.usuarios_view, name='usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/detalle/<int:usuario_id>/', views.detalle_usuario, name='detalle_usuario'),
    path('usuarios/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/toggle-estado/<int:usuario_id>/', views.toggle_estado_usuario, name='toggle_estado_usuario'),
    path('usuarios/cambiar-contrasena/<int:usuario_id>/', views.cambiar_contrasena_usuario, name='cambiar_contrasena_usuario'),
    path('usuarios/sucursales-roles/', views.obtener_sucursales_roles, name='obtener_sucursales_roles'),
    
    # Historial de precios y costos
    path('historial-precios/', historial_precios_views.historial_precios_view, name='historial_precios'),
    path('historial-precios/api/<int:insumo_id>/', historial_precios_views.historial_precios_api, name='historial_precios_api'),
    path('simulacion-costos/', historial_precios_views.simulacion_costos_view, name='simulacion_costos'),
    path('api/calcular-costo/', historial_precios_views.calcular_costo_api, name='calcular_costo_api'),
    path('api/descontar-stock-peps/', historial_precios_views.descontar_stock_peps_api, name='descontar_stock_peps'),
    
    # Módulo de Cajero
    path('cajero/', cajero_views.cajero_dashboard, name='cajero_dashboard'),
    path('cajero/pos/', cajero_views.punto_venta, name='punto_venta'),
    path('cajero/ordenes/', cajero_views.ordenes_activas, name='ordenes_activas'),
    path('cajero/historial/', cajero_views.historial_ventas, name='historial_ventas'),
    path('cajero/apertura-caja/', cajero_views.apertura_caja, name='apertura_caja'),
    path('cajero/cierre-caja/', cajero_views.cierre_caja, name='cierre_caja'),
    path('cajero/mesas/', cajero_views.admin_mesas, name='admin_mesas'),
    
    # APIs de Cajero
    path('api/cajero/agregar-producto/', cajero_views.api_agregar_producto, name='api_agregar_producto'),
    path('api/cajero/finalizar-venta/', cajero_views.api_finalizar_venta, name='api_finalizar_venta'),
    path('api/cajero/guardar-orden/', cajero_views.api_guardar_orden, name='api_guardar_orden'),
    path('api/cajero/orden/<int:orden_id>/', cajero_views.api_get_orden, name='api_get_orden'),
    path('api/cajero/orden/<int:orden_id>/estado/', cajero_views.api_cambiar_estado_orden, name='api_cambiar_estado_orden'),
    path('api/cajero/orden/<int:orden_id>/cancelar/', cajero_views.api_cancelar_orden, name='api_cancelar_orden'),
    path('api/cajero/procesar-pago/', cajero_views.api_procesar_pago, name='api_procesar_pago'),
    path('api/cajero/clientes/', cajero_views.api_buscar_clientes, name='api_buscar_clientes'),
    path('api/cajero/guardar-cliente/', cajero_views.api_guardar_cliente, name='api_guardar_cliente'),
    path('api/cajero/mesas/', cajero_views.api_get_mesas, name='api_get_mesas'),
    path('api/cajero/venta/<int:venta_id>/anular/', cajero_views.api_anular_venta, name='api_anular_venta'),
    path('api/cajero/venta/<int:venta_id>/ticket/', cajero_views.api_reimprimir_ticket, name='api_reimprimir_ticket'),

    # APIs para verificación y eliminación forzada de productos
    path('api/verificar-producto/<int:producto_id>/', api_views.verificar_producto_api, name='verificar_producto_api'),
    path('api/eliminar-forzado/<int:producto_id>/', api_views.eliminar_forzado_api, name='eliminar_forzado_api'),

    # Debug view for AJAX
    path('ajax-debug/', views.ajax_debug_view, name='ajax_debug'),
    
    # Productos de Venta
    path('productos-venta/', productos_venta_views.lista_productos_venta, name='lista_productos_venta'),
    path('productos-venta/crear/', productos_venta_views.crear_producto_venta, name='crear_producto_venta'),
    path('productos-venta/<int:producto_id>/editar/', productos_venta_views.editar_producto_venta, name='editar_producto_venta'),
    path('productos-venta/<int:producto_id>/eliminar/', productos_venta_views.eliminar_producto_venta, name='eliminar_producto_venta'),
    path('productos-venta/<int:producto_id>/eliminar-forzado/', lambda request, producto_id: productos_venta_views.eliminar_producto_venta(request, producto_id, force=True), name='eliminar_producto_venta_forzado'),
    path('productos-venta/<int:producto_id>/desactivar/', productos_venta_views.desactivar_producto_venta, name='desactivar_producto_venta'),
    path('productos-venta/<int:producto_id>/detalle/', productos_venta_views.ver_detalle_producto, name='ver_detalle_producto'),
    path('productos-venta/<int:producto_id>/cambiar-estado/', productos_venta_views.cambiar_estado_producto, name='cambiar_estado_producto'),
    path('productos-venta/diagnostico/', productos_venta_views.diagnostico_view, name='diagnostico_view'),
    path('api/productos-venta/recetas/', productos_venta_views.obtener_recetas, name='api_obtener_recetas'),

    # Vista moderna de productos de venta
    path('productos/', productos_venta_moderna_views.lista_productos_venta_moderna, name='productos_venta_moderna'),
    
    # Croquis - Editor de layout visual
    path('croquis/<int:sucursal_id>/', croquis_views.croquis_editor_view, name='croquis_editor'),
    path('croquis/<int:sucursal_id>/preview/', croquis_views.preview_croquis, name='croquis_preview'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
