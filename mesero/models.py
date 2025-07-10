from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class Mesa(models.Model):
    """Modelo para las mesas del restaurante"""
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('reservada', 'Reservada'),
        ('limpieza', 'En Limpieza'),
        ('mantenimiento', 'Mantenimiento'),
    ]
    
    numero = models.CharField(max_length=10)
    capacidad = models.IntegerField(default=4)
    sucursal = models.ForeignKey('accounts.Sucursal', on_delete=models.CASCADE, related_name='mesas_mesero')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    ubicacion = models.CharField(max_length=100, blank=True, null=True, help_text="Ej: Terraza, Salón principal, VIP")
    activa = models.BooleanField(default=True)
    notas = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['numero', 'sucursal']]
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'
    
    def __str__(self):
        return f"Mesa {self.numero} - {self.sucursal.nombre}"
    
    def cambiar_estado(self, nuevo_estado, usuario=None, motivo=None):
        """Cambia el estado de la mesa y registra el historial"""
        estado_anterior = self.estado
        self.estado = nuevo_estado
        self.save()
        
        # Registrar en historial
        HistorialMesa.objects.create(
            mesa=self,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            usuario=usuario,
            motivo=motivo
        )
    
    def obtener_orden_activa(self):
        """Obtiene la orden activa de esta mesa"""
        return self.ordenes_mesero.filter(estado__in=['pendiente', 'en_preparacion', 'lista']).first()
    
    def esta_disponible(self):
        """Verifica si la mesa está disponible"""
        return self.estado == 'disponible' and self.activa
    
    class Meta:
        verbose_name = "Mesa"
        verbose_name_plural = "Mesas"
        ordering = ['numero']


class HistorialMesa(models.Model):
    """Historial de cambios de estado de mesas"""
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=20)
    estado_nuevo = models.CharField(max_length=20)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    motivo = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Mesa {self.mesa.numero}: {self.estado_anterior} → {self.estado_nuevo}"
    
    class Meta:
        verbose_name = "Historial de mesa"
        verbose_name_plural = "Historiales de mesas"
        ordering = ['-fecha']


class Orden(models.Model):
    """Modelo para las órdenes de los clientes"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('en_preparacion', 'En Preparación'),
        ('lista', 'Lista'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
        ('cerrada', 'Cerrada'),
    ]
    
    TIPO_SERVICIO_CHOICES = [
        ('mesa', 'En Mesa'),
        ('llevar', 'Para Llevar'),
        ('delivery', 'Delivery'),
    ]
    
    numero_orden = models.CharField(max_length=20, unique=True)
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordenes_mesero')
    mesero = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ordenes_mesero_atendidas')
    cliente_nombre = models.CharField(max_length=200, blank=True, null=True)
    cliente_telefono = models.CharField(max_length=20, blank=True, null=True)
    tipo_servicio = models.CharField(max_length=20, choices=TIPO_SERVICIO_CHOICES, default='mesa')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    # Totales
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Observaciones y notas
    observaciones = models.TextField(blank=True, null=True)
    notas_cocina = models.TextField(blank=True, null=True)
    
    # Fechas importantes
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    fecha_preparacion = models.DateTimeField(null=True, blank=True)
    fecha_lista = models.DateTimeField(null=True, blank=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    
    # Campos para sistema de cuentas
    cuenta_solicitada = models.BooleanField(default=False)
    fecha_solicitud_cuenta = models.DateTimeField(null=True, blank=True)
    usuario_solicita_cuenta = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cuentas_solicitadas')
    cuenta_procesada = models.BooleanField(default=False)
    fecha_procesamiento_cuenta = models.DateTimeField(null=True, blank=True)
    cajero_procesa_cuenta = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cuentas_procesadas')
    metodo_pago_cuenta = models.CharField(max_length=20, choices=[('efectivo', 'Efectivo'), ('tarjeta', 'Tarjeta'), ('transferencia', 'Transferencia')], null=True, blank=True)
    monto_recibido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cambio_dado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    referencia_pago = models.CharField(max_length=100, null=True, blank=True)
    ticket_generado = models.BooleanField(default=False)
    
    def __str__(self):
        mesa_info = f"Mesa {self.mesa.numero}" if self.mesa else "Sin mesa"
        return f"Orden {self.numero_orden} - {mesa_info}"
    
    def save(self, *args, **kwargs):
        # Generar número de orden si no existe
        if not self.numero_orden:
            from django.utils import timezone
            fecha = timezone.now()
            ultimo_numero = Orden.objects.filter(
                fecha_creacion__date=fecha.date()
            ).count() + 1
            self.numero_orden = f"ORD-{fecha.strftime('%Y%m%d')}-{ultimo_numero:04d}"
        
        super().save(*args, **kwargs)
        
        # Actualizar estado de mesa si es necesario
        if self.mesa:
            if self.estado in ['pendiente', 'confirmada', 'en_preparacion', 'lista']:
                if self.mesa.estado == 'disponible':
                    self.mesa.cambiar_estado('ocupada', self.mesero, f"Orden {self.numero_orden} creada")
            elif self.estado in ['entregada', 'cancelada', 'cerrada']:
                # Verificar si hay otras órdenes activas en la mesa
                ordenes_activas = self.mesa.ordenes_mesero.filter(
                    estado__in=['pendiente', 'confirmada', 'en_preparacion', 'lista']
                ).exclude(id=self.id)
                
                if not ordenes_activas.exists():
                    self.mesa.cambiar_estado('disponible', self.mesero, f"Orden {self.numero_orden} finalizada - Mesa liberada")
                    print(f"✅ Mesa {self.mesa.numero} liberada automáticamente - Orden {self.numero_orden} finalizada")
    
    def calcular_totales(self):
        """Calcula los totales de la orden"""
        self.subtotal = sum(item.calcular_subtotal() for item in self.items.all())
        # Calcular impuesto (ejemplo: 12%)
        self.impuesto = self.subtotal * Decimal('0.12')
        self.total = self.subtotal + self.impuesto - self.descuento
        self.save()
    
    def cambiar_estado(self, nuevo_estado, usuario=None, observaciones=None):
        """Cambia el estado de la orden y registra el cambio"""
        estado_anterior = self.estado
        self.estado = nuevo_estado
        
        # Actualizar fechas según el estado
        now = timezone.now()
        if nuevo_estado == 'confirmada':
            self.fecha_confirmacion = now
        elif nuevo_estado == 'en_preparacion':
            self.fecha_preparacion = now
        elif nuevo_estado == 'lista':
            self.fecha_lista = now
        elif nuevo_estado == 'entregada':
            self.fecha_entrega = now
        elif nuevo_estado == 'cerrada':
            self.fecha_cierre = now
        
        self.save()
        
        # Registrar en historial
        HistorialOrden.objects.create(
            orden=self,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            usuario=usuario,
            observaciones=observaciones
        )
    
    def tiempo_transcurrido(self):
        """Calcula el tiempo transcurrido desde la creación"""
        if self.fecha_cierre:
            return self.fecha_cierre - self.fecha_creacion
        return timezone.now() - self.fecha_creacion
    
    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
        ordering = ['-fecha_creacion']


class OrdenItem(models.Model):
    """Items de una orden"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_preparacion', 'En Preparación'),
        ('listo', 'Listo'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey('restaurant.ProductoVenta', on_delete=models.PROTECT)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento_item = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    observaciones = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} - Orden {self.orden.numero_orden}"
    
    def calcular_subtotal(self):
        """Calcula el subtotal del item"""
        return (self.precio_unitario * self.cantidad) - self.descuento_item
    
    def save(self, *args, **kwargs):
        # Si no se ha establecido el precio, usar el del producto
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio
        
        # Calcular y guardar el subtotal
        self.subtotal = self.calcular_subtotal()
        
        super().save(*args, **kwargs)
        
        # Recalcular totales de la orden
        self.orden.calcular_totales()
    
    class Meta:
        verbose_name = "Item de orden"
        verbose_name_plural = "Items de órdenes"


