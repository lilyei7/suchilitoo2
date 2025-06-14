import json
from django.test import Client
from restaurant.models import Insumo
from django.contrib.auth import get_user_model

User = get_user_model()

print("=== PROBANDO MODAL DE INVENTARIO ===")

# Crear cliente de prueba
client = Client()

# Verificar que existen usuarios admin
admin_users = User.objects.filter(is_superuser=True)
print("Usuarios admin encontrados:", admin_users.count())

if admin_users.exists():
    admin_user = admin_users.first()
    print("Usuario admin:", admin_user.username)
    
    # Intentar login con varias contraseñas
    passwords = ['admin123', 'admin', '123456', 'password']
    login_successful = False
    
    for pwd in passwords:
        if client.login(username=admin_user.username, password=pwd):
            print("Login exitoso con", admin_user.username, "/", pwd)
            login_successful = True
            break    
    if not login_successful:
        print("No se pudo hacer login con ninguna contraseña")
    else:
        # Verificar insumos en la base de datos
        insumos = Insumo.objects.all()
        print("Total de insumos en BD:", insumos.count())
        
        if insumos.exists():
            # Tomar el primer insumo
            insumo = insumos.first()
            print("Probando con insumo:", insumo.nombre, "(ID:", insumo.id, ")")
            if insumo.categoria:
                print("   Categoría:", insumo.categoria.nombre)
            if insumo.unidad_medida:
                print("   Unidad:", insumo.unidad_medida.nombre)
            
            # Hacer petición GET al endpoint de edición
            url = "/dashboard/insumos/editar/" + str(insumo.id) + "/"
            print("Haciendo petición GET a:", url)
            
            response = client.get(url)
            print("Status de respuesta:", response.status_code)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("Datos JSON recibidos OK")
                    
                    # Verificar campos específicos del problema
                    print("=== ANÁLISIS DE CAMPOS PROBLEMÁTICOS ===")
                    
                    categoria_id = data.get('categoria')
                    categoria_nombre = data.get('categoria_nombre')
                    unidad_id = data.get('unidad_medida')
                    unidad_nombre = data.get('unidad_medida_nombre')
                    
                    print("categoria (ID):", categoria_id)
                    print("categoria_nombre:", categoria_nombre)
                    print("unidad_medida (ID):", unidad_id)
                    print("unidad_medida_nombre:", unidad_nombre)
                    
                    # Verificar si los campos problemáticos están presentes
                    if categoria_nombre:
                        print("categoria_nombre está presente")
                    else:
                        print("categoria_nombre está vacío o undefined")
                    
                    if unidad_nombre:
                        print("unidad_medida_nombre está presente")
                    else:
                        print("unidad_medida_nombre está vacío o undefined")
                        
                except Exception as e:
                    print("Error procesando respuesta:", e)
                    print("Contenido de respuesta:", response.content.decode())
            else:
                print("Error en la petición:", response.status_code)
                print("Contenido de respuesta:", response.content.decode())
        else:
            print("No hay insumos en la base de datos")
else:
    print("No hay usuarios admin")
