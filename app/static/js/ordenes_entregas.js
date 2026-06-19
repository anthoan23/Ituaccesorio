document.addEventListener('DOMContentLoaded', () => {
    // ==================== ICONOS SVG ====================
    const Iconos = {
        lapiz: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>`,
        basura: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>`,
        ojo: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`
    };

    // Elementos DOM
    const vistaPendientes = document.getElementById('vista-pendientes');
    const vistaEntregadas = document.getElementById('vista-entregadas');
    const btnPendientes = document.getElementById('btn-pendientes');
    const btnEntregadas = document.getElementById('btn-entregadas');
    const tablaPendientes = document.getElementById('tabla-ordenes-entregas-pendientes');
    const tablaHistorial = document.getElementById('tabla-ordenes-entregas-historial');
    const modalDetalle = document.getElementById('modal-detalle-orden');
    const modalEntrega = document.getElementById('modal-registrar-entrega');
    const modalEditar = document.getElementById('modal-editar-entrega');
    const modalEliminar = document.getElementById('modal-confirmar-eliminar-entrega');
    const btnConfirmarEntrega = document.getElementById('btn-confirmar-entrega');
    const btnGuardarEditar = document.getElementById('btn-guardar-editar-entrega');
    const btnConfirmarEliminar = document.getElementById('btn-confirmar-eliminar-entrega');
    const entregaRecibidoPor = document.getElementById('entrega-recibido-por');
    const entregaFecha = document.getElementById('entrega-fecha');

    // Estado
    let ordenParaEntrega = null;
    let entregaParaEditar = null;
    let entregaParaEliminar = null;

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

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
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

    // ==================== CARGAR PENDIENTES CON ICONOS ====================
    async function cargarPendientes() {
        if (!tablaPendientes) return;
        
        try {
            const data = await fetchJson('/api/ordenes_entregas/pendientes');
            
            if (Array.isArray(data) && data.length > 0) {
                tablaPendientes.innerHTML = data.map(orden => `
                    <tr>
                        <td>${escapeHtml(orden.ID_orden_c)}</td>
                        <td><strong>${escapeHtml(orden.N_proveedor || 'Sin proveedor')}</strong></td>
                        <td>${escapeHtml(formatDate(orden.Fecha_o))}</td>
                        <td><span class="status-badge status-pendiente">${escapeHtml(orden.Estado || 'Pendiente')}</span></td>
                        <td>Bs. ${escapeHtml(formatMoney(orden.Costo_venta || 0))}</td>
                        <td class="table__actions">
                            <button class="btn btn--small btn-ver" data-id="${escapeHtml(orden.ID_orden_c)}" title="Ver detalles">${Iconos.ojo}</button>
                            <button class="btn btn--small btn-editar" data-id="${escapeHtml(orden.ID_orden_c)}" title="Editar orden">${Iconos.lapiz}</button>
                            <button class="btn btn--small btn-entrega" data-id="${escapeHtml(orden.ID_orden_c)}" title="Registrar entrega">Registrar</button>
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

    // ==================== CARGAR HISTORIAL CON ICONOS ====================
    async function cargarHistorial() {
        if (!tablaHistorial) return;
        
        try {
            const data = await fetchJson('/api/ordenes_entregas/historial');
            
            if (Array.isArray(data) && data.length > 0) {
                tablaHistorial.innerHTML = data.map(entrega => `
                    <tr>
                        <td>${escapeHtml(entrega.ID_entrega)}</td>
                        <td>${escapeHtml(entrega.ID_orden_c)}</td>
                        <td>${escapeHtml(entrega.Proveedor || 'Sin proveedor')}</td>
                        <td>${escapeHtml(formatDate(entrega.Fecha_entrega))}</td>
                        <td>${escapeHtml(entrega.Recibido_por || '-')}</td>
                        <td class="table__actions">
                            <button class="btn btn--small btn-ver" data-id="${escapeHtml(entrega.ID_orden_c)}" title="Ver detalles">${Iconos.ojo}</button>
                            <button class="btn btn--small btn-editar-entrega" data-id="${escapeHtml(entrega.ID_entrega)}" title="Modificar entrega">${Iconos.lapiz}</button>
                            <button class="btn btn--small btn-eliminar-entrega" data-id="${escapeHtml(entrega.ID_entrega)}" title="Eliminar entrega">${Iconos.basura}</button>
                        </td>
                    </tr>
                `).join('');
            } else {
                tablaHistorial.innerHTML = '<tr><td colspan="6" class="table__empty">No hay entregas registradas.</td></tr>';
            }
        } catch (error) {
            console.error('Error cargando historial:', error);
            tablaHistorial.innerHTML = `<tr><td colspan="6" class="table__empty">Error: ${escapeHtml(error.message)}</td></tr>`;
        }
    }

    // Ver detalle de orden
    async function verDetalle(id) {
        try {
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

    // Cargar productos de la orden para preview de entrega
    async function cargarProductosOrdenParaEntrega(idOrden) {
        const container = document.getElementById('entrega-productos-preview');
        if (!container) return;
        
        try {
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

    // ==================== EDITAR ENTREGA ====================
    async function abrirEditarEntrega(idEntrega) {
        entregaParaEditar = idEntrega;
        
        try {
            const data = await fetchJson(`/api/ordenes_entregas/${idEntrega}`, { method: 'GET' });
            
            if (data.success && data.entrega) {
                const e = data.entrega;
                document.getElementById('editar-id-entrega').value = e.ID_entrega;
                document.getElementById('editar-id-orden-entrega').value = e.ID_orden_c;
                document.getElementById('editar-recibido-por').value = e.Recibido_por || '';
                
                if (e.Fecha_entrega) {
                    const dateParts = e.Fecha_entrega.split('/');
                    if (dateParts.length === 3) {
                        document.getElementById('editar-fecha-entrega').value = `${dateParts[2]}-${dateParts[1].padStart(2, '0')}-${dateParts[0].padStart(2, '0')}`;
                    }
                }
                
                openModal(modalEditar);
            } else {
                mostrarMensaje('No se pudo cargar la entrega para editar.', true);
            }
        } catch (error) {
            console.error('Error cargando entrega para editar:', error);
            mostrarMensaje(error.message || 'Error al cargar la entrega.', true);
        }
    }

    // ==================== ELIMINAR ENTREGA ====================
    function abrirEliminarEntrega(idEntrega) {
        entregaParaEliminar = idEntrega;
        const textoEl = document.getElementById('texto-confirmar-eliminar-entrega');
        if (textoEl) {
            textoEl.textContent = `¿Seguro que deseas eliminar la entrega "${idEntrega}"? Se revertirá el stock de los productos. Esta acción no se puede deshacer.`;
        }
        if (modalEliminar) {
            openModal(modalEliminar);
        }
    }

    async function confirmarEliminarEntrega() {
        if (!entregaParaEliminar) return;
        
        try {
            const response = await fetchJson(`/api/ordenes_entregas/${entregaParaEliminar}/eliminar`, {
                method: 'DELETE'
            });
            if (response.success) {
                mostrarMensaje('Entrega eliminada exitosamente. Stock revertido.');
                if (modalEliminar) closeModal(modalEliminar);
                entregaParaEliminar = null;
                cargarHistorial();
                cargarPendientes();
            } else {
                mostrarMensaje(response.error || 'Error al eliminar la entrega.', true);
            }
        } catch (error) {
            console.error('Error eliminando entrega:', error);
            mostrarMensaje(error.message || 'Error al eliminar la entrega.', true);
        }
    }

    // ==================== ABRIR EDITAR ORDEN (desde pendientes) ====================
    async function abrirEditarOrden(idOrden) {
        // Redirigir a la página de órdenes de compra con el modal de edición
        // O abrir un modal similar al de órdenes de compra
        mostrarMensaje('Para editar la orden ve a la sección de Órdenes de Compra', false);
        // Alternativa: redirigir
        // window.location.href = `/ordenes_compra?editar=${idOrden}`;
    }

    // Abrir modal
    function openModal(modal) {
        if (modal) modal.removeAttribute('hidden');
        document.body.style.overflow = 'hidden';
    }

    function closeModal(modal) {
        if (modal) modal.setAttribute('hidden', '');
        document.body.style.overflow = '';
    }

    // Event Listeners
    if (btnPendientes) btnPendientes.addEventListener('click', () => cambiarVista('pendientes'));
    if (btnEntregadas) btnEntregadas.addEventListener('click', () => cambiarVista('entregadas'));

    // ==================== ACCIONES EN TABLA DE PENDIENTES ====================
    if (tablaPendientes) {
        tablaPendientes.addEventListener('click', async (e) => {
            const btn = e.target.closest('button');
            if (!btn) return;
            const id = btn.dataset.id;
            if (!id) return;

            if (btn.classList.contains('btn-ver')) {
                await verDetalle(id);
            } else if (btn.classList.contains('btn-editar')) {
                // Editar orden - redirigir a órdenes de compra
                mostrarMensaje('Para editar la orden ve a la sección de Órdenes de Compra', false);
            } else if (btn.classList.contains('btn-entrega')) {
                ordenParaEntrega = id;
                if (entregaRecibidoPor) entregaRecibidoPor.value = '';
                if (entregaFecha) entregaFecha.value = new Date().toISOString().slice(0, 10);
                
                await cargarProductosOrdenParaEntrega(id);
                
                if (modalEntrega) openModal(modalEntrega);
            }
        });
    }

    // ==================== ACCIONES EN TABLA DE HISTORIAL ====================
    if (tablaHistorial) {
        tablaHistorial.addEventListener('click', async (e) => {
            const btn = e.target.closest('button');
            if (!btn) return;
            
            if (btn.classList.contains('btn-ver')) {
                const id = btn.dataset.id;
                if (id) await verDetalle(id);
            } else if (btn.classList.contains('btn-editar-entrega')) {
                const id = btn.dataset.id;
                if (id) await abrirEditarEntrega(id);
            } else if (btn.classList.contains('btn-eliminar-entrega')) {
                const id = btn.dataset.id;
                if (id) abrirEliminarEntrega(id);
            }
        });
    }

    // Confirmar entrega
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

    // Guardar edición de entrega
    if (btnGuardarEditar) {
        btnGuardarEditar.addEventListener('click', async () => {
            if (!entregaParaEditar) return;
            
            const recibidoPor = document.getElementById('editar-recibido-por')?.value.trim();
            const fechaEntrega = document.getElementById('editar-fecha-entrega')?.value;
            
            if (!recibidoPor) {
                mostrarMensaje('Debe especificar quién recibió la orden.', true);
                return;
            }
            
            if (!fechaEntrega) {
                mostrarMensaje('Debe especificar la fecha de entrega.', true);
                return;
            }
            
            btnGuardarEditar.disabled = true;
            btnGuardarEditar.textContent = 'Guardando...';
            
            try {
                const response = await fetchJson(`/api/ordenes_entregas/${entregaParaEditar}/editar`, {
                    method: 'PUT',
                    body: JSON.stringify({ recibido_por: recibidoPor, fecha_entrega: fechaEntrega })
                });
                if (response.success) {
                    mostrarMensaje('Entrega actualizada exitosamente.');
                    closeModal(modalEditar);
                    entregaParaEditar = null;
                    cargarHistorial();
                } else {
                    mostrarMensaje(response.error || 'Error al actualizar la entrega.', true);
                }
            } catch (error) {
                console.error('Error actualizando entrega:', error);
                mostrarMensaje(error.message || 'Error al actualizar la entrega.', true);
            } finally {
                btnGuardarEditar.disabled = false;
                btnGuardarEditar.textContent = 'Actualizar entrega';
            }
        });
    }

    // Confirmar eliminación de entrega
    if (btnConfirmarEliminar) {
        btnConfirmarEliminar.addEventListener('click', async () => {
            await confirmarEliminarEntrega();
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
    cargarPendientes();
});