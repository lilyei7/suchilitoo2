from django.contrib import admin
from .models import (
    Proveedor, CategoriaInsumo, UnidadMedida, Insumo, Receta, RecetaInsumo,
    Inventario, MovimientoInventario, CategoriaProducto, ProductoVenta,
    CheckListItem, CheckListEjecucion
)

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'contacto', 'telefono', 'email', 'activo']
    list_filter = ['activo', 'created_at']
    search_fields = ['nombre', 'contacto', 'email']

@admin.register(CategoriaInsumo)
class CategoriaInsumoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']

@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'abreviacion']
    search_fields = ['nombre', 'abreviacion']

@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'categoria', 'tipo', 'precio_unitario', 'stock_minimo', 'activo']
    list_filter = ['tipo', 'categoria', 'activo', 'perecedero', 'proveedor_principal']
    search_fields = ['codigo', 'nombre']
    list_editable = ['precio_unitario', 'stock_minimo', 'activo']


class RecetaInsumoInline(admin.TabularInline):
    model = RecetaInsumo
    extra = 1

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'tiempo_preparacion', 'porciones', 'activo']
    list_filter = ['activo', 'tiempo_preparacion']
    search_fields = ['producto__nombre', 'instrucciones']
    inlines = [RecetaInsumoInline]

@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ['sucursal', 'insumo', 'cantidad_actual', 'cantidad_reservada', 'cantidad_disponible', 'fecha_vencimiento']
    list_filter = ['sucursal', 'insumo__categoria', 'fecha_vencimiento']
    search_fields = ['insumo__nombre', 'insumo__codigo', 'lote']
    readonly_fields = ['cantidad_disponible']

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'sucursal', 'insumo', 'tipo_movimiento', 'cantidad', 'usuario']
    list_filter = ['tipo_movimiento', 'sucursal', 'created_at', 'insumo__categoria']
    search_fields = ['insumo__nombre', 'motivo', 'documento_referencia']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']

@admin.register(ProductoVenta)
class ProductoVentaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'categoria', 'precio', 'disponible', 'es_promocion']
    list_filter = ['categoria', 'disponible', 'es_promocion', 'fecha_creacion']
    search_fields = ['codigo', 'nombre', 'descripcion']
    list_editable = ['precio', 'disponible']

@admin.register(CheckListItem)
class CheckListItemAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'obligatorio', 'orden', 'activo']
    list_filter = ['tipo', 'obligatorio', 'activo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['orden', 'activo']

@admin.register(CheckListEjecucion)
class CheckListEjecucionAdmin(admin.ModelAdmin):
    list_display = ['item', 'sucursal', 'usuario', 'completado', 'fecha', 'fecha_ejecucion']
    list_filter = ['completado', 'item__tipo', 'sucursal', 'fecha']
    search_fields = ['item__nombre', 'observaciones']
    date_hierarchy = 'fecha'
