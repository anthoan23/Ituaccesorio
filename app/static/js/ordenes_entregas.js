document.addEventListener('DOMContentLoaded', () => {
    // Elementos DOM
    const vistaPendientes = document.getElementById('vista-pendientes');
    const vistaEntregadas = document.getElementById('vista-entregadas');
    const btnPendientes = document.getElementById('btn-pendientes');
    const btnEntregadas = document.getElementById('btn-entregadas');
    const tablaPendientes = document.getElementById('tabla-ordenes-entregas-pendientes');
    const tablaHistorial = document.getElementById('tabla-ordenes-entregas-historial');
    const modalDetalle = document.getElementById('modal-detalle-orden');
    const modalEntrega = document.getElementById('modal-registrar-entrega');
    const btnConfirmarEntrega = document.getElementById('btn-confirmar-entrega');
    const entregaRecibidoPor = document.getElementById('entrega-recibido-por');
    const entregaFecha = document.getElementById('entrega-fecha');

    // Estado
    let ordenParaEntrega = null;

    // CSRF Token
    const csrfToken = document.querySelector('input[name="_csrf_token"]')?.value || '';
    
    // Access Token
    function getAccessToken() {
        return localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || '';
    }

    // Helper: Fetch con autenticación
    async function fetchJson(url, options = {}) {
        const authToken = getAccessToken();
        
        const headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            ...(csrfToken && { 'X-CSRFToken': csrfToken }),
            ...(authToken && { 'Authorization': `Bearer ${authToken}` }),
            ...options.headers
        };

        console.log("Fetching:", url, options.method || 'GET');

        const response = await fetch(url, {
            ...options,
            headers,
            credentials: 'same-origin'
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            const errorMsg = data.error || data.message || `HTTP ${response.status}`;
            throw new Error(errorMsg);
        }

        return data;
    }

    // Función mostrarMensaje
    function mostrarMensaje(mensaje, esError = false) {
        if (window.FeedbackModal && typeof window.FeedbackModal.show === 'function') {
            window.FeedbackModal.show({
                type: esError ? 'error' : 'success',
                title: esError ? 'Error' : 'Éxito',
                message: mensaje,
            });
        } else {
            if (esError) {
                alert(mensaje);
            } else {
                console.log(mensaje);
            }
        }
    }

    // Formatear moneda
    function formatMoney(value) {
        const num = Number(value);
        if (isNaN(num)) return '0';
        return num.toLocaleString('es-VE');
    }

    // Formatear fecha
    function formatDate(dateStr) {
        if (!dateStr) return 'Fecha no disponible';
        try {
            if (typeof dateStr === 'string') {
                const datePart = dateStr.substring(0, 10);
                if (datePart.match(/^\d{4}-\d{2}-\d{2}/)) {
                    const [year, month, day] = datePart.split('-');
                    return `${day}/${month}/${year}`;
                }
            }
            const date = new Date(dateStr);
            if (!isNaN(date.getTime())) {
                const day = String(date.getDate()).padStart(2, '0');
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const year = date.getFullYear();
                return `${day}/${month}/${year}`;
            }
            return dateStr;
        } catch (error) {
            return dateStr || 'Fecha inválida';
        }
    }

    // Cambiar vista
    function cambiarVista(vista) {
        if (vista === 'pendientes') {
            if (vistaPendientes) vistaPendientes.classList.remove('hidden');
            if (vistaEntregadas) vistaEntregadas.classList.add('hidden');
            if (btnPendientes) btnPendientes.classList.add('is-active');
            if (btnEntregadas) btnEntregadas.classList.remove('is-active');
            cargarPendientes();
        } else {
            if (vistaPendientes) vistaPendientes.classList.add('hidden');
            if (vistaEntregadas) vistaEntregadas.classList.remove('hidden');
            if (btnPendientes) btnPendientes.classList.remove('is-active');
            if (btnEntregadas) btnEntregadas.classList.add('is-active');
            cargarHistorial();
        }
    }

    //Cargar pendientes de entrega - usa /api/ordenes_entregas/pendientes
    async function cargarPendientes() {
        if (!tablaPendientes) return;
        
        try {
            console.log("Cargando pendientes desde /api/ordenes_entregas/pendientes");
            const data = await fetchJson('/api/ordenes_entregas/pendientes');
            console.log("Datos recibidos:", data);
            
            if (Array.isArray(data) && data.length > 0) {
                tablaPendientes.innerHTML = data.map(orden => `
                    <tr>
                        <td>${escapeHtml(orden.ID_orden_c)}</td>
                        <td><strong>${escapeHtml(orden.N_proveedor || 'Sin proveedor')}</strong></td>
                        <td>${escapeHtml(formatDate(orden.Fecha_o))}</td>
                        <td><span class="status-badge status-pendiente">${escapeHtml(orden.Estado || 'Pendiente')}</span></td>
                        <td>Bs. ${escapeHtml(formatMoney(orden.Costo_venta || 0))}</td>
                        <td class="table__actions">
                            <button class="btn btn--small btn-ver" data-id="${escapeHtml(orden.ID_orden_c)}">Ver</button>
                            <button class="btn btn--small btn-entrega" data-id="${escapeHtml(orden.ID_orden_c)}">Registrar entrega</button>
                        </td>
                    </tr>
                `).join('');
            } else {
                tablaPendientes.innerHTML = '<tr><td colspan="6" class="table__empty">No hay órdenes pendientes de entrega.</td></tr>';
            }
        } catch (error) {
            console.error('Error cargando pendientes:', error);
            tablaPendientes.innerHTML = `<tr><td colspan="6" class="table__empty">Error al cargar las órdenes: ${escapeHtml(error.message)}</td></tr>`;
        }
    }

// Cargar historial de entregas
async function cargarHistorial() {
    console.log("📋 cargarHistorial() INICIADO");
    if (!tablaHistorial) {
        console.error("❌ tablaHistorial es NULL");
        return;
    }
    
    try {
        const data = await fetchJson('/api/ordenes_entregas/historial');
        console.log("📊 Datos historial:", data);
        
        if (Array.isArray(data) && data.length > 0) {
            tablaHistorial.innerHTML = data.map(entrega => `
                <tr>
                    <td>${escapeHtml(entrega.ID_entrega)}</td>
                    <td>${escapeHtml(entrega.ID_orden_c)}</td>
                    <td>${escapeHtml(entrega.Proveedor || 'Sin proveedor')}</td>
                    <td>${escapeHtml(formatDate(entrega.Fecha_entrega))}</td>
                    <td>${escapeHtml(entrega.Recibido_por || '-')}</td>
                    <td class="table__actions">
                        <button class="btn btn--small btn-ver" data-id="${escapeHtml(entrega.ID_orden_c)}">Ver orden</button>
                    </td>
                </tr>
            `).join('');
        } else {
            tablaHistorial.innerHTML = '<tr><td colspan="6" class="table__empty">No hay entregas registradas.</td></tr>';
        }
    } catch (error) {
        console.error('❌ Error cargando historial:', error);
        tablaHistorial.innerHTML = `<tr><td colspan="6" class="table__empty">Error: ${escapeHtml(error.message)}</td></tr>`;
    }
}

    // Ver detalle de orden
    async function verDetalle(id) {
        try {
            console.log("Ver detalle de orden:", id);
            const data = await fetchJson(`/api/detalles_orden/${id}`, { method: 'GET' });
            
            const detalle = data.datos_orden;
            const productos = data.productos_orden || [];

            if (detalle) {
                const infoContainer = document.getElementById('detalle-orden-info');
                const productosContainer = document.getElementById('detalle-orden-productos');
                const totalSpan = document.getElementById('detalle-orden-total-value');
                
                if (infoContainer) {
                    infoContainer.innerHTML = `
                        <div class="device-detail__grid">
                            <div class="detail-item">
                                <span class="device-detail__label">ID Orden</span>
                                <span class="device-detail__value">${escapeHtml(detalle.ID_orden_c)}</span>
                            </div>
                            <div class="detail-item">
                                <span class="device-detail__label">Proveedor</span>
                                <span class="device-detail__value">${escapeHtml(detalle.nombre)}</span>
                            </div>
                            <div class="detail-item">
                                <span class="device-detail__label">Fecha</span>
                                <span class="device-detail__value">${escapeHtml(formatDate(detalle.Fecha_o))}</span>
                            </div>
                            <div class="detail-item">
                                <span class="device-detail__label">Estado</span>
                                <span class="device-detail__value">${escapeHtml(detalle.Estado)}</span>
                            </div>
                            <div class="detail-item">
                                <span class="device-detail__label">Realizado por</span>
                                <span class="device-detail__value">${escapeHtml(detalle.Realizado_por || '-')}</span>
                            </div>
                        </div>
                    `;
                }

                if (productosContainer) {
                    if (productos.length > 0) {
                        productosContainer.innerHTML = productos.map(p => `
                            <tr>
                                <td>${escapeHtml(p.N_marca)}</td>
                                <td>${escapeHtml(p.N_modelo)}</td>
                                <td>${escapeHtml(p.Cantidad_p)}</td>
                                <td>Bs. ${formatMoney(p.Costo)}</td>
                                <td>Bs. ${formatMoney(p.sup_total)}</td>
                            </tr>
                        `).join('');
                    } else {
                        productosContainer.innerHTML = '<tr><td colspan="5" class="table__empty">No hay productos en esta orden.</td></tr>';
                    }
                }

                if (totalSpan) totalSpan.textContent = formatMoney(detalle.Costo_venta || 0);
                openModal(modalDetalle);
            } else {
                mostrarMensaje(`No se pudo encontrar la orden ${id}`, true);
            }
        } catch (error) {
            console.error('Error cargando detalle:', error);
            mostrarMensaje(error.message || 'No se pudo cargar el detalle de la orden.', true);
        }
    }

    // ✅ CORREGIDO: Cargar productos de la orden para preview de entrega
    async function cargarProductosOrdenParaEntrega(idOrden) {
        const container = document.getElementById('entrega-productos-preview');
        if (!container) return;
        
        try {
            console.log("Cargando productos para entrega:", idOrden);
            const data = await fetchJson(`/api/ordenes_entregas/${idOrden}/productos`, { method: 'GET' });
            const productos = data.productos || [];
            
            if (productos.length > 0) {
                let totalBs = 0;
                productos.forEach(p => {
                    totalBs += Number(p.Costo || 0) * Number(p.Cantidad_p || 0);
                });
                
                container.innerHTML = `
                    <div class="entrega-preview">
                        <div class="entrega-preview-header">
                            Productos a recibir
                        </div>
                        <table class="entrega-preview-table">
                            <thead>
                                <tr>
                                    <th>Producto</th>
                                    <th style="text-align: center;">Cantidad</th>
                                    <th style="text-align: right;">Costo unitario</th>
                                    <th style="text-align: right;">Subtotal</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${productos.map(p => `
                                    <tr>
                                        <td>${escapeHtml(p.N_modelo)}</td>
                                        <td style="text-align: center;">${escapeHtml(p.Cantidad_p)}</td>
                                        <td style="text-align: right;">Bs. ${formatMoney(p.Costo)}</td>
                                        <td style="text-align: right;">Bs. ${formatMoney(p.sup_total)}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td colspan="3" style="text-align: right; font-weight: 600;">Total:</td>
                                    <td style="text-align: right; font-weight: 600;">Bs. ${formatMoney(totalBs)}</td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                `;
            } else {
                container.innerHTML = '<div class="entrega-preview-empty">⚠️ No hay productos en esta orden</div>';
            }
        } catch (error) {
            console.error('Error cargando productos:', error);
            container.innerHTML = '<div class="entrega-preview-empty">❌ Error al cargar productos</div>';
        }
    }

    // Abrir modal
    function openModal(modal) {
        if (modal) modal.removeAttribute('hidden');
        document.body.style.overflow = 'hidden';
    }

    // Cerrar modal
    function closeModal(modal) {
        if (modal) modal.setAttribute('hidden', '');
        document.body.style.overflow = '';
    }

    // Escape HTML
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    // Event Listeners
    if (btnPendientes) btnPendientes.addEventListener('click', () => cambiarVista('pendientes'));
    if (btnEntregadas) btnEntregadas.addEventListener('click', () => cambiarVista('entregadas'));

    // Acciones en tabla de pendientes
    if (tablaPendientes) {
        tablaPendientes.addEventListener('click', async (e) => {
            const btn = e.target.closest('button');
            if (!btn) return;
            const id = btn.dataset.id;
            if (!id) return;

            if (btn.classList.contains('btn-ver')) {
                await verDetalle(id);
            } else if (btn.classList.contains('btn-entrega')) {
                ordenParaEntrega = id;
                if (entregaRecibidoPor) entregaRecibidoPor.value = '';
                if (entregaFecha) entregaFecha.value = new Date().toISOString().slice(0, 10);
                
                await cargarProductosOrdenParaEntrega(id);
                
                if (modalEntrega) openModal(modalEntrega);
            }
        });
    }

    // Acciones en tabla de historial
    if (tablaHistorial) {
        tablaHistorial.addEventListener('click', async (e) => {
            const btn = e.target.closest('.btn-ver');
            if (btn && btn.dataset.id) {
                await verDetalle(btn.dataset.id);
            }
        });
    }

    // ✅ CORREGIDO: Confirmar entrega - usa /api/ordenes_entregas
    if (btnConfirmarEntrega) {
        btnConfirmarEntrega.addEventListener('click', async () => {
            if (!ordenParaEntrega) return;
            
            const recibidoPor = entregaRecibidoPor?.value.trim();
            const fechaEntrega = entregaFecha?.value;
            
            if (!recibidoPor) {
                mostrarMensaje('Debe especificar quién recibe la orden.', true);
                return;
            }
            
            if (!fechaEntrega) {
                mostrarMensaje('Debe especificar la fecha de entrega.', true);
                return;
            }
            
            btnConfirmarEntrega.disabled = true;
            btnConfirmarEntrega.textContent = 'Procesando...';
            
            try {
                console.log("Registrando entrega para orden:", ordenParaEntrega);
                const response = await fetchJson(`/api/ordenes_entregas/${ordenParaEntrega}/registrar`, {
                    method: 'POST',
                    body: JSON.stringify({ recibido_por: recibidoPor, fecha_entrega: fechaEntrega })
                });
                if (response.success) {
                    mostrarMensaje('Entrega registrada exitosamente. Stock actualizado.');
                    closeModal(modalEntrega);
                    ordenParaEntrega = null;
                    cargarPendientes();
                    cargarHistorial();
                } else {
                    mostrarMensaje(response.error || 'Error al registrar la entrega.', true);
                }
            } catch (error) {
                console.error('Error registrando entrega:', error);
                mostrarMensaje(error.message || 'Error al registrar la entrega.', true);
            } finally {
                btnConfirmarEntrega.disabled = false;
                btnConfirmarEntrega.textContent = 'Registrar entrega';
            }
        });
    }

    // Cerrar modales
    document.querySelectorAll('[data-close-modal]').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('[data-modal]');
            if (modal) closeModal(modal);
        });
    });

    // Cargar datos iniciales
    console.log("=== Iniciando ordenes_entregas.js ===");
    cargarPendientes();
});