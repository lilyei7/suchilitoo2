from django.contrib import admin
from .models import EstadoCocina, TiempoPreparacion, OrdenCocina, ItemCocina, LogCocina

@admin.register(EstadoCocina)
class EstadoCocinaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'color', 'orden', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')
    ordering = ('orden', 'nombre')

@admin.register(TiempoPreparacion)
class TiempoPreparacionAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tiempo_estimado', 'tiempo_promedio', 'cantidad_preparaciones')
    list_filter = ('producto__categoria',)
    search_fields = ('producto__nombre',)
    readonly_fields = ('tiempo_promedio', 'cantidad_preparaciones')

@admin.register(OrdenCocina)
class OrdenCocinaAdmin(admin.ModelAdmin):
    list_display = ('orden', 'cocinero_asignado', 'prioridad', 'tiempo_estimado_total', 'fecha_creacion')
    list_filter = ('prioridad', 'cocinero_asignado', 'fecha_creacion')
    search_fields = ('orden__numero_orden', 'cocinero_asignado__username')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    raw_id_fields = ('orden', 'cocinero_asignado')

@admin.register(ItemCocina)
class ItemCocinaAdmin(admin.ModelAdmin):
    list_display = ('orden_item', 'estado_cocina', 'cocinero_responsable', 'tiempo_inicio', 'tiempo_finalizacion')
    list_filter = ('estado_cocina', 'cocinero_responsable')
    search_fields = ('orden_item__producto__nombre', 'cocinero_responsable__username')
    raw_id_fields = ('orden_item', 'cocinero_responsable')

@admin.register(LogCocina)
class LogCocinaAdmin(admin.ModelAdmin):
    list_display = ('orden', 'accion', 'usuario', 'timestamp')
    list_filter = ('accion', 'timestamp')
    search_fields = ('orden__numero_orden', 'usuario__username', 'descripcion')
    readonly_fields = ('timestamp',)
    raw_id_fields = ('orden', 'item', 'usuario')
