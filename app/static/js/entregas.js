// ============================================
// 1. CONSTANTES Y CONFIGURACIÓN
// ============================================
const CONFIG = {
    API: {
        ENTREGAS: '/api/entregas',
        PERSONAL: '/api/personal-delivery',
        FACTURAS_PENDIENTES: '/api/facturas-pendientes'
    }
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
        return localStorage.getItem("access_token") || sessionStorage.getItem("access_token") || "";
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
            const msg = (isJson && payload && (payload.message || payload.error)) ||
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
            .replace(/'/g, "&#39;");
    },

    mostrarToast(message, isError = false) {
        const toast = document.getElementById("toast");
        if (!toast) return;
        toast.textContent = message;
        toast.classList.toggle("toast--error", isError);
        toast.classList.add("is-visible");
        setTimeout(() => {
            toast.classList.remove("is-visible");
        }, 3000);
    },

    formatDate(dateString) {
        if (!dateString) return "N/A";
        try {
            const date = new Date(dateString);
            return date.toLocaleString("es-ES", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit"
            });
        } catch {
            return dateString;
        }
    }
};

// ============================================
// 3. MANEJADORES DE MODALES Y TABS
// ============================================
let activeTabKey = "entregas";

const modals = {
    entrega: document.getElementById("modal-entrega"),
    personal: document.getElementById("modal-personal"),
    eliminar: document.getElementById("modal-eliminar"),
};

const tabButtons = Array.from(document.querySelectorAll("[data-table-tab]"));
const tabPanels = Array.from(document.querySelectorAll("[data-table-panel]"));

function setActiveTab(key) {
    activeTabKey = key;

    tabButtons.forEach(btn => {
        const isActive = btn.dataset.tableTab === key;
        btn.setAttribute("aria-selected", isActive ? "true" : "false");
        btn.classList.toggle("is-active", isActive);
    });

    tabPanels.forEach(panel => {
        panel.hidden = panel.dataset.tablePanel !== key;
    });
}

function openModal(modalId) {
    const modal = modals[modalId];
    if (modal) {
        modal.hidden = false;
        document.body.classList.add("modal-open");
    }
}

function closeModal(modalId) {
    const modal = modals[modalId];
    if (modal) {
        modal.hidden = true;
        document.body.classList.remove("modal-open");
    }
}

function closeAllModals() {
    Object.keys(modals).forEach(key => {
        if (modals[key]) modals[key].hidden = true;
    });
    document.body.classList.remove("modal-open");
}

// ============================================
// 4. MANEJADORES DE TABLA
// ============================================
let entregaPendienteEliminar = null;
let personalPendienteEliminar = null;

function renderizarTablaEntregas(entregas) {
    const tbody = document.getElementById("tabla-entregas");
    if (!tbody) return;

    const stats = document.getElementById("stat-entregas");
    if (stats) stats.textContent = entregas.length;

    if (!entregas.length) {
        tbody.innerHTML = `<tr><td colspan="7">No hay entregas registradas</td></tr>`;
        return;
    }

    tbody.innerHTML = entregas.map(e => `
        <tr>
            <td><span class="chip">${Utils.escapeHtml(e.id)}</span></td>
            <td>${Utils.escapeHtml(e.factura_id)}</td>
            <td>${Utils.escapeHtml(e.delivery_nombre_completo || "No asignado")}</td>
            <td><span class="estado-badge ${e.estado_clase}">${Utils.escapeHtml(e.estado_texto)}</span></td>
            <td>${Utils.escapeHtml(e.direccion || "No especificada")}</td>
            <td>${Utils.formatDate(e.fecha_entrega)}</td>
            <td class="table__actions">
                <div class="row-actions">
                    <button class="icon-action" data-action="editar-entrega" data-id="${Utils.escapeHtml(e.id)}" 
                        data-factura="${Utils.escapeHtml(e.factura_id)}" data-cedula="${Utils.escapeHtml(e.cedula_delivery)}"
                        data-direccion="${Utils.escapeHtml(e.direccion || '')}" data-estado="${e.estado}" title="Editar">✎</button>
                    <button class="icon-action icon-action--danger" data-action="eliminar-entrega" data-id="${Utils.escapeHtml(e.id)}" 
                        title="Eliminar">🗑</button>
                </div>
            </td>
        </tr>
    `).join("");
}

