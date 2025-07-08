# 🍣 Sistema de Mesero - Sushi Restaurant

## 📋 Descripción

Sistema completo de gestión para meseros en un restaurante de sushi, desarrollado con Django. Incluye gestión de mesas, órdenes, menú y estado de cocina con un diseño ultra moderno y responsivo.

## ✨ Características Principales

### 🎯 Dashboard Principal
- Estadísticas en tiempo real del día
- Resumen de órdenes por estado
- Información de mesas (libres/ocupadas)
- Ventas del día
- Interfaz intuitiva y moderna

### 🪑 Gestión de Mesas
- Vista en tiempo real de todas las mesas
- Estado visual de ocupación
- Información de órdenes activas
- Acciones rápidas (nueva orden, ver detalles, entregar)
- Auto-actualización cada 30 segundos

### 📋 Sistema de Órdenes
- Creación de órdenes paso a paso
- Selección de productos por categorías
- Búsqueda de productos en tiempo real
- Gestión de cantidades y notas especiales
- Estados de orden: Pendiente → Preparando → Listo → Entregado
- Historial completo de órdenes

### 🍽️ Menú Digital
- Organización por categorías
- Búsqueda y filtros avanzados
- Información detallada de productos (precio, descripción, tiempo de preparación)
- Indicadores de disponibilidad
- Diseño visual atractivo

### 👨‍🍳 Estado de Cocina
- Vista en tiempo real de órdenes en preparación
- Órdenes listas para entregar
- Tiempos de preparación con alertas visuales
- Auto-actualización configurable (10 segundos)
- Acciones rápidas para cambiar estados

## 🚀 Instalación y Configuración

### 1. Requisitos Previos
- Python 3.8+
- Django 5.2+
- Base de datos SQLite (incluida)

### 2. Configuración Inicial

```bash
# Aplicar migraciones
python manage.py migrate

# Crear datos de prueba
python crear_datos_mesero.py

# Crear órdenes de ejemplo (opcional)
python crear_ordenes_prueba.py

# Iniciar servidor
python manage.py runserver
```

### 3. Credenciales de Prueba

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| mesero1 | mesero123 | Mesero |
| gerente1 | gerente123 | Gerente |
| admin | admin | Administrador |

## 🌐 URLs del Sistema

### URLs Principales
- **Login:** `http://127.0.0.1:8000/mesero/login/`
- **Dashboard:** `http://127.0.0.1:8000/mesero/`
- **Gestión de Mesas:** `http://127.0.0.1:8000/mesero/mesas/`
- **Menú:** `http://127.0.0.1:8000/mesero/menu/`
- **Estado de Cocina:** `http://127.0.0.1:8000/mesero/cocina/`

### URLs de Gestión
- **Mesa Detalle:** `http://127.0.0.1:8000/mesero/mesa/<id>/`
- **Nueva Orden:** `http://127.0.0.1:8000/mesero/mesa/<id>/nueva-orden/`
- **Detalle Orden:** `http://127.0.0.1:8000/mesero/orden/<id>/`
- **Editar Orden:** `http://127.0.0.1:8000/mesero/orden/<id>/editar/`

### APIs AJAX
- **Cambiar Estado:** `POST /mesero/api/orden/<id>/estado/`
- **Agregar Item:** `POST /mesero/api/orden/<id>/item/`
- **Ocupar Mesa:** `POST /mesero/api/mesa/<id>/ocupar/`

## 🎨 Diseño y UX

### Características del Diseño
- **Ultra Moderno:** Diseño clean y profesional
- **Responsivo:** Adaptable a móviles, tablets y desktop
- **Intuitivo:** Navegación sencilla y acciones claras
- **Tiempo Real:** Actualizaciones automáticas
- **Feedback Visual:** Animaciones y estados visuales claros

### Paleta de Colores
- **Primario:** #2563eb (Azul moderno)
- **Éxito:** #10b981 (Verde)
- **Advertencia:** #f59e0b (Amarillo)
- **Peligro:** #ef4444 (Rojo)
- **Info:** #06b6d4 (Cyan)

### Iconografía
- Font Awesome 6.0 para iconos consistentes
- Iconos semánticos para acciones rápidas
- Estados visuales claros

## 📱 Funcionalidades por Dispositivo

### 💻 Desktop
- Interfaz completa con todos los paneles
- Grid de mesas optimizado
- Sidebar de navegación completo
- Modales y acciones avanzadas

### 📱 Mobile/Tablet
- Navegación adaptiva
- Cards apiladas verticalmente
- Botones táctiles optimizados
- Menús colapsables

## 🔧 Estructura Técnica

### Modelos Principales
```python
Mesa:
- numero (único)
- capacidad
- sucursal
- activa
- esta_ocupada (property)

Orden:
- mesa (FK)
- mesero (FK)
- estado (choices)
- notas
- total
- created_at, updated_at

OrdenItem:
- orden (FK)
- producto (FK)
- cantidad
- precio_unitario
- notas
- subtotal (property)
```

