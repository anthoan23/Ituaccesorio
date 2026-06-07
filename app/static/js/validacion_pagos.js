(() => {
  "use strict";

  let facturaRechazoActual = null;
  let detallesAbiertos = new Set();

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

  function formatUSD(amount) {
    return `$${Number(amount).toFixed(2)}`;
  }

  function formatVES(amount) {
    return `Bs ${Number(amount).toFixed(2)}`;
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
        minute: "2-digit",
      });
    } catch {
      return dateString;
    }
  }

  async function cargarDetalleFactura(facturaId, detalleContainer) {
    console.log("=== INICIO cargarDetalleFactura ===");
    console.log("Factura ID:", facturaId);

    try {
      const url = `/api/validacion-pagos/venta/${facturaId}/detalle`;
      console.log("URL:", url);

      const response = await fetch(url, {
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${getAuthToken()}`,
        },
        credentials: "same-origin",
      });

      console.log("Response status:", response.status);

      const data = await response.json();
      console.log("Datos recibidos:", data);

      const items = data.detalle || [];
      console.log("Items encontrados:", items.length);

      if (items.length > 0) {
        let total = 0;
        let html = `
                <div class="productos-header">
                    <span>Producto</span>
                    <span>Cantidad</span>
                    <span>Subtotal</span>
                </div>
                <div class="productos-items">
            `;

        for (const item of items) {
          const subtotal = item.Costo_venta * item.Cantidad_articulo;
          total += subtotal;
          console.log(
            `Producto: ${item.Nombre_producto}, Cantidad: ${item.Cantidad_articulo}, Precio: ${item.Costo_venta}, Subtotal: ${subtotal}`,
          );

          html += `
                    <div class="producto-item">
                        <div class="producto-info">
                            <strong>${escapeHtml(item.Nombre_producto)}</strong>
                            <span class="producto-marca">${escapeHtml(item.marca || "")}</span>
                        </div>
                        <div class="producto-cantidad">
                            ${item.Cantidad_articulo}
                        </div>
                        <div class="producto-precio">
                            ${formatUSD(item.Costo_venta)} c/u
                            <span class="subtotal">(${formatUSD(subtotal)})</span>
                        </div>
                    </div>
                `;
        }

        html += `
                </div>
                <div class="productos-total">
                    <strong>TOTAL DE LA VENTA:</strong>
                    <strong class="total-amount">${formatUSD(total)}</strong>
                </div>
            `;

        detalleContainer.innerHTML = html;
        console.log("HTML generado correctamente, total:", total);
      } else {
        console.warn("No hay items para mostrar");
        detalleContainer.innerHTML = `
                <div class="empty-detalle">
                    📦 No hay productos registrados en esta venta
                </div>
            `;
      }
    } catch (err) {
      console.error("Error en cargarDetalleFactura:", err);
      detalleContainer.innerHTML = `
            <div class="error-detalle">
                ❌ Error: ${escapeHtml(err.message)}
            </div>
        `;
      mostrarToast(err.message, "error");
    }

    console.log("=== FIN cargarDetalleFactura ===");
  }

  async function toggleDetalle(facturaId, btnElement) {
    console.log("=== toggleDetalle ===");
    console.log("Factura ID:", facturaId);
    console.log("Botón:", btnElement);

    const detalleContainer = document.getElementById(`detalle-${facturaId}`);
    console.log("detalleContainer existe?", !!detalleContainer);

    if (detallesAbiertos.has(facturaId)) {
      console.log("Cerrando detalle");
      detalleContainer.style.display = "none";
      detallesAbiertos.delete(facturaId);
      btnElement.innerHTML = "📋 Ver productos";
      btnElement.classList.remove("active");
    } else {
      console.log("Abriendo detalle");
      detalleContainer.style.display = "block";
      detallesAbiertos.add(facturaId);
      btnElement.innerHTML = "⏳ Cargando...";
      btnElement.classList.add("active");

      detalleContainer.innerHTML =
        '<div class="loading-productos">🔄 Cargando productos...</div>';
      await cargarDetalleFactura(facturaId, detalleContainer);
      btnElement.innerHTML = "📋 Ocultar productos";
    }
  }

  function renderPagosList(pagos, tipo) {
    const container = document.getElementById(`${tipo}-list`);
    if (!container) return;

    if (!pagos || !pagos.length) {
      container.innerHTML =
        '<div class="empty-state">📭 No hay pagos en esta lista</div>';
        
      return;
    }

    console.log(`Renderizando ${pagos.length} pagos de tipo ${tipo}`);
    console.log("Primer pago:", pagos[0]);

    let html = "";

    for (const p of pagos) {
      let metodoIcono = "💳";
      if (p.metodo_pago === "pago_movil") metodoIcono = "📱";
      else if (p.metodo_pago === "zelle") metodoIcono = "🏦";
      else if (p.metodo_pago === "binance") metodoIcono = "₿";
      else if (p.metodo_pago === "efectivo_bs") metodoIcono = "💵";
      else if (p.metodo_pago === "efectivo_usd") metodoIcono = "💵";

      const captureImageHtml =
        p.capture_image && p.capture_image !== "NULL" && p.capture_image !== ""
          ? `
          <div class="capture-image">
            <img src="${escapeHtml(p.capture_image)}" alt="Comprobante de pago" onclick="window.open('${escapeHtml(p.capture_image)}', '_blank')" loading="lazy">
            <div style="font-size: 0.7rem; color: #888; margin-top: 0.5rem;">🖱️ Haz clic para ampliar</div>
          </div>
        `
          : '<div style="color: #999; font-size: 0.8rem; margin: 0.5rem 0; padding: 0.5rem; background: #f8f9fa; border-radius: 8px;">📷 Sin comprobante adjunto</div>';

      // Formatear monto según moneda
      let montoFormateado = "N/A";
      if (p.Monto && p.Monto !== "NULL") {
        const montoNum = parseFloat(p.Monto);
        if (!isNaN(montoNum)) {
          if (p.moneda_pago === "VES" || p.moneda_pago === "VES") {
            montoFormateado = formatVES(montoNum);
          } else if (p.moneda_pago === "USDT") {
            montoFormateado = `${montoNum.toFixed(2)} USDT`;
          } else {
            montoFormateado = formatUSD(montoNum);
          }
        }
      }

      const accionButtons =
        tipo === "pendientes"
          ? `
          <div class="pago-actions">
            <button class="btn btn--yellow btn-aprobar" data-factura="${p.factura_id}">✅ Aprobar</button>
            <button class="btn btn--ghost btn-rechazar" data-factura="${p.factura_id}">❌ Rechazar</button>
          </div>
        `
          : "";

      let estadoTexto = "";
      let estadoClase = "";
      if (tipo === "pendientes") {
        estadoTexto = "⏳ Pendiente";
        estadoClase = "pendiente";
      } else if (tipo === "aprobados") {
        estadoTexto = "✅ Aprobado";
        estadoClase = "aprobado";
      } else {
        estadoTexto = "❌ Rechazado";
        estadoClase = "rechazado";
      }

      const estaAbierto = detallesAbiertos.has(p.factura_id);

      html += `
        <div class="pago-card" data-factura="${p.factura_id}">
          <div class="pago-header">
            <span class="pago-factura">🧾 Factura: ${escapeHtml(p.factura_id)}</span>
            <span class="pago-estado ${estadoClase}">${estadoTexto}</span>
          </div>
          
          <div class="pago-info-grid">
            <div class="info-row">
              <strong>📅 Fecha de venta</strong>
              <span>${formatDate(p.fecha_venta)}</span>
            </div>
            <div class="info-row">
              <strong>👤 Cliente</strong>
              <span>${escapeHtml(p.cliente_nombre)} ${escapeHtml(p.cliente_apellido || "")}</span>
            </div>
            <div class="info-row">
              <strong>📞 Teléfono</strong>
              <span>${escapeHtml(p.cliente_celular || "N/A")}</span>
            </div>
            
            <div class="info-row">
              <strong>💰 Moneda</strong>
              <span>${escapeHtml(p.Moneda || "N/A")}</span>
            </div>
            <div class="info-row">
              <strong>${metodoIcono} Método de pago</strong>
              <span class="metodo-pago">${escapeHtml(p.metodo_pago || "N/A")}</span>
            </div>
            <div class="info-row">
              <strong>🔢 Número de Referencia</strong>
              <span>${escapeHtml(p.Referencia || "N/A")}</span>
            </div>
            <div class="info-row">
              <strong>💰 Monto Pagado</strong>
              <span>${montoFormateado}</span>
            </div>
          </div>
          
          ${captureImageHtml}
          
          <button class="btn-ver-detalle ${estaAbierto ? "active" : ""}" data-factura="${p.factura_id}">
            📋 ${estaAbierto ? "Ocultar productos" : "Ver productos"}
          </button>
          
          <div id="detalle-${p.factura_id}" class="productos-list" style="display: ${estaAbierto ? "block" : "none"};">
            ${estaAbierto ? '<div class="loading-productos">🔄 Cargando productos...</div>' : ""}
          </div>
          
          ${accionButtons}
        </div>
      `;
    }

    container.innerHTML = html;

    // Agregar event listeners después de renderizar
    const verDetalleBtns = container.querySelectorAll(".btn-ver-detalle");
    for (const btn of verDetalleBtns) {
      const facturaId = btn.dataset.factura;
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        toggleDetalle(facturaId, btn);
      });
    }

    if (tipo === "pendientes") {
      const aprobarBtns = container.querySelectorAll(".btn-aprobar");
      for (const btn of aprobarBtns) {
        btn.addEventListener("click", () => aprobarPago(btn.dataset.factura));
      }

      const rechazarBtns = container.querySelectorAll(".btn-rechazar");
      for (const btn of rechazarBtns) {
        btn.addEventListener("click", () =>
          mostrarModalRechazo(btn.dataset.factura),
        );
      }
    }
  }

  async function cargarPagosPendientes() {
    try {
      const data = await fetchJson("/api/validacion-pagos/pendientes");
      console.log("Pagos pendientes recibidos:", data);
      renderPagosList(data.pagos, "pendientes");
    } catch (err) {
      console.error("Error cargando pagos pendientes:", err);
      mostrarToast(err.message, "error");
      const container = document.getElementById("pendientes-list");
      if (container) {
        container.innerHTML =
          '<div class="empty-state">❌ Error al cargar pagos pendientes</div>';
      }
    }
  }

  async function cargarPagosAprobados() {
    try {
      const data = await fetchJson("/api/validacion-pagos/aprobados");
      renderPagosList(data.pagos, "aprobados");
    } catch (err) {
      console.error("Error cargando pagos aprobados:", err);
      const container = document.getElementById("aprobados-list");
      if (container) {
        container.innerHTML =
          '<div class="empty-state">❌ Error al cargar pagos aprobados</div>';
      }
    }
  }

  async function cargarPagosRechazados() {
    try {
      const data = await fetchJson("/api/validacion-pagos/rechazados");
      renderPagosList(data.pagos, "rechazados");
    } catch (err) {
      console.error("Error cargando pagos rechazados:", err);
      const container = document.getElementById("rechazados-list");
      if (container) {
        container.innerHTML =
          '<div class="empty-state">❌ Error al cargar pagos rechazados</div>';
      }
    }
  }

  async function aprobarPago(facturaId) {
    const confirmar = confirm(
      `¿Aprobar el pago de la factura ${facturaId}?\nSe actualizará automáticamente la fecha de pago.`,
    );
    if (!confirmar) return;

    const btn = document.querySelector(
      `.btn-aprobar[data-factura="${facturaId}"]`,
    );
    if (btn) {
      btn.disabled = true;
      btn.textContent = "⏳ Procesando...";
    }

    try {
      await fetchJson(`/api/validacion-pagos/aprobar/${facturaId}`, {
        method: "POST",
      });
      mostrarToast(`✅ Pago ${facturaId} aprobado correctamente`, "success");
      detallesAbiertos.clear();
      await Promise.all([cargarPagosPendientes(), cargarPagosAprobados()]);
    } catch (err) {
      mostrarToast(err.message, "error");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = "✅ Aprobar";
      }
    }
  }

  function mostrarModalRechazo(facturaId) {
    facturaRechazoActual = facturaId;
    const modal = document.getElementById("rechazo-modal");
    if (modal) {
      modal.classList.remove("is-hidden");
      const motivoInput = document.getElementById("motivo-rechazo");
      if (motivoInput) {
        motivoInput.value = "";
        motivoInput.focus();
      }
    }
  }

  async function confirmarRechazo() {
    const motivoInput = document.getElementById("motivo-rechazo");
    const motivo = motivoInput?.value.trim();

    if (!motivo) {
      mostrarToast("Debes escribir un motivo para el rechazo", "error");
      return;
    }

    try {
      await fetchJson(
        `/api/validacion-pagos/rechazar/${facturaRechazoActual}`,
        {
          method: "POST",
          body: JSON.stringify({ motivo }),
        },
      );
      mostrarToast(`❌ Pago ${facturaRechazoActual} rechazado`, "success");
      cerrarModalRechazo();
      detallesAbiertos.clear();
      cargarPagosPendientes();
      cargarPagosRechazados();
    } catch (err) {
      mostrarToast(err.message, "error");
    }
  }

  function cerrarModalRechazo() {
    const modal = document.getElementById("rechazo-modal");
    if (modal) modal.classList.add("is-hidden");
    facturaRechazoActual = null;
  }

  function initTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    for (const btn of tabBtns) {
      btn.addEventListener("click", () => {
        for (const b of tabBtns) {
          b.classList.remove("active");
        }
        btn.classList.add("active");

        const tab = btn.dataset.tab;

        const tabContents = document.querySelectorAll(".tab-content");
        for (const content of tabContents) {
          content.classList.add("is-hidden");
        }

        const tabContent = document.getElementById(`${tab}-tab`);
        if (tabContent) tabContent.classList.remove("is-hidden");

        detallesAbiertos.clear();

        if (tab === "pendientes") cargarPagosPendientes();
        else if (tab === "aprobados") cargarPagosAprobados();
        else if (tab === "rechazados") cargarPagosRechazados();
      });
    }
  }

  function init() {
    initTabs();

    const cancelarBtn = document.getElementById("cancelar-rechazo");
    if (cancelarBtn) cancelarBtn.addEventListener("click", cerrarModalRechazo);

    const confirmarBtn = document.getElementById("confirmar-rechazo");
    if (confirmarBtn) confirmarBtn.addEventListener("click", confirmarRechazo);

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") cerrarModalRechazo();
    });

    const rechazoModal = document.getElementById("rechazo-modal");
    if (rechazoModal) {
      rechazoModal.addEventListener("click", (e) => {
        if (e.target === rechazoModal) cerrarModalRechazo();
      });
    }

    cargarPagosPendientes();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
