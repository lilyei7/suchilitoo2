from django.db import models
from django.utils import timezone
from decimal import Decimal

class Proveedor(models.Model):
    """Modelo para proveedores de insumos"""
    nombre = models.CharField(max_length=200)
    ruc = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    notas = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']

class CategoriaInsumo(models.Model):
    """Modelo para categorías de insumos"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría de insumo"
        verbose_name_plural = "Categorías de insumos"
        ordering = ['nombre']


class UnidadMedida(models.Model):
    """Modelo para unidades de medida"""
    nombre = models.CharField(max_length=50, unique=True)
    abreviacion = models.CharField(max_length=10)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.abreviacion})"

    class Meta:
        verbose_name = "Unidad de medida"
        verbose_name_plural = "Unidades de medida"
        ordering = ['nombre']


class Insumo(models.Model):
    """Modelo para insumos del restaurante"""
    TIPO_CHOICES = [
        ('basico', 'Básico'),
        ('compuesto', 'Compuesto'),
        ('elaborado', 'Elaborado'),
    ]

    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='basico')
    categoria = models.ForeignKey(CategoriaInsumo, on_delete=models.PROTECT, related_name='insumos')
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Campos adicionales
    perecedero = models.BooleanField(default=False)
    dias_vencimiento = models.IntegerField(null=True, blank=True, help_text="Días para vencimiento")
    proveedor_principal = models.ForeignKey('Proveedor', on_delete=models.SET_NULL, null=True, blank=True, related_name='insumos_proveidos')
    
    # Campos para insumos compuestos/elaborados
    cantidad_producida = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    costo_produccion = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tiempo_preparacion = models.IntegerField(null=True, blank=True, help_text="Tiempo en minutos")
      # Campos para seguimiento
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def calcular_costo_total(self):
        """Calcula el costo total del insumo basado en sus componentes"""
        if self.tipo == 'basico':
            return self.precio_unitario
        elif self.tipo in ['compuesto', 'elaborado']:
            total = Decimal('0.00')
            for componente in self.componentes.all():
                total += componente.cantidad * componente.insumo_componente.precio_unitario
            return total
        return Decimal('0.00')

    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"
        ordering = ['codigo', 'nombre']


class InsumoCompuesto(models.Model):
    """Relación para insumos compuestos o elaborados"""
    insumo_compuesto = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='componentes')
    insumo_componente = models.ForeignKey(Insumo, on_delete=models.PROTECT, related_name='usado_en')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    notas = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.insumo_componente.nombre} en {self.insumo_compuesto.nombre}"

    class Meta:
        verbose_name = "Componente de insumo"
        verbose_name_plural = "Componentes de insumos"
        unique_together = ('insumo_compuesto', 'insumo_componente')


class Inventario(models.Model):
    """Modelo para gestionar el inventario"""
    sucursal = models.ForeignKey('accounts.Sucursal', on_delete=models.CASCADE, related_name='inventarios')
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='inventario')
    cantidad_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad_reservada = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad_disponible = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lote = models.CharField(max_length=50, blank=True, null=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Inventario de {self.insumo.nombre} en {self.sucursal.nombre}: {self.cantidad_actual} {self.insumo.unidad_medida.abreviacion}"
    
    def save(self, *args, **kwargs):
        # Calcular cantidad disponible
        self.cantidad_disponible = self.cantidad_actual - self.cantidad_reservada
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"
        unique_together = ('sucursal', 'insumo', 'lote')


class MovimientoInventario(models.Model):
    """Modelo para registrar movimientos de inventario"""
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
        ('transferencia', 'Transferencia'),
        ('produccion', 'Producción'),
        ('merma', 'Merma'),
    ]
    
    sucursal = models.ForeignKey('accounts.Sucursal', on_delete=models.CASCADE, related_name='movimientos_inventario', null=True)
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='movimientos')
    tipo_movimiento = models.CharField(max_length=20, choices=TIPO_CHOICES, default='ajuste')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_anterior = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad_nueva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    motivo = models.TextField(blank=True, null=True)
    documento_referencia = models.CharField(max_length=100, blank=True, null=True)
    usuario = models.ForeignKey('accounts.Usuario', on_delete=models.SET_NULL, null=True, related_name='movimientos_realizados')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f"{self.get_tipo_movimiento_display()} de {self.cantidad} {self.insumo.unidad_medida.abreviacion} de {self.insumo.nombre}"
    
    class Meta:
        verbose_name = "Movimiento de inventario"
        verbose_name_plural = "Movimientos de inventario"
        ordering = ['-created_at']


class CategoriaProducto(models.Model):
    """Modelo para categorías de productos de venta"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    orden = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Categoría de producto"
        verbose_name_plural = "Categorías de productos"
        ordering = ['orden', 'nombre']


