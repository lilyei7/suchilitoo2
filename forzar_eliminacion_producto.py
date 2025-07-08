#!/usr/bin/env python
"""
Script para forzar la eliminación de productos en la base de datos
que no pueden ser eliminados por la interfaz web.
"""

import os
import django
import logging
import traceback
import sys
import time
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

# Configurar logging
LOG_FILE = f"eliminacion_forzada_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Importar modelos relevantes
from django.contrib.auth.models import User
from django.db import connection, transaction, IntegrityError, OperationalError
from restaurant.models import ProductoVenta, CategoriaProducto
from django.db.models import ProtectedError

def print_separator(title=None):
    """Imprime un separador con título opcional"""
    message = ""
    if title:
        message = "\n" + "="*20 + f" {title} " + "="*20
    else:
        message = "\n" + "="*50
    
    print(message)
    logger.info(message)

def listar_productos(busqueda=None):
    """
    Lista todos los productos en la base de datos.
    Opcionalmente filtra por un texto de búsqueda en el nombre.
    """
    print_separator("PRODUCTOS ACTUALES")
    
    query = ProductoVenta.objects.all()
    
    if busqueda:
        query = query.filter(nombre__icontains=busqueda)
        print(f"Filtrando productos por: '{busqueda}'")
        logger.info(f"Filtrando productos por: '{busqueda}'")
    
    productos = query.order_by('id')
    print(f"Total de productos encontrados: {productos.count()}")
    logger.info(f"Total de productos encontrados: {productos.count()}")
    
    if productos.count() > 0:
        for producto in productos:
            mensaje = f"ID: {producto.id} | Nombre: {producto.nombre} | Precio: ${producto.precio} | Categoría: {producto.categoria.nombre if producto.categoria else 'Sin categoría'}"
            print(mensaje)
            logger.info(mensaje)
    else:
        mensaje = "No hay productos en la base de datos con los criterios especificados."
        print(mensaje)
        logger.info(mensaje)
    
    return productos

def verificar_producto_existe(producto_id):
    """Verifica si un producto existe en la base de datos"""
    try:
        producto = ProductoVenta.objects.get(id=producto_id)
        return True, producto
    except ProductoVenta.DoesNotExist:
        return False, None
    except Exception as e:
        logger.error(f"Error verificando producto ID {producto_id}: {e}")
        return False, None

