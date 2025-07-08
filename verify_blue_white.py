import os
import sys
import webbrowser

print("===== VERIFICANDO PALETA AZUL Y BLANCO =====")

# Abrir navegador con recarga forzada (Ctrl+F5)
url = "http://127.0.0.1:8000/mesero/menu/"
print(f"\nAbriendo el menú con la nueva paleta azul y blanco: {url}")
print("Recuerda presionar Ctrl+F5 en el navegador para forzar la recarga sin caché")

# Abrir el navegador
webbrowser.open(url)

print("\nPara iniciar sesión:")
print("- Usuario: mesero1")
print("- Contraseña: mesero123")

print("\nSi aún ves la paleta anterior (rojo y blanco), prueba estos pasos:")
print("1. Presiona Ctrl+F5 en el navegador para forzar la recarga")
print("2. Abre la consola del navegador (F12) y vacía la caché (en la pestaña Network)")
print("3. Intenta en una ventana de incógnito")
