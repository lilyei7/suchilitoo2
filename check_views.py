import requests
import sys
import time

# Esperar a que el servidor esté listo
print("Esperando a que el servidor esté listo...")
time.sleep(3)

# URLs a verificar
urls = [
    "http://127.0.0.1:8000/mesero/menu/",
    "http://127.0.0.1:8000/mesero/mesa/1/nueva_orden/"
]

# Verificar las URLs
print("\n===== VERIFICANDO VISTAS =====")
for url in urls:
    try:
        print(f"\nVerificando {url}...")
        response = requests.get(url)
        print(f"Código de estado: {response.status_code}")
        
        if response.status_code == 200:
            content_sample = response.text[:200]  # Muestra los primeros 200 caracteres
            print(f"Contenido (muestra): {content_sample}...")
            print("✅ Vista disponible correctamente")
        else:
            print("❌ Error al acceder a la vista")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

print("\nVerificación completada. Revisa los resultados para asegurar que todas las vistas funcionan.")
