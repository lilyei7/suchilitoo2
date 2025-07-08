#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario

gerente = Usuario.objects.filter(rol__nombre='gerente').first()
if gerente:
    print(f'Usuario: {gerente.username}')
    print(f'Sucursal: {gerente.sucursal.nombre if gerente.sucursal else "Sin sucursal"}')
    # Establecer una contraseña conocida
    gerente.set_password('123456')
    gerente.save()
    print('Contraseña establecida: 123456')
else:
    print('No se encontró gerente')
