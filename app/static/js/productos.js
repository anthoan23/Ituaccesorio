(() => {
  "use strict";

  const state = {
    clases: [],
    marcas: [],
    modelos: [],
  };

  const tabla = document.getElementById("tabla-productos");
  const btnNuevo = document.getElementById("btn-registrar-producto");
  const modal = document.getElementById("modal-registro-producto");
  const btnCancelar = document.getElementById("btn-cancelar-producto");
  const formProducto = document.getElementById("form-producto");
  const csrfToken = document.querySelector("input[name='_csrf_token']")?.value || "";

  const fClase = document.getElementById("f-clase");
  const fMarca = document.getElementById("f-marca");
  const fTexto = document.getElementById("f-texto");
  const btnAplicar = document.getElementById("btn-aplicar");
  const btnLimpiar = document.getElementById("btn-limpiar");

  const pClase = document.getElementById("p-clase");
  const pClaseNuevaWrap = document.getElementById("p-clase-nueva-wrap");
  const pClaseNueva = document.getElementById("p-clase-nueva");
  const pMarca = document.getElementById("p-marca");
  const pMarcaNuevaWrap = document.getElementById("p-marca-nueva-wrap");
  const pMarcaNueva = document.getElementById("p-marca-nueva");
  const pModelo = document.getElementById("p-modelo");
  const pDescripcion = document.getElementById("p-descripcion");
  const btnNuevaClase = document.getElementById("btn-nueva-clase");
  const btnNuevaMarca = document.getElementById("btn-nueva-marca");
  const btnGuardarClase = document.getElementById("btn-guardar-clase");
  const btnGuardarMarca = document.getElementById("btn-guardar-marca");

  let isCreatingNewClass = false;
  let isCreatingNewBrand = false;
  let isSubmitting = false;

  const MAX = {
    clase: 30,
    marca: 30,
    producto: 30,
    descripcion: 300,
  };

  // ==================== MODAL DE CONFIRMACIÓN ÚNICO ====================
  
  function mostrarModalConfirmacion(mensaje, onConfirmar, soloInformacion = false, tipo = 'info') {
    // Eliminar modal existente si hay
    const modalExistente = document.getElementById('confirmacion-modal');
    if (modalExistente) modalExistente.remove();
    
    // Determinar el tipo de modal
    const esError = tipo === 'error';
    const esExito = tipo === 'success';
    const esInfo = tipo === 'info';
    
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
      titulo = "Confirmar acción";
      btnTexto = "Eliminar";
      btnColor = "#dc2626";
      icono = "⚠️";
    }
    
    const modalDiv = document.createElement('div');
    modalDiv.id = 'confirmacion-modal';
    modalDiv.className = 'ui-modal';
    modalDiv.setAttribute('data-modal', '');
    modalDiv.setAttribute('hidden', '');
    modalDiv.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;z-index:10000;display:flex;align-items:center;justify-content:center;';
    
    modalDiv.innerHTML = `
        <div class="ui-modal__dialog ui-modal__dialog--sm" role="dialog" aria-modal="true" style="animation:modalFadeIn 0.2s ease-out;margin:1rem;background:white;border-radius:20px;box-shadow:0 25px 50px -12px rgba(0,0,0,0.25);max-width:450px;width:100%;${esError ? 'border-top:4px solid #dc2626' : 'border-top:4px solid #f3c500'}">
            <header class="ui-modal__header" style="display:flex;justify-content:space-between;align-items:center;padding:1rem 1.5rem;border-bottom:1px solid #e5e7eb;">
                <h3 class="ui-modal__title" style="margin:0;font-size:1.25rem;font-weight:600;">${titulo}</h3>
                <button type="button" class="ui-modal__close" data-close-modal aria-label="Cerrar" style="background:none;border:none;font-size:1.5rem;cursor:pointer;">×</button>
            </header>
            <div class="ui-modal__body" style="padding:1.5rem;">
                <div style="text-align:center;font-size:3rem;margin-bottom:0.5rem;">${icono}</div>
                <p id="confirmacion-modal-mensaje" style="margin:0;font-size:1rem;color:#121212;text-align:center;">${mensaje}</p>
            </div>
            <div class="ui-modal__footer" style="display:flex;gap:0.75rem;justify-content:center;padding:1rem 1.5rem;border-top:1px solid #e5e7eb;">
                ${!soloInformacion && !esExito && !esInfo ? '<button type="button" class="ui-btn ui-btn--ghost" id="btn-cancelar-confirmacion" style="padding:0.5rem 1rem;border:none;border-radius:8px;background:#f3f4f6;color:#121212;font-weight:500;cursor:pointer;">Cancelar</button>' : ''}
                <button type="button" class="ui-btn" id="btn-confirmar-accion" style="padding:0.5rem 1rem;border:none;border-radius:8px;background:${btnColor};color:white;font-weight:500;cursor:pointer;">${btnTexto}</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modalDiv);
    document.body.style.overflow = 'hidden';
    
    const cerrarModal = () => {
      modalDiv.remove();
      document.body.style.overflow = '';
    };
    
    // Botón cancelar (solo si no es solo información ni éxito)
    if (!soloInformacion && !esExito && !esInfo) {
      const cancelBtn = document.getElementById('btn-cancelar-confirmacion');
      if (cancelBtn) {
        cancelBtn.addEventListener('click', cerrarModal);
      }
    }
    
    // Botón confirmar
    const confirmBtn = document.getElementById('btn-confirmar-accion');
    if (confirmBtn) {
      confirmBtn.addEventListener('click', async () => {
        cerrarModal();
        if (onConfirmar && !soloInformacion && !esExito && !esInfo) {
          await onConfirmar();
        }
      });
    }
    
    // Botón cerrar (X)
    const closeBtn = modalDiv.querySelector('[data-close-modal]');
    if (closeBtn) {
      closeBtn.addEventListener('click', cerrarModal);
    }
    
    // Cerrar al hacer click en el backdrop
    modalDiv.addEventListener('click', (e) => {
      if (e.target === modalDiv) cerrarModal();
    });
    
    // Auto cerrar después de 3 segundos si es solo información o éxito
    if (soloInformacion || esExito || esInfo) {
      setTimeout(() => {
        if (document.getElementById('confirmacion-modal')) cerrarModal();
      }, 3000);
    }
  }

  function notify(type, message) {
    if (type === 'error') {
      mostrarModalConfirmacion(message, null, true, 'error');
    } else if (type === 'success') {
      mostrarModalConfirmacion(message, null, true, 'success');
    } else {
      mostrarModalConfirmacion(message, null, true, 'info');
    }
  }

  // ==================== FIN MODALES ====================

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
    return `<tr><td colspan="${colspan}">${escapeHtml(text)}</td></tr>`;
  }

  function setBodyScrollLocked() {
    const anyModalOpen = document.querySelector(".modal:not(.is-hidden)");
    document.body.style.overflow = anyModalOpen ? "hidden" : "";
  }

  function openModal() {
    if (!modal) return;
    modal.classList.remove("is-hidden");
    modal.setAttribute("aria-hidden", "false");
    if (btnNuevo) btnNuevo.setAttribute("aria-expanded", "true");
    setBodyScrollLocked();

    const firstInput = modal.querySelector("input, select");
    if (firstInput) firstInput.focus({ preventScroll: true });
    
    if (window.FieldValidator) {
      setTimeout(() => window.FieldValidator.init(), 100);
    }
  }

  function closeModal() {
    if (!modal) return;
    modal.classList.add("is-hidden");
    modal.setAttribute("aria-hidden", "true");
    if (btnNuevo) btnNuevo.setAttribute("aria-expanded", "false");
    setBodyScrollLocked();
    
    if (formProducto && window.FieldValidator) {
      window.FieldValidator.resetForm(formProducto);
    }
  }

  function resetFormToCreate() {
    if (!formProducto) return;
    formProducto.reset();
    const idInput = formProducto.querySelector("input[name='id_modelo']");
    if (idInput) idInput.value = "";
    const title = document.getElementById("producto-modal-title");
    if (title) title.textContent = "Registrar producto";
    setNewClassMode(false);
    setNewBrandMode(false);
    if (btnGuardarClase) btnGuardarClase.disabled = false;
    if (btnGuardarMarca) btnGuardarMarca.disabled = false;
    
    if (window.FieldValidator) {
      window.FieldValidator.resetForm(formProducto);
    }
  }

  function setNewClassMode(isNew) {
    isCreatingNewClass = Boolean(isNew);
    if (pClaseNuevaWrap) pClaseNuevaWrap.classList.toggle("is-hidden", !isNew);
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
    if (pMarcaNuevaWrap) pMarcaNuevaWrap.classList.toggle("is-hidden", !isNew);
    if (pMarcaNueva) {
      pMarcaNueva.required = Boolean(isNew);
      if (!isNew && pMarcaNueva.value) pMarcaNueva.value = "";
    }
    if (btnNuevaMarca) btnNuevaMarca.textContent = isNew ? "Cancelar" : "Nueva marca";
    
    if (window.FieldValidator) {
      setTimeout(() => window.FieldValidator.init(), 100);
    }
  }

  function renderSelect(select, items, { includeAll = false, allLabel = "Todos", placeholder = "Selecciona" } = {}) {
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

  async function cargarClases() {
    const data = await fetchJson("/api/productos/clases", { method: "GET" });
    state.clases = Array.isArray(data.clases) ? data.clases : [];
    renderSelect(fClase, state.clases, { includeAll: true, allLabel: "Todas" });
    renderClaseFormSelect();
  }

  async function cargarMarcas() {
    const data = await fetchJson("/api/productos/marcas", { method: "GET" });
    const marcas = Array.isArray(data.marcas) ? data.marcas : [];
    state.marcas = marcas;
    renderSelect(fMarca, marcas, { includeAll: true, allLabel: "Todas" });
    renderMarcaFormSelect(marcas);
  }

  async function cargarModelos({ claseId = "", marcaId = "", q = "" } = {}) {
    const params = new URLSearchParams();
    if (claseId) params.set("clase_id", String(claseId));
    if (marcaId) params.set("marca_id", String(marcaId));
    if (q) params.set("q", String(q));
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
          <tr>
            <td><span class="product-thumb" aria-hidden="true"></span></td>
            <td>
              <div class="product-meta">
                <strong class="product-name">${escapeHtml(m.nombre || "")}</strong>
                <span class="product-sku">Código: PRO${escapeHtml(m.id ?? "")}</span>
              </div>
            </td>
            <td>${escapeHtml(m.marca_nombre || "")}</td>
            <td><span class="chip">${escapeHtml(m.clase_nombre || "")}</span></td>
            <td class="table__actions">
              <div class="row-actions" aria-label="Acciones del producto">
                <button class="icon-action" type="button" aria-label="Editar" data-action="edit" data-id="${escapeHtml(m.id ?? "")}">
                  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25Zm18-11.5a1 1 0 0 0 0-1.41l-1.34-1.34a1 1 0 0 0-1.41 0l-1.12 1.12 3.75 3.75L21 5.75Z" fill="currentColor"/></svg>
                </button>
                <button class="icon-action" type="button" aria-label="Eliminar" data-action="delete" data-id="${escapeHtml(m.id ?? "")}">
                  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 7h12l-1 14H7L6 7Zm3-3h6l1 2H8l1-2Z" fill="currentColor"/></svg>
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
    const q = fTexto ? String(fTexto.value || "").trim() : "";

    let modelos = state.modelos;
    if (claseId) {
      modelos = modelos.filter((m) => String(m.id_clase || "") === String(claseId));
    }
    if (marcaId) {
      modelos = modelos.filter((m) => String(m.id_marca || "") === String(marcaId));
    }
    if (q) {
      const qNorm = q.toLowerCase();
      modelos = modelos.filter((m) => String(m.nombre || "").toLowerCase().includes(qNorm));
    }
    renderTabla(modelos);
  }

  async function onFiltroClaseChange() {
    await recargarModelosSegunFiltros();
  }

  async function recargarModelosSegunFiltros() {
    const claseId = fClase ? String(fClase.value || "") : "";
    const marcaId = fMarca ? String(fMarca.value || "") : "";
    const q = fTexto ? String(fTexto.value || "").trim() : "";
    await cargarModelos({ claseId, marcaId, q });
    aplicarFiltrosYRender();
  }

  function findModeloById(id) {
    return state.modelos.find((m) => String(m.id) === String(id));
  }

  async function prepararFormularioEdicion(idModelo) {
    const modelo = findModeloById(idModelo);
    if (!modelo || !formProducto) return;

    resetFormToCreate();
    const title = document.getElementById("producto-modal-title");
    if (title) title.textContent = "Editar producto";

    const idInput = formProducto.querySelector("input[name='id_modelo']");
    if (idInput) idInput.value = String(modelo.id || "");

    if (!state.clases.length) await cargarClases();
    if (!state.marcas.length) await cargarMarcas();

    if (pClase) pClase.value = String(modelo.id_clase || "");
    setNewClassMode(false);

    if (pMarca) pMarca.value = String(modelo.id_marca || "");
    setNewBrandMode(false);

    if (pModelo) pModelo.value = modelo.nombre || "";
    if (pDescripcion) pDescripcion.value = modelo.descripcion || "";
  }

  async function crearClaseSiHaceFalta() {
    if (!pClase) return null;
    if (!isCreatingNewClass) {
      const v = String(pClase.value || "");
      return v ? Number(v) : null;
    }

    const nombre = String(pClaseNueva?.value || "").trim();
    if (!nombre) throw new Error("Debes escribir el nombre de la nueva clase.");

    const data = await fetchJson("/api/productos/clases", {
      method: "POST",
      body: JSON.stringify({ nombre, num_i: null }),
    });

    return Number(data.id);
  }

  async function crearMarcaSiHaceFalta(idClase) {
    if (!pMarca) return null;
    if (!isCreatingNewBrand) {
      const v = String(pMarca.value || "");
      return v ? Number(v) : null;
    }

    const nombre = String(pMarcaNueva?.value || "").trim();
    if (!nombre) throw new Error("Debes escribir el nombre de la nueva marca.");

    const data = await fetchJson("/api/productos/marcas", {
      method: "POST",
      body: JSON.stringify({ nombre }),
    });
    return Number(data.id);
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
        await fetchJson("/api/productos/modelos", {
          method: "POST",
          body: JSON.stringify({ nombre: nombreModelo, id_marca: finalMarcaId, id_clase: claseIdFinal, descripcion }),
        });
      }

      closeModal();
      await recargarModelosSegunFiltros();
      notify("success", "Producto guardado correctamente.");
    } catch (err) {
      notify("error", err?.message || "No se pudo guardar.");
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

      if (pMarca) pMarca.value = "";

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

  // ==================== ELIMINAR PRODUCTO CON MODAL ====================
  
  async function onTablaClick(event) {
    const btn = event.target?.closest("button.icon-action");
    if (!btn) return;

    const action = btn.getAttribute("data-action");
    const id = btn.getAttribute("data-id");
    if (!action || !id) return;

    if (action === "edit") {
      await prepararFormularioEdicion(id);
      openModal();
      return;
    }

    if (action === "delete") {
      const modelo = findModeloById(id);
      const label = modelo ? `${modelo.nombre} (${modelo.marca_nombre || ""})` : `ID ${id}`;
      
      try {
        const data = await fetchJson(`/api/productos/modelos/${encodeURIComponent(id)}/verificar-stock`, { method: 'GET' });
        const tieneStock = data.tiene_stock || false;
        const stock = data.stock || 0;
        
        if (tieneStock) {
          mostrarModalConfirmacion(
            `No se puede eliminar el producto "${label}" porque tiene ${stock} unidades en inventario.`,
            null,
            true,
            'error'
          );
        } else {
          mostrarModalConfirmacion(`¿Seguro que deseas eliminar el producto "${label}"?`, async () => {
            try {
              await fetchJson(`/api/productos/modelos/${encodeURIComponent(id)}`, { method: "DELETE" });
              await recargarModelosSegunFiltros();
              notify("success", `Producto "${label}" eliminado correctamente.`);
            } catch (err) {
              notify("error", err?.message || "No se pudo eliminar el producto.");
            }
          });
        }
      } catch (err) {
        notify("error", "No se pudo verificar el stock del producto. Intente nuevamente.");
      }
      return;
    }
  }

  // ==================== FIN ELIMINAR PRODUCTO ====================

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
  const btnLimpiarFiltros = document.getElementById("btn-limpiar-filtros");
  const btnExportarExcel = document.getElementById("btn-exportar-excel");
  const btnExportarPdf = document.getElementById("btn-exportar-pdf");
  const btnImprimir = document.getElementById("btn-imprimir");
  const reportePreview = document.getElementById("reporte-preview");
  const reporteTotal = document.getElementById("reporte-total");
  const reporteTabla = document.getElementById("reporte-tabla");

  function abrirModalReportes() {
    if (!modalReportes) return;
    modalReportes.classList.remove("is-hidden");
    modalReportes.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function cerrarModalReportes() {
    if (!modalReportes) return;
    modalReportes.classList.add("is-hidden");
    modalReportes.setAttribute("aria-hidden", "true");
    if (!document.querySelector(".modal:not(.is-hidden)")) {
      document.body.style.overflow = "";
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
      clase_nombre: reporteClase?.options[reporteClase.selectedIndex]?.text || null,
      marca_nombre: reporteMarca?.options[reporteMarca.selectedIndex]?.text || null
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
          reporteTabla.innerHTML = reporteDatosActuales.map(p => `
            <tr>
              <td>${escapeHtml(p.id || '')}</td>
              <td>${escapeHtml(p.nombre || '')}</td>
              <td>${escapeHtml(p.marca_nombre || '-')}</td>
              <td>${escapeHtml(p.clase_nombre || '-')}</td>
              <td>${p.stock === 0 ? '<span style="color:#f44336;">Sin stock</span>' : (p.stock <= 5 ? '<span style="color:#ff9800;">' + p.stock + ' uds</span>' : p.stock)}</td>
            </tr>
          `).join("");
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
    
    const colors = {
      dark: '121212',
      primary: 'F3C500',
      white: 'FFFFFF',
      grayLight: 'F8F9FA',
      grayBorder: 'E0E0E0'
    };
    
    const now = new Date();
    const fechaReporte = now.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
    
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
    
    const filtrosTexto = [];
    if (reporteFiltrosActuales.clase_nombre) filtrosTexto.push(`Clase: ${reporteFiltrosActuales.clase_nombre}`);
    if (reporteFiltrosActuales.marca_nombre) filtrosTexto.push(`Marca: ${reporteFiltrosActuales.marca_nombre}`);
    if (reporteFiltrosActuales.q) filtrosTexto.push(`Búsqueda: ${reporteFiltrosActuales.q}`);
    if (reporteFiltrosActuales.stock_min) filtrosTexto.push(`Stock ≥ ${reporteFiltrosActuales.stock_min}`);
    if (reporteFiltrosActuales.stock_max) filtrosTexto.push(`Stock ≤ ${reporteFiltrosActuales.stock_max}`);
    
    const filtrosLine = filtrosTexto.length > 0 ? `Filtros aplicados: ${filtrosTexto.join(' | ')}` : 'Filtros aplicados: Todos los productos';
    wsData.push([filtrosLine]);
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
    const pageHeight = doc.internal.pageSize.getHeight();
    
    const colors = {
      primary: [243, 197, 0],
      dark: [18, 18, 18],
      white: [255, 255, 255],
      grayLight: [248, 249, 250],
      grayMedium: [245, 246, 248],
      grayText: [102, 102, 106],
      border: [225, 226, 230]
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
    
    const filtrosActivos = [];
    if (reporteFiltrosActuales.clase_nombre) filtrosActivos.push(`Clase: ${reporteFiltrosActuales.clase_nombre}`);
    if (reporteFiltrosActuales.marca_nombre) filtrosActivos.push(`Marca: ${reporteFiltrosActuales.marca_nombre}`);
    if (reporteFiltrosActuales.q) filtrosActivos.push(`Búsqueda: ${reporteFiltrosActuales.q}`);
    if (reporteFiltrosActuales.stock_min) filtrosActivos.push(`Stock ≥ ${reporteFiltrosActuales.stock_min}`);
    if (reporteFiltrosActuales.stock_max) filtrosActivos.push(`Stock ≤ ${reporteFiltrosActuales.stock_max}`);
    
    const filterBoxY = 54;
    doc.setFillColor(colors.grayLight[0], colors.grayLight[1], colors.grayLight[2]);
    doc.rect(15, filterBoxY, pageWidth - 30, 10, 'F');
    doc.setFont("helvetica", "italic");
    doc.setFontSize(8.5);
    doc.setTextColor(colors.grayText[0], colors.grayText[1], colors.grayText[2]);
    doc.text(filtrosActivos.length ? `Filtros: ${filtrosActivos.join(" • ")}` : "Filtros: Todos los productos", 18, filterBoxY + 7);
    
    const startY = filterBoxY + 14;
    const tableRows = reporteDatosActuales.map(p => {
      let stockDisplay = '';
      if (p.stock === 0) stockDisplay = 'Sin stock';
      else if (p.stock <= 5) stockDisplay = `${p.stock} uds`;
      else stockDisplay = `${p.stock} uds`;
      return [
        p.id || '-',
        p.nombre || '-',
        p.marca_nombre || '-',
        p.clase_nombre || '-',
        stockDisplay,
        (p.descripcion || '-').substring(0, 70)
      ];
    });
    
    doc.autoTable({
      startY: startY,
      head: [['ID', 'NOMBRE', 'MARCA', 'CLASE', 'STOCK', 'DESCRIPCIÓN']],
      body: tableRows,
      theme: 'grid',
      headStyles: { fillColor: colors.primary, textColor: colors.white, fontStyle: 'bold', fontSize: 8, halign: 'center' },
      bodyStyles: { fontSize: 8.5, textColor: colors.dark, cellPadding: 4 },
      alternateRowStyles: { fillColor: colors.grayLight },
      margin: { left: 15, right: 15 },
      didDrawPage: (data) => {
        doc.setFontSize(7);
        doc.setTextColor(colors.grayText[0], colors.grayText[1], colors.grayText[2]);
        doc.text("ItuAccesorio System · Reporte Generado Exclusivamente Para ituaccesorio", pageWidth / 2, pageHeight - 8, { align: 'center' });
        doc.text(`Página ${data.pageNumber}`, pageWidth - 15, pageHeight - 8, { align: 'right' });
      }
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
    
    const filtrosTexto = [];
    if (reporteFiltrosActuales.clase_nombre) filtrosTexto.push(`Clase: ${reporteFiltrosActuales.clase_nombre}`);
    if (reporteFiltrosActuales.marca_nombre) filtrosTexto.push(`Marca: ${reporteFiltrosActuales.marca_nombre}`);
    if (reporteFiltrosActuales.q) filtrosTexto.push(`Búsqueda: ${reporteFiltrosActuales.q}`);
    if (reporteFiltrosActuales.stock_min) filtrosTexto.push(`Stock ≥ ${reporteFiltrosActuales.stock_min}`);
    if (reporteFiltrosActuales.stock_max) filtrosTexto.push(`Stock ≤ ${reporteFiltrosActuales.stock_max}`);
    
    ventana.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>Reporte de Productos - ItuAccesorio</title>
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
        ${filtrosTexto.length ? `<div class="filters"><strong>Filtros:</strong> ${filtrosTexto.join(" • ")}</div>` : ''}
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

  // Eventos de reportes
  if (btnReportes) {
    btnReportes.addEventListener("click", () => {
      cargarClasesMarcasReporte();
      limpiarFiltrosReporte();
      reportePreview.style.display = "none";
      if (btnExportarExcel) btnExportarExcel.disabled = true;
      if (btnExportarPdf) btnExportarPdf.disabled = true;
      if (btnImprimir) btnImprimir.disabled = true;
      abrirModalReportes();
    });
  }

  if (modalReportes) {
    modalReportes.addEventListener("click", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      if (target.dataset.modalClose === "true") {
        cerrarModalReportes();
        return;
      }
      if (target === modalReportes) {
        cerrarModalReportes();
      }
    });
  }

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    if (modalReportes && !modalReportes.classList.contains("is-hidden")) {
      cerrarModalReportes();
    }
  });

  if (btnGenerarReporte) btnGenerarReporte.addEventListener("click", generarReporte);
  if (btnLimpiarFiltros) btnLimpiarFiltros.addEventListener("click", limpiarFiltrosReporte);
  if (btnExportarExcel) btnExportarExcel.addEventListener("click", exportarAExcel);
  if (btnExportarPdf) btnExportarPdf.addEventListener("click", exportarAPdf);
  if (btnImprimir) btnImprimir.addEventListener("click", imprimirReporte);

  // ==================== FIN REPORTES ====================

  async function init() {
    closeModal();

    if (btnNuevo) {
      btnNuevo.addEventListener("click", async () => {
        resetFormToCreate();
        if (!state.clases.length) await cargarClases();
        if (!state.marcas.length) await cargarMarcas();
        openModal();
      });
    }

    if (btnNuevaClase) {
      btnNuevaClase.addEventListener("click", async () => {
        setNewClassMode(!isCreatingNewClass);
        if (isCreatingNewClass) {
          if (pClase) pClase.value = "";
          renderMarcaFormSelect([]);
          setNewBrandMode(false);
          if (pClaseNueva) pClaseNueva.focus({ preventScroll: true });
        }
      });
    }

    if (btnNuevaMarca) {
      btnNuevaMarca.addEventListener("click", async () => {
        setNewBrandMode(!isCreatingNewBrand);
        if (isCreatingNewBrand) {
          if (pMarca) pMarca.value = "";
          if (pMarcaNueva) pMarcaNueva.focus({ preventScroll: true });
        }
      });
    }

    if (btnCancelar) {
      btnCancelar.addEventListener("click", closeModal);
    }

    if (modal) {
      modal.addEventListener("click", (event) => {
        const target = event.target;
        if (target && target instanceof HTMLElement && target.dataset.modalClose === "true") {
          closeModal();
        }
      });
    }

    document.addEventListener("keydown", (event) => {
      if (event.key !== "Escape") return;
      if (modal && !modal.classList.contains("is-hidden")) {
        closeModal();
      }
    });

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

    if (fClase) fClase.addEventListener("change", onFiltroClaseChange);
    if (fMarca) fMarca.addEventListener("change", recargarModelosSegunFiltros);
    if (btnAplicar) btnAplicar.addEventListener("click", recargarModelosSegunFiltros);
    if (btnLimpiar) {
      btnLimpiar.addEventListener("click", async () => {
        if (fTexto) fTexto.value = "";
        if (fClase) fClase.value = "";
        if (fMarca) fMarca.value = "";
        await recargarModelosSegunFiltros();
      });
    }

    if (pClase) {
      pClase.addEventListener("change", async () => {
        if (isCreatingNewClass) setNewClassMode(false);
        if (pMarca) pMarca.value = "";
      });
    }

    try {
      await cargarClases();
      await cargarMarcas();
      await cargarModelos({});
      aplicarFiltrosYRender();
    } catch (err) {
      if (tabla) tabla.innerHTML = emptyRow(5, err?.message || "No se pudo cargar el módulo.");
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();