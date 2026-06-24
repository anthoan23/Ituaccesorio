// ============================================
// 1. CONSTANTES Y CONFIGURACIÓN
// ============================================
const CONFIG = {
    API: {
        ORDENES_SERVICIO: '/api/ordenes-servicio',
        ORDENES: '/api/ordenes-servicio/ordenes',
        TECNICOS: '/api/ordenes-servicio/tecnicos',
        MODELOS: '/api/productos/modelos',
    }
};

const Iconos = {
    ojo: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" fill="currentColor"/></svg>`,
    asignar: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" fill="currentColor"/></svg>`
};

// ============================================
// 2. UTILIDADES
// ============================================
const Utils = {
    getCsrfToken() {
        const input = document.querySelector("input[name='_csrf_token']");
        return input ? input.value : "";
    },

    getAccessToken() {
        return (
            localStorage.getItem("access_token") ||
            localStorage.getItem("token") ||
            sessionStorage.getItem("access_token") ||
            sessionStorage.getItem("token") ||
            ""
        );
    },

    async fetchJson(url, options = {}) {
        const headers = new Headers(options.headers || {});
        headers.set("Accept", "application/json");

        if (options.body && !headers.has("Content-Type")) {
            headers.set("Content-Type", "application/json");
        }

        const csrf = this.getCsrfToken();
        if (csrf) {
            headers.set("X-CSRFToken", csrf);
        }

        const token = this.getAccessToken();
        if (token && !headers.has("Authorization")) {
            headers.set("Authorization", `Bearer ${token}`);
        }

        const response = await fetch(url, {
            credentials: "same-origin",
            ...options,
            headers,
        });

        const contentType = response.headers.get("content-type") || "";
        const isJson = contentType.includes("application/json");
        const payload = isJson ? await response.json() : await response.text();

        if (!response.ok) {
            const msg =
                (isJson && payload && (payload.message || payload.error)) ||
                String(payload || response.statusText || "Error en la solicitud");
            throw new Error(msg);
        }

        return payload;
    },

    escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    },

    showMessage(message, isError = false) {
        if (!message) return;
        if (isError) {
        } else {
            console.info(`✅ ${message}`);
        }
    },

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    formatFecha(value) {
        if (!value) return "";
        const fecha = new Date(value);
        if (Number.isNaN(fecha.getTime())) return value;
        return fecha.toLocaleDateString("es-ES");
    },

    getEstadoBadgeClass(estado) {
        const estadoLower = String(estado ?? "").toLowerCase().trim();
        if (estadoLower.includes("pendient")) {
            return "badge--pendiente";
        }
        if (estadoLower.includes("asign")) {
            return "badge--asignada";
        }
        if (estadoLower.includes("revis")) {
            return "badge--revisada";
        }
        if (estadoLower.includes("repar")) {
            return "badge--reparada";
        }
        return "badge--pendiente";
    },

    getFechaActual() {
        const hoy = new Date();
        return hoy.toISOString().slice(0, 10);
    },

    // Extraer solo el número de una orden con formato OS0000010
    extraerNumeroOrden(idOrden) {
        if (!idOrden) return null;
        const match = String(idOrden).match(/\d+/);
        if (match) {
            return parseInt(match[0], 10);
        }
        return parseInt(idOrden, 10);
    }
};

// ============================================
// 3. MANEJADORES DE MODALES
// ============================================
function openModal(id) {
    if (window.UiModal && typeof window.UiModal.openById === "function") {
        window.UiModal.openById(id);
        return;
    }

    const modal = document.getElementById(id);
    if (modal) {
        modal.removeAttribute("hidden");
        modal.setAttribute("aria-hidden", "false");
    }
}

function closeModal(id) {
    if (window.UiModal && typeof window.UiModal.closeById === "function") {
        window.UiModal.closeById(id);
        return;
    }

    const modal = document.getElementById(id);
    if (modal) {
        modal.setAttribute("hidden", "");
        modal.setAttribute("aria-hidden", "true");
    }
}

// ============================================
// 4. VARIABLES GLOBALES
// ============================================
let ordenes = [];
let clienteActualId = null;
let ordenActualId = null;
let testsOrdenActual = [];

// ============================================
// 5. REFERENCIAS DOM
// ============================================
function getDomElements() {
    return {
        tablaOrdenes: document.getElementById("tabla-ordenes"),
        tablaOrdenesEstadoBody: document.getElementById("modal-ordenes-estado-body"),
        modalOrdenesEstadoSubtitle: document.getElementById("modal-ordenes-estado-subtitle"),
        estadoCards: document.querySelectorAll("[data-estado-card]"),
        tablaPendientes: document.getElementById("tabla-pendientes"),
        tablaAsignadas: document.getElementById("tabla-asignadas"),
        tablaRevisadas: document.getElementById("tabla-revisadas"),
        tablaTrabajosTecnico: document.getElementById("tabla-trabajos-tecnico"),
        statPendientes: document.getElementById("stat-pendientes"),
        statAsignadas: document.getElementById("stat-asignadas"),
        statRevisadas: document.getElementById("stat-revisadas"),
        formOrden: document.getElementById("form-orden-servicio"),
        btnVerificarEquipo: document.getElementById("btn-verificar-equipo"),
        btnVerificarCliente: document.getElementById("btn-verificar-cliente"),
        btnCrearCliente: document.getElementById("btn-crear-cliente"),
        clienteStatus: document.getElementById("cliente-status"),
        equipoStatus: document.getElementById("equipo-status"),
        selectModelo: document.getElementById("orden-modelo"),
        inputFecha: document.getElementById("orden-fecha"),
        selectOrdenAsignar: document.getElementById("select-orden-asignar"),
        selectTecnico: document.getElementById("select-tecnico"),
        modalTecnicoSelect: document.getElementById("modal-tecnico-select"),
        btnAsignarOrden: document.getElementById("btn-asignar-orden"),
        btnCargarTrabajos: document.getElementById("btn-cargar-trabajos"),
        detalleOrdenId: document.getElementById("detalle-orden-id"),
        detalleInfo: document.getElementById("detalle-info"),
        detalleResponsables: document.getElementById("detalle-responsables"),
        detalleFotos: document.getElementById("detalle-fotos"),
        detalleTests: document.getElementById("detalle-tests"),
        revisionOrdenId: document.getElementById("revision-orden-id"),
        formRevision: document.getElementById("form-revision-orden"),
        fotosOrdenId: document.getElementById("fotos-orden-id"),
        formFotos: document.getElementById("form-fotos-orden"),
        inputFotos: document.getElementById("input-fotos-orden"),
        previewFotos: document.getElementById("preview-fotos"),
    };
}

