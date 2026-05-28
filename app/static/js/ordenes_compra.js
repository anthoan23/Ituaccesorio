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
	const btnRegistrarEntrada = document.getElementById('btn-registrar-entrada');
	const modalRegistrarEntradaTitle = document.getElementById('modal-registrar-entrada-title');
	const modalConfirmarAnularTexto = document.getElementById('texto-confirmar-anular-orden');
	const btnConfirmarAnularOrden = document.getElementById('btn-confirmar-anular-orden');

	const state = {
		proveedores: [],
		productosDisponibles: [],
		productosSeleccionados: [],
		proveedorSeleccionado: null,
		modoFormulario: 'registrar',
		ordenEditandoId: null,
		ordenParaAnularId: null,
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

	function establecerModoFormulario(modo) {
		const esEdicion = modo === 'editar';
		state.modoFormulario = esEdicion ? 'editar' : 'registrar';
		if (modalRegistrarEntradaTitle) {
			modalRegistrarEntradaTitle.textContent = esEdicion ? 'Modificar orden' : 'Registrar orden';
		}
		if (btnGuardarEntrada) {
			btnGuardarEntrada.textContent = esEdicion ? 'Modificar orden' : 'Registrar orden';
		}
		if (btnDesplegarProveedores) {
			btnDesplegarProveedores.hidden = false;
			btnDesplegarProveedores.disabled = esEdicion;
			btnDesplegarProveedores.setAttribute('aria-disabled', esEdicion ? 'true' : 'false');
		}
	}

	function limpiarFormularioEntrada() {
		state.proveedorSeleccionado = null;
		state.productosDisponibles = [];
		state.productosSeleccionados = [];
		state.ordenEditandoId = null;
		if (formRegistrarEntrada) formRegistrarEntrada.reset();
		if (entradaIdProveedor) entradaIdProveedor.value = '';
		if (entradaNombreProveedor) entradaNombreProveedor.value = '';
		renderProductosSeleccionados();
		actualizarTotal();
		if (btnDesplegarProductos) btnDesplegarProductos.disabled = true;
		establecerModoFormulario('registrar');
	}

	function abrirModalRegistro() {
		limpiarFormularioEntrada();
		if (window.UiModal && typeof window.UiModal.openById === 'function') {
			window.UiModal.openById('modal-registrar-entrada');
		} else {
			const modal = document.getElementById('modal-registrar-entrada');
			if (modal) modal.removeAttribute('hidden');
		}
	}

	function seleccionarProductoParaEdicion(productoDetalle) {
		const nombreModelo = String(productoDetalle?.N_modelo ?? productoDetalle?.modelo ?? productoDetalle?.nombre ?? '');
		const productoDisponible = state.productosDisponibles.find((item) => {
			const nombreItem = String(item.modelo_nombre ?? item.N_modelo ?? item.nombre ?? '');
			return nombreItem === nombreModelo;
		});

		return {
			id_modelo: String(productoDisponible?.id_modelo ?? productoDisponible?.ID_modelo ?? productoDisponible?.id ?? ''),
			nombre: nombreModelo,
			proveedor: entradaNombreProveedor ? entradaNombreProveedor.value : '',
			costo: Number(productoDetalle?.Costo ?? productoDisponible?.costo ?? productoDisponible?.Costo ?? 0),
			cantidad: Number(productoDetalle?.Cantidad_p ?? productoDetalle?.cantidad ?? 1),
		};
	}

	async function abrirModalModificarOrden(idOrden) {
		try {
			await cargarProveedores();
			const data = await fetchJson(`/api/detalles_orden/${encodeURIComponent(idOrden)}`, { method: 'POST' });
			const detalle = data?.datos_orden || null;
			const productos = Array.isArray(data?.productos_orden) ? data.productos_orden : [];
			if (!detalle) {
				throw new Error('No se pudo cargar la orden');
			}

			const proveedorNombre = String(detalle.N_proveedor ?? '');
			const proveedorEncontrado = state.proveedores.find((item) => String(item.N_proveedor ?? item.nombre ?? '') === proveedorNombre) || null;
			state.proveedorSeleccionado = proveedorEncontrado;
			state.ordenEditandoId = detalle.ID_orden_c ?? idOrden;

			if (entradaIdProveedor) entradaIdProveedor.value = String(proveedorEncontrado?.ID_proveedor ?? proveedorEncontrado?.id ?? '');
			if (entradaNombreProveedor) entradaNombreProveedor.value = proveedorNombre;
			if (btnDesplegarProductos) btnDesplegarProductos.disabled = !proveedorEncontrado;

			if (proveedorEncontrado) {
				await cargarProductosDeProveedor(proveedorEncontrado.ID_proveedor ?? proveedorEncontrado.id);
			}

			state.productosSeleccionados = productos
				.map((producto) => seleccionarProductoParaEdicion(producto))
				.filter((producto) => producto.id_modelo);

			establecerModoFormulario('editar');
		renderProductosSeleccionados();
			actualizarTotal();

			if (window.UiModal && typeof window.UiModal.openById === 'function') {
				window.UiModal.openById('modal-registrar-entrada');
			} else {
				const modal = document.getElementById('modal-registrar-entrada');
				if (modal) modal.removeAttribute('hidden');
			}
		} catch (error) {
			console.error(error);
			alert(error.message || 'No se pudo cargar la orden');
		}
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
			return state.proveedores;
		} catch (error) {
			console.error(error);
			state.proveedores = [];
			if (listaProveedores) {
				listaProveedores.innerHTML = '<tr><td colspan="3" class="table__empty">Error al cargar proveedores.</td></tr>';
			}
			return [];
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
			return [];
		}
		return state.productosDisponibles;
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

	if (btnRegistrarEntrada) {
		btnRegistrarEntrada.addEventListener('click', () => {
			abrirModalRegistro();
		});
	}

	// allow clicking the provider name input to open provider picker
	if (entradaNombreProveedor) {
		entradaNombreProveedor.style.cursor = 'pointer';
		entradaNombreProveedor.addEventListener('click', () => {
			if (state.modoFormulario === 'editar') return;
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

			const esEdicion = state.modoFormulario === 'editar';
			const payload = {
				...(esEdicion ? { ID_orden_c: Number(state.ordenEditandoId) } : {
					ID_proveedor: Number(state.proveedorSeleccionado.ID_proveedor ?? state.proveedorSeleccionado.id),
				}),
				productos: state.productosSeleccionados.map((p) => [Number(p.id_modelo), Number(p.cantidad)]),
			};

			try {
				await fetchJson(esEdicion ? '/api/ordenes_compra/actualizar_productos' : '/api/ordenes_compra/agregar', {
					method: 'POST',
					body: JSON.stringify(payload),
				});
				alert(esEdicion ? 'Orden modificada' : 'Orden registrada');
				limpiarFormularioEntrada();
				if (window.UiModal && typeof window.UiModal.closeById === 'function') {
					window.UiModal.closeById('modal-seleccionar-productos');
					window.UiModal.closeById('modal-seleccionar-proveedor');
						window.UiModal.closeById('modal-registrar-entrada');
				}
				cargarOrdenes();
			} catch (error) {
				console.error(error);
				alert(`Error ${esEdicion ? 'modificando' : 'registrando'} la orden: ${error.message}`);
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
				await abrirDetalleCompra(id);
				return;
			}

			if (btn.classList.contains('btn-anular')) {
				state.ordenParaAnularId = Number(id);
				if (modalConfirmarAnularTexto) {
					modalConfirmarAnularTexto.textContent = `¿Seguro de que quieres anular la orden ${id}?`;
				}
				if (window.UiModal && typeof window.UiModal.openById === 'function') {
					window.UiModal.openById('modal-confirmar-anular-orden');
				} else {
					const modal = document.getElementById('modal-confirmar-anular-orden');
					if (modal) modal.removeAttribute('hidden');
				}
				return;
			}

			if (btn.classList.contains('btn-edit')) {
				await abrirModalModificarOrden(id);
				return;
			}

			if (btn.classList.contains('btn-entrega')) {
				const recibidoPor = prompt('Pedido realizado por (nombre):', '');
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

	if (btnConfirmarAnularOrden) {
		btnConfirmarAnularOrden.addEventListener('click', async () => {
			if (!state.ordenParaAnularId) {
				alert('No se encontró la orden a anular.');
				return;
			}

			btnConfirmarAnularOrden.disabled = true;
			try {
				await fetchJson('/api/ordenes_compra/anular', {
					method: 'POST',
					body: JSON.stringify({ ID_orden_c: Number(state.ordenParaAnularId) }),
				});
				alert('Orden anulada');
				state.ordenParaAnularId = null;
				if (window.UiModal && typeof window.UiModal.closeById === 'function') {
					window.UiModal.closeById('modal-confirmar-anular-orden');
				} else {
					const modal = document.getElementById('modal-confirmar-anular-orden');
					if (modal) modal.setAttribute('hidden', '');
				}
				cargarOrdenes();
			} catch (err) {
				console.error(err);
				alert(err.message || 'Error de red al anular la orden');
			} finally {
				btnConfirmarAnularOrden.disabled = false;
			}
		});
	}

async function abrirDetalleCompra(id) {
	try {
		const data = await fetchJson(`/api/detalles_orden/${encodeURIComponent(id)}`, { method: 'POST' });
		const detalle = data.datos_orden || null;
		const productos = Array.isArray(data.productos_orden) ? data.productos_orden : [];

		renderDetalleCompraInfo(detalle);
		renderDetalleCompraProductos(productos);

		if (window.UiModal && typeof window.UiModal.openById === 'function') {
			window.UiModal.openById('modal-detalle-orden');
		}
	} catch (err) {
		console.error(err);
		alert(err.message || 'No se pudo cargar el detalle de la orden');
	}
}

function renderDetalleCompraInfo(detalle) {
	const container = document.getElementById('detalle-orden-info');
	const title = document.getElementById('modal-detalle-orden-title');
	if (!container) return;
	if (!detalle) {
		container.innerHTML = '<p>No se encontró información de la orden.</p>';
		const totalValueEmpty = document.getElementById('detalle-orden-total-value');
		if (totalValueEmpty) totalValueEmpty.textContent = '0';
		if (title) title.textContent = 'Detalle de orden';
		return;
	}
	if (title) title.textContent = `Detalle de orden #${detalle.ID_orden_c ?? ''}`;
	const nombreEm = `${detalle.Nombre_em ?? ''} ${detalle.Apellido_em ?? ''}`.trim();
	const items = [
		
		['Proveedor', detalle.N_proveedor],
		['Fecha', formatDate(detalle.Fecha_o)],
		['Estado', detalle.Estado],	
		['Realizado por', nombreEm],
	];

	container.innerHTML = `
		<div class="device-detail__grid">
			${items.map(([label, value]) => `
				<div class="detail-item">
					<span class="device-detail__label">${escapeHtml(label)}</span>
					<span class="device-detail__value">${escapeHtml(value)}</span>
				</div>
			`).join('')}
		</div>
	`;

	const totalValue = document.getElementById('detalle-orden-total-value');
	if (totalValue) totalValue.textContent = formatMoney(detalle.Costo_venta ?? 0);
}

function renderDetalleCompraProductos(productos) {
	const tbody = document.getElementById('detalle-orden-productos');
	if (!tbody) return;
	if (!productos || productos.length === 0) {
		tbody.innerHTML = '<tr><td colspan="5" class="table__empty">No hay productos.</td></tr>';
		return;
	}
	tbody.innerHTML = productos.map((p) => `
		<tr>
			<td>${escapeHtml(p.N_marca ?? p.marca ?? '')}</td>
			<td>${escapeHtml(p.N_modelo ?? p.modelo ?? '')}</td>
			<td>${escapeHtml(p.Cantidad_p ?? p.cantidad ?? '')}</td>
			<td>${escapeHtml(formatMoney(p.Costo ?? p.costo ?? 0))}</td>
			<td>${escapeHtml(formatMoney(p.sup_total ?? (p.Cantidad_p && p.Costo ? p.Cantidad_p * p.Costo : 0)))}</td>
		</tr>
	`).join('');
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
