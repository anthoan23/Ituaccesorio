/* global UiModal, FeedbackModal */

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
      .replaceAll("'", '&#39;');
  }

  // ==================== MODAL DE FEEDBACK (éxito/error) ====================
  function showFeedback(type, message, title) {
    if (window.FeedbackModal && typeof window.FeedbackModal.show === 'function') {
      window.FeedbackModal.show({
        type: type === 'error' ? 'error' : 'success',
        title: title || (type === 'error' ? 'Error' : 'Éxito'),
        message: message,
      });
      return;
    }
    
    // Fallback si no existe FeedbackModal
    const modal = document.getElementById('feedback-modal');
    if (modal) {
      const titleEl = modal.querySelector('#feedback-modal-title');
      const messageEl = document.getElementById('feedback-modal-message');
      const successIcon = modal.querySelector('[data-feedback-icon="success"]');
      const errorIcon = modal.querySelector('[data-feedback-icon="error"]');
      
      if (titleEl) titleEl.textContent = title || (type === 'error' ? 'Error' : 'Éxito');
      if (messageEl) messageEl.textContent = message;
      
      if (type === 'error') {
        if (successIcon) successIcon.setAttribute('hidden', '');
        if (errorIcon) errorIcon.removeAttribute('hidden');
      } else {
        if (successIcon) successIcon.removeAttribute('hidden');
        if (errorIcon) errorIcon.setAttribute('hidden', '');
      }
      
      modal.removeAttribute('hidden');
      modal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      
      setTimeout(() => {
        if (modal && !modal.hasAttribute('hidden')) {
          modal.setAttribute('hidden', '');
          modal.setAttribute('aria-hidden', 'true');
          document.body.style.overflow = '';
        }
      }, 2500);
      
      const closeBtn = modal.querySelector('[data-close-modal]');
      if (closeBtn) {
        const newCloseBtn = closeBtn.cloneNode(true);
        closeBtn.parentNode.replaceChild(newCloseBtn, closeBtn);
        newCloseBtn.addEventListener('click', () => {
          modal.setAttribute('hidden', '');
          modal.setAttribute('aria-hidden', 'true');
          document.body.style.overflow = '';
        });
      }
    } else {
      // Fallback final
      if (type === 'error') alert(message);
      else console.log(message);
    }
  }

  // ==================== MODAL DE CONFIRMACIÓN ====================
  function showConfirmModal(mensaje, onConfirmar, soloInformacion = false, productosRelacionados = []) {
    const modalExistente = document.getElementById('confirmacion-modal-proveedores');
    if (modalExistente) modalExistente.remove();
    
    const esError = soloInformacion && (mensaje.includes('No se puede') || mensaje.includes('productos'));
    const titulo = soloInformacion ? (esError ? "No se puede eliminar" : "Información") : "Confirmar acción";
    const btnTexto = soloInformacion ? "Aceptar" : "Eliminar";
    const btnColor = soloInformacion ? (esError ? "#dc2626" : "#16a34a") : "#dc2626";
    
    let mensajeCompleto = mensaje;
    
    if (productosRelacionados && productosRelacionados.length > 0 && !mensaje.includes('Productos asociados:')) {
      mensajeCompleto += '\n\nProductos asociados:\n';
      productosRelacionados.forEach(p => {
        const nombre = p?.modelo_nombre || p?.nombre || p?.N_modelo || 'Producto sin nombre';
        const id = p?.id_modelo || p?.id_producto || p?.id || 'N/A';
        mensajeCompleto += `• ${nombre} (ID: ${id})\n`;
      });
    }
    
    const modalDiv = document.createElement('div');
    modalDiv.id = 'confirmacion-modal-proveedores';
    modalDiv.className = 'ui-modal';
    modalDiv.setAttribute('data-modal', '');
    modalDiv.setAttribute('hidden', '');
    modalDiv.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;z-index:10001;display:flex;align-items:center;justify-content:center;';
    
    modalDiv.innerHTML = `
      <div class="ui-modal__dialog ui-modal__dialog--sm" role="dialog" aria-modal="true" style="animation:modalFadeIn 0.2s ease-out;margin:1rem;background:white;border-radius:20px;box-shadow:0 25px 50px -12px rgba(0,0,0,0.25);max-width:500px;width:100%;${esError ? 'border-top:4px solid #dc2626' : 'border-top:4px solid #f3c500'}">
        <header class="ui-modal__header" style="display:flex;justify-content:space-between;align-items:center;padding:1rem 1.5rem;border-bottom:1px solid #e5e7eb;">
          <h3 class="ui-modal__title" style="margin:0;font-size:1.25rem;font-weight:600;">${titulo}</h3>
          <button type="button" class="ui-modal__close" data-close-modal aria-label="Cerrar" style="background:none;border:none;font-size:1.5rem;cursor:pointer;">×</button>
        </header>
        <div class="ui-modal__body" style="padding:1.5rem;">
          <div style="white-space:pre-wrap;margin:0;font-size:1rem;color:#121212;line-height:1.5;">${escapeHtml(mensajeCompleto)}</div>
        </div>
        <div class="ui-modal__footer" style="display:flex;gap:0.75rem;justify-content:flex-end;padding:1rem 1.5rem;border-top:1px solid #e5e7eb;">
          ${!soloInformacion ? '<button type="button" class="ui-btn ui-btn--ghost" id="btn-cancelar-confirmacion-proveedores" style="padding:0.5rem 1rem;border:none;border-radius:8px;background:#f3f4f6;color:#121212;font-weight:500;cursor:pointer;">Cancelar</button>' : ''}
          <button type="button" class="ui-btn" id="btn-confirmar-accion-proveedores" style="padding:0.5rem 1rem;border:none;border-radius:8px;background:${btnColor};color:white;font-weight:500;cursor:pointer;">${btnTexto}</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modalDiv);
    document.body.style.overflow = 'hidden';
    
    const cerrarModal = () => {
      modalDiv.remove();
      document.body.style.overflow = '';
    };
    
    if (!soloInformacion) {
      const cancelBtn = document.getElementById('btn-cancelar-confirmacion-proveedores');
      if (cancelBtn) {
        cancelBtn.addEventListener('click', cerrarModal);
      }
    }
    
    const confirmBtn = document.getElementById('btn-confirmar-accion-proveedores');
    if (confirmBtn) {
      confirmBtn.addEventListener('click', async () => {
        cerrarModal();
        if (onConfirmar && !soloInformacion) {
          await onConfirmar();
        }
      });
    }
    
    const closeBtn = modalDiv.querySelector('[data-close-modal]');
    if (closeBtn) {
      closeBtn.addEventListener('click', cerrarModal);
    }
    
    modalDiv.addEventListener('click', (e) => {
      if (e.target === modalDiv) cerrarModal();
    });
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

  // ==================== FUNCIÓN DE ELIMINACIÓN ====================
  async function abrirEliminarProveedor(id) {
    state.currentProveedorId = id;
    
    try {
      const proveedorData = await fetchJson(`/api/proveedores/${encodeURIComponent(id)}`, { method: 'GET' });
      const proveedor = normalizeProveedor(proveedorData?.proveedor ?? proveedorData);
      const nombreProveedor = proveedor.nombre || `ID ${id}`;
      
      const productosData = await fetchJson(`/api/proveedores/${encodeURIComponent(id)}/productos`, { method: 'GET' });
      const productos = Array.isArray(productosData?.productos) ? productosData.productos : 
                        Array.isArray(productosData) ? productosData : [];
      
      if (productos.length > 0) {
        const listaProductos = productos.map(p => {
          const nombreProducto = p?.modelo_nombre || p?.nombre || p?.N_modelo || p?.modelo || 'Producto';
          const costo = p?.costo || p?.Costo || '';
          const costoTexto = costo ? ` (Costo: ${formatMoney(costo)} Bs)` : '';
          return `• ${nombreProducto}${costoTexto}`;
        }).join('\n');
        
        const mensaje = `No se puede eliminar el proveedor "${nombreProveedor}" porque tiene ${productos.length} producto(s) asociados en el inventario.\n\nProductos asociados:\n${listaProductos}`;
        showConfirmModal(mensaje, null, true, []);
      } else {
        showConfirmModal(`¿Seguro que deseas eliminar el proveedor "${nombreProveedor}"? Esta acción no se puede deshacer.`, async () => {
          try {
            await fetchJson(`/api/proveedores/${encodeURIComponent(id)}`, { method: 'DELETE' });
            await cargarProveedores(($id('f-texto')?.value || '').trim());
            showFeedback('success', `Proveedor "${nombreProveedor}" eliminado correctamente.`);
          } catch (e) {
            showFeedback('error', e.message || 'No se pudo eliminar el proveedor.');
          }
        });
      }
    } catch (e) {
      showFeedback('error', e.message || 'No se pudo verificar el estado del proveedor.');
    }
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
              <input class="table-input" type="number" min="0" step="1" value="${escapeHtml(costo)}" data-action="guardar-costo" data-id-modelo="${idModelo}" aria-label="Costo ${modelo}">
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
    
    // ✅ VALIDACIÓN: No permitir costo negativo
    if (costo !== '' && Number(costo) < 0) {
      throw new Error('El costo no puede ser negativo.');
    }

    const payload = {
      id_modelo: Number(idModelo),
      costo: Number(costo),
    };

    await fetchJson(`/api/proveedores/${encodeURIComponent(idProveedor)}/productos`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // ✅ FUNCIÓN MODIFICADA: Agregar validación de costo negativo
  function agregarProductoCrearFromForm() {
    const idModelo = getFormValue('cp-id-modelo');
    const costo = getFormValue('cp-costo');

    if (!idModelo) throw new Error('Selecciona un producto.');
    if (costo === '') throw new Error('El costo es obligatorio.');
    
    // ✅ VALIDACIÓN: No permitir costo negativo
    if (Number(costo) < 0) {
      throw new Error('El costo no puede ser negativo.');
    }

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

  // ✅ FUNCIÓN MODIFICADA: Agregar validación de costo negativo
  async function guardarCostoProductoProveedor(idModelo, costo) {
    const idProveedor = state.currentProveedorId;
    if (!idProveedor) return;

    // ✅ VALIDACIÓN: No permitir costo negativo
    if (costo !== '' && Number(costo) < 0) {
      showFeedback('error', 'El costo no puede ser negativo.');
      return;
    }

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
        showFeedback('error', e.message || 'No se pudo cargar el listado de proveedores.');
      }
    });

    btnLimpiar?.addEventListener('click', async () => {
      try {
        if (inputTexto) inputTexto.value = '';
        await cargarProveedores('');
      } catch (e) {
        showFeedback('error', e.message || 'No se pudo limpiar el filtro.');
      }
    });

    inputTexto?.addEventListener('keydown', async (ev) => {
      if (ev.key !== 'Enter') return;
      ev.preventDefault();
      try {
        await cargarProveedores((inputTexto.value || '').trim());
      } catch (e) {
        showFeedback('error', e.message || 'No se pudo cargar el listado de proveedores.');
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
        if (action === 'eliminar') await abrirEliminarProveedor(id);
      } catch (e) {
        showFeedback('error', e.message || 'No se pudo abrir la acción solicitada.');
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
        showFeedback('success', 'Proveedor creado correctamente.');
      } catch (e) {
        showFeedback('error', e.message || 'No se pudo crear el proveedor.');
      }
    });

    const formAgregarProductoCrear = $id('form-proveedor-agregar-producto-crear');
    formAgregarProductoCrear?.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      try {
        const costo = getFormValue('cp-costo');
        // ✅ VALIDACIÓN: No permitir costo negativo
        if (costo !== '' && Number(costo) < 0) {
          throw new Error('El costo no puede ser negativo.');
        }
        agregarProductoCrearFromForm();
        closeModal('modal-proveedor-agregar-producto-crear');
        formAgregarProductoCrear.reset();
        showFeedback('success', 'Producto agregado al proveedor inicial.');
      } catch (e) {
        showFeedback('error', e.message || 'No se pudo agregar el producto.');
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
        showFeedback('success', 'Proveedor actualizado correctamente.');
      } catch (e) {
        showFeedback('error', e.message || 'No se pudo actualizar el proveedor.');
      }
    });

    const formAgregarProducto = $id('form-proveedor-agregar-producto');
    formAgregarProducto?.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      try {
        const costo = getFormValue('ap-costo');
        // ✅ VALIDACIÓN: No permitir costo negativo
        if (costo !== '' && Number(costo) < 0) {
          throw new Error('El costo no puede ser negativo.');
        }
        await agregarProductoProveedorFromForm();
        closeModal('modal-proveedor-agregar-producto');
        await cargarProductosProveedorEditar(state.currentProveedorId);
        formAgregarProducto.reset();
        showFeedback('success', 'Producto agregado correctamente.');
      } catch (e) {
        showFeedback('error', e.message || 'No se pudo agregar el producto.');
      }
    });

    const tbodyProductosEditar = $id('tabla-proveedor-productos');
    tbodyProductosEditar?.addEventListener('change', async (ev) => {
      const input = ev.target?.closest?.('input[data-action="guardar-costo"][data-id-modelo]');
      if (!input) return;

      const idModelo = input.getAttribute('data-id-modelo');
      const costo = input.value;

      if (!idModelo) return;

      // ✅ VALIDACIÓN: No permitir costo negativo
      if (costo !== '' && Number(costo) < 0) {
        showFeedback('error', 'El costo no puede ser negativo.');
        input.value = 0;
        return;
      }

      try {
        await guardarCostoProductoProveedor(idModelo, costo);
        showFeedback('success', 'Costo actualizado correctamente.');
      } catch (e) {
        showFeedback('error', e.message || 'No se pudo actualizar el costo.');
      }
    });

    document.addEventListener('click', async (ev) => {
      const btn = ev.target?.closest?.('[data-open-modal="modal-proveedor-agregar-producto"]');
      if (!btn) return;

      try {
        setValue('ap-proveedor-id', state.currentProveedorId || '');
        const modelos = await cargarModelos();
        fillSelectModelos($id('ap-id-modelo'), modelos);
      } catch (e) {
        showFeedback('error', e.message || 'No se pudieron cargar los productos.');
      }
    });

    document.addEventListener('click', async (ev) => {
      const btn = ev.target?.closest?.('[data-open-modal="modal-proveedor-agregar-producto-crear"]');
      if (!btn) return;

      try {
        const modelos = await cargarModelos();
        fillSelectModelos($id('cp-id-modelo'), modelos);
      } catch (e) {
        showFeedback('error', e.message || 'No se pudieron cargar los productos.');
      }
    });
  }

  async function init() {
    bindEvents();
    renderProductosCrear();
    try {
      await cargarProveedores('');
    } catch (e) {
      console.error(e);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    void init();
  }
})();

// ==================== REPORTES ====================

let reporteDatosActuales = [];
let reporteFiltrosActuales = {};

const btnReportes = document.getElementById("btn-reportes");
const modalReportes = document.getElementById("modal-reportes");
const reporteBusqueda = document.getElementById("reporte-busqueda");
const reporteTipo = document.getElementById("reporte-tipo");
const reporteLimiteMin = document.getElementById("reporte-limite-min");
const reporteLimiteMax = document.getElementById("reporte-limite-max");
const btnGenerarReporte = document.getElementById("btn-generar-reporte");
const btnLimpiarFiltros = document.getElementById("btn-limpiar-filtros");
const btnExportarExcel = document.getElementById("btn-exportar-excel");
const btnExportarPdf = document.getElementById("btn-exportar-pdf");
const btnImprimir = document.getElementById("btn-imprimir");
const reportePreview = document.getElementById("reporte-preview");
const reporteTotal = document.getElementById("reporte-total");
const reporteTabla = document.getElementById("reporte-tabla");

function showFeedbackReportes(type, message) {
  if (window.FeedbackModal && typeof window.FeedbackModal.show === 'function') {
    window.FeedbackModal.show({
      type: type === 'error' ? 'error' : 'success',
      title: type === 'error' ? 'Error' : 'Éxito',
      message: message,
    });
    return;
  }
  if (type === 'error') alert(message);
  else console.log(message);
}

function getCsrfTokenReportes() {
  const input = document.querySelector('input[name="_csrf_token"]');
  return input ? input.value : '';
}

function getAccessTokenReportes() {
  return localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || '';
}

async function fetchJsonReportes(url, options = {}) {
  const csrfToken = getCsrfTokenReportes();
  const authToken = getAccessTokenReportes();
  
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
      ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
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
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function formatMoneyReportes(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return '';
  return n.toLocaleString('es-VE');
}

function limpiarFiltrosReporte() {
  if (reporteBusqueda) reporteBusqueda.value = "";
  if (reporteTipo) reporteTipo.value = "";
  if (reporteLimiteMin) reporteLimiteMin.value = "";
  if (reporteLimiteMax) reporteLimiteMax.value = "";
}

async function generarReporteProveedores() {
  const filtros = {
    q: reporteBusqueda?.value || "",
    tipo: reporteTipo?.value || null,
    limite_credito_min: reporteLimiteMin?.value ? parseInt(reporteLimiteMin.value) : null,
    limite_credito_max: reporteLimiteMax?.value ? parseInt(reporteLimiteMax.value) : null,
  };
  
  reporteFiltrosActuales = filtros;
  
  if (btnGenerarReporte) {
    btnGenerarReporte.disabled = true;
    btnGenerarReporte.textContent = "Cargando...";
  }
  
  try {
    const data = await fetchJsonReportes("/api/proveedores/reportes", {
      method: "POST",
      body: JSON.stringify(filtros)
    });
    
    reporteDatosActuales = data.proveedores || [];
    const total = data.total || 0;
    
    if (reportePreview) reportePreview.style.display = "block";
    if (reporteTotal) reporteTotal.textContent = `Total de proveedores: ${total}`;
    
    if (reporteTabla) {
      if (reporteDatosActuales.length === 0) {
        reporteTabla.innerHTML = '<tr><td colspan="6" class="table__empty">No hay proveedores con esos filtros</td></tr>';
      } else {
        reporteTabla.innerHTML = reporteDatosActuales.map(p => `
          <tr>
            <td>${escapeHtmlReportes(p.id || '')}</td>
            <td><strong>${escapeHtmlReportes(p.nombre || '')}</strong></td>
            <td>${escapeHtmlReportes(p.tipo || '-')}</td>
            <td>${escapeHtmlReportes(p.celular || '-')}</td>
            <td>${p.total_productos || 0} productos<br><small>${formatMoneyReportes(p.costo_total || 0)} Bs</small></td>
            <td>${p.limite_credito ? formatMoneyReportes(p.limite_credito) + ' Bs' : '-'}</td>
          </tr>
        `).join("");
      }
    }
    
    if (btnExportarExcel) btnExportarExcel.disabled = false;
    if (btnExportarPdf) btnExportarPdf.disabled = false;
    if (btnImprimir) btnImprimir.disabled = false;
    
  } catch (err) {
    showFeedbackReportes('error', err.message || "Error al generar el reporte");
  } finally {
    if (btnGenerarReporte) {
      btnGenerarReporte.disabled = false;
      btnGenerarReporte.textContent = "Generar reporte";
    }
  }
}

function exportarProveedoresExcel() {
  if (reporteDatosActuales.length === 0) {
    showFeedbackReportes('error', "No hay datos para exportar");
    return;
  }
  
  const datos = reporteDatosActuales.map(p => ({
    "ID": p.id || "",
    "Proveedor": p.nombre || "",
    "Tipo": p.tipo || "",
    "Teléfono": p.celular || "",
    "Correo": p.correo || "",
    "Dirección": p.direccion || "",
    "Límite Crédito": p.limite_credito || 0,
    "Productos": p.total_productos || 0
  }));
  
  if (typeof XLSX === 'undefined') {
    showFeedbackReportes('info', "Cargando librería de Excel...");
    const script = document.createElement('script');
    script.src = '/static/js/libs/xlsx.full.min.js';
    script.onload = () => exportarProveedoresExcel();
    document.head.appendChild(script);
    return;
  }
  
  const ws = XLSX.utils.json_to_sheet(datos);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "Proveedores");
  
  ws['!cols'] = [
    {wch: 8}, {wch: 35}, {wch: 12}, {wch: 15}, {wch: 30}, {wch: 35}, {wch: 15}, {wch: 10}
  ];
  
  XLSX.writeFile(wb, `proveedores_${new Date().toISOString().slice(0,19)}.xlsx`);
  showFeedbackReportes('success', "Reporte exportado a Excel");
}

function exportarProveedoresPdf() {
  if (reporteDatosActuales.length === 0) {
    showFeedbackReportes('error', "No hay datos para exportar");
    return;
  }
  
  if (typeof window.jspdf === 'undefined' || typeof window.jspdf.jsPDF === 'undefined') {
    showFeedbackReportes('info', "Cargando librería de PDF...");
    const script1 = document.createElement('script');
    script1.src = '/static/js/libs/jspdf.umd.min.js';
    script1.onload = () => {
      const script2 = document.createElement('script');
      script2.src = '/static/js/libs/jspdf.plugin.autotable.min.js';
      script2.onload = () => {
        setTimeout(() => exportarProveedoresPdf(), 100);
      };
      document.head.appendChild(script2);
    };
    document.head.appendChild(script1);
    return;
  }
  
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
  const pageWidth = doc.internal.pageSize.getWidth();
  
  const colors = {
    dark: [18, 18, 18],
    primary: [243, 197, 0],
    white: [255, 255, 255],
    grayLight: [248, 249, 250],
    grayText: [102, 102, 106]
  };
  
  const logoUrl = window.location.origin + '/static/img/LOGO TRAZO.png';
  try {
    doc.addImage(logoUrl, 'PNG', (pageWidth - 45) / 2, 8, 45, 14);
  } catch(e) {}
  
  doc.setFont("helvetica", "bold");
  doc.setFontSize(22);
  doc.setTextColor(colors.dark[0], colors.dark[1], colors.dark[2]);
  doc.text("REPORTE DE PROVEEDORES", pageWidth / 2, 30, { align: 'center' });
  
  doc.setDrawColor(colors.primary[0], colors.primary[1], colors.primary[2]);
  doc.setLineWidth(0.8);
  doc.line(pageWidth / 2 - 35, 34, pageWidth / 2 + 35, 34);
  
  const now = new Date();
  const fechaStr = now.toLocaleDateString('es-ES');
  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  doc.setTextColor(colors.grayText[0], colors.grayText[1], colors.grayText[2]);
  doc.text(`Generado: ${fechaStr} • Total proveedores: ${reporteDatosActuales.length}`, pageWidth / 2, 44, { align: 'center' });
  
  const filtrosTexto = [];
  if (reporteFiltrosActuales.q) filtrosTexto.push(`Búsqueda: ${reporteFiltrosActuales.q}`);
  if (reporteFiltrosActuales.tipo) filtrosTexto.push(`Tipo: ${reporteFiltrosActuales.tipo}`);
  if (reporteFiltrosActuales.limite_credito_min) filtrosTexto.push(`Crédito ≥ ${reporteFiltrosActuales.limite_credito_min}`);
  if (reporteFiltrosActuales.limite_credito_max) filtrosTexto.push(`Crédito ≤ ${reporteFiltrosActuales.limite_credito_max}`);
  
  const filterY = 52;
  doc.setFillColor(colors.grayLight[0], colors.grayLight[1], colors.grayLight[2]);
  doc.rect(15, filterY, pageWidth - 30, 10, 'F');
  doc.setFont("helvetica", "italic");
  doc.setFontSize(8.5);
  doc.setTextColor(colors.grayText[0], colors.grayText[1], colors.grayText[2]);
  doc.text(filtrosTexto.length ? `Filtros: ${filtrosTexto.join(" • ")}` : "Filtros: Todos los proveedores", 18, filterY + 7);
  
  const columns = ["ID", "PROVEEDOR", "TIPO", "TELÉFONO", "PRODUCTOS", "CRÉDITO"];
  const rows = reporteDatosActuales.map(p => [
    p.id || "",
    p.nombre || "",
    p.tipo || "-",
    p.celular || "-",
    `${p.total_productos || 0} uds`,
    p.limite_credito ? `${Number(p.limite_credito).toLocaleString('es-VE')} Bs` : "-"
  ]);
  
  doc.autoTable({
    head: [columns],
    body: rows,
    startY: filterY + 14,
    theme: 'grid',
    headStyles: {
      fillColor: colors.dark,
      textColor: colors.white,
      fontStyle: 'bold',
      fontSize: 9,
      halign: 'center'
    },
    bodyStyles: { fontSize: 8.5, cellPadding: 4 },
    alternateRowStyles: { fillColor: colors.grayLight },
    margin: { left: 15, right: 15 },
    didDrawPage: (data) => {
      doc.setFontSize(7);
      doc.setTextColor(colors.grayText[0], colors.grayText[1], colors.grayText[2]);
      doc.text("ItuAccesorio System · Reporte Generado Exclusivamente Para ituaccesorio", pageWidth / 2, doc.internal.pageSize.getHeight() - 8, { align: 'center' });
      doc.text(`Página ${data.pageNumber}`, pageWidth - 15, doc.internal.pageSize.getHeight() - 8, { align: 'right' });
    }
  });
  
  doc.save(`proveedores_${now.toISOString().slice(0,19)}.pdf`);
  showFeedbackReportes('success', "Reporte exportado a PDF");
}

function imprimirReporteProveedores() {
  if (reporteDatosActuales.length === 0) {
    showFeedbackReportes('error', "No hay datos para imprimir");
    return;
  }
  
  const ventana = window.open("", "_blank");
  const fecha = new Date().toLocaleString();
  const logoUrl = window.location.origin + '/static/img/LOGO TRAZO.png';
  
  const filtrosTexto = [];
  if (reporteFiltrosActuales.q) filtrosTexto.push(`Búsqueda: ${reporteFiltrosActuales.q}`);
  if (reporteFiltrosActuales.tipo) filtrosTexto.push(`Tipo: ${reporteFiltrosActuales.tipo}`);
  if (reporteFiltrosActuales.limite_credito_min) filtrosTexto.push(`Crédito ≥ ${reporteFiltrosActuales.limite_credito_min}`);
  if (reporteFiltrosActuales.limite_credito_max) filtrosTexto.push(`Crédito ≤ ${reporteFiltrosActuales.limite_credito_max}`);
  
  ventana.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Reporte de Proveedores</title>
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
      </style>
    </head>
    <body>
      <button class="btn-print no-print" onclick="window.print()">🖨 Imprimir</button>
      <div class="logo"><img src="${logoUrl}" alt="ItuAccesorio" onerror="this.style.display='none'"></div>
      <h1>REPORTE DE PROVEEDORES</h1>
      <div class="info">Generado: ${fecha} • Total proveedores: ${reporteDatosActuales.length}</div>
      ${filtrosTexto.length ? `<div class="filters"><strong>Filtros:</strong> ${filtrosTexto.join(" • ")}</div>` : ''}
      <table>
        <thead><tr><th>ID</th><th>Proveedor</th><th>Tipo</th><th>Teléfono</th><th>Productos</th><th>Límite Crédito</th></tr></thead>
        <tbody>
          ${reporteDatosActuales.map(p => `
            <tr>
              <td>${escapeHtmlReportes(p.id || '')}</td>
              <td><strong>${escapeHtmlReportes(p.nombre || '')}</strong></td>
              <td>${escapeHtmlReportes(p.tipo || '-')}</td>
              <td>${escapeHtmlReportes(p.celular || '-')}</td>
              <td>${p.total_productos || 0} productos</td>
              <td>${p.limite_credito ? Number(p.limite_credito).toLocaleString('es-VE') + ' Bs' : '-'}</td>
            </tr>
          `).join('')}
        </tbody>
      追赶
      <div class="footer">ItuAccesorio System - Reporte Generado Exclusivamente Para ituaccesorio</div>
    </body>
    </html>
  `);
  ventana.document.close();
}

