#!/usr/bin/env python
"""
Script para diagnóstico de productos huérfanos y verificación de UI vs DB
"""

import os
import django
import json
import logging
import traceback
import sys
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

# Configurar logging
LOG_FILE = f"diagnostico_ui_db_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Importar modelos
from restaurant.models import ProductoVenta, CategoriaProducto
from django.db import connection

def print_separator(title=None):
    """Imprime un separador con título opcional"""
    message = ""
    if title:
        message = "\n" + "="*20 + f" {title} " + "="*20
    else:
        message = "\n" + "="*50
    
    print(message)
    logger.info(message)

def listar_productos_db():
    """Lista todos los productos en la base de datos"""
    print_separator("PRODUCTOS EN BASE DE DATOS")
    
    productos = ProductoVenta.objects.all().order_by('id')
    print(f"Total de productos en DB: {productos.count()}")
    logger.info(f"Total de productos en DB: {productos.count()}")
    
    if productos.count() > 0:
        for producto in productos:
            mensaje = f"ID: {producto.id} | Nombre: {producto.nombre} | Precio: ${producto.precio} | " \
                     f"Categoría: {producto.categoria.nombre if producto.categoria else 'Sin categoría'} | " \
                     f"Disponible: {producto.disponible}"
            print(mensaje)
            logger.info(mensaje)
    else:
        mensaje = "No hay productos en la base de datos."
        print(mensaje)
        logger.info(mensaje)
    
    return productos

def exportar_productos_json():
    """Exporta los productos a un archivo JSON para comparar con lo que muestra la UI"""
    print_separator("EXPORTANDO PRODUCTOS A JSON")
    
    try:
        productos = ProductoVenta.objects.all().order_by('id')
        datos = []
        
        for producto in productos:
            datos.append({
                "id": producto.id,
                "nombre": producto.nombre,
                "precio": float(producto.precio),
                "descripcion": producto.descripcion,
                "categoria_id": producto.categoria_id,
                "categoria_nombre": producto.categoria.nombre if producto.categoria else None,
                "disponible": producto.disponible,
                "es_complemento": producto.es_complemento,
                "imagen": producto.imagen.url if producto.imagen else None
            })
        
        # Guardar a archivo
        nombre_archivo = f"productos_db_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        
        mensaje = f"Datos exportados a {nombre_archivo}"
        print(mensaje)
        logger.info(mensaje)
        return nombre_archivo
    
    except Exception as e:
        mensaje = f"Error al exportar productos: {e}"
        print(mensaje)
        logger.error(mensaje)
        traceback.print_exc()
        logger.error(traceback.format_exc())
        return None

