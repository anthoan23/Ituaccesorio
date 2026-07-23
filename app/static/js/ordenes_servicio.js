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
    ojo: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="16" height="16"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" fill="currentColor"/></svg>`,
    asignar: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="16" height="16"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" fill="currentColor"/></svg>`
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
            let msg = "";
            if (isJson && payload) {
                msg = payload.message || payload.error || payload.Mensaje || "Error en la solicitud";
            } else {
                msg = String(payload || response.statusText || "Error en la solicitud");
            }
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
            alert(`❌ ${message}`);
        } else {
            console.info(`✅ ${message}`);
        }
    },

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    validarCelular(celular) {
        if (!celular) return false;
        const limpio = celular.replace(/\D/g, '');
        const prefijos = ['0412', '0414', '0416', '0422', '0424', '0426'];
        if (limpio.length !== 11) return false;
        const prefijo = limpio.substring(0, 4);
        return prefijos.includes(prefijo);
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

    soloLetras(value) {
        return /^[a-zA-ZáéíóúñÁÉÍÓÚÑ\s]*$/.test(value);
    },

    soloNumeros(value) {
        return /^\d*$/.test(value);
    }
};

// ============================================
// 3. MANEJADORES DE MODALES (usando UiModal)
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
        revisionOrdenId: document.getElementById("revision-orden-id"),
        fotosOrdenId: document.getElementById("fotos-orden-id"),
        formRevision: document.getElementById("form-revision-orden"),
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
        tablaOrdenes.innerHTML = '<tr><td colspan="8" class="table__empty">No hay órdenes registradas.</td></tr>';
        return;
    }

    tablaOrdenes.innerHTML = ordenesFiltradas.map((orden) => {
        const clienteNombre = `${orden.Nombre_cliente ?? ""} ${orden.Apellido_cliente ?? ""}`.trim();
        const badgeClass = Utils.getEstadoBadgeClass(orden.Estado);
        return `
            <tr>
                <td><span class="chip">${Utils.escapeHtml(orden.ID_orden)}</span></td>
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
        tablaDestino.innerHTML = '<tr><td colspan="5" class="table__empty">Sin órdenes.</td></tr>';
        return;
    }

    const esPendiente = tablaDestino.id === 'tabla-pendientes';

    tablaDestino.innerHTML = lista.map((orden) => {
        const clienteNombre = `${orden.Nombre_cliente ?? ""} ${orden.Apellido_cliente ?? ""}`.trim();
        const estado = orden.Estado || orden.estado || '';
        const badgeClass = Utils.getEstadoBadgeClass(estado);

        let acciones = `
            <button type="button" class="ui-btn ui-btn--ghost ui-btn--sm" data-action="ver-detalle" data-id="${Utils.escapeHtml(orden.ID_orden)}">Detalle</button>
        `;

        if (esPendiente) {
            acciones += `
                <button type="button" class="ui-btn ui-btn--primary ui-btn--sm" data-action="seleccionar-asignacion" data-id="${Utils.escapeHtml(orden.ID_orden)}">Asignar</button>
            `;
        }

        return `
            <tr>
                <td><span class="chip">${Utils.escapeHtml(orden.ID_orden)}</span></td>
                <td><span class="badge ${badgeClass}">${Utils.escapeHtml(estado)}</span></td>
                <td>${Utils.escapeHtml(clienteNombre)}</td>
                <td>${Utils.escapeHtml(orden.Modelo ?? "")}</td>
                <td>${Utils.escapeHtml(Utils.formatFecha(orden.Fecha_e ?? ""))}</td>
                <td class="table__actions">
                    <div class="row-actions">
                        ${acciones}
                    </div>
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
        tablaOrdenesEstadoBody.innerHTML = `
            <tr>
                <td colspan="8" class="table__empty">
                    No hay órdenes en estado <strong>${label.toLowerCase()}</strong>
                </td>
            </tr>`;
        return;
    }

    const mostrarAsignar = label.toLowerCase().includes('pendiente');

    tablaOrdenesEstadoBody.innerHTML = ordenesFiltradas.map((orden) => {
        const clienteNombre = `${orden.Nombre_cliente ?? ""} ${orden.Apellido_cliente ?? ""}`.trim();
        const estado = orden.Estado || orden.estado || '';
        const badgeClass = Utils.getEstadoBadgeClass(estado);

        let acciones = `
            <button type="button" class="icon-action icon-action--view" data-action="ver-detalle" data-id="${Utils.escapeHtml(orden.ID_orden)}" title="Ver detalles">${Iconos.ojo}</button>
        `;

        if (mostrarAsignar) {
            acciones += `
                <button type="button" class="icon-action icon-action--primary" data-action="seleccionar-asignacion" data-id="${Utils.escapeHtml(orden.ID_orden)}" title="Asignar técnico">${Iconos.asignar}</button>
            `;
        }

        return `
            <tr>
                <td><span class="chip">${Utils.escapeHtml(orden.ID_orden)}</span></td>
                <td><span class="badge ${badgeClass}">${Utils.escapeHtml(estado)}</span></td>
                <td>${Utils.escapeHtml(clienteNombre)}</td>
                <td>${Utils.escapeHtml(orden.Equipo ?? "")}</td>
                <td>${Utils.escapeHtml(orden.Modelo ?? "")}</td>
                <td>${Utils.escapeHtml(orden.Des_cliente ?? "")}</td>
                <td>${Utils.escapeHtml(Utils.formatFecha(orden.Fecha_e ?? ""))}</td>
                <td class="table__actions">
                    <div class="row-actions">
                        ${acciones}
                    </div>
                </td>
            </tr>`;
    }).join("");

    setTimeout(() => {
        const modalBody = document.getElementById('modal-ordenes-estado-body');
        if (modalBody) {
            modalBody.removeEventListener('click', onModalEstadoClick);
            modalBody.addEventListener('click', onModalEstadoClick);
        }
    }, 50);
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
        tablaTrabajosTecnico.innerHTML = '<tr><td colspan="5" class="table__empty">Sin trabajos asignados.</td></tr>';
        return;
    }

    tablaTrabajosTecnico.innerHTML = lista.map((orden) => {
        const clienteNombre = `${orden.Nombre_cliente ?? ""} ${orden.Apellido_cliente ?? ""}`.trim();
        return `
            <tr>
                <td><span class="chip">${Utils.escapeHtml(orden.ID_orden)}</span></td>
                <td>${Utils.escapeHtml(clienteNombre)}</td>
                <td>${Utils.escapeHtml(orden.modelo ?? "")}</td>
                <td><span class="badge ${Utils.getEstadoBadgeClass(orden.Estado)}">${Utils.escapeHtml(orden.Estado ?? "")}</span></td>
                <td class="table__actions">
                    <button type="button" class="ui-btn ui-btn--ghost ui-btn--sm" data-action="ver-detalle" data-id="${Utils.escapeHtml(orden.ID_orden)}">Detalle</button>
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
            cargarOrdenesEstado(["Revisado", "Revisada", "En revisión", "En revision"], tablaRevisadas),
        ]);
    } catch (error) {
        console.error("Error cargando órdenes:", error);
        Utils.showMessage(error.message || "No se pudieron cargar las órdenes.", true);
    }
}

async function cargarOrdenesEstado(estado, tablaDestino) {
    if (!tablaDestino) return;
    try {
        const estadoParam = Array.isArray(estado) ? estado.join(',') : estado;
        const data = await Utils.fetchJson(`${CONFIG.API.ORDENES}?estado=${encodeURIComponent(estadoParam)}`);
        renderTablaEstado(tablaDestino, data.ordenes || []);
    } catch (error) {
        tablaDestino.innerHTML = '<tr><td colspan="5" class="table__empty">No se pudieron cargar las órdenes.</td></tr>';
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
        tablaTrabajosTecnico.innerHTML = '<tr><td colspan="5" class="table__empty">No se pudieron cargar los trabajos.</td></tr>';
    }
}

// ============================================
// 8. FUNCIONES DE ACCIÓN (CRUD)
// ============================================
function actualizarEstadisticas(ordenesData) {
    const count = (estado) => ordenesData.filter((o) => String(o.Estado || "").toLowerCase() === estado).length;
    const pendientes = count("pendiente");
    const asignadas = count("asignada");
    const revisadas = ordenesData.filter((o) => {
        const estado = String(o.Estado || "").toLowerCase();
        return estado.includes("revis");
    }).length;
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
    clienteStatus.classList.remove("is-error", "is-success");
    if (isError) {
        clienteStatus.classList.add("is-error");
    } else if (message && !message.toLowerCase().includes("no encontrado")) {
        clienteStatus.classList.add("is-success");
    }
}

function setEquipoStatus(message, isError = false) {
    const { equipoStatus } = getDomElements();
    if (!equipoStatus) return;
    equipoStatus.textContent = message;
    equipoStatus.classList.remove("is-error", "is-success");
    if (isError) {
        equipoStatus.classList.add("is-error");
    } else if (message && !message.toLowerCase().includes("no encontrado")) {
        equipoStatus.classList.add("is-success");
    }
}

function limpiarClienteForm() {
    setFieldValue("cliente-nombre", "");
    setFieldValue("cliente-apellido", "");
    setFieldValue("cliente-celular", "");
    setFieldValue("cliente-correo", "");
    setFieldValue("cliente-direccion", "");
    setFieldValue("cliente-tipo", "natural");
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
            setEquipoStatus("Equipo encontrado.");

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
            if (equipo.patron) {
                setFieldValue("orden-patron", equipo.patron);
            }
            if (equipo.clave) {
                setFieldValue("orden-clave", equipo.clave);
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

        if (!Utils.validarCelular(payload.celular)) {
            setClienteStatus("El celular debe tener 11 dígitos y comenzar con: 0412, 0414, 0416, 0422, 0424 o 0426.", true);
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

    // Validar usando FieldValidator si está disponible
    if (window.FieldValidator && typeof window.FieldValidator.validateForm === 'function') {
        const isValid = window.FieldValidator.validateForm(formOrden);
        if (!isValid) {
            Utils.showMessage("Por favor, corrige los errores en el formulario.", true);
            const primerError = formOrden.querySelector('.field-error');
            if (primerError) {
                primerError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                primerError.focus();
            }
            return;
        }
    }

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

    const color = getFieldValue("orden-color");
    if (color && color.length > 15) {
        Utils.showMessage("El color no puede exceder los 15 caracteres.", true);
        return;
    }
    if (color && !Utils.soloLetras(color)) {
        Utils.showMessage("El color solo debe contener letras.", true);
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
    if (modeloCustom && !/^[a-zA-Z0-9\s\-]+$/.test(modeloCustom)) {
        Utils.showMessage("El modelo solo puede contener letras, números, espacios y guiones.", true);
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
    if (celular && !Utils.validarCelular(celular)) {
        Utils.showMessage("El celular debe tener 11 dígitos y comenzar con: 0412, 0414, 0416, 0422, 0424 o 0426.", true);
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

    const nombre = getFieldValue("cliente-nombre");
    const apellido = getFieldValue("cliente-apellido");
    
    if (nombre && nombre.length > 20) {
        Utils.showMessage("El nombre no puede exceder los 20 caracteres.", true);
        return;
    }
    if (nombre && !Utils.soloLetras(nombre)) {
        Utils.showMessage("El nombre solo debe contener letras.", true);
        return;
    }
    if (apellido && apellido.length > 20) {
        Utils.showMessage("El apellido no puede exceder los 20 caracteres.", true);
        return;
    }
    if (apellido && !Utils.soloLetras(apellido)) {
        Utils.showMessage("El apellido solo debe contener letras.", true);
        return;
    }

    const direccion = getFieldValue("cliente-direccion");
    if (direccion && direccion.length > 50) {
        Utils.showMessage("La dirección no puede exceder los 50 caracteres.", true);
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
            setFieldValue("cliente-tipo", cliente.tipo || "natural");
        } catch (e) {}
    }

    if (!clienteId) {
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

    const fechaActual = Utils.getFechaActual();

    const payload = {
        id_cliente: clienteId,
        id_equipo: idEquipo,
        id_modelo: idModelo || null,
        modelo_custom: modeloCustom || null,
        color: color || "",
        capacidad: getFieldValue("orden-capacidad") || "",
        descripcion: descripcion,
        nota: nota || null,
        nombre: nombre || "",
        apellido: apellido || "",
        celular: celular || "",
        correo: correo || "",
        direccion: direccion || "",
        tipo: getFieldValue("cliente-tipo") || "natural",
        fecha_ingreso: fechaActual,
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
            inputFecha.value = Utils.getFechaActual();
        }

        await cargarOrdenes();
    } catch (error) {
        console.error("Error creando orden:", error);
        Utils.showMessage(error.message || "No se pudo crear la orden.", true);
    }
}

// ============================================
// FUNCIÓN DE DETALLE DE ORDEN (ESTILO TALLER)
// ============================================
async function abrirDetalleOrden(idOrden) {
    try {
        console.log(`Obteniendo detalle de orden: ${idOrden}`);

        const data = await Utils.fetchJson(`${CONFIG.API.ORDENES}/${encodeURIComponent(idOrden)}`);
        ordenActualId = idOrden;
        testsOrdenActual = data.test_orden || [];

        const detalle = data.detalle_orden || {};

        renderDetalleOrdenModal(detalle);
        renderFotosOrdenModal(data.fotos_orden || []);
        renderTestsOrdenModal(data.test_orden || []);

        const { detalleOrdenId, revisionOrdenId, fotosOrdenId } = getDomElements();
        if (detalleOrdenId) detalleOrdenId.value = String(idOrden);
        if (revisionOrdenId) revisionOrdenId.value = String(idOrden);
        if (fotosOrdenId) fotosOrdenId.value = String(idOrden);

        openModal("modal-detalle-orden");
    } catch (error) {
        console.error("Error cargando detalle:", error);
        Utils.showMessage(error.message || "No se pudo cargar el detalle de la orden.", true);
    }
}

function renderDetalleOrdenModal(detalle) {
    const container = document.getElementById('modal-order-info');
    if (!container) return;

    if (!detalle || Object.keys(detalle).length === 0) {
        container.innerHTML = '<p class="device-detail__empty">No se encontró información de la orden</p>';
        return;
    }

    const estado = detalle.Estado || 'Pendiente';
    const badgeClass = Utils.getEstadoBadgeClass(estado);
    const clienteNombre = `${detalle.Nombre_cliente || ''} ${detalle.Apellido_cliente || ''}`.trim() || 'No especificado';
    const costo = detalle.Costo_reparacion;

    container.innerHTML = `
        <div class="detail-group">
            <span class="detail-label">ID Orden</span>
            <span class="detail-value"><strong>#${Utils.escapeHtml(detalle.ID_orden || '---')}</strong></span>
        </div>
        <div class="detail-group">
            <span class="detail-label">Estado</span>
            <span class="detail-value"><span class="badge ${badgeClass}">${Utils.escapeHtml(estado)}</span></span>
        </div>
        <div class="detail-group">
            <span class="detail-label">Cliente</span>
            <span class="detail-value"><strong>${Utils.escapeHtml(clienteNombre)}</strong></span>
        </div>
        <div class="detail-group">
            <span class="detail-label">Equipo</span>
            <span class="detail-value"><strong>${Utils.escapeHtml(detalle.Equipo || 'No especificado')}</strong></span>
        </div>
        <div class="detail-group">
            <span class="detail-label">Modelo</span>
            <span class="detail-value"><strong>${Utils.escapeHtml(detalle.Modelo || 'No especificado')}</strong></span>
        </div>
        <div class="detail-group">
            <span class="detail-label">Costo</span>
            <span class="detail-value"><strong>${costo ? `$${Number(costo).toFixed(2)}` : 'Sin cotizar'}</strong></span>
        </div>
        <div class="detail-group field--full">
            <span class="detail-label">Descripción del problema</span>
            <span class="detail-value">${Utils.escapeHtml(detalle.Des_cliente || 'Sin descripción')}</span>
        </div>
        ${detalle.Nota || detalle.Nota_orden_servicio ? `
            <div class="detail-group field--full">
                <span class="detail-label">Notas adicionales</span>
                <span class="detail-value" style="font-style: italic;">${Utils.escapeHtml(detalle.Nota || detalle.Nota_orden_servicio)}</span>
            </div>
        ` : ''}
    `;
}

function renderFotosOrdenModal(fotos) {
    const container = document.getElementById('modal-order-photos');
    if (!container) return;

    if (!fotos || !fotos.length) {
        container.innerHTML = '<p class="device-detail__empty">No hay fotos registradas para esta orden.</p>';
        return;
    }

    container.innerHTML = `
        <h3 class="card__subtitle">Fotos del dispositivo</h3>
        <div class="fotos-grid">
            ${fotos.map((foto, index) => {
                let src = foto.Foto_e || foto.foto || foto.url || foto.Foto_orden_servicio || "";
                if (src && !src.startsWith("/") && !src.startsWith("http")) {
                    src = `/${src}`;
                }
                return `
                    <div class="foto-item" data-foto-index="${index}">
                        <div class="foto-thumbnail" onclick="window.open('${Utils.escapeHtml(src)}', '_blank')">
                            <img src="${Utils.escapeHtml(src)}" alt="Foto ${index + 1}" loading="lazy">
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

function renderTestsOrdenModal(tests) {
    const container = document.getElementById('modal-order-tests');
    if (!container) return;

    if (!tests || !tests.length) {
        container.innerHTML = '<p class="device-detail__empty">No hay revisiones registradas.</p>';
        return;
    }

    container.innerHTML = `
        <h3 class="card__subtitle">Historial de revisiones</h3>
        <div class="tests-table-wrap">
            <table class="table">
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>N°</th>
                        <th>Observaciones</th>
                        <th>Costo</th>
                    </tr>
                </thead>
                <tbody>
                    ${tests.map((test) => `
                        <tr>
                            <td>${Utils.escapeHtml(Utils.formatFecha(test.Fecha_e ?? test.Fecha ?? ""))}</td>
                            <td>${Utils.escapeHtml(test.Num_test ?? "")}</td>
                            <td>${Utils.escapeHtml(test.Observaciones ?? test.Resultado_test ?? "")}</td>
                            <td>${test.Costo_reparacion ? `$${Number(test.Costo_reparacion).toFixed(2)}` : "—"}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
    `;
}

// ============================================
// FUNCIÓN DE ASIGNACIÓN
// ============================================
async function asignarOrden() {
    const selectOrden = document.getElementById("select-orden-asignar");
    const selectTecnico = document.getElementById("modal-tecnico-select");

    const idOrden = selectOrden?.value;
    const idTecnico = selectTecnico?.value;

    console.log("=== ASIGNANDO ORDEN ===");
    console.log("ID Orden:", idOrden);
    console.log("ID Técnico:", idTecnico);

    if (!idOrden || idOrden === "") {
        Utils.showMessage("Por favor, selecciona una orden pendiente.", true);
        return;
    }

    if (!idTecnico || idTecnico === "") {
        Utils.showMessage("Por favor, selecciona un técnico.", true);
        return;
    }

    const url = `${CONFIG.API.ORDENES}/${encodeURIComponent(idOrden)}/asignar`;
    const payload = { id_empleado: parseInt(idTecnico, 10) };

    console.log("URL:", url);
    console.log("Payload:", payload);

    try {
        const result = await Utils.fetchJson(url, {
            method: "POST",
            body: JSON.stringify(payload),
        });

        console.log("Resultado:", result);
        Utils.showMessage("✅ Orden asignada correctamente.");
        closeModal("modal-asignar-tecnico");
        await cargarOrdenes();

        if (selectOrden) selectOrden.value = "";
        if (selectTecnico) selectTecnico.value = "";

    } catch (error) {
        console.error("Error completo:", error);
        console.error("Mensaje de error:", error.message);
        Utils.showMessage(`❌ ${error.message || "No se pudo asignar la orden."}`, true);
    }
}

// ============================================
// FUNCIÓN DE REVISIÓN
// ============================================
async function guardarRevision(event) {
    event.preventDefault();
    const { revisionOrdenId, formRevision } = getDomElements();
    const idOrden = revisionOrdenId?.value || ordenActualId;

    if (!idOrden) {
        Utils.showMessage("Selecciona una orden.", true);
        return;
    }

    // Validar usando FieldValidator si está disponible
    if (window.FieldValidator && typeof window.FieldValidator.validateForm === 'function') {
        const isValid = window.FieldValidator.validateForm(formRevision);
        if (!isValid) {
            Utils.showMessage("Por favor, corrige los errores en el formulario.", true);
            return;
        }
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
        payload[campo] = (el && el.type === "radio" && el.checked && el.value === "1") ? 1 : 0;
        if (el && el.type === "radio" && el.checked && el.value === "0") {
            payload[campo] = 0;
        }
    });

    payload.Num_test = obtenerSiguienteNumeroTest();
    payload.Observaciones = formRevision?.querySelector('[name="Observaciones"]')?.value || "";

    try {
        await Utils.fetchJson(`${CONFIG.API.ORDENES}/${encodeURIComponent(idOrden)}/revision`, {
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

// ============================================
// FUNCIÓN DE FOTOS
// ============================================
async function guardarFotos(event) {
    event.preventDefault();
    const { fotosOrdenId, formFotos } = getDomElements();
    const idOrden = fotosOrdenId?.value || ordenActualId;

    if (!idOrden || !formFotos) return;

    const formData = new FormData(formFotos);
    const csrf = Utils.getCsrfToken();
    const token = Utils.getAccessToken();

    try {
        const headers = new Headers();
        if (csrf) headers.set("X-CSRFToken", csrf);
        if (token) headers.set("Authorization", `Bearer ${token}`);

        const response = await fetch(`/api/taller/ordenes/${encodeURIComponent(idOrden)}/fotos`, {
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
// 11. EVENTOS DE TABLA
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

function onModalEstadoClick(event) {
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
            closeModal("modal-ordenes-estado");
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

    const estadoParamMap = {
        pendiente: "Pendiente",
        asignada: "Asignada",
        revisada: "Revisado,Revisada,En revisión,En revision",
        reparada: "Reparado",
    };

    const estadoParam = estadoParamMap[estado] || estado;

    console.log(`[DEBUG] Buscando órdenes ${label} con estado: ${estadoParam}`);

    Utils.fetchJson(`${CONFIG.API.ORDENES}?estado=${encodeURIComponent(estadoParam)}`)
        .then((data) => {
            console.log(`[DEBUG] Órdenes ${label} encontradas:`, data.ordenes);
            if (data.ordenes && data.ordenes.length > 0) {
                renderModalOrdenesEstado(label, data.ordenes);
            } else {
                renderModalOrdenesEstado(label, []);
            }
            openModal("modal-ordenes-estado");
        })
        .catch((error) => {
            console.error(`Error cargando órdenes ${estado}:`, error);
            const { modalOrdenesEstadoSubtitle } = getDomElements();
            if (modalOrdenesEstadoSubtitle) {
                modalOrdenesEstadoSubtitle.textContent = "No se pudo cargar la información.";
            }
            Utils.showMessage(`Error al cargar órdenes ${label}: ${error.message}`, true);
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
        const fechaActual = Utils.getFechaActual();
        inputFecha.value = fechaActual;
        inputFecha.min = fechaActual;
        inputFecha.max = fechaActual;
        inputFecha.readOnly = true;
        inputFecha.style.backgroundColor = 'var(--input-bg)';
        inputFecha.style.cursor = 'not-allowed';
        inputFecha.style.opacity = '0.7';
    }

    // Evento para inicializar FieldValidator
    if (window.FieldValidator) {
        setTimeout(() => window.FieldValidator.init(), 100);
    }

    // Validación de IMEI
    const inputImei = document.getElementById("orden-id-equipo");
    if (inputImei) {
        inputImei.addEventListener("input", (e) => {
            e.target.value = e.target.value.replace(/[^0-9]/g, "").slice(0, 15);
        });
    }

    // Validación de cédula
    const inputCedula = document.getElementById("cliente-cedula");
    if (inputCedula) {
        inputCedula.addEventListener("input", (e) => {
            e.target.value = e.target.value.replace(/[^0-9]/g, "").slice(0, 8);
        });
    }

    // Validación de patrón
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

    // Validación de celular
    const inputCelular = document.getElementById("cliente-celular");
    if (inputCelular) {
        inputCelular.addEventListener("input", (e) => {
            let value = e.target.value.replace(/[^0-9]/g, "").slice(0, 11);
            e.target.value = value;
        });
        
        inputCelular.addEventListener("blur", (e) => {
            const value = e.target.value;
            if (value && !Utils.validarCelular(value)) {
                e.target.style.borderColor = '#dc2626';
                e.target.title = 'Debe comenzar con: 0412, 0414, 0416, 0422, 0424 o 0426, seguido de 7 dígitos';
            } else {
                e.target.style.borderColor = '';
                e.target.title = '';
            }
        });
    }

    // Validación de clave (sin espacios)
    const inputClave = document.getElementById("orden-clave");
    if (inputClave) {
        inputClave.addEventListener("input", (e) => {
            e.target.value = e.target.value.replace(/\s/g, "").slice(0, 30);
        });
    }

    // Validación de color (solo letras)
    const inputColor = document.getElementById("orden-color");
    if (inputColor) {
        inputColor.addEventListener("input", (e) => {
            let value = e.target.value.replace(/[^a-zA-ZáéíóúñÁÉÍÓÚÑ\s]/g, "");
            if (value.length > 15) {
                value = value.slice(0, 15);
            }
            e.target.value = value;
        });
    }

    // Validación de nombre (solo letras, capitalizar)
    const inputNombre = document.getElementById("cliente-nombre");
    if (inputNombre) {
        inputNombre.addEventListener("input", (e) => {
            let value = e.target.value.replace(/[^a-zA-ZáéíóúñÁÉÍÓÚÑ\s]/g, "");
            if (value.length > 20) {
                value = value.slice(0, 20);
            }
            const palabras = value.split(' ');
            value = palabras.map(p => p.charAt(0).toUpperCase() + p.slice(1).toLowerCase()).join(' ');
            e.target.value = value;
        });
    }

    // Validación de apellido (solo letras, capitalizar)
    const inputApellido = document.getElementById("cliente-apellido");
    if (inputApellido) {
        inputApellido.addEventListener("input", (e) => {
            let value = e.target.value.replace(/[^a-zA-ZáéíóúñÁÉÍÓÚÑ\s]/g, "");
            if (value.length > 20) {
                value = value.slice(0, 20);
            }
            const palabras = value.split(' ');
            value = palabras.map(p => p.charAt(0).toUpperCase() + p.slice(1).toLowerCase()).join(' ');
            e.target.value = value;
        });
    }

    // Validación de dirección
    const inputDireccion = document.getElementById("cliente-direccion");
    if (inputDireccion) {
        inputDireccion.addEventListener("input", (e) => {
            if (e.target.value.length > 50) {
                e.target.value = e.target.value.slice(0, 50);
            }
        });
    }

    // Validación de modelo custom
    const inputModeloCustom = document.getElementById("orden-modelo-custom");
    if (inputModeloCustom) {
        inputModeloCustom.addEventListener("input", (e) => {
            let value = e.target.value.replace(/[^a-zA-Z0-9\s\-]/g, "");
            if (value.length > 30) {
                value = value.slice(0, 30);
            }
            e.target.value = value;
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

    const modalEstadoBody = document.getElementById('modal-ordenes-estado-body');
    if (modalEstadoBody) {
        modalEstadoBody.addEventListener('click', onModalEstadoClick);
    }

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
            inputFecha.value = Utils.getFechaActual();
        }
        // Resetear estado de cliente
        clienteActualId = null;
        setClienteStatus("");
        const { btnCrearCliente } = getDomElements();
        if (btnCrearCliente) btnCrearCliente.hidden = true;
    });

    Promise.all([
        cargarModelos(),
        cargarTecnicos(),
        cargarOrdenes(),
    ]).catch((error) => {
        console.error("Error en la inicialización:", error);
    });
});