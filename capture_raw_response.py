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
from django.middleware.csrf import get_token
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.test import Client
import json

User = get_user_model()

def capture_raw_response():
    """Capture the raw response from the server"""
    print("=== CAPTURING RAW SERVER RESPONSE ===")
    
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
    
    # Setup test client
    client = Client()
    client.force_login(user)
    
    # Get first insumo
    try:
        insumo = Insumo.objects.filter(activo=True).first()
        if not insumo:
            print("❌ No active insumos available")
            return
        print(f"✅ Found insumo: {insumo.nombre} (ID: {insumo.id})")
    except Exception as e:
        print(f"❌ Error getting insumo: {e}")
        return
    
    # Get provider
    try:
        proveedor = Proveedor.objects.first()
        if not proveedor:
            print("❌ No proveedores available")
            return
        print(f"✅ Found proveedor: {proveedor.nombre_comercial} (ID: {proveedor.id})")
    except Exception as e:
        print(f"❌ Error getting proveedor: {e}")
        return
    
    # Make the POST request
    post_data = {
        'insumo_id': insumo.id,
        'precio_unitario': 150.00,
        'cantidad_minima': 10,
        'tiempo_entrega_dias': 5,
        'observaciones': 'Prueba de captura de respuesta'
    }
    
    url = f'/dashboard/proveedor/{proveedor.id}/asignar-insumo/'
    print(f"\n📡 Making POST request to: {url}")
    print(f"📦 POST data: {post_data}")
    
    # Set AJAX headers to get JSON response
    headers = {
        'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest',
    }
    
    response = client.post(url, post_data, **headers)
    
    print(f"\n📝 Response details:")
    print(f"Status code: {response.status_code}")
    print(f"Content type: {response.get('Content-Type', 'Not specified')}")
    print(f"Content length: {len(response.content)} bytes")
    
    # Get the raw content before any processing
    raw_content = response.content.decode('utf-8')
    print(f"\n📄 Raw response content:")
    print("-------------RAW CONTENT START-------------")
    print(raw_content)
    print("-------------RAW CONTENT END-------------")
    
    # Try to parse as JSON
    print("\n🔍 Attempting to parse response as JSON:")
    try:
        json_data = json.loads(raw_content)
        print("✅ Successfully parsed as JSON:")
        print(json.dumps(json_data, indent=2))
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse as JSON: {e}")
        
        # If not valid JSON, check for common issues
        if raw_content.strip().startswith('{') and raw_content.strip().endswith('}'):
            print("🔍 Response starts with { and ends with }, but isn't valid JSON.")
            print("   Possible issues: Extra characters before/after JSON or invalid JSON syntax.")
        
        if '\n' in raw_content and raw_content.count('\n') > 0:
            print(f"🔍 Response contains {raw_content.count('\n')} newlines.")
            print("   First few lines:")
            lines = raw_content.split('\n')
            for i, line in enumerate(lines[:5]):
                print(f"   Line {i+1}: {repr(line)}")
                
        if len(raw_content) > 1000:
            print("🔍 Response is quite long, might contain HTML or other non-JSON content.")

if __name__ == "__main__":
    capture_raw_response()
