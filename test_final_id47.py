#!/usr/bin/env python
"""
Prueba final de creación de insumo elaborado con el ID 47
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Insumo, CategoriaInsumo, UnidadMedida, InsumoElaborado
from django.test import RequestFactory
from accounts.models import Usuario
from dashboard.views import crear_insumo_elaborado

def test_insumo_47():
    """Probar específicamente con el insumo ID 47"""
    
    print("🧪 PRUEBA FINAL: Crear insumo elaborado con ID 47")
    print("=" * 55)
    
    # Verificar que el insumo 47 existe y es válido
    print("1. Verificando insumo ID 47...")
    try:
        insumo_47 = Insumo.objects.get(id=47)
        print(f"   ✅ Encontrado: {insumo_47.nombre} ({insumo_47.codigo})")
        print(f"   - Tipo: '{insumo_47.tipo}'")
        print(f"   - Activo: {insumo_47.activo}")
        print(f"   - Precio: ${insumo_47.precio_unitario}")
    except Insumo.DoesNotExist:
        print("   ❌ Insumo ID 47 no existe")
        return False
    
    # Probar el filtro exacto de la vista
    print("\n2. Probando filtro de la vista...")
    resultado_filtro = Insumo.objects.filter(
        id=47, 
        tipo__in=['basico', 'compuesto'],
        activo=True
    )
    
    if resultado_filtro.exists():
        print("   ✅ El filtro encuentra el insumo correctamente")
        insumo_encontrado = resultado_filtro.first()
        print(f"   - Nombre: {insumo_encontrado.nombre}")
        print(f"   - Tipo: {insumo_encontrado.tipo}")
    else:
        print("   ❌ El filtro NO encuentra el insumo")
        return False
    
    # Obtener datos necesarios para crear un insumo elaborado
    print("\n3. Preparando datos para insumo elaborado...")
    
    categoria = CategoriaInsumo.objects.first()
    unidad = UnidadMedida.objects.first()
    usuario = Usuario.objects.filter(is_superuser=True).first()
    
    if not all([categoria, unidad, usuario]):
        print("   ❌ Faltan datos básicos (categoría, unidad o usuario)")
        return False
    
    print(f"   - Categoría: {categoria.nombre}")
    print(f"   - Unidad: {unidad.nombre}")
    print(f"   - Usuario: {usuario.username}")
    
    # Simular el POST request
    print("\n4. Simulando creación de insumo elaborado...")
    
    factory = RequestFactory()
    post_data = {
        'nombre': 'Test Roll con Aguacate ID47',
        'categoria_id': str(categoria.id),
        'unidad_medida_id': str(unidad.id),
        'cantidad_producida': '6',
        'descripcion': 'Roll de prueba usando aguacate ID 47',
        'tiempo_total_preparacion': '25',
        'componente_insumo[]': [str(47)],  # Usar específicamente el ID 47
        'componente_cantidad[]': ['2.0'],
        'componente_tiempo[]': ['10'],
        'componente_instrucciones[]': ['Cortar aguacate en láminas']
    }
    
    request = factory.post('/dashboard/insumos-elaborados/crear/', post_data)
    request.user = usuario
    
    print("   - Datos del formulario:")
    print(f"     * Componente ID: 47")
    print(f"     * Cantidad: 2.0")
    print(f"     * Esperando precio total: {float(insumo_47.precio_unitario) * 2.0}")
    
    # Ejecutar la vista
    print("\n5. Ejecutando vista crear_insumo_elaborado...")
    
    try:
        response = crear_insumo_elaborado(request)
        
        if hasattr(response, 'content'):
            import json
            response_data = json.loads(response.content.decode('utf-8'))
            
            print(f"   - Success: {response_data.get('success')}")
            print(f"   - Mensaje: {response_data.get('message')}")
            
            if response_data.get('success'):
                print(f"   ✅ ÉXITO: Insumo elaborado creado")
                print(f"   - ID creado: {response_data.get('insumo_id')}")
                print(f"   - Código: {response_data.get('codigo')}")
                print(f"   - Costo total: ${response_data.get('costo_total', 0):.2f}")
                print(f"   - Precio unitario: ${response_data.get('precio_unitario', 0):.2f}")
                
                # Verificar en la base de datos
                insumo_creado = Insumo.objects.filter(id=response_data.get('insumo_id')).first()
                if insumo_creado:
                    componentes = InsumoElaborado.objects.filter(insumo_elaborado=insumo_creado)
                    print(f"   - Componentes en BD: {componentes.count()}")
                    
                    for comp in componentes:
                        print(f"     * {comp.insumo_componente.nombre} (ID {comp.insumo_componente.id}): {comp.cantidad}")
                
                return True
            else:
                print(f"   ❌ ERROR: {response_data.get('message')}")
                return False
        else:
            print(f"   ❌ Respuesta inválida")
            return False
            
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    try:
        success = test_insumo_47()
        
        print("\n" + "=" * 55)
        if success:
            print("🎉 PRUEBA COMPLETADA CON ÉXITO")
            print("El insumo ID 47 funciona correctamente")
            print("El error 'insumo compuesto con ID 47 no existe' está RESUELTO")
        else:
            print("❌ PRUEBA FALLIDA")
            print("Aún hay problemas con el insumo ID 47")
        print("=" * 55)
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
