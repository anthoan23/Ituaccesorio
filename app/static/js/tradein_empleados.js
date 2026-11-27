(() => {
    "use strict";

    let tradeinActual = null;
    let catalogoTests = [];
    const ICON_TEST_CHECK = `
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"/>
        </svg>`;
    const ICON_TEST_X = `
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>`;

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

    function confirmarConModal({ titulo, mensaje, textoConfirmar, destructiva = false }) {
        const modalId = "modal-confirmacion-tradein";
        const modal = document.getElementById(modalId);
        const tituloEl = document.getElementById(`${modalId}-title`);
        const mensajeEl = document.getElementById("tradein-confirmacion-mensaje");
        const confirmarBtn = document.getElementById("tradein-confirmacion-btn");

        if (!modal || !tituloEl || !mensajeEl || !confirmarBtn
            || !window.UiModal || typeof window.UiModal.openById !== "function") {
            console.error("No se encontró el modal de confirmación de Trade-In.");
            return Promise.resolve(false);
        }

        tituloEl.textContent = titulo;
        mensajeEl.textContent = mensaje;
        confirmarBtn.textContent = textoConfirmar;
        confirmarBtn.classList.toggle("ui-btn--danger", destructiva);
        confirmarBtn.classList.toggle("ui-btn--primary", !destructiva);

        return new Promise((resolve) => {
            let resuelta = false;

            const finalizar = (confirmado) => {
                if (resuelta) return;
                resuelta = true;
                modal.removeEventListener("click", manejarClick);
                document.removeEventListener("keydown", manejarTecla);
                cerrarModal(modalId);
                resolve(confirmado);
            };

            const manejarClick = (event) => {
                const elemento = event.target;
                if (!(elemento instanceof Element)) return;

                if (elemento.closest("#tradein-confirmacion-btn")) {
                    finalizar(true);
                } else if (elemento.closest("[data-close-modal]") || elemento === modal) {
                    finalizar(false);
                }
            };

            const manejarTecla = (event) => {
                if (event.key === "Escape") finalizar(false);
            };

            modal.addEventListener("click", manejarClick);
            document.addEventListener("keydown", manejarTecla);
            abrirModal(modalId);
        });
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

    const inputPatron = document.getElementById("patron");
    const patronGrid = document.getElementById("patron-grid");
    const patronLineas = document.getElementById("patron-lineas");
    const patronSecuencia = document.getElementById("patron-secuencia");
    const patronLimpiar = document.getElementById("patron-limpiar");
    const puntosPatron = new Map(
        Array.from({ length: 9 }, (_, index) => {
            const numero = index + 1;
            return [numero, {
                x: 50 + ((numero - 1) % 3) * 100,
                y: 50 + Math.floor((numero - 1) / 3) * 100,
            }];
        })
    );
    let secuenciaPatron = [];
    let dibujandoPatron = false;
    let pointerPatron = null;
    let lineaTemporalPatron = null;

    function actualizarSecuenciaPatron() {
        const valor = secuenciaPatron.join("-");
        inputPatron.value = valor;
        patronSecuencia.textContent = valor || "—";
    }

    function limpiarPatron() {
        secuenciaPatron = [];
        dibujandoPatron = false;
        pointerPatron = null;
        lineaTemporalPatron = null;
        patronLineas.replaceChildren();
        patronGrid.querySelectorAll(".pattern-grid__dot").forEach(punto => {
            punto.classList.remove("is-active", "is-highlighted");
        });
        actualizarSecuenciaPatron();
    }

    function crearLineaPatron(x1, y1, x2, y2, temporal = false) {
        const linea = document.createElementNS("http://www.w3.org/2000/svg", "line");
        linea.setAttribute("x1", x1);
        linea.setAttribute("y1", y1);
        linea.setAttribute("x2", x2);
        linea.setAttribute("y2", y2);
        if (temporal) linea.classList.add("is-temporary");
        patronLineas.appendChild(linea);
        return linea;
    }

    function unirPuntosPatron(desde, hasta) {
        const inicio = puntosPatron.get(desde);
        const final = puntosPatron.get(hasta);
        const deltaX = final.x - inicio.x;
        const deltaY = final.y - inicio.y;
        const distanciaCuadrada = deltaX * deltaX + deltaY * deltaY;

        return Array.from(puntosPatron.entries())
            .filter(([numero, punto]) => {
                if (numero === desde || numero === hasta || secuenciaPatron.includes(numero)) {
                    return false;
                }
                const relativoX = punto.x - inicio.x;
                const relativoY = punto.y - inicio.y;
                const productoCruzado = relativoX * deltaY - relativoY * deltaX;
                const posicion = (relativoX * deltaX + relativoY * deltaY) / distanciaCuadrada;
                return Math.abs(productoCruzado) < 1 && posicion > 0 && posicion < 1;
            })
            .sort((a, b) => {
                const puntoA = puntosPatron.get(a[0]);
                const puntoB = puntosPatron.get(b[0]);
                return Math.hypot(puntoA.x - inicio.x, puntoA.y - inicio.y)
                    - Math.hypot(puntoB.x - inicio.x, puntoB.y - inicio.y);
            })
            .map(([numero]) => numero);
    }

    function agregarPuntoPatron(numero) {
        if (secuenciaPatron.includes(numero)) return;

        let anterior = secuenciaPatron[secuenciaPatron.length - 1];
        if (anterior) {
            unirPuntosPatron(anterior, numero).forEach(intermedio => {
                anterior = secuenciaPatron[secuenciaPatron.length - 1];
                secuenciaPatron.push(intermedio);
                const puntoAnterior = puntosPatron.get(anterior);
                const puntoIntermedio = puntosPatron.get(intermedio);
                crearLineaPatron(puntoAnterior.x, puntoAnterior.y, puntoIntermedio.x, puntoIntermedio.y);
                patronGrid.querySelector(`[data-punto="${intermedio}"]`).classList.add("is-active");
            });

            anterior = secuenciaPatron[secuenciaPatron.length - 1];
            const puntoAnterior = puntosPatron.get(anterior);
            const puntoNuevo = puntosPatron.get(numero);
            crearLineaPatron(puntoAnterior.x, puntoAnterior.y, puntoNuevo.x, puntoNuevo.y);
        }

        secuenciaPatron.push(numero);
        patronGrid.querySelector(`[data-punto="${numero}"]`).classList.add("is-active");
        actualizarSecuenciaPatron();
    }

    function obtenerCoordenadasPatron(event) {
        const rect = patronGrid.getBoundingClientRect();
        return {
            x: (event.clientX - rect.left) * 300 / rect.width,
            y: (event.clientY - rect.top) * 300 / rect.height,
        };
    }

    function puntoCercanoPatron(x, y) {
        let puntoCercano = null;
        let distanciaCercana = 34;
        puntosPatron.forEach((punto, numero) => {
            const distancia = Math.hypot(punto.x - x, punto.y - y);
            if (distancia < distanciaCercana) {
                puntoCercano = numero;
                distanciaCercana = distancia;
            }
        });
        return puntoCercano;
    }

    function finalizarDibujoPatron() {
        dibujandoPatron = false;
        pointerPatron = null;
        if (lineaTemporalPatron) lineaTemporalPatron.remove();
        lineaTemporalPatron = null;
    }

    function establecerPatron(valor) {
        limpiarPatron();
        if (!valor) return;

        const numeros = String(valor).split("-");
        const esPatronValido = /^[1-9](?:-[1-9])*$/.test(valor)
            && numeros.length <= 9
            && new Set(numeros).size === numeros.length;
        if (!esPatronValido) {
            inputPatron.value = valor;
            patronSecuencia.textContent = valor;
            return;
        }

        numeros.forEach(numero => agregarPuntoPatron(Number(numero)));
    }

    if (patronGrid && inputPatron && patronLineas && patronSecuencia) {
        patronGrid.addEventListener("pointerdown", event => {
            if (event.pointerType === "mouse" && event.button !== 0) return;
            const coordenadas = obtenerCoordenadasPatron(event);
            const numero = puntoCercanoPatron(coordenadas.x, coordenadas.y);
            if (!numero) return;

            event.preventDefault();
            limpiarPatron();
            dibujandoPatron = true;
            pointerPatron = event.pointerId;
            patronGrid.setPointerCapture(event.pointerId);
            agregarPuntoPatron(numero);
        });

        patronGrid.addEventListener("pointermove", event => {
            const puntoResaltado = patronGrid.querySelector(".is-highlighted");
            if (puntoResaltado) puntoResaltado.classList.remove("is-highlighted");

            const coordenadas = obtenerCoordenadasPatron(event);
            const numero = puntoCercanoPatron(coordenadas.x, coordenadas.y);
            if (numero && !secuenciaPatron.includes(numero)) {
                patronGrid.querySelector(`[data-punto="${numero}"]`).classList.add("is-highlighted");
            }

            if (!dibujandoPatron || event.pointerId !== pointerPatron) return;
            event.preventDefault();

            if (numero) {
                if (!secuenciaPatron.includes(numero)) agregarPuntoPatron(numero);
                if (lineaTemporalPatron) lineaTemporalPatron.remove();
                lineaTemporalPatron = null;
                return;
            }

            if (secuenciaPatron.length) {
                if (lineaTemporalPatron) lineaTemporalPatron.remove();
                const ultimo = puntosPatron.get(secuenciaPatron[secuenciaPatron.length - 1]);
                lineaTemporalPatron = crearLineaPatron(ultimo.x, ultimo.y, coordenadas.x, coordenadas.y, true);
            }
        });

        patronGrid.addEventListener("pointerup", finalizarDibujoPatron);
        patronGrid.addEventListener("pointercancel", finalizarDibujoPatron);
        patronGrid.addEventListener("click", event => {
            if (event.detail !== 0) return;
            const punto = event.target.closest("[data-punto]");
            if (punto) agregarPuntoPatron(Number(punto.dataset.punto));
        });
    }

    if (patronLimpiar) {
        patronLimpiar.addEventListener("click", limpiarPatron);
    }

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
    const zonaFotos = document.getElementById("fotos-dropzone");
    const hintZona = zonaFotos?.querySelector("[data-upload-hint]");
    const previewZona = zonaFotos?.querySelector("[data-upload-preview]");
    
    if (fotosInput && fotosPreview) {
        fotosInput.addEventListener("change", () => {
            const hayArchivos = fotosInput.files && fotosInput.files.length > 0;
            if (previewZona) previewZona.hidden = !hayArchivos;
            if (hintZona) hintZona.hidden = !!hayArchivos;
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

        // Zona de arrastre para las fotos (solo imágenes; reemplaza la selección actual,
        // igual que elegir de nuevo con el selector nativo)
        const dropzoneFotos = document.getElementById("fotos-dropzone");
        if (dropzoneFotos) {
            ["dragenter", "dragover"].forEach((tipo) => {
                dropzoneFotos.addEventListener(tipo, (e) => {
                    e.preventDefault();
                    dropzoneFotos.classList.add("upload-dropzone--dragover");
                });
            });

            ["dragleave", "drop"].forEach((tipo) => {
                dropzoneFotos.addEventListener(tipo, (e) => {
                    e.preventDefault();
                    dropzoneFotos.classList.remove("upload-dropzone--dragover");
                });
            });

            dropzoneFotos.addEventListener("drop", (e) => {
                const archivos = Array.from(e.dataTransfer?.files || [])
                    .filter((f) => f.type.startsWith("image/"));
                if (!archivos.length) return;

                const dt = new DataTransfer();
                archivos.forEach((f) => dt.items.add(f));
                fotosInput.files = dt.files;
                fotosInput.dispatchEvent(new Event("change"));
            });
        }
    }

    // ==================== CARGAR TESTS EN FORMULARIO ====================
    function cargarTestsEnFormulario(testsExistentes = []) {
    const container = document.getElementById("tests-container-registro");
    if (!container) return;

    const mitad = Math.ceil(catalogoTests.length / 2);
    const renderTest = test => {
        const safeName = test.nombre.replace(/[^a-zA-Z0-9]/g, '_');
        const existing = testsExistentes.find(t => t.nombre === test.nombre);
        const resultado = existing ? existing.resultado : "";
        return `
            <div class="test-item">
                <span class="test-nombre">${escapeHtml(test.nombre)}</span>
                <div class="test-resultados">
                    <label class="test-resultados__opcion test-resultados__opcion--success">
                        <input type="radio" name="test_${safeName}" value="Funciona" ${resultado === "Funciona" ? "checked" : ""}>
                        ${ICON_TEST_CHECK}
                    </label>
                    <label class="test-resultados__opcion test-resultados__opcion--danger">
                        <input type="radio" name="test_${safeName}" value="No funciona" ${resultado === "No funciona" ? "checked" : ""}>
                        ${ICON_TEST_X}
                    </label>
                </div>
            </div>
        `;
    };

    let html = `
        <div class="tests-section">
            <div class="tests-section__header">
                <div>
                    <h4>🔧 Pruebas del equipo</h4>
                    <p class="field-hint">Seleccione el resultado de cada prueba para el equipo</p>
                </div>
                ${catalogoTests.length ? `
                    <div class="tests-section__actions">
                        <button type="button" class="ui-btn ui-btn--ghost ui-btn--sm" data-test-action="aprobar">
                            ${ICON_TEST_CHECK} Marcar todos como OK
                        </button>
                        <button type="button" class="ui-btn ui-btn--ghost ui-btn--sm" data-test-action="reprobar">
                            ${ICON_TEST_X} Marcar todos como No funciona
                        </button>
                    </div>
                ` : ""}
            </div>
            <div class="test-items">
                <div class="test-column">
                    ${catalogoTests.slice(0, mitad).map(renderTest).join("")}
                </div>
                <div class="test-column">
                    ${catalogoTests.slice(mitad).map(renderTest).join("")}
                </div>
            </div>
        </div>
    `;
    container.innerHTML = html;

    container.querySelectorAll("[data-test-action]").forEach(button => {
        button.addEventListener("click", () => {
            const resultado = button.dataset.testAction === "aprobar"
                ? "Funciona"
                : "No funciona";
            container.querySelectorAll('input[type="radio"]').forEach(radio => {
                if (radio.value === resultado) radio.checked = true;
            });
        });
    });
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
            establecerPatron(detalle.Patron || "");
            document.getElementById("valor-pagado").value = detalle.valor_pagado || "";
            document.getElementById("observaciones").value = detalle.observaciones || "";
            
            // Mostrar fotos existentes
            const preview = document.getElementById("fotos-preview");
            const zonaFotosEditar = document.getElementById("fotos-dropzone");
            if (zonaFotosEditar) {
                zonaFotosEditar.querySelector("[data-upload-preview]")?.removeAttribute("hidden");
                zonaFotosEditar.querySelector("[data-upload-hint]")?.setAttribute("hidden", "");
            }
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
            submitBtn.dataset.imeiOriginal = detalle.imei || "";
            
            abrirModal("modal-registrar");
            
        } catch (err) {
            mostrarToast(err.message || "Error al cargar datos para editar", "error");
        }
    }

    // ==================== ENVIAR FORMULARIO ====================
    const formRegistrar = document.getElementById("form-registrar-tradein");
    if (formRegistrar) {
        formRegistrar.addEventListener("reset", limpiarPatron);
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

            const btnSubmit = formRegistrar.querySelector('button[type="submit"]');
            const modoFormulario = btnSubmit.dataset.modo || "registrar";
            const reutilizaEquipoActual = modoFormulario === "editar"
                && idEquipo === btnSubmit.dataset.imeiOriginal;
            
            const valorPagado = document.getElementById("valor-pagado")?.value;
            if (!valorPagado || Number(valorPagado) <= 0) {
                mostrarToast("Debe ingresar un valor pagado válido", "error");
                return;
            }
            
            if (!reutilizaEquipoActual) {
                let checkData;
                try {
                    const checkResponse = await fetch(`/api/tradein/verificar-equipo/${encodeURIComponent(idEquipo)}`, {
                        headers: { "Authorization": `Bearer ${getAuthToken()}` }
                    });
                    if (!checkResponse.ok) {
                        throw new Error(`HTTP ${checkResponse.status}`);
                    }
                    checkData = await checkResponse.json();
                } catch (err) {
                    console.warn("No se pudo verificar el equipo; se continúa como nuevo:", err);
                }

                if (checkData?.exists) {
                    const equipo = checkData.equipo || {};
                    const continuar = await confirmarConModal({
                        titulo: "Equipo ya registrado",
                        mensaje: `El equipo con ID "${idEquipo}" ya está registrado en el sistema.\n\nProducto: ${equipo.producto_nombre || 'N/A'}\nColor: ${equipo.Color || 'N/A'}\nCapacidad: ${equipo.Capacidad || 'N/A'}\n\n¿Desea continuar y reutilizar este equipo?`,
                        textoConfirmar: "Reutilizar equipo",
                    });
                    if (!continuar) return;
                }
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
                    delete btnSubmit.dataset.imeiOriginal;
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
                                    <img src="${escapeHtml(foto.url)}" alt="Foto del equipo" data-action="abrir-foto" data-url="${escapeHtml(foto.url)}">
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
        const confirmar = await confirmarConModal({
            titulo: "Confirmar eliminación",
            mensaje: "¿Estás seguro de que deseas eliminar este trade-in?\n\nEsta acción no se puede deshacer.",
            textoConfirmar: "Eliminar",
            destructiva: true,
        });
        if (!confirmar) return;
        
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
                const zonaFotosReset = document.getElementById("fotos-dropzone");
                if (zonaFotosReset) {
                    zonaFotosReset.querySelector("[data-upload-preview]")?.setAttribute("hidden", "");
                    zonaFotosReset.querySelector("[data-upload-hint]")?.removeAttribute("hidden");
                }
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
                delete submitBtn.dataset.imeiOriginal;
                
                abrirModal("modal-registrar");
            });
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
    
    // Visor de fotos por delegación: los onclick inline quedan bloqueados
    // por la CSP.
    document.addEventListener("click", (e) => {
      const el = e.target.closest("[data-action='abrir-foto']");
      if (el && el.dataset.url) window.open(el.dataset.url, "_blank");
    });

    document.addEventListener("DOMContentLoaded", init);
})();