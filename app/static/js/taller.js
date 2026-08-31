// ============================================
// TALLER.JS - Versión Completa con Iconos SVG y QR
// ============================================

// --------------------------------
// 1. CONFIGURACIÓN GLOBAL
// --------------------------------
const TALLER_CONFIG = {
    API: {
        ORDENES: '/api/taller/ordenes',
        REPARACIONES_ASIGNADAS: '/api/taller/reparaciones-asignadas',
        CONSULTAR_ORDEN: '/api/taller/consultar-ordene',
        CONSULTAR_TEST: '/api/taller/consultar-test',
        GUARDAR_REVISION: '/api/taller/guardar-revision',
        ASIGNAR_ORDEN: '/api/taller/asignar-orden',
        LIBERAR_ORDEN: '/api/taller/liberar-orden',
        GUARDAR_REPARACION: '/api/taller/guardar-reparacion',
        CONSULTAR_INVENTARIO: '/api/taller/consultar-inventario',
        REGISTRAR_FOTOS: '/api/taller/registrar-fotos',
        ELIMINAR_FOTO: '/api/taller/eliminar-fotos',
        CREAR_TOKEN_FOTOS: '/api/taller_celular/crear-token/{id}'
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
// 2. ICONOS SVG - CONSTANTES
// --------------------------------
const ICON_EYE = `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path d="M12 5c-7 0-10 7-10 7s3 7 10 7 10-7 10-7-3-7-10-7Zm0 12a5 5 0 1 1 0-10 5 5 0 0 1 0 10Zm0-2.7a2.3 2.3 0 1 0 0-4.6 2.3 2.3 0 0 0 0 4.6Z" fill="currentColor"/>
    </svg>`;

const ICON_TRASH = `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path d="M9 3h6l1 2h4v2H4V5h4l1-2Zm1 6h2v9h-2V9Zm4 0h2v9h-2V9ZM7 9h2v9H7V9Z" fill="currentColor"/>
    </svg>`;

const ICON_CHECK_GREEN = `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" fill="currentColor"/>
    </svg>`;

const ICON_WRENCH = `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1-.1-1.4z" fill="currentColor"/>
    </svg>`;

const ICON_CAMERA = `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="16" height="16">
        <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="12" cy="13" r="4" fill="none" stroke="currentColor" stroke-width="2"/>
    </svg>`;

const ICON_INVENTORY = `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="16" height="16">
        <rect x="2" y="7" width="20" height="14" rx="2" ry="2" fill="none" stroke="currentColor" stroke-width="2"/>
        <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" fill="none" stroke="currentColor" stroke-width="2"/>
    </svg>`;

const ICON_CLEAN = `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="16" height="16">
        <path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M10 11v6M14 11v6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`;

const ICON_SAVE = `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="16" height="16">
        <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <polyline points="17 21 17 13 7 13 7 21" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <polyline points="7 3 7 8 15 8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`;

const ICON_CANCEL = `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="16" height="16">
        <line x1="18" y1="6" x2="6" y2="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="6" y1="6" x2="18" y2="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    </svg>`;

const ICON_PHONE = `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="16" height="16">
        <rect x="5" y="2" width="14" height="20" rx="2" ry="2" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="12" y1="18" x2="12" y2="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    </svg>`;

const ICON_COPY = `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="14" height="14">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2" fill="none" stroke="currentColor" stroke-width="2"/>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" fill="none" stroke="currentColor" stroke-width="2"/>
    </svg>`;

const ICON_CLOSE = `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" width="14" height="14">
        <line x1="18" y1="6" x2="6" y2="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="6" y1="6" x2="18" y2="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    </svg>`;

// --------------------------------
// 3. UTILIDADES
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
        if (str === undefined || str === null) return '';
        const text = String(str);
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    showMessage(message, isError = false) {
        if (!message) return;
        console[isError ? 'error' : 'log'](message);
        if (isError) {
            console.log(`❌ Error: ${message}`);
        } else {
            console.log(`✅ ${message}`);
        }
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
        const estadoStr = String(estado || '').toLowerCase().trim();
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
// 4. GESTOR DE VISTAS
// --------------------------------
const ViewManager = {
    currentView: TALLER_CONFIG.VISTAS.ORDENES,
    
    labels: {
        [TALLER_CONFIG.VISTAS.ORDENES]: 'Órdenes de servicio',
        [TALLER_CONFIG.VISTAS.DETALLE]: 'Información de la orden',
        [TALLER_CONFIG.VISTAS.REVISION]: 'Revisión',
        [TALLER_CONFIG.VISTAS.REPARACION]: 'Reparación',
        [TALLER_CONFIG.VISTAS.ASIGNADAS]: 'Reparaciones asignadas'
    },

    activate(targetClass) {
        console.log('Activando vista:', targetClass);
        
        const showBreadcrumb = [TALLER_CONFIG.VISTAS.DETALLE, TALLER_CONFIG.VISTAS.REVISION, 
                                 TALLER_CONFIG.VISTAS.REPARACION, TALLER_CONFIG.VISTAS.ASIGNADAS].includes(targetClass);
        
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
        
        if (targetClass === TALLER_CONFIG.VISTAS.ORDENES) {
            OrdenesService.cargar();
        } else if (targetClass === TALLER_CONFIG.VISTAS.ASIGNADAS) {
            ReparacionesService.cargarAsignadas();
        } else if (targetClass === TALLER_CONFIG.VISTAS.REVISION) {
            const ordenActual = OrdenesService.obtenerOrdenActual();
            if (ordenActual) {
                document.getElementById('orden-id').textContent = ordenActual;
                document.getElementById('id_orden_servicio_revision').value = ordenActual;
            }
            RevisionService.iniciar();
        } else if (targetClass === TALLER_CONFIG.VISTAS.REPARACION) {
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
        this.activate(TALLER_CONFIG.VISTAS.ORDENES);
    }
};

// ============================================
// 5. SERVICIO DE FOTOS (COMPLETO)
// ============================================
const FotosService = {
    fotosSeleccionadas: [],
    ordenIdActual: null,

    iniciarModal(ordenId) {
        this.ordenIdActual = ordenId;
        this.fotosSeleccionadas = [];
        const previewContainer = document.getElementById('fotos-preview');
        const fileInput = document.getElementById('fotos-input');
        const btnSubir = document.getElementById('btn-subir-fotos');
        
        if (previewContainer) previewContainer.innerHTML = '';
        if (btnSubir) btnSubir.disabled = true;
        if (fileInput) fileInput.value = '';
        
        this.configurarDragDrop();
        this.configurarFileInput();
    },

    configurarDragDrop() {
        const dropzone = document.getElementById('photo-dropzone');
        if (!dropzone) return;

        // Bindear una sola vez y guardar la referencia: .bind() devuelve una
        // función nueva en cada llamada, por lo que removeEventListener solo
        // funciona si se usa exactamente la misma referencia que se agregó.
        this.handleDragOver = this.handleDragOver.bind(this);
        this.handleDragLeave = this.handleDragLeave.bind(this);
        this.handleDrop = this.handleDrop.bind(this);

        dropzone.removeEventListener('dragover', this.handleDragOver);
        dropzone.removeEventListener('dragleave', this.handleDragLeave);
        dropzone.removeEventListener('drop', this.handleDrop);

        dropzone.addEventListener('dragover', this.handleDragOver);
        dropzone.addEventListener('dragleave', this.handleDragLeave);
        dropzone.addEventListener('drop', this.handleDrop);
    },

    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        const dropzone = document.getElementById('photo-dropzone');
        if (dropzone) dropzone.classList.add('dragover');
    },

    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        const dropzone = document.getElementById('photo-dropzone');
        if (dropzone) dropzone.classList.remove('dragover');
    },

    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        const dropzone = document.getElementById('photo-dropzone');
        if (dropzone) dropzone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            this.procesarArchivos(files);
        }
    },

    configurarFileInput() {
        const dropzone = document.getElementById('photo-dropzone');
        const fileInput = document.getElementById('fotos-input');
        
        if (!dropzone || !fileInput) return;
        
        dropzone.removeEventListener('click', this.handleDropzoneClick);
        fileInput.removeEventListener('change', this.handleFileChange);
        
        this.handleDropzoneClick = this.handleDropzoneClick.bind(this);
        dropzone.addEventListener('click', this.handleDropzoneClick);
        
        this.handleFileChange = this.handleFileChange.bind(this);
        fileInput.addEventListener('change', this.handleFileChange);
    },

    handleDropzoneClick(e) {
        if (e.target.tagName === 'INPUT') return;
        const fileInput = document.getElementById('fotos-input');
        if (fileInput) {
            fileInput.click();
        }
    },

    handleFileChange(e) {
        const files = e.target.files;
        if (files && files.length > 0) {
            this.procesarArchivos(files);
        }
        e.target.value = '';
    },

    procesarArchivos(files) {
        const validExtensions = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'];
        let archivosValidos = 0;
        
        for (const file of files) {
            if (!validExtensions.includes(file.type)) {
                Utils.showMessage(`❌ Formato no soportado: ${file.name}`, true);
                continue;
            }
            
            if (file.size > 10 * 1024 * 1024) {
                Utils.showMessage(`❌ Archivo demasiado grande: ${file.name} (máx 10MB)`, true);
                continue;
            }
            
            const existe = this.fotosSeleccionadas.some(f => f.name === file.name && f.size === file.size);
            if (existe) {
                Utils.showMessage(`⚠️ "${file.name}" ya está en la lista`, true);
                continue;
            }
            
            const reader = new FileReader();
            reader.onload = (e) => {
                this.fotosSeleccionadas.push({
                    name: file.name,
                    size: file.size,
                    type: file.type,
                    dataUrl: e.target.result,
                    file: file
                });
                this.renderizarPrevisualizacion();
                this.actualizarBotonSubir();
            };
            reader.readAsDataURL(file);
            archivosValidos++;
        }
        
        if (archivosValidos === 0) {
            Utils.showMessage('⚠️ No se seleccionaron archivos válidos', true);
        }
    },

    renderizarPrevisualizacion() {
        const container = document.getElementById('fotos-preview');
        if (!container) return;
        
        if (this.fotosSeleccionadas.length === 0) {
            container.innerHTML = '';
            return;
        }
        
        container.innerHTML = this.fotosSeleccionadas.map((foto, index) => `
            <div class="photo-preview-item" data-index="${index}">
                <img src="${Utils.escapeHtml(foto.dataUrl)}" alt="${Utils.escapeHtml(foto.name)}" loading="lazy">
                <button type="button" class="preview-remove-btn" data-remover-foto="${index}" aria-label="Eliminar foto de la lista">
                    ✕
                </button>
                <span class="preview-file-name">${Utils.escapeHtml(foto.name)}</span>
            </div>
        `).join('');
        
        container.querySelectorAll('[data-remover-foto]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const index = parseInt(btn.getAttribute('data-remover-foto'));
                this.eliminarFotoSeleccionada(index);
            });
        });
    },

    eliminarFotoSeleccionada(index) {
        if (index >= 0 && index < this.fotosSeleccionadas.length) {
            const fotoEliminada = this.fotosSeleccionadas[index];
            this.fotosSeleccionadas.splice(index, 1);
            this.renderizarPrevisualizacion();
            this.actualizarBotonSubir();
            Utils.showMessage(`📸 "${fotoEliminada.name}" eliminada de la lista`);
        }
    },

    actualizarBotonSubir() {
        const btnSubir = document.getElementById('btn-subir-fotos');
        if (btnSubir) {
            btnSubir.disabled = this.fotosSeleccionadas.length === 0;
        }
    },

    async subirFotos() {
        if (this.fotosSeleccionadas.length === 0) {
            Utils.showMessage('No hay fotos para subir', true);
            return;
        }
        
        if (!this.ordenIdActual) {
            Utils.showMessage('No hay una orden seleccionada', true);
            return;
        }
        
        const btnSubir = document.getElementById('btn-subir-fotos');
        const originalText = btnSubir?.textContent || 'Subir fotos';
        
        try {
            if (btnSubir) {
                btnSubir.disabled = true;
                btnSubir.textContent = '⏳ Subiendo...';
            }
            
            const formData = new FormData();
            formData.append('id_orden', this.ordenIdActual);
            
            for (const foto of this.fotosSeleccionadas) {
                formData.append('fotos', foto.file);
            }
            
            const csrfToken = Utils.getCsrfToken();
            const accessToken = Utils.getAccessToken();
            
            const response = await fetch('/api/taller/registrar-fotos', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-CSRF-Token': csrfToken,
                    'Authorization': `Bearer ${accessToken}`
                },
                body: formData,
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Error al subir fotos');
            }
            
            Utils.showMessage(`✅ ${data.mensaje || 'Fotos subidas exitosamente'}`);
            
            this.fotosSeleccionadas = [];
            this.renderizarPrevisualizacion();
            this.actualizarBotonSubir();
            
            if (window.UiModal && typeof window.UiModal.close === 'function') {
                window.UiModal.close();
            }
            
            if (this.ordenIdActual) {
                OrdenesService.verDetalle(this.ordenIdActual);
            }
            
        } catch (error) {
            console.error('Error al subir fotos:', error);
            Utils.showMessage(`❌ Error: ${error.message}`, true);
        } finally {
            if (btnSubir) {
                btnSubir.disabled = false;
                btnSubir.textContent = originalText;
            }
        }
    }
};

