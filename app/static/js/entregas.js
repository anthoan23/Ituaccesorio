(() => {
    "use strict";

    let personalPendienteEliminar = null;

    function getAuthToken() {
        return localStorage.getItem("access_token") || sessionStorage.getItem("access_token") || "";
    }

    function getCsrfToken() {
        return document.querySelector("input[name='_csrf_token']")?.value || "";
    }

    async function fetchJson(url, options = {}) {
        const authToken = getAuthToken();
        const csrfToken = getCsrfToken();

        const headers = {
            "Accept": "application/json",
            ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
            ...(authToken ? { "Authorization": `Bearer ${authToken}` } : {})
        };

        if (options.body && !(options.body instanceof FormData)) {
            headers["Content-Type"] = "application/json";
        }

        const response = await fetch(url, {
            headers,
            credentials: "same-origin",
            method: options.method || "GET",
            body: options.body,
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok || data.success === false) {
            throw new Error(data.error || `Error ${response.status}`);
        }

        return data;
    }

    function mostrarToast(mensaje, tipo = "success") {
        const toastExistente = document.querySelector(".custom-toast");
        if (toastExistente) toastExistente.remove();

        const toast = document.createElement("div");
        toast.className = `custom-toast custom-toast--${tipo}`;
        toast.textContent = mensaje;
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: ${tipo === "error" ? "#ef4444" : "#22c55e"};
            color: white;
            padding: 12px 24px;
            border-radius: 40px;
            z-index: 10000;
            font-size: 14px;
            font-weight: 600;
            font-family: 'Space Grotesk', sans-serif;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transition = "opacity 0.3s";
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function formatDate(dateString) {
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

    // ==================== PERSONAL DELIVERY ====================

    async function cargarPersonal() {
        try {
            const data = await fetchJson("/api/personal-delivery");
            renderPersonalList(data.personal || []);
        } catch (err) {
            mostrarToast(err.message, "error");
        }
    }

    function renderPersonalList(personal) {
        const tbody = document.getElementById("tabla-personal");
        if (!tbody) return;

        if (!personal.length) {
            tbody.innerHTML = '<tr><td colspan="3">No hay personal de delivery registrado</td></tr>';
            return;
        }

        tbody.innerHTML = personal.map(p => `
            <tr>
                <td>${escapeHtml(p.cedula)}</td>
                <td>${escapeHtml(p.nombre_completo)}</td>
                <td class="table__actions">
                    <div class="row-actions">
                        <button class="icon-action btn-editar-personal" data-cedula="${escapeHtml(p.cedula)}" data-nombre="${escapeHtml(p.nombre)}" data-apellido="${escapeHtml(p.apellido)}" title="Editar">✎</button>
                        <button class="icon-action btn-eliminar-personal" data-cedula="${escapeHtml(p.cedula)}" data-nombre="${escapeHtml(p.nombre_completo)}" title="Eliminar">🗑</button>
                    </div>
                </td>
            </tr>
        `).join("");

        // Event listeners
        document.querySelectorAll(".btn-editar-personal").forEach(btn => {
            btn.addEventListener("click", () => {
                document.getElementById("personal-cedula-original").value = btn.dataset.cedula;
                document.getElementById("personal-cedula").value = btn.dataset.cedula;
                document.getElementById("personal-nombre").value = btn.dataset.nombre;
                document.getElementById("personal-apellido").value = btn.dataset.apellido;
                document.getElementById("personal-cedula").disabled = true;
                document.querySelector("#modal-personal .ui-modal__title").textContent = "Editar Delivery";
                openModal("modal-personal");
            });
        });

        document.querySelectorAll(".btn-eliminar-personal").forEach(btn => {
            btn.addEventListener("click", () => {
                personalPendienteEliminar = { cedula: btn.dataset.cedula, nombre: btn.dataset.nombre };
                document.getElementById("texto-confirmar-eliminar-personal").textContent = `¿Estás seguro de que quieres eliminar a ${btn.dataset.nombre}?`;
                openModal("modal-eliminar-personal");
            });
        });
    }

    async function guardarPersonal(event) {
        event.preventDefault();
        
        const cedula = document.getElementById("personal-cedula").value.trim();
        const nombre = document.getElementById("personal-nombre").value.trim();
        const apellido = document.getElementById("personal-apellido").value.trim();
        const cedulaOriginal = document.getElementById("personal-cedula-original").value;

        if (!cedula || !nombre || !apellido) {
            mostrarToast("Todos los campos son obligatorios", "error");
            return;
        }

        try {
            if (cedulaOriginal) {
                // Actualizar
                await fetchJson(`/api/personal-delivery/${cedulaOriginal}`, {
                    method: "PUT",
                    body: JSON.stringify({ nombre, apellido })
                });
                mostrarToast("Delivery actualizado correctamente", "success");
            } else {
                // Crear
                await fetchJson("/api/personal-delivery", {
                    method: "POST",
                    body: JSON.stringify({ cedula, nombre, apellido })
                });
                mostrarToast("Delivery registrado correctamente", "success");
            }
            
            closeModal("modal-personal");
            document.getElementById("form-personal").reset();
            document.getElementById("personal-cedula").disabled = false;
            document.querySelector("#modal-personal .ui-modal__title").textContent = "Registrar Delivery";
            await cargarPersonal();
        } catch (err) {
            mostrarToast(err.message, "error");
        }
    }

    async function eliminarPersonal() {
        if (!personalPendienteEliminar) return;

        try {
            await fetchJson(`/api/personal-delivery/${personalPendienteEliminar.cedula}`, { method: "DELETE" });
            mostrarToast("Delivery eliminado correctamente", "success");
            closeModal("modal-eliminar-personal");
            personalPendienteEliminar = null;
            await cargarPersonal();
        } catch (err) {
            mostrarToast(err.message, "error");
        }
    }

    // ==================== ENTREGAS ====================

    async function cargarEntregas() {
        try {
            const data = await fetchJson("/api/entregas");
            renderEntregasList(data.entregas || []);
        } catch (err) {
            mostrarToast(err.message, "error");
        }
    }

    function renderEntregasList(entregas) {
        const container = document.getElementById("entregas-list");
        if (!container) return;

        if (!entregas.length) {
            container.innerHTML = '<div class="empty-state">📭 No hay entregas registradas</div>';
            return;
        }

        container.innerHTML = entregas.map(e => `
            <div class="entrega-card">
                <div class="entrega-header">
                    <span class="entrega-id">📦 Entrega: ${escapeHtml(e.id_entrega)}</span>
                    <span class="entrega-estado estado-${e.estado}">${escapeHtml(e.estado_texto)}</span>
                </div>
                <div class="entrega-info-grid">
                    <div class="info-row">
                        <strong>📄 Factura</strong>
                        <span>${escapeHtml(e.factura_id)}</span>
                    </div>
                    <div class="info-row">
                        <strong>👤 Delivery</strong>
                        <span>${escapeHtml(e.delivery_nombre_completo || "No asignado")}</span>
                    </div>
                    <div class="info-row">
                        <strong>📅 Fecha de entrega</strong>
                        <span>${formatDate(e.fecha_entrega)}</span>
                    </div>
                    <div class="info-row">
                        <strong>📍 Dirección</strong>
                        <span>${escapeHtml(e.direccion || "No especificada")}</span>
                    </div>
                    <div class="info-row">
                        <strong>👤 Cliente</strong>
                        <span>${escapeHtml(e.cliente_nombre)} ${escapeHtml(e.cliente_apellido || "")}</span>
                    </div>
                    <div class="info-row">
                        <strong>📞 Teléfono</strong>
                        <span>${escapeHtml(e.cliente_celular || "N/A")}</span>
                    </div>
                </div>
                <div class="entrega-actions">
                    <button class="btn btn--ghost btn-ver-entrega" data-id="${escapeHtml(e.id_entrega)}">👁️ Ver detalle</button>
                    <button class="btn btn--yellow btn-cambiar-estado" data-id="${escapeHtml(e.id_entrega)}" data-estado="${e.estado}">🔄 Cambiar estado</button>
                </div>
            </div>
        `).join("");

        document.querySelectorAll(".btn-ver-entrega").forEach(btn => {
            btn.addEventListener("click", () => verDetalleEntrega(btn.dataset.id));
        });

        document.querySelectorAll(".btn-cambiar-estado").forEach(btn => {
            btn.addEventListener("click", () => abrirModalEstado(btn.dataset.id, btn.dataset.estado));
        });
    }

    async function verDetalleEntrega(entregaId) {
        try {
            const data = await fetchJson(`/api/entregas/${entregaId}`);
            const e = data.entrega;
            
            document.getElementById("detalle-id").textContent = e.id_entrega;
            document.getElementById("detalle-factura").textContent = e.factura_id;
            document.getElementById("detalle-estado").textContent = e.estado_texto;
            document.getElementById("detalle-fecha").textContent = formatDate(e.fecha_entrega);
            document.getElementById("detalle-direccion").textContent = e.direccion || "No especificada";
            document.getElementById("detalle-delivery").textContent = e.delivery_nombre_completo || "No asignado";
            document.getElementById("detalle-cliente").textContent = `${e.cliente_nombre || ""} ${e.cliente_apellido || ""}`.trim() || "N/A";
            document.getElementById("detalle-cliente-tel").textContent = e.cliente_celular || "N/A";
            
            openModal("modal-detalle-entrega");
        } catch (err) {
            mostrarToast(err.message, "error");
        }
    }

    function abrirModalEstado(entregaId, estadoActual) {
        document.getElementById("estado-entrega-id").value = entregaId;
        document.getElementById("estado-nuevo").value = estadoActual;
        openModal("modal-estado-entrega");
    }

    async function actualizarEstadoEntrega() {
        const entregaId = document.getElementById("estado-entrega-id").value;
        const nuevoEstado = document.getElementById("estado-nuevo").value;

        try {
            await fetchJson(`/api/entregas/${entregaId}/estado`, {
                method: "PUT",
                body: JSON.stringify({ estado: parseInt(nuevoEstado) })
            });
            mostrarToast("Estado actualizado correctamente", "success");
            closeModal("modal-estado-entrega");
            await cargarEntregas();
        } catch (err) {
            mostrarToast(err.message, "error");
        }
    }

    // ==================== REGISTRAR ENTREGA ====================

    async function cargarFacturasPendientes() {
        try {
            const data = await fetchJson("/api/entregas/facturas-pendientes");
            const select = document.getElementById("entrega-factura");
            const facturas = data.facturas || [];
            
            select.innerHTML = '<option value="">Seleccione una factura</option>' + 
                facturas.map(f => `<option value="${escapeHtml(f.factura_id)}" data-direccion="${escapeHtml(f.cliente_direccion || "")}" data-cliente="${escapeHtml(f.cliente_nombre)} ${escapeHtml(f.cliente_apellido || "")}" data-telefono="${escapeHtml(f.cliente_celular || "")}">${escapeHtml(f.factura_id)} - ${escapeHtml(f.cliente_nombre)} ${escapeHtml(f.cliente_apellido || "")}</option>`).join("");
            
            select.addEventListener("change", () => {
                const option = select.options[select.selectedIndex];
                const direccion = option.dataset.direccion;
                if (direccion) {
                    document.getElementById("entrega-direccion").value = direccion;
                }
            });
        } catch (err) {
            mostrarToast(err.message, "error");
        }
    }

    async function cargarPersonalParaSelect() {
        try {
            const data = await fetchJson("/api/personal-delivery");
            const select = document.getElementById("entrega-delivery");
            const personal = data.personal || [];
            
            select.innerHTML = '<option value="">Seleccione un delivery</option>' + 
                personal.map(p => `<option value="${escapeHtml(p.cedula)}">${escapeHtml(p.nombre_completo)} (${escapeHtml(p.cedula)})</option>`).join("");
        } catch (err) {
            mostrarToast(err.message, "error");
        }
    }

    async function registrarEntrega(event) {
        event.preventDefault();
        
        const facturaId = document.getElementById("entrega-factura").value;
        const cedulaDelivery = document.getElementById("entrega-delivery").value;
        const direccion = document.getElementById("entrega-direccion").value.trim();
        const estado = parseInt(document.getElementById("entrega-estado").value);

        if (!facturaId || !cedulaDelivery || !direccion) {
            mostrarToast("Todos los campos son obligatorios", "error");
            return;
        }

        try {
            await fetchJson("/api/entregas", {
                method: "POST",
                body: JSON.stringify({ factura_id: facturaId, cedula_delivery: cedulaDelivery, direccion, estado })
            });
            mostrarToast("Entrega registrada correctamente", "success");
            closeModal("modal-entrega");
            document.getElementById("form-entrega").reset();
            await Promise.all([cargarEntregas(), cargarFacturasPendientes()]);
        } catch (err) {
            mostrarToast(err.message, "error");
        }
    }

    // ==================== MODALES ====================

    function openModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.classList.remove("is-hidden");
            document.body.style.overflow = "hidden";
        }
    }

    function closeModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.classList.add("is-hidden");
            document.body.style.overflow = "";
        }
    }

    // ==================== TABS ====================

    function initTabs() {
        const tabBtns = document.querySelectorAll(".tab-btn");
        for (const btn of tabBtns) {
            btn.addEventListener("click", () => {
                for (const b of tabBtns) b.classList.remove("active");
                btn.classList.add("active");

                const tab = btn.dataset.tab;
                document.querySelectorAll(".tab-content").forEach(c => c.classList.add("is-hidden"));
                document.getElementById(`${tab}-tab`).classList.remove("is-hidden");

                if (tab === "entregas") cargarEntregas();
                else if (tab === "personal") cargarPersonal();
            });
        }
    }

    // ==================== INICIALIZACIÓN ====================

    async function init() {
        initTabs();
        
        // Formularios
        document.getElementById("form-personal")?.addEventListener("submit", guardarPersonal);
        document.getElementById("form-entrega")?.addEventListener("submit", registrarEntrega);
        document.getElementById("btn-actualizar-estado")?.addEventListener("click", actualizarEstadoEntrega);
        document.getElementById("btn-confirmar-eliminar-personal")?.addEventListener("click", eliminarPersonal);
        
        // Botones
        document.getElementById("btn-nuevo-personal")?.addEventListener("click", () => {
            document.getElementById("form-personal").reset();
            document.getElementById("personal-cedula").disabled = false;
            document.getElementById("personal-cedula-original").value = "";
            document.querySelector("#modal-personal .ui-modal__title").textContent = "Registrar Delivery";
            openModal("modal-personal");
        });
        
        document.getElementById("btn-nueva-entrega")?.addEventListener("click", async () => {
            await Promise.all([cargarFacturasPendientes(), cargarPersonalParaSelect()]);
            document.getElementById("form-entrega").reset();
            openModal("modal-entrega");
        });
        
        // Cerrar modales con ESC
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") {
                document.querySelectorAll(".modal:not(.is-hidden)").forEach(modal => {
                    modal.classList.add("is-hidden");
                    document.body.style.overflow = "";
                });
            }
        });
        
        // Cargar datos iniciales
        await cargarEntregas();
        await cargarPersonal();
    }
    
    document.addEventListener("DOMContentLoaded", init);
})();