// ============================================
// 6. FUNCIONES DE RENDERIZADO
// ============================================
function renderContador(total) {
    const contadores = document.querySelectorAll("[data-count]");
    contadores.forEach(el => {
        el.setAttribute("data-count", String(total));
        el.textContent = String(total);
    });
}

function renderTablaOrdenes(ordenesData) {
    const { tablaOrdenes } = getDomElements();
    if (!tablaOrdenes) return;

    const ordenesFiltradas = ordenesData.filter((o) => String(o.Estado || "").toLowerCase() !== "en proceso");
    if (!ordenesFiltradas.length) {
        tablaOrdenes.innerHTML = '<tr><td colspan="8">No hay órdenes registradas.</td></tr>';
        return;
    }

    tablaOrdenes.innerHTML = ordenesFiltradas.map((orden) => {
        const clienteNombre = `${orden.Nombre_cliente ?? ""} ${orden.Apellido_cliente ?? ""}`.trim();
        const badgeClass = Utils.getEstadoBadgeClass(orden.Estado);
        return `
            <tr>
                <td>${Utils.escapeHtml(orden.ID_orden)}</td>
                <td><span class="badge ${badgeClass}">${Utils.escapeHtml(orden.Estado)}</span></td>
                <td>${Utils.escapeHtml(clienteNombre)}</td>
                <td>${Utils.escapeHtml(orden.Equipo ?? "")}</td>
                <td>${Utils.escapeHtml(orden.Modelo ?? "")}</td>
                <td>${Utils.escapeHtml(orden.Des_cliente ?? "")}</td>
                <td>${Utils.escapeHtml(Utils.formatFecha(orden.Fecha_e ?? ""))}</td>
                <td class="table__actions">
                    <div class="row-actions">
                        <button type="button" class="icon-action icon-action--view" data-action="ver-detalle" data-id="${Utils.escapeHtml(orden.ID_orden)}" title="Ver detalles">${Iconos.ojo}</button>
                        <button type="button" class="icon-action icon-action--primary" data-action="seleccionar-asignacion" data-id="${Utils.escapeHtml(orden.ID_orden)}" title="Asignar técnico">${Iconos.asignar}</button>
                    </div>
                </td>
            </tr>
        `;
    }).join("");
}

function renderTablaEstado(tablaDestino, lista) {
    if (!tablaDestino) return;
    if (!lista.length) {
        tablaDestino.innerHTML = '<tr><td colspan="5">Sin órdenes.</td></tr>';
        return;
    }
    tablaDestino.innerHTML = lista.map((orden) => {
        const clienteNombre = `${orden.Nombre_cliente ?? ""} ${orden.Apellido_cliente ?? ""}`.trim();
        return `
            <tr>
                <td>${Utils.escapeHtml(orden.ID_orden)}</td>
                <td>${Utils.escapeHtml(clienteNombre)}</td>
                <td>${Utils.escapeHtml(orden.Modelo ?? "")}</td>
                <td>${Utils.escapeHtml(Utils.formatFecha(orden.Fecha_e ?? ""))}</td>
                <td class="table__actions">
                    <button type="button" class="btn btn--ghost" data-action="ver-detalle" data-id="${Utils.escapeHtml(orden.ID_orden)}">Detalle</button>
                </td>
            </tr>
        `;
    }).join("");
}

function renderModalOrdenesEstado(label, ordenesEstado) {
    const { tablaOrdenesEstadoBody, modalOrdenesEstadoSubtitle } = getDomElements();
    if (modalOrdenesEstadoSubtitle) {
        modalOrdenesEstadoSubtitle.textContent = `Órdenes ${label}`;
    }
    if (!tablaOrdenesEstadoBody) return;

    const ordenesFiltradas = ordenesEstado.filter((o) => String(o.Estado || "").toLowerCase() !== "en proceso");
    if (!ordenesFiltradas.length) {
        tablaOrdenesEstadoBody.innerHTML = '<tr><td colspan="8">No hay órdenes en esta categoría.</td></tr>';
        return;
    }

    tablaOrdenesEstadoBody.innerHTML = ordenesFiltradas.map((orden) => {
        const clienteNombre = `${orden.Nombre_cliente ?? ""} ${orden.Apellido_cliente ?? ""}`.trim();
        const badgeClass = Utils.getEstadoBadgeClass(orden.Estado);
        return `
            <tr>
                <td>${Utils.escapeHtml(orden.ID_orden)}</td>
                <td><span class="badge ${badgeClass}">${Utils.escapeHtml(orden.Estado ?? "")}</span></td>
                <td>${Utils.escapeHtml(clienteNombre)}</td>
                <td>${Utils.escapeHtml(orden.Equipo ?? "")}</td>
                <td>${Utils.escapeHtml(orden.Modelo ?? "")}</td>
                <td>${Utils.escapeHtml(orden.Des_cliente ?? "")}</td>
                <td>${Utils.escapeHtml(Utils.formatFecha(orden.Fecha_e ?? ""))}</td>
                <td class="table__actions">
                    <button type="button" class="icon-action icon-action--view" data-action="ver-detalle" data-id="${Utils.escapeHtml(orden.ID_orden)}" title="Ver detalles">${Iconos.ojo}</button>
                </td>
            </tr>`;
    }).join("");
}

