#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import Orden

def verificar_ordenes_especificas():
    print('=== VERIFICACIÓN ESPECÍFICA DE ÓRDENES 36, 37, 38 ===')
    for orden_id in [36, 37, 38]:
        try:
            orden = Orden.objects.get(id=orden_id)
            print(f'ID: {orden.id}, Numero: {orden.numero_orden}, Estado: {orden.estado}, Mesa: {orden.mesa.numero if orden.mesa else "Sin mesa"}')
        except Orden.DoesNotExist:
            print(f'Orden con ID {orden_id} no encontrada')

if __name__ == '__main__':
    verificar_ordenes_especificas()