### Vistas Principales
- `dashboard()` - Dashboard principal
- `mesas()` - Gestión de mesas
- `menu()` - Menú de productos
- `nueva_orden()` - Crear orden
- `estado_cocina()` - Estado de cocina
- APIs AJAX para acciones en tiempo real

### Templates
- `base.html` - Template base con navegación
- `dashboard.html` - Dashboard principal
- `mesas.html` - Gestión de mesas
- `menu.html` - Menú de productos
- `nueva_orden.html` - Formulario de orden
- `detalle_orden.html` - Detalles de orden
- `estado_cocina.html` - Estado de cocina
- `login.html` - Autenticación

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 5.2** - Framework principal
- **Python 3.8+** - Lenguaje de programación
- **SQLite** - Base de datos (desarrollo)

### Frontend
- **HTML5** - Estructura
- **CSS3** - Estilos (Grid, Flexbox, Animations)
- **JavaScript ES6** - Interactividad
- **Font Awesome 6** - Iconografía

### Características Técnicas
- **CSRF Protection** - Seguridad en formularios
- **Decorador personalizado** - Control de acceso por rol
- **Auto-actualización** - JavaScript intervals
- **API AJAX** - Acciones sin recarga
- **Responsive Design** - Media queries

## 📊 Datos de Prueba Incluidos

### Mesas (8 unidades)
- Mesa 1-8 con diferentes capacidades (2-8 personas)
- Asignadas a sucursal principal
- Todas activas

### Productos (24 unidades)
| Categoría | Productos | Precio Range |
|-----------|-----------|--------------|
| Sushi | 5 productos | $11.50 - $16.00 |
| Sashimi | 3 productos | $15.00 - $22.00 |
| Makis | 3 productos | $8.00 - $11.00 |
| Tempura | 3 productos | $12.00 - $16.00 |
| Sopas | 3 productos | $6.00 - $18.00 |
| Bebidas | 4 productos | $2.50 - $8.00 |
| Postres | 3 productos | $6.00 - $9.00 |

### Usuarios de Prueba
- **mesero1** - Usuario mesero básico
- **gerente1** - Usuario con permisos de gerente
- Roles y permisos configurados

## 🔄 Flujo de Trabajo

### 1. Login del Mesero
1. Acceder a `/mesero/login/`
2. Ingresar credenciales
3. Redirección automática al dashboard

### 2. Gestión de Mesas
1. Ver estado de todas las mesas
2. Identificar mesas libres/ocupadas
3. Crear nueva orden o ver detalles

### 3. Creación de Orden
1. Seleccionar mesa libre
2. Agregar productos del menú
3. Especificar cantidades y notas
4. Guardar borrador o enviar a cocina

### 4. Seguimiento en Cocina
1. Ver órdenes en preparación
2. Marcar órdenes como listas
3. Entregar órdenes a clientes

## 🚨 Alertas y Notificaciones

### Estados de Tiempo
- **Verde:** Tiempo normal (< 15 min)
- **Amarillo:** Alerta (15-30 min)
- **Rojo:** Crítico (> 30 min)

### Auto-actualización
- **Mesas:** Cada 30 segundos
- **Cocina:** Cada 10 segundos (configurable)
- **Dashboard:** Datos en tiempo real

## 🔒 Seguridad

### Autenticación
- Login requerido para todas las vistas
- Decorador `@mesero_required`
- Verificación de roles (mesero/gerente/admin)

### Autorización
- Control de acceso por sucursal
- Validación de permisos en APIs
- CSRF tokens en formularios

## 🎯 Próximas Mejoras

### Funcionalidades Pendientes
- [ ] Reportes de ventas detallados
- [ ] Integración con sistema de pagos
- [ ] Notificaciones push en tiempo real
- [ ] Aplicación móvil nativa
- [ ] Integración con impresoras de cocina
- [ ] Sistema de reservas
- [ ] Gestión de turnos de meseros
- [ ] Analytics y métricas avanzadas

### Optimizaciones Técnicas
- [ ] Caching con Redis
- [ ] WebSockets para actualizaciones en tiempo real
- [ ] API REST completa
- [ ] Tests automatizados
- [ ] Docker para deployment
- [ ] CI/CD pipeline

## 🆘 Solución de Problemas

### Errores Comunes

**Error de rutas:**
```bash
# Verificar configuración de URLs
python manage.py check
```

**Error de migraciones:**
```bash
python manage.py makemigrations mesero
python manage.py migrate
```

**Error de permisos:**
- Verificar que el usuario tenga rol asignado
- Verificar configuración en `mesero_required`

### Logs y Debug
- Activar `DEBUG = True` en desarrollo
- Revisar consola del navegador para errores JS
- Verificar logs del servidor Django

## 📞 Soporte

Para soporte técnico o reportar errores:
1. Verificar la documentación
2. Revisar logs del sistema
3. Contactar al equipo de desarrollo

---

## 🎉 ¡Sistema Listo!

El sistema de mesero está completamente funcional y listo para usar. Incluye todas las funcionalidades necesarias para la gestión eficiente de un restaurante de sushi con un diseño moderno y profesional.

**¡Disfruta del sistema! 🍣**