function renderDetalleInfo(detalle) {
    const { detalleInfo } = getDomElements();
    if (!detalleInfo) return;
    if (!detalle) {
        detalleInfo.innerHTML = "<p>No hay información disponible.</p>";
        return;
    }

    const getField = (...keys) => {
        for (const k of keys) {
            if (k in detalle && detalle[k] !== null && detalle[k] !== undefined && String(detalle[k]).trim() !== "") {
                return detalle[k];
            }
        }
        return "";
    };

    const cliente = `${getField("Nombre_cliente")} ${getField("Apellido_cliente")}`.trim();
    const fecha = getField("Fecha_e", "Fecha", "Fecha_o", "Fecha_ingreso");
    const items = [
        ["ID orden", getField("ID_orden", "ID")],
        ["Estado", getField("Estado")],
        ["Cliente", cliente],
        ["Modelo", getField("Modelo")],
        ["Fecha ingreso", Utils.formatFecha(fecha)],
        ["Descripción", getField("Des_cliente")],
        ["Nota", getField("Nota")],
        ["Cotización", getField("Costo_reparacion")],
        ["Reparación", getField("Reparacion")],
        ["Revisión", getField("Revision")],
    ];

    const html = `
        <div class="device-detail__grid">
            ${items
                .filter(([, value]) => value !== "")
                .map(([label, value]) => `
                    <div class="detail-item">
                        <span class="device-detail__label">${Utils.escapeHtml(label)}</span>
                        <span class="device-detail__value">${Utils.escapeHtml(value)}</span>
                    </div>
                `)
                .join("")}
        </div>`;
    detalleInfo.innerHTML = html || "<p>Sin información disponible.</p>";
}

function renderResponsables(empleados) {
    const { detalleResponsables } = getDomElements();
    if (!detalleResponsables) return;

    const roles = [
        { label: "Guardó la orden", acciones: ["Recepcion"] },
        { label: "Asignada a", acciones: ["Asignada"] },
        { label: "Reparó", acciones: ["Reparada"] },
        { label: "Revisó", acciones: ["Revisión"] },
    ];

    const responsables = {};
    empleados.forEach((item) => {
        const accion = item.Accion || item.accion;
        if (!accion) return;
        const nombre = `${item.Nombre_em ?? ""} ${item.Apellido_em ?? ""}`.trim();
        if (!responsables[accion]) responsables[accion] = [];
        responsables[accion].push(`${nombre} (${item.ID_em})`);
    });

    const rows = `
        <div class="device-detail__grid">
            ${roles.map((rol) => {
                const nombres = rol.acciones
                    .flatMap((accion) => responsables[accion] || [])
                    .filter(Boolean);
                return `
                    <div class="detail-item">
                        <span class="device-detail__label">${Utils.escapeHtml(rol.label)}</span>
                        <span class="device-detail__value">${Utils.escapeHtml(nombres.length ? nombres.join(", ") : "Sin registro")}</span>
                    </div>
                `;
            }).join("")}
        </div>`;
    detalleResponsables.innerHTML = rows;
}

function renderFotos(fotos) {
    const { detalleFotos } = getDomElements();
    if (!detalleFotos) return;
    if (!fotos.length) {
        detalleFotos.innerHTML = "<p>No hay fotos registradas.</p>";
        return;
    }

    detalleFotos.innerHTML = `
        <h3>Fotos</h3>
        <div class="device-photos">
            ${fotos.map((foto) => {
                let src = foto.Foto_e || foto.foto || foto.url || "";
                if (src && !src.startsWith("/") && !src.startsWith("http")) {
                    src = `/${src}`;
                }
                return `
                    <div class="img-wrap">
                        <img src="${Utils.escapeHtml(src)}" alt="Evidencia">
                    </div>`;
            }).join("")}
        </div>`;
}

function renderTests(tests) {
    const { detalleTests } = getDomElements();
    if (!detalleTests) return;
    if (!tests.length) {
        detalleTests.innerHTML = "<p>No hay tests registrados.</p>";
        return;
    }

    detalleTests.innerHTML = `
        <h3>Historial de revisiones</h3>
        <div class="table-wrap">
            <table class="table">
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Número</th>
                        <th>Observaciones</th>
                        <th>Costo</th>
                    </tr>
                </thead>
                <tbody>
                    ${tests.map((test) => `
                        <tr>
                            <td>${Utils.escapeHtml(Utils.formatFecha(test.Fecha_e ?? test.Fecha ?? ""))}</td>
                            <td>${Utils.escapeHtml(test.Num_test ?? "")}</td>
                            <td>${Utils.escapeHtml(test.Observaciones ?? "")}</td>
                            <td>${Utils.escapeHtml(test.Costo_reparacion ?? "0")}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
    `;
}

function renderSelectTecnicos(select, tecnicos) {
    if (!select) return;
    select.innerHTML = '<option value="">Seleccione un técnico</option>' + tecnicos.map((tec) => {
        const nombre = `${tec.nombre ?? ""} ${tec.apellido ?? ""}`.trim();
        return `<option value="${Utils.escapeHtml(tec.id)}">${Utils.escapeHtml(nombre)} (${Utils.escapeHtml(tec.id)})</option>`;
    }).join("");
}

function renderSelectOrdenesAsignar(ordenesData) {
    const { selectOrdenAsignar } = getDomElements();
    if (!selectOrdenAsignar) return;

    const pendientes = ordenesData.filter((o) => String(o.Estado || "").toLowerCase() === "pendiente");
    selectOrdenAsignar.innerHTML = '<option value="">Seleccione una orden</option>' + pendientes.map((orden) => {
        return `<option value="${Utils.escapeHtml(orden.ID_orden)}">#${Utils.escapeHtml(orden.ID_orden)} - ${Utils.escapeHtml(orden.Modelo ?? "")}</option>`;
    }).join("");
}

