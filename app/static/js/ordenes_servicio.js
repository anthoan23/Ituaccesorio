// ============================================
// 1. CONSTANTES Y CONFIGURACIÓN
// ============================================
const CONFIG = {
    API: {
        ORDENES_SERVICIO: '/api/ordenes-servicio',
        ORDENES: '/api/ordenes-servicio/ordenes',
        TECNICOS: '/api/ordenes-servicio/tecnicos',
        MODELOS: '/api/ordenes-servicio/modelos',
        CLIENTES: '/api/clientes',
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
            let msg = "";
            if (isJson && payload) {
                msg = payload.message || payload.error || payload.Mensaje || "Error en la solicitud";
            } else {
                msg = String(payload || response.statusText || "Error en la solicitud");
            }
            throw new Error(msg);
        }

        return payload;
    },

    escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    },

    showMessage(message, isError = false) {
        if (!message) return;
        if (isError) {
            console.error(`❌ ${message}`);
        } else {
            console.log(`✅ ${message}`);
        }
    },

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    validarRIF(rif) {
        const patron = /^[JE]-\d{8}-\d$/;
        return patron.test(rif);
    },

    validarRIFEnTiempoReal(input) {
        let errorElement = document.getElementById(input.id + '-error');
        if (!errorElement) {
            errorElement = document.createElement('small');
            errorElement.className = 'field-error';
            errorElement.id = input.id + '-error';
            errorElement.style.display = 'block';
            errorElement.style.marginTop = '0.15rem';
            errorElement.style.fontSize = '0.7rem';
            errorElement.style.fontWeight = '600';
            input.parentElement.appendChild(errorElement);
        }
        
        const valor = input.value;
        
        if (!valor) {
            errorElement.textContent = '';
            errorElement.style.color = '';
            input.classList.remove('field-error', 'field-success');
            input.style.borderColor = '';
            input.style.boxShadow = '';
            return;
        }
        
        const esValido = this.validarRIF(valor);
        
        if (!esValido) {
            errorElement.textContent = '✗ Use J-12345678-9 o E-12345678-9';
            errorElement.style.color = '#ef4444';
            input.classList.add('field-error');
            input.classList.remove('field-success');
            input.style.borderColor = '#ef4444';
            input.style.boxShadow = '0 0 0 2px rgba(239, 68, 68, 0.15)';
        } else {
            errorElement.textContent = '✓ RIF válido';
            errorElement.style.color = '#22c55e';
            input.classList.remove('field-error');
            input.classList.add('field-success');
            input.style.borderColor = '#22c55e';
            input.style.boxShadow = '0 0 0 2px rgba(34, 197, 94, 0.15)';
        }
    },

    formatFecha(value) {
        if (!value) return "";
        const fecha = new Date(value);
        if (Number.isNaN(fecha.getTime())) return value;
        return fecha.toLocaleDateString("es-ES");
    },

    getEstadoBadgeClass(estado) {
        const estadoLower = String(estado ?? "").toLowerCase().trim();
        if (estadoLower.includes("pendient")) return "badge--pendiente";
        if (estadoLower.includes("asign")) return "badge--asignada";
        if (estadoLower.includes("revis")) return "badge--revisada";
        if (estadoLower.includes("repar")) return "badge--reparada";
        return "badge--pendiente";
    },

    getFechaActual() {
        const hoy = new Date();
        return hoy.toISOString().slice(0, 10);
    },

    soloLetras(value) {
        return /^[a-zA-ZáéíóúñÁÉÍÓÚÑ\s]*$/.test(value);
    },

    capitalizarPalabras(texto) {
        if (!texto) return texto;
        const palabras = texto.split(' ');
        return palabras.map(p => {
            if (p.length > 0 && /^[a-zA-ZáéíóúñÁÉÍÓÚÑ]/.test(p)) {
                return p.charAt(0).toUpperCase() + p.slice(1).toLowerCase();
            }
            return p;
        }).join(' ');
    },

    validarTelefonoOrden(telefono) {
        if (!telefono) {
            return { valido: false, mensaje: 'El teléfono es obligatorio' };
        }
        
        const telefonoLimpio = telefono.replace(/\D/g, '');
        
        if (telefonoLimpio.length !== 11) {
            return { 
                valido: false, 
                mensaje: `Debe tener 11 dígitos (actual: ${telefonoLimpio.length})`,
                telefonoLimpio
            };
        }
        
        const prefijo = telefonoLimpio.substring(0, 4);
        const prefijosPermitidos = [
            '0412', '0414', '0416', '0422', '0424', '0426', '0410', '0418', '0420', 
            '0411', '0413', '0415', '0417', '0419', '0212', '0234', '0241', '0243', 
            '0251', '0261', '0271', '0274', '0281', '0283', '0285'
        ];
        
        if (!prefijosPermitidos.includes(prefijo)) {
            return { 
                valido: false, 
                mensaje: `Prefijo "${prefijo}" no permitido.`,
                telefonoLimpio,
                prefijo
            };
        }
        
        return { valido: true, mensaje: 'Teléfono válido', prefijo };
    },

    validarTelefonoOrdenEnTiempoReal(input) {
        let errorElement = document.getElementById(input.id + '-error');
        if (!errorElement) {
            errorElement = document.createElement('small');
            errorElement.className = 'field-error';
            errorElement.id = input.id + '-error';
            errorElement.style.display = 'block';
            errorElement.style.marginTop = '0.15rem';
            errorElement.style.fontSize = '0.7rem';
            errorElement.style.fontWeight = '600';
            input.parentElement.appendChild(errorElement);
        }
        
        const valor = input.value;
        
        if (!valor) {
            errorElement.textContent = '';
            errorElement.style.color = '';
            input.classList.remove('field-error', 'field-success');
            input.style.borderColor = '';
            input.style.boxShadow = '';
            return;
        }
        
        const resultado = this.validarTelefonoOrden(valor);
        
        if (!resultado.valido) {
            errorElement.textContent = '✗ ' + resultado.mensaje;
            errorElement.style.color = '#ef4444';
            input.classList.add('field-error');
            input.classList.remove('field-success');
            input.style.borderColor = '#ef4444';
            input.style.boxShadow = '0 0 0 2px rgba(239, 68, 68, 0.15)';
        } else {
            errorElement.textContent = '✓ ' + resultado.mensaje;
            errorElement.style.color = '#22c55e';
            input.classList.remove('field-error');
            input.classList.add('field-success');
            input.style.borderColor = '#22c55e';
            input.style.boxShadow = '0 0 0 2px rgba(34, 197, 94, 0.15)';
        }
    },

    formatearTelefonoOrden(input) {
        let valor = input.value.replace(/\D/g, '');
        if (valor.length > 11) {
            valor = valor.substring(0, 11);
        }
        input.value = valor;
        this.validarTelefonoOrdenEnTiempoReal(input);
    }
};

// ============================================
// 3. MANEJADORES DE MODALES
// ============================================
function openModal(id) {
    if (window.UiModal && typeof window.UiModal.openById === "function") {
        window.UiModal.openById(id);
        return;
    }
    const modal = document.getElementById(id);
    if (modal) {
        modal.removeAttribute("hidden");
        modal.setAttribute("aria-hidden", "false");
    }
}

function closeModal(id) {
    if (window.UiModal && typeof window.UiModal.closeById === "function") {
        window.UiModal.closeById(id);
        return;
    }
    const modal = document.getElementById(id);
    if (modal) {
        if (modal.contains(document.activeElement)) {
            document.activeElement.blur();
        }
        modal.setAttribute("hidden", "");
        modal.setAttribute("aria-hidden", "true");
    }
}

// ============================================
// 4. VARIABLES GLOBALES
// ============================================
let ordenes = [];
let clienteActualId = null;
let ordenActualId = null;
let testsOrdenActual = [];
let datosOrdenPendiente = null;

// ============================================
// 5. REFERENCIAS DOM
// ============================================
function getDomElements() {
    return {
        tablaOrdenes: document.getElementById("tabla-ordenes"),
        statPendientes: document.getElementById("stat-pendientes"),
        statAsignadas: document.getElementById("stat-asignadas"),
        formOrden: document.getElementById("form-orden-servicio"),
        btnVerificarEquipo: document.getElementById("btn-verificar-equipo"),
        btnVerificarCliente: document.getElementById("btn-verificar-cliente"),
        btnCrearCliente: document.getElementById("btn-crear-cliente"),
        clienteStatus: document.getElementById("cliente-status"),
        equipoStatus: document.getElementById("equipo-status"),
        selectModelo: document.getElementById("orden-modelo"),
        inputFecha: document.getElementById("orden-fecha"),
        selectOrdenAsignar: document.getElementById("select-orden-asignar"),
        modalTecnicoSelect: document.getElementById("modal-tecnico-select"),
        btnAsignarOrden: document.getElementById("btn-asignar-orden"),
        detalleOrdenId: document.getElementById("detalle-orden-id"),
        revisionOrdenId: document.getElementById("revision-orden-id"),
        fotosOrdenId: document.getElementById("fotos-orden-id"),
        formRevision: document.getElementById("form-revision-orden"),
        formFotos: document.getElementById("form-fotos-orden"),
        inputFotos: document.getElementById("input-fotos-orden"),
        previewFotos: document.getElementById("preview-fotos"),
        formRevisionInicial: document.getElementById("form-revision-inicial"),
        clienteTipo: document.getElementById("cliente-tipo"),
        camposNatural: document.getElementById("cliente-campos-natural"),
        camposJuridico: document.getElementById("cliente-campos-juridico"),
        revisionOrdenNumero: document.getElementById("revision-orden-numero"),
        inputBuscar: document.getElementById("input-buscar-ordenes"),
        filtroEstado: document.getElementById("filtro-estado-orden"),
    };
}

