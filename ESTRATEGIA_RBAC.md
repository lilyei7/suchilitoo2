# ESTRATEGIA DE CONTROL DE ACCESO BASADO EN ROLES (RBAC)

## Objetivo
Implementar un sistema de control de acceso robusto, escalable y fácil de mantener que permita gestionar permisos granulares por rol en todo el sistema de gestión del restaurante.

## Arquitectura del Sistema de Permisos

### 1. Estructura de Permisos
Cada rol tiene un campo `permisos` (JSONField) con la siguiente estructura:

```json
{
    "modules": {
        "dashboard": true,
        "inventario": true,
        "usuarios": false,
        "ventas": true,
        "recetas": false,
        "reportes": false,
        "proveedores": false,
        "configuracion": false
    },
    "actions": {
        "create": ["inventario", "ventas"],
        "read": ["inventario", "ventas", "dashboard"],
        "update": ["inventario"],
        "delete": []
    },
    "features": {
        "ver_precios": true,
        "ver_costos": false,
        "ver_reportes_completos": false,
        "gestionar_usuarios": false,
        "cambiar_configuracion": false
    }
}
```

### 2. Definición de Roles y Permisos por Defecto

#### 🔴 ADMIN - Acceso Completo
```json
{
    "modules": {"dashboard": true, "inventario": true, "usuarios": true, "ventas": true, "recetas": true, "reportes": true, "proveedores": true, "configuracion": true},
    "actions": {"create": ["*"], "read": ["*"], "update": ["*"], "delete": ["*"]},
    "features": {"ver_precios": true, "ver_costos": true, "ver_reportes_completos": true, "gestionar_usuarios": true, "cambiar_configuracion": true}
}
```

#### 🟣 GERENTE - Gestión Operativa
```json
{
    "modules": {"dashboard": true, "inventario": true, "usuarios": true, "ventas": true, "recetas": true, "reportes": true, "proveedores": true, "configuracion": false},
    "actions": {"create": ["inventario", "ventas", "recetas", "proveedores"], "read": ["*"], "update": ["inventario", "ventas", "recetas", "usuarios", "proveedores"], "delete": ["inventario", "ventas"]},
    "features": {"ver_precios": true, "ver_costos": true, "ver_reportes_completos": true, "gestionar_usuarios": false, "cambiar_configuracion": false}
}
```

#### 🟢 SUPERVISOR - Supervisión Operativa
```json
{
    "modules": {"dashboard": true, "inventario": true, "usuarios": false, "ventas": true, "recetas": true, "reportes": false, "proveedores": false, "configuracion": false},
    "actions": {"create": ["inventario", "ventas"], "read": ["dashboard", "inventario", "ventas", "recetas"], "update": ["inventario"], "delete": []},
    "features": {"ver_precios": true, "ver_costos": false, "ver_reportes_completos": false, "gestionar_usuarios": false, "cambiar_configuracion": false}
}
```

#### 🟠 CAJERO - Ventas y Caja
```json
{
    "modules": {"dashboard": true, "inventario": false, "usuarios": false, "ventas": true, "recetas": false, "reportes": false, "proveedores": false, "configuracion": false},
    "actions": {"create": ["ventas"], "read": ["dashboard", "ventas"], "update": ["ventas"], "delete": []},
    "features": {"ver_precios": true, "ver_costos": false, "ver_reportes_completos": false, "gestionar_usuarios": false, "cambiar_configuracion": false}
}
```

#### 🔴 COCINERO - Recetas y Producción
```json
{
    "modules": {"dashboard": true, "inventario": true, "usuarios": false, "ventas": false, "recetas": true, "reportes": false, "proveedores": false, "configuracion": false},
    "actions": {"create": ["recetas"], "read": ["dashboard", "inventario", "recetas"], "update": ["recetas"], "delete": []},
    "features": {"ver_precios": false, "ver_costos": true, "ver_reportes_completos": false, "gestionar_usuarios": false, "cambiar_configuracion": false}
}
```

#### 🔵 MESERO - Atención al Cliente
```json
{
    "modules": {"dashboard": true, "inventario": false, "usuarios": false, "ventas": true, "recetas": true, "reportes": false, "proveedores": false, "configuracion": false},
    "actions": {"create": ["ventas"], "read": ["dashboard", "ventas", "recetas"], "update": [], "delete": []},
    "features": {"ver_precios": true, "ver_costos": false, "ver_reportes_completos": false, "gestionar_usuarios": false, "cambiar_configuracion": false}
}
```

