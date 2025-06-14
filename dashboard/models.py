from django.db import models
from django.utils import timezone
from decimal import Decimal
# Importamos Insumo desde restaurant para tener referencia consistente
from restaurant.models import Insumo as RestaurantInsumo

class Proveedor(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('pendiente', 'Pendiente'),
    ]
    
    CATEGORIA_CHOICES = [
        ('ingredientes', 'Ingredientes'),
        ('bebidas', 'Bebidas'),
        ('utensilios', 'Utensilios'),
        ('empaque', 'Empaque'),
        ('limpieza', 'Limpieza'),
        ('equipos', 'Equipos'),
    ]
    
    FORMA_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('cheque', 'Cheque'),
        ('credito', 'Crédito'),
        ('tarjeta', 'Tarjeta'),    ]
    
    # Campos básicos
    nombre_comercial = models.CharField(max_length=200, verbose_name="Nombre comercial", default="Sin nombre")
    razon_social = models.CharField(max_length=200, blank=True, verbose_name="Razón social")
    rfc = models.CharField(max_length=13, blank=True, verbose_name="RFC")
    
    # Contacto
    persona_contacto = models.CharField(max_length=200, blank=True, verbose_name="Persona de contacto")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Email")
    
    # Términos comerciales
    forma_pago_preferida = models.CharField(
        max_length=20, 
        choices=FORMA_PAGO_CHOICES, 
        default='transferencia',
        verbose_name="Forma de pago preferida"
    )
    dias_credito = models.IntegerField(default=0, verbose_name="Días de crédito")
    
    # Ubicación
    direccion = models.TextField(blank=True, verbose_name="Dirección")
    ciudad_estado = models.CharField(max_length=200, blank=True, verbose_name="Ciudad/Estado")
    
    # Categorización
    categoria_productos = models.CharField(
        max_length=20, 
        choices=CATEGORIA_CHOICES, 
        default='ingredientes',
        verbose_name="Categoría de productos"
    )
    
    # Información adicional
    notas_adicionales = models.TextField(blank=True, verbose_name="Notas adicionales")
    
    # Campos de sistema (mantener compatibilidad)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')
    fecha_registro = models.DateTimeField(default=timezone.now)
    
    # Campos heredados del modelo anterior (para compatibilidad)
    nombre = models.CharField(max_length=200, editable=False)  # Se llenará automáticamente con nombre_comercial
    contacto = models.CharField(max_length=200, blank=True, editable=False)  # Se llenará con persona_contacto
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='ingredientes', editable=False)  # Se llenará con categoria_productos
    notas = models.TextField(blank=True, editable=False)  # Se llenará con notas_adicionales
    
    def save(self, *args, **kwargs):
        # Mantener compatibilidad con campos anteriores
        self.nombre = self.nombre_comercial
        self.contacto = self.persona_contacto
        self.categoria = self.categoria_productos
        self.notas = self.notas_adicionales
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nombre_comercial
    
    class Meta:
        verbose_name_plural = "Proveedores"
        verbose_name = "Proveedor"


# Usamos el modelo Insumo de restaurant.models, así que no necesitamos definirlo aquí
# El alias RestaurantInsumo fue importado al inicio del archivo
Insumo = RestaurantInsumo

# Clase Insumo eliminada - ahora usamos el modelo de restaurant.models


class ProveedorInsumo(models.Model):
    """Relación entre proveedores e insumos con precios específicos"""
    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.CASCADE, 
        related_name='insumos_proveedor'
    )    # Aquí usamos el nombre completo del modelo para evitar ambigüedades
    insumo = models.ForeignKey(
        'restaurant.Insumo', 
        on_delete=models.CASCADE, 
        related_name='proveedores_insumo'
    )
    precio_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Precio por unidad"
    )
    precio_descuento = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True, 
        blank=True,
        verbose_name="Precio con descuento"
    )
    cantidad_minima = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=1,
        verbose_name="Cantidad mínima de compra"
    )
    tiempo_entrega_dias = models.IntegerField(
        default=1,
        verbose_name="Tiempo de entrega (días)"
    )
    activo = models.BooleanField(default=True, verbose_name="Disponible")
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    notas = models.TextField(blank=True, verbose_name="Notas específicas")
    
    def precio_final(self):
        """Retorna el precio final considerando descuentos"""
        if self.precio_descuento and self.precio_descuento > 0:
            return self.precio_descuento
        return self.precio_unitario
    
    def descuento_porcentaje(self):
        """Calcula el porcentaje de descuento"""
        if self.precio_descuento and self.precio_descuento > 0:
            descuento = (self.precio_unitario - self.precio_descuento) / self.precio_unitario * 100
            return round(descuento, 2)
        return 0
    
    def __str__(self):
        return f"{self.proveedor.nombre_comercial} - {self.insumo.nombre} (${self.precio_final()})"
    
    class Meta:
        verbose_name_plural = "Insumos por Proveedor"
        verbose_name = "Insumo por Proveedor"
        unique_together = ('proveedor', 'insumo')
        ordering = ['proveedor', 'insumo__categoria', 'insumo__nombre']