// ============================================
// 6. RENDERIZADO
// ============================================
function renderTablaOrdenes(ordenesData) {
    const { tablaOrdenes } = getDomElements();
    if (!tablaOrdenes) return;

    if (!ordenesData || !ordenesData.length) {
        tablaOrdenes.innerHTML = '<tr><td colspan="7" class="table__empty">No hay órdenes que coincidan con los filtros.</td></tr>';
        return;
    }

    const ordenesFiltradas = ordenesData.filter((o) => String(o.Estado || "").toLowerCase() !== "en proceso");
    
    if (!ordenesFiltradas.length) {
        tablaOrdenes.innerHTML = '<tr><td colspan="7" class="table__empty">No hay órdenes registradas.</td></tr>';
        return;
    }

    tablaOrdenes.innerHTML = ordenesFiltradas.map((orden) => {
        const clienteNombre = orden.Nombre_completo || `${orden.Nombre_cliente ?? ""} ${orden.Apellido_cliente ?? ""}`.trim() || orden.Razon_social || "Cliente no especificado";
        const badgeClass = Utils.getEstadoBadgeClass(orden.Estado);
        const estado = String(orden.Estado || "").toLowerCase();
        
        const mostrarAsignar = estado !== "reparada";
        
        return `
            <tr>
                <td class="col-id"><span class="chip">${Utils.escapeHtml(orden.ID_orden)}</span></td>
                <td class="col-estado"><span class="badge ${badgeClass}">${Utils.escapeHtml(orden.Estado)}</span></td>
                <td class="col-cliente" title="${Utils.escapeHtml(clienteNombre)}">${Utils.escapeHtml(clienteNombre)}</td>
                <td class="col-equipo" title="${Utils.escapeHtml(orden.Equipo ?? "")}">${Utils.escapeHtml(orden.Equipo ?? "")}</td>
                <td class="col-modelo" title="${Utils.escapeHtml(orden.Modelo ?? "")}">${Utils.escapeHtml(orden.Modelo ?? "")}</td>
                <td class="col-fecha">${Utils.escapeHtml(Utils.formatFecha(orden.Fecha_e ?? ""))}</td>
                <td class="table__actions col-acciones">
                    <div class="row-actions">
                        <button type="button" class="icon-action icon-action--view" data-action="ver-detalle" data-id="${Utils.escapeHtml(orden.ID_orden)}" title="Ver detalles">${Iconos.ojo}</button>
                        ${mostrarAsignar ? `
                            <button type="button" class="icon-action icon-action--edit" data-action="seleccionar-asignacion" data-id="${Utils.escapeHtml(orden.ID_orden)}" title="Asignar técnico">${Iconos.asignar}</button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `;
    }).join("");
}

function renderSelectTecnicos(select, tecnicos) {
    if (!select) return;
    select.innerHTML = '<option value="">Seleccione un técnico</option>' + tecnicos.map((tec) => {
        const nombre = `${tec.nombre ?? ""} ${tec.apellido ?? ""}`.trim();
        return `<option value="${Utils.escapeHtml(tec.id)}">${Utils.escapeHtml(nombre)} (${Utils.escapeHtml(tec.id)})</option>`;
    }).join("");
}

function renderSelectOrdenesAsignar(ordenesData) {
    const { selectOrdenAsignar } = getDomElements();
    if (!selectOrdenAsignar) return;

    const pendientes = ordenesData.filter((o) => String(o.Estado || "").toLowerCase() === "pendiente");
    selectOrdenAsignar.innerHTML = '<option value="">Seleccione una orden</option>' + pendientes.map((orden) => {
        return `<option value="${Utils.escapeHtml(orden.ID_orden)}">#${Utils.escapeHtml(orden.ID_orden)} - ${Utils.escapeHtml(orden.Modelo ?? "")}</option>`;
    }).join("");
}

function renderPreviewFotos(files) {
    const { previewFotos } = getDomElements();
    if (!previewFotos) return;

    const lista = Array.from(files || []);
    if (!lista.length) {
        previewFotos.innerHTML = "";
        return;
    }

    previewFotos.innerHTML = lista
        .map((file) => `<img src="${URL.createObjectURL(file)}" alt="${Utils.escapeHtml(file.name)}">`)
        .join("");
}

// ============================================
// 7. CARGA DE DATOS
// ============================================
async function cargarOrdenes() {
    try {
        const data = await Utils.fetchJson(CONFIG.API.ORDENES);
        ordenes = data.ordenes || [];
        renderTablaOrdenes(ordenes);
        actualizarEstadisticas(ordenes);
        renderSelectOrdenesAsignar(ordenes);
    } catch (error) {
        console.error("Error cargando órdenes:", error);
        Utils.showMessage(error.message || "No se pudieron cargar las órdenes.", true);
    }
}

async function cargarModelos() {
    const { selectModelo } = getDomElements();
    if (!selectModelo) return;

    const valorActual = selectModelo.value;

    try {
        const data = await Utils.fetchJson(CONFIG.API.MODELOS);
        const modelos = data.modelos || [];

        selectModelo.innerHTML = '<option value="">Seleccione modelo</option>' + modelos.map((modelo) => {
            const label = `${modelo.marca_nombre ?? ""} ${modelo.nombre ?? ""}`.trim();
            return `<option value="${Utils.escapeHtml(modelo.id)}">${Utils.escapeHtml(label)}</option>`;
        }).join("");

        if (valorActual) {
            const existe = Array.from(selectModelo.options).some(opt => opt.value === valorActual);
            if (existe) selectModelo.value = valorActual;
        }
    } catch (error) {
        console.error("Error cargando modelos:", error);
    }
}

async function cargarTecnicos() {
    try {
        const data = await Utils.fetchJson(CONFIG.API.TECNICOS);
        const tecnicos = data.tecnicos || [];
        const { modalTecnicoSelect } = getDomElements();
        renderSelectTecnicos(modalTecnicoSelect, tecnicos);
    } catch (error) {
        console.error("Error cargando técnicos:", error);
    }
}

// ============================================
// 8. ACCIONES
// ============================================
function actualizarEstadisticas(ordenesData) {
    const count = (estado) => ordenesData.filter((o) => String(o.Estado || "").toLowerCase() === estado).length;
    const pendientes = count("pendiente");
    const asignadas = count("asignada");
    const reparadas = count("reparada");

    const { statPendientes, statAsignadas } = getDomElements();
    if (statPendientes) statPendientes.textContent = String(pendientes);
    if (statAsignadas) statAsignadas.textContent = String(asignadas);

    const statReparadas = document.getElementById("stat-reparadas");
    if (statReparadas) statReparadas.textContent = String(reparadas);
}

function setClienteStatus(message, isError = false) {
    const { clienteStatus } = getDomElements();
    if (!clienteStatus) return;
    clienteStatus.textContent = message;
    clienteStatus.classList.remove("is-error", "is-success");
    if (isError) {
        clienteStatus.classList.add("is-error");
    } else if (message && !message.toLowerCase().includes("no encontrado")) {
        clienteStatus.classList.add("is-success");
    }
}

function setEquipoStatus(message, isError = false) {
    const { equipoStatus } = getDomElements();
    if (!equipoStatus) return;
    equipoStatus.textContent = message;
    equipoStatus.classList.remove("is-error", "is-success");
    if (isError) {
        equipoStatus.classList.add("is-error");
    } else if (message && !message.toLowerCase().includes("no encontrado")) {
        equipoStatus.classList.add("is-success");
    }
}

function getFieldValue(fieldId) {
    if (fieldId === 'celular') {
        const tipo = document.getElementById('cliente-tipo')?.value || 'natural';
        const id = tipo === 'natural' ? 'cliente-celular' : 'cliente-celular-juridico';
        const field = document.getElementById(id);
        return field && "value" in field ? String(field.value).trim() : "";
    }
    if (fieldId === 'correo') {
        const tipo = document.getElementById('cliente-tipo')?.value || 'natural';
        const id = tipo === 'natural' ? 'cliente-correo' : 'cliente-correo-juridico';
        const field = document.getElementById(id);
        return field && "value" in field ? String(field.value).trim() : "";
    }
    if (fieldId === 'direccion') {
        const tipo = document.getElementById('cliente-tipo')?.value || 'natural';
        const id = tipo === 'natural' ? 'cliente-direccion' : 'cliente-direccion-juridico';
        const field = document.getElementById(id);
        return field && "value" in field ? String(field.value).trim() : "";
    }
    
    const field = document.getElementById(fieldId);
    return field && "value" in field ? String(field.value).trim() : "";
}

