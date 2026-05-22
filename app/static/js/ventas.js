(() => {
    "use strict";

    const state = {
        productos: [],
        masVendidos: [],
        carrito: [],
        filtros: { clase_id: "", marca_id: "", q: "" },
        paginacion: { pagina: 1, por_pagina: 12 },
        tasas: { oficial: 520.91, paralelo: 710.12 }
    };

    let facturaPendiente = null;

    function getAuthToken() {
        return localStorage.getItem("access_token") || sessionStorage.getItem("access_token") || "";
    }

    async function fetchJson(url, options = {}) {
        const authToken = getAuthToken();
        const csrfToken = document.querySelector("input[name='_csrf_token']")?.value || "";
        
        const response = await fetch(url, {
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
                ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
                ...(authToken ? { "Authorization": `Bearer ${authToken}` } : {})
            },
            credentials: "same-origin",
            ...options
        });
        
        const data = await response.json().catch(() => ({}));
        if (!response.ok || data.success === false) {
            throw new Error(data.error || "Error en la operación");
        }
        return data;
    }

    function formatUSD(amount) {
        return `$${Number(amount).toFixed(2)}`;
    }

    function formatVES(amount) {
        return `Bs ${Number(amount).toFixed(2)}`;
    }

    async function cargarCatalogo() {
        const params = new URLSearchParams();
        if (state.filtros.clase_id) params.set("clase_id", state.filtros.clase_id);
        if (state.filtros.marca_id) params.set("marca_id", state.filtros.marca_id);
        if (state.filtros.q) params.set("q", state.filtros.q);
        
        const data = await fetchJson(`/api/catalogo/productos?${params}`);
        state.productos = data.productos || [];
        state.masVendidos = data.mas_vendidos || [];
        state.tasas = data.tasas || state.tasas;
        
        renderProductos();
        renderMasVendidos();
        renderTasas();
        renderFiltros(data.clases, data.marcas);
    }

    function renderProductos() {
        const container = document.getElementById("productos-grid");
        if (!container) return;
        
        if (!state.productos.length) {
            container.innerHTML = '<p class="sin-resultados">No se encontraron productos</p>';
            return;
        }
        
        container.innerHTML = state.productos.map(p => {
            const bsFinal = Number(p.precio_usd) * (state.tasas.paralelo || state.tasas.oficial);
            const usdAjustado = bsFinal / (state.tasas.oficial || 1);
            return `
            <div class="producto-card">
                <div class="producto-imagen"></div>
                <div class="producto-nombre">${escapeHtml(p.nombre)}</div>
                <div class="producto-marca">${escapeHtml(p.marca)}</div>
                <div class="producto-precios">
                    <div class="precio-usd">${formatUSD(usdAjustado)}</div>
                    <div class="precio-bs">${formatVES(bsFinal)}</div>
                </div>
                <div class="producto-stock">Stock: ${p.stock} unidades</div>
                <button class="btn btn--yellow btn-agregar" data-id="${p.id}" ${p.stock <= 0 ? 'disabled' : ''}>
                    ${p.stock > 0 ? 'Agregar al carrito' : 'Agotado'}
                </button>
            </div>
        `}).join("");
        
        document.querySelectorAll(".btn-agregar").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                const id = btn.dataset.id;
                await agregarCarrito(id, 1);
            });
        });
    }

    function renderMasVendidos() {
        const container = document.getElementById("mas-vendidos");
        if (!container) return;
        
        if (!state.masVendidos.length) {
            container.innerHTML = "<p>Sin datos</p>";
            return;
        }
        
        container.innerHTML = state.masVendidos.map(p => {
            const bsFinal = Number(p.precio_usd) * (state.tasas.paralelo || state.tasas.oficial);
            const usdAjustado = bsFinal / (state.tasas.oficial || 1);
            return `
            <div class="mas-vendido-item">
                <span>${escapeHtml(p.nombre)}</span>
                <strong>${formatUSD(usdAjustado)}</strong>
            </div>
        `}).join("");
    }

    function renderTasas() {
        const container = document.getElementById("tasas-info");
        if (!container) return;
        
        container.innerHTML = `
            <div>Oficial: 1 USD = ${formatVES(state.tasas.oficial)}</div>
            <small>Los precios se calculan al momento del pago</small>
        `;
    }

    function renderFiltros(clases, marcas) {
        const claseSelect = document.getElementById("f-clase");
        const marcaSelect = document.getElementById("f-marca");
        
        if (claseSelect && clases) {
            claseSelect.innerHTML = '<option value="">Todas</option>' + 
                clases.map(c => `<option value="${c.id}">${escapeHtml(c.nombre)}</option>`).join("");
        }
        
        if (marcaSelect && marcas) {
            marcaSelect.innerHTML = '<option value="">Todas</option>' + 
                marcas.map(m => `<option value="${m.id}">${escapeHtml(m.nombre)}</option>`).join("");
        }
    }

    async function cargarCarrito() {
        const data = await fetchJson("/api/carrito");
        state.carrito = data.items || [];
        actualizarBadgeCarrito();
        renderCarritoModal();
        return data;
    }

    async function agregarCarrito(productoId, cantidad) {
        try {
            await fetchJson("/api/carrito", {
                method: "POST",
                body: JSON.stringify({ producto_id: productoId, cantidad })
            });
            await cargarCarrito();
            mostrarNotificacion("Producto agregado al carrito");
        } catch (err) {
            mostrarNotificacion(err.message, "error");
        }
    }

    async function actualizarCantidadCarrito(productoId, cantidad) {
        if (cantidad <= 0) {
            await fetchJson(`/api/carrito/${productoId}`, { method: "DELETE" });
        } else {
            await fetchJson("/api/carrito", {
                method: "PUT",
                body: JSON.stringify({ producto_id: productoId, cantidad })
            });
        }
        await cargarCarrito();
    }

    async function vaciarCarrito() {
        if (confirm("¿Vaciar todo el carrito?")) {
            await fetchJson("/api/carrito/vaciar", { method: "DELETE" });
            await cargarCarrito();
        }
    }

    function actualizarBadgeCarrito() {
        const badge = document.getElementById("cart-count");
        if (badge) {
            const total = state.carrito.reduce((sum, item) => sum + item.cantidad, 0);
            badge.textContent = total;
            badge.style.display = total > 0 ? "flex" : "none";
        }
    }

    function renderCarritoModal() {
        const container = document.getElementById("cart-items");
        const totalUsdSpan = document.getElementById("cart-total-usd");
        const totalBsSpan = document.getElementById("cart-total-bs");
        
        if (!container) return;
        
        if (!state.carrito.length) {
            container.innerHTML = '<p class="carrito-vacio">Tu carrito está vacío</p>';
            if (totalUsdSpan) totalUsdSpan.textContent = formatUSD(0);
            if (totalBsSpan) totalBsSpan.textContent = formatVES(0);
            return;
        }
        
        container.innerHTML = state.carrito.map(item => {
            const bsItem = Number(item.precio_usd) * (state.tasas.paralelo || state.tasas.oficial);
            const usdItem = bsItem / (state.tasas.oficial || 1);
            return `
            <div class="cart-item">
                <div class="cart-item-info">
                    <div class="cart-item-name">${escapeHtml(item.nombre)}</div>
                    <div class="cart-item-price">${formatUSD(usdItem)} / ${formatVES(bsItem)}</div>
                </div>
                <div class="cart-item-controls">
                    <button class="icon-action" data-action="decrement" data-id="${item.producto_id}">-</button>
                    <span class="cart-item-qty">${item.cantidad}</span>
                    <button class="icon-action" data-action="increment" data-id="${item.producto_id}">+</button>
                    <button class="icon-action" data-action="remove" data-id="${item.producto_id}" aria-label="Eliminar producto">X</button>
                </div>
            </div>
        `}).join("");
        
        // Total Bs uses tasa paralelo; USD mostrado es conversion de ese Bs por la tasa oficial
        const totalBs = state.carrito.reduce((sum, item) => sum + (Number(item.precio_usd) * (state.tasas.paralelo || state.tasas.oficial) * item.cantidad), 0);
        const totalUsdAjustado = totalBs / (state.tasas.oficial || 1);

        if (totalUsdSpan) totalUsdSpan.textContent = formatUSD(totalUsdAjustado);
        if (totalBsSpan) totalBsSpan.textContent = formatVES(totalBs);
        
        container.querySelectorAll("[data-action='increment']").forEach(btn => {
            btn.addEventListener("click", () => {
                const id = parseInt(btn.dataset.id);
                const item = state.carrito.find(i => i.producto_id === id);
                if (item) actualizarCantidadCarrito(id, item.cantidad + 1);
            });
        });
        
        container.querySelectorAll("[data-action='decrement']").forEach(btn => {
            btn.addEventListener("click", () => {
                const id = parseInt(btn.dataset.id);
                const item = state.carrito.find(i => i.producto_id === id);
                if (item) actualizarCantidadCarrito(id, item.cantidad - 1);
            });
        });
        
        container.querySelectorAll("[data-action='remove']").forEach(btn => {
            btn.addEventListener("click", () => {
                actualizarCantidadCarrito(parseInt(btn.dataset.id), 0);
            });
        });
    }

    function openCartModal() {
        const modal = document.getElementById("cart-modal");
        if (modal) {
            modal.classList.remove("is-hidden");
            document.body.style.overflow = "hidden";
        }
    }

    function closeModal() {
        document.querySelectorAll(".modal:not(.is-hidden)").forEach(modal => {
            modal.classList.add("is-hidden");
        });
        document.body.style.overflow = "";
    }

    async function iniciarCheckout() {
        if (!state.carrito.length) {
            mostrarNotificacion("El carrito está vacío", "error");
            return;
        }
        window.location.href = "/pagar";
    }

    async function cargarMetodosPago() {
        const data = await fetchJson("/api/metodos-pago");
        const select = document.getElementById("metodo-pago");
        if (select) {
            select.innerHTML = '<option value="">-- Selecciona --</option>' +
                data.metodos.map(m => `<option value="${m.id}">${m.nombre} (${m.moneda})</option>`).join("");
        }
    }

    function getFormularioPagoHtml(metodo) {
        const formularios = {
            pago_movil: `
                <div class="form-pago">
                    <h4>Pago Móvil (Bolívares)</h4>
                    <label class="field"><span class="field__label">Banco de Origen</span>
                        <select name="banco" required>
                            <option value="">Selecciona</option>
                            <option>Banesco</option><option>Mercantil</option>
                            <option>Provincial</option><option>BDV</option>
                            <option>Venezuela</option><option>Bancaribe</option>
                        </select>
                    </label>
                    <label class="field"><span class="field__label">Teléfono del Emisor</span>
                        <input type="tel" name="telefono" required placeholder="0412-XXX-XXXX">
                    </label>
                    <label class="field"><span class="field__label">Número de Referencia</span>
                        <input type="text" name="referencia" required placeholder="Últimos 6 dígitos">
                    </label>
                    <label class="field"><span class="field__label">Monto Pagado (Bs)</span>
                        <input type="number" name="monto" step="0.01" required>
                    </label>
                    <div class="pago-info">Adjunta el comprobante en el próximo paso</div>
                </div>
            `,
            zelle: `
                <div class="form-pago">
                    <h4>Zelle (Dólares)</h4>
                    <label class="field"><span class="field__label">Titular de la Cuenta</span>
                        <input type="text" name="titular" required placeholder="Nombre completo">
                    </label>
                    <label class="field"><span class="field__label">Correo o Teléfono Zelle</span>
                        <input type="text" name="correo" required>
                    </label>
                    <label class="field"><span class="field__label">Referencia / Confirmación</span>
                        <input type="text" name="referencia">
                    </label>
                    <label class="field"><span class="field__label">Monto Pagado (USD)</span>
                        <input type="number" name="monto" step="0.01" required>
                    </label>
                </div>
            `,
            binance: `
                <div class="form-pago">
                    <h4>Binance (USDT)</h4>
                    <label class="field"><span class="field__label">UID o Correo Binance</span>
                        <input type="text" name="uid" required>
                    </label>
                    <label class="field"><span class="field__label">Pay ID / Order ID</span>
                        <input type="text" name="pay_id" required>
                    </label>
                    <label class="field"><span class="field__label">Monto Pagado (USDT)</span>
                        <input type="number" name="monto" step="0.01" required>
                    </label>
                </div>
            `,
            efectivo_bs: `
                <div class="form-pago">
                    <h4>Efectivo (Bolívares)</h4>
                    <label class="field"><span class="field__label">¿Con qué billete vas a pagar?</span>
                        <input type="text" name="billete" required placeholder="Ej: Bs 500, Bs 200">
                    </label>
                    <div class="pago-info">Por favor, tenga el monto exacto o el billete indicado al momento de la entrega.</div>
                </div>
            `,
            efectivo_usd: `
                <div class="form-pago">
                    <h4>Efectivo (Dólares)</h4>
                    <label class="field"><span class="field__label">¿Con qué billete vas a pagar?</span>
                        <select name="billete" required>
                            <option value="">Selecciona</option>
                            <option>$1</option><option>$5</option><option>$10</option>
                            <option>$20</option><option>$50</option><option>$100</option>
                        </select>
                    </label>
                    <div class="pago-info">Por favor, tenga el monto exacto o el billete indicado al momento de la entrega.</div>
                </div>
            `
        };
        return formularios[metodo] || '<div class="form-pago">Método no disponible</div>';
    }

    function setupFormularioDinamico() {
        const select = document.getElementById("metodo-pago");
        const container = document.getElementById("form-pago-container");
        
        if (select && container) {
            select.addEventListener("change", () => {
                const metodo = select.value;
                if (metodo) {
                    container.innerHTML = getFormularioPagoHtml(metodo);
                } else {
                    container.innerHTML = "";
                }
            });
        }
    }

    async function procesarPago() {
        const metodoSelect = document.getElementById("metodo-pago");
        const metodo = metodoSelect?.value;
        
        if (!metodo) {
            mostrarNotificacion("Selecciona un método de pago", "error");
            return;
        }
        
        // Recoger datos del formulario dinámico
        const datosPago = {};
        const formContainer = document.getElementById("form-pago-container");
        if (formContainer) {
            formContainer.querySelectorAll("input, select").forEach(input => {
                if (input.name) datosPago[input.name] = input.value;
            });
        }
        
        // Validar campos requeridos
        const requiredFields = formContainer?.querySelectorAll("[required]") || [];
        for (const field of requiredFields) {
            if (!field.value) {
                mostrarNotificacion(`El campo "${field.placeholder || field.name}" es obligatorio`, "error");
                return;
            }
        }
        
        try {
            const data = await fetchJson("/api/procesar-pago", {
                method: "POST",
                body: JSON.stringify({ metodo_pago: metodo, datos_pago: datosPago })
            });
            
            facturaPendiente = data.factura_id;
            mostrarNotificacion(data.mensaje || "¡Pago registrado! En breve será verificado");
            window.location.href = "/catalogo";
        } catch (err) {
            mostrarNotificacion(err.message, "error");
        }
    }

    async function cargarPagosPendientes() {
        const data = await fetchJson("/api/admin/pagos-pendientes");
        renderPagosList(data.pagos, "pendientes");
    }

    async function cargarPagosAprobados() {
        const data = await fetchJson("/api/admin/pagos-aprobados");
        renderPagosList(data.pagos, "aprobados");
    }

    async function cargarPagosRechazados() {
        const data = await fetchJson("/api/admin/pagos-rechazados");
        renderPagosList(data.pagos, "rechazados");
    }

    function renderPagosList(pagos, tipo) {
        const container = document.getElementById(`${tipo}-list`);
        if (!container) return;
        
        if (!pagos.length) {
            container.innerHTML = '<p class="sin-resultados">No hay pagos en esta lista</p>';
            return;
        }
        
        container.innerHTML = pagos.map(p => `
            <div class="pago-card" data-factura="${p.factura_id}">
                <div class="info-row"><strong>Factura:</strong> ${escapeHtml(p.factura_id)}</div>
                <div class="info-row"><strong>Fecha:</strong> ${escapeHtml(p.fecha)}</div>
                <div class="info-row"><strong>Cliente:</strong> ${escapeHtml(p.cliente_nombre)} ${escapeHtml(p.cliente_apellido || '')}</div>
                <div class="info-row"><strong>Teléfono:</strong> ${escapeHtml(p.cliente_celular || 'N/A')}</div>
                <div class="info-row"><strong>Total:</strong> ${formatVES(p.total_bs)}</div>
                <div class="info-row"><strong>Método:</strong> ${escapeHtml(p.metodo_pago)}</div>
                ${p.banco ? `<div class="info-row"><strong>Banco:</strong> ${escapeHtml(p.banco)}</div>` : ''}
                ${p.titular ? `<div class="info-row"><strong>Titular:</strong> ${escapeHtml(p.titular)}</div>` : ''}
                ${p.referencia !== 'N/A' ? `<div class="info-row"><strong>Referencia:</strong> ${escapeHtml(p.referencia)}</div>` : ''}
                ${p.contacto !== 'N/A' ? `<div class="info-row"><strong>Contacto:</strong> ${escapeHtml(p.contacto)}</div>` : ''}
                ${p.billete !== 'N/A' ? `<div class="info-row"><strong>Billete:</strong> ${escapeHtml(p.billete)}</div>` : ''}
                ${tipo === "pendientes" ? `
                    <div class="pago-actions">
                        <button class="btn btn--yellow btn-aprobar" data-factura="${p.factura_id}">Aprobar</button>
                        <button class="btn btn--ghost btn-rechazar" data-factura="${p.factura_id}">Rechazar</button>
                    </div>
                ` : ''}
            </div>
        `).join("");
        
        if (tipo === "pendientes") {
            document.querySelectorAll(".btn-aprobar").forEach(btn => {
                btn.addEventListener("click", () => aprobarPago(btn.dataset.factura));
            });
            document.querySelectorAll(".btn-rechazar").forEach(btn => {
                btn.addEventListener("click", () => mostrarModalRechazo(btn.dataset.factura));
            });
        }
    }

    async function aprobarPago(facturaId) {
        if (confirm("¿Aprobar este pago?")) {
            try {
                await fetchJson(`/api/admin/aprobar-pago/${facturaId}`, { method: "POST" });
                mostrarNotificacion("Pago aprobado");
                cargarPagosPendientes();
                cargarPagosAprobados();
            } catch (err) {
                mostrarNotificacion(err.message, "error");
            }
        }
    }

    let facturaRechazoActual = null;
    
    function mostrarModalRechazo(facturaId) {
        facturaRechazoActual = facturaId;
        const modal = document.getElementById("rechazo-modal");
        if (modal) {
            modal.classList.remove("is-hidden");
            document.getElementById("motivo-rechazo").value = "";
        }
    }

    async function confirmarRechazo() {
        const motivo = document.getElementById("motivo-rechazo")?.value.trim();
        if (!motivo) {
            mostrarNotificacion("Debes escribir un motivo", "error");
            return;
        }
        
        try {
            await fetchJson(`/api/admin/rechazar-pago/${facturaRechazoActual}`, {
                method: "POST",
                body: JSON.stringify({ motivo })
            });
            mostrarNotificacion("Pago rechazado");
            cerrarModalRechazo();
            cargarPagosPendientes();
            cargarPagosRechazados();
        } catch (err) {
            mostrarNotificacion(err.message, "error");
        }
    }
    
    function cerrarModalRechazo() {
        const modal = document.getElementById("rechazo-modal");
        if (modal) modal.classList.add("is-hidden");
        facturaRechazoActual = null;
    }

    async function cargarProductosParaSelect() {
        const data = await fetchJson("/api/catalogo/productos");
        const select = document.getElementById("producto-select");
        if (select) {
            select.innerHTML = '<option value="">-- Selecciona --</option>' +
                (data.productos || []).map(p => `<option value="${p.id}" data-precio="${p.precio_usd}">${p.nombre} - ${formatUSD(p.precio_usd)}</option>`).join("");
        }
    }
    
    let itemsLocal = [];
    
    function agregarItemLocal() {
        const select = document.getElementById("producto-select");
        const cantidad = parseInt(document.getElementById("cantidad-local")?.value || 1);
        const productoId = select?.value;
        
        if (!productoId) {
            mostrarNotificacion("Selecciona un producto", "error");
            return;
        }
        
        const option = select.options[select.selectedIndex];
        const nombre = option.text.split(" - ")[0];
        const precio = parseFloat(option.dataset.precio);
        
        const existente = itemsLocal.find(i => i.producto_id == productoId);
        if (existente) {
            existente.cantidad += cantidad;
        } else {
            itemsLocal.push({ producto_id: parseInt(productoId), nombre, precio_usd: precio, cantidad });
        }
        
        renderItemsLocal();
        select.value = "";
        document.getElementById("cantidad-local").value = 1;
    }
    
    function renderItemsLocal() {
        const container = document.getElementById("items-local-list");
        if (!container) return;
        
        if (!itemsLocal.length) {
            container.innerHTML = '<p class="sin-resultados">No hay productos agregados</p>';
            return;
        }
        
        const totalBs = itemsLocal.reduce((sum, i) => sum + (Number(i.precio_usd) * (state.tasas.paralelo || state.tasas.oficial) * i.cantidad), 0);
        const totalUsd = totalBs / (state.tasas.oficial || 1);
        
        container.innerHTML = `
            <div class="items-local">
                ${itemsLocal.map((item, idx) => `
                    <div class="cart-item">
                        <span>${escapeHtml(item.nombre)} x${item.cantidad}</span>
                        <span>${formatUSD((Number(item.precio_usd) * (state.tasas.paralelo || state.tasas.oficial)) / (state.tasas.oficial || 1) * item.cantidad)} / ${formatVES(Number(item.precio_usd) * (state.tasas.paralelo || state.tasas.oficial) * item.cantidad)}</span>
                        <button class="icon-action" data-remove="${idx}" aria-label="Eliminar producto">X</button>
                    </div>
                `).join('')}
                <div class="cart-total">
                    <strong>Total: ${formatUSD(totalUsd)} / ${formatVES(totalBs)}</strong>
                </div>
            </div>
        `;
        
        document.querySelectorAll("[data-remove]").forEach(btn => {
            btn.addEventListener("click", () => {
                const idx = parseInt(btn.dataset.remove);
                itemsLocal.splice(idx, 1);
                renderItemsLocal();
            });
        });
    }
    
    async function registrarVentaLocal(event) {
        event.preventDefault();
        
        const clienteId = document.getElementById("cliente-id")?.value;
        const metodoPago = document.getElementById("metodo-local")?.value;
        const totalPagado = parseFloat(document.getElementById("total-pagado")?.value || 0);
        
        if (!clienteId) {
            mostrarNotificacion("ID del cliente requerido", "error");
            return;
        }
        if (!itemsLocal.length) {
            mostrarNotificacion("Agrega al menos un producto", "error");
            return;
        }
        
        try {
            await fetchJson("/api/admin/ventas-local", {
                method: "POST",
                body: JSON.stringify({
                    cliente_id: parseInt(clienteId),
                    items: itemsLocal,
                    total_pagado: totalPagado,
                    metodo_pago: metodoPago
                })
            });
            
            mostrarNotificacion("Venta registrada exitosamente");
            itemsLocal = [];
            renderItemsLocal();
            closeModal();
            document.getElementById("form-venta-local")?.reset();
        } catch (err) {
            mostrarNotificacion(err.message, "error");
        }
    }

    function mostrarNotificacion(msg, tipo = "success") {
        const notif = document.createElement("div");
        notif.className = `notificacion notificacion--${tipo}`;
        notif.textContent = msg;
        notif.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: ${tipo === "error" ? "#ef4444" : "#22c55e"};
            color: white;
            padding: 12px 24px;
            border-radius: 12px;
            z-index: 1000;
            animation: fadeOut 3s forwards;
        `;
        document.body.appendChild(notif);
        setTimeout(() => notif.remove(), 3000);
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

    async function init() {
        const path = window.location.pathname;
        
        document.addEventListener("click", (e) => {
            if (e.target.closest("[data-modal-close]")) {
                closeModal();
            }
        });
        
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") closeModal();
        });
        
        if (path === "/catalogo") {
            const cartToggle = document.getElementById("cart-toggle");
            const cartVaciar = document.getElementById("cart-vaciar");
            const cartCheckout = document.getElementById("cart-checkout");
            const btnAplicar = document.getElementById("btn-aplicar");
            const btnLimpiar = document.getElementById("btn-limpiar");
            const fClase = document.getElementById("f-clase");
            const fMarca = document.getElementById("f-marca");
            const fTexto = document.getElementById("f-texto");
            
            if (cartToggle) cartToggle.addEventListener("click", () => openCartModal());
            if (cartVaciar) cartVaciar.addEventListener("click", () => vaciarCarrito());
            if (cartCheckout) cartCheckout.addEventListener("click", () => iniciarCheckout());
            
            if (btnAplicar) {
                btnAplicar.addEventListener("click", () => {
                    state.filtros.clase_id = fClase?.value || "";
                    state.filtros.marca_id = fMarca?.value || "";
                    state.filtros.q = fTexto?.value || "";
                    cargarCatalogo();
                });
            }
            
            if (btnLimpiar) {
                btnLimpiar.addEventListener("click", () => {
                    if (fClase) fClase.value = "";
                    if (fMarca) fMarca.value = "";
                    if (fTexto) fTexto.value = "";
                    state.filtros = { clase_id: "", marca_id: "", q: "" };
                    cargarCatalogo();
                });
            }
            
            await cargarCatalogo();
            await cargarCarrito();
        }
        
        if (path === "/pagar") {
            await cargarMetodosPago();
            setupFormularioDinamico();
            
            const btnPagar = document.getElementById("btn-pagar");
            const btnVolver = document.getElementById("btn-volver");
            
            if (btnPagar) btnPagar.addEventListener("click", () => procesarPago());
            if (btnVolver) btnVolver.addEventListener("click", () => window.location.href = "/catalogo");
            
            const carritoData = await fetchJson("/api/carrito");
            const resumenContainer = document.getElementById("resumen-carrito");
            if (resumenContainer && carritoData.items?.length) {
                // Recalculate totals using paralelo for Bs and convert to USD via tasa oficial
                    const totalBs = (carritoData.items || []).reduce((sum, i) => sum + (Number(i.precio_usd) * (carritoData.tasas?.paralelo || state.tasas.paralelo || state.tasas.oficial) * i.cantidad), 0);
                    const totalUsd = totalBs / (carritoData.tasas?.oficial || state.tasas.oficial || 1);
                    resumenContainer.innerHTML = `
                        <div class="resumen-card">
                            <h3>Resumen de compra</h3>
                            <ul>
                                ${carritoData.items.map(i => {
                                    const bsItem = Number(i.precio_usd) * (carritoData.tasas?.paralelo || state.tasas.paralelo || state.tasas.oficial) * i.cantidad;
                                    const usdItem = bsItem / (carritoData.tasas?.oficial || state.tasas.oficial || 1);
                                    return `<li>${i.cantidad}x ${i.nombre} - ${formatUSD(usdItem)} / ${formatVES(bsItem)}</li>`;
                                }).join('')}
                            </ul>
                            <div class="resumen-total">Total: ${formatUSD(totalUsd)} / ${formatVES(totalBs)}</div>
                        </div>
                    `;
            }
        }
        
        if (path === "/admin/validar-pagos") {
            await cargarProductosParaSelect();
            
            const btnVentaLocal = document.getElementById("btn-venta-local");
            const ventaLocalModal = document.getElementById("venta-local-modal");
            const formVentaLocal = document.getElementById("form-venta-local");
            const btnAgregarProducto = document.getElementById("agregar-producto-local");
            
            if (btnVentaLocal) {
                btnVentaLocal.addEventListener("click", () => {
                    if (ventaLocalModal) ventaLocalModal.classList.remove("is-hidden");
                });
            }
            
            if (btnAgregarProducto) {
                btnAgregarProducto.addEventListener("click", () => agregarItemLocal());
            }
            
            if (formVentaLocal) {
                formVentaLocal.addEventListener("submit", registrarVentaLocal);
            }
            
            document.querySelectorAll(".tab-btn").forEach(btn => {
                btn.addEventListener("click", () => {
                    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
                    btn.classList.add("active");
                    
                    const tab = btn.dataset.tab;
                    document.querySelectorAll(".tab-content").forEach(content => content.classList.add("is-hidden"));
                    document.getElementById(`${tab}-tab`)?.classList.remove("is-hidden");
                    
                    if (tab === "pendientes") cargarPagosPendientes();
                    else if (tab === "aprobados") cargarPagosAprobados();
                    else if (tab === "rechazados") cargarPagosRechazados();
                });
            });
            
            document.getElementById("cancelar-rechazo")?.addEventListener("click", cerrarModalRechazo);
            document.getElementById("confirmar-rechazo")?.addEventListener("click", confirmarRechazo);
            
            await cargarPagosPendientes();
        }
    }
    
    document.addEventListener("DOMContentLoaded", init);
})();