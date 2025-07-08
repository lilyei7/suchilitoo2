from django.test import Client
from django.contrib.auth import get_user_model
from django.core.management import call_command
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def debug_mesero_view():
    print("=== Iniciando diagnóstico de vista mesero ===")
    
    # 1. Crear usuario de prueba
    User = get_user_model()
    username = "test_mesero"
    password = "test12345"
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, password=password)
        print(f"Usuario de prueba creado: {username}")
    
    # 2. Configurar cliente de prueba
    client = Client()
    
    # 3. Intentar login
    login_success = client.login(username=username, password=password)
    print(f"Login exitoso: {login_success}")
    
    if not login_success:
        print("ERROR: No se pudo iniciar sesión")
        return
    
    # 4. Intentar acceder a la vista del mesero
    print("\nProbando acceso a /mesero/...")
    response = client.get('/mesero/')
    
    print(f"Código de respuesta: {response.status_code}")
    print(f"Content-Type: {response.get('Content-Type', 'No Content-Type')}")
    
    if response.status_code == 200:
        print("Vista cargada exitosamente")
        print("\nContexto de la vista:")
        if hasattr(response, 'context'):
            for key, value in response.context.items():
                print(f"{key}: {value}")
        else:
            print("No hay contexto disponible")
    else:
        print(f"ERROR: La vista retornó código {response.status_code}")
        if hasattr(response, 'content'):
            print("\nContenido de la respuesta:")
            print(response.content.decode('utf-8')[:500])  # Primeros 500 caracteres

if __name__ == '__main__':
    debug_mesero_view()