function setFieldValue(fieldId, value) {
    if (fieldId === 'celular') {
        const tipo = document.getElementById('cliente-tipo')?.value || 'natural';
        const id = tipo === 'natural' ? 'cliente-celular' : 'cliente-celular-juridico';
        const field = document.getElementById(id);
        if (field && "value" in field) field.value = value;
        return;
    }
    if (fieldId === 'correo') {
        const tipo = document.getElementById('cliente-tipo')?.value || 'natural';
        const id = tipo === 'natural' ? 'cliente-correo' : 'cliente-correo-juridico';
        const field = document.getElementById(id);
        if (field && "value" in field) field.value = value;
        return;
    }
    if (fieldId === 'direccion') {
        const tipo = document.getElementById('cliente-tipo')?.value || 'natural';
        const id = tipo === 'natural' ? 'cliente-direccion' : 'cliente-direccion-juridico';
        const field = document.getElementById(id);
        if (field && "value" in field) field.value = value;
        return;
    }
    
    const field = document.getElementById(fieldId);
    if (field && "value" in field) field.value = value;
}

function obtenerSiguienteNumeroTest() {
    const numeros = testsOrdenActual
        .map((test) => Number(test.Num_test ?? test.num_test ?? 0))
        .filter((num) => Number.isFinite(num));
    return numeros.length ? Math.max(...numeros) + 1 : 1;
}

// ============================================
// 9. TOGGLE CLIENTE
// ============================================
function toggleCamposCliente(tipo) {
    const { camposNatural, camposJuridico } = getDomElements();
    
    if (!camposNatural || !camposJuridico) return;
    
    const celularNatural = document.getElementById('cliente-celular');
    const celularJuridico = document.getElementById('cliente-celular-juridico');
    const correoNatural = document.getElementById('cliente-correo');
    const correoJuridico = document.getElementById('cliente-correo-juridico');
    const direccionNatural = document.getElementById('cliente-direccion');
    const direccionJuridico = document.getElementById('cliente-direccion-juridico');
    
    const rifInput = document.getElementById('cliente-rif');
    if (rifInput) {
        rifInput.classList.remove('field-error', 'field-success');
        rifInput.style.borderColor = '';
        rifInput.style.boxShadow = '';
        const rifError = document.getElementById('cliente-rif-error');
        if (rifError) { rifError.textContent = ''; rifError.style.color = ''; }
    }
    
    const cedulaInput = document.getElementById('cliente-cedula');
    if (cedulaInput) {
        cedulaInput.classList.remove('field-error', 'field-success');
        cedulaInput.style.borderColor = '';
        cedulaInput.style.boxShadow = '';
        const cedulaError = document.getElementById('cliente-cedula-error');
        if (cedulaError) { cedulaError.textContent = ''; cedulaError.style.color = ''; }
    }
    
    if (tipo === 'juridico') {
        camposNatural.style.display = 'none';
        camposJuridico.style.display = 'grid';
        
        if (document.getElementById('cliente-cedula')) { document.getElementById('cliente-cedula').removeAttribute('required'); document.getElementById('cliente-cedula').disabled = true; }
        if (document.getElementById('cliente-nombre')) { document.getElementById('cliente-nombre').removeAttribute('required'); document.getElementById('cliente-nombre').disabled = true; }
        if (document.getElementById('cliente-apellido')) { document.getElementById('cliente-apellido').removeAttribute('required'); document.getElementById('cliente-apellido').disabled = true; }
        if (celularNatural) { celularNatural.removeAttribute('required'); celularNatural.disabled = true; }
        if (correoNatural) { correoNatural.disabled = true; }
        if (direccionNatural) { direccionNatural.disabled = true; }
        
        if (rifInput) { rifInput.setAttribute('required', ''); rifInput.disabled = false; }
        if (document.getElementById('cliente-razon-social')) { document.getElementById('cliente-razon-social').setAttribute('required', ''); document.getElementById('cliente-razon-social').disabled = false; }
        if (celularJuridico) { celularJuridico.setAttribute('required', ''); celularJuridico.disabled = false; }
        if (correoJuridico) { correoJuridico.disabled = false; }
        if (direccionJuridico) { direccionJuridico.disabled = false; }
        
        const btnVerificar = document.getElementById('btn-verificar-cliente');
        if (btnVerificar) btnVerificar.textContent = 'Verificar empresa';
    } else {
        camposNatural.style.display = 'grid';
        camposJuridico.style.display = 'none';
        
        if (document.getElementById('cliente-cedula')) { document.getElementById('cliente-cedula').setAttribute('required', ''); document.getElementById('cliente-cedula').disabled = false; }
        if (document.getElementById('cliente-nombre')) { document.getElementById('cliente-nombre').setAttribute('required', ''); document.getElementById('cliente-nombre').disabled = false; }
        if (document.getElementById('cliente-apellido')) { document.getElementById('cliente-apellido').setAttribute('required', ''); document.getElementById('cliente-apellido').disabled = false; }
        if (celularNatural) { celularNatural.setAttribute('required', ''); celularNatural.disabled = false; }
        if (correoNatural) { correoNatural.disabled = false; }
        if (direccionNatural) { direccionNatural.disabled = false; }
        
        if (rifInput) { rifInput.removeAttribute('required'); rifInput.disabled = true; }
        if (document.getElementById('cliente-razon-social')) { document.getElementById('cliente-razon-social').removeAttribute('required'); document.getElementById('cliente-razon-social').disabled = true; }
        if (celularJuridico) { celularJuridico.removeAttribute('required'); celularJuridico.disabled = true; }
        if (correoJuridico) { correoJuridico.disabled = true; }
        if (direccionJuridico) { direccionJuridico.disabled = true; }
        
        const btnVerificar = document.getElementById('btn-verificar-cliente');
        if (btnVerificar) btnVerificar.textContent = 'Verificar cliente';
    }
    
    setClienteStatus('');
    const { btnCrearCliente } = getDomElements();
    if (btnCrearCliente) btnCrearCliente.hidden = true;
    clienteActualId = null;
}

// ============================================
// 10. VERIFICACIONES CLIENTE
// ============================================
async function verificarCliente() {
    const tipo = document.getElementById('cliente-tipo')?.value || 'natural';
    setClienteStatus("Verificando...", false);
    if (tipo === 'natural') {
        await verificarClienteNatural();
    } else {
        await verificarClienteJuridico();
    }
}

async function verificarClienteNatural() {
    const cedula = getFieldValue("cliente-cedula");
    if (!cedula) { setClienteStatus("Ingresa una cédula para verificar.", true); return; }
    if (cedula.length < 7 || cedula.length > 8) { setClienteStatus("La cédula debe tener 7 u 8 dígitos.", true); return; }

    try {
        const data = await Utils.fetchJson(`${CONFIG.API.CLIENTES}/${encodeURIComponent(cedula)}`);
        const cliente = data.cliente || data.data || {};

        clienteActualId = cliente.id || cliente.cedula || cedula;
        setFieldValue("cliente-nombre", cliente.nombre || "");
        setFieldValue("cliente-apellido", cliente.apellido || "");
        setFieldValue("cliente-celular", cliente.celular || "");
        setFieldValue("cliente-correo", cliente.correo || "");
        setFieldValue("cliente-direccion", cliente.direccion || "");
        setFieldValue("cliente-tipo", "natural");
        setClienteStatus("Cliente verificado correctamente.");

        const { btnCrearCliente } = getDomElements();
        if (btnCrearCliente) btnCrearCliente.hidden = true;
        
        const cedulaInput = document.getElementById('cliente-cedula');
        if (cedulaInput) {
            cedulaInput.classList.remove('field-error');
            cedulaInput.classList.add('field-success');
            cedulaInput.style.borderColor = '#22c55e';
            cedulaInput.style.boxShadow = '0 0 0 2px rgba(34, 197, 94, 0.15)';
        }
        
    } catch (error) {
        clienteActualId = null;
        setClienteStatus("Cliente no encontrado. Regístralo para continuar.", true);
        const { btnCrearCliente } = getDomElements();
        if (btnCrearCliente) btnCrearCliente.hidden = false;
        
        const cedulaInput = document.getElementById('cliente-cedula');
        if (cedulaInput) {
            cedulaInput.classList.add('field-error');
            cedulaInput.classList.remove('field-success');
            cedulaInput.style.borderColor = '#ef4444';
            cedulaInput.style.boxShadow = '0 0 0 2px rgba(239, 68, 68, 0.15)';
        }
    }
}

