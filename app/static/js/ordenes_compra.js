document.addEventListener('DOMContentLoaded', () => {
    // Elementos DOM
    const vistaPendientes = document.getElementById('vista-pendientes');
    const vistaEntregadas = document.getElementById('vista-entregadas');
    const btnPendientes = document.getElementById('btn-pendientes');
    const btnEntregadas = document.getElementById('btn-entregadas');
    const tablaPendientes = document.getElementById('tabla-ordenes-pendientes');
    const tablaEntregadas = document.getElementById('tabla-ordenes-entregadas');
    const btnRegistrar = document.getElementById('btn-registrar-entrada');
    const modalRegistro = document.getElementById('modal-registrar-entrada');
    const modalProveedores = document.getElementById('modal-seleccionar-proveedor');
    const modalProductos = document.getElementById('modal-seleccionar-productos');
    const modalDetalle = document.getElementById('modal-detalle-orden');
    const modalAnular = document.getElementById('modal-confirmar-anular-orden');
    const modalEntrega = document.getElementById('modal-registrar-entrega');
    const modalMensaje = document.getElementById('modal-mensaje');
    const btnBuscarProveedor = document.getElementById('btn-desplegar-proveedores');
    const btnBuscarProductos = document.getElementById('btn-desplegar-productos');
    const listaProveedores = document.getElementById('lista-proveedores');
    const listaProductos = document.getElementById('lista-productos');
    const tablaSeleccionados = document.getElementById('tabla-productos-seleccionados');
    const costoTotalSpan = document.getElementById('entrada-costo-total');
    const btnGuardar = document.getElementById('btn-guardar-entrada');
    const formRegistro = document.getElementById('form-registrar-entrada');
    const entradaIdProveedor = document.getElementById('entrada-id-proveedor');
    const entradaNombreProveedor = document.getElementById('entrada-nombre-proveedor');
    const btnConfirmarAnular = document.getElementById('btn-confirmar-anular-orden');
    const btnConfirmarEntrega = document.getElementById('btn-confirmar-entrega');
    const entregaRecibidoPor = document.getElementById('entrega-recibido-por');
    const entregaFecha = document.getElementById('entrega-fecha');
    const mensajeTexto = document.getElementById('mensaje-texto');
    const btnCerrarMensaje = document.getElementById('btn-cerrar-mensaje');

    // Estado
    let proveedores = [];
    let empleados = [];
    let productosDisponibles = [];
    let productosSeleccionados = [];
    let proveedorSeleccionado = null;
    let ordenParaAnular = null;
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

    // Mostrar modal de mensaje
    function mostrarMensaje(mensaje, esError = false) {
        if (mensajeTexto) {
            mensajeTexto.textContent = mensaje;
            mensajeTexto.style.color = esError ? '#dc2626' : '#10b981';
        }
        if (modalMensaje) modalMensaje.removeAttribute('hidden');
        setTimeout(() => {
            if (modalMensaje) modalMensaje.setAttribute('hidden', '');
        }, 3000);
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
        
        if (dateStr === '%Y-%m-%d') {
            return 'Fecha por definir';
        }
        
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
            console.error("Error formateando fecha:", dateStr, error);
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
            cargarOrdenesPendientes();
        } else {
            if (vistaPendientes) vistaPendientes.classList.add('hidden');
            if (vistaEntregadas) vistaEntregadas.classList.remove('hidden');
            if (btnPendientes) btnPendientes.classList.remove('is-active');
            if (btnEntregadas) btnEntregadas.classList.add('is-active');
            cargarOrdenesEntregadas();
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
                    
                    return `
                        <tr>
                            <td>${escapeHtml(orden.ID_orden_c)}</td>
                            <td><strong>${escapeHtml(nombreProveedor)}</strong></td>
                            <td>${escapeHtml(fecha)}</td>
                            <td><span class="status-badge status-pendiente">${escapeHtml(orden.Estado || 'Pendiente')}</span></td>
                            <td>Bs. ${escapeHtml(formatMoney(orden.Costo_venta || 0))}</td>
                            <td class="table__actions">
                                <button class="btn btn--small btn-ver" data-id="${escapeHtml(orden.ID_orden_c)}">Ver</button>
                                <button class="btn btn--small btn-anular" data-id="${escapeHtml(orden.ID_orden_c)}">Anular</button>
                                <button class="btn btn--small btn-entrega" data-id="${escapeHtml(orden.ID_orden_c)}">Registrar entrega</button>
                            </td>
                        </tr>
                    `;
                }).join('');
            } else {
                tablaPendientes.innerHTML = '<tr><td colspan="6" class="table__empty">No hay órdenes de compra pendientes.穷';
            }
        } catch (error) {
            console.error('Error cargando órdenes:', error);
            tablaPendientes.innerHTML = '<tr><td colspan="6" class="table__empty">Error al cargar las órdenes.穷';
        }
    }

    // Cargar órdenes entregadas
    async function cargarOrdenesEntregadas() {
        if (!tablaEntregadas) return;
        
        try {
            const data = await fetchJson('/api/ordenes_compra/entregadas');
            
            if (Array.isArray(data) && data.length > 0) {
                tablaEntregadas.innerHTML = data.map(orden => {
                    const nombreProveedor = orden.N_proveedor || orden.nombre || 'Sin proveedor';
                    const fechaEntrega = orden.Fecha_entrega ? formatDate(orden.Fecha_entrega) : 'Fecha no disponible';
                    
                    return `
                        <tr>
                            <td>${escapeHtml(orden.ID_orden_c)}</td>
                            <td><strong>${escapeHtml(nombreProveedor)}</strong></td>
                            <td>${escapeHtml(fechaEntrega)}</td>
                            <td>${escapeHtml(orden.Recibido_por || '-')}</td>
                            <td>Bs. ${escapeHtml(formatMoney(orden.Costo_venta || 0))}</td>
                            <td class="table__actions">
                                <button class="btn btn--small btn-ver" data-id="${escapeHtml(orden.ID_orden_c)}">Ver</button>
                            </td>
                        </tr>
                    `;
                }).join('');
            } else {
                tablaEntregadas.innerHTML = '</tr><td colspan="6" class="table__empty">No hay órdenes de compra entregadas.穷';
            }
        } catch (error) {
            console.error('Error cargando órdenes entregadas:', error);
            tablaEntregadas.innerHTML = '<tr><td colspan="6" class="table__empty">Error al cargar las órdenes.穷';
        }
    }