def analizar_inconsistencias_ui_db(archivo_json_ui=None):
    """
    Analiza inconsistencias entre la UI y la DB
    Si se proporciona un archivo JSON de la UI, compara con la DB
    """
    print_separator("ANÁLISIS DE INCONSISTENCIAS UI vs DB")
    
    if not archivo_json_ui:
        mensaje = "No se proporcionó archivo JSON de la UI para comparar"
        print(mensaje)
        logger.warning(mensaje)
        return
    
    try:
        # Cargar datos de la UI
        with open(archivo_json_ui, 'r', encoding='utf-8') as f:
            productos_ui = json.load(f)
        
        # Cargar datos de la DB
        productos_db = list(ProductoVenta.objects.all().values('id', 'nombre', 'precio', 'categoria_id', 'disponible'))
        
        # Convertir a diccionarios para facilitar la búsqueda
        db_dict = {p['id']: p for p in productos_db}
        ui_dict = {p['id']: p for p in productos_ui}
        
        # Productos en UI pero no en DB (huérfanos en UI)
        huerfanos_ui = [p_id for p_id in ui_dict.keys() if p_id not in db_dict]
        
        # Productos en DB pero no en UI (ocultos)
        ocultos_db = [p_id for p_id in db_dict.keys() if p_id not in ui_dict]
        
        # Productos con datos inconsistentes
        inconsistentes = []
        for p_id in ui_dict.keys():
            if p_id in db_dict:
                ui_item = ui_dict[p_id]
                db_item = db_dict[p_id]
                
                # Convertir precio a float para comparación (puede venir como string o decimal)
                ui_precio = float(ui_item['precio'])
                db_precio = float(db_item['precio'])
                
                if (ui_item['nombre'] != db_item['nombre'] or 
                    abs(ui_precio - db_precio) > 0.01 or  # Comparación con tolerancia
                    ui_item['categoria_id'] != db_item['categoria_id'] or
                    ui_item['disponible'] != db_item['disponible']):
                    
                    inconsistentes.append({
                        'id': p_id,
                        'ui': ui_item,
                        'db': db_item
                    })
        
        # Imprimir resultados
        print(f"\nTotal productos en UI: {len(ui_dict)}")
        print(f"Total productos en DB: {len(db_dict)}")
        logger.info(f"Total productos en UI: {len(ui_dict)}")
        logger.info(f"Total productos en DB: {len(db_dict)}")
        
        print("\n1. PRODUCTOS HUÉRFANOS EN UI (mostrados en UI pero no existen en DB):")
        logger.info("1. PRODUCTOS HUÉRFANOS EN UI (mostrados en UI pero no existen en DB):")
        if huerfanos_ui:
            for p_id in huerfanos_ui:
                mensaje = f"  - ID: {p_id}, Nombre: {ui_dict[p_id]['nombre']}"
                print(mensaje)
                logger.info(mensaje)
        else:
            mensaje = "  No hay productos huérfanos en UI"
            print(mensaje)
            logger.info(mensaje)
        
        print("\n2. PRODUCTOS OCULTOS EN DB (existen en DB pero no se muestran en UI):")
        logger.info("2. PRODUCTOS OCULTOS EN DB (existen en DB pero no se muestran en UI):")
        if ocultos_db:
            for p_id in ocultos_db:
                mensaje = f"  - ID: {p_id}, Nombre: {db_dict[p_id]['nombre']}"
                print(mensaje)
                logger.info(mensaje)
        else:
            mensaje = "  No hay productos ocultos en DB"
            print(mensaje)
            logger.info(mensaje)
        
        print("\n3. PRODUCTOS CON DATOS INCONSISTENTES:")
        logger.info("3. PRODUCTOS CON DATOS INCONSISTENTES:")
        if inconsistentes:
            for item in inconsistentes:
                p_id = item['id']
                ui = item['ui']
                db = item['db']
                mensaje = f"  - ID: {p_id}, Nombre UI: {ui['nombre']}, Nombre DB: {db['nombre']}"
                print(mensaje)
                logger.info(mensaje)
                
                # Detallar las diferencias
                if ui['nombre'] != db['nombre']:
                    mensaje = f"    * Nombre: UI='{ui['nombre']}', DB='{db['nombre']}'"
                    print(mensaje)
                    logger.info(mensaje)
                
                if abs(float(ui['precio']) - float(db['precio'])) > 0.01:
                    mensaje = f"    * Precio: UI=${ui['precio']}, DB=${db['precio']}"
                    print(mensaje)
                    logger.info(mensaje)
                
                if ui['categoria_id'] != db['categoria_id']:
                    mensaje = f"    * Categoría ID: UI={ui['categoria_id']}, DB={db['categoria_id']}"
                    print(mensaje)
                    logger.info(mensaje)
                
                if ui['disponible'] != db['disponible']:
                    mensaje = f"    * Disponible: UI={ui['disponible']}, DB={db['disponible']}"
                    print(mensaje)
                    logger.info(mensaje)
        else:
            mensaje = "  No hay productos con datos inconsistentes"
            print(mensaje)
            logger.info(mensaje)
        
        # Resumen
        print("\nRESUMEN:")
        logger.info("RESUMEN:")
        mensaje = f"  - Productos huérfanos en UI: {len(huerfanos_ui)}"
        print(mensaje)
        logger.info(mensaje)
        mensaje = f"  - Productos ocultos en DB: {len(ocultos_db)}"
        print(mensaje)
        logger.info(mensaje)
        mensaje = f"  - Productos con datos inconsistentes: {len(inconsistentes)}"
        print(mensaje)
        logger.info(mensaje)
        
        return {
            'huerfanos_ui': huerfanos_ui,
            'ocultos_db': ocultos_db,
            'inconsistentes': inconsistentes
        }
    
    except Exception as e:
        mensaje = f"Error al analizar inconsistencias: {e}"
        print(mensaje)
        logger.error(mensaje)
        traceback.print_exc()
        logger.error(traceback.format_exc())
        return None

