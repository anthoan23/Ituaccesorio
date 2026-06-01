document.addEventListener("DOMContentLoaded", () => {
	const tbody = document.getElementById("tabla-cargos");
	const formCrear = document.getElementById("form-cargo");
	const formEditar = document.getElementById("form-editar-cargo");
	const btnActualizar = document.getElementById("btn-actualizar-cargos");
	const btnConfirmarEliminar = document.getElementById("btn-confirmar-eliminar-cargo");
	const textoEliminar = document.getElementById("texto-confirmar-eliminar-cargo");
	const contador = document.querySelector("[data-count]");

	const inputEditarId = document.getElementById("editar-id-cargo");
	const inputEditarNombre = document.getElementById("editar-nombre-cargo");
	const inputEditarDescripcion = document.getElementById("editar-descripcion-cargo");

	let cargoPendienteEliminar = null;

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

	function normalizeCargo(cargo) {
		return {
			id: cargo?.id ?? cargo?.ID_cargo ?? "",
			nombre: cargo?.nombre ?? cargo?.Nombre_cargo ?? "",
			descripcion: cargo?.descripcion ?? cargo?.Descripcion_cargo ?? "",
		};
	}

	function renderContador(total) {
		if (!contador) return;
		contador.setAttribute("data-count", String(total));
		contador.textContent = String(total);
	}

	function renderTabla(cargos) {
		if (!tbody) return;

		if (!cargos.length) {
			tbody.innerHTML = `
				<tr>
					<td colspan="4">No hay cargos para mostrar.</td>
				</tr>
			`;
			renderContador(0);
			return;
		}

		tbody.innerHTML = cargos
			.map((raw) => {
				const cargo = normalizeCargo(raw);
				const id = escapeHtml(cargo.id);
				const nombre = escapeHtml(cargo.nombre);
				const descripcion = escapeHtml(cargo.descripcion || "-");

				return `
					<tr>
						<td>${id}</td>
						<td>${nombre}</td>
						<td>${descripcion}</td>
						<td class="table__actions">
							<div class="row-actions" aria-label="Acciones del cargo">
								<button type="button" class="table-action table-action--accent" data-action="editar" data-id="${id}" data-nombre="${nombre}" data-descripcion="${descripcion}">Modificar</button>
								<button type="button" class="table-action" data-action="eliminar" data-id="${id}" data-nombre="${nombre}">Eliminar</button>
							</div>
						</td>
					</tr>
				`;
			})
			.join("");

		renderContador(cargos.length);
	}

	async function cargarCargos() {
		const data = await fetchJson("/api/cargos", { method: "GET" });
		const cargos = Array.isArray(data) ? data : Array.isArray(data?.cargos) ? data.cargos : [];
		renderTabla(cargos);
	}

	function abrirModalEditar(button) {
		const id = button.getAttribute("data-id") || "";
		const nombre = button.getAttribute("data-nombre") || "";
		const descripcion = button.getAttribute("data-descripcion") || "";

		inputEditarId.value = id;
		inputEditarNombre.value = nombre;
		inputEditarDescripcion.value = descripcion === "-" ? "" : descripcion;
		openModal("modal-editar-cargo");
	}

	function abrirModalEliminar(button) {
		const id = button.getAttribute("data-id") || "";
		const nombre = button.getAttribute("data-nombre") || "";
		cargoPendienteEliminar = { id, nombre };

		if (textoEliminar) {
			textoEliminar.textContent = `¿Estás seguro de que quieres eliminar el registro ${nombre} (${id})?`;
		}

		openModal("modal-eliminar-cargo");
	}

	formCrear?.addEventListener("submit", async (event) => {
		event.preventDefault();

		const payload = {
			nombre_cargo: formCrear.nombre_cargo.value.trim(),
			descripcion_cargo: formCrear.descripcion_cargo.value.trim(),
		};

		try {
			const result = await fetchJson("/api/cargos", {
				method: "POST",
				body: JSON.stringify(payload),
			});
			showMessage(result?.message || "Cargo registrado correctamente.");
			formCrear.reset();
			await cargarCargos();
		} catch (error) {
			showMessage(error.message || "No fue posible registrar el cargo.", true);
		}
	});

	formEditar?.addEventListener("submit", async (event) => {
		event.preventDefault();

		const idCargo = inputEditarId.value.trim();
		const payload = {
			id_cargo: idCargo,
			nombre_cargo: inputEditarNombre.value.trim(),
			descripcion_cargo: inputEditarDescripcion.value.trim(),
		};

		try {
			const result = await fetchJson("/api/cargos", {
				method: "PUT",
				body: JSON.stringify(payload),
			});
			showMessage(result?.message || "Cargo modificado correctamente.");
			closeModal("modal-editar-cargo");
			await cargarCargos();
		} catch (error) {
			showMessage(error.message || "No fue posible modificar el cargo.", true);
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
		if (!cargoPendienteEliminar?.id) return;

		try {
			const result = await fetchJson("/api/cargos", {
				method: "DELETE",
				body: JSON.stringify({ id_cargo: cargoPendienteEliminar.id }),
			});
			showMessage(result?.message || "Cargo eliminado correctamente.");
			cargoPendienteEliminar = null;
			closeModal("modal-eliminar-cargo");
			await cargarCargos();
		} catch (error) {
			showMessage(error.message || "No fue posible eliminar el cargo.", true);
		}
	});

	btnActualizar?.addEventListener("click", () => {
		cargarCargos().catch((error) => {
			showMessage(error.message || "No fue posible actualizar los cargos.", true);
		});
	});

	cargarCargos().catch((error) => {
		showMessage(error.message || "No fue posible cargar los cargos.", true);
	});
});