#### 🟡 INVENTARIO - Gestión de Stock
```json
{
    "modules": {"dashboard": true, "inventario": true, "usuarios": false, "ventas": false, "recetas": true, "reportes": false, "proveedores": true, "configuracion": false},
    "actions": {"create": ["inventario", "proveedores"], "read": ["dashboard", "inventario", "recetas", "proveedores"], "update": ["inventario", "proveedores"], "delete": ["inventario"]},
    "features": {"ver_precios": true, "ver_costos": true, "ver_reportes_completos": false, "gestionar_usuarios": false, "cambiar_configuracion": false}
}
```

#### 🟢 RRHH - Recursos Humanos
```json
{
    "modules": {"dashboard": true, "inventario": false, "usuarios": true, "ventas": false, "recetas": false, "reportes": true, "proveedores": false, "configuracion": false},
    "actions": {"create": ["usuarios"], "read": ["dashboard", "usuarios", "reportes"], "update": ["usuarios"], "delete": []},
    "features": {"ver_precios": false, "ver_costos": false, "ver_reportes_completos": false, "gestionar_usuarios": true, "cambiar_configuracion": false}
}
```

## Implementación Técnica

### 1. Utilidades de Permisos (permissions.py)
- Funciones centralizadas para verificar permisos
- Cache de permisos para optimizar rendimiento
- Validadores para diferentes tipos de acceso

### 2. Decoradores Avanzados
- `@require_permission(module, action)` - Para permisos específicos
- `@require_feature(feature_name)` - Para características especiales
- `@require_role(role_names)` - Para roles específicos
- `@require_module_access(module_name)` - Para acceso a módulos

### 3. Mixins para CBV (Class-Based Views)
- `PermissionRequiredMixin` - Para vistas basadas en clase
- `ModuleAccessMixin` - Para control de acceso por módulo
- `FeatureAccessMixin` - Para características específicas

### 4. Context Processors
- Inyectar permisos del usuario en todos los templates
- Disponibilizar funciones de verificación en plantillas

### 5. Frontend/Templates
- Helpers de plantilla para mostrar/ocultar elementos
- JavaScript para control dinámico de UI
- Componentes reutilizables para manejo de permisos

## Beneficios del Sistema

1. **Escalabilidad**: Fácil agregar nuevos módulos y permisos
2. **Mantenibilidad**: Lógica centralizada y reutilizable
3. **Granularidad**: Control fino sobre accesos y características
4. **Performance**: Sistema de cache para optimizar consultas
5. **Flexibilidad**: Permisos configurables por rol
6. **Auditoría**: Registro de accesos y cambios de permisos

## Fase de Implementación

### Fase 1: Infraestructura Base ✅
- [x] Modelos de Usuario y Rol existentes
- [x] Sistema básico de decoradores
- [x] Control de acceso en vistas críticas

### Fase 2: Sistema de Permisos Avanzado (ACTUAL)
- [ ] Crear utilidades de permisos centralizadas
- [ ] Implementar decoradores avanzados
- [ ] Crear mixins para CBV
- [ ] Actualizar permisos por defecto de roles

### Fase 3: Frontend y UX
- [ ] Context processors para templates
- [ ] Helpers de plantilla
- [ ] Control dinámico de UI con JavaScript
- [ ] Componentes reutilizables

### Fase 4: Optimización y Auditoría
- [ ] Sistema de cache para permisos
- [ ] Logging de accesos
- [ ] Interface de administración de permisos
- [ ] Tests unitarios y de integración

## Casos de Uso Ejemplo

### Caso 1: Cajero intentando acceder a inventario
```python
# En la vista de inventario
@require_module_access('inventario')
def inventario_view(request):
    # Si el usuario no tiene acceso al módulo inventario, se redirige
    pass
```

### Caso 2: Cocinero viendo precios vs costos
```html
<!-- En template de recetas -->
{% if user|has_feature:'ver_costos' %}
    <td>Costo: ${{ receta.costo_total }}</td>
{% endif %}

{% if user|has_feature:'ver_precios' %}
    <td>Precio: ${{ receta.precio_venta }}</td>
{% endif %}
```

### Caso 3: Gerente creando usuarios
```python
# En vista de crear usuario
@require_permission('usuarios', 'create')
def crear_usuario(request):
    # Solo si tiene permiso de crear en módulo usuarios
    pass
```

## Siguiente Paso
Implementar las utilidades centralizadas de permisos y actualizar el sistema de roles con los permisos por defecto definidos.
