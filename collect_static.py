import os
import django
from django.core.management import call_command

# Configurar entorno Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sushi_core.settings")
django.setup()

# Ejecutar collectstatic
print("Ejecutando collectstatic...")
call_command("collectstatic", "--noinput")

print("¡Archivos estáticos recolectados con éxito!")
