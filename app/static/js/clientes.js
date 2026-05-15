const tablaClientes = document.getElementById("tabla-clientes");
const btnNuevoCliente = document.getElementById("btn-nuevo-cliente");
const formCliente = document.getElementById("form-cliente");
const toast = document.getElementById("toast-mensaje");
const statClientes = document.getElementById("stat-clientes");

let clientes = [];
const csrfToken = document.querySelector("input[name='_csrf_token']")?.value || "";

initClientes();

function initClientes() {
    btnNuevoCliente?.addEventListener("click", abrirFormularioNuevo);
    formCliente?.addEventListener("submit", onSubmitCliente);
    document.addEventListener("click", onTablaClick);
    cargarClientes();
}

function abrirFormularioNuevo() {
    limpiarFormulario();
    if (window.UiModal && typeof window.UiModal.openById === "function") {
        window.UiModal.openById("modal-cliente");
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
    statClientes.textContent = String(clientes.length);
    if (!tablaClientes) return;

    if (!clientes.length) {
        tablaClientes.innerHTML = `<tr><td colspan="8">No hay clientes registrados.</td></tr>`;
        return;
    }

    tablaClientes.innerHTML = clientes
        .map((cliente) => {
            return `
                <tr>
                    <td>${escapeHtml(String(cliente.ID_c))}</td>
                    <td>${escapeHtml(cliente.nombre || "")}</td>
                    <td>${escapeHtml(cliente.apellido || "")}</td>
                    <td>${escapeHtml(cliente.celular || "")}</td>
                    <td>${escapeHtml(cliente.correo || "")}</td>
                    <td>${escapeHtml(cliente.direccion || "")}</td>
                    <td>${escapeHtml(cliente.tipo || "")}</td>
                    <td class="table__actions">
                        <button type="button" class="icon-action" data-action="edit" data-id="${encodeURIComponent(
                cliente.ID_c,
            )}" aria-label="Modificar">✎</button>
                        <button type="button" class="icon-action" data-action="delete" data-id="${encodeURIComponent(
                cliente.ID_c,
            )}" aria-label="Eliminar">🗑</button>
                    </td>
                </tr>
            `;
        })
        .join("");
}

function abrirEdicion(id) {
    const cliente = clientes.find((item) => String(item.ID_c) === String(id));
    if (!cliente || !formCliente) return;

    formCliente.nombre.value = cliente.nombre || "";
    formCliente.apellido.value = cliente.apellido || "";
    formCliente.celular.value = cliente.celular || "";
    formCliente.correo.value = cliente.correo || "";
    formCliente.direccion.value = cliente.direccion || "";
    formCliente.tipo.value = cliente.tipo || "";
    formCliente.id.value = String(cliente.ID_c);
    formCliente.dataset.editing = "true";

    if (window.UiModal && typeof window.UiModal.openById === "function") {
        window.UiModal.openById("modal-cliente");
    }
}

async function onSubmitCliente(event) {
    event.preventDefault();
    if (!formCliente) return;

    const payload = {
        nombre: formCliente.nombre.value.trim(),
        apellido: formCliente.apellido.value.trim(),
        celular: formCliente.celular.value.trim(),
        correo: formCliente.correo.value.trim(),
        direccion: formCliente.direccion.value.trim(),
        tipo: formCliente.tipo.value.trim(),
    };

    if (!payload.nombre || !payload.apellido || !payload.celular) {
        mostrarToast("Nombre, apellido y celular son obligatorios.", true);
        return;
    }

    const isEdit = formCliente.dataset.editing === "true";
    const url = isEdit ? `/api/clientes/${encodeURIComponent(formCliente.id.value)}` : "/api/clientes";
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
    formCliente.id.value = "";
    delete formCliente.dataset.editing;
}

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
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
