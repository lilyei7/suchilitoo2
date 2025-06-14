#!/usr/bin/env python
"""
Script de diagnóstico completo del sistema.
Este script ejecuta pruebas en diferentes módulos para verificar que todo esté funcionando correctamente.
"""
import os
import sys
import django
import json
from datetime import datetime

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth import get_user_model
from django.template.loader import get_template, TemplateDoesNotExist
from accounts.models import Usuario, Rol, Sucursal
from restaurant.models import Insumo, Categoria, UnidadMedida

# Colores para la consola
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD} {text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")

def print_subheader(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD} {text}{Colors.ENDC}")
    print(f"{Colors.BLUE}{'-' * 40}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️ {text}{Colors.ENDC}")

def test_template_loading():
    """Prueba la carga de plantillas"""
    print_subheader("PRUEBA DE CARGA DE TEMPLATES")
    
    templates_to_test = [
        'dashboard/base.html',
        'dashboard/login.html',
        'dashboard/usuarios.html',
        'dashboard/sucursales.html',
        'dashboard/insumos_elaborados.html',
        'dashboard/modals/gestionar_categorias.html',
        'dashboard/modals/gestionar_unidades.html',
    ]
    
    success_count = 0
    for template_name in templates_to_test:
        try:
            template = get_template(template_name)
            print_success(f"{template_name}")
            success_count += 1
        except TemplateDoesNotExist as e:
            print_error(f"{template_name} - No encontrado: {str(e)}")
        except Exception as e:
            print_warning(f"{template_name} - Error: {str(e)}")
    
    return success_count, len(templates_to_test)

def test_models():
    """Prueba la disponibilidad y conteo de modelos"""
    print_subheader("PRUEBA DE MODELOS")
    
    models_to_test = [
        (Usuario, "Usuarios"),
        (Rol, "Roles"),
        (Sucursal, "Sucursales"),
        (Insumo, "Insumos"),
        (Categoria, "Categorías"),
        (UnidadMedida, "Unidades de Medida")
    ]
    
    for model, name in models_to_test:
        try:
            count = model.objects.count()
            if count > 0:
                print_success(f"{name}: {count} registros")
            else:
                print_warning(f"{name}: No hay registros")
        except Exception as e:
            print_error(f"{name}: Error - {str(e)}")

def test_login():
    """Prueba el inicio de sesión"""
    print_subheader("PRUEBA DE LOGIN")
    
    client = Client()
    User = get_user_model()
    
    # Verificar si existe el usuario admin
    if User.objects.filter(username='admin').exists():
        # Intentar login con credenciales correctas
        try:
            login_success = client.login(username='admin', password='admin123456')
            if login_success:
                print_success("Login exitoso con credenciales admin/admin123456")
            else:
                print_error("Login fallido con credenciales admin/admin123456")
        except Exception as e:
            print_error(f"Error en proceso de login: {str(e)}")
    else:
        print_error("Usuario admin no existe")
    
    return client if 'login_success' in locals() and login_success else None

def test_api_endpoints(client):
    """Prueba los endpoints de la API"""
    print_subheader("PRUEBA DE ENDPOINTS API")
    
    if not client:
        print_warning("No hay cliente autenticado, omitiendo pruebas de API")
        return
    
    endpoints = [
        ('/dashboard/api/sucursales-roles/', "API Roles y Sucursales"),
        ('/dashboard/api/categorias/', "API Categorías"),
        ('/dashboard/api/unidades-medida/', "API Unidades de Medida"),
        ('/dashboard/insumos/detalle/1/', "API Detalle Insumo (si existe ID 1)")
    ]
    
    for url, name in endpoints:
        try:
            response = client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            if response.status_code == 200:
                try:
                    data = json.loads(response.content)
                    if data.get('success') is True:
                        print_success(f"{name}: Respuesta correcta")
                    else:
                        print_warning(f"{name}: Respuesta sin éxito - {data.get('message', 'Sin mensaje')}")
                except:
                    print_warning(f"{name}: No es una respuesta JSON válida")
            else:
                print_error(f"{name}: Error HTTP {response.status_code}")
        except Exception as e:
            print_error(f"{name}: Excepción - {str(e)}")

def test_usuario_module(client):
    """Prueba específica del módulo de usuarios"""
    print_subheader("PRUEBA DE MÓDULO DE USUARIOS")
    
    if not client:
        print_warning("No hay cliente autenticado, omitiendo pruebas de usuarios")
        return
    
    # Verificar que se pueda acceder a la página de usuarios
    try:
        response = client.get('/dashboard/usuarios/')
        if response.status_code == 200:
            print_success("Acceso a página de usuarios")
        else:
            print_error(f"Error accediendo a página de usuarios: HTTP {response.status_code}")
    except Exception as e:
        print_error(f"Excepción accediendo a página de usuarios: {str(e)}")
    
    # Verificar API de roles
    try:
        response = client.get('/dashboard/api/sucursales-roles/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        if response.status_code == 200:
            data = json.loads(response.content)
            if data.get('success'):
                roles = data.get('roles', [])
                print_success(f"API de roles devuelve {len(roles)} roles")
                
                # Verificar que estén los roles principales
                role_names = [role['nombre'] for role in roles]
                expected_roles = ['admin', 'gerente', 'supervisor', 'cajero']
                missing_roles = [r for r in expected_roles if r not in role_names]
                
                if missing_roles:
                    print_warning(f"Faltan roles: {', '.join(missing_roles)}")
                else:
                    print_success("Todos los roles principales están presentes")
            else:
                print_error(f"API de roles sin éxito: {data.get('message')}")
        else:
            print_error(f"Error en API de roles: HTTP {response.status_code}")
    except Exception as e:
        print_error(f"Excepción en API de roles: {str(e)}")

def test_sucursales_module(client):
    """Prueba específica del módulo de sucursales"""
    print_subheader("PRUEBA DE MÓDULO DE SUCURSALES")
    
    if not client:
        print_warning("No hay cliente autenticado, omitiendo pruebas de sucursales")
        return
    
    # Verificar que se pueda acceder a la página de sucursales
    try:
        response = client.get('/dashboard/sucursales/')
        if response.status_code == 200:
            print_success("Acceso a página de sucursales")
        else:
            print_error(f"Error accediendo a página de sucursales: HTTP {response.status_code}")
    except Exception as e:
        print_error(f"Excepción accediendo a página de sucursales: {str(e)}")
    
    # Verificar existencia de sucursales
    sucursales_count = Sucursal.objects.count()
    sucursales_activas = Sucursal.objects.filter(activa=True).count()
    
    if sucursales_count > 0:
        print_success(f"Hay {sucursales_count} sucursales en la base de datos")
        print_info(f"Sucursales activas: {sucursales_activas}")
    else:
        print_warning("No hay sucursales en la base de datos")

def run_all_tests():
    """Ejecuta todas las pruebas y muestra un resumen"""
    print_header("DIAGNÓSTICO COMPLETO DEL SISTEMA")
    print_info(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Prueba de templates
    templates_ok, templates_total = test_template_loading()
    
    # Prueba de modelos
    test_models()
    
    # Prueba de login
    client = test_login()
    
    # Pruebas de API
    test_api_endpoints(client)
    
    # Pruebas específicas de módulos
    test_usuario_module(client)
    test_sucursales_module(client)
    
    # Resumen
    print_header("RESUMEN DE DIAGNÓSTICO")
    print_info(f"Templates: {templates_ok}/{templates_total} cargados correctamente")
    
    # Estado de modelos principales
    usuarios = Usuario.objects.count()
    roles = Rol.objects.count()
    sucursales = Sucursal.objects.count()
    insumos = Insumo.objects.count()
    
    print_info(f"Usuarios: {usuarios}")
    print_info(f"Roles: {roles}")
    print_info(f"Sucursales: {sucursales}")
    print_info(f"Insumos: {insumos}")
    
    # Recomendaciones
    print_subheader("RECOMENDACIONES")
    
    if usuarios == 0:
        print_warning("No hay usuarios en el sistema. Ejecuta: python inicializar_sistema.py")
    
    if roles == 0:
        print_warning("No hay roles en el sistema. Ejecuta: python crear_roles_base.py")
    
    if sucursales == 0:
        print_warning("No hay sucursales en el sistema. Ejecuta: python crear_sucursal.py")
    
    print_info("Para reconstruir todo el sistema: python inicializar_sistema.py")
    print_info("Para recrear solo los datos básicos: python recrear_datos_basicos.py")

if __name__ == "__main__":
    run_all_tests()
