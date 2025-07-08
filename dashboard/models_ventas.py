from django.db import models
from django.utils import timezone
from decimal import Decimal

from accounts.models import Usuario, Sucursal
from restaurant.models import ProductoVenta, Receta, RecetaInsumo, Insumo


class Mesa(models.Model):
    """Modelo para mesas del restaurante"""
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('reservada', 'Reservada'),
        ('mantenimiento', 'En Mantenimiento'),
    ]
    
    numero = models.CharField(max_length=10)
    nombre = models.CharField(max_length=50, blank=True, null=True)
    capacidad = models.IntegerField(default=4)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name='mesas')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    codigo_qr = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Mesa {self.numero} - {self.sucursal.nombre}"
    
    class Meta:
        verbose_name = "Mesa"
        verbose_name_plural = "Mesas"
        unique_together = ('numero', 'sucursal')
        ordering = ['sucursal', 'numero']


class Cliente(models.Model):
    """Modelo para clientes del restaurante"""
    nombre = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultima_visita = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']


class Orden(models.Model):
    """Modelo para órdenes de venta"""
    ESTADO_CHOICES = [
        ('abierta', 'Abierta'),
        ('en_proceso', 'En Proceso'),
        ('lista', 'Lista para Entrega'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
        ('cerrada', 'Cerrada'),
    ]
    
    TIPO_CHOICES = [
        ('mesa', 'Para Mesa'),
        ('llevar', 'Para Llevar'),
        ('delivery', 'Delivery'),
    ]
    
    numero = models.CharField(max_length=20, unique=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordenes')
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordenes')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='mesa')
    cajero = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='ordenes_creadas')
    mesero = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordenes_atendidas')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='abierta')
    notas = models.TextField(blank=True, null=True)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name='ordenes')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pagada = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Orden #{self.numero} - {self.get_estado_display()}"
    
    def calcular_totales(self):
        """Calcula los totales de la orden"""
        self.subtotal = sum(item.precio_total for item in self.items.all())
        self.total = self.subtotal - self.descuento + self.impuestos
        self.save()
    
    def generar_numero(self):
        """Genera un número único para la orden"""
        if not self.numero:
            fecha = timezone.now().strftime('%Y%m%d')
            ultimo_numero = Orden.objects.filter(
                numero__startswith=f"{fecha}-"
            ).order_by('-numero').first()
            
            if ultimo_numero:
                numero_secuencial = int(ultimo_numero.numero.split('-')[1]) + 1
            else:
                numero_secuencial = 1
            
            self.numero = f"{fecha}-{numero_secuencial:04d}"
    
    def save(self, *args, **kwargs):
        if not self.numero:
            self.generar_numero()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
        ordering = ['-fecha_hora']


class OrdenItem(models.Model):
    """Items de una orden"""
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(ProductoVenta, on_delete=models.PROTECT, related_name='items_orden')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notas = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, default='pendiente')
    
    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad} - Orden #{self.orden.numero}"
    
    def save(self, *args, **kwargs):
        self.precio_total = self.precio_unitario * self.cantidad
        self.costo_total = self.costo_unitario * self.cantidad
        super().save(*args, **kwargs)
        
        # Actualizar totales de la orden
        self.orden.calcular_totales()
    
    class Meta:
        verbose_name = "Item de orden"
        verbose_name_plural = "Items de orden"


class Venta(models.Model):
    """Modelo para ventas realizadas"""
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('credito', 'Crédito'),
        ('mixto', 'Pago Mixto'),
    ]
    
    numero_factura = models.CharField(max_length=50, blank=True, null=True)
    orden = models.OneToOneField(Orden, on_delete=models.PROTECT, related_name='venta')
    fecha_hora = models.DateTimeField(auto_now_add=True)
    cajero = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='ventas_realizadas')
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='compras')
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name='ventas')
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='efectivo')
    monto_recibido = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cambio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    anulada = models.BooleanField(default=False)
    motivo_anulacion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Venta #{self.id} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
    
    def calcular_cambio(self):
        """Calcula el cambio a devolver"""
        if self.metodo_pago == 'efectivo' and self.monto_recibido > 0:
            self.cambio = self.monto_recibido - self.total
        else:
            self.cambio = Decimal('0')
    
    def save(self, *args, **kwargs):
        # Tomar valores de la orden si existe
        if self.orden:
            self.subtotal = self.orden.subtotal
            self.descuento = self.orden.descuento
            self.impuestos = self.orden.impuestos
            self.total = self.orden.total
            
            # Marcar la orden como pagada
            self.orden.pagada = True
            self.orden.estado = 'cerrada'
            self.orden.save()
        
        self.calcular_cambio()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha_hora']


class DetalleVenta(models.Model):
    """Detalle de productos vendidos"""
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(ProductoVenta, on_delete=models.PROTECT, related_name='ventas')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad} - Venta #{self.venta.id}"
    
    def save(self, *args, **kwargs):
        self.precio_total = (self.precio_unitario * self.cantidad) - self.descuento
        self.costo_total = self.costo_unitario * self.cantidad
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Detalle de venta"
        verbose_name_plural = "Detalles de venta"


class CajaApertura(models.Model):
    """Registro de aperturas de caja"""
    cajero = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='aperturas_caja')
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name='aperturas_caja')
    fecha_hora = models.DateTimeField(auto_now_add=True)
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notas = models.TextField(blank=True, null=True)
    cerrada = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Apertura de caja - {self.cajero.get_full_name()} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
    
    class Meta:
        verbose_name = "Apertura de caja"
        verbose_name_plural = "Aperturas de caja"
        ordering = ['-fecha_hora']


class CajaCierre(models.Model):
    """Registro de cierres de caja"""
    apertura = models.OneToOneField(CajaApertura, on_delete=models.PROTECT, related_name='cierre')
    fecha_hora = models.DateTimeField(auto_now_add=True)
    monto_sistema = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_fisico = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    diferencia = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ventas_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ventas_tarjeta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ventas_otros = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notas = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Cierre de caja - {self.apertura.cajero.get_full_name()} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        self.diferencia = self.monto_fisico - self.monto_sistema
        self.total_ventas = self.ventas_efectivo + self.ventas_tarjeta + self.ventas_otros
        
        # Marcar la apertura como cerrada
        self.apertura.cerrada = True
        self.apertura.save()
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Cierre de caja"
        verbose_name_plural = "Cierres de caja"
        ordering = ['-fecha_hora']
