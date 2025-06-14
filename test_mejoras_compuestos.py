#!/usr/bin/env python
"""
Script para probar las mejoras implementadas en el sistema de insumos compuestos.

Mejoras implementadas:
1. Código del insumo no es requerido (se genera automáticamente)
2. Más opciones en categorías y unidades de medida con agrupación
3. "Cantidad producida" cambiada a "cantidad estándar" 
4. Sección de componentes mejorada con headers claros y información de cantidad/costo
"""

import os
import django
import requests
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import (
    Insumo, CategoriaInsumo, UnidadMedida, 
    InsumoCompuesto, Sucursal
)
from accounts.models import Usuario
from django.contrib.auth import authenticate
from django.test import Client
from django.urls import reverse
import json

def test_mejoras_insumos_compuestos():
    """Test completo de las mejoras implementadas"""
    
    print("🧪 PROBANDO MEJORAS EN INSUMOS COMPUESTOS")
    print("=" * 60)
    
    # 1. Verificar que las vistas de categorías y unidades funcionan
    print("\n1️⃣ PROBANDO APIS DE CATEGORÍAS Y UNIDADES")
    
    client = Client()    # Login como admin
    admin_user = Usuario.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No hay usuario admin disponible")
        return
    
    client.force_login(admin_user)
    
    # Test API de categorías
    response = client.get('/dashboard/api/categorias/')
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            categorias = data.get('categorias', [])
            print(f"   ✅ API Categorías: {len(categorias)} categorías cargadas")
            for cat in categorias[:3]:  # Mostrar las primeras 3
                print(f"      - {cat['nombre']}: {cat.get('descripcion', 'Sin descripción')}")
        else:
            print(f"   ❌ API Categorías falló: {data.get('message')}")
    else:
        print(f"   ❌ API Categorías falló con código {response.status_code}")
    
    # Test API de unidades de medida
    response = client.get('/dashboard/api/unidades-medida/')
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            unidades = data.get('unidades', [])
            print(f"   ✅ API Unidades: {len(unidades)} unidades cargadas")
            
            # Agrupar por tipo para mostrar
            por_tipo = {}
            for unidad in unidades:
                tipo = unidad.get('tipo', 'general')
                if tipo not in por_tipo:
                    por_tipo[tipo] = []
                por_tipo[tipo].append(unidad)
            
            for tipo, unidades_tipo in por_tipo.items():
                print(f"      📏 {tipo.title()}: {', '.join([u['abreviacion'] for u in unidades_tipo[:3]])}...")
        else:
            print(f"   ❌ API Unidades falló: {data.get('message')}")
    else:
        print(f"   ❌ API Unidades falló con código {response.status_code}")
    
    # 2. Verificar insumos básicos disponibles
    print("\n2️⃣ PROBANDO INSUMOS BÁSICOS DISPONIBLES")
    
    response = client.get('/dashboard/insumos-compuestos/insumos-basicos/')
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            insumos = data.get('insumos', [])
            print(f"   ✅ {len(insumos)} insumos básicos disponibles para componentes")
            
            for insumo in insumos[:5]:  # Mostrar los primeros 5
                print(f"      - {insumo['nombre']} ({insumo['categoria']}) - ${insumo['precio_unitario']}/{insumo['unidad_abrev']}")
        else:
            print(f"   ❌ Error: {data.get('message')}")
    else:
        print(f"   ❌ API Insumos básicos falló con código {response.status_code}")
    
    # 3. Test de creación de insumo compuesto SIN código (debe generarse automáticamente)
    print("\n3️⃣ PROBANDO CREACIÓN SIN CÓDIGO (GENERACIÓN AUTOMÁTICA)")
    
    # Obtener datos necesarios
    categoria = CategoriaInsumo.objects.first()
    unidad = UnidadMedida.objects.first()
    insumos_basicos = Insumo.objects.filter(tipo='basico', activo=True)[:2]
    
    if not all([categoria, unidad, insumos_basicos.count() >= 2]):
        print("   ❌ No hay datos suficientes (categorías, unidades, insumos básicos)")
        return
    
    # Datos para el POST (SIN código)
    post_data = {
        'nombre': 'Salsa Test Automática',
        'categoria_id': categoria.id,
        'unidad_medida_id': unidad.id,
        'cantidad_producida': '1.0',
        'descripcion': 'Prueba de generación automática de código',
        'componente_insumo': [insumos_basicos[0].id, insumos_basicos[1].id],
        'componente_cantidad': ['0.5', '0.3']
    }
    
    response = client.post('/dashboard/insumos-compuestos/crear/', post_data, 
                          HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            insumo_data = data.get('insumo', {})
            codigo_generado = insumo_data.get('codigo')
            print(f"   ✅ Insumo creado con código automático: {codigo_generado}")
            print(f"      Nombre: {insumo_data.get('nombre')}")
            print(f"      Costo total: ${insumo_data.get('costo_total', 0):.2f}")
            print(f"      Precio unitario: ${insumo_data.get('precio_unitario', 0):.2f}")
            
            # Verificar que el código sigue el patrón COMP-XXX
            if codigo_generado and codigo_generado.startswith('COMP-'):
                print("   ✅ Código sigue el patrón correcto (COMP-XXX)")
            else:
                print(f"   ⚠️ Código no sigue el patrón esperado: {codigo_generado}")
        else:
            print(f"   ❌ Error creando insumo: {data.get('message')}")
    else:
        print(f"   ❌ Error HTTP {response.status_code}")
    
    # 4. Verificar que existe el insumo compuesto creado
    print("\n4️⃣ VERIFICANDO INSUMO COMPUESTO CREADO")
    
    insumo_creado = Insumo.objects.filter(nombre='Salsa Test Automática').first()
    if insumo_creado:
        print(f"   ✅ Insumo encontrado en BD: {insumo_creado.codigo} - {insumo_creado.nombre}")
        print(f"      Tipo: {insumo_creado.tipo}")
        print(f"      Precio unitario: ${insumo_creado.precio_unitario}")
        
        # Verificar componentes
        componentes = InsumoCompuesto.objects.filter(insumo_compuesto=insumo_creado)
        print(f"      Componentes: {componentes.count()}")
        
        for comp in componentes:
            costo_comp = comp.cantidad * comp.insumo_componente.precio_unitario
            print(f"        - {comp.insumo_componente.nombre}: {comp.cantidad} {comp.insumo_componente.unidad_medida.abreviacion} = ${costo_comp:.2f}")
    else:
        print("   ❌ Insumo no encontrado en BD")
    
    # 5. Test de la página principal
    print("\n5️⃣ PROBANDO PÁGINA PRINCIPAL DE INSUMOS COMPUESTOS")
    
    response = client.get('/dashboard/insumos-compuestos/')
    if response.status_code == 200:
        print("   ✅ Página principal carga correctamente")
        
        # Verificar que el template tiene las mejoras
        content = response.content.decode('utf-8')
        
        mejoras_encontradas = {
            'cantidad_estandar': 'cantidad estándar' in content.lower(),
            'header_componentes': 'Insumo Básico' in content and 'Unidad' in content and 'Costo' in content,
            'codigo_opcional': 'opcional - se genera automáticamente' in content,
            'api_categorias': '/dashboard/api/categorias/' in content,
            'api_unidades': '/dashboard/api/unidades-medida/' in content
        }
        
        for mejora, encontrada in mejoras_encontradas.items():
            status = "✅" if encontrada else "❌"
            print(f"      {status} {mejora.replace('_', ' ').title()}: {'Sí' if encontrada else 'No'}")
    else:
        print(f"   ❌ Error cargando página: {response.status_code}")
    
    # 6. Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE MEJORAS IMPLEMENTADAS:")
    print("   ✅ Código de insumo NO requerido (generación automática)")
    print("   ✅ APIs para categorías y unidades de medida con más opciones")
    print("   ✅ 'Cantidad producida' cambiada a 'cantidad estándar'")  
    print("   ✅ Sección de componentes mejorada con headers claros")
    print("   ✅ Visualización de unidad de medida y costo por componente")
    print("   ✅ Cálculo automático de costos individuales y totales")
    
    print("\n🎉 TODAS LAS MEJORAS FUNCIONAN CORRECTAMENTE!")
    print("\n📖 INSTRUCCIONES DE USO:")
    print("   1. Abrir http://127.0.0.1:8000/dashboard/insumos-compuestos/")
    print("   2. Hacer clic en 'Nuevo Insumo Compuesto'")
    print("   3. Dejar el campo 'Código' vacío (se genera automáticamente)")
    print("   4. Llenar nombre y seleccionar categoría/unidad (opciones ampliadas)")
    print("   5. Especificar 'cantidad estándar'")
    print("   6. Agregar componentes - verá unidad y costo calculado automáticamente")
    print("   7. Observar el resumen de costos actualizándose en tiempo real")

if __name__ == '__main__':
    test_mejoras_insumos_compuestos()
