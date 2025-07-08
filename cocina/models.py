from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from mesero.models import Orden, OrdenItem

User = get_user_model()

class EstadoCocina(models.Model):
    """Estados específicos para el manejo en cocina"""
    ESTADO_CHOICES = [
        ('recibida', 'Recibida'),
        ('en_preparacion', 'En Preparación'),
        ('lista', 'Lista'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
    ]
    
    nombre = models.CharField(max_length=50, choices=ESTADO_CHOICES, unique=True)
    descripcion = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6c757d', help_text="Color hexadecimal para la interfaz")
    orden = models.IntegerField(default=0, help_text="Orden de visualización")
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.get_nombre_display()
    
    class Meta:
        verbose_name = "Estado de cocina"
        verbose_name_plural = "Estados de cocina"
        ordering = ['orden', 'nombre']

class TiempoPreparacion(models.Model):
    """Registro de tiempos de preparación por producto"""
    producto = models.ForeignKey('restaurant.ProductoVenta', on_delete=models.CASCADE)
    tiempo_estimado = models.IntegerField(help_text="Tiempo estimado en minutos")
    tiempo_promedio = models.FloatField(default=0, help_text="Tiempo promedio real en minutos")
    cantidad_preparaciones = models.IntegerField(default=0)
    
    def actualizar_tiempo_promedio(self, nuevo_tiempo):
        """Actualiza el tiempo promedio con un nuevo tiempo real"""
        if self.cantidad_preparaciones == 0:
            self.tiempo_promedio = nuevo_tiempo
        else:
            # Calcular nueva media
            total_tiempo = self.tiempo_promedio * self.cantidad_preparaciones
            self.tiempo_promedio = (total_tiempo + nuevo_tiempo) / (self.cantidad_preparaciones + 1)
        
        self.cantidad_preparaciones += 1
        self.save()
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.tiempo_estimado}min"
    
    class Meta:
        verbose_name = "Tiempo de preparación"
        verbose_name_plural = "Tiempos de preparación"

class OrdenCocina(models.Model):
    """Extensión de Orden para manejo específico de cocina"""
    orden = models.OneToOneField(Orden, on_delete=models.CASCADE, related_name='cocina_info')
    cocinero_asignado = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='ordenes_cocina_asignadas'
    )
    prioridad = models.IntegerField(default=0, help_text="0=Normal, 1=Alta, 2=Urgente")
    tiempo_estimado_total = models.IntegerField(default=0, help_text="Tiempo estimado total en minutos")
    fecha_inicio_preparacion = models.DateTimeField(null=True, blank=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    notas_cocina = models.TextField(blank=True, help_text="Notas específicas para cocina")
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def tiempo_preparacion_real(self):
        """Calcula el tiempo real de preparación"""
        if self.fecha_inicio_preparacion and self.fecha_finalizacion:
            delta = self.fecha_finalizacion - self.fecha_inicio_preparacion
            return delta.total_seconds() / 60  # Retorna en minutos
        return None
    
    def tiempo_transcurrido(self):
        """Calcula el tiempo transcurrido desde el inicio de preparación"""
        if self.fecha_inicio_preparacion:
            delta = timezone.now() - self.fecha_inicio_preparacion
            return delta.total_seconds() / 60  # Retorna en minutos
        return None
    
    def calcular_tiempo_estimado(self):
        """Calcula el tiempo estimado basado en los productos"""
        total_tiempo = 0
        for item in self.orden.items.all():
            try:
                tiempo_prep = TiempoPreparacion.objects.get(producto=item.producto)
                total_tiempo += tiempo_prep.tiempo_estimado * item.cantidad
            except TiempoPreparacion.DoesNotExist:
                # Tiempo por defecto si no hay datos
                total_tiempo += 15 * item.cantidad  # 15 minutos por defecto
        
        self.tiempo_estimado_total = total_tiempo
        self.save()
        return total_tiempo
    
    def iniciar_preparacion(self, cocinero=None):
        """Marca el inicio de preparación"""
        self.fecha_inicio_preparacion = timezone.now()
        if cocinero:
            self.cocinero_asignado = cocinero
        self.save()
    
    def finalizar_preparacion(self):
        """Marca la finalización de preparación"""
        self.fecha_finalizacion = timezone.now()
        self.save()
        
        # Actualizar tiempos promedio de cada producto
        tiempo_real = self.tiempo_preparacion_real()
        if tiempo_real:
            items_count = self.orden.items.count()
            tiempo_por_item = tiempo_real / items_count if items_count > 0 else tiempo_real
            
            for item in self.orden.items.all():
                tiempo_prep, created = TiempoPreparacion.objects.get_or_create(
                    producto=item.producto,
                    defaults={'tiempo_estimado': 15}
                )
                tiempo_prep.actualizar_tiempo_promedio(tiempo_por_item * item.cantidad)
    
    def __str__(self):
        return f"Cocina - {self.orden.numero_orden}"
    
    class Meta:
        verbose_name = "Orden de cocina"
        verbose_name_plural = "Órdenes de cocina"
        ordering = ['-prioridad', 'fecha_creacion']

class ItemCocina(models.Model):
    """Extensión de OrdenItem para manejo específico de cocina"""
    orden_item = models.OneToOneField(OrdenItem, on_delete=models.CASCADE, related_name='cocina_info')
    estado_cocina = models.CharField(
        max_length=20,
        choices=EstadoCocina.ESTADO_CHOICES,
        default='recibida'
    )
    tiempo_inicio = models.DateTimeField(null=True, blank=True)
    tiempo_finalizacion = models.DateTimeField(null=True, blank=True)
    cocinero_responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items_cocina_responsables'
    )
    notas_preparacion = models.TextField(blank=True)
    
    def tiempo_preparacion(self):
        """Calcula el tiempo de preparación del item"""
        if self.tiempo_inicio and self.tiempo_finalizacion:
            delta = self.tiempo_finalizacion - self.tiempo_inicio
            return delta.total_seconds() / 60  # Retorna en minutos
        return None
    
    def iniciar_preparacion(self, cocinero=None):
        """Inicia la preparación del item"""
        self.tiempo_inicio = timezone.now()
        self.estado_cocina = 'en_preparacion'
        if cocinero:
            self.cocinero_responsable = cocinero
        self.save()
    
    def finalizar_preparacion(self):
        """Finaliza la preparación del item"""
        self.tiempo_finalizacion = timezone.now()
        self.estado_cocina = 'lista'
        self.save()
    
    def __str__(self):
        return f"{self.orden_item.producto.nombre} - {self.get_estado_cocina_display()}"
    
    class Meta:
        verbose_name = "Item de cocina"
        verbose_name_plural = "Items de cocina"

class LogCocina(models.Model):
    """Log de actividades en cocina"""
    ACCION_CHOICES = [
        ('orden_recibida', 'Orden Recibida'),
        ('preparacion_iniciada', 'Preparación Iniciada'),
        ('item_completado', 'Item Completado'),
        ('orden_completada', 'Orden Completada'),
        ('orden_cancelada', 'Orden Cancelada'),
        ('cambio_estado', 'Cambio de Estado'),
        ('asignacion_cocinero', 'Asignación de Cocinero'),
    ]
    
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='logs_cocina')
    item = models.ForeignKey(OrdenItem, on_delete=models.CASCADE, null=True, blank=True)
    accion = models.CharField(max_length=30, choices=ACCION_CHOICES)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.orden.numero_orden} - {self.get_accion_display()}"
    
    class Meta:
        verbose_name = "Log de cocina"
        verbose_name_plural = "Logs de cocina"
        ordering = ['-timestamp']
