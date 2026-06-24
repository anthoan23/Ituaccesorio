(() => {
  "use strict";

  let reporteDatosActuales = [];
  let reporteFiltrosActuales = {};
  let itemsLocal = [];
  let clientesMap = {};

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
      animation: slideInRight 0.3s ease;
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

  function formatMoney(value, currency = "USD") {
    const n = Number(value);
    if (!Number.isFinite(n)) return "0.00";
    const formatted = n.toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (currency === "USD") return `$${formatted}`;
    if (currency === "VES") return `Bs ${formatted}`;
    if (currency === "USDT") return `${formatted} USDT`;
    return formatted;
  }

  function getEstadoBadge(estado) {
    if (estado === "pendiente") {
      return '<span class="pago-estado pendiente">⏳ Pendiente</span>';
    } else if (estado === "aprobado") {
      return '<span class="pago-estado aprobado">✅ Aprobado</span>';
    } else {
      return '<span class="pago-estado rechazado">❌ Rechazado</span>';
    }
  }

  function limpiarFiltros() {
    document.getElementById("reporte-busqueda").value = "";
    document.getElementById("reporte-estado").value = "";
    document.getElementById("reporte-metodo").value = "";
    document.getElementById("reporte-moneda").value = "";
    document.getElementById("reporte-fecha-desde").value = "";
    document.getElementById("reporte-fecha-hasta").value = "";
    document.getElementById("reporte-monto-min").value = "";
    document.getElementById("reporte-monto-max").value = "";
  }

  async function generarReporte() {
    const filtros = {
      q: document.getElementById("reporte-busqueda").value || "",
      estado: document.getElementById("reporte-estado").value || null,
      metodo_pago: document.getElementById("reporte-metodo").value || null,
      moneda: document.getElementById("reporte-moneda").value || null,
      fecha_desde: document.getElementById("reporte-fecha-desde").value || null,
      fecha_hasta: document.getElementById("reporte-fecha-hasta").value || null,
      monto_min: document.getElementById("reporte-monto-min").value ? parseFloat(document.getElementById("reporte-monto-min").value) : null,
      monto_max: document.getElementById("reporte-monto-max").value ? parseFloat(document.getElementById("reporte-monto-max").value) : null,
    };
    
    reporteFiltrosActuales = filtros;
    
    const btn = document.getElementById("btn-generar-reporte");
    btn.disabled = true;
    btn.textContent = "⏳ Cargando...";
    
    try {
      const data = await fetchJson("/api/reportes-ventas/listar", {
        method: "POST",
        body: JSON.stringify(filtros)
      });
      
      reporteDatosActuales = data.ventas || [];
      
      document.getElementById("reporte-resumen").style.display = "block";
      document.getElementById("reporte-preview").style.display = "block";
      document.getElementById("reporte-export").style.display = "flex";
      
      document.getElementById("reporte-total").textContent = data.total || 0;
      document.getElementById("reporte-total-monto").textContent = formatMoney(data.total_monto || 0);
      document.getElementById("reporte-pendientes").textContent = data.pendientes || 0;
      document.getElementById("reporte-aprobados").textContent = data.aprobados || 0;
      document.getElementById("reporte-rechazados").textContent = data.rechazados || 0;
      
      const tabla = document.getElementById("reporte-tabla");
      if (reporteDatosActuales.length === 0) {
        tabla.innerHTML = '<tr><td colspan="8" class="table__empty">No hay ventas con esos filtros</td></tr>';
      } else {
        tabla.innerHTML = reporteDatosActuales.map(p => `
          <tr>
            <td><strong>${escapeHtml(p.factura_id || '')}</strong></td>
            <td>${escapeHtml(p.cliente_nombre || '')} ${escapeHtml(p.cliente_apellido || '')}</td>
            <td>${formatDateShort(p.fecha_venta)}</td>
            <td><span class="metodo-pago">${escapeHtml(p.metodo_pago || '-')}</span></td>
            <td>${escapeHtml(p.Referencia || '-')}</td>
            <td>${formatMoney(p.monto_pagado, p.venta_moneda)}</td>
            <td>${getEstadoBadge(p.estado)}</td>
            <td style="text-align: center;">
              <button class="btn-ver-detalle-reporte" data-factura="${escapeHtml(p.factura_id)}">📋 Ver</button>
            </td>
          </tr>
        `).join("");
        
        tabla.querySelectorAll(".btn-ver-detalle-reporte").forEach(btn => {
          btn.addEventListener("click", () => mostrarDetalleVenta(btn.dataset.factura));
        });
      }
      
      document.getElementById("btn-exportar-excel").disabled = false;
      document.getElementById("btn-exportar-pdf").disabled = false;
      document.getElementById("btn-imprimir").disabled = false;
      
      mostrarToast(`✅ Reporte generado: ${reporteDatosActuales.length} transacciones`, "success");
      
    } catch (err) {
      mostrarToast(err.message || "Error al generar el reporte", "error");
    } finally {
      btn.disabled = false;
      btn.textContent = "📊 Generar reporte";
    }
  }

  async function mostrarDetalleVenta(facturaId) {
    try {
      const data = await fetchJson(`/api/reportes-ventas/detalle/${facturaId}`, { method: 'GET' });

      const venta = data.venta;
      const productos = data.productos;
      const totalVenta = data.total_venta;

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
            <span>${venta.estado || 'pendiente'}</span>
          </div>
        </div>
      `;

      document.getElementById("detalle-venta-info").innerHTML = infoHtml;

      let productosHtml = "";
      for (const p of productos) {
        productosHtml += `
          <tr>
            <td>${escapeHtml(p.Nombre_producto)}</td>
            <td>${escapeHtml(p.marca || '-')}</td>
            <td>${escapeHtml(p.clase || '-')}</td>
            <td style="text-align: center;">${p.Cantidad_articulo}</td>
            <td style="text-align: right;">${formatMoney(p.precio_unitario, venta.Moneda)}</td>
            <td style="text-align: right;">${formatMoney(p.subtotal, venta.Moneda)}</td>
          </tr>
        `;
      }

      document.getElementById("detalle-venta-productos").innerHTML = productosHtml;
      document.getElementById("detalle-venta-total-amount").innerHTML = formatMoney(totalVenta, venta.Moneda);

      document.getElementById("modal-detalle-venta").hidden = false;
      document.getElementById("modal-detalle-venta").setAttribute("aria-hidden", "false");

    } catch (err) {
      mostrarToast(err.message, "error");
    }
  }

  // ==================== VENTAS LOCALES ====================

  async function cargarProductosParaSelect() {
    try {
      const data = await fetchJson("/api/catalogo/productos");
      const select = document.getElementById("producto-select");
      if (select) {
        select.innerHTML = '<option value="">-- Selecciona --</option>' +
          (data.productos || [])
            .map(p => `<option value="${p.id}" data-precio="${p.precio_usd}">${p.nombre} - $${p.precio_usd}</option>`)
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
      list.innerHTML = clientes.map(c => {
        const text = `${c.id} - ${c.nombre} ${c.apellido || ""}`.trim();
        clientesMap[String(c.id)] = c.id;
        clientesMap[(c.nombre + " " + (c.apellido || "")).trim().toLowerCase()] = c.id;
        return `<option value="${escapeHtml(text)}"></option>`;
      }).join("");
    } catch (err) {
      console.warn("Error cargando clientes:", err);
    }
  }

  function agregarItemLocal() {
    const select = document.getElementById("producto-select");
    const cantidad = parseInt(document.getElementById("cantidad-local")?.value || 1);
    const productoId = select?.value;

    if (!productoId) {
      mostrarToast("Selecciona un producto", "error");
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

    const totalUsd = itemsLocal.reduce((sum, i) => sum + Number(i.precio_usd) * i.cantidad, 0);

    container.innerHTML = `
      <div class="items-local">
        ${itemsLocal.map((item, idx) => `
          <div class="cart-item">
            <span>${escapeHtml(item.nombre)} x${item.cantidad}</span>
            <span>$${(Number(item.precio_usd) * item.cantidad).toFixed(2)}</span>
            <button class="icon-action" data-remove="${idx}" aria-label="Eliminar producto">🗑</button>
          </div>
        `).join("")}
        <div class="cart-total">
          <strong>Total: $${totalUsd.toFixed(2)}</strong>
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
      mostrarToast("Cliente no encontrado. Escribe ID o selecciona un cliente válido.", "error");
      return;
    }
    if (!itemsLocal.length) {
      mostrarToast("Agrega al menos un producto", "error");
      return;
    }
    if (!metodoPago) {
      mostrarToast("Selecciona un método de pago", "error");
      return;
    }

    try {
      const data = await fetchJson("/api/reportes-ventas/venta-local", {
        method: "POST",
        body: JSON.stringify({
          cliente_id: parseInt(clienteId),
          items: itemsLocal,
          metodo_pago: metodoPago,
        }),
      });

      mostrarToast(`✅ Venta registrada: ${data.factura_id}`, "success");
      itemsLocal = [];
      renderItemsLocal();
      document.getElementById("form-venta-local")?.reset();
      cerrarModalVentaLocal();
      cargarVentasLocales();
    } catch (err) {
      mostrarToast(err.message, "error");
    }
  }

  function cerrarModalVentaLocal() {
    const modal = document.getElementById("venta-local-modal");
    if (modal) modal.classList.add("is-hidden");
    document.body.style.overflow = "";
  }

  function abrirModalVentaLocal() {
    const modal = document.getElementById("venta-local-modal");
    if (modal) {
      modal.classList.remove("is-hidden");
      document.body.style.overflow = "hidden";
    }
  }

  async function cargarVentasLocales() {
    const tabla = document.getElementById("ventas-locales-tabla");
    const busqueda = document.getElementById("venta-local-busqueda")?.value || "";
    const fecha = document.getElementById("venta-local-fecha")?.value || "";

    try {
      const params = new URLSearchParams();
      if (busqueda) params.set("q", busqueda);
      if (fecha) params.set("fecha", fecha);

      const data = await fetchJson(`/api/reportes-ventas/ventas-locales?${params}`);

      if (data.ventas.length === 0) {
        tabla.innerHTML = '<tr><td colspan="7" class="table__empty">No hay ventas locales registradas</td></tr>';
      } else {
        tabla.innerHTML = data.ventas.map(v => `
          <tr>
            <td><strong>${escapeHtml(v.factura_id)}</strong></td>
            <td>${escapeHtml(v.cliente_nombre)} ${escapeHtml(v.cliente_apellido || '')}</td>
            <td>${formatDateShort(v.fecha_venta)}</td>
            <td>${escapeHtml(v.metodo_pago)}</td>
            <td>${formatMoney(v.monto, v.Moneda)}</td>
            <td>${getEstadoBadge(v.estado)}</td>
            <td style="text-align: center;">
              <button class="btn-ver-detalle-reporte" data-factura="${escapeHtml(v.factura_id)}">📋 Ver</button>
            </td>
          </tr>
        `).join("");

        tabla.querySelectorAll(".btn-ver-detalle-reporte").forEach(btn => {
          btn.addEventListener("click", () => mostrarDetalleVenta(btn.dataset.factura));
        });
      }
    } catch (err) {
      tabla.innerHTML = `<tr><td colspan="7" class="table__empty">❌ Error: ${escapeHtml(err.message)}</td></tr>`;
    }
  }

  // ==================== EXPORTACIONES ====================

  function exportarExcel() {
    if (reporteDatosActuales.length === 0) {
      mostrarToast("No hay datos para exportar", "error");
      return;
    }

    if (typeof XLSX === 'undefined') {
      mostrarToast("Cargando librería...", "info");
      const script = document.createElement('script');
      script.src = '/static/js/libs/xlsx.full.min.js';
      script.onload = () => exportarExcel();
      document.head.appendChild(script);
      return;
    }

    const datos = reporteDatosActuales.map(p => ({
      "Factura": p.factura_id || "",
      "Cliente": `${p.cliente_nombre || ""} ${p.cliente_apellido || ""}`.trim(),
      "Teléfono": p.cliente_celular || "",
      "Correo": p.cliente_correo || "",
      "Fecha Venta": formatDateShort(p.fecha_venta),
      "Método Pago": p.metodo_pago || "",
      "Referencia": p.Referencia || "",
      "Monto": p.monto_pagado || 0,
      "Moneda": p.venta_moneda || "USD",
      "Estado": p.estado || ""
    }));

    const ws = XLSX.utils.json_to_sheet(datos);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Reporte_Ventas");
    XLSX.writeFile(wb, `reporte_ventas_${new Date().toISOString().slice(0,19)}.xlsx`);
    mostrarToast("Reporte exportado a Excel", "success");
  }

  function exportarPDF() {
    if (reporteDatosActuales.length === 0) {
      mostrarToast("No hay datos para exportar", "error");
      return;
    }

    if (typeof window.jspdf === 'undefined' || typeof window.jspdf.jsPDF === 'undefined') {
      mostrarToast("Cargando librería...", "info");
      const script1 = document.createElement('script');
      script1.src = '/static/js/libs/jspdf.umd.min.js';
      script1.onload = () => {
        const script2 = document.createElement('script');
        script2.src = '/static/js/libs/jspdf.plugin.autotable.min.js';
        script2.onload = () => setTimeout(() => exportarPDF(), 100);
        document.head.appendChild(script2);
      };
      document.head.appendChild(script1);
      return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
    const pageWidth = doc.internal.pageSize.getWidth();

    doc.setFont("helvetica", "bold");
    doc.setFontSize(22);
    doc.text("REPORTE DE VENTAS", pageWidth / 2, 25, { align: 'center' });

    doc.setDrawColor(243, 197, 0);
    doc.setLineWidth(0.8);
    doc.line(pageWidth / 2 - 35, 29, pageWidth / 2 + 35, 29);

    const now = new Date();
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.text(`Generado: ${now.toLocaleDateString('es-ES')} • Total: ${reporteDatosActuales.length} ventas`, pageWidth / 2, 37, { align: 'center' });

    const columns = ["FACTURA", "CLIENTE", "FECHA", "MÉTODO", "REFERENCIA", "MONTO", "ESTADO"];
    const rows = reporteDatosActuales.map(p => [
      p.factura_id || "",
      `${p.cliente_nombre || ""} ${p.cliente_apellido || ""}`.trim(),
      formatDateShort(p.fecha_venta),
      p.metodo_pago || "-",
      p.Referencia || "-",
      formatMoney(p.monto_pagado, p.venta_moneda),
      p.estado || "-"
    ]);

    doc.autoTable({
      head: [columns],
      body: rows,
      startY: 42,
      theme: 'grid',
      headStyles: { fillColor: [18, 18, 18], textColor: [255, 255, 255], fontStyle: 'bold', fontSize: 9 },
      bodyStyles: { fontSize: 8.5, cellPadding: 4 },
      alternateRowStyles: { fillColor: [248, 249, 250] },
      margin: { left: 15, right: 15 },
      didDrawPage: (data) => {
        doc.setFontSize(7);
        doc.text("ItuAccesorio System", pageWidth / 2, doc.internal.pageSize.getHeight() - 8, { align: 'center' });
        doc.text(`Página ${data.pageNumber}`, pageWidth - 15, doc.internal.pageSize.getHeight() - 8, { align: 'right' });
      }
    });

    doc.save(`reporte_ventas_${now.toISOString().slice(0,19)}.pdf`);
    mostrarToast("Reporte exportado a PDF", "success");
  }

  function imprimirReporte() {
    if (reporteDatosActuales.length === 0) {
      mostrarToast("No hay datos para imprimir", "error");
      return;
    }

    const ventana = window.open("", "_blank");
    const fecha = new Date().toLocaleString();

    ventana.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>Reporte de Ventas</title>
        <style>
          @media print { body { margin: 0; padding: 20px; } .no-print { display: none; } }
          body { font-family: 'Manrope', sans-serif; margin: 20px; padding: 20px; background: white; }
          h1 { font-family: 'Space Grotesk', sans-serif; font-size: 24px; text-align: center; border-bottom: 3px solid #f3c500; padding-bottom: 10px; }
          .info { text-align: center; margin-bottom: 20px; color: #666; font-size: 12px; }
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
        <h1>REPORTE DE VENTAS</h1>
        <div class="info">Generado: ${fecha} • Total ventas: ${reporteDatosActuales.length}</div>
        <table>
          <thead>
            <tr><th>Factura</th><th>Cliente</th><th>Fecha</th><th>Método</th><th>Referencia</th><th>Monto</th><th>Estado</th></tr>
          </thead>
          <tbody>
            ${reporteDatosActuales.map(p => `
              <tr>
                <td><strong>${escapeHtml(p.factura_id || '')}</strong></td>
                <td>${escapeHtml(p.cliente_nombre || '')} ${escapeHtml(p.cliente_apellido || '')}</td>
                <td>${formatDateShort(p.fecha_venta)}</td>
                <td>${escapeHtml(p.metodo_pago || '-')}</td>
                <td>${escapeHtml(p.Referencia || '-')}</td>
                <td>${formatMoney(p.monto_pagado, p.venta_moneda)}</td>
                <td><span class="badge badge-${p.estado || 'pendiente'}">${p.estado || 'pendiente'}</span></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
        <div class="footer">ItuAccesorio System</div>
      </body>
      </html>
    `);
    ventana.document.close();
  }

  // ==================== INICIALIZACIÓN ====================

  function initTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    for (const btn of tabBtns) {
      btn.addEventListener("click", () => {
        for (const b of tabBtns) b.classList.remove("active");
        btn.classList.add("active");

        const tab = btn.dataset.tab;
        for (const content of document.querySelectorAll(".tab-content")) {
          content.classList.add("is-hidden");
        }
        document.getElementById(`${tab}-tab`)?.classList.remove("is-hidden");

        if (tab === "ventas-local") {
          cargarVentasLocales();
        }
      });
    }
  }

  function init() {
    initTabs();

    // Reportes
    document.getElementById("btn-generar-reporte").addEventListener("click", generarReporte);
    document.getElementById("btn-limpiar-filtros").addEventListener("click", limpiarFiltros);
    document.getElementById("btn-exportar-excel").addEventListener("click", exportarExcel);
    document.getElementById("btn-exportar-pdf").addEventListener("click", exportarPDF);
    document.getElementById("btn-imprimir").addEventListener("click", imprimirReporte);

    // Ventas locales
    document.getElementById("btn-venta-local").addEventListener("click", abrirModalVentaLocal);
    document.getElementById("btn-buscar-ventas-locales").addEventListener("click", cargarVentasLocales);
    document.getElementById("btn-limpiar-filtros-locales").addEventListener("click", () => {
      document.getElementById("venta-local-busqueda").value = "";
      document.getElementById("venta-local-fecha").value = "";
      cargarVentasLocales();
    });
    document.getElementById("agregar-producto-local").addEventListener("click", agregarItemLocal);
    document.getElementById("form-venta-local").addEventListener("submit", registrarVentaLocal);

    // Modal
    document.querySelector("[data-modal-close]")?.addEventListener("click", cerrarModalVentaLocal);
    document.getElementById("venta-local-modal")?.addEventListener("click", (e) => {
      if (e.target === e.currentTarget) cerrarModalVentaLocal();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") cerrarModalVentaLocal();
    });

    // Modal detalle
    document.querySelector("[data-close-modal]")?.addEventListener("click", () => {
      document.getElementById("modal-detalle-venta").hidden = true;
      document.getElementById("modal-detalle-venta").setAttribute("aria-hidden", "true");
    });
    document.getElementById("modal-detalle-venta")?.addEventListener("click", (e) => {
      if (e.target === e.currentTarget) {
        document.getElementById("modal-detalle-venta").hidden = true;
        document.getElementById("modal-detalle-venta").setAttribute("aria-hidden", "true");
      }
    });

    // Cargar datos iniciales
    cargarProductosParaSelect();
    cargarClientesParaDatalist();
    cargarVentasLocales();
    generarReporte();
  }

  document.addEventListener("DOMContentLoaded", init);
})();