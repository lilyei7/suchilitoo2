#!/usr/bin/env python3
"""
Script para probar el sistema completo de insumos compuestos
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from restaurant.models import Insumo, CategoriaInsumo, UnidadMedida, InsumoCompuesto
import json

User = get_user_model()

def test_basic_setup():
    """Verifica que la configuración básica esté en orden"""
    print("🔍 VERIFICACIÓN BÁSICA DEL SISTEMA")
    print("="*50)
    
    # Verificar que existan categorías
    categorias = CategoriaInsumo.objects.count()
    print(f"📊 Categorías disponibles: {categorias}")
    
    # Verificar que existan unidades de medida
    unidades = UnidadMedida.objects.count()
    print(f"📊 Unidades de medida: {unidades}")
    
    # Verificar que existan insumos básicos
    insumos_basicos = Insumo.objects.filter(tipo='basico').count()
    print(f"📊 Insumos básicos: {insumos_basicos}")
    
    # Verificar que existan insumos compuestos
    insumos_compuestos = Insumo.objects.filter(tipo='compuesto').count()
    print(f"📊 Insumos compuestos: {insumos_compuestos}")
    
    return categorias > 0 and unidades > 0 and insumos_basicos > 0

def test_form_data_endpoint():
    """Prueba el endpoint de datos del formulario"""
    print("\n🔍 PRUEBA: ENDPOINT DE DATOS DEL FORMULARIO")
    print("="*50)
    
    user, _ = User.objects.get_or_create(username='test_user')
    client = Client()
    client.force_login(user)
    
    try:
        response = client.get('/dashboard/insumos/form-data/')
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content.decode('utf-8'))
            print(f"📥 Categorías: {len(data.get('categorias', []))}")
            print(f"📥 Unidades: {len(data.get('unidades_medida', []))}")
            print("✅ Endpoint de form-data funciona")
            return True
        else:
            print(f"❌ Status incorrecto: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

def test_insumos_basicos_endpoint():
    """Prueba el endpoint de insumos básicos"""
    print("\n🔍 PRUEBA: ENDPOINT DE INSUMOS BÁSICOS")
    print("="*50)
    
    user, _ = User.objects.get_or_create(username='test_user')
    client = Client()
    client.force_login(user)
    
    try:
        response = client.get('/dashboard/insumos-compuestos/insumos-basicos/')
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content.decode('utf-8'))
            print(f"📥 Insumos básicos disponibles: {len(data.get('insumos', []))}")
            
            if data.get('insumos'):
                print(f"📥 Ejemplo: {data['insumos'][0]['nombre']}")
            
            print("✅ Endpoint de insumos básicos funciona")
            return True
        else:
            print(f"❌ Status incorrecto: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

def test_page_load():
    """Prueba que la página de insumos compuestos cargue correctamente"""
    print("\n🔍 PRUEBA: CARGA DE PÁGINA")
    print("="*50)
    
    user, _ = User.objects.get_or_create(username='test_user')
    client = Client()
    client.force_login(user)
    
    try:
        response = client.get('/dashboard/insumos-compuestos/')
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Verificar elementos clave en la página
            checks = [
                ('Modal de crear', 'crearCompuestoModal' in content),
                ('Botón crear', 'abrirModalCrearCompuesto' in content),
                ('JavaScript', 'actualizarCostos' in content),
                ('Tabla de compuestos', 'table table-hover' in content)
            ]
            
            print("📥 Verificaciones de contenido:")
            all_good = True
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"   {status} {check_name}: {'OK' if result else 'FALTA'}")
                if not result:
                    all_good = False
            
            if all_good:
                print("✅ Página carga correctamente")
                return True
            else:
                print("❌ Faltan elementos en la página")
                return False
        else:
            print(f"❌ Status incorrecto: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

def test_create_sample_compuesto():
    """Prueba crear un insumo compuesto de ejemplo"""
    print("\n🔍 PRUEBA: CREAR INSUMO COMPUESTO")
    print("="*50)
    
    # Verificar que tengamos los datos necesarios
    categoria = CategoriaInsumo.objects.first()
    unidad = UnidadMedida.objects.first()
    insumos_basicos = Insumo.objects.filter(tipo='basico')[:2]
    
    if not categoria or not unidad or len(insumos_basicos) < 2:
        print("❌ No hay suficientes datos básicos para crear el compuesto")
        return False
    
    user, _ = User.objects.get_or_create(username='test_admin')
    user.is_superuser = True
    user.save()
    
    client = Client()
    client.force_login(user)
    
    # Datos para crear el insumo compuesto
    data = {
        'codigo': 'COMP-TEST-001',
        'nombre': 'Salsa de Prueba Compuesta',
        'categoria_id': categoria.id,
        'unidad_medida_id': unidad.id,
        'cantidad_producida': '1.000',
        'descripcion': 'Insumo compuesto de prueba creado automáticamente',
        'componente_insumo[]': [insumos_basicos[0].id, insumos_basicos[1].id],
        'componente_cantidad[]': ['0.500', '0.250']
    }
    
    print(f"📤 Creando insumo compuesto:")
    print(f"   Nombre: {data['nombre']}")
    print(f"   Código: {data['codigo']}")
    print(f"   Componentes: {len(data['componente_insumo[]'])}")
    
    try:
        response = client.post('/dashboard/insumos-compuestos/crear/', data)
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = json.loads(response.content.decode('utf-8'))
            print(f"📥 Respuesta: {response_data}")
            
            if response_data.get('success'):
                print("✅ Insumo compuesto creado exitosamente")
                
                # Verificar en la base de datos
                compuesto = Insumo.objects.filter(codigo='COMP-TEST-001').first()
                if compuesto:
                    print(f"✅ Verificado en BD: {compuesto.nombre}")
                    print(f"   Componentes: {compuesto.componentes.count()}")
                    return True
                else:
                    print("❌ No se encontró en la BD")
                    return False
            else:
                print(f"❌ Error en la creación: {response_data.get('message')}")
                return False
        else:
            print(f"❌ Status incorrecto: {response.status_code}")
            print(f"   Content: {response.content.decode('utf-8')[:200]}...")
            return False
            
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 PRUEBAS COMPLETAS DEL SISTEMA DE INSUMOS COMPUESTOS")
    print("="*60)
    
    tests = [
        ("Configuración básica", test_basic_setup),
        ("Endpoint form-data", test_form_data_endpoint),
        ("Endpoint insumos básicos", test_insumos_basicos_endpoint),
        ("Carga de página", test_page_load),
        ("Crear insumo compuesto", test_create_sample_compuesto)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🎯 Ejecutando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"   {'✅ ÉXITO' if result else '❌ FALLO'}")
        except Exception as e:
            print(f"   💥 ERROR: {e}")
            results.append((test_name, False))
    
    print(f"\n🎯 RESUMEN DE RESULTADOS:")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🏆 RESULTADO FINAL: {passed}/{len(results)} pruebas exitosas")
    
    if passed == len(results):
        print(f"\n🎉 ¡TODO PERFECTO! El sistema de insumos compuestos está listo.")
        print(f"   Puedes probarlo en: http://localhost:8000/dashboard/insumos-compuestos/")
    elif passed > len(results) // 2:
        print(f"\n⚠️  La mayoría de las pruebas pasaron. Revisar los fallos menores.")
    else:
        print(f"\n❌ Hay problemas importantes que necesitan atención.")

if __name__ == '__main__':
    main()
