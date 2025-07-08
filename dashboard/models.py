from django.db import models
from django.utils import timezone
from decimal import Decimal
# Importamos Insumo desde restaurant para tener referencia consistente
from restaurant.models import Insumo as RestaurantInsumo
from accounts.models import Usuario, Sucursal

# Modelo para historial de precios de insumos
class HistorialPrecios(models.Model):
    """
    Modelo para llevar registro histórico de precios de los insumos.
    Permite calcular costos según método PEPS (Primero en Entrar, Primero en Salir)
    o costo promedio.
    """
    insumo = models.ForeignKey(RestaurantInsumo, on_delete=models.CASCADE, related_name='historial_precios')
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, null=True, blank=True)
    
    fecha_compra = models.DateTimeField(default=timezone.now)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_comprada = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_restante = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Campo opcional para referencia al MovimientoInventario (entrada)
    movimiento = models.ForeignKey(
        'restaurant.MovimientoInventario', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='historial_precios'
    )
    
    # Campos para auditoría
    creado_por = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='historial_precios_creados'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Historial de Precios'
        verbose_name_plural = 'Historial de Precios'
        ordering = ['insumo', 'fecha_compra']
    
    def __str__(self):
        return f"{self.insumo.nombre} - {self.fecha_compra.strftime('%d/%m/%Y')} - ${self.precio_unitario}"
    
    @property
    def valor_total(self):
        """Calcula el valor total de este lote de insumo (precio x cantidad restante)"""
        return self.precio_unitario * self.cantidad_restante
    
    @property
    def valor_inicial(self):
        """Calcula el valor inicial de compra (precio x cantidad comprada)"""
        return self.precio_unitario * self.cantidad_comprada
    
    @staticmethod
    def calcular_costo_peps(insumo, cantidad, sucursal=None):
        """
        Calcula el costo total de una cantidad dada de un insumo utilizando el método PEPS
        (Primero en Entrar, Primero en Salir).
        
        Args:
            insumo: Instancia del modelo Insumo
            cantidad: Cantidad a calcular
            sucursal: Sucursal específica (opcional)
            
        Returns:
            tuple: (costo_total, detalles)
                - costo_total: Decimal con el costo total calculado
                - detalles: Lista de diccionarios con el desglose de lotes usados
        """
        # Filtrar por insumo y sucursal si se especifica
        query = HistorialPrecios.objects.filter(
            insumo=insumo,
            cantidad_restante__gt=0
        ).order_by('fecha_compra')
        
        if sucursal:
            query = query.filter(sucursal=sucursal)
        
        # Obtener los lotes con stock disponible
        lotes = list(query)
        cantidad_pendiente = Decimal(str(cantidad))
        costo_total = Decimal('0')
        detalles = []
        
        # Recorrer lotes por fecha (PEPS)
        for lote in lotes:
            if cantidad_pendiente <= 0:
                break
                
            # Determinar cuánto tomamos de este lote
            cantidad_tomada = min(lote.cantidad_restante, cantidad_pendiente)
            costo_lote = cantidad_tomada * lote.precio_unitario
            
            # Agregar al costo total
            costo_total += costo_lote
            cantidad_pendiente -= cantidad_tomada
            
            # Registrar detalle de este lote
            detalles.append({
                'lote_id': lote.id,
                'fecha_compra': lote.fecha_compra,
                'precio_unitario': lote.precio_unitario,
                'cantidad_tomada': cantidad_tomada,
                'costo_lote': costo_lote
            })
        
        # Si no hay suficiente stock, usar el último precio conocido
        if cantidad_pendiente > 0:
            ultimo_precio = insumo.precio_unitario
            if lotes:
                ultimo_precio = lotes[-1].precio_unitario
                
            costo_faltante = cantidad_pendiente * ultimo_precio
            costo_total += costo_faltante
            
            detalles.append({
                'lote_id': None,
                'fecha_compra': None,
                'precio_unitario': ultimo_precio,
                'cantidad_tomada': cantidad_pendiente,
                'costo_lote': costo_faltante,
                'stock_insuficiente': True
            })
            
        return costo_total, detalles
    
    @staticmethod
    def calcular_costo_promedio(insumo, cantidad, sucursal=None):
        """
        Calcula el costo utilizando el método de costo promedio ponderado.
        
        Args:
            insumo: Instancia del modelo Insumo
            cantidad: Cantidad a calcular
            sucursal: Sucursal específica (opcional)
            
        Returns:
            tuple: (costo_total, precio_promedio)
        """
        query = HistorialPrecios.objects.filter(
            insumo=insumo,
            cantidad_restante__gt=0
        )
        
        if sucursal:
            query = query.filter(sucursal=sucursal)
            
        # Calcular costo promedio ponderado
        lotes = list(query)
        if not lotes:
            return insumo.precio_unitario * Decimal(str(cantidad)), insumo.precio_unitario
            
        total_unidades = sum(lote.cantidad_restante for lote in lotes)
        total_valor = sum(lote.cantidad_restante * lote.precio_unitario for lote in lotes)
        
        if total_unidades > 0:
            precio_promedio = total_valor / total_unidades
        else:
            precio_promedio = insumo.precio_unitario
            
        costo_total = precio_promedio * Decimal(str(cantidad))
        return costo_total, precio_promedio
    
    @staticmethod
    def descontar_stock_peps(insumo, cantidad, sucursal=None, descripcion="Venta de producto"):
        """
        Descuenta stock utilizando el método PEPS y registra el movimiento.
        
        Args:
            insumo: Instancia del modelo Insumo
            cantidad: Cantidad a descontar
            sucursal: Sucursal específica
            descripcion: Descripción del movimiento
            
        Returns:
            tuple: (costo_total, movimiento)
        """
        from restaurant.models import MovimientoInventario
        
        # Calcular costo PEPS
        costo_total, detalles = HistorialPrecios.calcular_costo_peps(insumo, cantidad, sucursal)
        
        # Registrar movimiento de salida
        movimiento = MovimientoInventario.objects.create(
            insumo=insumo,
            sucursal=sucursal,
            tipo_movimiento='salida',
            cantidad=cantidad,
            motivo='venta',
            observaciones=descripcion,
            costo_unitario=costo_total / Decimal(str(cantidad)) if cantidad else 0
        )
        
        # Actualizar lotes (descontar de cada uno según PEPS)
        for detalle in detalles:
            if detalle.get('lote_id'):
                lote = HistorialPrecios.objects.get(id=detalle['lote_id'])
                lote.cantidad_restante -= detalle['cantidad_tomada']
                lote.save()
        
        # Actualizar stock actual del insumo
        insumo.stock_actual -= cantidad
        insumo.save()
        
        return costo_total, movimiento

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
    
    # Campos para filtros de permisos
    creado_por = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='proveedores_creados',
        verbose_name="Creado por"
    )
    sucursal = models.ForeignKey(
        Sucursal, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='proveedores',
        verbose_name="Sucursal"
    )
    
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

# Importar modelos del sistema de ventas
from .models_ventas import (
    Mesa, Cliente, Orden, OrdenItem, Venta, DetalleVenta, 
    CajaApertura, CajaCierre
)

# Importar modelos del sistema de croquis
from .models_croquis import CroquisLayout