function renderizarTablaPersonal(personal) {
    const tbody = document.getElementById("tabla-personal");
    if (!tbody) return;

    const stats = document.getElementById("stat-personal");
    if (stats) stats.textContent = personal.length;

    if (!personal.length) {
        tbody.innerHTML = `<tr><td colspan="3">No hay personal de delivery registrado</td></tr>`;
        return;
    }

    tbody.innerHTML = personal.map(p => `
        <tr>
            <td><span class="chip">${Utils.escapeHtml(p.cedula)}</span></td>
            <td>${Utils.escapeHtml(p.nombre_completo)}</td>
            <td class="table__actions">
                <div class="row-actions">
                    <button class="icon-action" data-action="editar-personal" data-cedula="${Utils.escapeHtml(p.cedula)}" 
                        data-nombre="${Utils.escapeHtml(p.nombre)}" data-apellido="${Utils.escapeHtml(p.apellido)}" title="Editar">✎</button>
                    <button class="icon-action icon-action--danger" data-action="eliminar-personal" data-cedula="${Utils.escapeHtml(p.cedula)}" 
                        data-nombre="${Utils.escapeHtml(p.nombre_completo)}" title="Eliminar">🗑</button>
                </div>
            </td>
        </tr>
    `).join("");
}

// ============================================
// 5. CRUD DE ENTREGAS
// ============================================
async function cargarEntregas() {
    try {
        const data = await Utils.fetchJson(CONFIG.API.ENTREGAS, { method: "GET" });
        renderizarTablaEntregas(data.entregas || []);
    } catch (error) {
        Utils.mostrarToast(error.message, true);
    }
}

async function cargarFacturasPendientes() {
    try {
        const data = await Utils.fetchJson(CONFIG.API.FACTURAS_PENDIENTES, { method: "GET" });
        const select = document.getElementById("factura-id");
        const facturas = data.facturas || [];
        
        const statPendientes = document.getElementById("stat-pendientes");
        if (statPendientes) statPendientes.textContent = facturas.length;
        
        select.innerHTML = '<option value="">Seleccione una factura</option>' +
            facturas.map(f => `<option value="${Utils.escapeHtml(f.factura_id)}" data-direccion="${Utils.escapeHtml(f.cliente_direccion || '')}">${Utils.escapeHtml(f.factura_id)} - ${Utils.escapeHtml(f.cliente_nombre)} ${Utils.escapeHtml(f.cliente_apellido || '')}</option>`).join("");
        
        select.addEventListener("change", () => {
            const option = select.options[select.selectedIndex];
            const direccion = option.dataset.direccion;
            const direccionTextarea = document.querySelector("#form-entrega textarea[name='direccion']");
            if (direccion && direccionTextarea) {
                direccionTextarea.value = direccion;
            }
        });
    } catch (error) {
        Utils.mostrarToast(error.message, true);
    }
}

async function cargarPersonalSelect() {
    try {
        const data = await Utils.fetchJson(CONFIG.API.PERSONAL, { method: "GET" });
        const select = document.getElementById("delivery-cedula");
        const personal = data.personal || [];
        
        select.innerHTML = '<option value="">Seleccione un delivery</option>' +
            personal.map(p => `<option value="${Utils.escapeHtml(p.cedula)}">${Utils.escapeHtml(p.nombre_completo)} (${Utils.escapeHtml(p.cedula)})</option>`).join("");
    } catch (error) {
        Utils.mostrarToast(error.message, true);
    }
}

async function registrarEntrega(event) {
    event.preventDefault();
    const form = document.getElementById("form-entrega");
    const id = form.querySelector("input[name='id']").value;
    
    const payload = {
        factura_id: form.factura_id.value,
        cedula_delivery: form.cedula_delivery.value,
        direccion: form.direccion.value.trim(),
        estado: parseInt(form.estado.value)
    };
    
    if (!payload.factura_id || !payload.cedula_delivery || !payload.direccion) {
        Utils.mostrarToast("Todos los campos son obligatorios", true);
        return;
    }
    
    try {
        if (id) {
            await Utils.fetchJson(`${CONFIG.API.ENTREGAS}/${id}`, {
                method: "PUT",
                body: JSON.stringify(payload)
            });
            Utils.mostrarToast("Entrega actualizada exitosamente");
        } else {
            await Utils.fetchJson(CONFIG.API.ENTREGAS, {
                method: "POST",
                body: JSON.stringify(payload)
            });
            Utils.mostrarToast("Entrega registrada exitosamente");
        }
        form.reset();
        closeModal("entrega");
        await Promise.all([cargarEntregas(), cargarFacturasPendientes()]);
    } catch (error) {
        Utils.mostrarToast(error.message, true);
    }
}

function abrirModalEditarEntrega(button) {
    const id = button.dataset.id;
    const factura = button.dataset.factura;
    const cedula = button.dataset.cedula;
    const direccion = button.dataset.direccion;
    const estado = button.dataset.estado;
    
    const form = document.getElementById("form-entrega");
    const title = document.getElementById("modal-entrega-title");
    
    form.querySelector("input[name='id']").value = id;
    form.factura_id.value = factura;
    form.cedula_delivery.value = cedula;
    form.direccion.value = direccion;
    form.estado.value = estado;
    
    if (title) title.textContent = "Editar entrega";
    openModal("entrega");
}

