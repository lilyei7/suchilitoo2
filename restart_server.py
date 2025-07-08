import os
import signal
import subprocess
import time
import sys

# Detener cualquier servidor que esté corriendo en el puerto 8000
print("Buscando servidores existentes...")
try:
    # En Windows, usamos netstat
    output = subprocess.check_output("netstat -ano | findstr :8000", shell=True).decode()
    for line in output.strip().split('\n'):
        parts = line.strip().split()
        if len(parts) >= 5 and parts[1].endswith(':8000'):
            pid = parts[4]
            print(f"Encontrado proceso en puerto 8000, PID: {pid}")
            try:
                os.kill(int(pid), signal.SIGTERM)
                print(f"Proceso con PID {pid} terminado")
                time.sleep(1)
            except Exception as e:
                print(f"No se pudo terminar el proceso: {e}")
except Exception as e:
    print(f"No se encontraron servidores corriendo: {e}")

# Iniciar servidor Django
print("\nIniciando servidor Django...")
try:
    subprocess.Popen([sys.executable, "manage.py", "runserver", "127.0.0.1:8000"])
    print("Servidor iniciado exitosamente en http://127.0.0.1:8000/")
except Exception as e:
    print(f"Error al iniciar el servidor: {e}")
