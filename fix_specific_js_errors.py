#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corregir los errores específicos de sintaxis JavaScript sin afectar otras funciones
"""

import re
import os

def fix_specific_javascript_errors():
    file_path = r'c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\inventario.html'
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    print("🔧 Corrigiendo errores específicos de JavaScript...")
    
    # 1. Corregir el error de sintaxis en línea ~1268 (fetch con template malformateado)
    # Buscar y corregir el fetch problemático
    fetch_pattern = r"fetch\(`{%\s*url\s*'dashboard:eliminar_insumo'\s*0\s*%}`\.replace\('0',\s*insumoId\),\s*{"
    if re.search(fetch_pattern, content):
        print("✅ Corrigiendo fetch URL en función eliminarInsumo...")
        content = re.sub(
            r"fetch\(`{%\s*url\s*'dashboard:eliminar_insumo'\s*0\s*%}`\.replace\('0',\s*insumoId\),",
            "fetch(`{% url 'dashboard:eliminar_insumo' 0 %}`.replace('0', insumoId),",
            content
        )
    
    # 2. Eliminar funciones duplicadas y mantener solo las correctas
    lines = content.split('\n')
    cleaned_lines = []
    skip_lines = 0
    function_definitions_seen = set()
    
    for i, line in enumerate(lines):
        if skip_lines > 0:
            skip_lines -= 1
            continue
            
        # Detectar funciones duplicadas
        func_match = re.match(r'^\s*function\s+(\w+)\s*\(', line)
        if func_match:
            func_name = func_match.group(1)
            
            # Si es una función que ya vimos y es una de las problemáticas, saltarla
            if func_name in ['abrirModalCategoria', 'abrirModalUnidad'] and func_name in function_definitions_seen:
                print(f"🗑️  Eliminando función duplicada: {func_name}")
                # Buscar el final de la función y saltarla
                brace_count = 0
                j = i
                while j < len(lines):
                    if '{' in lines[j]:
                        brace_count += lines[j].count('{')
                    if '}' in lines[j]:
                        brace_count -= lines[j].count('}')
                    if brace_count == 0 and j > i:
                        skip_lines = j - i
                        break
                    j += 1
                continue
            else:
                function_definitions_seen.add(func_name)
        
        cleaned_lines.append(line)
    
    content = '\n'.join(cleaned_lines)
    
    # 3. Asegurar que las funciones necesarias estén definidas
    required_functions = {
        'abrirModalCategoria': '''function abrirModalCategoria() {
    const modal = new bootstrap.Modal(document.getElementById('nuevaCategoriaModal'));
    cargarCategorias();
    modal.show();
}''',
        'abrirModalUnidad': '''function abrirModalUnidad() {
    const modal = new bootstrap.Modal(document.getElementById('nuevaUnidadModal'));
    cargarUnidades();
    modal.show();
}''',
        'cargarCategorias': '''function cargarCategorias() {
    fetch('{% url "dashboard:get_form_data" %}')
        .then(response => response.json())
        .then(data => {
            const listaCategorias = document.getElementById('listaCategorias');
            if (data.categorias && data.categorias.length > 0) {
                let html = '<div class="row g-2">';
                data.categorias.forEach(categoria => {
                    html += `
                        <div class="col-md-6">
                            <div class="badge bg-primary bg-opacity-10 text-primary p-2 w-100 text-start">
                                <i class="fas fa-tag me-2"></i>${categoria.nombre}
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                listaCategorias.innerHTML = html;
            } else {
                listaCategorias.innerHTML = `
                    <div class="text-center text-muted">
                        <i class="fas fa-info-circle me-2"></i>
                        No hay categorías registradas aún
                    </div>
                `;
            }
        })
        .catch(error => {
            document.getElementById('listaCategorias').innerHTML = `
                <div class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error al cargar categorías
                </div>
            `;
        });
}''',
        'cargarUnidades': '''function cargarUnidades() {
    fetch('{% url "dashboard:get_form_data" %}')
        .then(response => response.json())
        .then(data => {
            const listaUnidades = document.getElementById('listaUnidades');
            if (data.unidades && data.unidades.length > 0) {
                let html = '<div class="row g-2">';
                data.unidades.forEach(unidad => {
                    html += `
                        <div class="col-md-6">
                            <div class="badge bg-success bg-opacity-10 text-success p-2 w-100 text-start">
                                <i class="fas fa-balance-scale me-2"></i>${unidad.nombre} (${unidad.abreviacion})
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                listaUnidades.innerHTML = html;
            } else {
                listaUnidades.innerHTML = `
                    <div class="text-center text-muted">
                        <i class="fas fa-info-circle me-2"></i>
                        No hay unidades registradas aún
                    </div>
                `;
            }
        })
        .catch(error => {
            document.getElementById('listaUnidades').innerHTML = `
                <div class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error al cargar unidades
                </div>
            `;
        });
}'''
    }
    
    # Verificar qué funciones faltan y agregarlas
    functions_added = 0
    for func_name, func_code in required_functions.items():
        if f'function {func_name}(' not in content:
            print(f"➕ Agregando función faltante: {func_name}")
            # Agregar antes del cierre del script
            script_end = content.rfind('</script>')
            if script_end != -1:
                content = content[:script_end] + f'\n\n{func_code}\n\n' + content[script_end:]
                functions_added += 1
    
    # 4. Verificar y corregir llamadas a cargarDatosFormulario
    if 'cargarDatosFormulario();' not in content:
        print("🔄 Asegurando que cargarDatosFormulario se llame al abrir el modal...")
        # Buscar el event listener del modal y agregar la llamada
        modal_listener_pattern = r"modal\.addEventListener\('show\.bs\.modal',\s*function\(\)\s*{"
        if re.search(modal_listener_pattern, content):
            content = re.sub(
                modal_listener_pattern,
                "modal.addEventListener('show.bs.modal', function() {\n            cargarDatosFormulario();",
                content
            )
    
    # Verificar si se hicieron cambios
    if content != original_content:
        # Crear backup
        backup_path = file_path + '.syntax_fix_backup.' + str(int(os.path.getmtime(file_path)))
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"📁 Backup creado: {backup_path}")
        
        # Escribir archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n🎉 CORRECCIÓN ESPECÍFICA COMPLETADA")
        print(f"📊 Funciones agregadas: {functions_added}")
        print(f"📁 Archivo corregido: {file_path}")
        
        return True
    else:
        print("ℹ️  No se necesitaron cambios")
        return False

def verify_functions():
    """Verificar que las funciones necesarias estén presentes"""
    file_path = r'c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\inventario.html'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_functions = [
        'function cargarDatosFormulario(',
        'function abrirModalCategoria(',
        'function abrirModalUnidad(',
        'function cargarCategorias(',
        'function cargarUnidades(',
        'function crearInsumo('
    ]
    
    print("\n🔍 Verificando funciones necesarias:")
    all_present = True
    
    for func in required_functions:
        if func in content:
            print(f"✅ {func.replace('function ', '').replace('(', '')}: Presente")
        else:
            print(f"❌ {func.replace('function ', '').replace('(', '')}: Faltante")
            all_present = False
    
    return all_present

def main():
    """Función principal"""
    print("🔧 CORRECCIÓN ESPECÍFICA DE ERRORES JAVASCRIPT")
    print("=" * 50)
    
    success = fix_specific_javascript_errors()
    
    print("\n" + "=" * 50)
    print("🔍 Verificando resultado...")
    functions_ok = verify_functions()
    
    print("=" * 50)
    if success and functions_ok:
        print("✅ Corrección completada exitosamente")
        print("💡 Recarga la página y prueba los botones '+' en el formulario")
    else:
        print("⚠️  Puede que aún haya problemas")
        print("🔍 Revisar manualmente los errores en la consola del navegador")

if __name__ == "__main__":
    main()
