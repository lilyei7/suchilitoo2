import os
import sys
import time
import webbrowser

# Mensaje informativo
print("===== VISUALIZANDO NUEVO MENÚ CON PALETA AZUL Y BLANCO =====")

# URLs a abrir
urls = [
    {"url": "http://127.0.0.1:8000/mesero/login/", "desc": "Página de login"},
]

print("\nAbriendo el sistema de mesero...")
print("Para ver el nuevo diseño:")
print("1. Inicia sesión con usuario: mesero1 / contraseña: mesero123")
print("2. Serás redirigido al dashboard")
print("3. Ve a http://127.0.0.1:8000/mesero/menu/ para ver el nuevo menú con paleta azul y blanco")

# Abrir navegador
for item in urls:
    print(f"\nAbriendo: {item['url']} - {item['desc']}")
    webbrowser.open(item["url"])

print("\n✅ Navegador abierto.")
print("Después de iniciar sesión, accede al menú para ver el nuevo diseño minimalista en azul y blanco.")
