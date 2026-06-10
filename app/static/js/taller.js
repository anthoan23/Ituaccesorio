// ============================================
// TALLER.JS - Versión Refactorizada
// Módulos separados por responsabilidad
// ============================================

// --------------------------------
// 1. CONFIGURACIÓN GLOBAL
// --------------------------------
const CONFIG = {
    API: {
        ORDENES: '/api/taller/ordenes',
        REPARACIONES_ASIGNADAS: '/api/taller/reparaciones-asignadas',
        CONSULTAR_ORDEN: '/api/taller/consultar-ordene',
        CONSULTAR_TEST: '/api/taller/consultar-test',
        GUARDAR_REVISION: '/api/taller/guardar-revision',
        ASIGNAR_ORDEN: '/api/taller/asignar-orden',
        LIBERAR_ORDEN: '/api/taller/liberar-orden',
        GUARDAR_REPARACION: '/api/taller/guardar-reparacion'
    },
    VISTAS: {
        ORDENES: 'vista-1',
        DETALLE: 'vista-2',
        REVISION: 'vista-3',
        REPARACION: 'vista-4',
        ASIGNADAS: 'vista-5'
    },
    COMPONENTES_TEST: [
        'Btn_power', 'Cornetas', 'Mica', 'LCD', 'Tactil',
        'Btn_vol', 'Btn_sil', 'Puerto_carga', 'Wifi', 'Cam_pos',
        'Cam_del', 'Flash', 'Senal', 'Microfono', 'Sensor_proximidad',
        'Face_id', 'Bluetooth', 'Caja', 'Cargador', 'Cable',
        'Auricular', 'Manuales'
    ]
};

// --------------------------------
// 2. UTILIDADES
// --------------------------------
const Utils = {
    getCsrfToken() {
        const input = document.querySelector("input[name='_csrf_token']");
        return input?.value || "";
    },

    getAccessToken() {
        return localStorage.getItem("access_token") || 
               localStorage.getItem("token") || 
               sessionStorage.getItem("access_token") || 
               sessionStorage.getItem("token") || 
               "";
    },

    async fetchJson(url, options = {}) {
        const headers = new Headers(options.headers || {});
        headers.set("Accept", "application/json");

        if (options.body && !headers.has("Content-Type")) {
            headers.set("Content-Type", "application/json");
        }

        const csrf = this.getCsrfToken();
        if (csrf) {
            headers.set("X-CSRFToken", csrf);
            headers.set("X-CSRF-Token", csrf);
        }

        const token = this.getAccessToken();
        if (token && !headers.has("Authorization")) {
            headers.set("Authorization", `Bearer ${token}`);
        }

        const response = await fetch(url, {
            credentials: "same-origin",
            ...options,
            headers,
        });

        const contentType = response.headers.get("content-type") || "";
        const isJson = contentType.includes("application/json");
        const payload = isJson ? await response.json() : await response.text();

        if (!response.ok) {
            const msg = (isJson && payload?.message) || payload?.error || 
                       String(payload) || response.statusText || "Error en la solicitud";
            throw new Error(msg);
        }

        return payload;
    },

    escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    showMessage(message, isError = false) {
        if (!message) return;
        console[isError ? 'error' : 'log'](message);
    },

    formatDate(dateValue) {
        if (!dateValue) return '-';
        try {
            const date = new Date(dateValue);
            if (isNaN(date.getTime())) return '-';
            return date.toLocaleDateString('es-ES');
        } catch {
            return '-';
        }
    },

    getEstadoClase(estado) {
        const estados = {
            'pendiente': 'estado-pendiente',
            'en revisión': 'estado-revision',
            'en reparación': 'estado-reparacion',
            'completado': 'estado-completado',
            'entregado': 'estado-entregado',
            'asignada': 'estado-asignada'
        };
        return estados[String(estado || '').toLowerCase()] || 'estado-default';
    },

    obtenerIdEmpleadoActual() {
        const userStr = localStorage.getItem('user') || sessionStorage.getItem('user');
        if (userStr) {
            try {
                const user = JSON.parse(userStr);
                return user.id_empleado || user.ID_empleado || user.empleado_id;
            } catch(e) {}
        }
        
        const token = this.getAccessToken();
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                return payload.id_empleado || payload.ID_empleado || payload.empleado_id;
            } catch(e) {}
        }
        
        console.warn('No se pudo obtener ID del empleado, usando valor por defecto');
        return '32014004';
    }
};

