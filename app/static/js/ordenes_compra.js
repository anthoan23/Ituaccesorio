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

// ==================== REPORTES ORDENES DE COMPRA ====================

let reporteDatosActuales = [];
let reporteFiltrosActuales = {};

const btnReportes = document.getElementById("btn-reportes");
const modalReportes = document.getElementById("modal-reportes");
const reporteProveedor = document.getElementById("reporte-proveedor");
const reporteEstado = document.getElementById("reporte-estado");
const reporteFechaDesde = document.getElementById("reporte-fecha-desde");
const reporteFechaHasta = document.getElementById("reporte-fecha-hasta");
const reporteCostoMin = document.getElementById("reporte-costo-min");
const reporteCostoMax = document.getElementById("reporte-costo-max");
const btnGenerarReporte = document.getElementById("btn-generar-reporte");
const btnLimpiarFiltrosReporte = document.getElementById("btn-limpiar-filtros");
const btnExportarExcel = document.getElementById("btn-exportar-excel");
const btnExportarPdf = document.getElementById("btn-exportar-pdf");
const btnImprimir = document.getElementById("btn-imprimir");
const reportePreview = document.getElementById("reporte-preview");
const reporteTotal = document.getElementById("reporte-total");
const reporteTabla = document.getElementById("reporte-tabla");

function notifyReportes(type, message) {
    if (window.FeedbackModal && typeof window.FeedbackModal.show === "function") {
        window.FeedbackModal.show({
            type: type === "error" ? "error" : "success",
            title: type === "error" ? "No se pudo completar" : "Acción exitosa",
            message: message,
        });
        return;
    }
    if (type === "error") {
        alert(message);
    } else {
        console.log(message);
    }
}

async function fetchJsonReportes(url, options = {}) {
    const csrfTokenInput = document.querySelector('input[name="_csrf_token"]')?.value || "";
    const authToken = localStorage.getItem("access_token") || sessionStorage.getItem("access_token") || "";
    
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            ...(csrfTokenInput ? { "X-CSRFToken": csrfTokenInput } : {}),
            ...(authToken ? { "Authorization": `Bearer ${authToken}` } : {}),
        },
        credentials: "same-origin",
        ...options,
    });
    
    const data = await response.json().catch(() => ({}));
    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Error en la operación");
    }
    return data;
}

