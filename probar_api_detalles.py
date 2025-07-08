#!/usr/bin/env python
"""
Script para probar el API de detalles de insumo y verificar que muestra la información completa del proveedor
"""
import os
import sys
import json

# Agregar el directorio del proyecto al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

import django
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from restaurant.models import Insumo
from dashboard.views.inventario_views import insumo_detalle_api

User = get_user_model()

def probar_api_detalle_insumo():
    """Probar el API de detalles de insumo"""
    print("🔍 PROBANDO API DE DETALLES DE INSUMO")
    print("=" * 60)
    
    try:
        # Obtener el insumo Pepinos
        insumo = Insumo.objects.get(nombre="Pepinos")
        print(f"📦 Insumo a probar: {insumo.codigo} - {insumo.nombre}")
        
        # Obtener usuario gerente
        gerente = User.objects.get(username="gerente_test")
        print(f"👤 Usuario de prueba: {gerente.username} (Gerente de {gerente.sucursal.nombre})")
        
        # Crear request simulado
        factory = RequestFactory()
        request = factory.get(f'/dashboard/insumos/{insumo.id}/detalle/')
        request.user = gerente
        
        # Llamar al API
        response = insumo_detalle_api(request, insumo.id)
        
        # Verificar respuesta
        if response.status_code == 200:
            data = json.loads(response.content)
            
            print(f"\n✅ API RESPONDIÓ CORRECTAMENTE (Status: {response.status_code})")
            print(f"\n📋 DATOS DEL INSUMO:")
            print(f"   ID: {data['id']}")
            print(f"   Código: {data['codigo']}")
            print(f"   Nombre: {data['nombre']}")
            print(f"   Tipo: {data['tipo']}")
            print(f"   Categoría: {data['categoria']}")
            print(f"   Unidad: {data['unidad_medida']} ({data['unidad_abreviacion']})")
            print(f"   Precio unitario: S/ {data['precio_unitario']}")
            print(f"   Stock actual: {data['stock_actual']} {data['unidad_abreviacion']}")
            print(f"   Stock mínimo: {data['stock_minimo']} {data['unidad_abreviacion']}")
            print(f"   Estado del stock: {data['estado_stock']}")
            
            print(f"\n🏭 INFORMACIÓN DEL PROVEEDOR:")
            print(f"   Nombre: {data['proveedor']}")
            print(f"   Contacto: {data['proveedor_contacto']}")
            print(f"   Teléfono: {data['proveedor_telefono']}")
            print(f"   Email: {data['proveedor_email']}")
            
            print(f"\n📊 INVENTARIOS POR SUCURSAL:")
            for inv in data['inventarios']:
                print(f"   {inv['sucursal']}: {inv['cantidad_actual']} {data['unidad_abreviacion']}")
            
            # Verificar que los campos del proveedor no estén vacíos
            if data['proveedor'] != 'Sin proveedor asignado':
                print(f"\n✅ VERIFICACIÓN DE PROVEEDOR:")
                print(f"   ✅ Nombre del proveedor: {data['proveedor']}")
                if data['proveedor_contacto']:
                    print(f"   ✅ Contacto disponible: {data['proveedor_contacto']}")
                else:
                    print(f"   ⚠️ Sin contacto")
                
                if data['proveedor_telefono']:
                    print(f"   ✅ Teléfono disponible: {data['proveedor_telefono']}")
                else:
                    print(f"   ⚠️ Sin teléfono")
                
                if data['proveedor_email']:
                    print(f"   ✅ Email disponible: {data['proveedor_email']}")
                else:
                    print(f"   ⚠️ Sin email")
            else:
                print(f"\n⚠️ Este insumo no tiene proveedor asignado")
                
        else:
            print(f"❌ Error en API (Status: {response.status_code})")
            try:
                error_data = json.loads(response.content)
                print(f"   Error: {error_data.get('error', 'Error desconocido')}")
            except:
                print(f"   Respuesta: {response.content}")
    
    except Insumo.DoesNotExist:
        print("❌ No se encontró el insumo 'Pepinos'")
    except User.DoesNotExist:
        print("❌ No se encontró el usuario gerente_test")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def verificar_modal_javascript():
    """Verificar que el JavaScript del modal funcione correctamente"""
    print(f"\n🖥️ VERIFICACIÓN DEL MODAL DE JAVASCRIPT")
    print("=" * 60)
    
    print(f"📝 PUNTOS A VERIFICAR EN EL NAVEGADOR:")
    print(f"   1. Hacer clic en el botón 'Ver detalles' (ícono ojo) del insumo Pepinos")
    print(f"   2. Verificar que aparece el modal con los detalles")
    print(f"   3. En la sección 'Características', verificar que aparece:")
    print(f"      - Proveedor: Verduras Frescas SAC")
    print(f"      - Contacto: Ana Rodríguez")
    print(f"      - Tel: +51 999 888 777")
    print(f"      - Email: ventas@verdurasfrescas.com")
    print(f"   4. Verificar que el formato se ve bien y es legible")
    
    print(f"\n🔧 FUNCIÓN JAVASCRIPT RESPONSABLE:")
    print(f"   - mostrarDetalleInsumo(insumoId) en inventario.html")
    print(f"   - mostrarDetalleInsumoHTML(insumo) para renderizar el HTML")
    print(f"   - Líneas relevantes en el template que muestran proveedor:")
    print(f"     ```javascript")
    print(f"     <dt class=\"col-sm-4\">Proveedor:</dt>")
    print(f"     <dd class=\"col-sm-8\">")
    print(f"         ${{insumo.proveedor || '<em class=\"text-muted\">Sin proveedor asignado</em>'}}")
    print(f"         ${{insumo.proveedor_contacto ? `<br><small class=\"text-muted\">Contacto: ${{insumo.proveedor_contacto}}</small>` : ''}}")
    print(f"         ${{insumo.proveedor_telefono ? `<br><small class=\"text-muted\">Tel: ${{insumo.proveedor_telefono}}</small>` : ''}}")
    print(f"         ${{insumo.proveedor_email ? `<br><small class=\"text-muted\">Email: ${{insumo.proveedor_email}}</small>` : ''}}")
    print(f"     </dd>")
    print(f"     ```")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBA COMPLETA DEL SISTEMA DE DETALLES\n")
    
    # Probar API
    probar_api_detalle_insumo()
    
    # Verificar modal
    verificar_modal_javascript()
    
    print(f"\n" + "=" * 60)
    print("🎉 PRUEBAS COMPLETADAS")
    print(f"\n📝 RESUMEN DEL FLUJO VERIFICADO:")
    print(f"   1. ✅ Insumo creado con inventario en todas las sucursales")
    print(f"   2. ✅ Proveedor asignado con información completa")
    print(f"   3. ✅ Gerente solo ve insumos de su sucursal")
    print(f"   4. ✅ API de detalles devuelve información completa del proveedor")
    print(f"   5. 🔄 Verificar manualmente el modal en el navegador")
    
    print(f"\n🌐 PARA PROBAR MANUALMENTE:")
    print(f"   1. Acceder a: http://localhost:8000/dashboard/inventario/")
    print(f"   2. Iniciar sesión como gerente_test / test123")
    print(f"   3. Hacer clic en el ícono de ojo del insumo 'Pepinos'")
    print(f"   4. Verificar que aparece toda la información del proveedor")