def verificar_dependencias(producto_id):
    """Verifica y cuenta todas las dependencias que podrían bloquear la eliminación"""
    print_separator(f"DEPENDENCIAS PARA PRODUCTO ID: {producto_id}")
    logger.info(f"Verificando dependencias para producto ID: {producto_id}")
    
    dependencias = {
        "ProductoReceta": 0,
        "ProductoCategoria": 0,
        "Receta": 0,
        "OrdenItem": 0,
        "DetalleVenta": 0,
        "Otras": 0
    }
    
    try:
        existe, producto = verificar_producto_existe(producto_id)
        if not existe:
            mensaje = f"ERROR: Producto con ID {producto_id} no existe"
            print(mensaje)
            logger.error(mensaje)
            return False, mensaje, dependencias
        
        mensaje = f"Verificando dependencias para: {producto.nombre} (ID: {producto_id})"
        print(mensaje)
        logger.info(mensaje)
        
        # 1. Verificar relaciones directas
        print("\n1. Relaciones directas:")
        logger.info("1. Relaciones directas:")
        
        # ProductoReceta
        try:
            from restaurant.models import ProductoReceta
            recetas = ProductoReceta.objects.filter(producto=producto)
            dependencias["ProductoReceta"] = recetas.count()
            mensaje = f"   ProductoReceta: {recetas.count()} relaciones"
            print(mensaje)
            logger.info(mensaje)
            for receta in recetas:
                mensaje = f"     - Producto-Receta ID: {receta.id}"
                print(mensaje)
                logger.debug(mensaje)
        except ImportError:
            mensaje = "   ProductoReceta: Modelo no encontrado"
            print(mensaje)
            logger.warning(mensaje)
        
        # ProductoCategoria
        try:
            from restaurant.models import ProductoCategoria
            categorias = ProductoCategoria.objects.filter(producto=producto)
            dependencias["ProductoCategoria"] = categorias.count()
            mensaje = f"   ProductoCategoria: {categorias.count()} relaciones"
            print(mensaje)
            logger.info(mensaje)
            for categoria in categorias:
                mensaje = f"     - Producto-Categoría ID: {categoria.id}, Categoría: {categoria.categoria.nombre if hasattr(categoria, 'categoria') and categoria.categoria else 'N/A'}"
                print(mensaje)
                logger.debug(mensaje)
        except ImportError:
            mensaje = "   ProductoCategoria: Modelo no encontrado"
            print(mensaje)
            logger.warning(mensaje)
        
        # Receta (relación inversa)
        try:
            from restaurant.models import Receta
            recetas_inv = Receta.objects.filter(producto=producto)
            dependencias["Receta"] = recetas_inv.count()
            mensaje = f"   Receta (inversa): {recetas_inv.count()} relaciones"
            print(mensaje)
            logger.info(mensaje)
            for receta in recetas_inv:
                mensaje = f"     - Receta ID: {receta.id}"
                print(mensaje)
                logger.debug(mensaje)
        except ImportError:
            mensaje = "   Receta: Modelo no encontrado"
            print(mensaje)
            logger.warning(mensaje)
        
        # 2. Verificar relaciones en aplicación Dashboard
        print("\n2. Relaciones en Dashboard:")
        logger.info("2. Relaciones en Dashboard:")
        
        # OrdenItem
        try:
            from dashboard.models_ventas import OrdenItem
            ordenes = OrdenItem.objects.filter(producto=producto)
            dependencias["OrdenItem"] = ordenes.count()
            mensaje = f"   OrdenItem: {ordenes.count()} relaciones"
            print(mensaje)
            logger.info(mensaje)
            for orden in ordenes:
                mensaje = f"     - OrdenItem ID: {orden.id}, Orden: {orden.orden_id}"
                print(mensaje)
                logger.debug(mensaje)
        except ImportError:
            mensaje = "   OrdenItem: Modelo no encontrado"
            print(mensaje)
            logger.warning(mensaje)
        
        # DetalleVenta
        try:
            from dashboard.models_ventas import DetalleVenta
            detalles = DetalleVenta.objects.filter(producto=producto)
            dependencias["DetalleVenta"] = detalles.count()
            mensaje = f"   DetalleVenta: {detalles.count()} relaciones"
            print(mensaje)
            logger.info(mensaje)
            for detalle in detalles:
                mensaje = f"     - DetalleVenta ID: {detalle.id}, Venta: {detalle.venta_id}"
                print(mensaje)
                logger.debug(mensaje)
        except ImportError:
            mensaje = "   DetalleVenta: Modelo no encontrado"
            print(mensaje)
            logger.warning(mensaje)
            
        # 3. Verificar tablas relacionadas mediante consulta SQL directa
        print("\n3. Verificación SQL directa:")
        logger.info("3. Verificación SQL directa:")
        
        tablas_posibles = [
            'dashboard_ordenitem', 
            'dashboard_detalleventa', 
            'restaurant_productoreceta', 
            'restaurant_productocategoria',
            'restaurant_receta',
            'mesero_ordenitem',  # Posibles tablas huérfanas
            'mesero_orden',      # Posibles tablas huérfanas
            'cashier_detalleventa'  # Posibles tablas de cajero
        ]
        
        with connection.cursor() as cursor:
            for tabla in tablas_posibles:
                try:
                    # Primero verificar si existe la tabla
                    cursor.execute(
                        f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{tabla}'"
                    )
                    if cursor.fetchone()[0] == 0:
                        mensaje = f"   Tabla '{tabla}' no existe en la base de datos"
                        print(mensaje)
                        logger.debug(mensaje)
                        continue
                    
                    # Verificar si tiene una columna producto_id
                    cursor.execute(f"PRAGMA table_info({tabla})")
                    columnas = cursor.fetchall()
                    tiene_producto_id = any(col[1] == 'producto_id' for col in columnas)
                    
                    if tiene_producto_id:
                        cursor.execute(f"SELECT COUNT(*) FROM {tabla} WHERE producto_id = ?", [producto_id])
                        count = cursor.fetchone()[0]
                        mensaje = f"   Tabla {tabla}: {count} referencias"
                        print(mensaje)
                        logger.info(mensaje)
                        
                        if count > 0:
                            cursor.execute(f"SELECT * FROM {tabla} WHERE producto_id = ? LIMIT 5", [producto_id])
                            rows = cursor.fetchall()
                            for row in rows:
                                mensaje = f"     - Registro: {row}"
                                print(mensaje)
                                logger.debug(mensaje)
                            
                            # Incrementar contador de "Otras" si la tabla no está en los contadores principales
                            if tabla not in ['restaurant_productoreceta', 'restaurant_productocategoria', 
                                            'restaurant_receta', 'dashboard_ordenitem', 'dashboard_detalleventa']:
                                dependencias["Otras"] += count
                    else:
                        mensaje = f"   Tabla {tabla}: No tiene columna producto_id"
                        print(mensaje)
                        logger.debug(mensaje)
                        
                except Exception as e:
                    mensaje = f"   Error verificando tabla {tabla}: {e}"
                    print(mensaje)
                    logger.error(mensaje)
        
        # Resumen de dependencias
        print("\nRESUMEN DE DEPENDENCIAS:")
        logger.info("RESUMEN DE DEPENDENCIAS:")
        for tipo, cantidad in dependencias.items():
            mensaje = f"  - {tipo}: {cantidad}"
            print(mensaje)
            logger.info(mensaje)
        
        total_deps = sum(dependencias.values())
        mensaje = f"  Total de dependencias: {total_deps}"
        print(mensaje)
        logger.info(mensaje)
        
        return True, "Verificación de dependencias completada", dependencias
    
    except Exception as e:
        mensaje = f"ERROR: {e}"
        print(mensaje)
        logger.error(mensaje)
        traceback.print_exc()
        logger.error(traceback.format_exc())
        return False, str(e), dependencias