function escapeHtmlReportes(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function formatMoneyReportes(value) {
    const n = Number(value);
    if (!Number.isFinite(n)) return "0";
    return n.toLocaleString("es-VE");
}

function limpiarFiltrosReporte() {
    if (reporteProveedor) reporteProveedor.value = "";
    if (reporteEstado) reporteEstado.value = "";
    if (reporteFechaDesde) reporteFechaDesde.value = "";
    if (reporteFechaHasta) reporteFechaHasta.value = "";
    if (reporteCostoMin) reporteCostoMin.value = "";
    if (reporteCostoMax) reporteCostoMax.value = "";
}

async function cargarProveedoresReporte() {
    if (!reporteProveedor) return;
    
    try {
        const data = await fetchJsonReportes("/api/proveedores", { method: "GET" });
        const proveedores = Array.isArray(data) ? data : (data.proveedores || []);
        reporteProveedor.innerHTML = '<option value="">Todos</option>' + 
            proveedores.map(p => `<option value="${escapeHtmlReportes(p.ID_proveedor)}">${escapeHtmlReportes(p.N_proveedor)}</option>`).join("");
    } catch (err) {
        console.error("Error cargando proveedores:", err);
    }
}

async function generarReporteOrdenes() {
    const filtros = {
        proveedor_id: reporteProveedor?.value || null,
        estado: reporteEstado?.value || null,
        fecha_desde: reporteFechaDesde?.value || null,
        fecha_hasta: reporteFechaHasta?.value || null,
        costo_min: reporteCostoMin?.value ? parseFloat(reporteCostoMin.value) : null,
        costo_max: reporteCostoMax?.value ? parseFloat(reporteCostoMax.value) : null,
    };
    
    reporteFiltrosActuales = filtros;
    
    if (btnGenerarReporte) {
        btnGenerarReporte.disabled = true;
        btnGenerarReporte.textContent = "Cargando...";
    }
    
    try {
        const data = await fetchJsonReportes("/api/ordenes_compra/reportes", {
            method: "POST",
            body: JSON.stringify(filtros)
        });
        
        reporteDatosActuales = data.ordenes || [];
        const total = data.total || 0;
        
        if (reportePreview) reportePreview.style.display = "block";
        if (reporteTotal) reporteTotal.textContent = `Total de órdenes: ${total}`;
        
        if (reporteTabla) {
            if (reporteDatosActuales.length === 0) {
                reporteTabla.innerHTML = '<tr><td colspan="6" class="table__empty">No hay órdenes con esos filtros</td></tr>';
            } else {
                reporteTabla.innerHTML = reporteDatosActuales.map(p => `
                    <tr>
                        <td>${escapeHtmlReportes(p.ID_orden_c || "-")}</td>
                        <td><strong>${escapeHtmlReportes(p.N_proveedor || "-")}</strong></td>
                        <td>${escapeHtmlReportes(p.Fecha_o || "-")}</td>
                        <td><span class="status-badge status-${(p.Estado || "Pendiente").toLowerCase()}">${escapeHtmlReportes(p.Estado || "Pendiente")}</span></td>
                        <td>$${formatMoneyReportes(p.Costo_venta || 0)}</td>
                        <td>${escapeHtmlReportes(p.Recibido_por || "-")}</td>
                    </tr>
                `).join("");
            }
        }
        
        if (btnExportarExcel) btnExportarExcel.disabled = false;
        if (btnExportarPdf) btnExportarPdf.disabled = false;
        if (btnImprimir) btnImprimir.disabled = false;
        
    } catch (err) {
        notifyReportes("error", err.message || "Error al generar el reporte");
    } finally {
        if (btnGenerarReporte) {
            btnGenerarReporte.disabled = false;
            btnGenerarReporte.textContent = "Generar reporte";
        }
    }
}

function exportarOrdenesExcel() {
    if (reporteDatosActuales.length === 0) {
        notifyReportes("error", "No hay datos para exportar");
        return;
    }
    
    const datos = reporteDatosActuales.map(p => ({
        "ID Orden": p.ID_orden_c || "",
        "Proveedor": p.N_proveedor || "",
        "Fecha": p.Fecha_o || "",
        "Estado": p.Estado || "",
        "Costo Total": p.Costo_venta || 0,
        "Recibido Por": p.Recibido_por || ""
    }));
    
    if (typeof XLSX === "undefined") {
        notifyReportes("info", "Cargando librería de Excel...");
        const script = document.createElement("script");
        script.src = "/static/js/libs/xlsx.full.min.js";
        script.onload = () => exportarOrdenesExcel();
        document.head.appendChild(script);
        return;
    }
    
    const ws = XLSX.utils.json_to_sheet(datos);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "OrdenesCompra");
    
    ws["!cols"] = [
        {wch: 10}, {wch: 35}, {wch: 12}, {wch: 12}, {wch: 15}, {wch: 20}
    ];
    
    XLSX.writeFile(wb, `ordenes_compra_${new Date().toISOString().slice(0,19)}.xlsx`);
    notifyReportes("success", "Reporte exportado a Excel");
}

