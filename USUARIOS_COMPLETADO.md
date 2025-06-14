# IMPLEMENTACIÓN DE CRUD Y VISTA DETALLE PARA USUARIOS

## Descripción
Se ha implementado un sistema completo de CRUD (Crear, Leer, Actualizar, Eliminar) para la gestión de usuarios del sistema, incluyendo vistas detalladas y funcionalidad para activar/desactivar usuarios.

## Funcionalidad Implementada

### Backend (Python/Django)
- **Vistas separadas**: Se ha creado el archivo `dashboard/views/usuarios_views.py` que contiene todas las vistas relacionadas con usuarios.
- **Funciones implementadas**:
  - `usuarios_view`: Vista principal para la gestión de usuarios
  - `crear_usuario`: Crear un nuevo usuario con validación completa
  - `detalle_usuario`: Obtener detalles de un usuario específico
  - `editar_usuario`: Actualizar datos de un usuario existente
  - `eliminar_usuario`: Eliminar un usuario del sistema
  - `toggle_estado_usuario`: Activar o desactivar un usuario
  - `cambiar_contrasena_usuario`: Cambiar la contraseña de un usuario
  - `obtener_sucursales_roles`: API para obtener sucursales y roles para formularios

### Frontend (HTML/CSS/JavaScript)
- **Interfaz moderna**: Tarjetas de usuario con diseño moderno y responsive
- **Modales para acciones**:
  - Modal para crear usuario
  - Modal para editar usuario
  - Modal para ver detalles de usuario
  - Modal para cambiar contraseña
- **Funcionalidad AJAX**:
  - Carga dinámica de sucursales y roles
  - Operaciones CRUD asincrónicas
  - Notificaciones toast para feedback al usuario
- **Validación de formularios**:
  - Validación de campos requeridos
  - Validación de correo electrónico
  - Validación de contraseñas (coincidencia y longitud mínima)

### Características de Seguridad
- **Protección CSRF** en todos los formularios
- **Permisos basados en roles**: Solo administradores y gerentes pueden crear, editar y eliminar usuarios
- **Validación de datos**: Validación completa tanto en frontend como en backend
- **Contraseñas seguras**: Hasheo de contraseñas y validación de longitud mínima

### Modelo de Datos
- Modelo `Usuario` que extiende de `AbstractUser` de Django
- Campos adicionales:
  - `sucursal`: Relación con la sucursal asignada
  - `rol`: Relación con el rol asignado
  - `telefono`: Número de teléfono
  - `cedula`: Cédula o identificación personal
  - `fecha_ingreso`: Fecha de ingreso a la empresa
  - `salario`: Salario asignado
  - `activo`: Estado del usuario
  - `foto`: Foto de perfil

## Instrucciones de Uso

### Crear un Usuario
1. Hacer clic en el botón "Nuevo Usuario"
2. Completar el formulario con los datos requeridos
3. Hacer clic en "Crear Usuario"

### Ver Detalles de Usuario
1. En la tarjeta del usuario, hacer clic en "Ver perfil"
2. Se mostrará un modal con toda la información del usuario

### Editar un Usuario
1. En la tarjeta del usuario, hacer clic en "Editar"
2. Modificar los campos necesarios
3. Hacer clic en "Actualizar Usuario"

### Cambiar Contraseña
1. En el menú desplegable de la tarjeta del usuario, seleccionar "Cambiar contraseña"
2. Ingresar y confirmar la nueva contraseña
3. Hacer clic en "Guardar Contraseña"

### Eliminar un Usuario
1. En el menú desplegable de la tarjeta del usuario, seleccionar "Eliminar"
2. Confirmar la acción en el diálogo de confirmación

### Activar/Desactivar un Usuario
1. En el menú desplegable de la tarjeta del usuario, seleccionar "Activar" o "Desactivar"
2. Confirmar la acción en el diálogo de confirmación

## Consideraciones Técnicas
- La implementación utiliza AJAX para todas las operaciones para evitar recargas de página
- Se incluye manejo de errores robusto en todos los endpoints
- El sistema valida que no se puedan crear usuarios con nombres de usuario, emails o cédulas duplicadas
- Los usuarios no pueden eliminar o desactivar su propio usuario para evitar bloqueos
- Solo superusuarios pueden eliminar a otros superusuarios

## Mejoras Futuras Posibles
- Implementar sistema de permisos más granular
- Agregar registro de actividad para auditoría
- Implementar recuperación de contraseña
- Agregar carga de foto de perfil
- Implementar filtrado y búsqueda avanzada de usuarios
