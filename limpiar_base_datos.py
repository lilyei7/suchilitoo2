#!/usr/bin/env python
"""
Script para vaciar la base de datos manteniendo estructura y usuario admin
"""

import os
import django
import sys
from django.db import transaction

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from mesero.models import (
    Orden, OrdenItem, Mesa, HistorialMesa, HistorialOrden, 
    NotificacionCuenta, OpcionPersonalizacion, ProductoPersonalizacion,
    OrdenItemPersonalizacion
)
from restaurant.models import (
    ProductoVenta, CategoriaProducto, Insumo, InsumoCompuesto,
    MovimientoInventario, Receta, RecetaInsumo, CategoriaInsumo,
    UnidadMedida, Proveedor, Inventario, ProductoCategoria,
    CheckListItem, CheckListEjecucion, InsumoElaborado
)
from accounts.models import Usuario, Sucursal, Rol

User = get_user_model()

def limpiar_base_datos():
    """Limpia la base de datos manteniendo estructura y usuario admin"""
    
    print("=" * 80)
    print("🧹 LIMPIEZA DE BASE DE DATOS")
    print("=" * 80)
    print("⚠️  ADVERTENCIA: Esto eliminará TODOS los datos excepto el usuario admin")
    print("✅ Se mantendrá la estructura de las tablas")
    print("✅ Se conservará el usuario administrador")
    print()
    
    # Confirmación de seguridad
    respuesta = input("¿Estás seguro de continuar? (escribe 'SI CONFIRMO' para continuar): ")
    if respuesta != 'SI CONFIRMO':
        print("❌ Operación cancelada")
        return
    
    try:
        with transaction.atomic():
            print("\n🔍 Identificando usuario admin...")
            
            # Buscar usuario admin (superuser)
            admin_users = Usuario.objects.filter(is_superuser=True)
            if not admin_users.exists():
                print("❌ No se encontró usuario administrador")
                return
            
            admin_user = admin_users.first()
            print(f"✅ Usuario admin encontrado: {admin_user.username} (ID: {admin_user.id})")
            
            print("\n🗑️  Iniciando limpieza de datos...")
            
            # 1. ÓRDENES Y RELACIONADOS
            print("📋 Limpiando órdenes...")
            count_notificaciones = NotificacionCuenta.objects.count()
            count_historial_ordenes = HistorialOrden.objects.count()
            count_personalizaciones = OrdenItemPersonalizacion.objects.count()
            count_orden_items = OrdenItem.objects.count()
            count_ordenes = Orden.objects.count()
            
            NotificacionCuenta.objects.all().delete()
            HistorialOrden.objects.all().delete()
            OrdenItemPersonalizacion.objects.all().delete()
            OrdenItem.objects.all().delete()
            Orden.objects.all().delete()
            
            print(f"  - {count_notificaciones} notificaciones de cuenta")
            print(f"  - {count_historial_ordenes} registros de historial de órdenes")
            print(f"  - {count_personalizaciones} personalizaciones de items")
            print(f"  - {count_orden_items} items de órdenes")
            print(f"  - {count_ordenes} órdenes")
            
            # 2. MESAS Y HISTORIAL
            print("\n🏠 Limpiando mesas...")
            count_historial_mesas = HistorialMesa.objects.count()
            count_mesas = Mesa.objects.count()
            
            HistorialMesa.objects.all().delete()
            Mesa.objects.all().delete()
            
            print(f"  - {count_historial_mesas} registros de historial de mesas")
            print(f"  - {count_mesas} mesas")
            
            # 3. PRODUCTOS Y RECETAS
            print("\n🍽️  Limpiando productos y recetas...")
            count_prod_personal = ProductoPersonalizacion.objects.count()
            count_receta_insumos = RecetaInsumo.objects.count()
            count_recetas = Receta.objects.count()
            count_productos = ProductoVenta.objects.count()
            count_categorias = CategoriaProducto.objects.count()
            
            ProductoPersonalizacion.objects.all().delete()
            RecetaInsumo.objects.all().delete()
            Receta.objects.all().delete()
            ProductoVenta.objects.all().delete()
            
            # Intentar eliminar categorías de productos con manejo de errores
            try:
                CategoriaProducto.objects.all().delete()
                print(f"  - {count_categorias} categorías de productos")
            except Exception as e:
                print(f"  - ⚠️  Error eliminando categorías de productos: {str(e)}")
                print(f"  - ⚠️  Continuando sin eliminar categorías...")
            
            print(f"  - {count_prod_personal} personalizaciones de productos")
            print(f"  - {count_receta_insumos} insumos de recetas")
            print(f"  - {count_recetas} recetas")
            print(f"  - {count_productos} productos")
            
            # 4. INVENTARIO E INSUMOS
            print("\n📦 Limpiando inventario e insumos...")
            count_movimientos = MovimientoInventario.objects.count()
            count_inventarios = Inventario.objects.count()
            count_checklist_ejecuciones = CheckListEjecucion.objects.count()
            count_checklist_items = CheckListItem.objects.count()
            count_insumos_elaborados = InsumoElaborado.objects.count()
            count_insumos_comp = InsumoCompuesto.objects.count()
            count_insumos = Insumo.objects.count()
            count_categorias_insumo = CategoriaInsumo.objects.count()
            count_unidades = UnidadMedida.objects.count()
            
            MovimientoInventario.objects.all().delete()
            Inventario.objects.all().delete()
            CheckListEjecucion.objects.all().delete()
            CheckListItem.objects.all().delete()
            InsumoElaborado.objects.all().delete()
            InsumoCompuesto.objects.all().delete()
            Insumo.objects.all().delete()
            CategoriaInsumo.objects.all().delete()
            UnidadMedida.objects.all().delete()
            
            print(f"  - {count_movimientos} movimientos de inventario")
            print(f"  - {count_inventarios} registros de inventario")
            print(f"  - {count_checklist_ejecuciones} ejecuciones de checklist")
            print(f"  - {count_checklist_items} items de checklist")
            print(f"  - {count_insumos_elaborados} insumos elaborados")
            print(f"  - {count_insumos_comp} insumos compuestos")
            print(f"  - {count_insumos} insumos")
            print(f"  - {count_categorias_insumo} categorías de insumos")
            print(f"  - {count_unidades} unidades de medida")
            
            # 5. PROVEEDORES
            print("\n🚚 Limpiando proveedores...")
            count_proveedores = Proveedor.objects.count()
            Proveedor.objects.all().delete()
            print(f"  - {count_proveedores} proveedores")
            
            # 6. PERSONALIZACIONES
            print("\n⚙️  Limpiando personalizaciones...")
            
            # Intentar eliminar opciones de personalización con manejo de errores
            try:
                count_opciones = OpcionPersonalizacion.objects.count()
                OpcionPersonalizacion.objects.all().delete()
                print(f"  - {count_opciones} opciones de personalización")
            except Exception as e:
                print(f"  - ⚠️  Error eliminando opciones de personalización: {str(e)}")
                print(f"  - ⚠️  Puede ser por problemas de esquema de base de datos")
                # Intentar eliminar manualmente con SQL directo
                try:
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM mesero_opcionpersonalizacion")
                        print(f"  - ✅ Eliminadas opciones usando SQL directo")
                except Exception as sql_error:
                    print(f"  - ⚠️  Error con SQL directo: {str(sql_error)}")
                    print(f"  - ⚠️  Continuando sin eliminar opciones de personalización...")
            
            # 7. USUARIOS (excepto admin) Y ROLES
            print("\n👥 Limpiando usuarios y roles...")
            count_usuarios = Usuario.objects.exclude(id=admin_user.id).count()
            count_sucursales = Sucursal.objects.count()
            count_roles = Rol.objects.count()
            
            # Eliminar usuarios excepto el admin
            Usuario.objects.exclude(id=admin_user.id).delete()
            Sucursal.objects.all().delete()
            Rol.objects.all().delete()
            
            print(f"  - {count_usuarios} usuarios (conservando admin)")
            print(f"  - {count_sucursales} sucursales")
            print(f"  - {count_roles} roles")
            
            print("\n" + "=" * 80)
            print("✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
            print("=" * 80)
            print(f"🔐 Usuario administrador conservado: {admin_user.username}")
            print("📊 Base de datos limpia y lista para usar")
            print("🏗️  Estructura de tablas intacta")
            print()
            print("💡 Próximos pasos recomendados:")
            print("   1. Crear roles básicos (Admin, Gerente, Mesero, Cajero, etc.)")
            print("   2. Crear sucursales")
            print("   3. Crear usuarios de prueba")
            print("   4. Configurar mesas")
            print("   5. Cargar productos básicos")
            
    except Exception as e:
        print(f"\n❌ ERROR durante la limpieza: {str(e)}")
        print("🔄 La transacción fue revertida, no se perdieron datos")
        raise

def verificar_estado_bd():
    """Verifica el estado actual de la base de datos"""
    print("\n📊 ESTADO ACTUAL DE LA BASE DE DATOS:")
    print("-" * 50)
    
    # Conteos por tabla
    tablas = [
        ('Usuarios', Usuario.objects.count()),
        ('Roles', Rol.objects.count()),
        ('Sucursales', Sucursal.objects.count()),
        ('Mesas', Mesa.objects.count()),
        ('Órdenes', Orden.objects.count()),
        ('Items de Órdenes', OrdenItem.objects.count()),
        ('Productos', ProductoVenta.objects.count()),
        ('Categorías Productos', CategoriaProducto.objects.count()),
        ('Recetas', Receta.objects.count()),
        ('Insumos', Insumo.objects.count()),
        ('Categorías Insumos', CategoriaInsumo.objects.count()),
        ('Inventarios', Inventario.objects.count()),
        ('Proveedores', Proveedor.objects.count()),
        ('Movimientos Inventario', MovimientoInventario.objects.count()),
        ('Items Checklist', CheckListItem.objects.count()),
        ('Ejecuciones Checklist', CheckListEjecucion.objects.count()),
        ('Insumos Elaborados', InsumoElaborado.objects.count()),
    ]
    
    for nombre, count in tablas:
        print(f"  {nombre}: {count}")
    
    # Usuario admin
    admin_users = Usuario.objects.filter(is_superuser=True)
    if admin_users.exists():
        print(f"\n👑 Usuario admin: {admin_users.first().username}")
    else:
        print("\n⚠️  No hay usuario administrador")

if __name__ == "__main__":
    print("🔍 Verificando estado actual...")
    verificar_estado_bd()
    
    print("\n" + "=" * 80)
    limpiar_base_datos()
    
    print("\n🔍 Verificando estado después de la limpieza...")
    verificar_estado_bd()