if (btnReportes) {
  btnReportes.addEventListener("click", () => {
    limpiarFiltrosReporte();
    if (reportePreview) reportePreview.style.display = "none";
    if (btnExportarExcel) btnExportarExcel.disabled = true;
    if (btnExportarPdf) btnExportarPdf.disabled = true;
    if (btnImprimir) btnImprimir.disabled = true;
    if (window.UiModal && typeof window.UiModal.openById === 'function') {
      window.UiModal.openById('modal-reportes');
    } else if (modalReportes) {
      modalReportes.hidden = false;
      modalReportes.setAttribute("aria-hidden", "false");
    }
  });
}

if (btnGenerarReporte) btnGenerarReporte.addEventListener("click", generarReporteProveedores);
if (btnLimpiarFiltros) btnLimpiarFiltros.addEventListener("click", limpiarFiltrosReporte);
if (btnExportarExcel) btnExportarExcel.addEventListener("click", exportarProveedoresExcel);
if (btnExportarPdf) btnExportarPdf.addEventListener("click", exportarProveedoresPdf);
if (btnImprimir) btnImprimir.addEventListener("click", imprimirReporteProveedores);

if (modalReportes) {
  modalReportes.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;

    if (target.dataset.modalClose === "true") {
      if (window.UiModal && typeof window.UiModal.closeById === 'function') {
        window.UiModal.closeById('modal-reportes');
      } else {
        modalReportes.hidden = true;
        modalReportes.setAttribute("aria-hidden", "true");
      }
      return;
    }

    if (target === modalReportes) {
      if (window.UiModal && typeof window.UiModal.closeById === 'function') {
        window.UiModal.closeById('modal-reportes');
      } else {
        modalReportes.hidden = true;
        modalReportes.setAttribute("aria-hidden", "true");
      }
    }
  });
}

document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  if (window.UiModal && typeof window.UiModal.closeById === 'function') {
    window.UiModal.closeById('modal-reportes');
  } else if (modalReportes && !modalReportes.hidden) {
    modalReportes.hidden = true;
    modalReportes.setAttribute("aria-hidden", "true");
  }
});