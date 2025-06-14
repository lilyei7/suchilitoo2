from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Sucursal, Rol

@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'direccion', 'telefono', 'activa', 'fecha_apertura']
    list_filter = ['activa', 'fecha_apertura']
    search_fields = ['nombre', 'direccion']
    date_hierarchy = 'fecha_apertura'

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['get_nombre_display', 'descripcion', 'activo', 'created_at']
    list_filter = ['nombre', 'activo']
    search_fields = ['nombre', 'descripcion']

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'sucursal', 'rol', 'activo', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'activo', 'sucursal', 'rol', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'cedula']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('sucursal', 'rol', 'telefono', 'cedula', 'fecha_ingreso', 'salario', 'activo', 'foto')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('sucursal', 'rol', 'telefono', 'cedula', 'fecha_ingreso', 'salario', 'activo')
        }),
    )