// --------------------------------
// 3. GESTOR DE VISTAS
// --------------------------------
const ViewManager = {
    currentView: CONFIG.VISTAS.ORDENES,
    
    labels: {
        [CONFIG.VISTAS.ORDENES]: 'Órdenes de servicio',
        [CONFIG.VISTAS.DETALLE]: 'Información de la orden',
        [CONFIG.VISTAS.REVISION]: 'Revisión',
        [CONFIG.VISTAS.REPARACION]: 'Reparación',
        [CONFIG.VISTAS.ASIGNADAS]: 'Reparaciones asignadas'
    },

    activate(targetClass) {
        console.log('Activando vista:', targetClass);
        
        const showBreadcrumb = [CONFIG.VISTAS.DETALLE, CONFIG.VISTAS.REVISION, 
                                 CONFIG.VISTAS.REPARACION, CONFIG.VISTAS.ASIGNADAS].includes(targetClass);
        
        document.querySelectorAll('.content').forEach(panel => {
            panel.hidden = !panel.classList.contains(targetClass);
        });
        
        const separator = document.getElementById('breadcrumb-separator');
        const section = document.getElementById('breadcrumb-section');
        if (separator) separator.style.display = showBreadcrumb ? 'inline' : 'none';
        if (section) {
            section.style.display = showBreadcrumb ? 'inline' : 'none';
            section.textContent = showBreadcrumb ? this.labels[targetClass] : '';
        }
        
        document.querySelectorAll('[data-view-target]').forEach(btn => {
            const isActive = btn.getAttribute('data-view-target') === targetClass;
            btn.classList.toggle('is-active', isActive);
            btn.setAttribute('aria-pressed', String(isActive));
        });
        
        this.currentView = targetClass;
        
        if (targetClass === CONFIG.VISTAS.ORDENES) {
            OrdenesService.cargar();
        } else if (targetClass === CONFIG.VISTAS.ASIGNADAS) {
            ReparacionesService.cargarAsignadas();
        } else if (targetClass === CONFIG.VISTAS.REVISION) {
            const ordenActual = OrdenesService.obtenerOrdenActual();
            if (ordenActual) {
                document.getElementById('orden-id').textContent = ordenActual;
                document.getElementById('id_orden_servicio_revision').value = ordenActual;
            }
            // Llamar a iniciar cuando se activa la vista de revisión
            RevisionService.iniciar();
        } else if (targetClass === CONFIG.VISTAS.REPARACION) {
            const ordenActual = OrdenesService.obtenerOrdenActual();
            if (ordenActual) {
                document.getElementById('reparacion-orden-id').textContent = ordenActual;
            }
        }
    },

    init() {
        document.querySelectorAll('[data-view-target]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const target = btn.getAttribute('data-view-target');
                if (target) this.activate(target);
            });
        });
        this.activate(CONFIG.VISTAS.ORDENES);
    }
};