def limpiar_dependencias(producto_id):
    """Limpia todas las dependencias de un producto"""
    print_separator(f"LIMPIEZA DE DEPENDENCIAS PARA PRODUCTO ID: {producto_id}")
    logger.info(f"Limpiando dependencias para producto ID: {producto_id}")
    
    resultado = {
        "ProductoReceta": 0,
        "ProductoCategoria": 0,
        "Receta": 0,
        "OrdenItem": 0,
        "DetalleVenta": 0,
        "Otras": 0
    }
    
    try:
        existe, producto = verificar_producto_existe(producto_id)
        if not existe:
            mensaje = f"ERROR: Producto con ID {producto_id} no existe"
            print(mensaje)
            logger.error(mensaje)
            return False, mensaje, resultado
        
        mensaje = f"Limpiando dependencias para: {producto.nombre} (ID: {producto_id})"
        print(mensaje)
        logger.info(mensaje)
        
        with transaction.atomic():
            # 1. Limpiar ProductoReceta
            try:
                from restaurant.models import ProductoReceta
                recetas = ProductoReceta.objects.filter(producto=producto)
                count = recetas.count()
                recetas.delete()
                resultado["ProductoReceta"] = count
                mensaje = f"Eliminadas {count} relaciones ProductoReceta"
                print(mensaje)
                logger.info(mensaje)
            except ImportError:
                mensaje = "Modelo ProductoReceta no encontrado"
                print(mensaje)
                logger.warning(mensaje)
            except Exception as e:
                mensaje = f"Error eliminando ProductoReceta: {e}"
                print(mensaje)
                logger.error(mensaje)
                raise
            
            # 2. Limpiar ProductoCategoria
            try:
                from restaurant.models import ProductoCategoria
                categorias = ProductoCategoria.objects.filter(producto=producto)
                count = categorias.count()
                categorias.delete()
                resultado["ProductoCategoria"] = count
                mensaje = f"Eliminadas {count} relaciones ProductoCategoria"
                print(mensaje)
                logger.info(mensaje)
            except ImportError:
                mensaje = "Modelo ProductoCategoria no encontrado"
                print(mensaje)
                logger.warning(mensaje)
            except Exception as e:
                mensaje = f"Error eliminando ProductoCategoria: {e}"
                print(mensaje)
                logger.error(mensaje)
                raise
            
            # 3. Limpiar Receta (actualizar relaciones)
            try:
                from restaurant.models import Receta
                recetas = Receta.objects.filter(producto=producto)
                count = recetas.count()
                recetas.update(producto=None)
                resultado["Receta"] = count
                mensaje = f"Actualizadas {count} relaciones Receta"
                print(mensaje)
                logger.info(mensaje)
            except ImportError:
                mensaje = "Modelo Receta no encontrado"
                print(mensaje)
                logger.warning(mensaje)
            except Exception as e:
                mensaje = f"Error actualizando Receta: {e}"
                print(mensaje)
                logger.error(mensaje)
                raise
            
            # 4. Limpiar OrdenItem
            try:
                from dashboard.models_ventas import OrdenItem
                ordenes = OrdenItem.objects.filter(producto=producto)
                count = ordenes.count()
                ordenes.delete()
                resultado["OrdenItem"] = count
                mensaje = f"Eliminadas {count} relaciones OrdenItem"
                print(mensaje)
                logger.info(mensaje)
            except ImportError:
                mensaje = "Modelo OrdenItem no encontrado"
                print(mensaje)
                logger.warning(mensaje)
            except Exception as e:
                mensaje = f"Error eliminando OrdenItem: {e}"
                print(mensaje)
                logger.error(mensaje)
                raise
            
            # 5. Limpiar DetalleVenta
            try:
                from dashboard.models_ventas import DetalleVenta
                detalles = DetalleVenta.objects.filter(producto=producto)
                count = detalles.count()
                detalles.delete()
                resultado["DetalleVenta"] = count
                mensaje = f"Eliminadas {count} relaciones DetalleVenta"
                print(mensaje)
                logger.info(mensaje)
            except ImportError:
                mensaje = "Modelo DetalleVenta no encontrado"
                print(mensaje)
                logger.warning(mensaje)
            except Exception as e:
                mensaje = f"Error eliminando DetalleVenta: {e}"
                print(mensaje)
                logger.error(mensaje)
                raise
            
            # 6. Limpiar otras tablas con SQL directo
            tablas_posibles = [
                'mesero_ordenitem',
                'mesero_orden',
                'cashier_detalleventa'
            ]
            
            with connection.cursor() as cursor:
                for tabla in tablas_posibles:
                    try:
                        # Verificar si existe la tabla
                        cursor.execute(
                            f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{tabla}'"
                        )
                        if cursor.fetchone()[0] == 0:
                            continue
                        
                        # Verificar si tiene columna producto_id
                        cursor.execute(f"PRAGMA table_info({tabla})")
                        columnas = cursor.fetchall()
                        tiene_producto_id = any(col[1] == 'producto_id' for col in columnas)
                        
                        if tiene_producto_id:
                            # Verificar si hay referencias
                            cursor.execute(f"SELECT COUNT(*) FROM {tabla} WHERE producto_id = ?", [producto_id])
                            count = cursor.fetchone()[0]
                            
                            if count > 0:
                                # Eliminar referencias
                                cursor.execute(f"DELETE FROM {tabla} WHERE producto_id = ?", [producto_id])
                                resultado["Otras"] += count
                                mensaje = f"Eliminadas {count} referencias en tabla {tabla}"
                                print(mensaje)
                                logger.info(mensaje)
                    except Exception as e:
                        mensaje = f"Error eliminando referencias en tabla {tabla}: {e}"
                        print(mensaje)
                        logger.error(mensaje)
        
        # Resumen de limpieza
        print("\nRESUMEN DE LIMPIEZA:")
        logger.info("RESUMEN DE LIMPIEZA:")
        for tipo, cantidad in resultado.items():
            mensaje = f"  - {tipo}: {cantidad}"
            print(mensaje)
            logger.info(mensaje)
        
        total_limpiados = sum(resultado.values())
        mensaje = f"  Total de dependencias limpiadas: {total_limpiados}"
        print(mensaje)
        logger.info(mensaje)
        
        return True, f"Se limpiaron {total_limpiados} dependencias", resultado
    
    except Exception as e:
        mensaje = f"ERROR en limpieza de dependencias: {e}"
        print(mensaje)
        logger.error(mensaje)
        traceback.print_exc()
        logger.error(traceback.format_exc())
        return False, str(e), resultado