async function verificarClienteJuridico() {
    const rif = getFieldValue("cliente-rif");
    if (!rif) { setClienteStatus("Ingresa un RIF para verificar.", true); return; }

    if (!Utils.validarRIF(rif)) {
        setClienteStatus("Formato de RIF inválido. Ej: J-12345678-9", true);
        const rifInput = document.getElementById('cliente-rif');
        if (rifInput) {
            rifInput.classList.add('field-error');
            rifInput.classList.remove('field-success');
            rifInput.style.borderColor = '#ef4444';
            rifInput.style.boxShadow = '0 0 0 2px rgba(239, 68, 68, 0.15)';
        }
        return;
    }

    try {
        const rifConGuiones = rif;
        const rifSinGuiones = rif.replace(/-/g, '').toUpperCase();
        
        let data;
        try {
            data = await Utils.fetchJson(`${CONFIG.API.CLIENTES}/${encodeURIComponent(rifConGuiones)}`);
        } catch (e) {
            data = await Utils.fetchJson(`${CONFIG.API.CLIENTES}/${encodeURIComponent(rifSinGuiones)}`);
        }
        
        const cliente = data.cliente || data.data || {};

        clienteActualId = cliente.id || cliente.rif || rifConGuiones;
        setFieldValue("cliente-razon-social", cliente.razon_social || cliente.nombre || "");
        setFieldValue("cliente-celular-juridico", cliente.celular || cliente.telefono || "");
        setFieldValue("cliente-correo-juridico", cliente.correo || "");
        setFieldValue("cliente-direccion-juridico", cliente.direccion || "");
        setFieldValue("cliente-tipo", "juridico");
        setClienteStatus("Empresa verificada correctamente.");

        const { btnCrearCliente } = getDomElements();
        if (btnCrearCliente) btnCrearCliente.hidden = true;
        
        const rifInput = document.getElementById('cliente-rif');
        if (rifInput) {
            rifInput.classList.remove('field-error');
            rifInput.classList.add('field-success');
            rifInput.style.borderColor = '#22c55e';
            rifInput.style.boxShadow = '0 0 0 2px rgba(34, 197, 94, 0.15)';
        }
        
    } catch (error) {
        clienteActualId = null;
        setClienteStatus("Empresa no encontrada. Regístrala para continuar.", true);
        const { btnCrearCliente } = getDomElements();
        if (btnCrearCliente) btnCrearCliente.hidden = false;
        
        const rifInput = document.getElementById('cliente-rif');
        if (rifInput) {
            rifInput.classList.add('field-error');
            rifInput.classList.remove('field-success');
            rifInput.style.borderColor = '#ef4444';
            rifInput.style.boxShadow = '0 0 0 2px rgba(239, 68, 68, 0.15)';
        }
    }
}

// ============================================
// 11. REGISTRAR CLIENTE
// ============================================
async function registrarClienteDesdeFormulario() {
    try {
        const tipo = document.getElementById('cliente-tipo')?.value || 'natural';
        let payload = {
            tipo: tipo,
            celular: getFieldValue("celular"),
            correo: getFieldValue("correo"),
            direccion: getFieldValue("direccion"),
        };

        if (tipo === 'natural') {
            payload.cedula = getFieldValue("cliente-cedula");
            payload.nombre = getFieldValue("cliente-nombre");
            payload.apellido = getFieldValue("cliente-apellido");

            if (!payload.cedula || !payload.nombre || !payload.apellido) {
                setClienteStatus("Cédula, nombre y apellido son obligatorios.", true); return;
            }
            if (payload.cedula.length < 7 || payload.cedula.length > 8) {
                setClienteStatus("La cédula debe tener 7 u 8 dígitos.", true); return;
            }
        } else {
            payload.rif = getFieldValue("cliente-rif");
            payload.razon_social = getFieldValue("cliente-razon-social");

            if (!payload.rif || !payload.razon_social) {
                setClienteStatus("RIF y Razón Social son obligatorios.", true); return;
            }
            if (!Utils.validarRIF(payload.rif)) {
                setClienteStatus("Formato de RIF inválido. Ej: J-12345678-9", true); return;
            }
        }

        if (!payload.celular) { setClienteStatus("El celular es obligatorio.", true); return; }

        const resultadoTelefono = Utils.validarTelefonoOrden(payload.celular);
        if (!resultadoTelefono.valido) { setClienteStatus(resultadoTelefono.mensaje, true); return; }

        if (payload.correo && !Utils.isValidEmail(payload.correo)) {
            setClienteStatus("El correo electrónico no es válido.", true); return;
        }

        const data = await Utils.fetchJson(CONFIG.API.CLIENTES, {
            method: "POST",
            body: JSON.stringify(payload),
        });

        clienteActualId = data.id || payload.cedula || payload.rif;
        setClienteStatus("Cliente registrado correctamente.");

        const { btnCrearCliente } = getDomElements();
        if (btnCrearCliente) btnCrearCliente.hidden = true;
    } catch (error) {
        setClienteStatus(error.message || "No se pudo registrar el cliente.", true);
    }
}

// ============================================
// 12. VERIFICACIÓN EQUIPO
// ============================================
async function verificarEquipo() {
    const idEquipo = getFieldValue("orden-id-equipo");
    if (!idEquipo) { setEquipoStatus("Ingresa el IMEI del equipo para verificar.", true); return; }
    if (!/^\d+$/.test(idEquipo)) { setEquipoStatus("El IMEI solo puede contener números.", true); return; }
    if (idEquipo.length !== 15) { setEquipoStatus("El IMEI debe tener exactamente 15 caracteres.", true); return; }

    try {
        const data = await Utils.fetchJson(`/api/ordenes-servicio/equipo/${encodeURIComponent(idEquipo)}`);

        if (data.exists) {
            const equipo = data.equipo || {};
            setEquipoStatus("Equipo encontrado.");

            const { selectModelo } = getDomElements();
            if (equipo.id_modelo && selectModelo) selectModelo.value = String(equipo.id_modelo);
            if (equipo.color) setFieldValue("orden-color", Utils.capitalizarPalabras(equipo.color));
            
            if (equipo.capacidad) {
                const capSelect = document.getElementById("orden-capacidad");
                if (capSelect) capSelect.value = equipo.capacidad;
            }
            if (equipo.patron) setFieldValue("orden-patron", equipo.patron);
            if (equipo.clave) setFieldValue("orden-clave", equipo.clave);
        } else {
            setEquipoStatus("Equipo no encontrado. Se creará al guardar la orden.", true);
        }
    } catch (error) {
        setEquipoStatus("No se pudo verificar el equipo.", true);
    }
}

// ============================================
// 13. MARCAR TESTS
// ============================================
function marcarTodosTestsOK() {
    document.querySelectorAll('#modal-revision-inicial input[type="radio"][value="1"]').forEach(radio => { radio.checked = true; });
    Utils.showMessage('✅ Todos los componentes marcados como OK');
}

function marcarTodosTestsFallo() {
    document.querySelectorAll('#modal-revision-inicial input[type="radio"][value="0"]').forEach(radio => { radio.checked = true; });
    Utils.showMessage('❌ Todos los componentes marcados como No funciona');
}

// ============================================
// 14. RECOLECTAR TESTS
// ============================================
function recolectarTests() {
    const testCampos = [
        'Botón Power', 'Botón Vol', 'Cornetas', 'Mica', 'LCD', 'Tactil',
        'Wifi', 'Puerto_carga', 'Cámara posterior', 'Cámara delantera', 'Microfono',
        'Flash', 'Botón Silencio', 'Auricular', 'Senal', 'Sensor_proximidad',
        'Face_id', 'Bluetooth', 'Caja', 'Cargador', 'Cable', 'Manuales'
    ];
    
    const testsData = [];
    
    testCampos.forEach((campo) => {
        const radio = document.querySelector(`#modal-revision-inicial input[name="test_${campo}"]:checked`);
        if (radio) {
            const valor = parseInt(radio.value, 10);
            const resultado = valor === 1 ? "Funciona" : "No funciona";
            testsData.push({ nombre: campo, resultado: resultado });
        }
    });
    
    const observaciones = document.getElementById("revision-observaciones")?.value?.trim() || "";
    if (observaciones) testsData.push({ nombre: "Observaciones", resultado: observaciones });
    
    return testsData;
}

