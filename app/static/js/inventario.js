(() => {
	"use strict";

	const csrfToken = document.querySelector("input[name='_csrf_token']")?.value || "";

	function getAuthToken() {
		const fromLocal = window.localStorage ? window.localStorage.getItem("access_token") : "";
		if (fromLocal) return fromLocal;
		const fromSession = window.sessionStorage ? window.sessionStorage.getItem("access_token") : "";
		if (fromSession) return fromSession;
		return "";
	}

	async function fetchJson(url, options = {}) {
		const authToken = getAuthToken();
		const response = await fetch(url, {
			headers: {
				Accept: "application/json",
				...(options.method && options.method !== "GET" ? { "Content-Type": "application/json" } : {}),
				...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
				...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
				...(options.headers || {}),
			},
			credentials: "same-origin",
			...options,
		});

		const data = await response.json().catch(() => ({}));
		if (!response.ok || data?.success === false) {
			throw new Error(data?.error || `HTTP ${response.status}`);
		}
		return data;
	}

	const formatMoney = (value) => {
		if (value === null || value === undefined || value === '') return '-';
		const num = Number(value);
		if (Number.isNaN(num)) return String(value);
		return `$${num.toLocaleString('es-VE')}`;
	};

	const normalizeText = (value) => {
		if (value === null || value === undefined) return '-';
		const text = String(value).trim();
		return text === '' ? '-' : text;
	};

	const escapeHtml = (value) => String(value ?? '').replace(/[&<>"]|'/g, (char) => ({
		'&': '&amp;',
		'<': '&lt;',
		'>': '&gt;',
		'"': '&quot;',
		"'": '&#39;',
	}[char]));

	const computeStatus = (existencia) => {
		const qty = Number(existencia);
		if (!Number.isFinite(qty)) {
			return { badgeClass: 'badge--warn', statusClass: 'status--warn', label: 'Revisar' };
		}
		if (qty <= 10) return { badgeClass: 'badge--warn', statusClass: 'status--warn', label: qty <= 0 ? 'Sin stock' : 'Bajo stock' };
		return { badgeClass: 'badge--good', statusClass: 'status--good', label: qty >= 30 ? 'Alto stock' : 'Disponible' };
	};

	const setText = (id, value) => {
		const el = document.getElementById(id);
		if (el) el.textContent = String(value);
	};

	const renderTable = (rows) => {
		const tbody = document.getElementById('inventario-tbody');
		if (!tbody) return;

		tbody.innerHTML = '';

		if (!Array.isArray(rows) || rows.length === 0) {
			const tr = document.createElement('tr');
			tr.innerHTML = '<td colspan="7">No hay datos de inventario.</td>';
			tbody.appendChild(tr);
			return;
		}

		const frag = document.createDocumentFragment();
		for (const item of rows) {
			const foto = normalizeText(item?.Foto_inventario ?? item?.foto_inventario);
			const tipo = normalizeText(item?.tipo);
			const marca = normalizeText(item?.N_marca);
			const modelo = normalizeText(item?.N_modelo);
			const existencia = item?.Existencia;
			const costo = item?.Costo_venta;

			const status = computeStatus(existencia);
			const imageCell = foto !== '-' ? `<img class="inventory-thumb" src="${escapeHtml(foto)}" alt="${escapeHtml(modelo)}">` : '<span class="inventory-thumb inventory-thumb--empty">Sin foto</span>';
			const tr = document.createElement('tr');
			tr.innerHTML = `
				<td>${imageCell}</td>
				<td>${escapeHtml(tipo)}</td>
				<td>${escapeHtml(marca)}</td>
				<td>${escapeHtml(modelo)}</td>
				<td><span class="badge ${status.badgeClass}">${escapeHtml(normalizeText(existencia))}</span></td>
				<td>${formatMoney(costo)}</td>
				<td><span class="status ${status.statusClass}">${escapeHtml(status.label)}</span></td>
			`;
			frag.appendChild(tr);
		}
		tbody.appendChild(frag);
	};

	const renderStats = (rows) => {
		const tipos = new Set();
		const marcas = new Set();
		const modelos = new Set();
		let piezas = 0;

		for (const item of rows || []) {
			if (item?.tipo) tipos.add(String(item.tipo));
			if (item?.N_marca) marcas.add(String(item.N_marca));
			if (item?.N_modelo) modelos.add(String(item.N_modelo));
			const qty = Number(item?.Existencia);
			if (Number.isFinite(qty)) piezas += qty;
		}

		setText('inv-stat-clases', tipos.size);
		setText('inv-stat-marcas', marcas.size);
		setText('inv-stat-modelos', modelos.size);
		setText('inv-stat-piezas', piezas);
	};

	const setNote = (text) => {
		const el = document.getElementById('inventario-note');
		if (el) el.textContent = text;
	};

	const stripAccents = (value) => {
		try {
			return String(value ?? '')
				.normalize('NFD')
				.replace(/[\u0300-\u036f]/g, '');
		} catch {
			return String(value ?? '');
		}
	};

	const normalizeKey = (value) => stripAccents(value).toLowerCase().trim();

	let lastRows = [];
	let activeFilter = { kind: 'all', value: '' };

	const filterRows = (rows) => {
		const list = Array.isArray(rows) ? rows : [];
		if (activeFilter.kind === 'all') return list;
		if (activeFilter.kind === 'tipo') {
			const target = normalizeKey(activeFilter.value);
			return list.filter((x) => normalizeKey(x?.tipo) === target);
		}
		if (activeFilter.kind === 'low') {
			return list.filter((x) => {
				const qty = Number(x?.Existencia);
				return Number.isFinite(qty) && qty <= 10;
			});
		}
		return list;
	};

	const getFilterLabel = () => {
		if (activeFilter.kind === 'all') return 'Todos';
		if (activeFilter.kind === 'tipo') return String(activeFilter.value || '');
		if (activeFilter.kind === 'low') return 'Bajo stock';
		return 'Filtro';
	};

	const applyFilterAndRender = () => {
		const filtered = filterRows(lastRows);
		renderTable(filtered);
		renderStats(filtered);
		setNote(`Mostrando ${filtered.length} de ${lastRows.length} registros · ${getFilterLabel()}.`);
	};

	const loadInventario = async () => {
		try {
			setNote('Cargando datos desde el backend…');
			const data = await fetchJson('/api/inventario', { method: 'GET' });
			const rows = Array.isArray(data?.inventario) ? data.inventario : [];
			lastRows = rows;
			applyFilterAndRender();
		} catch (err) {
			console.error('Error cargando inventario:', err);
			const message = String(err?.message || err || '').toLowerCase().includes('401')
				? 'Autenticación requerida para ver inventario.'
				: 'Error cargando inventario.';
			setNote(message);
			renderTable([]);
			renderStats([]);
		}
	};

	const initChips = () => {
		const chipsWrap = document.querySelector('.hero__chips');
		if (!chipsWrap) return;
		const chips = Array.from(chipsWrap.querySelectorAll('.chip'));
		if (chips.length === 0) return;

		const setActiveChip = (chip) => {
			chips.forEach((c) => {
				const isActive = c === chip;
				c.classList.toggle('chip--active', isActive);
				c.setAttribute('aria-pressed', isActive ? 'true' : 'false');
			});
		};

		const activate = (chip) => {
			const kind = String(chip?.dataset?.filter || 'all');
			const value = String(chip?.dataset?.value || '');
			activeFilter = { kind, value };
			setActiveChip(chip);
			applyFilterAndRender();
		};

		chips.forEach((chip) => {
			chip.addEventListener('click', () => activate(chip));
			chip.addEventListener('keydown', (e) => {
				if (e.key === 'Enter' || e.key === ' ') {
					e.preventDefault();
					activate(chip);
				}
			});
		});

		const initial = chips.find((c) => c.classList.contains('chip--active')) || chips[0];
		if (initial) activate(initial);
	};

	document.addEventListener('DOMContentLoaded', () => {
		initChips();
		loadInventario();
	});

})();

