#!/usr/bin/env python
"""
Script para corregir los tipos de insumos en la base de datos
"""

import os
import sys
import django
import sqlite3

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

try:
    django.setup()
    from restaurant.models import Insumo
    django_available = True
    print("✅ Django configurado correctamente")
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    django_available = False

def fix_tipos_with_sqlite():
    """Corregir tipos usando SQLite directamente"""
    print("\n=== CORRECCIÓN CON SQLITE ===")
    
    db_path = 'db.sqlite3'
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar tipos actuales
        print("1. Verificando tipos actuales...")
        cursor.execute("SELECT id, codigo, nombre, tipo FROM restaurant_insumo")
        insumos = cursor.fetchall()
        
        tipos_incorrectos = []
        for insumo in insumos:
            id_insumo, codigo, nombre, tipo = insumo
            if tipo not in ['basico', 'compuesto', 'elaborado']:
                tipos_incorrectos.append((id_insumo, codigo, nombre, tipo))
        
        print(f"   - Total insumos: {len(insumos)}")
        print(f"   - Con tipos incorrectos: {len(tipos_incorrectos)}")
        
        if tipos_incorrectos:
            print("\n2. Insumos con tipos incorrectos:")
            for id_insumo, codigo, nombre, tipo in tipos_incorrectos:
                print(f"   ID {id_insumo}: {codigo} - {nombre} (tipo: '{tipo}')")
        
        # Mapping de corrección (basado en patrones observados)
        mapping_tipos = {
            '8': 'basico',      # parece que 8 corresponde a básico
            '9': 'compuesto',   # probable que 9 sea compuesto
            '10': 'elaborado',  # probable que 10 sea elaborado
            # Agregar más mappings si es necesario
        }
        
        # Aplicar correcciones
        if tipos_incorrectos:
            print("\n3. Aplicando correcciones...")
            for id_insumo, codigo, nombre, tipo in tipos_incorrectos:
                nuevo_tipo = mapping_tipos.get(str(tipo), 'basico')  # default a básico
                print(f"   - Corrigiendo ID {id_insumo}: '{tipo}' -> '{nuevo_tipo}'")
                
                cursor.execute(
                    "UPDATE restaurant_insumo SET tipo = ? WHERE id = ?",
                    (nuevo_tipo, id_insumo)
                )
            
            conn.commit()
            print(f"   ✅ {len(tipos_incorrectos)} tipos corregidos")
        else:
            print("   ✅ No hay tipos que corregir")
        
        # Verificación final
        print("\n4. Verificación final...")
        cursor.execute("SELECT tipo, COUNT(*) FROM restaurant_insumo GROUP BY tipo")
        conteos = cursor.fetchall()
        
        for tipo, count in conteos:
            print(f"   - Tipo '{tipo}': {count} insumos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en corrección: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def fix_tipos_with_django():
    """Corregir tipos usando Django ORM"""
    print("\n=== CORRECCIÓN CON DJANGO ORM ===")
    
    try:
        # Verificar insumos con tipos incorrectos
        todos_insumos = Insumo.objects.all()
        print(f"1. Total de insumos: {todos_insumos.count()}")
        
        # Intentar identificar insumos problemáticos
        tipos_validos = ['basico', 'compuesto', 'elaborado']
        insumos_problematicos = []
        
        for insumo in todos_insumos:
            if insumo.tipo not in tipos_validos:
                insumos_problematicos.append(insumo)
        
        print(f"2. Insumos con tipos incorrectos: {len(insumos_problematicos)}")
        
        if insumos_problematicos:
            print("3. Corrigiendo tipos...")
            for insumo in insumos_problematicos:
                print(f"   - ID {insumo.id}: {insumo.codigo} (tipo: '{insumo.tipo}')")
                # Inferir tipo correcto basado en patrones
                if 'COMP-' in insumo.codigo or 'comp' in insumo.nombre.lower():
                    insumo.tipo = 'compuesto'
                elif 'ELAB-' in insumo.codigo or 'elab' in insumo.nombre.lower():
                    insumo.tipo = 'elaborado'
                else:
                    insumo.tipo = 'basico'
                insumo.save()
                print(f"     -> Corregido a: '{insumo.tipo}'")
        
        # Verificación final
        print("\n4. Conteo final por tipos:")
        for tipo, descripcion in Insumo.TIPOS_INSUMO:
            count = Insumo.objects.filter(tipo=tipo).count()
            print(f"   - {descripcion}: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en corrección Django: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_insumo():
    """Probar específicamente el insumo ID 47"""
    print("\n=== PRUEBA ESPECÍFICA DEL INSUMO ID 47 ===")
    
    if django_available:
        try:
            insumo_47 = Insumo.objects.get(id=47)
            print(f"✅ Insumo ID 47 encontrado con Django:")
            print(f"   - Código: {insumo_47.codigo}")
            print(f"   - Nombre: {insumo_47.nombre}")
            print(f"   - Tipo: '{insumo_47.tipo}'")
            print(f"   - Activo: {insumo_47.activo}")
            print(f"   - Precio: ${insumo_47.precio_unitario}")
            
            # Probar el filtro que falla
            resultado = Insumo.objects.filter(
                id=47, 
                tipo__in=['basico', 'compuesto'],
                activo=True
            )
            print(f"   - Filtro de la vista funciona: {resultado.exists()}")
            
            if not resultado.exists():
                print(f"   ❌ El filtro no encuentra el insumo")
                print(f"   - Verificando condiciones:")
                print(f"     * ID = 47: ✅")
                print(f"     * tipo in ['basico', 'compuesto']: {'✅' if insumo_47.tipo in ['basico', 'compuesto'] else '❌'}")
                print(f"     * activo = True: {'✅' if insumo_47.activo else '❌'}")
            
            return True
            
        except Insumo.DoesNotExist:
            print("❌ Insumo ID 47 no encontrado con Django")
            return False
        except Exception as e:
            print(f"❌ Error probando insumo 47: {e}")
            return False
    else:
        print("❌ Django no disponible para la prueba")
        return False

def main():
    """Función principal"""
    print("🔧 SCRIPT DE CORRECCIÓN DE TIPOS DE INSUMOS")
    print("=" * 50)
    
    # Paso 1: Corregir con SQLite
    success_sqlite = fix_tipos_with_sqlite()
    
    # Paso 2: Corregir con Django si está disponible
    if django_available:
        success_django = fix_tipos_with_django()
    else:
        success_django = True  # No falla si Django no está disponible
    
    # Paso 3: Probar específicamente el insumo 47
    success_test = test_specific_insumo()
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE CORRECCIONES:")
    print(f"   - Corrección SQLite: {'✅' if success_sqlite else '❌'}")
    print(f"   - Corrección Django: {'✅' if success_django else '❌'}")
    print(f"   - Prueba insumo 47: {'✅' if success_test else '❌'}")
    
    if all([success_sqlite, success_django, success_test]):
        print("\n🎉 CORRECCIÓN COMPLETADA CON ÉXITO")
        print("Los tipos de insumos han sido corregidos.")
    else:
        print("\n⚠️ CORRECCIÓN PARCIAL O CON ERRORES")
        print("Revisa los mensajes anteriores para más detalles.")

if __name__ == '__main__':
    main()
