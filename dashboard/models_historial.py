from django.db import models
from django.utils import timezone
from decimal import Decimal
from restaurant.models import Insumo
from accounts.models import Usuario, Sucursal

class HistorialPrecios(models.Model):
    """
    Modelo para llevar registro histórico de precios de los insumos.
    Permite calcular costos según método PEPS (Primero en Entrar, Primero en Salir)
    o costo promedio.
    """
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='historial_precios')
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
