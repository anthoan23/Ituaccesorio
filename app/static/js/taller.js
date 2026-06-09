// ============================================
// 1. CONSTANTES Y CONFIGURACIÓN
// ============================================
const CONFIG = {
    API: {
        ORDENES: '/api/taller/ordenes',
        REPARACIONES_ASIGNADAS: '/api/taller/reparaciones-asignadas',
        CONSULTAR_ORDEN: '/api/taller/consultar-ordene',
        CONSULTAR_TEST: '/api/taller/consultar-test',
        GUARDAR_REVISION: '/api/taller/guardar-revision'
    },
    VISTAS: {
        ORDENES: 'vista-1',
        REPARACIONES_ASIGNADAS: 'vista-5'
    }
};

// ============================================
// 2. UTILIDADES
// ============================================
const Utils = {
    getCsrfToken() {
        const input = document.querySelector("input[name='_csrf_token']");
        return input ? input.value : "";
    },

    getAccessToken() {
        return (
            localStorage.getItem("access_token") ||
            localStorage.getItem("token") ||
            sessionStorage.getItem("access_token") ||
            sessionStorage.getItem("token") ||
            ""
        );
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
            const msg =
                (isJson && payload && (payload.message || payload.error)) ||
                String(payload || response.statusText || "Error en la solicitud");
            throw new Error(msg);
        }

        return payload;
    },

    escapeHtml(value) {
        if (value === null || value === undefined) return '';
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    },

    showMessage(message, isError = false) {
        if (!message) return;
        console.info(message);
        // Aquí puedes implementar un toast o alerta visual
        if (isError) {
            alert(`❌ Error: ${message}`);
        } else {
            alert(`✅ ${message}`);
        }
    },

    formatDate(dateValue) {
        if (!dateValue) return '-';
        
        try {
            if (dateValue instanceof Date) {
                const day = String(dateValue.getDate()).padStart(2, '0');
                const month = String(dateValue.getMonth() + 1).padStart(2, '0');
                const year = dateValue.getFullYear();
                return `${day}/${month}/${year}`;
            }
            
            let dateStr = String(dateValue);
            
            const rfcMatch = dateStr.match(/(\d{2})\s+(\w+)\s+(\d{4})/);
            if (rfcMatch) {
                const day = rfcMatch[1];
                const monthName = rfcMatch[2];
                const year = rfcMatch[3];
                
                const meses = {
                    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                };
                const month = meses[monthName] || '01';
                return `${day}/${month}/${year}`;
            }
            
            if (dateStr.includes(' ') || dateStr.includes('T')) {
                dateStr = dateStr.split(/[ T]/)[0];
            }
            
            if (dateStr.match(/^\d{4}-\d{2}-\d{2}/)) {
                const [year, month, day] = dateStr.split('-');
                return `${day}/${month}/${year}`;
            }
            
            if (dateStr.match(/^\d{2}\/\d{2}\/\d{4}/)) {
                return dateStr;
            }
            
            const date = new Date(dateStr);
            if (!isNaN(date.getTime())) {
                const day = String(date.getDate()).padStart(2, '0');
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const year = date.getFullYear();
                return `${day}/${month}/${year}`;
            }
            
            return '-';
        } catch (e) {
            console.error('Error formateando fecha:', e, dateValue);
            return '-';
        }
    },

    getEstadoClase(estado) {
        const estadoStr = String(estado || '').toLowerCase();
        const estados = {
            'pendiente': 'estado-pendiente',
            'en revisión': 'estado-revision',
            'en reparación': 'estado-reparacion',
            'completado': 'estado-completado',
            'entregado': 'estado-entregado',
            'asignada': 'estado-asignada'
        };
        return estados[estadoStr] || 'estado-default';
    },

    getEstadoTexto(estado) {
        if (!estado) return 'Desconocido';
        return estado;
    },

    obtenerIdEmpleadoActual() {
        // MÉTODO 1: Desde localStorage/sessionStorage (si guardas el usuario al hacer login)
        const userStr = localStorage.getItem('user') || sessionStorage.getItem('user');
        if (userStr) {
            try {
                const user = JSON.parse(userStr);
                return user.id_empleado || user.ID_empleado || user.empleado_id || user.ID_empleado;
            } catch(e) {}
        }
        
        // MÉTODO 2: Desde el token JWT (decodificarlo)
        const token = this.getAccessToken();
        if (token) {
            try {
                // Decodificar JWT (solo la parte del payload)
                const parts = token.split('.');
                if (parts.length === 3) {
                    const payload = JSON.parse(atob(parts[1]));
                    return payload.id_empleado || payload.ID_empleado || payload.empleado_id;
                }
            } catch(e) {}
        }
        
        // MÉTODO 3: Desde un campo oculto en el HTML
        const campoEmpleado = document.getElementById('id_empleado_actual');
        if (campoEmpleado && campoEmpleado.value) {
            return campoEmpleado.value;
        }
        
        // MÉTODO 4: Desde un meta tag
        const metaEmpleado = document.querySelector('meta[name="empleado-id"]');
        if (metaEmpleado && metaEmpleado.getAttribute('content')) {
            return metaEmpleado.getAttribute('content');
        }
        
        // Valor por defecto para pruebas (NO USAR EN PRODUCCIÓN)
        console.warn('No se pudo obtener el ID del empleado, usando valor por defecto 32014004');
        return 32014004;
    }
};

