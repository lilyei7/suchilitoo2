import os
import django
from django.test import Client

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

print("=== VERIFICACIÓN DE SUCURSAL EN HTML ===")

# Crear cliente de prueba
client = Client()

# Login
login_response = client.post('/dashboard/login/', {
    'username': 'mesero_test',
    'password': '123456'
})

# Acceder al menú
menu_response = client.get('/mesero/menu/')

if menu_response.status_code == 200:
    content = menu_response.content.decode('utf-8')
    
    # Buscar elementos específicos de la sucursal
    elementos_sucursal = [
        'Sucursal Actual',
        'Sucursal Centro',
        'sucursal-info',
        'sucursal-nombre',
        'sucursal-label'
    ]
    
    print("Búsqueda de elementos de sucursal:")
    sucursal_encontrada = False
    
    for elemento in elementos_sucursal:
        if elemento in content:
            print(f"✓ Encontrado: '{elemento}'")
            sucursal_encontrada = True
        else:
            print(f"✗ No encontrado: '{elemento}'")
    
    if sucursal_encontrada:
        print("\n🎉 ¡La información de sucursal está presente en el HTML!")
        
        # Extraer el contexto alrededor de la sucursal
        inicio = content.find('Sucursal Actual')
        if inicio != -1:
            contexto = content[inicio:inicio+200]
            print(f"\nContexto de la sucursal:\n{contexto}")
    else:
        print("\n❌ La información de sucursal NO está presente en el HTML")
        
    # Verificar también si hay información del usuario
    print("\n=== VERIFICACIÓN DE INFORMACIÓN DE USUARIO ===")
    elementos_usuario = [
        'bienvenida-header',
        'avatar',
        'mesero_test'
    ]
    
    for elemento in elementos_usuario:
        if elemento in content:
            print(f"✓ Encontrado: '{elemento}'")
        else:
            print(f"✗ No encontrado: '{elemento}'")
    
    # Guardar un fragmento específico del header
    inicio_header = content.find('<div class="bienvenida-header">')
    if inicio_header != -1:
        fin_header = content.find('</div>', inicio_header + 500)  # Buscar el cierre del header
        if fin_header != -1:
            header_content = content[inicio_header:fin_header + 6]
            print(f"\n=== CONTENIDO DEL HEADER ===")
            print(header_content[:800])  # Primeros 800 caracteres
            
            with open('header_debug.html', 'w', encoding='utf-8') as f:
                f.write(header_content)
            print(f"\n✓ Header guardado en 'header_debug.html'")

else:
    print(f"❌ Error accediendo al menú: {menu_response.status_code}")

print("\n=== FIN DE LA VERIFICACIÓN ===")
