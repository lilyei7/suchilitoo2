import os
import re

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
    
    # Comprobar si hay otras etiquetas scripts
    all_scripts = re.findall(r'<script.*?>', lista_content)
    if len(all_scripts) > len(scripts_in_lista):
        print(f"⚠️ ADVERTENCIA: Hay {len(all_scripts)} tags de apertura <script> pero solo {len(scripts_in_lista)} bloques completos.")
        
    # Crear página de diagnóstico simplificada
    diagnostico_path = r'c:\Users\olcha\Desktop\sushi_restaurant - Copy (2)\suchilitoo2\dashboard\templates\dashboard\productos_venta\diagnostico.html'
    with open(diagnostico_path, 'w', encoding='utf-8') as file:
        file.write('''{% extends 'dashboard/base.html' %}
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
{% endblock %}''')
    print(f"\n✅ Creada página simplificada para diagnóstico en: {diagnostico_path}")
    return True

if __name__ == "__main__":
    analyze_template_structure()
