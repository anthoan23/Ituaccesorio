const tablaClientes = document.getElementById("tabla-clientes");
const btnNuevoCliente = document.getElementById("btn-nuevo-cliente");
const formCliente = document.getElementById("form-cliente");
const clienteIdInput = formCliente?.querySelector("input[name='id']");
const toast = document.getElementById("toast-mensaje");
const statClientes = document.getElementById("stat-clientes");
const tipoClienteSelect = document.getElementById("tipo-cliente");

let clientes = [];
const csrfToken = document.querySelector("input[name='_csrf_token']")?.value || "";

// ==================== VALIDACIÓN ====================

function validarFormularioAntesDeEnviar(form, nombreFormulario) {
    if (!window.FieldValidator) {
        console.warn('FieldValidator no disponible');
        return true;
    }
    
    const isValid = window.FieldValidator.validateForm(form);
    
    if (!isValid) {
        mostrarToast(`Por favor, corrige los errores en el formulario de ${nombreFormulario}.`, true);
        
        const primerError = form.querySelector('.field-error');
        if (primerError) {
            primerError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            primerError.focus();
        }
        
        return false;
    }
    
    return true;
}

// ==================== MOSTRAR/OCULTAR CAMPOS POR TIPO ====================

function toggleCamposPorTipo() {
    const tipo = tipoClienteSelect?.value;
    const camposNatural = document.getElementById("campos-natural");
    const camposJuridico = document.getElementById("campos-juridico");
    const inputsNatural = camposNatural?.querySelectorAll("input, select");
    const inputsJuridico = camposJuridico?.querySelectorAll("input, select");
    
    if (tipo === "natural") {
        if (camposNatural) camposNatural.style.display = "grid";
        if (camposJuridico) camposJuridico.style.display = "none";
        // Habilitar/requerir campos de persona natural
        inputsNatural?.forEach(input => {
            if (input.hasAttribute('data-required')) {
                input.required = true;
            } else if (input.id !== 'id' && input.name !== 'id') {
                input.required = true;
            }
        });
        inputsJuridico?.forEach(input => {
            input.required = false;
            input.value = "";
        });
    } else if (tipo === "juridico") {
        if (camposNatural) camposNatural.style.display = "none";
        if (camposJuridico) camposJuridico.style.display = "grid";
        // Habilitar/requerir campos de persona jurídica
        inputsJuridico?.forEach(input => {
            if (input.hasAttribute('data-required')) {
                input.required = true;
            } else if (input.name?.includes('rif') || input.name?.includes('razon_social') || input.name?.includes('telefono')) {
                input.required = true;
            }
        });
        inputsNatural?.forEach(input => {
            input.required = false;
            input.value = "";
        });
    } else {
        if (camposNatural) camposNatural.style.display = "none";
        if (camposJuridico) camposJuridico.style.display = "none";
    }
    
    // Reinicializar validadores
    if (window.FieldValidator) {
        setTimeout(() => window.FieldValidator.init(), 50);
    }
}

// ==================== INICIALIZACIÓN ====================

function initClientes() {
    btnNuevoCliente?.addEventListener("click", abrirFormularioNuevo);
    formCliente?.addEventListener("submit", onSubmitCliente);
    tipoClienteSelect?.addEventListener("change", toggleCamposPorTipo);
    document.addEventListener("click", onTablaClick);
    cargarClientes();
}

initClientes();

// ==================== FUNCIONES DE UI ====================

function abrirFormularioNuevo() {
    limpiarFormulario();
    if (tipoClienteSelect) tipoClienteSelect.value = "";
    toggleCamposPorTipo();
    if (window.UiModal && typeof window.UiModal.openById === "function") {
        window.UiModal.openById("modal-cliente");
        if (window.FieldValidator) {
            setTimeout(() => window.FieldValidator.init(), 100);
        }
    }
}

function onTablaClick(event) {
    const btn = event.target.closest("button[data-action]");
    if (!btn) return;

    const id = btn.dataset.id;
    const action = btn.dataset.action;
    if (!id || !action) return;

    if (action === "edit") {
        abrirEdicion(id);
        return;
    }

    if (action === "delete") {
        eliminarCliente(id);
        return;
    }
}

// ==================== CRUD ====================

async function cargarClientes() {
    try {
        const data = await fetchJson("/api/clientes");
        clientes = data.clientes || [];
        renderClientes();
    } catch (error) {
        mostrarToast(error.message || "No se pudo cargar la lista de clientes.", true);
    }
}

