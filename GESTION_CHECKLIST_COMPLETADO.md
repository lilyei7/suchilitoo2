# IMPLEMENTACIÓN DE GESTIÓN DE CHECKLIST

## Descripción
Este documento describe las nuevas funcionalidades implementadas para la gestión de tareas y categorías del sistema de checklist, incluyendo la capacidad de crear, editar y eliminar tareas y categorías, así como un historial detallado para revisar y aprobar las tareas completadas.

## Funcionalidades Implementadas

### 1. Gestión de Categorías
- **Ver todas las categorías**: Lista todas las categorías de checklist con su nombre, estado y número de tareas.
- **Crear categoría**: Formulario para agregar nuevas categorías con nombre y orden.
- **Editar categoría**: Formulario para modificar el nombre, orden y estado de activación de una categoría.
- **Eliminar categoría**: Opción para eliminar categorías que no tengan tareas asociadas.

### 2. Gestión de Tareas
- **Ver todas las tareas**: Lista todas las tareas con filtros por categoría y estado.
- **Crear tarea**: Formulario para agregar nuevas tareas con título, descripción, categoría, requisito de evidencia y rol predeterminado.
- **Editar tarea**: Formulario para modificar todos los atributos de una tarea.
- **Eliminar tarea**: Opción para eliminar tareas que no tengan instancias asociadas.

### 3. Historial de Tareas
- **Ver historial**: Lista de todas las instancias de tareas filtradas por sucursal, categoría, estado y rango de fechas.
- **Detalles de instancia**: Vista detallada de una instancia específica mostrando información de la tarea, evidencias y opciones de verificación.
- **Aprobar tareas**: Posibilidad de aprobar una tarea completada, notificando al usuario que la realizó.
- **Rechazar tareas**: Posibilidad de rechazar una tarea y devolverla a estado pendiente, notificando a los usuarios responsables.
- **Sistema de verificación**: Registro de quién verificó cada tarea, cuándo y cualquier comentario de verificación.

## Rutas Implementadas

### Categorías
- `/dashboard/checklist/categorias/` - Vista de todas las categorías
- `/dashboard/checklist/categoria/crear/` - Crear nueva categoría
- `/dashboard/checklist/categoria/<id>/editar/` - Editar categoría existente
- `/dashboard/checklist/categoria/<id>/eliminar/` - Eliminar categoría

### Tareas
- `/dashboard/checklist/tareas/` - Vista de todas las tareas
- `/dashboard/checklist/tarea/crear/` - Crear nueva tarea
- `/dashboard/checklist/tarea/<id>/editar/` - Editar tarea existente
- `/dashboard/checklist/tarea/<id>/eliminar/` - Eliminar tarea

### Historial
- `/dashboard/checklist/historial/` - Historial de instancias de tareas
- `/dashboard/checklist/historial/tarea/<id>/` - Detalles de una instancia específica
- `/dashboard/checklist/historial/tarea/<id>/verificar/` - Aprobar o rechazar tarea

## Control de Acceso
- **Gestión de categorías y tareas**: Solo usuarios con roles de 'admin' o 'gerente'.
- **Historial y verificación de tareas**: Usuarios con roles de 'admin', 'gerente' o 'supervisor'.
- **Ver checklist y completar tareas**: Todos los usuarios autenticados según sus asignaciones.

## Notificaciones
El sistema envía notificaciones en los siguientes casos:
- Cuando se aprueba una tarea completada
- Cuando se rechaza una tarea y se devuelve a estado pendiente
- Cuando se completa una tarea (ya existente)
- Cuando se genera una tarea nueva (ya existente)

## Consideraciones Técnicas
- Las categorías y tareas tienen un atributo 'active' para desactivarlas sin eliminarlas.
- No se permite eliminar categorías con tareas asociadas.
- No se permite eliminar tareas con instancias asociadas.
- Las tareas rechazadas vuelven a estado pendiente y se notifica a los usuarios responsables.

## Mejoras Futuras Posibles
- Implementar un sistema de plantillas de checklist para facilitar la creación de conjuntos de tareas.
- Añadir estadísticas de cumplimiento por sucursal, usuario o categoría.
- Implementar un sistema de niveles de aprobación para tareas críticas.
- Añadir la posibilidad de adjuntar archivos específicos como evidencia (no solo imágenes).