function renderPreviewFotos(files) {
    const { previewFotos } = getDomElements();
    if (!previewFotos) return;

    const lista = Array.from(files || []);
    if (!lista.length) {
        previewFotos.innerHTML = "";
        return;
    }

    previewFotos.innerHTML = lista
        .map((file) => `<img src="${URL.createObjectURL(file)}" alt="${Utils.escapeHtml(file.name)}">`)
        .join("");
}

function renderTablaTrabajosTecnico(lista) {
    const { tablaTrabajosTecnico } = getDomElements();
    if (!tablaTrabajosTecnico) return;

    if (!lista.length) {
        tablaTrabajosTecnico.innerHTML = '<tr><td colspan="5">Sin trabajos asignados.</td></tr>';
        return;
    }

    tablaTrabajosTecnico.innerHTML = lista.map((orden) => {
        const clienteNombre = `${orden.Nombre_cliente ?? ""} ${orden.Apellido_cliente ?? ""}`.trim();
        return `
            <tr>
                <td>${Utils.escapeHtml(orden.ID_orden)}</td>
                <td>${Utils.escapeHtml(clienteNombre)}</td>
                <td>${Utils.escapeHtml(orden.modelo ?? "")}</td>
                <td>${Utils.escapeHtml(orden.Estado ?? "")}</td>
                <td class="table__actions">
                    <button type="button" class="btn btn--ghost" data-action="ver-detalle" data-id="${Utils.escapeHtml(orden.ID_orden)}">Detalle</button>
                </td>
            </tr>
        `;
    }).join("");
}

// ============================================
// 7. FUNCIONES DE CARGA DE DATOS
// ============================================
async function cargarOrdenes() {
    try {
        const data = await Utils.fetchJson(CONFIG.API.ORDENES);
        ordenes = data.ordenes || [];
        renderTablaOrdenes(ordenes);
        actualizarEstadisticas(ordenes);
        renderSelectOrdenesAsignar(ordenes);

        const { tablaPendientes, tablaAsignadas, tablaRevisadas } = getDomElements();
        await Promise.all([
            cargarOrdenesEstado("Pendiente", tablaPendientes),
            cargarOrdenesEstado("Asignada", tablaAsignadas),
            cargarOrdenesEstado("Revisado", tablaRevisadas),
        ]);
    } catch (error) {
        console.error("Error cargando órdenes:", error);
        Utils.showMessage(error.message || "No se pudieron cargar las órdenes.", true);
    }
}

async function cargarOrdenesEstado(estado, tablaDestino) {
    if (!tablaDestino) return;
    try {
        const data = await Utils.fetchJson(`${CONFIG.API.ORDENES}?estado=${encodeURIComponent(estado)}`);
        renderTablaEstado(tablaDestino, data.ordenes || []);
    } catch (error) {
        tablaDestino.innerHTML = '<tr><td colspan="5">No se pudieron cargar las órdenes.</td></tr>';
    }
}

async function cargarModelos() {
    const { selectModelo } = getDomElements();
    if (!selectModelo) return;

    try {
        const data = await Utils.fetchJson(CONFIG.API.MODELOS);
        const modelos = data.modelos || [];
        selectModelo.innerHTML = '<option value="">Seleccione modelo</option>' + modelos.map((modelo) => {
            const label = `${modelo.clase_nombre ?? ""} ${modelo.marca_nombre ?? ""} ${modelo.nombre ?? ""}`.trim();
            return `<option value="${Utils.escapeHtml(modelo.id)}">${Utils.escapeHtml(label)}</option>`;
        }).join("");
    } catch (error) {
        console.error("Error cargando modelos:", error);
    }
}

async function cargarTecnicos() {
    try {
        const data = await Utils.fetchJson(CONFIG.API.TECNICOS);
        const tecnicos = data.tecnicos || [];
        const { selectTecnico, modalTecnicoSelect } = getDomElements();
        renderSelectTecnicos(selectTecnico, tecnicos);
        renderSelectTecnicos(modalTecnicoSelect, tecnicos);
    } catch (error) {
        console.error("Error cargando técnicos:", error);
    }
}

async function cargarTrabajosTecnico() {
    const { modalTecnicoSelect, tablaTrabajosTecnico } = getDomElements();
    const idTecnico = modalTecnicoSelect?.value;

    if (!idTecnico) {
        Utils.showMessage("Selecciona un técnico.", true);
        return;
    }
    if (!tablaTrabajosTecnico) return;

    try {
        const data = await Utils.fetchJson(`${CONFIG.API.TECNICOS}/${encodeURIComponent(idTecnico)}/ordenes`);
        renderTablaTrabajosTecnico(data.ordenes || []);
    } catch (error) {
        tablaTrabajosTecnico.innerHTML = '<tr><td colspan="5">No se pudieron cargar los trabajos.</td></tr>';
    }
}

