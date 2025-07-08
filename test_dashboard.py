import os
import sys
import django

# Configurar entorno Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sushi_core.settings")
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from mesero.views import dashboard

def add_middleware_to_request(request, middleware_class):
    middleware = middleware_class()
    middleware.process_request(request)
    return request

def add_session_to_request(request):
    """Add session to the request."""
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    return request

def add_messages_to_request(request):
    """Add messages to the request."""
    middleware = MessageMiddleware()
    middleware.process_request(request)
    return request

def add_auth_to_request(request):
    """Add authentication to the request."""
    middleware = AuthenticationMiddleware()
    middleware.process_request(request)
    return request

def main():
    print("Probando vista de dashboard...")
    
    try:
        # Crear un usuario administrador
        User = get_user_model()
        try:
            user = User.objects.get(username='admin_test')
            print("Usuario encontrado:", user.username)
        except User.DoesNotExist:
            print("Creando usuario de prueba...")
            user = User.objects.create_superuser(
                username='admin_test',
                email='admin@test.com',
                password='password123',
                is_staff=True,
                is_active=True,
                is_superuser=True
            )
            print(f"Usuario creado: {user}")
        
        # Crear request simulado
        factory = RequestFactory()
        request = factory.get('/mesero/')
        
        # Agregar sesión
        request = add_session_to_request(request)
        request = add_auth_to_request(request)
        request = add_messages_to_request(request)
        
        # Simular login
        request.user = user
        
        # Llamar a la vista
        print("Llamando a la vista dashboard...")
        response = dashboard(request)
        
        print(f"Código de estado: {response.status_code}")
        print(f"Tipo de contenido: {response.get('Content-Type', 'No especificado')}")
        print(f"Tamaño de respuesta: {len(response.content)} bytes")
        
        # Ver primeros 500 caracteres del contenido
        print("\nPrimeros 500 caracteres del contenido:")
        if hasattr(response, 'content'):
            print(response.content[:500].decode('utf-8', errors='ignore'))
        else:
            print("La respuesta no tiene contenido directo.")
            
        # Verificar si es una redirección
        if response.status_code in [301, 302]:
            print(f"Redirección a: {response.url}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
