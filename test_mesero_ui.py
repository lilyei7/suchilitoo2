import sys
import webbrowser
import time

# Mensaje informativo
print("===== ACCEDIENDO AL SISTEMA DE MESERO =====")
print("⚠️ Importante: Deberás iniciar sesión en la página usando:")
print("   • Usuario: mesero1")
print("   • Contraseña: mesero123")

# Lista de URLs a abrir
urls = [
    "http://127.0.0.1:8000/mesero/login/",
    "http://127.0.0.1:8000/mesero/menu/",
]

# Abrir las URLs secuencialmente
for i, url in enumerate(urls):
    print(f"\n[{i+1}/{len(urls)}] Abriendo: {url}")
    webbrowser.open(url)
    
    if i < len(urls) - 1:
        wait_time = 3
        print(f"Esperando {wait_time} segundos antes de abrir la siguiente URL...")
        time.sleep(wait_time)

print("\n✅ URLs abiertas en el navegador.")
print("📌 Después de iniciar sesión, navega manualmente a: http://127.0.0.1:8000/mesero/mesas/")
print("   para ver la lista de mesas y acceder a 'Nueva Orden' desde ahí.")
