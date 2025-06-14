import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

# Import necessary models
from dashboard.models import Proveedor, ProveedorInsumo
from restaurant.models import Insumo
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from dashboard.views import asignar_insumo_proveedor
from django.middleware.csrf import get_token
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.test import Client

User = get_user_model()

def test_function_directly():
    """Test directly by calling the view function"""
    print("=== TESTING DIRECT FUNCTION CALL ===")
    
    # Get first insumo
    try:
        insumo = Insumo.objects.first()
        if not insumo:
            print("❌ No insumos available")
            return
        print(f"✅ Found insumo: {insumo.nombre} (ID: {insumo.id})")
    except Exception as e:
        print(f"❌ Error getting insumo: {e}")
        return
    
    # Get provider
    try:
        proveedor = Proveedor.objects.get(id=6)
        print(f"✅ Found proveedor: {proveedor.nombre_comercial} (ID: {proveedor.id})")
    except Proveedor.DoesNotExist:
        print("❌ Proveedor with ID 6 doesn't exist")
        return
    except Exception as e:
        print(f"❌ Error getting proveedor: {e}")
        return
    
    # Create a fake request
    factory = RequestFactory()
    request = factory.post(f'/dashboard/proveedor/{proveedor.id}/asignar-insumo/', {
        'insumo_id': insumo.id,
        'precio_unitario': 150.00,
        'cantidad_minima': 10,
        'tiempo_entrega_dias': 5,
        'observaciones': 'Prueba directa'
    })
    
    # Setup session
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    
    # Get a user
    try:
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            print("❌ No superuser found")
            return
        print(f"✅ Using admin user: {user.username}")
    except Exception as e:
        print(f"❌ Error getting user: {e}")
        return
    
    # Setup auth
    auth_middleware = AuthenticationMiddleware(lambda req: None)
    auth_middleware.process_request(request)
    request.user = user
    
    # Call the function directly
    print("\nCalling asignar_insumo_proveedor...")
    try:
        response = asignar_insumo_proveedor(request, proveedor.id)
        print(f"✅ Got response: {type(response)}")
        
        if isinstance(response, JsonResponse):
            data = response.content.decode('utf-8')
            print(f"Status code: {response.status_code}")
            print(f"Response: {data}")
        else:
            print(f"❌ Unexpected response type: {type(response)}")
    except Exception as e:
        print(f"❌ Error calling function: {e}")

def main():
    # Run the direct test
    test_function_directly()
    
    print("\n=== TESTING WITH DJANGO TEST CLIENT ===")
    
    # Test with Django client
    client = Client()
    
    # Login first
    login_success = client.login(username='admin', password='admin123')
    if login_success:
        print("✅ Login successful")
    else:
        print("❌ Login failed")
        return
    
    # Get insumo and proveedor
    insumo = Insumo.objects.first()
    proveedor_id = 6
    
    data = {
        'insumo_id': insumo.id,
        'precio_unitario': 200.00,
        'cantidad_minima': 5,
        'tiempo_entrega_dias': 3,
        'observaciones': 'Prueba con client'
    }
    
    response = client.post(f'/dashboard/proveedor/{proveedor_id}/asignar-insumo/', data)
    print(f"Status code: {response.status_code}")
    print(f"Response content: {response.content.decode('utf-8')}")

if __name__ == '__main__':
    main()