class HistorialOrden(models.Model):
    """Historial de cambios de estado de órdenes"""
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=20)
    estado_nuevo = models.CharField(max_length=20)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Orden {self.orden.numero_orden}: {self.estado_anterior} → {self.estado_nuevo}"
    
    class Meta:
        verbose_name = "Historial de orden"
        verbose_name_plural = "Historiales de órdenes"
        ordering = ['-fecha']

class OpcionPersonalizacion(models.Model):
    """Modelo para opciones de personalización de productos"""
    TIPO_CHOICES = [
        ('quitar', 'Quitar ingrediente'),
        ('agregar', 'Agregar extra'),
        ('cambiar', 'Cambiar ingrediente'),
        ('nota', 'Nota especial'),
    ]
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='quitar')
    precio_extra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    activa = models.BooleanField(default=True)
    categoria = models.ForeignKey('restaurant.CategoriaProducto', on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"
    
    class Meta:
        verbose_name = "Opción de personalización"
        verbose_name_plural = "Opciones de personalización"
        ordering = ['tipo', 'nombre']

class ProductoPersonalizacion(models.Model):
    """Relación entre productos y opciones de personalización disponibles"""
    producto = models.ForeignKey('restaurant.ProductoVenta', on_delete=models.CASCADE, related_name='personalizaciones')
    opcion = models.ForeignKey(OpcionPersonalizacion, on_delete=models.CASCADE)
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.opcion.nombre}"
    
    class Meta:
        unique_together = ['producto', 'opcion']
        verbose_name = "Personalización de producto"
        verbose_name_plural = "Personalizaciones de productos"

class OrdenItemPersonalizacion(models.Model):
    """Personalizaciones aplicadas a un item de orden específico"""
    orden_item = models.ForeignKey(OrdenItem, on_delete=models.CASCADE, related_name='personalizaciones')
    opcion = models.ForeignKey(OpcionPersonalizacion, on_delete=models.CASCADE)
    valor = models.TextField(blank=True, null=True, help_text="Valor específico para notas o cambios")
    precio_aplicado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.orden_item.producto.nombre} - {self.opcion.nombre}"
    
    class Meta:
        verbose_name = "Personalización del item"
        verbose_name_plural = "Personalizaciones de items"


class NotificacionCuenta(models.Model):
    """Modelo para notificaciones de cuenta solicitada"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='notificaciones_cuenta')
    mesero = models.ForeignKey('accounts.Usuario', on_delete=models.CASCADE, related_name='notificaciones_enviadas')
    cajero = models.ForeignKey('accounts.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='notificaciones_recibidas')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_procesamiento = models.DateTimeField(null=True, blank=True)
    notas = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Notificación de Cuenta"
        verbose_name_plural = "Notificaciones de Cuenta"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Cuenta solicitada - Orden {self.orden.numero_orden} - Mesa {self.orden.mesa.numero if self.orden.mesa else 'Sin mesa'}"
