#!/usr/bin/env python
"""
Script para probar el Editor de Croquis de Sucursales
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Sucursal, Usuario
from dashboard.models_ventas import Mesa
from dashboard.models_croquis import CroquisLayout
import json

def main():
    print("🎨 === DEMO EDITOR DE CROQUIS ===")
    print()
    
    # Verificar sucursales existentes
    sucursales = Sucursal.objects.all()
    if not sucursales.exists():
        print("❌ No hay sucursales registradas.")
        print("Ejecuta 'crear_sucursal.py' primero para crear sucursales.")
        return
    
    print(f"✅ Encontradas {sucursales.count()} sucursales:")
    for sucursal in sucursales:
        mesas_count = Mesa.objects.filter(sucursal=sucursal).count()
        print(f"   🏢 {sucursal.nombre} - {mesas_count} mesas")
    print()
    
    # Tomar la primera sucursal para demo
    sucursal_demo = sucursales.first()
    print(f"🎯 Usando sucursal de demo: {sucursal_demo.nombre}")
    
    # Verificar mesas de la sucursal
    mesas = Mesa.objects.filter(sucursal=sucursal_demo, activo=True)
    print(f"📋 Mesas disponibles en {sucursal_demo.nombre}:")
    
    if not mesas.exists():
        print("⚠️  No hay mesas registradas. Creando mesas de ejemplo...")
        crear_mesas_ejemplo(sucursal_demo)
        mesas = Mesa.objects.filter(sucursal=sucursal_demo, activo=True)
    
    for mesa in mesas[:5]:  # Mostrar solo las primeras 5
        print(f"   🪑 Mesa {mesa.numero} - {mesa.capacidad} personas - {mesa.estado}")
    
    if mesas.count() > 5:
        print(f"   ... y {mesas.count() - 5} mesas más")
    print()
    
    # Crear layout de ejemplo
    crear_layout_ejemplo(sucursal_demo, mesas)
    
    # Información de uso
    print("🚀 === CÓMO USAR EL EDITOR DE CROQUIS ===")
    print()
    print("1. 📂 Accede al dashboard de sucursales:")
    print("   http://127.0.0.1:8000/dashboard/sucursales/")
    print()
    print("2. 🎨 Para cualquier sucursal, haz clic en el menú '⋮' y selecciona:")
    print("   • 'Diseñar Croquis' - Para abrir el editor")
    print("   • 'Ver Croquis' - Para ver la vista previa")
    print()
    print("3. 🛠️  Herramientas del editor:")
    print("   • Seleccionar - Para mover objetos")
    print("   • Mesa - Agregar mesas al diseño")
    print("   • Pared - Agregar paredes")
    print("   • Puerta - Agregar puertas de entrada")
    print("   • Barra - Agregar barra del bar")
    print()
    print("4. 🔗 Vinculación de mesas:")
    print("   • Al crear una mesa en el croquis, puedes vincularla")
    print("   • con una mesa real de la base de datos")
    print("   • Esto permite asociar el diseño visual con mesas reales")
    print()
    print("5. 💾 Guardar y cargar:")
    print("   • 'Guardar Layout' - Guarda el diseño actual")
    print("   • 'Cargar Layout' - Carga un diseño guardado")
    print()
    print("6. 🔍 Vista previa:")
    print("   • Ver el diseño final sin herramientas de edición")
    print("   • Estadísticas del croquis")
    print("   • Lista de mesas ubicadas")
    print()
    
    # Verificar si ya existe un layout
    try:
        layout_existente = CroquisLayout.objects.get(sucursal=sucursal_demo)
        print("📋 Ya existe un layout guardado para esta sucursal.")
        print(f"   📅 Última actualización: {layout_existente.updated_at.strftime('%d/%m/%Y %H:%M')}")
        print(f"   📊 Objetos en el croquis: {len(layout_existente.layout_data.get('objetos', []))}")
        print()
    except CroquisLayout.DoesNotExist:
        print("📋 Se ha creado un layout de ejemplo para esta sucursal.")
        print()
    
    print("✨ === CARACTERÍSTICAS DEL CROQUIS ===")
    print()
    print("🎨 Editor Visual:")
    print("   • Canvas HTML5 con herramientas drag-and-drop")
    print("   • Zoom y pan para trabajar en detalle")
    print("   • Grid de alineación automática")
    print("   • Selección y edición de propiedades")
    print()
    print("🔧 Objetos Disponibles:")
    print("   • Mesas (cuadradas, redondas, rectangulares)")
    print("   • Paredes y divisiones")
    print("   • Puertas y entradas")
    print("   • Barra del bar")
    print()
    print("📊 Panel de Propiedades:")
    print("   • Posición (X, Y)")
    print("   • Tamaño (ancho, alto)")
    print("   • Propiedades específicas (capacidad, número)")
    print("   • Vinculación con mesas reales")
    print()
    print("💾 Persistencia de Datos:")
    print("   • Layouts guardados en base de datos (JSON)")
    print("   • Versionado de layouts")
    print("   • Validación de integridad de datos")
    print()
    
    print("🎯 === PRÓXIMAS FUNCIONALIDADES ===")
    print()
    print("🔮 Funciones Avanzadas (Futuras):")
    print("   • Múltiples layouts por sucursal")
    print("   • Plantillas predefinidas de diseños")
    print("   • Exportar a PDF/imagen")
    print("   • Modo colaborativo en tiempo real")
    print("   • Integración con reservas")
    print()
    
    print("🌐 === ENLACES DIRECTOS ===")
    print()
    print(f"📊 Dashboard Principal: http://127.0.0.1:8000/dashboard/")
    print(f"🏢 Gestión Sucursales: http://127.0.0.1:8000/dashboard/sucursales/")
    print(f"🎨 Editor de Croquis: http://127.0.0.1:8000/dashboard/sucursales/{sucursal_demo.id}/croquis/")
    print(f"👁️  Vista Previa: http://127.0.0.1:8000/dashboard/sucursales/{sucursal_demo.id}/croquis/preview/")
    print()

def crear_mesas_ejemplo(sucursal):
    """Crear mesas de ejemplo para la sucursal"""
    mesas_ejemplo = [
        {"numero": "M01", "capacidad": 2, "estado": "disponible", "nombre": "Terraza A"},
        {"numero": "M02", "capacidad": 4, "estado": "disponible", "nombre": "Sala Principal"},
        {"numero": "M03", "capacidad": 4, "estado": "ocupada", "nombre": "Sala Principal"},
        {"numero": "M04", "capacidad": 6, "estado": "disponible", "nombre": "Salon VIP"},
        {"numero": "M05", "capacidad": 2, "estado": "reservada", "nombre": "Terraza B"},
        {"numero": "M06", "capacidad": 8, "estado": "disponible", "nombre": "Salon Familiar"},
        {"numero": "B01", "capacidad": 10, "estado": "disponible", "nombre": "Barra Principal"},
    ]
    
    for mesa_data in mesas_ejemplo:
        Mesa.objects.get_or_create(
            numero=mesa_data["numero"],
            sucursal=sucursal,
            defaults={
                "capacidad": mesa_data["capacidad"],
                "estado": mesa_data["estado"],
                "nombre": mesa_data["nombre"],
                "activo": True
            }
        )
    
    print(f"✅ Creadas {len(mesas_ejemplo)} mesas de ejemplo")

def crear_layout_ejemplo(sucursal, mesas):
    """Crear un layout de ejemplo si no existe"""
    
    # Verificar si ya existe
    if CroquisLayout.objects.filter(sucursal=sucursal).exists():
        return
    
    # Crear objetos de ejemplo
    objetos_ejemplo = [
        # Paredes del restaurante
        {
            "id": 1,
            "tipo": "pared",
            "x": 50,
            "y": 50,
            "width": 400,
            "height": 20,
            "color": "#6c757d",
            "propiedades": {}
        },
        {
            "id": 2,
            "tipo": "pared",
            "x": 50,
            "y": 50,
            "width": 20,
            "height": 300,
            "color": "#6c757d",
            "propiedades": {}
        },
        {
            "id": 3,
            "tipo": "pared",
            "x": 450,
            "y": 50,
            "width": 20,
            "height": 300,
            "color": "#6c757d",
            "propiedades": {}
        },
        {
            "id": 4,
            "tipo": "pared",
            "x": 50,
            "y": 350,
            "width": 420,
            "height": 20,
            "color": "#6c757d",
            "propiedades": {}
        },
        
        # Puerta de entrada
        {
            "id": 5,
            "tipo": "puerta",
            "x": 200,
            "y": 350,
            "width": 80,
            "height": 20,
            "color": "#ffc107",
            "propiedades": {}
        },
        
        # Barra
        {
            "id": 6,
            "tipo": "barra",
            "x": 350,
            "y": 100,
            "width": 80,
            "height": 150,
            "color": "#fd7e14",
            "propiedades": {}
        }
    ]
    
    # Agregar mesas vinculadas
    mesa_positions = [
        (120, 120), (220, 120), (120, 200), (220, 200),
        (120, 280), (320, 280), (280, 150)
    ]
    
    for i, mesa in enumerate(mesas[:len(mesa_positions)]):
        x, y = mesa_positions[i]
        objetos_ejemplo.append({
            "id": 10 + i,
            "tipo": "mesa",
            "x": x,
            "y": y,
            "width": 60,
            "height": 60,
            "color": "#28a745",
            "mesaId": mesa.id,
            "propiedades": {
                "numero": mesa.numero,
                "capacidad": mesa.capacidad,
                "forma": "cuadrada"
            }
        })
    
    # Crear layout
    layout_data = {
        "sucursalId": sucursal.id,
        "objetos": objetos_ejemplo,
        "version": "1.0",
        "fechaCreacion": "2025-07-03T10:00:00Z"
    }
    
    CroquisLayout.objects.create(
        sucursal=sucursal,
        layout_data=layout_data,
        version="1.0"
    )
    
    print(f"✅ Layout de ejemplo creado con {len(objetos_ejemplo)} objetos")

if __name__ == '__main__':
    main()