// ============================================
// 3. MANEJADORES DE VISTAS (TABS)
// ============================================

function activateView(targetClass) {
    console.log('Activando vista:', targetClass);
    
    const breadcrumbLabels = {
        'vista-1': 'Ordenes de servicio',
        'vista-2': 'Informacion de la orden',
        'vista-3': 'Revision',
        'vista-4': 'Reparacion',
        'vista-5': 'Reparaciones asignadas',
    };
    
    const showBreadcrumbSuffix = ['vista-2', 'vista-3', 'vista-4', 'vista-5'].includes(targetClass);
    
    const viewPanels = document.querySelectorAll(".content.vista-1, .content.vista-2, .content.vista-3, .content.vista-4, .content.vista-5");
    viewPanels.forEach((panel) => {
        panel.hidden = !panel.classList.contains(targetClass);
    });
    
    const breadcrumbSeparator = document.getElementById('breadcrumb-separator');
    const breadcrumbSection = document.getElementById('breadcrumb-section');
    
    if (breadcrumbSeparator) {
        breadcrumbSeparator.style.display = showBreadcrumbSuffix ? 'inline' : 'none';
    }
    
    if (breadcrumbSection) {
        breadcrumbSection.style.display = showBreadcrumbSuffix ? 'inline' : 'none';
        breadcrumbSection.textContent = showBreadcrumbSuffix ? (breadcrumbLabels[targetClass] || '') : '';
    }
    
    const allButtons = document.querySelectorAll('.vista-switcher__btn');
    allButtons.forEach((button) => {
        const isActive = button.getAttribute('data-view-target') === targetClass;
        button.classList.toggle("is-active", isActive);
        button.setAttribute("aria-pressed", String(isActive));
    });
    
    if (targetClass === 'vista-1') {
        cargarOrdenesServicio();
    } else if (targetClass === 'vista-5') {
        cargarReparacionesAsignadas();
    }
}

function inicializarCambioVistas() {
    const viewButtons = document.querySelectorAll("[data-view-target]");
    
    console.log('Botones de vista encontrados:', viewButtons.length);
    
    viewButtons.forEach((button) => {
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        
        newButton.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            
            const targetView = newButton.getAttribute("data-view-target");
            console.log('Click en botón, vista target:', targetView);
            
            if (targetView) {
                activateView(targetView);
            }
        });
    });
}