// ==================== REPORTES INVENTARIO ====================

let reporteDatosActuales = [];
let reporteFiltrosActuales = {};
let clasesDisponibles = [];
let marcasDisponibles = [];

const btnReportes = document.getElementById("btn-reportes");
const modalReportes = document.getElementById("modal-reportes");
const reporteBusqueda = document.getElementById("reporte-busqueda");
const reporteClase = document.getElementById("reporte-clase");
const reporteMarca = document.getElementById("reporte-marca");
const reporteStockMin = document.getElementById("reporte-stock-min");
const reporteStockMax = document.getElementById("reporte-stock-max");
const btnGenerarReporte = document.getElementById("btn-generar-reporte");
const btnLimpiarFiltros = document.getElementById("btn-limpiar-filtros");
const btnExportarExcel = document.getElementById("btn-exportar-excel");
const btnExportarPdf = document.getElementById("btn-exportar-pdf");
const btnImprimir = document.getElementById("btn-imprimir");
const reportePreview = document.getElementById("reporte-preview");
const reporteTotal = document.getElementById("reporte-total");
const reporteTabla = document.getElementById("reporte-tabla");

function notifyReportes(type, message) {
  if (window.FeedbackModal && typeof window.FeedbackModal.show === 'function') {
    window.FeedbackModal.show({
      type: type === 'error' ? 'error' : 'success',
      title: type === 'error' ? 'No se pudo completar' : 'Acción exitosa',
      message: message,
    });
    return;
  }
  if (type === 'error') {
    alert(message);
  } else {
    console.log(message);
  }
}

