# Este archivo es necesario para que Python reconozca el directorio 'views' como un paquete
# Importamos todas las vistas para que estén disponibles cuando se importe dashboard.views

# Auth views
from .auth_views import login_view, logout_view

# Base views
from .base_views import principal_view, get_sidebar_context, is_admin_or_manager, is_admin

# Inventario views
from .inventario_views import inventario_view, entradas_salidas_view

# Insumos básicos views
from .insumos_views import (
    crear_insumo, detalle_insumo, editar_insumo, eliminar_insumo
)

# Insumos elaborados views
from .insumos_elaborados_views import (
    insumos_elaborados_view, crear_insumo_elaborado, obtener_insumos_para_elaborados,
    detalle_insumo_elaborado, editar_insumo_elaborado, eliminar_insumo_elaborado
)

# Insumos compuestos views
from .insumos_compuestos_views import (
    insumos_compuestos_view, crear_insumo_compuesto, detalle_insumo_compuesto,
    editar_insumo_compuesto, eliminar_insumo_compuesto
)

# Recetas views
from .recetas_views import (
    recetas_view, crear_receta, detalle_receta, eliminar_receta, editar_receta, duplicar_receta,
    obtener_insumos_basicos, obtener_insumos_compuestos, obtener_insumos_elaborados,
    obtener_todos_los_insumos, obtener_categorias_productos, crear_categoria_producto,
    eliminar_categoria_producto, obtener_categorias_recetas, crear_categoria_receta,
    editar_categoria_receta, eliminar_categoria_receta
)

# Categorias views
from .categorias_views import (
    obtener_categorias, crear_categoria, eliminar_categoria, get_form_data, 
    obtener_unidades_medida, crear_unidad, eliminar_unidad
)

# Proveedores views
from .proveedores_views import (
    proveedores_view, crear_proveedor, detalle_proveedor, editar_proveedor, 
    eliminar_proveedor, asignar_insumo_proveedor, remover_insumo_proveedor, 
    obtener_insumos_disponibles
)

# Sucursales views
from .sucursales_views import (
    sucursales_view, crear_sucursal, detalle_sucursal, editar_sucursal,
    eliminar_sucursal, toggle_estado_sucursal
)

# Usuarios views
from .usuarios_views import (
    usuarios_view, crear_usuario, detalle_usuario, editar_usuario,
    eliminar_usuario, toggle_estado_usuario, obtener_sucursales_roles,
    cambiar_contrasena_usuario
)

# Otros views
from .otros_views import (
    productos_venta_view, reportes_view, 
    checklist_view, ventas_view, recursos_humanos_view
)
