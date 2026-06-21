const Iconos = {
	ojo: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" fill="currentColor"/></svg>`,
	asignar: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" fill="currentColor"/></svg>`
};

document.addEventListener("DOMContentLoaded", () => {
	const csrfToken = document.getElementById("csrf-token")?.value || "";
	const tablaOrdenes = document.getElementById("tabla-ordenes");
	const tablaOrdenesEstadoBody = document.getElementById("modal-ordenes-estado-body");
	const modalOrdenesEstadoSubtitle = document.getElementById("modal-ordenes-estado-subtitle");
	const estadoCards = document.querySelectorAll("[data-estado-card]");
	const tablaPendientes = document.getElementById("tabla-pendientes");
	const tablaAsignadas = document.getElementById("tabla-asignadas");
	const tablaRevisadas = document.getElementById("tabla-revisadas");
	const tablaTrabajosTecnico = document.getElementById("tabla-trabajos-tecnico");
	const statPendientes = document.getElementById("stat-pendientes");
	const statAsignadas = document.getElementById("stat-asignadas");
	const statRevisadas = document.getElementById("stat-revisadas");
	const formOrden = document.getElementById("form-orden-servicio");
	const btnVerificarEquipo = document.getElementById("btn-verificar-equipo");
	const btnVerificarCliente = document.getElementById("btn-verificar-cliente");
	const btnCrearCliente = document.getElementById("btn-crear-cliente");
	const clienteStatus = document.getElementById("cliente-status");
	const equipoStatus = document.getElementById("equipo-status");
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
		// Establecer fecha mínima de hoy
		if (inputFecha) {
			const hoy = new Date();
			const fechaHoy = hoy.toISOString().slice(0, 10);
			inputFecha.min = fechaHoy;
			if (!inputFecha.value) {
				inputFecha.value = fechaHoy;
			}
		}

		// Filtrar IMEI para solo números
		const inputImei = document.getElementById("orden-id-equipo");
		if (inputImei) {
			inputImei.addEventListener("input", (e) => {
				e.target.value = e.target.value.replace(/[^0-9]/g, "");
			});
		}

		// Filtrar cédula para solo números
		const inputCedula = document.getElementById("cliente-cedula");
		if (inputCedula) {
			inputCedula.addEventListener("input", (e) => {
				e.target.value = e.target.value.replace(/[^0-9]/g, "");
			});
		}

		// Validador de patrón (1-9, sin repetición, con guiones automáticos)
		const inputPatron = document.getElementById("orden-patron");
		if (inputPatron) {
			inputPatron.addEventListener("input", (e) => {
				let value = e.target.value.replace(/[^0-9-]/g, ""); // Solo números y guiones
				let numbers = value.replace(/-/g, "").split(""); // Extraer números
				
				// Validar que no haya repetidos y que todos estén entre 1-9
				let used = new Set();
				let validNumbers = [];
				for (let num of numbers) {
					if (num >= "1" && num <= "9" && !used.has(num)) {
						validNumbers.push(num);
						used.add(num);
					}
				}
				
				// Limitar a máximo 9 números (1-9)
				validNumbers = validNumbers.slice(0, 9);
				
				// Agregar guiones
				e.target.value = validNumbers.join("-");
			});
		}

		// Validador de celular (solo números, máximo 11)
		const inputCelular = document.getElementById("cliente-celular");
		if (inputCelular) {
			inputCelular.addEventListener("input", (e) => {
				e.target.value = e.target.value.replace(/[^0-9]/g, "").slice(0, 11);
			});
		}

		btnVerificarEquipo?.addEventListener("click", verificarEquipo);
		btnVerificarCliente?.addEventListener("click", verificarCliente);
		btnCrearCliente?.addEventListener("click", registrarClienteDesdeFormulario);
		formOrden?.addEventListener("submit", onSubmitOrden);
		btnAsignarOrden?.addEventListener("click", asignarOrden);
		document.getElementById("btn-asignar-tecnico")?.addEventListener("click", () => {
			if (window.UiModal && typeof window.UiModal.openById === "function") {
				window.UiModal.openById("modal-asignar-tecnico");
			}
		});
		btnCargarTrabajos?.addEventListener("click", cargarTrabajosTecnico);
		formRevision?.addEventListener("submit", guardarRevision);
		formFotos?.addEventListener("submit", guardarFotos);
		inputFotos?.addEventListener("change", () => renderPreviewFotos(inputFotos.files));
		document.addEventListener("click", onTablaClick);
		bindEstadoCards();

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

	function getAuthToken() {
		const fromLocal = window.localStorage ? window.localStorage.getItem("access_token") : "";
		if (fromLocal) return fromLocal;
		const fromSession = window.sessionStorage ? window.sessionStorage.getItem("access_token") : "";
		if (fromSession) return fromSession;
		return "";
	}

	async function fetchJson(url, options = {}) {
		const authToken = getAuthToken();
		const { headers: extraHeaders, ...otherOptions } = options;

		const response = await fetch(url, {
			...otherOptions,
			credentials: "same-origin",
			headers: {
				"Content-Type": "application/json",
				"Accept": "application/json",
				...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
				...(authToken ? { "Authorization": `Bearer ${authToken}` } : {}),
				...(extraHeaders || {}),
			},
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
			const authToken = getAuthToken();
			const response = await fetch(`/api/clientes/${encodeURIComponent(cedula)}`, {
				credentials: "same-origin",
				headers: {
					"Accept": "application/json",
					...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
					...(authToken ? { "Authorization": `Bearer ${authToken}` } : {}),
				},
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
			clienteActualId = cliente.id || cedula;
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

	async function verificarEquipo() {
		const idEquipo = getFieldValue("orden-id-equipo");
		if (!idEquipo) {
			setEquipoStatus("Ingresa el IMEI/ID del equipo para verificar.", true);
			return;
		}

		// Validar que solo contenga números
		if (!/^\d+$/.test(idEquipo)) {
			setEquipoStatus("El IMEI solo puede contener números.", true);
			return;
		}

		if (idEquipo.length !== 15) {
			setEquipoStatus("El IMEI debe tener exactamente 15 caracteres.", true);
			return;
		}

		try {
			const authToken = getAuthToken();
			const response = await fetch(`/api/ordenes-servicio/equipo/${encodeURIComponent(idEquipo)}`, {
				credentials: "same-origin",
				headers: {
					"Accept": "application/json",
					...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
					...(authToken ? { "Authorization": `Bearer ${authToken}` } : {}),
				},
			});
			const data = await response.json().catch(() => ({}));
			if (!response.ok || data.success === false) {
				setEquipoStatus("No se pudo verificar el equipo.", true);
				return;
			}

			if (data.exists) {
				const equipo = data.equipo || {};
				setEquipoStatus("Equipo existente encontrado. Usa los datos cargados.");
				if (equipo.id_modelo && selectModelo) {
					selectModelo.value = String(equipo.id_modelo);
				}
			} else {
				setEquipoStatus("Equipo no encontrado. Se creará al guardar la orden.", true);
			}
		} catch (error) {
			setEquipoStatus("No se pudo verificar el equipo.", true);
		}
	}

	function setEquipoStatus(message, isError = false) {
		if (!equipoStatus) return;
		equipoStatus.textContent = message;
		equipoStatus.classList.toggle("is-error", isError);
	}

	async function registrarClienteDesdeFormulario() {
		try {
			const payload = obtenerClientePayload();
			if (!payload.cedula || !payload.nombre || !payload.apellido || !payload.celular) {
				setClienteStatus("Cédula, nombre, apellido y celular son obligatorios.", true);
				return;
			}
			
			// Validar celular (solo números, exactamente 11)
			if (!/^\d{11}$/.test(payload.celular)) {
				setClienteStatus("El celular debe tener exactamente 11 dígitos.", true);
				return;
			}
			
			// Validar email si se proporciona
			if (payload.correo && !isValidEmail(payload.correo)) {
				setClienteStatus("El correo electrónico no es válido.", true);
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

		// Validar IMEI
		const idEquipo = getFieldValue("orden-id-equipo");
		if (!idEquipo) {
			mostrarToast("El IMEI del equipo es obligatorio.", true);
			return;
		}
		if (!/^\d+$/.test(idEquipo)) {
			mostrarToast("El IMEI solo puede contener números.", true);
			return;
		}
		if (idEquipo.length !== 15) {
			mostrarToast("El IMEI debe tener exactamente 15 caracteres.", true);
			return;
		}

		// Validar fecha (el input type date con min previene fechas pasadas)
		const fechaIngreso = inputFecha?.value;
		if (!fechaIngreso) {
			mostrarToast("La fecha de ingreso es obligatoria.", true);
			return;
		}

		// Validar modelo (debe haber uno del dropdown O uno personalizado, no ambos vacíos)
		const idModelo = selectModelo?.value;
		const modeloCustom = getFieldValue("orden-modelo-custom");
		if (!idModelo && !modeloCustom) {
			mostrarToast("Debes seleccionar un modelo o escribir uno personalizado.", true);
			return;
		}

		// Validar que modelo personalizado no pase 30 caracteres
		if (modeloCustom && modeloCustom.length > 30) {
			mostrarToast("El modelo personalizado no puede exceder 30 caracteres.", true);
			return;
		}

		// Validar patrón si se proporciona
		const patron = getFieldValue("orden-patron");
		if (patron) {
			const patronClean = patron.replace(/-/g, "");
			if (!/^[1-9]+$/.test(patronClean)) {
				mostrarToast("El patrón solo puede contener números del 1 al 9.", true);
				return;
			}
			if (patronClean.length !== new Set(patronClean).size) {
				mostrarToast("El patrón no puede contener números repetidos.", true);
				return;
			}
			if (patronClean.length > 9) {
				mostrarToast("El patrón no puede tener más de 9 números.", true);
				return;
			}
		}

		// Validar clave (máximo 30 caracteres)
		const clave = getFieldValue("orden-clave");
		if (clave && clave.length > 30) {
			mostrarToast("La clave no puede exceder 30 caracteres.", true);
			return;
		}

		// Validar descripción (máximo 100 caracteres)
		const descripcion = getFieldValue("orden-descripcion");
		if (!descripcion) {
			mostrarToast("La descripción del problema es obligatoria.", true);
			return;
		}
		if (descripcion.length > 100) {
			mostrarToast("La descripción no puede exceder 100 caracteres.", true);
			return;
		}

		// Validar nota (máximo 50 caracteres)
		const nota = getFieldValue("orden-nota");
		if (nota && nota.length > 50) {
			mostrarToast("Las notas no pueden exceder 50 caracteres.", true);
			return;
		}

		// Validar correo si se proporciona
		const correo = getFieldValue("cliente-correo");
		if (correo && !isValidEmail(correo)) {
			mostrarToast("El correo electrónico no es válido.", true);
			return;
		}

		// Validar celular
		const celular = getFieldValue("cliente-celular");
		if (celular && !/^\d{11}$/.test(celular)) {
			mostrarToast("El celular debe tener exactamente 11 dígitos.", true);
			return;
		}

		// Validar cédula (8 caracteres, solo números)
		const cedula = getFieldValue("cliente-cedula");
		if (!cedula) {
			mostrarToast("La cédula del cliente es obligatoria.", true);
			return;
		}
		if (!/^\d{8}$/.test(cedula)) {
			mostrarToast("La cédula debe tener exactamente 8 dígitos numéricos.", true);
			return;
		}

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
			id_equipo: idEquipo,
			id_modelo: idModelo || null,
			modelo_custom: modeloCustom || null,
			fecha_ingreso: fechaIngreso,
			patron: patron,
			clave: clave,
			color: getFieldValue("orden-color"),
			capacidad: getFieldValue("orden-capacidad"),
			descripcion: descripcion,
			nota: nota,
		};

		try {
			await fetchJson("/api/ordenes-servicio", {
				method: "POST",
				body: JSON.stringify(payload),
			});
			mostrarToast("Orden creada correctamente.");
			formOrden.reset();
			if (window.UiModal && typeof window.UiModal.closeById === "function") {
				window.UiModal.closeById("modal-nueva-orden");
			}
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

	function bindEstadoCards() {
		estadoCards.forEach((card) => {
			const estado = card.dataset.estadoCard;
			if (!estado) return;
			card.addEventListener("click", () => onEstadoCardClick(estado));
			card.addEventListener("keydown", (event) => {
				if (event.key === "Enter" || event.key === " ") {
					event.preventDefault();
					onEstadoCardClick(estado);
				}
			});
		});
	}

	async function onEstadoCardClick(estado) {
		const label = {
			pendiente: "Pendientes",
			asignada: "Asignadas",
			revisada: "Revisadas",
			reparada: "Reparadas",
		}[estado] || "Órdenes";
		const estadoParam = {
			pendiente: "Pendiente",
			asignada: "Asignado",
			revisada: "Revisado",
			reparada: "Reparado",
		}[estado] || estado;
		try {
			const data = await fetchJson(`/api/ordenes-servicio/ordenes?estado=${encodeURIComponent(estadoParam)}`);
			renderModalOrdenesEstado(label, data.ordenes || []);
			if (window.UiModal && typeof window.UiModal.openById === "function") {
				window.UiModal.openById("modal-ordenes-estado");
			}
		} catch (error) {
			console.error(`Error cargando órdenes ${estado}`, error);
			if (modalOrdenesEstadoSubtitle) {
				modalOrdenesEstadoSubtitle.textContent = "No se pudo cargar la información.";
			}
		}
	}

	function renderModalOrdenesEstado(label, ordenesEstado) {
		if (modalOrdenesEstadoSubtitle) {
			modalOrdenesEstadoSubtitle.textContent = `Órdenes ${label}`;
		}
		if (!tablaOrdenesEstadoBody) return;
		// Filtrar órdenes excluyendo "En Proceso"
		const ordenesFiltradas = ordenesEstado.filter((o) => String(o.Estado || "").toLowerCase() !== "en proceso");
		if (!ordenesFiltradas.length) {
			tablaOrdenesEstadoBody.innerHTML = '<tr><td colspan="8">No hay órdenes en esta categoría.</td></tr>';
			return;
		}
		tablaOrdenesEstadoBody.innerHTML = ordenesFiltradas.map((orden) => {
			const clienteNombre = `${orden.Nombre_cliente ?? ""} ${orden.Apellido_cliente ?? ""}`.trim();
			const badgeClass = getEstadoBadgeClass(orden.Estado);
			return `
				<tr>
					<td>${escapeHtml(orden.ID_orden)}</td>
					<td><span class="badge ${badgeClass}">${escapeHtml(orden.Estado ?? "")}</span></td>
					<td>${escapeHtml(clienteNombre)}</td>
					<td>${escapeHtml(orden.Equipo ?? "")}</td>
					<td>${escapeHtml(orden.Modelo ?? "")}</td>
					<td>${escapeHtml(orden.Des_cliente ?? "")}</td>
					<td>${escapeHtml(formatFecha(getFechaOrden(orden)))}</td>
					<td class="table__actions">
						<button type="button" class="icon-action icon-action--view" data-action="ver-detalle" data-id="${escapeHtml(orden.ID_orden)}" title="Ver detalles">${Iconos.ojo}</button>
					</td>
				</tr>`;
		}).join("");
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
		// Filtrar órdenes excluyendo "En Proceso" que es exclusivo de taller
		const ordenesFiltradas = ordenes.filter((o) => String(o.Estado || "").toLowerCase() !== "en proceso");
		if (!ordenesFiltradas.length) {
			tablaOrdenes.innerHTML = '<tr><td colspan="8">No hay órdenes registradas.</td></tr>';
			return;
		}

		tablaOrdenes.innerHTML = ordenesFiltradas.map((orden) => {
			const clienteNombre = `${orden.Nombre_cliente ?? ""} ${orden.Apellido_cliente ?? ""}`.trim();
			const badgeClass = getEstadoBadgeClass(orden.Estado);
			return `
				<tr>
					<td>${escapeHtml(orden.ID_orden)}</td>
					<td><span class="badge ${badgeClass}">${escapeHtml(orden.Estado)}</span></td>
					<td>${escapeHtml(clienteNombre)}</td>
					<td>${escapeHtml(orden.Equipo ?? "")}</td>
					<td>${escapeHtml(orden.Modelo ?? "")}</td>
					<td>${escapeHtml(orden.Des_cliente ?? "")}</td>
					<td>${escapeHtml(formatFecha(getFechaOrden(orden)))}</td>
					<td class="table__actions">
						<div class="row-actions">
							<button type="button" class="icon-action icon-action--view" data-action="ver-detalle" data-id="${escapeHtml(orden.ID_orden)}" title="Ver detalles">${Iconos.ojo}</button>
							<button type="button" class="icon-action icon-action--primary" data-action="seleccionar-asignacion" data-id="${escapeHtml(orden.ID_orden)}" title="Asignar técnico">${Iconos.asignar}</button>
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
		const reparadas = count("reparado");
		if (statPendientes) statPendientes.textContent = String(pendientes);
		if (statAsignadas) statAsignadas.textContent = String(asignadas);
		if (statRevisadas) statRevisadas.textContent = String(revisadas);
		if (document.getElementById("stat-reparadas")) {
			document.getElementById("stat-reparadas").textContent = String(reparadas);
		}
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
		const html = `
			<div class="device-detail__grid">
				${items
					.filter(([, value]) => value !== "")
					.map(([label, value]) => `
						<div class="detail-item">
							<span class="device-detail__label">${escapeHtml(label)}</span>
							<span class="device-detail__value">${escapeHtml(value)}</span>
						</div>
					`)
					.join("")}
			</div>`;
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

		const rows = `
			<div class="device-detail__grid">
				${roles.map((rol) => {
					const nombres = rol.acciones
						.flatMap((accion) => responsables[accion] || [])
						.filter(Boolean);
					return `
						<div class="detail-item">
							<span class="device-detail__label">${escapeHtml(rol.label)}</span>
							<span class="device-detail__value">${escapeHtml(nombres.length ? nombres.join(", ") : "Sin registro")}</span>
						</div>
					`;
				}).join("")}
			</div>`;
		detalleResponsables.innerHTML = rows;
	}

	function renderFotos(fotos) {
		if (!detalleFotos) return;
		if (!fotos.length) {
			detalleFotos.innerHTML = "<p>No hay fotos registradas.</p>";
			return;
		}
		detalleFotos.innerHTML = `
			<h3>Fotos</h3>
			<div class="device-photos">
				${fotos.map((foto) => {
					let src = foto.Foto_e || foto.foto || foto.url || "";
					if (src && !src.startsWith("/") && !src.startsWith("http")) {
						src = `/${src}`;
					}
					return `
						<div class="img-wrap">
							<img src="${escapeHtml(src)}" alt="Evidencia">
						</div>`;
				}).join("")}
			</div>`;
	}

	function renderTests(tests) {
		if (!detalleTests) return;
		if (!tests.length) {
			detalleTests.innerHTML = "<p>No hay tests registrados.</p>";
			return;
		}
		detalleTests.innerHTML = `
			<h3>Historial de revisiones</h3>
			<div class="table-wrap">
				<table class="table">
					<thead>
						<tr>
							<th>Fecha</th>
							<th>Número</th>
							<th>Observaciones</th>
							<th>Costo</th>
						</tr>
					</thead>
					<tbody>
						${tests.map((test) => `
							<tr>
								<td>${escapeHtml(formatFecha(test.Fecha_e ?? test.Fecha ?? ""))}</td>
								<td>${escapeHtml(test.Num_test ?? "")}</td>
								<td>${escapeHtml(test.Observaciones ?? "")}</td>
								<td>${escapeHtml(test.Costo_reparacion ?? "0")}</td>
							</tr>
						`).join("")}
					</tbody>
				</table>
			</div>
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
			// Buscamos el elemento por nombre exacto (PascalCase)
			const el = formRevision?.querySelector(`[name="${campo}"]`);
			if (el && el.type === "checkbox") {
				payload[campo] = el.checked ? 1 : 0;
			} else {
				// Si no existe en el DOM, enviamos 0 para evitar NULLs inesperados
				payload[campo] = 0;
			}
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
		const authToken = getAuthToken();
		try {
			const response = await fetch(`/api/taller/ordenes/${encodeURIComponent(idOrden)}/fotos`, {
				method: "POST",
				body: formData,
				headers: {
					...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
					...(authToken ? { "Authorization": `Bearer ${authToken}` } : {}),
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

	function isValidEmail(email) {
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		return emailRegex.test(email);
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

	function getEstadoBadgeClass(estado) {
		const estadoLower = String(estado ?? "").toLowerCase().trim();
		if (estadoLower.includes("pendient")) {
			return "badge--pendiente";
		}
		if (estadoLower.includes("asign")) {
			return "badge--asignada";
		}
		if (estadoLower.includes("revis")) {
			return "badge--revisada";
		}
		if (estadoLower.includes("repar")) {
			return "badge--reparada";
		}
		return "badge--pendiente";
	}
});
