const tablaEmpleados = document.getElementById("tabla-empleados");
const tablaCargos = document.getElementById("tabla-cargos");
const tablaEspecialidades = document.getElementById("tabla-especialidades");
const formEmpleado = document.getElementById("form-empleado");
const formCargo = document.getElementById("form-cargo");
const formEspecialidad = document.getElementById("form-especialidad");

const state = {
    empleados: [],
    cargos: [],
    especialidades: [],
};

const csrfToken = document.querySelector("input[name='_csrf_token']")?.value || "";

iniciar();

function iniciar() {
    formEmpleado?.addEventListener("submit", registrarEmpleado);
    formCargo?.addEventListener("submit", registrarCargo);
    formEspecialidad?.addEventListener("submit", registrarEspecialidad);
    cargarTodo();
}

async function registrarEmpleado(event) {
    event.preventDefault();

    const payload = {
        cedula: formEmpleado?.cedula?.value?.trim() || "",
        nombre: formEmpleado?.nombre?.value?.trim() || "",
        apellido: formEmpleado?.apellido?.value?.trim() || "",
        celular: formEmpleado?.celular?.value?.trim() || "",
        correo: formEmpleado?.correo?.value?.trim() || "",
        direccion: formEmpleado?.direccion?.value?.trim() || "",
    };

    try {
        await fetchJson("/api/empleados", {
            method: "POST",
            body: JSON.stringify(payload),
        });

        formEmpleado?.reset();
        cerrarModalDeFormulario(formEmpleado);
        await cargarTodo();
    } catch (error) {
        mostrarToast(error.message || "No se pudo registrar el empleado.", true);
    }
}

async function registrarCargo(event) {
    event.preventDefault();

    const payload = {
        cargo: formCargo?.cargo?.value?.trim() || "",
    };

    try {
        await fetchJson("/api/cargos", {
            method: "POST",
            body: JSON.stringify(payload),
        });

        formCargo?.reset();
        cerrarModalDeFormulario(formCargo);
        await cargarTodo();
    } catch (error) {
        mostrarToast(error.message || "No se pudo registrar el cargo.", true);
    }
}

async function registrarEspecialidad(event) {
    event.preventDefault();

    const payload = {
        especialidad: formEspecialidad?.especialidad?.value?.trim() || "",
    };

    try {
        await fetchJson("/api/especialidades", {
            method: "POST",
            body: JSON.stringify(payload),
        });

        formEspecialidad?.reset();
        cerrarModalDeFormulario(formEspecialidad);
        await cargarTodo();
    } catch (error) {
        mostrarToast(error.message || "No se pudo registrar la especialidad.", true);
    }
}

function cerrarModalDeFormulario(form) {
    const modal = form?.closest("[data-modal]");
    if (!modal) return;

    if (window.UiModal && typeof window.UiModal.closeById === "function") {
        window.UiModal.closeById(modal.id);
        return;
    }

    modal.setAttribute("hidden", "");
    modal.setAttribute("aria-hidden", "true");
}

async function cargarTodo() {
    try {
        const [empleados, cargos, especialidades] = await Promise.all([
            fetchJson('/api/empleados'),
            fetchJson('/api/cargos'),
            fetchJson('/api/especialidades'),
        ]);

        state.empleados = Array.isArray(empleados) ? empleados : (empleados.empleados || []);
        state.cargos = Array.isArray(cargos) ? cargos : (cargos.cargos || []);
        state.especialidades = Array.isArray(especialidades) ? especialidades : (especialidades.especialidades || []);

        renderTodo();
    } catch (error) {
        mostrarToast(error.message || 'No se pudieron cargar los datos.', true);
    }
}

function renderTodo() {
    renderEmpleados();
    renderCargos();
    renderEspecialidades();
}

function renderEmpleados() {
    if (!tablaEmpleados) return;

    if (!state.empleados.length) {
        tablaEmpleados.innerHTML = emptyRow(4, 'No hay empleados registrados.');
        return;
    }

    tablaEmpleados.innerHTML = state.empleados.map(emp => `
        <tr>
            <td>${escapeHtml(emp.cedula || '')}</td>
            <td>${escapeHtml(((emp.nombre || '') + ' ' + (emp.apellido || '')).trim())}</td>
            <td>${escapeHtml(emp.cargo_nombre || '—')}</td>
            <td class="table__actions">
                <div class="row-actions">
                    <button class="icon-action" type="button">Ver</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function renderCargos() {
    if (!tablaCargos) return;

    if (!state.cargos.length) {
        tablaCargos.innerHTML = emptyRow(2, 'No hay cargos creados.');
        return;
    }

    tablaCargos.innerHTML = state.cargos.map(c => `
        <tr>
            <td>${escapeHtml(String(c.id || ''))}</td>
            <td>${escapeHtml(c.nombre || '')}</td>
        </tr>
    `).join('');
}

function renderEspecialidades() {
    if (!tablaEspecialidades) return;

    if (!state.especialidades.length) {
        tablaEspecialidades.innerHTML = emptyRow(2, 'No hay especialidades creadas.');
        return;
    }

    tablaEspecialidades.innerHTML = state.especialidades.map(e => `
        <tr>
            <td>${escapeHtml(String(e.id || ''))}</td>
            <td>${escapeHtml(e.nombre || '')}</td>
        </tr>
    `).join('');
}

async function fetchJson(url, options = {}) {
    const authToken = getAuthToken();

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
        throw new Error(data.error || 'No se pudo completar la operacion.');
    }

    return data;
}

function mostrarToast(message, isError = false) {
    // minimal toast fallback: console + alert for errors
    if (isError) {
        console.error(message);
    } else {
        console.log(message);
    }
}

function getAuthToken() {
    const fromLocal = window.localStorage ? window.localStorage.getItem("access_token") : "";
    if (fromLocal) return fromLocal;

    const fromSession = window.sessionStorage ? window.sessionStorage.getItem("access_token") : "";
    if (fromSession) return fromSession;

    return "";
}

function emptyRow(colspan, text) {
    return `<tr><td colspan="${colspan}">${escapeHtml(text)}</td></tr>`;
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#39;");
}
