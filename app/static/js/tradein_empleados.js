// ============================================
// ICONOS (consistentes con módulo de empleados)
// ============================================
const Iconos = {
  lapiz: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="18" height="18"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25Zm18-11.5a1 1 0 0 0 0-1.41l-1.34-1.34a1 1 0 0 0-1.41 0l-1.12 1.12 3.75 3.75L21 5.75Z" fill="currentColor"/></svg>`,
  basura: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="18" height="18"><path d="M6 7h12l-1 14H7L6 7Zm3-3h6l1 2H8l1-2Z" fill="currentColor"/></svg>`,
  ojo: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="18" height="18"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" fill="currentColor"/></svg>`,
  herramientas: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="18" height="18"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z" fill="currentColor"/></svg>`
};

(() => {
    "use strict";

    let tradeinActual = null;
    let catalogoTests = [];

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

        let body = options.body;
        if (body && !(body instanceof FormData) && !(body instanceof URLSearchParams)) {
            headers["Content-Type"] = "application/json";
            body = JSON.stringify(body);
        }

        const response = await fetch(url, {
            headers,
            credentials: "same-origin",
            method: options.method || "GET",
            body: body,
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
        if (value === null || value === undefined) return "$0.00";
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

    // ==================== ESTADÍSTICAS ====================
    async function cargarEstadisticas() {
        try {
            const data = await fetchJson("/api/tradein/estadisticas");
            const stats = data.estadisticas;
            
            document.getElementById("stat-total").textContent = stats.total || 0;
            document.getElementById("stat-valor-total").textContent = formatCurrency(stats.valor_total || 0);
            document.getElementById("stat-equipos").textContent = stats.equipos || 0;
        } catch (err) {
            console.error("Error cargando estadísticas:", err);
            document.getElementById("stat-total").textContent = "0";
            document.getElementById("stat-valor-total").textContent = "$0.00";
            document.getElementById("stat-equipos").textContent = "0";
        }
    }

    // ==================== LISTAR TRADE-INS ====================
    async function cargarTradeIns() {
        const tbody = document.getElementById("tradein-list");
        
        try {
            const data = await fetchJson("/api/tradein");
            const tradeins = data.tradeins || [];
            
            if (tradeins.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" class="table__empty">📭 No hay trade-ins registrados</td>' + '</tr>';
                return;
            }
            
            tbody.innerHTML = tradeins.map(trade => `
                <tr data-id="${trade.id}">
                    <td><span class="chip">${escapeHtml(trade.id)}</span></td>
                    <td>${formatDate(trade.fecha)}</td>
                    <td>
                        <strong>${escapeHtml(trade.cliente_nombre)} ${escapeHtml(trade.cliente_apellido || "")}</strong>
                        ${trade.cliente_celular ? `<br><small style="color: #6d7480;">${escapeHtml(trade.cliente_celular)}</small>` : ''}
                    </td>
                    <td><strong>${escapeHtml(trade.producto_nombre || "N/A")}</strong></td>
                    <td>${escapeHtml(trade.marca || "N/A")}</td>
                    <td><strong style="color: #121418;">${formatCurrency(trade.valor_pagado || 0)}</strong></td>
                    <td>
                        ${trade.tests && trade.tests.length > 0 ? 
                            `<span class="badge badge--success">✅ ${trade.tests.length} pruebas</span>` : 
                            `<span class="badge badge--warning">⏳ Sin pruebas</span>`}
                    </td>
                    <td class="table__actions">
                        <div class="row-actions" aria-label="Acciones del trade-in">
                            <button class="icon-action icon-action--view" type="button" data-action="ver" data-id="${trade.id}" title="Ver detalle">
                                ${Iconos.ojo}
                            </button>
                            ${(!trade.tests || trade.tests.length === 0) ? 
                                `<button class="icon-action icon-action--tests" type="button" data-action="tests" data-id="${trade.id}" title="Realizar pruebas">
                                    ${Iconos.herramientas}
                                </button>` : ''}
                            <button class="icon-action icon-action--danger" type="button" data-action="eliminar" data-id="${trade.id}" title="Eliminar">
                                ${Iconos.basura}
                            </button>
                        </div>
                    </td>
                 </tr>
            `).join("");
            
            document.querySelectorAll('.icon-action[data-action="ver"]').forEach(btn => {
                btn.removeEventListener('click', handleVerClick);
                btn.addEventListener('click', handleVerClick);
            });
            
            document.querySelectorAll('.icon-action[data-action="tests"]').forEach(btn => {
                btn.removeEventListener('click', handleTestsClick);
                btn.addEventListener('click', handleTestsClick);
            });
            
            document.querySelectorAll('.icon-action[data-action="eliminar"]').forEach(btn => {
                btn.removeEventListener('click', handleEliminarClick);
                btn.addEventListener('click', handleEliminarClick);
            });
            
        } catch (err) {
            console.error("Error cargando trade-ins:", err);
            tbody.innerHTML = '<tr><td colspan="8" class="table__empty">❌ Error al cargar los datos</td>' + '</tr>';
        }
    }

    function handleVerClick(e) {
        const btn = e.currentTarget;
        const id = btn.getAttribute('data-id');
        if (id) mostrarDetalle(id);
    }

    function handleTestsClick(e) {
        const btn = e.currentTarget;
        const id = btn.getAttribute('data-id');
        if (id) abrirModalTests(id);
    }

    function handleEliminarClick(e) {
        const btn = e.currentTarget;
        const id = btn.getAttribute('data-id');
        if (id) eliminarTradeIn(id);
    }

    // ==================== REGISTRAR NUEVO TRADE-IN ====================
    async function cargarProductos() {
        try {
            const data = await fetchJson("/api/tradein/productos");
            const select = document.getElementById("producto-id");
            if (!select) return;
            
            select.innerHTML = '<option value="">Seleccionar iPhone...</option>';
            
            const productos = data.productos || [];
            const iPhones = productos.filter(producto => {
                const marca = (producto.marca || "").toLowerCase();
                const nombre = (producto.nombre || "").toLowerCase();
                return marca === 'apple' || marca === 'iphone' || nombre.includes('iphone');
            });
            
            if (iPhones.length === 0) {
                select.innerHTML += '<option value="" disabled>⚠️ No hay iPhones disponibles para trade-in</option>';
                return;
            }
            
            iPhones.forEach(producto => {
                const marcaTexto = producto.marca ? ` (${escapeHtml(producto.marca)})` : '';
                const nombreCompleto = `${escapeHtml(producto.nombre)}${marcaTexto}`;
                select.innerHTML += `<option value="${producto.id}">📱 ${nombreCompleto}</option>`;
            });
            
        } catch (err) {
            console.error("Error cargando productos:", err);
            const select = document.getElementById("producto-id");
            if (select) {
                select.innerHTML = '<option value="">❌ Error al cargar productos</option>';
            }
        }
    }

    // Búsqueda de clientes
    let busquedaTimeout;
    const clienteSearch = document.getElementById("cliente-search-input");
    const clienteResults = document.getElementById("cliente-results");
    const clienteIdInput = document.getElementById("cliente-id");

    if (clienteSearch) {
        clienteSearch.addEventListener("input", () => {
            clearTimeout(busquedaTimeout);
            const q = clienteSearch.value.trim();
            
            if (q.length < 2) {
                clienteResults.classList.add("is-hidden");
                return;
            }
            
            busquedaTimeout = setTimeout(async () => {
                try {
                    const data = await fetchJson(`/api/tradein/clientes?q=${encodeURIComponent(q)}`);
                    const clientes = data.clientes || [];
                    
                    if (clientes.length === 0) {
                        clienteResults.innerHTML = '<div class="search-result-item">No se encontraron clientes</div>';
                    } else {
                        clienteResults.innerHTML = clientes.map(cliente => `
                            <div class="search-result-item" data-id="${cliente.id}" data-nombre="${escapeHtml(cliente.nombre_completo)}" data-celular="${escapeHtml(cliente.celular || '')}">
                                <strong>${escapeHtml(cliente.nombre_completo)}</strong>
                                <small>📞 ${escapeHtml(cliente.celular || 'Sin teléfono')} · 🆔 ${cliente.id}</small>
                            </div>
                        `).join("");
                        
                        document.querySelectorAll(".search-result-item").forEach(item => {
                            item.addEventListener("click", () => {
                                clienteIdInput.value = item.dataset.id;
                                clienteSearch.value = item.dataset.nombre;
                                clienteResults.classList.add("is-hidden");
                            });
                        });
                    }
                    clienteResults.classList.remove("is-hidden");
                } catch (err) {
                    console.error("Error buscando clientes:", err);
                }
            }, 300);
        });
        
        document.addEventListener("click", (e) => {
            if (clienteSearch && !clienteSearch.contains(e.target) && clienteResults && !clienteResults.contains(e.target)) {
                clienteResults.classList.add("is-hidden");
            }
        });
    }

    // Preview de fotos
    const fotosInput = document.getElementById("fotos");
    const fotosPreview = document.getElementById("fotos-preview");
    
    if (fotosInput && fotosPreview) {
        fotosInput.addEventListener("change", () => {
            fotosPreview.innerHTML = "";
            Array.from(fotosInput.files).forEach((file, index) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const preview = document.createElement("div");
                    preview.className = "foto-preview";
                    preview.innerHTML = `<img src="${e.target.result}" alt="Preview"><button type="button" class="remove-foto" data-index="${index}">×</button>`;
                    preview.querySelector(".remove-foto")?.addEventListener("click", () => {
                        preview.remove();
                    });
                    fotosPreview.appendChild(preview);
                };
                reader.readAsDataURL(file);
            });
        });
    }

    // Enviar formulario de registro
    const formRegistrar = document.getElementById("form-registrar-tradein");
    if (formRegistrar) {
        formRegistrar.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const clienteId = document.getElementById("cliente-id")?.value;
            if (!clienteId) {
                mostrarToast("Debe seleccionar un cliente válido", "error");
                return;
            }
            
            const productoId = document.getElementById("producto-id")?.value;
            if (!productoId) {
                mostrarToast("Debe seleccionar un iPhone válido", "error");
                return;
            }
            
            const idEquipo = document.getElementById("id_equipo")?.value;
            if (!idEquipo) {
                mostrarToast("Debe ingresar el IMEI/ID del equipo", "error");
                return;
            }
            
            const valorPagado = document.getElementById("valor-pagado")?.value;
            if (!valorPagado || Number(valorPagado) <= 0) {
                mostrarToast("Debe ingresar un valor pagado válido", "error");
                return;
            }
            
            // Verificar si el equipo ya existe
            try {
                const checkResponse = await fetch(`/api/tradein/verificar-equipo/${encodeURIComponent(idEquipo)}`, {
                    headers: { "Authorization": `Bearer ${getAuthToken()}` }
                });
                const checkData = await checkResponse.json();
                if (checkData.exists) {
                    if (!confirm(`⚠️ El equipo con ID "${idEquipo}" ya está registrado en el sistema.\n\nProducto: ${checkData.equipo?.producto_nombre || 'N/A'}\nColor: ${checkData.equipo?.Color || 'N/A'}\nCapacidad: ${checkData.equipo?.Capacidad || 'N/A'}\n\n¿Desea continuar y reutilizar este equipo?`)) {
                        return;
                    }
                }
            } catch (err) {
                console.log("Equipo nuevo o error:", err);
            }
            
            const formData = new FormData(formRegistrar);
            
            const btnSubmit = formRegistrar.querySelector('button[type="submit"]');
            const textoOriginal = btnSubmit.textContent;
            btnSubmit.disabled = true;
            btnSubmit.textContent = "Registrando...";
            
            try {
                const response = await fetch("/api/tradein", {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${getAuthToken()}`
                    },
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    mostrarToast(data.message || "Trade-in registrado correctamente");
                    cerrarModal("modal-registrar");
                    formRegistrar.reset();
                    if (fotosPreview) fotosPreview.innerHTML = "";
                    if (clienteIdInput) clienteIdInput.value = "";
                    if (clienteSearch) clienteSearch.value = "";
                    await cargarEstadisticas();
                    await cargarTradeIns();
                } else {
                    mostrarToast(data.error || "Error al registrar", "error");
                }
            } catch (err) {
                mostrarToast(err.message || "Error de conexión", "error");
            } finally {
                btnSubmit.disabled = false;
                btnSubmit.textContent = textoOriginal;
            }
        });
    }

    // ==================== TESTS ====================
    async function cargarCatalogoTests() {
        try {
            const data = await fetchJson("/api/tradein/catalogo-tests");
            catalogoTests = data.tests || [];
        } catch (err) {
            console.error("Error cargando catálogo de tests:", err);
            catalogoTests = [];
        }
    }

    async function abrirModalTests(tradeinId) {
        try {
            const data = await fetchJson(`/api/tradein/${tradeinId}/detalle`);
            const detalle = data.detalle || {};
            tradeinActual = tradeinId;
            
            const infoContainer = document.getElementById("tests-equipo-info");
            if (infoContainer) {
                infoContainer.innerHTML = `
                    <div class="equipo-info-card">
                        <strong>📱 ${escapeHtml(detalle.producto_nombre || "N/A")}</strong>
                        ${detalle.marca ? `<span>🏷️ ${escapeHtml(detalle.marca)}</span>` : ''}
                        ${detalle.imei ? `<span>🔢 IMEI: ${escapeHtml(detalle.imei)}</span>` : ''}
                        <span>👤 ${escapeHtml(detalle.cliente_nombre)} ${escapeHtml(detalle.cliente_apellido || "")}</span>
                    </div>
                `;
            }
            
            const container = document.getElementById("tests-container");
            if (!container) return;
            
            const testsPorCategoria = {};
            
            catalogoTests.forEach(test => {
                if (!testsPorCategoria[test.categoria]) {
                    testsPorCategoria[test.categoria] = [];
                }
                testsPorCategoria[test.categoria].push(test);
            });
            
            let html = "";
            for (const [categoria, tests] of Object.entries(testsPorCategoria)) {
                html += `
                    <div class="test-categoria">
                        <h4>${escapeHtml(categoria)}</h4>
                        <div class="test-items">
                            ${tests.map(test => {
                                const safeName = test.nombre.replace(/[^a-zA-Z0-9]/g, '_');
                                return `
                                <div class="test-item">
                                    <span class="test-nombre">${escapeHtml(test.nombre)}</span>
                                    <div class="test-resultados">
                                        <label><input type="radio" name="test_${safeName}" value="Funciona"> ✅ Funciona</label>
                                        <label><input type="radio" name="test_${safeName}" value="No funciona"> ❌ No funciona</label>
                                    </div>
                                </div>
                            `}).join("")}
                        </div>
                    </div>
                `;
            }
            container.innerHTML = html || '<p style="text-align:center; padding:2rem;">No hay pruebas configuradas</p>';
            
            abrirModal("modal-tests");
            
        } catch (err) {
            mostrarToast(err.message || "Error al cargar datos del trade-in", "error");
        }
    }

    async function guardarTests() {
        if (!tradeinActual) return;
        
        const tests = [];
        document.querySelectorAll("#tests-container .test-item").forEach(item => {
            const nombre = item.querySelector(".test-nombre")?.textContent || "";
            const seleccionado = item.querySelector('input[type="radio"]:checked');
            const resultado = seleccionado ? seleccionado.value : "Dañado";
            tests.push({ nombre, resultado });
        });
        
        if (tests.length === 0) {
            mostrarToast("No hay pruebas para registrar", "error");
            return;
        }
        
        const btnGuardar = document.getElementById("btn-guardar-tests");
        if (!btnGuardar) return;
        
        const textoOriginal = btnGuardar.textContent;
        btnGuardar.disabled = true;
        btnGuardar.textContent = "Guardando...";
        
        try {
            const data = await fetchJson(`/api/tradein/${tradeinActual}/tests`, {
                method: "POST",
                body: { tests }
            });
            
            if (data.success) {
                mostrarToast(data.message || "Pruebas registradas correctamente");
                cerrarModal("modal-tests");
                await cargarTradeIns();
            } else {
                mostrarToast(data.error || "Error al registrar pruebas", "error");
            }
        } catch (err) {
            mostrarToast(err.message || "Error de conexión", "error");
        } finally {
            btnGuardar.disabled = false;
            btnGuardar.textContent = textoOriginal;
        }
    }

    // ==================== DETALLE ====================
    async function mostrarDetalle(tradeinId) {
        try {
            const data = await fetchJson(`/api/tradein/${tradeinId}/detalle`);
            const detalle = data.detalle || {};
            const tests = data.tests || [];
            const fotos = data.fotos || [];
            
            const contenido = document.getElementById("detalle-contenido");
            if (!contenido) return;
            
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
                                    <span class="test-nombre">${escapeHtml(test.nombre)}</span>
                                    <span class="test-resultado ${test.resultado === "Funciona" ? "funciona" : "no-funciona"}">
                                        ${test.resultado === "Funciona" ? "✅" : "❌"} ${escapeHtml(test.resultado || "Sin resultado")}
                                    </span>
                                </div>
                            `).join("")}
                        </div>
                    </div>
                `;
            }
            
            contenido.innerHTML = `
                <div class="detalle-section">
                    <h4>📋 Información del trade-in</h4>
                    <div class="detalle-grid">
                        <div class="detalle-item">
                            <strong>ID Trade-in</strong>
                            <span>#${escapeHtml(detalle.id || "N/A")}</span>
                        </div>
                        <div class="detalle-item">
                            <strong>Fecha</strong>
                            <span>${formatDate(detalle.fecha)}</span>
                        </div>
                        <div class="detalle-item">
                            <strong>Valor pagado</strong>
                            <span style="font-size:1.2rem; font-weight:900; color:#f3c500;">${formatCurrency(detalle.valor_pagado || 0)}</span>
                        </div>
                    </div>
                </div>
                
                <div class="detalle-section">
                    <h4>📱 Información del equipo</h4>
                    <div class="detalle-grid">
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
                            <span>${escapeHtml(detalle.imei || "N/A")}</span>
                        </div>
                        ${detalle.Clave ? `
                        <div class="detalle-item">
                            <strong>Clave numérica</strong>
                            <span>${escapeHtml(detalle.Clave)}</span>
                        </div>
                        ` : ""}
                        ${detalle.Patron ? `
                        <div class="detalle-item">
                            <strong>Patrón</strong>
                            <span>${escapeHtml(detalle.Patron)}</span>
                        </div>
                        ` : ""}
                        ${detalle.observaciones ? `
                        <div class="detalle-item">
                            <strong>Observaciones</strong>
                            <span>${escapeHtml(detalle.observaciones)}</span>
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
            `;
            
            abrirModal("modal-detalle");
            
        } catch (err) {
            mostrarToast(err.message || "Error al cargar el detalle", "error");
        }
    }

    // ==================== ELIMINAR ====================
    async function eliminarTradeIn(tradeinId) {
        if (!confirm("⚠️ ¿Estás seguro de que deseas eliminar este trade-in?\n\nEsta acción no se puede deshacer.")) return;
        
        try {
            const data = await fetchJson(`/api/tradein/${tradeinId}`, {
                method: "DELETE"
            });
            
            if (data.success) {
                mostrarToast("Trade-in eliminado correctamente");
                await cargarEstadisticas();
                await cargarTradeIns();
            } else {
                mostrarToast(data.error || "Error al eliminar", "error");
            }
        } catch (err) {
            mostrarToast(err.message || "Error de conexión", "error");
        }
    }

    // ==================== MODALES ====================
    function abrirModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.classList.remove("is-hidden");
            document.body.classList.add("modal-open");
        }
    }

    function cerrarModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.classList.add("is-hidden");
            document.body.classList.remove("modal-open");
        }
    }

    function initModales() {
        document.querySelectorAll("[data-close-modal], .modal__close, .modal__backdrop").forEach(el => {
            el.addEventListener("click", (e) => {
                const modal = el.closest(".modal");
                if (modal) {
                    modal.classList.add("is-hidden");
                    document.body.classList.remove("modal-open");
                }
            });
        });
        
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") {
                document.querySelectorAll(".modal:not(.is-hidden)").forEach(modal => {
                    modal.classList.add("is-hidden");
                    document.body.classList.remove("modal-open");
                });
            }
        });
    }

    // ==================== INICIALIZACIÓN ====================
    async function init() {
        initModales();
        await cargarCatalogoTests();
        await cargarProductos();
        await cargarEstadisticas();
        await cargarTradeIns();
        
        const btnNuevo = document.getElementById("btn-nuevo-tradein");
        if (btnNuevo) {
            btnNuevo.addEventListener("click", () => {
                const form = document.getElementById("form-registrar-tradein");
                if (form) form.reset();
                const preview = document.getElementById("fotos-preview");
                if (preview) preview.innerHTML = "";
                const clienteId = document.getElementById("cliente-id");
                if (clienteId) clienteId.value = "";
                const clienteSearchInput = document.getElementById("cliente-search-input");
                if (clienteSearchInput) clienteSearchInput.value = "";
                abrirModal("modal-registrar");
            });
        }
        
        const btnGuardarTests = document.getElementById("btn-guardar-tests");
        if (btnGuardarTests) {
            btnGuardarTests.addEventListener("click", guardarTests);
        }
    }
    
    document.addEventListener("DOMContentLoaded", init);
})();