// ============================================
// 4. MANEJADORES DE TABLA (ÓRDENES)
// ============================================
function renderTablaOrdenes(ordenes) {
    const tbody = document.getElementById("tabla-ordenes-servicio");
    if (!tbody) {
        console.error('No se encontró el elemento tabla-ordenes-servicio');
        return;
    }

    if (!ordenes || !ordenes.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center;">No hay órdenes de servicio para mostrar.</td>
            </tr>
        `;
        return;
    }

    console.log('Órdenes a renderizar:', ordenes);

    tbody.innerHTML = ordenes
        .map((raw) => {
            const idOrden = Utils.escapeHtml(raw.id_orden);
            const estado = Utils.escapeHtml(raw.estado);
            const estadoClase = Utils.getEstadoClase(raw.estado);
            const idCliente = Utils.escapeHtml(raw.id_cliente);
            const nombreCliente = Utils.escapeHtml(raw.nombre_cliente);
            const modelo = Utils.escapeHtml(raw.modelo);
            const descripcion = Utils.escapeHtml(raw.descripcion || '-');
            const fechaIngreso = Utils.formatDate(raw.fecha_e);

            return `
                <tr>
                    <td data-label="ID orden">${idOrden}</td>
                    <td data-label="Estado"><span class="estado-badge ${estadoClase}">${estado}</span></td>
                    <td data-label="ID cliente">${idCliente}</td>
                    <td data-label="Nombre cliente">${nombreCliente}</td>
                    <td data-label="Modelo">${modelo}</td>
                    <td data-label="Descripción">${descripcion}</td>
                    <td data-label="Fecha ingreso">${fechaIngreso}</td>
                    <td class="table__actions" data-label="Acciones">
                        <div class="row-actions">
                            <button type="button" class="table-action" data-accion="ver" data-id="${idOrden}">Ver detalle</button>
                            <button type="button" class="table-action" data-accion="cambiar-estado" data-id="${idOrden}" data-estado="${estado}">Cambiar estado</button>
                        </div>
                    </td>
                </tr>
            `;
        })
        .join("");
    
    console.log('Tabla de órdenes renderizada correctamente');
}

// ============================================
// 5. MANEJADORES DE TABLA (REPARACIONES ASIGNADAS)
// ============================================
function renderTablaReparaciones(reparaciones) {
    const tbody = document.getElementById("tabla-reparaciones-asignadas");
    if (!tbody) {
        console.error('No se encontró el elemento tabla-reparaciones-asignadas');
        return;
    }

    if (!reparaciones || !reparaciones.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="3" style="text-align: center;">Sin reparaciones asignadas por ahora.</td>
            </tr>
        `;
        return;
    }

    console.log('Reparaciones a renderizar:', reparaciones);

    tbody.innerHTML = reparaciones
        .map((raw) => {
            const idOrden = Utils.escapeHtml(raw.id_orden);
            const modelo = Utils.escapeHtml(raw.modelo);
            const estado = Utils.escapeHtml(raw.estado);
            const estadoClase = Utils.getEstadoClase(raw.estado);

            return `
                <tr>
                    <td data-label="ID orden">${idOrden}</td>
                    <td data-label="Modelo">${modelo}</td>
                    <td class="table__actions" data-label="Acciones">
                        <div class="row-actions">
                            <button type="button" class="table-action" data-accion="ver" data-id="${idOrden}">Ver detalle</button>
                            <button type="button" class="table-action" data-accion="iniciar-reparacion" data-id="${idOrden}">Iniciar reparación</button>
                        </div>
                    </td>
                </tr>
            `;
        })
        .join("");
    
    console.log('Tabla de reparaciones renderizada correctamente');
}

// ============================================
// 6. CRUD DE ÓRDENES Y REPARACIONES
// ============================================
async function cargarOrdenesServicio() {
    try {
        console.log('Cargando órdenes de servicio desde:', CONFIG.API.ORDENES);
        const data = await Utils.fetchJson(CONFIG.API.ORDENES, { method: "GET" });
        console.log('Respuesta de la API:', data);
        
        let ordenes = [];
        if (Array.isArray(data)) {
            ordenes = data;
        } else if (data?.ordenes && Array.isArray(data.ordenes)) {
            ordenes = data.ordenes;
        } else if (data?.data && Array.isArray(data.data)) {
            ordenes = data.data;
        }
        
        console.log('Órdenes procesadas:', ordenes.length);
        renderTablaOrdenes(ordenes);
    } catch (error) {
        console.error('Error cargando órdenes:', error);
        Utils.showMessage(error.message || "No fue posible cargar las órdenes de servicio.", true);
        renderTablaOrdenes([]);
    }
}

async function cargarReparacionesAsignadas() {
    try {
        console.log('Cargando reparaciones asignadas desde:', CONFIG.API.REPARACIONES_ASIGNADAS);
        
        const data = await Utils.fetchJson(CONFIG.API.REPARACIONES_ASIGNADAS, { 
            method: "POST",
            body: JSON.stringify({})
        });
        
        console.log('Respuesta de la API reparaciones:', data);
        
        let reparaciones = [];
        if (Array.isArray(data)) {
            reparaciones = data;
        } else if (data?.reparaciones && Array.isArray(data.reparaciones)) {
            reparaciones = data.reparaciones;
        } else if (data?.data && Array.isArray(data.data)) {
            reparaciones = data.data;
        }
        
        console.log('Reparaciones procesadas:', reparaciones.length);
        renderTablaReparaciones(reparaciones);
    } catch (error) {
        console.error('Error cargando reparaciones:', error);
        Utils.showMessage(error.message || "No fue posible cargar las reparaciones asignadas.", true);
        renderTablaReparaciones([]);
    }
}

