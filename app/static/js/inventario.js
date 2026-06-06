(() => {
	"use strict";

	const csrfToken = document.querySelector("input[name='_csrf_token']")?.value || "";

	function getAuthToken() {
		const fromLocal = window.localStorage ? window.localStorage.getItem("access_token") : "";
		if (fromLocal) return fromLocal;
		const fromSession = window.sessionStorage ? window.sessionStorage.getItem("access_token") : "";
		if (fromSession) return fromSession;
		return "";
	}

	async function fetchJson(url, options = {}) {
		const authToken = getAuthToken();
		const isFormData = typeof FormData !== "undefined" && options.body instanceof FormData;
		const response = await fetch(url, {
			headers: {
				Accept: "application/json",
				...(options.method && options.method !== "GET" && !isFormData ? { "Content-Type": "application/json" } : {}),
				...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
				...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
				...(options.headers || {}),
			},
			credentials: "same-origin",
			...options,
		});

		const data = await response.json().catch(() => ({}));
		if (!response.ok || data?.success === false) {
			throw new Error(data?.error || `HTTP ${response.status}`);
		}
		return data;
	}

	const formatMoney = (value) => {
		if (value === null || value === undefined || value === '') return '-';
		const num = Number(value);
		if (Number.isNaN(num)) return String(value);
		try {
			return `$${new Intl.NumberFormat('es-VE').format(num)}`;
		} catch (e) {
			return `$${num.toLocaleString()}`;
		}
	};

	const normalizeText = (value) => {
		if (value === null || value === undefined) return '-';
		const text = String(value).trim();
		return text === '' ? '-' : text;
	};

	const escapeHtml = (value) => String(value ?? '').replace(/[&<>"]|'/g, (char) => ({
		'&': '&amp;',
		'<': '&lt;',
		'>': '&gt;',
		'"': '&quot;',
		"'": '&#39;',
	}[char]));

	const computeStatus = (existencia) => {
		const qty = Number(existencia);
		if (!Number.isFinite(qty)) {
			return { badgeClass: 'badge--warn', statusClass: 'status--warn', label: 'Revisar' };
		}
		if (qty <= 10) return { badgeClass: 'badge--warn', statusClass: 'status--warn', label: qty <= 0 ? 'Sin stock' : 'Bajo stock' };
		return { badgeClass: 'badge--good', statusClass: 'status--good', label: qty >= 30 ? 'Alto stock' : 'Disponible' };
	};

	const setText = (id, value) => {
		const el = document.getElementById(id);
		if (el) el.textContent = String(value);
	};

	const renderTable = (rows) => {
		const tbody = document.getElementById('inventario-tbody');
		if (!tbody) return;

		tbody.innerHTML = '';

		if (!Array.isArray(rows) || rows.length === 0) {
			const tr = document.createElement('tr');
			tr.innerHTML = '<td colspan="7">No hay datos de inventario.</td>';
			tbody.appendChild(tr);
			return;
		}

		const frag = document.createDocumentFragment();
		for (const item of rows) {
			const foto = normalizeText(item?.Foto_inventario ?? item?.foto_inventario);
			const tipo = normalizeText(item?.tipo);
			const marca = normalizeText(item?.N_marca);
			const modelo = normalizeText(item?.N_modelo);
			const existencia = item?.Existencia;
			const costo = item?.Costo_venta;

			const status = computeStatus(existencia);
			const imageCell = foto !== '-' ? `<img class="inventory-thumb" src="${escapeHtml(foto)}" alt="${escapeHtml(modelo)}">` : '<span class="inventory-thumb inventory-thumb--empty">Sin foto</span>';
			const tr = document.createElement('tr');
			tr.innerHTML = `
				<td>${imageCell}</td>
				<td>${escapeHtml(tipo)}</td>
				<td>${escapeHtml(marca)}</td>
				<td>${escapeHtml(modelo)}</td>
				<td><span class="badge ${status.badgeClass}">${escapeHtml(normalizeText(existencia))}</span></td>
				<td>${formatMoney(costo)}</td>
				<td><span class="status ${status.statusClass}">${escapeHtml(status.label)}</span></td>
			`;
			frag.appendChild(tr);
		}
		tbody.appendChild(frag);
	};

	const renderStats = (rows) => {
		const tipos = new Set();
		const marcas = new Set();
		const modelos = new Set();
		let piezas = 0;

		for (const item of rows || []) {
			if (item?.tipo) tipos.add(String(item.tipo));
			if (item?.N_marca) marcas.add(String(item.N_marca));
			if (item?.N_modelo) modelos.add(String(item.N_modelo));
			const qty = Number(item?.Existencia);
			if (Number.isFinite(qty)) piezas += qty;
		}

		setText('inv-stat-clases', tipos.size);
		setText('inv-stat-marcas', marcas.size);
		setText('inv-stat-modelos', modelos.size);
		setText('inv-stat-piezas', piezas);
	};

	const setNote = (text) => {
		const el = document.getElementById('inventario-note');
		if (el) el.textContent = text;
	};

	const renderSelect = (select, items, placeholder) => {
		if (!select) return;
		select.innerHTML = '';
		const opt = document.createElement('option');
		opt.value = '';
		opt.textContent = placeholder;
		select.appendChild(opt);

		(items || []).forEach((item) => {
			const option = document.createElement('option');
			option.value = String(item.id);
			option.textContent = String(item.nombre);
			select.appendChild(option);
		});
	};

	const parseIntSafe = (value) => {
		const str = String(value ?? '').trim();
		if (!str) return NaN;
		const cleaned = str.replace(/[^0-9-]/g, '');
		return Number.parseInt(cleaned, 10);
	};

	const parseDecimalSafe = (value) => {
		const str = String(value ?? '').trim();
		if (!str) return NaN;
		// Permite 12,50 o 12.50
		const cleaned = str.replace(/[^0-9.,-]/g, '').replace(',', '.');
		return Number.parseFloat(cleaned);
	};

	const stripAccents = (value) => {
		try {
			return String(value ?? '')
				.normalize('NFD')
				.replace(/[\u0300-\u036f]/g, '');
		} catch {
			return String(value ?? '');
		}
	};

	const normalizeKey = (value) => stripAccents(value).toLowerCase().trim();

	let lastRows = [];
	let activeFilter = { kind: 'all', value: '' };

	const filterRows = (rows) => {
		const list = Array.isArray(rows) ? rows : [];
		if (activeFilter.kind === 'all') return list;
		if (activeFilter.kind === 'tipo') {
			const target = normalizeKey(activeFilter.value);
			return list.filter((x) => normalizeKey(x?.tipo) === target);
		}
		if (activeFilter.kind === 'low') {
			return list.filter((x) => {
				const qty = Number(x?.Existencia);
				return Number.isFinite(qty) && qty <= 10;
			});
		}
		return list;
	};

	const getFilterLabel = () => {
		if (activeFilter.kind === 'all') return 'Todos';
		if (activeFilter.kind === 'tipo') return String(activeFilter.value || '');
		if (activeFilter.kind === 'low') return 'Bajo stock';
		return 'Filtro';
	};

	const applyFilterAndRender = () => {
		const filtered = filterRows(lastRows);
		renderTable(filtered);
		renderStats(filtered);
		setNote(`Mostrando ${filtered.length} de ${lastRows.length} registros · ${getFilterLabel()}.`);
	};

	const loadInventario = async () => {
		try {
			setNote('Cargando datos desde el backend…');
			const data = await fetchJson('/api/inventario', { method: 'GET' });
			const rows = Array.isArray(data?.inventario) ? data.inventario : [];
			lastRows = rows;
			applyFilterAndRender();
		} catch (err) {
			console.error('Error cargando inventario:', err);
			const message = String(err?.message || err || '').toLowerCase().includes('401')
				? 'Autenticación requerida para ver inventario.'
				: 'Error cargando inventario.';
			setNote(message);
			renderTable([]);
			renderStats([]);
		}
	};

	const initChips = () => {
		const chipsWrap = document.querySelector('.hero__chips');
		if (!chipsWrap) return;
		const chips = Array.from(chipsWrap.querySelectorAll('.chip'));
		if (chips.length === 0) return;

		const setActiveChip = (chip) => {
			chips.forEach((c) => {
				const isActive = c === chip;
				c.classList.toggle('chip--active', isActive);
				c.setAttribute('aria-pressed', isActive ? 'true' : 'false');
			});
		};

		const activate = (chip) => {
			const kind = String(chip?.dataset?.filter || 'all');
			const value = String(chip?.dataset?.value || '');
			activeFilter = { kind, value };
			setActiveChip(chip);
			applyFilterAndRender();
		};

		chips.forEach((chip) => {
			chip.addEventListener('click', () => activate(chip));
			chip.addEventListener('keydown', (e) => {
				if (e.key === 'Enter' || e.key === ' ') {
					e.preventDefault();
					activate(chip);
				}
			});
		});

		const initial = chips.find((c) => c.classList.contains('chip--active')) || chips[0];
		if (initial) activate(initial);
	};

	const initFormularioStock = async () => {
		const form = document.getElementById('inventario-form');
		const selectClase = document.getElementById('inv-clase');
		const selectMarca = document.getElementById('inv-marca');
		const selectModelo = document.getElementById('inv-modelo');
		const inputFoto = document.getElementById('inv-foto');
		const inputExistencia = document.getElementById('inv-existencia');
		const inputCosto = document.getElementById('inv-costo');
		const btnLimpiar = document.getElementById('inv-limpiar');
		const btnGuardar = document.getElementById('inv-guardar');
		if (!form || !selectClase || !selectMarca || !selectModelo || !btnGuardar) return;

		renderSelect(selectClase, [], 'Cargando clases…');
		renderSelect(selectMarca, [], 'Selecciona una marca');
		renderSelect(selectModelo, [], 'Selecciona un producto');

		try {
			const dataClases = await fetchJson('/api/productos/clases', { method: 'GET' });
			const clases = Array.isArray(dataClases?.clases) ? dataClases.clases : [];
			renderSelect(selectClase, clases, 'Selecciona una clase');
		} catch (err) {
			console.error('Error cargando clases:', err);
			renderSelect(selectClase, [], 'No se pudieron cargar clases');
		}

		const cargarMarcas = async (idClase) => {
			try {
				renderSelect(selectMarca, [], 'Cargando marcas…');
				renderSelect(selectModelo, [], 'Selecciona un producto');
				if (!idClase) {
					renderSelect(selectMarca, [], 'Selecciona una marca');
					return;
				}
				const data = await fetchJson(`/api/productos/marcas?clase_id=${encodeURIComponent(String(idClase))}`, { method: 'GET' });
				const marcas = Array.isArray(data?.marcas) ? data.marcas : [];
				renderSelect(selectMarca, marcas, 'Selecciona una marca');
			} catch (err) {
				console.error('Error cargando marcas:', err);
				renderSelect(selectMarca, [], 'No se pudieron cargar marcas');
			}
		};

		const cargarProductos = async (idMarca) => {
			try {
				renderSelect(selectModelo, [], 'Cargando productos…');
				if (!idMarca) {
					renderSelect(selectModelo, [], 'Selecciona un producto');
					return;
				}
				const idClase = String(selectClase?.value || '');
				const qs = new URLSearchParams();
				qs.set('marca_id', String(idMarca));
				if (idClase) qs.set('clase_id', String(idClase));
				const data = await fetchJson(`/api/productos/modelos?${qs.toString()}`, { method: 'GET' });
				const productos = Array.isArray(data?.modelos) ? data.modelos : [];
				renderSelect(selectModelo, productos, 'Selecciona un producto');
			} catch (err) {
				console.error('Error cargando productos:', err);
				renderSelect(selectModelo, [], 'No se pudieron cargar productos');
			}
		};

		selectClase.addEventListener('change', () => {
			cargarMarcas(String(selectClase.value || ''));
		});
		selectMarca.addEventListener('change', () => {
			cargarProductos(String(selectMarca.value || ''));
		});

		btnLimpiar?.addEventListener('click', () => {
			form.reset();
			renderSelect(selectMarca, [], 'Selecciona una marca');
			renderSelect(selectModelo, [], 'Selecciona un producto');
			setNote('Formulario limpiado.');
		});

		form.addEventListener('submit', async (e) => {
			e.preventDefault();
			const idProducto = String(selectModelo.value || '').trim();
			if (!idProducto) {
				setNote('Selecciona un producto antes de guardar.');
				return;
			}
			if (!inputFoto?.files?.length) {
				setNote('Selecciona una foto antes de guardar.');
				return;
			}

			const existencia = parseIntSafe(inputExistencia?.value);
			const costoVenta = parseDecimalSafe(inputCosto?.value);
			if (!Number.isFinite(existencia) || existencia < 0) {
				setNote('Existencia inválida.');
				return;
			}
			if (!Number.isFinite(costoVenta) || costoVenta < 0) {
				setNote('Costo venta inválido.');
				return;
			}

			const payload = new FormData(form);
			payload.set('id_producto', idProducto);
			payload.set('existencia', String(existencia));
			payload.set('costo_venta', String(inputCosto?.value || '').trim());

			const oldText = btnGuardar.textContent;
			btnGuardar.disabled = true;
			btnGuardar.textContent = 'Guardando…';
			try {
				await fetchJson('/api/inventario/stock', {
					method: 'POST',
					body: payload,
				});
				setNote('Stock guardado correctamente.');
				form.reset();
				renderSelect(selectMarca, [], 'Selecciona una marca');
				renderSelect(selectModelo, [], 'Selecciona un producto');
				window.UiModal?.closeById('modal-inventario-stock');
				await loadInventario();
			} catch (err) {
				console.error('Error guardando stock:', err);
				setNote(`No se pudo guardar stock: ${String(err?.message || err)}`);
			} finally {
				btnGuardar.disabled = false;
				btnGuardar.textContent = oldText;
			}
		});
	};

	document.addEventListener('DOMContentLoaded', () => {
		initChips();
		loadInventario();
		initFormularioStock();
	});
})();
