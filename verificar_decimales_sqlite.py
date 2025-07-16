#!/usr/bin/env python3
"""
Script para verificar que la migración de decimales funcionó correctamente
"""
import sqlite3
import os

def verificar_precision_decimales():
    """
    Verifica la precisión de decimales en la base de datos
    """
    print("=== VERIFICACIÓN DE PRECISIÓN DE DECIMALES ===")
    
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    if not os.path.exists(db_path):
        print("❌ No se encontró la base de datos")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar el esquema de la tabla RecetaInsumo
        print("🔍 Verificando esquema de la tabla restaurant_recetainsumo:")
        cursor.execute("PRAGMA table_info(restaurant_recetainsumo)")
        columns = cursor.fetchall()
        
        cantidad_column = None
        for col in columns:
            if col[1] == 'cantidad':  # col[1] es el nombre de la columna
                cantidad_column = col
                break
        
        if cantidad_column:
            print(f"  ✅ Columna 'cantidad' encontrada: {cantidad_column}")
        else:
            print("  ❌ No se encontró la columna 'cantidad'")
            return
        
        # Obtener datos actuales de RecetaInsumo
        print("\n🔍 Datos actuales en restaurant_recetainsumo:")
        cursor.execute("""
            SELECT ri.id, i.nombre as insumo_nombre, ri.cantidad, r.nombre as receta_nombre
            FROM restaurant_recetainsumo ri
            JOIN restaurant_insumo i ON ri.insumo_id = i.id  
            JOIN restaurant_receta r ON ri.receta_id = r.id
            ORDER BY ri.id
        """)
        
        resultados = cursor.fetchall()
        if resultados:
            print("ID  | Insumo                     | Cantidad      | Receta")
            print("-" * 70)
            for row in resultados:
                print(f"{row[0]:3d} | {row[1]:25s} | {str(row[2]):12s} | {row[3]}")
        else:
            print("  ❌ No hay datos en la tabla")
            
        # Mostrar recetas actuales
        print("\n🔍 Recetas actuales:")
        cursor.execute("SELECT id, nombre, instrucciones FROM restaurant_receta ORDER BY id")
        recetas = cursor.fetchall()
        
        if recetas:
            print("ID  | Nombre                              | Instrucciones")
            print("-" * 80)
            for receta in recetas:
                nombre = receta[1] or "Sin nombre"
                instrucciones = (receta[2] or "Sin instrucciones")[:30]
                print(f"{receta[0]:3d} | {nombre:35s} | {instrucciones}")
        else:
            print("  ❌ No hay recetas en el sistema")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al verificar la base de datos: {e}")

def probar_insercion_decimal():
    """
    Prueba insertar un valor decimal con 4 decimales
    """
    print("\n=== PRUEBA DE INSERCIÓN DE DECIMALES ===")
    
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar un registro existente para actualizar
        cursor.execute("SELECT id, cantidad FROM restaurant_recetainsumo LIMIT 1")
        resultado = cursor.fetchone()
        
        if not resultado:
            print("❌ No hay registros para probar")
            return
        
        record_id = resultado[0]
        cantidad_original = resultado[1]
        
        print(f"🔍 Probando con registro ID {record_id}")
        print(f"  Cantidad original: {cantidad_original}")
        
        # Probar valores con diferentes precisiones
        valores_prueba = ['0.0001', '0.025', '1.2345', '10.5678']
        
        for valor in valores_prueba:
            print(f"\n  Probando valor: {valor}")
            
            # Actualizar con el nuevo valor
            cursor.execute(
                "UPDATE restaurant_recetainsumo SET cantidad = ? WHERE id = ?",
                (valor, record_id)
            )
            conn.commit()
            
            # Verificar que se guardó correctamente
            cursor.execute(
                "SELECT cantidad FROM restaurant_recetainsumo WHERE id = ?",
                (record_id,)
            )
            resultado_guardado = cursor.fetchone()[0]
            
            if str(resultado_guardado) == valor:
                print(f"    ✅ ÉXITO: Se guardó correctamente como {resultado_guardado}")
            else:
                print(f"    ❌ ERROR: Se guardó como {resultado_guardado} en lugar de {valor}")
        
        # Restaurar valor original
        cursor.execute(
            "UPDATE restaurant_recetainsumo SET cantidad = ? WHERE id = ?",
            (cantidad_original, record_id)
        )
        conn.commit()
        print(f"\n  ↻ Valor original restaurado: {cantidad_original}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")

if __name__ == "__main__":
    verificar_precision_decimales()
    probar_insercion_decimal()
    print("\n=== VERIFICACIÓN COMPLETADA ===")
