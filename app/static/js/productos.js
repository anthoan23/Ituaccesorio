(() => {
  "use strict";

  const state = {
    clases: [],
    marcas: [],
    categorias: [],
    modelos: [],
  };

  const tabla = document.getElementById("tabla-productos");
  const btnNuevo = document.getElementById("btn-registrar-producto");
  const btnNuevoHeader = document.getElementById("btn-registrar-producto-header");
  const modal = document.getElementById("modal-producto");
  const formProducto = document.getElementById("form-producto");
  const csrfToken = document.querySelector("input[name='_csrf_token']")?.value || "";

  // Filtros principales
  const fClase = document.getElementById("f-clase");
  const fMarca = document.getElementById("f-marca");
  const fClaseSidebar = document.getElementById("f-clase-sidebar");
  const fMarcaSidebar = document.getElementById("f-marca-sidebar");
  const btnAplicarFiltros = document.getElementById("btn-aplicar-filtros");
  const btnLimpiarFiltros = document.getElementById("btn-limpiar-filtros");
  const inputBuscar = document.getElementById("input-buscar-productos");

  // Formulario
  const pClase = document.getElementById("p-clase");
  const pClaseNuevaWrap = document.getElementById("p-clase-nueva-wrap");
  const pClaseNueva = document.getElementById("p-clase-nueva");
  const pMarca = document.getElementById("p-marca");
  const pMarcaNuevaWrap = document.getElementById("p-marca-nueva-wrap");
  const pMarcaNueva = document.getElementById("p-marca-nueva");
  const pCategoria = document.getElementById("p-categoria");
  const pModelo = document.getElementById("p-modelo");
  const pDescripcion = document.getElementById("p-descripcion");
  const btnNuevaClase = document.getElementById("btn-nueva-clase");
  const btnNuevaMarca = document.getElementById("btn-nueva-marca");
  const btnGuardarClase = document.getElementById("btn-guardar-clase");
  const btnGuardarMarca = document.getElementById("btn-guardar-marca");
  const btnCancelarClase = document.getElementById("btn-cancelar-clase");
  const btnCancelarMarca = document.getElementById("btn-cancelar-marca");

  let isCreatingNewClass = false;
  let isCreatingNewBrand = false;
  let isSubmitting = false;
  let searchQuery = "";

  const MAX = {
    clase: 30,
    marca: 30,
    producto: 50,
    descripcion: 300,
  };

  // ==================== VALIDACIÓN DE SEGURIDAD ====================
  
  function validarIdProducto(id) {
    if (!id || id === '' || id === null || id === undefined) {
      return false;
    }
    const idStr = String(id).trim();
    return /^[a-zA-Z0-9]+$/.test(idStr) && idStr.length > 0;
  }

  function mostrarErrorSeguridad(mensaje) {
    const msg = mensaje || 'Se ha detectado una acción no válida. Por favor, recarga la página e intenta nuevamente.';
    
    if (window.FeedbackModal && typeof window.FeedbackModal.show === 'function') {
      window.FeedbackModal.show({
        type: 'error',
        title: 'Acción no permitida',
        message: msg,
        duration: 5000
      });
    } else {
      mostrarModalConfirmacion(`${msg}`, null, true, 'error');
    }
  }

  function mostrarModalConfirmacion(mensaje, onConfirmar, soloInformacion = false, tipo = 'info') {
    const modalExistente = document.getElementById('confirmacion-modal');
    if (modalExistente) modalExistente.remove();
    
    const esError = tipo === 'error';
    const esExito = tipo === 'success';
    
    let titulo = "Información";
    let btnTexto = "Aceptar";
    let btnColor = "#f3c500";
    let icono = "ℹ️";
    
    if (esError) {
      titulo = "Error";
      btnColor = "#dc2626";
      icono = "❌";
    } else if (esExito) {
      titulo = "Éxito";
      btnColor = "#16a34a";
      icono = "✅";
    } else if (soloInformacion) {
      titulo = "Información";
      btnColor = "#f3c500";
      icono = "ℹ️";
    } else {
      titulo = "Confirmar eliminación";
      btnTexto = "Eliminar";
      icono = "⚠️";
    }

    const modalClass = esError
      ? 'ui-modal--confirm-danger'
      : esExito
        ? 'ui-modal--confirm-success'
        : soloInformacion
          ? 'ui-modal--confirm-info'
          : 'ui-modal--confirm-danger';
    const btnClass = esError
      ? 'ui-btn--danger'
      : esExito
        ? 'ui-btn--success'
        : soloInformacion
          ? 'ui-btn--primary'
          : 'ui-btn--danger';
    
    const modalDiv = document.createElement('div');
    modalDiv.id = 'confirmacion-modal';
    modalDiv.className = `ui-modal ui-modal--confirm ${modalClass}`;
    
    modalDiv.innerHTML = `
      <div class="ui-modal__dialog ui-modal__dialog--sm" role="dialog" aria-modal="true">
        <header class="ui-modal__header">
          <h3 class="ui-modal__title">${titulo}</h3>
          <button type="button" class="ui-modal__close" data-close-modal aria-label="Cerrar">×</button>
        </header>
        <div class="ui-modal__body">
          <div class="confirm-modal__icon">${icono}</div>
          <p id="confirmacion-modal-mensaje" class="confirm-modal__message confirm-modal__message--center">${mensaje}</p>
        </div>
        <div class="ui-modal__footer ui-modal__footer--center">
          ${!soloInformacion && !esExito && !esError ? '<button type="button" class="ui-btn ui-btn--ghost" id="btn-cancelar-confirmacion">Cancelar</button>' : ''}
          <button type="button" class="ui-btn ${btnClass}" id="btn-confirmar-accion">${btnTexto}</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modalDiv);
    document.body.style.overflow = 'hidden';
    
    const cerrarModal = () => {
      modalDiv.remove();
      document.body.style.overflow = '';
    };
    
    if (!soloInformacion && !esExito && !esError) {
      const cancelBtn = document.getElementById('btn-cancelar-confirmacion');
      if (cancelBtn) {
        cancelBtn.addEventListener('click', cerrarModal);
      }
    }
    
    const confirmBtn = document.getElementById('btn-confirmar-accion');
    if (confirmBtn) {
      confirmBtn.addEventListener('click', async () => {
        cerrarModal();
        if (onConfirmar && !soloInformacion && !esExito && !esError) {
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
    
    if (soloInformacion || esExito || esError) {
      setTimeout(() => {
        if (document.getElementById('confirmacion-modal')) cerrarModal();
      }, 4000);
    }
  }

  function notify(type, message) {
    if (type === 'error') {
      if (window.FeedbackModal && typeof window.FeedbackModal.show === 'function') {
        window.FeedbackModal.show({
          type: 'error',
          title: 'Error',
          message: message,
        });
      } else {
        mostrarModalConfirmacion(message, null, true, 'error');
      }
    } else if (type === 'success') {
      if (window.FeedbackModal && typeof window.FeedbackModal.show === 'function') {
        window.FeedbackModal.show({
          type: 'success',
          title: 'Éxito',
          message: message,
        });
      } else {
        mostrarModalConfirmacion(message, null, true, 'success');
      }
    } else {
      console.log(message);
    }
  }

  function validarFormularioAntesDeEnviar(form, nombreFormulario) {
    if (!window.FieldValidator) {
      console.warn('FieldValidator no disponible');
      return true;
    }
    
    const isValid = window.FieldValidator.validateForm(form);
    
    if (!isValid) {
      notify("error", `Por favor, corrige los errores en el formulario de ${nombreFormulario}.`);
      
      const primerError = form.querySelector('.field-error');
      if (primerError) {
        primerError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        primerError.focus();
      }
      
      return false;
    }
    
    return true;
  }

  function validateMaxLen(label, value, max) {
    const v = String(value || "");
    if (v.length > max) {
      throw new Error(`${label} no puede exceder ${max} caracteres.`);
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

    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
        ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
      },
      credentials: "same-origin",
      ...options,
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok || data.success === false) {
      if (response.status === 404) {
        throw new Error(`404: ${data.error || 'El recurso solicitado no existe.'}`);
      }
      throw new Error(data.error || "No se pudo completar la operación.");
    }
    return data;
  }

  async function fetchFormData(url, formData) {
    const authToken = getAuthToken();
    
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json",
        ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
        ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
      },
      credentials: "same-origin",
      body: formData,
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok || data.success === false) {
      if (response.status === 404) {
        throw new Error(`404: ${data.error || 'El recurso solicitado no existe.'}`);
      }
      throw new Error(data.error || "No se pudo completar la operación.");
    }
    return data;
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function emptyRow(colspan, text) {
    return `<tr><td colspan="${colspan}" class="table__empty">${escapeHtml(text)}</td></tr>`;
  }

  function openModal() {
    if (window.UiModal && typeof window.UiModal.openById === "function") {
      window.UiModal.openById("modal-producto");
      if (window.FieldValidator) {
        setTimeout(() => window.FieldValidator.init(), 100);
      }
    }
  }

  function closeModal() {
    if (window.UiModal && typeof window.UiModal.closeById === "function") {
      window.UiModal.closeById("modal-producto");
    }
    if (formProducto && window.FieldValidator) {
      window.FieldValidator.resetForm(formProducto);
    }
  }

  function resetFormToCreate() {
    if (!formProducto) return;
    formProducto.reset();
    const idInput = formProducto.querySelector("input[name='id_modelo']");
    if (idInput) idInput.value = "";
    const title = document.querySelector("#modal-producto .ui-modal__title");
    if (title) title.textContent = "Registrar producto";
    setNewClassMode(false);
    setNewBrandMode(false);
    
    if (window.FieldValidator) {
      window.FieldValidator.resetForm(formProducto);
    }
  }

  function setNewClassMode(isNew) {
    isCreatingNewClass = Boolean(isNew);
    if (pClaseNuevaWrap) {
      if (isNew) {
        pClaseNuevaWrap.classList.remove("is-hidden");
      } else {
        pClaseNuevaWrap.classList.add("is-hidden");
      }
    }
    if (pClaseNueva) {
      pClaseNueva.required = Boolean(isNew);
      if (!isNew && pClaseNueva.value) pClaseNueva.value = "";
    }
    if (btnNuevaClase) btnNuevaClase.textContent = isNew ? "Cancelar" : "Nueva clase";
    
    if (window.FieldValidator) {
      setTimeout(() => window.FieldValidator.init(), 100);
    }
  }

  function setNewBrandMode(isNew) {
    isCreatingNewBrand = Boolean(isNew);
    if (pMarcaNuevaWrap) {
      if (isNew) {
        pMarcaNuevaWrap.classList.remove("is-hidden");
      } else {
        pMarcaNuevaWrap.classList.add("is-hidden");
      }
    }
    if (pMarcaNueva) {
      pMarcaNueva.required = Boolean(isNew);
      if (!isNew && pMarcaNueva.value) pMarcaNueva.value = "";
    }
    if (btnNuevaMarca) btnNuevaMarca.textContent = isNew ? "Cancelar" : "Nueva marca";
    
    if (window.FieldValidator) {
      setTimeout(() => window.FieldValidator.init(), 100);
    }
  }

  function renderSelect(select, items, { includeAll = false, allLabel = "Todas", placeholder = "Selecciona" } = {}) {
    if (!select) return;
    select.innerHTML = "";

    if (includeAll) {
      const optAll = document.createElement("option");
      optAll.value = "";
      optAll.textContent = allLabel;
      select.appendChild(optAll);
    } else {
      const optPlaceholder = document.createElement("option");
      optPlaceholder.value = "";
      optPlaceholder.textContent = placeholder;
      select.appendChild(optPlaceholder);
    }

    items.forEach((item) => {
      const opt = document.createElement("option");
      opt.value = String(item.id);
      opt.textContent = item.nombre;
      select.appendChild(opt);
    });
  }

  function renderClaseFormSelect() {
    if (!pClase) return;
    pClase.innerHTML = "";

    const optPlaceholder = document.createElement("option");
    optPlaceholder.value = "";
    optPlaceholder.textContent = "Selecciona una clase";
    pClase.appendChild(optPlaceholder);

    state.clases.forEach((c) => {
      const opt = document.createElement("option");
      opt.value = String(c.id);
      opt.textContent = c.nombre;
      pClase.appendChild(opt);
    });
  }

  function renderMarcaFormSelect(marcas) {
    if (!pMarca) return;
    pMarca.innerHTML = "";

    const optPlaceholder = document.createElement("option");
    optPlaceholder.value = "";
    optPlaceholder.textContent = "Selecciona una marca";
    pMarca.appendChild(optPlaceholder);

    marcas.forEach((m) => {
      const opt = document.createElement("option");
      opt.value = String(m.id);
      opt.textContent = m.nombre;
      pMarca.appendChild(opt);
    });
  }

  function renderCategoriaSelect() {
    if (!pCategoria) return;
    pCategoria.innerHTML = '<option value="0">Sin categoría</option>';
    
    state.categorias.forEach((c) => {
      const opt = document.createElement("option");
      opt.value = String(c.id);
      opt.textContent = c.nombre;
      pCategoria.appendChild(opt);
    });
  }

  // Función para sincronizar selects de filtros
  function syncFilterSelects() {
    if (fClase && fClaseSidebar) {
      fClaseSidebar.value = fClase.value;
    }
    if (fMarca && fMarcaSidebar) {
      fMarcaSidebar.value = fMarca.value;
    }
  }

  async function cargarClases() {
    const data = await fetchJson("/api/productos/clases", { method: "GET" });
    state.clases = Array.isArray(data.clases) ? data.clases : [];
    renderSelect(fClase, state.clases, { includeAll: true, allLabel: "Todas" });
    renderSelect(fClaseSidebar, state.clases, { includeAll: true, allLabel: "Todas" });
    renderClaseFormSelect();
  }

  async function cargarMarcas() {
    const data = await fetchJson("/api/productos/marcas", { method: "GET" });
    const marcas = Array.isArray(data.marcas) ? data.marcas : [];
    state.marcas = marcas;
    renderSelect(fMarca, marcas, { includeAll: true, allLabel: "Todas" });
    renderSelect(fMarcaSidebar, marcas, { includeAll: true, allLabel: "Todas" });
    renderMarcaFormSelect(marcas);
  }

  async function cargarCategorias() {
    const data = await fetchJson("/api/productos/categorias", { method: "GET" });
    state.categorias = Array.isArray(data.categorias) ? data.categorias : [];
    renderCategoriaSelect();
  }

  async function cargarModelos({ claseId = "", marcaId = "" } = {}) {
    const params = new URLSearchParams();
    if (claseId) params.set("clase_id", String(claseId));
    if (marcaId) params.set("marca_id", String(marcaId));
    if (searchQuery) params.set("q", searchQuery);
    const url = `/api/productos/modelos${params.toString() ? `?${params}` : ""}`;

    const data = await fetchJson(url, { method: "GET" });
    state.modelos = Array.isArray(data.modelos) ? data.modelos : [];
  }

  function renderTabla(modelos) {
    if (!tabla) return;
    if (!modelos.length) {
      tabla.innerHTML = emptyRow(5, "No hay productos registrados.");
      return;
    }

    tabla.innerHTML = modelos
      .map(
        (m) => `
          <tr data-id="${escapeHtml(m.id ?? "")}">
            <td><span class="product-thumb" aria-hidden="true"></span></td>
            <td>
              <div class="product-meta">
                <strong class="product-name">${escapeHtml(m.nombre || "")}</strong>
                <span class="product-sku">Código: PRO${escapeHtml(m.id ?? "")}</span>
              </div>
            </td>
            <td><span class="badge-marca">${escapeHtml(m.marca_nombre || "")}</span></td>
            <td><span class="badge-clase">${escapeHtml(m.clase_nombre || "")}</span></td>
            <td class="table__actions">
              <div class="row-actions" aria-label="Acciones del producto">
                <button class="icon-action icon-action--edit" type="button" aria-label="Editar" data-action="edit" data-id="${escapeHtml(m.id ?? "")}">
                  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="16" height="16"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25Zm18-11.5a1 1 0 0 0 0-1.41l-1.34-1.34a1 1 0 0 0-1.41 0l-1.12 1.12 3.75 3.75L21 5.75Z" fill="currentColor"/></svg>
                </button>
                <button class="icon-action icon-action--danger" type="button" aria-label="Eliminar" data-action="delete" data-id="${escapeHtml(m.id ?? "")}">
                  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="16" height="16"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" fill="currentColor"/></svg>
                </button>
              </div>
            </td>
          </tr>
        `,
      )
      .join("");
  }

  function aplicarFiltrosYRender() {
    const claseId = fClase ? String(fClase.value || "") : "";
    const marcaId = fMarca ? String(fMarca.value || "") : "";

    let modelos = state.modelos;
    if (claseId) {
      modelos = modelos.filter((m) => String(m.id_clase || "") === String(claseId));
    }
    if (marcaId) {
      modelos = modelos.filter((m) => String(m.id_marca || "") === String(marcaId));
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      modelos = modelos.filter((m) => 
        (m.nombre || "").toLowerCase().includes(q) ||
        (m.marca_nombre || "").toLowerCase().includes(q) ||
        String(m.id || "").includes(q)
      );
    }
    renderTabla(modelos);
  }

  async function recargarModelosSegunFiltros() {
    const claseId = fClase ? String(fClase.value || "") : "";
    const marcaId = fMarca ? String(fMarca.value || "") : "";
    syncFilterSelects();
    await cargarModelos({ claseId, marcaId });
    aplicarFiltrosYRender();
  }

  function findModeloById(id) {
    return state.modelos.find((m) => String(m.id) === String(id));
  }

  // ==================== FUNCIONES CON VALIDACIÓN DE SEGURIDAD ====================

  async function prepararFormularioEdicion(idModelo) {
    if (!validarIdProducto(idModelo)) {
      mostrarErrorSeguridad('El ID del producto que intentas editar no es válido.');
      return;
    }
    
    const modelo = findModeloById(idModelo);
    if (!modelo || !formProducto) {
      mostrarErrorSeguridad(`El producto con ID "${idModelo}" no existe o ha sido eliminado.`);
      return;
    }

    resetFormToCreate();
    const title = document.querySelector("#modal-producto .ui-modal__title");
    if (title) title.textContent = "Editar producto";

    const idInput = formProducto.querySelector("input[name='id_modelo']");
    if (idInput) idInput.value = String(modelo.id || "");

    if (!state.clases.length) await cargarClases();
    if (!state.marcas.length) await cargarMarcas();
    await cargarCategorias();

    if (pClase) pClase.value = String(modelo.id_clase || "");
    setNewClassMode(false);

    if (pMarca) pMarca.value = String(modelo.id_marca || "");
    setNewBrandMode(false);

    if (pModelo) pModelo.value = modelo.nombre || "";
    if (pDescripcion) pDescripcion.value = modelo.descripcion || "";
  }

  async function onSubmitProducto(event) {
    event.preventDefault();
    if (!formProducto) return;
    if (isSubmitting) return;

    if (!validarFormularioAntesDeEnviar(formProducto, 'producto')) {
      return;
    }

    const idModelo = String(formProducto.querySelector("input[name='id_modelo']")?.value || "").trim();
    const nombreModelo = String(pModelo?.value || "").trim();
    const descripcion = String(pDescripcion?.value || "").trim();
    
    if (!nombreModelo) {
      notify("error", "El nombre del producto es obligatorio.");
      return;
    }

    try {
      isSubmitting = true;
      const submitBtn = formProducto.querySelector("button[type='submit']");
      if (submitBtn) submitBtn.disabled = true;

      if (isCreatingNewBrand) {
        throw new Error("Primero guarda la marca con el botón 'Guardar marca'.");
      }

      if (isCreatingNewClass) {
        throw new Error("Primero guarda la clase con el botón 'Guardar clase'.");
      }

      const claseIdFinal = Number(pClase?.value || 0);
      if (!claseIdFinal) throw new Error("La clase es obligatoria.");

      const finalMarcaId = Number(pMarca?.value || 0);
      if (!finalMarcaId) throw new Error("La marca es obligatoria.");

      validateMaxLen("Producto", nombreModelo, MAX.producto);
      validateMaxLen("Descripción", descripcion, MAX.descripcion);

      if (idModelo) {
        await fetchJson(`/api/productos/modelos/${encodeURIComponent(idModelo)}`, {
          method: "PUT",
          body: JSON.stringify({ nombre: nombreModelo, id_marca: finalMarcaId, id_clase: claseIdFinal, descripcion }),
        });
      } else {
        const formData = new FormData(formProducto);
        
        formData.set("modelo", nombreModelo);
        formData.set("id_marca", String(finalMarcaId));
        formData.set("id_clase", String(claseIdFinal));
        formData.set("descripcion", descripcion || "");
        formData.set("id_categoria", pCategoria?.value || "0");
        
        await fetchFormData("/api/productos/modelos", formData);
      }

      closeModal();
      await recargarModelosSegunFiltros();
      notify("success", "Producto guardado correctamente.");
    } catch (err) {
      console.error("Error:", err);
      if (err.message && err.message.includes('404')) {
        mostrarErrorSeguridad('El producto que intentas modificar ya no existe en el sistema.');
      } else {
        notify("error", err?.message || "No se pudo guardar.");
      }
    } finally {
      isSubmitting = false;
      const submitBtn = formProducto.querySelector("button[type='submit']");
      if (submitBtn) submitBtn.disabled = false;
    }
  }

  async function onGuardarClaseClick() {
    try {
      if (btnGuardarClase) btnGuardarClase.disabled = true;

      if (!isCreatingNewClass) {
        setNewClassMode(true);
        if (pClaseNueva) pClaseNueva.focus();
        return;
      }

      const nombreClase = String(pClaseNueva?.value || "").trim();
      if (!nombreClase) {
        throw new Error("Escribe el nombre de la clase.");
      }

      validateMaxLen("Clase", nombreClase, MAX.clase);

      const soloLetrasRegex = /^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ\s]+$/;
      if (!soloLetrasRegex.test(nombreClase)) {
        throw new Error("La clase solo puede contener letras y espacios.");
      }

      const data = await fetchJson("/api/productos/clases", {
        method: "POST",
        body: JSON.stringify({ nombre: nombreClase, num_i: null }),
      });

      await cargarClases();
      renderClaseFormSelect();
      if (pClase) pClase.value = String(data.id || "");

      setNewClassMode(false);
      if (pClaseNueva) pClaseNueva.value = "";
      
      notify("success", `Clase "${nombreClase}" creada correctamente.`);
    } catch (err) {
      notify("error", err?.message || "No se pudo guardar la clase.");
    } finally {
      if (btnGuardarClase) btnGuardarClase.disabled = false;
    }
  }

  async function onGuardarMarcaClick() {
    try {
      if (btnGuardarMarca) btnGuardarMarca.disabled = true;

      if (!isCreatingNewBrand) {
        setNewBrandMode(true);
        if (pMarcaNueva) pMarcaNueva.focus();
        return;
      }

      const nombreMarca = String(pMarcaNueva?.value || "").trim();
      if (!nombreMarca) {
        throw new Error("Escribe el nombre de la marca.");
      }

      validateMaxLen("Marca", nombreMarca, MAX.marca);

      const letrasNumerosRegex = /^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ0-9\s]+$/;
      if (!letrasNumerosRegex.test(nombreMarca)) {
        throw new Error("La marca solo puede contener letras, números y espacios.");
      }

      const data = await fetchJson("/api/productos/marcas", {
        method: "POST",
        body: JSON.stringify({ nombre: nombreMarca }),
      });

      await cargarMarcas();
      if (pMarca) pMarca.value = String(data.id || "");

      setNewBrandMode(false);
      if (pMarcaNueva) pMarcaNueva.value = "";
      
      notify("success", `Marca "${nombreMarca}" creada correctamente.`);
    } catch (err) {
      notify("error", err?.message || "No se pudo guardar la marca.");
    } finally {
      if (btnGuardarMarca) btnGuardarMarca.disabled = false;
    }
  }

  // ==================== ELIMINAR PRODUCTO CON VALIDACIÓN ====================
  
  async function eliminarProducto(id, nombreProducto) {
    if (!validarIdProducto(id)) {
      mostrarErrorSeguridad('El ID del producto que intentas eliminar no es válido.');
      return;
    }
    
    try {
      const data = await fetchJson(`/api/productos/modelos/${encodeURIComponent(id)}/verificar-stock`, { method: 'GET' });
      const tieneStock = data.tiene_stock || false;
      const stock = data.stock || 0;
      
      if (tieneStock) {
        mostrarModalConfirmacion(
          `No se puede eliminar el producto "${nombreProducto}" porque tiene ${stock} unidades en inventario.`,
          null,
          true,
          'error'
        );
      } else {
        mostrarModalConfirmacion(`¿Seguro que deseas eliminar el producto "${nombreProducto}"?`, async () => {
          try {
            await fetchJson(`/api/productos/modelos/${encodeURIComponent(id)}`, { method: "DELETE" });
            await recargarModelosSegunFiltros();
            notify("success", `Producto "${nombreProducto}" eliminado correctamente.`);
          } catch (err) {
            if (err.message && err.message.includes('404')) {
              mostrarErrorSeguridad(`El producto "${nombreProducto}" ya no existe en el sistema.`);
            } else {
              notify("error", err?.message || "No se pudo eliminar el producto.");
            }
          }
        });
      }
    } catch (err) {
      if (err.message && (err.message.includes('404') || err.message.includes('no existe'))) {
        mostrarErrorSeguridad(`El producto "${nombreProducto}" ya no existe en el sistema.`);
      } else {
        notify("error", "No se pudo verificar el stock del producto. Intente nuevamente.");
      }
    }
  }

  async function onTablaClick(event) {
    let target = event.target;
    
    if (target.tagName === 'svg' || target.tagName === 'path') {
      target = target.closest('button');
    }
    
    const btn = target?.closest('.icon-action');
    
    if (!btn) return;

    const action = btn.getAttribute('data-action');
    const id = btn.getAttribute('data-id');
    
    if (!action || !id) return;

    event.stopPropagation();
    event.preventDefault();

    if (!validarIdProducto(id)) {
      mostrarErrorSeguridad('El ID del producto no es válido.');
      return;
    }

    if (action === "edit") {
      await prepararFormularioEdicion(id);
      openModal();
      return;
    }

    if (action === "delete") {
      const modelo = findModeloById(id);
      const nombreProducto = modelo ? `${modelo.nombre} (${modelo.marca_nombre || ""})` : `ID ${id}`;
      await eliminarProducto(id, nombreProducto);
      return;
    }
  }

  // ==================== REPORTES ====================
  
  let reporteDatosActuales = [];
  let reporteFiltrosActuales = {};

  const btnReportes = document.getElementById("btn-reportes");
  const modalReportes = document.getElementById("modal-reportes");
  const reporteClase = document.getElementById("reporte-clase");
  const reporteMarca = document.getElementById("reporte-marca");
  const reporteBusqueda = document.getElementById("reporte-busqueda");
  const reporteStockMin = document.getElementById("reporte-stock-min");
  const reporteStockMax = document.getElementById("reporte-stock-max");
  const btnGenerarReporte = document.getElementById("btn-generar-reporte");
  const btnLimpiarFiltrosReporte = document.getElementById("btn-limpiar-filtros-reporte");
  const btnExportarExcel = document.getElementById("btn-exportar-excel");
  const btnExportarPdf = document.getElementById("btn-exportar-pdf");
  const btnImprimir = document.getElementById("btn-imprimir");
  const reportePreview = document.getElementById("reporte-preview");
  const reporteTotal = document.getElementById("reporte-total");
  const reporteTabla = document.getElementById("reporte-tabla");

  function abrirModalReportes() {
    if (window.UiModal && typeof window.UiModal.openById === "function") {
      window.UiModal.openById("modal-reportes");
    }
  }

  function cerrarModalReportes() {
    if (window.UiModal && typeof window.UiModal.closeById === "function") {
      window.UiModal.closeById("modal-reportes");
    }
  }

  function cargarClasesMarcasReporte() {
    if (reporteClase) {
      fetchJson("/api/productos/clases", { method: "GET" }).then(data => {
        const clases = data.clases || [];
        reporteClase.innerHTML = '<option value="">Todas</option>' + 
          clases.map(c => `<option value="${c.id}">${escapeHtml(c.nombre)}</option>`).join("");
      }).catch(() => {});
    }
    
    if (reporteMarca) {
      fetchJson("/api/productos/marcas", { method: "GET" }).then(data => {
        const marcas = data.marcas || [];
        reporteMarca.innerHTML = '<option value="">Todas</option>' + 
          marcas.map(m => `<option value="${m.id}">${escapeHtml(m.nombre)}</option>`).join("");
      }).catch(() => {});
    }
  }

  function limpiarFiltrosReporte() {
    if (reporteClase) reporteClase.value = "";
    if (reporteMarca) reporteMarca.value = "";
    if (reporteBusqueda) reporteBusqueda.value = "";
    if (reporteStockMin) reporteStockMin.value = "";
    if (reporteStockMax) reporteStockMax.value = "";
  }

  async function generarReporte() {
    const filtros = {
      clase_id: reporteClase?.value || null,
      marca_id: reporteMarca?.value || null,
      q: reporteBusqueda?.value || "",
      stock_min: reporteStockMin?.value ? parseInt(reporteStockMin.value) : null,
      stock_max: reporteStockMax?.value ? parseInt(reporteStockMax.value) : null,
    };
    
    reporteFiltrosActuales = filtros;
    
    btnGenerarReporte.disabled = true;
    btnGenerarReporte.textContent = "Cargando...";
    
    try {
      const data = await fetchJson("/api/productos/reportes", {
        method: "POST",
        body: JSON.stringify(filtros)
      });
      
      reporteDatosActuales = data.productos || [];
      const total = data.total || 0;
      
      if (reportePreview) reportePreview.style.display = "block";
      if (reporteTotal) reporteTotal.textContent = `Total de productos: ${total}`;
      
      if (reporteTabla) {
        if (reporteDatosActuales.length === 0) {
          reporteTabla.innerHTML = '<tr><td colspan="5" class="table__empty">No hay productos con esos filtros</td></tr>';
        } else {
          reporteTabla.innerHTML = reporteDatosActuales.map(p => {
            let stockClass = '';
            if (p.stock === 0) stockClass = 'stock-out';
            else if (p.stock <= 5) stockClass = 'stock-low';
            else stockClass = 'stock-good';
            return `
              <tr>
                <td>${escapeHtml(p.id || '')}</td>
                <td><strong>${escapeHtml(p.nombre || '')}</strong></td>
                <td>${escapeHtml(p.marca_nombre || '-')}</td>
                <td>${escapeHtml(p.clase_nombre || '-')}</td>
                <td class="${stockClass}">${p.stock || 0} uds</td>
              </tr>
            `;
          }).join("");
        }
      }
      
      if (btnExportarExcel) btnExportarExcel.disabled = false;
      if (btnExportarPdf) btnExportarPdf.disabled = false;
      if (btnImprimir) btnImprimir.disabled = false;
      
    } catch (err) {
      notify("error", err.message || "Error al generar el reporte");
    } finally {
      btnGenerarReporte.disabled = false;
      btnGenerarReporte.textContent = "Generar reporte";
    }
  }

  function exportarAExcel() {
    if (reporteDatosActuales.length === 0) {
      notify("error", "No hay datos para exportar");
      return;
    }
    
    if (typeof XLSX === 'undefined') {
      notify("info", "Cargando librería de Excel...");
      const script = document.createElement('script');
      script.src = '/static/js/libs/xlsx.full.min.js';
      script.onload = () => exportarAExcel();
      document.head.appendChild(script);
      return;
    }
    
    const now = new Date();
    const fechaReporte = now.toLocaleDateString('es-ES');
    
    const tableData = reporteDatosActuales.map(p => ({
      id: p.id || '-',
      nombre: p.nombre || '-',
      marca: p.marca_nombre || '-',
      clase: p.clase_nombre || '-',
      stock: p.stock || 0,
      descripcion: p.descripcion || '-'
    }));
    
    const wb = XLSX.utils.book_new();
    const wsData = [];
    
    wsData.push(['REPORTE DE PRODUCTOS']);
    wsData.push(['']);
    wsData.push([`Generado: ${fechaReporte}`]);
    wsData.push([`Total productos: ${tableData.length}`]);
    wsData.push(['']);
    wsData.push(['ID', 'NOMBRE', 'MARCA', 'CLASE', 'STOCK', 'DESCRIPCIÓN']);
    
    tableData.forEach(item => {
      wsData.push([
        item.id,
        item.nombre,
        item.marca,
        item.clase,
        item.stock === 0 ? 'SIN STOCK' : String(item.stock),
        item.descripcion
      ]);
    });
    
    const ws = XLSX.utils.aoa_to_sheet(wsData);
    ws['!cols'] = [{ wch: 8 }, { wch: 30 }, { wch: 20 }, { wch: 20 }, { wch: 12 }, { wch: 45 }];
    
    XLSX.utils.book_append_sheet(wb, ws, "Productos");
    const timestamp = now.toISOString().slice(0, 19).replace(/:/g, '-');
    XLSX.writeFile(wb, `productos_${timestamp}.xlsx`);
    notify("success", "Reporte exportado a Excel");
  }

  function exportarAPdf() {
    if (reporteDatosActuales.length === 0) {
      notify("error", "No hay datos para exportar");
      return;
    }
    
    if (typeof window.jspdf === 'undefined' || typeof window.jspdf.jsPDF === 'undefined') {
      notify("info", "Cargando librería de PDF...");
      const script1 = document.createElement('script');
      script1.src = '/static/js/libs/jspdf.umd.min.js';
      script1.onload = () => {
        const script2 = document.createElement('script');
        script2.src = '/static/js/libs/jspdf.plugin.autotable.min.js';
        script2.onload = () => {
          setTimeout(() => exportarAPdf(), 150);
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
      primary: [243, 197, 0],
      dark: [18, 18, 18],
      white: [255, 255, 255],
      grayLight: [248, 249, 250],
      grayText: [102, 102, 106],
    };
    
    const logoUrl = window.location.origin + '/static/img/LOGO TRAZO.png';
    try {
      doc.addImage(logoUrl, 'PNG', (pageWidth - 45) / 2, 8, 45, 14);
    } catch(e) {}
    
    doc.setFont("helvetica", "bold");
    doc.setFontSize(22);
    doc.setTextColor(colors.dark[0], colors.dark[1], colors.dark[2]);
    doc.text("REPORTE DE PRODUCTOS", pageWidth / 2, 30, { align: 'center' });
    
    doc.setDrawColor(colors.primary[0], colors.primary[1], colors.primary[2]);
    doc.setLineWidth(0.8);
    doc.line(pageWidth / 2 - 35, 34, pageWidth / 2 + 35, 34);
    
    const now = new Date();
    const fechaStr = now.toLocaleDateString('es-ES');
    const horaStr = now.toLocaleTimeString('es-ES');
    
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.setTextColor(colors.grayText[0], colors.grayText[1], colors.grayText[2]);
    const metadata = [`Generado: ${fechaStr}`, `Hora: ${horaStr}`, `Total productos: ${reporteDatosActuales.length}`];
    doc.text(metadata.join(" • "), pageWidth / 2, 44, { align: 'center' });
    
    const startY = 52;
    const tableRows = reporteDatosActuales.map(p => [
      p.id || '-',
      p.nombre || '-',
      p.marca_nombre || '-',
      p.clase_nombre || '-',
      p.stock === 0 ? 'Sin stock' : `${p.stock} uds`,
      (p.descripcion || '-').substring(0, 70)
    ]);
    
    doc.autoTable({
      startY: startY,
      head: [['ID', 'NOMBRE', 'MARCA', 'CLASE', 'STOCK', 'DESCRIPCIÓN']],
      body: tableRows,
      theme: 'grid',
      headStyles: { fillColor: colors.primary, textColor: colors.white, fontStyle: 'bold', fontSize: 8, halign: 'center' },
      bodyStyles: { fontSize: 8.5, textColor: colors.dark, cellPadding: 4 },
      alternateRowStyles: { fillColor: colors.grayLight },
      margin: { left: 15, right: 15 },
    });
    
    const timestamp = now.toISOString().slice(0, 19).replace(/:/g, '-');
    doc.save(`productos_${timestamp}.pdf`);
    notify("success", "Reporte exportado a PDF");
  }

  function imprimirReporte() {
    if (reporteDatosActuales.length === 0) {
      notify("error", "No hay datos para imprimir");
      return;
    }
    
    const ventana = window.open("", "_blank");
    const fecha = new Date().toLocaleString();
    const logoUrl = window.location.origin + '/static/img/LOGO TRAZO.png';
    
    ventana.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>Reporte de Productos - ItuAccesorio</title>
        <style>
          @media print { body { margin: 0; padding: 20px; } .no-print { display: none; } }
          body { font-family: Arial, sans-serif; margin: 20px; padding: 20px; background: white; }
          h1 { text-align: center; border-bottom: 3px solid #f3c500; padding-bottom: 10px; }
          .logo { text-align: center; margin-bottom: 20px; }
          .logo img { height: 50px; }
          .info { text-align: center; margin-bottom: 20px; color: #666; font-size: 12px; }
          table { width: 100%; border-collapse: collapse; margin-top: 20px; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
          th { background: #121212; color: white; font-weight: bold; }
          tr:nth-child(even) { background: #f8f9fa; }
          .footer { margin-top: 30px; text-align: center; font-size: 10px; color: #666; border-top: 1px solid #ddd; padding-top: 10px; }
          .btn-print { background: #f3c500; border: none; padding: 10px 20px; cursor: pointer; margin-bottom: 20px; }
          .stock-out { color: #dc2626; font-weight: bold; }
          .stock-low { color: #f59e0b; font-weight: bold; }
          .stock-good { color: #10b981; }
        </style>
      </head>
      <body>
        <button class="btn-print no-print" onclick="window.print()">🖨 Imprimir</button>
        <div class="logo"><img src="${logoUrl}" alt="ItuAccesorio" onerror="this.style.display='none'"></div>
        <h1>REPORTE DE PRODUCTOS</h1>
        <div class="info">Generado: ${fecha} • Total productos: ${reporteDatosActuales.length}</div>
        <table>
          <thead><tr><th>ID</th><th>Nombre</th><th>Marca</th><th>Clase</th><th>Stock</th><th>Descripción</th></tr></thead>
          <tbody>
            ${reporteDatosActuales.map(p => {
              let stockClass = '';
              if (p.stock === 0) stockClass = 'stock-out';
              else if (p.stock <= 5) stockClass = 'stock-low';
              else stockClass = 'stock-good';
              return `
                <tr>
                  <td>${escapeHtml(p.id || '')}</td>
                  <td><strong>${escapeHtml(p.nombre || '')}</strong></td>
                  <td>${escapeHtml(p.marca_nombre || '-')}</td>
                  <td>${escapeHtml(p.clase_nombre || '-')}</td>
                  <td class="${stockClass}">${p.stock || 0} uds</td>
                  <td>${escapeHtml((p.descripcion || '-').substring(0, 100))}</td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
        <div class="footer">ItuAccesorio - Sistema de Gestión Comercial y Taller<br>Reporte generado automáticamente • ${fecha}</div>
      </body>
      </html>
    `);
    ventana.document.close();
  }

  // ==================== EVENTOS DE REPORTES ====================
  
  if (btnReportes) {
    btnReportes.addEventListener("click", () => {
      cargarClasesMarcasReporte();
      limpiarFiltrosReporte();
      if (reportePreview) reportePreview.style.display = "none";
      if (btnExportarExcel) btnExportarExcel.disabled = true;
      if (btnExportarPdf) btnExportarPdf.disabled = true;
      if (btnImprimir) btnImprimir.disabled = true;
      abrirModalReportes();
    });
  }

  if (btnGenerarReporte) btnGenerarReporte.addEventListener("click", generarReporte);
  if (btnLimpiarFiltrosReporte) btnLimpiarFiltrosReporte.addEventListener("click", limpiarFiltrosReporte);
  if (btnExportarExcel) btnExportarExcel.addEventListener("click", exportarAExcel);
  if (btnExportarPdf) btnExportarPdf.addEventListener("click", exportarAPdf);
  if (btnImprimir) btnImprimir.addEventListener("click", imprimirReporte);

  // ==================== EVENTOS DE FILTROS ====================
  
  if (btnAplicarFiltros) {
    btnAplicarFiltros.addEventListener("click", () => {
      if (fClaseSidebar) fClase.value = fClaseSidebar.value;
      if (fMarcaSidebar) fMarca.value = fMarcaSidebar.value;
      recargarModelosSegunFiltros();
    });
  }

  if (btnLimpiarFiltros) {
    btnLimpiarFiltros.addEventListener("click", () => {
      if (fClase) fClase.value = "";
      if (fMarca) fMarca.value = "";
      if (fClaseSidebar) fClaseSidebar.value = "";
      if (fMarcaSidebar) fMarcaSidebar.value = "";
      if (inputBuscar) inputBuscar.value = "";
      searchQuery = "";
      recargarModelosSegunFiltros();
    });
  }

  if (inputBuscar) {
    let timeoutId;
    inputBuscar.addEventListener("input", (e) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        searchQuery = e.target.value.trim();
        recargarModelosSegunFiltros();
      }, 300);
    });
  }

  // ==================== INICIALIZACIÓN ====================

  async function init() {
    if (btnNuevo) {
      btnNuevo.addEventListener("click", async () => {
        resetFormToCreate();
        setNewClassMode(false);
        setNewBrandMode(false);
        if (!state.clases.length) await cargarClases();
        if (!state.marcas.length) await cargarMarcas();
        await cargarCategorias();
        openModal();
      });
    }

    if (btnNuevoHeader) {
      btnNuevoHeader.addEventListener("click", async () => {
        resetFormToCreate();
        setNewClassMode(false);
        setNewBrandMode(false);
        if (!state.clases.length) await cargarClases();
        if (!state.marcas.length) await cargarMarcas();
        await cargarCategorias();
        openModal();
      });
    }

    if (btnNuevaClase) {
      btnNuevaClase.addEventListener("click", async (e) => {
        e.preventDefault();
        if (isCreatingNewClass) {
          setNewClassMode(false);
          if (pClase) pClase.focus();
        } else {
          setNewClassMode(true);
          if (pClase) pClase.value = "";
          setNewBrandMode(false);
          if (pClaseNueva) pClaseNueva.focus({ preventScroll: true });
        }
      });
    }

    if (btnNuevaMarca) {
      btnNuevaMarca.addEventListener("click", async (e) => {
        e.preventDefault();
        if (isCreatingNewBrand) {
          setNewBrandMode(false);
          if (pMarca) pMarca.focus();
        } else {
          setNewBrandMode(true);
          if (pMarca) pMarca.value = "";
          setNewClassMode(false);
          if (pMarcaNueva) pMarcaNueva.focus({ preventScroll: true });
        }
      });
    }

    if (btnCancelarClase) {
      btnCancelarClase.addEventListener("click", () => {
        setNewClassMode(false);
      });
    }

    if (btnCancelarMarca) {
      btnCancelarMarca.addEventListener("click", () => {
        setNewBrandMode(false);
      });
    }

    if (formProducto) {
      formProducto.addEventListener("submit", onSubmitProducto);
    }

    if (btnGuardarClase) {
      btnGuardarClase.addEventListener("click", onGuardarClaseClick);
    }

    if (btnGuardarMarca) {
      btnGuardarMarca.addEventListener("click", onGuardarMarcaClick);
    }

    if (tabla) {
      tabla.addEventListener("click", onTablaClick);
    }

    if (fClase) fClase.addEventListener("change", recargarModelosSegunFiltros);
    if (fMarca) fMarca.addEventListener("change", recargarModelosSegunFiltros);
    if (fClaseSidebar) fClaseSidebar.addEventListener("change", () => {
      if (fClase) fClase.value = fClaseSidebar.value;
    });
    if (fMarcaSidebar) fMarcaSidebar.addEventListener("change", () => {
      if (fMarca) fMarca.value = fMarcaSidebar.value;
    });

    try {
      await cargarClases();
      await cargarMarcas();
      await cargarCategorias();
      await cargarModelos({});
      aplicarFiltrosYRender();
    } catch (err) {
      if (tabla) tabla.innerHTML = emptyRow(5, err?.message || "No se pudo cargar el módulo.");
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();