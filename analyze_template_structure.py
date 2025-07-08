import os
import re
import shutil

def analyze_template_structure():
    # Define la ruta del archivo
    file_path = r'c:\Users\olcha\Desktop\sushi_restaurant - Copy (2)\suchilitoo2\dashboard\templates\dashboard\productos_venta\lista.html'
    base_path = r'c:\Users\olcha\Desktop\sushi_restaurant - Copy (2)\suchilitoo2\dashboard\templates\dashboard\base.html'
    
    # Verifica que ambos archivos existan
    if not os.path.exists(file_path):
        print(f"Error: El archivo {file_path} no existe.")
        return False
    
    if not os.path.exists(base_path):
        print(f"Error: El archivo base {base_path} no existe.")
        return False
    
    # Lee los contenidos
    with open(file_path, 'r', encoding='utf-8') as file:
        lista_content = file.read()
    
    with open(base_path, 'r', encoding='utf-8') as file:
        base_content = file.read()
    
    # Análisis de bloques en base.html
    base_blocks = re.findall(r'{% block (\w+) %}', base_content)
    print("\n=== Bloques definidos en base.html ===")
    for block in base_blocks:
        print(f"- {block}")
    
    # Análisis de bloques en lista.html
    lista_blocks = re.findall(r'{% block (\w+) %}', lista_content)
    print("\n=== Bloques usados en lista.html ===")
    for block in lista_blocks:
        print(f"- {block}")
    
    # Verificar si hay bloques en lista.html que no están en base.html
    invalid_blocks = [block for block in lista_blocks if block not in base_blocks]
    if invalid_blocks:
        print("\n⚠️ ADVERTENCIA: Bloques utilizados en lista.html que no están definidos en base.html:")
        for block in invalid_blocks:
            print(f"- {block}")
    
    # Verificar estructura del bloque extra_js
    extra_js_in_base = "{% block extra_js %}" in base_content
    extra_js_in_lista = "{% block extra_js %}" in lista_content
    
    print(f"\n=== Análisis del bloque extra_js ===")
    print(f"- Bloque extra_js definido en base.html: {'✅ Sí' if extra_js_in_base else '❌ No'}")
    print(f"- Bloque extra_js usado en lista.html: {'✅ Sí' if extra_js_in_lista else '❌ No'}")
    
    # Verificar scripts
    scripts_in_lista = re.findall(r'<script[^>]*>(.*?)</script>', lista_content, re.DOTALL)
    print(f"\n=== Análisis de scripts en lista.html ===")
    print(f"- Número de bloques <script> encontrados: {len(scripts_in_lista)}")
    
    # Verificar si hay scripts fuera de bloques
    for i, script in enumerate(scripts_in_lista):
        script_pos = lista_content.find(f'<script>{script}</script>')
        if script_pos != -1:
            before_script = lista_content[:script_pos]
            nearest_block_start = max(before_script.rfind('{% block '), before_script.rfind('{% endblock %}'))
            
            if nearest_block_start != -1 and before_script[nearest_block_start:nearest_block_start+9] == '{% block ':
                block_name = re.search(r'{% block (\w+) %}', before_script[nearest_block_start:], re.DOTALL)
                if block_name:
                    print(f"- Script #{i+1} está dentro del bloque: {block_name.group(1)}")
            else:
                print(f"- ⚠️ Script #{i+1} parece estar fuera de cualquier bloque")
    
    # Crear una versión simplificada para diagnóstico
    simplified_path = file_path + '.simplified'
    with open(simplified_path, 'w', encoding='utf-8') as file:
        file.write("""{% extends 'dashboard/base.html' %}
{% load static %}

{% block title %}Diagnóstico JavaScript{% endblock %}

{% block content %}
<div class="container">
    <h1>Diagnóstico de JavaScript</h1>
    <p>Esta página es para diagnosticar problemas con la carga de JavaScript.</p>
    
    <div class="alert alert-info">
        <p>Si ves este mensaje y el indicador azul abajo a la derecha, el JavaScript se está cargando correctamente.</p>
    </div>
    
    <div class="my-4">
        <button id="testButton" class="btn btn-primary">Probar JavaScript</button>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    console.log('🔍 [DEBUG] JavaScript de diagnóstico cargado', {
        time: new Date().toISOString(),
        page: 'diagnóstico',
        url: window.location.href
    });
    
    // Mostrar un indicador visual de que el JS está cargado
    window.addEventListener('DOMContentLoaded', function() {
        // Crear un elemento de notificación
        const debugNotification = document.createElement('div');
        debugNotification.style.position = 'fixed';
        debugNotification.style.bottom = '20px';
        debugNotification.style.right = '20px';
        debugNotification.style.backgroundColor = 'rgba(0, 128, 255, 0.9)';
        debugNotification.style.color = 'white';
        debugNotification.style.padding = '10px 15px';
        debugNotification.style.borderRadius = '5px';
        debugNotification.style.zIndex = '9999';
        debugNotification.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
        debugNotification.textContent = '✓ JavaScript de diagnóstico cargado correctamente';
        
        // Añadir al DOM
        document.body.appendChild(debugNotification);
        
        // Configurar botón de prueba
        document.getElementById('testButton').addEventListener('click', function() {
            alert('¡El JavaScript funciona correctamente!');
            console.log('Botón de prueba clickeado');
        });
    });
</script>
{% endblock %}
""")
    print(f"\n✅ Creada página simplificada para diagnóstico en: {simplified_path}")
    
    # Crear un archivo HTML estático para pruebas directas
    static_path = file_path[:-5] + '_diagnostico.html'
    with open(static_path, 'w', encoding='utf-8') as file:
        file.write("""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Diagnóstico JavaScript - Página Estática</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h1 class="h4 mb-0">Diagnóstico JavaScript - Página Estática</h1>
            </div>
            <div class="card-body">
                <p>Esta es una página HTML estática para diagnóstico. Si ves la notificación azul, el JavaScript está funcionando correctamente.</p>
                
                <div class="alert alert-info">
                    <p>Esta página no requiere Django y debería funcionar directamente en el navegador.</p>
                </div>
                
                <div class="my-4">
                    <button id="testButton" class="btn btn-primary">Probar JavaScript</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        console.log('🔍 [DEBUG] JavaScript estático cargado', {
            time: new Date().toISOString(),
            page: 'diagnóstico-estático',
            url: window.location.href
        });
        
        // Mostrar un indicador visual de que el JS está cargado
        window.addEventListener('DOMContentLoaded', function() {
            // Crear un elemento de notificación
            const debugNotification = document.createElement('div');
            debugNotification.style.position = 'fixed';
            debugNotification.style.bottom = '20px';
            debugNotification.style.right = '20px';
            debugNotification.style.backgroundColor = 'rgba(0, 128, 255, 0.9)';
            debugNotification.style.color = 'white';
            debugNotification.style.padding = '10px 15px';
            debugNotification.style.borderRadius = '5px';
            debugNotification.style.zIndex = '9999';
            debugNotification.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
            debugNotification.textContent = '✓ JavaScript estático cargado correctamente';
            
            // Añadir al DOM
            document.body.appendChild(debugNotification);
            
            // Configurar botón de prueba
            document.getElementById('testButton').addEventListener('click', function() {
                alert('¡El JavaScript funciona correctamente!');
                console.log('Botón de prueba clickeado');
            });
        });
    </script>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")
    print(f"✅ Creada página HTML estática para diagnóstico directo en: {static_path}")
    
    # Crear un script para crear una página de diagnóstico del modal
    diagnostico_modal_path = r'c:\Users\olcha\Desktop\sushi_restaurant - Copy (2)\suchilitoo2\crear_pagina_diagnostico_modal.py'
    with open(diagnostico_modal_path, 'w', encoding='utf-8') as file:
        file.write("""import os

def crear_pagina_diagnostico():
    # Definir ruta del archivo
    file_path = r'c:\\Users\\olcha\\Desktop\\sushi_restaurant - Copy (2)\\suchilitoo2\\dashboard\\templates\\dashboard\\productos_venta\\diagnostico_modal.html'
    
    # Crear el contenido
    content = '''{% extends 'dashboard/base.html' %}
{% load static %}

{% block title %}Diagnóstico de Modal{% endblock %}

{% block content %}
<div class="container-fluid px-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="h3 mb-1">
                <i class="fas fa-bug me-2 text-primary"></i>
                Diagnóstico de Modal y JavaScript
            </h1>
            <p class="text-muted mb-0">
                Página para diagnosticar problemas con modales y JavaScript
            </p>
        </div>
    </div>

    <div class="row mb-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">Prueba de Modal y JavaScript</h5>
                </div>
                <div class="card-body">
                    <p>Esta página permite diagnosticar si los modales y el JavaScript están funcionando correctamente.</p>
                    
                    <div class="mb-4">
                        <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#testModal"
                                data-id="123" data-nombre="Producto de Prueba">
                            <i class="fas fa-exclamation-triangle me-2"></i>Abrir Modal de Prueba
                        </button>
                    </div>
                    
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>Instrucciones:</strong> Haz clic en el botón para abrir un modal de prueba. Verifica que:
                        <ul>
                            <li>El modal se abre correctamente</li>
                            <li>Los datos del producto aparecen en el modal</li>
                            <li>En la consola del navegador aparecen los logs de debug</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Modal para prueba -->
<div class="modal fade" id="testModal" tabindex="-1" aria-labelledby="testModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header bg-primary text-white">
                <h5 class="modal-title" id="testModalLabel">Confirmación de Prueba</h5>
                <button type="button" class="btn-close bg-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <p>¿Estás seguro de que deseas eliminar el producto <strong id="productoNombre"></strong>?</p>
                <p>ID del producto: <strong id="productoId"></strong></p>
                
                <form id="testForm" method="post" action="/test-action/">
                    {% csrf_token %}
                    <input type="hidden" name="producto_id" id="producto_id_input" value="">
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <button type="button" class="btn btn-danger" id="confirmarAccion">Confirmar</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    // Log de inicio
    console.log('🔍 [DEBUG] Página de diagnóstico de modal cargada', {
        time: new Date().toISOString(),
        page: 'diagnostico_modal.html',
        url: window.location.href
    });
    
    // Mostrar indicador visual
    window.addEventListener('DOMContentLoaded', function() {
        // Crear elemento de notificación
        const debugNotification = document.createElement('div');
        debugNotification.style.position = 'fixed';
        debugNotification.style.bottom = '20px';
        debugNotification.style.right = '20px';
        debugNotification.style.backgroundColor = 'rgba(0, 128, 255, 0.9)';
        debugNotification.style.color = 'white';
        debugNotification.style.padding = '10px 15px';
        debugNotification.style.borderRadius = '5px';
        debugNotification.style.zIndex = '9999';
        debugNotification.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
        debugNotification.textContent = '✓ JavaScript de diagnóstico cargado';
        
        // Añadir al DOM
        document.body.appendChild(debugNotification);
        
        console.log('✅ [DOM] DOMContentLoaded ejecutado');
    });
    
    // Manejo del modal de prueba
    const testModal = document.getElementById('testModal');
    const testForm = document.getElementById('testForm');
    
    if (testModal) {
        console.log('✅ [MODAL] Modal de prueba encontrado');
        
        // Evento cuando se abre el modal
        testModal.addEventListener('show.bs.modal', function (event) {
            console.log('📖 [MODAL] Modal de prueba abriéndose...');
            
            const button = event.relatedTarget;
            const productoId = button.getAttribute('data-id');
            const productoNombre = button.getAttribute('data-nombre');
            
            console.log(`🎯 [MODAL] Producto seleccionado para prueba:`, {
                id: productoId,
                nombre: productoNombre,
                button: button,
                buttonTagName: button.tagName,
                buttonClasses: button.className
            });
            
            document.getElementById('productoNombre').textContent = productoNombre;
            document.getElementById('productoId').textContent = productoId;
            document.getElementById('producto_id_input').value = productoId;
            
            console.log(`📋 [FORM] Campo producto_id actualizado a: ${document.getElementById('producto_id_input').value}`);
        });
        
        // Evento cuando se confirma el modal
        testModal.addEventListener('shown.bs.modal', function (event) {
            console.log('✅ [MODAL] Modal completamente visible');
        });
        
        // Manejar el botón de confirmar
        document.getElementById('confirmarAccion').addEventListener('click', function() {
            const productoId = document.getElementById('producto_id_input').value;
            console.log(`👆 [CLICK] Botón confirmar clickeado para producto ID: ${productoId}`);
            
            // No enviamos el formulario, solo simulamos
            alert(`Acción confirmada para producto ID: ${productoId}`);
            
            // Cerrar el modal
            const modalInstance = bootstrap.Modal.getInstance(testModal);
            modalInstance.hide();
        });
    } else {
        console.error('❌ [ERROR] Modal de prueba no encontrado');
    }
    
    // Log para clicks globales (debugging)
    document.addEventListener('click', function(event) {
        if (event.target.matches('button, a, [data-bs-toggle]')) {
            console.log('👆 [GLOBAL-CLICK] Click en elemento interactivo:', {
                element: event.target.tagName,
                classes: event.target.className,
                id: event.target.id,
                text: event.target.textContent?.trim().substring(0, 50),
                timestamp: new Date().toISOString()
            });
        }
    });
</script>
{% endblock %}'''
    
    # Crear el archivo
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"✅ Creada página de diagnóstico de modal en: {file_path}")
    print("Puedes acceder a esta página en tu navegador usando la URL:")
    print("/dashboard/productos-venta/diagnostico-modal/")
    print("Asegúrate de agregar esta URL a urls.py")