// ============================================
// 8. FUNCIONES DE ACCIÓN (CRUD)
// ============================================
function actualizarEstadisticas(ordenesData) {
    const count = (estado) => ordenesData.filter((o) => String(o.Estado || "").toLowerCase() === estado).length;
    const pendientes = count("pendiente");
    const asignadas = count("asignada");
    const revisadas = ordenesData.filter((o) => ["revisado", "en revisión", "en revision"].includes(String(o.Estado || "").toLowerCase())).length;
    const reparadas = count("reparada");

    const { statPendientes, statAsignadas, statRevisadas } = getDomElements();
    if (statPendientes) statPendientes.textContent = String(pendientes);
    if (statAsignadas) statAsignadas.textContent = String(asignadas);
    if (statRevisadas) statRevisadas.textContent = String(revisadas);

    const statReparadas = document.getElementById("stat-reparadas");
    if (statReparadas) statReparadas.textContent = String(reparadas);
}

function setClienteStatus(message, isError = false) {
    const { clienteStatus } = getDomElements();
    if (!clienteStatus) return;
    clienteStatus.textContent = message;
    clienteStatus.classList.toggle("is-error", isError);
}

function setEquipoStatus(message, isError = false) {
    const { equipoStatus } = getDomElements();
    if (!equipoStatus) return;
    equipoStatus.textContent = message;
    equipoStatus.classList.toggle("is-error", isError);
}

function limpiarClienteForm() {
    setFieldValue("cliente-nombre", "");
    setFieldValue("cliente-apellido", "");
    setFieldValue("cliente-celular", "");
    setFieldValue("cliente-correo", "");
    setFieldValue("cliente-direccion", "");
    setFieldValue("cliente-tipo", "");
}

function getFieldValue(fieldId) {
    const field = document.getElementById(fieldId);
    return field && "value" in field ? String(field.value).trim() : "";
}

function setFieldValue(fieldId, value) {
    const field = document.getElementById(fieldId);
    if (field && "value" in field) {
        field.value = value;
    }
}

function obtenerSiguienteNumeroTest() {
    const numeros = testsOrdenActual
        .map((test) => Number(test.Num_test ?? test.num_test ?? 0))
        .filter((num) => Number.isFinite(num));
    return numeros.length ? Math.max(...numeros) + 1 : 1;
}

// ============================================
// 9. VERIFICACIONES
// ============================================
async function verificarCliente() {
    const cedula = getFieldValue("cliente-cedula");
    if (!cedula) {
        setClienteStatus("Ingresa una cédula para verificar.", true);
        return;
    }

    if (cedula.length !== 8) {
        setClienteStatus("La cédula debe tener exactamente 8 dígitos.", true);
        return;
    }

    try {
        const data = await Utils.fetchJson(`/api/clientes/${encodeURIComponent(cedula)}`);
        const cliente = data.cliente || data.data || {};

        clienteActualId = cliente.id || cliente.cedula || cedula;
        setFieldValue("cliente-nombre", cliente.nombre || "");
        setFieldValue("cliente-apellido", cliente.apellido || "");
        setFieldValue("cliente-celular", cliente.celular || "");
        setFieldValue("cliente-correo", cliente.correo || "");
        setFieldValue("cliente-direccion", cliente.direccion || "");
        setFieldValue("cliente-tipo", cliente.tipo || "natural");
        setClienteStatus("Cliente verificado correctamente.");

        const { btnCrearCliente } = getDomElements();
        if (btnCrearCliente) btnCrearCliente.hidden = true;
    } catch (error) {
        clienteActualId = null;
        limpiarClienteForm();
        setClienteStatus("Cliente no encontrado. Regístralo para continuar.", true);
        const { btnCrearCliente } = getDomElements();
        if (btnCrearCliente) btnCrearCliente.hidden = false;
    }
}

async function verificarEquipo() {
    const idEquipo = getFieldValue("orden-id-equipo");
    if (!idEquipo) {
        setEquipoStatus("Ingresa el IMEI del equipo para verificar.", true);
        return;
    }

    if (!/^\d+$/.test(idEquipo)) {
        setEquipoStatus("El IMEI solo puede contener números.", true);
        return;
    }

    if (idEquipo.length !== 15) {
        setEquipoStatus("El IMEI debe tener exactamente 15 caracteres.", true);
        return;
    }

    try {
        const data = await Utils.fetchJson(`/api/ordenes-servicio/equipo/${encodeURIComponent(idEquipo)}`);

        if (data.exists) {
            const equipo = data.equipo || {};
            setEquipoStatus("Equipo encontrado. Los datos se cargarán automáticamente.");

            const { selectModelo } = getDomElements();
            if (equipo.id_modelo && selectModelo) {
                selectModelo.value = String(equipo.id_modelo);
            }
            if (equipo.color) {
                setFieldValue("orden-color", equipo.color);
            }
            if (equipo.capacidad) {
                const capSelect = document.getElementById("orden-capacidad");
                if (capSelect) {
                    capSelect.value = equipo.capacidad;
                }
            }
        } else {
            setEquipoStatus("Equipo no encontrado. Se creará al guardar la orden.", true);
        }
    } catch (error) {
        console.error("Error verificando equipo:", error);
        setEquipoStatus("No se pudo verificar el equipo.", true);
    }
}

async function registrarClienteDesdeFormulario() {
    try {
        const payload = {
            cedula: getFieldValue("cliente-cedula"),
            nombre: getFieldValue("cliente-nombre"),
            apellido: getFieldValue("cliente-apellido"),
            celular: getFieldValue("cliente-celular"),
            correo: getFieldValue("cliente-correo"),
            direccion: getFieldValue("cliente-direccion"),
            tipo: getFieldValue("cliente-tipo") || "natural",
        };

        if (!payload.cedula || !payload.nombre || !payload.apellido || !payload.celular) {
            setClienteStatus("Cédula, nombre, apellido y celular son obligatorios.", true);
            return;
        }

        if (!/^\d{8}$/.test(payload.cedula)) {
            setClienteStatus("La cédula debe tener exactamente 8 dígitos.", true);
            return;
        }

        if (!/^\d{11}$/.test(payload.celular)) {
            setClienteStatus("El celular debe tener exactamente 11 dígitos.", true);
            return;
        }

        if (payload.correo && !Utils.isValidEmail(payload.correo)) {
            setClienteStatus("El correo electrónico no es válido.", true);
            return;
        }

        const data = await Utils.fetchJson("/api/clientes", {
            method: "POST",
            body: JSON.stringify(payload),
        });

        clienteActualId = data.id || payload.cedula;
        setClienteStatus("Cliente registrado correctamente.");

        const { btnCrearCliente } = getDomElements();
        if (btnCrearCliente) btnCrearCliente.hidden = true;
    } catch (error) {
        console.error("Error registrando cliente:", error);
        setClienteStatus(error.message || "No se pudo registrar el cliente.", true);
    }
}

