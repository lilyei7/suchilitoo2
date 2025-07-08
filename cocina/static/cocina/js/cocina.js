// JavaScript específico para la aplicación de cocina

// Configuración global
const CocinaApp = {
    refreshInterval: 30000, // 30 segundos
    soundEnabled: true,
    notificationSound: null,
    
    init: function() {
        this.setupEventListeners();
        this.setupNotifications();
        this.startAutoRefresh();
        this.setupSounds();
    },
    
    setupEventListeners: function() {
        // Delegación de eventos para botones dinámicos
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('btn-cambiar-estado')) {
                CocinaApp.cambiarEstadoOrden(e.target.dataset.ordenId, e.target.dataset.estado);
            }
            
            if (e.target.classList.contains('btn-cambiar-estado-item')) {
                CocinaApp.cambiarEstadoItem(e.target.dataset.itemId, e.target.dataset.estado);
            }
        });
        
        // Filtros en tiempo real
        const filtros = document.querySelectorAll('.filtro-cocina');
        filtros.forEach(filtro => {
            filtro.addEventListener('change', CocinaApp.aplicarFiltros);
        });
        
        // Shortcuts de teclado
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                CocinaApp.refrescarOrdenes();
            }
            
            if (e.key === 'F5') {
                e.preventDefault();
                CocinaApp.refrescarOrdenes();
            }
        });
    },
    
    setupNotifications: function() {
        if ('Notification' in window) {
            if (Notification.permission !== 'granted' && Notification.permission !== 'denied') {
                Notification.requestPermission();
            }
        }
    },
    
    setupSounds: function() {
        // Crear elementos de audio para notificaciones
        this.notificationSound = new Audio('/static/cocina/sounds/notification.mp3');
        this.notificationSound.volume = 0.5;
    },
    
    startAutoRefresh: function() {
        setInterval(() => {
            if (document.hidden) return; // No refrescar si la pestaña no está activa
            
            this.refrescarOrdenes();
        }, this.refreshInterval);
    },
    
    refrescarOrdenes: function() {
        // Mostrar indicador de carga
        this.mostrarCargando();
        
        // Recargar la página o hacer petición AJAX
        if (typeof window.location !== 'undefined') {
            window.location.reload();
        }
    },
    
    mostrarCargando: function() {
        const loading = document.createElement('div');
        loading.className = 'loading-overlay';
        loading.innerHTML = '<div class="spinner-border text-primary" role="status"></div>';
        document.body.appendChild(loading);
        
        setTimeout(() => {
            if (loading.parentNode) {
                loading.parentNode.removeChild(loading);
            }
        }, 2000);
    },
    
    cambiarEstadoOrden: function(ordenId, nuevoEstado) {
        if (!confirm('¿Está seguro de cambiar el estado de esta orden?')) {
            return;
        }
        
        this.mostrarCargando();
        
        fetch(`/cocina/orden/${ordenId}/cambiar-estado/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCookie('csrftoken')
            },
            body: JSON.stringify({
                'estado': nuevoEstado
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.mostrarNotificacion('Estado cambiado exitosamente', 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                this.mostrarNotificacion('Error al cambiar el estado: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.mostrarNotificacion('Error al cambiar el estado', 'error');
        });
    },
    
    cambiarEstadoItem: function(itemId, nuevoEstado) {
        if (!confirm('¿Está seguro de cambiar el estado de este item?')) {
            return;
        }
        
        this.mostrarCargando();
        
        const ordenId = window.location.pathname.split('/')[2]; // Obtener orden ID de la URL
        
        fetch(`/cocina/orden/${ordenId}/item/${itemId}/cambiar-estado/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCookie('csrftoken')
            },
            body: JSON.stringify({
                'estado': nuevoEstado
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.mostrarNotificacion('Estado del item cambiado exitosamente', 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                this.mostrarNotificacion('Error al cambiar el estado: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.mostrarNotificacion('Error al cambiar el estado', 'error');
        });
    },
    
    aplicarFiltros: function() {
        const filtros = {
            estado: document.getElementById('filter-estado')?.value || '',
            mesa: document.getElementById('filter-mesa')?.value || '',
            prioridad: document.getElementById('filter-prioridad')?.value || '',
            cocinero: document.getElementById('filter-cocinero')?.value || ''
        };
        
        const cards = document.querySelectorAll('.orden-card');
        
        cards.forEach(card => {
            let mostrar = true;
            
            // Filtro por estado
            if (filtros.estado && card.dataset.estado !== filtros.estado) {
                mostrar = false;
            }
            
            // Filtro por mesa
            if (filtros.mesa && card.dataset.mesa !== filtros.mesa) {
                mostrar = false;
            }
            
            // Filtro por prioridad
            if (filtros.prioridad && card.dataset.prioridad !== filtros.prioridad) {
                mostrar = false;
            }
            
            // Filtro por cocinero
            if (filtros.cocinero && card.dataset.cocinero !== filtros.cocinero) {
                mostrar = false;
            }
            
            card.style.display = mostrar ? 'block' : 'none';
        });
        
        // Actualizar contador de resultados
        const visibles = document.querySelectorAll('.orden-card[style="display: block"], .orden-card:not([style])').length;
        CocinaApp.actualizarContador(visibles);
    },
    
    actualizarContador: function(cantidad) {
        const contador = document.getElementById('contador-resultados');
        if (contador) {
            contador.textContent = `${cantidad} orden${cantidad !== 1 ? 'es' : ''}`;
        }
    },
    
    mostrarNotificacion: function(mensaje, tipo = 'info') {
        // Crear notificación en pantalla
        const notificacion = document.createElement('div');
        notificacion.className = `alert alert-${tipo === 'error' ? 'danger' : tipo} alert-dismissible fade show notification`;
        notificacion.innerHTML = `
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notificacion);
        
        // Remover después de 5 segundos
        setTimeout(() => {
            if (notificacion.parentNode) {
                notificacion.remove();
            }
        }, 5000);
        
        // Notificación del navegador
        if (Notification.permission === 'granted') {
            new Notification('Cocina - ' + mensaje, {
                icon: '/static/cocina/img/icon.png',
                badge: '/static/cocina/img/badge.png'
            });
        }
        
        // Reproducir sonido
        if (this.soundEnabled && this.notificationSound) {
            this.notificationSound.play().catch(e => {
                console.log('No se pudo reproducir el sonido:', e);
            });
        }
    },
    
    getCookie: function(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },
    
    formatearTiempo: function(segundos) {
        const horas = Math.floor(segundos / 3600);
        const minutos = Math.floor((segundos % 3600) / 60);
        const segs = segundos % 60;
        
        if (horas > 0) {
            return `${horas}:${minutos.toString().padStart(2, '0')}:${segs.toString().padStart(2, '0')}`;
        } else {
            return `${minutos}:${segs.toString().padStart(2, '0')}`;
        }
    },
    
    iniciarCronometro: function() {
        if (this.cronometroInterval) {
            clearInterval(this.cronometroInterval);
        }
        
        this.tiempoCronometro = 0;
        this.cronometroInterval = setInterval(() => {
            this.tiempoCronometro++;
            const display = document.getElementById('cronometro');
            if (display) {
                display.textContent = this.formatearTiempo(this.tiempoCronometro);
            }
        }, 1000);
    },
    
    detenerCronometro: function() {
        if (this.cronometroInterval) {
            clearInterval(this.cronometroInterval);
            this.cronometroInterval = null;
        }
    },
    
    reiniciarCronometro: function() {
        this.detenerCronometro();
        this.tiempoCronometro = 0;
        const display = document.getElementById('cronometro');
        if (display) {
            display.textContent = '00:00';
        }
    }
};

// Funciones globales para compatibilidad con templates
function cambiarEstadoOrden(ordenId, estado) {
    CocinaApp.cambiarEstadoOrden(ordenId, estado);
}

function cambiarEstadoItem(itemId, estado) {
    CocinaApp.cambiarEstadoItem(itemId, estado);
}

function refrescarOrdenes() {
    CocinaApp.refrescarOrdenes();
}

function iniciarCronometro() {
    CocinaApp.iniciarCronometro();
}

function detenerCronometro() {
    CocinaApp.detenerCronometro();
}

function reiniciarCronometro() {
    CocinaApp.reiniciarCronometro();
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    CocinaApp.init();
});

// Manejar visibilidad de la pestaña
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        // La pestaña volvió a estar visible, refrescar datos
        CocinaApp.refrescarOrdenes();
    }
});

// Detectar nuevas órdenes (simulación)
function detectarNuevasOrdenes() {
    // Esta función sería llamada por WebSocket o polling
    CocinaApp.mostrarNotificacion('Nueva orden recibida', 'info');
}

// Utilidades adicionales
const Utils = {
    formatearFecha: function(fecha) {
        return new Date(fecha).toLocaleString('es-ES', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    calcularTiempoTranscurrido: function(fechaInicio) {
        const ahora = new Date();
        const inicio = new Date(fechaInicio);
        const diff = Math.floor((ahora - inicio) / 1000);
        
        if (diff < 60) {
            return `${diff} segundos`;
        } else if (diff < 3600) {
            return `${Math.floor(diff / 60)} minutos`;
        } else {
            return `${Math.floor(diff / 3600)} horas`;
        }
    },
    
    generarColorEstado: function(estado) {
        const colores = {
            'pendiente': '#ffc107',
            'en_preparacion': '#17a2b8',
            'lista': '#28a745',
            'entregada': '#007bff',
            'cancelada': '#dc3545'
        };
        return colores[estado] || '#6c757d';
    }
};

// Exportar para uso global
window.CocinaApp = CocinaApp;
window.Utils = Utils;
