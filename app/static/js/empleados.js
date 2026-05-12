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

// Global click listener to handle any 'Eliminar' buttons (tables or cards)
document.addEventListener('click', function (e) {
    const btn = e.target.closest('button.icon-action[aria-label="Eliminar"]');
    if (!btn) return;

    // try to infer target from table row
    const row = btn.closest('tr');
    let url = null;
    let typeText = '';
    let displayText = '';

    if (row) {
        const cells = Array.from(row.querySelectorAll('td'));
        const first = cells[0]?.textContent?.trim() || '';
        const second = cells[1]?.textContent?.trim() || '';

        const tbody = row.closest('tbody');
        if (tbody === tablaEmpleados) {
            typeText = 'empleado';
            displayText = second || first; // nombre o cédula
            url = `/api/empleados/${encodeURIComponent(first)}`;
        } else if (tbody === tablaCargos) {
            typeText = 'cargo';
            displayText = second || first;
            url = `/api/cargos/${encodeURIComponent(second)}`;
        } else if (tbody === tablaEspecialidades) {
            typeText = 'especialidad';
            displayText = second || first;
            url = `/api/especialidades/${encodeURIComponent(second)}`;
        }
    }

    // fallback: allow buttons with data attributes (cards)
    if (!url) {
        const dataId = btn.getAttribute('data-id') || btn.dataset.id;
        const origen = btn.getAttribute('data-origen') || btn.dataset.origen || btn.getAttribute('data-type') || btn.dataset.type;
        if (dataId && origen) {
            if (/emplead/i.test(origen)) {
                typeText = 'empleado';
                displayText = dataId;
                url = `/api/empleados/${encodeURIComponent(dataId)}`;
            } else if (/cargo/i.test(origen)) {
                typeText = 'cargo';
                displayText = dataId;
                url = `/api/cargos/${encodeURIComponent(dataId)}`;
            } else if (/especial/i.test(origen)) {
                typeText = 'especialidad';
                displayText = dataId;
                url = `/api/especialidades/${encodeURIComponent(dataId)}`;
            }
        }
    }

    if (!url) return;

    const deleteMessageEl = document.getElementById('delete-message');
    const confirmBtn = document.getElementById('delete-confirm-btn');
    if (!deleteMessageEl || !confirmBtn) return;

    deleteMessageEl.textContent = `¿Seguro que desea eliminar el ${typeText} ${displayText}?`;

    // store pending URL (the actual deletion will be handled by the delegated
    // click listener on `#delete-confirm-btn` below)
    window.__deletePendingUrl = url;

    openModalById('modal-delete');
});

// Delegated handler for the "Modificar" buttons — opens the correct modal and
// fills the form with the selected record's data.
document.addEventListener('click', function (e) {
    const btn = e.target.closest('button.icon-action[aria-label="Modificar"]');
    if (!btn) return;

    const row = btn.closest('tr');
    let tipo = null;
    let id = null;

    if (row) {
        const cells = Array.from(row.querySelectorAll('td'));
        const first = cells[0]?.textContent?.trim() || '';
        const tbody = row.closest('tbody');

        if (tbody === tablaEmpleados) {
            tipo = 'empleado';
            id = first;
        } else if (tbody === tablaCargos) {
            tipo = 'cargo';
            id = first;
        } else if (tbody === tablaEspecialidades) {
            tipo = 'especialidad';
            id = first;
        }
    }

    if (!tipo || !id) return;

    if (tipo === 'empleado') {
        const empleado = state.empleados.find(e => String(e.cedula) === String(id));
        if (!empleado) return;

        formEmpleado.cedula.value = empleado.cedula || '';
        formEmpleado.nombre.value = empleado.nombre || '';
        formEmpleado.apellido.value = empleado.apellido || '';
        formEmpleado.celular.value = empleado.celular || '';
        formEmpleado.correo.value = empleado.correo || '';
        formEmpleado.direccion.value = empleado.direccion || '';

        formEmpleado.dataset.editing = 'true';
        formEmpleado.dataset.editingId = encodeURIComponent(empleado.cedula);
        const hidEmp = formEmpleado.querySelector('input[name="id_viejo"]');
        if (hidEmp) hidEmp.value = empleado.cedula || '';

        openModalById('modal-empleado');
    }

    if (tipo === 'cargo') {
        const cargo = state.cargos.find(c => String(c.id) === String(id));
        if (!cargo) return;

        formCargo.cargo.value = cargo.nombre || '';
        formCargo.dataset.editing = 'true';
        formCargo.dataset.editingId = encodeURIComponent(cargo.id);
        const hid = formCargo.querySelector('input[name="id_viejo"]');
        if (hid) hid.value = cargo.nombre || '';

        openModalById('modal-cargo');
    }

    if (tipo === 'especialidad') {
        const esp = state.especialidades.find(s => String(s.id) === String(id));
        if (!esp) return;

        formEspecialidad.especialidad.value = esp.nombre || '';
        formEspecialidad.dataset.editing = 'true';
        formEspecialidad.dataset.editingId = encodeURIComponent(esp.id);
        const hidE = formEspecialidad.querySelector('input[name="id_viejo"]');
        if (hidE) hidE.value = esp.nombre || '';

        openModalById('modal-especialidad');
    }
});