async function verDetalleOrden(idOrden) {
    console.log(`Consultando datos combinados para la orden: ${idOrden}`);
   
    
    const infoContainer = document.getElementById("order-info");
    const testsContainer = document.getElementById("order-tests");
    const subtitleContainer = document.getElementById("detalle-orden-subtitle");
    
    try {
        const data = await Utils.fetchJson(CONFIG.API.CONSULTAR_ORDEN, {
            method: "POST",
            body: JSON.stringify({ id_orden: idOrden })
        });
        
        console.log('Datos combinados del backend:', data);
        
        const orden = data.orden;
        const listaTests = data.tests || [];
        
        let ultimoNumeroTest = 0;
        if (listaTests.length > 0) {
            ultimoNumeroTest = Math.max(...listaTests.map(t => parseInt(t.Numero_test) || 0));
        }
        const proximoNumeroTest = ultimoNumeroTest + 1;

        if (infoContainer && orden) {
            const estadoOrden = orden.Estado_orden_servicio || orden.Estado || "Desconocido";
            const estadoClase = Utils.getEstadoClase(estadoOrden);
            
            const descripcionTexto = orden.Descripcion_reparacion || "Sin descripción de reparación registrada.";
            const notaTexto = orden.Nota_orden_servicio || "Ninguna nota adicional.";
            
            const estiloCajaUnificada = `
                background: #f8f9fa; 
                color: #212529; 
                padding: 0.85rem; 
                border-radius: 6px; 
                border: 1px solid #dee2e6; 
                font-size: 0.9rem; 
                line-height: 1.5;
                min-height: 60px;
            `;
            
            infoContainer.innerHTML = `
                <div class="detail-group">
                    <span class="detail-label">ID de la Orden:</span>
                    <strong class="detail-value">#${Utils.escapeHtml(orden.ID_orden_servicio || idOrden)}</strong>
                </div>
                <div class="detail-group">
                    <span class="detail-label">Estado:</span>
                    <span class="estado-badge ${estadoClase}">${Utils.escapeHtml(estadoOrden)}</span>
                </div>
                <div class="detail-group">
                    <span class="detail-label">Cliente:</span>
                    <strong class="detail-value">${Utils.escapeHtml(orden.nombre_cliente || 'No especificado')}</strong>
                </div>
                <div class="detail-group">
                    <span class="detail-label">Modelo del Equipo:</span>
                    <strong class="detail-value">${Utils.escapeHtml(orden.Modelo || 'No especificado')}</strong>
                </div>
                
                <div class="detail-group field--full" style="grid-column: span 2; margin-top: 1rem;">
                    <span class="detail-label" style="display: block; margin-bottom: 0.35rem; font-weight: 600; color: #495057;">Descripción de la Reparación:</span>
                    <div class="detail-value-box" style="${estiloCajaUnificada}">
                        ${Utils.escapeHtml(descripcionTexto)}
                    </div>
                </div>
                
                <div class="detail-group field--full" style="grid-column: span 2; margin-top: 1rem;">
                    <span class="detail-label" style="display: block; margin-bottom: 0.35rem; font-weight: 600; color: #495057;">Nota de la Orden:</span>
                    <div class="detail-value-box" style="${estiloCajaUnificada}">
                        ${Utils.escapeHtml(notaTexto)}
                    </div>
                </div>
            `;
        }
        
        const contenedorDetalleDispositivo = document.getElementById("detalle-dispositivo");
        if (contenedorDetalleDispositivo) {
            const botonAntiguo = document.getElementById("btn-realizar-revision-container");
            if (botonAntiguo) botonAntiguo.remove();

            const divAcciones = document.createElement("div");
            divAcciones.id = "btn-realizar-revision-container";
            divAcciones.style.cssText = "display: flex; justify-content: flex-end; width: 100%; margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #e9ecef;";
            
            divAcciones.innerHTML = `
                <button type="button" 
                        class="form-btn form-btn--primary" 
                        id="btn-realizar-revision"
                        data-id-orden="${idOrden}" 
                        data-proximo-test="${proximoNumeroTest}"
                        style="padding: 0.7rem 1.5rem; font-weight: 600; display: flex; align-items: center; gap: 8px; min-width: 220px; justify-content: center;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                    Realizar revisión
                </button>
            `;
            
            contenedorDetalleDispositivo.appendChild(divAcciones);

            document.getElementById("btn-realizar-revision").addEventListener("click", (e) => {
                const btn = e.currentTarget;
                const id = btn.getAttribute("data-id-orden");
                const numTest = btn.getAttribute("data-proximo-test");
                ejecutarAccionIrARevision(id, numTest);
            });
        }
        
        if (testsContainer) {
            if (listaTests.length === 0) {
                testsContainer.innerHTML = `
                    <h3 class="card__subtitle" style="margin-top: 2rem; margin-bottom: 0.5rem;">Tests Realizados</h3>
                    <p class="device-detail__empty">Esta orden no tiene ningún test registrado todavía.</p>
                `;
            } else {
                const filasHtml = listaTests.map((test) => {
                    const numTest = Utils.escapeHtml(test.Numero_test);
                    const cantidad = Utils.escapeHtml(test.cantidad);
                    
                    return `
                        <tr>
                            <td data-label="Número de Test" style="font-weight: 600; color: #495057;">Test #${numTest}</td>
                            <td data-label="Cantidad de Interacciones">${cantidad}</td>
                            <td data-label="Acción" class="table__actions">
                                <button type="button" class="table-action" data-accion="ver-test" data-id-test="${numTest}" data-id-orden="${idOrden}">Ver</button>
                            </td>
                        </tr>
                    `;
                }).join("");

                testsContainer.innerHTML = `
                    <h3 class="card__subtitle" style="margin-top: 2rem; margin-bottom: 0.75rem; font-weight: 600; color: #212529;">Tests</h3>
                    <div class="table-wrap" style="box-shadow: none; border: 1px solid #dee2e6; border-radius: 6px;">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Número de test</th>
                                    <th>Cantidad</th>
                                    <th class="table__actions">Acción</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${filasHtml}
                            </tbody>
                        </table>
                    </div>
                `;
            }
        }

        if (subtitleContainer) {
            subtitleContainer.textContent = `Visualizando la información completa de la orden #${idOrden}`;
        }
        
        activateView('vista-2');

    } catch (error) {
        console.error('Error al consultar la orden y tests en el servidor:', error);
        Utils.showMessage(error.message || "No se pudo obtener la información completa.", true);
    }
}

