(() => {
  "use strict";

  const state = {
    productos: [],
    masVendidos: [],
    carrito: [],
    filtros: { clase_id: "", marca_id: "", q: "" },
    paginacion: { pagina: 1, por_pagina: 12 },
    tasas: { oficial: 520.91, paralelo: 710.12 },
  };

  let facturaPendiente = null;
  let carritoItems = [];

  function getAuthToken() {
    return (
      localStorage.getItem("access_token") ||
      sessionStorage.getItem("access_token") ||
      ""
    );
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

    // Si es FormData, no establecer Content-Type (el navegador lo hace)
    if (!(options.body instanceof FormData)) {
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

  function formatUSD(amount) {
    return `$${Number(amount).toFixed(2)}`;
  }

  function formatVES(amount) {
    return `Bs ${Number(amount).toFixed(2)}`;
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
            border-radius: 12px;
            z-index: 10000;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;

    document.body.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transition = "opacity 0.3s";
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  // ==================== CATÁLOGO ====================

  function setCatalogStatus(message, type = "loading", actionsHtml = "") {
    const status = document.getElementById("catalog-status");
    if (!status) return;

    if (!message) {
      status.className = "catalog-status";
      status.innerHTML = "";
      return;
    }

    const spinner =
      type === "loading"
        ? '<span class="catalog-spinner" aria-hidden="true"></span>'
        : "";
    status.className = `catalog-status is-visible catalog-status--${type}`;
    status.innerHTML = `
            <div class="catalog-status__content">
                ${spinner}
                <span>${escapeHtml(message)}</span>
            </div>
            ${actionsHtml ? `<div class="catalog-status__actions">${actionsHtml}</div>` : ""}
        `;
  }

  function renderCatalogLoading() {
    const container = document.getElementById("productos-grid");
    if (!container) return;

    container.innerHTML = Array.from({ length: 8 })
      .map(
        () => `
            <article class="producto-card producto-card--skeleton" aria-hidden="true">
                <div class="skeleton-block skeleton-block--image"></div>
                <div class="skeleton-block skeleton-block--line"></div>
                <div class="skeleton-block skeleton-block--line short"></div>
                <div class="skeleton-block skeleton-block--line"></div>
            </article>
        `,
      )
      .join("");
  }

  function renderCatalogError(message) {
    const container = document.getElementById("productos-grid");
    if (!container) return;

    container.innerHTML = `
            <div class="catalog-error-box">
                <p>No fue posible cargar el catálogo.</p>
                <p>${escapeHtml(message)}</p>
                <button class="btn btn--yellow" id="catalog-retry" type="button">Reintentar</button>
            </div>
        `;

    const retry = document.getElementById("catalog-retry");
    if (retry) {
      retry.addEventListener("click", () => cargarCatalogo());
    }
  }

  async function cargarCatalogo() {
    setCatalogStatus("Cargando productos...", "loading");
    renderCatalogLoading();

    const params = new URLSearchParams();
    if (state.filtros.clase_id) params.set("clase_id", state.filtros.clase_id);
    if (state.filtros.marca_id) params.set("marca_id", state.filtros.marca_id);
    if (state.filtros.q) params.set("q", state.filtros.q);

    try {
      const data = await fetchJson(`/api/catalogo/productos?${params}`);
      state.productos = data.productos || [];
      state.masVendidos = data.mas_vendidos || [];
      state.tasas = data.tasas || state.tasas;
      window.tasas = state.tasas;

      renderProductos();
      renderMasVendidos();
      renderTasas();
      renderFiltros(data.clases, data.marcas);
      setCatalogStatus("");
    } catch (err) {
      state.productos = [];
      state.masVendidos = [];
      renderCatalogError(err.message);
      setCatalogStatus(
        err.message === "Autenticación requerida."
          ? "Inicia sesión para ver el catálogo completo."
          : "No pudimos cargar el catálogo.",
        "error",
        '<button class="catalog-retry" type="button" id="catalog-status-retry">Reintentar</button>',
      );

      const retry = document.getElementById("catalog-status-retry");
      if (retry) {
        retry.addEventListener("click", () => cargarCatalogo());
      }
    }
  }

  async function handleAgregarClick(e) {
    const btn = e.currentTarget;
    const inventarioId = btn.dataset.id;
    if (inventarioId) {
      await agregarCarrito(inventarioId, 1);
    }
  }

  function renderProductos() {
    const container = document.getElementById("productos-grid");
    const count = document.getElementById("productos-count");
    if (!container) return;

    if (count) {
      count.textContent = `${state.productos.length} producto${state.productos.length === 1 ? "" : "s"}`;
    }

    if (!state.productos.length) {
      container.innerHTML =
        '<div class="catalog-empty"><p>No se encontraron productos con esos filtros.</p></div>';
      return;
    }

    container.innerHTML = state.productos
      .map((p) => {
        const precioUsd = Number(p.precio_usd || 0);
        const bsFinal =
          precioUsd * (state.tasas.paralelo || state.tasas.oficial);
        const imagenSrc =
          p.imagen && p.imagen.trim()
            ? p.imagen
            : "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=900&q=80";
        const stockNum = Number(p.stock);
        const avisoStockBajo =
          Number.isFinite(stockNum) && stockNum > 0 && stockNum <= 5
            ? '<div class="producto-stock producto-stock--low">Pocas unidades disponibles</div>'
            : "";

        return `
                <div class="producto-card">
                    <div class="producto-imagen">
                        <img src="${escapeHtml(imagenSrc)}" alt="${escapeHtml(p.nombre)}" loading="lazy" decoding="async" onerror="this.onerror=null;this.src='https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=900&q=80';">
                    </div>
                    <div class="producto-nombre">${escapeHtml(p.nombre)}</div>
                    <div class="producto-marca">${escapeHtml(p.marca)}</div>
                    <div class="producto-precios">
                        <div class="precio-usd">${formatUSD(precioUsd)}</div>
                        <div class="precio-bs">${formatVES(bsFinal)}</div>
                    </div>
                    ${avisoStockBajo}
                    <button class="btn btn--yellow btn-agregar" data-id="${p.id}" ${p.stock <= 0 ? "disabled" : ""}>
                        ${p.stock > 0 ? "Agregar al carrito" : "Agotado"}
                    </button>
                </div>
            `;
      })
      .join("");

    document.querySelectorAll(".btn-agregar").forEach((btn) => {
      btn.removeEventListener("click", handleAgregarClick);
      btn.addEventListener("click", handleAgregarClick);
    });
  }

  function renderMasVendidos() {
    const container = document.getElementById("mas-vendidos");
    if (!container) return;

    if (!state.masVendidos.length) {
      container.innerHTML = "<p>Sin datos</p>";
      return;
    }

    container.innerHTML = state.masVendidos
      .map((p) => {
        const precioUsd = Number(p.precio_usd || 0);
        return `
                <div class="mas-vendido-item">
                    <span>${escapeHtml(p.nombre)}</span>
                    <strong>${formatUSD(precioUsd)}</strong>
                </div>
            `;
      })
      .join("");
  }

  function renderTasas() {
    const container = document.getElementById("tasas-info");
    if (!container) return;

    container.innerHTML = `
            <div>Oficial: 1 USD = ${formatVES(state.tasas.oficial)}</div>
            <small>Los precios se calculan al momento del pago</small>
        `;
  }

  function setupCatalogSearchToggle() {
    const searchToggle = document.getElementById("catalog-search-toggle");
    const searchBox = document.getElementById("catalog-search-box");
    const searchInput = document.getElementById("f-texto");
    if (!searchToggle || !searchBox) return;

    const abrirBusqueda = () => {
      searchBox.classList.add("is-open");
      searchBox.setAttribute("aria-hidden", "false");
      searchToggle.setAttribute("aria-expanded", "true");
      window.setTimeout(() => {
        searchInput?.focus();
      }, 220);
    };

    const cerrarBusqueda = () => {
      searchBox.classList.remove("is-open");
      searchBox.setAttribute("aria-hidden", "true");
      searchToggle.setAttribute("aria-expanded", "false");
    };

    searchToggle.addEventListener("click", () => {
      const abierta = searchBox.classList.contains("is-open");
      if (abierta) {
        cerrarBusqueda();
      } else {
        abrirBusqueda();
      }
    });
  }

  function renderFiltros(clases, marcas) {
    const claseSelect = document.getElementById("f-clase");
    const marcaSelect = document.getElementById("f-marca");

    if (claseSelect && clases) {
      claseSelect.innerHTML =
        '<option value="">Todas</option>' +
        clases
          .map(
            (c) => `<option value="${c.id}">${escapeHtml(c.nombre)}</option>`,
          )
          .join("");
    }

    if (marcaSelect && marcas) {
      marcaSelect.innerHTML =
        '<option value="">Todas</option>' +
        marcas
          .map(
            (m) => `<option value="${m.id}">${escapeHtml(m.nombre)}</option>`,
          )
          .join("");
    }
  }

  // ==================== CARRITO ====================

async function cargarCarrito() {
    const container = document.getElementById("cart-items");
    if (container) {
        container.innerHTML =
            '<div class="catalog-empty"><p>Cargando carrito...</p></div>';
    }

    try {
        const data = await fetchJson("/api/carrito");
        console.log("Datos del carrito desde backend:", data);
        
        // Los items pueden venir en diferentes formatos
        let items = [];
        
        if (data.items && Array.isArray(data.items)) {
            items = data.items;
        } else if (data.carrito && Array.isArray(data.carrito)) {
            items = data.carrito;
        } else if (Array.isArray(data)) {
            items = data;
        }
        
        console.log("Items encontrados:", items);
        
        if (items.length > 0) {
            carritoItems = items.map(item => {
                console.log("Item raw:", item);
                
                // Intentar obtener el ID desde diferentes claves
                const id = item.ID_inventario || item.producto_id || item.id || item.inventario_id;
                
                // Intentar obtener el precio desde diferentes claves
                const precio = parseFloat(item.Costo_venta || item.precio_usd || item.precio || 0);
                
                // Intentar obtener la cantidad desde diferentes claves
                const cantidad = parseInt(item.Cantidad_producto || item.cantidad || 0);
                
                // Intentar obtener el nombre desde diferentes claves
                const nombre = item.Nombre_producto || item.nombre || item.N_modelo || "Producto";
                
                // Intentar obtener la marca desde diferentes claves
                const marca = item.Nombre_marca || item.marca || "";
                
                // Intentar obtener la imagen desde diferentes claves
                const imagen = item.Foto_inventario || item.imagen || "";
                
                // Intentar obtener el stock desde diferentes claves
                const stock = parseInt(item.Existencia || item.stock_disponible || item.stock || 0);
                
                const itemNormalizado = {
                    // Claves para ventas.js
                    producto_id: id,
                    precio_usd: precio,
                    cantidad: cantidad,
                    nombre: nombre,
                    marca: marca,
                    imagen: imagen,
                    stock_disponible: stock,
                    id: id,
                    precio: precio,
                    
                    // Mantener claves originales para compatibilidad
                    ID_inventario: id,
                    Costo_venta: precio,
                    Cantidad_producto: cantidad,
                    Nombre_producto: nombre,
                    Nombre_marca: marca,
                    Foto_inventario: imagen,
                    Existencia: stock
                };
                
                console.log("Item normalizado:", itemNormalizado);
                return itemNormalizado;
            });
        } else {
            carritoItems = [];
        }
        
        console.log("Carrito final:", carritoItems);
        
        actualizarBadgeCarrito();
        renderCarritoModal();
        return data;
    } catch (err) {
        console.error("Error cargando carrito:", err);
        if (container) {
            const carritoMsg =
                err.message === "Autenticación requerida."
                    ? "Inicia sesión para guardar y consultar tu carrito."
                    : err.message;
            container.innerHTML = `<div class="catalog-error-box"><p>No se pudo cargar el carrito.</p><p>${escapeHtml(carritoMsg)}</p></div>`;
        }
        carritoItems = [];
        actualizarBadgeCarrito();
        renderCarritoModal();
        return null;
    }
}

async function agregarCarrito(inventarioId, cantidad) {
    try {
        console.log("Agregando al carrito:", { inventarioId, cantidad });
        
        const response = await fetchJson("/api/carrito", {
            method: "POST",
            body: JSON.stringify({ 
                producto_id: inventarioId,
                cantidad: cantidad 
            }),
        });
        
        console.log("Respuesta:", response);
        
        if (response.success) {
            await cargarCarrito();
            mostrarToast("Producto agregado al carrito", "success");
        } else {
            mostrarToast(response.error || "Error al agregar al carrito", "error");
        }
    } catch (err) {
        console.error("Error:", err);
        mostrarToast(err.message, "error");
    }
}

async function actualizarCantidadCarrito(inventarioId, cantidad) {
    if (cantidad <= 0) {
        await fetchJson(`/api/carrito/${inventarioId}`, { method: "DELETE" });
    } else {
        await fetchJson("/api/carrito", {
            method: "PUT",
            body: JSON.stringify({ 
                producto_id: inventarioId,
                cantidad: cantidad 
            }),
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
    const badges = document.querySelectorAll("#cart-count, #cart-nav-count");
    const total = carritoItems.reduce(
        (sum, item) => sum + (item.cantidad || 0),
        0,
    );

    badges.forEach((badge) => {
        if (badge) {
            badge.textContent = total;
            badge.style.display = total > 0 ? "flex" : "none";
        }
    });
}

async function handleIncrement(e) {
    const btn = e.currentTarget;
    const inventarioId = btn.dataset.id;
    const item = carritoItems.find(
        (i) => String(i.producto_id || i.ID_inventario || i.id) === String(inventarioId),
    );
    if (item) {
        const stockDisponible = item.stock_disponible || item.Existencia || 0;
        const nuevaCantidad = (item.cantidad || item.Cantidad_producto || 0) + 1;
        if (nuevaCantidad <= stockDisponible) {
            await actualizarCantidadCarrito(inventarioId, nuevaCantidad);
        } else {
            mostrarToast(`Solo hay ${stockDisponible} unidades disponibles`, "error");
        }
    }
}

async function handleDecrement(e) {
    const btn = e.currentTarget;
    const inventarioId = btn.dataset.id;
    const item = carritoItems.find(
        (i) => String(i.producto_id || i.ID_inventario || i.id) === String(inventarioId),
    );
    if (item) {
        const nuevaCantidad = (item.cantidad || item.Cantidad_producto || 0) - 1;
        if (nuevaCantidad >= 0) {
            await actualizarCantidadCarrito(inventarioId, nuevaCantidad);
        }
    }
}


async function handleRemove(e) {
    const btn = e.currentTarget;
    const inventarioId = btn.dataset.id;
    await actualizarCantidadCarrito(inventarioId, 0);
}

function renderCarritoModal() {
    const container = document.getElementById("cart-items");
    const totalUsdSpan = document.getElementById("cart-total-usd");
    const totalBsSpan = document.getElementById("cart-total-bs");

    if (!container) return;

    console.log("Renderizando carrito, items:", carritoItems);

    if (!carritoItems || carritoItems.length === 0) {
        container.innerHTML =
            '<p class="carrito-vacio">Tu carrito está vacío</p>';
        if (totalUsdSpan) totalUsdSpan.textContent = formatUSD(0);
        if (totalBsSpan) totalBsSpan.textContent = formatVES(0);
        return;
    }

    const tasas = window.tasas || state.tasas;
    let totalUsd = 0;

    container.innerHTML = carritoItems
        .map((item) => {
            const inventarioId = item.producto_id || item.ID_inventario || item.id;
            const precioUsd = Number(item.precio_usd || item.Costo_venta || item.precio || 0);
            const cantidad = Number(item.cantidad || item.Cantidad_producto || 0);
            const nombre = item.nombre || item.Nombre_producto || "Producto";
            const marca = item.marca || item.Nombre_marca || "";
            const subtotalUsd = precioUsd * cantidad;

            totalUsd += subtotalUsd;

            const imagenSrc =
                item.imagen || item.Foto_inventario
                    ? item.imagen || item.Foto_inventario
                    : "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=900&q=80";

            return `
                <div class="cart-item" data-producto-id="${inventarioId}">
                    <div class="cart-item-imagen">
                        <img src="${escapeHtml(imagenSrc)}" alt="${escapeHtml(nombre)}" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=900&q=80'">
                    </div>
                    <div class="cart-item-info">
                        <div class="cart-item-name">${escapeHtml(nombre)}</div>
                        <div class="cart-item-marca">${escapeHtml(marca)}</div>
                        <div class="cart-item-price">${formatUSD(precioUsd)}</div>
                    </div>
                    <div class="cart-item-controls">
                        <button class="icon-action cart-decrement" data-id="${inventarioId}" title="Disminuir cantidad">-</button>
                        <span class="cart-item-qty">${cantidad}</span>
                        <button class="icon-action cart-increment" data-id="${inventarioId}" title="Aumentar cantidad">+</button>
                        <button class="icon-action icon-action--danger cart-remove" data-id="${inventarioId}" title="Eliminar producto">🗑</button>
                    </div>
                </div>
            `;
        })
        .join("");

    const totalBs = totalUsd * (tasas.paralelo || tasas.oficial);

    if (totalUsdSpan) totalUsdSpan.textContent = formatUSD(totalUsd);
    if (totalBsSpan) totalBsSpan.textContent = formatVES(totalBs);

    setTimeout(() => {
        document.querySelectorAll(".cart-increment").forEach((btn) => {
            btn.removeEventListener("click", handleIncrement);
            btn.addEventListener("click", handleIncrement);
        });

        document.querySelectorAll(".cart-decrement").forEach((btn) => {
            btn.removeEventListener("click", handleDecrement);
            btn.addEventListener("click", handleDecrement);
        });

        document.querySelectorAll(".cart-remove").forEach((btn) => {
            btn.removeEventListener("click", handleRemove);
            btn.addEventListener("click", handleRemove);
        });
    }, 10);
}

  function openCartModal() {
    const modal = document.getElementById("cart-modal");
    if (modal) {
      modal.classList.remove("is-hidden");
      document.body.style.overflow = "hidden";
    }
  }

  function closeModal() {
    document.querySelectorAll(".modal:not(.is-hidden)").forEach((modal) => {
      modal.classList.add("is-hidden");
    });
    document.body.style.overflow = "";
  }

  async function iniciarCheckout() {
    if (!carritoItems.length) {
      mostrarToast("El carrito está vacío", "error");
      return;
    }
    window.location.href = "/pagar";
  }

  // ==================== PROCESO DE PAGO ====================

  async function cargarMetodosPago() {
    const data = await fetchJson("/api/metodos-pago");
    const select = document.getElementById("metodo-pago");
    if (select) {
      select.innerHTML =
        '<option value="">-- Selecciona --</option>' +
        data.metodos
          .map(
            (m) => `<option value="${m.id}">${m.nombre} (${m.moneda})</option>`,
          )
          .join("");
    }
  }

  // Previsualizar imagen seleccionada
  let previewUrl = null;

  function previewImagen(input) {
    const previewContainer = document.getElementById("capture-preview");
    if (!previewContainer) return;

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    const file = input.files[0];
    if (file) {
      previewUrl = URL.createObjectURL(file);
      previewContainer.innerHTML = `
                <img src="${previewUrl}" alt="Vista previa del comprobante" class="comprobante-preview">
                <small class="comprobante-nombre">${file.name} (${(file.size / 1024).toFixed(2)} KB)</small>
            `;
    } else {
      previewContainer.innerHTML = "";
    }
  }

  function getFormularioPagoHtml(metodo) {
    const today = new Date().toISOString().split("T")[0];

    let formHtml = `
        <div class="form-pago">
            <h4>${
                metodo === "pago_movil"
                    ? "Pago Móvil (Bolívares)"
                    : metodo === "zelle"
                      ? "Zelle (Dólares)"
                      : metodo === "binance"
                        ? "Binance (USDT)"
                        : metodo === "efectivo_bs"
                          ? "Efectivo (Bolívares)"
                          : metodo === "efectivo_usd"
                            ? "Efectivo (Dólares)"
                            : "Método de pago"
            }</h4>
            
            <label class="field">
                <span class="field__label">Fecha del Pago</span>
                <input type="date" name="fecha_pago" value="${today}" max="${today}" required>
                <small class="field-hint">Solo se permiten fechas actuales o anteriores</small>
            </label>
            
            <label class="field">
                <span class="field__label">Número de Referencia / Transacción</span>
                <input type="text" name="referencia" placeholder="Ej: REF-123456789" required>
                <small class="field-hint">Número de operación, referencia bancaria o ID de transacción</small>
            </label>
            
            <label class="field">
                <span class="field__label">Monto Pagado</span>
                <input type="number" name="monto" step="0.01" placeholder="0.00" required>
                <small class="field-hint">Monto exacto que pagaste</small>
            </label>`;

    // Para métodos que requieren comprobante (no efectivo)
    if (metodo !== "efectivo_bs" && metodo !== "efectivo_usd") {
        formHtml += `
            <label class="field">
                <span class="field__label">Comprobante de Pago (Capture)</span>
                <input type="file" name="capture" accept="image/*" data-capture-input required>
                <small class="field-hint">Sube una imagen del comprobante (JPG, PNG, máximo 5MB)</small>
            </label>
            <div id="capture-preview" class="capture-preview"></div>`;
    }

    formHtml += `
            <div class="pago-info">${
                metodo !== "efectivo_bs" && metodo !== "efectivo_usd"
                    ? "El comprobante será verificado por nuestro equipo."
                    : "Pago confirmado al momento de la entrega."
            }</div>
        </div>
    `;

    return formHtml;
  }

  function setupFormularioDinamico() {
    const select = document.getElementById("metodo-pago");
    const container = document.getElementById("form-pago-container");

    if (select && container) {
      select.addEventListener("change", () => {
        const metodo = select.value;
        if (metodo) {
          container.innerHTML = getFormularioPagoHtml(metodo);

          // Configurar preview de imagen
          const captureInput = container.querySelector("[data-capture-input]");
          if (captureInput) {
            captureInput.addEventListener("change", function () {
              previewImagen(this);
            });
          }
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
      mostrarToast("Selecciona un método de pago", "error");
      return;
    }

    const formData = new FormData();
    const formContainer = document.getElementById("form-pago-container");

    if (formContainer) {
      // Fecha del pago
      const fechaInput = formContainer.querySelector(
        "input[name='fecha_pago']",
      );
      if (fechaInput && fechaInput.value) {
        formData.append("fecha_pago", fechaInput.value);
      }

      // Referencia
      const referenciaInput = formContainer.querySelector(
        "input[name='referencia']",
      );
      if (referenciaInput && referenciaInput.value) {
        formData.append("referencia", referenciaInput.value);
        console.log("Referencia capturada:", referenciaInput.value);
      } else {
        mostrarToast("Debes ingresar el número de referencia", "error");
        return;
      }

      // Monto
      const montoInput = formContainer.querySelector("input[name='monto']");
      if (montoInput && montoInput.value) {
        formData.append("monto", montoInput.value);
        console.log("Monto capturado:", montoInput.value);
      } else {
        mostrarToast("Debes ingresar el monto pagado", "error");
        return;
      }

      // Para métodos que requieren comprobante
      if (metodo !== "efectivo_bs" && metodo !== "efectivo_usd") {
        const captureFile = formContainer.querySelector("[data-capture-input]")
          ?.files[0];
        if (!captureFile) {
          mostrarToast("Debes subir el comprobante de pago", "error");
          return;
        }

        if (!captureFile.type.startsWith("image/")) {
          mostrarToast("Solo se permiten archivos de imagen", "error");
          return;
        }

        if (captureFile.size > 5 * 1024 * 1024) {
          mostrarToast("La imagen no puede superar los 5MB", "error");
          return;
        }

        formData.append("capture", captureFile);
      }
    }

    formData.append("metodo_pago", metodo);

    try {
      const authToken = getAuthToken();
      const csrfToken = getCsrfToken();

      const response = await fetch("/api/procesar-pago", {
        method: "POST",
        headers: {
          Accept: "application/json",
          ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
          ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
        },
        credentials: "same-origin",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok || data.success === false) {
        throw new Error(data.error || "Error al procesar el pago");
      }

      facturaPendiente = data.factura_id;
      mostrarToast("¡Pago registrado! Redirigiendo...", "success");
      window.setTimeout(() => {
        window.location.href = "/catalogo";
      }, 2000);
    } catch (err) {
      mostrarToast(err.message, "error");
    }
  }

  // ==================== VALIDACIÓN DE PAGOS ====================

  async function cargarPagosPendientes() {
    try {
      const data = await fetchJson("/api/admin/pagos-pendientes");
      renderPagosList(data.pagos, "pendientes");
    } catch (err) {
      console.warn("Error cargando pagos pendientes:", err);
    }
  }

  function renderPagosList(pagos, tipo) {
    const container = document.getElementById(`${tipo}-list`);
    if (!container) return;

    if (!pagos || !pagos.length) {
      container.innerHTML =
        '<p class="sin-resultados">No hay pagos en esta lista</p>';
      return;
    }

    container.innerHTML = pagos
      .map(
        (p) => `
            <div class="pago-card" data-factura="${p.factura_id}">
                <div class="info-row"><strong>Factura:</strong> <span>${escapeHtml(p.factura_id)}</span></div>
                <div class="info-row"><strong>Fecha:</strong> <span>${escapeHtml(p.fecha)}</span></div>
                <div class="info-row"><strong>Cliente:</strong> <span>${escapeHtml(p.cliente_nombre)} ${escapeHtml(p.cliente_apellido || "")}</span></div>
                <div class="info-row"><strong>Teléfono:</strong> <span>${escapeHtml(p.cliente_celular || "N/A")}</span></div>
                <div class="info-row"><strong>Método:</strong> <span>${escapeHtml(p.metodo_pago)}</span></div>
                ${p.capture ? `<div class="info-row"><strong>Comprobante:</strong> <a href="${p.capture}" target="_blank">Ver imagen</a></div>` : ""}
                ${
                  tipo === "pendientes"
                    ? `
                    <div class="pago-actions">
                        <button class="btn btn--yellow btn-aprobar" data-factura="${p.factura_id}">Aprobar</button>
                        <button class="btn btn--ghost btn-rechazar" data-factura="${p.factura_id}">Rechazar</button>
                    </div>
                `
                    : ""
                }
            </div>
        `,
      )
      .join("");

    if (tipo === "pendientes") {
      document.querySelectorAll(".btn-aprobar").forEach((btn) => {
        btn.addEventListener("click", () => aprobarPago(btn.dataset.factura));
      });
      document.querySelectorAll(".btn-rechazar").forEach((btn) => {
        btn.addEventListener("click", () =>
          mostrarModalRechazo(btn.dataset.factura),
        );
      });
    }
  }

  async function aprobarPago(facturaId) {
    if (confirm("¿Aprobar este pago?")) {
      try {
        await fetchJson(`/api/admin/aprobar-pago/${facturaId}`, {
          method: "POST",
        });
        mostrarToast("Pago aprobado", "success");
        cargarPagosPendientes();
      } catch (err) {
        mostrarToast(err.message, "error");
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
      mostrarToast("Debes escribir un motivo", "error");
      return;
    }

    try {
      await fetchJson(`/api/admin/rechazar-pago/${facturaRechazoActual}`, {
        method: "POST",
        body: JSON.stringify({ motivo }),
      });
      mostrarToast("Pago rechazado", "success");
      cerrarModalRechazo();
      cargarPagosPendientes();
    } catch (err) {
      mostrarToast(err.message, "error");
    }
  }

  function cerrarModalRechazo() {
    const modal = document.getElementById("rechazo-modal");
    if (modal) modal.classList.add("is-hidden");
    facturaRechazoActual = null;
  }

  // ==================== VENTA LOCAL ====================

  let itemsLocal = [];
  let clientesMap = {};

  async function cargarProductosParaSelect() {
    try {
      const data = await fetchJson("/api/catalogo/productos");
      const select = document.getElementById("producto-select");
      if (select) {
        select.innerHTML =
          '<option value="">-- Selecciona --</option>' +
          (data.productos || [])
            .map(
              (p) =>
                `<option value="${p.id}" data-precio="${p.precio_usd}">${p.nombre} - ${formatUSD(p.precio_usd)}</option>`,
            )
            .join("");
      }
    } catch (err) {
      console.warn("Error cargando productos:", err);
    }
  }

  async function cargarClientesParaDatalist() {
    try {
      const data = await fetchJson("/api/clientes");
      const list = document.getElementById("clientes-list");
      if (!list) return;
      clientesMap = {};
      const clientes = data.clientes || [];
      list.innerHTML = clientes
        .map((c) => {
          const text = `${c.id} - ${c.nombre} ${c.apellido || ""}`.trim();
          clientesMap[String(c.id)] = c.id;
          clientesMap[
            (c.nombre + " " + (c.apellido || "")).trim().toLowerCase()
          ] = c.id;
          return `<option value="${escapeHtml(text)}"></option>`;
        })
        .join("");
    } catch (err) {
      console.warn("Error cargando clientes:", err);
    }
  }

  function agregarItemLocal() {
    const select = document.getElementById("producto-select");
    const cantidad = parseInt(
      document.getElementById("cantidad-local")?.value || 1,
    );
    const productoId = select?.value;

    if (!productoId) {
      mostrarToast("Selecciona un producto", "error");
      return;
    }

    const option = select.options[select.selectedIndex];
    const nombre = option.text.split(" - ")[0];
    const precio = parseFloat(option.dataset.precio);

    const existente = itemsLocal.find((i) => i.producto_id == productoId);
    if (existente) {
      existente.cantidad += cantidad;
    } else {
      itemsLocal.push({
        producto_id: parseInt(productoId),
        nombre,
        precio_usd: precio,
        cantidad,
      });
    }

    renderItemsLocal();
    select.value = "";
    document.getElementById("cantidad-local").value = 1;
  }

  function renderItemsLocal() {
    const container = document.getElementById("items-local-list");
    if (!container) return;

    if (!itemsLocal.length) {
      container.innerHTML =
        '<p class="sin-resultados">No hay productos agregados</p>';
      return;
    }

    const totalBs = itemsLocal.reduce(
      (sum, i) =>
        sum +
        Number(i.precio_usd) *
          (state.tasas.paralelo || state.tasas.oficial) *
          i.cantidad,
      0,
    );
    const totalUsd = totalBs / (state.tasas.oficial || 1);

    container.innerHTML = `
            <div class="items-local">
                ${itemsLocal
                  .map(
                    (item, idx) => `
                    <div class="cart-item">
                        <span>${escapeHtml(item.nombre)} x${item.cantidad}</span>
                        <span>${formatUSD(Number(item.precio_usd) * item.cantidad)} / ${formatVES(Number(item.precio_usd) * (state.tasas.paralelo || state.tasas.oficial) * item.cantidad)}</span>
                        <button class="icon-action" data-remove="${idx}" aria-label="Eliminar producto">🗑</button>
                    </div>
                `,
                  )
                  .join("")}
                <div class="cart-total">
                    <strong>Total: ${formatUSD(totalUsd)} / ${formatVES(totalBs)}</strong>
                </div>
            </div>
        `;

    document.querySelectorAll("[data-remove]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const idx = parseInt(btn.dataset.remove);
        itemsLocal.splice(idx, 1);
        renderItemsLocal();
      });
    });
  }

  async function registrarVentaLocal(event) {
    event.preventDefault();

    const clienteInput = document.getElementById("cliente-id")?.value || "";
    let clienteId = null;
    const v = String(clienteInput).trim();
    if (/^\d+$/.test(v)) {
      clienteId = parseInt(v);
    } else if (v.includes(" - ")) {
      const parts = v.split(" - ");
      if (/^\d+$/.test(parts[0].trim())) clienteId = parseInt(parts[0].trim());
    } else {
      const lookup = v.toLowerCase();
      if (clientesMap[lookup]) clienteId = clientesMap[lookup];
    }
    const metodoPago = document.getElementById("metodo-local")?.value;

    if (!clienteId) {
      mostrarToast(
        "Cliente no encontrado. Escribe ID o selecciona un cliente válido.",
        "error",
      );
      return;
    }
    if (!itemsLocal.length) {
      mostrarToast("Agrega al menos un producto", "error");
      return;
    }

    try {
      await fetchJson("/api/admin/ventas-local", {
        method: "POST",
        body: JSON.stringify({
          cliente_id: parseInt(clienteId),
          items: itemsLocal,
          metodo_pago: metodoPago,
        }),
      });

      mostrarToast("Venta registrada exitosamente", "success");
      itemsLocal = [];
      renderItemsLocal();
      closeModal();
      document.getElementById("form-venta-local")?.reset();
    } catch (err) {
      mostrarToast(err.message, "error");
    }
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

  // ==================== INICIALIZACIÓN ====================

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

    const navCartBtn = document.getElementById("cart-nav-btn");
    if (navCartBtn) {
      navCartBtn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        openCartModal();
      });
    }

    if (path === "/catalogo") {
      const cartToggle = document.getElementById("cart-toggle");
      const cartVaciar = document.getElementById("cart-vaciar");
      const cartCheckout = document.getElementById("cart-checkout");
      const fClase = document.getElementById("f-clase");
      const fMarca = document.getElementById("f-marca");
      const fTexto = document.getElementById("f-texto");

      const aplicarFiltros = () => {
        state.filtros.clase_id = fClase?.value || "";
        state.filtros.marca_id = fMarca?.value || "";
        state.filtros.q = (fTexto?.value || "").trim();
        cargarCatalogo();
      };

      if (cartToggle)
        cartToggle.addEventListener("click", () => openCartModal());
      if (cartVaciar)
        cartVaciar.addEventListener("click", () => vaciarCarrito());
      if (cartCheckout)
        cartCheckout.addEventListener("click", () => iniciarCheckout());
      setupCatalogSearchToggle();

      if (fClase) fClase.addEventListener("change", aplicarFiltros);
      if (fMarca) fMarca.addEventListener("change", aplicarFiltros);
      if (fTexto) {
        fTexto.addEventListener("keydown", (e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            aplicarFiltros();
          }
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
      if (btnVolver)
        btnVolver.addEventListener(
          "click",
          () => (window.location.href = "/catalogo"),
        );

      try {
        const carritoData = await fetchJson("/api/carrito");
        const resumenContainer = document.getElementById("resumen-carrito");
        if (resumenContainer && carritoData.items?.length) {
          const tasas = carritoData.tasas || state.tasas;
          const totalBs = carritoData.items.reduce(
            (sum, i) =>
              sum +
              Number(i.precio_usd) *
                (tasas.paralelo || tasas.oficial) *
                i.cantidad,
            0,
          );
          const totalUsd = totalBs / (tasas.oficial || 1);
          resumenContainer.innerHTML = `
                        <div class="resumen-card">
                            <h3>Resumen de compra</h3>
                            <ul>
                                ${carritoData.items
                                  .map((i) => {
                                    const bsItem =
                                      Number(i.precio_usd) *
                                      (tasas.paralelo || tasas.oficial) *
                                      i.cantidad;
                                    const usdItem =
                                      bsItem / (tasas.oficial || 1);
                                    return `<li>${i.cantidad}x ${i.nombre} - ${formatUSD(usdItem)} / ${formatVES(bsItem)}</li>`;
                                  })
                                  .join("")}
                            </ul>
                            <div class="resumen-total">Total: ${formatUSD(totalUsd)} / ${formatVES(totalBs)}</div>
                        </div>
                    `;
        }
      } catch (err) {
        console.warn("Error cargando resumen:", err);
      }
    }

    if (path === "/admin/validar-pagos") {
      await cargarProductosParaSelect();
      await cargarClientesParaDatalist();

      const btnVentaLocal = document.getElementById("btn-venta-local");
      const ventaLocalModal = document.getElementById("venta-local-modal");
      const formVentaLocal = document.getElementById("form-venta-local");
      const btnAgregarProducto = document.getElementById(
        "agregar-producto-local",
      );

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

      document.querySelectorAll(".tab-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
          document
            .querySelectorAll(".tab-btn")
            .forEach((b) => b.classList.remove("active"));
          btn.classList.add("active");

          const tab = btn.dataset.tab;
          document
            .querySelectorAll(".tab-content")
            .forEach((content) => content.classList.add("is-hidden"));
          document.getElementById(`${tab}-tab`)?.classList.remove("is-hidden");

          if (tab === "pendientes") cargarPagosPendientes();
        });
      });

      document
        .getElementById("cancelar-rechazo")
        ?.addEventListener("click", cerrarModalRechazo);
      document
        .getElementById("confirmar-rechazo")
        ?.addEventListener("click", confirmarRechazo);

      await cargarPagosPendientes();
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();