#!/usr/bin/env python
"""
Script para diagnosticar problemas con la eliminación de productos en la base de datos
"""

import os
import django
import logging
import traceback
import json
import sys
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importar modelos relevantes
from django.contrib.auth.models import User
from django.db import connection, transaction, IntegrityError, OperationalError
from restaurant.models import ProductoVenta, CategoriaProducto
from django.db.models import ProtectedError

def print_separator(title=None):
    """Imprime un separador con título opcional"""
    if title:
        print("\n" + "="*20 + f" {title} " + "="*20)
    else:
        print("\n" + "="*50)

def listar_productos():
    """Lista todos los productos en la base de datos"""
    print_separator("PRODUCTOS ACTUALES")
    productos = ProductoVenta.objects.all().order_by('id')
    print(f"Total de productos encontrados: {productos.count()}")
    
    if productos.count() > 0:
        for producto in productos:
            print(f"ID: {producto.id} | Nombre: {producto.nombre} | Precio: ${producto.precio} | Categoría: {producto.categoria.nombre if producto.categoria else 'Sin categoría'}")
    else:
        print("No hay productos en la base de datos.")
    
    return productos

def verificar_dependencias(producto_id):
    """Verifica dependencias que podrían bloquear la eliminación"""
    print_separator(f"DEPENDENCIAS PARA PRODUCTO ID: {producto_id}")
    
    try:
        producto = ProductoVenta.objects.get(id=producto_id)
        print(f"Verificando dependencias para: {producto.nombre} (ID: {producto_id})")
        
        # 1. Verificar relaciones directas
        print("\n1. Relaciones directas:")
        
        # ProductoReceta
        try:
            from restaurant.models import ProductoReceta
            recetas = ProductoReceta.objects.filter(producto=producto)
            print(f"   ProductoReceta: {recetas.count()} relaciones")
            for receta in recetas:
                print(f"     - Producto-Receta ID: {receta.id}")
        except ImportError:
            print("   ProductoReceta: Modelo no encontrado")
        
        # ProductoCategoria
        try:
            from restaurant.models import ProductoCategoria
            categorias = ProductoCategoria.objects.filter(producto=producto)
            print(f"   ProductoCategoria: {categorias.count()} relaciones")
            for categoria in categorias:
                print(f"     - Producto-Categoría ID: {categoria.id}, Categoría: {categoria.categoria.nombre}")
        except ImportError:
            print("   ProductoCategoria: Modelo no encontrado")
        
        # Receta (relación inversa)
        try:
            from restaurant.models import Receta
            recetas_inv = Receta.objects.filter(producto=producto)
            print(f"   Receta (inversa): {recetas_inv.count()} relaciones")
            for receta in recetas_inv:
                print(f"     - Receta ID: {receta.id}")
        except ImportError:
            print("   Receta: Modelo no encontrado")
        
        # 2. Verificar relaciones en aplicación Dashboard
        print("\n2. Relaciones en Dashboard:")
        
        # OrdenItem
        try:
            from dashboard.models_ventas import OrdenItem
            ordenes = OrdenItem.objects.filter(producto=producto)
            print(f"   OrdenItem: {ordenes.count()} relaciones")
            for orden in ordenes:
                print(f"     - OrdenItem ID: {orden.id}, Orden: {orden.orden_id}")
        except ImportError:
            print("   OrdenItem: Modelo no encontrado")
        
        # DetalleVenta
        try:
            from dashboard.models_ventas import DetalleVenta
            detalles = DetalleVenta.objects.filter(producto=producto)
            print(f"   DetalleVenta: {detalles.count()} relaciones")
            for detalle in detalles:
                print(f"     - DetalleVenta ID: {detalle.id}, Venta: {detalle.venta_id}")
        except ImportError:
            print("   DetalleVenta: Modelo no encontrado")
            
        # 3. Verificar tablas relacionadas mediante consulta SQL directa
        print("\n3. Verificación SQL directa:")
        
        tablas_posibles = [
            'dashboard_ordenitem', 
            'dashboard_detalleventa', 
            'restaurant_productoreceta', 
            'restaurant_productocategoria',
            'restaurant_receta',
            'mesero_ordenitem',  # Posibles tablas huérfanas
            'mesero_orden'       # Posibles tablas huérfanas
        ]
        
        with connection.cursor() as cursor:
            for tabla in tablas_posibles:
                try:
                    # Primero verificar si existe la tabla
                    cursor.execute(
                        f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{tabla}'"
                    )
                    if cursor.fetchone()[0] == 0:
                        print(f"   Tabla '{tabla}' no existe en la base de datos")
                        continue
                    
                    # Verificar si tiene una columna producto_id
                    cursor.execute(f"PRAGMA table_info({tabla})")
                    columnas = cursor.fetchall()
                    tiene_producto_id = any(col[1] == 'producto_id' for col in columnas)
                    
                    if tiene_producto_id:
                        cursor.execute(f"SELECT COUNT(*) FROM {tabla} WHERE producto_id = ?", [producto_id])
                        count = cursor.fetchone()[0]
                        print(f"   Tabla {tabla}: {count} referencias")
                        
                        if count > 0:
                            cursor.execute(f"SELECT * FROM {tabla} WHERE producto_id = ? LIMIT 5", [producto_id])
                            rows = cursor.fetchall()
                            for row in rows:
                                print(f"     - Registro: {row}")
                    else:
                        print(f"   Tabla {tabla}: No tiene columna producto_id")
                        
                except Exception as e:
                    print(f"   Error verificando tabla {tabla}: {e}")
        
        return True, "Verificación de dependencias completada"
    
    except ProductoVenta.DoesNotExist:
        print(f"ERROR: Producto con ID {producto_id} no existe")
        return False, f"Producto con ID {producto_id} no existe"
    
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        return False, str(e)

