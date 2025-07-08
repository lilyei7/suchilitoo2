import os
import re

def corregir_formulario_eliminacion():
    """
    Corrige los problemas detectados en el formulario de eliminación
    """
    # Define la ruta del archivo
    file_path = r'c:\Users\olcha\Desktop\sushi_restaurant - Copy (2)\suchilitoo2\dashboard\templates\dashboard\productos_venta\lista.html'
    
    # Lee el contenido del archivo
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Crear copia de seguridad
    backup_path = file_path + '.form_backup'
    with open(backup_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Copia de seguridad creada en: {backup_path}")
    
    # 1. Verificar y corregir el campo oculto para el ID del producto
    form_match = re.search(r'<form id="deleteForm".*?</form>', content, re.DOTALL)
    if form_match:
        form_content = form_match.group(0)
        input_match = re.search(r'<input type="hidden" name="producto_id".*?>', form_content)
        
        if not input_match:
            print("Añadiendo campo oculto para el ID del producto...")
            # Buscar el token CSRF
            csrf_match = re.search(r'{% csrf_token %}', form_content)
            if csrf_match:
                # Añadir después del token CSRF
                new_form_content = form_content.replace(
                    '{% csrf_token %}',
                    '{% csrf_token %}\n                    <input type="hidden" name="producto_id" id="producto_id_input" value="">'
                )
                content = content.replace(form_content, new_form_content)
                print("✅ Campo oculto para el ID del producto añadido")
            else:
                print("❌ No se encontró el token CSRF en el formulario")
    else:
        print("❌ No se encontró el formulario de eliminación")
    
    # 2. Corregir cómo se establece el ID en el campo oculto
    modal_event_match = re.search(r'deleteModal\.addEventListener\(\'show\.bs\.modal\', function \(event\).*?\}\);', content, re.DOTALL)
    if modal_event_match:
        modal_event = modal_event_match.group(0)
        id_set_match = re.search(r'document\.getElementById\(\'producto_id_input\'\)\.value = .*?;', modal_event)
        
        if not id_set_match and 'const productoId = button.getAttribute' in modal_event:
            print("Añadiendo código para establecer el ID en el campo oculto...")
            # Buscar dónde añadir el código
            after_product_id = re.search(r'const productoId = button\.getAttribute\(\'data-id\'\);.*?\n', modal_event, re.DOTALL)
            if after_product_id:
                # Añadir después de la definición de productoId
                new_modal_event = modal_event.replace(
                    after_product_id.group(0),
                    after_product_id.group(0) + '\n                document.getElementById(\'producto_id_input\').value = productoId;\n'
                )
                content = content.replace(modal_event, new_modal_event)
                print("✅ Código para establecer el ID en el campo oculto añadido")
            else:
                print("❌ No se encontró dónde añadir el código para establecer el ID")
        else:
            print("✅ Ya existe código para establecer el ID en el campo oculto")
    else:
        print("❌ No se encontró el evento de apertura del modal")
    
    # 3. Corregir la acción del formulario
    if form_match:
        form_content = re.search(r'<form id="deleteForm".*?</form>', content, re.DOTALL).group(0)
        action_match = re.search(r'action="(.*?)"', form_content)
        
        if not action_match:
            print("Añadiendo acción al formulario...")
            # Añadir acción al formulario
            new_form_content = form_content.replace(
                '<form id="deleteForm" method="post"',
                '<form id="deleteForm" method="post" action="/dashboard/productos-venta/0/eliminar/"'
            )
            content = content.replace(form_content, new_form_content)
            print("✅ Acción añadida al formulario")
        else:
            print(f"✅ El formulario ya tiene una acción: {action_match.group(1)}")
    
    # 4. Añadir código para actualizar dinámicamente la acción del formulario
    if 'const actionUrl = "{% url' not in content:
        print("Añadiendo código para actualizar dinámicamente la acción del formulario...")
        # Buscar dónde añadir el código
        after_product_id_input = re.search(r'document\.getElementById\(\'producto_id_input\'\)\.value = productoId;.*?\n', content, re.DOTALL)
        if after_product_id_input:
            # Añadir después de establecer el valor del input
            new_content = content.replace(
                after_product_id_input.group(0),
                after_product_id_input.group(0) + '\n                const actionUrl = "{% url \'dashboard:eliminar_producto_venta\' 0 %}"'
                + '.replace(\'0\', productoId);\n'
                + '                document.getElementById(\'deleteForm\').action = actionUrl;\n'
            )
            content = new_content
            print("✅ Código para actualizar dinámicamente la acción del formulario añadido")
        else:
            print("❌ No se encontró dónde añadir el código para actualizar la acción")
    else:
        print("✅ Ya existe código para actualizar dinámicamente la acción del formulario")
    
    # 5. Añadir logs adicionales para depuración
    if 'console.log(`🔑 [FORM] ID del producto a eliminar' not in content:
        print("Añadiendo logs adicionales para depuración...")
        # Buscar dónde añadir los logs
        after_action_update = re.search(r'document\.getElementById\(\'deleteForm\'\)\.action = actionUrl;.*?\n', content, re.DOTALL)
        if after_action_update:
            # Añadir después de actualizar la acción del formulario
            new_content = content.replace(
                after_action_update.group(0),
                after_action_update.group(0) + '\n                console.log(`🔗 [FORM] Acción del formulario actualizada a: ${actionUrl}`);\n'
                + '                console.log(`🔑 [FORM] ID del producto a eliminar: ${productoId}`);\n'
            )
            content = new_content
            print("✅ Logs adicionales para depuración añadidos")
        else:
            print("❌ No se encontró dónde añadir los logs adicionales")
    else:
        print("✅ Ya existen logs adicionales para depuración")
    
    # Guardar los cambios
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"✅ Archivo actualizado: {file_path}")
    
    print("\n=== RESUMEN DE CORRECCIONES ===")
    print("1. Se ha añadido/verificado el campo oculto para el ID del producto")
    print("2. Se ha añadido/verificado el código para establecer el ID en el campo oculto")
    print("3. Se ha añadido/verificado la acción del formulario")
    print("4. Se ha añadido/verificado el código para actualizar dinámicamente la acción del formulario")
    print("5. Se han añadido/verificado logs adicionales para depuración")
    print("\nPrueba ahora la eliminación de productos y verifica que todo funciona correctamente.")

# Ejecuta la función principal
if __name__ == "__main__":
    corregir_formulario_eliminacion()
