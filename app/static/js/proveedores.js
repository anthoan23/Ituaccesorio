/* global UiModal */

(function () {
  'use strict';

  const state = {
    proveedores: [],
    currentProveedorId: null,
    modelos: null,
    productosCrear: [],
  };

  function getCsrfToken() {
    const input = document.querySelector('input[name="_csrf_token"]');
    return input ? input.value : '';
  }

  function getAccessToken() {
    // Si el backend usa JWT en cookie, no hace falta header.
    // Si el frontend guarda un token, intenta leerlo.
    return (
      localStorage.getItem('access_token') ||
      localStorage.getItem('token') ||
      sessionStorage.getItem('access_token') ||
      sessionStorage.getItem('token') ||
      ''
    );
  }

  async function fetchJson(url, options = {}) {
    const headers = new Headers(options.headers || {});
    headers.set('Accept', 'application/json');

    if (options.body && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }

    const csrf = getCsrfToken();
    if (csrf) {
      headers.set('X-CSRFToken', csrf);
    }

    const token = getAccessToken();
    if (token && !headers.has('Authorization')) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    const res = await fetch(url, {
      credentials: 'same-origin',
      ...options,
      headers,
    });

    const contentType = res.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');

    const payload = isJson ? await res.json() : await res.text();

    if (!res.ok) {
      const msg = isJson
        ? (payload && (payload.error || payload.message)) || JSON.stringify(payload)
        : String(payload || res.statusText);
      throw new Error(msg || `HTTP ${res.status}`);
    }

    return payload;
  }

  function escapeHtml(value) {
    return String(value ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function iconEye() {
    return `
      <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path d="M12 5c-7 0-10 7-10 7s3 7 10 7 10-7 10-7-3-7-10-7Zm0 12a5 5 0 1 1 0-10 5 5 0 0 1 0 10Zm0-2.7a2.3 2.3 0 1 0 0-4.6 2.3 2.3 0 0 0 0 4.6Z" fill="currentColor"/>
      </svg>`;
  }

  function iconPencil() {
    return `
      <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25Zm2.92 2.83H5v-.92l9.06-9.06.92.92L5.92 20.08ZM20.71 7.04a1 1 0 0 0 0-1.41L18.37 3.29a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83Z" fill="currentColor"/>
      </svg>`;
  }

  function iconTrash() {
    return `
      <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path d="M9 3h6l1 2h4v2H4V5h4l1-2Zm1 6h2v9h-2V9Zm4 0h2v9h-2V9ZM7 9h2v9H7V9Z" fill="currentColor"/>
      </svg>`;
  }

  function findModeloById(idModelo) {
    if (!Array.isArray(state.modelos)) return null;
    return state.modelos.find((m) => String(m?.id ?? m?.ID_modelo) === String(idModelo)) || null;
  }

  function $id(id) {
    return document.getElementById(id);
  }

  function openModal(id) {
    if (window.UiModal && typeof window.UiModal.openById === 'function') {
      window.UiModal.openById(id);
      return;
    }

    // Fallback básico
    const el = $id(id);
    if (el) {
      el.hidden = false;
      el.setAttribute('aria-hidden', 'false');
    }
  }

  function closeModal(id) {
    if (window.UiModal && typeof window.UiModal.closeById === 'function') {
      window.UiModal.closeById(id);
      return;
    }

    const el = $id(id);
    if (el) {
      el.hidden = true;
      el.setAttribute('aria-hidden', 'true');
    }
  }

  function formatMoney(value) {
    const n = Number(value);
    if (!Number.isFinite(n)) return '';
    return n.toLocaleString('es-VE');
  }

  function normalizeProveedor(p) {
    return {
      id: p?.ID_proveedor ?? p?.id ?? '',
      nombre: p?.N_proveedor ?? p?.nombre ?? '',
      tipo: p?.Tipo ?? p?.tipo ?? '',
      celular: p?.celular ?? p?.Celular ?? '',
      correo: p?.correo ?? p?.Correo ?? '',
      direccion: p?.direccion ?? p?.Direccion ?? '',
      limite_credito: p?.limite_credito ?? p?.Limite_credito ?? '',
    };
  }

  function renderTablaProveedores(proveedores) {
    const tbody = $id('tabla-proveedores');
    if (!tbody) return;

    if (!proveedores.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" class="table__empty">No hay proveedores para mostrar.</td>
        </tr>`;
      return;
    }

    tbody.innerHTML = proveedores
      .map((raw) => {
        const p = normalizeProveedor(raw);
        const id = escapeHtml(p.id);
        const nombre = escapeHtml(p.nombre);
        const tipo = escapeHtml(p.tipo);
        const celular = escapeHtml(p.celular);
        const direccion = escapeHtml(p.direccion);

        return `
          <tr>
            <td><span class="chip">${id}</span></td>
            <td>${nombre}</td>
            <td>${tipo}</td>
            <td>${celular}</td>
            <td>${direccion}</td>
            <td class="table__actions">
              <div class="row-actions" aria-label="Acciones">
                <button class="icon-action" type="button" data-action="ver" data-id="${id}" aria-label="Ver">${iconEye()}</button>
                <button class="icon-action" type="button" data-action="editar" data-id="${id}" aria-label="Modificar">${iconPencil()}</button>
                <button class="icon-action icon-action--danger" type="button" data-action="eliminar" data-id="${id}" aria-label="Eliminar">${iconTrash()}</button>
              </div>
            </td>
          </tr>`;
      })
      .join('');
  }

  async function cargarProveedores(q = '') {
    const url = q ? `/api/proveedores?q=${encodeURIComponent(q)}` : '/api/proveedores';
    const data = await fetchJson(url, { method: 'GET' });
    state.proveedores = Array.isArray(data?.proveedores)
      ? data.proveedores
      : Array.isArray(data)
        ? data
        : [];
    renderTablaProveedores(state.proveedores);
  }

  async function cargarModelos() {
    if (state.modelos) return state.modelos;
    const data = await fetchJson('/api/proveedores/modelos', { method: 'GET' });
    state.modelos = Array.isArray(data?.modelos) ? data.modelos : Array.isArray(data) ? data : [];
    return state.modelos;
  }

  function fillSelectModelos(selectEl, modelos) {
    if (!selectEl) return;

    const options = [`<option value="">Selecciona un producto</option>`];
    for (const m of modelos) {
      const id = escapeHtml(m?.ID_modelo ?? m?.id ?? '');
      const nombre = escapeHtml(m?.N_modelo ?? m?.nombre ?? '');
      options.push(`<option value="${id}">${nombre}</option>`);
    }
    selectEl.innerHTML = options.join('');
  }

  function getFormValue(id) {
    const el = $id(id);
    return el ? el.value : '';
  }

  function setValue(id, value) {
    const el = $id(id);
    if (el) el.value = value ?? '';
  }

  function setText(id, value) {
    const el = $id(id);
    if (el) el.textContent = value ?? '';
  }

  async function abrirVerProveedor(id) {
    state.currentProveedorId = id;
    const data = await fetchJson(`/api/proveedores/${encodeURIComponent(id)}`, { method: 'GET' });
    const p = normalizeProveedor(data?.proveedor ?? data);

    setText('v-id', p.id);
    setText('v-nombre', p.nombre);
    setText('v-tipo', p.tipo);
    setText('v-celular', p.celular);
    setText('v-correo', p.correo);
    setText('v-limite', p.limite_credito !== '' ? formatMoney(p.limite_credito) : '');
    setText('v-direccion', p.direccion);

    await cargarProductosProveedorVer(p.id, data?.productos);
    openModal('modal-proveedor-ver');
  }

  async function abrirEditarProveedor(id) {
    state.currentProveedorId = id;
    const data = await fetchJson(`/api/proveedores/${encodeURIComponent(id)}`, { method: 'GET' });
    const p = normalizeProveedor(data?.proveedor ?? data);

    setValue('e-id-hidden', p.id);
    setValue('e-id', p.id);
    setValue('e-nombre', p.nombre);
    setValue('e-tipo', p.tipo);
    setValue('e-celular', p.celular);
    setValue('e-correo', p.correo);
    setValue('e-direccion', p.direccion);
    setValue('e-limite', p.limite_credito);

    await cargarProductosProveedorEditar(p.id, data?.productos);
    openModal('modal-proveedor-editar');
  }

  function abrirEliminarProveedor(id) {
    state.currentProveedorId = id;
    openModal('modal-proveedor-eliminar');
  }

  function renderProductosEditar(items) {
    const tbody = $id('tabla-proveedor-productos');
    if (!tbody) return;

    if (!items.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="4" class="table__empty">Este proveedor no tiene productos asignados.</td>
        </tr>`;
      return;
    }

    tbody.innerHTML = items
      .map((it) => {
        const idModelo = escapeHtml(it?.ID_modelo ?? it?.id_modelo ?? it?.id ?? '');
        const modelo = escapeHtml(it?.modelo_nombre ?? it?.N_modelo ?? it?.modelo ?? '');
        const marca = escapeHtml(it?.marca_nombre ?? it?.N_marca ?? it?.marca ?? '');
        const clase = escapeHtml(it?.clase_nombre ?? it?.N_clase ?? it?.clase ?? '');
        const costo = it?.costo ?? it?.Costo ?? '';

        return `
          <tr>
            <td>${modelo}</td>
            <td>${marca}</td>
            <td>${clase}</td>
            <td class="col-cost">
              <input class="table-input" type="number" inputmode="numeric" min="0" step="1" value="${escapeHtml(costo)}" data-action="guardar-costo" data-id-modelo="${idModelo}" aria-label="Costo ${modelo}">
            </td>
          </tr>`;
      })
      .join('');
  }

  function renderProductosCrear() {
    const tbody = $id('tabla-proveedor-productos-crear');
    if (!tbody) return;

    if (!state.productosCrear.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" class="table__empty">No has agregado productos iniciales.</td>
        </tr>`;
      return;
    }

    tbody.innerHTML = state.productosCrear
      .map((it) => {
        const idModelo = escapeHtml(it.id_modelo);
        const modelo = escapeHtml(it.modelo_nombre || '');
        const marca = escapeHtml(it.marca_nombre || '');
        const clase = escapeHtml(it.clase_nombre || '');
        const costo = escapeHtml(it.costo);

        return `
          <tr>
            <td>${modelo}</td>
            <td>${marca}</td>
            <td>${clase}</td>
            <td class="col-cost">${formatMoney(costo)} $</td>
            <td class="table__actions">
              <div class="row-actions" aria-label="Acciones">
                <button class="icon-action icon-action--danger" type="button" data-action="quitar-producto-crear" data-id-modelo="${idModelo}" aria-label="Quitar">${iconTrash()}</button>
              </div>
            </td>
          </tr>`;
      })
      .join('');
  }

  function renderProductosVer(items) {
    const tbody = $id('tabla-proveedor-productos-ver');
    if (!tbody) return;

    if (!items.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="4" class="table__empty">Sin productos.</td>
        </tr>`;
      return;
    }

    tbody.innerHTML = items
      .map((it) => {
        const modelo = escapeHtml(it?.modelo_nombre ?? it?.N_modelo ?? it?.modelo ?? '');
        const marca = escapeHtml(it?.marca_nombre ?? it?.N_marca ?? it?.marca ?? '');
        const clase = escapeHtml(it?.clase_nombre ?? it?.N_clase ?? it?.clase ?? '');
        const costo = it?.costo ?? it?.Costo ?? '';

        return `
          <tr>
            <td>${modelo}</td>
            <td>${marca}</td>
            <td>${clase}</td>
            <td class="col-cost">${formatMoney(costo)} $</td>
          </tr>`;
      })
      .join('');
  }

  async function cargarProductosProveedorEditar(idProveedor, productosPreCargados = null) {
    if (Array.isArray(productosPreCargados)) {
      renderProductosEditar(productosPreCargados);
      return;
    }
    const data = await fetchJson(`/api/proveedores/${encodeURIComponent(idProveedor)}/productos`, { method: 'GET' });
    const items = Array.isArray(data?.productos) ? data.productos : Array.isArray(data) ? data : [];
    renderProductosEditar(items);
  }

  async function cargarProductosProveedorVer(idProveedor, productosPreCargados = null) {
    if (Array.isArray(productosPreCargados)) {
      renderProductosVer(productosPreCargados);
      return;
    }
    const data = await fetchJson(`/api/proveedores/${encodeURIComponent(idProveedor)}/productos`, { method: 'GET' });
    const items = Array.isArray(data?.productos) ? data.productos : Array.isArray(data) ? data : [];
    renderProductosVer(items);
  }

  async function crearProveedorFromForm() {
    const productos = state.productosCrear.map((it) => ({
      id_modelo: Number(it.id_modelo),
      costo: it.costo === '' ? null : Number(it.costo),
    }));

    const payload = {
      id: getFormValue('c-id') ? Number(getFormValue('c-id')) : null,
      nombre: getFormValue('c-nombre').trim(),
      tipo: getFormValue('c-tipo') || null,
      celular: getFormValue('c-celular') || null,
      correo: getFormValue('c-correo') || null,
      direccion: getFormValue('c-direccion') || null,
      limite_credito: getFormValue('c-limite') ? Number(getFormValue('c-limite')) : null,
      productos,
    };

    await fetchJson('/api/proveedores', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async function editarProveedorFromForm() {
    const id = getFormValue('e-id-hidden');
    const payload = {
      id: id ? Number(id) : null,
      nombre: getFormValue('e-nombre').trim(),
      tipo: getFormValue('e-tipo') || null,
      celular: getFormValue('e-celular') || null,
      correo: getFormValue('e-correo') || null,
      direccion: getFormValue('e-direccion') || null,
      limite_credito: getFormValue('e-limite') ? Number(getFormValue('e-limite')) : null,
    };

    await fetchJson(`/api/proveedores/${encodeURIComponent(id)}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  }

  async function eliminarProveedorActual() {
    const id = state.currentProveedorId;
    if (!id) return;

    await fetchJson(`/api/proveedores/${encodeURIComponent(id)}`, { method: 'DELETE' });
  }

  async function agregarProductoProveedorFromForm() {
    const idProveedor = state.currentProveedorId;
    const idModelo = getFormValue('ap-id-modelo');
    const costo = getFormValue('ap-costo');

    if (!idProveedor) throw new Error('Proveedor no seleccionado.');
    if (!idModelo) throw new Error('Selecciona un producto.');

    const payload = {
      id_modelo: Number(idModelo),
      costo: Number(costo),
    };

    await fetchJson(`/api/proveedores/${encodeURIComponent(idProveedor)}/productos`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  function agregarProductoCrearFromForm() {
    const idModelo = getFormValue('cp-id-modelo');
    const costo = getFormValue('cp-costo');

    if (!idModelo) throw new Error('Selecciona un producto.');
    if (costo === '') throw new Error('El costo es obligatorio.');

    const modelo = findModeloById(idModelo);
    const existenteIdx = state.productosCrear.findIndex((it) => String(it.id_modelo) === String(idModelo));

    const item = {
      id_modelo: Number(idModelo),
      costo: Number(costo),
      modelo_nombre: modelo?.nombre ?? modelo?.N_modelo ?? '',
      marca_nombre: modelo?.marca_nombre ?? modelo?.N_marca ?? '',
      clase_nombre: modelo?.clase_nombre ?? modelo?.N_clase ?? '',
    };

    if (existenteIdx >= 0) {
      state.productosCrear[existenteIdx] = item;
    } else {
      state.productosCrear.push(item);
    }

    renderProductosCrear();
  }

  async function guardarCostoProductoProveedor(idModelo, costo) {
    const idProveedor = state.currentProveedorId;
    if (!idProveedor) return;

    const payload = {
      id_modelo: Number(idModelo),
      costo: costo === '' ? null : Number(costo),
    };

    await fetchJson(`/api/proveedores/${encodeURIComponent(idProveedor)}/productos`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  function bindEvents() {
    const btnAplicar = $id('btn-aplicar');
    const btnLimpiar = $id('btn-limpiar');
    const inputTexto = $id('f-texto');

    btnAplicar?.addEventListener('click', async () => {
      try {
        await cargarProveedores((inputTexto?.value || '').trim());
      } catch (e) {
        alert(e.message);
      }
    });

    btnLimpiar?.addEventListener('click', async () => {
      try {
        if (inputTexto) inputTexto.value = '';
        await cargarProveedores('');
      } catch (e) {
        alert(e.message);
      }
    });

    inputTexto?.addEventListener('keydown', async (ev) => {
      if (ev.key !== 'Enter') return;
      ev.preventDefault();
      try {
        await cargarProveedores((inputTexto.value || '').trim());
      } catch (e) {
        alert(e.message);
      }
    });

    const tbody = $id('tabla-proveedores');
    tbody?.addEventListener('click', async (ev) => {
      const btn = ev.target?.closest?.('button[data-action][data-id]');
      if (!btn) return;

      const action = btn.getAttribute('data-action');
      const id = btn.getAttribute('data-id');
      if (!action || !id) return;

      try {
        if (action === 'ver') await abrirVerProveedor(id);
        if (action === 'editar') await abrirEditarProveedor(id);
        if (action === 'eliminar') abrirEliminarProveedor(id);
      } catch (e) {
        alert(e.message);
      }
    });

    const formCrear = $id('form-proveedor-crear');
    formCrear?.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      try {
        await crearProveedorFromForm();
        closeModal('modal-proveedor-crear');
        await cargarProveedores((inputTexto?.value || '').trim());
        formCrear.reset();
        state.productosCrear = [];
        renderProductosCrear();
      } catch (e) {
        alert(e.message);
      }
    });

    const formAgregarProductoCrear = $id('form-proveedor-agregar-producto-crear');
    formAgregarProductoCrear?.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      try {
        agregarProductoCrearFromForm();
        closeModal('modal-proveedor-agregar-producto-crear');
        formAgregarProductoCrear.reset();
      } catch (e) {
        alert(e.message);
      }
    });

    const tbodyProductosCrear = $id('tabla-proveedor-productos-crear');
    tbodyProductosCrear?.addEventListener('click', (ev) => {
      const btn = ev.target?.closest?.('button[data-action="quitar-producto-crear"][data-id-modelo]');
      if (!btn) return;
      const idModelo = btn.getAttribute('data-id-modelo');
      if (!idModelo) return;
      state.productosCrear = state.productosCrear.filter((it) => String(it.id_modelo) !== String(idModelo));
      renderProductosCrear();
    });

    const formEditar = $id('form-proveedor-editar');
    formEditar?.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      try {
        await editarProveedorFromForm();
        closeModal('modal-proveedor-editar');
        await cargarProveedores((inputTexto?.value || '').trim());
      } catch (e) {
        alert(e.message);
      }
    });

    const btnConfirmarEliminar = $id('btn-confirmar-eliminar');
    btnConfirmarEliminar?.addEventListener('click', async () => {
      try {
        await eliminarProveedorActual();
        closeModal('modal-proveedor-eliminar');
        await cargarProveedores((inputTexto?.value || '').trim());
      } catch (e) {
        alert(e.message);
      }
    });

    const formAgregarProducto = $id('form-proveedor-agregar-producto');
    formAgregarProducto?.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      try {
        await agregarProductoProveedorFromForm();
        closeModal('modal-proveedor-agregar-producto');
        await cargarProductosProveedorEditar(state.currentProveedorId);
        formAgregarProducto.reset();
      } catch (e) {
        alert(e.message);
      }
    });

    const tbodyProductosEditar = $id('tabla-proveedor-productos');
    tbodyProductosEditar?.addEventListener('change', async (ev) => {
      const input = ev.target?.closest?.('input[data-action="guardar-costo"][data-id-modelo]');
      if (!input) return;

      const idModelo = input.getAttribute('data-id-modelo');
      const costo = input.value;

      if (!idModelo) return;

      try {
        await guardarCostoProductoProveedor(idModelo, costo);
      } catch (e) {
        alert(e.message);
      }
    });

    // Cuando se abra el modal de agregar producto, precargar modelos y setear proveedor.
    document.addEventListener('click', async (ev) => {
      const btn = ev.target?.closest?.('[data-open-modal="modal-proveedor-agregar-producto"]');
      if (!btn) return;

      try {
        setValue('ap-proveedor-id', state.currentProveedorId || '');
        const modelos = await cargarModelos();
        fillSelectModelos($id('ap-id-modelo'), modelos);
      } catch (e) {
        alert(e.message);
      }
    });

    document.addEventListener('click', async (ev) => {
      const btn = ev.target?.closest?.('[data-open-modal="modal-proveedor-agregar-producto-crear"]');
      if (!btn) return;

      try {
        const modelos = await cargarModelos();
        fillSelectModelos($id('cp-id-modelo'), modelos);
      } catch (e) {
        alert(e.message);
      }
    });
  }

  async function init() {
    bindEvents();
    renderProductosCrear();
    try {
      await cargarProveedores('');
    } catch (e) {
      // No rompas la página si no hay sesión
      console.error(e);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    void init();
  }
})();
