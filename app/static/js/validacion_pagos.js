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

  function formatMoneyByCurrency(amount, currency) {
    const n = Number(amount);
    if (isNaN(n)) return "0.00";
    if (currency === "VES") return formatVES(n);
    if (currency === "USDT") return `${n.toFixed(2)} USDT`;
    return formatUSD(n);
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

  function formatDateShort(dateString) {
    if (!dateString) return "N/A";
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("es-ES", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      });
    } catch {
      return dateString;
    }
  }

  function getEstadoFromPago(p) {
    const raw = p && (p.estado || p.Estado || p.status || p.estado_pago || "");
    return String(raw || "").toLowerCase();
  }

  function getEstadoBadgeClass(estado) {
    const estadoLower = String(estado || "").toLowerCase();
    if (estadoLower === "pendiente") return "pendiente";
    if (estadoLower === "aprobado") return "aprobado";
    if (estadoLower === "rechazado") return "rechazado";
    return "pendiente";
  }

  // ==================== ABRIR/CERRAR MODALES (con UiModal) ====================
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

  // ==================== DETALLE DE FACTURA ====================
  async function cargarDetalleFactura(facturaId, detalleContainer) {
    try {
      const url = `/api/validacion-pagos/venta/${facturaId}/detalle`;
      const data = await fetchJson(url, { method: 'GET' });

      const items = data.detalle || [];

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
      } else {
        detalleContainer.innerHTML = `
          <div class="empty-detalle">No hay productos registrados en esta venta</div>
        `;
      }
    } catch (err) {
      console.error("Error en cargarDetalleFactura:", err);
      detalleContainer.innerHTML = `
        <div class="error-detalle">Error: ${escapeHtml(err.message)}</div>
      `;
      mostrarToast(err.message, "error");
    }
  }

  async function toggleDetalle(facturaId, btnElement) {
    const detalleContainer = document.getElementById(`detalle-${facturaId}`);

    if (detallesAbiertos.has(facturaId)) {
      detalleContainer.classList.add("is-hidden");
      detallesAbiertos.delete(facturaId);
      btnElement.innerHTML = "Ver productos";
      btnElement.classList.remove("is-active");
    } else {
      detalleContainer.classList.remove("is-hidden");
      detallesAbiertos.add(facturaId);
      btnElement.innerHTML = "Cargando...";
      btnElement.classList.add("is-active");

      detalleContainer.innerHTML = '<div class="loading-productos">Cargando productos...</div>';
      await cargarDetalleFactura(facturaId, detalleContainer);
      btnElement.innerHTML = "Ocultar productos";
    }
  }

  // ==================== DETALLE DE VENTA (modal) ====================
  async function mostrarDetalleVenta(facturaId) {
    try {
      const url = `/api/validacion-pagos/detalle-venta/${facturaId}`;
      const data = await fetchJson(url, { method: 'GET' });

      const venta = data.venta;
      const productos = data.productos;
      const totalVenta = data.total_venta;

      // Información de la venta
      const infoHtml = `
        <div class="detail-info-grid">
          <div class="detail-info-item">
            <strong>Factura</strong>
            <span>${escapeHtml(venta.factura_id)}</span>
          </div>
          <div class="detail-info-item">
            <strong>Cliente</strong>
            <span>${escapeHtml(venta.cliente_nombre)} ${escapeHtml(venta.cliente_apellido)}</span>
          </div>
          <div class="detail-info-item">
            <strong>Teléfono</strong>
            <span>${escapeHtml(venta.Celular_cliente || 'N/A')}</span>
          </div>
          <div class="detail-info-item">
            <strong>Correo</strong>
            <span>${escapeHtml(venta.Correo_cliente || 'N/A')}</span>
          </div>
          <div class="detail-info-item">
            <strong>Dirección</strong>
            <span>${escapeHtml(venta.Direccion_cliente || 'N/A')}</span>
          </div>
          <div class="detail-info-item">
            <strong>Fecha Venta</strong>
            <span>${formatDate(venta.Fecha_venta)}</span>
          </div>
          <div class="detail-info-item">
            <strong>Método Pago</strong>
            <span>${escapeHtml(venta.metodo_pago || 'N/A')}</span>
          </div>
          <div class="detail-info-item">
            <strong>Referencia</strong>
            <span>${escapeHtml(venta.Referencia || 'N/A')}</span>
          </div>
          <div class="detail-info-item">
            <strong>Estado</strong>
            <span><span class="pago-estado ${getEstadoBadgeClass(venta.estado)}">${escapeHtml(venta.estado || 'pendiente')}</span></span>
          </div>
        </div>
      `;

      document.getElementById("detalle-venta-info").innerHTML = infoHtml;

      // Tabla de productos
      let productosHtml = "";
      for (const p of productos) {
        productosHtml += `
          <tr>
            <td>${escapeHtml(p.Nombre_producto)}</td>
            <td>${escapeHtml(p.marca || '-')}</td>
            <td>${escapeHtml(p.clase || '-')}</td>
            <td class="cell-center">${p.Cantidad_articulo}</td>
            <td class="cell-right">${formatMoneyByCurrency(p.precio_unitario, venta.Moneda)}</td>
            <td class="cell-right">${formatMoneyByCurrency(p.subtotal, venta.Moneda)}</td>
          </tr>
        `;
      }

      document.getElementById("detalle-venta-productos").innerHTML = productosHtml;
      document.getElementById("detalle-venta-total-amount").innerHTML = formatMoneyByCurrency(totalVenta, venta.Moneda);

      // Abrir modal
      abrirModal("modal-detalle-venta");
    } catch (err) {
      mostrarToast(err.message, "error");
    }
  }

  // ==================== RENDERIZAR LISTA DE PAGOS ====================
  function renderPagosList(pagos, tipo) {
    const container = document.getElementById(`${tipo}-list`);
    if (!container) return;

    // Limpia contenedores de otras pestañas para evitar duplicados residuales
    try {
      ['pendientes', 'aprobados', 'rechazados'].forEach(t => {
        if (t !== tipo) {
          const c = document.getElementById(`${t}-list`);
          if (c) c.innerHTML = '';
        }
      });
    } catch (e) {
      console.error('Error limpiando otros contenedores', e);
    }

    container.innerHTML = "";

    if (!pagos || !pagos.length) {
      container.innerHTML = '<div class="empty-state">No hay pagos en esta lista</div>';
      return;
    }

    let html = "";

    for (const p of pagos) {
      const estadoNorm = getEstadoFromPago(p);

      let estadoInferido = estadoNorm;
      if (!estadoInferido) {
        if (p.Fecha_aprobacion || p.Aprobado_por) estadoInferido = 'aprobado';
        else if (p.Fecha_rechazo || p.Rechazado_por || p.Motivo_rechazo) estadoInferido = 'rechazado';
        else estadoInferido = 'pendiente';
      }

      if (tipo) {
        const tipoNorm = tipo.replace(/s$/, '').toLowerCase();
        if (tipoNorm !== estadoInferido) {
          continue;
        }
      }

      const captureImageHtml =
        p.capture_image && p.capture_image !== "NULL" && p.capture_image !== ""
          ? `
            <div class="capture-image">
              <img src="${escapeHtml(p.capture_image)}" alt="Comprobante de pago" onclick="window.open('${escapeHtml(p.capture_image)}', '_blank')" loading="lazy">
              <div class="capture-hint">Haz clic para ampliar</div>
            </div>
          `
          : '<div class="no-capture">Sin comprobante adjunto</div>';

      let montoFormateado = "N/A";
      if (p.Monto && p.Monto !== "NULL") {
        const montoNum = parseFloat(p.Monto);
        if (!isNaN(montoNum)) {
          if (p.pago_moneda === "VES") {
            montoFormateado = formatVES(montoNum);
          } else if (p.pago_moneda === "USDT") {
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
              <button class="ui-btn ui-btn--primary btn-aprobar" data-factura="${p.factura_id}">Aprobar</button>
              <button class="ui-btn ui-btn--danger btn-rechazar" data-factura="${p.factura_id}">Rechazar</button>
            </div>
          `
          : "";

      const estadoFinal = estadoInferido;
      let estadoTexto = "";
      let estadoClase = "";
      if (estadoFinal === "pendiente") {
        estadoTexto = "Pendiente";
        estadoClase = "pendiente";
      } else if (estadoFinal === "aprobado" || estadoFinal === "aprobados") {
        estadoTexto = "Aprobado";
        estadoClase = "aprobado";
      } else if (estadoFinal === "rechazado" || estadoFinal === "rechazados") {
        estadoTexto = "Rechazado";
        estadoClase = "rechazado";
      } else {
        estadoTexto = estadoFinal || "Pendiente";
        estadoClase = "pendiente";
      }

      const estaAbierto = detallesAbiertos.has(p.factura_id);

      html += `
        <div class="pago-card pago-card--enter" data-factura="${p.factura_id}">
          <div class="pago-header">
            <div class="pago-factura">Factura: ${escapeHtml(p.factura_id)}</div>
            <div class="pago-estado ${estadoClase}">${estadoTexto}</div>
          </div>

          <div class="pago-main">
            <div class="pago-capture">
              ${captureImageHtml}
            </div>
            <div class="pago-summary">
              <div class="detail-info-grid">
                <div class="detail-info-item"><strong>Cliente</strong><span>${escapeHtml(p.cliente_nombre)} ${escapeHtml(p.cliente_apellido || "")}</span></div>
                <div class="detail-info-item"><strong>Teléfono</strong><span>${escapeHtml(p.cliente_celular || "N/A")}</span></div>
                <div class="detail-info-item"><strong>Correo</strong><span>${escapeHtml(p.Correo_cliente || 'N/A')}</span></div>
                <div class="detail-info-item"><strong>Fecha</strong><span>${formatDate(p.fecha_venta)}</span></div>
                <div class="detail-info-item"><strong>Método</strong><span>${escapeHtml(p.metodo_pago || "N/A")}</span></div>
                <div class="detail-info-item"><strong>Referencia</strong><span>${escapeHtml(p.Referencia || "N/A")}</span></div>
                <div class="detail-info-item"><strong>Monto Pagado</strong><span>${montoFormateado}</span></div>
              </div>
            </div>
          </div>

          <div class="detalle-actions">
            <button class="btn-ver-detalle ${estaAbierto ? "is-active" : ""}" data-factura="${p.factura_id}">${estaAbierto ? "Ocultar productos" : "Ver productos"}</button>
          </div>

          <div id="detalle-${p.factura_id}" class="productos-list${estaAbierto ? "" : " is-hidden"}">
            ${estaAbierto ? '<div class="loading-productos">Cargando productos...</div>' : ""}
          </div>

          ${accionButtons}
        </div>
      `;
    }

    container.innerHTML = html;

    // Animación de entrada
    const entering = container.querySelectorAll('.pago-card--enter');
    for (const el of entering) {
      el.addEventListener('animationend', () => el.classList.remove('pago-card--enter'));
    }

    // Listeners para ver detalle
    const verDetalleBtns = container.querySelectorAll(".btn-ver-detalle");
    for (const btn of verDetalleBtns) {
      const facturaId = btn.dataset.factura;
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        toggleDetalle(facturaId, btn);
      });
    }

    // Listeners para aprobar
    const aprobarBtns = container.querySelectorAll(".btn-aprobar");
    for (const btn of aprobarBtns) {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        aprobarPago(btn.dataset.factura);
      });
    }

    // Listeners para rechazar
    const rechazarBtns = container.querySelectorAll(".btn-rechazar");
    for (const btn of rechazarBtns) {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        mostrarModalRechazo(btn.dataset.factura);
      });
    }
  }

  // ==================== CARGAR PAGOS ====================
  async function cargarPagosPendientes() {
    try {
      const data = await fetchJson("/api/validacion-pagos/pendientes");
      const pagos = (data.pagos || []).filter(p => {
        const estado = getEstadoFromPago(p);
        return !estado || estado === 'pendiente';
      });
      renderPagosList(pagos, "pendientes");
    } catch (err) {
      console.error("Error cargando pagos pendientes:", err);
      mostrarToast(err.message, "error");
      const container = document.getElementById("pendientes-list");
      if (container) {
        container.innerHTML = '<div class="empty-state">Error al cargar pagos pendientes</div>';
      }
    }
  }

  async function cargarPagosAprobados() {
    try {
      const data = await fetchJson("/api/validacion-pagos/aprobados");
      const pagos = (data.pagos || []).filter(p => {
        const estado = getEstadoFromPago(p);
        const hasAprobacion = Boolean(p.Fecha_aprobacion || p.Aprobado_por);
        return estado === 'aprobado' || hasAprobacion;
      });
      renderPagosList(pagos, "aprobados");
    } catch (err) {
      console.error("Error cargando pagos aprobados:", err);
      const container = document.getElementById("aprobados-list");
      if (container) {
        container.innerHTML = '<div class="empty-state">Error al cargar pagos aprobados</div>';
      }
    }
  }

  async function cargarPagosRechazados() {
    try {
      const data = await fetchJson("/api/validacion-pagos/rechazados");
      const pagos = (data.pagos || []).filter(p => {
        const estado = getEstadoFromPago(p);
        const hasRechazo = Boolean(p.Fecha_rechazo || p.Rechazado_por || p.Motivo_rechazo);
        return estado === 'rechazado' || hasRechazo;
      });
      renderPagosList(pagos, "rechazados");
    } catch (err) {
      console.error("Error cargando pagos rechazados:", err);
      const container = document.getElementById("rechazados-list");
      if (container) {
        container.innerHTML = '<div class="empty-state">Error al cargar pagos rechazados</div>';
      }
    }
  }

  // ==================== APROBAR PAGO ====================
  async function aprobarPago(facturaId) {
    const confirmar = confirm(`¿Aprobar el pago de la factura ${facturaId}?\nSe actualizará automáticamente la fecha de pago.`);
    if (!confirmar) return;

    const btn = document.querySelector(`.btn-aprobar[data-factura="${facturaId}"]`);
    const btnRechazar = document.querySelector(`.btn-rechazar[data-factura="${facturaId}"]`);
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Procesando...";
    }
    if (btnRechazar) btnRechazar.disabled = true;

    try {
      await fetchJson(`/api/validacion-pagos/aprobar/${facturaId}`, { method: "POST" });
      mostrarToast(`Pago ${facturaId} aprobado correctamente`, "success");
      detallesAbiertos.clear();
      await Promise.all([cargarPagosPendientes(), cargarPagosAprobados()]);
      
      const card = document.querySelector(`.pago-card[data-factura="${facturaId}"]`);
      if (card) {
        card.classList.add('status-updated');
        setTimeout(() => card.classList.remove('status-updated'), 1200);
      }
    } catch (err) {
      mostrarToast(err.message, "error");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = "Aprobar";
      }
      if (btnRechazar) btnRechazar.disabled = false;
    }
  }

  // ==================== RECHAZAR PAGO ====================
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

  function cerrarModalRechazo() {
    const modal = document.getElementById("rechazo-modal");
    if (modal) modal.classList.add("is-hidden");
    facturaRechazoActual = null;
  }

  async function confirmarRechazo() {
    const motivoInput = document.getElementById("motivo-rechazo");
    const motivo = motivoInput?.value.trim();

    if (!motivo) {
      mostrarToast("Debes escribir un motivo para el rechazo", "error");
      return;
    }

    const confirmarBtn = document.getElementById("confirmar-rechazo");
    const cancelarBtn = document.getElementById("cancelar-rechazo");
    try {
      if (confirmarBtn) {
        confirmarBtn.disabled = true;
        confirmarBtn.textContent = "Procesando...";
      }
      if (cancelarBtn) cancelarBtn.disabled = true;

      await fetchJson(`/api/validacion-pagos/rechazar/${facturaRechazoActual}`, {
        method: "POST",
        body: JSON.stringify({ motivo }),
      });

      mostrarToast(`Pago ${facturaRechazoActual} rechazado`, "success");
      
      const cardR = document.querySelector(`.pago-card[data-factura="${facturaRechazoActual}"]`);
      if (cardR) {
        cardR.classList.add('status-updated');
        setTimeout(() => cardR.classList.remove('status-updated'), 1200);
      }
      cerrarModalRechazo();
      detallesAbiertos.clear();
      await Promise.all([cargarPagosPendientes(), cargarPagosRechazados()]);
    } catch (err) {
      mostrarToast(err.message || "Error al rechazar el pago", "error");
    } finally {
      if (confirmarBtn) {
        confirmarBtn.disabled = false;
        confirmarBtn.textContent = "Confirmar rechazo";
      }
      if (cancelarBtn) cancelarBtn.disabled = false;
    }
  }

  // ==================== TABS ====================
  function initTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    for (const btn of tabBtns) {
      btn.addEventListener("click", () => {
        for (const b of tabBtns) {
          b.classList.remove("is-active");
          b.setAttribute("aria-selected", "false");
        }
        btn.classList.add("is-active");
        btn.setAttribute("aria-selected", "true");

        const tab = btn.dataset.tab;

        const tabContents = document.querySelectorAll(".tab-content");
        for (const content of tabContents) {
          content.classList.add("is-hidden");
        }

        const tabContent = document.getElementById(`${tab}-tab`);
        if (tabContent) tabContent.classList.remove("is-hidden");

        detallesAbiertos.clear();

        if (tab === "pendientes") {
          cargarPagosPendientes();
        } else if (tab === "aprobados") {
          cargarPagosAprobados();
        } else if (tab === "rechazados") {
          cargarPagosRechazados();
        }
      });
    }
  }

  // ==================== REPORTES ====================
  let reporteDatosActualesPagos = [];
  let reporteFiltrosActualesPagos = {};

  const btnReportesPagos = document.getElementById("btn-reportes-pagos");
  const modalReportesPagos = document.getElementById("modal-reportes-pagos");
  const reporteBusquedaPagos = document.getElementById("reporte-busqueda-pagos");
  const reporteEstadoPagos = document.getElementById("reporte-estado-pagos");
  const reporteMetodoPagos = document.getElementById("reporte-metodo-pagos");
  const reporteMonedaPagos = document.getElementById("reporte-moneda-pagos");
  const reporteFechaDesdePagos = document.getElementById("reporte-fecha-desde-pagos");
  const reporteFechaHastaPagos = document.getElementById("reporte-fecha-hasta-pagos");
  const reporteMontoMinPagos = document.getElementById("reporte-monto-min-pagos");
  const reporteMontoMaxPagos = document.getElementById("reporte-monto-max-pagos");
  const btnGenerarReportePagos = document.getElementById("btn-generar-reporte-pagos");
  const btnLimpiarFiltrosPagos = document.getElementById("btn-limpiar-filtros-pagos");
  const btnExportarExcelPagos = document.getElementById("btn-exportar-excel-pagos");
  const btnExportarPdfPagos = document.getElementById("btn-exportar-pdf-pagos");
  const btnImprimirPagos = document.getElementById("btn-imprimir-pagos");
  const reportePreviewPagos = document.getElementById("reporte-preview-pagos");
  const reporteResumenPagos = document.getElementById("reporte-resumen-pagos");
  const reporteTablaPagos = document.getElementById("reporte-tabla-pagos");
  const reporteTotalPagos = document.getElementById("reporte-total-pagos");
  const reporteTotalMontoPagos = document.getElementById("reporte-total-monto-pagos");
  const reportePendientesPagos = document.getElementById("reporte-pendientes-pagos");
  const reporteAprobadosPagos = document.getElementById("reporte-aprobados-pagos");
  const reporteRechazadosPagos = document.getElementById("reporte-rechazados-pagos");

  function formatMoneyPagos(value, currency = "USD") {
    const n = Number(value);
    if (!Number.isFinite(n)) return "0.00";
    
    const formatted = n.toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    
    if (currency === "USD") return `$${formatted}`;
    if (currency === "VES") return `Bs ${formatted}`;
    if (currency === "USDT") return `${formatted} USDT`;
    return formatted;
  }

  function getEstadoBadgeHtml(estado) {
    const badgeClass = getEstadoBadgeClass(estado);
    const label = estado === "pendiente" ? "Pendiente" : 
                  estado === "aprobado" ? "Aprobado" : "Rechazado";
    return `<span class="pago-estado ${badgeClass}">${label}</span>`;
  }

  function limpiarFiltrosReportePagos() {
    if (reporteBusquedaPagos) reporteBusquedaPagos.value = "";
    if (reporteEstadoPagos) reporteEstadoPagos.value = "";
    if (reporteMetodoPagos) reporteMetodoPagos.value = "";
    if (reporteMonedaPagos) reporteMonedaPagos.value = "";
    if (reporteFechaDesdePagos) reporteFechaDesdePagos.value = "";
    if (reporteFechaHastaPagos) reporteFechaHastaPagos.value = "";
    if (reporteMontoMinPagos) reporteMontoMinPagos.value = "";
    if (reporteMontoMaxPagos) reporteMontoMaxPagos.value = "";
  }

  async function generarReportePagos() {
    const filtros = {
      q: reporteBusquedaPagos?.value || "",
      estado: reporteEstadoPagos?.value || null,
      metodo_pago: reporteMetodoPagos?.value || null,
      moneda: reporteMonedaPagos?.value || null,
      fecha_desde: reporteFechaDesdePagos?.value || null,
      fecha_hasta: reporteFechaHastaPagos?.value || null,
      monto_min: reporteMontoMinPagos?.value ? parseFloat(reporteMontoMinPagos.value) : null,
      monto_max: reporteMontoMaxPagos?.value ? parseFloat(reporteMontoMaxPagos.value) : null,
    };
    
    reporteFiltrosActualesPagos = filtros;
    
    if (btnGenerarReportePagos) {
      btnGenerarReportePagos.disabled = true;
      btnGenerarReportePagos.textContent = "Cargando...";
    }
    
    try {
      const data = await fetchJson("/api/validacion-pagos/reportes", {
        method: "POST",
        body: JSON.stringify(filtros)
      });
      
      reporteDatosActualesPagos = data.pagos || [];
      
      if (reporteResumenPagos) reporteResumenPagos.classList.remove("is-hidden");
      if (reportePreviewPagos) reportePreviewPagos.classList.remove("is-hidden");
      
      if (reporteTotalPagos) reporteTotalPagos.textContent = data.total || 0;
      if (reporteTotalMontoPagos) reporteTotalMontoPagos.textContent = formatMoneyPagos(data.total_monto || 0);
      if (reportePendientesPagos) reportePendientesPagos.textContent = data.pendientes || 0;
      if (reporteAprobadosPagos) reporteAprobadosPagos.textContent = data.aprobados || 0;
      if (reporteRechazadosPagos) reporteRechazadosPagos.textContent = data.rechazados || 0;
      
      if (reporteTablaPagos) {
        if (reporteDatosActualesPagos.length === 0) {
          reporteTablaPagos.innerHTML = '<tr><td colspan="9" class="table__empty">No hay pagos con esos filtros</td></tr>';
        } else {
          reporteTablaPagos.innerHTML = reporteDatosActualesPagos.map(p => `
            <tr>
              <td><strong>${escapeHtml(p.factura_id || '')}</strong></td>
              <td>${escapeHtml(p.cliente_nombre || '')} ${escapeHtml(p.cliente_apellido || '')}</td>
              <td>${formatDateShort(p.fecha_venta)}</td>
              <td><span class="metodo-pago">${escapeHtml(p.metodo_pago || '-')}</span></td>
              <td>${escapeHtml(p.Referencia || '-')}</td>
              <td>${formatMoneyPagos(p.monto_pagado, p.pago_moneda)}</td>
              <td>${getEstadoBadgeHtml(p.estado)}</td>
              <td class="cell-center">${p.total_productos || 0}</td>
              <td class="cell-center">
                <button class="ui-btn ui-btn--ghost ui-btn--sm btn-ver-detalle-reporte" data-factura="${escapeHtml(p.factura_id)}">Ver</button>
              </td>
            </tr>
          `).join("");
          
          const verDetalleBtns = reporteTablaPagos.querySelectorAll(".btn-ver-detalle-reporte");
          for (const btn of verDetalleBtns) {
            btn.addEventListener("click", () => mostrarDetalleVenta(btn.dataset.factura));
          }
        }
      }
      
      if (btnExportarExcelPagos) btnExportarExcelPagos.disabled = false;
      if (btnExportarPdfPagos) btnExportarPdfPagos.disabled = false;
      if (btnImprimirPagos) btnImprimirPagos.disabled = false;
      
      mostrarToast(`Reporte generado: ${reporteDatosActualesPagos.length} transacciones`, "success");
      
    } catch (err) {
      mostrarToast(err.message || "Error al generar el reporte", "error");
    } finally {
      if (btnGenerarReportePagos) {
        btnGenerarReportePagos.disabled = false;
        btnGenerarReportePagos.textContent = "Generar reporte";
      }
    }
  }

  function exportarPagosExcel() {
    if (reporteDatosActualesPagos.length === 0) {
      mostrarToast("No hay datos para exportar", "error");
      return;
    }
    
    const datos = reporteDatosActualesPagos.map(p => ({
      "Factura": p.factura_id || "",
      "Cliente": `${p.cliente_nombre || ""} ${p.cliente_apellido || ""}`.trim(),
      "Teléfono": p.cliente_celular || "",
      "Correo": p.cliente_correo || "",
      "Fecha Venta": formatDateShort(p.fecha_venta),
      "Método Pago": p.metodo_pago || "",
      "Referencia": p.Referencia || "",
      "Monto Pagado": p.monto_pagado || 0,
      "Moneda": p.pago_moneda || "USD",
      "Estado": p.estado || "",
      "Productos": p.total_productos || 0,
      "Total Venta": p.total_venta || 0
    }));
    
    if (typeof XLSX === 'undefined') {
      mostrarToast("Cargando librería de Excel...", "info");
      const script = document.createElement('script');
      script.src = '/static/js/libs/xlsx.full.min.js';
      script.onload = () => exportarPagosExcel();
      document.head.appendChild(script);
      return;
    }
    
    const ws = XLSX.utils.json_to_sheet(datos);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Reporte_Pagos");
    
    ws['!cols'] = [
      {wch: 15}, {wch: 30}, {wch: 15}, {wch: 30},
      {wch: 12}, {wch: 15}, {wch: 20}, {wch: 12},
      {wch: 8}, {wch: 12}, {wch: 10}, {wch: 15}
    ];
    
    XLSX.writeFile(wb, `reporte_pagos_${new Date().toISOString().slice(0,19)}.xlsx`);
    mostrarToast("Reporte exportado a Excel", "success");
  }

  function exportarPagosPdf() {
    if (reporteDatosActualesPagos.length === 0) {
      mostrarToast("No hay datos para exportar", "error");
      return;
    }
    
    if (typeof window.jspdf === 'undefined' || typeof window.jspdf.jsPDF === 'undefined') {
      mostrarToast("Cargando librería de PDF...", "info");
      const script1 = document.createElement('script');
      script1.src = '/static/js/libs/jspdf.umd.min.js';
      script1.onload = () => {
        const script2 = document.createElement('script');
        script2.src = '/static/js/libs/jspdf.plugin.autotable.min.js';
        script2.onload = () => {
          setTimeout(() => exportarPagosPdf(), 100);
        };
        document.head.appendChild(script2);
      };
      document.head.appendChild(script1);
      return;
    }
    
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
    const pageWidth = doc.internal.pageSize.getWidth();
    
    const colors = {
      dark: [18, 18, 18],
      primary: [243, 197, 0],
      white: [255, 255, 255],
      grayLight: [248, 249, 250],
      grayText: [102, 102, 106]
    };
    
    const logoUrl = window.location.origin + '/static/img/LOGO TRAZO.png';
    try {
      doc.addImage(logoUrl, 'PNG', (pageWidth - 45) / 2, 8, 45, 14);
    } catch(e) {}
    
    doc.setFont("helvetica", "bold");
    doc.setFontSize(22);
    doc.setTextColor(colors.dark[0], colors.dark[1], colors.dark[2]);
    doc.text("REPORTE DE PAGOS", pageWidth / 2, 30, { align: 'center' });
    
    doc.setDrawColor(colors.primary[0], colors.primary[1], colors.primary[2]);
    doc.setLineWidth(0.8);
    doc.line(pageWidth / 2 - 35, 34, pageWidth / 2 + 35, 34);
    
    const now = new Date();
    const fechaStr = now.toLocaleDateString('es-ES');
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.setTextColor(colors.grayText[0], colors.grayText[1], colors.grayText[2]);
    doc.text(`Generado: ${fechaStr} • Total transacciones: ${reporteDatosActualesPagos.length}`, pageWidth / 2, 44, { align: 'center' });
    
    const filtrosTexto = [];
    if (reporteFiltrosActualesPagos.q) filtrosTexto.push(`Búsqueda: ${reporteFiltrosActualesPagos.q}`);
    if (reporteFiltrosActualesPagos.estado) filtrosTexto.push(`Estado: ${reporteFiltrosActualesPagos.estado}`);
    if (reporteFiltrosActualesPagos.metodo_pago) filtrosTexto.push(`Método: ${reporteFiltrosActualesPagos.metodo_pago}`);
    
    const filterY = 52;
    doc.setFillColor(colors.grayLight[0], colors.grayLight[1], colors.grayLight[2]);
    doc.rect(15, filterY, pageWidth - 30, 10, 'F');
    doc.setFont("helvetica", "italic");
    doc.setFontSize(8.5);
    doc.setTextColor(colors.grayText[0], colors.grayText[1], colors.grayText[2]);
    doc.text(filtrosTexto.length ? `Filtros: ${filtrosTexto.join(" • ")}` : "Filtros: Todos los pagos", 18, filterY + 7);
    
    const columns = ["FACTURA", "CLIENTE", "FECHA", "MÉTODO", "REFERENCIA", "MONTO", "ESTADO", "PRODUCTOS"];
    const rows = reporteDatosActualesPagos.map(p => [
      p.factura_id || "",
      `${p.cliente_nombre || ""} ${p.cliente_apellido || ""}`.trim(),
      formatDateShort(p.fecha_venta),
      p.metodo_pago || "-",
      p.Referencia || "-",
      formatMoneyPagos(p.monto_pagado, p.pago_moneda),
      p.estado || "-",
      String(p.total_productos || 0)
    ]);
    
    doc.autoTable({
      head: [columns],
      body: rows,
      startY: filterY + 14,
      theme: 'grid',
      headStyles: {
        fillColor: colors.dark,
        textColor: colors.white,
        fontStyle: 'bold',
        fontSize: 9,
        halign: 'center'
      },
      bodyStyles: { fontSize: 8.5, cellPadding: 4 },
      alternateRowStyles: { fillColor: colors.grayLight },
      margin: { left: 15, right: 15 },
      didDrawPage: (data) => {
        doc.setFontSize(7);
        doc.setTextColor(colors.grayText[0], colors.grayText[1], colors.grayText[2]);
        doc.text("ItuAccesorio System · Reporte Generado Exclusivamente Para ituaccesorio", pageWidth / 2, doc.internal.pageSize.getHeight() - 8, { align: 'center' });
        doc.text(`Página ${data.pageNumber}`, pageWidth - 15, doc.internal.pageSize.getHeight() - 8, { align: 'right' });
      }
    });
    
    doc.save(`reporte_pagos_${now.toISOString().slice(0,19)}.pdf`);
    mostrarToast("Reporte exportado a PDF", "success");
  }

  function imprimirReportePagos() {
    if (reporteDatosActualesPagos.length === 0) {
      mostrarToast("No hay datos para imprimir", "error");
      return;
    }
    
    const ventana = window.open("", "_blank");
    const fecha = new Date().toLocaleString();
    const logoUrl = window.location.origin + '/static/img/LOGO TRAZO.png';
    
    const filtrosTexto = [];
    if (reporteFiltrosActualesPagos.q) filtrosTexto.push(`Búsqueda: ${reporteFiltrosActualesPagos.q}`);
    if (reporteFiltrosActualesPagos.estado) filtrosTexto.push(`Estado: ${reporteFiltrosActualesPagos.estado}`);
    if (reporteFiltrosActualesPagos.metodo_pago) filtrosTexto.push(`Método: ${reporteFiltrosActualesPagos.metodo_pago}`);
    
    ventana.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>Reporte de Pagos</title>
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
          @media print { body { margin: 0; padding: 20px; } .no-print { display: none; } }
          body { font-family: 'Manrope', sans-serif; margin: 20px; padding: 20px; background: white; }
          h1 { font-family: 'Space Grotesk', sans-serif; font-size: 24px; text-align: center; border-bottom: 3px solid #f3c500; padding-bottom: 10px; }
          .logo { text-align: center; margin-bottom: 20px; }
          .logo img { height: 50px; }
          .info { text-align: center; margin-bottom: 20px; color: #666; font-size: 12px; }
          .filters { background: #f8f9fa; padding: 10px; margin-bottom: 20px; border-left: 4px solid #f3c500; font-size: 12px; }
          table { width: 100%; border-collapse: collapse; margin-top: 20px; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
          th { background: #121212; color: white; font-weight: bold; }
          tr:nth-child(even) { background: #f8f9fa; }
          .footer { margin-top: 30px; text-align: center; font-size: 10px; color: #666; border-top: 1px solid #ddd; padding-top: 10px; }
          .btn-print { background: #f3c500; border: none; padding: 10px 20px; cursor: pointer; margin-bottom: 20px; }
          .badge { display: inline-block; padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: bold; }
          .badge-pendiente { background: #fff3e0; color: #f5a623; }
          .badge-aprobado { background: #e8f5e9; color: #2e7d32; }
          .badge-rechazado { background: #ffebee; color: #c62828; }
        </style>
      </head>
      <body>
        <button class="btn-print no-print" onclick="window.print()">🖨 Imprimir</button>
        <div class="logo"><img src="${logoUrl}" alt="ItuAccesorio" onerror="this.style.display='none'"></div>
        <h1>REPORTE DE PAGOS</h1>
        <div class="info">Generado: ${fecha} • Total transacciones: ${reporteDatosActualesPagos.length}</div>
        ${filtrosTexto.length ? `<div class="filters"><strong>Filtros:</strong> ${filtrosTexto.join(" • ")}</div>` : ''}
        <table>
          <thead>
            <tr><th>Factura</th><th>Cliente</th><th>Fecha</th><th>Método</th><th>Referencia</th><th>Monto</th><th>Estado</th><th>Productos</th></tr>
          </thead>
          <tbody>
            ${reporteDatosActualesPagos.map(p => `
              <tr>
                <td><strong>${escapeHtml(p.factura_id || '')}</strong></td>
                <td>${escapeHtml(p.cliente_nombre || '')} ${escapeHtml(p.cliente_apellido || '')}</td>
                <td>${formatDateShort(p.fecha_venta)}</td>
                <td>${escapeHtml(p.metodo_pago || '-')}</td>
                <td>${escapeHtml(p.Referencia || '-')}</td>
                <td>${formatMoneyPagos(p.monto_pagado, p.pago_moneda)}</td>
                <td><span class="badge badge-${p.estado || 'pendiente'}">${p.estado || 'pendiente'}</span></td>
                <td class="cell-center">${p.total_productos || 0}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
        <div class="footer">ItuAccesorio System - Reporte Generado Exclusivamente Para ituaccesorio</div>
      </body>
      </html>
    `);
    ventana.document.close();
  }

  // ==================== INICIALIZACIÓN ====================
  function init() {
    initTabs();

    const cancelarBtn = document.getElementById("cancelar-rechazo");
    if (cancelarBtn) cancelarBtn.addEventListener("click", cerrarModalRechazo);

    const confirmarBtn = document.getElementById("confirmar-rechazo");
    if (confirmarBtn) confirmarBtn.addEventListener("click", confirmarRechazo);

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        cerrarModalRechazo();
        if (window.UiModal && typeof window.UiModal.closeById === 'function') {
          const modalesAbiertos = document.querySelectorAll('.ui-modal:not([hidden])');
          for (const modal of modalesAbiertos) {
            if (modal.id) window.UiModal.closeById(modal.id);
          }
        }
      }
    });

    const rechazoModal = document.getElementById("rechazo-modal");
    if (rechazoModal) {
      rechazoModal.addEventListener("click", (e) => {
        if (e.target === rechazoModal) cerrarModalRechazo();
      });
    }

    // ==================== REPORTES ====================
    if (btnReportesPagos) {
      btnReportesPagos.addEventListener("click", () => {
        limpiarFiltrosReportePagos();
        if (reportePreviewPagos) reportePreviewPagos.classList.add("is-hidden");
        if (reporteResumenPagos) reporteResumenPagos.classList.add("is-hidden");
        if (btnExportarExcelPagos) btnExportarExcelPagos.disabled = true;
        if (btnExportarPdfPagos) btnExportarPdfPagos.disabled = true;
        if (btnImprimirPagos) btnImprimirPagos.disabled = true;
        abrirModal("modal-reportes-pagos");
      });
    }

    if (btnGenerarReportePagos) btnGenerarReportePagos.addEventListener("click", generarReportePagos);
    if (btnLimpiarFiltrosPagos) btnLimpiarFiltrosPagos.addEventListener("click", limpiarFiltrosReportePagos);
    if (btnExportarExcelPagos) btnExportarExcelPagos.addEventListener("click", exportarPagosExcel);
    if (btnExportarPdfPagos) btnExportarPdfPagos.addEventListener("click", exportarPagosPdf);
    if (btnImprimirPagos) btnImprimirPagos.addEventListener("click", imprimirReportePagos);

    // Inicializar FieldValidator
    if (window.FieldValidator) {
      setTimeout(() => window.FieldValidator.init(), 100);
    }

    // Cargar datos iniciales
    cargarPagosPendientes();
  }

  document.addEventListener("DOMContentLoaded", init);
})();