# Ejecutar la función
if __name__ == "__main__":
    crear_pagina_diagnostico()
""")
    print(f"✅ Creado script para generar página de diagnóstico de modal: {diagnostico_modal_path}")
    
    # Crear un script para añadir la URL
    add_url_path = r'c:\Users\olcha\Desktop\sushi_restaurant - Copy (2)\suchilitoo2\agregar_url_diagnostico.py'
    with open(add_url_path, 'w', encoding='utf-8') as file:
        file.write('''import os
import re

def agregar_url_diagnostico():
    # Definir ruta del archivo
    urls_path = r'c:\\Users\\olcha\\Desktop\\sushi_restaurant - Copy (2)\\suchilitoo2\\dashboard\\urls.py'
    
    # Verificar que el archivo existe
    if not os.path.exists(urls_path):
        print(f"Error: El archivo {urls_path} no existe.")
        return False
    
    # Leer el contenido
    with open(urls_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Crear una copia de seguridad
    backup_path = urls_path + '.backup'
    with open(backup_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Copia de seguridad creada en: {backup_path}")
    
    # Buscar dónde añadir la nueva URL
    productos_pattern = r'(path\\(\'productos-venta/.*?\',.*?\\),)'
    productos_urls = re.findall(productos_pattern, content, re.DOTALL)
    
    if productos_urls:
        # Encontrar la última URL de productos
        last_url = productos_urls[-1]
        
        # Preparar la nueva URL
        nueva_url = "path('productos-venta/diagnostico-modal/', views.diagnostico_modal, name='diagnostico_modal'),"
        
        # Insertar la nueva URL después de la última URL de productos
        content_modified = content.replace(last_url, last_url + "\\n    " + nueva_url)
        
        # Guardar el contenido modificado
        with open(urls_path, 'w', encoding='utf-8') as file:
            file.write(content_modified)
        
        print("✅ URL de diagnóstico añadida correctamente")
        
        # Ahora crear la vista
        views_path = r'c:\\Users\\olcha\\Desktop\\sushi_restaurant - Copy (2)\\suchilitoo2\\dashboard\\views\\productos_venta_views.py'
        
        if os.path.exists(views_path):
            # Leer el contenido
            with open(views_path, 'r', encoding='utf-8') as file:
                views_content = file.read()
            
            # Crear copia de seguridad
            views_backup = views_path + '.backup'
            with open(views_backup, 'w', encoding='utf-8') as file:
                file.write(views_content)
            print(f"Copia de seguridad de views creada en: {views_backup}")
            
            # Añadir la vista de diagnóstico
            nueva_vista = '''

@login_required
def diagnostico_modal(request):
    """
    Vista para página de diagnóstico de modal y JavaScript
    """
    print("DEBUG: Cargando página de diagnóstico de modal")
    
    return render(request, 'dashboard/productos_venta/diagnostico_modal.html', {
        'sidebar_active': 'productos_venta',
    })
'''
            
            # Añadir la vista al final del archivo
            with open(views_path, 'a', encoding='utf-8') as file:
                file.write(nueva_vista)
            
            print("✅ Vista de diagnóstico añadida correctamente")
        else:
            print(f"Error: El archivo de vistas {views_path} no existe.")
    else:
        print("No se encontraron URLs de productos en el archivo urls.py")
        return False
    
    return True

# Ejecutar la función
if __name__ == "__main__":
    agregar_url_diagnostico()
""")
    print(f"✅ Creado script para añadir URL de diagnóstico: {add_url_path}")
    
    return True

# Ejecutar la función principal
if __name__ == "__main__":
    analyze_template_structure()
