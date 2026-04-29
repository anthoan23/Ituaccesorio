console.log("Cargando script de telefonos.js...");

const listaTelefonos = document.getElementById("lista-telefonos");

fetch('/api/telefonos')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(data.telefonos);

            if (!listaTelefonos) {
                return;
            }

            if (!Array.isArray(data.telefonos) || data.telefonos.length === 0) {
                listaTelefonos.innerHTML = '<li>No hay telefonos registrados.</li>';
                return;
            }

            listaTelefonos.innerHTML = data.telefonos
                .map(telefono => `<li><strong>${telefono.cod_telefono}</strong> - ${telefono.marca} ${telefono.modelo}</li>`)
                .join('');
        }
    })
    .catch(error => {
        console.error('Error cargando telefonos:', error);
    });