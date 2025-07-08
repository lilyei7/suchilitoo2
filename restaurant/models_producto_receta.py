from django.db import models
from django.utils import timezone

class ProductoReceta(models.Model):
    """Modelo para relacionar productos de venta con múltiples recetas"""
    producto = models.ForeignKey('ProductoVenta', on_delete=models.CASCADE, related_name='recetas_asociadas')
    receta = models.ForeignKey('Receta', on_delete=models.CASCADE, related_name='productos_asociados')
    orden = models.IntegerField(default=0)
    notas = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.receta.producto.nombre if self.receta.producto else 'Receta sin nombre'}"
    
    class Meta:
        verbose_name = "Receta de producto"
        verbose_name_plural = "Recetas de productos"
        ordering = ['producto', 'orden']
        unique_together = ('producto', 'receta')
