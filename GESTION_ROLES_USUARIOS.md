# Gestión de Roles y Usuarios

Este documento describe cómo administrar roles y usuarios en el sistema de restaurante de sushi.

## Scripts Disponibles

Para garantizar que el sistema siempre tenga los roles necesarios, se proporcionan los siguientes scripts:

1. **verificar_roles_basicos.py** - Verifica que todos los roles básicos existan y estén activos.
   - Se recomienda ejecutar este script después de iniciar el sistema o restaurar la base de datos.
   - No elimina roles existentes, solo crea los que faltan o reactiva los inactivos.

2. **regenerar_roles.py** - Regenera completamente todos los roles del sistema.
   - ⚠️ **ADVERTENCIA**: Este script elimina todos los roles existentes.
   - Solo debe usarse cuando hay problemas graves con los roles.
   - Restaura automáticamente el rol 'admin' a los superusuarios.

## Roles Básicos del Sistema

El sistema incluye los siguientes roles predefinidos:

| Rol         | Descripción                                  |
|-------------|----------------------------------------------|
| admin       | Administrador del sistema con acceso completo|
| gerente     | Gerente con acceso a gestión y reportes      |
| supervisor  | Supervisor de operaciones                    |
| cajero      | Cajero para manejo de ventas                 |
| cocinero    | Cocinero para preparación de alimentos       |
| mesero      | Mesero para atención al cliente              |
| inventario  | Encargado de inventario                      |
| rrhh        | Recursos Humanos                             |

## Solución de Problemas

### No Aparecen Roles al Crear/Editar Usuarios

Si no se muestran roles al crear o editar usuarios, puede deberse a:

1. **No hay roles activos en el sistema**:
   - Ejecute `python verificar_roles_basicos.py` para crear los roles básicos.

2. **Problemas con la base de datos**:
   - Como último recurso, ejecute `python regenerar_roles.py` para regenerar todos los roles.

3. **Problemas de carga AJAX**:
   - Los roles ahora se cargan desde el HTML y como respaldo por AJAX.
   - Verifique la consola del navegador para errores de red o JavaScript.

## Buenas Prácticas

- Siempre mantenga al menos un usuario con rol de 'admin' activo.
- Utilice roles específicos para cada tipo de usuario según sus responsabilidades.
- Ejecute `verificar_roles_basicos.py` después de restaurar la base de datos.
- Haga una copia de seguridad antes de ejecutar `regenerar_roles.py`.