function renderClientes() {
    if (statClientes) statClientes.textContent = String(clientes.length);
    if (!tablaClientes) return;

    if (!clientes.length) {
        tablaClientes.innerHTML = `<tr><td colspan="8" class="table__empty">No hay clientes registrados.</td></tr>`;
        return;
    }

    tablaClientes.innerHTML = clientes
        .map((cliente) => {
            const tipo = cliente.tipo || (cliente.cedula ? "natural" : "juridico");
            let nombreDisplay = "";
            let apellidoDisplay = "";
            
            if (tipo === "natural") {
                const nombreCompleto = cliente.nombre || "";
                const espacioIndex = nombreCompleto.indexOf(' ');
                if (espacioIndex > 0) {
                    nombreDisplay = nombreCompleto.substring(0, espacioIndex);
                    apellidoDisplay = nombreCompleto.substring(espacioIndex + 1);
                } else {
                    nombreDisplay = nombreCompleto;
                    apellidoDisplay = "";
                }
            } else {
                nombreDisplay = cliente.razon_social || cliente.nombre || "";
                apellidoDisplay = cliente.rif || "";
            }
            
            return `
                <tr>
                    <td class="col-id"><span class="chip">${escapeHtml(String(cliente.id))}</span></td>
                    <td><span class="badge ${tipo === 'natural' ? 'badge--natural' : 'badge--juridico'}">${tipo === 'natural' ? 'Persona Natural' : 'Persona Jurídica'}</span></td>
                    <td>${escapeHtml(nombreDisplay)}</td>
                    <td>${escapeHtml(apellidoDisplay)}</td>
                    <td>${escapeHtml(cliente.celular || cliente.telefono || "")}</td>
                    <td>${escapeHtml(cliente.correo || "")}</td>
                    <td>${escapeHtml(cliente.direccion || "")}</td>
                    <td class="table__actions">
                        <div class="row-actions">
                            <button class="icon-action" type="button" data-action="edit" data-id="${escapeHtml(String(cliente.id))}" title="Editar">✎</button>
                            <button class="icon-action icon-action--danger" type="button" data-action="delete" data-id="${escapeHtml(String(cliente.id))}" title="Eliminar">🗑</button>
                        </div>
                    </td>
                </tr>
            `;
        })
        .join("");
}

function abrirEdicion(id) {
    const cliente = clientes.find((item) => String(item.id) === String(id));
    if (!cliente || !formCliente) return;

    limpiarFormulario();
    
    const tipo = cliente.tipo || (cliente.cedula ? "natural" : "juridico");
    if (tipoClienteSelect) tipoClienteSelect.value = tipo;
    toggleCamposPorTipo();
    
    if (tipo === "natural") {
        const nombreCompleto = cliente.nombre || "";
        const espacioIndex = nombreCompleto.indexOf(' ');
        let nombre = nombreCompleto;
        let apellido = "";
        if (espacioIndex > 0) {
            nombre = nombreCompleto.substring(0, espacioIndex);
            apellido = nombreCompleto.substring(espacioIndex + 1);
        }
        
        setFieldValue("cedula", String(cliente.id || ""));
        setFieldValue("nombre", nombre);
        setFieldValue("apellido", apellido);
        setFieldValue("celular", cliente.celular || "");
        setFieldValue("correo", cliente.correo || "");
        setFieldValue("direccion", cliente.direccion || "");
    } else {
        setFieldValue("rif", cliente.rif || "");
        setFieldValue("razon_social", cliente.razon_social || cliente.nombre || "");
        setFieldValue("telefono", cliente.celular || cliente.telefono || "");
        setFieldValue("correo_juridico", cliente.correo || "");
        setFieldValue("direccion_juridico", cliente.direccion || "");
    }
    
    if (clienteIdInput) {
        clienteIdInput.value = String(cliente.id || "");
    }
    formCliente.dataset.editing = "true";

    if (window.UiModal && typeof window.UiModal.openById === "function") {
        window.UiModal.openById("modal-cliente");
        if (window.FieldValidator) {
            setTimeout(() => window.FieldValidator.init(), 100);
        }
    }
}

