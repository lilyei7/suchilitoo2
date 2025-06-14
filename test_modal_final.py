print("=== PROBANDO FIX DEL MODAL - RESULTADO FINAL ===")

# Test usando el cliente interno de Django
from django.test import Client
from restaurant.models import Insumo
from django.contrib.auth import get_user_model

User = get_user_model()
client = Client()

# Login
admin_user = User.objects.filter(is_superuser=True).first()
login_ok = client.login(username=admin_user.username, password='admin123')

if not login_ok:
    print("❌ Error en login")
else:
    print("✅ Login exitoso")
    
    # Obtener primer insumo
    insumo = Insumo.objects.first()
    if not insumo:
        print("❌ No hay insumos en la BD")
    else:
        print(f"✅ Probando con insumo: {insumo.nombre}")
        
        # Test del endpoint
        response = client.get(f'/dashboard/insumos/editar/{insumo.id}/')
        
        if response.status_code != 200:
            print(f"❌ Error en endpoint: {response.status_code}")
        else:
            print("✅ Endpoint funcionando")
            
            try:
                data = response.json()
                
                categoria_nombre = data.get('categoria_nombre')
                unidad_medida_nombre = data.get('unidad_medida_nombre')
                
                print("\n=== RESULTADOS ===")
                print(f"categoria_nombre: '{categoria_nombre}'")
                print(f"unidad_medida_nombre: '{unidad_medida_nombre}'")
                
                # Verificación final
                if categoria_nombre and categoria_nombre.strip():
                    print("✅ categoria_nombre: CORRECTO")
                else:
                    print("❌ categoria_nombre: PROBLEMA")
                
                if unidad_medida_nombre and unidad_medida_nombre.strip():
                    print("✅ unidad_medida_nombre: CORRECTO")
                else:
                    print("❌ unidad_medida_nombre: PROBLEMA")
                
                if categoria_nombre and unidad_medida_nombre:
                    print("\n🎉 ¡FIX EXITOSO! El modal debería mostrar correctamente:")
                    print(f"   - Categoría: {categoria_nombre}")
                    print(f"   - Unidad: {unidad_medida_nombre}")
                    print("\nEl JavaScript ahora usará estos campos para poblar las etiquetas.")
                else:
                    print("\n❌ Aún hay problemas con los datos")
                    
            except Exception as e:
                print(f"❌ Error procesando JSON: {e}")

print("\n=== FIN DEL TEST ===")