// --------------------------------
// 4. SERVICIO DE ÓRDENES
// --------------------------------
const OrdenesService = {
    ordenActualId: null,

    async cargar() {
        const tbody = document.getElementById('tabla-ordenes-servicio');
        if (!tbody) return;

        try {
            const data = await Utils.fetchJson(CONFIG.API.ORDENES, { method: 'GET' });
            const ordenes = Array.isArray(data) ? data : data?.ordenes || data?.data || [];
            this.renderizar(ordenes, tbody);
        } catch (error) {
            console.error('Error cargando órdenes:', error);
            this.renderizar([], tbody);
        }
    },

    renderizar(ordenes, tbody) {
        if (!ordenes.length) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No hay órdenes de servicio</td></tr>';
            return;
        }

        tbody.innerHTML = ordenes.map(orden => `
            <tr>
                <td data-label="ID orden">${Utils.escapeHtml(orden.id_orden)}</td>
                <td data-label="Estado"><span class="estado-badge ${Utils.getEstadoClase(orden.estado)}">${Utils.escapeHtml(orden.estado)}</span></td>
                <td data-label="ID cliente">${Utils.escapeHtml(orden.id_cliente)}</td>
                <td data-label="Nombre cliente">${Utils.escapeHtml(orden.nombre_cliente)}</td>
                <td data-label="Modelo">${Utils.escapeHtml(orden.modelo)}</td>
                <td data-label="Fecha ingreso">${Utils.formatDate(orden.fecha_e)}</td>
                <td class="table__actions" data-label="Acciones">
                    <div class="row-actions">
                        <button type="button" class="table-action" data-accion="ver-orden" data-id="${orden.id_orden}">Ver orden</button>
                        <button type="button" class="table-action table-action--accent" data-accion="tomar-orden" data-id="${orden.id_orden}">Tomar orden</button>
                    </div>
                </td>
            </tr>
        `).join('');
    },

    async verOrdenPreview(idOrden) {
        const modalBodyInfo = document.getElementById('modal-order-info');
        const modalBodyTests = document.getElementById('modal-order-tests');
        const tomarOrdenBtn = document.getElementById('modal-tomar-orden-btn');
        
        if (!modalBodyInfo) return;

        modalBodyInfo.innerHTML = '<p class="device-detail__empty">Cargando información de la orden...</p>';
        modalBodyTests.innerHTML = '';
        
        if (window.UiModal && typeof window.UiModal.openById === 'function') {
            window.UiModal.openById('modal-preview-orden');
        }

        if (tomarOrdenBtn) {
            tomarOrdenBtn.setAttribute('data-id', idOrden);
        }

        try {
            const data = await Utils.fetchJson(CONFIG.API.CONSULTAR_ORDEN, {
                method: 'POST',
                body: JSON.stringify({ id_orden: idOrden })
            });

            const orden = data.orden;
            const tests = data.tests || [];

            if (orden) {
                this.renderizarDetalleModal(modalBodyInfo, orden);
            } else {
                modalBodyInfo.innerHTML = '<p class="device-detail__empty error">No se encontró información de la orden</p>';
            }

            if (tests.length) {
                this.renderizarTestsModal(modalBodyTests, tests, idOrden);
            } else {
                modalBodyTests.innerHTML = '<h3 class="card__subtitle">Tests Realizados</h3><p class="device-detail__empty">No hay tests registrados para esta orden.</p>';
            }

        } catch (error) {
            console.error('Error al consultar orden:', error);
            modalBodyInfo.innerHTML = `<p class="device-detail__empty error">Error: ${Utils.escapeHtml(error.message)}</p>`;
            modalBodyTests.innerHTML = '';
        }
    },

    renderizarDetalleModal(container, orden) {
        const estiloCaja = 'background: #f8f9fa; padding: 0.85rem; border-radius: 6px; border: 1px solid #dee2e6;';
        
        container.innerHTML = `
            <div class="detail-group"><span class="detail-label">ID de la Orden:</span><strong>#${Utils.escapeHtml(orden.ID_orden_servicio)}</strong></div>
            <div class="detail-group"><span class="detail-label">Estado:</span><span class="estado-badge ${Utils.getEstadoClase(orden.Estado_orden_servicio)}">${Utils.escapeHtml(orden.Estado_orden_servicio)}</span></div>
            <div class="detail-group"><span class="detail-label">Cliente:</span><strong>${Utils.escapeHtml(orden.nombre_cliente)}</strong></div>
            <div class="detail-group"><span class="detail-label">Modelo:</span><strong>${Utils.escapeHtml(orden.Modelo)}</strong></div>
            <div class="detail-group field--full" style="grid-column: span 2;"><span class="detail-label">Descripción:</span><div style="${estiloCaja}">${Utils.escapeHtml(orden.Descripcion_reparacion || 'Sin descripción')}</div></div>
            <div class="detail-group field--full" style="grid-column: span 2;"><span class="detail-label">Nota:</span><div style="${estiloCaja}">${Utils.escapeHtml(orden.Nota_orden_servicio || 'Ninguna nota')}</div></div>
        `;
    },

    renderizarTestsModal(container, tests, idOrden) {
        container.innerHTML = `
            <h3 class="card__subtitle">Tests Realizados</h3>
            <div class="table-wrap" style="max-height: 300px; overflow-y: auto;">
                <table class="table" style="min-width: 100%;">
                    <thead>
                        <tr>
                            <th>N° Test</th>
                            <th>Cantidad</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tests.map(test => `
                            <tr>
                                <td data-label="N° Test">Test #${Utils.escapeHtml(test.Numero_test)}</td>
                                <td data-label="Cantidad">${Utils.escapeHtml(test.cantidad)}</td>
                                <td data-label="Acción" class="table__actions">
                                    <button class="table-action" data-accion="ver-test-modal" data-id-test="${Utils.escapeHtml(test.Numero_test)}" data-id-orden="${idOrden}">Ver detalles</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        container.querySelectorAll('[data-accion="ver-test-modal"]').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const numTest = btn.getAttribute('data-id-test');
                const idOrd = btn.getAttribute('data-id-orden');
                await RevisionService.verDetalle(idOrd, numTest);
            });
        });
    },

    async verDetalle(idOrden) {
        this.ordenActualId = idOrden;
        sessionStorage.setItem('orden_actual_id', idOrden);
        
        const infoContainer = document.getElementById('order-info');
        const testsContainer = document.getElementById('order-tests');
        const subtitle = document.getElementById('detalle-orden-subtitle');
        
        try {
            const data = await Utils.fetchJson(CONFIG.API.CONSULTAR_ORDEN, {
                method: 'POST',
                body: JSON.stringify({ id_orden: idOrden })
            });

            const orden = data.orden;
            const tests = data.tests || [];

            if (infoContainer && orden) {
                this.renderizarDetalle(infoContainer, orden);
            }

            if (testsContainer) {
                this.renderizarTests(testsContainer, tests, idOrden);
            }

            if (subtitle) {
                subtitle.textContent = `Visualizando la información completa de la orden #${idOrden}`;
            }

            this.actualizarTitulosVistas(idOrden, orden?.Modelo);
            
            ViewManager.activate(CONFIG.VISTAS.DETALLE);
        } catch (error) {
            console.error('Error al consultar orden:', error);
        }
    },

    renderizarDetalle(container, orden) {
        const estiloCaja = 'background: #f8f9fa; padding: 0.85rem; border-radius: 6px; border: 1px solid #dee2e6;';
        
        container.innerHTML = `
            <div class="detail-group"><span class="detail-label">ID de la Orden:</span><strong>#${Utils.escapeHtml(orden.ID_orden_servicio)}</strong></div>
            <div class="detail-group"><span class="detail-label">Estado:</span><span class="estado-badge ${Utils.getEstadoClase(orden.Estado_orden_servicio)}">${Utils.escapeHtml(orden.Estado_orden_servicio)}</span></div>
            <div class="detail-group"><span class="detail-label">Cliente:</span><strong>${Utils.escapeHtml(orden.nombre_cliente)}</strong></div>
            <div class="detail-group"><span class="detail-label">Modelo:</span><strong>${Utils.escapeHtml(orden.Modelo)}</strong></div>
            <div class="detail-group field--full" style="grid-column: span 2;"><span class="detail-label">Descripción:</span><div style="${estiloCaja}">${Utils.escapeHtml(orden.Descripcion_reparacion || 'Sin descripción')}</div></div>
            <div class="detail-group field--full" style="grid-column: span 2;"><span class="detail-label">Nota:</span><div style="${estiloCaja}">${Utils.escapeHtml(orden.Nota_orden_servicio || 'Ninguna nota')}</div></div>
        `;
        
        // Agregar botón de revisión
        this.agregarBotonRevision(container);
    },

    renderizarTests(container, tests, idOrden) {
        if (!tests || !tests.length) {
            container.innerHTML = '<h3 class="card__subtitle">Tests Realizados</h3><p class="device-detail__empty">No hay tests registrados.</p>';
            return;
        }

        container.innerHTML = `
            <h3 class="card__subtitle">Tests Realizados</h3>
            <div class="table-wrap">
                <table class="table">
                    <thead>
                        <tr>
                            <th>N° Test</th>
                            <th>Cantidad</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tests.map(test => `
                            <tr>
                                <td data-label="N° Test">Test #${Utils.escapeHtml(test.Numero_test)}</td>
                                <td data-label="Cantidad">${Utils.escapeHtml(test.cantidad)}</td>
                                <td data-label="Acción" class="table__actions">
                                    <button class="table-action" data-accion="ver-test" data-id-test="${Utils.escapeHtml(test.Numero_test)}" data-id-orden="${idOrden}">Ver detalles</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    },

    agregarBotonRevision(container) {
        const btnExistente = document.getElementById('btn-realizar-revision');
        if (btnExistente) btnExistente.remove();

        const btn = document.createElement('button');
        btn.id = 'btn-realizar-revision';
        btn.type = 'button';
        btn.className = 'form-btn form-btn--primary';
        btn.style.cssText = 'margin-top: 1rem; width: 100%;';
        btn.innerHTML = '🔧 Realizar revisión técnica';
        btn.addEventListener('click', () => {
            ViewManager.activate(CONFIG.VISTAS.REVISION);
        });
        
        container.appendChild(btn);
    },

    actualizarTitulosVistas(idOrden, modelo) {
        const reparacionOrdenId = document.getElementById('reparacion-orden-id');
        const reparacionModelo = document.getElementById('reparacion-modelo');
        if (reparacionOrdenId) reparacionOrdenId.textContent = idOrden;
        if (reparacionModelo) reparacionModelo.textContent = modelo || '-';
        
        const ordenIdSpan = document.getElementById('orden-id');
        if (ordenIdSpan) ordenIdSpan.textContent = idOrden;
        
        const inputOrden = document.getElementById('id_orden_servicio_revision');
        if (inputOrden) inputOrden.value = idOrden;
    },

    obtenerOrdenActual() {
        return this.ordenActualId || sessionStorage.getItem('orden_actual_id');
    },

    async asignarOrden(idOrden) {
        try {
            const idEmpleado = Utils.obtenerIdEmpleadoActual();
            
            await Utils.fetchJson(CONFIG.API.ASIGNAR_ORDEN, {
                method: 'POST',
                body: JSON.stringify({ 
                    id_orden: idOrden,
                    id_empleado: idEmpleado
                })
            });
            
            if (window.UiModal && typeof window.UiModal.close === 'function') {
                window.UiModal.close();
            }
            
            await this.cargar();
            
            if (ViewManager.currentView === CONFIG.VISTAS.ASIGNADAS) {
                await ReparacionesService.cargarAsignadas();
            }
            
            return true;
        } catch (error) {
            console.error('Error al tomar orden:', error);
            return false;
        }
    }
};

