#!/usr/bin/env python3
"""
Script para corregir errores específicos de sintaxis JavaScript
"""

import re

def fix_javascript_syntax():
    """Corregir errores específicos de sintaxis JavaScript"""
    print("🔧 === CORRIGIENDO ERRORES DE SINTAXIS JAVASCRIPT ===")
    
    file_path = r'c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\inventario.html'
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Lista de correcciones específicas
    corrections = [
        # Corregir comentarios perdidos y espacios
        (r'document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{          // Verificar elementos críticos', 
         'document.addEventListener(\'DOMContentLoaded\', function() {\n    // Verificar elementos críticos'),
        
        # Corregir bloques else vacíos
        (r'        if \(elemento\) \{            \}', 
         '        if (elemento) {\n            // Elemento encontrado\n        }'),
        
        # Corregir estructuras console.log perdidas
        (r'    console\.log\(\'📝 Formulario encontrado:\', form\);      if \(!form\) \{        alert\(\'Error: No se encontró el formulario\'\);',
         '    if (!form) {\n        alert(\'Error: No se encontró el formulario\');'),
        
        # Corregir espacios en console.log
        (r'    console\.log\(\'  - Código:\', formData\.get\(\'codigo\'\)\);\n    console\.log\(\'  - Stock actual:\', formData\.get\(\'stock_actual\'\)\);\n    console\.log\(\'  - Stock mínimo:\', formData\.get\(\'stock_minimo\'\)\);\n    console\.log\(\'  - Precio unitario:\', formData\.get\(\'precio_unitario\'\)\);',
         '    // Validación de datos del formulario'),
        
        # Corregir función crearInsumo línea inicial
        (r'function crearInsumo\(\) \{    // Verificar si ya se está procesando una petición',
         'function crearInsumo() {\n    // Verificar si ya se está procesando una petición'),
        
        # Corregir if conditions
        (r'    if \(creandoInsumo\) \{        return;',
         '    if (creandoInsumo) {\n        return;'),
        
        # Corregir FormData
        (r'    const formData = new FormData\(form\);    // Validar campos obligatorios',
         '    const formData = new FormData(form);\n    \n    // Validar campos obligatorios'),
        
        # Corregir declaración de variables
        (r'    const unidad_medida = formData\.get\(\'unidad_medida\'\);      if \(!nombre',
         '    const unidad_medida = formData.get(\'unidad_medida\');\n    \n    if (!nombre'),
        
        # Corregir console.error
        (r'        console\.error\(\'❌ ERROR: Campos obligatorios faltantes\'\);        console\.log\(\'  - Unidad medida válida:\', !!unidad_medida\);',
         '        // Campos obligatorios faltantes'),
        
        # Corregir formData.set
        (r'    formData\.set\(\'tipo\', \'basico\'\);    // Generar código si no existe',
         '    formData.set(\'tipo\', \'basico\');\n    \n    // Generar código si no existe'),
        
        # Corregir formData.set codigo
        (r'        formData\.set\(\'codigo\', codigo\);    \}',
         '        formData.set(\'codigo\', codigo);\n    }'),
        
        # Corregir CSRF token
        (r'    const csrfToken = document\.querySelector\(\'\[name=csrfmiddlewaretoken\]\'\);    console\.log\(\'🔐 CSRF Token value:\', csrfToken \? csrfToken\.value : \'NO ENCONTRADO\'\);      if \(!csrfToken\) \{        alert\(\'Error: Token de seguridad no encontrado\'\);',
         '    const csrfToken = document.querySelector(\'[name=csrfmiddlewaretoken]\');\n    \n    if (!csrfToken) {\n        alert(\'Error: Token de seguridad no encontrado\');'),
        
        # Corregir bloques else vacíos en cargar datos
        (r'            \} else \{            \}',
         '            }'),
        
        # Corregir catch errors
        (r'        \}\).catch\(error => \{            mostrarNotificacionElegante\(',
         '        }).catch(error => {\n            mostrarNotificacionElegante('),
        
        # Corregir líneas de comentarios perdidos
        (r'            // Mostrar notificación elegante principal\n            mostrarNotificacionElegante\(',
         '            // Mostrar notificación elegante principal\n            mostrarNotificacionElegante('),
        
        # Corregir form.reset
        (r'            // Limpiar formulario            form\.reset\(\);',
         '            // Limpiar formulario\n            form.reset();'),
        
        # Corregir modal.hide
        (r'            // Cerrar modal            const modal = bootstrap\.Modal\.getInstance\(document\.getElementById\(\'nuevoInsumoModal\'\)\);',
         '            // Cerrar modal\n            const modal = bootstrap.Modal.getInstance(document.getElementById(\'nuevoInsumoModal\'));'),
        
        # Corregir else vacíos en modal
        (r'                modal\.hide\(\);            \} else \{            \}',
         '                modal.hide();\n            }'),
        
        # Corregir window.location.reload
        (r'            // Recargar página inmediatamente para mostrar el nuevo insumo            window\.location\.reload\(\);',
         '            // Recargar página inmediatamente para mostrar el nuevo insumo\n            window.location.reload();'),
        
        # Corregir else principal
        (r'        \} else \{            // Ocultar notificación de carga',
         '        } else {\n            // Ocultar notificación de carga'),
        
        # Corregir catch principal
        (r'    \}\).catch\(error => \{          // Ocultar notificación de carga',
         '    }).catch(error => {\n        // Ocultar notificación de carga'),
    ]
    
    # Aplicar correcciones
    for pattern, replacement in corrections:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Corregir espacios y tabulaciones
    content = re.sub(r'([{}])\s*([{}])', r'\1\n    \2', content)  # Mejorar formato
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # Reducir líneas vacías múltiples
    
    # Escribir archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Errores de sintaxis JavaScript corregidos")
    print("📝 Se aplicaron múltiples correcciones de formato")

if __name__ == "__main__":
    fix_javascript_syntax()