def verificar_eliminacion_correcta():
    """
    Verifica si hay inconsistencias en el proceso de eliminación
    mediante consultas SQL directas a las tablas relacionadas
    """
    print_separator("VERIFICACIÓN DE ELIMINACIÓN CORRECTA")
    
    try:
        with connection.cursor() as cursor:
            # 1. Verificar si hay productos eliminados pero con relaciones huérfanas
            print("\n1. Buscando relaciones huérfanas en ProductoReceta:")
            logger.info("1. Buscando relaciones huérfanas en ProductoReceta:")
            
            # Verificar si existe la tabla
            cursor.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='restaurant_productoreceta'"
            )
            if cursor.fetchone()[0] > 0:
                cursor.execute("""
                    SELECT pr.id, pr.producto_id, pr.receta_id 
                    FROM restaurant_productoreceta pr
                    LEFT JOIN restaurant_productoventa pv ON pr.producto_id = pv.id
                    WHERE pv.id IS NULL
                """)
                rows = cursor.fetchall()
                if rows:
                    for row in rows:
                        mensaje = f"  - ProductoReceta huérfano: ID={row[0]}, producto_id={row[1]}, receta_id={row[2]}"
                        print(mensaje)
                        logger.info(mensaje)
                else:
                    mensaje = "  No se encontraron relaciones huérfanas en ProductoReceta"
                    print(mensaje)
                    logger.info(mensaje)
            else:
                mensaje = "  La tabla restaurant_productoreceta no existe"
                print(mensaje)
                logger.info(mensaje)
            
            # 2. Verificar ProductoCategoria
            print("\n2. Buscando relaciones huérfanas en ProductoCategoria:")
            logger.info("2. Buscando relaciones huérfanas en ProductoCategoria:")
            
            cursor.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='restaurant_productocategoria'"
            )
            if cursor.fetchone()[0] > 0:
                cursor.execute("""
                    SELECT pc.id, pc.producto_id, pc.categoria_id 
                    FROM restaurant_productocategoria pc
                    LEFT JOIN restaurant_productoventa pv ON pc.producto_id = pv.id
                    WHERE pv.id IS NULL
                """)
                rows = cursor.fetchall()
                if rows:
                    for row in rows:
                        mensaje = f"  - ProductoCategoria huérfano: ID={row[0]}, producto_id={row[1]}, categoria_id={row[2]}"
                        print(mensaje)
                        logger.info(mensaje)
                else:
                    mensaje = "  No se encontraron relaciones huérfanas en ProductoCategoria"
                    print(mensaje)
                    logger.info(mensaje)
            else:
                mensaje = "  La tabla restaurant_productocategoria no existe"
                print(mensaje)
                logger.info(mensaje)
            
            # 3. Verificar OrdenItem
            print("\n3. Buscando relaciones huérfanas en OrdenItem:")
            logger.info("3. Buscando relaciones huérfanas en OrdenItem:")
            
            cursor.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='dashboard_ordenitem'"
            )
            if cursor.fetchone()[0] > 0:
                cursor.execute("""
                    SELECT oi.id, oi.producto_id, oi.orden_id 
                    FROM dashboard_ordenitem oi
                    LEFT JOIN restaurant_productoventa pv ON oi.producto_id = pv.id
                    WHERE pv.id IS NULL
                """)
                rows = cursor.fetchall()
                if rows:
                    for row in rows:
                        mensaje = f"  - OrdenItem huérfano: ID={row[0]}, producto_id={row[1]}, orden_id={row[2]}"
                        print(mensaje)
                        logger.info(mensaje)
                else:
                    mensaje = "  No se encontraron relaciones huérfanas en OrdenItem"
                    print(mensaje)
                    logger.info(mensaje)
            else:
                mensaje = "  La tabla dashboard_ordenitem no existe"
                print(mensaje)
                logger.info(mensaje)
            
            # 4. Verificar DetalleVenta
            print("\n4. Buscando relaciones huérfanas en DetalleVenta:")
            logger.info("4. Buscando relaciones huérfanas en DetalleVenta:")
            
            cursor.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='dashboard_detalleventa'"
            )
            if cursor.fetchone()[0] > 0:
                cursor.execute("""
                    SELECT dv.id, dv.producto_id, dv.venta_id 
                    FROM dashboard_detalleventa dv
                    LEFT JOIN restaurant_productoventa pv ON dv.producto_id = pv.id
                    WHERE pv.id IS NULL
                """)
                rows = cursor.fetchall()
                if rows:
                    for row in rows:
                        mensaje = f"  - DetalleVenta huérfano: ID={row[0]}, producto_id={row[1]}, venta_id={row[2]}"
                        print(mensaje)
                        logger.info(mensaje)
                else:
                    mensaje = "  No se encontraron relaciones huérfanas en DetalleVenta"
                    print(mensaje)
                    logger.info(mensaje)
            else:
                mensaje = "  La tabla dashboard_detalleventa no existe"
                print(mensaje)
                logger.info(mensaje)
            
            # 5. Verificar otras posibles tablas de mesero y cajero
            print("\n5. Buscando relaciones huérfanas en otras tablas posibles:")
            logger.info("5. Buscando relaciones huérfanas en otras tablas posibles:")
            
            tablas_posibles = [
                'mesero_ordenitem',
                'cashier_detalleventa'
            ]
            
            for tabla in tablas_posibles:
                cursor.execute(
                    f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{tabla}'"
                )
                if cursor.fetchone()[0] > 0:
                    # Verificar si tiene columna producto_id
                    cursor.execute(f"PRAGMA table_info({tabla})")
                    columnas = cursor.fetchall()
                    tiene_producto_id = any(col[1] == 'producto_id' for col in columnas)
                    
                    if tiene_producto_id:
                        cursor.execute(f"""
                            SELECT t.id, t.producto_id 
                            FROM {tabla} t
                            LEFT JOIN restaurant_productoventa pv ON t.producto_id = pv.id
                            WHERE pv.id IS NULL
                        """)
                        rows = cursor.fetchall()
                        if rows:
                            for row in rows:
                                mensaje = f"  - {tabla} huérfano: ID={row[0]}, producto_id={row[1]}"
                                print(mensaje)
                                logger.info(mensaje)
                        else:
                            mensaje = f"  No se encontraron relaciones huérfanas en {tabla}"
                            print(mensaje)
                            logger.info(mensaje)
                    else:
                        mensaje = f"  La tabla {tabla} no tiene columna producto_id"
                        print(mensaje)
                        logger.info(mensaje)
                else:
                    mensaje = f"  La tabla {tabla} no existe"
                    print(mensaje)
                    logger.info(mensaje)
        
        print("\nVerificación de eliminación completada. Revise el log para más detalles.")
        logger.info("Verificación de eliminación completada.")
    
    except Exception as e:
        mensaje = f"Error en la verificación de eliminación: {e}"
        print(mensaje)
        logger.error(mensaje)
        traceback.print_exc()
        logger.error(traceback.format_exc())

