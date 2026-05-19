document.addEventListener("DOMContentLoaded", () => {
	const csrfToken = document.getElementById("csrf-token")?.value || "";
	const tablaOrdenes = document.getElementById("tabla-ordenes-servicio");
	const tablaPendientes = document.getElementById("tabla-pendientes");
	const tablaAsignadas = document.getElementById("tabla-asignadas");
	const tablaRevisadas = document.getElementById("tabla-revisadas");
	const tablaTrabajosTecnico = document.getElementById("tabla-trabajos-tecnico");
	const statPendientes = document.getElementById("stat-pendientes");
	const statAsignadas = document.getElementById("stat-asignadas");
	const statRevisadas = document.getElementById("stat-revisadas");
	const formOrden = document.getElementById("form-orden-servicio");
	const btnVerificarCliente = document.getElementById("btn-verificar-cliente");
	const btnCrearCliente = document.getElementById("btn-crear-cliente");
	const clienteStatus = document.getElementById("cliente-status");
	const selectModelo = document.getElementById("orden-modelo");
	const inputFecha = document.getElementById("orden-fecha");
	const selectOrdenAsignar = document.getElementById("select-orden-asignar");
	const selectTecnico = document.getElementById("select-tecnico");
	const btnAsignarOrden = document.getElementById("btn-asignar-orden");
	const modalTecnicoSelect = document.getElementById("modal-tecnico-select");
	const btnCargarTrabajos = document.getElementById("btn-cargar-trabajos");
	const detalleOrdenId = document.getElementById("detalle-orden-id");
	const detalleInfo = document.getElementById("detalle-info");
	const detalleResponsables = document.getElementById("detalle-responsables");
	const detalleFotos = document.getElementById("detalle-fotos");
	const detalleTests = document.getElementById("detalle-tests");
	const revisionOrdenId = document.getElementById("revision-orden-id");
	const formRevision = document.getElementById("form-revision-orden");
	const fotosOrdenId = document.getElementById("fotos-orden-id");
	const formFotos = document.getElementById("form-fotos-orden");
	const inputFotos = document.getElementById("input-fotos-orden");
	const previewFotos = document.getElementById("preview-fotos");
	const toast = document.getElementById("toast-mensaje");

	let ordenes = [];
	let clienteActualId = null;
	let ordenActualId = null;
	let testsOrdenActual = [];

	init();

	function init() {
		if (inputFecha && !inputFecha.value) {
			const hoy = new Date();
			inputFecha.value = hoy.toISOString().slice(0, 10);
		}

		btnVerificarCliente?.addEventListener("click", verificarCliente);
		btnCrearCliente?.addEventListener("click", registrarClienteDesdeFormulario);
		formOrden?.addEventListener("submit", onSubmitOrden);
		btnAsignarOrden?.addEventListener("click", asignarOrden);
		btnCargarTrabajos?.addEventListener("click", cargarTrabajosTecnico);
		formRevision?.addEventListener("submit", guardarRevision);
		formFotos?.addEventListener("submit", guardarFotos);
		inputFotos?.addEventListener("change", () => renderPreviewFotos(inputFotos.files));
		document.addEventListener("click", onTablaClick);

		cargarModelos();
		cargarTecnicos();
		cargarOrdenes();
	}

	function onTablaClick(event) {
		const btn = event.target.closest("button[data-action]");
		if (!btn) return;
		const action = btn.dataset.action;
		const id = btn.dataset.id;
		if (!id) return;

		if (action === "ver-detalle") {
			abrirDetalleOrden(id);
			return;
		}

		if (action === "seleccionar-asignacion") {
			if (selectOrdenAsignar) {
				selectOrdenAsignar.value = String(id);
			}
			return;
		}
	}

	async function fetchJson(url, options = {}) {
		const response = await fetch(url, {
			headers: {
				"Content-Type": "application/json",
				"Accept": "application/json",
				...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
			},
			credentials: "same-origin",
			...options,
		});
		const data = await response.json().catch(() => ({}));
		if (!response.ok || data.success === false) {
			throw new Error(data.error || "No se pudo completar la operación.");
		}
		return data;
	}

	function mostrarToast(message, isError = false) {
		if (!toast) return;
		toast.textContent = message;
		toast.classList.toggle("toast--error", isError);
		toast.classList.add("is-visible");
		window.clearTimeout(mostrarToast._timer);
		mostrarToast._timer = window.setTimeout(() => {
			toast.classList.remove("is-visible");
		}, 2600);
	}

	function setClienteStatus(message, isError = false) {
		if (!clienteStatus) return;
		clienteStatus.textContent = message;
		clienteStatus.classList.toggle("is-error", isError);
	}

	function limpiarClienteForm() {
		setFieldValue("cliente-nombre", "");
		setFieldValue("cliente-apellido", "");
		setFieldValue("cliente-celular", "");
		setFieldValue("cliente-correo", "");
		setFieldValue("cliente-direccion", "");
		setFieldValue("cliente-tipo", "");
	}

	async function verificarCliente() {
		const cedula = getFieldValue("cliente-cedula");
		if (!cedula) {
			setClienteStatus("Ingresa una cédula para verificar.", true);
			return;
		}

		try {
			const response = await fetch(`/api/clientes/${encodeURIComponent(cedula)}`, {
				headers: {
					"Accept": "application/json",
					...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
				},
				credentials: "same-origin",
			});
			const data = await response.json().catch(() => ({}));
			if (!response.ok || data.success === false) {
				clienteActualId = null;
				limpiarClienteForm();
				setClienteStatus("Cliente no encontrado. Regístralo para continuar.", true);
				if (btnCrearCliente) btnCrearCliente.hidden = false;
				return;
			}
			const cliente = data.cliente || {};
			clienteActualId = cliente.ID_c || cedula;
			setFieldValue("cliente-nombre", cliente.nombre || "");
			setFieldValue("cliente-apellido", cliente.apellido || "");
			setFieldValue("cliente-celular", cliente.celular || "");
			setFieldValue("cliente-correo", cliente.correo || "");
			setFieldValue("cliente-direccion", cliente.direccion || "");
			setFieldValue("cliente-tipo", cliente.tipo || "");
			setClienteStatus("Cliente verificado correctamente.");
			if (btnCrearCliente) btnCrearCliente.hidden = true;
		} catch (error) {
			setClienteStatus("No se pudo verificar el cliente.", true);
		}
	}

	async function registrarClienteDesdeFormulario() {
		try {
			const payload = obtenerClientePayload();
			if (!payload.cedula || !payload.nombre || !payload.apellido || !payload.celular) {
				setClienteStatus("Cédula, nombre, apellido y celular son obligatorios.", true);
				return;
			}
			const data = await fetchJson("/api/clientes", {
				method: "POST",
				body: JSON.stringify(payload),
			});
			clienteActualId = data.id || payload.cedula;
			setClienteStatus("Cliente registrado.");
			if (btnCrearCliente) btnCrearCliente.hidden = true;
		} catch (error) {
			setClienteStatus(error.message || "No se pudo registrar el cliente.", true);
		}
	}

	function obtenerClientePayload() {
		return {
			cedula: getFieldValue("cliente-cedula"),
			nombre: getFieldValue("cliente-nombre"),
			apellido: getFieldValue("cliente-apellido"),
			celular: getFieldValue("cliente-celular"),
			correo: getFieldValue("cliente-correo"),
			direccion: getFieldValue("cliente-direccion"),
			tipo: getFieldValue("cliente-tipo"),
		};
	}

	async function onSubmitOrden(event) {
		event.preventDefault();
		if (!formOrden) return;

		let clienteId = clienteActualId;
		if (!clienteId) {
			await registrarClienteDesdeFormulario();
			clienteId = clienteActualId;
		}
		if (!clienteId) {
			mostrarToast("Debes verificar o registrar el cliente primero.", true);
			return;
		}

		const payload = {
			id_cliente: clienteId,
			id_modelo: selectModelo?.value,
			fecha_ingreso: inputFecha?.value,
			patron: getFieldValue("orden-patron"),
			clave: getFieldValue("orden-clave"),
			descripcion: getFieldValue("orden-descripcion"),
			nota: getFieldValue("orden-nota"),
		};

		try {
			await fetchJson("/api/ordenes-servicio", {
				method: "POST",
				body: JSON.stringify(payload),
			});
			mostrarToast("Orden creada correctamente.");
			formOrden.reset();
			clienteActualId = null;
			setClienteStatus("");
			if (btnCrearCliente) btnCrearCliente.hidden = true;
			if (inputFecha) {
				const hoy = new Date();
				inputFecha.value = hoy.toISOString().slice(0, 10);
			}
			cargarOrdenes();
		} catch (error) {
			mostrarToast(error.message || "No se pudo crear la orden.", true);
		}
	}

	async function cargarModelos() {
		if (!selectModelo) return;
		try {
			const data = await fetchJson("/api/productos/modelos");
			const modelos = data.modelos || [];
			selectModelo.innerHTML = '<option value="">Seleccione modelo</option>' + modelos.map((modelo) => {
				const label = `${modelo.clase_nombre ?? ""} ${modelo.marca_nombre ?? ""} ${modelo.nombre ?? ""}`.trim();
				return `<option value="${escapeHtml(modelo.id)}">${escapeHtml(label)}</option>`;
			}).join("");
		} catch (error) {
			console.error("Error cargando modelos", error);
		}
	}

	async function cargarTecnicos() {
		try {
			const data = await fetchJson("/api/ordenes-servicio/tecnicos");
			const tecnicos = data.tecnicos || [];
			renderSelectTecnicos(selectTecnico, tecnicos);
			renderSelectTecnicos(modalTecnicoSelect, tecnicos);
		} catch (error) {
			console.error("Error cargando técnicos", error);
		}
	}

	function renderSelectTecnicos(select, tecnicos) {
		if (!select) return;
		select.innerHTML = '<option value="">Seleccione un técnico</option>' + tecnicos.map((tec) => {
			const nombre = `${tec.nombre ?? ""} ${tec.apellido ?? ""}`.trim();
			return `<option value="${escapeHtml(tec.id)}">${escapeHtml(nombre)} (${escapeHtml(tec.id)})</option>`;
		}).join("");
	}

	async function cargarOrdenes() {
		try {
			const data = await fetchJson("/api/ordenes-servicio/ordenes");
			ordenes = data.ordenes || [];
			renderTablaOrdenes();
			actualizarEstadisticas();
			renderSelectOrdenesAsignar();
			await Promise.all([
				cargarOrdenesEstado("Pendiente", tablaPendientes),
				cargarOrdenesEstado("Asignado", tablaAsignadas),
				cargarOrdenesEstado("Revisado", tablaRevisadas),
			]);
		} catch (error) {
			console.error("Error cargando órdenes", error);
		}
	}

	async function cargarOrdenesEstado(estado, tablaDestino) {
		if (!tablaDestino) return;
		try {
			const data = await fetchJson(`/api/ordenes-servicio/ordenes?estado=${encodeURIComponent(estado)}`);
			renderTablaEstado(tablaDestino, data.ordenes || []);
		} catch (error) {
			tablaDestino.innerHTML = '<tr><td colspan="5">No se pudieron cargar las órdenes.</td></tr>';
		}
	}

	function renderTablaOrdenes() {
		if (!tablaOrdenes) return;
		if (!ordenes.length) {
			tablaOrdenes.innerHTML = '<tr><td colspan="7">No hay órdenes registradas.</td></tr>';
			return;
		}

		tablaOrdenes.innerHTML = ordenes.map((orden) => {
			const clienteNombre = `${orden.Nombre_cliente ?? ""} ${orden.Apellido_cliente ?? ""}`.trim();
			return `
				<tr>
					<td>${escapeHtml(orden.ID_orden)}</td>
					<td>${escapeHtml(orden.Estado)}</td>
					<td>${escapeHtml(clienteNombre)}</td>
					<td>${escapeHtml(orden.Modelo ?? "")}</td>
					<td>${escapeHtml(orden.Des_cliente ?? "")}</td>
					<td>${escapeHtml(formatFecha(getFechaOrden(orden)))}</td>
					<td class="table__actions">
						<div class="row-actions">
							<button type="button" class="btn btn--ghost" data-action="ver-detalle" data-id="${escapeHtml(orden.ID_orden)}">Detalle</button>
							<button type="button" class="btn btn--primary" data-action="seleccionar-asignacion" data-id="${escapeHtml(orden.ID_orden)}">Asignar</button>
						</div>
					</td>
				</tr>
			`;
		}).join("");
	}

	function renderTablaEstado(tablaDestino, lista) {
		if (!lista.length) {
			tablaDestino.innerHTML = '<tr><td colspan="5">Sin órdenes.</td></tr>';
			return;
		}
		tablaDestino.innerHTML = lista.map((orden) => {
			const clienteNombre = `${orden.Nombre_cliente ?? ""} ${orden.Apellido_cliente ?? ""}`.trim();
			return `
				<tr>
					<td>${escapeHtml(orden.ID_orden)}</td>
					<td>${escapeHtml(clienteNombre)}</td>
					<td>${escapeHtml(orden.Modelo ?? "")}</td>
					<td>${escapeHtml(formatFecha(getFechaOrden(orden)))}</td>
					<td class="table__actions">
						<button type="button" class="btn btn--ghost" data-action="ver-detalle" data-id="${escapeHtml(orden.ID_orden)}">Detalle</button>
					</td>
				</tr>
			`;
		}).join("");
	}

	function actualizarEstadisticas() {
		const count = (estado) => ordenes.filter((o) => String(o.Estado || "").toLowerCase() === estado).length;
		const pendientes = count("pendiente");
		const asignadas = count("asignado");
		const revisadas = ordenes.filter((o) => ["revisado", "en revisión", "en revision"].includes(String(o.Estado || "").toLowerCase())).length;
		if (statPendientes) statPendientes.textContent = String(pendientes);
		if (statAsignadas) statAsignadas.textContent = String(asignadas);
		if (statRevisadas) statRevisadas.textContent = String(revisadas);
	}

	function renderSelectOrdenesAsignar() {
		if (!selectOrdenAsignar) return;
		const pendientes = ordenes.filter((o) => String(o.Estado || "").toLowerCase() === "pendiente");
		selectOrdenAsignar.innerHTML = '<option value="">Seleccione una orden</option>' + pendientes.map((orden) => {
			return `<option value="${escapeHtml(orden.ID_orden)}">#${escapeHtml(orden.ID_orden)} - ${escapeHtml(orden.Modelo ?? "")}</option>`;
		}).join("");
	}

	async function asignarOrden() {
		const idOrden = selectOrdenAsignar?.value;
		const idTecnico = selectTecnico?.value;
		if (!idOrden || !idTecnico) {
			mostrarToast("Selecciona una orden y un técnico.", true);
			return;
		}

		try {
			await fetchJson(`/api/ordenes-servicio/ordenes/${encodeURIComponent(idOrden)}/asignar`, {
				method: "POST",
				body: JSON.stringify({ id_empleado: idTecnico }),
			});
			mostrarToast("Orden asignada.");
			cargarOrdenes();
		} catch (error) {
			mostrarToast(error.message || "No se pudo asignar la orden.", true);
		}
	}

	async function cargarTrabajosTecnico() {
		const idTecnico = modalTecnicoSelect?.value;
		if (!idTecnico) {
			mostrarToast("Selecciona un técnico.", true);
			return;
		}
		if (!tablaTrabajosTecnico) return;
		try {
			const data = await fetchJson(`/api/ordenes-servicio/tecnicos/${encodeURIComponent(idTecnico)}/ordenes`);
			renderTablaTrabajosTecnico(data.ordenes || []);
		} catch (error) {
			tablaTrabajosTecnico.innerHTML = '<tr><td colspan="5">No se pudieron cargar los trabajos.</td></tr>';
		}
	}

	function renderTablaTrabajosTecnico(lista) {
		if (!tablaTrabajosTecnico) return;
		if (!lista.length) {
			tablaTrabajosTecnico.innerHTML = '<tr><td colspan="5">Sin trabajos asignados.</td></tr>';
			return;
		}
		tablaTrabajosTecnico.innerHTML = lista.map((orden) => {
			const clienteNombre = `${orden.Nombre_cliente ?? ""} ${orden.Apellido_cliente ?? ""}`.trim();
			return `
				<tr>
					<td>${escapeHtml(orden.ID_orden)}</td>
					<td>${escapeHtml(clienteNombre)}</td>
					<td>${escapeHtml(orden.Modelo ?? "")}</td>
					<td>${escapeHtml(orden.Estado ?? "")}</td>
					<td class="table__actions">
						<button type="button" class="btn btn--ghost" data-action="ver-detalle" data-id="${escapeHtml(orden.ID_orden)}">Detalle</button>
					</td>
				</tr>
			`;
		}).join("");
	}

	async function abrirDetalleOrden(idOrden) {
		try {
			const data = await fetchJson(`/api/ordenes-servicio/ordenes/${encodeURIComponent(idOrden)}`);
			ordenActualId = idOrden;
			testsOrdenActual = data.test_orden || [];
			if (detalleOrdenId) detalleOrdenId.value = String(idOrden);
			if (revisionOrdenId) revisionOrdenId.value = String(idOrden);
			if (fotosOrdenId) fotosOrdenId.value = String(idOrden);
			renderDetalleInfo(data.detalle_orden);
			renderResponsables(data.empleados_orden || []);
			renderFotos(data.fotos_orden || []);
			renderTests(data.test_orden || []);
			if (window.UiModal && typeof window.UiModal.openById === "function") {
				window.UiModal.openById("modal-detalle-orden");
			}
		} catch (error) {
			mostrarToast(error.message || "No se pudo cargar el detalle.", true);
		}
	}

	function renderDetalleInfo(detalle) {
		if (!detalleInfo) return;
		if (!detalle) {
			detalleInfo.innerHTML = "<p>No hay información disponible.</p>";
			return;
		}
		const getField = (...keys) => {
			for (const k of keys) {
				if (k in detalle && detalle[k] !== null && detalle[k] !== undefined && String(detalle[k]).trim() !== "") {
					return detalle[k];
				}
			}
			return "";
		};
		const cliente = `${getField("Nombre_cliente")} ${getField("Apellido_cliente")}`.trim();
		const fecha = getField("Fecha_e", "Fecha", "Fecha_o", "Fecha_ingreso");
		const items = [
			["ID orden", getField("ID_orden_e", "ID_orden", "ID")],
			["Estado", getField("Estado_o", "Estado")],
			["Cliente", cliente],
			["Modelo", getField("Modelo")],
			["Fecha ingreso", formatFecha(fecha)],
			["Patrón", getField("Patron")],
			["Clave", getField("Clave")],
			["Descripción", getField("Des_cliente")],
			["Nota", getField("Nota")],
			["Cotización", getField("Costo_reparacion")],
			["Reparación", getField("Reparacion")],
			["Revisión", getField("Revision")],
		];
		const html = items
			.filter(([, value]) => value !== "")
			.map(([label, value]) => `
				<div class="detail-item">
					<span class="detail-item__label">${escapeHtml(label)}</span>
					<span class="detail-item__value">${escapeHtml(value)}</span>
				</div>
			`)
			.join("");
		detalleInfo.innerHTML = html || "<p>Sin información disponible.</p>";
	}

	function renderResponsables(empleados) {
		if (!detalleResponsables) return;
		const roles = [
			{ label: "Guardó la orden", acciones: ["Recepcion"] },
			{ label: "Asignada a", acciones: ["Asignado"] },
			{ label: "Reparó", acciones: ["Reparacion", "Reparado"] },
			{ label: "Revisó", acciones: ["Revision", "Revisado"] },
		];
		const responsables = {};
		empleados.forEach((item) => {
			const accion = item.Accion || item.accion;
			if (!accion) return;
			const nombre = `${item.Nombre_em ?? ""} ${item.Apellido_em ?? ""}`.trim();
			if (!responsables[accion]) responsables[accion] = [];
			responsables[accion].push(`${nombre} (${item.ID_em})`);
		});

		const rows = roles.map((rol) => {
			const nombres = rol.acciones
				.flatMap((accion) => responsables[accion] || [])
				.filter(Boolean);
			return `
				<div class="detail-item">
					<span class="detail-item__label">${escapeHtml(rol.label)}</span>
					<span class="detail-item__value">${escapeHtml(nombres.length ? nombres.join(", ") : "Sin registro")}</span>
				</div>
			`;
		});
		detalleResponsables.innerHTML = rows.join("");
	}

	function renderFotos(fotos) {
		if (!detalleFotos) return;
		if (!fotos.length) {
			detalleFotos.innerHTML = "<p>No hay fotos registradas.</p>";
			return;
		}
		detalleFotos.innerHTML = fotos.map((foto) => {
			let src = foto.Foto_e || foto.foto || foto.url || "";
			if (src && !src.startsWith("/") && !src.startsWith("http")) {
				src = `/${src}`;
			}
			return `<img src="${escapeHtml(src)}" alt="Evidencia">`;
		}).join("");
	}

	function renderTests(tests) {
		if (!detalleTests) return;
		if (!tests.length) {
			detalleTests.innerHTML = "<p>No hay tests registrados.</p>";
			return;
		}
		detalleTests.innerHTML = `
			<table class="table">
				<thead>
					<tr>
						<th>Fecha</th>
						<th>Número</th>
						<th>Observaciones</th>
					</tr>
				</thead>
				<tbody>
					${tests.map((test) => `
						<tr>
							<td>${escapeHtml(formatFecha(test.Fecha_e ?? test.Fecha ?? ""))}</td>
							<td>${escapeHtml(test.Num_test ?? "")}</td>
							<td>${escapeHtml(test.Observaciones ?? "")}</td>
						</tr>
					`).join("")}
				</tbody>
			</table>
		`;
	}

	async function guardarRevision(event) {
		event.preventDefault();
		const idOrden = revisionOrdenId?.value || ordenActualId;
		if (!idOrden) {
			mostrarToast("Selecciona una orden.", true);
			return;
		}

		const payload = {};
		const campos = [
			"Btn_power",
			"Btn_vol",
			"Cornetas",
			"Mica",
			"LCD",
			"Tactil",
			"Wifi",
			"Puerto_carga",
			"Cam_pos",
			"Cam_del",
			"Microfono",
			"Flash",
			"Btn_sil",
			"Auricular",
			"Senal",
			"Sensor_proximidad",
			"Face_id",
			"Bluetooth",
		];
		campos.forEach((campo) => {
			const el = formRevision?.querySelector(`[name="${campo}"]`);
			if (el) payload[campo] = el.checked ? 1 : 0;
		});

		payload.Num_test = obtenerSiguienteNumeroTest();
		payload.Observaciones = formRevision?.querySelector('[name="Observaciones"]')?.value || "";
		payload.Costo = formRevision?.querySelector('[name="Costo"]')?.value || "";

		try {
			await fetchJson(`/api/ordenes-servicio/ordenes/${encodeURIComponent(idOrden)}/revision`, {
				method: "POST",
				body: JSON.stringify(payload),
			});
			mostrarToast("Revisión registrada.");
			formRevision?.reset();
			if (window.UiModal && typeof window.UiModal.closeById === "function") {
				window.UiModal.closeById("modal-revision-orden");
			}
			await abrirDetalleOrden(idOrden);
			cargarOrdenes();
		} catch (error) {
			mostrarToast(error.message || "No se pudo guardar la revisión.", true);
		}
	}

	function obtenerSiguienteNumeroTest() {
		const numeros = testsOrdenActual
			.map((test) => Number(test.Num_test ?? test.num_test ?? 0))
			.filter((num) => Number.isFinite(num));
		return numeros.length ? Math.max(...numeros) + 1 : 1;
	}

	async function guardarFotos(event) {
		event.preventDefault();
		const idOrden = fotosOrdenId?.value || ordenActualId;
		if (!idOrden || !formFotos) return;
		const formData = new FormData(formFotos);
		try {
			const response = await fetch(`/api/taller/ordenes/${encodeURIComponent(idOrden)}/fotos`, {
				method: "POST",
				body: formData,
				headers: {
					...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
				},
				credentials: "same-origin",
			});
			const data = await response.json().catch(() => ({}));
			if (!response.ok || data.ok === false) {
				throw new Error(data.message || "No se pudieron guardar las fotos.");
			}
			mostrarToast("Fotos registradas.");
			formFotos.reset();
			renderPreviewFotos([]);
			if (window.UiModal && typeof window.UiModal.closeById === "function") {
				window.UiModal.closeById("modal-fotos-orden");
			}
			await abrirDetalleOrden(idOrden);
		} catch (error) {
			mostrarToast(error.message || "No se pudieron guardar las fotos.", true);
		}
	}

	function renderPreviewFotos(files) {
		if (!previewFotos) return;
		const lista = Array.from(files || []);
		if (!lista.length) {
			previewFotos.innerHTML = "";
			return;
		}
		previewFotos.innerHTML = lista
			.map(
				(file) =>
					`<img src="${URL.createObjectURL(file)}" alt="${escapeHtml(file.name)}">`,
			)
			.join("");
	}

	function getFieldValue(fieldId) {
		const field = document.getElementById(fieldId);
		return field && "value" in field ? String(field.value).trim() : "";
	}

	function setFieldValue(fieldId, value) {
		const field = document.getElementById(fieldId);
		if (field && "value" in field) {
			field.value = value;
		}
	}

	function formatFecha(value) {
		if (!value) return "";
		const fecha = new Date(value);
		if (Number.isNaN(fecha.getTime())) return value;
		return fecha.toLocaleDateString("es-ES");
	}

	function getFechaOrden(orden) {
		if (!orden) return "";
		return orden.Fecha_e ?? orden.Fecha ?? orden.Fecha_o ?? orden.Fecha_ingreso ?? "";
	}

	function escapeHtml(text) {
		return String(text ?? "")
			.replace(/&/g, "&amp;")
			.replace(/</g, "&lt;")
			.replace(/>/g, "&gt;")
			.replace(/"/g, "&quot;")
			.replace(/'/g, "&#039;");
	}
});