def eliminar_producto_forzado(producto_id):
    """Elimina un producto de forma forzada, limpiando todas sus dependencias primero"""
    print_separator(f"ELIMINACIÓN FORZADA PRODUCTO ID: {producto_id}")
    logger.info(f"Iniciando eliminación forzada para producto ID: {producto_id}")
    
    try:
        # Verificar si el producto existe
        existe, producto = verificar_producto_existe(producto_id)
        if not existe:
            mensaje = f"ERROR: Producto con ID {producto_id} no existe"
            print(mensaje)
            logger.error(mensaje)
            return False, mensaje
        
        nombre_producto = producto.nombre
        mensaje = f"Producto encontrado: {nombre_producto} (ID: {producto_id})"
        print(mensaje)
        logger.info(mensaje)
        
        # Verificar dependencias
        _, _, dependencias = verificar_dependencias(producto_id)
        total_deps = sum(dependencias.values())
        
        if total_deps > 0:
            mensaje = f"El producto tiene {total_deps} dependencias que deben limpiarse"
            print(mensaje)
            logger.info(mensaje)
            
            # Limpiar dependencias
            exito, mensaje_limpieza, _ = limpiar_dependencias(producto_id)
            if not exito:
                mensaje = f"Error al limpiar dependencias: {mensaje_limpieza}"
                print(mensaje)
                logger.error(mensaje)
                return False, mensaje
            
            mensaje = f"Dependencias limpiadas con éxito: {mensaje_limpieza}"
            print(mensaje)
            logger.info(mensaje)
        else:
            mensaje = "El producto no tiene dependencias que bloqueen su eliminación"
            print(mensaje)
            logger.info(mensaje)
        
        # Ahora intentar eliminar el producto
        print("\nEliminando producto...")
        logger.info("Eliminando producto...")
        try:
            with transaction.atomic():
                resultado = producto.delete()
                mensaje = f"Resultado: {resultado}"
                print(mensaje)
                logger.info(mensaje)
                
                # Verificar si se eliminó correctamente
                try:
                    ProductoVenta.objects.get(id=producto_id)
                    mensaje = f"ERROR: El producto {nombre_producto} (ID: {producto_id}) aún existe después de eliminarlo"
                    print(mensaje)
                    logger.error(mensaje)
                    return False, mensaje
                except ProductoVenta.DoesNotExist:
                    mensaje = f"ÉXITO: Producto {nombre_producto} (ID: {producto_id}) eliminado correctamente"
                    print(mensaje)
                    logger.info(mensaje)
                    return True, mensaje
        except Exception as e:
            mensaje = f"ERROR al eliminar producto: {e}"
            print(mensaje)
            logger.error(mensaje)
            traceback.print_exc()
            logger.error(traceback.format_exc())
            
            # Intentar SQL directo como último recurso
            print("\nIntentando eliminación por SQL directo...")
            logger.info("Intentando eliminación por SQL directo...")
            try:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM restaurant_productoventa WHERE id = ?", [producto_id])
                    if cursor.rowcount == 1:
                        mensaje = f"ÉXITO: Producto {nombre_producto} (ID: {producto_id}) eliminado por SQL directo"
                        print(mensaje)
                        logger.info(mensaje)
                        return True, mensaje
                    else:
                        mensaje = f"ERROR: No se pudo eliminar el producto por SQL directo (filas afectadas: {cursor.rowcount})"
                        print(mensaje)
                        logger.error(mensaje)
                        return False, mensaje
            except Exception as e:
                mensaje = f"ERROR en eliminación SQL directa: {e}"
                print(mensaje)
                logger.error(mensaje)
                traceback.print_exc()
                logger.error(traceback.format_exc())
                return False, mensaje
    
    except Exception as e:
        mensaje = f"ERROR global en eliminación forzada: {e}"
        print(mensaje)
        logger.error(mensaje)
        traceback.print_exc()
        logger.error(traceback.format_exc())
        return False, str(e)

