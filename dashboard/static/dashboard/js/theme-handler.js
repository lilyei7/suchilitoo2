// theme-handler.js - Script para aplicar el tema del sistema dinámicamente

document.addEventListener('DOMContentLoaded', function() {
    // Cargar el tema actual del sistema
    cargarTemaActual();
});

// Función para cargar el tema actual desde el servidor
function cargarTemaActual() {
    // Solo cargamos el tema si no estamos en la página de configuración de temas
    // para evitar conflictos con la previsualización
    if (!window.location.pathname.includes('/configuracion/temas/')) {
        fetch('/dashboard/api/configuracion/temas/actual/')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.tema) {
                    aplicarTema(data.tema);
                }
            })
            .catch(error => {
                console.error('Error al obtener tema actual:', error);
            });
    }
}

// Función para aplicar un tema
function aplicarTema(tema) {
    // Crear o actualizar la hoja de estilo personalizada
    let styleElement = document.getElementById('custom-theme-style');
    if (!styleElement) {
        styleElement = document.createElement('style');
        styleElement.id = 'custom-theme-style';
        document.head.appendChild(styleElement);
    }
    
    // Crear las reglas CSS
    const cssRules = `
        /* Sidebar */
        #sidebar-wrapper {
            background-color: ${tema.sidebar_bg} !important;
        }
        
        .sidebar-item, .sidebar-subitem {
            color: ${tema.sidebar_text} !important;
        }
        
        /* Navbar */
        .navbar {
            background-color: ${tema.navbar_bg} !important;
            color: ${tema.navbar_text} !important;
        }
        
        .navbar .nav-link {
            color: ${tema.navbar_text} !important;
        }
        
        /* Primary Color */
        .btn-primary {
            background-color: ${tema.primary_color} !important;
            border-color: ${tema.primary_color} !important;
        }
        
        .btn-outline-primary {
            color: ${tema.primary_color} !important;
            border-color: ${tema.primary_color} !important;
        }
        
        .btn-outline-primary:hover {
            background-color: ${tema.primary_color} !important;
            color: #fff !important;
        }
        
        /* Secondary Color */
        .btn-secondary {
            background-color: ${tema.secondary_color} !important;
            border-color: ${tema.secondary_color} !important;
        }
        
        /* Accent Color */
        .accent-color {
            color: ${tema.accent_color} !important;
        }
        
        .bg-accent {
            background-color: ${tema.accent_color} !important;
        }
        
        /* Links */
        a {
            color: ${tema.primary_color};
        }
        
        a:hover {
            color: ${adjustColor(tema.primary_color, -20)};
        }
        
        /* Active items */
        .sidebar-item.active, .sidebar-subitem.active {
            background-color: ${adjustColor(tema.primary_color, 0, 0.8)} !important;
            color: white !important;
        }
        
        /* Card headers */
        .card-header {
            border-bottom-color: ${adjustColor(tema.primary_color, 0, 0.2)} !important;
        }
        
        /* Progress bars */
        .progress-bar {
            background-color: ${tema.primary_color} !important;
        }
    `;
    
    styleElement.innerHTML = cssRules;
}

// Función para ajustar un color (más claro o más oscuro)
function adjustColor(hex, amount = 0, opacity = 1) {
    if (amount === 0 && opacity === 1) return hex;
    
    // Si incluye el símbolo #, quitarlo
    if (hex.startsWith('#')) {
        hex = hex.slice(1);
    }
    
    // Convertir a RGB
    let r = parseInt(hex.slice(0, 2), 16);
    let g = parseInt(hex.slice(2, 4), 16);
    let b = parseInt(hex.slice(4, 6), 16);
    
    // Ajustar luminosidad
    r = Math.max(0, Math.min(255, r + amount));
    g = Math.max(0, Math.min(255, g + amount));
    b = Math.max(0, Math.min(255, b + amount));
    
    // Aplicar opacidad si es distinta de 1
    if (opacity !== 1) {
        return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    }
    
    // Convertir de vuelta a hexadecimal
    const rHex = r.toString(16).padStart(2, '0');
    const gHex = g.toString(16).padStart(2, '0');
    const bHex = b.toString(16).padStart(2, '0');
    
    return `#${rHex}${gHex}${bHex}`;
}