async function verDetallesDeUnTest(idOrden, numeroTest) {
    const modalBody = document.getElementById("modal-test-body");
    if (!modalBody) return;

    modalBody.innerHTML = `<p style="text-align:center; width:100%; grid-column: span 4; padding: 2rem;">Cargando componentes del test...</p>`;
    
    if (window.UiModal && typeof window.UiModal.openById === 'function') {
        window.UiModal.openById('modal-test-detail');
    }

    try {
        const respuesta = await Utils.fetchJson(CONFIG.API.CONSULTAR_TEST, {
            method: "POST",
            body: JSON.stringify({ 
                id_orden: idOrden, 
                numero_test: numeroTest 
            })
        });

        console.log("Datos del test recibidos:", respuesta);

        const itemsTest = Array.isArray(respuesta) ? respuesta : [respuesta];

        if (!itemsTest || itemsTest.length === 0 || !itemsTest[0]) {
            modalBody.innerHTML = `<p style="text-align:center; width:100%; grid-column: span 4; padding: 2rem; color: #6c757d;">No se encontraron registros de componentes para este test.</p>`;
            return;
        }

        modalBody.innerHTML = itemsTest.map((item) => {
            const nombreComponente = item.test || "Componente Desconocido";
            const resultado = item.Resultado_test || "Sin especificar";
            
            const esLargo = resultado.length > 30;
            
            const estiloDinamico = esLargo 
                ? `grid-column: span 4 !important; order: 999 !important; background: #f8f9fa; border-left: 4px solid #28a745;` 
                : `background: #ffffff; order: 0;`;

            return `
                <div class="test-item-card" style="${estiloDinamico}">
                    <span style="display: block; font-size: 0.75rem; text-transform: uppercase; color: #6c757d; font-weight: 700; letter-spacing: 0.5px;">
                        ${Utils.escapeHtml(nombreComponente)}
                    </span>
                    <strong style="display: block; font-size: 0.95rem; color: #212529; margin-top: 0.25rem; word-break: break-word;">
                        ${Utils.escapeHtml(resultado)}
                    </strong>
                </div>
            `;
        }).join("");

    } catch (error) {
        console.error("Error al consultar detalles del test:", error);
        modalBody.innerHTML = `<p style="text-align:center; width:100%; grid-column: span 4; padding: 2rem; color: #dc3545; font-weight: 600;">
            Error al cargar la información: ${Utils.escapeHtml(error.message)}
        </p>`;
    }
}

