import os
import sys
import subprocess
import time
import webbrowser

# Mensaje informativo
print("===== INICIANDO SISTEMA DE MESERO CON DISEÑO MODERNO =====")

# Reiniciar servidor Django
print("Reiniciando servidor Django...")
try:
    # Ejecutar el script de reinicio de servidor
    subprocess.Popen([sys.executable, "restart_server.py"])
    # Esperar a que el servidor esté listo
    time.sleep(5)
except Exception as e:
    print(f"Error al reiniciar el servidor: {e}")

# Abrir URLs en el navegador
print("\nAbriendo sistema en el navegador...\n")

# URLs a abrir
print("📌 Instrucciones de acceso:")
print("1) Usa estas credenciales para iniciar sesión:")
print("   • Usuario: mesero1")
print("   • Contraseña: mesero123")
print("2) Explora las vistas con el nuevo diseño moderno:")

urls = [
    {"url": "http://127.0.0.1:8000/mesero/login/", "desc": "Login del sistema"},
]

# Mostrar URLs disponibles para navegar manualmente
available_urls = [
    {"url": "http://127.0.0.1:8000/mesero/", "desc": "Dashboard principal"},
    {"url": "http://127.0.0.1:8000/mesero/menu/", "desc": "🆕 Menú con diseño moderno"},
    {"url": "http://127.0.0.1:8000/mesero/mesas/", "desc": "Lista de mesas"},
]

# Abrir la página de login
for item in urls:
    print(f"\n🌐 Abriendo: {item['url']} - {item['desc']}")
    webbrowser.open(item["url"])

print("\n📋 Otras páginas disponibles (para navegar manualmente):")
for i, item in enumerate(available_urls):
    print(f"   {i+1}) {item['url']} - {item['desc']}")

print("\n✅ Sistema iniciado correctamente.")
print("   Después de iniciar sesión, prueba el menú moderno y crea una nueva orden.")
