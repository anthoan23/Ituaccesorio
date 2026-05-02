const tabla = document.getElementById("tabla-empleados");
const listaLogs = document.getElementById("lista-logs");

const modal = document.getElementById("modal");
const modalCerrar = document.getElementById("modal-cerrar");
const form = document.getElementById("form-empleado");
const btnCancelar = document.getElementById("btn-cancelar");
const btnRegistrar = document.getElementById("btn-registrar");

const btnBusqueda = document.getElementById("btn-busqueda");
const panelFiltros = document.getElementById("panel-filtros");
const btnAplicar = document.getElementById("btn-aplicar");
const btnLimpiar = document.getElementById("btn-limpiar");

const fCedula = document.getElementById("f-cedula");

const btnReporte = document.getElementById("btn-reporte");

const pagerPages = document.getElementById("pager-pages");
const pagerButtons = document.querySelectorAll(".pager__btn");

const toast = document.getElementById("toast");

let empleados = [];
let paginaActual = 1;
const tamPagina = 6;

let modoEdicion = null;

iniciar();

function iniciar() {
    btnRegistrar?.addEventListener("click", () => abrirModal());
    modalCerrar?.addEventListener("click", cerrarModal);
    btnCancelar?.addEventListener("click", cerrarModal);

    modal?.addEventListener("click", event => {
        if (event.target === modal) {
            cerrarModal();
        }
    });

    form?.addEventListener("submit", onSubmit);

    btnBusqueda?.addEventListener("click", () => {
        const abierto = !panelFiltros.hidden;
        panelFiltros.hidden = abierto;
    });

    btnAplicar?.addEventListener("click", () => {
        paginaActual = 1;
        renderTabla();
    });

    btnLimpiar?.addEventListener("click", () => {
        if (fCedula) {
            fCedula.value = "";
        }
        paginaActual = 1;
        renderTabla();
    });

    btnReporte?.addEventListener("click", () => {
        window.open("/api/empleados/reporte", "_blank", "noopener");
    });

    pagerButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            if (btn.dataset.page === "prev") {
                paginaActual = Math.max(1, paginaActual - 1);
            } else {
                paginaActual = Math.min(getTotalPaginas(), paginaActual + 1);
            }
            renderTabla();
        });
    });

    recargar();
}

function recargar() {
    Promise.all([cargarEmpleados(), cargarRecientes()]).catch(() => {
        mostrarToast("No se pudieron cargar los datos.");
    });
}

function cargarEmpleados() {
    return fetch("/api/empleados")
        .then(r => r.json())
        .then(data => {
            if (!data.success) {
                throw new Error(data.error || "Error");
            }
            empleados = Array.isArray(data.empleados) ? data.empleados : [];
            paginaActual = 1;
            renderTabla();
        });
}

function cargarRecientes() {
    return fetch("/api/empleados/recientes?limit=5")
        .then(r => r.json())
        .then(data => {
            if (!data.success) {
                throw new Error(data.error || "Error");
            }
            renderLogs(Array.isArray(data.logs) ? data.logs : []);
        });
}

function getFiltrados() {
    const cedula = (fCedula?.value || "").trim();

    return empleados.filter(e => {
        const matchCedula = !cedula || String(e.cedula).includes(cedula);
        return matchCedula;
    });
}

function getTotalPaginas() {
    const total = getFiltrados().length;
    return Math.max(1, Math.ceil(total / tamPagina));
}

function renderTabla() {
    if (!tabla) return;

    const filtrados = getFiltrados();
    const totalPaginas = Math.max(1, Math.ceil(filtrados.length / tamPagina));
    paginaActual = Math.min(paginaActual, totalPaginas);

    const start = (paginaActual - 1) * tamPagina;
    const pageItems = filtrados.slice(start, start + tamPagina);

    pagerPages.textContent = `${paginaActual} | ${totalPaginas}`;

    if (pageItems.length === 0) {
        tabla.innerHTML = `<tr><td colspan="4">No hay empleados para mostrar.</td></tr>`;
        return;
    }

    tabla.innerHTML = pageItems.map(renderFila).join("");

    tabla.querySelectorAll("button[data-action]").forEach(btn => {
        btn.addEventListener("click", () => {
            const action = btn.dataset.action;
            const cedula = Number(btn.dataset.cedula);
            const empleado = empleados.find(e => Number(e.cedula) === cedula);

            if (action === "edit") {
                abrirModal(empleado);
                return;
            }

            if (action === "delete") {
                eliminarEmpleado(cedula);
            }
        });
    });
}

function renderFila(e) {
    const nombre = `${e.nombre || ""} ${e.apellido || ""}`.trim();
    return `
        <tr>
            <td>${escapeHtml(String(e.cedula ?? ""))}</td>
            <td>${escapeHtml(nombre || "—")}</td>
            <td>${escapeHtml(String(e.rol || "—"))}</td>
            <td class="table__actions">
                <div class="row-actions">
                    <button class="icon-action" type="button" data-action="edit" data-cedula="${escapeHtml(String(e.cedula))}" aria-label="Editar">
                        ${iconPencil()}
                    </button>
                    <button class="icon-action" type="button" data-action="delete" data-cedula="${escapeHtml(String(e.cedula))}" aria-label="Eliminar">
                        ${iconTrash()}
                    </button>
                </div>
            </td>
        </tr>
    `;
}