async function eliminarEntrega() {
    if (!entregaPendienteEliminar) return;
    
    try {
        await Utils.fetchJson(`${CONFIG.API.ENTREGAS}/${entregaPendienteEliminar}`, { method: "DELETE" });
        Utils.mostrarToast("Entrega eliminada exitosamente");
        closeModal("eliminar");
        entregaPendienteEliminar = null;
        await cargarEntregas();
    } catch (error) {
        Utils.mostrarToast(error.message, true);
    }
}

// ============================================
// 6. CRUD DE PERSONAL DELIVERY
// ============================================
async function cargarPersonal() {
    try {
        const data = await Utils.fetchJson(CONFIG.API.PERSONAL, { method: "GET" });
        renderizarTablaPersonal(data.personal || []);
    } catch (error) {
        Utils.mostrarToast(error.message, true);
    }
}

function abrirModalEditarPersonal(button) {
    const cedula = button.dataset.cedula;
    const nombre = button.dataset.nombre;
    const apellido = button.dataset.apellido;
    
    const form = document.getElementById("form-personal");
    const title = document.getElementById("modal-personal-title");
    
    form.querySelector("input[name='cedula_original']").value = cedula;
    form.cedula.value = cedula;
    form.nombre.value = nombre;
    form.apellido.value = apellido;
    form.cedula.disabled = true;
    
    if (title) title.textContent = "Editar delivery";
    openModal("personal");
}

function resetFormPersonal() {
    const form = document.getElementById("form-personal");
    const title = document.getElementById("modal-personal-title");
    
    form.reset();
    form.cedula.disabled = false;
    form.querySelector("input[name='cedula_original']").value = "";
    if (title) title.textContent = "Registrar delivery";
}

async function registrarPersonal(event) {
    event.preventDefault();
    const form = document.getElementById("form-personal");
    const cedulaOriginal = form.querySelector("input[name='cedula_original']").value;
    
    const payload = {
        cedula: form.cedula.value,
        nombre: form.nombre.value.trim(),
        apellido: form.apellido.value.trim()
    };
    
    if (!payload.cedula || !payload.nombre || !payload.apellido) {
        Utils.mostrarToast("Todos los campos son obligatorios", true);
        return;
    }
    
    if (!/^\d+$/.test(payload.cedula)) {
        Utils.mostrarToast("La cédula debe contener solo números", true);
        return;
    }
    
    try {
        if (cedulaOriginal) {
            await Utils.fetchJson(`${CONFIG.API.PERSONAL}/${cedulaOriginal}`, {
                method: "PUT",
                body: JSON.stringify(payload)
            });
            Utils.mostrarToast("Delivery actualizado exitosamente");
        } else {
            await Utils.fetchJson(CONFIG.API.PERSONAL, {
                method: "POST",
                body: JSON.stringify(payload)
            });
            Utils.mostrarToast("Delivery registrado exitosamente");
        }
        resetFormPersonal();
        closeModal("personal");
        await Promise.all([cargarPersonal(), cargarPersonalSelect()]);
    } catch (error) {
        Utils.mostrarToast(error.message, true);
    }
}

async function eliminarPersonal() {
    if (!personalPendienteEliminar) return;
    
    try {
        await Utils.fetchJson(`${CONFIG.API.PERSONAL}/${personalPendienteEliminar}`, { method: "DELETE" });
        Utils.mostrarToast("Delivery eliminado exitosamente");
        closeModal("eliminar");
        personalPendienteEliminar = null;
        await Promise.all([cargarPersonal(), cargarPersonalSelect()]);
    } catch (error) {
        Utils.mostrarToast(error.message, true);
    }
}

