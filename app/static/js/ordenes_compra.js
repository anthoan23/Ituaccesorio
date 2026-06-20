document.addEventListener('DOMContentLoaded', () => {
    // Elementos DOM - SOLO PARA ÓRDENES DE COMPRA
    const tablaPendientes = document.getElementById('tabla-ordenes-pendientes');
    const btnRegistrar = document.getElementById('btn-registrar-entrada');
    const modalRegistro = document.getElementById('modal-registrar-entrada');
    const modalProveedores = document.getElementById('modal-seleccionar-proveedor');
    const modalProductos = document.getElementById('modal-seleccionar-productos');
    const modalDetalle = document.getElementById('modal-detalle-orden');
    const modalEliminar = document.getElementById('modal-confirmar-eliminar-orden');
    const modalMensaje = document.getElementById('modal-mensaje');
    const modalEditar = document.getElementById('modal-editar-orden');
    const btnBuscarProveedor = document.getElementById('btn-desplegar-proveedores');
    const btnBuscarProductos = document.getElementById('btn-desplegar-productos');
    const listaProveedores = document.getElementById('lista-proveedores');
    const listaProductos = document.getElementById('lista-productos');
    const tablaSeleccionados = document.getElementById('tabla-productos-seleccionados');
    const tablaSeleccionadosEditar = document.getElementById('tabla-productos-seleccionados-editar');
    const costoTotalSpan = document.getElementById('entrada-costo-total');
    const costoTotalEditarSpan = document.getElementById('entrada-costo-total-editar');
    const btnGuardar = document.getElementById('btn-guardar-entrada');
    const btnGuardarEditar = document.getElementById('btn-guardar-editar');
    const formRegistro = document.getElementById('form-registrar-entrada');
    const formEditar = document.getElementById('form-editar-orden');
    const entradaIdProveedor = document.getElementById('entrada-id-proveedor');
    const entradaNombreProveedor = document.getElementById('entrada-nombre-proveedor');
    const btnConfirmarEliminar = document.getElementById('btn-confirmar-eliminar-orden');
    const mensajeTexto = document.getElementById('mensaje-texto');
    const btnCerrarMensaje = document.getElementById('btn-cerrar-mensaje');

    // ==================== ICONOS SVG CON ESTILOS ====================
    const Iconos = {
        lapiz: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>`,
        basura: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>`,
        ojo: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`
    };

    // Estado
    let proveedores = [];
    let empleados = [];
    let productosDisponibles = [];
    let productosSeleccionados = [];
    let productosSeleccionadosEditar = [];
    let proveedorSeleccionado = null;
    let proveedorSeleccionadoEditar = null;
    let ordenParaEliminar = null;
    let ordenParaEditar = null;

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

    // función mostrarMensaje
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

    // Cargar órdenes pendientes
    async function cargarOrdenesPendientes() {
        if (!tablaPendientes) return;
        
        try {
            const data = await fetchJson('/api/ordenes_compra');
            
            if (Array.isArray(data) && data.length > 0) {
                tablaPendientes.innerHTML = data.map(orden => {
                    const nombreProveedor = orden.N_proveedor || orden.nombre || 'Sin proveedor';
                    const fecha = orden.Fecha_o ? formatDate(orden.Fecha_o) : 'Fecha no disponible';
                    const estado = orden.Estado || 'Pendiente';
                    const estadoClass = estado === 'Pendiente' ? 'status-pendiente' : 'status-completada';
                    
                    return `
                        <tr data-id="${escapeHtml(orden.ID_orden_c)}">
                            <td>${escapeHtml(orden.ID_orden_c)}</td>
                            <td><strong>${escapeHtml(nombreProveedor)}</strong></td>
                            <td>${escapeHtml(fecha)}</td>
                            <td><span class="status-badge ${estadoClass}">${escapeHtml(estado)}</span></td>
                            <td>Bs. ${escapeHtml(formatMoney(orden.Costo_venta || 0))}</td>
                            <td class="table__actions">
                                <button class="btn btn--small btn-ver" data-id="${escapeHtml(orden.ID_orden_c)}" title="Ver detalles">${Iconos.ojo}</button>
                                <button class="btn btn--small btn-editar" data-id="${escapeHtml(orden.ID_orden_c)}" title="Modificar">${Iconos.lapiz}</button>
                                <button class="btn btn--small btn-eliminar" data-id="${escapeHtml(orden.ID_orden_c)}" title="Eliminar">${Iconos.basura}</button>
                            </td>
                        </tr>
                    `;
                }).join('');
            } else {
                tablaPendientes.innerHTML = '<tr><td colspan="6" class="table__empty">No hay órdenes de compra pendientes.</td></tr>';
            }
        } catch (error) {
            console.error('Error cargando órdenes:', error);
            tablaPendientes.innerHTML = '<tr><td colspan="6" class="table__empty">Error al cargar las órdenes.</td></tr>';
        }
    }

    // ==================== CARGAR EMPLEADOS ====================
    
    async function cargarEmpleados(selectId = 'entrada-id-empleado') {
        const selectEmpleado = document.getElementById(selectId);
        if (!selectEmpleado) return;
        
        try {
            const data = await fetchJson('/api/empleados');
            empleados = data || [];
            
            if (empleados.length > 0) {
                selectEmpleado.innerHTML = '<option value="">Seleccione un empleado</option>' +
                    empleados.map(e => {
                        const textoMostrar = `${e.nombre} ${e.apellido} (${e.cedula})`;
                        return `<option value="${e.cedula}">${escapeHtml(textoMostrar)}</option>`;
                    }).join('');
            } else {
                selectEmpleado.innerHTML = '<option value="">No hay empleados registrados</option>';
            }
        } catch (error) {
            console.error('Error cargando empleados:', error);
            selectEmpleado.innerHTML = '<option value="">Error al cargar empleados</option>';
        }
    }

    // Cargar proveedores
    async function cargarProveedores() {
        if (!listaProveedores) return;
        
        try {
            const data = await fetchJson('/api/proveedores');
            proveedores = data.proveedores || [];
            
            if (proveedores.length > 0) {
                listaProveedores.innerHTML = proveedores.map(p => `
                    <tr data-proveedor-id="${escapeHtml(p.id)}" class="row-selectable">
                        <td>${escapeHtml(p.id)}</td>
                        <td>${escapeHtml(p.nombre)}</td>
                        <td>${escapeHtml(p.celular || '-')}</td>
                        <td>${escapeHtml(p.correo || '-')}</td>
                    </tr>
                `).join('');
            } else {
                listaProveedores.innerHTML = '<tr><td colspan="4" class="table__empty">No hay proveedores registrados.</td></tr>';
            }
        } catch (error) {
            console.error('Error cargando proveedores:', error);
            listaProveedores.innerHTML = '<tr><td colspan="4" class="table__empty">Error al cargar proveedores.</td></tr>';
        }
    }

    // Cargar productos de un proveedor
    async function cargarProductosProveedor(idProveedor) {
        if (!listaProductos) return;
        
        try {
            const data = await fetchJson(`/api/productos_proveedor/${idProveedor}`, { method: 'POST' });
            productosDisponibles = data.productos || [];
            
            if (productosDisponibles.length > 0) {
                listaProductos.innerHTML = productosDisponibles.map(p => `
                    <tr data-producto-id="${escapeHtml(p.ID_modelo)}" class="row-selectable">
                        <td>${escapeHtml(p.N_clase || '-')}</td>
                        <td>${escapeHtml(p.N_marca || '-')}</td>
                        <td>${escapeHtml(p.N_modelo)}</td>
                        <td>Bs. ${escapeHtml(formatMoney(p.Costo))}</td>
                    </tr>
                `).join('');
            } else {
                listaProductos.innerHTML = '<tr><td colspan="4" class="table__empty">Este proveedor no tiene productos registrados.</td></tr>';
            }
        } catch (error) {
            console.error('Error cargando productos:', error);
            listaProductos.innerHTML = '<tr><td colspan="4" class="table__empty">Error al cargar productos.</td></tr>';
        }
    }

    // Renderizar productos seleccionados (crear)
    function renderizarSeleccionados() {
        if (!tablaSeleccionados) return;
        
        if (productosSeleccionados.length === 0) {
            tablaSeleccionados.innerHTML = '<tr><td colspan="5" class="table__empty">Aún no hay productos seleccionados.</td></tr>';
            actualizarTotal();
            return;
        }

        tablaSeleccionados.innerHTML = productosSeleccionados.map((p, idx) => `
            <tr>
                <td>${escapeHtml(p.nombre)}</td>
                <td>${escapeHtml(p.proveedor)}</td>
                <td>
                    <div class="cantidad-control">
                        <button class="btn-cantidad" data-index="${idx}" data-op="menos">-</button>
                        <span class="cantidad-valor">${p.cantidad}</span>
                        <button class="btn-cantidad" data-index="${idx}" data-op="mas">+</button>
                    </div>
                </td>
                <td>Bs. ${formatMoney(p.costo)}</td>
                <td class="table__actions">
                    <button class="btn btn--small btn-eliminar" data-index="${idx}">Eliminar</button>
                </td>
            </tr>
        `).join('');
        actualizarTotal();
    }

    // Renderizar productos seleccionados (editar)
    function renderizarSeleccionadosEditar() {
        if (!tablaSeleccionadosEditar) return;
        
        console.log('📋 Productos seleccionados editar:', productosSeleccionadosEditar);
        
        if (!productosSeleccionadosEditar || productosSeleccionadosEditar.length === 0) {
            tablaSeleccionadosEditar.innerHTML = '<tr><td colspan="5" class="table__empty">Aún no hay productos seleccionados.</td></tr>';
            actualizarTotalEditar();
            return;
        }

        tablaSeleccionadosEditar.innerHTML = productosSeleccionadosEditar.map((p, idx) => `
            <tr>
                <td>${escapeHtml(p.nombre || 'Sin nombre')}</td>
                <td>${escapeHtml(p.proveedor || 'Sin proveedor')}</td>
                <td>
                    <div class="cantidad-control">
                        <button class="btn-cantidad" data-index="${idx}" data-op="menos">-</button>
                        <span class="cantidad-valor">${p.cantidad || 0}</span>
                        <button class="btn-cantidad" data-index="${idx}" data-op="mas">+</button>
                    </div>
                </td>
                <td>Bs. ${formatMoney(p.costo || 0)}</td>
                <td class="table__actions">
                    <button class="btn btn--small btn-eliminar-editar" data-index="${idx}">Eliminar</button>
                </td>
            </tr>
        `).join('');
        actualizarTotalEditar();
    }

    // Actualizar costo total (crear)
    function actualizarTotal() {
        const total = productosSeleccionados.reduce((sum, p) => sum + (p.costo * p.cantidad), 0);
        if (costoTotalSpan) costoTotalSpan.textContent = formatMoney(total);
        if (btnGuardar) btnGuardar.disabled = productosSeleccionados.length === 0 || !proveedorSeleccionado;
    }

    // Actualizar costo total (editar)
    function actualizarTotalEditar() {
        const total = productosSeleccionadosEditar.reduce((sum, p) => sum + (p.costo * p.cantidad), 0);
        if (costoTotalEditarSpan) costoTotalEditarSpan.textContent = formatMoney(total);
        if (btnGuardarEditar) btnGuardarEditar.disabled = productosSeleccionadosEditar.length === 0 || !proveedorSeleccionadoEditar;
    }

    // Limpiar formulario (crear)
    function limpiarFormulario() {
        productosSeleccionados = [];
        proveedorSeleccionado = null;
        if (entradaIdProveedor) entradaIdProveedor.value = '';
        if (entradaNombreProveedor) entradaNombreProveedor.value = '';
        if (btnBuscarProductos) btnBuscarProductos.disabled = true;
        renderizarSeleccionados();
    }

    // Limpiar formulario (editar) - NO RESETEA productosSeleccionadosEditar
    function limpiarFormularioEditar() {
        proveedorSeleccionadoEditar = null;
        document.getElementById('editar-id-proveedor').value = '';
        document.getElementById('editar-nombre-proveedor').value = '';
        document.getElementById('editar-id-orden').value = '';
        document.getElementById('editar-id-empleado').value = '';
        if (document.getElementById('btn-desplegar-productos-editar')) {
            document.getElementById('btn-desplegar-productos-editar').disabled = true;
        }
        renderizarSeleccionadosEditar();
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

    // ==================== EDITAR ORDEN ====================
    
    async function abrirEditarOrden(id) {
        ordenParaEditar = id;
        
        // Limpiar solo campos, NO productos seleccionados
        document.getElementById('editar-id-orden').value = '';
        document.getElementById('editar-id-proveedor').value = '';
        document.getElementById('editar-nombre-proveedor').value = '';
        document.getElementById('editar-id-empleado').value = '';
        if (document.getElementById('btn-desplegar-productos-editar')) {
            document.getElementById('btn-desplegar-productos-editar').disabled = true;
        }
        
        // Cargar empleados en el select de editar
        await cargarEmpleados('editar-id-empleado');
        
        try {
            // Cargar datos de la orden
            const data = await fetchJson(`/api/detalles_orden/${id}`, { method: 'GET' });
            const detalle = data.datos_orden;
            const productos = data.productos_orden || [];
            
            console.log('📋 Productos de la orden:', productos);
            
            if (detalle) {
                document.getElementById('editar-id-orden').value = detalle.ID_orden_c;
                
                // Seleccionar el empleado correcto
                if (detalle.ID_empleado) {
                    const selectEmpleado = document.getElementById('editar-id-empleado');
                    setTimeout(() => {
                        selectEmpleado.value = String(detalle.ID_empleado);
                    }, 300);
                }
                
                // Cargar proveedor
                const proveedorData = await fetchJson(`/api/proveedores/${detalle.ID_proveedor}`);
                if (proveedorData.success && proveedorData.proveedor) {
                    const p = proveedorData.proveedor;
                    proveedorSeleccionadoEditar = {
                        id: p.id,
                        nombre: p.nombre
                    };
                    document.getElementById('editar-id-proveedor').value = p.id;
                    document.getElementById('editar-nombre-proveedor').value = p.nombre;
                    document.getElementById('btn-desplegar-productos-editar').disabled = false;
                    
                    // Cargar productos del proveedor
                    await cargarProductosProveedorEditar(p.id);
                }
                
                // Cargar productos de la orden con los IDs correctos
                productosSeleccionadosEditar = productos.map(p => ({
                    id_modelo: String(p.ID_producto || p.ID_modelo || p.id_modelo || ''),
                    nombre: p.N_modelo || p.modelo || 'Producto',
                    proveedor: detalle.nombre || '',
                    costo: Number(p.Costo || p.costo || 0),
                    cantidad: Number(p.Cantidad_p || p.cantidad || 1)
                }));
                
                console.log('📋 Productos seleccionados para editar:', productosSeleccionadosEditar);
                
                // Filtrar productos con id_modelo vacío
                productosSeleccionadosEditar = productosSeleccionadosEditar.filter(p => p.id_modelo && p.id_modelo !== '');
                
                renderizarSeleccionadosEditar();
                openModal(modalEditar);
            }
        } catch (error) {
            console.error('Error cargando orden para editar:', error);
            mostrarMensaje('Error al cargar la orden para editar.', true);
        }
    }

    // Cargar productos de un proveedor (editar)
    async function cargarProductosProveedorEditar(idProveedor) {
        const lista = document.getElementById('lista-productos-editar');
        if (!lista) return;
        
        try {
            const data = await fetchJson(`/api/productos_proveedor/${idProveedor}`, { method: 'POST' });
            const productos = data.productos || [];
            productosDisponibles = productos;
            
            console.log('📦 Productos disponibles para editar:', productos);
            
            if (productos.length > 0) {
                lista.innerHTML = productos.map(p => `
                    <tr data-producto-id="${escapeHtml(p.ID_modelo)}" class="row-selectable">
                        <td>${escapeHtml(p.N_clase || '-')}</td>
                        <td>${escapeHtml(p.N_marca || '-')}</td>
                        <td>${escapeHtml(p.N_modelo)}</td>
                        <td>Bs. ${escapeHtml(formatMoney(p.Costo))}</td>
                    </tr>
                `).join('');
            } else {
                lista.innerHTML = '<tr><td colspan="4" class="table__empty">Este proveedor no tiene productos registrados.</td></tr>';
            }
        } catch (error) {
            console.error('Error cargando productos:', error);
            lista.innerHTML = '<tr><td colspan="4" class="table__empty">Error al cargar productos.</td></tr>';
        }
    }

    // ==================== ELIMINAR ORDEN ====================
    
    function abrirEliminarOrden(id) {
        ordenParaEliminar = id;
        const textoEl = document.getElementById('texto-confirmar-eliminar-orden');
        if (textoEl) {
            textoEl.textContent = `¿Seguro que deseas eliminar (anular) la orden "${id}"? Esta acción no se puede deshacer.`;
        }
        if (modalEliminar) {
            openModal(modalEliminar);
        }
    }

    async function confirmarEliminarOrden() {
        if (!ordenParaEliminar) return;
        
        try {
            const response = await fetchJson('/api/ordenes_compra/anular', {
                method: 'POST',
                body: JSON.stringify({ ID_orden_c: ordenParaEliminar })
            });
            if (response.success) {
                mostrarMensaje('Orden eliminada exitosamente.');
                if (modalEliminar) closeModal(modalEliminar);
                ordenParaEliminar = null;
                cargarOrdenesPendientes();
            } else {
                mostrarMensaje(response.error || 'Error al eliminar la orden.', true);
            }
        } catch (error) {
            console.error('Error eliminando orden:', error);
            mostrarMensaje(error.message || 'Error al eliminar la orden.', true);
        }
    }

    // Event Listeners
    if (btnRegistrar) {
        btnRegistrar.addEventListener('click', () => {
            limpiarFormulario();
            cargarEmpleados('entrada-id-empleado');
            openModal(modalRegistro);
        });
    }

    if (btnBuscarProveedor) {
        btnBuscarProveedor.addEventListener('click', async () => {
            await cargarProveedores();
            openModal(modalProveedores);
        });
    }

    // Seleccionar proveedor (crear)
    if (listaProveedores) {
        listaProveedores.addEventListener('click', async (e) => {
            const row = e.target.closest('tr[data-proveedor-id]');
            if (!row) return;
            const id = row.dataset.proveedorId;
            const proveedor = proveedores.find(p => String(p.id) === String(id));
            
            if (proveedor) {
                proveedorSeleccionado = {
                    id: proveedor.id,
                    nombre: proveedor.nombre
                };
                if (entradaIdProveedor) entradaIdProveedor.value = proveedorSeleccionado.id;
                if (entradaNombreProveedor) entradaNombreProveedor.value = proveedorSeleccionado.nombre;
                if (btnBuscarProductos) btnBuscarProductos.disabled = false;
                closeModal(modalProveedores);
                await cargarProductosProveedor(id);
            }
        });
    }

    // Seleccionar proveedor (editar)
    const listaProveedoresEditar = document.getElementById('lista-proveedores-editar');
    if (listaProveedoresEditar) {
        listaProveedoresEditar.addEventListener('click', async (e) => {
            const row = e.target.closest('tr[data-proveedor-id]');
            if (!row) return;
            const id = row.dataset.proveedorId;
            const proveedor = proveedores.find(p => String(p.id) === String(id));
            
            if (proveedor) {
                proveedorSeleccionadoEditar = {
                    id: proveedor.id,
                    nombre: proveedor.nombre
                };
                document.getElementById('editar-id-proveedor').value = proveedorSeleccionadoEditar.id;
                document.getElementById('editar-nombre-proveedor').value = proveedorSeleccionadoEditar.nombre;
                document.getElementById('btn-desplegar-productos-editar').disabled = false;
                closeModal(document.getElementById('modal-seleccionar-proveedor-editar'));
                await cargarProductosProveedorEditar(id);
            }
        });
    }

    // Buscar productos (crear)
    if (btnBuscarProductos) {
        btnBuscarProductos.addEventListener('click', () => {
            if (proveedorSeleccionado) {
                openModal(modalProductos);
            } else {
                mostrarMensaje('Primero debe seleccionar un proveedor.', true);
            }
        });
    }

    // Buscar productos (editar)
    const btnBuscarProductosEditar = document.getElementById('btn-desplegar-productos-editar');
    if (btnBuscarProductosEditar) {
        btnBuscarProductosEditar.addEventListener('click', () => {
            if (proveedorSeleccionadoEditar) {
                openModal(document.getElementById('modal-seleccionar-productos-editar'));
            } else {
                mostrarMensaje('Primero debe seleccionar un proveedor.', true);
            }
        });
    }

    // Seleccionar producto (crear)
    if (listaProductos) {
        listaProductos.addEventListener('click', function(e) {
            const row = e.target.closest('tr[data-producto-id]');
            if (!row) return;
            const id = row.dataset.productoId;
            
            const producto = productosDisponibles.find(p => String(p.ID_modelo) === String(id));
            
            if (!producto) {
                mostrarMensaje('Producto no encontrado', true);
                return;
            }
            
            if (!proveedorSeleccionado) {
                mostrarMensaje('Primero debe seleccionar un proveedor.', true);
                return;
            }
            
            if (!producto.ID_modelo) {
                mostrarMensaje('El producto no tiene un ID válido', true);
                return;
            }
            
            const existente = productosSeleccionados.find(p => p.id_modelo === String(producto.ID_modelo));
            if (existente) {
                existente.cantidad++;
            } else {
                productosSeleccionados.push({
                    id_modelo: String(producto.ID_modelo),
                    nombre: producto.N_modelo || 'Producto sin nombre',
                    proveedor: proveedorSeleccionado.nombre || '',
                    costo: Number(producto.Costo) || 0,
                    cantidad: 1
                });
            }
            renderizarSeleccionados();
            closeModal(modalProductos);
        });
    }

    // Seleccionar producto (editar)
    const listaProductosEditar = document.getElementById('lista-productos-editar');
    if (listaProductosEditar) {
        listaProductosEditar.addEventListener('click', function(e) {
            const row = e.target.closest('tr[data-producto-id]');
            if (!row) return;
            const id = row.dataset.productoId;
            
            const producto = productosDisponibles.find(p => String(p.ID_modelo) === String(id));
            
            if (!producto) {
                mostrarMensaje('Producto no encontrado', true);
                return;
            }
            
            if (!proveedorSeleccionadoEditar) {
                mostrarMensaje('Primero debe seleccionar un proveedor.', true);
                return;
            }
            
            if (!producto.ID_modelo) {
                mostrarMensaje('El producto no tiene un ID válido', true);
                return;
            }
            
            const existente = productosSeleccionadosEditar.find(p => p.id_modelo === String(producto.ID_modelo));
            if (existente) {
                existente.cantidad++;
            } else {
                productosSeleccionadosEditar.push({
                    id_modelo: String(producto.ID_modelo),
                    nombre: producto.N_modelo || 'Producto sin nombre',
                    proveedor: proveedorSeleccionadoEditar.nombre || '',
                    costo: Number(producto.Costo) || 0,
                    cantidad: 1
                });
            }
            renderizarSeleccionadosEditar();
            closeModal(document.getElementById('modal-seleccionar-productos-editar'));
        });
    }

    // Control de cantidad y eliminar (crear)
    if (tablaSeleccionados) {
        tablaSeleccionados.addEventListener('click', (e) => {
            const btn = e.target.closest('.btn-cantidad');
            if (btn) {
                const idx = parseInt(btn.dataset.index);
                const op = btn.dataset.op;
                if (!isNaN(idx) && productosSeleccionados[idx]) {
                    if (op === 'mas') productosSeleccionados[idx].cantidad++;
                    else if (op === 'menos' && productosSeleccionados[idx].cantidad > 1) productosSeleccionados[idx].cantidad--;
                    renderizarSeleccionados();
                }
                return;
            }

            const btnEliminar = e.target.closest('.btn-eliminar');
            if (btnEliminar) {
                const idx = parseInt(btnEliminar.dataset.index);
                if (!isNaN(idx)) {
                    productosSeleccionados.splice(idx, 1);
                    renderizarSeleccionados();
                }
            }
        });
    }

    // Control de cantidad y eliminar (editar)
    if (tablaSeleccionadosEditar) {
        tablaSeleccionadosEditar.addEventListener('click', (e) => {
            const btn = e.target.closest('.btn-cantidad');
            if (btn) {
                const idx = parseInt(btn.dataset.index);
                const op = btn.dataset.op;
                if (!isNaN(idx) && productosSeleccionadosEditar[idx]) {
                    if (op === 'mas') productosSeleccionadosEditar[idx].cantidad++;
                    else if (op === 'menos' && productosSeleccionadosEditar[idx].cantidad > 1) productosSeleccionadosEditar[idx].cantidad--;
                    renderizarSeleccionadosEditar();
                }
                return;
            }

            const btnEliminar = e.target.closest('.btn-eliminar-editar');
            if (btnEliminar) {
                const idx = parseInt(btnEliminar.dataset.index);
                if (!isNaN(idx)) {
                    productosSeleccionadosEditar.splice(idx, 1);
                    renderizarSeleccionadosEditar();
                }
            }
        });
    }

    // Guardar orden (crear)
    if (formRegistro) {
        formRegistro.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (!proveedorSeleccionado) {
                mostrarMensaje('Debe seleccionar un proveedor.', true);
                return;
            }
            
            if (productosSeleccionados.length === 0) {
                mostrarMensaje('Debe agregar al menos un producto.', true);
                return;
            }
            
            const selectEmpleado = document.getElementById('entrada-id-empleado');
            const ID_empleado = selectEmpleado?.value;
            
            if (!ID_empleado) {
                mostrarMensaje('Debe seleccionar el empleado que registra la orden.', true);
                return;
            }

            const payload = {
                ID_proveedor: parseInt(proveedorSeleccionado.id),
                ID_empleado: parseInt(ID_empleado),
                productos: productosSeleccionados.map(p => [String(p.id_modelo), p.cantidad])
            };

            try {
                const response = await fetchJson('/api/ordenes_compra/agregar', {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });
                if (response.success) {
                    mostrarMensaje('Orden de compra registrada exitosamente.');
                    limpiarFormulario();
                    closeModal(modalRegistro);
                    cargarOrdenesPendientes();
                } else {
                    mostrarMensaje(response.error || 'Error al registrar la orden.', true);
                }
            } catch (error) {
                console.error('Error guardando orden:', error);
                mostrarMensaje(error.message || 'Error al registrar la orden.', true);
            }
        });
    }

    // Guardar orden (editar)
    if (formEditar) {
        formEditar.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            console.log('📝 Enviando formulario de edición...');
            console.log('📋 Productos seleccionados:', productosSeleccionadosEditar);
            
            if (!proveedorSeleccionadoEditar) {
                mostrarMensaje('Debe seleccionar un proveedor.', true);
                return;
            }
            
            if (productosSeleccionadosEditar.length === 0) {
                mostrarMensaje('Debe agregar al menos un producto.', true);
                return;
            }
            
            // Validar que todos los productos tengan id_modelo
            for (const p of productosSeleccionadosEditar) {
                if (!p.id_modelo || p.id_modelo === '') {
                    mostrarMensaje('Hay un producto sin ID válido. Elimínelo y vuelva a agregarlo.', true);
                    return;
                }
            }
            
            const selectEmpleado = document.getElementById('editar-id-empleado');
            const ID_empleado = selectEmpleado?.value;
            
            if (!ID_empleado) {
                mostrarMensaje('Debe seleccionar el empleado que registra la orden.', true);
                return;
            }

            const payload = {
                ID_orden_c: ordenParaEditar,
                ID_proveedor: parseInt(proveedorSeleccionadoEditar.id),
                ID_empleado: parseInt(ID_empleado),
                productos: productosSeleccionadosEditar.map(p => [String(p.id_modelo), p.cantidad])
            };

            console.log('📤 Payload enviado:', payload);

            try {
                const response = await fetchJson('/api/ordenes_compra/actualizar', {
                    method: 'PUT',
                    body: JSON.stringify(payload)
                });
                if (response.success) {
                    mostrarMensaje('Orden de compra actualizada exitosamente.');
                    limpiarFormularioEditar();
                    closeModal(modalEditar);
                    cargarOrdenesPendientes();
                } else {
                    mostrarMensaje(response.error || 'Error al actualizar la orden.', true);
                }
            } catch (error) {
                console.error('Error actualizando orden:', error);
                mostrarMensaje(error.message || 'Error al actualizar la orden.', true);
            }
        });
    }

    // Acciones en tabla de pendientes
    if (tablaPendientes) {
        tablaPendientes.addEventListener('click', async (e) => {
            const btn = e.target.closest('button');
            if (!btn) return;
            const id = btn.dataset.id;
            if (!id) return;

            if (btn.classList.contains('btn-ver')) {
                await verDetalle(id);
            } else if (btn.classList.contains('btn-editar')) {
                await abrirEditarOrden(id);
            } else if (btn.classList.contains('btn-eliminar')) {
                abrirEliminarOrden(id);
            }
        });
    }

    // Confirmar eliminación
    if (btnConfirmarEliminar) {
        btnConfirmarEliminar.addEventListener('click', async () => {
            await confirmarEliminarOrden();
        });
    }

    // Cerrar modales
    document.querySelectorAll('[data-close-modal]').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('[data-modal]');
            if (modal) closeModal(modal);
        });
    });

    // Cerrar mensaje automático
    if (btnCerrarMensaje) {
        btnCerrarMensaje.addEventListener('click', () => {
            if (modalMensaje) modalMensaje.setAttribute('hidden', '');
        });
    }

    // Cargar datos iniciales
    cargarOrdenesPendientes();
    cargarProveedores();
});

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}