// ============================================
// 6. SERVICIO DE ÓRDENES
// ============================================
const OrdenesService = {
    ordenActualId: null,

    async cargar() {
        const tbody = document.getElementById('tabla-ordenes-servicio');
        if (!tbody) return;

        try {
            const data = await Utils.fetchJson(TALLER_CONFIG.API.ORDENES, { method: 'GET' });
            const ordenes = Array.isArray(data) ? data : data?.ordenes || data?.data || [];
            this.renderizar(ordenes, tbody);
        } catch (error) {
            console.error('Error cargando órdenes:', error);
            this.renderizar([], tbody);
        }
    },

    renderizar(ordenes, tbody) {
        if (!ordenes.length) {
            tbody.innerHTML = '<tr><td colspan="7" class="cell-center">No hay órdenes de servicio</td></tr>';
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
                        <button class="icon-action" type="button" data-accion="ver-orden" data-id="${orden.id_orden}" aria-label="Ver orden">${ICON_EYE}</button>
                        <button class="icon-action" type="button" data-accion="tomar-orden" data-id="${orden.id_orden}" aria-label="Tomar orden">${ICON_CHECK_GREEN}</button>
                    </div>
                </td>
            </tr>
        `).join('');
    },

    async verOrdenPreview(idOrden) {
        const modalBodyInfo = document.getElementById('modal-order-info');
        const modalBodyTests = document.getElementById('modal-order-tests');
        const modalBodyFotos = document.getElementById('modal-order-photos');
        const tomarOrdenBtn = document.getElementById('modal-tomar-orden-btn');
        
        if (!modalBodyInfo) return;

        modalBodyInfo.innerHTML = '<p class="device-detail__empty">Cargando información de la orden...</p>';
        modalBodyTests.innerHTML = '';
        if (modalBodyFotos) modalBodyFotos.innerHTML = '';
        
        if (window.UiModal && typeof window.UiModal.openById === 'function') {
            window.UiModal.openById('modal-preview-orden');
        }

        if (tomarOrdenBtn) {
            tomarOrdenBtn.setAttribute('data-id', idOrden);
        }

        try {
            const data = await Utils.fetchJson(TALLER_CONFIG.API.CONSULTAR_ORDEN, {
                method: 'POST',
                body: JSON.stringify({ id_orden: idOrden })
            });

            const orden = data.orden;
            const tests = data.tests || [];
            const fotos = data.fotos || [];

            if (orden) {
                this.renderizarDetalleModal(modalBodyInfo, orden);
            } else {
                modalBodyInfo.innerHTML = '<p class="device-detail__empty error">No se encontró información de la orden</p>';
            }

            if (modalBodyFotos) {
                if (fotos && fotos.length > 0) {
                    this.renderizarFotosModal(modalBodyFotos, fotos);
                } else {
                    modalBodyFotos.innerHTML = '<p class="device-detail__empty">No hay fotos registradas</p>';
                }
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
            if (modalBodyFotos) modalBodyFotos.innerHTML = '';
        }
    },

    renderizarDetalleModal(container, orden) {
        container.innerHTML = `
            <div class="detail-group"><span class="detail-label">ID de la Orden:</span><strong>#${Utils.escapeHtml(orden.ID_orden_servicio)}</strong></div>
            <div class="detail-group"><span class="detail-label">Estado:</span><span class="estado-badge ${Utils.getEstadoClase(orden.Estado_orden_servicio)}">${Utils.escapeHtml(orden.Estado_orden_servicio)}</span></div>
            <div class="detail-group"><span class="detail-label">Cliente:</span><strong>${Utils.escapeHtml(orden.nombre_cliente)}</strong></div>
            <div class="detail-group"><span class="detail-label">Modelo:</span><strong>${Utils.escapeHtml(orden.Modelo)}</strong></div>
            <div class="detail-group field--full"><span class="detail-label">Descripción:</span><div class="detail-value">${Utils.escapeHtml(orden.Descripcion_reparacion || 'Sin descripción')}</div></div>
            <div class="detail-group field--full"><span class="detail-label">Nota:</span><div class="detail-value">${Utils.escapeHtml(orden.Nota_orden_servicio || 'Ninguna nota')}</div></div>
        `;
    },

    renderizarFotosModal(container, fotos) {
        if (!fotos || !fotos.length) {
            container.innerHTML = '<p class="device-detail__empty">No hay fotos registradas para esta orden.</p>';
            return;
        }

        container.innerHTML = `
            <h3 class="card__subtitle">Fotos del dispositivo</h3>
            <div class="fotos-grid">
                ${fotos.map((foto, index) => {
                    const fotoUrl = foto.Foto_orden_servicio || foto.Url_foto || foto.Ruta_foto || foto.url || '';
                    return `
                        <div class="foto-item" data-foto-index="${index}">
                            <div class="foto-thumbnail">
                                <img src="${Utils.escapeHtml(fotoUrl)}"
                                     alt="Foto ${index + 1}"
                                     loading="lazy"
                                     data-foto-url="${Utils.escapeHtml(fotoUrl)}"
                                     title="Clic para ampliar">
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
        this.configurarZoomFotos(container);
    },

    renderizarTestsModal(container, tests, idOrden) {
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
                                    <button class="icon-action" data-accion="ver-test-modal" data-id-test="${Utils.escapeHtml(test.Numero_test)}" data-id-orden="${idOrden}" aria-label="Ver detalles">${ICON_EYE}</button>
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
        const fotosContainer = document.getElementById('order-photos');
        const subtitle = document.getElementById('detalle-orden-subtitle');
        
        try {
            const data = await Utils.fetchJson(TALLER_CONFIG.API.CONSULTAR_ORDEN, {
                method: 'POST',
                body: JSON.stringify({ id_orden: idOrden })
            });

            const orden = data.orden;
            const tests = data.tests || [];
            const fotos = data.fotos || [];

            if (infoContainer && orden) {
                this.renderizarDetalle(infoContainer, orden);
            }

            if (fotosContainer) {
                if (fotos && fotos.length > 0) {
                    this.renderizarFotos(fotosContainer, fotos, true);
                } else {
                    fotosContainer.innerHTML = '<p class="device-detail__empty">No hay fotos registradas para esta orden</p>';
                }
            }

            if (testsContainer) {
                this.renderizarTests(testsContainer, tests, idOrden);
            }

            if (subtitle) {
                subtitle.textContent = `Visualizando la información completa de la orden #${idOrden}`;
            }

            this.actualizarTitulosVistas(idOrden, orden?.Modelo);
            
            this.asignarEventoBotonRevision();
            
            ViewManager.activate(TALLER_CONFIG.VISTAS.DETALLE);
        } catch (error) {
            console.error('Error al consultar orden:', error);
        }
    },

    async actualizarFotos() {
        const idOrden = this.obtenerOrdenActual();
        if (!idOrden) {
            Utils.showMessage('No hay una orden seleccionada', true);
            return;
        }
        
        const fotosContainer = document.getElementById('order-photos');
        if (!fotosContainer) return;
        
        fotosContainer.innerHTML = `
            <div class="spinner-loading-wrapper">
                <span class="spinner-loading"></span>
                <span>Actualizando fotos...</span>
            </div>
        `;
        
        const btnActualizar = document.getElementById('btn-actualizar-fotos');
        if (btnActualizar) btnActualizar.classList.add('loading');
        
        try {
            const data = await Utils.fetchJson(TALLER_CONFIG.API.CONSULTAR_ORDEN, {
                method: 'POST',
                body: JSON.stringify({ id_orden: idOrden })
            });
            
            const fotos = data.fotos || [];
            
            if (fotos.length > 0) {
                this.renderizarFotos(fotosContainer, fotos, true);
                Utils.showMessage(`✅ ${fotos.length} fotos cargadas`);
            } else {
                fotosContainer.innerHTML = '<p class="device-detail__empty">No hay fotos registradas para esta orden</p>';
                Utils.showMessage('📸 No hay fotos registradas');
            }
        } catch (error) {
            console.error('Error al actualizar fotos:', error);
            fotosContainer.innerHTML = `
                <p class="device-detail__empty error">Error al cargar fotos: ${Utils.escapeHtml(error.message)}</p>
            `;
            Utils.showMessage(`❌ Error: ${error.message}`, true);
        } finally {
            if (btnActualizar) btnActualizar.classList.remove('loading');
        }
    },

    renderizarDetalle(container, orden) {
        container.innerHTML = `
            <div class="detail-group"><span class="detail-label">ID de la Orden:</span><strong>#${Utils.escapeHtml(orden.ID_orden_servicio)}</strong></div>
            <div class="detail-group"><span class="detail-label">Estado:</span><span class="estado-badge ${Utils.getEstadoClase(orden.Estado_orden_servicio)}">${Utils.escapeHtml(orden.Estado_orden_servicio)}</span></div>
            <div class="detail-group"><span class="detail-label">Cliente:</span><strong>${Utils.escapeHtml(orden.nombre_cliente)}</strong></div>
            <div class="detail-group"><span class="detail-label">Modelo:</span><strong>${Utils.escapeHtml(orden.Modelo)}</strong></div>
            <div class="detail-group field--full"><span class="detail-label">Descripción:</span><div class="detail-value">${Utils.escapeHtml(orden.Descripcion_reparacion || 'Sin descripción')}</div></div>
            <div class="detail-group field--full"><span class="detail-label">Nota:</span><div class="detail-value">${Utils.escapeHtml(orden.Nota_orden_servicio || 'Ninguna nota')}</div></div>
        `;
    },

    asignarEventoBotonRevision() {
        const btn = document.getElementById('btn-realizar-revision');
        if (btn) {
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
            newBtn.addEventListener('click', () => {
                ViewManager.activate(TALLER_CONFIG.VISTAS.REVISION);
            });
        }
    },

    renderizarTests(container, tests, idOrden) {
        if (!tests || !tests.length) {
            container.innerHTML = '<p class="device-detail__empty">No hay tests registrados.</p>';
            return;
        }

        container.innerHTML = `
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
                                    <button class="icon-action" data-accion="ver-test" data-id-test="${Utils.escapeHtml(test.Numero_test)}" data-id-orden="${idOrden}" aria-label="Ver detalles">${ICON_EYE}</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    },

    renderizarFotos(container, fotos, showDelete = false) {
        if (!container) return;
        
        if (!fotos || !fotos.length) {
            container.innerHTML = '<p class="device-detail__empty">No hay fotos registradas para esta orden.</p>';
            return;
        }

        container.innerHTML = `
            <div class="fotos-grid">
                ${fotos.map((foto, index) => {
                    const fotoUrl = foto.Foto_orden_servicio || foto.Url_foto || foto.Ruta_foto || foto.url || '';
                    const fotoId = foto.ID_foto_orden_servicio || foto.ID_foto || foto.id || index;
                    return `
                        <div class="foto-item" data-foto-index="${index}">
                            <div class="foto-thumbnail">
                                <img src="${Utils.escapeHtml(fotoUrl)}"
                                     alt="Foto ${index + 1}"
                                     loading="lazy"
                                     data-foto-url="${Utils.escapeHtml(fotoUrl)}"
                                     title="Clic para ampliar">
                                ${showDelete ? `
                                    <button type="button" class="foto-delete-btn"
                                            data-accion="eliminar-foto"
                                            data-id-foto="${Utils.escapeHtml(fotoId)}"
                                            aria-label="Eliminar foto">
                                        ✕
                                    </button>
                                ` : ''}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
        this.configurarZoomFotos(container);

        if (showDelete) {
            container.querySelectorAll('[data-accion="eliminar-foto"]').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const fotoId = btn.getAttribute('data-id-foto');
                    const ordenId = OrdenesService.obtenerOrdenActual();
                    if (fotoId && ordenId) {
                        confirmarEliminarFoto(fotoId, ordenId);
                    }
                });
            });
        }
    },

    configurarZoomFotos(container) {
        if (!container) return;
        container.querySelectorAll('.foto-thumbnail img[data-foto-url]').forEach(img => {
            img.addEventListener('click', () => this.verFotoAmpliada(img.dataset.fotoUrl));
        });
    },

    verFotoAmpliada(url) {
        const existingOverlay = document.querySelector('.foto-modal-overlay');
        if (existingOverlay) existingOverlay.remove();

        const overlay = document.createElement('div');
        overlay.className = 'foto-modal-overlay';
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-modal', 'true');
        overlay.setAttribute('aria-label', 'Foto ampliada');
        overlay.innerHTML = `
            <button type="button" class="close-btn" aria-label="Cerrar">✕</button>
            <img src="${Utils.escapeHtml(url)}" alt="Foto ampliada">
        `;

        const cerrar = () => {
            overlay.remove();
            document.removeEventListener('keydown', onKey);
        };
        const onKey = (e) => {
            if (e.key === 'Escape') cerrar();
        };

        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) cerrar();
        });
        overlay.querySelector('.close-btn').addEventListener('click', cerrar);
        document.addEventListener('keydown', onKey);
        document.body.appendChild(overlay);
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
            
            await Utils.fetchJson(TALLER_CONFIG.API.ASIGNAR_ORDEN, {
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
            
            if (ViewManager.currentView === TALLER_CONFIG.VISTAS.ASIGNADAS) {
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
// 7. SERVICIO DE REVISIONES
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

        this.calcularProximoNumeroTest(ordenId).then(proximoTest => {
            const numeroTestInput = document.getElementById('numero_test_revision');
            const testIdSpan = document.getElementById('test-id-form');
            
            if (numeroTestInput) numeroTestInput.value = proximoTest;
            if (testIdSpan) testIdSpan.textContent = proximoTest;
            
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
            const data = await Utils.fetchJson(TALLER_CONFIG.API.CONSULTAR_ORDEN, {
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
        
        container.innerHTML = TALLER_CONFIG.COMPONENTES_TEST.map(comp => {
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
            await Utils.fetchJson(TALLER_CONFIG.API.GUARDAR_REVISION, {
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
                ViewManager.activate(TALLER_CONFIG.VISTAS.DETALLE);
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
            const data = await Utils.fetchJson(TALLER_CONFIG.API.CONSULTAR_TEST, {
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
// 8. SERVICIO DE REPUESTOS
// --------------------------------
const RepuestosService = {
    repuestosSeleccionados: [],
    inventarioData: [],

    async cargarInventario() {
        const tbody = document.getElementById('tabla-inventario-body');
        if (!tbody) return;

        tbody.innerHTML = '<tr><td colspan="5">Cargando inventario...</td></tr>';
        
        const tablaContainer = document.getElementById('tabla-inventario-repuestos');
        if (tablaContainer) {
            tablaContainer.removeEventListener('click', this.handleInventarioClick);
            tablaContainer.addEventListener('click', this.handleInventarioClick.bind(this));
        }

        try {
            const data = await Utils.fetchJson(TALLER_CONFIG.API.CONSULTAR_INVENTARIO, { method: 'GET' });
            const inventario = Array.isArray(data) ? data : data?.inventario || data?.data || [];
            this.inventarioData = inventario;
            this.renderizarInventario(inventario, tbody);
        } catch (error) {
            console.error('Error cargando inventario:', error);
            tbody.innerHTML = `<tr><td colspan="5" class="texto-error">Error al cargar inventario: ${error.message}</td></tr>`;
        }
    },

    renderizarInventario(inventario, tbody) {
        if (!inventario || !inventario.length) {
            tbody.innerHTML = '<tr><td colspan="5">No hay repuestos disponibles en inventario</td></tr>';
            return;
        }

        tbody.innerHTML = inventario.map(item => {
            const idInventario = item.ID_inventario;
            const nombreProducto = item.Nombre_producto || 'Sin nombre';
            const nombreMarca = item.Nombre_marca || '-';
            const nombreClase = item.Nombre_Clase || '-';
            const existencia = item.Existencia || 0;
            
            const rowClass = existencia > 0 ? 'inventario-row-clickable' : 'inventario-row-sinstock';
            
            return `
                <tr class="${rowClass}" 
                    data-id="${Utils.escapeHtml(idInventario)}"
                    data-nombre="${Utils.escapeHtml(nombreProducto)}"
                    data-existencia="${existencia}">
                    <td data-label="ID">${Utils.escapeHtml(idInventario)}</td>
                    <td data-label="Producto"><strong>${Utils.escapeHtml(nombreProducto)}</strong></td>
                    <td data-label="Marca">${Utils.escapeHtml(nombreMarca)}</td>
                    <td data-label="Clase">${Utils.escapeHtml(nombreClase)}</td>
                    <td data-label="Existencia">
                        <span class="${existencia > 0 ? 'stock-ok' : 'stock-out'}">
                            ${Utils.escapeHtml(existencia)}
                        </span>
                    </td>
                </tr>
            `;
        }).join('');
    },

    obtenerStockDisponible(idInventario) {
        const item = this.inventarioData.find(i => String(i.ID_inventario) === String(idInventario));
        return item ? (item.Existencia || 0) : 0;
    },

    obtenerCantidadSeleccionada(idInventario) {
        const encontrado = this.repuestosSeleccionados.find(r => String(r.id) === String(idInventario));
        return encontrado ? encontrado.cantidad : 0;
    },

    obtenerStockRestante(idInventario) {
        const stockTotal = this.obtenerStockDisponible(idInventario);
        const cantidadSeleccionada = this.obtenerCantidadSeleccionada(idInventario);
        return stockTotal - cantidadSeleccionada;
    },

    handleInventarioClick(event) {
        const row = event.target.closest('tr');
        if (!row) return;
        
        const idInventario = row.getAttribute('data-id');
        const nombreProducto = row.getAttribute('data-nombre');
        const existencia = parseInt(row.getAttribute('data-existencia') || '0');
        
        if (!idInventario || !nombreProducto) return;
        
        if (event.target.hasAttribute('data-processing')) return;
        event.target.setAttribute('data-processing', 'true');
        
        try {
            if (existencia <= 0) {
                Utils.showMessage(`❌ "${nombreProducto}" no tiene stock disponible`, true);
                return;
            }
            
            const stockRestante = this.obtenerStockRestante(idInventario);
            if (stockRestante <= 0) {
                Utils.showMessage(`❌ No queda stock disponible de "${nombreProducto}" para seleccionar`, true);
                return;
            }
            
            this.agregarRepuesto(idInventario, nombreProducto);
        } finally {
            setTimeout(() => {
                event.target.removeAttribute('data-processing');
            }, 300);
        }
    },

    agregarRepuesto(idInventario, nombreProducto) {
        const stockDisponible = this.obtenerStockDisponible(idInventario);
        const existente = this.repuestosSeleccionados.find(r => String(r.id) === String(idInventario));
        
        if (existente) {
            if (existente.cantidad < stockDisponible) {
                existente.cantidad++;
                Utils.showMessage(`📦 Se aumentó la cantidad de "${nombreProducto}" a ${existente.cantidad}`);
            } else {
                Utils.showMessage(`❌ No hay más stock disponible de "${nombreProducto}"`, true);
                return;
            }
        } else {
            this.repuestosSeleccionados.push({
                id: idInventario,
                nombre: nombreProducto,
                cantidad: 1,
                stockMaximo: stockDisponible
            });
            Utils.showMessage(`✅ Repuesto "${nombreProducto}" agregado correctamente`);
        }

        this.renderizarRepuestosUsados();
        this.actualizarContadorTotal();
    },

    renderizarRepuestosUsados() {
        const container = document.getElementById('repuestos-usados-list');
        if (!container) return;

        if (this.repuestosSeleccionados.length === 0) {
            container.innerHTML = `
                <div class="device-detail__empty">
                    No hay repuestos agregados aún.<br />
                    <small>Haz clic en "Inventario de repuestos" para agregar productos.</small>
                </div>
            `;
            const btnLimpiar = document.getElementById('btn-limpiar-repuestos');
            if (btnLimpiar) btnLimpiar.style.display = 'none';
            return;
        }

        const btnLimpiar = document.getElementById('btn-limpiar-repuestos');
        if (btnLimpiar) btnLimpiar.style.display = 'inline-flex';

        container.innerHTML = this.repuestosSeleccionados.map((repuesto, index) => {
            const stockMaximo = this.obtenerStockDisponible(repuesto.id);
            return `
                <div class="repuesto-item" data-repuesto-index="${index}">
                    <div class="repuesto-info">
                        <div class="repuesto-nombre">🔧 ${Utils.escapeHtml(repuesto.nombre)}</div>
                        <div class="repuesto-cantidad-control">
                            <label>Cantidad (máx ${stockMaximo}):</label>
                            <input type="number" 
                                   class="repuesto-cantidad-input" 
                                   data-index="${index}"
                                   data-stock-max="${stockMaximo}"
                                   value="${repuesto.cantidad}" 
                                   min="1" 
                                   max="${stockMaximo}" 
                                   step="1">
                            <span class="repuesto-stock-max">/ ${stockMaximo}</span>
                        </div>
                    </div>
                    <button type="button" class="btn-eliminar-repuesto" data-eliminar-repuesto="${index}">
                        ✖ Eliminar
                    </button>
                </div>
            `;
        }).join('');

        container.querySelectorAll('.repuesto-cantidad-input').forEach(input => {
            input.removeEventListener('change', this.handleCantidadChange);
            input.removeEventListener('input', this.handleCantidadInput);
            input.addEventListener('change', this.handleCantidadChange.bind(this));
            input.addEventListener('input', this.handleCantidadInput.bind(this));
        });

        container.querySelectorAll('.btn-eliminar-repuesto').forEach(btn => {
            btn.removeEventListener('click', this.handleEliminarClick);
            btn.addEventListener('click', this.handleEliminarClick.bind(this));
        });
    },

    handleCantidadInput(event) {
        const input = event.target;
        const stockMax = parseInt(input.getAttribute('data-stock-max') || '0');
        let valor = parseInt(input.value);
        
        if (!isNaN(valor) && valor > stockMax) {
            input.classList.add('error');
        } else {
            input.classList.remove('error');
        }
    },

    handleCantidadChange(event) {
        const input = event.target;
        const index = parseInt(input.getAttribute('data-index'));
        const stockMax = parseInt(input.getAttribute('data-stock-max') || '0');
        let nuevaCantidad = parseInt(input.value);
        
        if (!isNaN(nuevaCantidad) && nuevaCantidad > 0) {
            if (nuevaCantidad > stockMax) {
                Utils.showMessage(`❌ No puedes seleccionar más de ${stockMax} unidades de este repuesto`, true);
                nuevaCantidad = stockMax;
                input.value = stockMax;
            }
            
            if (nuevaCantidad <= 0) {
                nuevaCantidad = 1;
                input.value = 1;
            }
            
            this.repuestosSeleccionados[index].cantidad = nuevaCantidad;
            this.renderizarRepuestosUsados();
            this.actualizarContadorTotal();
            Utils.showMessage(`Cantidad actualizada a ${nuevaCantidad}`);
        } else {
            const cantidadActual = this.repuestosSeleccionados[index]?.cantidad || 1;
            input.value = cantidadActual;
            Utils.showMessage('Cantidad inválida', true);
        }
        
        input.classList.remove('error');
    },

    handleEliminarClick(event) {
        event.stopPropagation();
        const btn = event.target.closest('[data-eliminar-repuesto]');
        if (!btn) return;
        
        const index = parseInt(btn.getAttribute('data-eliminar-repuesto'));
        const repuestoEliminado = this.repuestosSeleccionados[index];
        this.repuestosSeleccionados.splice(index, 1);
        this.renderizarRepuestosUsados();
        this.actualizarContadorTotal();
        Utils.showMessage(`Repuesto "${repuestoEliminado.nombre}" eliminado`);
    },

    actualizarContadorTotal() {
        const totalUnidades = this.repuestosSeleccionados.reduce((sum, r) => sum + r.cantidad, 0);
        const totalCountSpan = document.getElementById('repuestos-total-count');
        if (totalCountSpan) {
            totalCountSpan.textContent = `${totalUnidades} unidad${totalUnidades !== 1 ? 'es' : ''}`;
            totalCountSpan.className = `estado-badge ${totalUnidades > 0 ? 'estado-completado' : 'estado-default'}`;
        }
    },

    limpiar() {
        this.repuestosSeleccionados = [];
        this.renderizarRepuestosUsados();
        this.actualizarContadorTotal();
        Utils.showMessage('Lista de repuestos limpiada');
    },

    obtenerRepuestos() {
        return this.repuestosSeleccionados;
    }
};

// --------------------------------
// 9. SERVICIO DE REPARACIONES
// --------------------------------
const ReparacionesService = {
    async cargarAsignadas() {
        const tbody = document.getElementById('tabla-reparaciones-asignadas');
        if (!tbody) return;

        try {
            const data = await Utils.fetchJson(TALLER_CONFIG.API.REPARACIONES_ASIGNADAS, { 
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
            tbody.innerHTML = '<tr><td colspan="4">Sin reparaciones asignadas por ahora.</td></tr>';
            return;
        }

        tbody.innerHTML = reparaciones.map(rep => `
            <tr>
                <td data-label="ID orden">${Utils.escapeHtml(rep.id_orden)}</td>
                <td data-label="Modelo">${Utils.escapeHtml(rep.modelo)}</td>
                <td data-label="Fecha ingreso">${Utils.formatDate(rep.fecha_e)}</td>
                <td class="table__actions" data-label="Acciones">
                    <div class="row-actions">
                        <button class="icon-action" type="button" data-accion="ver-detalle" data-id="${rep.id_orden}" aria-label="Ver detalle de la orden">${ICON_WRENCH}</button>
                        <button class="icon-action icon-action--danger" type="button" data-accion="liberar-orden" data-id="${rep.id_orden}" aria-label="Liberar orden">${ICON_TRASH}</button>
                    </div>
                </td>
            </tr>
        `).join('');
    },

    verDetalleOrden(idOrden) {
        if (!idOrden) {
            console.warn('No hay ID de orden');
            return;
        }
        
        OrdenesService.verDetalle(idOrden);
    },

    iniciar(idOrden = null) {
        const ordenId = idOrden || OrdenesService.obtenerOrdenActual();
        
        if (!ordenId) {
            console.warn('No hay orden seleccionada');
            return;
        }
        
        RepuestosService.limpiar();
        
        const reparacionOrdenId = document.getElementById('reparacion-orden-id');
        if (reparacionOrdenId) reparacionOrdenId.textContent = ordenId;
        
        const reparacionTextarea = document.getElementById('reparacion-textarea');
        if (reparacionTextarea) reparacionTextarea.value = '';
        
        setTimeout(() => {
            OrdenesService.verDetalle(ordenId);
            ViewManager.activate(TALLER_CONFIG.VISTAS.REPARACION);
        }, 500);
    },

    async liberarOrden(idOrden) {
        try {
            const idEmpleado = Utils.obtenerIdEmpleadoActual();
            
            await Utils.fetchJson(TALLER_CONFIG.API.LIBERAR_ORDEN, {
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
            Utils.showMessage(error.message, true);
        }
    },

    async guardarReparacion() {
        const ordenId = OrdenesService.obtenerOrdenActual();
        const reparacionTexto = document.getElementById('reparacion-textarea')?.value.trim();
        const repuestos = RepuestosService.obtenerRepuestos();
        
        if (!ordenId) {
            Utils.showMessage('No hay una orden seleccionada', true);
            return;
        }
        
        if (!reparacionTexto) {
            Utils.showMessage('Debes describir la reparación realizada', true);
            return;
        }
        
        const regexEspeciales = /[<>{}[\]|\\^]/;
        if (regexEspeciales.test(reparacionTexto)) {
            Utils.showMessage('La descripción no puede contener caracteres especiales como < > { } [ ] | \\ ^', true);
            return;
        }
        
        try {
            const idEmpleado = Utils.obtenerIdEmpleadoActual();
            
            const payload = {
                id_orden: ordenId,
                descripcion_reparacion: reparacionTexto,
                repuestos_utilizados: repuestos.map(r => ({
                    id_inventario: r.id,
                    cantidad: r.cantidad
                }))
            };
            
            await Utils.fetchJson(TALLER_CONFIG.API.GUARDAR_REPARACION, {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            
            Utils.showMessage('✅ Reparación guardada exitosamente');
            
            document.getElementById('reparacion-textarea').value = '';
            RepuestosService.limpiar();
            
            await OrdenesService.cargar();
            await this.cargarAsignadas();
            
            ViewManager.activate(TALLER_CONFIG.VISTAS.ORDENES);
            
        } catch (error) {
            console.error('Error al guardar reparación:', error);
            Utils.showMessage(error.message, true);
        }
    }
};

// ============================================
// 10. FUNCIONALIDAD QR - MODAL
// ============================================

let modalQrCodeInstance = null;

function getQrBaseUrl() {
    const ordenId = OrdenesService.obtenerOrdenActual();
    if (!ordenId) return null;
    return `${window.location.origin}/taller_celular/${ordenId}`;
}

async function getQrUrl() {
    const baseUrl = getQrBaseUrl();
    if (!baseUrl) return null;

    const response = await Utils.fetchJson(
        TALLER_CONFIG.API.CREAR_TOKEN_FOTOS.replace('{id}', OrdenesService.obtenerOrdenActual()),
        { method: 'POST' }
    );

    if (!response || !response.firma) {
        throw new Error('El servidor no devolvió una firma válida. Vuelve a iniciar sesión e intenta de nuevo.');
    }

    return `${baseUrl}?t=${encodeURIComponent(response.firma)}`;
}

async function abrirModalQr() {
    const ordenId = OrdenesService.obtenerOrdenActual();
    if (!ordenId) {
        Utils.showMessage('Primero selecciona una orden en la vista de detalle', true);
        return;
    }
    
    let url;
    try {
        url = await getQrUrl();
    } catch (error) {
        if (window.FeedbackModal && typeof window.FeedbackModal.showError === 'function') {
            window.FeedbackModal.showError(error.message || 'No se pudo generar el QR', 'QR no disponible');
        } else {
            Utils.showMessage('❌ No se pudo generar el QR: ' + (error.message || error), true);
        }
        return;
    }
    if (!url) return;
    
    const qrContainer = document.getElementById('modal-qr-code');
    if (!qrContainer) return;
    qrContainer.innerHTML = '';

    if (window.UiModal && typeof window.UiModal.openById === 'function') {
        window.UiModal.openById('modal-qr-celular');
    }
    
    setTimeout(() => {
        try {
            if (modalQrCodeInstance) {
                try { modalQrCodeInstance.clear(); } catch(e) {}
                modalQrCodeInstance = null;
            }
            
            modalQrCodeInstance = new QRCode(qrContainer, {
                text: url,
                width: 220,
                height: 220,
                colorDark: '#000000',
                colorLight: '#ffffff',
                correctLevel: QRCode.CorrectLevel.H
            });
        } catch (error) {
            console.error('Error al generar QR:', error);
            qrContainer.innerHTML = '<p class="texto-error">Error al generar el código QR</p>';
        }
    }, 200);
}

const btnUsarCelular = document.getElementById('btn-usar-celular');

// ============================================
// 11. MODAL DE CONFIRMACIÓN PARA ELIMINAR FOTO
// ============================================

let fotoAEliminar = null;

function confirmarEliminarFoto(fotoId, ordenId) {
    fotoAEliminar = { id: fotoId, orden: ordenId };
    
    if (window.UiModal && typeof window.UiModal.openById === 'function') {
        window.UiModal.openById('modal-confirm-eliminar');
    } else {
        console.error('UiModal no disponible');
    }
}

function cerrarModalConfirmacion() {
    if (window.UiModal && typeof window.UiModal.close === 'function') {
        window.UiModal.close();
    }
    fotoAEliminar = null;
}

async function eliminarFotoConfirmada() {
    if (!fotoAEliminar) return;
    
    const { id, orden } = fotoAEliminar;
    
    try {
        await Utils.fetchJson(TALLER_CONFIG.API.ELIMINAR_FOTO, {
            method: 'DELETE',
            body: JSON.stringify({ id_foto: id })
        });
        
        Utils.showMessage('✅ Foto eliminada exitosamente');
        
        cerrarModalConfirmacion();
        
        if (orden) {
            OrdenesService.verDetalle(orden);
        }
        
    } catch (error) {
        console.error('Error al eliminar foto:', error);
        Utils.showMessage(`❌ Error: ${error.message}`, true);
        cerrarModalConfirmacion();
    } finally {
        fotoAEliminar = null;
    }
}

// ============================================
// 12. INICIALIZACIÓN Y EVENTOS
// ============================================
document.addEventListener("DOMContentLoaded", () => {
    console.log('DOM cargado - Inicializando taller.js');
    
    ViewManager.init();

    const reparacionTextarea = document.getElementById('reparacion-textarea');
    if (reparacionTextarea) {
        const contadorSpan = document.getElementById('caracteres-contador');
        if (contadorSpan) {
            reparacionTextarea.addEventListener('input', () => {
                const length = reparacionTextarea.value.length;
                contadorSpan.textContent = length;
                if (length >= 450) {
                    contadorSpan.classList.add('warning');
                } else {
                    contadorSpan.classList.remove('warning');
                }
            });
        }
    }

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

            if (accion === "ver-detalle") {
                ReparacionesService.verDetalleOrden(idOrden);
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
            ReparacionesService.guardarReparacion();
        });
    }

    const btnInventarioRepuestos = document.getElementById('btn-inventario-repuestos');
    if (btnInventarioRepuestos) {
        btnInventarioRepuestos.addEventListener('click', async () => {
            if (window.UiModal && typeof window.UiModal.openById === 'function') {
                window.UiModal.openById('modal-inventario-repuestos');
                await RepuestosService.cargarInventario();
            } else {
                console.error('UiModal no disponible');
                Utils.showMessage('Error al abrir el inventario', true);
            }
        });
    }

    const btnLimpiarRepuestos = document.getElementById('btn-limpiar-repuestos');
    if (btnLimpiarRepuestos) {
        btnLimpiarRepuestos.addEventListener('click', () => {
            RepuestosService.limpiar();
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

    document.querySelectorAll('[data-open-modal="modal-fotos-registrar"]').forEach(btn => {
        btn.addEventListener('click', () => {
            const ordenId = OrdenesService.obtenerOrdenActual();
            if (!ordenId) {
                Utils.showMessage('Primero selecciona una orden', true);
                return;
            }
            
            FotosService.iniciarModal(ordenId);
            
            if (window.UiModal && typeof window.UiModal.openById === 'function') {
                window.UiModal.openById('modal-fotos-registrar');
            }
        });
    });

    const btnSubirFotos = document.getElementById('btn-subir-fotos');
    if (btnSubirFotos) {
        btnSubirFotos.addEventListener('click', () => {
            FotosService.subirFotos();
        });
    }

    const btnActualizarFotos = document.getElementById('btn-actualizar-fotos');
    if (btnActualizarFotos) {
        btnActualizarFotos.addEventListener('click', () => {
            OrdenesService.actualizarFotos();
        });
    }

    if (btnUsarCelular) {
        btnUsarCelular.addEventListener('click', (e) => {
            e.preventDefault();
            abrirModalQr();
        });
    }

    document.querySelectorAll('#modal-confirm-eliminar [data-close-modal]').forEach(btn => {
        btn.addEventListener('click', cerrarModalConfirmacion);
    });

    const btnConfirmEliminar = document.getElementById('confirm-eliminar-foto-btn');
    if (btnConfirmEliminar) {
        btnConfirmEliminar.addEventListener('click', async () => {
            await eliminarFotoConfirmada();
        });
    }

    document.querySelectorAll('[data-view-target]').forEach(btn => {
        btn.addEventListener('click', () => {
            if (window.UiModal && typeof window.UiModal.close === 'function') {
                window.UiModal.close();
            }
        });
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modalConfirm = document.getElementById('modal-confirm-eliminar');
            if (modalConfirm && !modalConfirm.hidden) {
                cerrarModalConfirmacion();
            }
        }
    });
});