async function onSubmitCliente(event) {
    event.preventDefault();
    
    // Validar formulario antes de enviar
    if (!validarFormularioAntesDeEnviar(formCliente, 'cliente')) {
        return;
    }

    const tipo = tipoClienteSelect?.value;
    let payload = {};
    
    if (tipo === "natural") {
        const cedula = getFieldValue("cedula");
        const nombre = getFieldValue("nombre");
        const apellido = getFieldValue("apellido");
        const celular = getFieldValue("celular");
        const correo = getFieldValue("correo");
        const direccion = getFieldValue("direccion");

        if (!cedula || !nombre || !apellido || !celular) {
            mostrarToast("Cédula, nombre, apellido y celular son obligatorios.", true);
            return;
        }

        if (!/^\d+$/.test(cedula)) {
            mostrarToast("La cédula debe contener solo números.", true);
            return;
        }

        payload = {
            tipo: "natural",
            cedula: cedula,
            nombre: nombre,
            apellido: apellido,
            celular: celular,
            correo: correo,
            direccion: direccion
        };
    } else if (tipo === "juridico") {
        const rif = getFieldValue("rif");
        const razonSocial = getFieldValue("razon_social");
        const telefono = getFieldValue("telefono");
        const correo = getFieldValue("correo_juridico");
        const direccion = getFieldValue("direccion_juridico");

        if (!rif || !razonSocial || !telefono) {
            mostrarToast("RIF, razón social y teléfono son obligatorios.", true);
            return;
        }

        payload = {
            tipo: "juridico",
            rif: rif,
            razon_social: razonSocial,
            telefono: telefono,
            correo: correo,
            direccion: direccion
        };
    } else {
        mostrarToast("Seleccione el tipo de cliente.", true);
        return;
    }

    const isEdit = formCliente.dataset.editing === "true";
    const clienteId = clienteIdInput?.value || "";
    if (isEdit && !clienteId) {
        mostrarToast("No se encontró el cliente a actualizar.", true);
        return;
    }
    const url = isEdit ? `/api/clientes/${encodeURIComponent(clienteId)}` : "/api/clientes";
    const method = isEdit ? "PUT" : "POST";

    try {
        await fetchJson(url, { method, body: JSON.stringify(payload) });
        mostrarToast(isEdit ? "Cliente actualizado." : "Cliente creado.");
        limpiarFormulario();
        if (window.UiModal && typeof window.UiModal.closeById === "function") {
            window.UiModal.closeById("modal-cliente");
        }
        cargarClientes();
    } catch (error) {
        mostrarToast(error.message || "No se pudo guardar el cliente.", true);
    }
}

async function eliminarCliente(id) {
    if (!confirm(`¿Estás seguro de eliminar al cliente con ID ${id}?`)) {
        return;
    }
    
    try {
        await fetchJson(`/api/clientes/${encodeURIComponent(id)}`, { method: "DELETE" });
        mostrarToast("Cliente eliminado.");
        cargarClientes();
    } catch (error) {
        mostrarToast(error.message || "No se pudo eliminar el cliente.", true);
    }
}

function limpiarFormulario() {
    if (!formCliente) return;
    formCliente.reset();
    if (clienteIdInput) {
        clienteIdInput.value = "";
    }
    delete formCliente.dataset.editing;
    
    // Limpiar campos condicionales
    const camposNatural = document.getElementById("campos-natural");
    const camposJuridico = document.getElementById("campos-juridico");
    if (camposNatural) {
        camposNatural.querySelectorAll("input").forEach(input => input.value = "");
    }
    if (camposJuridico) {
        camposJuridico.querySelectorAll("input").forEach(input => input.value = "");
    }
    
    if (window.FieldValidator) {
        window.FieldValidator.resetForm(formCliente);
    }
}

function getFieldValue(fieldName) {
    const field = formCliente?.elements?.namedItem(fieldName);
    return field && "value" in field ? String(field.value).trim() : "";
}

function setFieldValue(fieldName, value) {
    const field = formCliente?.elements?.namedItem(fieldName);
    if (field && "value" in field) {
        field.value = value;
    }
}

// ==================== FETCH ====================

async function fetchJson(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
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

// ==================== UTILITIES ====================

function mostrarToast(message, isError = false) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.toggle("toast--error", isError);
    toast.classList.add("is-visible");
    window.clearTimeout(mostrarToast._timer);
    mostrarToast._timer = window.setTimeout(() => {
        toast.classList.remove("is-visible");
    }, 2600);
}

function escapeHtml(text) {
    if (text === null || text === undefined) return "";
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}