// ============================================
// 7. FILTROS Y BÚSQUEDA
// ============================================
function setupFiltros() {
    // Filtros para entregas
    const inputBuscar = document.getElementById("input-buscar-entregas");
    const filtroEstado = document.getElementById("filtro-estado");
    
    const filtrarEntregas = () => {
        const busqueda = inputBuscar?.value.toLowerCase() || "";
        const estado = filtroEstado?.value || "";
        
        const rows = document.querySelectorAll("#tabla-entregas tr");
        rows.forEach(row => {
            if (row.cells.length < 7) return;
            const text = Array.from(row.cells).slice(0, 4).map(cell => cell.textContent.toLowerCase()).join(" ");
            const estadoCell = row.cells[3]?.textContent.toLowerCase() || "";
            
            let estadoMatch = true;
            if (estado) {
                const estadoMap = { "0": "pendiente", "1": "camino", "2": "entregado", "3": "cancelado", "4": "programado" };
                estadoMatch = estadoCell.includes(estadoMap[estado] || "");
            }
            
            const searchMatch = !busqueda || text.includes(busqueda);
            row.style.display = (estadoMatch && searchMatch) ? "" : "none";
        });
    };
    
    inputBuscar?.addEventListener("input", filtrarEntregas);
    filtroEstado?.addEventListener("change", filtrarEntregas);
    
    // Filtro para personal
    const inputBuscarPersonal = document.getElementById("input-buscar-personal");
    
    const filtrarPersonal = () => {
        const busqueda = inputBuscarPersonal?.value.toLowerCase() || "";
        
        const rows = document.querySelectorAll("#tabla-personal tr");
        rows.forEach(row => {
            if (row.cells.length < 2) return;
            const text = row.cells[0]?.textContent.toLowerCase() + " " + row.cells[1]?.textContent.toLowerCase();
            row.style.display = !busqueda || text.includes(busqueda) ? "" : "none";
        });
    };
    
    inputBuscarPersonal?.addEventListener("input", filtrarPersonal);
}

// ============================================
// 8. EVENTOS E INICIALIZACIÓN
// ============================================
function setupEventos() {
    // Configurar tabs
    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const key = btn.dataset.tableTab;
            if (key) setActiveTab(key);
        });
    });
    
    // Botón nueva entrega
    document.getElementById("btn-nueva-entrega")?.addEventListener("click", async () => {
        const form = document.getElementById("form-entrega");
        const title = document.getElementById("modal-entrega-title");
        
        form.reset();
        form.querySelector("input[name='id']").value = "";
        if (title) title.textContent = "Registrar entrega";
        
        await Promise.all([cargarFacturasPendientes(), cargarPersonalSelect()]);
        openModal("entrega");
    });
    
    // Botón nuevo personal
    document.getElementById("btn-nuevo-personal")?.addEventListener("click", () => {
        resetFormPersonal();
        openModal("personal");
    });
    
    // Eventos de la tabla de entregas
    document.getElementById("tabla-entregas")?.addEventListener("click", (e) => {
        const btn = e.target.closest("[data-action]");
        if (!btn) return;
        
        const action = btn.dataset.action;
        if (action === "editar-entrega") {
            abrirModalEditarEntrega(btn);
        } else if (action === "eliminar-entrega") {
            entregaPendienteEliminar = btn.dataset.id;
            const confirmMessage = document.getElementById("confirmar-mensaje");
            if (confirmMessage) confirmMessage.textContent = "¿Estás seguro de que quieres eliminar esta entrega?";
            openModal("eliminar");
        }
    });
    
    // Eventos de la tabla de personal
    document.getElementById("tabla-personal")?.addEventListener("click", (e) => {
        const btn = e.target.closest("[data-action]");
        if (!btn) return;
        
        const action = btn.dataset.action;
        if (action === "editar-personal") {
            abrirModalEditarPersonal(btn);
        } else if (action === "eliminar-personal") {
            personalPendienteEliminar = btn.dataset.cedula;
            const confirmMessage = document.getElementById("confirmar-mensaje");
            if (confirmMessage) confirmMessage.textContent = `¿Estás seguro de que quieres eliminar a ${btn.dataset.nombre}?`;
            openModal("eliminar");
        }
    });
    
    // Formularios
    document.getElementById("form-entrega")?.addEventListener("submit", registrarEntrega);
    document.getElementById("form-personal")?.addEventListener("submit", registrarPersonal);
    
    // Botón confirmar eliminar
    document.getElementById("btn-confirmar-eliminar")?.addEventListener("click", () => {
        if (entregaPendienteEliminar) eliminarEntrega();
        else if (personalPendienteEliminar) eliminarPersonal();
    });
    
    // Botones de reset
    document.querySelectorAll("[data-reset-form]").forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.dataset.resetForm;
            if (target === "entrega") {
                document.getElementById("form-entrega")?.reset();
            } else if (target === "personal") {
                resetFormPersonal();
            }
        });
    });
    
    // Cerrar modales con backdrop
    document.querySelectorAll("[data-modal-close]").forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.dataset.modalClose;
            if (target && modals[target]) {
                closeModal(target);
            } else {
                closeAllModals();
            }
        });
    });
    
    // Cerrar modales con ESC
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            closeAllModals();
        }
    });
}

async function init() {
    setActiveTab("entregas");
    await Promise.all([cargarEntregas(), cargarPersonal(), cargarFacturasPendientes(), cargarPersonalSelect()]);
    setupFiltros();
    setupEventos();
}

document.addEventListener("DOMContentLoaded", init);