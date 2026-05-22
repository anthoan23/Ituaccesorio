document.addEventListener('DOMContentLoaded', () => {
	const sections = Array.from(document.querySelectorAll('.content'));
	const viewButtons = Array.from(document.querySelectorAll('[data-view-target]'));
	const breadcrumbSection = document.getElementById('breadcrumb-section');
	const titles = {
		'vista-1': 'Órdenes pendientes',
		'vista-2': 'Órdenes entregadas',
	};

	const tablaOrdenesPendientes = document.getElementById('tabla-ordenes-pendientes');
	const tablaOrdenesEntregadas = document.getElementById('tabla-ordenes-entregadas');
	const csrfToken = document.getElementById('ordenes-compra-csrf-token')?.value
		|| document.querySelector("input[name='_csrf_token']")?.value
		|| '';

	const formRegistrarEntrada = document.getElementById('form-registrar-entrada');
	const btnDesplegarProveedores = document.getElementById('btn-desplegar-proveedores');
	const listaProveedores = document.getElementById('lista-proveedores');
	const entradaIdProveedor = document.getElementById('entrada-id-proveedor');
	const entradaNombreProveedor = document.getElementById('entrada-nombre-proveedor');
	const btnDesplegarProductos = document.getElementById('btn-desplegar-productos');
	const listaProductos = document.getElementById('lista-productos');
	const tablaProductosSeleccionados = document.getElementById('tabla-productos-seleccionados');
	const entradaCostoTotal = document.getElementById('entrada-costo-total');
	const entradaCostoTotalInput = document.getElementById('entrada-costo-total-input');
	const btnGuardarEntrada = document.getElementById('btn-guardar-entrada');

	const state = {
		proveedores: [],
		productosDisponibles: [],
		productosSeleccionados: [],
		proveedorSeleccionado: null,
	};

	const formatMoney = (value) => {
		const number = Number(value);
		if (!Number.isFinite(number)) return '0';
		return number.toLocaleString('es-VE');
	};

	function escapeHtml(value) {
		return String(value ?? '')
			.replaceAll('&', '&amp;')
			.replaceAll('<', '&lt;')
			.replaceAll('>', '&gt;')
			.replaceAll('"', '&quot;')
			.replaceAll("'", '&#039;');
	}

	async function fetchJson(url, options = {}) {
		const headers = new Headers(options.headers || {});
		headers.set('Accept', 'application/json');
		const method = String(options.method || 'GET').toUpperCase();
		if (method !== 'GET' && method !== 'HEAD' && csrfToken && !headers.has('X-CSRFToken')) {
			headers.set('X-CSRFToken', csrfToken);
		}
		if (options.body && !headers.has('Content-Type')) {
			headers.set('Content-Type', 'application/json');
		}

		const res = await fetch(url, {
			credentials: 'same-origin',
			...options,
			headers,
		});

		const contentType = res.headers.get('content-type') || '';
		const payload = contentType.includes('application/json') ? await res.json() : await res.text();

		if (!res.ok) {
			const message = typeof payload === 'string'
				? payload
				: (payload && (payload.error || payload.message)) || `HTTP ${res.status}`;
			throw new Error(message);
		}

		return payload;
	}

	const activateView = (viewId) => {
		sections.forEach((section) => {
			section.hidden = !section.classList.contains(viewId);
		});

		viewButtons.forEach((button) => {
			button.classList.toggle('is-active', button.dataset.viewTarget === viewId);
		});

		if (breadcrumbSection) {
			breadcrumbSection.textContent = titles[viewId] || '';
		}

		window.location.hash = viewId;
	};

	viewButtons.forEach((button) => {
		button.addEventListener('click', () => activateView(button.dataset.viewTarget));
	});

	const initialView = window.location.hash.replace('#', '') || 'vista-1';
	activateView(titles[initialView] ? initialView : 'vista-1');

	function formatDate(val) {
		try {
			const date = new Date(val);
			if (!Number.isNaN(date.getTime())) return date.toLocaleDateString();
		} catch (error) {
			void error;
		}
		return String(val || '');
	}

	function renderPendientes(ordenes) {
		if (!tablaOrdenesPendientes) return;
		if (!ordenes || ordenes.length === 0) {
			tablaOrdenesPendientes.innerHTML = '<tr><td colspan="5" class="table__empty">No hay órdenes de compra pendientes.</td></tr>';
			return;
		}

		tablaOrdenesPendientes.innerHTML = ordenes.map((orden) => `
			<tr>
				<td>${escapeHtml(orden.ID_orden_c)}</td>
				<td>${escapeHtml(orden.N_proveedor)}</td>
				<td>${escapeHtml(formatDate(orden.Fecha_o))}</td>
				<td>${escapeHtml(orden.Estado || '')}</td>
				<td>${escapeHtml(formatMoney(orden.Costo_venta))}</td>
				<td class="table__actions">
					<button type="button" class="btn btn--small btn-ver" data-id="${escapeHtml(orden.ID_orden_c)}">Ver</button>
					<button type="button" class="btn btn--small btn-edit" data-id="${escapeHtml(orden.ID_orden_c)}">Modificar</button>
					<button type="button" class="btn btn--small btn-anular" data-id="${escapeHtml(orden.ID_orden_c)}">Anular</button>
					<button type="button" class="btn btn--small btn-entrega" data-id="${escapeHtml(orden.ID_orden_c)}">Agregar entrega</button>
				</td>
			</tr>
		`).join('');
	}

	function renderProveedores() {
		// keep select rendering for backward compatibility if needed
		// also render modal list when available
		if (listaProveedores) {
			if (!state.proveedores.length) {
				listaProveedores.innerHTML = '<tr><td colspan="2" class="table__empty">No hay proveedores.</td></tr>';
				return;
			}
			listaProveedores.innerHTML = state.proveedores.map((p) => `
				<tr data-proveedor-id="${escapeHtml(p.ID_proveedor ?? p.id ?? '')}" class="row-selectable">
					<td>${escapeHtml(p.ID_proveedor ?? p.id ?? '')}</td>
					<td>${escapeHtml(p.N_proveedor ?? p.nombre ?? '')}</td>
				</tr>
			`).join('');
		}
	}

	function renderProductosDisponibles() {
		if (!listaProductos) return;
		if (!state.productosDisponibles.length) {
			listaProductos.innerHTML = '<tr><td colspan="4" class="table__empty">No hay productos disponibles para este proveedor.</td></tr>';
			return;
		}
		listaProductos.innerHTML = state.productosDisponibles.map((producto) => `
			<tr data-producto-id="${escapeHtml(producto.id_modelo ?? producto.ID_modelo ?? producto.id ?? '')}" class="row-selectable">
				<td>${escapeHtml(producto.clase_nombre ?? producto.N_Clase ?? '')}</td>
				<td>${escapeHtml(producto.marca_nombre ?? producto.N_marca ?? '')}</td>
				<td>${escapeHtml(producto.modelo_nombre ?? producto.N_modelo ?? producto.nombre ?? '')}</td>
				<td>${escapeHtml(formatMoney(producto.costo ?? producto.Costo ?? 0))}</td>
			</tr>
		`).join('');
	}

	function renderProductosSeleccionados() {
		if (!tablaProductosSeleccionados) return;

		if (!state.productosSeleccionados.length) {
			tablaProductosSeleccionados.innerHTML = '<tr><td colspan="5" class="table__empty">Aún no hay productos seleccionados.</td></tr>';
			return;
		}

		tablaProductosSeleccionados.innerHTML = state.productosSeleccionados.map((producto, index) => `
			<tr>
				<td>${escapeHtml(producto.nombre)}</td>
				<td>${escapeHtml(producto.proveedor)}</td>
				<td>${escapeHtml(producto.cantidad)}</td>
				<td>${escapeHtml(formatMoney(Number(producto.costo || 0) * Number(producto.cantidad || 0)))}</td>
				<td class="table__actions">
					<button type="button" class="btn btn--small btn-agregar-mas" data-product-index="${index}">Agregar más</button>
					<button type="button" class="btn btn--small btn-anular" data-product-index="${index}">Quitar</button>
				</td>
			</tr>
		`).join('');
	}

	function actualizarTotal() {
		const total = state.productosSeleccionados.reduce((suma, producto) => {
			const cantidad = Number(producto.cantidad || 0);
			const costo = Number(producto.costo || 0);
			return suma + (cantidad * costo);
		}, 0);
		if (entradaCostoTotal) entradaCostoTotal.textContent = String(total);
		if (entradaCostoTotalInput) entradaCostoTotalInput.value = String(total);
		if (btnGuardarEntrada) btnGuardarEntrada.disabled = !state.proveedorSeleccionado || state.productosSeleccionados.length === 0;
	}

	function limpiarProductosSeleccionados() {
		state.productosSeleccionados = [];
		renderProductosSeleccionados();
		actualizarTotal();
	}

	function normalizarProveedores(payload) {
		// Compatible with `return jsonify(proveedores)` and wrapped payloads.
		if (Array.isArray(payload)) return payload;
		if (payload && Array.isArray(payload.proveedores)) return payload.proveedores;
		return [];
	}

	function normalizarProductos(payload) {
		// Compatible with `return jsonify(productos)` and wrapped payloads.
		if (Array.isArray(payload)) return payload;
		if (payload && Array.isArray(payload.productos)) return payload.productos;
		return [];
	}

	async function cargarProveedores() {
		try {
			const data = await fetchJson('/api/proveedores');
			state.proveedores = normalizarProveedores(data);
			renderProveedores();
		} catch (error) {
			console.error(error);
			state.proveedores = [];
			if (listaProveedores) {
				listaProveedores.innerHTML = '<tr><td colspan="3" class="table__empty">Error al cargar proveedores.</td></tr>';
			}
		}
	}

	async function cargarProductosDeProveedor(idProveedor) {
		try {
			const data = await fetchJson(`/api/productos_proveedor/${encodeURIComponent(idProveedor)}`, {
				method: 'POST',
			});
			state.productosDisponibles = normalizarProductos(data);
			// render modal list if available
			if (listaProductos) {
				if (!state.productosDisponibles.length) {
					listaProductos.innerHTML = '<tr><td colspan="4" class="table__empty">No hay productos para este proveedor.</td></tr>';
					return;
				}
				listaProductos.innerHTML = state.productosDisponibles.map((pr) => `
					<tr data-producto-id="${escapeHtml(pr.id_modelo ?? pr.ID_modelo ?? pr.id ?? '')}" class="row-selectable">
						<td>${escapeHtml(pr.clase_nombre ?? pr.N_Clase ?? '')}</td>
						<td>${escapeHtml(pr.marca_nombre ?? pr.N_marca ?? '')}</td>
						<td>${escapeHtml(pr.modelo_nombre ?? pr.N_modelo ?? pr.nombre ?? '')}</td>
						<td>${escapeHtml(formatMoney(pr.costo ?? pr.Costo ?? 0))}</td>
					</tr>
				`).join('');
			}
		} catch (error) {
			console.error(error);
			state.productosDisponibles = [];
			if (listaProductos) listaProductos.innerHTML = '<tr><td colspan="4" class="table__empty">Error al cargar productos.</td></tr>';
		}
	}

	function seleccionarProveedor(idProveedor) {
		const proveedor = state.proveedores.find((item) => String(item.ID_proveedor ?? item.id ?? '') === String(idProveedor)) || null;
		state.proveedorSeleccionado = proveedor;
		state.productosDisponibles = [];
		limpiarProductosSeleccionados();

		if (entradaIdProveedor) entradaIdProveedor.value = proveedor ? String(proveedor.ID_proveedor ?? proveedor.id ?? '') : '';
		if (entradaNombreProveedor) entradaNombreProveedor.value = proveedor ? String(proveedor.N_proveedor ?? proveedor.nombre ?? '') : '';

		if (btnDesplegarProductos) btnDesplegarProductos.disabled = !proveedor;
		if (btnGuardarEntrada) btnGuardarEntrada.disabled = true;

		if (proveedor) {
			cargarProductosDeProveedor(entradaIdProveedor ? entradaIdProveedor.value : idProveedor);
		}
	}

	if (btnDesplegarProveedores) {
		btnDesplegarProveedores.addEventListener('click', async () => {
			await cargarProveedores();
			if (window.UiModal && typeof window.UiModal.openById === 'function') window.UiModal.openById('modal-seleccionar-proveedor');
			else {
				const m = document.getElementById('modal-seleccionar-proveedor');
				if (m) m.removeAttribute('hidden');
			}
		});
	}

	// allow clicking the provider name input to open provider picker
	if (entradaNombreProveedor) {
		entradaNombreProveedor.style.cursor = 'pointer';
		entradaNombreProveedor.addEventListener('click', () => {
			if (btnDesplegarProveedores) btnDesplegarProveedores.click();
		});
	}

	if (listaProveedores) {
		listaProveedores.addEventListener('click', (event) => {
			const row = event.target.closest('tr[data-proveedor-id]');
			if (!row) return;
			const id = row.dataset.proveedorId;
			if (!id) return;
			seleccionarProveedor(id);
			if (window.UiModal && typeof window.UiModal.closeById === 'function') window.UiModal.closeById('modal-seleccionar-proveedor');
		});
	}

	if (btnDesplegarProductos) {
		btnDesplegarProductos.addEventListener('click', async () => {
			if (!state.proveedorSeleccionado) { alert('Selecciona un proveedor primero.'); return; }
			await cargarProductosDeProveedor(state.proveedorSeleccionado.ID_proveedor ?? state.proveedorSeleccionado.id);
			if (window.UiModal && typeof window.UiModal.openById === 'function') window.UiModal.openById('modal-seleccionar-productos');
		});
	}

	if (listaProductos) {
		listaProductos.addEventListener('click', (event) => {
			const row = event.target.closest('tr[data-producto-id]');
			if (!row) return;
			const idModelo = row.dataset.productoId;
			const producto = state.productosDisponibles.find((item) => String(item.id_modelo ?? item.ID_modelo ?? item.id ?? '') === String(idModelo));
			if (!producto) return;
			const existente = state.productosSeleccionados.find((item) => String(item.id_modelo) === String(idModelo));
			if (existente) {
				existente.cantidad = Number(existente.cantidad || 0) + 1;
			} else {
				state.productosSeleccionados.push({
					id_modelo: String(idModelo),
					nombre: producto.modelo_nombre ?? producto.N_modelo ?? producto.nombre ?? '',
					proveedor: entradaNombreProveedor ? entradaNombreProveedor.value : '',
					costo: Number(producto.costo ?? producto.Costo ?? 0),
					cantidad: 1,
				});
			}
			renderProductosSeleccionados();
			actualizarTotal();
		});
	}

	if (tablaProductosSeleccionados) {
		tablaProductosSeleccionados.addEventListener('click', (event) => {
			const btnAgregarMas = event.target.closest('button[data-product-index].btn-agregar-mas');
			if (btnAgregarMas) {
				const index = Number(btnAgregarMas.dataset.productIndex);
				if (!Number.isInteger(index) || !state.productosSeleccionados[index]) return;
				state.productosSeleccionados[index].cantidad = Number(state.productosSeleccionados[index].cantidad || 0) + 1;
				renderProductosSeleccionados();
				actualizarTotal();
				return;
			}

			const btn = event.target.closest('button[data-product-index]');
			if (!btn) return;
			const index = Number(btn.dataset.productIndex);
			if (!Number.isInteger(index)) return;
				const producto = state.productosSeleccionados[index];
				if (!producto) return;
				const cantidadActual = Number(producto.cantidad || 0);
				if (cantidadActual > 1) {
					producto.cantidad = cantidadActual - 1;
				} else {
					state.productosSeleccionados.splice(index, 1);
				}
			renderProductosSeleccionados();
			actualizarTotal();
		});
	}

	if (formRegistrarEntrada) {
		formRegistrarEntrada.addEventListener('submit', async (event) => {
			event.preventDefault();

			if (!state.proveedorSeleccionado) {
				alert('Selecciona un proveedor.');
				return;
			}

			if (state.productosSeleccionados.length === 0) {
				alert('Agrega al menos un producto.');
				return;
			}

			const payload = {
				ID_proveedor: Number(state.proveedorSeleccionado.ID_proveedor ?? state.proveedorSeleccionado.id),
				Costo_venta: Number(entradaCostoTotalInput?.value || 0),
			};

			try {
				await fetchJson('/api/ordenes_compra', {
					method: 'POST',
					body: JSON.stringify(payload),
				});
				alert('Orden registrada');
				formRegistrarEntrada.reset();
				state.proveedorSeleccionado = null;
				state.productosDisponibles = [];
				limpiarProductosSeleccionados();
				if (entradaIdProveedor) entradaIdProveedor.value = '';
				if (entradaNombreProveedor) entradaNombreProveedor.value = '';
				if (entradaCostoTotal) entradaCostoTotal.textContent = '0';
				if (entradaCostoTotalInput) entradaCostoTotalInput.value = '0';
				if (btnDesplegarProductos) btnDesplegarProductos.disabled = true;
				// close selector modals if open
				if (window.UiModal && typeof window.UiModal.closeById === 'function') {
					window.UiModal.closeById('modal-seleccionar-productos');
					window.UiModal.closeById('modal-seleccionar-proveedor');
				}
				if (btnGuardarEntrada) btnGuardarEntrada.disabled = true;
					if (window.UiModal && typeof window.UiModal.closeById === 'function') {
						window.UiModal.closeById('modal-registrar-entrada');
					}
				cargarOrdenes();
			} catch (error) {
				console.error(error);
				alert(`Error registrando la orden: ${error.message}`);
			}
		});
	}

	if (tablaOrdenesPendientes) {
		tablaOrdenesPendientes.addEventListener('click', async (ev) => {
			const btn = ev.target.closest('button');
			if (!btn) return;
			const id = btn.dataset.id;
			if (!id) return;

			if (btn.classList.contains('btn-ver')) {
				window.location.href = `/ordenes_compra/${id}`;
				return;
			}

			if (btn.classList.contains('btn-anular')) {
				if (!confirm('¿Anular esta orden de compra? Esta acción no se puede deshacer.')) return;
				try {
					await fetchJson(`/api/ordenes_compra/${id}`, { method: 'DELETE' });
					alert('Orden anulada');
					cargarOrdenes();
				} catch (err) {
					console.error(err);
					alert('Error de red al anular la orden');
				}
				return;
			}

			if (btn.classList.contains('btn-edit')) {
				const nuevoEstado = prompt('Nuevo estado:', 'Pendiente');
				if (nuevoEstado === null) return;
				const nuevoCosto = prompt('Nuevo costo total (numérico):', '0');
				if (nuevoCosto === null) return;
				try {
					await fetchJson(`/api/ordenes_compra/${id}`, {
						method: 'PUT',
						body: JSON.stringify({ Estado: nuevoEstado, Costo_venta: Number(nuevoCosto) }),
					});
					alert('Orden actualizada');
					cargarOrdenes();
				} catch (err) {
					console.error(err);
					alert('Error de red al actualizar la orden');
				}
				return;
			}

			if (btn.classList.contains('btn-entrega')) {
				const recibidoPor = prompt('Recibido por (nombre):', '');
				if (recibidoPor === null) return;
				const fechaEntrega = prompt('Fecha de entrega (YYYY-MM-DD):', new Date().toISOString().slice(0, 10));
				if (fechaEntrega === null) return;
				try {
					await fetchJson(`/api/ordenes_compra/${id}/entrega`, {
						method: 'POST',
						body: JSON.stringify({ recibido_por: recibidoPor, fecha_entrega: fechaEntrega }),
					});
					alert('Entrega registrada');
					cargarOrdenes();
				} catch (err) {
					console.error(err);
					alert('Error de red al registrar entrega');
				}
			}
		});
	}

	async function cargarOrdenes() {
		try {
			const res = await fetch('/api/ordenes_compra', { credentials: 'same-origin' });
			if (!res.ok) throw new Error('Error fetching órdenes');
			const data = await res.json();
			if (Array.isArray(data)) renderPendientes(data);
			else if (data && data.ordenes) renderPendientes(data.ordenes);
			else renderPendientes([]);
		} catch (error) {
			console.error(error);
			renderPendientes([]);
		}
	}

	cargarOrdenes();

	document.querySelectorAll('[data-view-target="vista-1"]').forEach((btn) => btn.addEventListener('click', cargarOrdenes));

	if (tablaOrdenesEntregadas && !tablaOrdenesEntregadas.children.length) {
		tablaOrdenesEntregadas.innerHTML = '<tr><td colspan="5" class="table__empty">No hay órdenes de compra entregadas.</td></tr>';
	}

	if (btnDesplegarProductos) {
		btnDesplegarProductos.disabled = true;
	}

	cargarProveedores();
});
