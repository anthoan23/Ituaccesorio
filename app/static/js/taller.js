document.addEventListener("DOMContentLoaded", () => {
	const viewButtons = Array.from(document.querySelectorAll("[data-view-target]"));
	const viewPanels = Array.from(document.querySelectorAll(".content.vista-1, .content.vista-2, .content.vista-3, .content.vista-4"));
	const tablaOrdenes = document.getElementById("tabla-ordenes-servicio");
	const paginasOrdenes = document.querySelector(".pager__pages");
	const detalleDispositivo = document.getElementById("detalle-dispositivo");
	const detalleOrdenSubtitle = document.getElementById("detalle-orden-subtitle");
	const orderInfo = document.getElementById('order-info');
	const orderPhotos = document.getElementById('order-photos');
	const orderTests = document.getElementById('order-tests');
	const csrfToken = document.querySelector("input[name='_csrf_token']")?.value || "";
	let ordenesCargadas = [];

	if (!viewButtons.length || !viewPanels.length) {
		return;
	}

	const escapeHtml = (value) => String(value ?? "")
		.replaceAll("&", "&amp;")
		.replaceAll("<", "&lt;")
		.replaceAll(">", "&gt;")
		.replaceAll('"', "&quot;")
		.replaceAll("'", "&#39;");

	const formatFecha = (value) => {
		if (!value) {
			return "";
		}

		const fecha = new Date(value);
		if (Number.isNaN(fecha.getTime())) {
			return value;
		}

		return fecha.toLocaleDateString("es-ES");
	};

	const labelPorCampo = {
		ID_orden: "ID orden",
		Estado: "Estado",
		Modelo: "Modelo",
		Des_cliente: "Descripción cliente",
		Fecha_e: "Fecha ingreso",
	};

	const renderDetalleOrden = (orden, accion) => {
		if (!orderInfo) return;

		if (!orden || typeof orden !== 'object') {
			orderInfo.innerHTML = '<p class="device-detail__empty">Todavía no has seleccionado ninguna orden.</p>';
			if (detalleOrdenSubtitle) detalleOrdenSubtitle.textContent = 'Selecciona una orden para ver toda su información.';
			return;
		}

		const entries = Object.entries(orden)
			.filter(([_, value]) => value !== null && value !== undefined && value !== '')
			.map(([key, value]) => {
				const label = labelPorCampo[key] ?? key.replaceAll('_', ' ');
				const displayValue = key === 'Fecha_e' ? formatFecha(value) : value;
				return `
					<div class="device-detail__item">
						<span class="device-detail__label">${escapeHtml(label)}</span>
						<strong class="device-detail__value">${escapeHtml(displayValue)}</strong>
					</div>`;
			});

		orderInfo.innerHTML = entries.join('');
		if (detalleOrdenSubtitle) detalleOrdenSubtitle.textContent = `Información completa de la orden ${orden.ID_orden} (${accion}).`;
	};

	const renderOrdenes = (ordenes) => {
		if (!tablaOrdenes) {
			return;
		}

		ordenesCargadas = Array.isArray(ordenes) ? ordenes : [];

		if (!Array.isArray(ordenes) || ordenes.length === 0) {
			tablaOrdenes.innerHTML = '<tr><td colspan="6">No hay órdenes registradas.</td></tr>';
			if (paginasOrdenes) {
				paginasOrdenes.textContent = "0";
			}
			return;
		}

		tablaOrdenes.innerHTML = ordenes.map((orden) => `
			<tr>
				<td>${escapeHtml(orden.ID_orden)}</td>
				<td>${escapeHtml(orden.Estado)}</td>
				<td>${escapeHtml(orden.Modelo)}</td>
				<td>${escapeHtml(orden.Des_cliente)}</td>
				<td>${escapeHtml(formatFecha(orden.Fecha_e))}</td>
				<td class="table__actions">
					<div class="row-actions">
						<button type="button" class="table-action" data-accion="ver" data-id="${escapeHtml(orden.ID_orden)}">Ver</button>
						<button type="button" class="table-action" data-accion="revisar" data-id="${escapeHtml(orden.ID_orden)}">Revisar</button>
						<button type="button" class="table-action table-action--accent" data-accion="reparar" data-id="${escapeHtml(orden.ID_orden)}">Reparar</button>
					</div>
				</td>
			</tr>
		`).join("");

		if (paginasOrdenes) {
			paginasOrdenes.textContent = String(ordenes.length);
		}
	};

	const manejarAccionOrden = (accion, idOrden) => {
		if (accion === "ver") {
			cargarDetalleOrden(idOrden);
			return;
		}

		const ordenSeleccionada = ordenesCargadas.find((orden) => String(orden.ID_orden) === String(idOrden));
		if (!ordenSeleccionada) {
			console.log("No se encontró la orden seleccionada", idOrden);
			return;
		}

		if (accion === "revisar") {
			renderDetalleOrden(ordenSeleccionada, accion);
			activateView("vista-3");
			return;
		}

		if (accion === "reparar") {
			renderDetalleOrden(ordenSeleccionada, accion);
			activateView("vista-2");
			return;
		}

		console.log("Acción no reconocida para la orden", idOrden);
	};

	const cargarOrdenes = async () => {
		try {
			const response = await fetch("/api/taller/ordenes", { cache: "no-store" });
			if (!response.ok) {
				throw new Error(`HTTP ${response.status}`);
			}

			const data = await response.json();
			renderOrdenes(Array.isArray(data) ? data : data.ordenes);
		} catch (error) {
			console.error("Error cargando órdenes del taller:", error);
			if (tablaOrdenes) {
				tablaOrdenes.innerHTML = '<tr><td colspan="4">No se pudieron cargar las órdenes.</td></tr>';
			}
		}
	};

	const cargarDetalleOrden = async (idOrden) => {
		try {
			const getAuthToken = () => {
				const fromLocal = window.localStorage ? window.localStorage.getItem('access_token') : '';
				if (fromLocal) return fromLocal;
				const fromSession = window.sessionStorage ? window.sessionStorage.getItem('access_token') : '';
				if (fromSession) return fromSession;
				return '';
			};

			const authToken = getAuthToken();

			console.log('cargarDetalleOrden: llamando endpoint detalle, authToken present?', !!authToken);
			const response = await fetch(`/api/taller/ordenes/${encodeURIComponent(idOrden)}`, {
				method: 'POST',
				cache: 'no-store',
				headers: {
					'Content-Type': 'application/json',
					...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
					...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {}),
				},
				credentials: 'same-origin',
			});
			if (!response.ok) throw new Error(`HTTP ${response.status}`);
			const data = await response.json();

			// detalle_orden: objeto, fotos_orden: array, test_orden: array
			const detalle = data.detalle_orden || data.detalle || {};
			const fotos = Array.isArray(data.fotos_orden) ? data.fotos_orden : (Array.isArray(data.fotos) ? data.fotos : []);
			const tests = Array.isArray(data.test_orden) ? data.test_orden : (Array.isArray(data.test_orden) ? data.test_orden : []);

			// Render principal (todos los campos de detalle)
			renderDetalleOrden(detalle, 'ver');

			// Render fotos en contenedor específico
			if (orderPhotos) {
				if (!fotos || fotos.length === 0) {
					orderPhotos.innerHTML = '<p class="device-detail__empty">No hay fotos de esta orden.</p>';
				} else {
					orderPhotos.innerHTML = '<h3>Fotos</h3><div class="device-photos">' + fotos.map((f) => {
						const src = f.Foto_e || f.foto || f.url || f.path || f.ruta || '';
						if (src && (src.endsWith('.jpg') || src.endsWith('.png') || src.endsWith('.jpeg') || src.endsWith('.gif'))) {
							return `<div class="device-photo"><img src="${escapeHtml(src)}" alt="Foto orden"/></div>`;
						}
						return `<div class="device-photo"><a href="${escapeHtml(src)}" target="_blank">${escapeHtml(src)}</a></div>`;
					}).join('') + '</div>';
				}
			}

			// Render tabla de tests
			if (orderTests) {
				if (!tests || tests.length === 0) {
					orderTests.innerHTML = '<p class="device-detail__empty">No hay tests relacionados.</p>';
				} else {
					const testsTable = `
						<table class="table">
							<thead>
								<tr>
									<th>ID test</th>
									<th>Número</th>
									<th>Observaciones</th>
									<th class="table__actions">Acciones</th>
								</tr>
							</thead>
							<tbody>
							${tests.map((t) => `
								<tr>
									<td>${escapeHtml(t.ID_test ?? t.ID_test)}</td>
									<td>${escapeHtml(t.Num_test ?? t.Num_test)}</td>
									<td>${escapeHtml(t.Observaciones ?? t.Observaciones ?? '')}</td>
									<td class="table__actions"><button type="button" class="table-action" data-test-id="${escapeHtml(t.ID_test)}">Ver detalle</button></td>
								</tr>
							`).join('')}
							</tbody>
						</table>`;
					orderTests.innerHTML = `<h3>Tests</h3>${testsTable}`;

					// delegation listener for test detail buttons
					orderTests.addEventListener('click', (e) => {
						const btn = e.target.closest('button[data-test-id]');
						if (!btn) return;
						const testId = btn.getAttribute('data-test-id');
						const testObj = tests.find((x) => String(x.ID_test) === String(testId));
						if (!testObj) return;
						const modalBody = document.getElementById('modal-test-body');
						if (modalBody) {
							modalBody.innerHTML = Object.entries(testObj).map(([k, v]) => `
								<div style="margin-bottom:.5rem;"><strong>${escapeHtml(k)}:</strong> ${escapeHtml(v)}</div>
							`).join('');
						}
						if (window.UiModal && typeof window.UiModal.openById === 'function') {
							window.UiModal.openById('modal-test-detail');
						}
					});
				}
			}

			// show view
			activateView('vista-2');
		} catch (error) {
			console.error('Error cargando detalle de orden:', error);
			if (detalleDispositivo) {
				detalleDispositivo.innerHTML = '<p class="device-detail__empty">No se pudo cargar el detalle de la orden.</p>';
			}
		}
	};

	const activateView = (targetClass) => {
		viewPanels.forEach((panel) => {
			panel.hidden = !panel.classList.contains(targetClass);
		});

		viewButtons.forEach((button) => {
			const isActive = button.dataset.viewTarget === targetClass;
			button.classList.toggle("is-active", isActive);
			button.setAttribute("aria-pressed", String(isActive));
		});
	};

	viewButtons.forEach((button) => {
		button.addEventListener("click", () => {
			activateView(button.dataset.viewTarget);
		});
	});

	if (tablaOrdenes) {
		tablaOrdenes.addEventListener("click", (event) => {
			const button = event.target.closest("button[data-accion]");
			if (!button) {
				return;
			}

			manejarAccionOrden(button.dataset.accion, button.dataset.id);
		});
	}

	activateView("vista-1");
	cargarOrdenes();
});