def verificar_base_datos():
    """Verifica la salud general de la base de datos"""
    print_separator("VERIFICACIÓN DE SALUD DE LA BASE DE DATOS")
    
    try:
        with connection.cursor() as cursor:
            # 1. Verificar integridad de la base de datos
            print("\n1. Verificando integridad de la base de datos:")
            logger.info("1. Verificando integridad de la base de datos:")
            
            cursor.execute("PRAGMA integrity_check")
            resultado = cursor.fetchone()
            mensaje = f"  Resultado: {resultado[0]}"
            print(mensaje)
            logger.info(mensaje)
            
            # 2. Verificar constraints de clave foránea
            print("\n2. Verificando constraints de clave foránea:")
            logger.info("2. Verificando constraints de clave foránea:")
            
            cursor.execute("PRAGMA foreign_key_check")
            resultados = cursor.fetchall()
            if resultados:
                for resultado in resultados:
                    mensaje = f"  - Violación de clave foránea: {resultado}"
                    print(mensaje)
                    logger.error(mensaje)
            else:
                mensaje = "  No se encontraron violaciones de clave foránea"
                print(mensaje)
                logger.info(mensaje)
            
            # 3. Verificar si hay tablas con índices inválidos
            print("\n3. Verificando índices:")
            logger.info("3. Verificando índices:")
            
            cursor.execute("PRAGMA index_list(restaurant_productoventa)")
            indices = cursor.fetchall()
            if indices:
                mensaje = f"  Índices en restaurant_productoventa: {len(indices)}"
                print(mensaje)
                logger.info(mensaje)
                for indice in indices:
                    mensaje = f"  - {indice}"
                    print(mensaje)
                    logger.debug(mensaje)
            else:
                mensaje = "  No se encontraron índices en restaurant_productoventa"
                print(mensaje)
                logger.info(mensaje)
        
        print("\nVerificación de base de datos completada. Revise el log para más detalles.")
        logger.info("Verificación de base de datos completada.")
    
    except Exception as e:
        mensaje = f"Error en la verificación de la base de datos: {e}"
        print(mensaje)
        logger.error(mensaje)
        traceback.print_exc()
        logger.error(traceback.format_exc())

