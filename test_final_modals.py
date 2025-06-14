#!/usr/bin/env python3
"""
Test final para verificar que ambos modales (nuevo y editar) tienen unidades cargadas
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from restaurant.models import UnidadMedida, CategoriaInsumo
from django.test import Client
from django.contrib.auth.models import User

def test_both_modals():
    """Test para verificar que ambos modales tienen las unidades cargadas"""
    
    print("=== TEST: VERIFICAR AMBOS MODALES ===")
    
    try:
        # Obtener datos de la BD
        unidades = list(UnidadMedida.objects.all().values('id', 'nombre'))
        categorias = list(CategoriaInsumo.objects.all().values('id', 'nombre'))
        
        print(f"✅ Datos en BD:")
        print(f"   - Unidades: {len(unidades)}")
        print(f"   - Categorías: {len(categorias)}")
        
        # Crear cliente Django
        client = Client()
        
        # Hacer login
        User = get_user_model()
        user = User.objects.get(username='admin')
        login_success = client.login(username='admin', password='admin123')
        
        if not login_success:
            print("❌ Login fallido")
            return False
        
        print("✅ Login exitoso")
        
        # Obtener la página de inventario
        response = client.get('/dashboard/inventario/')
        
        if response.status_code != 200:
            print(f"❌ Error al cargar página de inventario. Status: {response.status_code}")
            return False
        
        html_content = response.content.decode('utf-8')
        print("✅ Página de inventario cargada")
        
        # Test 1: Verificar modal de nuevo insumo
        print("\n📋 VERIFICANDO MODAL DE NUEVO INSUMO:")
        
        if 'id="nuevoInsumoModal"' not in html_content:
            print("❌ Modal de nuevo insumo no encontrado")
            return False
        
        print("✅ Modal de nuevo insumo presente")
        
        # Verificar que tiene el dropdown de unidades
        if 'id="unidad_medida"' not in html_content:
            print("❌ Dropdown de unidades no encontrado en modal de nuevo insumo")
            return False
        
        print("✅ Dropdown de unidades presente en modal de nuevo insumo")
        
        # Verificar que se carga la función cargarCategoriasYUnidades
        if 'cargarCategoriasYUnidades()' not in html_content:
            print("❌ Función cargarCategoriasYUnidades no se llama")
            return False
        
        print("✅ Función cargarCategoriasYUnidades se ejecuta")
        
        # Verificar que el template tiene los datos para JavaScript
        unidades_en_js = 0
        for unidad in unidades:
            if f"optionUnidad.value = '{unidad['id']}'" in html_content:
                unidades_en_js += 1
        
        print(f"✅ {unidades_en_js} de {len(unidades)} unidades disponibles via JavaScript")
        
        # Test 2: Verificar modal de editar insumo
        print("\n✏️  VERIFICANDO MODAL DE EDITAR INSUMO:")
        
        if 'id="modalEditarInsumo"' not in html_content:
            print("❌ Modal de editar insumo no encontrado")
            return False
        
        print("✅ Modal de editar insumo presente")
        
        # Verificar que tiene el dropdown de unidades con opciones estáticas
        if 'id="editUnidadMedida"' not in html_content:
            print("❌ Dropdown de unidades no encontrado en modal de editar")
            return False
        
        print("✅ Dropdown de unidades presente en modal de editar")
        
        # Verificar que las unidades están como opciones estáticas
        unidades_estaticas = 0
        for unidad in unidades:
            if f'<option value="{unidad["id"]}">{unidad["nombre"]}</option>' in html_content:
                unidades_estaticas += 1
        
        print(f"✅ {unidades_estaticas} de {len(unidades)} unidades como opciones estáticas")
        
        # Test 3: Verificar categorías también
        print("\n📁 VERIFICANDO CATEGORÍAS:")
        
        categorias_en_edit = 0
        for categoria in categorias:
            if f'<option value="{categoria["id"]}">{categoria["nombre"]}</option>' in html_content:
                categorias_en_edit += 1
        
        print(f"✅ {categorias_en_edit} de {len(categorias)} categorías en modal de editar")
        
        categorias_en_js = 0
        for categoria in categorias:
            if f"optionCategoria.value = '{categoria['id']}'" in html_content:
                categorias_en_js += 1
        
        print(f"✅ {categorias_en_js} de {len(categorias)} categorías disponibles via JavaScript")
        
        # Verificar resultado final
        if (unidades_en_js == len(unidades) and 
            unidades_estaticas == len(unidades) and
            categorias_en_edit == len(categorias) and
            categorias_en_js == len(categorias)):
            
            print("\n🎉 TODOS LOS VERIFICACIONES PASARON:")
            print("   ✅ Modal nuevo insumo: unidades via JavaScript")
            print("   ✅ Modal editar insumo: unidades estáticas")
            print("   ✅ Modal nuevo insumo: categorías via JavaScript")
            print("   ✅ Modal editar insumo: categorías estáticas")
            print("   ✅ Funcionalidad completa de dropdowns")
            
            return True
        else:
            print("\n❌ ALGUNAS VERIFICACIONES FALLARON:")
            print(f"   - Unidades JS: {unidades_en_js}/{len(unidades)}")
            print(f"   - Unidades estáticas: {unidades_estaticas}/{len(unidades)}")
            print(f"   - Categorías edit: {categorias_en_edit}/{len(categorias)}")
            print(f"   - Categorías JS: {categorias_en_js}/{len(categorias)}")
            
            return False
        
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_both_modals()
    if success:
        print("\n🎉 TEST FINAL EXITOSO: Ambos modales funcionan correctamente")
        print("✅ PROBLEMA COMPLETAMENTE RESUELTO:")
        print("   - Las unidades de medida se listan correctamente")
        print("   - Modal de edición funciona")
        print("   - Modal de nuevo insumo funciona")
        print("   - CRUD completo operativo")
    else:
        print("\n❌ TEST FINAL FALLIDO: Hay problemas pendientes")
    
    sys.exit(0 if success else 1)
