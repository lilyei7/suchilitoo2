import os
import sys
import webbrowser
import time
from datetime import datetime

print(f"===== VISUALIZANDO MENÚ CON PALETA AZUL Y BLANCO =====")
print(f"Timestamp de caché: {int(datetime.now().timestamp())}")

# Generar URL con parámetro para forzar recarga
cache_buster = int(datetime.now().timestamp())
url = f"http://127.0.0.1:8000/mesero/login/?cache_bust={cache_buster}"

print(f"\nAbriendo URL con cache buster: {url}")
print("Esto debería forzar la carga de los nuevos estilos.")

webbrowser.open(url)

print("\nPara ver la paleta azul y blanco:")
print("1. Inicia sesión con: usuario=mesero1, contraseña=mesero123")
print("2. Una vez dentro, ve a: http://127.0.0.1:8000/mesero/menu/")

print("\nSi los colores todavía son rojos:")
print("1. Presiona Ctrl+F5 en el navegador")
print("2. Abre las herramientas de desarrollador (F12)")
print("3. Ve a la pestaña 'Network' y marca 'Disable cache'")
print("4. Recarga la página")