// ============================================
// 10. EVENTOS PRINCIPALES
// ============================================
async function onSubmitOrden(event) {
    event.preventDefault();
    const { formOrden, inputFecha, selectModelo, btnCrearCliente } = getDomElements();
    if (!formOrden) return;

    const idEquipo = getFieldValue("orden-id-equipo");
    if (!idEquipo) {
        Utils.showMessage("El IMEI del equipo es obligatorio.", true);
        return;
    }
    if (!/^\d+$/.test(idEquipo)) {
        Utils.showMessage("El IMEI solo puede contener números.", true);
        return;
    }
    if (idEquipo.length !== 15) {
        Utils.showMessage("El IMEI debe tener exactamente 15 caracteres.", true);
        return;
    }

    const idModelo = selectModelo?.value;
    const modeloCustom = getFieldValue("orden-modelo-custom");
    if (!idModelo && !modeloCustom) {
        Utils.showMessage("Debes seleccionar un modelo o escribir uno personalizado.", true);
        return;
    }

    if (modeloCustom && modeloCustom.length > 30) {
        Utils.showMessage("El modelo personalizado no puede exceder 30 caracteres.", true);
        return;
    }

    const descripcion = getFieldValue("orden-descripcion");
    if (!descripcion) {
        Utils.showMessage("La descripción del problema es obligatoria.", true);
        return;
    }
    if (descripcion.length > 100) {
        Utils.showMessage("La descripción no puede exceder 100 caracteres.", true);
        return;
    }

    const nota = getFieldValue("orden-nota");
    if (nota && nota.length > 50) {
        Utils.showMessage("Las notas no pueden exceder 50 caracteres.", true);
        return;
    }

    const correo = getFieldValue("cliente-correo");
    if (correo && !Utils.isValidEmail(correo)) {
        Utils.showMessage("El correo electrónico no es válido.", true);
        return;
    }

    const celular = getFieldValue("cliente-celular");
    if (celular && !/^\d{11}$/.test(celular)) {
        Utils.showMessage("El celular debe tener exactamente 11 dígitos.", true);
        return;
    }

    const cedula = getFieldValue("cliente-cedula");
    if (!cedula) {
        Utils.showMessage("La cédula del cliente es obligatoria.", true);
        return;
    }
    if (!/^\d{8}$/.test(cedula)) {
        Utils.showMessage("La cédula debe tener exactamente 8 dígitos numéricos.", true);
        return;
    }

    let clienteId = clienteActualId;
    if (!clienteId) {
        try {
            const data = await Utils.fetchJson(`/api/clientes/${encodeURIComponent(cedula)}`);
            const cliente = data.cliente || data.data || {};
            clienteId = cliente.id || cliente.cedula || cedula;
            setFieldValue("cliente-nombre", cliente.nombre || "");
            setFieldValue("cliente-apellido", cliente.apellido || "");
            setFieldValue("cliente-celular", cliente.celular || "");
            setFieldValue("cliente-correo", cliente.correo || "");
            setFieldValue("cliente-direccion", cliente.direccion || "");
        } catch (e) {}
    }

    if (!clienteId) {
        const nombre = getFieldValue("cliente-nombre");
        const apellido = getFieldValue("cliente-apellido");
        const celular = getFieldValue("cliente-celular");

        if (!nombre || !apellido || !celular) {
            Utils.showMessage("Para registrar un nuevo cliente, completa nombre, apellido y celular.", true);
            return;
        }

        await registrarClienteDesdeFormulario();
        clienteId = clienteActualId;
    }

    if (!clienteId) {
        Utils.showMessage("Debes verificar o registrar el cliente primero.", true);
        return;
    }

    const payload = {
        id_cliente: clienteId,
        id_equipo: idEquipo,
        id_modelo: idModelo || null,
        modelo_custom: modeloCustom || null,
        color: getFieldValue("orden-color") || "",
        capacidad: getFieldValue("orden-capacidad") || "",
        descripcion: descripcion,
        nota: nota || null,
        nombre: getFieldValue("cliente-nombre") || "",
        apellido: getFieldValue("cliente-apellido") || "",
        celular: getFieldValue("cliente-celular") || "",
        correo: getFieldValue("cliente-correo") || "",
        direccion: getFieldValue("cliente-direccion") || "",
        tipo: getFieldValue("cliente-tipo") || "natural",
    };

    try {
        await Utils.fetchJson(CONFIG.API.ORDENES_SERVICIO, {
            method: "POST",
            body: JSON.stringify(payload),
        });

        Utils.showMessage("Orden creada correctamente.");
        formOrden.reset();
        closeModal("modal-nueva-orden");

        clienteActualId = null;
        setClienteStatus("");
        if (btnCrearCliente) btnCrearCliente.hidden = true;

        if (inputFecha) {
            inputFecha.value = "";
        }

        await cargarOrdenes();
    } catch (error) {
        console.error("Error creando orden:", error);
        Utils.showMessage(error.message || "No se pudo crear la orden.", true);
    }
}