class ProductoVenta(models.Model):
    """Modelo para productos disponibles para venta"""
    TIPO_CHOICES = [
        ('plato', 'Plato'),
        ('bebida', 'Bebida'),
        ('combo', 'Combo'),
        ('adicional', 'Adicional'),
        ('postre', 'Postre'),
    ]
    
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Cambiado de precio_venta a precio
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    margen = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='plato')
    disponible = models.BooleanField(default=True)  # Cambiado de activo a disponible
    es_promocion = models.BooleanField(default=False)  # Campo añadido
    destacado = models.BooleanField(default=False)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos_venta')  # Cambiado related_name
    calorias = models.IntegerField(default=0, blank=True, null=True, help_text="Calorías por porción")
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def calcular_margen(self):
        """Calcula el margen de ganancia"""
        if self.costo and self.costo > 0:
            return ((self.precio - self.costo) / self.costo) * 100
        return 0
    
    def calcular_costo_desde_recetas(self):
        """Calcula el costo del producto basado en las recetas asociadas"""
        from decimal import Decimal
        
        costo_total = Decimal('0.00')
        recetas_asociadas = self.recetas_asociadas.all()
        
        if recetas_asociadas.exists():
            for producto_receta in recetas_asociadas:
                receta = producto_receta.receta
                # Si la receta tiene un producto asociado, usamos su costo
                if receta.producto and receta.producto.costo > 0:
                    costo_total += receta.producto.costo
                else:
                    # Si no, calculamos el costo de la receta basado en sus insumos
                    for insumo_receta in receta.insumos.all():
                        costo_insumo = insumo_receta.insumo.precio_unitario * insumo_receta.cantidad
                        costo_total += costo_insumo
        
        self.costo = costo_total
        self.margen = self.calcular_margen()
        self.save()
    
    class Meta:
        verbose_name = "Producto de venta"
        verbose_name_plural = "Productos de venta"
        ordering = ['codigo', 'nombre']


class ProductoCategoria(models.Model):
    """Relación entre productos y categorías"""
    producto = models.ForeignKey(ProductoVenta, on_delete=models.CASCADE, related_name='categorias_asignadas')
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE, related_name='productos_asignados')
    
    def __str__(self):
        return f"{self.producto.nombre} en {self.categoria.nombre}"
    
    class Meta:
        verbose_name = "Categoría de producto"
        verbose_name_plural = "Categorías de productos"
        unique_together = ('producto', 'categoria')


class Receta(models.Model):
    """Modelo para recetas de los productos"""
    nombre = models.CharField(max_length=200)
    producto = models.OneToOneField(ProductoVenta, on_delete=models.SET_NULL, related_name='receta', null=True)
    tiempo_preparacion = models.IntegerField(default=0, help_text="Tiempo en minutos")
    porciones = models.IntegerField(default=1)
    instrucciones = models.TextField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        if self.producto:
            return f"Receta de {self.producto.nombre}"
        return "Receta sin producto"
    
    class Meta:
        verbose_name = "Receta"
        verbose_name_plural = "Recetas"


class RecetaInsumo(models.Model):
    """Relación entre recetas e insumos"""
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name='insumos')
    insumo = models.ForeignKey(Insumo, on_delete=models.PROTECT, related_name='usado_en_recetas')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    orden = models.IntegerField(default=0)
    opcional = models.BooleanField(default=False)
    notas = models.TextField(blank=True, null=True)
    
    def __str__(self):
        receta_nombre = "Sin producto" if not self.receta.producto else self.receta.producto.nombre
        return f"{self.insumo.nombre} en {receta_nombre}"
    
    class Meta:
        verbose_name = "Insumo de receta"
        verbose_name_plural = "Insumos de recetas"
        ordering = ['orden']


class CheckListItem(models.Model):
    """Modelo para items de checklist de operaciones"""
    TIPO_CHOICES = [
        ('apertura', 'Apertura'),
        ('cierre', 'Cierre'),
        ('limpieza', 'Limpieza'),
        ('mantenimiento', 'Mantenimiento'),
        ('seguridad', 'Seguridad'),
        ('calidad', 'Control de Calidad'),
        ('otro', 'Otro'),
    ]
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='otro')
    obligatorio = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    tiempo_estimado = models.IntegerField(default=5, help_text="Tiempo estimado en minutos")
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"
    
    class Meta:
        verbose_name = "Ítem de checklist"
        verbose_name_plural = "Ítems de checklist"
        ordering = ['tipo', 'orden', 'nombre']


class CheckListEjecucion(models.Model):
    """Modelo para registrar ejecuciones de checklist"""
    item = models.ForeignKey(CheckListItem, on_delete=models.CASCADE, related_name='ejecuciones')
    sucursal = models.ForeignKey('accounts.Sucursal', on_delete=models.CASCADE, related_name='checklists')
    usuario = models.ForeignKey('accounts.Usuario', on_delete=models.CASCADE, related_name='checklists')
    completado = models.BooleanField(default=False)
    fecha = models.DateField()
    fecha_ejecucion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    observaciones = models.TextField(blank=True, null=True)
    
    def __str__(self):
        estado = "Completado" if self.completado else "Pendiente"
        return f"{self.item.nombre} - {self.fecha} - {estado}"
    
    class Meta:
        verbose_name = "Ejecución de checklist"
        verbose_name_plural = "Ejecuciones de checklist"
        ordering = ['-fecha', 'item__orden']


class InsumoElaborado(models.Model):
    """Modelo para insumos elaborados con receta"""
    insumo = models.OneToOneField(Insumo, on_delete=models.CASCADE, related_name='elaborado', null=True)
    receta = models.TextField(blank=True, null=True)
    instrucciones = models.TextField(blank=True, null=True)
    tiempo_elaboracion = models.IntegerField(default=0, help_text="Tiempo en minutos")
    
    def __str__(self):
        return f"Elaboración de {self.insumo.nombre}"
    
    class Meta:
        verbose_name = "Insumo elaborado"
        verbose_name_plural = "Insumos elaborados"


class ConfiguracionSistema(models.Model):
    """Modelo para almacenar configuraciones generales del sistema"""
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre único para identificar la configuración")
    valor = models.TextField(blank=True, null=True, help_text="Valor de la configuración (puede ser JSON)")
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción de la configuración")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Configuración del sistema"
        verbose_name_plural = "Configuraciones del sistema"
        ordering = ['nombre']

# Importar el modelo ProductoReceta
from .models_producto_receta import ProductoReceta