def eliminar_producto_normal(producto_id):
    """Intenta eliminar un producto de forma normal usando Django ORM"""
    print_separator(f"ELIMINACIÓN NORMAL PRODUCTO ID: {producto_id}")
    logger.info(f"Iniciando eliminación normal para producto ID: {producto_id}")
    
    try:
        # Verificar si el producto existe
        existe, producto = verificar_producto_existe(producto_id)
        if not existe:
            mensaje = f"ERROR: Producto con ID {producto_id} no existe"
            print(mensaje)
            logger.error(mensaje)
            return False, mensaje
        
        nombre_producto = producto.nombre
        mensaje = f"Producto encontrado: {nombre_producto} (ID: {producto_id})"
        print(mensaje)
        logger.info(mensaje)
        
        # Intentar eliminar normalmente
        print("\nIntento de eliminación normal usando Django ORM")
        logger.info("Intentando eliminación normal usando Django ORM")
        try:
            resultado = producto.delete()
            mensaje = f"Resultado: {resultado}"
            print(mensaje)
            logger.info(mensaje)
            
            # Verificar si se eliminó correctamente
            try:
                ProductoVenta.objects.get(id=producto_id)
                mensaje = f"ERROR: El producto {nombre_producto} (ID: {producto_id}) aún existe después de eliminarlo"
                print(mensaje)
                logger.error(mensaje)
                return False, mensaje
            except ProductoVenta.DoesNotExist:
                mensaje = f"ÉXITO: Producto {nombre_producto} (ID: {producto_id}) eliminado correctamente"
                print(mensaje)
                logger.info(mensaje)
                return True, mensaje
        except ProtectedError as e:
            mensaje = f"ERROR (ProtectedError): {e}"
            print(mensaje)
            logger.error(mensaje)
            return False, f"El producto está protegido por relaciones: {e}"
        except Exception as e:
            mensaje = f"ERROR: {e}"
            print(mensaje)
            logger.error(mensaje)
            traceback.print_exc()
            logger.error(traceback.format_exc())
            return False, str(e)
    
    except Exception as e:
        mensaje = f"ERROR global en eliminación normal: {e}"
        print(mensaje)
        logger.error(mensaje)
        traceback.print_exc()
        logger.error(traceback.format_exc())
        return False, str(e)