async function fetchJsonReportes(url, options = {}) {
  const csrfTokenInput = document.querySelector('input[name="_csrf_token"]')?.value || "";
  const authToken = localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || "";
  
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
      ...(csrfTokenInput ? { "X-CSRFToken": csrfTokenInput } : {}),
      ...(authToken ? { "Authorization": `Bearer ${authToken}` } : {}),
    },
    credentials: "same-origin",
    ...options,
  });
  
  const data = await response.json().catch(() => ({}));
  if (!response.ok || data.success === false) {
    throw new Error(data.error || "Error en la operación");
  }
  return data;
}

function escapeHtmlReportes(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function formatMoneyReportes(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return '';
  return n.toLocaleString('es-VE');
}

function limpiarFiltrosReporte() {
  if (reporteBusqueda) reporteBusqueda.value = "";
  if (reporteClase) reporteClase.value = "";
  if (reporteMarca) reporteMarca.value = "";
  if (reporteStockMin) reporteStockMin.value = "";
  if (reporteStockMax) reporteStockMax.value = "";
}

function cargarFiltrosReporte(clases, marcas) {
  clasesDisponibles = clases || [];
  marcasDisponibles = marcas || [];
  
  if (reporteClase) {
    reporteClase.innerHTML = '<option value="">Todas</option>' + 
      clasesDisponibles.map(c => `<option value="${escapeHtmlReportes(c)}">${escapeHtmlReportes(c)}</option>`).join("");
  }
  if (reporteMarca) {
    reporteMarca.innerHTML = '<option value="">Todas</option>' + 
      marcasDisponibles.map(m => `<option value="${escapeHtmlReportes(m)}">${escapeHtmlReportes(m)}</option>`).join("");
  }
}

async function cargarClasesMarcasIniciales() {
  try {
    const clasesData = await fetchJsonReportes("/api/productos/clases", { method: "GET" });
    const clases = (clasesData.clases || []).map(c => c.nombre);
    clasesDisponibles = [...new Set(clases)];
    
    const marcasData = await fetchJsonReportes("/api/productos/marcas", { method: "GET" });
    const marcas = (marcasData.marcas || []).map(m => m.nombre);
    marcasDisponibles = [...new Set(marcas)];
    
    if (reporteClase) {
      reporteClase.innerHTML = '<option value="">Todas</option>' + 
        clasesDisponibles.map(c => `<option value="${escapeHtmlReportes(c)}">${escapeHtmlReportes(c)}</option>`).join("");
    }
    if (reporteMarca) {
      reporteMarca.innerHTML = '<option value="">Todas</option>' + 
        marcasDisponibles.map(m => `<option value="${escapeHtmlReportes(m)}">${escapeHtmlReportes(m)}</option>`).join("");
    }
  } catch (err) {
    console.error("Error cargando clases/marcas iniciales:", err);
  }
}

function getStatusLabel(stock) {
  const qty = Number(stock);
  if (qty === 0) return { label: 'Sin stock', class: 'status-out' };
  if (qty <= 5) return { label: 'Bajo stock', class: 'status-low' };
  if (qty >= 30) return { label: 'Alto stock', class: 'status-good' };
  return { label: 'Disponible', class: 'status-normal' };
}

async function generarReporteInventario() {
  const filtros = {
    q: reporteBusqueda?.value || "",
    tipo: reporteClase?.value || null,
    marca: reporteMarca?.value || null,
    stock_min: reporteStockMin?.value ? parseInt(reporteStockMin.value) : null,
    stock_max: reporteStockMax?.value ? parseInt(reporteStockMax.value) : null,
  };
  
  reporteFiltrosActuales = filtros;
  
  if (btnGenerarReporte) {
    btnGenerarReporte.disabled = true;
    btnGenerarReporte.textContent = "Cargando...";
  }
  
  try {
    const data = await fetchJsonReportes("/api/inventario/reportes", {
      method: "POST",
      body: JSON.stringify(filtros)
    });
    
    reporteDatosActuales = data.inventario || [];
    const total = data.total || 0;
    
    if (data.clases && data.clases.length > 0) {
      cargarFiltrosReporte(data.clases, data.marcas || []);
    } else {
      cargarFiltrosReporte(clasesDisponibles, marcasDisponibles);
    }
    
    if (reportePreview) reportePreview.style.display = "block";
    if (reporteTotal) reporteTotal.textContent = `Total de productos: ${total}`;
    
    if (reporteTabla) {
      if (reporteDatosActuales.length === 0) {
        reporteTabla.innerHTML = '<tr><td colspan="7" class="table__empty">No hay productos con esos filtros</td</tr>';
      } else {
        reporteTabla.innerHTML = reporteDatosActuales.map(p => {
          const status = getStatusLabel(p.existencia || 0);
          const foto = p.foto_inventario || '';
          const fotoHtml = foto ? `<img src="${foto}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 6px;">` : '<span style="color:#999;">Sin foto</span>';
          return `
            <tr>
              <td>${fotoHtml}</td>
              <td><strong>${escapeHtmlReportes(p.nombre_producto || '-')}</strong></td>
              <td>${escapeHtmlReportes(p.nombre_marca || '-')}</td>
              <td>${escapeHtmlReportes(p.nombre_clase || '-')}</td>
              <td><span class="status-badge ${status.class}">${p.existencia || 0} uds</span></td>
              <td>$${formatMoneyReportes(p.costo_venta || 0)}</td>
              <td><span class="status-badge ${status.class}">${status.label}</span></td>
            </tr>
          `;
        }).join("");
      }
    }
    
    if (btnExportarExcel) btnExportarExcel.disabled = false;
    if (btnExportarPdf) btnExportarPdf.disabled = false;
    if (btnImprimir) btnImprimir.disabled = false;
    
  } catch (err) {
    notifyReportes('error', err.message || "Error al generar el reporte");
  } finally {
    if (btnGenerarReporte) {
      btnGenerarReporte.disabled = false;
      btnGenerarReporte.textContent = "🔍 Generar reporte";
    }
  }
}

function exportarInventarioExcel() {
  if (reporteDatosActuales.length === 0) {
    notifyReportes('error', "No hay datos para exportar");
    return;
  }
  
  const datos = reporteDatosActuales.map(p => ({
    "Producto": p.nombre_producto || '',
    "Marca": p.nombre_marca || '',
    "Clase": p.nombre_clase || '',
    "Existencia": p.existencia || 0,
    "Costo Venta (USD)": p.costo_venta || 0,
    "Valor Total (USD)": (p.existencia || 0) * (p.costo_venta || 0)
  }));
  
  if (typeof XLSX === 'undefined') {
    notifyReportes('info', "Cargando librería de Excel...");
    const script = document.createElement('script');
    script.src = '/static/js/libs/xlsx.full.min.js';
    script.onload = () => exportarInventarioExcel();
    document.head.appendChild(script);
    return;
  }
  
  const ws = XLSX.utils.json_to_sheet(datos);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "Inventario");
  
  ws['!cols'] = [{ wch: 35 }, { wch: 20 }, { wch: 20 }, { wch: 12 }, { wch: 15 }, { wch: 18 }];
  
  XLSX.writeFile(wb, `inventario_${new Date().toISOString().slice(0,19)}.xlsx`);
  notifyReportes('success', "Reporte exportado a Excel");
}

