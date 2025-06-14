#!/usr/bin/env python3
"""
Script para verificar la funcionalidad de creación de categorías y unidades
"""
import os
import sys
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.template.loader import get_template
from django.contrib.auth import get_user_model
from restaurant.models import CategoriaInsumo, UnidadMedida

def verificar_modales():
    """Verificar si los modales están presentes en el template"""
    print("🔍 VERIFICANDO MODALES EN TEMPLATE")
    print("=" * 60)
    
    try:
        template = get_template('dashboard/inventario.html')
        content = template.template.source
        
        # Verificar modal de categoría
        if 'nuevaCategoriaModal' in content:
            print("✅ Modal de categoría encontrado")
            
            # Verificar formulario
            if 'nuevaCategoriaForm' in content:
                print("   ✅ Formulario de categoría encontrado")
            else:
                print("   ❌ Formulario de categoría NO encontrado")
        else:
            print("❌ Modal de categoría NO encontrado")
        
        # Verificar modal de unidad
        if 'nuevaUnidadModal' in content:
            print("✅ Modal de unidad encontrado")
            
            # Verificar formulario
            if 'nuevaUnidadForm' in content:
                print("   ✅ Formulario de unidad encontrado")
            else:
                print("   ❌ Formulario de unidad NO encontrado")
        else:
            print("❌ Modal de unidad NO encontrado")
        
        # Verificar JS
        if 'crearCategoria' in content:
            print("✅ Función crearCategoria encontrada en template")
        else:
            print("❌ Función crearCategoria NO encontrada en template")
        
        if 'crearUnidadMedida' in content:
            print("✅ Función crearUnidadMedida encontrada en template")
        else:
            print("❌ Función crearUnidadMedida NO encontrada en template")
    
    except Exception as e:
        print(f"❌ Error al verificar template: {str(e)}")

def verificar_script():
    """Verificar si el archivo de script existe"""
    print("\n🔍 VERIFICANDO ARCHIVOS JS")
    print("=" * 60)
      script_path = os.path.join('dashboard', 'static', 'dashboard', 'js', 'categorias_unidades.js')
    if os.path.exists(script_path):
        print(f"✅ Script encontrado: {script_path}")
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Verificar funciones
                if 'function crearCategoria()' in content:
                    print("   ✅ Función crearCategoria() definida")
                else:
                    print("   ❌ Función crearCategoria() NO definida")
                
                if 'function crearUnidadMedida()' in content:
                    print("   ✅ Función crearUnidadMedida() definida")
                else:
                    print("   ❌ Función crearUnidadMedida() NO definida")
                
                # Verificar eventos
                if 'formCategoria.addEventListener' in content:
                    print("   ✅ Evento para formulario de categoría configurado")
                else:
                    print("   ❌ Evento para formulario de categoría NO configurado")
                
                if 'formUnidad.addEventListener' in content:
                    print("   ✅ Evento para formulario de unidad configurado")
                else:
                    print("   ❌ Evento para formulario de unidad NO configurado")
        except Exception as e:
            print(f"   ❌ Error al leer el archivo: {str(e)}")
    else:
        print(f"❌ Script NO encontrado: {script_path}")

def verificar_vistas():
    """Verificar si las vistas están definidas"""
    print("\n🔍 VERIFICANDO VISTAS")
    print("=" * 60)
    
    views_path = os.path.join('dashboard', 'views', 'categorias_unidades_views.py')
    if os.path.exists(views_path):
        print(f"✅ Archivo de vistas encontrado: {views_path}")
        
        # Verificar funciones
        with open(views_path, 'r') as f:
            content = f.read()
            
            if 'def crear_categoria(' in content:
                print("   ✅ Vista crear_categoria definida")
            else:
                print("   ❌ Vista crear_categoria NO definida")
            
            if 'def crear_unidad(' in content:
                print("   ✅ Vista crear_unidad definida")
            else:
                print("   ❌ Vista crear_unidad NO definida")
            
            if 'def listar_categorias(' in content:
                print("   ✅ Vista listar_categorias definida")
            else:
                print("   ❌ Vista listar_categorias NO definida")
            
            if 'def listar_unidades(' in content:
                print("   ✅ Vista listar_unidades definida")
            else:
                print("   ❌ Vista listar_unidades NO definida")
    else:
        print(f"❌ Archivo de vistas NO encontrado: {views_path}")

def verificar_urls():
    """Verificar si las URLs están configuradas"""
    print("\n🔍 VERIFICANDO URLS")
    print("=" * 60)
    
    urls_path = os.path.join('dashboard', 'urls.py')
    if os.path.exists(urls_path):
        print(f"✅ Archivo de URLs encontrado: {urls_path}")
        
        with open(urls_path, 'r') as f:
            content = f.read()
            
            # Verificar importación
            if 'from .views import categorias_unidades_views' in content:
                print("   ✅ Importación de vistas encontrada")
            else:
                print("   ❌ Importación de vistas NO encontrada")
            
            # Verificar rutas
            urls_to_check = [
                "path('categorias/crear/'",
                "path('categorias/listar/'",
                "path('unidades/crear/'",
                "path('unidades/listar/'"
            ]
            
            for url in urls_to_check:
                if url in content:
                    print(f"   ✅ URL encontrada: {url}")
                else:
                    print(f"   ❌ URL NO encontrada: {url}")
    else:
        print(f"❌ Archivo de URLs NO encontrado: {urls_path}")

def verificar_modelos():
    """Verificar si los modelos existen y están funcionando"""
    print("\n🔍 VERIFICANDO MODELOS")
    print("=" * 60)
    
    # Verificar CategoriaInsumo
    try:
        categorias_count = CategoriaInsumo.objects.count()
        print(f"✅ Modelo CategoriaInsumo disponible ({categorias_count} registros)")
        
        # Mostrar algunas categorías
        if categorias_count > 0:
            categorias = CategoriaInsumo.objects.all()[:5]
            print("   Ejemplos de categorías:")
            for cat in categorias:
                print(f"   - {cat.nombre}")
    except Exception as e:
        print(f"❌ Error al verificar CategoriaInsumo: {str(e)}")
    
    # Verificar UnidadMedida
    try:
        unidades_count = UnidadMedida.objects.count()
        print(f"✅ Modelo UnidadMedida disponible ({unidades_count} registros)")
        
        # Mostrar algunas unidades
        if unidades_count > 0:
            unidades = UnidadMedida.objects.all()[:5]
            print("   Ejemplos de unidades:")
            for unidad in unidades:
                print(f"   - {unidad.nombre} ({unidad.abreviacion})")
    except Exception as e:
        print(f"❌ Error al verificar UnidadMedida: {str(e)}")

def main():
    print("🔍 VERIFICACIÓN DE FUNCIONALIDAD DE CATEGORÍAS Y UNIDADES")
    print("=" * 60)
    
    verificar_modales()
    verificar_script()
    verificar_vistas()
    verificar_urls()
    verificar_modelos()
    
    print("\n✅ VERIFICACIÓN COMPLETADA")
    print("=" * 60)
    print("Para probar la funcionalidad:")
    print("1. Inicia el servidor con: python manage.py runserver")
    print("2. Accede a la página de inventario")
    print("3. Intenta crear una categoría y una unidad")
    print("4. Verifica que se muestren las notificaciones de éxito")

if __name__ == "__main__":
    main()