// --------------------------------
// 5. SERVICIO DE REVISIONES
// --------------------------------
const RevisionService = {
    iniciar() {
        const ordenId = OrdenesService.obtenerOrdenActual();
        
        if (!ordenId) {
            console.warn('No hay orden seleccionada');
            return;
        }
        
        const inputOrden = document.getElementById('id_orden_servicio_revision');
        const spanOrden = document.getElementById('orden-id');

        if (inputOrden) inputOrden.value = ordenId;
        if (spanOrden) spanOrden.textContent = ordenId;

        // Calcular el próximo número de test
        this.calcularProximoNumeroTest(ordenId).then(proximoTest => {
            const numeroTestInput = document.getElementById('numero_test_revision');
            const testIdSpan = document.getElementById('test-id-form');
            
            if (numeroTestInput) numeroTestInput.value = proximoTest;
            if (testIdSpan) testIdSpan.textContent = proximoTest;
            
            // Cargar los componentes
            this.cargarComponentes();
        }).catch(() => {
            const numeroTestInput = document.getElementById('numero_test_revision');
            const testIdSpan = document.getElementById('test-id-form');
            if (numeroTestInput) numeroTestInput.value = 1;
            if (testIdSpan) testIdSpan.textContent = 1;
            this.cargarComponentes();
        });
    },

    async calcularProximoNumeroTest(ordenId) {
        try {
            const data = await Utils.fetchJson(CONFIG.API.CONSULTAR_ORDEN, {
                method: 'POST',
                body: JSON.stringify({ id_orden: ordenId })
            });
            
            const tests = data.tests || [];
            if (tests.length === 0) return 1;
            
            const maxNumero = Math.max(...tests.map(t => parseInt(t.Numero_test) || 0));
            return maxNumero + 1;
        } catch (error) {
            console.error('Error calculando próximo test:', error);
            return 1;
        }
    },

    cargarComponentes() {
        const container = document.getElementById('test-componentes-grid');
        if (!container) {
            console.error('No se encontró el contenedor test-componentes-grid');
            return;
        }

        console.log('Cargando componentes de prueba...');
        
        container.innerHTML = CONFIG.COMPONENTES_TEST.map(comp => {
            const nombreLegible = comp.replace(/_/g, ' ')
                .replace('Btn', 'Botón')
                .replace('Cam', 'Cámara')
                .replace('sil', 'silencio')
                .replace('pos', 'posterior')
                .replace('del', 'delantera');
            return `
                <div class="test-row-item">
                    <span class="test-component-name">${Utils.escapeHtml(nombreLegible)}</span>
                    <div class="radio-group">
                        <label class="radio-label radio-label--success">
                            <input type="radio" name="test_${comp}" value="Funciona"> ✅ Funciona
                        </label>
                        <label class="radio-label radio-label--danger">
                            <input type="radio" name="test_${comp}" value="No funciona"> ❌ No funciona
                        </label>
                    </div>
                </div>
            `;
        }).join('');
        
        console.log('Componentes cargados correctamente');
    },

    async guardar(event) {
        event.preventDefault();
        
        const idOrden = document.getElementById('id_orden_servicio_revision')?.value;
        const numeroTest = document.getElementById('numero_test_revision')?.value;
        const observaciones = document.querySelector('textarea[name="observaciones"]')?.value;
        const idEmpleado = Utils.obtenerIdEmpleadoActual();

        if (!idOrden || !numeroTest) {
            console.warn('Datos de orden incompletos');
            return;
        }

        const componentesEvaluados = [];
        document.querySelectorAll('#form-revision-tecnica input[type="radio"]:checked').forEach(radio => {
            const nombre = radio.name.replace('test_', '').replace(/_/g, ' ');
            componentesEvaluados.push({ nombre, resultado: radio.value });
        });

        if (observaciones?.trim()) {
            componentesEvaluados.push({ nombre: 'Observaciones', resultado: observaciones.trim() });
        }

        if (!componentesEvaluados.length) {
            Utils.showMessage('Debes evaluar al menos un componente', true);
            return;
        }

        try {
            await Utils.fetchJson(CONFIG.API.GUARDAR_REVISION, {
                method: 'POST',
                body: JSON.stringify({
                    id_orden: idOrden,
                    id_empleado: parseInt(idEmpleado),
                    numero_test: parseInt(numeroTest),
                    componentes_evaluados: componentesEvaluados
                })
            });

            document.getElementById('form-revision-tecnica')?.reset();
            
            setTimeout(() => {
                ViewManager.activate(CONFIG.VISTAS.DETALLE);
                OrdenesService.verDetalle(idOrden);
            }, 1500);
        } catch (error) {
            console.error('Error al guardar revisión:', error);
            Utils.showMessage(error.message, true);
        }
    },

    async verDetalle(idOrden, numeroTest) {
        const modalBody = document.getElementById('modal-test-body');
        if (!modalBody) return;

        modalBody.innerHTML = '<p>Cargando...</p>';
        
        if (window.UiModal && typeof window.UiModal.openById === 'function') {
            window.UiModal.openById('modal-test-detail');
        }

        try {
            const data = await Utils.fetchJson(CONFIG.API.CONSULTAR_TEST, {
                method: 'POST',
                body: JSON.stringify({ id_orden: idOrden, numero_test: numeroTest })
            });

            const items = Array.isArray(data) ? data : [data];
            
            if (!items.length || !items[0]) {
                modalBody.innerHTML = '<p>No se encontraron registros</p>';
                return;
            }

            modalBody.innerHTML = items.map(item => `
                <div class="test-item-card">
                    <span class="test-component-name">${Utils.escapeHtml(item.test || 'Componente')}</span>
                    <strong>${Utils.escapeHtml(item.Resultado_test || 'Sin especificar')}</strong>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error al cargar test:', error);
            modalBody.innerHTML = `<p class="error">Error: ${Utils.escapeHtml(error.message)}</p>`;
        }
    }
};

// --------------------------------
// 6. SERVICIO DE REPARACIONES
// --------------------------------
const ReparacionesService = {
    async cargarAsignadas() {
        const tbody = document.getElementById('tabla-reparaciones-asignadas');
        if (!tbody) return;

        try {
            const data = await Utils.fetchJson(CONFIG.API.REPARACIONES_ASIGNADAS, { 
                method: 'POST',
                body: JSON.stringify({})
            });

            const reparaciones = Array.isArray(data) ? data : data?.reparaciones || data?.data || [];
            this.renderizarAsignadas(reparaciones, tbody);
        } catch (error) {
            console.error('Error cargando reparaciones:', error);
            this.renderizarAsignadas([], tbody);
        }
    },

    renderizarAsignadas(reparaciones, tbody) {
        if (!reparaciones.length) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">Sin reparaciones asignadas por ahora.</td></tr>';
            return;
        }

        tbody.innerHTML = reparaciones.map(rep => `
            <tr>
                <td data-label="ID orden">${Utils.escapeHtml(rep.id_orden)}</td>
                <td data-label="Modelo">${Utils.escapeHtml(rep.modelo)}</td>
                <td data-label="Fecha ingreso">${Utils.formatDate(rep.fecha_e)}</td>
                <td class="table__actions" data-label="Acciones">
                    <div class="row-actions">
                        <button type="button" class="table-action" data-accion="ver" data-id="${rep.id_orden}">Ver detalle</button>
                        <button type="button" class="table-action" data-accion="iniciar-reparacion" data-id="${rep.id_orden}">Iniciar reparación</button>
                        <button type="button" class="table-action table-action--danger" data-accion="liberar-orden" data-id="${rep.id_orden}">Liberar orden</button>
                    </div>
                </td>
            </tr>
        `).join('');
    },

    iniciar(idOrden = null) {
        const ordenId = idOrden || OrdenesService.obtenerOrdenActual();
        
        if (!ordenId) {
            console.warn('No hay orden seleccionada');
            return;
        }
        
        console.log('Iniciar reparación de orden:', ordenId);
        
        const reparacionOrdenId = document.getElementById('reparacion-orden-id');
        if (reparacionOrdenId) reparacionOrdenId.textContent = ordenId;
        
        setTimeout(() => {
            OrdenesService.verDetalle(ordenId);
            ViewManager.activate(CONFIG.VISTAS.REPARACION);
        }, 500);
    },

    async liberarOrden(idOrden) {
        try {
            const idEmpleado = Utils.obtenerIdEmpleadoActual();
            
            await Utils.fetchJson(CONFIG.API.LIBERAR_ORDEN, {
                method: 'POST',
                body: JSON.stringify({ 
                    id_orden: idOrden,
                    id_empleado: idEmpleado
                })
            });
            
            await this.cargarAsignadas();
            await OrdenesService.cargar();
            
        } catch (error) {
            console.error('Error al liberar orden:', error);
        }
    }
};

// --------------------------------
// 7. INICIALIZACIÓN Y EVENTOS
// --------------------------------
document.addEventListener("DOMContentLoaded", () => {
    console.log('DOM cargado - Inicializando taller.js');
    
    ViewManager.init();

    const tablaOrdenes = document.getElementById("tabla-ordenes-servicio");
    if (tablaOrdenes) {
        tablaOrdenes.addEventListener("click", async (event) => {
            const button = event.target.closest("button[data-accion]");
            if (!button) return;

            const accion = button.getAttribute("data-accion");
            const idOrden = button.getAttribute("data-id");

            if (accion === "ver-orden") {
                OrdenesService.verOrdenPreview(idOrden);
            } else if (accion === "tomar-orden") {
                await OrdenesService.asignarOrden(idOrden);
            }
        });
    }

    const tablaReparaciones = document.getElementById("tabla-reparaciones-asignadas");
    if (tablaReparaciones) {
        tablaReparaciones.addEventListener("click", async (event) => {
            const button = event.target.closest("button[data-accion]");
            if (!button) return;

            const accion = button.getAttribute("data-accion");
            const idOrden = button.getAttribute("data-id");

            if (accion === "ver") {
                OrdenesService.verDetalle(idOrden);
            } else if (accion === "iniciar-reparacion") {
                ReparacionesService.iniciar(idOrden);
            } else if (accion === "liberar-orden") {
                await ReparacionesService.liberarOrden(idOrden);
            }
        });
    }

    const contenedorTests = document.getElementById("order-tests");
    if (contenedorTests) {
        contenedorTests.addEventListener("click", (event) => {
            const button = event.target.closest("button[data-accion='ver-test']");
            if (!button) return;

            const numTest = button.getAttribute("data-id-test");
            const idOrden = button.getAttribute("data-id-orden");
            RevisionService.verDetalle(idOrden, numTest);
        });
    }

    const formularioRevision = document.getElementById('form-revision-tecnica');
    if (formularioRevision) {
        formularioRevision.addEventListener('submit', (e) => RevisionService.guardar(e));
    }

    const btnGuardarReparacion = document.getElementById('btn-guardar-reparacion');
    if (btnGuardarReparacion) {
        btnGuardarReparacion.addEventListener('click', () => {
            console.log('Función guardar reparación en desarrollo');
        });
    }

    const modalTomarOrdenBtn = document.getElementById('modal-tomar-orden-btn');
    if (modalTomarOrdenBtn) {
        modalTomarOrdenBtn.addEventListener('click', async () => {
            const idOrden = modalTomarOrdenBtn.getAttribute('data-id');
            if (idOrden) {
                await OrdenesService.asignarOrden(idOrden);
            }
        });
    }
});