async function abrirDetalleOrden(idOrden) {
    try {
        // Extraer solo el número para la URL
        const numeroOrden = Utils.extraerNumeroOrden(idOrden);
        if (!numeroOrden) {
            Utils.showMessage("ID de orden inválido.", true);
            return;
        }
        
        console.log(`Obteniendo detalle de orden #${numeroOrden}`);
        
        const data = await Utils.fetchJson(`${CONFIG.API.ORDENES}/${numeroOrden}`);
        ordenActualId = idOrden;
        testsOrdenActual = data.test_orden || [];

        const { detalleOrdenId, revisionOrdenId, fotosOrdenId } = getDomElements();
        if (detalleOrdenId) detalleOrdenId.value = String(idOrden);
        if (revisionOrdenId) revisionOrdenId.value = String(idOrden);
        if (fotosOrdenId) fotosOrdenId.value = String(idOrden);

        renderDetalleInfo(data.detalle_orden);
        renderResponsables(data.empleados_orden || []);
        renderFotos(data.fotos_orden || []);
        renderTests(data.test_orden || []);

        openModal("modal-detalle-orden");
    } catch (error) {
        console.error("Error cargando detalle:", error);
        Utils.showMessage(error.message || "No se pudo cargar el detalle de la orden.", true);
    }
}

// ============================================
// FUNCIÓN DE ASIGNACIÓN CORREGIDA
// ============================================
async function asignarOrden() {
    const selectOrden = document.getElementById("select-orden-asignar");
    const selectTecnico = document.getElementById("modal-tecnico-select");
    
    const idOrden = selectOrden?.value;
    const idTecnico = selectTecnico?.value;
    
    console.log("Valor orden:", idOrden);
    console.log("Valor técnico:", idTecnico);

    if (!idOrden || idOrden === "") {
        Utils.showMessage("Por favor, selecciona una orden pendiente.", true);
        return;
    }

    if (!idTecnico || idTecnico === "") {
        Utils.showMessage("Por favor, selecciona un técnico.", true);
        return;
    }

    // Extraer solo el número de la orden para la URL
    const numeroOrden = Utils.extraerNumeroOrden(idOrden);
    if (!numeroOrden) {
        Utils.showMessage("ID de orden inválido.", true);
        return;
    }

    try {
        console.log(`Asignando orden #${numeroOrden} (${idOrden}) al técnico ${idTecnico}`);
        
        const result = await Utils.fetchJson(`${CONFIG.API.ORDENES}/${numeroOrden}/asignar`, {
            method: "POST",
            body: JSON.stringify({ 
                id_empleado: parseInt(idTecnico, 10) 
            }),
        });

        console.log("Resultado asignación:", result);
        
        Utils.showMessage("✅ Orden asignada correctamente.");
        closeModal("modal-asignar-tecnico");
        await cargarOrdenes();
        
        if (selectOrden) selectOrden.value = "";
        if (selectTecnico) selectTecnico.value = "";
        
    } catch (error) {
        console.error("Error asignando orden:", error);
        Utils.showMessage(`❌ ${error.message || "No se pudo asignar la orden."}`, true);
    }
}

async function guardarRevision(event) {
    event.preventDefault();
    const { revisionOrdenId, formRevision } = getDomElements();
    const idOrden = revisionOrdenId?.value || ordenActualId;

    if (!idOrden) {
        Utils.showMessage("Selecciona una orden.", true);
        return;
    }

    // Extraer solo el número para la URL
    const numeroOrden = Utils.extraerNumeroOrden(idOrden);
    if (!numeroOrden) {
        Utils.showMessage("ID de orden inválido.", true);
        return;
    }

    const payload = {};
    const campos = [
        "Btn_power", "Btn_vol", "Cornetas", "Mica", "LCD", "Tactil",
        "Wifi", "Puerto_carga", "Cam_pos", "Cam_del", "Microfono",
        "Flash", "Btn_sil", "Auricular", "Senal", "Sensor_proximidad",
        "Face_id", "Bluetooth"
    ];

    campos.forEach((campo) => {
        const el = formRevision?.querySelector(`[name="${campo}"]`);
        payload[campo] = (el && el.type === "checkbox" && el.checked) ? 1 : 0;
    });

    payload.Num_test = obtenerSiguienteNumeroTest();
    payload.Observaciones = formRevision?.querySelector('[name="Observaciones"]')?.value || "";

    try {
        await Utils.fetchJson(`${CONFIG.API.ORDENES}/${numeroOrden}/revision`, {
            method: "POST",
            body: JSON.stringify(payload),
        });

        Utils.showMessage("Revisión registrada.");
        formRevision?.reset();
        closeModal("modal-revision-orden");
        await abrirDetalleOrden(idOrden);
        await cargarOrdenes();
    } catch (error) {
        Utils.showMessage(error.message || "No se pudo guardar la revisión.", true);
    }
}

async function guardarFotos(event) {
    event.preventDefault();
    const { fotosOrdenId, formFotos } = getDomElements();
    const idOrden = fotosOrdenId?.value || ordenActualId;

    if (!idOrden || !formFotos) return;

    // Extraer solo el número para la URL
    const numeroOrden = Utils.extraerNumeroOrden(idOrden);
    if (!numeroOrden) {
        Utils.showMessage("ID de orden inválido.", true);
        return;
    }

    const formData = new FormData(formFotos);
    const csrf = Utils.getCsrfToken();
    const token = Utils.getAccessToken();

    try {
        const headers = new Headers();
        if (csrf) headers.set("X-CSRFToken", csrf);
        if (token) headers.set("Authorization", `Bearer ${token}`);

        const response = await fetch(`/api/taller/ordenes/${numeroOrden}/fotos`, {
            method: "POST",
            body: formData,
            headers,
            credentials: "same-origin",
        });

        const data = await response.json().catch(() => ({}));
        if (!response.ok || data.ok === false) {
            throw new Error(data.message || "No se pudieron guardar las fotos.");
        }

        Utils.showMessage("Fotos registradas.");
        formFotos.reset();
        renderPreviewFotos([]);
        closeModal("modal-fotos-orden");
        await abrirDetalleOrden(idOrden);
    } catch (error) {
        Utils.showMessage(error.message || "No se pudieron guardar las fotos.", true);
    }
}

