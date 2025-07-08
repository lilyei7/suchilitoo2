import os
import re

def verificar_funcionamiento_boton_eliminar():
    """
    Verifica el funcionamiento del botón de eliminar productos
    """
    # Define la ruta del archivo
    file_path = r'c:\Users\olcha\Desktop\sushi_restaurant - Copy (2)\suchilitoo2\dashboard\templates\dashboard\productos_venta\lista.html'
    
    # Lee el contenido del archivo
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Analizar el modal de eliminación
    print("\n=== ANÁLISIS DEL MODAL DE ELIMINACIÓN ===")
    modal_match = re.search(r'<div class="modal fade" id="deleteModal".*?</div>\s*</div>\s*</div>', content, re.DOTALL)
    
    if modal_match:
        modal_content = modal_match.group(0)
        print("✅ Modal de eliminación encontrado")
        
        # Verificar el formulario dentro del modal
        form_match = re.search(r'<form.*?id="deleteForm".*?</form>', modal_content, re.DOTALL)
        if form_match:
            form_content = form_match.group(0)
            print("✅ Formulario de eliminación encontrado")
            
            # Verificar el campo oculto para el ID del producto
            input_match = re.search(r'<input type="hidden" name="producto_id".*?>', form_content)
            if input_match:
                print("✅ Campo oculto para ID del producto encontrado")
                print(f"  - Input: {input_match.group(0)}")
            else:
                print("❌ No se encontró el campo oculto para el ID del producto")
                
            # Verificar el método del formulario
            method_match = re.search(r'method="(.*?)"', form_content)
            if method_match:
                method = method_match.group(1)
                print(f"✅ Método del formulario: {method}")
            else:
                print("❌ No se especificó un método para el formulario")
                
            # Verificar la acción del formulario
            action_match = re.search(r'action="(.*?)"', form_content)
            if action_match:
                action = action_match.group(1)
                print(f"✅ Acción del formulario: {action}")
            else:
                print("❌ No se especificó una acción para el formulario")
        else:
            print("❌ No se encontró el formulario en el modal")
    else:
        print("❌ No se encontró el modal de eliminación")
    
    # Analizar el evento de apertura del modal
    print("\n=== ANÁLISIS DEL JAVASCRIPT DE ELIMINACIÓN ===")
    modal_event_match = re.search(r'deleteModal\.addEventListener\(\'show\.bs\.modal\', function \(event\).*?\}\);', content, re.DOTALL)
    
    if modal_event_match:
        modal_event = modal_event_match.group(0)
        print("✅ Evento de apertura del modal encontrado")
        
        # Verificar cómo se obtiene el ID del producto
        id_get_match = re.search(r'const productoId = (.*?);', modal_event)
        if id_get_match:
            id_get = id_get_match.group(1)
            print(f"✅ Obtención del ID del producto: {id_get}")
        else:
            print("❌ No se encontró cómo se obtiene el ID del producto")
            
        # Verificar cómo se establece el ID en el campo oculto
        id_set_match = re.search(r'document\.getElementById\(\'producto_id_input\'\)\.value = (.*?);', modal_event)
        if id_set_match:
            id_set = id_set_match.group(1)
            print(f"✅ Establecimiento del ID en el campo oculto: {id_set}")
        else:
            print("❌ No se encontró cómo se establece el ID en el campo oculto")
    else:
        print("❌ No se encontró el evento de apertura del modal")
    
    # Buscar botones de eliminar en la tabla
    print("\n=== ANÁLISIS DE BOTONES DE ELIMINACIÓN ===")
    delete_buttons = re.findall(r'<button.*?data-bs-toggle="modal".*?data-bs-target="#deleteModal".*?</button>', content, re.DOTALL)
    
    if delete_buttons:
        print(f"✅ Se encontraron {len(delete_buttons)} botones de eliminación")
        
        # Analizar un ejemplo de botón
        example_button = delete_buttons[0]
        
        # Verificar los atributos data-*
        data_id_match = re.search(r'data-id="(.*?)"', example_button)
        if data_id_match:
            print(f"✅ Atributo data-id encontrado: {data_id_match.group(1)}")
        else:
            print("❌ No se encontró el atributo data-id")
            
        data_nombre_match = re.search(r'data-nombre="(.*?)"', example_button)
        if data_nombre_match:
            print(f"✅ Atributo data-nombre encontrado: {data_nombre_match.group(1)}")
        else:
            print("❌ No se encontró el atributo data-nombre")
    else:
        print("❌ No se encontraron botones de eliminación")
    
    # Verificar logs
    print("\n=== ANÁLISIS DE LOGS DE DEPURACIÓN ===")
    console_logs = re.findall(r'console\.log\((.*?)\);', content)
    delete_logs = [log for log in console_logs if 'elimin' in log.lower() or 'delet' in log.lower() or 'modal' in log.lower()]
    
    if delete_logs:
        print(f"✅ Se encontraron {len(delete_logs)} logs relacionados con la eliminación")
    else:
        print("❌ No se encontraron logs relacionados con la eliminación")
    
    print("\n=== RECOMENDACIONES ===")
    print("1. Verificar que los botones de eliminar tengan correctamente establecidos los atributos data-id y data-nombre")
    print("2. Verificar que el ID del producto se está obteniendo y estableciendo correctamente en el campo oculto")
    print("3. Verificar que el formulario tiene el método y la acción correctos")
    print("4. Comprobar en el navegador que los logs de depuración aparecen en la consola")
    print("5. Probar la eliminación de un producto y verificar los logs en la consola")
    print("6. Probar la página de diagnóstico en /dashboard/productos-venta/diagnostico/")

# Ejecuta la función principal
if __name__ == "__main__":
    verificar_funcionamiento_boton_eliminar()
