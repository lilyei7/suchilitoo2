#!/usr/bin/env python
"""
Script para crear proveedores de ejemplo en el sistema de restaurant
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from dashboard.models import Proveedor

def crear_proveedores_ejemplo():
    """Crear proveedores de ejemplo para la demostración"""
    
    proveedores_data = [
        {
            'nombre': 'Mariscos del Pacífico S.A.',
            'contacto': 'Carlos Mendoza',
            'telefono': '+52 55 1234-5678',
            'email': 'carlos@mariscospacifico.com',
            'direccion': 'Av. Costera Miguel Alemán 125, Acapulco, Guerrero',
            'categoria': 'ingredientes',
            'estado': 'activo',
            'notas': 'Proveedor principal de pescados frescos y mariscos. Entregas diarias.'
        },
        {
            'nombre': 'Vegetales Orgánicos Tierra Verde',
            'contacto': 'María González',
            'telefono': '+52 55 9876-5432',
            'email': 'maria@tierraverde.mx',
            'direccion': 'Carretera Federal México-Cuernavaca Km 28, Morelos',
            'categoria': 'ingredientes',
            'estado': 'activo',
            'notas': 'Especialistas en vegetales orgánicos. Certificación orgánica vigente.'
        },
        {
            'nombre': 'Bebidas Premium Tokyo',
            'contacto': 'Hiroshi Tanaka',
            'telefono': '+52 55 5555-0123',
            'email': 'h.tanaka@tokyodrinks.com',
            'direccion': 'Polanco Business Center, Ciudad de México',
            'categoria': 'bebidas',
            'estado': 'activo',
            'notas': 'Importador oficial de sake, cerveza japonesa y té verde premium.'
        },
        {
            'nombre': 'Empaques Sustentables EcoBox',
            'contacto': 'Ana Ruiz',
            'telefono': '+52 55 7777-8888',
            'email': 'ana.ruiz@ecobox.mx',
            'direccion': 'Zona Industrial Vallejo, Ciudad de México',
            'categoria': 'empaque',
            'estado': 'activo',
            'notas': 'Contenedores biodegradables y empaques eco-friendly para delivery.'
        },
        {
            'nombre': 'Utensilios Profesionales KitchenPro',
            'contacto': 'Roberto Jiménez',
            'telefono': '+52 55 4444-3333',
            'email': 'roberto@kitchenpro.com.mx',
            'direccion': 'Mercado de San Juan, Centro Histórico, CDMX',
            'categoria': 'utensilios',
            'estado': 'activo',
            'notas': 'Cuchillos japoneses, bambú para sushi, y utensilios especializados.'
        },
        {
            'nombre': 'Limpieza Industrial HygienMax',
            'contacto': 'Patricia López',
            'telefono': '+52 55 2222-1111',
            'email': 'patricia@hygienmax.com',
            'direccion': 'Av. Insurgentes Sur 1234, Benito Juárez, CDMX',
            'categoria': 'limpieza',
            'estado': 'activo',
            'notas': 'Productos de limpieza grado alimentario y desinfectantes industriales.'
        },
        {
            'nombre': 'Equipos de Refrigeración ColdTech',
            'contacto': 'Miguel Vargas',
            'telefono': '+52 55 6666-9999',
            'email': 'miguel@coldtech.mx',
            'direccion': 'Parque Industrial Ecatepec, Estado de México',
            'categoria': 'equipos',
            'estado': 'pendiente',
            'notas': 'Especialistas en refrigeración comercial y mantenimiento de equipos.'
        },
        {
            'nombre': 'Condimentos Asiáticos Yamato',
            'contacto': 'Kenji Yamamoto',
            'telefono': '+52 55 8888-7777',
            'email': 'kenji@yamato.com.mx',
            'direccion': 'Little Tokyo, Zona Rosa, Ciudad de México',
            'categoria': 'ingredientes',
            'estado': 'inactivo',
            'notas': 'Importador de salsas, condimentos y especias japonesas. Temporalmente inactivo.'
        }
    ]
    
    print("Creando proveedores de ejemplo...")
    
    for data in proveedores_data:
        proveedor, created = Proveedor.objects.get_or_create(
            nombre=data['nombre'],
            defaults=data
        )
        
        if created:
            print(f"✅ Creado: {proveedor.nombre}")
        else:
            print(f"📝 Ya existe: {proveedor.nombre}")
    
    # Actualizar fechas para que algunos sean "nuevos este mes"
    print("\nActualizando fechas de registro...")
    
    # Algunos proveedores de este mes
    nuevos_este_mes = Proveedor.objects.filter(
        nombre__in=['Equipos de Refrigeración ColdTech', 'Condimentos Asiáticos Yamato']
    )
    
    for proveedor in nuevos_este_mes:
        proveedor.fecha_registro = datetime.now() - timedelta(days=15)
        proveedor.save()
        print(f"📅 Fecha actualizada: {proveedor.nombre}")
    
    print(f"\n🎉 Proceso completado. Total de proveedores: {Proveedor.objects.count()}")
    print(f"   Activos: {Proveedor.objects.filter(estado='activo').count()}")
    print(f"   Inactivos: {Proveedor.objects.filter(estado='inactivo').count()}")
    print(f"   Pendientes: {Proveedor.objects.filter(estado='pendiente').count()}")

if __name__ == '__main__':
    crear_proveedores_ejemplo()
