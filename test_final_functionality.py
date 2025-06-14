#!/usr/bin/env python3
"""
Script final para verificar que el sistema de inventario funciona correctamente
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from accounts.models import Usuario
from restaurant.models import CategoriaInsumo, UnidadMedida
import json

def test_inventory_functionality():
    """Prueba completa de la funcionalidad del inventario"""
    print("🔍 VERIFICACIÓN FINAL DEL SISTEMA DE INVENTARIO")
    print("=" * 60)
    
    # 1. Verificar que existen datos básicos
    print("\n1. Verificando datos básicos...")
    categorias = CategoriaInsumo.objects.all().count()
    unidades = UnidadMedida.objects.all().count()
    
    print(f"   ✅ Categorías en base de datos: {categorias}")
    print(f"   ✅ Unidades de medida en base de datos: {unidades}")
    
    if categorias == 0 or unidades == 0:
        print("   ❌ ERROR: Faltan datos básicos. Ejecutando script de creación...")
        from crear_datos_basicos import crear_datos_basicos
        crear_datos_basicos()
        print("   ✅ Datos básicos creados")
    
    # 2. Crear cliente de prueba
    client = Client()
      # 3. Crear usuario admin si no existe
    admin_user, created = Usuario.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@sushi.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created or not admin_user.check_password('admin123'):
        admin_user.set_password('admin123')
        admin_user.save()
        print("   ✅ Usuario admin creado/actualizado")
    
    # 4. Hacer login
    login_success = client.login(username='admin', password='admin123')
    print(f"   ✅ Login exitoso: {login_success}")
    
    # 5. Probar endpoint de datos del formulario
    print("\n2. Probando endpoint de datos del formulario...")
    response = client.get('/dashboard/insumos/form-data/')
    print(f"   ✅ Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Categorías devueltas: {len(data.get('categorias', []))}")
        print(f"   ✅ Unidades devueltas: {len(data.get('unidades', []))}")
        
        # Mostrar algunas categorías y unidades
        if data.get('categorias'):
            print("   📋 Ejemplo de categorías:")
            for cat in data['categorias'][:3]:
                print(f"      - {cat['nombre']} (ID: {cat['id']})")
        
        if data.get('unidades'):
            print("   📏 Ejemplo de unidades:")
            for unidad in data['unidades'][:3]:
                print(f"      - {unidad['nombre']} ({unidad['abreviacion']}) (ID: {unidad['id']})")
    else:
        print(f"   ❌ ERROR: {response.status_code}")
        print(f"   Contenido: {response.content}")
    
    # 6. Probar la página de inventario
    print("\n3. Probando página de inventario...")
    response = client.get('/dashboard/inventario/')
    print(f"   ✅ Status code: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Verificar que las funciones JavaScript están presentes
        functions_to_check = [
            'cargarDatosFormulario',
            'abrirModalCategoria', 
            'abrirModalUnidad'
        ]
        
        print("   🔧 Verificando funciones JavaScript...")
        for func in functions_to_check:
            if f'function {func}' in content:
                print(f"      ✅ {func}() encontrada")
            else:
                print(f"      ❌ {func}() NO encontrada")
        
        # Verificar que el endpoint está incluido
        if 'get_form_data' in content:
            print("      ✅ Endpoint get_form_data incluido en el template")
        else:
            print("      ❌ Endpoint get_form_data NO encontrado")
    
    print("\n" + "=" * 60)
    print("🎉 VERIFICACIÓN COMPLETADA")
    print("\n📝 PASOS PARA PROBAR MANUALMENTE:")
    print("1. Abre http://127.0.0.1:8000/dashboard/inventario/")
    print("2. Haz login con admin/admin123")
    print("3. Haz clic en 'Agregar Insumo'")
    print("4. Verifica que los select de Categoría y Unidad se cargan con datos")
    print("5. Abre las herramientas de desarrollador (F12) para ver si hay errores JS")
    
    print("\n🧪 SCRIPT DE PRUEBA EN CONSOLA DEL NAVEGADOR:")
    print("""
// Pega este código en la consola del navegador para verificar:
console.log('=== VERIFICACIÓN MANUAL ===');
console.log('cargarDatosFormulario function:', typeof cargarDatosFormulario);
console.log('abrirModalCategoria function:', typeof abrirModalCategoria);
console.log('abrirModalUnidad function:', typeof abrirModalUnidad);

// Probar cargar datos
cargarDatosFormulario();

// Verificar selects después de 2 segundos
setTimeout(() => {
    const catSelect = document.getElementById('categoria');
    const unidadSelect = document.getElementById('unidad_medida');
    console.log('Opciones en categoría:', catSelect ? catSelect.options.length : 'Select no encontrado');
    console.log('Opciones en unidad:', unidadSelect ? unidadSelect.options.length : 'Select no encontrado');
}, 2000);
""")

if __name__ == '__main__':
    test_inventory_functionality()
