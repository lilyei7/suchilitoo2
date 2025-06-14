#!/usr/bin/env python
"""
Script final de verificación completa del sistema
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.urls import reverse

def final_system_verification():
    print("🎯 VERIFICACIÓN FINAL DEL SISTEMA")
    print("=" * 50)
    
    client = Client()
    
    # Login
    login_success = client.login(username='admin', password='admin123')
    print(f"🔐 Login del administrador: {'✅ EXITOSO' if login_success else '❌ FALLIDO'}")
    
    if not login_success:
        print("❌ No se puede continuar sin login")
        return
    
    # URLs principales del sistema
    urls_to_test = [
        ('dashboard:principal', 'Dashboard Principal'),
        ('dashboard:inventario', 'Inventario'),
        ('dashboard:insumos_elaborados', 'Insumos Elaborados'),
        ('dashboard:insumos_compuestos', 'Insumos Compuestos'),
        ('dashboard:proveedores', 'Proveedores'),
        ('dashboard:entradas_salidas', 'Entradas/Salidas'),
    ]
    
    all_working = True
    
    for url_name, description in urls_to_test:
        try:
            url = reverse(url_name)
            response = client.get(url)
            
            status_icon = "✅" if response.status_code == 200 else "❌"
            print(f"{status_icon} {description:<20} | Status: {response.status_code} | URL: {url}")
            
            if response.status_code != 200:
                all_working = False
                
            # Verificar contenido específico
            content = response.content.decode('utf-8')
            
            # Para insumos elaborados, verificar que los includes funcionan
            if url_name == 'dashboard:insumos_elaborados':
                has_categories_modal = 'gestionar_categorias' in content
                has_units_modal = 'gestionar_unidades' in content
                print(f"   📋 Modal categorías: {'✅' if has_categories_modal else '❌'}")
                print(f"   📏 Modal unidades: {'✅' if has_units_modal else '❌'}")
                
                if not (has_categories_modal and has_units_modal):
                    all_working = False
                    
        except Exception as e:
            print(f"❌ {description:<20} | ERROR: {str(e)}")
            all_working = False
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN FINAL:")
    
    if all_working:
        print("🎉 ¡TODAS LAS PÁGINAS FUNCIONAN CORRECTAMENTE!")
        print("✅ Los templates cargan sin errores")
        print("✅ Los modales están incluidos correctamente")
        print("✅ La autenticación funciona")
        print("✅ Las rutas responden correctamente")
    else:
        print("⚠️  Hay algunos problemas detectados")
        
    print("\n🔧 VERIFICACIONES ADICIONALES:")
    
    # Verificar archivos de templates críticos
    template_files = [
        'dashboard/templates/dashboard/insumos_elaborados.html',
        'dashboard/templates/dashboard/insumos_compuestos.html', 
        'dashboard/templates/dashboard/proveedores.html',
        'dashboard/templates/dashboard/modals/gestionar_categorias.html',
        'dashboard/templates/dashboard/modals/gestionar_unidades.html',
    ]
    
    for template_file in template_files:
        template_path = os.path.join(os.getcwd(), template_file)
        exists = os.path.exists(template_path)
        print(f"{'✅' if exists else '❌'} {template_file}")
        
        if exists:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > 100:  # Verificar que no esté vacío
                    print(f"   📄 Contenido: {len(content)} caracteres")
                else:
                    print(f"   ⚠️  Archivo muy pequeño: {len(content)} caracteres")
    
    print("\n🚀 El sistema está listo para usar!")
    print("📝 Para acceder:")
    print("   1. Servidor: http://127.0.0.1:8001/")
    print("   2. Usuario: admin")
    print("   3. Contraseña: admin123")

if __name__ == "__main__":
    final_system_verification()
