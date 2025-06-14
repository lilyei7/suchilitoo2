#!/usr/bin/env python
"""
Script para probar el sistema de insumos elaborados
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Insumo, InsumoElaborado, CategoriaInsumo, UnidadMedida

def probar_insumos_elaborados():
    """Probar creación de insumos elaborados"""
    print("🍣 Probando sistema de insumos elaborados...")
    
    # Verificar insumos compuestos disponibles
    insumos_compuestos = Insumo.objects.filter(tipo='compuesto', activo=True)
    print(f"\n📋 Insumos compuestos disponibles: {insumos_compuestos.count()}")
    for insumo in insumos_compuestos[:5]:  # Mostrar solo los primeros 5
        print(f"   • {insumo.codigo} - {insumo.nombre} (${insumo.precio_unitario:.2f}/{insumo.unidad_medida.abreviacion})")
    
    # Crear categoría para platos elaborados
    categoria_platos, _ = CategoriaInsumo.objects.get_or_create(
        nombre="Platos Elaborados",
        defaults={'descripcion': "Platos y recetas completas"}
    )
    
    unidad_porcion, _ = UnidadMedida.objects.get_or_create(
        nombre="Porción", 
        defaults={'abreviacion': "prc"}
    )
    
    # 1. Crear Roll California (insumo elaborado)
    if not Insumo.objects.filter(codigo='ELAB-001').exists():
        print(f"\n🍱 Creando Roll California...")
        
        # Crear el insumo elaborado principal
        roll_california = Insumo.objects.create(
            codigo='ELAB-001',
            nombre='Roll California',
            categoria=categoria_platos,
            unidad_medida=unidad_porcion,
            tipo='elaborado',
            precio_unitario=0,  # Se calculará
            cantidad_producida=8,  # 8 porciones por roll
            stock_minimo=1,
            descripcion='Roll California con aguacate, salmón y mayonesa spicy',
            activo=True
        )
        
        # Buscar componentes (insumos compuestos)
        arroz_sushi = Insumo.objects.filter(codigo='COMP-ARROZ-001').first()
        salsa_spicy = Insumo.objects.filter(codigo='COMP-SALSA-001').first()
        
        if arroz_sushi and salsa_spicy:
            costo_total = 0
            
            # Componente 1: Arroz de sushi preparado
            componente1 = InsumoElaborado.objects.create(
                insumo_elaborado=roll_california,
                insumo_componente=arroz_sushi,
                cantidad=150,  # 150g de arroz
                orden=1,
                tiempo_preparacion_minutos=5,
                instrucciones='Formar la base del roll con arroz de sushi'
            )
            costo_total += 150 * arroz_sushi.precio_unitario
            
            # Componente 2: Salsa spicy mayo
            componente2 = InsumoElaborado.objects.create(
                insumo_elaborado=roll_california,
                insumo_componente=salsa_spicy,
                cantidad=20,  # 20ml de salsa
                orden=2,
                tiempo_preparacion_minutos=2,
                instrucciones='Aplicar salsa spicy mayo por encima'
            )
            costo_total += 20 * salsa_spicy.precio_unitario
            
            # Calcular precio unitario por porción
            precio_unitario = costo_total / roll_california.cantidad_producida
            roll_california.precio_unitario = precio_unitario
            roll_california.save()
            
            print(f"   ✅ Roll California creado")
            print(f"   💰 Costo total: ${costo_total:.2f}")
            print(f"   💵 Precio por porción: ${precio_unitario:.2f}")
            print(f"   📦 Produce: {roll_california.cantidad_producida} porciones")
        else:
            print("   ❌ No se encontraron los insumos compuestos necesarios")
    
    # 2. Crear Temaki Especial (insumo elaborado)
    if not Insumo.objects.filter(codigo='ELAB-002').exists():
        print(f"\n🍙 Creando Temaki Especial...")
        
        temaki = Insumo.objects.create(
            codigo='ELAB-002',
            nombre='Temaki Especial',
            categoria=categoria_platos,
            unidad_medida=unidad_porcion,
            tipo='elaborado',
            precio_unitario=0,
            cantidad_producida=4,  # 4 temakis
            stock_minimo=1,
            descripcion='Temaki con múltiples ingredientes elaborados',
            activo=True
        )
        
        # Buscar componentes
        arroz_sushi = Insumo.objects.filter(codigo='COMP-ARROZ-001').first()
        salsa_spicy = Insumo.objects.filter(codigo='COMP-SALSA-001').first()
        mix_sesamo = Insumo.objects.filter(codigo='COMP-SESAMO-001').first()
        
        if arroz_sushi and salsa_spicy and mix_sesamo:
            costo_total = 0
            
            # Componentes múltiples
            componentes = [
                (arroz_sushi, 100, 3, 'Base de arroz del temaki'),
                (salsa_spicy, 15, 1, 'Salsa interior'),
                (mix_sesamo, 10, 2, 'Decoración exterior con sésamo'),
            ]
            
            for i, (insumo_comp, cantidad, tiempo, instruccion) in enumerate(componentes):
                InsumoElaborado.objects.create(
                    insumo_elaborado=temaki,
                    insumo_componente=insumo_comp,
                    cantidad=cantidad,
                    orden=i + 1,
                    tiempo_preparacion_minutos=tiempo,
                    instrucciones=instruccion
                )
                costo_total += cantidad * insumo_comp.precio_unitario
            
            precio_unitario = costo_total / temaki.cantidad_producida
            temaki.precio_unitario = precio_unitario
            temaki.save()
            
            print(f"   ✅ Temaki Especial creado")
            print(f"   💰 Costo total: ${costo_total:.2f}")
            print(f"   💵 Precio por porción: ${precio_unitario:.2f}")
            print(f"   📦 Produce: {temaki.cantidad_producida} temakis")
        else:
            print("   ❌ No se encontraron todos los insumos compuestos necesarios")
    
    # Mostrar resumen final
    print(f"\n📊 RESUMEN DEL SISTEMA:")
    print(f"   🥢 Insumos básicos: {Insumo.objects.filter(tipo='basico', activo=True).count()}")
    print(f"   🍱 Insumos compuestos: {Insumo.objects.filter(tipo='compuesto', activo=True).count()}")
    print(f"   🍣 Insumos elaborados: {Insumo.objects.filter(tipo='elaborado', activo=True).count()}")
    
    elaborados = Insumo.objects.filter(tipo='elaborado', activo=True)
    if elaborados.exists():
        print(f"\n🍽️ Insumos elaborados disponibles:")
        for elaborado in elaborados:
            componentes_count = InsumoElaborado.objects.filter(insumo_elaborado=elaborado).count()
            print(f"   • {elaborado.codigo} - {elaborado.nombre}")
            print(f"     💰 ${elaborado.precio_unitario:.2f}/{elaborado.unidad_medida.abreviacion}")
            print(f"     🔧 {componentes_count} componentes")
    
    print(f"\n✅ Sistema de insumos elaborados funcionando correctamente!")
    print(f"🌐 Accede a: http://127.0.0.1:8000/dashboard/insumos-elaborados/")

if __name__ == '__main__':
    probar_insumos_elaborados()