function exportarInventarioPdf() {
  if (reporteDatosActuales.length === 0) {
    notifyReportes('error', "No hay datos para exportar");
    return;
  }
  
  if (typeof window.jspdf === 'undefined' || typeof window.jspdf.jsPDF === 'undefined') {
    notifyReportes('info', "Cargando librería de PDF...");
    const script1 = document.createElement('script');
    script1.src = '/static/js/libs/jspdf.umd.min.js';
    script1.onload = () => {
      const script2 = document.createElement('script');
      script2.src = '/static/js/libs/jspdf.plugin.autotable.min.js';
      script2.onload = () => {
        setTimeout(() => exportarInventarioPdf(), 100);
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
  
  const logoUrl = window.location.origin + '/static/img/LOGO COMPLETO.png';
  try {
    doc.addImage(logoUrl, 'PNG', (pageWidth - 45) / 2, 8, 45, 14);
  } catch(e) {}
  
  doc.setFont("helvetica", "bold");
  doc.setFontSize(22);
  doc.setTextColor(colors.dark[0], colors.dark[1], colors.dark[2]);
  doc.text("REPORTE DE INVENTARIO", pageWidth / 2, 30, { align: 'center' });
  
  doc.setDrawColor(colors.primary[0], colors.primary[1], colors.primary[2]);
  doc.setLineWidth(0.8);
  doc.line(pageWidth / 2 - 35, 34, pageWidth / 2 + 35, 34);
  
  const now = new Date();
  const fechaStr = now.toLocaleDateString('es-ES');
  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  doc.setTextColor(colors.grayText[0], colors.grayText[1], colors.grayText[2]);
  doc.text(`Generado: ${fechaStr} • Total productos: ${reporteDatosActuales.length}`, pageWidth / 2, 44, { align: 'center' });
  
  const filtrosTexto = [];
  if (reporteFiltrosActuales.q) filtrosTexto.push(`Búsqueda: ${reporteFiltrosActuales.q}`);
  if (reporteFiltrosActuales.tipo) filtrosTexto.push(`Clase: ${reporteFiltrosActuales.tipo}`);
  if (reporteFiltrosActuales.marca) filtrosTexto.push(`Marca: ${reporteFiltrosActuales.marca}`);
  if (reporteFiltrosActuales.stock_min) filtrosTexto.push(`Stock ≥ ${reporteFiltrosActuales.stock_min}`);
  if (reporteFiltrosActuales.stock_max) filtrosTexto.push(`Stock ≤ ${reporteFiltrosActuales.stock_max}`);
  
  const filterY = 52;
  doc.setFillColor(colors.grayLight[0], colors.grayLight[1], colors.grayLight[2]);
  doc.rect(15, filterY, pageWidth - 30, 10, 'F');
  doc.setFont("helvetica", "italic");
  doc.setFontSize(8.5);
  doc.setTextColor(colors.grayText[0], colors.grayText[1], colors.grayText[2]);
  doc.text(filtrosTexto.length ? `Filtros: ${filtrosTexto.join(" • ")}` : "Filtros: Todos los productos", 18, filterY + 7);
  
  const columns = ["PRODUCTO", "MARCA", "CLASE", "STOCK", "COSTO (USD)", "VALOR TOTAL"];
  const rows = reporteDatosActuales.map(p => [
    p.nombre_producto || "",
    p.nombre_marca || "-",
    p.nombre_clase || "-",
    `${p.existencia || 0} uds`,
    `$${Number(p.costo_venta || 0).toLocaleString('es-VE')}`,
    `$${((p.existencia || 0) * (p.costo_venta || 0)).toLocaleString('es-VE')}`
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
  });
  
  doc.save(`inventario_${now.toISOString().slice(0,19)}.pdf`);
  notifyReportes('success', "Reporte exportado a PDF");
}

function imprimirReporteInventario() {
  if (reporteDatosActuales.length === 0) {
    notifyReportes('error', "No hay datos para imprimir");
    return;
  }
  
  const ventana = window.open("", "_blank");
  const fecha = new Date().toLocaleString();
  const logoUrl = window.location.origin + '/static/img/LOGO COMPLETO.png';
  
  const filtrosTexto = [];
  if (reporteFiltrosActuales.q) filtrosTexto.push(`Búsqueda: ${reporteFiltrosActuales.q}`);
  if (reporteFiltrosActuales.tipo) filtrosTexto.push(`Clase: ${reporteFiltrosActuales.tipo}`);
  if (reporteFiltrosActuales.marca) filtrosTexto.push(`Marca: ${reporteFiltrosActuales.marca}`);
  if (reporteFiltrosActuales.stock_min) filtrosTexto.push(`Stock ≥ ${reporteFiltrosActuales.stock_min}`);
  if (reporteFiltrosActuales.stock_max) filtrosTexto.push(`Stock ≤ ${reporteFiltrosActuales.stock_max}`);
  
  ventana.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Reporte de Inventario</title>
      <style>
        @media print { body { margin: 0; padding: 20px; } .no-print { display: none; } }
        body { font-family: Arial, sans-serif; margin: 20px; padding: 20px; background: white; }
        h1 { text-align: center; border-bottom: 3px solid #f3c500; padding-bottom: 10px; }
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
        .status-out { color: #dc2626; font-weight: bold; }
        .status-low { color: #f59e0b; font-weight: bold; }
        .status-good { color: #10b981; font-weight: bold; }
        .status-normal { color: #3b82f6; }
      </style>
    </head>
    <body>
      <button class="btn-print no-print" onclick="window.print()">🖨 Imprimir</button>
      <div class="logo"><img src="${logoUrl}" alt="ItuAccesorio" onerror="this.style.display='none'"></div>
      <h1>REPORTE DE INVENTARIO</h1>
      <div class="info">Generado: ${fecha} • Total productos: ${reporteDatosActuales.length}</div>
      ${filtrosTexto.length ? `<div class="filters"><strong>Filtros:</strong> ${filtrosTexto.join(" • ")}</div>` : ''}
      <table>
        <thead>
          <tr>
            <th>Producto</th>
            <th>Marca</th>
            <th>Clase</th>
            <th>Stock</th>
            <th>Costo (USD)</th>
          </tr>
        </thead>
        <tbody>
          ${reporteDatosActuales.map(p => {
            let stockClass = '';
            if (p.existencia === 0) stockClass = 'status-out';
            else if (p.existencia <= 5) stockClass = 'status-low';
            else if (p.existencia >= 30) stockClass = 'status-good';
            else stockClass = 'status-normal';
            return `
              <tr>
                <td><strong>${escapeHtmlReportes(p.nombre_producto || '-')}</strong></td>
                <td>${escapeHtmlReportes(p.nombre_marca || '-')}</td>
                <td>${escapeHtmlReportes(p.nombre_clase || '-')}</td>
                <td class="${stockClass}">${p.existencia || 0} uds</td>
                <td>$${Number(p.costo_venta || 0).toLocaleString('es-VE')}</td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
      <div class="footer">ItuAccesorio System - Reporte Generado Exclusivamente Para ituaccesorio</div>
    </body>
    </html>
  `);
  ventana.document.close();
}

// Eventos de reportes
if (btnReportes) {
  btnReportes.addEventListener("click", async () => {
    limpiarFiltrosReporte();
    if (reportePreview) reportePreview.style.display = "none";
    if (btnExportarExcel) btnExportarExcel.disabled = true;
    if (btnExportarPdf) btnExportarPdf.disabled = true;
    if (btnImprimir) btnImprimir.disabled = true;
    
    await cargarClasesMarcasIniciales();
    
    if (window.UiModal && typeof window.UiModal.openById === 'function') {
      window.UiModal.openById('modal-reportes');
    } else if (modalReportes) {
      modalReportes.hidden = false;
      modalReportes.setAttribute("aria-hidden", "false");
    }
  });
}

if (btnGenerarReporte) btnGenerarReporte.addEventListener("click", generarReporteInventario);
if (btnLimpiarFiltros) btnLimpiarFiltros.addEventListener("click", limpiarFiltrosReporte);
if (btnExportarExcel) btnExportarExcel.addEventListener("click", exportarInventarioExcel);
if (btnExportarPdf) btnExportarPdf.addEventListener("click", exportarInventarioPdf);
if (btnImprimir) btnImprimir.addEventListener("click", imprimirReporteInventario);

if (modalReportes) {
  modalReportes.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;

    if (target.dataset.modalClose === "true") {
      if (window.UiModal && typeof window.UiModal.closeById === 'function') {
        window.UiModal.closeById('modal-reportes');
      } else {
        modalReportes.hidden = true;
        modalReportes.setAttribute("aria-hidden", "true");
      }
      return;
    }

    if (target === modalReportes) {
      if (window.UiModal && typeof window.UiModal.closeById === 'function') {
        window.UiModal.closeById('modal-reportes');
      } else {
        modalReportes.hidden = true;
        modalReportes.setAttribute("aria-hidden", "true");
      }
    }
  });
}

document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  if (window.UiModal && typeof window.UiModal.closeById === 'function') {
    window.UiModal.closeById('modal-reportes');
  } else if (modalReportes && !modalReportes.hidden) {
    modalReportes.hidden = true;
    modalReportes.setAttribute("aria-hidden", "true");
  }
});