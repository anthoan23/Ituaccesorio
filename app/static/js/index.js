document.addEventListener('DOMContentLoaded', function() {
    // ============================================================
    // 1. FECHA ACTUAL - ya está en el navbar
    // ============================================================

    // ============================================================
    // 2. LOAD KPI DATA
    // ============================================================
    async function loadKPI() {
        try {
            // Ventas Hoy
            const ventasResp = await fetch('/api/dashboard/ventas-hoy');
            const ventasData = await ventasResp.json();
            if (ventasData.success) {
                const simbolo = ventasData.simbolo || '$';
                const kpiVentas = document.getElementById('kpi-ventas-hoy');
                if (kpiVentas) kpiVentas.textContent = `${simbolo} ${ventasData.total_formateado || '0.00'}`;
                
                const widgetVentas = document.getElementById('widget-ventas-semana');
                if (widgetVentas) widgetVentas.textContent = `${simbolo} ${ventasData.total_formateado || '0.00'}`;
            }

            // Órdenes Activas
            const ordenesResp = await fetch('/api/dashboard/ordenes-servicio');
            const ordenesData = await ordenesResp.json();
            if (ordenesData.success) {
                const kpiOrdenes = document.getElementById('kpi-ordenes-activas');
                if (kpiOrdenes) kpiOrdenes.textContent = ordenesData.total || '0';
                
                const widgetReparaciones = document.getElementById('widget-reparaciones-pendientes');
                if (widgetReparaciones) widgetReparaciones.textContent = ordenesData.total || '0';
            }

            // Equipos Reparados (simulado)
            const kpiReparados = document.getElementById('kpi-reparados');
            if (kpiReparados) kpiReparados.textContent = '24';

            // Ingresos Mensuales (simulado)
            const kpiIngresos = document.getElementById('kpi-ingresos');
            if (kpiIngresos) kpiIngresos.textContent = '$12,450';

            // Stock Bajo
            const stockResp = await fetch('/api/dashboard/bajo-stock');
            const stockData = await stockResp.json();
            if (stockData.success) {
                const widgetStock = document.getElementById('widget-stock-bajo');
                if (widgetStock) widgetStock.textContent = (stockData.productos || []).length || '0';
            }

            // Técnicos Activos (simulado)
            const widgetTecnicos = document.getElementById('widget-tecnicos-activos');
            if (widgetTecnicos) widgetTecnicos.textContent = '4';

        } catch (error) {
            console.error('Error cargando KPI:', error);
        }
    }
    loadKPI();

    // ============================================================
    // 3. CHART.JS - GRÁFICO PRINCIPAL
    // ============================================================
    async function loadChart() {
        const canvas = document.getElementById('main-chart');
        if (!canvas) return;

        try {
            const response = await fetch('/api/dashboard/ingresos-gastos');
            const data = await response.json();

            const ctx = canvas.getContext('2d');
            const labels = data.success ? (data.etiquetas || ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']) : ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
            const ingresos = data.success ? (data.ingresos || [0, 0, 0, 0, 0, 0, 0]) : [1200, 1900, 1500, 2200, 1800, 2500, 2100];
            const gastos = data.success ? (data.gastos || [0, 0, 0, 0, 0, 0, 0]) : [800, 1400, 1100, 1600, 1300, 1900, 1500];

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Ingresos',
                            data: ingresos,
                            borderColor: '#FFD60A',
                            backgroundColor: 'rgba(255,214,10,0.08)',
                            fill: true,
                            tension: 0.4,
                            pointBackgroundColor: '#FFD60A',
                            pointBorderColor: '#FFD60A',
                            pointRadius: 4,
                            pointHoverRadius: 6,
                        },
                        {
                            label: 'Gastos',
                            data: gastos,
                            borderColor: '#6B6B76',
                            backgroundColor: 'rgba(107,107,118,0.08)',
                            fill: true,
                            tension: 0.4,
                            pointBackgroundColor: '#6B6B76',
                            pointBorderColor: '#6B6B76',
                            pointRadius: 4,
                            pointHoverRadius: 6,
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: 'rgba(10,10,10,0.95)',
                            titleColor: '#FFFFFF',
                            bodyColor: '#A1A1AA',
                            cornerRadius: 12,
                            padding: 12,
                            borderColor: 'rgba(255,255,255,0.06)',
                            borderWidth: 1,
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { color: '#6B6B76' }
                        },
                        y: {
                            grid: { color: 'rgba(255,255,255,0.04)' },
                            ticks: { color: '#6B6B76' }
                        }
                    },
                    interaction: {
                        intersect: false,
                        mode: 'index',
                    },
                }
            });
        } catch (error) {
            console.error('Error cargando gráfico:', error);
        }
    }
    loadChart();

    // ============================================================
    // 4. ACTIVIDAD RECIENTE
    // ============================================================
    async function loadActivity() {
        const container = document.getElementById('activity-list');
        if (!container) return;

        try {
            const response = await fetch('/api/dashboard/actividad-reciente');
            const data = await response.json();

            if (data.success && data.actividades && data.actividades.length > 0) {
                const icons = {
                    'venta': '💰',
                    'inventario': '📦',
                    'producto': '📱',
                    'proveedor': '🏭',
                    'orden': '📋',
                    'entrega': '🚚',
                };
                
                container.innerHTML = data.actividades.slice(0, 5).map(act => {
                    const modulo = (act.modulo_nombre || '').toLowerCase();
                    let icon = '🔔';
                    for (const [key, value] of Object.entries(icons)) {
                        if (modulo.includes(key)) { icon = value; break; }
                    }
                    return `
                        <div class="activity-item">
                            <div class="activity-item__icon">${icon}</div>
                            <div class="activity-item__content">
                                <p class="activity-item__text">
                                    <strong>${escapeHtml(act.usuario_id || 'Sistema')}</strong>
                                    ${escapeHtml(act.descripcion || act.accion || 'Actividad registrada')}
                                </p>
                                <span class="activity-item__time">${escapeHtml(act.tiempo_relativo || 'recientemente')}</span>
                            </div>
                        </div>
                    `;
                }).join('');
            } else {
                container.innerHTML = `
                    <div class="activity-item">
                        <div class="activity-item__icon">📭</div>
                        <div class="activity-item__content">
                            <p class="activity-item__text">No hay actividad reciente</p>
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error cargando actividad:', error);
            container.innerHTML = `
                <div class="activity-item">
                    <div class="activity-item__icon">⚠️</div>
                    <div class="activity-item__content">
                        <p class="activity-item__text">Error al cargar actividad</p>
                    </div>
                </div>
            `;
        }
    }
    loadActivity();

    // ============================================================
    // 5. ÓRDENES RECIENTES
    // ============================================================
    async function loadOrders() {
        const container = document.getElementById('orders-table-body');
        if (!container) return;

        try {
            const response = await fetch('/api/ordenes_compra');
            const data = await response.json();

            if (Array.isArray(data) && data.length > 0) {
                const orders = data.slice(0, 5);
                const statusMap = {
                    'Pendiente': 'pendiente',
                    'En proceso': 'proceso',
                    'Completada': 'completada',
                };
                
                container.innerHTML = orders.map(order => {
                    const estado = order.Estado || 'Pendiente';
                    const statusClass = statusMap[estado] || 'pendiente';
                    return `
                        <tr>
                            <td>${escapeHtml(order.ID_orden_c)}</td>
                            <td>${escapeHtml(order.N_proveedor || 'Sin proveedor')}</td>
                            <td><span class="status-chip status-chip--${statusClass}">${escapeHtml(estado)}</span></td>
                            <td>${escapeHtml(formatDate(order.Fecha_o))}</td>
                            <td>Bs ${escapeHtml(formatMoney(order.Costo_venta || 0))}</td>
                        </tr>
                    `;
                }).join('');
            } else {
                container.innerHTML = `
                    <tr>
                        <td colspan="5" style="text-align:center;color:var(--text-muted);padding:16px;">
                            No hay órdenes recientes
                        </td>
                    </tr>
                `;
            }
        } catch (error) {
            console.error('Error cargando órdenes:', error);
            container.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align:center;color:var(--text-muted);padding:16px;">
                        Error al cargar órdenes
                    </td>
                </tr>
            `;
        }
    }
    loadOrders();

    // ============================================================
    // 6. PRODUCTOS BAJO STOCK (card original)
    // ============================================================
    async function cargarProductosBajoStock() {
        const container = document.getElementById('low-stock-list');
        if (!container) return;

        try {
            const response = await fetch('/api/dashboard/bajo-stock', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });

            const data = await response.json();

            if (data.success && data.productos && data.productos.length > 0) {
                container.innerHTML = data.productos.map(producto => {
                    const stock = producto.existencia || 0;
                    const foto = producto.foto_inventario || '';
                    
                    let stockClass = '';
                    let stockText = '';
                    if (stock === 0) {
                        stockClass = 'badge--danger';
                        stockText = 'Sin stock';
                    } else if (stock <= 5) {
                        stockClass = 'badge--warning';
                        stockText = 'Bajo stock';
                    } else if (stock <= 10) {
                        stockClass = 'badge--info';
                        stockText = 'Stock límite';
                    } else {
                        stockClass = 'badge--success';
                        stockText = 'Stock disponible';
                    }
                    
                    const imagenHtml = foto ? 
                        `<img src="${foto}" alt="${escapeHtml(producto.nombre_producto || 'Producto')}" class="low-stock-img">` : 
                        `<div class="low-stock-img low-stock-img--empty">📦</div>`;
                    
                    return `
                        <div class="low-stock-item">
                            <div class="low-stock-thumb">
                                ${imagenHtml}
                            </div>
                            <div class="low-stock-info">
                                <div class="low-stock-name">${escapeHtml(producto.nombre_producto || 'Sin nombre')}</div>
                                <div class="low-stock-marca">${escapeHtml(producto.nombre_marca || 'Sin marca')} • ${escapeHtml(producto.nombre_clase || 'Sin clase')}</div>
                            </div>
                            <div class="low-stock-stock">
                                <div class="low-stock-cantidad">${stock} uds</div>
                                <span class="low-stock-badge ${stockClass}">${stockText}</span>
                            </div>
                        </div>
                    `;
                }).join('');
            } else {
                container.innerHTML = '<div class="empty-message">✅ No hay productos con bajo stock</div>';
            }
        } catch (error) {
            console.error('Error cargando productos con bajo stock:', error);
            container.innerHTML = '<div class="empty-message">❌ Error al cargar los datos</div>';
        }
    }

    // ============================================================
    // 7. ACCIONES RÁPIDAS
    // ============================================================
    document.querySelectorAll('.quick-action').forEach(btn => {
        btn.addEventListener('click', function() {
            const action = this.dataset.action;
            if (action === 'orden') window.location.href = '/ordenes_compra';
            else if (action === 'reparacion') window.location.href = '/ordenes_servicio';
            else if (action === 'producto') window.location.href = '/productos';
            else if (action === 'cliente') window.location.href = '/clientes';
        });
    });

    // ============================================================
    // 8. UTILITIES
    // ============================================================
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function formatDate(dateStr) {
        if (!dateStr) return 'Fecha no disponible';
        try {
            if (typeof dateStr === 'string' && dateStr.match(/^\d{4}-\d{2}-\d{2}/)) {
                const [year, month, day] = dateStr.split('-');
                return `${day}/${month}/${year}`;
            }
            const date = new Date(dateStr);
            if (!isNaN(date.getTime())) {
                return `${String(date.getDate()).padStart(2, '0')}/${String(date.getMonth() + 1).padStart(2, '0')}/${date.getFullYear()}`;
            }
            return dateStr;
        } catch {
            return dateStr || 'Fecha inválida';
        }
    }

    function formatMoney(value) {
        const num = Number(value);
        if (isNaN(num)) return '0';
        return num.toLocaleString('es-VE');
    }

    // ============================================================
    // 9. INICIALIZAR
    // ============================================================
    cargarProductosBajoStock();
});