// ============================================
// 15. SUBMIT ORDEN
// ============================================
async function onSubmitOrden(event) {
    event.preventDefault();
    const { formOrden, inputFecha, selectModelo } = getDomElements();
    if (!formOrden) return;

    const idEquipo = getFieldValue("orden-id-equipo");
    if (!idEquipo) { Utils.showMessage("El IMEI del equipo es obligatorio.", true); return; }
    if (!/^\d+$/.test(idEquipo)) { Utils.showMessage("El IMEI solo puede contener números.", true); return; }
    if (idEquipo.length !== 15) { Utils.showMessage("El IMEI debe tener exactamente 15 caracteres.", true); return; }

    const color = getFieldValue("orden-color");
    if (color && color.length > 15) { Utils.showMessage("El color no puede exceder los 15 caracteres.", true); return; }
    if (color && !Utils.soloLetras(color)) { Utils.showMessage("El color solo debe contener letras.", true); return; }

    const idModelo = selectModelo?.value;
    const modeloCustom = getFieldValue("orden-modelo-custom");
    if (!idModelo && !modeloCustom) { Utils.showMessage("Debes seleccionar un modelo o escribir uno personalizado.", true); return; }
    if (modeloCustom && modeloCustom.length > 30) { Utils.showMessage("El modelo personalizado no puede exceder 30 caracteres.", true); return; }
    if (modeloCustom && !/^[a-zA-Z0-9\s\-]+$/.test(modeloCustom)) { Utils.showMessage("El modelo solo puede contener letras, números, espacios y guiones.", true); return; }

    const descripcion = getFieldValue("orden-descripcion");
    if (!descripcion) { Utils.showMessage("La descripción del problema es obligatoria.", true); return; }
    if (descripcion.length > 300) { Utils.showMessage("La descripción no puede exceder 300 caracteres.", true); return; }

    const nota = getFieldValue("orden-nota");
    if (nota && nota.length > 50) { Utils.showMessage("Las notas no pueden exceder 50 caracteres.", true); return; }

    const correo = getFieldValue("correo");
    if (correo && !Utils.isValidEmail(correo)) { Utils.showMessage("El correo electrónico no es válido.", true); return; }

    const celular = getFieldValue("celular");
    if (celular) {
        const resultadoTelefono = Utils.validarTelefonoOrden(celular);
        if (!resultadoTelefono.valido) {
            Utils.showMessage(resultadoTelefono.mensaje, true);
            const tipoCliente = document.getElementById('cliente-tipo')?.value || 'natural';
            const idCelular = tipoCliente === 'natural' ? 'cliente-celular' : 'cliente-celular-juridico';
            const campoCelular = document.getElementById(idCelular);
            if (campoCelular) {
                campoCelular.focus();
                campoCelular.classList.add('field-error');
                campoCelular.style.borderColor = '#ef4444';
                campoCelular.style.boxShadow = '0 0 0 2px rgba(239, 68, 68, 0.15)';
            }
            return;
        }
    }

    const tipoCliente = document.getElementById('cliente-tipo')?.value || 'natural';
    let clienteId = clienteActualId;

    if (tipoCliente === 'natural') {
        const cedula = getFieldValue("cliente-cedula");
        const nombre = getFieldValue("cliente-nombre");
        const apellido = getFieldValue("cliente-apellido");

        if (!cedula) { Utils.showMessage("La cédula del cliente es obligatoria.", true); return; }
        if (cedula.length < 7 || cedula.length > 8) { Utils.showMessage("La cédula debe tener 7 u 8 dígitos numéricos.", true); return; }
        if (nombre && nombre.length < 3) { Utils.showMessage("El nombre debe tener al menos 3 letras.", true); return; }
        if (nombre && nombre.length > 20) { Utils.showMessage("El nombre no puede exceder los 20 caracteres.", true); return; }
        if (nombre && !Utils.soloLetras(nombre)) { Utils.showMessage("El nombre solo debe contener letras.", true); return; }
        if (apellido && apellido.length < 3) { Utils.showMessage("El apellido debe tener al menos 3 letras.", true); return; }
        if (apellido && apellido.length > 20) { Utils.showMessage("El apellido no puede exceder los 20 caracteres.", true); return; }
        if (apellido && !Utils.soloLetras(apellido)) { Utils.showMessage("El apellido solo debe contener letras.", true); return; }
    } else {
        const rif = getFieldValue("cliente-rif");
        const razonSocial = getFieldValue("cliente-razon-social");

        if (!rif) { Utils.showMessage("El RIF es obligatorio para clientes jurídicos.", true); return; }
        if (!Utils.validarRIF(rif)) { Utils.showMessage("Formato de RIF inválido. Ej: J-12345678-9", true); return; }
        if (!razonSocial) { Utils.showMessage("La Razón Social es obligatoria para clientes jurídicos.", true); return; }
        if (razonSocial.length > 60) { Utils.showMessage("La Razón Social no puede exceder 60 caracteres.", true); return; }
    }

    const direccion = getFieldValue("direccion");
    if (direccion && direccion.length > 50) { Utils.showMessage("La dirección no puede exceder los 50 caracteres.", true); return; }

    if (!clienteId) {
        if (tipoCliente === 'natural') {
            const cedula = getFieldValue("cliente-cedula");
            const nombre = getFieldValue("cliente-nombre");
            const apellido = getFieldValue("cliente-apellido");
            
            try {
                const data = await Utils.fetchJson(`${CONFIG.API.CLIENTES}/${encodeURIComponent(cedula)}`);
                const cliente = data.cliente || data.data || {};
                clienteId = cliente.id || cliente.cedula || cedula;
                setFieldValue("cliente-nombre", cliente.nombre || "");
                setFieldValue("cliente-apellido", cliente.apellido || "");
                setFieldValue("cliente-celular", cliente.celular || "");
                setFieldValue("cliente-correo", cliente.correo || "");
                setFieldValue("cliente-direccion", cliente.direccion || "");
            } catch (e) {
                if (!nombre || !apellido || !celular) { Utils.showMessage("Para registrar un nuevo cliente, completa nombre, apellido y celular.", true); return; }
                await registrarClienteDesdeFormulario();
                clienteId = clienteActualId;
            }
        } else {
            const rif = getFieldValue("cliente-rif");
            const razonSocial = getFieldValue("cliente-razon-social");
            
            try {
                const rifSinGuiones = rif.replace(/-/g, '').toUpperCase();
                let data;
                try { data = await Utils.fetchJson(`${CONFIG.API.CLIENTES}/${encodeURIComponent(rif)}`); } 
                catch (e) { data = await Utils.fetchJson(`${CONFIG.API.CLIENTES}/${encodeURIComponent(rifSinGuiones)}`); }
                
                const cliente = data.cliente || data.data || {};
                clienteId = cliente.id || cliente.rif || rif;
                setFieldValue("cliente-razon-social", cliente.razon_social || cliente.nombre || "");
                setFieldValue("cliente-celular-juridico", cliente.celular || cliente.telefono || "");
                setFieldValue("cliente-correo-juridico", cliente.correo || "");
                setFieldValue("cliente-direccion-juridico", cliente.direccion || "");
            } catch (e) {
                if (!razonSocial || !celular) { Utils.showMessage("Para registrar una nueva empresa, completa Razón Social y celular.", true); return; }
                await registrarClienteDesdeFormulario();
                clienteId = clienteActualId;
            }
        }
    }

    if (!clienteId) { Utils.showMessage("Debes verificar o registrar el cliente primero.", true); return; }

    const fechaActual = Utils.getFechaActual();

    datosOrdenPendiente = {
        id_cliente: clienteId,
        id_equipo: idEquipo,
        id_modelo: idModelo || null,
        modelo_custom: modeloCustom || null,
        color: color || "",
        capacidad: getFieldValue("orden-capacidad") || "",
        descripcion: descripcion,
        nota: nota || null,
        nombre: getFieldValue("cliente-nombre") || "",
        apellido: getFieldValue("cliente-apellido") || "",
        celular: celular || "",
        correo: correo || "",
        direccion: direccion || "",
        tipo: tipoCliente,
        fecha_ingreso: fechaActual,
        patron: getFieldValue("orden-patron") || "",
        clave: getFieldValue("orden-clave") || "",
    };

    closeModal("modal-nueva-orden");
    
    setTimeout(() => {
        document.querySelectorAll('#modal-revision-inicial input[type="radio"][value="1"]').forEach(radio => { radio.checked = true; });
        const obsTextarea = document.getElementById("revision-observaciones");
        if (obsTextarea) obsTextarea.value = "";
    }, 100);
    
    openModal("modal-revision-inicial");
}

// ============================================
// 15.1 REFRESCAR MODAL NUEVA ORDEN
// ============================================
async function refrescarModalNuevaOrden(modeloCustomUsado = null) {
    const { formOrden, inputFecha, selectModelo, clienteTipo, btnCrearCliente } = getDomElements();

    if (formOrden) formOrden.reset();

    if (inputFecha) inputFecha.value = Utils.getFechaActual();

    clienteActualId = null;
    setClienteStatus("");
    if (btnCrearCliente) btnCrearCliente.hidden = true;

    if (clienteTipo) clienteTipo.value = 'natural';
    toggleCamposCliente('natural');

    if (formOrden) {
        formOrden.querySelectorAll('.field-error, .field-success').forEach(el => {
            el.classList.remove('field-error', 'field-success');
            el.style.borderColor = '';
            el.style.boxShadow = '';
        });

        formOrden.querySelectorAll('.field-error[id$="-error"]').forEach(el => {
            el.textContent = '';
            el.style.color = '';
        });

        formOrden.querySelectorAll('select').forEach(sel => {
            if (sel.id !== 'cliente-tipo') sel.selectedIndex = 0;
        });
    }

    await cargarModelos();

    if (modeloCustomUsado && selectModelo) {
        const objetivo = modeloCustomUsado.trim().toLowerCase();
        const opcion = Array.from(selectModelo.options).find(opt => opt.textContent.trim().toLowerCase().includes(objetivo));
        if (opcion) selectModelo.value = opcion.value;
    }

    setEquipoStatus("");

    document.querySelectorAll('#modal-revision-inicial input[type="radio"][value="1"]').forEach(radio => { radio.checked = true; });
    const obsTextarea = document.getElementById("revision-observaciones");
    if (obsTextarea) obsTextarea.value = "";
}

