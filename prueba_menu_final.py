import os
import django
from django.test import Client

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

print("=== PRUEBA FINAL DEL MENÚ CORREGIDO ===")

# Crear cliente de prueba
client = Client()

# Login
print("1. Realizando login...")
login_response = client.post('/dashboard/login/', {
    'username': 'mesero_test',
    'password': '123456'
})
print(f"Login status: {login_response.status_code}")

# Acceder al menú
print("\n2. Accediendo al menú...")
menu_response = client.get('/mesero/menu/')
print(f"Menu status: {menu_response.status_code}")

if menu_response.status_code == 200:
    content = menu_response.content.decode('utf-8')
    
    print(f"\n3. Análisis del contenido del menú:")
    print(f"Tamaño del HTML: {len(content)} caracteres")
    
    # Buscar productos específicos que sabemos que existen
    productos_esperados = [
        'Té Verde',
        'Sake Caliente', 
        'Gyozas',
        'Edamame',
        'California Roll',
        'Ramen Tonkotsu'
    ]
    
    productos_encontrados = []
    for producto in productos_esperados:
        if producto in content:
            productos_encontrados.append(producto)
            print(f"✓ Encontrado: {producto}")
        else:
            print(f"✗ No encontrado: {producto}")
    
    print(f"\n4. Resumen:")
    print(f"Productos esperados: {len(productos_esperados)}")
    print(f"Productos encontrados: {len(productos_encontrados)}")
    
    if len(productos_encontrados) >= 5:
        print("🎉 ¡ÉXITO! El menú está mostrando los productos correctamente")
        
        # Verificar que los precios también aparezcan
        if '$' in content or 'precio' in content.lower():
            print("✓ Los precios también están incluidos")
        
        # Verificar categorías
        categorias_esperadas = ['Bebidas', 'Entradas', 'Postres', 'Sushi Rolls', 'Platos Principales']
        categorias_encontradas = []
        for categoria in categorias_esperadas:
            if categoria in content:
                categorias_encontradas.append(categoria)
                print(f"✓ Categoría encontrada: {categoria}")
        
        print(f"\nCategorías encontradas: {len(categorias_encontradas)}/{len(categorias_esperadas)}")
        
    else:
        print("❌ El menú aún no está mostrando suficientes productos")
        
    # Guardar una muestra para inspección
    with open('menu_final_test.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n✓ HTML guardado en 'menu_final_test.html' para inspección")
    
else:
    print(f"❌ Error accediendo al menú: {menu_response.status_code}")

print("\n=== FIN DE LA PRUEBA ===")
