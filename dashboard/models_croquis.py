from django.db import models
from accounts.models import Sucursal

class CroquisLayout(models.Model):
    """Modelo para guardar los layouts de croquis de las sucursales"""
    sucursal = models.OneToOneField(Sucursal, on_delete=models.CASCADE, related_name='croquis_layout')
    layout_data = models.JSONField(help_text="Datos del layout en formato JSON")
    version = models.CharField(max_length=10, default='1.0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Layout de Croquis"
        verbose_name_plural = "Layouts de Croquis"
        db_table = 'dashboard_croquis_layout'
    
    def __str__(self):
        return f"Croquis de {self.sucursal.nombre}"
    
    def get_objetos_por_tipo(self):
        """Obtiene estadísticas de objetos por tipo en el layout"""
        objetos = self.layout_data.get('objetos', [])
        estadisticas = {}
        
        for objeto in objetos:
            tipo = objeto.get('tipo', 'desconocido')
            estadisticas[tipo] = estadisticas.get(tipo, 0) + 1
            
        return estadisticas
    
    def get_mesas_vinculadas(self):
        """Obtiene lista de IDs de mesas vinculadas en el croquis"""
        objetos = self.layout_data.get('objetos', [])
        mesas_vinculadas = []
        
        for objeto in objetos:
            if objeto.get('tipo') == 'mesa' and objeto.get('mesaId'):
                mesas_vinculadas.append(objeto.get('mesaId'))
                
        return mesas_vinculadas
    
    def validar_integridad(self):
        """Valida que las mesas vinculadas existan en la base de datos"""
        from dashboard.models_ventas import Mesa
        
        mesas_vinculadas = self.get_mesas_vinculadas()
        mesas_existentes = Mesa.objects.filter(
            id__in=mesas_vinculadas, 
            sucursal=self.sucursal
        ).values_list('id', flat=True)
        
        mesas_faltantes = set(mesas_vinculadas) - set(mesas_existentes)
        
        return {
            'valido': len(mesas_faltantes) == 0,
            'mesas_faltantes': list(mesas_faltantes),
            'total_vinculadas': len(mesas_vinculadas),
            'total_existentes': len(mesas_existentes)
        }