function renderLogs(logs) {
    if (!listaLogs) return;

    if (!Array.isArray(logs) || logs.length === 0) {
        listaLogs.innerHTML = "<li><span class='log__avatar' aria-hidden='true'></span><div><p class='log__line'>Sin registros recientes</p><div class='log__meta'>Aún no hay actividad.</div></div></li>";
        return;
    }

    listaLogs.innerHTML = logs.map(l => {
        return `
            <li>
                <span class="log__avatar" aria-hidden="true"></span>
                <div>
                    <p class="log__line">${escapeHtml(l.linea || "")}</p>
                    <div class="log__meta">${escapeHtml(l.meta || "")}</div>
                </div>
            </li>
        `;
    }).join("");
}

function abrirModal(empleado = null) {
    if (!modal || !form) return;

    modoEdicion = empleado ? Number(empleado.cedula) : null;

    const title = document.getElementById("modal-title");
    if (title) {
        title.textContent = modoEdicion ? "Editar empleado" : "Registrar empleado";
    }

    form.reset();

    const cedulaInput = form.querySelector("input[name='cedula']");
    if (cedulaInput) {
        cedulaInput.disabled = Boolean(modoEdicion);
    }

    if (empleado) {
        form.cedula.value = empleado.cedula ?? "";
        form.nombre.value = empleado.nombre ?? "";
        form.apellido.value = empleado.apellido ?? "";
        const celularRaw = String(empleado.celular ?? "").replace(/\s|-/g, "");
        const prefijo = celularRaw.length >= 4 ? celularRaw.slice(0, 4) : "0414";
        const resto = celularRaw.length >= 4 ? celularRaw.slice(4) : celularRaw;
        if (form.celular_prefijo) {
            form.celular_prefijo.value = prefijo;
        }
        if (form.celular_numero) {
            form.celular_numero.value = resto;
        }
        form.correo.value = empleado.correo ?? "";
        form.direccion.value = empleado.direccion ?? "";
        form.rol.value = empleado.rol ?? "";
    }

    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
}

function cerrarModal() {
    if (!modal) return;
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    modoEdicion = null;
}

function onSubmit(event) {
    event.preventDefault();

    const payload = Object.fromEntries(new FormData(form).entries());
    payload.cedula = payload.cedula ? Number(payload.cedula) : payload.cedula;

    const prefijo = (payload.celular_prefijo || "").trim();
    const numero = (payload.celular_numero || "").trim();
    payload.celular = numero ? `${prefijo}${numero}` : "";
    delete payload.celular_prefijo;
    delete payload.celular_numero;

    const endpoint = modoEdicion ? `/api/empleados/${modoEdicion}` : "/api/empleados";
    const method = modoEdicion ? "PUT" : "POST";

    fetch(endpoint, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    })
        .then(async r => {
            const data = await r.json().catch(() => ({}));
            return { r, data };
        })
        .then(({ r, data }) => {
            if (!r.ok || !data.success) {
                mostrarToast(data.error || "No se pudo guardar.");
                return;
            }

            mostrarToast(modoEdicion ? "Empleado actualizado" : "Empleado registrado");
            cerrarModal();
            recargar();
        })
        .catch(() => {
            mostrarToast("Error guardando empleado");
        });
}

function eliminarEmpleado(cedula) {
    if (!Number.isFinite(cedula)) return;

    fetch(`/api/empleados/${cedula}`, { method: "DELETE" })
        .then(async r => {
            const data = await r.json().catch(() => ({}));
            return { r, data };
        })
        .then(({ r, data }) => {
            if (!r.ok || !data.success) {
                mostrarToast(data.error || "No se pudo eliminar.");
                return;
            }

            mostrarToast("Empleado eliminado");
            recargar();
        })
        .catch(() => {
            mostrarToast("Error eliminando empleado");
        });
}

function mostrarToast(texto) {
    if (!toast) return;

    toast.textContent = texto;
    toast.classList.add("is-show");
    window.clearTimeout(mostrarToast._t);
    mostrarToast._t = window.setTimeout(() => toast.classList.remove("is-show"), 2200);
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function iconPencil() {
    return `
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
            <path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25Zm2.92 2.83H5v-.92l9.06-9.06.92.92-9.06 9.06ZM20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83Z"/>
        </svg>
    `;
}

function iconTrash() {
    return `
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
            <path fill="currentColor" d="M9 3h6l1 2h4v2H4V5h4l1-2Zm1 6h2v9h-2V9Zm4 0h2v9h-2V9ZM7 9h2v9H7V9Z"/>
        </svg>
    `;
}
