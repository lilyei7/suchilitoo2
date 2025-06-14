from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Sucursal

User = get_user_model()

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    direccion = models.TextField()
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.nombre

class CategoriaInsumo(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Categoría de Insumo'
        verbose_name_plural = 'Categorías de Insumos'

    def __str__(self):
        return self.nombre

class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=20)  # kg, gr, lt, ml, unidad, etc.
    abreviacion = models.CharField(max_length=10)
    
    class Meta:
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'

    def __str__(self):
        return f"{self.nombre} ({self.abreviacion})"

class Insumo(models.Model):
    TIPOS_INSUMO = [
        ('basico', 'Insumo Básico'),
        ('compuesto', 'Insumo Compuesto'),
        ('elaborado', 'Insumo Elaborado'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(CategoriaInsumo, on_delete=models.CASCADE)
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPOS_INSUMO, default='basico')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad_producida = models.DecimalField(
        max_digits=10, 
        decimal_places=3, 
        null=True, 
        blank=True,
        help_text="Cantidad que se produce de este insumo compuesto"
    )
    descripcion = models.TextField(blank=True, help_text="Descripción del insumo")
    proveedor_principal = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    perecedero = models.BooleanField(default=False)
    dias_vencimiento = models.IntegerField(null=True, blank=True, help_text="Días hasta vencimiento")
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Insumo'
        verbose_name_plural = 'Insumos'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def calcular_costo_compuesto(self):
        """Calcula el costo total de un insumo compuesto basado en sus componentes"""
        if self.tipo != 'compuesto':
            return self.precio_unitario
        
        total_costo = 0
        for componente in self.componentes.all():
            total_costo += componente.costo_total()
        
        return total_costo

class InsumoCompuesto(models.Model):
    """Modelo para manejar los componentes de un insumo compuesto"""
    insumo_compuesto = models.ForeignKey(
        Insumo, 
        on_delete=models.CASCADE, 
        related_name='componentes',
        limit_choices_to={'tipo': 'compuesto'}
    )
    insumo_componente = models.ForeignKey(
        Insumo, 
        on_delete=models.CASCADE, 
        related_name='usado_en_compuestos',
        limit_choices_to={'tipo': 'basico'}
    )
    cantidad = models.DecimalField(
        max_digits=10, 
        decimal_places=3,
        help_text="Cantidad del componente necesaria"
    )
    orden = models.IntegerField(default=0, help_text="Orden en la lista de componentes")
    
    class Meta:
        verbose_name = 'Componente de Insumo Compuesto'
        verbose_name_plural = 'Componentes de Insumos Compuestos'
        unique_together = ['insumo_compuesto', 'insumo_componente']
        ordering = ['orden', 'insumo_componente__nombre']
    
    def costo_total(self):
        """Calcula el costo total de este componente"""
        return self.cantidad * self.insumo_componente.precio_unitario
    
    def __str__(self):
        return f"{self.insumo_compuesto.nombre} - {self.insumo_componente.nombre} ({self.cantidad} {self.insumo_componente.unidad_medida.abreviacion})"

class InsumoElaborado(models.Model):
    """Modelo para manejar los componentes de un insumo elaborado (usa insumos compuestos)"""
    insumo_elaborado = models.ForeignKey(
        Insumo, 
        on_delete=models.CASCADE, 
        related_name='componentes_elaborados',
        limit_choices_to={'tipo': 'elaborado'}
    )
    insumo_componente = models.ForeignKey(
        Insumo, 
        on_delete=models.CASCADE, 
        related_name='usado_en_elaborados',
        limit_choices_to={'tipo': 'compuesto'}
    )
    cantidad = models.DecimalField(
        max_digits=10, 
        decimal_places=3,
        help_text="Cantidad del componente necesaria"
    )
    orden = models.IntegerField(default=0, help_text="Orden en la lista de componentes")
    tiempo_preparacion_minutos = models.IntegerField(
        default=0, 
        help_text="Tiempo adicional de preparación en minutos"
    )
    instrucciones = models.TextField(
        blank=True,
        help_text="Instrucciones específicas para este componente"
    )
    
    class Meta:
        verbose_name = 'Componente de Insumo Elaborado'
        verbose_name_plural = 'Componentes de Insumos Elaborados'
        unique_together = ['insumo_elaborado', 'insumo_componente']
        ordering = ['orden', 'insumo_componente__nombre']
    
    def costo_total(self):
        """Calcula el costo total de este componente"""
        return self.cantidad * self.insumo_componente.precio_unitario
    
    def __str__(self):
        return f"{self.insumo_elaborado.nombre} - {self.insumo_componente.nombre} ({self.cantidad} {self.insumo_componente.unidad_medida.abreviacion})"

class CategoriaReceta(models.Model):
    """Categorías específicas para recetas de sushi"""
    codigo = models.CharField(max_length=50, unique=True, help_text="Código único para la categoría")
    nombre = models.CharField(max_length=100, help_text="Nombre de la categoría")
    descripcion = models.TextField(blank=True, help_text="Descripción de la categoría")
    activa = models.BooleanField(default=True, help_text="Si la categoría está activa")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Categoría de Receta'
        verbose_name_plural = 'Categorías de Recetas'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Receta(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey('CategoriaReceta', on_delete=models.SET_NULL, null=True, blank=True, help_text="Categoría de la receta")
    descripcion = models.TextField()
    instrucciones = models.TextField()
    tiempo_preparacion = models.IntegerField(help_text="Tiempo en minutos")
    porciones = models.IntegerField(default=1)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Receta'
        verbose_name_plural = 'Recetas'

    def __str__(self):
        return self.nombre

class RecetaInsumo(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name='ingredientes')
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)
    
    class Meta:
        verbose_name = 'Ingrediente de Receta'
        verbose_name_plural = 'Ingredientes de Recetas'
        unique_together = ['receta', 'insumo']

    def __str__(self):
        return f"{self.receta.nombre} - {self.insumo.nombre}"

class Inventario(models.Model):
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    cantidad_actual = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    cantidad_reservada = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fecha_ultimo_movimiento = models.DateTimeField(auto_now=True)
    lote = models.CharField(max_length=50, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'
        unique_together = ['sucursal', 'insumo', 'lote']

    def __str__(self):
        return f"{self.sucursal.nombre} - {self.insumo.nombre}: {self.cantidad_actual}"

    @property
    def cantidad_disponible(self):
        return self.cantidad_actual - self.cantidad_reservada

class MovimientoInventario(models.Model):
    TIPOS_MOVIMIENTO = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
        ('merma', 'Merma'),
        ('transferencia', 'Transferencia'),
    ]
    
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    tipo_movimiento = models.CharField(max_length=20, choices=TIPOS_MOVIMIENTO)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    motivo = models.TextField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    lote = models.CharField(max_length=50, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    documento_referencia = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'

    def __str__(self):
        return f"{self.get_tipo_movimiento_display()} - {self.insumo.nombre} - {self.cantidad}"

class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Categoría de Producto'
        verbose_name_plural = 'Categorías de Productos'

    def __str__(self):
        return self.nombre

class ProductoVenta(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    receta = models.ForeignKey(Receta, on_delete=models.SET_NULL, null=True, blank=True)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    disponible = models.BooleanField(default=True)
    es_promocion = models.BooleanField(default=False)
    precio_promocion = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_inicio_promocion = models.DateField(null=True, blank=True)
    fecha_fin_promocion = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto de Venta'
        verbose_name_plural = 'Productos de Venta'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class CheckListItem(models.Model):
    TIPOS_CHECKLIST = [
        ('apertura', 'Apertura'),
        ('cierre', 'Cierre'),
        ('limpieza', 'Limpieza'),
        ('seguridad', 'Seguridad'),
        ('inventario', 'Inventario'),
    ]
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS_CHECKLIST)
    obligatorio = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Item de CheckList'
        verbose_name_plural = 'Items de CheckList'
        ordering = ['tipo', 'orden']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nombre}"

class CheckListEjecucion(models.Model):
    item = models.ForeignKey(CheckListItem, on_delete=models.CASCADE)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    completado = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True)
    fecha_ejecucion = models.DateTimeField(auto_now_add=True)
    fecha = models.DateField()

    class Meta:
        verbose_name = 'Ejecución de CheckList'
        verbose_name_plural = 'Ejecuciones de CheckList'
        unique_together = ['item', 'sucursal', 'fecha', 'usuario']

    def __str__(self):
        return f"{self.item.nombre} - {self.sucursal.nombre} - {self.fecha}"
