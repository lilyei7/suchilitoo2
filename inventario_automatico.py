#!/usr/bin/env python3
"""
Sistema de descuento automático de inventario para el restaurante de sushi.

Este módulo implementa la lógica para descontar automáticamente los insumos 
del inventario cuando se crea una orden, siguiendo la estructura de recetas
y teniendo en cuenta insumos básicos, compuestos y elaborados.
"""

import os
import sys
import django
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import (
    ProductoVenta, Receta, RecetaInsumo, Insumo, InsumoCompuesto,
    InsumoElaborado, Inventario, MovimientoInventario
)
from mesero.models import Orden, OrdenItem
from accounts.models import Sucursal

class InventarioAutomatico:
    """Clase para manejar el descuento automático de inventario"""
    
    def __init__(self, sucursal):
        self.sucursal = sucursal
        self.debug = True
        self.log_messages = []
    
    def log(self, message):
        """Registra un mensaje de debug"""
        if self.debug:
            print(f"[INVENTARIO] {message}")
            self.log_messages.append(message)
    
    def procesar_orden(self, orden):
        """
        Procesa una orden completa y descuenta todos los insumos necesarios
        """
        self.log(f"🔄 Procesando orden #{orden.numero_orden}")
        
        try:
            with transaction.atomic():
                # Procesar cada item de la orden
                for orden_item in orden.items.all():
                    self.log(f"📦 Procesando item: {orden_item.cantidad}x {orden_item.producto.nombre}")
                    
                    # Descontar insumos para este item
                    self.descontar_insumos_producto(orden_item.producto, orden_item.cantidad, orden)
                
                self.log(f"✅ Orden #{orden.numero_orden} procesada exitosamente")
                return True, self.log_messages
                
        except Exception as e:
            self.log(f"❌ Error al procesar orden #{orden.numero_orden}: {str(e)}")
            return False, self.log_messages
    
    def descontar_insumos_producto(self, producto, cantidad, orden):
        """
        Descuenta los insumos necesarios para un producto específico
        """
        self.log(f"  🔍 Buscando receta para {producto.nombre}")
        
        # Buscar la receta del producto
        try:
            receta = producto.receta
            if not receta:
                self.log(f"  ⚠️  No hay receta para {producto.nombre}")
                return
        except:
            self.log(f"  ⚠️  No hay receta para {producto.nombre}")
            return
        
        # Procesar cada insumo de la receta
        for receta_insumo in receta.insumos.all():
            cantidad_necesaria = receta_insumo.cantidad * cantidad
            self.log(f"    🧪 Necesario: {cantidad_necesaria} {receta_insumo.insumo.unidad_medida.abreviacion} de {receta_insumo.insumo.nombre}")
            
            # Descontar este insumo recursivamente
            self.descontar_insumo_recursivo(receta_insumo.insumo, cantidad_necesaria, orden)
    
    def descontar_insumo_recursivo(self, insumo, cantidad_necesaria, orden):
        """
        Descuenta un insumo de manera recursiva, teniendo en cuenta si es básico, compuesto o elaborado
        """
        self.log(f"      🔄 Procesando insumo {insumo.nombre} (tipo: {insumo.tipo})")
        
        if insumo.tipo == 'basico':
            # Insumo básico: descontar directamente del inventario
            self.descontar_insumo_basico(insumo, cantidad_necesaria, orden)
            
        elif insumo.tipo == 'compuesto':
            # Insumo compuesto: descontar sus componentes
            self.descontar_insumo_compuesto(insumo, cantidad_necesaria, orden)
            
        elif insumo.tipo == 'elaborado':
            # Insumo elaborado: descontar sus componentes
            self.descontar_insumo_elaborado(insumo, cantidad_necesaria, orden)
        
        else:
            self.log(f"        ⚠️  Tipo de insumo desconocido: {insumo.tipo}")
    
    def descontar_insumo_basico(self, insumo, cantidad_necesaria, orden):
        """
        Descuenta un insumo básico del inventario
        """
        self.log(f"        📦 Descontando insumo básico: {cantidad_necesaria} {insumo.unidad_medida.abreviacion} de {insumo.nombre}")
        
        # Buscar el inventario para este insumo en la sucursal
        inventario, created = Inventario.objects.get_or_create(
            sucursal=self.sucursal,
            insumo=insumo,
            defaults={
                'cantidad_actual': insumo.stock_actual,
                'cantidad_reservada': 0,
                'costo_unitario': insumo.precio_unitario
            }
        )
        
        if created:
            self.log(f"        ℹ️  Inventario creado para {insumo.nombre}")
        
        # Verificar si hay suficiente stock
        if inventario.cantidad_disponible < cantidad_necesaria:
            error_msg = f"Stock insuficiente para {insumo.nombre}. Disponible: {inventario.cantidad_disponible}, Necesario: {cantidad_necesaria}"
            self.log(f"        ❌ {error_msg}")
            raise ValueError(error_msg)
        
        # Descontar del inventario
        cantidad_anterior = inventario.cantidad_actual
        inventario.cantidad_actual -= cantidad_necesaria
        inventario.save()
        
        # Actualizar el stock del insumo
        insumo.stock_actual -= cantidad_necesaria
        insumo.save()
        
        # Registrar el movimiento
        MovimientoInventario.objects.create(
            sucursal=self.sucursal,
            insumo=insumo,
            tipo_movimiento='salida',
            cantidad=cantidad_necesaria,
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=inventario.cantidad_actual,
            motivo=f'Descuento automático por orden #{orden.numero_orden}',
            documento_referencia=orden.numero_orden,
            usuario=orden.mesero
        )
        
        self.log(f"        ✅ Descontado: {cantidad_necesaria} {insumo.unidad_medida.abreviacion} de {insumo.nombre}")
        self.log(f"        📊 Stock anterior: {cantidad_anterior}, Stock actual: {inventario.cantidad_actual}")
    
    def descontar_insumo_compuesto(self, insumo, cantidad_necesaria, orden):
        """
        Descuenta un insumo compuesto procesando sus componentes
        """
        self.log(f"        🧬 Procesando insumo compuesto: {insumo.nombre}")
        
        # Obtener todos los componentes del insumo compuesto
        componentes = InsumoCompuesto.objects.filter(insumo_compuesto=insumo)
        
        if not componentes.exists():
            self.log(f"        ⚠️  Insumo compuesto {insumo.nombre} no tiene componentes definidos")
            return
        
        # Procesar cada componente
        for componente in componentes:
            cantidad_componente_necesaria = componente.cantidad * cantidad_necesaria
            self.log(f"          🔸 Componente: {cantidad_componente_necesaria} {componente.insumo_componente.unidad_medida.abreviacion} de {componente.insumo_componente.nombre}")
            
            # Descontar recursivamente el componente
            self.descontar_insumo_recursivo(componente.insumo_componente, cantidad_componente_necesaria, orden)
    
    def descontar_insumo_elaborado(self, insumo, cantidad_necesaria, orden):
        """
        Descuenta un insumo elaborado procesando sus componentes
        """
        self.log(f"        👨‍🍳 Procesando insumo elaborado: {insumo.nombre}")
        
        # Los insumos elaborados también usan InsumoCompuesto para sus componentes
        componentes = InsumoCompuesto.objects.filter(insumo_compuesto=insumo)
        
        if not componentes.exists():
            self.log(f"        ⚠️  Insumo elaborado {insumo.nombre} no tiene componentes definidos")
            return
        
        # Procesar cada componente
        for componente in componentes:
            cantidad_componente_necesaria = componente.cantidad * cantidad_necesaria
            self.log(f"          🔸 Componente: {cantidad_componente_necesaria} {componente.insumo_componente.unidad_medida.abreviacion} de {componente.insumo_componente.nombre}")
            
            # Descontar recursivamente el componente
            self.descontar_insumo_recursivo(componente.insumo_componente, cantidad_componente_necesaria, orden)
    
    def verificar_stock_disponible(self, producto, cantidad):
        """
        Verifica si hay suficiente stock para un producto antes de crear la orden
        """
        self.log(f"🔍 Verificando stock para {cantidad}x {producto.nombre}")
        
        try:
            # Buscar la receta del producto
            receta = producto.receta
            if not receta:
                self.log(f"  ⚠️  No hay receta para {producto.nombre}")
                return True, []  # Si no hay receta, no hay restricciones de stock
            
            # Calcular los insumos necesarios
            insumos_necesarios = []
            self.calcular_insumos_necesarios(receta, cantidad, insumos_necesarios)
            
            # Verificar stock para cada insumo
            faltantes = []
            for insumo_data in insumos_necesarios:
                insumo = insumo_data['insumo']
                cantidad_necesaria = insumo_data['cantidad']
                
                # Obtener inventario actual
                try:
                    inventario = Inventario.objects.get(sucursal=self.sucursal, insumo=insumo)
                    disponible = inventario.cantidad_disponible
                except Inventario.DoesNotExist:
                    disponible = insumo.stock_actual
                
                if disponible < cantidad_necesaria:
                    faltantes.append({
                        'insumo': insumo.nombre,
                        'necesario': cantidad_necesaria,
                        'disponible': disponible,
                        'unidad': insumo.unidad_medida.abreviacion
                    })
            
            if faltantes:
                self.log(f"  ❌ Stock insuficiente para {producto.nombre}")
                for faltante in faltantes:
                    self.log(f"    - {faltante['insumo']}: necesario {faltante['necesario']} {faltante['unidad']}, disponible {faltante['disponible']} {faltante['unidad']}")
                return False, faltantes
            
            self.log(f"  ✅ Stock suficiente para {producto.nombre}")
            return True, []
            
        except Exception as e:
            self.log(f"  ❌ Error verificando stock: {str(e)}")
            return False, [{'error': str(e)}]
    
    def calcular_insumos_necesarios(self, receta, cantidad, insumos_necesarios):
        """
        Calcula recursivamente todos los insumos necesarios para una receta
        """
        for receta_insumo in receta.insumos.all():
            cantidad_necesaria = receta_insumo.cantidad * cantidad
            self.calcular_insumos_necesarios_recursivo(receta_insumo.insumo, cantidad_necesaria, insumos_necesarios)
    
    def calcular_insumos_necesarios_recursivo(self, insumo, cantidad_necesaria, insumos_necesarios):
        """
        Calcula recursivamente los insumos necesarios para un insumo específico
        """
        if insumo.tipo == 'basico':
            # Insumo básico: agregarlo a la lista
            # Buscar si ya existe en la lista
            for item in insumos_necesarios:
                if item['insumo'] == insumo:
                    item['cantidad'] += cantidad_necesaria
                    return
            
            # Si no existe, agregarlo
            insumos_necesarios.append({
                'insumo': insumo,
                'cantidad': cantidad_necesaria
            })
            
        elif insumo.tipo in ['compuesto', 'elaborado']:
            # Insumo compuesto/elaborado: procesar sus componentes
            componentes = InsumoCompuesto.objects.filter(insumo_compuesto=insumo)
            
            for componente in componentes:
                cantidad_componente_necesaria = componente.cantidad * cantidad_necesaria
                self.calcular_insumos_necesarios_recursivo(componente.insumo_componente, cantidad_componente_necesaria, insumos_necesarios)

def test_inventario_automatico():
    """Función de prueba para el sistema de inventario automático"""
    print("🧪 Iniciando prueba del sistema de inventario automático")
    
    # Obtener la primera sucursal
    sucursal = Sucursal.objects.first()
    if not sucursal:
        print("❌ No se encontró ninguna sucursal")
        return
    
    print(f"🏢 Usando sucursal: {sucursal.nombre}")
    
    # Crear instancia del inventario automático
    inventario = InventarioAutomatico(sucursal)
    
    # Buscar una orden reciente para probar
    orden = Orden.objects.filter(estado='pendiente').first()
    if not orden:
        print("❌ No se encontró ninguna orden pendiente para probar")
        return
    
    print(f"📋 Probando con orden #{orden.numero_orden}")
    
    # Procesar la orden
    success, messages = inventario.procesar_orden(orden)
    
    print(f"\n{'='*50}")
    print(f"Resultado: {'✅ ÉXITO' if success else '❌ ERROR'}")
    print(f"{'='*50}")
    
    for message in messages:
        print(message)

if __name__ == "__main__":
    test_inventario_automatico()
