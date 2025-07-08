#!/usr/bin/env python3
"""
Script para probar el modelo TiempoPreparacion
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

# Importar el modelo de usuario personalizado
from accounts.models import Usuario

def probar_modelo_tiempopreparacion():
    """Probar las consultas al modelo TiempoPreparacion"""
    print("=== PRUEBA DEL MODELO TIEMPOPREPARACION ===\n")
    
    try:
        from cocina.models import TiempoPreparacion
        from django.db.models import Avg
        
        print("1. Importación exitosa del modelo TiempoPreparacion")
        
        # Probar consulta básica
        print("2. Probando consulta básica...")
        count = TiempoPreparacion.objects.count()
        print(f"   Total registros: {count}")
        
        # Probar consulta aggregate que está causando problemas
        print("3. Probando consulta aggregate...")
        try:
            tiempo_promedio = TiempoPreparacion.objects.aggregate(
                promedio=Avg('tiempo_promedio')
            )['promedio'] or 0
            print(f"   Tiempo promedio: {tiempo_promedio}")
        except Exception as e:
            print(f"   ❌ Error en aggregate: {e}")
            return False
        
        # Probar otras consultas
        print("4. Probando otras consultas...")
        try:
            # Primera consulta
            primer_registro = TiempoPreparacion.objects.first()
            if primer_registro:
                print(f"   Primer registro: {primer_registro}")
            else:
                print("   No hay registros")
            
            # Listar algunos registros
            registros = TiempoPreparacion.objects.all()[:5]
            print(f"   Primeros 5 registros:")
            for i, registro in enumerate(registros, 1):
                print(f"     {i}. {registro}")
            
        except Exception as e:
            print(f"   ❌ Error en consultas adicionales: {e}")
        
        print("\n✅ Todas las pruebas del modelo pasaron exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error importando o usando TiempoPreparacion: {e}")
        import traceback
        traceback.print_exc()
        return False

def probar_vista_dashboard():
    """Probar la vista del dashboard"""
    print("\n=== PRUEBA DE LA VISTA DASHBOARD ===\n")
    
    try:
        from cocina.views import dashboard
        from django.http import HttpRequest
        from django.utils import timezone
        
        print("1. Importación de vista exitosa")
        
        # Crear un request mock
        request = HttpRequest()
        request.method = 'GET'
        request.user = Usuario.objects.filter(is_superuser=True).first()
        
        if not request.user:
            print("   ⚠ No hay superusuario disponible, creando usuario de prueba")
            request.user = Usuario.objects.create_user(
                username='test_cocina',
                password='test123',
                is_staff=True,
                is_superuser=True
            )
        
        print(f"2. Usuario de prueba: {request.user.username}")
        
        # Intentar ejecutar la vista
        print("3. Ejecutando vista dashboard...")
        try:
            response = dashboard(request)
            print(f"   ✅ Vista ejecutada exitosamente (status: {response.status_code if hasattr(response, 'status_code') else 'OK'})")
            return True
        except Exception as e:
            print(f"   ❌ Error ejecutando vista: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de vista: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🧪 PRUEBAS PARA DIAGNOSTICAR ERROR DE COCINA")
    print("=" * 60)
    
    # Probar modelo
    modelo_ok = probar_modelo_tiempopreparacion()
    
    # Probar vista solo si el modelo funciona
    if modelo_ok:
        vista_ok = probar_vista_dashboard()
    else:
        print("\n⚠ Saltando prueba de vista debido a errores en el modelo")
        vista_ok = False
    
    print("\n" + "=" * 60)
    if modelo_ok and vista_ok:
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("El problema debe estar en otra parte (tal vez permisos o datos)")
    else:
        print("❌ SE ENCONTRARON PROBLEMAS")
        print("\n🔧 SOLUCIONES RECOMENDADAS:")
        if not modelo_ok:
            print("1. Verificar las migraciones: python manage.py migrate")
            print("2. Recrear datos de cocina: python configurar_cocina.py")
        if not vista_ok:
            print("3. Verificar permisos de usuario de cocina")
            print("4. Verificar que el usuario esté en el grupo 'Cocina'")

if __name__ == '__main__':
    main()