function exportarOrdenesPdf() {
    if (reporteDatosActuales.length === 0) {
        notifyReportes("error", "No hay datos para exportar");
        return;
    }
    
    if (typeof window.jspdf === "undefined" || typeof window.jspdf.jsPDF === "undefined") {
        notifyReportes("info", "Cargando librería de PDF...");
        const script1 = document.createElement("script");
        script1.src = "/static/js/libs/jspdf.umd.min.js";
        script1.onload = () => {
            const script2 = document.createElement("script");
            script2.src = "/static/js/libs/jspdf.plugin.autotable.min.js";
            script2.onload = () => {
                setTimeout(() => exportarOrdenesPdf(), 100);
            };
            document.head.appendChild(script2);
        };
        document.head.appendChild(script1);
        return;
    }
    
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ orientation: "landscape", unit: "mm", format: "a4" });
    const pageWidth = doc.internal.pageSize.getWidth();
    
    const colors = {
        dark: [18, 18, 18],
        primary: [243, 197, 0],
        white: [255, 255, 255],
        grayLight: [248, 249, 250],
        grayText: [102, 102, 106]
    };
    
    const logoUrl = window.location.origin + "/static/img/LOGO COMPLETO.png";
    try {
        doc.addImage(logoUrl, "PNG", (pageWidth - 45) / 2, 8, 45, 14);
    } catch(e) {}
    
    doc.setFont("helvetica", "bold");
    doc.setFontSize(22);
    doc.setTextColor(colors.dark[0], colors.dark[1], colors.dark[2]);
    doc.text("REPORTE DE ORDENES DE COMPRA", pageWidth / 2, 30, { align: "center" });
    
    doc.setDrawColor(colors.primary[0], colors.primary[1], colors.primary[2]);
    doc.setLineWidth(0.8);
    doc.line(pageWidth / 2 - 45, 34, pageWidth / 2 + 45, 34);
    
    const now = new Date();
    const fechaStr = now.toLocaleDateString("es-ES");
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.setTextColor(colors.grayText[0], colors.grayText[1], colors.grayText[2]);
    doc.text(`Generado: ${fechaStr} • Total órdenes: ${reporteDatosActuales.length}`, pageWidth / 2, 44, { align: "center" });
    
    const filtrosTexto = [];
    if (reporteFiltrosActuales.proveedor_id) filtrosTexto.push(`Proveedor ID: ${reporteFiltrosActuales.proveedor_id}`);
    if (reporteFiltrosActuales.estado) filtrosTexto.push(`Estado: ${reporteFiltrosActuales.estado}`);
    if (reporteFiltrosActuales.fecha_desde) filtrosTexto.push(`Desde: ${reporteFiltrosActuales.fecha_desde}`);
    if (reporteFiltrosActuales.fecha_hasta) filtrosTexto.push(`Hasta: ${reporteFiltrosActuales.fecha_hasta}`);
    if (reporteFiltrosActuales.costo_min) filtrosTexto.push(`Costo ≥ $${reporteFiltrosActuales.costo_min}`);
    if (reporteFiltrosActuales.costo_max) filtrosTexto.push(`Costo ≤ $${reporteFiltrosActuales.costo_max}`);
    
    const filterY = 52;
    doc.setFillColor(colors.grayLight[0], colors.grayLight[1], colors.grayLight[2]);
    doc.rect(15, filterY, pageWidth - 30, 10, "F");
    doc.setFont("helvetica", "italic");
    doc.setFontSize(8.5);
    doc.setTextColor(colors.grayText[0], colors.grayText[1], colors.grayText[2]);
    doc.text(filtrosTexto.length ? `Filtros: ${filtrosTexto.join(" • ")}` : "Filtros: Todas las órdenes", 18, filterY + 7);
    
    const columns = ["ID", "PROVEEDOR", "FECHA", "ESTADO", "COSTO", "RECIBIDO POR"];
    const rows = reporteDatosActuales.map(p => [
        p.ID_orden_c || "",
        p.N_proveedor || "",
        p.Fecha_o || "",
        p.Estado || "Pendiente",
        `$${Number(p.Costo_venta || 0).toLocaleString("es-VE")}`,
        p.Recibido_por || "-"
    ]);
    
    doc.autoTable({
        head: [columns],
        body: rows,
        startY: filterY + 14,
        theme: "grid",
        headStyles: {
            fillColor: colors.dark,
            textColor: colors.white,
            fontStyle: "bold",
            fontSize: 9,
            halign: "center"
        },
        bodyStyles: { fontSize: 8.5, cellPadding: 4 },
        alternateRowStyles: { fillColor: colors.grayLight },
        margin: { left: 15, right: 15 },
        didDrawPage: (data) => {
            doc.setFontSize(7);
            doc.setTextColor(colors.grayText[0], colors.grayText[1], colors.grayText[2]);
            doc.text("ItuAccesorio System - Reporte Generado Exclusivamente Para ituaccesorio", pageWidth / 2, doc.internal.pageSize.getHeight() - 8, { align: "center" });
            doc.text(`Página ${data.pageNumber}`, pageWidth - 15, doc.internal.pageSize.getHeight() - 8, { align: "right" });
        }
    });
    
    doc.save(`ordenes_compra_${now.toISOString().slice(0,19)}.pdf`);
    notifyReportes("success", "Reporte exportado a PDF");
}

