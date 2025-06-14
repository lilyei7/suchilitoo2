#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario

def resetear_password():
    try:
        user = Usuario.objects.get(username='jhayco')
        user.set_password('admin123')  # Contraseña simple para testing
        user.save()
        print(f"✅ Contraseña establecida para usuario: {user.username}")
        print("Credenciales:")
        print("  Usuario: jhayco")
        print("  Contraseña: admin123")
    except Usuario.DoesNotExist:
        print("❌ Usuario 'jhayco' no encontrado")

if __name__ == "__main__":
    resetear_password()