function ejecutarAccionIrARevision(idOrden, numeroTest) {
    console.log(`Redireccionando a Vista 3 (Revisión) para Orden #${idOrden} y Test #${numeroTest}`);
    
    const inputOrden = document.getElementById("id_orden_servicio_revision");
    const inputTest = document.getElementById("numero_test_revision");

    if (inputOrden) inputOrden.value = idOrden;
    if (inputTest) inputTest.value = numeroTest;

    const spanInfoRevision = document.getElementById("orden-id");
    if (spanInfoRevision) {
        spanInfoRevision.textContent = idOrden;
    }
    
    const testIdSpan = document.getElementById("test-id-form");
    if (testIdSpan) {
        testIdSpan.textContent = numeroTest;
    }
    
    if (typeof activateView === "function") {
        activateView("vista-3");
    } else {
        console.warn("La función activateView no está disponible en el scope.");
    }
    
    
}

function cambiarEstadoOrden(idOrden, estadoActual) {
    console.log(`Cambiar estado de orden: ${idOrden}, estado actual: ${estadoActual}`);
    
    // TODO: Implementar modal de cambio de estado
}

function iniciarReparacion(idOrden) {
    console.log(`Iniciar reparación de orden: ${idOrden}`);
    
    // TODO: Implementar lógica de inicio de reparación
}

// ============================================
// 7. GUARDAR REVISIÓN TÉCNICA
// ============================================

// ============================================
// 7. GUARDAR REVISIÓN TÉCNICA
// ============================================