def eliminar_producto_forzado(producto_id):
    """Intenta eliminar un producto de forma forzada usando SQL directo"""
    print_separator(f"ELIMINACIÓN FORZADA PRODUCTO ID: {producto_id}")
    
    try:
        # Primero verificar si el producto existe
        try:
            producto = ProductoVenta.objects.get(id=producto_id)
            nombre_producto = producto.nombre
            print(f"Producto encontrado: {nombre_producto} (ID: {producto_id})")
        except ProductoVenta.DoesNotExist:
            print(f"ERROR: Producto con ID {producto_id} no existe")
            return False, f"Producto con ID {producto_id} no existe"
        
        # Mostrar SQL que generaría Django
        print("\nSQL que Django ejecutaría:")
        print(ProductoVenta.objects.filter(id=producto_id).query)
        
        # Intento 1: Eliminar relaciones primero
        print("\nIntento 1: Eliminar relaciones primero")
        try:
            with transaction.atomic():
                # 1. Eliminar relaciones ProductoReceta
                from restaurant.models import ProductoReceta
                print("Eliminando relaciones ProductoReceta...")
                relaciones = ProductoReceta.objects.filter(producto=producto)
                count = relaciones.count()
                relaciones.delete()
                print(f"  {count} relaciones ProductoReceta eliminadas")
                
                # 2. Eliminar relaciones ProductoCategoria
                from restaurant.models import ProductoCategoria
                print("Eliminando relaciones ProductoCategoria...")
                categorias = ProductoCategoria.objects.filter(producto=producto)
                count = categorias.count()
                categorias.delete()
                print(f"  {count} relaciones ProductoCategoria eliminadas")
                
                # 3. Actualizar relaciones Receta (OneToOneField inversa)
                from restaurant.models import Receta
                print("Actualizando relaciones Receta...")
                recetas = Receta.objects.filter(producto=producto)
                count = recetas.count()
                recetas.update(producto=None)
                print(f"  {count} relaciones Receta actualizadas")
                
                # 4. Ahora intentar eliminar el producto
                print("Eliminando producto...")
                resultado = producto.delete()
                print(f"Resultado: {resultado}")
                print(f"Producto {nombre_producto} (ID: {producto_id}) eliminado exitosamente")
                return True, f"Producto {nombre_producto} (ID: {producto_id}) eliminado exitosamente"
        except ProtectedError as e:
            print(f"ERROR (ProtectedError): {e}")
            print("Fallback al siguiente método...")
        except Exception as e:
            print(f"ERROR: {e}")
            traceback.print_exc()
            print("Fallback al siguiente método...")
        
        # Intento 2: SQL directo
        print("\nIntento 2: SQL directo")
        try:
            with transaction.atomic():
                print("Ejecutando SQL directo para limpiar relaciones...")
                
                with connection.cursor() as cursor:
                    # 1. Eliminar ProductoReceta
                    try:
                        cursor.execute("DELETE FROM restaurant_productoreceta WHERE producto_id = ?", [producto_id])
                        print(f"  SQL: DELETE FROM restaurant_productoreceta WHERE producto_id = {producto_id}")
                        print(f"  Filas afectadas: {cursor.rowcount}")
                    except Exception as e:
                        print(f"  Error borrando ProductoReceta: {e}")
                    
                    # 2. Eliminar ProductoCategoria
                    try:
                        cursor.execute("DELETE FROM restaurant_productocategoria WHERE producto_id = ?", [producto_id])
                        print(f"  SQL: DELETE FROM restaurant_productocategoria WHERE producto_id = {producto_id}")
                        print(f"  Filas afectadas: {cursor.rowcount}")
                    except Exception as e:
                        print(f"  Error borrando ProductoCategoria: {e}")
                    
                    # 3. Actualizar Receta
                    try:
                        cursor.execute("UPDATE restaurant_receta SET producto_id = NULL WHERE producto_id = ?", [producto_id])
                        print(f"  SQL: UPDATE restaurant_receta SET producto_id = NULL WHERE producto_id = {producto_id}")
                        print(f"  Filas afectadas: {cursor.rowcount}")
                    except Exception as e:
                        print(f"  Error actualizando Receta: {e}")
                    
                    # 4. Eliminar el producto
                    try:
                        cursor.execute("DELETE FROM restaurant_productoventa WHERE id = ?", [producto_id])
                        print(f"  SQL: DELETE FROM restaurant_productoventa WHERE id = {producto_id}")
                        print(f"  Filas afectadas: {cursor.rowcount}")
                        
                        if cursor.rowcount == 1:
                            print(f"Producto {nombre_producto} (ID: {producto_id}) eliminado exitosamente por SQL directo")
                            return True, f"Producto {nombre_producto} (ID: {producto_id}) eliminado exitosamente por SQL directo"
                        else:
                            print(f"Error: No se pudo eliminar el producto (filas afectadas: {cursor.rowcount})")
                            return False, f"No se pudo eliminar el producto (filas afectadas: {cursor.rowcount})"
                    except Exception as e:
                        print(f"  Error borrando ProductoVenta: {e}")
                        raise
        except Exception as e:
            print(f"ERROR en SQL directo: {e}")
            traceback.print_exc()
        
        # Verificar si todavía existe
        try:
            producto_check = ProductoVenta.objects.get(id=producto_id)
            print(f"ERROR: El producto {nombre_producto} (ID: {producto_id}) aún existe después de los intentos de eliminación")
            return False, f"El producto {nombre_producto} (ID: {producto_id}) aún existe después de los intentos de eliminación"
        except ProductoVenta.DoesNotExist:
            print(f"ÉXITO: El producto {nombre_producto} (ID: {producto_id}) ya no existe en la base de datos")
            return True, f"El producto {nombre_producto} (ID: {producto_id}) ya no existe en la base de datos"
    
    except Exception as e:
        print(f"ERROR global: {e}")
        traceback.print_exc()
        return False, str(e)

