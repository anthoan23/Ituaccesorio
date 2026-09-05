document.addEventListener('DOMContentLoaded', () => {
    // ==================== ICONOS SVG ====================
    const Iconos = {
        lapiz: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25Zm18-11.5a1 1 0 0 0 0-1.41l-1.34-1.34a1 1 0 0 0-1.41 0l-1.12 1.12 3.75 3.75L21 5.75Z" fill="currentColor"/></svg>`,
        basura: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 7h12l-1 14H7L6 7Zm3-3h6l1 2H8l1-2Z" fill="currentColor"/></svg>`,
        ojo: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" fill="currentColor"/></svg>`,
        registro: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>`
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
    const btnActualizar = document.getElementById('btn-actualizar');
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

    // Función mostrarMensaje (usando FeedbackModal o fallback)
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
            if (vistaPendientes) vistaPendientes.classList.remove('is-hidden');
            if (vistaEntregadas) vistaEntregadas.classList.add('is-hidden');
            if (btnPendientes) btnPendientes.classList.add('is-active');
            if (btnEntregadas) btnEntregadas.classList.remove('is-active');
            cargarPendientes();
        } else {
            if (vistaPendientes) vistaPendientes.classList.add('is-hidden');
            if (vistaEntregadas) vistaEntregadas.classList.remove('is-hidden');
            if (btnPendientes) btnPendientes.classList.remove('is-active');
            if (btnEntregadas) btnEntregadas.classList.add('is-active');
            cargarHistorial();
        }
    }

    // ==================== CARGAR PENDIENTES ====================
    async function cargarPendientes() {
        if (!tablaPendientes) return;
        
        try {
            const data = await fetchJson('/api/ordenes_entregas/pendientes');
            
            if (Array.isArray(data) && data.length > 0) {
                tablaPendientes.innerHTML = data.map(orden => `
                    <tr>
                        <td><span class="chip">${escapeHtml(orden.ID_orden_c)}</span></td>
                        <td><strong>${escapeHtml(orden.N_proveedor || 'Sin proveedor')}</strong></td>
                        <td>${escapeHtml(formatDate(orden.Fecha_o))}</td>
                        <td><span class="status-badge status-pendiente">${escapeHtml(orden.Estado || 'Pendiente')}</span></td>
                        <td class="order-total">Bs. ${escapeHtml(formatMoney(orden.Costo_venta || 0))}</td>
                        <td class="table__actions">
                            <div class="row-actions">
                                <button class="icon-action icon-action--view" data-action="ver" data-id="${escapeHtml(orden.ID_orden_c)}" title="Ver detalles">${Iconos.ojo}</button>
                                <button class="icon-action icon-action--edit" data-action="editar" data-id="${escapeHtml(orden.ID_orden_c)}" title="Editar orden">${Iconos.lapiz}</button>
                                <button class="btn-entrega" data-action="registrar-entrega" data-id="${escapeHtml(orden.ID_orden_c)}" title="Registrar entrega" aria-label="Registrar entrega">${Iconos.registro}</button>
                            </div>
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

    // ==================== CARGAR HISTORIAL ====================
    async function cargarHistorial() {
        if (!tablaHistorial) return;
        
        try {
            const data = await fetchJson('/api/ordenes_entregas/historial');
            
            if (Array.isArray(data) && data.length > 0) {
                tablaHistorial.innerHTML = data.map(entrega => `
                    <tr>
                        <td><span class="chip">${escapeHtml(entrega.ID_entrega)}</span></td>
                        <td>${escapeHtml(entrega.ID_orden_c)}</td>
                        <td>${escapeHtml(entrega.Proveedor || 'Sin proveedor')}</td>
                        <td>${escapeHtml(formatDate(entrega.Fecha_entrega))}</td>
                        <td>${escapeHtml(entrega.Recibido_por || '-')}</td>
                        <td class="table__actions">
                            <div class="row-actions">
                                <button class="icon-action icon-action--view" data-action="ver-historial" data-id="${escapeHtml(entrega.ID_orden_c)}" title="Ver detalles">${Iconos.ojo}</button>
                                <button class="icon-action icon-action--edit" data-action="editar-entrega" data-id="${escapeHtml(entrega.ID_entrega)}" title="Modificar entrega">${Iconos.lapiz}</button>
                                <button class="icon-action icon-action--danger" data-action="eliminar-entrega" data-id="${escapeHtml(entrega.ID_entrega)}" title="Eliminar entrega">${Iconos.basura}</button>
                            </div>
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
                        <div class="detail-item">
                            <span class="device-detail__label">ID Orden</span>
                            <span class="device-detail__value">#${escapeHtml(detalle.ID_orden_c)}</span>
                        </div>
                        <div class="detail-item">
                            <span class="device-detail__label">Proveedor</span>
                            <span class="device-detail__value"><strong>${escapeHtml(detalle.nombre)}</strong></span>
                        </div>
                        <div class="detail-item">
                            <span class="device-detail__label">Fecha</span>
                            <span class="device-detail__value">${escapeHtml(formatDate(detalle.Fecha_o))}</span>
                        </div>
                        <div class="detail-item">
                            <span class="device-detail__label">Estado</span>
                            <span class="device-detail__value"><span class="status-badge ${detalle.Estado === 'Pendiente' ? 'status-pendiente' : 'status-completada'}">${escapeHtml(detalle.Estado)}</span></span>
                        </div>
                        <div class="detail-item">
                            <span class="device-detail__label">Realizado por</span>
                            <span class="device-detail__value">${escapeHtml(detalle.Realizado_por || '-')}</span>
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
                if (window.UiModal && typeof window.UiModal.openById === 'function') {
                    window.UiModal.openById('modal-detalle-orden');
                }
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
                                    <th class="cell-center">Cantidad</th>
                                    <th class="cell-right">Costo unitario</th>
                                    <th class="cell-right">Subtotal</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${productos.map(p => `
                                    <tr>
                                        <td>${escapeHtml(p.N_modelo)}</td>
                                        <td class="cell-center">${escapeHtml(p.Cantidad_p)}</td>
                                        <td class="cell-right">Bs. ${formatMoney(p.Costo)}</td>
                                        <td class="cell-right">Bs. ${formatMoney(p.sup_total)}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td colspan="3" class="cell-right-bold">Total:</td>
                                    <td class="cell-right-bold">Bs. ${formatMoney(totalBs)}</td>
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
                
                if (window.UiModal && typeof window.UiModal.openById === 'function') {
                    window.UiModal.openById('modal-editar-entrega');
                    setTimeout(() => {
                        if (window.FieldValidator) window.FieldValidator.init();
                    }, 100);
                }
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
        if (window.UiModal && typeof window.UiModal.openById === 'function') {
            window.UiModal.openById('modal-confirmar-eliminar-entrega');
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
                if (window.UiModal && typeof window.UiModal.closeById === 'function') {
                    window.UiModal.closeById('modal-confirmar-eliminar-entrega');
                }
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

    // ==================== ABRIR EDITAR ORDEN ====================
    function abrirEditarOrden(idOrden) {
        mostrarMensaje('Para editar la orden ve a la sección de Órdenes de Compra', false);
    }

    // ==================== EVENT LISTENERS ====================
    
    // Switcher de vistas
    if (btnPendientes) btnPendientes.addEventListener('click', () => cambiarVista('pendientes'));
    if (btnEntregadas) btnEntregadas.addEventListener('click', () => cambiarVista('entregadas'));

    // Botón actualizar
    if (btnActualizar) {
        btnActualizar.addEventListener('click', () => {
            const vistaActiva = btnPendientes?.classList.contains('is-active') ? 'pendientes' : 'entregadas';
            if (vistaActiva === 'pendientes') cargarPendientes();
            else cargarHistorial();
            mostrarMensaje('Datos actualizados correctamente');
        });
    }

    // ==================== ACCIONES EN TABLA DE PENDIENTES ====================
    if (tablaPendientes) {
        tablaPendientes.addEventListener('click', async (e) => {
            const btn = e.target.closest('button');
            if (!btn) return;
            const id = btn.dataset.id;
            if (!id) return;

            const action = btn.dataset.action;

            if (action === 'ver') {
                await verDetalle(id);
            } else if (action === 'editar') {
                abrirEditarOrden(id);
            } else if (action === 'registrar-entrega') {
                ordenParaEntrega = id;
                document.getElementById('entrega-orden-id').value = id;
                if (entregaRecibidoPor) entregaRecibidoPor.value = '';
                if (entregaFecha) entregaFecha.value = new Date().toISOString().slice(0, 10);
                
                await cargarProductosOrdenParaEntrega(id);
                
                if (window.UiModal && typeof window.UiModal.openById === 'function') {
                    window.UiModal.openById('modal-registrar-entrega');
                    setTimeout(() => {
                        if (window.FieldValidator) window.FieldValidator.init();
                    }, 100);
                }
            }
        });
    }

    // ==================== ACCIONES EN TABLA DE HISTORIAL ====================
    if (tablaHistorial) {
        tablaHistorial.addEventListener('click', async (e) => {
            const btn = e.target.closest('button');
            if (!btn) return;
            
            const action = btn.dataset.action;
            const id = btn.dataset.id;
            if (!id) return;

            if (action === 'ver-historial') {
                await verDetalle(id);
            } else if (action === 'editar-entrega') {
                await abrirEditarEntrega(id);
            } else if (action === 'eliminar-entrega') {
                abrirEliminarEntrega(id);
            }
        });
    }

    // Confirmar entrega
    if (btnConfirmarEntrega) {
        btnConfirmarEntrega.addEventListener('click', async (e) => {
            e.preventDefault();
            if (!ordenParaEntrega) return;
            
            const recibidoPor = entregaRecibidoPor?.value.trim();
            const fechaEntrega = entregaFecha?.value;
            
            // Validar con FieldValidator
            const form = document.getElementById('form-registrar-entrega');
            if (window.FieldValidator && typeof window.FieldValidator.validateForm === 'function') {
                const isValid = window.FieldValidator.validateForm(form);
                if (!isValid) {
                    mostrarMensaje('Por favor, corrige los errores en el formulario.', true);
                    return;
                }
            }
            
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
                    if (window.UiModal && typeof window.UiModal.closeById === 'function') {
                        window.UiModal.closeById('modal-registrar-entrega');
                    }
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
        btnGuardarEditar.addEventListener('click', async (e) => {
            e.preventDefault();
            if (!entregaParaEditar) return;
            
            const recibidoPor = document.getElementById('editar-recibido-por')?.value.trim();
            const fechaEntrega = document.getElementById('editar-fecha-entrega')?.value;
            
            // Validar con FieldValidator
            const form = document.getElementById('form-editar-entrega');
            if (window.FieldValidator && typeof window.FieldValidator.validateForm === 'function') {
                const isValid = window.FieldValidator.validateForm(form);
                if (!isValid) {
                    mostrarMensaje('Por favor, corrige los errores en el formulario.', true);
                    return;
                }
            }
            
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
                    if (window.UiModal && typeof window.UiModal.closeById === 'function') {
                        window.UiModal.closeById('modal-editar-entrega');
                    }
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

    // Inicializar FieldValidator
    if (window.FieldValidator) {
        setTimeout(() => window.FieldValidator.init(), 100);
    }

    // Cargar datos iniciales
    cargarPendientes();
});