def corregir_huerfanos():
    """Corrige relaciones huérfanas en la base de datos"""
    print_separator("CORRECCIÓN DE RELACIONES HUÉRFANAS")
    
    try:
        with connection.cursor() as cursor:
            tablas_relaciones = [
                'restaurant_productoreceta',
                'restaurant_productocategoria',
                'dashboard_ordenitem',
                'dashboard_detalleventa',
                'mesero_ordenitem',
                'cashier_detalleventa'
            ]
            
            for tabla in tablas_relaciones:
                # Verificar si existe la tabla
                cursor.execute(
                    f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{tabla}'"
                )
                if cursor.fetchone()[0] == 0:
                    print(f"La tabla {tabla} no existe. Omitiendo.")
                    logger.info(f"La tabla {tabla} no existe. Omitiendo.")
                    continue
                
                # Verificar si tiene columna producto_id
                cursor.execute(f"PRAGMA table_info({tabla})")
                columnas = cursor.fetchall()
                tiene_producto_id = any(col[1] == 'producto_id' for col in columnas)
                
                if tiene_producto_id:
                    # Contar registros huérfanos
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM {tabla} t
                        LEFT JOIN restaurant_productoventa pv ON t.producto_id = pv.id
                        WHERE pv.id IS NULL
                    """)
                    count = cursor.fetchone()[0]
                    
                    if count > 0:
                        # Eliminar registros huérfanos
                        cursor.execute(f"""
                            DELETE FROM {tabla}
                            WHERE producto_id IN (
                                SELECT t.producto_id FROM {tabla} t
                                LEFT JOIN restaurant_productoventa pv ON t.producto_id = pv.id
                                WHERE pv.id IS NULL
                            )
                        """)
                        
                        mensaje = f"Corregidos {count} registros huérfanos en {tabla}"
                        print(mensaje)
                        logger.info(mensaje)
                    else:
                        mensaje = f"No se encontraron registros huérfanos en {tabla}"
                        print(mensaje)
                        logger.info(mensaje)
                else:
                    mensaje = f"La tabla {tabla} no tiene columna producto_id. Omitiendo."
                    print(mensaje)
                    logger.info(mensaje)
        
        print("\nCorrección de relaciones huérfanas completada.")
        logger.info("Corrección de relaciones huérfanas completada.")
    
    except Exception as e:
        mensaje = f"Error corrigiendo relaciones huérfanas: {e}"
        print(mensaje)
        logger.error(mensaje)
        traceback.print_exc()
        logger.error(traceback.format_exc())

def main():
    """Función principal"""
    print_separator("DIAGNÓSTICO DE PRODUCTOS UI vs DB")
    logger.info("="*30)
    logger.info("INICIANDO DIAGNÓSTICO DE PRODUCTOS UI vs DB")
    logger.info("="*30)
    
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Django version: {django.get_version()}")
    print(f"Python version: {sys.version}")
    print(f"Log guardado en: {LOG_FILE}")
    
    logger.info(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Django version: {django.get_version()}")
    logger.info(f"Python version: {sys.version}")
    
    # Modos de operación
    print_separator("MODOS DE OPERACIÓN")
    print("1. Listar productos en DB")
    print("2. Exportar productos a JSON (para comparar con UI)")
    print("3. Analizar inconsistencias UI vs DB")
    print("4. Verificar integridad de eliminación")
    print("5. Verificar salud de base de datos")
    print("6. Corregir relaciones huérfanas")
    
    try:
        modo = int(input("\nSeleccione un modo (1-6): "))
    except ValueError:
        modo = 1  # Por defecto listar productos
    
    # Ejecutar según el modo seleccionado
    if modo == 1:
        # Listar productos en DB
        listar_productos_db()
    
    elif modo == 2:
        # Exportar productos a JSON
        archivo = exportar_productos_json()
        if archivo:
            print(f"\nArchivo JSON creado: {archivo}")
            print("Puede usar este archivo para comparar con datos de la UI")
    
    elif modo == 3:
        # Analizar inconsistencias UI vs DB
        archivo_ui = input("\nIngrese la ruta del archivo JSON con datos de la UI: ")
        if not archivo_ui:
            print("Primero exportando datos de la DB...")
            exportar_productos_json()
            print("\nDebe capturar los datos de la UI y luego ejecutar este modo nuevamente.")
            print("Para capturar los datos de la UI, puede usar la consola del navegador en la página")
            print("de productos y ejecutar este código JavaScript:")
            print("\n```javascript")
            print("// Código para capturar productos en la UI")
            print("const productCards = document.querySelectorAll('.product-card');")
            print("const productosUI = [];")
            print("productCards.forEach(card => {")
            print("    const id = parseInt(card.dataset.productId);")
            print("    const nombre = card.querySelector('.product-name').textContent.trim();")
            print("    const precioText = card.querySelector('.product-price').textContent.trim();")
            print("    const precio = parseFloat(precioText.replace('$', '').replace(',', ''));")
            print("    const categoriaId = parseInt(card.dataset.categoryId || '0');")
            print("    const disponible = !card.classList.contains('no-disponible');")
            print("    productosUI.push({id, nombre, precio, categoria_id: categoriaId, disponible});")
            print("});")
            print("console.log(JSON.stringify(productosUI, null, 2));")
            print("// Copie el resultado y guárdelo en un archivo JSON")
            print("```")
        else:
            analizar_inconsistencias_ui_db(archivo_ui)
    
    elif modo == 4:
        # Verificar integridad de eliminación
        verificar_eliminacion_correcta()
    
    elif modo == 5:
        # Verificar salud de base de datos
        verificar_base_datos()
    
    elif modo == 6:
        # Corregir relaciones huérfanas
        confirmacion = input("\n¿Está seguro de que desea corregir relaciones huérfanas? Esta acción eliminará datos. (s/n): ")
        if confirmacion.lower() == 's':
            corregir_huerfanos()
        else:
            print("Operación cancelada.")
    
    else:
        print("Modo no válido.")
    
    print_separator("FIN DEL DIAGNÓSTICO")
    logger.info("FIN DEL DIAGNÓSTICO")

if __name__ == "__main__":
    main()
