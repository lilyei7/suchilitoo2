/**
 * Logo Handler - Script para manejar la carga dinámica del logo personalizado
 */

document.addEventListener('DOMContentLoaded', function() {
    // Cargar el logo actual
    cargarLogoActual();
});

/**
 * Función para cargar el logo actual desde la API
 */
function cargarLogoActual() {
    fetch('/dashboard/api/configuracion/logo/actual/')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.logo) {
                aplicarLogo(data.logo);
            }
        })
        .catch(error => {
            console.error('Error al obtener logo actual:', error);
        });
}

/**
 * Función para aplicar el logo en toda la aplicación
 */
function aplicarLogo(logoData) {
    if (logoData && logoData.logo_path) {
        const logoPath = logoData.logo_path;
        
        // Actualizar logo en la barra lateral
        const sidebarLogo = document.querySelector('.sidebar-logo');
        if (sidebarLogo) {
            sidebarLogo.src = `/static/${logoPath}`;
        }
        
        // Actualizar logo en la barra de navegación
        const navbarLogo = document.querySelector('.navbar-logo');
        if (navbarLogo) {
            navbarLogo.src = `/static/${logoPath}`;
        }
        
        // Actualizar favicon si es necesario
        const favicon = document.querySelector('link[rel="icon"]');
        if (favicon && logoData.usar_logo_personalizado) {
            favicon.href = `/static/${logoPath}`;
        }
    }
}
