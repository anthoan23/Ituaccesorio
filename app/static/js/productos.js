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

  // Validar formulario antes de enviar
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

  function notify(type, message) {
    if (window.FeedbackModal && typeof window.FeedbackModal.show === "function") {
      window.FeedbackModal.show({
        type: type === "error" ? "error" : "success",
        title: type === "error" ? "No se pudo completar" : "Acción exitosa",
        message,
      });
      return;
    }
    alert(message);
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
    
    // Inicializar validadores después de abrir el modal
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
    
    // Limpiar validaciones al cerrar
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
    
    // Resetear validadores
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
    
    // Reinicializar validadores después de mostrar/ocultar campos
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
    
    // Reinicializar validadores después de mostrar/ocultar campos
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

    // Validar formulario antes de enviar
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

      // Validar solo letras
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

      // Validar letras, números y espacios
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
      const ok = confirm(`¿Seguro que deseas eliminar el producto ${label}?`);
      if (!ok) return;

      try {
        await fetchJson(`/api/productos/modelos/${encodeURIComponent(id)}`, { method: "DELETE" });
        await recargarModelosSegunFiltros();
        notify("success", "Producto eliminado correctamente.");
      } catch (err) {
        notify("error", err?.message || "No se pudo eliminar.");
      }
    }
  }

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