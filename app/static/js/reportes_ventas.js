(() => {
  "use strict";

  let reporteDatosActuales = [];
  let reporteFiltrosActuales = {};
  let itemsLocal = [];
  let clientesCache = [];

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

  function getEstadoBadgeHtml(estado) {
    if (estado === "pendiente") {
      return '<span class="pago-estado pendiente">Pendiente</span>';
    } else if (estado === "aprobado") {
      return '<span class="pago-estado aprobado">Aprobado</span>';
    } else {
      return '<span class="pago-estado rechazado">Rechazado</span>';
    }
  }

  // ==================== MODALES ====================
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

  // ==================== REPORTES ====================

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
    btn.textContent = "Cargando...";
    
    try {
      const data = await fetchJson("/api/reportes-ventas/listar", {
        method: "POST",
        body: JSON.stringify(filtros)
      });
      
      reporteDatosActuales = data.ventas || [];
      
      document.getElementById("reporte-resumen").classList.remove("is-hidden");
      document.getElementById("reporte-preview").classList.remove("is-hidden");
      document.getElementById("reporte-export").classList.remove("is-hidden");
      
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
            <td>${getEstadoBadgeHtml(p.estado)}</td>
            <td style="text-align: center;">
              <button class="ui-btn ui-btn--ghost ui-btn--sm btn-ver-detalle-reporte" data-factura="${escapeHtml(p.factura_id)}">Ver</button>
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
      
      mostrarToast(`Reporte generado: ${reporteDatosActuales.length} transacciones`, "success");
      
    } catch (err) {
      mostrarToast(err.message || "Error al generar el reporte", "error");
    } finally {
      btn.disabled = false;
      btn.textContent = "Generar reporte";
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

      abrirModal("modal-detalle-venta");

    } catch (err) {
      mostrarToast(err.message, "error");
    }
  }

  // ==================== VENTAS LOCALES ====================

  // --- Buscador de Clientes (estilo proveedores) ---
  async function cargarClientes() {
    try {
      const data = await fetchJson("/api/clientes");
      clientesCache = data.clientes || [];
      return clientesCache;
    } catch (err) {
      console.warn("Error cargando clientes:", err);
      return [];
    }
  }

  function buscarClientes(query) {
    if (!query || query.length < 1) return [];
    const q = query.toLowerCase().trim();
    return clientesCache.filter(c => {
      const id = String(c.id || "");
      const nombre = (c.nombre || "").toLowerCase();
      const apellido = (c.apellido || "").toLowerCase();
      const cedula = String(c.cedula || c.id || "").toLowerCase();
      return id.includes(q) || nombre.includes(q) || apellido.includes(q) || cedula.includes(q);
    }).slice(0, 10);
  }

  function renderClientesResultados(resultados) {
    const container = document.getElementById("cliente-resultados");
    if (!container) return;

    if (resultados.length === 0) {
      container.innerHTML = '<div class="sin-resultados">No se encontraron clientes</div>';
      container.classList.remove("is-hidden");
      return;
    }

    container.innerHTML = resultados.map(c => `
      <div class="resultado-item" data-id="${escapeHtml(c.id)}" data-nombre="${escapeHtml(c.nombre)}" data-apellido="${escapeHtml(c.apellido || '')}" data-cedula="${escapeHtml(c.cedula || '')}">
        <div class="nombre">${escapeHtml(c.nombre)} ${escapeHtml(c.apellido || '')}</div>
        <div class="detalle">ID: ${escapeHtml(c.id)} ${c.cedula ? '• Cédula: ' + escapeHtml(c.cedula) : ''}</div>
      </div>
    `).join("");

    container.querySelectorAll(".resultado-item").forEach(el => {
      el.addEventListener("click", () => {
        const id = el.dataset.id;
        const nombre = el.dataset.nombre;
        const apellido = el.dataset.apellido;
        const cedula = el.dataset.cedula;
        seleccionarCliente(id, nombre, apellido, cedula);
      });
    });

    container.classList.remove("is-hidden");
  }

  function seleccionarCliente(id, nombre, apellido, cedula) {
    document.getElementById("cliente-id").value = id;
    document.getElementById("cliente-busqueda-input").value = "";
    document.getElementById("cliente-resultados").classList.add("is-hidden");
    
    const info = document.getElementById("cliente-seleccionado-info");
    info.textContent = `${nombre} ${apellido || ''} (ID: ${id}${cedula ? ' • Cédula: ' + cedula : ''})`;
    document.getElementById("cliente-seleccionado").classList.remove("is-hidden");
  }

  function limpiarCliente() {
    document.getElementById("cliente-id").value = "";
    document.getElementById("cliente-busqueda-input").value = "";
    document.getElementById("cliente-resultados").classList.add("is-hidden");
    document.getElementById("cliente-seleccionado").classList.add("is-hidden");
  }

  function initClienteBuscador() {
    const input = document.getElementById("cliente-busqueda-input");
    const btn = document.getElementById("cliente-buscar-btn");
    const resultados = document.getElementById("cliente-resultados");

    if (!input) return;

    // Cargar clientes en cache
    cargarClientes();

    const handleSearch = () => {
      const query = input.value;
      if (!query || query.length < 1) {
        resultados.classList.add("is-hidden");
        return;
      }
      const results = buscarClientes(query);
      renderClientesResultados(results);
    };

    input.addEventListener("input", handleSearch);
    input.addEventListener("focus", () => {
      if (input.value.length >= 1) handleSearch();
    });

    if (btn) {
      btn.addEventListener("click", handleSearch);
    }

    // Cerrar dropdown al hacer clic fuera
    document.addEventListener("click", (e) => {
      const container = document.querySelector(".cliente-busqueda-container");
      if (container && !container.contains(e.target)) {
        resultados.classList.add("is-hidden");
      }
    });

    // Enter para seleccionar el primer resultado
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const firstItem = resultados?.querySelector(".resultado-item");
        if (firstItem) firstItem.click();
      }
    });

    document.getElementById("cliente-limpiar")?.addEventListener("click", limpiarCliente);
  }

  // --- Productos ---
  async function cargarProductosParaSelect() {
    try {
      const data = await fetchJson("/api/catalogo/productos");
      const select = document.getElementById("producto-select");
      if (select) {
        select.innerHTML = '<option value="">-- Selecciona un producto --</option>' +
          (data.productos || [])
            .map(p => `<option value="${p.id}" data-precio="${p.precio_usd}">${escapeHtml(p.nombre)} - $${p.precio_usd}</option>`)
            .join("");
      }
    } catch (err) {
      console.warn("Error cargando productos:", err);
    }
  }

  // --- Items del carrito ---
  function agregarItemLocal() {
    const select = document.getElementById("producto-select");
    const cantidad = parseInt(document.getElementById("cantidad-local")?.value || 1);
    const productoId = select?.value;

    if (!productoId) {
      mostrarToast("Selecciona un producto", "error");
      return;
    }

    const option = select.options[select.selectedIndex];
    const nombre = option.text.split(" - $")[0] || option.text;
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
      container.innerHTML = '<div class="sin-resultados">No hay productos agregados</div>';
      return;
    }

    const totalUsd = itemsLocal.reduce((sum, i) => sum + Number(i.precio_usd) * i.cantidad, 0);

    container.innerHTML = `
      ${itemsLocal.map((item, idx) => `
        <div class="cart-item">
          <span>${escapeHtml(item.nombre)} x${item.cantidad}</span>
          <span>$${(Number(item.precio_usd) * item.cantidad).toFixed(2)}</span>
          <button class="icon-action" data-remove="${idx}" aria-label="Eliminar producto">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" fill="currentColor"/></svg>
          </button>
        </div>
      `).join("")}
      <div class="cart-total">
        <strong>Total: $${totalUsd.toFixed(2)}</strong>
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

  // --- Registrar Venta Local ---
  async function registrarVentaLocal(event) {
    event.preventDefault();

    const clienteId = document.getElementById("cliente-id")?.value;
    const metodoPago = document.getElementById("metodo-local")?.value;

    if (!clienteId) {
      mostrarToast("Selecciona un cliente válido", "error");
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

    // Validar con FieldValidator si está disponible
    const form = document.getElementById("form-venta-local");
    if (window.FieldValidator && typeof window.FieldValidator.validateForm === 'function') {
      const isValid = window.FieldValidator.validateForm(form);
      if (!isValid) {
        mostrarToast("Por favor, corrige los errores en el formulario.", "error");
        return;
      }
    }

    const btn = document.getElementById("btn-registrar-venta-local");
    btn.disabled = true;
    btn.textContent = "Registrando...";

    try {
      const data = await fetchJson("/api/reportes-ventas/venta-local", {
        method: "POST",
        body: JSON.stringify({
          cliente_id: parseInt(clienteId),
          items: itemsLocal,
          metodo_pago: metodoPago,
        }),
      });

      mostrarToast(`Venta registrada: ${data.factura_id}`, "success");
      
      // Limpiar y cerrar
      itemsLocal = [];
      renderItemsLocal();
      form?.reset();
      limpiarCliente();
      cerrarModal("venta-local-modal");
      
      // ✅ ACTUALIZAR LA LISTA DE VENTAS LOCALES
      await cargarVentasLocales();
      
      // ✅ ACTUALIZAR EL REPORTE GENERAL
      await generarReporte();

    } catch (err) {
      mostrarToast(err.message, "error");
    } finally {
      btn.disabled = false;
      btn.textContent = "Registrar Venta";
    }
  }

  function abrirModalVentaLocal() {
    const form = document.getElementById("form-venta-local");
    if (form) form.reset();
    itemsLocal = [];
    renderItemsLocal();
    limpiarCliente();
    // Cargar clientes en cache
    cargarClientes();
    abrirModal("venta-local-modal");
    // Enfocar el buscador de clientes
    setTimeout(() => {
      document.getElementById("cliente-busqueda-input")?.focus();
    }, 300);
  }

  // --- Cargar Ventas Locales ---
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
            <td>${getEstadoBadgeHtml(v.estado)}</td>
            <td style="text-align: center;">
              <button class="ui-btn ui-btn--ghost ui-btn--sm btn-ver-detalle-reporte" data-factura="${escapeHtml(v.factura_id)}">Ver</button>
            </td>
          </tr>
        `).join("");

        tabla.querySelectorAll(".btn-ver-detalle-reporte").forEach(btn => {
          btn.addEventListener("click", () => mostrarDetalleVenta(btn.dataset.factura));
        });
      }
    } catch (err) {
      tabla.innerHTML = `<tr><td colspan="7" class="table__empty">Error: ${escapeHtml(err.message)}</td></tr>`;
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
    doc.text("REPORTE DE VENTAS", pageWidth / 2, 30, { align: 'center' });

    doc.setDrawColor(colors.primary[0], colors.primary[1], colors.primary[2]);
    doc.setLineWidth(0.8);
    doc.line(pageWidth / 2 - 35, 34, pageWidth / 2 + 35, 34);

    const now = new Date();
    const fechaStr = now.toLocaleDateString('es-ES');
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.setTextColor(colors.grayText[0], colors.grayText[1], colors.grayText[2]);
    doc.text(`Generado: ${fechaStr} • Total ventas: ${reporteDatosActuales.length}`, pageWidth / 2, 44, { align: 'center' });

    const filtrosTexto = [];
    if (reporteFiltrosActuales.q) filtrosTexto.push(`Búsqueda: ${reporteFiltrosActuales.q}`);
    if (reporteFiltrosActuales.estado) filtrosTexto.push(`Estado: ${reporteFiltrosActuales.estado}`);
    if (reporteFiltrosActuales.metodo_pago) filtrosTexto.push(`Método: ${reporteFiltrosActuales.metodo_pago}`);

    const filterY = 52;
    doc.setFillColor(colors.grayLight[0], colors.grayLight[1], colors.grayLight[2]);
    doc.rect(15, filterY, pageWidth - 30, 10, 'F');
    doc.setFont("helvetica", "italic");
    doc.setFontSize(8.5);
    doc.setTextColor(colors.grayText[0], colors.grayText[1], colors.grayText[2]);
    doc.text(filtrosTexto.length ? `Filtros: ${filtrosTexto.join(" • ")}` : "Filtros: Todas las ventas", 18, filterY + 7);

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
    const logoUrl = window.location.origin + '/static/img/LOGO TRAZO.png';

    const filtrosTexto = [];
    if (reporteFiltrosActuales.q) filtrosTexto.push(`Búsqueda: ${reporteFiltrosActuales.q}`);
    if (reporteFiltrosActuales.estado) filtrosTexto.push(`Estado: ${reporteFiltrosActuales.estado}`);
    if (reporteFiltrosActuales.metodo_pago) filtrosTexto.push(`Método: ${reporteFiltrosActuales.metodo_pago}`);

    ventana.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>Reporte de Ventas</title>
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
        <h1>REPORTE DE VENTAS</h1>
        <div class="info">Generado: ${fecha} • Total ventas: ${reporteDatosActuales.length}</div>
        ${filtrosTexto.length ? `<div class="filters"><strong>Filtros:</strong> ${filtrosTexto.join(" • ")}</div>` : ''}
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
        <div class="footer">ItuAccesorio System · Reporte Generado Exclusivamente Para ituaccesorio</div>
      </body>
      </html>
    `);
    ventana.document.close();
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

  // ==================== INICIALIZACIÓN ====================
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

    // Inicializar buscador de clientes
    initClienteBuscador();

    // Inicializar FieldValidator
    if (window.FieldValidator) {
      setTimeout(() => window.FieldValidator.init(), 100);
    }

    // Cargar datos iniciales
    cargarProductosParaSelect();
    cargarClientes();
    cargarVentasLocales();
    generarReporte();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
