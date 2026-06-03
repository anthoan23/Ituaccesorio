document.addEventListener('DOMContentLoaded', function () {
	const tbody = document.getElementById("tabla-empleados");
	const btnActualizar = document.getElementById("btn-actualizar-empleados");
	const contador = document.querySelector('[data-count]');
    const ctx = document.getElementById('miGrafico1');
	const cts = document.getElementById('miGrafico2');

	async function fetchJson(url, options = {}) {
		const response = await fetch(url, options);
		if (!response.ok) throw new Error('Error en la petición');
		return await response.json();
	}

	function escapeHtml(value) {
		return String(value ?? "")
			.replaceAll("&", "&amp;")
			.replaceAll("<", "&lt;")
			.replaceAll(">", "&gt;")
			.replaceAll('"', "&quot;")
			.replaceAll("'", "&#039;");
	}

    if (ctx) {
        new Chart(ctx, {
            type: 'pie', // Cambiado a 'pie' para gráfico de pastel
            data: {
                labels: ['Soporte Técnico', 'Reparaciones', 'Ventas', 'Administración'], // Tus categorías
                datasets: [{
                    label: 'Distribución de Empleados',
                    data: [3, 2, 1, 1], // Cantidad por categoría (suma el total de 7)
                    backgroundColor: [
                        '#ffce54',  // Azul
                        '#f3c500',  // Rojo/Rosa
                        '#ffe36b',  // Amarillo
                        '#e67e00'   // Verde menta
                    ],
                    borderColor: [
                        '#ffce54',  // Azul
                        '#f3c500',  // Rojo/Rosa
                        '#ffe36b',  // Amarillo
                        '#e67e00'   // Verde menta
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom' // Coloca las etiquetas abajo para que no queden apretadas
                    }
                }
            }
        });
    }

	

    if (cts) {
        new Chart(cts, {
            type: 'pie', // Cambiado a 'pie' para gráfico de pastel
            data: {
                labels: ['Soporte Técnico', 'Reparaciones', 'Ventas', 'Administración'], // Tus categorías
                datasets: [{
                    label: 'Distribución de Empleados',
                    data: [3, 2, 1, 1], // Cantidad por categoría (suma el total de 7)
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.7)',  // Azul
                        'rgba(255, 99, 132, 0.7)',  // Rojo/Rosa
                        'rgba(255, 206, 86, 0.7)',  // Amarillo
                        'rgba(75, 192, 192, 0.7)'   // Verde menta
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom' // Coloca las etiquetas abajo para que no queden apretadas
                    }
                }
            }
        });
    }

	function normalizeEmpleado(empleado) {
		return {
			id: empleado?.id ?? empleado?.ID_empleado ?? "",
			cedula: empleado?.cedula ?? empleado?.Cedula ?? "",
			nombre: empleado?.nombre ?? empleado?.Nombre ?? "",
			apellido: empleado?.apellido ?? empleado?.Apellido ?? "",
			cargo: empleado?.cargo ?? empleado?.Cargo ?? "",
		};
	}

	function renderContador(total) {
		if (!contador) return;
		contador.setAttribute("data-count", String(total));
		contador.textContent = String(total);
	}

	function rendertabla(empleados) {
		if (!tbody) return;

		if (!empleados.length) {
			tbody.innerHTML = `
				<tr>
					<td colspan="5">No hay empleados para mostrar.</td>
				</tr>
			`;
			renderContador(0);
			return;
		}

		tbody.innerHTML = empleados
			.map((raw) => {
				const empleado = normalizeEmpleado(raw);
				const cedula = escapeHtml(empleado.cedula);
				const nombre = escapeHtml(empleado.nombre);
				const apellido = escapeHtml(empleado.apellido);
				const cargo = escapeHtml(empleado.cargo || "-");

				return `
					<tr>
						<td>${cedula}</td>
						<td>${nombre}</td>
						<td>${apellido}</td>
						<td>${cargo}</td>
						<td class="table__actions">
							<div class="row-actions" aria-label="Acciones del empleado">
								<button type="button" class="table-action table-action--accent" data-action="editar" data-cedula="${cedula}">Modificar</button>
								<button type="button" class="table-action table-action--ghost" data-action="ver" data-cedula="${cedula}">Ver</button>
								<button type="button" class="table-action table-action--danger" data-action="eliminar" data-cedula="${cedula}">Eliminar</button>
							</div>
						</td>
					</tr>
				`;
			})
			.join("");

		renderContador(empleados.length);
				
	}

	async function cargarempleados() {
			const data = await fetchJson("/api/empleados", { method: "GET" });
			const empleados = Array.isArray(data) ? data : Array.isArray(data?.empleados) ? data.empleados : [];
			rendertabla(empleados);
		}


	tbody?.addEventListener("click", (event) => {
		const button = event.target.closest("button[data-action]");
		if (!button) return;

		const action = button.getAttribute("data-action");
		if (action === "editar") {
			abrirModalEditar(button);
			return;
		}

		if (action === "eliminar") {
			abrirModalEliminar(button);
		}
	});

	btnActualizar?.addEventListener("click", () => {
		cargarempleados().catch((error) => {
			showMessage(error.message || "No fue posible actualizar los empleados.", true);
		});
	});

	cargarempleados().catch((error) => {
		showMessage(error.message || "No fue posible cargar los empleados.", true);
	});


});



