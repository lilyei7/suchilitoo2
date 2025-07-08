#!/usr/bin/env python3
"""
Test exhaustivo del editor de croquis - validación de template
"""
import os
import django
import sys

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from accounts.models import Usuario, Sucursal

def test_template_croquis():
    print("🔍 VALIDANDO TEMPLATE DEL EDITOR DE CROQUIS")
    print("=" * 60)
    
    # Setup cliente y login
    client = Client()
    
    # Crear o obtener admin
    try:
        user = Usuario.objects.get(username='admin')
    except Usuario.DoesNotExist:
        user = Usuario.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    
    # Login
    login_success = client.login(username='admin', password='admin123')
    print(f"🔐 Login: {'✅ Exitoso' if login_success else '❌ Fallido'}")
    
    # Obtener sucursal
    sucursal = Sucursal.objects.first()
    if not sucursal:
        sucursal = Sucursal.objects.create(
            nombre='Test Sucursal',
            direccion='Test 123',
            telefono='123456789'
        )
    
    print(f"🏢 Sucursal: {sucursal.nombre} (ID: {sucursal.id})")
    
    # Test del editor de croquis
    print(f"\n📡 Probando: GET /dashboard/croquis/{sucursal.id}/")
    
    try:
        response = client.get(f'/dashboard/croquis/{sucursal.id}/')
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Validaciones críticas
            validaciones = [
                # Template structure
                ('{% extends \'dashboard/base.html\' %}', 'Template extends base'),
                ('{% block content %}', 'Block content abierto'),
                ('{% endblock %}', 'Blocks cerrados'),
                
                # Canvas y elementos principales
                ('croquiCanvas', 'Canvas del editor'),
                ('canvasContainer', 'Container del canvas'),
                
                # JavaScript functions
                ('inicializarCanvas', 'Función inicializar canvas'),
                ('cargarMesasDisponibles', 'Función cargar mesas'),
                ('seleccionarHerramienta', 'Función seleccionar herramienta'),
                ('guardarLayout', 'Función guardar layout'),
                ('cargarLayout', 'Función cargar layout'),
                
                # UI Elements
                ('listaMesas', 'Lista de mesas'),
                ('propiedadesPanel', 'Panel de propiedades'),
                ('tool-seleccionar', 'Herramienta seleccionar'),
                
                # CSRF and security
                ('{% csrf_token %}', 'CSRF Token'),
                ('csrfmiddlewaretoken', 'CSRF Input'),
                
                # Event handlers
                ('onMouseDown', 'Mouse down handler'),
                ('onMouseMove', 'Mouse move handler'),
                ('onMouseUp', 'Mouse up handler'),
                
                # Error handling
                ('showToast', 'Función mostrar notificaciones'),
                ('ajax_login_required', 'Decorador login AJAX')
            ]
            
            print("\n🔎 VALIDACIONES:")
            errores = []
            
            for busqueda, descripcion in validaciones:
                if busqueda in content:
                    print(f"✅ {descripcion}")
                else:
                    print(f"❌ {descripcion} - NO ENCONTRADO")
                    errores.append(descripcion)
            
            # Verificar errores específicos
            print("\n🚨 VERIFICACIÓN DE ERRORES:")
            errores_comunes = [
                ('TemplateDoesNotExist', 'Error de template no existe'),
                ('TemplateSyntaxError', 'Error de sintaxis de template'),
                ('NoReverseMatch', 'Error de URL reverse'),
                ('ReferenceError', 'Error de referencia JavaScript'),
                ('SyntaxError', 'Error de sintaxis'),
                ('Unclosed tag', 'Tag no cerrado'),
                ('endblock', 'Error de endblock')
            ]
            
            for error, descripcion in errores_comunes:
                if error in content:
                    print(f"🚨 {descripcion} - ENCONTRADO")
                    errores.append(descripcion)
                else:
                    print(f"✅ Sin {descripcion}")
            
            # Resumen final
            print(f"\n📋 RESUMEN:")
            print(f"   Template Size: {len(content):,} caracteres")
            print(f"   Errores encontrados: {len(errores)}")
            
            if errores:
                print("\n❌ ERRORES DETECTADOS:")
                for error in errores:
                    print(f"   • {error}")
                return False
            else:
                print("\n✅ TEMPLATE VÁLIDO - TODAS LAS VALIDACIONES PASARON")
                return True
                
        elif response.status_code == 302:
            location = response.get('Location', 'Unknown')
            print(f"🔄 Redirección a: {location}")
            return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            try:
                content = response.content.decode()
                print(f"Contenido del error: {content[:500]}...")
            except:
                pass
            return False
            
    except Exception as e:
        print(f"❌ Excepción: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    resultado = test_template_croquis()
    print(f"\n🏁 RESULTADO FINAL: {'✅ ÉXITO' if resultado else '❌ FALLO'}")
    sys.exit(0 if resultado else 1)