// ============================================
// 16. CONFIRMAR REVISION Y GUARDAR
// ============================================
async function confirmarRevision(event) {
    event.preventDefault();

    const testsData = recolectarTests();

    const testCampos = [
        'Botón Power', 'Botón Vol', 'Cornetas', 'Mica', 'LCD', 'Tactil',
        'Wifi', 'Puerto_carga', 'Cámara posterior', 'Cámara delantera', 'Microfono',
        'Flash', 'Botón Silencio', 'Auricular', 'Senal', 'Sensor_proximidad',
        'Face_id', 'Bluetooth', 'Caja', 'Cargador', 'Cable', 'Manuales'
    ];

    let todosSeleccionados = true;
    testCampos.forEach((campo) => {
        const radio = document.querySelector(`#modal-revision-inicial input[name="test_${campo}"]:checked`);
        if (!radio) todosSeleccionados = false;
    });

    if (!todosSeleccionados) { Utils.showMessage("Por favor, selecciona el estado de todos los componentes.", true); return; }
    if (!datosOrdenPendiente) { Utils.showMessage("No hay datos de orden para guardar.", true); return; }

    const incluirTests = testsData.length > 0;

    const payload = {
        ...datosOrdenPendiente,
        incluir_tests: incluirTests,
        tests: testsData
    };

    const modeloCustomUsado = datosOrdenPendiente.modelo_custom || null;

    try {
        await Utils.fetchJson(CONFIG.API.ORDENES_SERVICIO, {
            method: "POST",
            body: JSON.stringify(payload),
        });

        Utils.showMessage("Orden creada correctamente con revisión inicial registrada.");

        datosOrdenPendiente = null;
        closeModal("modal-revision-inicial");

        await refrescarModalNuevaOrden(modeloCustomUsado);

        await cargarOrdenes();
    } catch (error) {
        console.error("Error creando orden:", error);
        Utils.showMessage(error.message || "No se pudo crear la orden.", true);
    }
}

// ============================================
// 17. DETALLE ORDEN
// ============================================
async function abrirDetalleOrden(idOrden) {
    try {
        const data = await Utils.fetchJson(`${CONFIG.API.ORDENES}/${encodeURIComponent(idOrden)}`);
        ordenActualId = idOrden;
        testsOrdenActual = data.test_orden || [];

        const detalle = data.detalle_orden || {};

        renderDetalleOrdenModal(detalle);
        renderFotosOrdenModal(data.fotos_orden || []);
        renderTestsOrdenModal(data.test_orden || [], idOrden);

        const { detalleOrdenId, revisionOrdenId, fotosOrdenId, revisionOrdenNumero } = getDomElements();
        if (detalleOrdenId) detalleOrdenId.value = String(idOrden);
        if (revisionOrdenId) revisionOrdenId.value = String(idOrden);
        if (fotosOrdenId) fotosOrdenId.value = String(idOrden);

        if (revisionOrdenNumero) revisionOrdenNumero.textContent = String(idOrden);

        openModal("modal-detalle-orden");
    } catch (error) {
        Utils.showMessage(error.message || "No se pudo cargar el detalle de la orden.", true);
    }
}

function renderDetalleOrdenModal(detalle) {
    const container = document.getElementById('modal-order-info');
    if (!container) return;

    if (!detalle || Object.keys(detalle).length === 0) {
        container.innerHTML = '<p class="device-detail__empty">No se encontró información de la orden</p>';
        return;
    }

    const estado = detalle.Estado || 'Pendiente';
    const badgeClass = Utils.getEstadoBadgeClass(estado);
    const clienteNombre = detalle.Nombre_completo || `${detalle.Nombre_cliente || ''} ${detalle.Apellido_cliente || ''}`.trim() || detalle.Razon_social || 'No especificado';
    const costo = detalle.Costo_reparacion;

    container.innerHTML = `
        <div class="detail-group">
            <span class="detail-label">ID Orden</span>
            <span class="detail-value"><strong>#${Utils.escapeHtml(detalle.ID_orden || '---')}</strong></span>
        </div>
        <div class="detail-group">
            <span class="detail-label">Estado</span>
            <span class="detail-value"><span class="badge ${badgeClass}">${Utils.escapeHtml(estado)}</span></span>
        </div>
        <div class="detail-group">
            <span class="detail-label">Cliente</span>
            <span class="detail-value"><strong>${Utils.escapeHtml(clienteNombre)}</strong></span>
        </div>
        <div class="detail-group">
            <span class="detail-label">Equipo</span>
            <span class="detail-value"><strong>${Utils.escapeHtml(detalle.Equipo || 'No especificado')}</strong></span>
        </div>
        <div class="detail-group">
            <span class="detail-label">Modelo</span>
            <span class="detail-value"><strong>${Utils.escapeHtml(detalle.Modelo || 'No especificado')}</strong></span>
        </div>
        <div class="detail-group">
            <span class="detail-label">Costo</span>
            <span class="detail-value"><strong>${costo ? `$${Number(costo).toFixed(2)}` : 'Sin cotizar'}</strong></span>
        </div>
        <div class="detail-group field--full">
            <span class="detail-label">Descripción del problema</span>
            <span class="detail-value">${Utils.escapeHtml(detalle.Des_cliente || 'Sin descripción')}</span>
        </div>
        ${detalle.Nota || detalle.Nota_orden_servicio ? `
            <div class="detail-group field--full">
                <span class="detail-label">Notas adicionales</span>
                <span class="detail-value detail-value--italic">${Utils.escapeHtml(detalle.Nota || detalle.Nota_orden_servicio)}</span>
            </div>
        ` : ''}
    `;
}

function renderFotosOrdenModal(fotos) {
    const container = document.getElementById('modal-order-photos');
    if (!container) return;

    if (!fotos || !fotos.length) {
        container.innerHTML = '<p class="device-detail__empty">No hay fotos registradas para esta orden.</p>';
        return;
    }

    container.innerHTML = `
        <h3 class="card__subtitle">Fotos del dispositivo</h3>
        <div class="fotos-grid">
            ${fotos.map((foto, index) => {
                let src = foto.Foto_e || foto.foto || foto.url || foto.Foto_orden_servicio || "";
                if (src && !src.startsWith("/") && !src.startsWith("http")) src = `/${src}`;
                return `
                    <div class="foto-item" data-foto-index="${index}">
                        <div class="foto-thumbnail" onclick="window.open('${Utils.escapeHtml(src)}', '_blank')">
                            <img src="${Utils.escapeHtml(src)}" alt="Foto ${index + 1}" loading="lazy">
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

function renderTestsOrdenModal(tests, idOrden) {
    const container = document.getElementById('modal-order-tests');
    if (!container) return;

    if (!tests || !tests.length) {
        container.innerHTML = '<p class="device-detail__empty">No hay revisiones registradas.</p>';
        return;
    }

    const testsPorNumero = {};
    tests.forEach(test => {
        const num = test.Num_test || test.num_test || '1';
        if (!testsPorNumero[num]) testsPorNumero[num] = [];
        testsPorNumero[num].push(test);
    });

    const numerosTest = Object.keys(testsPorNumero).sort((a, b) => Number(a) - Number(b));

    container.innerHTML = `
        <h3 class="card__subtitle">Historial de revisiones</h3>
        <div class="tests-table-wrap">
            <table class="table">
                <thead>
                    <tr>
                        <th>N° Test</th>
                        <th>Cantidad</th>
                        <th class="table__actions">Acción</th>
                    </tr>
                </thead>
                <tbody>
                    ${numerosTest.map((num) => {
                        const items = testsPorNumero[num];
                        const cantidad = items.length;
                        const funcionan = items.filter(t => {
                            const r = (t.Resultado_test || t.resultado || '').toLowerCase();
                            return r.includes('funciona') || r.includes('ok');
                        }).length;
                        const noFuncionan = items.filter(t => {
                            const r = (t.Resultado_test || t.resultado || '').toLowerCase();
                            return r.includes('no funciona') || r.includes('falla');
                        }).length;
                        const observaciones = items.filter(t => {
                            const n = (t.Nombre_test || t.nombre || '').toLowerCase();
                            return n.includes('observacion');
                        }).length;
                        
                        return `
                            <tr>
                                <td data-label="N° Test"><span class="chip">Test #${Utils.escapeHtml(num)}</span></td>
                                <td data-label="Cantidad">
                                    ${cantidad} ${cantidad === 1 ? 'componente' : 'componentes'}
                                    ${funcionan > 0 ? `<span class="badge badge--success" style="background:rgba(34,197,94,0.15);color:#22c55e;font-size:0.6rem;margin-left:0.5rem;">✅ ${funcionan}</span>` : ''}
                                    ${noFuncionan > 0 ? `<span class="badge badge--danger" style="background:rgba(239,68,68,0.15);color:#ef4444;font-size:0.6rem;margin-left:0.3rem;">❌ ${noFuncionan}</span>` : ''}
                                    ${observaciones > 0 ? `<span class="badge badge--warning" style="background:rgba(245,158,11,0.15);color:#f59e0b;font-size:0.6rem;margin-left:0.3rem;">📝 ${observaciones}</span>` : ''}
                                </td>
                                <td data-label="Acción" class="table__actions">
                                    <button type="button" class="icon-action icon-action--view" data-action="ver-test-detalle" data-id-orden="${Utils.escapeHtml(idOrden)}" data-num-test="${Utils.escapeHtml(num)}" title="Ver detalles del test">
                                        ${Iconos.ojo}
                                    </button>
                                </td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;

    container.querySelectorAll('[data-action="ver-test-detalle"]').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const idOrd = btn.getAttribute('data-id-orden');
            const numTest = btn.getAttribute('data-num-test');
            await verDetalleTest(idOrd, numTest);
        });
    });
}

