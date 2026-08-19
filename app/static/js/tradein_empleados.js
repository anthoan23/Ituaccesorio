// ============================================
// ICONOS (consistentes con módulo de empleados)
// ============================================
const Iconos = {
  lapiz: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="18" height="18"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25Zm18-11.5a1 1 0 0 0 0-1.41l-1.34-1.34a1 1 0 0 0-1.41 0l-1.12 1.12 3.75 3.75L21 5.75Z" fill="currentColor"/></svg>`,
  basura: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="18" height="18"><path d="M6 7h12l-1 14H7L6 7Zm3-3h6l1 2H8l1-2Z" fill="currentColor"/></svg>`,
  ojo: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="18" height="18"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" fill="currentColor"/></svg>`,
  herramientas: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="18" height="18"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z" fill="currentColor"/></svg>`,
  recargar: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="18" height="18"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z" fill="currentColor"/></svg>`
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

    // ==================== ABRIR/CERRAR MODALES ====================
    function abrirModal(id) {
        if (window.UiModal && typeof window.UiModal.openById === 'function') {
            window.UiModal.openById(id);
        }
    }

    function cerrarModal(id) {
        if (window.UiModal && typeof window.UiModal.closeById === 'function') {
            window.UiModal.closeById(id);
        }
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
                tbody.innerHTML = '<tr><td colspan="8" class="table__empty">📭 No hay trade-ins registrados</td></tr>';
                return;
            }
            
            tbody.innerHTML = tradeins.map(trade => `
                <tr data-id="${trade.id}">
                    <td><span class="chip">${escapeHtml(trade.id)}</span></td>
                    <td>${formatDate(trade.fecha)}</td>
                    <td>
                        <strong>${escapeHtml(trade.cliente_nombre)} ${escapeHtml(trade.cliente_apellido || "")}</strong>
                        ${trade.cliente_celular ? `<br><small class="texto-muted">${escapeHtml(trade.cliente_celular)}</small>` : ''}
                    </td>
                    <td><strong>${escapeHtml(trade.producto_nombre || "N/A")}</strong></td>
                    <td>${escapeHtml(trade.marca || "N/A")}</td>
                    <td><strong class="texto-yellow">${formatCurrency(trade.valor_pagado || 0)}</strong></td>
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
                            <button class="icon-action icon-action--edit" type="button" data-action="editar" data-id="${trade.id}" title="Editar">
                                ${Iconos.lapiz}
                            </button>
                            <button class="icon-action icon-action--danger" type="button" data-action="eliminar" data-id="${trade.id}" title="Eliminar">
                                ${Iconos.basura}
                            </button>
                        </div>
                    </td>
                 </tr>
            `).join("");
            
            // Event listeners
            document.querySelectorAll('.icon-action[data-action="ver"]').forEach(btn => {
                btn.removeEventListener('click', handleVerClick);
                btn.addEventListener('click', handleVerClick);
            });
            
            document.querySelectorAll('.icon-action[data-action="editar"]').forEach(btn => {
                btn.removeEventListener('click', handleEditarClick);
                btn.addEventListener('click', handleEditarClick);
            });
            
            document.querySelectorAll('.icon-action[data-action="eliminar"]').forEach(btn => {
                btn.removeEventListener('click', handleEliminarClick);
                btn.addEventListener('click', handleEliminarClick);
            });
            
        } catch (err) {
            console.error("Error cargando trade-ins:", err);
            tbody.innerHTML = '<tr><td colspan="8" class="table__empty">❌ Error al cargar los datos</td></tr>';
        }
    }

    function handleVerClick(e) {
        const btn = e.currentTarget;
        const id = btn.getAttribute('data-id');
        if (id) mostrarDetalle(id);
    }

    function handleEditarClick(e) {
        const btn = e.currentTarget;
        const id = btn.getAttribute('data-id');
        if (id) abrirModalEditar(id);
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

    // ==================== CARGAR TESTS EN FORMULARIO ====================
    function cargarTestsEnFormulario(testsExistentes = []) {
    const container = document.getElementById("tests-container-registro");
    if (!container) return;
    
    const testsPorCategoria = {};
    catalogoTests.forEach(test => {
        if (!testsPorCategoria[test.categoria]) {
            testsPorCategoria[test.categoria] = [];
        }
        testsPorCategoria[test.categoria].push(test);
    });
    
    let html = `
        <div class="tests-section">
            <h4>🔧 Pruebas del equipo</h4>
            <p class="field-hint">Seleccione el resultado de cada prueba para el equipo</p>
    `;
    
    for (const [categoria, tests] of Object.entries(testsPorCategoria)) {
        html += `
            <div class="test-categoria">
                <h5>${escapeHtml(categoria)}</h5>
                <div class="test-items">
                    ${tests.map(test => {
                        const safeName = test.nombre.replace(/[^a-zA-Z0-9]/g, '_');
                        const existing = testsExistentes.find(t => t.nombre === test.nombre);
                        const resultado = existing ? existing.resultado : "";
                        return `
                        <div class="test-item">
                            <span class="test-nombre">${escapeHtml(test.nombre)}</span>
                            <div class="test-resultados">
                                <label><input type="radio" name="test_${safeName}" value="Funciona" ${resultado === "Funciona" ? "checked" : ""}> ✅ Funciona</label>
                                <label><input type="radio" name="test_${safeName}" value="No funciona" ${resultado === "No funciona" ? "checked" : ""}> ❌ No funciona</label>
                            </div>
                        </div>
                    `}).join("")}
                </div>
            </div>
        `;
    }
    html += '</div>';
    container.innerHTML = html;
}

    // ==================== ABRIR MODAL EDITAR ====================
    async function abrirModalEditar(tradeinId) {
        try {
            const data = await fetchJson(`/api/tradein/${tradeinId}/detalle`);
            const detalle = data.detalle || {};
            const tests = data.tests || [];
            const fotos = data.fotos || [];
            
            tradeinActual = tradeinId;
            
            // Llenar el formulario con los datos existentes
            document.getElementById("cliente-id").value = detalle.cliente_id || "";
            document.getElementById("cliente-search-input").value = 
                `${detalle.cliente_nombre || ""} ${detalle.cliente_apellido || ""}`.trim();
            document.getElementById("producto-id").value = detalle.producto_id || "";
            document.getElementById("id_equipo").value = detalle.imei || "";
            document.getElementById("color").value = detalle.Color || "";
            document.getElementById("capacidad").value = detalle.Capacidad || "";
            document.getElementById("clave").value = detalle.Clave || "";
            document.getElementById("patron").value = detalle.Patron || "";
            document.getElementById("valor-pagado").value = detalle.valor_pagado || "";
            document.getElementById("observaciones").value = detalle.observaciones || "";
            
            // Mostrar fotos existentes
            const preview = document.getElementById("fotos-preview");
            if (preview) {
                preview.innerHTML = fotos.map(foto => `
                    <div class="foto-preview foto-existente">
                        <img src="${escapeHtml(foto.url)}" alt="Foto del equipo">
                        <button type="button" class="remove-foto" data-url="${escapeHtml(foto.url)}">×</button>
                    </div>
                `).join("");
                
                preview.querySelectorAll('.remove-foto[data-url]').forEach(btn => {
                    btn.addEventListener('click', () => {
                        const container = btn.closest('.foto-preview');
                        if (container) {
                            container.style.opacity = '0.5';
                            container.style.textDecoration = 'line-through';
                            const hidden = document.createElement('input');
                            hidden.type = 'hidden';
                            hidden.name = 'fotos_eliminar';
                            hidden.value = btn.dataset.url;
                            container.appendChild(hidden);
                        }
                    });
                });
            }
            
            // Cargar tests en el formulario
            cargarTestsEnFormulario(tests);
            
            // Cambiar el título del modal y el botón de submit
            document.querySelector('#modal-registrar .ui-modal__title').textContent = 'Editar Trade-In';
            const submitBtn = document.querySelector('#form-registrar-tradein button[type="submit"]');
            submitBtn.textContent = 'Actualizar Trade-In';
            submitBtn.dataset.modo = 'editar';
            submitBtn.dataset.id = tradeinId;
            
            abrirModal("modal-registrar");
            
        } catch (err) {
            mostrarToast(err.message || "Error al cargar datos para editar", "error");
        }
    }

    // ==================== ENVIAR FORMULARIO ====================
    const formRegistrar = document.getElementById("form-registrar-tradein");
    if (formRegistrar) {
        formRegistrar.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            // Validar con FieldValidator
            if (window.FieldValidator && typeof window.FieldValidator.validateForm === 'function') {
                const isValid = window.FieldValidator.validateForm(formRegistrar);
                if (!isValid) {
                    mostrarToast("Por favor, corrige los errores en el formulario.", "error");
                    return;
                }
            }
            
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
            
            // Validar que el IMEI no tenga espacios
            if (idEquipo.includes(' ')) {
                mostrarToast("El IMEI no debe contener espacios", "error");
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
            
            // Recopilar tests
            const tests = [];
            document.querySelectorAll("#tests-container-registro .test-item").forEach(item => {
                const nombre = item.querySelector(".test-nombre")?.textContent || "";
                const seleccionado = item.querySelector('input[type="radio"]:checked');
                const resultado = seleccionado ? seleccionado.value : "Pendiente";
                tests.push({ nombre, resultado });
            });
            
            const formData = new FormData(formRegistrar);
            if (tests.length > 0) {
                formData.append('tests', JSON.stringify(tests));
            }
            
            const btnSubmit = formRegistrar.querySelector('button[type="submit"]');
            const textoOriginal = btnSubmit.textContent;
            btnSubmit.disabled = true;
            btnSubmit.textContent = "Guardando...";
            
            try {
                const modo = btnSubmit.dataset.modo || 'registrar';
                const url = modo === 'editar' ? `/api/tradein/${btnSubmit.dataset.id}` : "/api/tradein";
                const method = modo === 'editar' ? "PUT" : "POST";
                
                const response = await fetch(url, {
                    method: method,
                    headers: {
                        "Authorization": `Bearer ${getAuthToken()}`
                    },
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    mostrarToast(data.message || (modo === 'editar' ? "Trade-in actualizado correctamente" : "Trade-in registrado correctamente"));
                    cerrarModal("modal-registrar");
                    formRegistrar.reset();
                    if (fotosPreview) fotosPreview.innerHTML = "";
                    if (clienteIdInput) clienteIdInput.value = "";
                    if (clienteSearch) clienteSearch.value = "";
                    
                    // Resetear estado del formulario
                    delete btnSubmit.dataset.modo;
                    delete btnSubmit.dataset.id;
                    document.querySelector('#modal-registrar .ui-modal__title').textContent = 'Registrar nuevo Trade-In';
                    btnSubmit.textContent = 'Registrar Trade-In';
                    
                    await cargarEstadisticas();
                    await cargarTradeIns();
                } else {
                    mostrarToast(data.error || "Error al guardar", "error");
                }
            } catch (err) {
                mostrarToast(err.message || "Error de conexión", "error");
            } finally {
                btnSubmit.disabled = false;
                if (btnSubmit.dataset.modo !== 'editar') {
                    btnSubmit.textContent = textoOriginal;
                }
            }
        });
    }

    // ==================== TESTS EN MODAL SEPARADO (PARA COMPATIBILIDAD) ====================
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
            container.innerHTML = html || '<p class="empty-pruebas">No hay pruebas configuradas</p>';
            
            abrirModal("modal-tests");
            
            if (window.FieldValidator) {
                setTimeout(() => window.FieldValidator.init(), 100);
            }
            
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
            const resultado = seleccionado ? seleccionado.value : "Pendiente";
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
                            <span class="detalle-valor">${formatCurrency(detalle.valor_pagado || 0)}</span>
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

    // ==================== INICIALIZACIÓN ====================
    async function init() {
        // Inicializar FieldValidator
        if (window.FieldValidator) {
            setTimeout(() => window.FieldValidator.init(), 100);
        }
        
        await cargarCatalogoTests();
        await cargarProductos();
        await cargarEstadisticas();
        await cargarTradeIns();
        
        // Cargar tests en el formulario de registro por defecto
        cargarTestsEnFormulario();
        
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
                
                // Resetear tests
                cargarTestsEnFormulario();
                
                // Resetear título y botón
                document.querySelector('#modal-registrar .ui-modal__title').textContent = 'Registrar nuevo Trade-In';
                const submitBtn = document.querySelector('#form-registrar-tradein button[type="submit"]');
                submitBtn.textContent = 'Registrar Trade-In';
                delete submitBtn.dataset.modo;
                delete submitBtn.dataset.id;
                
                abrirModal("modal-registrar");
            });
        }
        
        const btnGuardarTests = document.getElementById("btn-guardar-tests");
        if (btnGuardarTests) {
            btnGuardarTests.addEventListener("click", guardarTests);
        }
        
        // Búsqueda en tabla
        const searchInput = document.getElementById("search-tradein");
        if (searchInput) {
            searchInput.addEventListener("input", () => {
                const query = searchInput.value.toLowerCase().trim();
                const rows = document.querySelectorAll("#tradein-list tr");
                rows.forEach(row => {
                    if (row.querySelector(".table__empty")) return;
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(query) ? "" : "none";
                });
            });
        }
    }
    
    document.addEventListener("DOMContentLoaded", init);
})();