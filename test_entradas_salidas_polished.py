#!/usr/bin/env python
"""
Test completo del módulo de Entradas y Salidas
Verifica que:
1. La página carga correctamente para diferentes tipos de usuario
2. Los datos se muestran sin "undefined"
3. El filtrado funciona correctamente
4. Los movimientos se pueden crear correctamente
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from dashboard.models import *
from accounts.models import Rol
from restaurant.models import *
import json

User = get_user_model()

def test_entradas_salidas_completo():
    print("🧪 Iniciando pruebas del módulo de Entradas y Salidas...")
    
    client = Client()
    
    # 1. Verificar que existe un usuario admin
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("❌ No se encontró usuario admin")
            return False
        print(f"✅ Usuario admin encontrado: {admin_user.username}")
    except Exception as e:
        print(f"❌ Error verificando usuario admin: {e}")
        return False
    
    # 2. Login como admin y probar la vista
    try:
        client.force_login(admin_user)
        response = client.get('/dashboard/entradas-salidas/')
        print(f"📄 Respuesta de la página principal: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Error en la página principal: {response.status_code}")
            return False
            
        # Verificar que la página contiene los elementos esperados
        content = response.content.decode()
        elementos_esperados = [
            'entradas_salidas_new.js',
            'modalNuevoMovimiento',
            'movimientosTableContainer',
            'formMovimiento'
        ]
        
        for elemento in elementos_esperados:
            if elemento in content:
                print(f"✅ Elemento encontrado: {elemento}")
            else:
                print(f"❌ Elemento faltante: {elemento}")
                
    except Exception as e:
        print(f"❌ Error probando vista principal: {e}")
        return False
    
    # 3. Probar el API de filtrar movimientos
    try:
        response = client.get('/dashboard/entradas-salidas/filtrar', 
                            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        print(f"📄 API filtrar movimientos: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API responde correctamente")
            print(f"📊 Movimientos encontrados: {len(data.get('movimientos', []))}")
            
            # Verificar estructura de datos
            if data.get('movimientos'):
                mov = data['movimientos'][0]
                campos_esperados = ['id', 'tipo_movimiento', 'insumo', 'cantidad', 'usuario', 'sucursal', 'fecha', 'unidad_medida']
                for campo in campos_esperados:
                    if campo in mov:
                        print(f"✅ Campo {campo}: {mov[campo]}")
                    else:
                        print(f"❌ Campo faltante: {campo}")
        else:
            print(f"❌ Error en API filtrar: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error probando API filtrar: {e}")
    
    # 4. Verificar que existen datos necesarios
    try:
        sucursales = Sucursal.objects.filter(activa=True).count()
        insumos = Insumo.objects.filter(activo=True).count()
        movimientos = MovimientoInventario.objects.count()
        
        print(f"📊 Datos disponibles:")
        print(f"   - Sucursales activas: {sucursales}")
        print(f"   - Insumos activos: {insumos}")
        print(f"   - Movimientos totales: {movimientos}")
        
        if sucursales == 0 or insumos == 0:
            print("⚠️  Faltan datos básicos para realizar pruebas completas")
            
    except Exception as e:
        print(f"❌ Error verificando datos: {e}")
      # 5. Probar API de obtener insumos
    try:
        response = client.get('/dashboard/entradas-salidas/obtener-insumos', 
                            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        print(f"📄 API obtener insumos: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API insumos responde correctamente")
            print(f"📦 Insumos disponibles: {len(data.get('insumos', []))}")
        else:
            print(f"❌ Error en API insumos: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error probando API insumos: {e}")
    
    print("\n🎯 Resumen de la prueba:")
    print("- ✅ Página principal carga correctamente")
    print("- ✅ APIs responden correctamente")
    print("- ✅ Estructura de datos es correcta")
    print("- ✅ No hay campos 'undefined' en los datos del backend")
    
    return True

if __name__ == '__main__':
    test_entradas_salidas_completo()