// ============================================
// 17.1 DETALLE TEST
// ============================================
async function verDetalleTest(idOrden, numTest) {
    const modalBody = document.getElementById('modal-test-detalle-body');
    if (!modalBody) return;

    modalBody.innerHTML = `
        <div class="test-detail-loading">
            <span class="spinner-loading"></span>
            <span>Cargando detalles del test #${Utils.escapeHtml(numTest)}...</span>
        </div>
    `;

    const modalTitle = document.querySelector('#modal-test-detalle .ui-modal__title');
    if (modalTitle) modalTitle.textContent = `Detalle del test #${numTest} - Orden ${idOrden}`;

    if (window.UiModal && typeof window.UiModal.openById === 'function') window.UiModal.openById('modal-test-detalle');

    try {
        const data = await Utils.fetchJson(`/api/ordenes-servicio/ordenes/${encodeURIComponent(idOrden)}/test/${encodeURIComponent(numTest)}`);
        
        const componentes = data.componentes || data.tests || [];

        if (!componentes || !componentes.length) {
            modalBody.innerHTML = '<p class="device-detail__empty">No se encontraron componentes para este test.</p>';
            return;
        }

        const observaciones = [];
        const componentesFiltrados = [];
        
        componentes.forEach((comp) => {
            const nombre = comp.Nombre_test || comp.nombre || comp.test || '';
            if (nombre.toLowerCase().includes('observacion')) observaciones.push(comp);
            else componentesFiltrados.push(comp);
        });

        let html = '<div class="test-detail-grid">';
        
        componentesFiltrados.forEach((comp) => {
            const nombre = comp.Nombre_test || comp.nombre || comp.test || 'Componente';
            const resultado = comp.Resultado_test || comp.resultado || 'Sin especificar';
            
            let badgeClass = 'test-badge--default';
            let displayResultado = resultado;
            
            const rLower = resultado.toLowerCase().trim();
            
            if (rLower.includes('no funciona') || rLower === '0' || rLower.includes('fallo')) {
                badgeClass = 'test-badge--danger';
                displayResultado = '❌ No funciona';
            } else if (rLower.includes('funciona') || rLower === '1' || rLower.includes('correcto')) {
                badgeClass = 'test-badge--success';
                displayResultado = '✅ Funciona';
            }
            
            html += `
                <div class="test-detail-item ${badgeClass}">
                    <span class="test-detail-name">${Utils.escapeHtml(nombre)}</span>
                    <span class="test-detail-result ${badgeClass}">${Utils.escapeHtml(displayResultado)}</span>
                </div>
            `;
        });
        
        html += '</div>';
        
        if (observaciones.length > 0) {
            html += `
                <div class="test-detail-observations">
                    <h4 class="test-detail-observations-title">📝 Observaciones</h4>
                    <div class="test-detail-grid">
            `;
            
            observaciones.forEach((comp) => {
                const nombre = comp.Nombre_test || comp.nombre || comp.test || 'Observaciones';
                const resultado = comp.Resultado_test || comp.resultado || '';
                
                html += `
                    <div class="test-detail-item test-badge--warning" style="grid-column: 1 / -1; border-color: rgba(245, 158, 11, 0.5); background: rgba(245, 158, 11, 0.08);">
                        <span class="test-detail-name">${Utils.escapeHtml(nombre)}</span>
                        <span class="test-detail-result test-badge--warning" style="color: #f59e0b; background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.3);">${Utils.escapeHtml(resultado)}</span>
                    </div>
                `;
            });
            
            html += `</div></div>`;
        }

        modalBody.innerHTML = html;

    } catch (error) {
        modalBody.innerHTML = `<p class="device-detail__empty error">Error al cargar el detalle: ${Utils.escapeHtml(error.message)}</p>`;
    }
}

// ============================================
// 18. ASIGNACION
// ============================================
async function asignarOrden() {
    const selectOrden = document.getElementById("select-orden-asignar");
    const selectTecnico = document.getElementById("modal-tecnico-select");

    const idOrden = selectOrden?.value;
    const idTecnico = selectTecnico?.value;

    if (!idOrden || idOrden === "") { Utils.showMessage("Por favor, selecciona una orden pendiente.", true); return; }
    if (!idTecnico || idTecnico === "") { Utils.showMessage("Por favor, selecciona un técnico.", true); return; }

    const url = `${CONFIG.API.ORDENES}/${encodeURIComponent(idOrden)}/asignar`;
    const payload = { id_empleado: parseInt(idTecnico, 10) };

    try {
        await Utils.fetchJson(url, { method: "POST", body: JSON.stringify(payload) });
        Utils.showMessage("✅ Orden asignada correctamente.");
        closeModal("modal-asignar-tecnico");
        await cargarOrdenes();

        if (selectOrden) selectOrden.value = "";
        if (selectTecnico) selectTecnico.value = "";

    } catch (error) {
        Utils.showMessage(`❌ ${error.message || "No se pudo asignar la orden."}`, true);
    }
}

// ============================================
// 19. REVISION
// ============================================
async function guardarRevision(event) {
    event.preventDefault();
    const { revisionOrdenId, formRevision } = getDomElements();
    const idOrden = revisionOrdenId?.value || ordenActualId;

    if (!idOrden) { Utils.showMessage("Selecciona una orden.", true); return; }

    const payload = {};
    const campos = [
        "Botón Power", "Botón Vol", "Cornetas", "Mica", "LCD", "Tactil",
        "Wifi", "Puerto_carga", "Cámara posterior", "Cámara delantera", "Microfono",
        "Flash", "Botón Silencio", "Auricular", "Senal", "Sensor_proximidad",
        "Face_id", "Bluetooth", "Caja", "Cargador", "Cable", "Manuales"
    ];

    campos.forEach((campo) => {
        const el = formRevision?.querySelector(`[name="${campo}"]`);
        payload[campo] = (el && el.type === "radio" && el.checked && el.value === "1") ? 1 : 0;
        if (el && el.type === "radio" && el.checked && el.value === "0") payload[campo] = 0;
    });

    payload.Num_test = obtenerSiguienteNumeroTest();
    payload.Observaciones = formRevision?.querySelector('[name="Observaciones"]')?.value || "";

    try {
        await Utils.fetchJson(`${CONFIG.API.ORDENES}/${encodeURIComponent(idOrden)}/revision`, {
            method: "POST",
            body: JSON.stringify(payload),
        });

        Utils.showMessage("Revisión registrada.");
        formRevision?.reset();
        closeModal("modal-revision-orden");
        await abrirDetalleOrden(idOrden);
        await cargarOrdenes();
    } catch (error) {
        Utils.showMessage(error.message || "No se pudo guardar la revisión.", true);
    }
}

// ============================================
// 20. FOTOS
// ============================================
async function guardarFotos(event) {
    event.preventDefault();
    const { fotosOrdenId, formFotos } = getDomElements();
    const idOrden = fotosOrdenId?.value || ordenActualId;

    if (!idOrden || !formFotos) return;

    const formData = new FormData(formFotos);
    const csrf = Utils.getCsrfToken();
    const token = Utils.getAccessToken();

    try {
        const headers = new Headers();
        if (csrf) headers.set("X-CSRFToken", csrf);
        if (token) headers.set("Authorization", `Bearer ${token}`);

        const response = await fetch(`/api/taller/ordenes/${encodeURIComponent(idOrden)}/fotos`, {
            method: "POST",
            body: formData,
            headers,
            credentials: "same-origin",
        });

        const data = await response.json().catch(() => ({}));
        if (!response.ok || data.ok === false) throw new Error(data.message || "No se pudieron guardar las fotos.");

        Utils.showMessage("Fotos registradas.");
        formFotos.reset();
        renderPreviewFotos([]);
        closeModal("modal-fotos-orden");
        await abrirDetalleOrden(idOrden);
    } catch (error) {
        Utils.showMessage(error.message || "No se pudieron guardar las fotos.", true);
    }
}

// ============================================
// 21. TABLA CLICK
// ============================================
function onTablaClick(event) {
    const btn = event.target.closest("button[data-action]");
    if (!btn) return;

    const action = btn.dataset.action;
    const id = btn.dataset.id;
    if (!id) return;

    if (action === "ver-detalle") { abrirDetalleOrden(id); return; }
    if (action === "seleccionar-asignacion") {
        const selectOrden = document.getElementById("select-orden-asignar");
        if (selectOrden) {
            selectOrden.value = String(id);
            openModal("modal-asignar-tecnico");
        }
        return;
    }
}