async function guardarRevisionTecnica(event) {
    event.preventDefault();
    
    console.log('Iniciando guardado de revisión técnica...');
    
    // Obtener los valores básicos
    const idOrden = document.getElementById('id_orden_servicio_revision').value;
    const numeroTest = document.getElementById('numero_test_revision').value;
    const observaciones = document.querySelector('textarea[name="observaciones"]').value;
    
    // Validar campos requeridos
    if (!idOrden) {
        Utils.showMessage('No se ha seleccionado una orden de servicio', true);
        return;
    }
    
    if (!numeroTest) {
        Utils.showMessage('Número de test no válido', true);
        return;
    }
    
    // Obtener el ID del empleado (técnico actual)
    const idEmpleado = Utils.obtenerIdEmpleadoActual();
    
    if (!idEmpleado) {
        Utils.showMessage('No se pudo identificar al técnico', true);
        return;
    }
    
    console.log(`ID Empleado: ${idEmpleado}, ID Orden: ${idOrden}, Test #: ${numeroTest}`);
    console.log(`Observaciones: ${observaciones}`);  // Debug
    
    // Construir el array de componentes evaluados
    const componentesEvaluados = [];
    
    // Seleccionar todos los radio buttons que están marcados
    const radiosMarcados = document.querySelectorAll('#form-revision-tecnica input[type="radio"]:checked');
    
    console.log(`Radios marcados encontrados: ${radiosMarcados.length}`);
    
    radiosMarcados.forEach(radio => {
        // Obtener el nombre del componente del atributo data-label o del name
        let nombreComponente = radio.getAttribute('data-label');
        if (!nombreComponente) {
            // Si no tiene data-label, limpiar el nombre del campo
            nombreComponente = radio.name.replace('test_', '').replace(/_/g, ' ');
        }
        const resultado = radio.value;
        
        componentesEvaluados.push({
            nombre: nombreComponente,
            resultado: resultado
        });
    });
    
    // AGREGAR LAS OBSERVACIONES COMO UN COMPONENTE MÁS
    if (observaciones && observaciones.trim() !== '') {
        componentesEvaluados.push({
            nombre: 'Observaciones',
            resultado: observaciones.trim()
        });
    }
    
    // Validar que se haya evaluado al menos un componente
    if (componentesEvaluados.length === 0) {
        Utils.showMessage('Debes evaluar al menos un componente del dispositivo', true);
        return;
    }
    
    console.log('Componentes evaluados (incluyendo observaciones):', componentesEvaluados);
    
    // Preparar el payload
    const payload = {
        id_orden: idOrden,
        id_empleado: parseInt(idEmpleado),
        numero_test: parseInt(numeroTest),
        componentes_evaluados: componentesEvaluados  // Aquí ya están incluidas las observaciones
    };
    
    console.log('Payload completo a enviar:', payload);
    
    try {
        Utils.showMessage('Guardando revisión técnica...');
        
        const response = await Utils.fetchJson(CONFIG.API.GUARDAR_REVISION, {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        
        console.log('Respuesta del servidor:', response);
        Utils.showMessage(response.mensaje || 'Revisión guardada exitosamente');
        
        // Limpiar el formulario
        const formulario = document.getElementById('form-revision-tecnica');
        if (formulario) {
            formulario.reset();
        }
        
        // Opcional: Volver a la vista de detalle de la orden
        setTimeout(() => {
            activateView('vista-2');
            // Recargar los detalles de la orden para mostrar el nuevo test
            verDetalleOrden(idOrden);
        }, 1500);
        
    } catch (error) {
        console.error('Error al guardar la revisión:', error);
        Utils.showMessage(error.message || 'Error al guardar la revisión técnica', true);
    }
}

// ============================================
// 8. EVENTOS E INICIALIZACIÓN
// ============================================
document.addEventListener("DOMContentLoaded", () => {
    console.log('DOM cargado - Inicializando taller.js');
    
    const tablaOrdenes = document.getElementById("tabla-ordenes-servicio");
    const tablaReparaciones = document.getElementById("tabla-reparaciones-asignadas");
    const contenedorTests = document.getElementById("order-tests");

    inicializarCambioVistas();

    if (tablaOrdenes) {
        tablaOrdenes.addEventListener("click", (event) => {
            const button = event.target.closest("button[data-accion]");
            if (!button) return;

            const accion = button.getAttribute("data-accion");
            const idOrden = button.getAttribute("data-id");

            console.log(`Acción en tabla órdenes: ${accion}, ID: ${idOrden}`);

            if (accion === "ver") {
                verDetalleOrden(idOrden);
            } else if (accion === "cambiar-estado") {
                const estadoActual = button.getAttribute("data-estado");
                cambiarEstadoOrden(idOrden, estadoActual);
            }
        });
    }

    if (tablaReparaciones) {
        tablaReparaciones.addEventListener("click", (event) => {
            const button = event.target.closest("button[data-accion]");
            if (!button) return;

            const accion = button.getAttribute("data-accion");
            const idOrden = button.getAttribute("data-id");

            console.log(`Acción en tabla reparaciones: ${accion}, ID: ${idOrden}`);

            if (accion === "ver") {
                verDetalleOrden(idOrden);
            } else if (accion === "iniciar-reparacion") {
                iniciarReparacion(idOrden);
            }
        });
    }

    if (contenedorTests) {
        contenedorTests.addEventListener("click", (event) => {
            const button = event.target.closest("button[data-accion='ver-test']");
            if (!button) return;

            const numTest = button.getAttribute("data-id-test");
            const idOrden = button.getAttribute("data-id-orden");

            console.log(`Abriendo detalles del Test #${numTest} para la Orden: ${idOrden}`);
            
            verDetallesDeUnTest(idOrden, numTest);
        });
    }
    
    // ============================================
    // AGREGAR EVENT LISTENER PARA EL FORMULARIO DE REVISIÓN
    // ============================================
    const formularioRevision = document.getElementById('form-revision-tecnica');
    if (formularioRevision) {
        console.log('Formulario de revisión encontrado, agregando event listener');
        formularioRevision.addEventListener('submit', guardarRevisionTecnica);
    } else {
        console.warn('No se encontró el formulario de revisión');
    }

    activateView("vista-1");
});