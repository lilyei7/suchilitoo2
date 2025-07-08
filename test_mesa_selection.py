import requests
import os
from django.contrib.auth import authenticate

# Configurar sesión para las pruebas
session = requests.Session()

def test_login_and_mesa_selection():
    """Test login and mesa selection"""
    print("=== PRUEBA DE LOGIN Y SELECCIÓN DE MESA ===")
    
    # URLs
    login_url = "http://127.0.0.1:8000/accounts/login/"
    mesa_url = "http://127.0.0.1:8000/mesero/seleccionar-mesa/"
    
    # Credenciales
    username = "mesero_demo"
    password = "demo123"
    
    try:
        # 1. Obtener el formulario de login
        print("1. Obteniendo formulario de login...")
        login_response = session.get(login_url)
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   Error: No se pudo acceder al login. Status: {login_response.status_code}")
            return False
        
        # 2. Obtener el CSRF token
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(login_response.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if csrf_token:
            csrf_value = csrf_token.get('value')
            print(f"   CSRF token obtenido: {csrf_value[:20]}...")
        else:
            print("   Error: No se pudo obtener el CSRF token")
            return False
        
        # 3. Hacer login
        print("2. Haciendo login...")
        login_data = {
            'username': username,
            'password': password,
            'csrfmiddlewaretoken': csrf_value
        }
        
        login_post_response = session.post(login_url, data=login_data)
        print(f"   Status: {login_post_response.status_code}")
        print(f"   URL final: {login_post_response.url}")
        
        # 4. Verificar si el login fue exitoso
        if 'login' in login_post_response.url:
            print("   Error: Login fallido, aún en página de login")
            return False
        else:
            print("   ✓ Login exitoso")
        
        # 5. Acceder a la selección de mesa
        print("3. Accediendo a selección de mesa...")
        mesa_response = session.get(mesa_url)
        print(f"   Status: {mesa_response.status_code}")
        
        if mesa_response.status_code == 200:
            print("   ✓ Acceso a selección de mesa exitoso")
            
            # Verificar contenido
            content = mesa_response.text
            if 'Mesa' in content:
                print("   ✓ Contenido de mesas encontrado")
                
                # Buscar mesas específicas
                import re
                mesa_pattern = r'Mesa\s+(\d+)'
                mesas_found = re.findall(mesa_pattern, content)
                print(f"   Mesas encontradas: {mesas_found}")
                
                if mesas_found:
                    print("   ✓ Mesas visibles en el HTML")
                    return True
                else:
                    print("   ✗ No se encontraron mesas específicas")
                    return False
            else:
                print("   ✗ No se encontró contenido de mesas")
                # Mostrar parte del contenido para debug
                print("   Contenido (primeros 500 chars):")
                print(content[:500])
                return False
        else:
            print(f"   Error: No se pudo acceder a selección de mesa. Status: {mesa_response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error en la prueba: {e}")
        return False

def main():
    """Función principal"""
    try:
        # Instalar BeautifulSoup si no está instalado
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            print("Instalando BeautifulSoup...")
            os.system("pip install beautifulsoup4")
            from bs4 import BeautifulSoup
        
        success = test_login_and_mesa_selection()
        
        if success:
            print("\n✅ PRUEBA EXITOSA: Las mesas se están mostrando correctamente")
            print("   El usuario puede ver las mesas de su sucursal")
        else:
            print("\n❌ PRUEBA FALLIDA: Hay un problema con la visualización de mesas")
            print("   Revisar:")
            print("   - Configuración de URLs")
            print("   - Plantilla HTML")
            print("   - Logs del servidor Django")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
