#!/usr/bin/env python3
"""
Script para integrar el sistema de inventario automático con las vistas del mesero.
Actualiza la vista crear_orden para incluir el descuento automático de inventario.
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def actualizar_vista_crear_orden():
    """
    Actualiza la vista crear_orden para incluir el descuento automático de inventario
    """
    
    # Leer el archivo actual
    views_path = r'c:\Users\olcha\Desktop\sushi_restaurant - Copy (2)\suchilitoo2\mesero\views.py'
    
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Agregar el import del inventario automático al inicio del archivo
    import_line = "from inventario_automatico import InventarioAutomatico"
    
    if import_line not in content:
        # Encontrar la línea donde están los imports
        lines = content.split('\n')
        import_index = -1
        
        for i, line in enumerate(lines):
            if 'import json' in line:
                import_index = i
                break
        
        if import_index != -1:
            lines.insert(import_index + 1, import_line)
            content = '\n'.join(lines)
            print("✅ Agregado import del inventario automático")
        else:
            print("❌ No se pudo encontrar la línea de imports")
    
    # Buscar y reemplazar la función crear_orden
    start_marker = "@login_required\n@csrf_exempt\ndef crear_orden(request):"
    end_marker = "return JsonResponse({'success': False, 'error': 'Método no permitido'})"
    
    start_index = content.find(start_marker)
    end_index = content.find(end_marker, start_index)
    
    if start_index != -1 and end_index != -1:
        # Encontrar el final de la función
        end_index = content.find('\n', end_index + len(end_marker))
        
        new_function = '''@login_required
@csrf_exempt
def crear_orden(request):
    """Vista AJAX para crear una nueva orden desde el menú con descuento automático de inventario"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mesa_id = data.get('mesa_id')
            items = data.get('items', [])
            notas = data.get('notas', '')
            
            if not mesa_id:
                return JsonResponse({
                    'success': False, 
                    'error': 'Debe seleccionar una mesa'
                })
            
            if not items:
                return JsonResponse({
                    'success': False, 
                    'error': 'Debe agregar al menos un producto'
                })
            
            # Verificar que el usuario tenga sucursal asignada
            if not request.user.sucursal:
                return JsonResponse({
                    'success': False, 
                    'error': 'Usuario sin sucursal asignada'
                })
            
            # Obtener y validar la mesa
            try:
                mesa = Mesa.objects.get(
                    id=mesa_id,
                    sucursal=request.user.sucursal,
                    activa=True
                )
            except Mesa.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'error': 'Mesa no encontrada o no pertenece a tu sucursal'
                })
            
            # 🆕 VERIFICAR STOCK DISPONIBLE ANTES DE CREAR LA ORDEN
            inventario_automatico = InventarioAutomatico(request.user.sucursal)
            
            # Verificar stock para cada item
            stock_faltante = []
            for item_data in items:
                producto = get_object_or_404(ProductoVenta, id=item_data['id'])
                cantidad = int(item_data['cantidad'])
                
                # Verificar stock disponible
                stock_ok, faltantes = inventario_automatico.verificar_stock_disponible(producto, cantidad)
                
                if not stock_ok:
                    stock_faltante.extend([
                        {
                            'producto': producto.nombre,
                            'cantidad_solicitada': cantidad,
                            'faltantes': faltantes
                        }
                    ])
            
            # Si hay stock faltante, retornar error
            if stock_faltante:
                error_msg = "Stock insuficiente para los siguientes productos:\\n"
                for faltante in stock_faltante:
                    error_msg += f"• {faltante['producto']} (cantidad: {faltante['cantidad_solicitada']})\\n"
                    for item in faltante['faltantes']:
                        if 'error' in item:
                            error_msg += f"  - Error: {item['error']}\\n"
                        else:
                            error_msg += f"  - {item['insumo']}: necesario {item['necesario']} {item['unidad']}, disponible {item['disponible']} {item['unidad']}\\n"
                
                return JsonResponse({
                    'success': False,
                    'error': error_msg,
                    'stock_faltante': stock_faltante
                })
            
            # Crear la orden
            orden = Orden.objects.create(
                mesa=mesa,
                mesero=request.user,
                estado='pendiente',
                observaciones=notas
            )
            
            # Agregar los items a la orden
            total = 0
            for item_data in items:
                producto = get_object_or_404(ProductoVenta, id=item_data['id'])
                cantidad = int(item_data['cantidad'])
                precio_unitario = producto.precio
                
                # Calcular precio extra por personalizaciones
                precio_extra_personalizaciones = 0
                personalizaciones = item_data.get('personalizaciones', [])
                
                if personalizaciones:
                    from .models import OpcionPersonalizacion
                    for personalizacion_id in personalizaciones:
                        try:
                            opcion = OpcionPersonalizacion.objects.get(id=personalizacion_id, activa=True)
                            precio_extra_personalizaciones += opcion.precio_extra
                        except OpcionPersonalizacion.DoesNotExist:
                            continue
                
                # Precio final por unidad incluyendo personalizaciones
                precio_final_unitario = precio_unitario + precio_extra_personalizaciones
                
                # Crear el item de orden
                orden_item = OrdenItem.objects.create(
                    orden=orden,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_final_unitario,
                    observaciones=item_data.get('observaciones', '')  # Agregar las observaciones del producto
                )
                
                # Guardar las personalizaciones del item
                if personalizaciones:
                    from .models import OpcionPersonalizacion, OrdenItemPersonalizacion
                    for personalizacion_id in personalizaciones:
                        try:
                            opcion = OpcionPersonalizacion.objects.get(id=personalizacion_id, activa=True)
                            OrdenItemPersonalizacion.objects.create(
                                orden_item=orden_item,
                                opcion=opcion,
                                precio_aplicado=opcion.precio_extra
                            )
                        except OpcionPersonalizacion.DoesNotExist:
                            continue
                
                total += orden_item.calcular_subtotal()
            
            # Actualizar el total de la orden
            orden.total = total
            orden.save()
            
            # 🆕 DESCONTAR INVENTARIO AUTOMÁTICAMENTE
            try:
                inventario_success, inventario_messages = inventario_automatico.procesar_orden(orden)
                
                if not inventario_success:
                    # Si falla el descuento de inventario, eliminar la orden
                    orden.delete()
                    return JsonResponse({
                        'success': False,
                        'error': 'Error al descontar inventario: ' + '\\n'.join(inventario_messages[-3:])
                    })
                
                # Log del inventario para debugging
                print(f"📦 Inventario descontado para orden #{orden.numero_orden}")
                for msg in inventario_messages:
                    print(f"  {msg}")
                    
            except Exception as e:
                # Si falla el descuento de inventario, eliminar la orden
                orden.delete()
                return JsonResponse({
                    'success': False,
                    'error': f'Error al procesar inventario: {str(e)}'
                })
            
            # Actualizar el estado de la mesa
            mesa.estado = 'ocupada'
            mesa.save()
            
            # Crear historial
            HistorialOrden.objects.create(
                orden=orden,
                estado_anterior='',
                estado_nuevo='pendiente',
                usuario=request.user,
                observaciones=f'Orden creada con {len(items)} items - Inventario descontado automáticamente'
            )
            
            return JsonResponse({
                'success': True,
                'orden_id': orden.id,
                'mesa_numero': mesa.numero,
                'total': float(total),
                'message': f'Orden creada exitosamente para Mesa #{mesa.numero}\\nInventario actualizado automáticamente',
                'inventario_info': inventario_messages[-5:] if len(inventario_messages) > 5 else inventario_messages
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f'Error al crear la orden: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})'''
        
        # Reemplazar la función
        new_content = content[:start_index] + new_function + content[end_index:]
        
        # Guardar el archivo
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Vista crear_orden actualizada con inventario automático")
        
        # Crear backup
        backup_path = views_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"💾 Backup creado en: {backup_path}")
        
    else:
        print("❌ No se pudo encontrar la función crear_orden")

def crear_vista_inventario_status():
    """
    Crea una nueva vista para mostrar el estado del inventario
    """
    
    nueva_vista = '''

@login_required
def inventario_status(request):
    """Vista para mostrar el estado del inventario"""
    if not request.user.sucursal:
        messages.error(request, 'Usuario sin sucursal asignada')
        return redirect('mesero:dashboard')
    
    # Obtener inventario con stock bajo
    from restaurant.models import Inventario, Insumo
    
    inventarios = Inventario.objects.filter(
        sucursal=request.user.sucursal
    ).select_related('insumo').order_by('insumo__nombre')
    
    # Identificar productos con stock bajo
    stock_bajo = []
    stock_critico = []
    
    for inventario in inventarios:
        porcentaje_stock = 0
        if inventario.insumo.stock_minimo > 0:
            porcentaje_stock = (inventario.cantidad_disponible / inventario.insumo.stock_minimo) * 100
        
        if inventario.cantidad_disponible <= inventario.insumo.stock_minimo:
            if inventario.cantidad_disponible <= (inventario.insumo.stock_minimo * 0.5):
                stock_critico.append({
                    'inventario': inventario,
                    'porcentaje': porcentaje_stock
                })
            else:
                stock_bajo.append({
                    'inventario': inventario,
                    'porcentaje': porcentaje_stock
                })
    
    # Obtener movimientos recientes
    from restaurant.models import MovimientoInventario
    
    movimientos_recientes = MovimientoInventario.objects.filter(
        sucursal=request.user.sucursal
    ).select_related('insumo').order_by('-created_at')[:10]
    
    context = {
        'inventarios': inventarios,
        'stock_bajo': stock_bajo,
        'stock_critico': stock_critico,
        'movimientos_recientes': movimientos_recientes,
        'total_inventarios': inventarios.count(),
        'total_stock_bajo': len(stock_bajo),
        'total_stock_critico': len(stock_critico),
    }
    
    return render(request, 'mesero/inventario_status.html', context)

@login_required
def verificar_stock_producto(request, producto_id):
    """Vista AJAX para verificar stock de un producto específico"""
    if not request.user.sucursal:
        return JsonResponse({
            'success': False,
            'error': 'Usuario sin sucursal asignada'
        })
    
    try:
        from inventario_automatico import InventarioAutomatico
        
        producto = get_object_or_404(ProductoVenta, id=producto_id)
        cantidad = int(request.GET.get('cantidad', 1))
        
        inventario_automatico = InventarioAutomatico(request.user.sucursal)
        stock_ok, faltantes = inventario_automatico.verificar_stock_disponible(producto, cantidad)
        
        return JsonResponse({
            'success': True,
            'stock_ok': stock_ok,
            'faltantes': faltantes,
            'producto': producto.nombre,
            'cantidad': cantidad
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })'''
    
    # Agregar la nueva vista al archivo
    views_path = r'c:\Users\olcha\Desktop\sushi_restaurant - Copy (2)\suchilitoo2\mesero\views.py'
    
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Agregar al final del archivo
    if 'def inventario_status(request):' not in content:
        content += nueva_vista
        
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Vista inventario_status agregada")
    else:
        print("ℹ️  Vista inventario_status ya existe")

def actualizar_urls():
    """
    Actualiza las URLs para incluir las nuevas vistas de inventario
    """
    
    urls_path = r'c:\Users\olcha\Desktop\sushi_restaurant - Copy (2)\suchilitoo2\mesero\urls.py'
    
    with open(urls_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Agregar las nuevas URLs
    new_urls = '''    # URLs para inventario
    path('inventario/status/', views.inventario_status, name='inventario_status'),
    path('inventario/verificar-stock/<int:producto_id>/', views.verificar_stock_producto, name='verificar_stock_producto'),
'''
    
    if 'inventario_status' not in content:
        # Encontrar donde insertar las URLs
        if 'urlpatterns = [' in content:
            insert_index = content.find('urlpatterns = [') + len('urlpatterns = [')
            content = content[:insert_index] + '\\n' + new_urls + content[insert_index:]
            
            with open(urls_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ URLs de inventario agregadas")
        else:
            print("❌ No se pudo encontrar urlpatterns")
    else:
        print("ℹ️  URLs de inventario ya existen")

if __name__ == "__main__":
    print("🔧 Integrando sistema de inventario automático...")
    print("=" * 50)
    
    actualizar_vista_crear_orden()
    crear_vista_inventario_status()
    actualizar_urls()
    
    print("=" * 50)
    print("✅ Integración completada")
    print("\\nPróximos pasos:")
    print("1. Ejecutar el script inventario_automatico.py para probar el sistema")
    print("2. Crear plantilla HTML para inventario_status.html")
    print("3. Agregar alertas de stock bajo en el dashboard")
    print("4. Probar el sistema con una orden real")