def eliminar_producto_normal(producto_id):
    """Intenta eliminar un producto de forma normal usando Django ORM"""
    print_separator(f"ELIMINACIÓN NORMAL PRODUCTO ID: {producto_id}")
    
    try:
        # Verificar si el producto existe
        try:
            producto = ProductoVenta.objects.get(id=producto_id)
            nombre_producto = producto.nombre
            print(f"Producto encontrado: {nombre_producto} (ID: {producto_id})")
        except ProductoVenta.DoesNotExist:
            print(f"ERROR: Producto con ID {producto_id} no existe")
            return False, f"Producto con ID {producto_id} no existe"
        
        # Intentar eliminar normalmente
        print("\nIntento de eliminación normal usando Django ORM")
        try:
            resultado = producto.delete()
            print(f"Resultado: {resultado}")
            print(f"Producto {nombre_producto} (ID: {producto_id}) eliminado exitosamente")
            return True, f"Producto {nombre_producto} (ID: {producto_id}) eliminado exitosamente"
        except ProtectedError as e:
            print(f"ERROR (ProtectedError): {e}")
            print("El producto está protegido por relaciones que impiden su eliminación")
            return False, f"El producto está protegido por relaciones: {e}"
        except Exception as e:
            print(f"ERROR: {e}")
            traceback.print_exc()
            return False, str(e)
    
    except Exception as e:
        print(f"ERROR global: {e}")
        traceback.print_exc()
        return False, str(e)

def main():
    """Función principal"""
    print_separator("DIAGNÓSTICO DE ELIMINACIÓN DE PRODUCTOS")
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Django version: {django.get_version()}")
    print(f"Python version: {sys.version}")
    
    # Listar productos actuales
    productos = listar_productos()
    
    if productos.count() == 0:
        print("\nNo hay productos para eliminar.")
        return
    
    # Solicitar ID del producto a diagnosticar/eliminar
    if len(sys.argv) > 1:
        producto_id = int(sys.argv[1])
        print(f"\nUsando producto ID {producto_id} pasado como argumento")
    else:
        print("\nProductos disponibles:")
        for i, producto in enumerate(productos):
            print(f"{i+1}. ID: {producto.id} | {producto.nombre}")
        
        try:
            seleccion = int(input("\nSeleccione el número del producto a diagnosticar (o 0 para salir): "))
            if seleccion == 0:
                print("Saliendo...")
                return
            
            producto_id = productos[seleccion-1].id
        except (ValueError, IndexError):
            print("Selección inválida. Usando el primer producto.")
            producto_id = productos[0].id
    
    # Verificar dependencias del producto
    verificar_dependencias(producto_id)
    
    # Preguntar qué acción realizar
    print_separator("OPCIONES")
    print("1. Solo verificar (no eliminar)")
    print("2. Intentar eliminación normal")
    print("3. Forzar eliminación")
    
    try:
        accion = int(input("\nSeleccione una opción (1-3): "))
    except ValueError:
        accion = 1
    
    if accion == 2:
        # Intentar eliminación normal
        eliminar_producto_normal(producto_id)
    elif accion == 3:
        # Forzar eliminación
        eliminar_producto_forzado(producto_id)
    else:
        print("\nSolo verificación realizada. No se eliminó ningún producto.")
    
    # Listar productos después de la acción
    print_separator("ESTADO FINAL")
    listar_productos()

if __name__ == "__main__":
    main()
