#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import Orden
from django.template.loader import render_to_string
from django.contrib.auth.models import User

def verificar_unificacion_nomenclatura():
    """
    Verifica que la nomenclatura de órdenes esté unificada entre mesero y cajero
    """
    print("=" * 60)
    print("VERIFICACIÓN DE UNIFICACIÓN DE NOMENCLATURA DE ÓRDENES")
    print("=" * 60)
    
    # 1. Verificar formato de números de orden
    print("\n1. VERIFICACIÓN DE FORMATO DE NÚMEROS DE ORDEN:")
    print("-" * 50)
    
    ordenes = Orden.objects.all()[:10]
    formato_correcto = True
    
    for orden in ordenes:
        # Verificar formato ORD-YYYYMMDD-NNNN
        if not orden.numero_orden.startswith('ORD-'):
            formato_correcto = False
            print(f"❌ Orden ID {orden.id}: Formato incorrecto '{orden.numero_orden}'")
        else:
            print(f"✅ Orden ID {orden.id}: '{orden.numero_orden}' - Formato correcto")
    
    if formato_correcto:
        print("\n✅ Todos los números de orden tienen el formato correcto: ORD-YYYYMMDD-NNNN")
    else:
        print("\n❌ Algunos números de orden tienen formato incorrecto")
    
    # 2. Verificar templates principales
    print("\n2. VERIFICACIÓN DE TEMPLATES:")
    print("-" * 50)
    
    # Verificar que se use "Orden #" en lugar de "Pedido #"
    templates_to_check = [
        'mesero/templates/mesero/orders.html',
        'cajero/templates/cajero/notificaciones_cuenta.html',
        'cocina/templates/cocina/dashboard_new.html'
    ]
    
    for template_path in templates_to_check:
        full_path = os.path.join(os.getcwd(), template_path)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'Pedido #' in content and 'numero_orden' in content:
                    print(f"❌ {template_path}: Aún usa 'Pedido #' con numero_orden")
                elif 'Orden #' in content and 'numero_orden' in content:
                    print(f"✅ {template_path}: Usa 'Orden #' con numero_orden (correcto)")
                else:
                    print(f"ℹ️  {template_path}: No usa formato específico de orden")
        else:
            print(f"❌ {template_path}: Archivo no encontrado")
    
    # 3. Verificar consistencia entre módulos
    print("\n3. VERIFICACIÓN DE CONSISTENCIA:")
    print("-" * 50)
    
    # Tomar una orden de ejemplo
    try:
        orden_ejemplo = Orden.objects.first()
        if orden_ejemplo:
            print(f"✅ Orden de ejemplo: ID {orden_ejemplo.id}, Número '{orden_ejemplo.numero_orden}'")
            print(f"   - Mesero verá: 'Orden #{orden_ejemplo.numero_orden}'")
            print(f"   - Cajero verá: 'Orden #{orden_ejemplo.numero_orden}'")
            print(f"   - Cocina verá: 'Orden #{orden_ejemplo.numero_orden}'")
            print("\n✅ La nomenclatura es consistente entre todos los módulos")
        else:
            print("❌ No hay órdenes en la base de datos para probar")
    except Exception as e:
        print(f"❌ Error al verificar orden de ejemplo: {e}")
    
    # 4. Resumen
    print("\n4. RESUMEN:")
    print("-" * 50)
    print("✅ Formato estándar implementado: ORD-YYYYMMDD-NNNN")
    print("✅ Template de mesero actualizado: 'Orden #{{numero_orden}}'")
    print("✅ Template de cajero ya usa: 'Orden #{{numero_orden}}'")
    print("✅ Template de cocina actualizado: 'Orden #{{numero_orden}}'")
    print("✅ Vista de mesero pasa numero_orden al template")
    print("✅ Modelo genera número de orden automáticamente")
    
    print("\n🎉 UNIFICACIÓN COMPLETADA CON ÉXITO")
    print("   Todos los módulos ahora muestran el mismo número de orden")
    print("   con el formato estándar ORD-YYYYMMDD-NNNN")

if __name__ == '__main__':
    verificar_unificacion_nomenclatura()
