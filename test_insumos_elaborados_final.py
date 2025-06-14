#!/usr/bin/env python
"""
Script para probar la creación de insumos elaborados con componentes básicos y compuestos
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_restaurant.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from restaurant.models import Insumo, CategoriaInsumo, UnidadMedida
from accounts.models import Usuario, Rol
from dashboard.views import crear_insumo_elaborado

def test_crear_insumo_elaborado():
    """Probar la creación de un insumo elaborado"""
    
    print("=" * 60)
    print("PRUEBA: Crear insumo elaborado con componentes mixtos")
    print("=" * 60)
    
    # Verificar datos disponibles
    print("\n1. Verificando datos disponibles...")
    
    insumos_basicos = Insumo.objects.filter(tipo='basico', activo=True)
    insumos_compuestos = Insumo.objects.filter(tipo='compuesto', activo=True)
    
    print(f"   - Insumos básicos disponibles: {insumos_basicos.count()}")
    for insumo in insumos_basicos[:3]:
        print(f"     ID {insumo.id}: {insumo.nombre} (${insumo.precio_unitario})")
    
    print(f"   - Insumos compuestos disponibles: {insumos_compuestos.count()}")
    for insumo in insumos_compuestos[:3]:
        print(f"     ID {insumo.id}: {insumo.nombre} (${insumo.precio_unitario})")
    
    if insumos_basicos.count() == 0 and insumos_compuestos.count() == 0:
        print("   ❌ No hay insumos disponibles para usar como componentes")
        return False
    
    # Obtener categoría y unidad de medida
    categoria = CategoriaInsumo.objects.first()
    unidad = UnidadMedida.objects.first()
    
    if not categoria or not unidad:
        print("   ❌ No hay categorías o unidades de medida disponibles")
        return False
    
    print(f"   - Categoría a usar: {categoria.nombre}")
    print(f"   - Unidad a usar: {unidad.nombre}")
    
    # Crear un usuario de prueba para la vista
    try:
        usuario = Usuario.objects.filter(is_superuser=True).first()
        if not usuario:
            print("   ❌ No hay usuario administrador disponible")
            return False
        print(f"   - Usuario: {usuario.username}")
    except Exception as e:
        print(f"   ❌ Error obteniendo usuario: {e}")
        return False
    
    # Configurar el request
    factory = RequestFactory()
    
    # Preparar datos del formulario
    post_data = {
        'nombre': 'Sushi Roll Mixto Test',
        'categoria_id': str(categoria.id),
        'unidad_medida_id': str(unidad.id),
        'cantidad_producida': '8',
        'descripcion': 'Sushi roll con componentes básicos y compuestos',
        'tiempo_total_preparacion': '30'
    }
    
    # Agregar componentes (básicos y compuestos si están disponibles)
    componente_insumos = []
    componente_cantidades = []
    componente_tiempos = []
    componente_instrucciones = []
    
    # Agregar un insumo básico si está disponible
    if insumos_basicos.exists():
        insumo_basico = insumos_basicos.first()
        componente_insumos.append(str(insumo_basico.id))
        componente_cantidades.append('2.5')
        componente_tiempos.append('5')
        componente_instrucciones.append(f'Usar {insumo_basico.nombre} como base')
        print(f"   - Agregando componente básico: {insumo_basico.nombre}")
    
    # Agregar un insumo compuesto si está disponible
    if insumos_compuestos.exists():
        insumo_compuesto = insumos_compuestos.first()
        componente_insumos.append(str(insumo_compuesto.id))
        componente_cantidades.append('1.0')
        componente_tiempos.append('10')
        componente_instrucciones.append(f'Incorporar {insumo_compuesto.nombre}')
        print(f"   - Agregando componente compuesto: {insumo_compuesto.nombre}")
    
    # Si no hay componentes, usar cualquier insumo disponible
    if not componente_insumos:
        cualquier_insumo = Insumo.objects.filter(activo=True).first()
        if cualquier_insumo:
            componente_insumos.append(str(cualquier_insumo.id))
            componente_cantidades.append('1.0')
            componente_tiempos.append('5')
            componente_instrucciones.append('Componente de prueba')
            print(f"   - Agregando componente disponible: {cualquier_insumo.nombre}")
    
    # Agregar componentes al post_data
    post_data['componente_insumo[]'] = componente_insumos
    post_data['componente_cantidad[]'] = componente_cantidades
    post_data['componente_tiempo[]'] = componente_tiempos
    post_data['componente_instrucciones[]'] = componente_instrucciones
    
    print(f"\n2. Datos del formulario preparados...")
    print(f"   - Nombre: {post_data['nombre']}")
    print(f"   - Cantidad a producir: {post_data['cantidad_producida']}")
    print(f"   - Componentes: {len(componente_insumos)}")
    
    # Crear request POST
    request = factory.post('/dashboard/insumos-elaborados/crear/', post_data)
    request.user = usuario
    
    print(f"\n3. Ejecutando vista crear_insumo_elaborado...")
    
    try:
        response = crear_insumo_elaborado(request)
        
        if hasattr(response, 'content'):
            import json
            response_data = json.loads(response.content.decode('utf-8'))
            
            print(f"   - Respuesta recibida")
            print(f"   - Success: {response_data.get('success', False)}")
            print(f"   - Mensaje: {response_data.get('message', 'Sin mensaje')}")
            
            if response_data.get('success'):
                print(f"   - ID del insumo: {response_data.get('insumo_id')}")
                print(f"   - Código: {response_data.get('codigo')}")
                print(f"   - Costo total: ${response_data.get('costo_total', 0):.2f}")
                print(f"   - Precio unitario: ${response_data.get('precio_unitario', 0):.2f}")
                
                # Verificar que se creó en la base de datos
                insumo_creado = Insumo.objects.filter(id=response_data.get('insumo_id')).first()
                if insumo_creado:
                    print(f"   ✅ Insumo creado correctamente en la base de datos")
                    print(f"      - Tipo: {insumo_creado.tipo}")
                    print(f"      - Activo: {insumo_creado.activo}")
                    
                    # Verificar componentes
                    from restaurant.models import InsumoElaborado
                    componentes = InsumoElaborado.objects.filter(insumo_elaborado=insumo_creado)
                    print(f"      - Componentes creados: {componentes.count()}")
                    
                    for comp in componentes:
                        print(f"        * {comp.insumo_componente.nombre} ({comp.insumo_componente.tipo}): {comp.cantidad}")
                    
                    return True
                else:
                    print(f"   ❌ No se encontró el insumo creado en la base de datos")
                    return False
            else:
                print(f"   ❌ Error en la creación: {response_data.get('message')}")
                return False
        else:
            print(f"   ❌ Respuesta inválida: {response}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error ejecutando la vista: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("Iniciando pruebas de insumos elaborados...")
    
    try:
        success = test_crear_insumo_elaborado()
        
        print("\n" + "=" * 60)
        if success:
            print("✅ PRUEBA COMPLETADA CON ÉXITO")
            print("El sistema puede crear insumos elaborados correctamente")
        else:
            print("❌ PRUEBA FALLIDA")
            print("Hay problemas con la creación de insumos elaborados")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error general en las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
