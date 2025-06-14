import requests
import sys
import os
import django

# Configure Django settings
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

# Import models
from dashboard.models import Proveedor, ProveedorInsumo
from restaurant.models import Insumo
from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()

def inspect_database():
    # Check existencia de proveedores
    proveedores = Proveedor.objects.all()
    print(f"Total proveedores: {proveedores.count()}")
    
    if proveedores.exists():
        for p in proveedores:
            print(f"ID: {p.id}, Nombre: {p.nombre_comercial}, Estado: {p.estado}")
    
    # Check existencia de insumos
    insumos = Insumo.objects.all()
    print(f"\nTotal insumos: {insumos.count()}")
    
    if insumos.exists():
        for i in insumos:
            print(f"ID: {i.id}, Nombre: {i.nombre}, Categoría: {i.categoria_id}")
    
    # Check existencia de ProveedorInsumo
    prov_insumos = ProveedorInsumo.objects.all()
    print(f"\nTotal relaciones ProveedorInsumo: {prov_insumos.count()}")
    
    if prov_insumos.exists():
        for pi in prov_insumos:
            print(f"ID: {pi.id}, Proveedor: {pi.proveedor_id}, Insumo: {pi.insumo_id}, Precio: {pi.precio_unitario}")

def test_direct_assignment():
    # Tomamos un proveedor que exista
    proveedor_id = 6
    try:
        proveedor = Proveedor.objects.get(id=proveedor_id)
        print(f"✅ Proveedor encontrado: {proveedor.nombre_comercial} (ID: {proveedor.id})")
    except Proveedor.DoesNotExist:
        print(f"❌ Proveedor con ID {proveedor_id} no existe")
        return
    
    # Tomamos un insumo que NO esté asignado al proveedor
    try:
        # Obtenemos los IDs de insumos ya asignados a este proveedor
        insumos_asignados = ProveedorInsumo.objects.filter(
            proveedor=proveedor
        ).values_list('insumo_id', flat=True)
        
        # Buscamos un insumo que no esté en esa lista
        insumo = Insumo.objects.exclude(id__in=insumos_asignados).first()
        
        if not insumo:
            print("❌ No hay insumos disponibles sin asignar a este proveedor")
            return
            
        print(f"✅ Insumo encontrado: {insumo.nombre} (ID: {insumo.id})")
    except Exception as e:
        print(f"❌ Error buscando insumos: {e}")
        return
    
    # Intentamos crear la relación
    print("\nIntentando crear relación...")
    try:
        proveedor_insumo = ProveedorInsumo(
            proveedor=proveedor,
            insumo=insumo,
            precio_unitario=100.00,
            cantidad_minima=1,
            tiempo_entrega_dias=3,
            notas="Prueba desde script"
        )
        proveedor_insumo.save()
        print(f"✅ Relación creada exitosamente con ID: {proveedor_insumo.id}")
    except Exception as e:
        print(f"❌ Error al crear relación: {str(e)}")
        # Ver el último query SQL ejecutado
        print("\nÚltima consulta SQL:")
        print(connection.queries[-1]['sql'] if connection.queries else "No hay consultas registradas")

def login_and_test_api():
    # Intentar hacer login via API primero
    print("\n=== Probando a través del API ===")
    session = requests.Session()
    
    # Obtener CSRF token inicial
    login_url = "http://localhost:8000/dashboard/login/"
    login_response = session.get(login_url)
    if login_response.status_code != 200:
        print(f"❌ Error al acceder a la página de login: {login_response.status_code}")
        return
    
    # Buscar el CSRF token en cookies primero y luego en el HTML
    csrf_token = None
    if 'csrftoken' in session.cookies:
        csrf_token = session.cookies['csrftoken']
        print(f"✅ CSRF token obtenido de cookies: {csrf_token[:15]}...")
    
    if not csrf_token:
        # Intentar extraer token del HTML
        import re
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_response.text)
        if match:
            csrf_token = match.group(1)
            print(f"✅ CSRF token obtenido del HTML: {csrf_token[:15]}...")
    
    if not csrf_token:
        print("❌ No se pudo obtener CSRF token")
        return
    
    # Hacer login
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    login_post_response = session.post(
        login_url, 
        data=login_data, 
        headers={
            'Referer': login_url,
            'X-CSRFToken': csrf_token
        }
    )
    
    if login_post_response.status_code != 200 and login_post_response.status_code != 302:
        print(f"❌ Error al hacer login: {login_post_response.status_code}")
        return
    
    print("✅ Login exitoso")
    
    # Después del login, actualizar el token si cambió
    if 'csrftoken' in session.cookies:
        csrf_token = session.cookies['csrftoken']
        print(f"✅ CSRF token actualizado después del login: {csrf_token[:15]}...")
    
    # Cargar la página de proveedores para obtener un token fresco y referencia adecuada
    proveedores_url = "http://localhost:8000/dashboard/proveedores/"
    proveedores_response = session.get(proveedores_url)
    
    # Actualizar token si cambió
    if 'csrftoken' in session.cookies:
        csrf_token = session.cookies['csrftoken']
        print(f"✅ CSRF token actualizado: {csrf_token[:15]}...")
    
    # Intentar asignar insumo via API
    print("\nBuscando un proveedor e insumo para la prueba...")
    proveedor_id = 6  # Usa un ID de proveedor que sepas que existe
    
    try:
        insumo = Insumo.objects.filter(activo=True).first()
        if not insumo:
            print("❌ No hay insumos disponibles para la prueba")
            return
        insumo_id = insumo.id
        print(f"✅ Usando proveedor ID: {proveedor_id}, insumo ID: {insumo_id} ({insumo.nombre})")
    except Exception as e:
        print(f"❌ Error al buscar insumo para prueba: {e}")
        return
    
    # Preparar datos para el envío
    assign_data = {
        'insumo_id': insumo_id,
        'precio_unitario': 100.00,
        'cantidad_minima': 1,
        'tiempo_entrega_dias': 3,
        'observaciones': 'Prueba desde API'
    }
    
    assign_url = f"http://localhost:8000/dashboard/proveedor/{proveedor_id}/asignar-insumo/"
    
    # Importante: Incluir el CSRF token tanto en la data como en los headers
    assign_data['csrfmiddlewaretoken'] = csrf_token
    
    print(f"\nEnviando petición a: {assign_url}")
    print(f"Datos: {assign_data}")
    print(f"CSRF Token: {csrf_token[:15]}...")
    
    assign_response = session.post(
        assign_url, 
        data=assign_data,
        headers={
            'Referer': proveedores_url,
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrf_token
        }
    )
    
    print(f"\nStatus code: {assign_response.status_code}")
    print(f"Response headers: {dict(assign_response.headers)}")
    print(f"Respuesta: {assign_response.text}")

if __name__ == "__main__":
    print("=== INSPECCIÓN DEL ESTADO DE LA BASE DE DATOS ===")
    inspect_database()
    print("\n=== PRUEBA DE ASIGNACIÓN DIRECTA ===")
    test_direct_assignment()
    print("\n=== PRUEBA DE ASIGNACIÓN VIA API ===")
    login_and_test_api()
