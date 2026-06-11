(() => {
    "use strict";

    let tradeinActual = null;
    let catalogoFallas = [];

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
            Accept: "application/json",
            ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
            ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
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

    function formatDate(dateString) {
        if (!dateString) return "N/A";
        try {
            const date = new Date(dateString);
            return date.toLocaleString("es-ES", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
            });
        } catch {
            return dateString;
        }
    }

    function formatCurrency(value) {
        return `$${Number(value).toFixed(2)}`;
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

    async function cargarEstadisticas() {
        try {
            const data = await fetchJson("/api/tradein/estadisticas");
            const stats = data.estadisticas;
            
            document.getElementById("stat-total").textContent = stats.total || 0;
            document.getElementById("stat-pendientes").textContent = stats.pendientes || 0;
            document.getElementById("stat-evaluados").textContent = stats.evaluados || 0;
            document.getElementById("stat-valor-total").textContent = formatCurrency(stats.valor_total || 0);
        } catch (err) {
            console.error("Error cargando estadísticas:", err);
        }
    }

    async function cargarCatalogoFallas() {
        try {
            const data = await fetchJson("/api/tradein/catalogo-fallas");
            catalogoFallas = data.fallas || [];
        } catch (err) {
            console.error("Error cargando catálogo de fallas:", err);
            catalogoFallas = [];
        }
    }

    function renderFallasCheckboxes() {
        const container = document.getElementById("fallas-checkboxes");
        if (!container) return;
        
        container.innerHTML = catalogoFallas.map(falla => `
            <label class="falla-checkbox">
                <input type="checkbox" value="${escapeHtml(falla.id)}" data-nombre="${escapeHtml(falla.nombre)}">
                <span>${escapeHtml(falla.nombre)}</span>
                <small style="color:#888;">(-${formatCurrency(falla.deduccion_base)})</small>
            </label>
        `).join("");
    }

    async function cargarTradeIns(tipo) {
        const url = tipo === "pendientes" ? "/api/tradein/pendientes" : "/api/tradein/evaluados";
        const container = document.getElementById(`${tipo}-list`);
        
        if (!container) return;
        
        try {
            const data = await fetchJson(url);
            const tradeins = data.tradeins || [];
            
            if (tradeins.length === 0) {
                container.innerHTML = '<div class="empty-state">📭 No hay trade-ins en esta lista</div>';
                return;
            }
            
            container.innerHTML = tradeins.map(trade => `
                <div class="tradein-card" data-id="${trade.id}">
                    <div class="tradein-header-card">
                        <span class="tradein-id">🔁 Trade-in: ${escapeHtml(trade.id)}</span>
                        <span class="tradein-estado ${trade.estado}">${trade.estado === "pendiente" ? "⏳ Pendiente" : "✅ Evaluado"}</span>
                    </div>
                    
                    <div class="tradein-info-grid">
                        <div class="info-row">
                            <strong>📱 Equipo</strong>
                            <span>${escapeHtml(trade.producto_nombre || "N/A")}</span>
                        </div>
                        <div class="info-row">
                            <strong>🏷️ Marca</strong>
                            <span>${escapeHtml(trade.marca || "N/A")}</span>
                        </div>
                        <div class="info-row">
                            <strong>📦 Clase</strong>
                            <span>${escapeHtml(trade.clase || "N/A")}</span>
                        </div>
                        <div class="info-row">
                            <strong>🎨 Color</strong>
                            <span>${escapeHtml(trade.Color || "N/A")}</span>
                        </div>
                        <div class="info-row">
                            <strong>💾 Capacidad</strong>
                            <span>${escapeHtml(trade.Capacidad || "N/A")}</span>
                        </div>
                        <div class="info-row">
                            <strong>🔢 IMEI</strong>
                            <span>${escapeHtml(trade.IMEI || "N/A")}</span>
                        </div>
                        <div class="info-row">
                            <strong>👤 Cliente</strong>
                            <span>${escapeHtml(trade.cliente_nombre)} ${escapeHtml(trade.cliente_apellido || "")}</span>
                        </div>
                        <div class="info-row">
                            <strong>📞 Teléfono</strong>
                            <span>${escapeHtml(trade.cliente_celular || "N/A")}</span>
                        </div>
                        <div class="info-row">
                            <strong>📅 Fecha de registro</strong>
                            <span>${formatDate(trade.fecha)}</span>
                        </div>
                        ${trade.cotizacion ? `
                        <div class="info-row">
                            <strong>💰 Cotización</strong>
                            <span>${formatCurrency(trade.cotizacion)}</span>
                        </div>
                        ` : ""}
                    </div>
                    
                    <div class="tradein-actions">
                        <button class="btn btn--ghost btn-ver-detalle" data-id="${trade.id}">📋 Ver detalle</button>
                        ${trade.estado === "pendiente" ? `
                        <button class="btn btn--yellow btn-evaluar" data-id="${trade.id}">📝 Evaluar</button>
                        ` : ""}
                    </div>
                </div>
            `).join("");
            
            // Event listeners para botones
            document.querySelectorAll(".btn-ver-detalle").forEach(btn => {
                btn.addEventListener("click", () => mostrarDetalle(btn.dataset.id));
            });
            
            document.querySelectorAll(".btn-evaluar").forEach(btn => {
                btn.addEventListener("click", () => mostrarModalEvaluacion(btn.dataset.id));
            });
            
        } catch (err) {
            console.error(`Error cargando trade-ins ${tipo}:`, err);
            container.innerHTML = '<div class="empty-state">❌ Error al cargar los datos</div>';
        }
    }

    async function mostrarDetalle(tradeinId) {
        try {
            const data = await fetchJson(`/api/tradein/${tradeinId}/detalle`);
            const detalle = data.detalle || {};
            const tests = data.tests || [];
            const fotos = data.fotos || [];
            
            const modal = document.getElementById("modal-detalle");
            const contenido = document.getElementById("detalle-contenido");
            
            let fotosHtml = "";
            if (fotos.length > 0) {
                fotosHtml = `
                    <div class="detalle-section">
                        <h4>📸 Fotos del equipo</h4>
                        <div class="fotos-grid">
                            ${fotos.map(foto => `
                                <div class="foto-item">
                                    <img src="${escapeHtml(foto.url)}" alt="Foto del equipo" onclick="window.open('${escapeHtml(foto.url)}', '_blank')">
                                </div>
                            `).join("")}
                        </div>
                    </div>
                `;
            }
            
            let testsHtml = "";
            if (tests.length > 0) {
                testsHtml = `
                    <div class="detalle-section">
                        <h4>🔧 Pruebas realizadas</h4>
                        <div class="tests-list">
                            ${tests.map(test => `
                                <div class="test-item">
                                    <span class="test-nombre">${escapeHtml(test.Nombre_test)}</span>
                                    <span class="test-resultado ${test.Resultado_test === "Funciona" ? "funciona" : "no-funciona"}">
                                        ${escapeHtml(test.Resultado_test || "Sin resultado")}
                                    </span>
                                </div>
                            `).join("")}
                        </div>
                    </div>
                `;
            }
            
            contenido.innerHTML = `
                <div class="detalle-section">
                    <h4>📋 Información del equipo</h4>
                    <div class="detalle-grid">
                        <div class="detalle-item">
                            <strong>ID Trade-in</strong>
                            <span>${escapeHtml(detalle.id || "N/A")}</span>
                        </div>
                        <div class="detalle-item">
                            <strong>Producto</strong>
                            <span>${escapeHtml(detalle.producto_nombre || "N/A")}</span>
                        </div>
                        <div class="detalle-item">
                            <strong>Marca</strong>
                            <span>${escapeHtml(detalle.marca || "N/A")}</span>
                        </div>
                        <div class="detalle-item">
                            <strong>Clase</strong>
                            <span>${escapeHtml(detalle.clase || "N/A")}</span>
                        </div>
                        <div class="detalle-item">
                            <strong>Color</strong>
                            <span>${escapeHtml(detalle.Color || "N/A")}</span>
                        </div>
                        <div class="detalle-item">
                            <strong>Capacidad</strong>
                            <span>${escapeHtml(detalle.Capacidad || "N/A")}</span>
                        </div>
                        <div class="detalle-item">
                            <strong>IMEI</strong>
                            <span>${escapeHtml(detalle.IMEI || "N/A")}</span>
                        </div>
                        ${detalle.Clave ? `
                        <div class="detalle-item">
                            <strong>Clave</strong>
                            <span>${escapeHtml(detalle.Clave)}</span>
                        </div>
                        ` : ""}
                    </div>
                </div>
                
                <div class="detalle-section">
                    <h4>👤 Información del cliente</h4>
                    <div class="detalle-grid">
                        <div class="detalle-item">
                            <strong>Nombre</strong>
                            <span>${escapeHtml(detalle.cliente_nombre)} ${escapeHtml(detalle.cliente_apellido || "")}</span>
                        </div>
                        <div class="detalle-item">
                            <strong>Teléfono</strong>
                            <span>${escapeHtml(detalle.cliente_celular || "N/A")}</span>
                        </div>
                        <div class="detalle-item">
                            <strong>Correo</strong>
                            <span>${escapeHtml(detalle.cliente_correo || "N/A")}</span>
                        </div>
                        <div class="detalle-item">
                            <strong>Dirección</strong>
                            <span>${escapeHtml(detalle.cliente_direccion || "N/A")}</span>
                        </div>
                    </div>
                </div>
                
                ${testsHtml}
                ${fotosHtml}
                
                ${detalle.cotizacion ? `
                <div class="detalle-section">
                    <h4>💰 Cotización</h4>
                    <div class="detalle-grid">
                        <div class="detalle-item">
                            <strong>Valor</strong>
                            <span style="font-size:1.2rem; color:var(--yellow);">${formatCurrency(detalle.cotizacion)}</span>
                        </div>
                    </div>
                </div>
                ` : ""}
            `;
            
            modal.classList.remove("is-hidden");
            
        } catch (err) {
            mostrarToast(err.message, "error");
        }
    }

    async function mostrarModalEvaluacion(tradeinId) {
        try {
            const data = await fetchJson(`/api/tradein/${tradeinId}/detalle`);
            const detalle = data.detalle || {};
            tradeinActual = tradeinId;
            
            const infoContainer = document.getElementById("evaluacion-info");
            infoContainer.innerHTML = `
                <div class="detalle-grid">
                    <div class="detalle-item">
                        <strong>Equipo</strong>
                        <span>${escapeHtml(detalle.producto_nombre || "N/A")}</span>
                    </div>
                    <div class="detalle-item">
                        <strong>Marca</strong>
                        <span>${escapeHtml(detalle.marca || "N/A")}</span>
                    </div>
                    <div class="detalle-item">
                        <strong>Cliente</strong>
                        <span>${escapeHtml(detalle.cliente_nombre)} ${escapeHtml(detalle.cliente_apellido || "")}</span>
                    </div>
                </div>
            `;
            
            // Limpiar checkboxes
            document.querySelectorAll("#fallas-checkboxes input").forEach(cb => cb.checked = false);
            document.getElementById("evaluacion-observaciones").value = "";
            document.getElementById("evaluacion-valor").value = "";
            
            const modal = document.getElementById("modal-evaluacion");
            modal.classList.remove("is-hidden");
            
        } catch (err) {
            mostrarToast(err.message, "error");
        }
    }

    async function confirmarEvaluacion() {
        if (!tradeinActual) return;
        
        const valor = document.getElementById("evaluacion-valor").value;
        if (!valor || parseFloat(valor) < 0) {
            mostrarToast("Ingrese un valor válido para la cotización", "error");
            return;
        }
        
        const fallasSeleccionadas = Array.from(document.querySelectorAll("#fallas-checkboxes input:checked"))
            .map(cb => cb.getAttribute("data-nombre") || cb.value);
        
        const observaciones = document.getElementById("evaluacion-observaciones").value;
        
        const btnConfirmar = document.getElementById("confirmar-evaluacion");
        const textoOriginal = btnConfirmar.textContent;
        btnConfirmar.disabled = true;
        btnConfirmar.textContent = "Procesando...";
        
        try {
            await fetchJson(`/api/tradein/evaluar/${tradeinActual}`, {
                method: "POST",
                body: JSON.stringify({
                    valor: parseFloat(valor),
                    fallas: fallasSeleccionadas,
                    observaciones: observaciones
                })
            });
            
            mostrarToast(`Trade-in evaluado correctamente por ${formatCurrency(parseFloat(valor))}`);
            cerrarModalEvaluacion();
            
            // Recargar datos
            await Promise.all([
                cargarEstadisticas(),
                cargarTradeIns("pendientes"),
                cargarTradeIns("evaluados")
            ]);
            
        } catch (err) {
            mostrarToast(err.message, "error");
        } finally {
            btnConfirmar.disabled = false;
            btnConfirmar.textContent = textoOriginal;
        }
    }

    function cerrarModalEvaluacion() {
        const modal = document.getElementById("modal-evaluacion");
        modal.classList.add("is-hidden");
        tradeinActual = null;
    }

    function cerrarModalDetalle() {
        const modal = document.getElementById("modal-detalle");
        modal.classList.add("is-hidden");
    }

    function initTabs() {
        const tabBtns = document.querySelectorAll(".tab-btn");
        
        tabBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                tabBtns.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                
                const tab = btn.dataset.tab;
                
                document.querySelectorAll(".tab-content").forEach(content => {
                    content.classList.add("is-hidden");
                });
                
                const tabContent = document.getElementById(`${tab}-tab`);
                if (tabContent) tabContent.classList.remove("is-hidden");
                
                if (tab === "pendientes") cargarTradeIns("pendientes");
                else if (tab === "evaluados") cargarTradeIns("evaluados");
            });
        });
    }

    async function init() {
        await cargarCatalogoFallas();
        renderFallasCheckboxes();
        initTabs();
        
        document.getElementById("cancelar-evaluacion")?.addEventListener("click", cerrarModalEvaluacion);
        document.getElementById("confirmar-evaluacion")?.addEventListener("click", confirmarEvaluacion);
        document.getElementById("close-modal")?.addEventListener("click", cerrarModalEvaluacion);
        document.getElementById("close-detalle")?.addEventListener("click", cerrarModalDetalle);
        
        // Cerrar modal al hacer clic fuera
        document.getElementById("modal-evaluacion")?.addEventListener("click", (e) => {
            if (e.target === document.getElementById("modal-evaluacion")) cerrarModalEvaluacion();
        });
        
        document.getElementById("modal-detalle")?.addEventListener("click", (e) => {
            if (e.target === document.getElementById("modal-detalle")) cerrarModalDetalle();
        });
        
        await cargarEstadisticas();
        await cargarTradeIns("pendientes");
    }
    
    document.addEventListener("DOMContentLoaded", init);
})();