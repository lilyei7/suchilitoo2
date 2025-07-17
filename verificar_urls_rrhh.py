#!/usr/bin/env python
"""
Script para verificar URLs del módulo RRHH y reportar cuáles faltan
"""
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.urls import reverse, NoReverseMatch
from django.conf import settings

# URLs que se esperan en el módulo RRHH
urls_esperadas = [
    # Empleados
    'dashboard:rrhh_empleados_listado',
    'dashboard:rrhh_empleado_crear',
    'dashboard:rrhh_empleado_detalle',
    'dashboard:rrhh_empleado_editar',
    
    # Turnos
    'dashboard:rrhh_turnos_listado',
    'dashboard:rrhh_turno_crear',
    'dashboard:rrhh_turno_detalle',
    'dashboard:rrhh_turno_editar',
    'dashboard:rrhh_turno_asignar_empleados',
    'dashboard:rrhh_turno_eliminar',
    
    # Asistencias
    'dashboard:rrhh_asistencias_listado',
    'dashboard:rrhh_asistencia_registrar',
    'dashboard:rrhh_asistencia_detalle',
    'dashboard:rrhh_asistencia_editar',
    
    # Nóminas
    'dashboard:rrhh_nominas_listado',
    'dashboard:rrhh_nomina_generar',
    'dashboard:rrhh_nomina_crear',
    'dashboard:rrhh_nomina_detalle',
    'dashboard:rrhh_nomina_editar',
]

print("=== Verificación de URLs del módulo RRHH ===\n")

urls_existentes = []
urls_faltantes = []

for url_name in urls_esperadas:
    try:
        url = reverse(url_name)
        urls_existentes.append((url_name, url))
        print(f"✅ {url_name} -> {url}")
    except NoReverseMatch:
        urls_faltantes.append(url_name)
        print(f"❌ {url_name} -> NO ENCONTRADA")

print(f"\n=== Resumen ===")
print(f"URLs existentes: {len(urls_existentes)}")
print(f"URLs faltantes: {len(urls_faltantes)}")

if urls_faltantes:
    print(f"\n=== URLs que necesitan ser creadas ===")
    for url in urls_faltantes:
        print(f"- {url}")