function imprimirReporteOrdenes() {
    if (reporteDatosActuales.length === 0) {
        notifyReportes("error", "No hay datos para imprimir");
        return;
    }
    
    const ventana = window.open("", "_blank");
    const fecha = new Date().toLocaleString();
    const logoUrl = window.location.origin + "/static/img/LOGO COMPLETO.png";
    
    const filtrosTexto = [];
    if (reporteFiltrosActuales.proveedor_id) filtrosTexto.push(`Proveedor ID: ${reporteFiltrosActuales.proveedor_id}`);
    if (reporteFiltrosActuales.estado) filtrosTexto.push(`Estado: ${reporteFiltrosActuales.estado}`);
    if (reporteFiltrosActuales.fecha_desde) filtrosTexto.push(`Desde: ${reporteFiltrosActuales.fecha_desde}`);
    if (reporteFiltrosActuales.fecha_hasta) filtrosTexto.push(`Hasta: ${reporteFiltrosActuales.fecha_hasta}`);
    if (reporteFiltrosActuales.costo_min) filtrosTexto.push(`Costo ≥ $${reporteFiltrosActuales.costo_min}`);
    if (reporteFiltrosActuales.costo_max) filtrosTexto.push(`Costo ≤ $${reporteFiltrosActuales.costo_max}`);
    
    ventana.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Reporte de Ordenes de Compra</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
                @media print { body { margin: 0; padding: 20px; } .no-print { display: none; } }
                body { font-family: 'Manrope', sans-serif; margin: 20px; padding: 20px; background: white; }
                h1 { font-family: 'Space Grotesk', sans-serif; font-size: 24px; text-align: center; border-bottom: 3px solid #f3c500; padding-bottom: 10px; }
                .logo { text-align: center; margin-bottom: 20px; }
                .logo img { height: 50px; }
                .info { text-align: center; margin-bottom: 20px; color: #666; font-size: 12px; }
                .filters { background: #f8f9fa; padding: 10px; margin-bottom: 20px; border-left: 4px solid #f3c500; font-size: 12px; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background: #121212; color: white; font-weight: bold; }
                tr:nth-child(even) { background: #f8f9fa; }
                .footer { margin-top: 30px; text-align: center; font-size: 10px; color: #666; border-top: 1px solid #ddd; padding-top: 10px; }
                .btn-print { background: #f3c500; border: none; padding: 10px 20px; cursor: pointer; margin-bottom: 20px; }
                .status-pendiente { color: #f59e0b; font-weight: bold; }
                .status-completada { color: #10b981; font-weight: bold; }
                .status-anulada { color: #dc2626; font-weight: bold; }
            </style>
        </head>
        <body>
            <button class="btn-print no-print" onclick="window.print()">Imprimir</button>
            <div class="logo"><img src="${logoUrl}" alt="ItuAccesorio" onerror="this.style.display='none'"></div>
            <h1>REPORTE DE ORDENES DE COMPRA</h1>
            <div class="info">Generado: ${fecha} • Total órdenes: ${reporteDatosActuales.length}</div>
            ${filtrosTexto.length ? `<div class="filters"><strong>Filtros:</strong> ${filtrosTexto.join(" • ")}</div>` : ""}
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Proveedor</th>
                        <th>Fecha</th>
                        <th>Estado</th>
                        <th>Costo</th>
                        <th>Recibido por</th>
                    </tr>
                </thead>
                <tbody>
                    ${reporteDatosActuales.map(p => {
                        let estadoClass = "";
                        if (p.Estado === "Pendiente") estadoClass = "status-pendiente";
                        else if (p.Estado === "Completada") estadoClass = "status-completada";
                        else if (p.Estado === "Anulada") estadoClass = "status-anulada";
                        return `
                            <tr>
                                <td>${escapeHtmlReportes(p.ID_orden_c || "-")}</td>
                                <td><strong>${escapeHtmlReportes(p.N_proveedor || "-")}</strong></td>
                                <td>${escapeHtmlReportes(p.Fecha_o || "-")}</td>
                                <td class="${estadoClass}">${escapeHtmlReportes(p.Estado || "Pendiente")}</td>
                                <td>$${Number(p.Costo_venta || 0).toLocaleString("es-VE")}</td>
                                <td>${escapeHtmlReportes(p.Recibido_por || "-")}</td>
                            </tr>
                        `;
                    }).join("")}
                </tbody>
            </table>
            <div class="footer">ItuAccesorio System - Reporte Generado Exclusivamente Para ituaccesorio</div>
        </body>
        </html>
    `);
    ventana.document.close();
}

// Eventos de reportes
if (btnReportes) {
    btnReportes.addEventListener("click", async () => {
        limpiarFiltrosReporte();
        await cargarProveedoresReporte();
        if (reportePreview) reportePreview.style.display = "none";
        if (btnExportarExcel) btnExportarExcel.disabled = true;
        if (btnExportarPdf) btnExportarPdf.disabled = true;
        if (btnImprimir) btnImprimir.disabled = true;
        if (window.UiModal && typeof window.UiModal.openById === "function") {
            window.UiModal.openById("modal-reportes");
        } else if (modalReportes) {
            modalReportes.hidden = false;
            modalReportes.setAttribute("aria-hidden", "false");
        }
    });
}

if (btnGenerarReporte) btnGenerarReporte.addEventListener("click", generarReporteOrdenes);
if (btnLimpiarFiltrosReporte) btnLimpiarFiltrosReporte.addEventListener("click", limpiarFiltrosReporte);
if (btnExportarExcel) btnExportarExcel.addEventListener("click", exportarOrdenesExcel);
if (btnExportarPdf) btnExportarPdf.addEventListener("click", exportarOrdenesPdf);
if (btnImprimir) btnImprimir.addEventListener("click", imprimirReporteOrdenes);

if (modalReportes) {
    modalReportes.addEventListener("click", (event) => {
        const target = event.target;
        if (!(target instanceof HTMLElement)) return;

        if (target.dataset.modalClose === "true") {
            if (window.UiModal && typeof window.UiModal.closeById === "function") {
                window.UiModal.closeById("modal-reportes");
            } else {
                modalReportes.hidden = true;
                modalReportes.setAttribute("aria-hidden", "true");
            }
            return;
        }

        if (target === modalReportes) {
            if (window.UiModal && typeof window.UiModal.closeById === "function") {
                window.UiModal.closeById("modal-reportes");
            } else {
                modalReportes.hidden = true;
                modalReportes.setAttribute("aria-hidden", "true");
            }
        }
    });
}

document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    if (window.UiModal && typeof window.UiModal.closeById === "function") {
        window.UiModal.closeById("modal-reportes");
    } else if (modalReportes && !modalReportes.hidden) {
        modalReportes.hidden = true;
        modalReportes.setAttribute("aria-hidden", "true");
    }
});
});