// Cargar empleados - Versión simplificada
async function cargarEmpleados() {
    const selectEmpleado = document.getElementById('entrada-id-empleado');
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
                    </table>
                `).join('');
            } else {
                listaProveedores.innerHTML = '<tr><td colspan="4" class="table__empty">No hay proveedores registrados.穷';
            }
        } catch (error) {
            console.error('Error cargando proveedores:', error);
            listaProveedores.innerHTML = '<tr><td colspan="4" class="table__empty">Error al cargar proveedores.穷';
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
                listaProductos.innerHTML = '<tr><td colspan="4" class="table__empty">Este proveedor no tiene productos registrados.穷';
            }
        } catch (error) {
            console.error('Error cargando productos:', error);
            listaProductos.innerHTML = '<tr><td colspan="4" class="table__empty">Error al cargar productos.穷';
        }
    }

    // Renderizar productos seleccionados
    function renderizarSeleccionados() {
        if (!tablaSeleccionados) return;
        
        if (productosSeleccionados.length === 0) {
            tablaSeleccionados.innerHTML = '<table><td colspan="5" class="table__empty">Aún no hay productos seleccionados.穷';
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

    // Actualizar costo total
    function actualizarTotal() {
        const total = productosSeleccionados.reduce((sum, p) => sum + (p.costo * p.cantidad), 0);
        if (costoTotalSpan) costoTotalSpan.textContent = formatMoney(total);
        if (btnGuardar) btnGuardar.disabled = productosSeleccionados.length === 0 || !proveedorSeleccionado;
    }

    // Limpiar formulario
    function limpiarFormulario() {
        productosSeleccionados = [];
        proveedorSeleccionado = null;
        if (entradaIdProveedor) entradaIdProveedor.value = '';
        if (entradaNombreProveedor) entradaNombreProveedor.value = '';
        if (btnBuscarProductos) btnBuscarProductos.disabled = true;
        renderizarSeleccionados();
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

// Cargar productos de la orden para preview
async function cargarProductosOrdenParaEntrega(idOrden) {
    const container = document.getElementById('entrega-productos-preview');
    if (!container) return;
    
    try {
        const data = await fetchJson(`/api/detalles_orden/${idOrden}`, { method: 'GET' });
        const productos = data.productos_orden || [];
        
        if (productos.length > 0) {
            // Calcular total
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

    // Ver detalle de orden
    async function verDetalle(id) {
        console.log("=== VER DETALLE ===");
        console.log("ID de orden a buscar:", id);
        
        try {
            const data = await fetchJson(`/api/detalles_orden/${id}`, { method: 'GET' });
            console.log("Respuesta del servidor:", data);
            
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
                        productosContainer.innerHTML = '<tr><td colspan="5" class="table__empty">No hay productos en esta orden.穷';
                    }
                }

                if (totalSpan) totalSpan.textContent = formatMoney(detalle.Costo_venta || 0);
                openModal(modalDetalle);
            } else {
                console.error("No se encontró la orden:", id);
                mostrarMensaje(`No se pudo encontrar la orden ${id}`, true);
            }
        } catch (error) {
            console.error('Error cargando detalle:', error);
            mostrarMensaje(error.message || 'No se pudo cargar el detalle de la orden.', true);
        }
    }

    // Event Listeners
    if (btnPendientes) btnPendientes.addEventListener('click', () => cambiarVista('pendientes'));
    if (btnEntregadas) btnEntregadas.addEventListener('click', () => cambiarVista('entregadas'));

    if (btnRegistrar) {
        btnRegistrar.addEventListener('click', () => {
            limpiarFormulario();
            cargarEmpleados();
            openModal(modalRegistro);
        });
    }

    if (btnBuscarProveedor) {
        btnBuscarProveedor.addEventListener('click', async () => {
            await cargarProveedores();
            openModal(modalProveedores);
        });
    }

    // Seleccionar proveedor
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

    // Buscar productos
    if (btnBuscarProductos) {
        btnBuscarProductos.addEventListener('click', () => {
            if (proveedorSeleccionado) {
                openModal(modalProductos);
            } else {
                mostrarMensaje('Primero debe seleccionar un proveedor.', true);
            }
        });
    }

    // Seleccionar producto
    if (listaProductos) {
        listaProductos.addEventListener('click', (e) => {
            const row = e.target.closest('tr[data-producto-id]');
            if (!row) return;
            const id = row.dataset.productoId;
            const producto = productosDisponibles.find(p => String(p.ID_modelo) === String(id));
            
            if (producto && proveedorSeleccionado) {
                const existente = productosSeleccionados.find(p => p.id_modelo === id);
                if (existente) {
                    existente.cantidad++;
                } else {
                    productosSeleccionados.push({
                        id_modelo: id,
                        nombre: producto.N_modelo,
                        proveedor: proveedorSeleccionado.nombre,
                        costo: Number(producto.Costo),
                        cantidad: 1
                    });
                }
                renderizarSeleccionados();
                closeModal(modalProductos);
            }
        });
    }

    // Control de cantidad y eliminar
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

    // Guardar orden
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
            
            // Obtener el empleado seleccionado
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

            console.log("Payload enviado:", payload);

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

    // Acciones en tabla de pendientes
    if (tablaPendientes) {
        tablaPendientes.addEventListener('click', async (e) => {
            const btn = e.target.closest('button');
            if (!btn) return;
            const id = btn.dataset.id;
            if (!id) return;

            if (btn.classList.contains('btn-ver')) {
                await verDetalle(id);
            } else if (btn.classList.contains('btn-anular')) {
                ordenParaAnular = id;
                if (modalAnular) openModal(modalAnular);
            } else if (btn.classList.contains('btn-entrega')) {
                ordenParaEntrega = id;
                if (entregaRecibidoPor) entregaRecibidoPor.value = '';
                if (entregaFecha) entregaFecha.value = new Date().toISOString().slice(0, 10);
                
                await cargarProductosOrdenParaEntrega(id);
                
                if (modalEntrega) openModal(modalEntrega);
            }
        });
    }

    // Confirmar anulación
    if (btnConfirmarAnular) {
        btnConfirmarAnular.addEventListener('click', async () => {
            if (!ordenParaAnular) return;
            
            try {
                const response = await fetchJson('/api/ordenes_compra/anular', {
                    method: 'POST',
                    body: JSON.stringify({ ID_orden_c: ordenParaAnular })
                });
                if (response.success) {
                    mostrarMensaje('Orden anulada exitosamente.');
                    closeModal(modalAnular);
                    ordenParaAnular = null;
                    cargarOrdenesPendientes();
                } else {
                    mostrarMensaje(response.error || 'Error al anular la orden.', true);
                }
            } catch (error) {
                console.error('Error anulando orden:', error);
                mostrarMensaje(error.message || 'Error al anular la orden.', true);
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
                const response = await fetchJson(`/api/ordenes_compra/${ordenParaEntrega}/entrega`, {
                    method: 'POST',
                    body: JSON.stringify({ recibido_por: recibidoPor, fecha_entrega: fechaEntrega })
                });
                if (response.success) {
                    mostrarMensaje('Entrega registrada exitosamente. Stock actualizado.');
                    closeModal(modalEntrega);
                    ordenParaEntrega = null;
                    cargarOrdenesPendientes();
                    cargarOrdenesEntregadas();
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

    // Acciones en tabla de entregadas
    if (tablaEntregadas) {
        tablaEntregadas.addEventListener('click', async (e) => {
            const btn = e.target.closest('.btn-ver');
            if (btn && btn.dataset.id) {
                await verDetalle(btn.dataset.id);
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