def main():
    """Función principal"""
    print_separator("FORZADOR DE ELIMINACIÓN DE PRODUCTOS")
    logger.info("="*30)
    logger.info("INICIANDO FORZADOR DE ELIMINACIÓN DE PRODUCTOS")
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
    print("1. Eliminar producto por ID")
    print("2. Buscar y eliminar producto por nombre")
    print("3. Listar todos los productos")
    print("4. Diagnóstico de producto")
    
    try:
        modo = int(input("\nSeleccione un modo (1-4): "))
    except ValueError:
        modo = 3  # Por defecto listar productos
    
    # Ejecutar según el modo seleccionado
    if modo == 1:
        # Eliminar por ID
        try:
            producto_id = int(input("\nIngrese el ID del producto a eliminar: "))
        except ValueError:
            print("ID inválido. Operación cancelada.")
            logger.error("ID inválido ingresado por el usuario. Operación cancelada.")
            return
        
        ejecutar_eliminacion(producto_id)
    
    elif modo == 2:
        # Buscar y eliminar por nombre
        busqueda = input("\nIngrese parte del nombre del producto a buscar: ")
        productos = listar_productos(busqueda)
        
        if productos.count() == 0:
            print("No se encontraron productos con ese criterio.")
            logger.info("No se encontraron productos con el criterio de búsqueda.")
            return
        
        try:
            seleccion = int(input("\nSeleccione el número del producto a eliminar (o 0 para cancelar): "))
            if seleccion == 0 or seleccion > productos.count():
                print("Operación cancelada.")
                logger.info("Operación cancelada por el usuario.")
                return
            
            producto_id = productos[seleccion-1].id
            ejecutar_eliminacion(producto_id)
        except (ValueError, IndexError):
            print("Selección inválida. Operación cancelada.")
            logger.error("Selección inválida. Operación cancelada.")
            return
    
    elif modo == 3:
        # Listar todos los productos
        productos = listar_productos()
        
        if productos.count() == 0:
            print("No hay productos en la base de datos.")
            logger.info("No hay productos en la base de datos.")
            return
        
        try:
            seleccion = int(input("\n¿Desea eliminar algún producto? Ingrese su número (o 0 para cancelar): "))
            if seleccion == 0 or seleccion > productos.count():
                print("Operación cancelada.")
                logger.info("Operación cancelada por el usuario.")
                return
            
            producto_id = productos[seleccion-1].id
            ejecutar_eliminacion(producto_id)
        except (ValueError, IndexError):
            print("Selección inválida. Operación cancelada.")
            logger.error("Selección inválida. Operación cancelada.")
            return
    
    elif modo == 4:
        # Diagnóstico de producto
        try:
            producto_id = int(input("\nIngrese el ID del producto a diagnosticar: "))
        except ValueError:
            print("ID inválido. Operación cancelada.")
            logger.error("ID inválido ingresado por el usuario. Operación cancelada.")
            return
        
        existe, producto = verificar_producto_existe(producto_id)
        if not existe:
            print(f"El producto con ID {producto_id} no existe.")
            logger.error(f"El producto con ID {producto_id} no existe.")
            return
        
        print(f"Diagnóstico para producto: {producto.nombre} (ID: {producto_id})")
        logger.info(f"Iniciando diagnóstico para producto: {producto.nombre} (ID: {producto_id})")
        
        # Verificar dependencias
        verificar_dependencias(producto_id)
        
        # Preguntar si desea eliminar
        try:
            eliminar = input("\n¿Desea eliminar este producto? (s/n): ").lower()
            if eliminar != 's':
                print("Operación cancelada.")
                logger.info("Operación cancelada por el usuario.")
                return
            
            ejecutar_eliminacion(producto_id)
        except Exception as e:
            print(f"Error: {e}")
            logger.error(f"Error en diagnóstico: {e}")
            traceback.print_exc()
            logger.error(traceback.format_exc())
    
    else:
        print("Modo no válido. Operación cancelada.")
        logger.error("Modo no válido seleccionado. Operación cancelada.")
        return

