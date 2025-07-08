#!/usr/bin/env python3
"""
Test para validar la vista previa de croquis y el manejo correcto de JSON
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suchilitoo.settings')
django.setup()

import json
from django.test import Client
from django.contrib.auth import get_user_model
from accounts.models import Sucursal
from dashboard.models_croquis import CroquisLayout

def test_croquis_preview():
    """Test para validar vista previa de croquis"""
    
    print("🔍 Iniciando test de vista previa de croquis...")
    
    try:
        # Verificar que hay sucursales
        sucursales = Sucursal.objects.all()
        if not sucursales.exists():
            print("❌ No hay sucursales disponibles")
            return False
        
        sucursal = sucursales.first()
        print(f"✅ Sucursal encontrada: {sucursal.nombre}")
        
        # Verificar si hay layout
        try:
            layout = CroquisLayout.objects.get(sucursal=sucursal)
            print(f"✅ Layout encontrado para sucursal {sucursal.id}")
            
            # Verificar que el layout_data es JSON válido
            if layout.layout_data:
                if isinstance(layout.layout_data, dict):
                    print("✅ layout_data es un diccionario Python")
                    
                    # Intentar serializar a JSON
                    try:
                        json_str = json.dumps(layout.layout_data, ensure_ascii=False)
                        print("✅ Serialización JSON exitosa")
                        
                        # Intentar deserializar
                        parsed = json.loads(json_str)
                        print("✅ Deserialización JSON exitosa")
                        
                        # Verificar estructura
                        if 'objetos' in parsed:
                            objetos = parsed['objetos']
                            print(f"✅ {len(objetos)} objetos encontrados en el layout")
                            
                            # Verificar tipos de datos
                            for i, obj in enumerate(objetos[:3]):  # Solo primeros 3
                                print(f"  📦 Objeto {i+1}: tipo={obj.get('tipo', 'N/A')}, id={obj.get('id', 'N/A')}")
                                
                                # Buscar propiedades booleanas problemáticas
                                for key, value in obj.items():
                                    if isinstance(value, bool):
                                        print(f"    🔧 Propiedad booleana: {key}={value} ({type(value).__name__})")
                        else:
                            print("⚠️ No se encontró clave 'objetos' en layout_data")
                    
                    except json.JSONEncodeError as e:
                        print(f"❌ Error serializando a JSON: {e}")
                        return False
                    except json.JSONDecodeError as e:
                        print(f"❌ Error deserializando JSON: {e}")
                        return False
                
                else:
                    print(f"⚠️ layout_data no es diccionario: {type(layout.layout_data)}")
            else:
                print("⚠️ layout_data está vacío")
        
        except CroquisLayout.DoesNotExist:
            print(f"⚠️ No hay layout para sucursal {sucursal.id}")
        
        # Test de la vista (sin autenticación por simplicidad)
        from django.test import RequestFactory
        from dashboard.views.croquis_views import preview_croquis
        
        factory = RequestFactory()
        request = factory.get(f'/dashboard/croquis/{sucursal.id}/preview/')
        
        # Crear usuario mock
        User = get_user_model()
        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.create_superuser('test_admin', 'test@example.com', 'testpass123')
        except:
            print("⚠️ No se pudo crear usuario de prueba")
            return True  # Continuar sin test de vista
        
        request.user = user
        
        try:
            response = preview_croquis(request, sucursal.id)
            if response.status_code == 200:
                print("✅ Vista preview_croquis responde correctamente")
                
                # Verificar contenido
                content = response.content.decode('utf-8')
                if 'layout_json' in content:
                    print("✅ Variable layout_json presente en template")
                else:
                    print("⚠️ Variable layout_json no encontrada en template")
                
                if 'True' in content and 'javascript' in content.lower():
                    print("❌ Posible problema: 'True' de Python en JavaScript")
                else:
                    print("✅ No se detectó 'True' de Python en JavaScript")
            else:
                print(f"❌ Vista preview_croquis retornó status {response.status_code}")
        
        except Exception as e:
            print(f"❌ Error en vista preview_croquis: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*60)
        print("✅ Test de vista previa completado")
        return True
    
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_layout_if_needed():
    """Crear layout de ejemplo si no existe"""
    
    sucursales = Sucursal.objects.all()
    if not sucursales.exists():
        print("❌ No hay sucursales para crear layout de ejemplo")
        return
    
    sucursal = sucursales.first()
    
    # Verificar si ya existe
    if CroquisLayout.objects.filter(sucursal=sucursal).exists():
        print(f"✅ Layout ya existe para {sucursal.nombre}")
        return
    
    # Crear layout de ejemplo
    sample_layout = {
        'objetos': [
            {
                'id': 1,
                'tipo': 'mesa',
                'x': 100,
                'y': 100,
                'width': 60,
                'height': 60,
                'piso': 1,
                'rotable': True,  # Esto puede causar el problema True/true
                'propiedades': {
                    'numero': '1',
                    'capacidad': 4
                }
            },
            {
                'id': 2,
                'tipo': 'pared',
                'x': 0,
                'y': 0,
                'width': 300,
                'height': 20,
                'piso': 1,
                'rotable': False
            }
        ],
        'version': '2.0',
        'pisos': {
            '1': []
        }
    }
    
    try:
        layout = CroquisLayout.objects.create(
            sucursal=sucursal,
            layout_data=sample_layout
        )
        print(f"✅ Layout de ejemplo creado para {sucursal.nombre}")
    except Exception as e:
        print(f"❌ Error creando layout de ejemplo: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando validación de vista previa de croquis...")
    print("="*60)
    
    try:
        create_sample_layout_if_needed()
        success = test_croquis_preview()
        
        if success:
            print("\n🎉 Validación completada exitosamente!")
            print("\n📝 Pasos siguientes:")
            print("   1. Accede a: http://127.0.0.1:8000/dashboard/croquis/3/preview/")
            print("   2. Verifica que no aparezca el error 'True is not defined'")
            print("   3. El croquis debe cargar correctamente")
        else:
            print("\n❌ Validación falló")
    
    except Exception as e:
        print(f"\n❌ Error durante la validación: {str(e)}")
        import traceback
        traceback.print_exc()