// Delegated handler for the modal confirm button — always present and robust
document.addEventListener('click', async (e) => {
    const confirm = e.target.closest('#delete-confirm-btn');
    if (!confirm) return;

    const url = window.__deletePendingUrl;
    if (!url) return;

    try {
        await fetchJson(url, { method: 'DELETE' });
        closeModalById('modal-delete');
        await cargarTodo();
        mostrarToast('Registro eliminado.');
    } catch (err) {
        mostrarToast(err.message || 'No se pudo eliminar el registro.', true);
    }
});

function openModalById(id) {
    const modal = document.getElementById(id);
    if (!modal) return;
    modal.removeAttribute('hidden');
    modal.setAttribute('aria-hidden', 'false');
}

function closeModalById(id) {
    const modal = document.getElementById(id);
    if (!modal) return;
    modal.setAttribute('hidden', '');
    modal.setAttribute('aria-hidden', 'true');
}

// Close modal when clicking elements with data-close-modal
document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-close-modal]');
    if (!btn) return;
    const modal = btn.closest('[data-modal]');
    if (!modal) return;
    modal.setAttribute('hidden', '');
    modal.setAttribute('aria-hidden', 'true');
});

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
        if (formEmpleado.dataset.editing === 'true' && formEmpleado.dataset.editingId) {
            const id = formEmpleado.dataset.editingId;
            const hid = formEmpleado.querySelector('input[name="id_viejo"]');
            if (hid) payload.id_viejo = hid.value || '';
            await fetchJson(`/api/empleados/${id}`, {
                method: 'PUT',
                body: JSON.stringify(payload),
            });
            delete formEmpleado.dataset.editing;
            delete formEmpleado.dataset.editingId;
            if (hid) hid.value = '';
        } else {
            await fetchJson("/api/empleados", {
                method: "POST",
                body: JSON.stringify(payload),
            });
        }

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
        cargo_nuevo: formCargo?.cargo?.value?.trim() || "",
    };

    try {
        if (formCargo.dataset.editing === 'true' && formCargo.dataset.editingId) {
            const id = formCargo.dataset.editingId;
            const hid = formCargo.querySelector('input[name="id_viejo"]');
            if (hid) payload.id_viejo = hid.value || '';
            await fetchJson(`/api/cargos/${id}`, {
                method: 'PUT',
                body: JSON.stringify(payload),
            });
            delete formCargo.dataset.editing;
            delete formCargo.dataset.editingId;
            if (hid) hid.value = '';
        } else {
            await fetchJson("/api/cargos", {
                method: "POST",
                body: JSON.stringify({ cargo: payload.cargo_nuevo }),
            });
        }

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
        especialidad_nuevo: formEspecialidad?.especialidad?.value?.trim() || "",
    };

    try {
        if (formEspecialidad.dataset.editing === 'true' && formEspecialidad.dataset.editingId) {
            const id = formEspecialidad.dataset.editingId;
            const hid = formEspecialidad.querySelector('input[name="id_viejo"]');
            if (hid) payload.especialidad_viejo = hid.value || '';
            await fetchJson(`/api/especialidades/${id}`, {
                method: 'PUT',
                body: JSON.stringify(payload),
            });
            delete formEspecialidad.dataset.editing;
            delete formEspecialidad.dataset.editingId;
            if (hid) hid.value = '';
        } else {
            await fetchJson("/api/especialidades", {
                method: "POST",
                body: JSON.stringify({ especialidad: payload.especialidad_nuevo }),
            });
        }

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
                <div class="row-actions" aria-label="Acciones del empleado">
                    <button class="icon-action" type="button" aria-label="Ver">
                        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 5c-7 0-11 7-11 7s4 7 11 7 11-7 11-7-4-7-11-7zm0 12a5 5 0 1 1 0-10 5 5 0 0 1 0 10z" fill="currentColor"/></svg>
                    </button>
                    <button class="icon-action" type="button" aria-label="Modificar">
                        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25Zm18-11.5a1 1 0 0 0 0-1.41l-1.34-1.34a1 1 0 0 0-1.41 0l-1.12 1.12 3.75 3.75L21 5.75Z" fill="currentColor"/></svg>
                    </button>
                    <button class="icon-action" type="button" aria-label="Eliminar">
                        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 7h12l-1 14H7L6 7Zm3-3h6l1 2H8l1-2Z" fill="currentColor"/></svg>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function renderCargos() {
    if (!tablaCargos) return;

    if (!state.cargos.length) {
        tablaCargos.innerHTML = emptyRow(3, 'No hay cargos creados.');
        return;
    }

    tablaCargos.innerHTML = state.cargos.map(c => `
        <tr>
            <td>${escapeHtml(String(c.id || ''))}</td>
            <td>${escapeHtml(c.nombre || '')}</td>
            <td class="table__actions">
                <div class="row-actions" aria-label="Acciones del cargo">
                    <button class="icon-action" type="button" aria-label="Ver">
                        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 5c-7 0-11 7-11 7s4 7 11 7 11-7 11-7-4-7-11-7zm0 12a5 5 0 1 1 0-10 5 5 0 0 1 0 10z" fill="currentColor"/></svg>
                    </button>
                    <button class="icon-action" type="button" aria-label="Modificar">
                        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25Zm18-11.5a1 1 0 0 0 0-1.41l-1.34-1.34a1 1 0 0 0-1.41 0l-1.12 1.12 3.75 3.75L21 5.75Z" fill="currentColor"/></svg>
                    </button>
                    <button class="icon-action" type="button" aria-label="Eliminar">
                        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 7h12l-1 14H7L6 7Zm3-3h6l1 2H8l1-2Z" fill="currentColor"/></svg>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function renderEspecialidades() {
    if (!tablaEspecialidades) return;

    if (!state.especialidades.length) {
        tablaEspecialidades.innerHTML = emptyRow(3, 'No hay especialidades creadas.');
        return;
    }

    tablaEspecialidades.innerHTML = state.especialidades.map(e => `
        <tr>
            <td>${escapeHtml(String(e.id || ''))}</td>
            <td>${escapeHtml(e.nombre || '')}</td>
            <td class="table__actions">
                <div class="row-actions" aria-label="Acciones de la especialidad">
                    <button class="icon-action" type="button" aria-label="Ver">
                        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 5c-7 0-11 7-11 7s4 7 11 7 11-7 11-7-4-7-11-7zm0 12a5 5 0 1 1 0-10 5 5 0 0 1 0 10z" fill="currentColor"/></svg>
                    </button>
                    <button class="icon-action" type="button" aria-label="Modificar">
                        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25Zm18-11.5a1 1 0 0 0 0-1.41l-1.34-1.34a1 1 0 0 0-1.41 0l-1.12 1.12 3.75 3.75L21 5.75Z" fill="currentColor"/></svg>
                    </button>
                    <button class="icon-action" type="button" aria-label="Eliminar">
                        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 7h12l-1 14H7L6 7Zm3-3h6l1 2H8l1-2Z" fill="currentColor"/></svg>
                    </button>
                </div>
            </td>
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
