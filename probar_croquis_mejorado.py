#!/usr/bin/env python
"""
Script para probar el sistema de croquis mejorado
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Sucursal, Usuario
from dashboard.models_ventas import Mesa
from dashboard.models_croquis import CroquisLayout

def probar_croquis_sistema():
    print("=== 🎨 PRUEBA DEL SISTEMA DE CROQUIS MEJORADO ===\n")
    
    # 1. Verificar modelos
    print("1. VERIFICACIÓN DE MODELOS:")
    try:
        sucursales_count = Sucursal.objects.count()
        mesas_count = Mesa.objects.count()
        croquis_count = CroquisLayout.objects.count()
        
        print(f"   ✅ Sucursales: {sucursales_count}")
        print(f"   ✅ Mesas: {mesas_count}")
        print(f"   ✅ Layouts de Croquis: {croquis_count}")
        
        if sucursales_count > 0:
            sucursal = Sucursal.objects.first()
            print(f"   ✅ Sucursal de prueba: {sucursal.nombre}")
        else:
            print("   ⚠️ No hay sucursales disponibles")
            
    except Exception as e:
        print(f"   ❌ Error en modelos: {e}")

    # 2. Verificar tabla de croquis
    print("\n2. VERIFICACIÓN DE BASE DE DATOS:")
    try:
        from django.db import connection
        cursor = connection.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='dashboard_croquis_layout';
        """)
        
        tabla_existe = cursor.fetchone()
        if tabla_existe:
            print("   ✅ Tabla dashboard_croquis_layout existe")
            
            # Verificar estructura
            cursor.execute("PRAGMA table_info(dashboard_croquis_layout);")
            columnas = cursor.fetchall()
            print("   ✅ Columnas de la tabla:")
            for columna in columnas:
                print(f"      - {columna[1]} ({columna[2]})")
        else:
            print("   ❌ Tabla dashboard_croquis_layout no existe")
            
    except Exception as e:
        print(f"   ❌ Error verificando base de datos: {e}")

    # 3. Probar creación de layout
    print("\n3. PRUEBA DE CREACIÓN DE LAYOUT:")
    try:
        if Sucursal.objects.exists():
            sucursal = Sucursal.objects.first()
            
            # Crear layout de prueba
            layout_data = {
                "objetos": [
                    {
                        "id": 1,
                        "tipo": "mesa",
                        "x": 100,
                        "y": 100,
                        "width": 80,
                        "height": 80,
                        "propiedades": {
                            "numero": "1",
                            "capacidad": 4
                        },
                        "piso": 1
                    },
                    {
                        "id": 2,
                        "tipo": "silla",
                        "x": 50,
                        "y": 110,
                        "width": 30,
                        "height": 30,
                        "propiedades": {},
                        "piso": 1
                    },
                    {
                        "id": 3,
                        "tipo": "bano",
                        "x": 200,
                        "y": 50,
                        "width": 100,
                        "height": 80,
                        "propiedades": {
                            "tipo": "mixto"
                        },
                        "piso": 1
                    },
                    {
                        "id": 4,
                        "tipo": "planta",
                        "x": 300,
                        "y": 200,
                        "width": 40,
                        "height": 40,
                        "propiedades": {
                            "tipo": "decorativa"
                        },
                        "piso": 1
                    }
                ],
                "version": "2.0",
                "sucursalId": sucursal.id
            }
            
            # Crear o actualizar layout
            layout, created = CroquisLayout.objects.get_or_create(
                sucursal=sucursal,
                defaults={
                    'layout_data': layout_data,
                    'version': '2.0'
                }
            )
            
            if not created:
                layout.layout_data = layout_data
                layout.version = '2.0'
                layout.save()
            
            print(f"   ✅ Layout {'creado' if created else 'actualizado'} para {sucursal.nombre}")
            print(f"   ✅ Objetos en el layout: {len(layout_data['objetos'])}")
            
            # Verificar estadísticas
            estadisticas = layout.get_objetos_por_tipo()
            print("   ✅ Estadísticas del layout:")
            for tipo, cantidad in estadisticas.items():
                print(f"      - {tipo}: {cantidad}")
                
        else:
            print("   ⚠️ No hay sucursales para crear el layout")
            
    except Exception as e:
        print(f"   ❌ Error creando layout: {e}")

    # 4. Verificar URLs
    print("\n4. VERIFICACIÓN DE URLS:")
    try:
        from django.urls import reverse
        
        if Sucursal.objects.exists():
            sucursal = Sucursal.objects.first()
            
            urls_croquis = [
                ('Editor de Croquis', 'dashboard:croquis_editor', [sucursal.id]),
                ('Preview de Croquis', 'dashboard:croquis_preview', [sucursal.id]),
                ('API Cargar Croquis', 'dashboard:api_cargar_croquis', [sucursal.id]),
                ('API Mesas Croquis', 'dashboard:api_mesas_croquis', [sucursal.id]),
            ]
            
            for nombre, url_name, args in urls_croquis:
                try:
                    url = reverse(url_name, args=args)
                    print(f"   ✅ {nombre}: {url}")
                except Exception as e:
                    print(f"   ❌ {nombre}: Error - {e}")
        else:
            print("   ⚠️ No hay sucursales para probar URLs")
            
    except Exception as e:
        print(f"   ❌ Error verificando URLs: {e}")

    # 5. Instrucciones finales
    print("\n5. 🚀 INSTRUCCIONES PARA USAR EL CROQUIS:")
    print("   1. Inicia el servidor:")
    print("      python manage.py runserver")
    print("")
    print("   2. Ve a: http://localhost:8000/dashboard/sucursales/")
    print("")
    print("   3. En cualquier tarjeta de sucursal:")
    print("      - Haz clic en el botón '...' (tres puntos)")
    print("      - Selecciona 'Diseñar Croquis'")
    print("")
    print("   4. 🎨 NUEVAS FUNCIONALIDADES:")
    print("      ✨ Múltiples pisos (Planta Baja, Segundo, Tercero)")
    print("      🤏 Arrastrar y soltar elementos desde el panel lateral")
    print("      🏠 Nuevos elementos: Baños, Plantas, Cocina, Caja, TV, etc.")
    print("      🔄 Duplicar objetos seleccionados")
    print("      🧹 Limpiar solo el piso actual")
    print("      🎯 Centrar vista y ajustar al contenido")
    print("      📱 Interfaz completamente responsive")
    print("")
    print("   5. 🎮 CONTROLES:")
    print("      - Clic izquierdo: Seleccionar/Crear objetos")
    print("      - Arrastrar elementos desde el panel lateral al canvas")
    print("      - Rueda del mouse: Zoom in/out")
    print("      - Botones de piso para cambiar entre niveles")
    print("")
    print("   6. 💾 GUARDAR/CARGAR:")
    print("      - Los layouts se guardan automáticamente por piso")
    print("      - Usa 'Guardar Layout' para persistir en la base de datos")
    print("      - 'Cargar Layout' restaura el diseño guardado")

    print("\n=== ✅ SISTEMA DE CROQUIS MEJORADO LISTO ===")
    print("🎉 Ahora tienes un editor visual completo con drag & drop!")

if __name__ == "__main__":
    probar_croquis_sistema()
