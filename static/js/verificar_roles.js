// Script para verificar si los roles se cargan correctamente
// Ejecutar esto en la consola del navegador desde la página de usuarios

function verificarRoles() {
    console.log("Verificando carga de roles...");
    
    // Obtener los selectores de roles
    const selectRolCrear = document.getElementById('rol');
    const selectRolEditar = document.getElementById('editar_rol');
    
    console.log("Select de roles (crear):", selectRolCrear);
    console.log("Select de roles (editar):", selectRolEditar);
    
    if (selectRolCrear) {
        console.log("Opciones en select de crear:", selectRolCrear.options.length);
        for (let i = 0; i < selectRolCrear.options.length; i++) {
            console.log(`  - Opción ${i}: value="${selectRolCrear.options[i].value}", text="${selectRolCrear.options[i].text}"`);
        }
    }
    
    if (selectRolEditar) {
        console.log("Opciones en select de editar:", selectRolEditar.options.length);
        for (let i = 0; i < selectRolEditar.options.length; i++) {
            console.log(`  - Opción ${i}: value="${selectRolEditar.options[i].value}", text="${selectRolEditar.options[i].text}"`);
        }
    }
    
    // Hacer una llamada directa a la API
    console.log("Haciendo llamada directa a la API...");
    fetch('/dashboard/api/sucursales-roles/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Respuesta de la API:", data);
        if (data.success) {
            console.log("Roles devueltos por la API:", data.roles.length);
            data.roles.forEach(rol => {
                console.log(`  - Rol: id=${rol.id}, nombre="${rol.nombre}"`);
            });
        }
    })
    .catch(error => {
        console.error("Error en la llamada a la API:", error);
    });
}

// Ejecutar la verificación
verificarRoles();
