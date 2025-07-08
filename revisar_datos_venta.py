import os
import django
import sys
from decimal import Decimal
from collections import defaultdict

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from restaurant.models import ProductoVenta
from dashboard.models_ventas import Venta, DetalleVenta
from dashboard.models import Mesa, Cliente
from accounts.models import Sucursal
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta

def revisar_datos_venta():
    print("\n=== ANÁLISIS DE DATOS DE VENTA ===")
    print("=" * 40)
    
    # 1. Conteo general
    total_ventas = Venta.objects.count()
    total_productos = ProductoVenta.objects.count()
    productos_activos = ProductoVenta.objects.filter(disponible=True).count()
    
    print(f"\n1. RESUMEN GENERAL")
    print(f"Total de ventas registradas: {total_ventas}")
    print(f"Total de productos: {total_productos}")
    print(f"Productos activos: {productos_activos}")
    
    # 2. Ventas por sucursal
    print("\n2. VENTAS POR SUCURSAL")
    ventas_sucursal = Venta.objects.values('sucursal__nombre').annotate(
        total_ventas=Count('id'),
        monto_total=Sum('total')
    )
    
    for venta in ventas_sucursal:
        print(f"Sucursal: {venta['sucursal__nombre']}")
        print(f"  - Número de ventas: {venta['total_ventas']}")
        print(f"  - Monto total: ${venta['monto_total']:.2f}")
    
    # 3. Productos más vendidos
    print("\n3. PRODUCTOS MÁS VENDIDOS")
    productos_vendidos = DetalleVenta.objects.values(
        'producto__nombre'
    ).annotate(
        cantidad_total=Sum('cantidad'),
        ingreso_total=Sum('precio_total')
    ).order_by('-cantidad_total')[:5]
    
    for producto in productos_vendidos:
        print(f"Producto: {producto['producto__nombre']}")
        print(f"  - Cantidad vendida: {producto['cantidad_total']}")
        print(f"  - Ingreso total: ${producto['ingreso_total']:.2f}")
    
    # 4. Ventas recientes
    print("\n4. VENTAS RECIENTES (Últimas 24 horas)")
    ventas_recientes = Venta.objects.filter(
        fecha_hora__gte=timezone.now() - timedelta(days=1)
    ).order_by('-fecha_hora')[:5]
    
    for venta in ventas_recientes:
        print(f"Venta #{venta.id}")
        print(f"  - Fecha: {venta.fecha_hora.strftime('%Y-%m-%d %H:%M')}")
        print(f"  - Total: ${venta.total:.2f}")
        print(f"  - Sucursal: {venta.sucursal.nombre}")
    
    # 5. Estado de productos
    print("\n5. ESTADO DE PRODUCTOS")
    productos_stats = {
        'total': ProductoVenta.objects.count(),
        'activos': ProductoVenta.objects.filter(disponible=True).count(),
        'inactivos': ProductoVenta.objects.filter(disponible=False).count(),
        'sin_ventas': ProductoVenta.objects.filter(detalleventa=None).count()
    }
    
    print(f"Total de productos: {productos_stats['total']}")
    print(f"  - Productos activos: {productos_stats['activos']}")
    print(f"  - Productos inactivos: {productos_stats['inactivos']}")
    print(f"  - Productos sin ventas: {productos_stats['sin_ventas']}")
    
    # 6. Promedio de ventas
    print("\n6. PROMEDIO DE VENTAS")
    promedio_venta = Venta.objects.aggregate(
        promedio=Avg('total')
    )['promedio'] or 0
    
    print(f"Promedio por venta: ${promedio_venta:.2f}")

if __name__ == '__main__':
    try:
        revisar_datos_venta()
    except Exception as e:
        print(f"\nError al revisar los datos: {str(e)}")
    finally:
        print("\n=== FIN DEL ANÁLISIS ===")