def ejecutar_eliminacion(producto_id):
    """Ejecuta el proceso de eliminación para un producto"""
    print_separator(f"PROCESO DE ELIMINACIÓN PARA PRODUCTO ID: {producto_id}")
    logger.info(f"Iniciando proceso de eliminación para producto ID: {producto_id}")
    
    # Verificar si el producto existe
    existe, producto = verificar_producto_existe(producto_id)
    if not existe:
        print(f"El producto con ID {producto_id} no existe.")
        logger.error(f"El producto con ID {producto_id} no existe.")
        return
    
    print(f"Se eliminará el producto: {producto.nombre} (ID: {producto_id})")
    logger.info(f"Se eliminará el producto: {producto.nombre} (ID: {producto_id})")
    
    # Preguntar tipo de eliminación
    print("\nTIPOS DE ELIMINACIÓN:")
    print("1. Eliminación normal (Django ORM)")
    print("2. Eliminación forzada (limpia dependencias)")
    
    try:
        tipo = int(input("\nSeleccione tipo de eliminación (1-2): "))
        if tipo not in [1, 2]:
            print("Tipo no válido. Usando eliminación normal.")
            logger.warning("Tipo no válido seleccionado. Usando eliminación normal.")
            tipo = 1
    except ValueError:
        print("Valor no válido. Usando eliminación normal.")
        logger.warning("Valor no válido ingresado. Usando eliminación normal.")
        tipo = 1
    
    # Confirmar eliminación
    confirmacion = input(f"\n¿Está seguro de eliminar el producto '{producto.nombre}'? (s/n): ").lower()
    if confirmacion != 's':
        print("Operación cancelada.")
        logger.info("Operación cancelada por el usuario.")
        return
    
    # Ejecutar eliminación según el tipo seleccionado
    if tipo == 1:
        exito, mensaje = eliminar_producto_normal(producto_id)
    else:
        exito, mensaje = eliminar_producto_forzado(producto_id)
    
    # Verificar resultado
    if exito:
        print_separator("RESULTADO")
        print(f"ÉXITO: {mensaje}")
        logger.info(f"ÉXITO: {mensaje}")
    else:
        print_separator("RESULTADO")
        print(f"ERROR: {mensaje}")
        logger.error(f"ERROR: {mensaje}")
        
        # Si falló la eliminación normal, ofrecer la forzada
        if tipo == 1:
            intentar_forzado = input("\n¿Desea intentar la eliminación forzada? (s/n): ").lower()
            if intentar_forzado == 's':
                print("\nIntentando eliminación forzada...")
                logger.info("Usuario solicitó intentar eliminación forzada después de fallo en eliminación normal")
                exito, mensaje = eliminar_producto_forzado(producto_id)
                
                if exito:
                    print_separator("RESULTADO FINAL")
                    print(f"ÉXITO EN ELIMINACIÓN FORZADA: {mensaje}")
                    logger.info(f"ÉXITO EN ELIMINACIÓN FORZADA: {mensaje}")
                else:
                    print_separator("RESULTADO FINAL")
                    print(f"ERROR EN ELIMINACIÓN FORZADA: {mensaje}")
                    logger.error(f"ERROR EN ELIMINACIÓN FORZADA: {mensaje}")
    
    # Verificar estado final
    existe, _ = verificar_producto_existe(producto_id)
    if not existe:
        print(f"\nVERIFICACIÓN FINAL: Producto con ID {producto_id} ya no existe en la base de datos.")
        logger.info(f"VERIFICACIÓN FINAL: Producto con ID {producto_id} ya no existe en la base de datos.")
    else:
        print(f"\nVERIFICACIÓN FINAL: ¡ALERTA! Producto con ID {producto_id} todavía existe en la base de datos.")
        logger.error(f"VERIFICACIÓN FINAL: ¡ALERTA! Producto con ID {producto_id} todavía existe en la base de datos.")
    
    # Mostrar productos restantes
    time.sleep(1)  # Pequeña pausa para asegurar que los cambios estén sincronizados
    listar_productos()

if __name__ == "__main__":
    main()