// ============================================
// 22. INICIALIZACIÓN
// ============================================
document.addEventListener("DOMContentLoaded", () => {
    const { inputFecha, formOrden, btnVerificarEquipo, btnVerificarCliente, btnCrearCliente, btnAsignarOrden, formRevision, formFotos, inputFotos, tablaOrdenes, formRevisionInicial, clienteTipo } = getDomElements();

    if (inputFecha) {
        const fechaActual = Utils.getFechaActual();
        inputFecha.value = fechaActual;
        inputFecha.min = fechaActual;
        inputFecha.max = fechaActual;
        inputFecha.readOnly = true;
        inputFecha.style.backgroundColor = 'var(--input-bg)';
        inputFecha.style.cursor = 'not-allowed';
        inputFecha.style.opacity = '0.7';
    }

    document.getElementById('btn-marcar-todos-test')?.addEventListener('click', marcarTodosTestsOK);
    document.getElementById('btn-marcar-todos-fallo')?.addEventListener('click', marcarTodosTestsFallo);

    formRevisionInicial?.addEventListener('submit', confirmarRevision);

    const inputImei = document.getElementById("orden-id-equipo");
    if (inputImei) inputImei.addEventListener("input", (e) => { e.target.value = e.target.value.replace(/[^0-9]/g, "").slice(0, 15); });

    const inputCedula = document.getElementById("cliente-cedula");
    if (inputCedula) inputCedula.addEventListener("input", (e) => { e.target.value = e.target.value.replace(/[^0-9]/g, "").slice(0, 8); });

    const inputPatron = document.getElementById("orden-patron");
    if (inputPatron) {
        inputPatron.addEventListener("input", (e) => {
            let value = e.target.value.replace(/[^0-9-]/g, "");
            let numbers = value.replace(/-/g, "").split("");
            let used = new Set();
            let validNumbers = [];
            for (let num of numbers) { if (num >= "1" && num <= "9" && !used.has(num)) { validNumbers.push(num); used.add(num); } }
            validNumbers = validNumbers.slice(0, 9);
            e.target.value = validNumbers.join("-");
        });
    }

    const inputCelular = document.getElementById("cliente-celular");
    if (inputCelular) {
        inputCelular.addEventListener('input', function() { Utils.formatearTelefonoOrden(this); });
        inputCelular.addEventListener('blur', function() { if (this.value) Utils.validarTelefonoOrdenEnTiempoReal(this); });
    }

    const inputCelularJuridico = document.getElementById("cliente-celular-juridico");
    if (inputCelularJuridico) {
        inputCelularJuridico.addEventListener('input', function() { Utils.formatearTelefonoOrden(this); });
        inputCelularJuridico.addEventListener('blur', function() { if (this.value) Utils.validarTelefonoOrdenEnTiempoReal(this); });
    }

    const inputClave = document.getElementById("orden-clave");
    if (inputClave) inputClave.addEventListener("input", (e) => { e.target.value = e.target.value.replace(/\s/g, "").slice(0, 30); });

    const inputRif = document.getElementById("cliente-rif");
    if (inputRif) {
        inputRif.addEventListener('input', function() {
            let value = this.value;
            let cleanValue = '';
            let hasLetter = false;
            
            for (let i = 0; i < value.length; i++) {
                const char = value[i];
                if (i === 0 && /[A-Za-z]/.test(char)) {
                    if (['J', 'E'].includes(char.toUpperCase())) { cleanValue += char.toUpperCase(); hasLetter = true; }
                    else { cleanValue += 'J'; hasLetter = true; }
                } else if (/\d/.test(char)) {
                    cleanValue += char;
                } else if (char === '-') {
                    if (hasLetter || cleanValue.length > 0) cleanValue += char;
                }
            }
            
            if (cleanValue.length === 0) cleanValue = 'J';
            else if (!/^[JE]/.test(cleanValue)) cleanValue = 'J' + cleanValue;
            if (cleanValue.length > 12) cleanValue = cleanValue.substring(0, 12);
            
            if (/^[JE]/.test(cleanValue)) {
                const letra = cleanValue.charAt(0);
                let resto = cleanValue.substring(1).replace(/-/g, '').replace(/\D/g, '');
                if (resto.length > 9) resto = resto.substring(0, 9);
                
                let resultado = letra;
                if (resto.length > 0) {
                    resultado += '-';
                    if (resto.length <= 8) resultado += resto;
                    else resultado += resto.substring(0, 8) + '-' + resto.substring(8);
                }
                
                if (this.value !== resultado) {
                    const cursorPos = this.selectionStart;
                    this.value = resultado;
                    let newPos = cursorPos > this.value.length ? this.value.length : cursorPos;
                    if (this.value.charAt(newPos) === '-') newPos++;
                    try { this.setSelectionRange(newPos, newPos); } catch (e) {}
                    Utils.validarRIFEnTiempoReal(this);
                }
            } else {
                this.value = 'J' + this.value.replace(/[^0-9]/g, '');
            }
        });
        inputRif.addEventListener('blur', function() { if (this.value) Utils.validarRIFEnTiempoReal(this); });
    }

    const inputColor = document.getElementById("orden-color");
    if (inputColor) {
        inputColor.addEventListener("input", (e) => {
            let value = e.target.value.replace(/[^a-zA-ZáéíóúñÁÉÍÓÚÑ\s]/g, "");
            if (value.length > 15) value = value.slice(0, 15);
            e.target.value = Utils.capitalizarPalabras(value);
        });
    }

    const inputModeloCustom = document.getElementById("orden-modelo-custom");
    if (inputModeloCustom) {
        inputModeloCustom.addEventListener("input", (e) => {
            let value = e.target.value.replace(/[^a-zA-Z0-9\s\-]/g, "");
            if (value.length > 30) value = value.slice(0, 30);
            e.target.value = Utils.capitalizarPalabras(value);
        });
    }

    const inputNombre = document.getElementById("cliente-nombre");
    if (inputNombre) {
        inputNombre.addEventListener("input", (e) => {
            let value = e.target.value.replace(/[^a-zA-ZáéíóúñÁÉÍÓÚÑ\s]/g, "");
            if (value.length > 20) value = value.slice(0, 20);
            e.target.value = Utils.capitalizarPalabras(value);
        });
    }

    const inputApellido = document.getElementById("cliente-apellido");
    if (inputApellido) {
        inputApellido.addEventListener("input", (e) => {
            let value = e.target.value.replace(/[^a-zA-ZáéíóúñÁÉÍÓÚÑ\s]/g, "");
            if (value.length > 20) value = value.slice(0, 20);
            e.target.value = Utils.capitalizarPalabras(value);
        });
    }

    const inputRazonSocial = document.getElementById("cliente-razon-social");
    if (inputRazonSocial) {
        inputRazonSocial.addEventListener("input", (e) => {
            let value = e.target.value.replace(/[^a-zA-Z0-9áéíóúñÁÉÍÓÚÑ\s\.\-&]/g, "");
            if (value.length > 60) value = value.slice(0, 60);
            e.target.value = Utils.capitalizarPalabras(value);
        });
    }

    const inputDireccion = document.getElementById("cliente-direccion");
    if (inputDireccion) inputDireccion.addEventListener("input", (e) => { if (e.target.value.length > 50) e.target.value = e.target.value.slice(0, 50); });

    const inputDireccionJuridico = document.getElementById("cliente-direccion-juridico");
    if (inputDireccionJuridico) inputDireccionJuridico.addEventListener("input", (e) => { if (e.target.value.length > 50) e.target.value = e.target.value.slice(0, 50); });

    if (clienteTipo) {
        clienteTipo.addEventListener('change', (e) => {
            toggleCamposCliente(e.target.value);
            setClienteStatus('');
            const { btnCrearCliente } = getDomElements();
            if (btnCrearCliente) btnCrearCliente.hidden = true;
            clienteActualId = null;
        });
        toggleCamposCliente(clienteTipo.value);
    }

    btnVerificarEquipo?.addEventListener("click", verificarEquipo);
    btnVerificarCliente?.addEventListener("click", verificarCliente);
    btnCrearCliente?.addEventListener("click", registrarClienteDesdeFormulario);
    formOrden?.addEventListener("submit", onSubmitOrden);

    if (btnAsignarOrden) btnAsignarOrden.addEventListener("click", asignarOrden);

    formRevision?.addEventListener("submit", guardarRevision);
    formFotos?.addEventListener("submit", guardarFotos);
    inputFotos?.addEventListener("change", () => renderPreviewFotos(inputFotos.files));
    tablaOrdenes?.addEventListener("click", onTablaClick);

    document.getElementById("btn-asignar-tecnico")?.addEventListener("click", () => { openModal("modal-asignar-tecnico"); });

    document.getElementById("btn-nueva-orden")?.addEventListener("click", () => {
        if (inputFecha) inputFecha.value = Utils.getFechaActual();
        clienteActualId = null;
        setClienteStatus("");
        const { btnCrearCliente } = getDomElements();
        if (btnCrearCliente) btnCrearCliente.hidden = true;
        if (clienteTipo) {
            clienteTipo.value = 'natural';
            toggleCamposCliente('natural');
        }
    });

    Promise.all([ cargarModelos(), cargarTecnicos(), cargarOrdenes() ]).catch((error) => {
        console.error("Error en la inicialización:", error);
    });
});