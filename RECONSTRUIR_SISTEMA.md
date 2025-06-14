# Instrucciones para reconstruir el sistema después de borrar la base de datos

Si has borrado la base de datos (`db.sqlite3`) o necesitas reconstruir el sistema desde cero, sigue estas instrucciones para que todo vuelva a funcionar correctamente.

## Opciones disponibles

Tienes dos opciones principales dependiendo de tu situación:

### Opción 1: Reconstrucción completa (base de datos borrada)

Utiliza esta opción si has borrado completamente el archivo `db.sqlite3` o si estás configurando el sistema por primera vez:

```bash
python inicializar_sistema.py
```

Este script realizará los siguientes pasos:
1. Ejecutará las migraciones necesarias para crear la estructura de la base de datos
2. Creará un superusuario administrador
3. Creará los roles básicos del sistema
4. Creará sucursales de ejemplo
5. Creará usuarios de ejemplo con diferentes roles
6. Verificará que todo esté funcionando correctamente

### Opción 2: Recrear solo los datos básicos

Utiliza esta opción si la estructura de la base de datos sigue intacta pero has perdido los datos (por ejemplo, si has ejecutado `python manage.py flush`):

```bash
python recrear_datos_basicos.py
```

Este script solo creará:
1. Un superusuario administrador
2. Roles básicos
3. Una sucursal principal

## Credenciales de acceso por defecto

Después de ejecutar cualquiera de los scripts, podrás acceder al sistema con las siguientes credenciales:

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| admin   | admin123456 | Superusuario |
| gerente | gerente123 | Gerente |
| supervisor | supervisor123 | Supervisor |
| cajero | cajero123 | Cajero |
| cocinero | cocinero123 | Cocinero |
| mesero | mesero123 | Mesero |

## Problemas comunes y soluciones

### 1. Error "No such table"

Si ves errores como "no such table", significa que la estructura de la base de datos no se ha creado correctamente. Ejecuta:

```bash
python manage.py makemigrations
python manage.py migrate
```

Y luego vuelve a ejecutar `python inicializar_sistema.py`.

### 2. Error "User already exists"

Si ves errores indicando que un usuario ya existe, puedes borrar solo ese usuario desde la consola de Django:

```bash
python manage.py shell
```

```python
from accounts.models import Usuario
Usuario.objects.filter(username='admin').delete()
exit()
```

### 3. Los roles no aparecen en el formulario de crear usuario

Si después de reconstruir la base de datos, los roles no aparecen en el formulario de crear usuario, asegúrate de que:

1. Los roles se han creado correctamente (verifica en el panel de administración)
2. Los roles tienen el campo `activo` establecido a `True`

Puedes verificar y activar todos los roles con el siguiente comando:

```bash
python verificar_roles.py
```

## Reconstruir categorías y otros datos específicos

Si necesitas reconstruir datos específicos como categorías, unidades de medida, etc., puedes usar los scripts específicos:

```bash
python crear_categorias.py
python crear_datos_basicos.py
```

## Nota importante

Después de reconstruir la base de datos, es recomendable reiniciar el servidor Django para asegurarte de que todos los cambios surtan efecto.