// ============================================
// 11. EVENTOS DE TABLA (Delegación)
// ============================================
function onTablaClick(event) {
    const btn = event.target.closest("button[data-action]");
    if (!btn) return;

    const action = btn.dataset.action;
    const id = btn.dataset.id;
    if (!id) return;

    if (action === "ver-detalle") {
        abrirDetalleOrden(id);
        return;
    }

    if (action === "seleccionar-asignacion") {
        const selectOrden = document.getElementById("select-orden-asignar");
        if (selectOrden) {
            selectOrden.value = String(id);
            openModal("modal-asignar-tecnico");
        }
        return;
    }
}

function onEstadoCardClick(estado) {
    const label = {
        pendiente: "Pendientes",
        asignada: "Asignadas",
        revisada: "Revisadas",
        reparada: "Reparadas",
    }[estado] || "Órdenes";

    const estadoParam = {
        pendiente: "Pendiente",
        asignada: "Asignada",
        revisada: "Revisado",
        reparada: "Reparado",
    }[estado] || estado;

    Utils.fetchJson(`${CONFIG.API.ORDENES}?estado=${encodeURIComponent(estadoParam)}`)
        .then((data) => {
            renderModalOrdenesEstado(label, data.ordenes || []);
            openModal("modal-ordenes-estado");
        })
        .catch((error) => {
            console.error(`Error cargando órdenes ${estado}:`, error);
            const { modalOrdenesEstadoSubtitle } = getDomElements();
            if (modalOrdenesEstadoSubtitle) {
                modalOrdenesEstadoSubtitle.textContent = "No se pudo cargar la información.";
            }
        });
}

// ============================================
// 12. INICIALIZACIÓN
// ============================================
document.addEventListener("DOMContentLoaded", () => {
    const {
        inputFecha,
        formOrden,
        btnVerificarEquipo,
        btnVerificarCliente,
        btnCrearCliente,
        btnAsignarOrden,
        btnCargarTrabajos,
        formRevision,
        formFotos,
        inputFotos,
        estadoCards,
        tablaOrdenes,
    } = getDomElements();

    if (inputFecha) {
        const hoy = new Date();
        const fechaHoy = hoy.toISOString().slice(0, 10);
        inputFecha.min = fechaHoy;
        inputFecha.value = "";
    }

    const inputImei = document.getElementById("orden-id-equipo");
    if (inputImei) {
        inputImei.addEventListener("input", (e) => {
            e.target.value = e.target.value.replace(/[^0-9]/g, "").slice(0, 15);
        });
    }

    const inputCedula = document.getElementById("cliente-cedula");
    if (inputCedula) {
        inputCedula.addEventListener("input", (e) => {
            e.target.value = e.target.value.replace(/[^0-9]/g, "").slice(0, 8);
        });
    }

    const inputPatron = document.getElementById("orden-patron");
    if (inputPatron) {
        inputPatron.addEventListener("input", (e) => {
            let value = e.target.value.replace(/[^0-9-]/g, "");
            let numbers = value.replace(/-/g, "").split("");
            let used = new Set();
            let validNumbers = [];
            for (let num of numbers) {
                if (num >= "1" && num <= "9" && !used.has(num)) {
                    validNumbers.push(num);
                    used.add(num);
                }
            }
            validNumbers = validNumbers.slice(0, 9);
            e.target.value = validNumbers.join("-");
        });
    }

    const inputCelular = document.getElementById("cliente-celular");
    if (inputCelular) {
        inputCelular.addEventListener("input", (e) => {
            e.target.value = e.target.value.replace(/[^0-9]/g, "").slice(0, 11);
        });
    }

    const inputClave = document.getElementById("orden-clave");
    if (inputClave) {
        inputClave.addEventListener("input", (e) => {
            e.target.value = e.target.value.replace(/[^0-9]/g, "").slice(0, 30);
        });
    }

    btnVerificarEquipo?.addEventListener("click", verificarEquipo);
    btnVerificarCliente?.addEventListener("click", verificarCliente);
    btnCrearCliente?.addEventListener("click", registrarClienteDesdeFormulario);
    formOrden?.addEventListener("submit", onSubmitOrden);
    
    if (btnAsignarOrden) {
        btnAsignarOrden.addEventListener("click", asignarOrden);
    }
    
    btnCargarTrabajos?.addEventListener("click", cargarTrabajosTecnico);
    formRevision?.addEventListener("submit", guardarRevision);
    formFotos?.addEventListener("submit", guardarFotos);
    inputFotos?.addEventListener("change", () => renderPreviewFotos(inputFotos.files));
    tablaOrdenes?.addEventListener("click", onTablaClick);

    document.getElementById("btn-asignar-tecnico")?.addEventListener("click", () => {
        openModal("modal-asignar-tecnico");
    });

    estadoCards.forEach((card) => {
        const estado = card.dataset.estadoCard;
        if (!estado) return;
        card.addEventListener("click", () => onEstadoCardClick(estado));
        card.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                onEstadoCardClick(estado);
            }
        });
    });

    document.getElementById("btn-nueva-orden")?.addEventListener("click", () => {
        if (inputFecha) {
            inputFecha.value = "";
        }
    });

    Promise.all([
        cargarModelos(),
        cargarTecnicos(),
        cargarOrdenes(),
    ]).catch((error) => {
        console.error("Error en la inicialización:", error);
    });
});