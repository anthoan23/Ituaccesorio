document.addEventListener("DOMContentLoaded", () => {
	const viewButtons = Array.from(document.querySelectorAll("[data-view-target]"));
		const viewPanels = Array.from(document.querySelectorAll(".content.vista-1, .content.vista-2, .content.vista-3, .content.vista-4, .content.vista-5"));
	const tablaOrdenes = document.getElementById("tabla-ordenes-servicio");
	const tablaReparacionesAsignadas = document.getElementById("tabla-reparaciones-asignadas");
	const paginasOrdenes = document.querySelector(".pager__pages");
	const detalleDispositivo = document.getElementById("detalle-dispositivo");
	const detalleOrdenSubtitle = document.getElementById("detalle-orden-subtitle");
	const breadcrumbSection = document.getElementById("breadcrumb-section");
	const breadcrumbSeparator = document.getElementById("breadcrumb-separator");
	const orderInfo = document.getElementById('order-info');
	const orderPhotos = document.getElementById('order-photos');
	const orderTests = document.getElementById('order-tests');
	const orderPeople = document.getElementById('order-people');
	const modalFotosBody = document.getElementById('modal-fotos-body');
	const modalPhotoBody = document.getElementById('modal-photo-view-body');
	const modalPhotoImg = document.getElementById('modal-photo-view-img');
	const fotosDropzone = document.getElementById('fotos-dropzone');
	const formFotosOrden = document.getElementById('form-fotos-orden');
	const inputFotosOrden = document.getElementById('input-fotos-orden');
	const modalFotosIdOrden = document.getElementById('modal-fotos-id-orden');
	const btnConfirmDeletePhoto = document.getElementById('btn-confirm-delete-photo');
	const btnConfirmDeleteSavedPhoto = document.getElementById('btn-confirm-delete-saved-photo');
	const csrfToken = document.querySelector("input[name='_csrf_token']")?.value || "";
	let ordenesCargadas = [];
	let fotosOrdenActual = [];
	let fotosSeleccionadas = [];
	let fotoIndexPendienteEliminar = null;
	let fotoGuardadaPendienteEliminar = null;
	let ordenActualId = '';

	if (!viewButtons.length || !viewPanels.length) {
		return;
	}

	const escapeHtml = (value) => String(value ?? "")
		.replaceAll("&", "&amp;")
		.replaceAll("<", "&lt;")
		.replaceAll(">", "&gt;")
		.replaceAll('"', "&quot;")
		.replaceAll("'", "&#39;");

	const normalizarRutaFoto = (valor) => {
		if (!valor) return '';
		try {
			return new URL(String(valor), window.location.origin).pathname;
		} catch (_) {
			return String(valor);
		}
	};

	const resolverIdFotoGuardada = (target) => {
		const wrapper = target.closest('[data-foto-path]');
		const rutaObjetivo = normalizarRutaFoto(wrapper?.getAttribute('data-foto-path') || target.getAttribute('data-foto-path') || '');
		if (rutaObjetivo) {
			const encontrada = fotosOrdenActual.find((foto) => {
				const rutaFoto = normalizarRutaFoto(foto.Foto_e || foto.foto || foto.url || foto.path || foto.ruta || '');
				return rutaFoto === rutaObjetivo;
			});

			const idEncontrado = Number(encontrada?.ID_evidencia_e || encontrada?.ID_evidencia || encontrada?.id || encontrada?.ID);
			if (Number.isFinite(idEncontrado) && idEncontrado > 0) {
				return idEncontrado;
			}
		}

		const idAttr = target.getAttribute('data-remove-saved-photo');
		const idNumerico = Number(idAttr);
		return Number.isFinite(idNumerico) && idNumerico > 0 ? idNumerico : null;
	};

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

		// Helper para obtener campos con varios posibles nombres
		const getField = (...keys) => {
			for (const k of keys) {
				if (k in orden && orden[k] !== null && orden[k] !== undefined && String(orden[k]).trim() !== '') {
					return orden[k];
				}
			}
			return '';
		};

		const id = getField('ID_orden', 'ID_orden_e', 'ID');
		const fecha = getField('Fecha_e', 'Fecha', 'Fecha_ingreso');
		const nombre = getField('Nombre_cliente', 'Nombre_c', 'Nombre', 'ClienteNombre');
		const apellido = getField('Apellido_cliente', 'Apellido_c', 'Apellido', 'ClienteApellido');
		const modelo = getField('Modelo', 'N_modelo', 'Modelo_producto');
		const patron = getField('Patron', 'Patrón', 'Patron_o');
		const clave = getField('Clave', 'Clave_o', 'Clave_acc');
		const descripcion = getField('Des_cliente', 'Descripcion', 'Descripcion_cliente');
		const nota = getField('Nota', 'Observaciones', 'Nota_o');

		const parts = [];
		parts.push(`
			<div class="device-detail__item">
				<span class="device-detail__label">ID orden</span>
				<strong class="device-detail__value">${escapeHtml(id)}</strong>
			</div>`);

		parts.push(`
			<div class="device-detail__item">
				<span class="device-detail__label">Fecha de ingreso</span>
				<strong class="device-detail__value">${escapeHtml(fecha ? formatFecha(fecha) : '')}</strong>
			</div>`);

		parts.push(`
			<div class="device-detail__item">
				<span class="device-detail__label">Nombre cliente</span>
				<strong class="device-detail__value">${escapeHtml(((nombre || '') + ' ' + (apellido || '')).trim())}</strong>
			</div>`);

		parts.push(`
			<div class="device-detail__item">
				<span class="device-detail__label">Modelo</span>
				<strong class="device-detail__value">${escapeHtml(modelo)}</strong>
			</div>`);

		parts.push(`
			<div class="device-detail__item">
				<span class="device-detail__label">Patrón</span>
				<strong class="device-detail__value">${escapeHtml(patron)}</strong>
			</div>`);

		parts.push(`
			<div class="device-detail__item">
				<span class="device-detail__label">Clave</span>
				<strong class="device-detail__value">${escapeHtml(clave)}</strong>
			</div>`);

		parts.push(`
			<div class="device-detail__item">
				<span class="device-detail__label">Descripción cliente</span>
				<strong class="device-detail__value">${escapeHtml(descripcion)}</strong>
			</div>`);

		parts.push(`
			<div class="device-detail__item">
				<span class="device-detail__label">Nota</span>
				<strong class="device-detail__value">${escapeHtml(nota)}</strong>
			</div>`);

		orderInfo.innerHTML = parts.join('');
		if (detalleOrdenSubtitle) detalleOrdenSubtitle.textContent = `Información de la orden ${id} (${accion}).`;
	};

	const renderOrdenes = (ordenes) => {
		if (!tablaOrdenes) {
			return;
		}

		ordenesCargadas = Array.isArray(ordenes) ? ordenes : [];

		if (!Array.isArray(ordenes) || ordenes.length === 0) {
			tablaOrdenes.innerHTML = '<tr><td colspan="8">No hay órdenes registradas.</td></tr>';
			if (paginasOrdenes) {
				paginasOrdenes.textContent = "0";
			}
			return;
		}

		tablaOrdenes.innerHTML = ordenes.map((orden) => `
			<tr>
				<td>${escapeHtml(orden.ID_orden)}</td>
				<td>${escapeHtml(orden.Estado)}</td>
				<td>${escapeHtml(orden.ID_c ?? orden.ID_cliente ?? '')}</td>
				<td>${escapeHtml(((orden.Nombre_cliente ?? orden.Nombre_c ?? '') + ' ' + (orden.Apellido_cliente ?? orden.Apellido_c ?? '')).trim())}</td>
				<td>${escapeHtml(orden.Modelo ?? orden.N_modelo ?? '')}</td>
				<td>${escapeHtml(orden.Des_cliente)}</td>
				<td>${escapeHtml(formatFecha(orden.Fecha_e))}</td>
				<td class="table__actions">
					<div class="row-actions">
						<button type="button" class="table-action" data-accion="ver" data-id="${escapeHtml(orden.ID_orden)}">Ver</button>
						<button type="button" class="table-action" data-accion="tomar" data-id="${escapeHtml(orden.ID_orden)}">Tomar orden</button>
					</div>
				</td>
			</tr>
		`).join("");

			if (paginasOrdenes) {
			paginasOrdenes.textContent = String(ordenes.length);
		}
	};

		const renderReparacionesAsignadas = (ordenes) => {
			if (!tablaReparacionesAsignadas) {
				return;
			}

			if (!Array.isArray(ordenes) || ordenes.length === 0) {
				tablaReparacionesAsignadas.innerHTML = '<tr><td colspan="3">Sin reparaciones asignadas por ahora.</td></tr>';
				return;
			}

			tablaReparacionesAsignadas.innerHTML = ordenes.map((orden) => `
				<tr>
					<td>${escapeHtml(orden.ID_orden)}</td>
					<td>${escapeHtml(orden.N_modelo ?? orden.Modelo ?? '')}</td>
					<td class="table__actions">
						<div class="row-actions">
							<button type="button" class="table-action" data-accion="ver" data-id="${escapeHtml(orden.ID_orden)}">Ver</button>
							<button type="button" class="table-action" data-accion="revisar" data-id="${escapeHtml(orden.ID_orden)}">Revisar</button>
							<button type="button" class="table-action table-action--accent" data-accion="reparar" data-id="${escapeHtml(orden.ID_orden)}">Reparar</button>
							<button type="button" class="table-action table-action--danger" data-accion="liberar" data-id="${escapeHtml(orden.ID_orden)}">Liberar</button>
						</div>
					</td>
				</tr>
			`).join("");
		};

	const tomarOrden = async (idOrden) => {
		try {
			const response = await fetch(`/api/taller/asignar/${encodeURIComponent(idOrden)}/1004/estado`, {
				method: "POST",
				cache: "no-store",
				headers: {
					...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
				},
				credentials: "same-origin",
			});

			if (!response.ok) {
				throw new Error(`HTTP ${response.status}`);
			}

			await cargarOrdenes();
			await cargarReparacionesAsignadas();
			await cargarDetalleOrden(idOrden, "vista-5");
		} catch (error) {
			console.error("Error tomando la orden:", error);
		}
	};

	const liberarOrden = async (idOrden) => {
		try {
			const response = await fetch(`/api/taller/liberar/${encodeURIComponent(idOrden)}/1004/estado`, {
				method: "POST",
				cache: "no-store",
				headers: {
					...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
				},
				credentials: "same-origin",
			});

			if (!response.ok) {
				throw new Error(`HTTP ${response.status}`);
			}

			await cargarOrdenes();
			await cargarReparacionesAsignadas();			
		} catch (error) {
			console.error("Error liberando la orden:", error);
		}
	};

	const manejarAccionOrden = (accion, idOrden) => {
		if (accion === "ver") {
			cargarDetalleOrden(idOrden);
			return;
		}

		const ordenSeleccionada = ordenesCargadas.find((orden) => String(orden.ID_orden) === String(idOrden));
		if (!ordenSeleccionada) {
			return;
		}

		if (accion === "tomar" || accion === "revisar") {
			tomarOrden(idOrden);
			return;
		}

		if (accion === "reparar") {
			renderDetalleOrden(ordenSeleccionada, accion);
			activateView("vista-4");
			return;
		}

		return;
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

	const cargarReparacionesAsignadas = async () => {
		if (!tablaReparacionesAsignadas) {
			return;
		}

		try {
			const response = await fetch("/api/taller/reparaciones-asignadas", { cache: "no-store" });
			if (!response.ok) {
				throw new Error(`HTTP ${response.status}`);
			}

			const data = await response.json();
			renderReparacionesAsignadas(Array.isArray(data) ? data : data.ordenes);
		} catch (error) {
			console.error("Error cargando reparaciones asignadas:", error);
			tablaReparacionesAsignadas.innerHTML = '<tr><td colspan="3">No se pudieron cargar las reparaciones asignadas.</td></tr>';
		}
	};

	const cargarDetalleOrden = async (idOrden, desiredView = 'vista-2') => {
		try {
			const getAuthToken = () => {
				const fromLocal = window.localStorage ? window.localStorage.getItem('access_token') : '';
				if (fromLocal) return fromLocal;
				const fromSession = window.sessionStorage ? window.sessionStorage.getItem('access_token') : '';
				if (fromSession) return fromSession;
				return '';
			};

			const authToken = getAuthToken();

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
			fotosOrdenActual = fotos;
			ordenActualId = detalle.ID_orden || idOrden;
			if (modalFotosIdOrden) {
				modalFotosIdOrden.value = String(ordenActualId || '');
			}

			// Render principal (todos los campos de detalle)
			renderDetalleOrden(detalle, 'ver');

			// Render fotos en contenedor específico
			if (orderPhotos) {
				if (!fotos || fotos.length === 0) {
					orderPhotos.innerHTML = '<p class="device-detail__empty">No hay fotos de esta orden.</p>';
				} else {
					orderPhotos.innerHTML = '<h3>Fotos</h3><div class="device-photos">' + fotos.map((f, index) => {
						const src = f.Foto_e || f.foto || f.url || f.path || f.ruta || '';
						const idFoto = f.ID_evidencia_e || f.ID_evidencia || f.id || f.ID || index;
						const titulo = f.Nombre || f.nombre || f.Nombre_e || `Foto ${index + 1}`;
						return `
								<div class="img-wrap" data-saved-photo-id="${escapeHtml(idFoto)}" data-foto-path="${escapeHtml(src)}">
								<img class="order-photo order-photo--saved" data-saved-photo-id="${escapeHtml(idFoto)}" src="${escapeHtml(src)}" alt="${escapeHtml(titulo)}"/>
									<button type="button" class="device-photo__remove" data-remove-saved-photo="${escapeHtml(idFoto)}" data-foto-path="${escapeHtml(src)}" aria-label="Eliminar ${escapeHtml(titulo)}">×</button>
							</div>
						`;
					}).join('') + '</div>';
				}
			}

			if (modalFotosBody) {
				modalFotosBody.innerHTML = '<p class="device-detail__empty">Selecciona una o más imágenes para ver aquí solo la vista previa de las nuevas fotos.</p>';
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

			// Render revisión / reparación / costo debajo de tests
			if (orderPeople) {
				// Normaliza cadenas para buscar claves con/ sin acentos, guiones, espacios y mayúsculas
				const normalize = (s) => String(s || '').toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '').replace(/[_\s-]/g, '');

				const getVal = (obj, ...keys) => {
					if (!obj) return '';
					// búsqueda directa por claves listadas
					for (const k of keys) {
						if (k in obj && obj[k] !== null && obj[k] !== undefined && String(obj[k]).trim() !== '') return obj[k];
					}
					// fallback: buscar por clave normalizada
					const objKeys = Object.keys(obj);
					for (const k of keys) {
						const nk = normalize(k);
						const found = objKeys.find(ok => normalize(ok) === nk);
						if (found) {
							const v = obj[found];
							if (v !== null && v !== undefined && String(v).trim() !== '') return v;
						}
					}
					return '';
				};

				const revisionVal = getVal(detalle, 'Revision', 'Revision_o', 'Revisión', 'revison', 'revisison');
				const reparacionVal = getVal(detalle, 'Reparacion', 'Reparacion_o', 'Reparación', 'reparaciondesc', 'reparacion_desc');
				const costoVal = getVal(detalle, 'Costo_reparacion', 'Costo', 'Costo_repar', 'Costo reparación');

				if (!revisionVal && !reparacionVal && !costoVal) {
					orderPeople.innerHTML = '<p class="device-detail__empty">No hay información de revisión o reparación.</p>';
				} else {
					orderPeople.innerHTML = `
						${revisionVal ? `<div class="device-detail__item"><span class="device-detail__label">Revisión</span><strong class="device-detail__value">${escapeHtml(revisionVal)}</strong></div>` : ''}
						${reparacionVal ? `<div class="device-detail__item"><span class="device-detail__label">Reparación</span><strong class="device-detail__value">${escapeHtml(reparacionVal)}</strong></div>` : ''}
						${costoVal ? `<div class="device-detail__item"><span class="device-detail__label">Costo de reparación</span><strong class="device-detail__value">${escapeHtml(costoVal)}</strong></div>` : ''}
						<div class="device-detail__actions" style="margin-top:1rem; display:flex; gap:.5rem;">
							<button type="button" class="form-btn form-btn--ghost" data-accion-detail="revisar">Revisar</button>
							<button type="button" class="form-btn form-btn--primary" data-accion-detail="reparar">Reparar</button>
						</div>
					`;
				}
			}
			}

			// show view requested by caller
			activateView(desiredView);
		} catch (error) {
			console.error('Error cargando detalle de orden:', error);
			if (detalleDispositivo) {
				detalleDispositivo.innerHTML = '<p class="device-detail__empty">No se pudo cargar el detalle de la orden.</p>';
			}
		}
	};

	const activateView = (targetClass) => {
		const breadcrumbLabels = {
			'vista-2': 'Informacion de la orden',
			'vista-3': 'Revision',
			'vista-4': 'Reparacion',
			'vista-5': 'Reparaciones asignadas',
		};
		const showBreadcrumbSuffix = ['vista-2', 'vista-3', 'vista-4', 'vista-5'].includes(targetClass);

		viewPanels.forEach((panel) => {
			panel.hidden = !panel.classList.contains(targetClass);
		});

		if (breadcrumbSeparator) {
			breadcrumbSeparator.hidden = !showBreadcrumbSuffix;
		}

		if (breadcrumbSection) {
			breadcrumbSection.hidden = !showBreadcrumbSuffix;
			breadcrumbSection.textContent = showBreadcrumbSuffix ? breadcrumbLabels[targetClass] || '' : '';
		}

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

	if (tablaReparacionesAsignadas) {
		tablaReparacionesAsignadas.addEventListener("click", (event) => {
			const button = event.target.closest("button[data-accion]");
			if (!button) return;

			const accion = button.dataset.accion;
			const id = button.dataset.id;

			if (accion === 'ver') {
				cargarDetalleOrden(id, 'vista-2');
				return;
			}

			if (accion === 'tomar') {
				tomarOrden(id);
				return;
			}

			if (accion === 'revisar') {
				cargarDetalleOrden(id, 'vista-3');
				return;
			}

			if (accion === 'reparar') {
				cargarDetalleOrden(id, 'vista-4');
				return;
			}

			if (accion === 'liberar') {
				liberarOrden(id);
				return;
			}
		});
	}

	// Delegation listener para botones dentro del detalle de orden (Revisar / Reparar)
	if (orderPeople) {
		orderPeople.addEventListener('click', (e) => {
			const btn = e.target.closest('button[data-accion-detail]');
			if (!btn) return;
			const accion = btn.getAttribute('data-accion-detail');
			// obtener id de la orden desde el detalle cargado en pantalla
			const currentId = (window.currentOrderId) ? window.currentOrderId : (document.getElementById('order-info')?.querySelector('.device-detail__value')?.textContent || '');
			if (accion === 'revisar') {
				activateView('vista-3');
				return;
			}
			if (accion === 'reparar') {
				activateView('vista-4');
				return;
			}
		});
	}

	const renderPreviewFotos = (files) => {
		if (!modalFotosBody) return;
		const lista = Array.isArray(files) ? files : Array.from(files || []);
		if (lista.length === 0) {
			modalFotosBody.innerHTML = '<p class="device-detail__empty">Selecciona una o más imágenes para ver la vista previa.</p>';
			return;
		}

		modalFotosBody.innerHTML = `
			<div class="device-photos">
				${lista.map((file, index) => `
					<div class="img-wrap" data-preview-index="${index}">
						<img class="preview-photo" data-preview-index="${index}" data-remove-photo="${index}" alt="${escapeHtml(file.name)}" />
						<button type="button" class="device-photo__remove" data-remove-photo="${index}" aria-label="Eliminar ${escapeHtml(file.name)}">×</button>
					</div>
				`).join('')}
			</div>
		`;

		lista.forEach((file, index) => {
			const wrapper = modalFotosBody.querySelector(`[data-preview-index="${index}"]`);
			if (!wrapper) return;
			const imgEl = wrapper.querySelector('img');

			const reader = new FileReader();
			reader.onload = () => {
				imgEl.src = reader.result;
				imgEl.alt = escapeHtml(file.name);
			};
			reader.onerror = () => {
				wrapper.innerHTML = `
					<div class="device-detail__empty">No se pudo cargar la vista previa.</div>
				`;
			};
			reader.readAsDataURL(file);
		});
	};

	const syncInputFotos = () => {
		if (!inputFotosOrden) {
			return;
		}

		const dataTransfer = new DataTransfer();
		fotosSeleccionadas.forEach((file) => dataTransfer.items.add(file));
		inputFotosOrden.files = dataTransfer.files;
	};

	const setFotosSeleccionadas = (files) => {
		fotosSeleccionadas = Array.from(files || []).filter((file) => file && file.type && file.type.startsWith('image/'));
		syncInputFotos();
		renderPreviewFotos(fotosSeleccionadas);
	};

	const eliminarFotoSeleccionada = (index) => {
		if (index < 0 || index >= fotosSeleccionadas.length) {
			return;
		}

		fotosSeleccionadas.splice(index, 1);
		syncInputFotos();
		renderPreviewFotos(fotosSeleccionadas);
	};

	if (inputFotosOrden) {
		inputFotosOrden.addEventListener('change', () => {
			setFotosSeleccionadas(inputFotosOrden.files);
		});
	}

	if (fotosDropzone && inputFotosOrden) {
		const setDropzoneActive = (isActive) => {
			fotosDropzone.classList.toggle('is-dragover', isActive);
		};

		fotosDropzone.addEventListener('dragenter', (event) => {
			event.preventDefault();
			event.stopPropagation();
			setDropzoneActive(true);
		});

		fotosDropzone.addEventListener('dragover', (event) => {
			event.preventDefault();
			event.stopPropagation();
			setDropzoneActive(true);
		});

		fotosDropzone.addEventListener('dragleave', (event) => {
			event.preventDefault();
			event.stopPropagation();
			if (event.target === fotosDropzone) {
				setDropzoneActive(false);
			}
		});

		fotosDropzone.addEventListener('drop', (event) => {
			event.preventDefault();
			event.stopPropagation();
			setDropzoneActive(false);

			const files = Array.from(event.dataTransfer?.files || []).filter((file) => file.type && file.type.startsWith('image/'));
			if (files.length === 0) {
				return;
			}

			const dataTransfer = new DataTransfer();
			files.forEach((file) => dataTransfer.items.add(file));
			setFotosSeleccionadas(dataTransfer.files);
		});
	}

	if (modalFotosBody) {
		modalFotosBody.addEventListener('click', (event) => {
			const targetSaved = event.target.closest('[data-remove-saved-photo]');
			if (targetSaved) {
				const idFoto = resolverIdFotoGuardada(targetSaved);
				if (!idFoto) {
					console.warn('No se pudo resolver el ID real de la foto guardada para eliminar.');
					return;
				}

				fotoGuardadaPendienteEliminar = {
					idFoto,
					card: targetSaved.closest('[data-saved-photo-id]') || targetSaved,
				};
				if (window.UiModal && typeof window.UiModal.openById === 'function') {
					window.UiModal.openById('modal-foto-eliminar-guardada');
				}
				return;
			}

			const targetPreview = event.target.closest('[data-remove-photo]');
			if (targetPreview) {
				const indexPreview = Number(targetPreview.getAttribute('data-remove-photo'));
				if (!Number.isFinite(indexPreview)) return;
				eliminarFotoSeleccionada(indexPreview);
				return;
			}

			// Abrir vista ampliada al hacer click en la imagen de la vista previa
			const clickedImg = event.target.closest('img.preview-photo');
			if (clickedImg) {
				if (modalPhotoImg) {
					modalPhotoImg.src = clickedImg.src;
					modalPhotoImg.alt = clickedImg.alt || '';
				}
				if (window.UiModal && typeof window.UiModal.openById === 'function') {
					window.UiModal.openById('modal-photo-view');
				}
			}
		});
	}

	if (orderPhotos) {
		orderPhotos.addEventListener('click', (event) => {
			const targetSaved = event.target.closest('[data-remove-saved-photo]');
			if (targetSaved) {
				const idFoto = resolverIdFotoGuardada(targetSaved);
				if (!idFoto) {
					console.warn('No se pudo resolver el ID real de la foto guardada para eliminar.');
					return;
				}

				fotoGuardadaPendienteEliminar = {
					idFoto,
					card: targetSaved.closest('[data-saved-photo-id]') || targetSaved,
				};

				if (window.UiModal && typeof window.UiModal.openById === 'function') {
					window.UiModal.openById('modal-foto-eliminar-guardada');
				}
				return;
			}

			// Si se clickeó la imagen misma, abrir el modal para verla ampliada
			const clickedImg = event.target.closest('img.order-photo');
			if (clickedImg) {
				if (modalPhotoImg) {
					modalPhotoImg.src = clickedImg.src;
					modalPhotoImg.alt = clickedImg.alt || '';
				}
				if (window.UiModal && typeof window.UiModal.openById === 'function') {
					window.UiModal.openById('modal-photo-view');
				}
			}
		});
	}

	if (btnConfirmDeleteSavedPhoto) {
		btnConfirmDeleteSavedPhoto.addEventListener('click', async () => {
			if (!fotoGuardadaPendienteEliminar?.idFoto) return;

			const btn = btnConfirmDeleteSavedPhoto;
			const originalText = btn.textContent;
			try {
				btn.disabled = true;
				btn.textContent = 'Eliminando...';
				const response = await fetch(`/api/taller/fotos/${encodeURIComponent(fotoGuardadaPendienteEliminar.idFoto)}`, {
					method: 'DELETE',
					cache: 'no-store',
					headers: {
						'Accept': 'application/json',
						...(csrfToken ? { 'X-CSRFToken': csrfToken, 'X-CSRF-Token': csrfToken } : {}),
					},
					credentials: 'same-origin',
				});

				if (!response.ok) {
					let text = '';
					try { text = (await response.json()).message || await response.text(); } catch (_) { text = await response.text(); }
					throw new Error(`HTTP ${response.status} - ${text}`);
				}

				const data = await response.json().catch(() => ({}));
				// eliminar del DOM
				fotoGuardadaPendienteEliminar.card?.remove();
				await cargarDetalleOrden(ordenActualId, 'vista-2');
				if (!data.ok) console.warn('Respuesta eliminación:', data);
			} catch (error) {
				console.error('Error eliminando foto guardada:', error);
				alert('No se pudo eliminar la imagen. Revisa la consola para más detalles.');
			} finally {
				fotoGuardadaPendienteEliminar = null;
				btn.disabled = false;
				btn.textContent = originalText;
				if (window.UiModal && typeof window.UiModal.closeById === 'function') {
					window.UiModal.closeById('modal-foto-eliminar-guardada');
				}
			}
		});
	}

	if (formFotosOrden) {
		formFotosOrden.addEventListener('submit', async (event) => {
			event.preventDefault();
			const files = inputFotosOrden?.files;
			if (!files || files.length === 0) return;
			const idOrden = modalFotosIdOrden?.value || ordenActualId;
			if (!idOrden) return;

			const formData = new FormData();
			Array.from(files).forEach((file) => formData.append('fotos', file));

			try {
				const response = await fetch(`/api/taller/ordenes/${encodeURIComponent(idOrden)}/fotos`, {
					method: 'POST',
					body: formData,
					credentials: 'same-origin',
					headers: {
						...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
					},
				});
				if (!response.ok) throw new Error(`HTTP ${response.status}`);
				inputFotosOrden.value = '';
				await cargarDetalleOrden(idOrden, 'vista-2');
				if (window.UiModal && typeof window.UiModal.closeById === 'function') {
					window.UiModal.closeById('modal-fotos-registrar');
				}
			} catch (error) {
				console.error('Error registrando fotos:', error);
			}
		});
	}

	activateView("vista-1");
	cargarOrdenes();
	cargarReparacionesAsignadas();
});
