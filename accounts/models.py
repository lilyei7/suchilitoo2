from django.db import models
from django.contrib.auth.models import AbstractUser

class Sucursal(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    activa = models.BooleanField(default=True)
    fecha_apertura = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'

    def __str__(self):
        return self.nombre

class Rol(models.Model):
    TIPOS_ROL = [
        ('admin', 'Administrador'),
        ('gerente', 'Gerente'),
        ('supervisor', 'Supervisor'),
        ('cajero', 'Cajero'),
        ('cocinero', 'Cocinero'),
        ('mesero', 'Mesero'),
        ('inventario', 'Encargado de Inventario'),
        ('rrhh', 'Recursos Humanos'),
    ]
    
    nombre = models.CharField(max_length=50, choices=TIPOS_ROL, unique=True)
    descripcion = models.TextField(blank=True)
    permisos = models.JSONField(default=dict, help_text="Permisos específicos del rol")
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.get_nombre_display()

class Usuario(AbstractUser):
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, null=True, blank=True)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)
    telefono = models.CharField(max_length=20, blank=True)
    cedula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    salario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    activo = models.BooleanField(default=True)
    foto = models.ImageField(upload_to='usuarios/', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.username}"
    
    def has_feature(self, feature_name):
        """
        Verifica si el usuario tiene acceso a una característica específica
        
        Args:
            feature_name (str): Nombre de la característica a verificar
            
        Returns:
            bool: True si el usuario tiene la característica
        """
        from dashboard.utils.permissions import has_feature
        return has_feature(self, feature_name)
