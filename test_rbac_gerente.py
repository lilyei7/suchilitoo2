#!/usr/bin/env python
"""
Script para probar las restricciones RBAC del gerente.
Verifica que el gerente solo tenga acceso a inventario básico de su sucursal.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario, Rol, Sucursal
from restaurant.models import Insumo, Inventario
from dashboard.utils.permissions import get_user_permissions, has_module_access, has_submodule_access
from django.contrib.auth import get_user_model

def test_gerente_permissions():
    """Prueba las restricciones de permisos del gerente"""
    print("=" * 60)
    print("PRUEBA DE RESTRICCIONES RBAC PARA GERENTE")
    print("=" * 60)
    
    try:
        # Buscar un usuario gerente
        rol_gerente = Rol.objects.filter(nombre='gerente').first()
        if not rol_gerente:
            print("❌ No se encontró el rol 'gerente'")
            return
        
        gerente = Usuario.objects.filter(rol=rol_gerente).first()
        if not gerente:
            print("❌ No se encontró ningún usuario con rol gerente")
            return
        
        print(f"✅ Probando permisos para usuario: {gerente.username} (Rol: {gerente.rol.nombre})")
        print(f"   Sucursal: {gerente.sucursal.nombre if gerente.sucursal else 'Sin sucursal'}")
        print()
        
        # Obtener permisos del usuario
        permisos = get_user_permissions(gerente)
        print("📋 PERMISOS DEL GERENTE:")
        print("-" * 40)
          # Probar acceso a módulos
        modulos_permitidos = ['inventario']
        modulos_negados = ['recetas', 'productos_venta', 'usuarios', 'sucursales']
        
        print("🔓 MÓDULOS PERMITIDOS:")
        for modulo in modulos_permitidos:
            tiene_acceso = has_module_access(gerente, modulo)
            print(f"   {modulo}: {'✅' if tiene_acceso else '❌'}")
        
        print("\n🔒 MÓDULOS NEGADOS:")
        for modulo in modulos_negados:
            tiene_acceso = has_module_access(gerente, modulo)
            print(f"   {modulo}: {'❌' if not tiene_acceso else '⚠️  PERMITIDO (ERROR)'}")
          # Probar submódulos de inventario
        print("\n📦 SUBMÓDULOS DE INVENTARIO:")
        submodulos_permitidos = ['insumos', 'entradas_salidas', 'proveedores']  # Para gerente
        submodulos_negados = ['compuestos', 'elaborados']
        
        print("   🔓 Permitidos:")
        for submodulo in submodulos_permitidos:
            tiene_acceso = has_submodule_access(gerente, 'inventario', submodulo)
            print(f"      inventario.{submodulo}: {'✅' if tiene_acceso else '❌'}")
        
        print("   🔒 Negados:")
        for submodulo in submodulos_negados:
            tiene_acceso = has_submodule_access(gerente, 'inventario', submodulo)
            print(f"      inventario.{submodulo}: {'❌' if not tiene_acceso else '⚠️  PERMITIDO (ERROR)'}")
        
        # Probar características especiales
        print("\n🎯 CARACTERÍSTICAS ESPECIALES:")
        if hasattr(gerente, 'has_feature'):
            filtrar_sucursal = gerente.has_feature('filtrar_por_sucursal')
            ver_datos_sensibles = gerente.has_feature('ver_datos_sensibles')
            print(f"   filtrar_por_sucursal: {'✅' if filtrar_sucursal else '❌'}")
            print(f"   ver_datos_sensibles: {'❌' if not ver_datos_sensibles else '⚠️  PERMITIDO (ERROR)'}")
        else:
            print("   ⚠️  Método has_feature no disponible")
        
        # Probar filtros de sucursal
        print("\n🏪 FILTROS POR SUCURSAL:")
        if gerente.sucursal:            # Contar insumos totales vs insumos de la sucursal del gerente
            total_insumos = Insumo.objects.count()
            inventarios_sucursal = Inventario.objects.filter(sucursal=gerente.sucursal).count()
            
            print(f"   Total insumos en sistema: {total_insumos}")
            print(f"   Inventarios en sucursal del gerente: {inventarios_sucursal}")
            print(f"   ✅ El gerente debería ver solo los de su sucursal")
        else:
            print("   ⚠️  El gerente no tiene sucursal asignada")
        
        print("\n" + "=" * 60)
        print("RESUMEN:")
        print("✅ Gerente DEBE tener acceso a:")
        print("   - inventario.insumos (básicos)")
        print("   - inventario.entradas_salidas")
        print("   - inventario.proveedores")
        print("   - Filtrado por su propia sucursal")
        print()
        print("❌ Gerente NO DEBE tener acceso a:")
        print("   - inventario.compuestos")
        print("   - inventario.elaborados")
        print("   - recetas")
        print("   - usuarios")
        print("   - sucursales")
        print("   - Ver datos sensibles")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

def test_admin_permissions():
    """Prueba que el admin siga teniendo acceso completo"""
    print("\n" + "=" * 60)
    print("PRUEBA DE PERMISOS ADMIN (VERIFICACIÓN)")
    print("=" * 60)
    
    try:
        # Buscar un usuario admin
        admin = Usuario.objects.filter(is_superuser=True).first()
        if not admin:
            print("❌ No se encontró ningún usuario admin")
            return
        
        print(f"✅ Probando permisos para admin: {admin.username}")
        
        # El admin debería tener acceso a todo
        modulos_test = ['inventario', 'recetas', 'usuarios', 'sucursales']
        
        print("🔓 ACCESO A MÓDULOS:")
        for modulo in modulos_test:
            tiene_acceso = has_module_access(admin, modulo)
            print(f"   {modulo}: {'✅' if tiene_acceso else '❌ ERROR'}")
        
    except Exception as e:
        print(f"❌ Error durante la prueba admin: {e}")

if __name__ == "__main__":
    test_gerente_permissions()
    test_admin_permissions()
