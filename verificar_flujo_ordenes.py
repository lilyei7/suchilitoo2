#!/usr/bin/env python
"""
Script para verificar el flujo completo de órdenes en el sistema
"""

import os
import django
import sys

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.utils import timezone
from mesero.models import Orden, OrdenItem, Mesa, NotificacionCuenta, HistorialOrden
from django.contrib.auth import get_user_model

User = get_user_model()

def verificar_flujo_ordenes():
    """Verifica el estado actual del sistema de órdenes"""
    
    print("=" * 80)
    print("🔍 VERIFICACIÓN DEL FLUJO DE ÓRDENES")
    print("=" * 80)
    
    # 1. Estado de las órdenes actuales
    print("\n📋 ESTADO ACTUAL DE ÓRDENES:")
    print("-" * 50)
    
    total_ordenes = Orden.objects.count()
    print(f"Total de órdenes en el sistema: {total_ordenes}")
    
    # Agrupar por estado
    estados = Orden.objects.values('estado').distinct()
    for estado_dict in estados:
        estado = estado_dict['estado']
        count = Orden.objects.filter(estado=estado).count()
        print(f"  {estado.upper()}: {count} órdenes")
    
    # 2. Órdenes recientes (últimas 10)
    print("\n🕒 ÓRDENES RECIENTES (últimas 10):")
    print("-" * 50)
    ordenes_recientes = Orden.objects.order_by('-fecha_creacion')[:10]
    
    for orden in ordenes_recientes:
        mesa_info = f"Mesa {orden.mesa.numero}" if orden.mesa else "Sin mesa"
        mesero_info = orden.mesero.username if orden.mesero else "Sin mesero"
        
        print(f"  {orden.numero_orden} | {mesa_info} | {orden.estado.upper()} | {mesero_info}")
        print(f"    Total: ${orden.total} | Creada: {orden.fecha_creacion.strftime('%d/%m/%Y %H:%M')}")
        
        # Estado de cuenta
        if orden.cuenta_solicitada:
            fecha_solicitud = orden.fecha_solicitud_cuenta.strftime('%H:%M') if orden.fecha_solicitud_cuenta else "N/A"
            print(f"    💳 Cuenta solicitada: {fecha_solicitud}")
        
        if orden.cuenta_procesada:
            fecha_procesamiento = orden.fecha_procesamiento_cuenta.strftime('%H:%M') if orden.fecha_procesamiento_cuenta else "N/A"
            print(f"    ✅ Cuenta procesada: {fecha_procesamiento} | Método: {orden.metodo_pago_cuenta}")
            if orden.monto_recibido:
                print(f"    💰 Recibido: ${orden.monto_recibido} | Cambio: ${orden.cambio_dado or 0}")
        
        print()
    
    # 3. Estado de mesas
    print("\n🏠 ESTADO DE MESAS:")
    print("-" * 50)
    
    mesas_estados = Mesa.objects.values('estado').distinct()
    for estado_dict in mesas_estados:
        estado = estado_dict['estado']
        count = Mesa.objects.filter(estado=estado).count()
        print(f"  {estado.upper()}: {count} mesas")
    
    # Mesas con órdenes activas
    mesas_con_ordenes = Mesa.objects.filter(
        ordenes_mesero__estado__in=['pendiente', 'confirmada', 'en_preparacion', 'lista', 'entregada']
    ).distinct()
    
    print(f"\n🔥 MESAS CON ÓRDENES ACTIVAS ({mesas_con_ordenes.count()}):")
    for mesa in mesas_con_ordenes:
        ordenes_activas = mesa.ordenes_mesero.filter(
            estado__in=['pendiente', 'confirmada', 'en_preparacion', 'lista', 'entregada']
        )
        print(f"  Mesa {mesa.numero} ({mesa.estado}): {ordenes_activas.count()} órdenes activas")
        for orden in ordenes_activas:
            print(f"    - {orden.numero_orden} ({orden.estado})")
    
    # 4. Notificaciones de cuenta pendientes
    print("\n🔔 NOTIFICACIONES DE CUENTA:")
    print("-" * 50)
    
    notificaciones_pendientes = NotificacionCuenta.objects.filter(estado='pendiente')
    print(f"Pendientes: {notificaciones_pendientes.count()}")
    
    for notif in notificaciones_pendientes:
        print(f"  {notif.orden.numero_orden} | Mesa {notif.orden.mesa.numero if notif.orden.mesa else 'N/A'}")
        print(f"    Solicitada: {notif.fecha_creacion.strftime('%d/%m/%Y %H:%M')}")
    
    notificaciones_procesadas = NotificacionCuenta.objects.filter(estado='completada')
    print(f"Completadas: {notificaciones_procesadas.count()}")
    
    # 5. Problemas potenciales
    print("\n⚠️  ANÁLISIS DE PROBLEMAS POTENCIALES:")
    print("-" * 50)
    
    # Mesas ocupadas sin órdenes activas
    mesas_ocupadas_sin_ordenes = Mesa.objects.filter(estado='ocupada').exclude(
        ordenes_mesero__estado__in=['pendiente', 'confirmada', 'en_preparacion', 'lista', 'entregada']
    )
    
    if mesas_ocupadas_sin_ordenes.exists():
        print(f"🚨 {mesas_ocupadas_sin_ordenes.count()} mesas marcadas como ocupadas sin órdenes activas:")
        for mesa in mesas_ocupadas_sin_ordenes:
            print(f"  - Mesa {mesa.numero}")
    else:
        print("✅ No hay mesas ocupadas sin órdenes activas")
    
    # Órdenes sin número de orden (formato antiguo)
    ordenes_sin_formato = Orden.objects.exclude(numero_orden__startswith='ORD-')
    if ordenes_sin_formato.exists():
        print(f"🚨 {ordenes_sin_formato.count()} órdenes con formato de número obsoleto:")
        for orden in ordenes_sin_formato[:5]:  # Mostrar solo 5
            print(f"  - {orden.numero_orden} (ID: {orden.id})")
    else:
        print("✅ Todas las órdenes tienen el formato de número estándar (ORD-YYYYMMDD-NNNN)")
    
    # Cuentas solicitadas pero no procesadas por mucho tiempo
    from datetime import timedelta
    limite_tiempo = timezone.now() - timedelta(hours=2)
    cuentas_antiguas = NotificacionCuenta.objects.filter(
        estado='pendiente',
        fecha_creacion__lt=limite_tiempo
    )
    
    if cuentas_antiguas.exists():
        print(f"🚨 {cuentas_antiguas.count()} cuentas solicitadas hace más de 2 horas sin procesar:")
        for notif in cuentas_antiguas:
            print(f"  - {notif.orden.numero_orden} (solicitada hace {(timezone.now() - notif.fecha_creacion).total_seconds() / 3600:.1f} horas)")
    else:
        print("✅ No hay cuentas pendientes por mucho tiempo")
    
    # 6. Flujo de estados de órdenes
    print("\n📊 FLUJO DE ESTADOS DE ÓRDENES:")
    print("-" * 50)
    print("1. PENDIENTE → Orden creada, esperando confirmación")
    print("2. CONFIRMADA → Orden confirmada, enviada a cocina")
    print("3. EN_PREPARACION → Cocina preparando la orden")
    print("4. LISTA → Orden terminada, lista para entregar")
    print("5. ENTREGADA → Orden entregada al cliente")
    print("6. CUENTA_SOLICITADA → Mesero solicita cuenta")
    print("7. CUENTA_PROCESADA → Cajero procesa pago")
    print("8. CERRADA → Mesa liberada, servicio terminado")
    
    # 7. Resumen del sistema de pagos
    print("\n💳 SISTEMA DE PAGOS:")
    print("-" * 50)
    print("✅ Mesero puede solicitar cuenta cuando orden está LISTA o ENTREGADA")
    print("✅ Se crea NotificacionCuenta para alertar al cajero")
    print("✅ Cajero procesa pago y marca cuenta_procesada=True")
    print("✅ Mesero puede liberar mesa cuando cuenta_procesada=True")
    print("✅ Al liberar mesa, orden pasa a estado CERRADA")
    
    print("\n" + "=" * 80)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("=" * 80)

if __name__ == "__main__":
    verificar_flujo_ordenes()
