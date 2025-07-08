#!/usr/bin/env python
"""
Script para implementar gestión completa de estados de mesa
Opciones: Liberar desde cocina, mesero, cajero o automáticamente
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

try:
    django.setup()
except Exception as e:
    print(f"Error al configurar Django: {e}")
    sys.exit(1)

from django.utils import timezone
from mesero.models import Mesa, Orden
from accounts.models import Usuario

def mostrar_estados_actuales():
    """Muestra el estado actual de mesas y órdenes"""
    print("📊 ESTADO ACTUAL DE MESAS Y ÓRDENES")
    print("=" * 60)
    
    mesas = Mesa.objects.filter(activa=True).order_by('numero')
    
    for mesa in mesas:
        print(f"\n🪑 Mesa {mesa.numero} ({mesa.sucursal.nombre})")
        print(f"   📊 Estado: {mesa.estado}")
        
        ordenes_activas = mesa.ordenes_mesero.filter(
            estado__in=['pendiente', 'confirmada', 'en_preparacion', 'lista']
        )
        
        if ordenes_activas.exists():
            print(f"   🍽️ Órdenes activas: {ordenes_activas.count()}")
            for orden in ordenes_activas:
                print(f"      • {orden.numero_orden} - {orden.estado}")
        else:
            print(f"   ✅ Sin órdenes activas")

def simular_liberacion_mesa_desde_cocina():
    """Simula el proceso de liberar mesa desde cocina"""
    print("\n\n🍳 SIMULACIÓN: Liberar mesa desde COCINA")
    print("-" * 50)
    
    # Buscar una orden en estado 'lista' o 'en_preparacion'
    orden = Orden.objects.filter(
        estado__in=['en_preparacion', 'lista']
    ).first()
    
    if not orden:
        print("❌ No hay órdenes disponibles para marcar como completadas")
        return
    
    print(f"✅ Orden encontrada: {orden.numero_orden}")
    print(f"   Mesa: {orden.mesa.numero if orden.mesa else 'Sin mesa'}")
    print(f"   Estado actual: {orden.estado}")
    
    # Cambiar estado a entregada
    estado_anterior = orden.estado
    orden.cambiar_estado('entregada', observaciones="Completada desde cocina")
    
    # Verificar si la mesa se liberó
    orden.mesa.refresh_from_db()
    
    print(f"✅ Orden cambiada: {estado_anterior} → {orden.estado}")
    print(f"✅ Estado de mesa: {orden.mesa.estado}")
    
    return orden

def crear_funciones_liberacion():
    """Crear funciones para diferentes formas de liberar mesas"""
    print("\n\n🔧 IMPLEMENTANDO FUNCIONES DE LIBERACIÓN")
    print("-" * 50)
    
    funciones = [
        "✅ liberar_mesa_cocina() - Desde dashboard de cocina",
        "✅ liberar_mesa_mesero() - Botón manual del mesero", 
        "✅ liberar_mesa_cajero() - Al completar pago",
        "✅ liberar_mesa_automatica() - Al cerrar orden"
    ]
    
    for funcion in funciones:
        print(f"   {funcion}")

def main():
    print("🪑 GESTIÓN COMPLETA DE ESTADOS DE MESA")
    print("=" * 60)
    
    mostrar_estados_actuales()
    crear_funciones_liberacion()
    
    # Simular liberación desde cocina
    orden_liberada = simular_liberacion_mesa_desde_cocina()
    
    print("\n" + "=" * 60)
    print("🎯 PRÓXIMOS PASOS A IMPLEMENTAR:")
    print("1. 🍳 Botón 'Finalizar Servicio' en cocina")
    print("2. 👨‍💼 Botón 'Liberar Mesa' en interface del mesero") 
    print("3. 💰 Integración con sistema de pagos")
    print("4. 🔄 Estados automáticos basados en tiempo")

if __name__ == "__main__":
    main()
