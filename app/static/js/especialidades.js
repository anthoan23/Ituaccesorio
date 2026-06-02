document.addEventListener("DOMContentLoaded", () => {
	const tbody = document.getElementById("tabla-especialidades");
	const formCrear = document.getElementById("form-especialidad");
	const formEditar = document.getElementById("form-editar-especialidad");
	const btnActualizar = document.getElementById("btn-actualizar-especialidades");
	const btnConfirmarEliminar = document.getElementById("btn-confirmar-eliminar-especialidad");
	const textoEliminar = document.getElementById("texto-confirmar-eliminar-especialidad");
	const contador = document.querySelector("[data-count]");

	const inputEditarId = document.getElementById("editar-id-especialidad");
	const inputEditarNombre = document.getElementById("editar-nombre-especialidad");
	const inputEditarDescripcion = document.getElementById("editar-descripcion-especialidad");

	let especialidadPendienteEliminar = null;

	function getCsrfToken() {
		const input = document.querySelector("input[name='_csrf_token']");
		return input ? input.value : "";
	}

	function getAccessToken() {
		return (
			localStorage.getItem("access_token") ||
			localStorage.getItem("token") ||
			sessionStorage.getItem("access_token") ||
			sessionStorage.getItem("token") ||
			""
		);
	}

	async function fetchJson(url, options = {}) {
		const headers = new Headers(options.headers || {});
		headers.set("Accept", "application/json");

		if (options.body && !headers.has("Content-Type")) {
			headers.set("Content-Type", "application/json");
		}

		const csrf = getCsrfToken();
		if (csrf) {
			headers.set("X-CSRFToken", csrf);
		}

		const token = getAccessToken();
		if (token && !headers.has("Authorization")) {
			headers.set("Authorization", `Bearer ${token}`);
		}

		const response = await fetch(url, {
			credentials: "same-origin",
			...options,
			headers,
		});

		const contentType = response.headers.get("content-type") || "";
		const isJson = contentType.includes("application/json");
		const payload = isJson ? await response.json() : await response.text();

		if (!response.ok) {
			const msg =
				(isJson && payload && (payload.message || payload.error)) ||
				String(payload || response.statusText || "Error en la solicitud");
			throw new Error(msg);
		}

		return payload;
	}

	function escapeHtml(value) {
		return String(value ?? "")
			.replaceAll("&", "&amp;")
			.replaceAll("<", "&lt;")
			.replaceAll(">", "&gt;")
			.replaceAll('"', "&quot;")
			.replaceAll("'", "&#039;");
	}

	function openModal(id) {
		if (window.UiModal && typeof window.UiModal.openById === "function") {
			window.UiModal.openById(id);
			return;
		}

		const modal = document.getElementById(id);
		if (modal) {
			modal.removeAttribute("hidden");
			modal.setAttribute("aria-hidden", "false");
		}
	}

	function closeModal(id) {
		if (window.UiModal && typeof window.UiModal.closeById === "function") {
			window.UiModal.closeById(id);
			return;
		}

		const modal = document.getElementById(id);
		if (modal) {
			modal.setAttribute("hidden", "");
			modal.setAttribute("aria-hidden", "true");
		}
	}

	function showMessage(message, isError = false) {
		if (!message) return;
		if (isError) {
			window.alert(message);
			return;
		}
		console.info(message);
	}

	function normalizeEspecialidad(especialidad) {
		return {
			id: especialidad?.id ?? especialidad?.ID_especialidad ?? "",
			nombre: especialidad?.nombre ?? especialidad?.Nombre_especialidad ?? "",
			descripcion: especialidad?.descripcion ?? especialidad?.Descripcion_especialidad ?? "",
		};
	}

	function renderContador(total) {
		if (!contador) return;
		contador.setAttribute("data-count", String(total));
		contador.textContent = String(total);
	}

	function renderTabla(especialidades) {
		if (!tbody) return;

		if (!especialidades.length) {
			tbody.innerHTML = `
				<tr>
					<td colspan="4">No hay especialidades para mostrar.</td>
				</tr>
			`;
			renderContador(0);
			return;
		}

		tbody.innerHTML = especialidades
			.map((raw) => {
				const especialidad = normalizeEspecialidad(raw);
				const id = escapeHtml(especialidad.id);
				const nombre = escapeHtml(especialidad.nombre);
				const descripcion = escapeHtml(especialidad.descripcion || "-");

				return `
					<tr>
						<td>${id}</td>
						<td>${nombre}</td>
						<td>${descripcion}</td>
						<td class="table__actions">
							<div class="row-actions" aria-label="Acciones de la especialidad">
								<button type="button" class="table-action table-action--accent" data-action="editar" data-id="${id}" data-nombre="${nombre}" data-descripcion="${descripcion}">Modificar</button>
								<button type="button" class="table-action" data-action="eliminar" data-id="${id}" data-nombre="${nombre}">Eliminar</button>
							</div>
						</td>
					</tr>
				`;
			})
			.join("");

		renderContador(especialidades.length);
	}

	async function cargarEspecialidades() {
		const data = await fetchJson("/api/especialidades", { method: "GET" });
		const especialidades = Array.isArray(data) ? data : Array.isArray(data?.especialidades) ? data.especialidades : [];
		renderTabla(especialidades);
	}

	function abrirModalEditar(button) {
		const id = button.getAttribute("data-id") || "";
		const nombre = button.getAttribute("data-nombre") || "";
		const descripcion = button.getAttribute("data-descripcion") || "";

		inputEditarId.value = id;
		inputEditarNombre.value = nombre;
		inputEditarDescripcion.value = descripcion === "-" ? "" : descripcion;
		openModal("modal-editar-especialidad");
	}

	function abrirModalEliminar(button) {
		const id = button.getAttribute("data-id") || "";
		const nombre = button.getAttribute("data-nombre") || "";
		especialidadPendienteEliminar = { id, nombre };

		if (textoEliminar) {
			textoEliminar.textContent = `¿Estás seguro de que quieres eliminar el registro ${nombre} (${id})?`;
		}

		openModal("modal-eliminar-especialidad");
	}

	formCrear?.addEventListener("submit", async (event) => {
		event.preventDefault();

		const payload = {
			nombre_especialidad: formCrear.nombre_especialidad.value.trim(),
			descripcion_especialidad: formCrear.descripcion_especialidad.value.trim(),
		};

		try {
			const result = await fetchJson("/api/especialidades", {
				method: "POST",
				body: JSON.stringify(payload),
			});
			showMessage(result?.message || "Especialidad registrada correctamente.");
			formCrear.reset();
			await cargarEspecialidades();
		} catch (error) {
			showMessage(error.message || "No fue posible registrar la especialidad.", true);
		}
	});

	formEditar?.addEventListener("submit", async (event) => {
		event.preventDefault();

		const idEspecialidad = inputEditarId.value.trim();
		const payload = {
			id_especialidad: idEspecialidad,
			nombre_especialidad: inputEditarNombre.value.trim(),
			descripcion_especialidad: inputEditarDescripcion.value.trim(),
		};

		try {
			const result = await fetchJson("/api/especialidades", {
				method: "PUT",
				body: JSON.stringify(payload),
			});
			showMessage(result?.message || "Especialidad modificada correctamente.");
			closeModal("modal-editar-especialidad");
			await cargarEspecialidades();
		} catch (error) {
			showMessage(error.message || "No fue posible modificar la especialidad.", true);
		}
	});

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

	btnConfirmarEliminar?.addEventListener("click", async () => {
		if (!especialidadPendienteEliminar?.id) return;

		try {
			const result = await fetchJson("/api/especialidades", {
				method: "DELETE",
				body: JSON.stringify({ id_especialidad: especialidadPendienteEliminar.id }),
			});
			showMessage(result?.message || "Especialidad eliminada correctamente.");
			especialidadPendienteEliminar = null;
			closeModal("modal-eliminar-especialidad");
			await cargarEspecialidades();
		} catch (error) {
			showMessage(error.message || "No fue posible eliminar la especialidad.", true);
		}
	});

	btnActualizar?.addEventListener("click", () => {
		cargarEspecialidades().catch((error) => {
			showMessage(error.message || "No fue posible actualizar las especialidades.", true);
		});
	});

	cargarEspecialidades().catch((error) => {
		showMessage(error.message || "No fue posible cargar las especialidades.", true);
	});
});
