const tablaClientes = document.getElementById("tabla-clientes");
const btnNuevoCliente = document.getElementById("btn-nuevo-cliente");
const formCliente = document.getElementById("form-cliente");
const clienteIdInput = formCliente?.querySelector("input[name='id']");
const toast = document.getElementById("toast-mensaje");
const statClientes = document.getElementById("stat-clientes");
const statNatural = document.getElementById("stat-natural");
const statJuridico = document.getElementById("stat-juridico");
const tipoClienteSelect = document.getElementById("tipo-cliente");
const inputBuscarClientes = document.getElementById("input-buscar-clientes");
const filtroTipoCliente = document.getElementById("filtro-tipo-cliente");

const NATURAL_REQUIRED_FIELDS = new Set(["cedula", "nombre", "apellido", "celular"]);
const JURIDICO_REQUIRED_FIELDS = new Set(["rif", "razon_social", "telefono"]);

let clientes = [];
let searchQuery = "";
let tipoFilter = "";
let modoEdicion = false;
const csrfToken = document.querySelector("input[name='_csrf_token']")?.value || "";

// ==================== ICONOS SVG (igual que empleados) ====================

const Iconos = {
    lapiz: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25Zm18-11.5a1 1 0 0 0 0-1.41l-1.34-1.34a1 1 0 0 0-1.41 0l-1.12 1.12 3.75 3.75L21 5.75Z" fill="currentColor"/></svg>`,
    basura: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 7h12l-1 14H7L6 7Zm3-3h6l1 2H8l1-2Z" fill="currentColor"/></svg>`,
    ojo: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" fill="currentColor"/></svg>`
};

// ==================== FUNCIONES PARA MODAL DE ELIMINACIÓN ====================

function abrirModalEliminar(clienteId, nombreCliente) {
    const modal = document.getElementById('modal-eliminar-cliente');
    if (!modal) {
        console.warn('Modal de eliminación no encontrado');
        return;
    }
    
    const confirmText = document.getElementById('texto-confirmar-eliminar-cliente');
    if (confirmText) {
        confirmText.textContent = `¿Estás seguro de que quieres eliminar a "${nombreCliente}"?`;
    }
    
    const confirmBtn = document.getElementById('btn-confirmar-eliminar-cliente');
    if (confirmBtn) {
        confirmBtn.setAttribute('data-cliente-id', clienteId);
        confirmBtn.setAttribute('data-cliente-nombre', nombreCliente);
    }
    
    modal.removeAttribute('hidden');
    modal.setAttribute('aria-hidden', 'false');
}

function cerrarModalEliminar() {
    const modal = document.getElementById('modal-eliminar-cliente');
    if (modal) {
        modal.setAttribute('hidden', '');
        modal.setAttribute('aria-hidden', 'true');
    }
}

async function confirmarEliminarCliente() {
    const confirmBtn = document.getElementById('btn-confirmar-eliminar-cliente');
    const clienteId = confirmBtn?.getAttribute('data-cliente-id');
    const nombreCliente = confirmBtn?.getAttribute('data-cliente-nombre') || clienteId;
    
    if (!clienteId) {
        mostrarToast('No se pudo identificar el cliente a eliminar.', true);
        return;
    }
    
    try {
        await fetchJson(`/api/clientes/${encodeURIComponent(clienteId)}`, { method: "DELETE" });
        mostrarToast(`Cliente "${nombreCliente}" eliminado exitosamente.`);
        cerrarModalEliminar();
        cargarClientes();
    } catch (error) {
        console.error('Error al eliminar cliente:', error);
        mostrarToast(error.message || "No se pudo eliminar el cliente.", true);
    }
}

// ==================== FUNCIONES PARA MODAL DE DETALLES ====================

function abrirModalVerCliente(clienteId) {
    const cliente = clientes.find((item) => String(item.id) === String(clienteId) || String(item.rif) === String(clienteId));
    if (!cliente) {
        mostrarToast('Cliente no encontrado.', true);
        return;
    }
    
    const modal = document.getElementById('modal-ver-cliente');
    if (!modal) {
        console.warn('Modal de detalles no encontrado');
        return;
    }
    
    // Obtener inicial para el avatar
    const tipo = getTipoCliente(cliente);
    let inicial = '?';
    if (tipo === 'natural') {
        inicial = (cliente.nombre || '?').charAt(0).toUpperCase();
    } else {
        inicial = (cliente.razon_social || cliente.nombre || '?').charAt(0).toUpperCase();
    }
    
    // Llenar datos
    document.getElementById('detalle-cliente-inicial').textContent = inicial;
    document.getElementById('detalle-cliente-id').textContent = cliente.id || cliente.rif || '-';
    document.getElementById('detalle-cliente-tipo').textContent = tipo === 'natural' ? 'Persona Natural' : 'Persona Jurídica';
    
    if (tipo === 'natural') {
        document.getElementById('detalle-cliente-nombre').textContent = `${cliente.nombre || ''} ${cliente.apellido || ''}`.trim() || '-';
        document.getElementById('detalle-cliente-apellido-rif').textContent = cliente.apellido || '-';
        document.getElementById('detalle-cliente-celular').textContent = cliente.celular || 'No registrado';
    } else {
        document.getElementById('detalle-cliente-nombre').textContent = cliente.razon_social || cliente.nombre || '-';
        document.getElementById('detalle-cliente-apellido-rif').textContent = cliente.rif || '-';
        document.getElementById('detalle-cliente-celular').textContent = cliente.telefono || cliente.celular || 'No registrado';
    }
    
    document.getElementById('detalle-cliente-correo').textContent = cliente.correo || 'No registrado';
    document.getElementById('detalle-cliente-direccion').textContent = cliente.direccion || 'No registrada';
    
    modal.removeAttribute('hidden');
    modal.setAttribute('aria-hidden', 'false');
}

function cerrarModalVerCliente() {
    const modal = document.getElementById('modal-ver-cliente');
    if (modal) {
        modal.setAttribute('hidden', '');
        modal.setAttribute('aria-hidden', 'true');
    }
}

// ==================== VALIDACIÓN RIF ====================

function formatearRIF(input) {
    let valor = input.value.replace(/[^a-zA-Z0-9]/g, '');
    valor = valor.toUpperCase();
    
    if (valor.length === 0) {
        input.value = '';
        return;
    }
    
    if (!['J', 'E'].includes(valor.charAt(0))) {
        valor = 'J' + valor.substring(1);
    }
    
    const letra = valor.charAt(0);
    let numeros = valor.substring(1);
    numeros = numeros.substring(0, 9);
    
    let resultado = letra;
    if (numeros.length > 0) {
        resultado += '-';
        if (numeros.length <= 8) {
            resultado += numeros;
        } else {
            resultado += numeros.substring(0, 8) + '-' + numeros.substring(8);
        }
    }
    
    input.value = resultado;
}

function validarRIF(valor) {
    const patronRIF = /^[JE]-\d{8}-\d$/;
    
    if (!patronRIF.test(valor)) {
        return { 
            valido: false, 
            mensaje: 'El RIF debe tener el formato: J-12345678-9 o E-12345678-9' 
        };
    }
    
    if (valor.length !== 12) {
        return { 
            valido: false, 
            mensaje: 'El RIF debe tener 12 caracteres (ej: J-12345678-9)' 
        };
    }
    
    const partes = valor.split('-');
    if (partes.length !== 3) {
        return { 
            valido: false, 
            mensaje: 'El RIF debe tener el formato: Letra-8dígitos-1dígito' 
        };
    }
    
    const letraParte = partes[0];
    const numerosParte1 = partes[1];
    const numerosParte2 = partes[2];
    
    if (!['J', 'E'].includes(letraParte)) {
        return { 
            valido: false, 
            mensaje: 'La primera parte debe ser J o E' 
        };
    }
    
    if (numerosParte1.length !== 8 || !/^\d{8}$/.test(numerosParte1)) {
        return { 
            valido: false, 
            mensaje: 'Debe tener 8 dígitos después del primer guion' 
        };
    }
    
    if (numerosParte2.length !== 1 || !/^\d$/.test(numerosParte2)) {
        return { 
            valido: false, 
            mensaje: 'Debe tener 1 dígito después del segundo guion' 
        };
    }
    
    return { valido: true };
}

function validarRIFEnTiempoReal(input) {
    const errorElement = document.getElementById('rif-error');
    if (!errorElement) return;
    
    const valor = input.value;
    if (!valor) {
        errorElement.textContent = '';
        errorElement.style.color = '';
        input.classList.remove('field-error', 'field-success');
        return;
    }
    
    const resultado = validarRIF(valor);
    if (!resultado.valido) {
        errorElement.textContent = resultado.mensaje;
        errorElement.style.color = '#ef4444';
        input.classList.add('field-error');
        input.classList.remove('field-success');
    } else {
        errorElement.textContent = '✓ Formato válido';
        errorElement.style.color = '#22c55e';
        input.classList.remove('field-error');
        input.classList.add('field-success');
    }
}

// ==================== VALIDACIÓN TELÉFONO ====================

function validarTelefono(telefono) {
    if (!telefono) return { valido: false, mensaje: 'El teléfono es obligatorio' };
    
    const telefonoLimpio = telefono.replace(/\D/g, '');
    
    if (telefonoLimpio.length !== 11) {
        return { 
            valido: false, 
            mensaje: 'El teléfono debe tener exactamente 11 dígitos' 
        };
    }
    
    const prefijo = telefonoLimpio.substring(0, 4);
    const prefijosPermitidos = ['0416', '0426', '0414', '0424', '0412', '0422', '0251'];
    
    if (!prefijosPermitidos.includes(prefijo)) {
        return { 
            valido: false, 
            mensaje: `El prefijo ${prefijo} no está permitido. Use: 0416, 0426, 0414, 0424, 0412, 0422 o 0251` 
        };
    }
    
    return { valido: true };
}

function validarTelefonoEnTiempoReal(input) {
    const errorId = input.name + '-error';
    const errorElement = document.getElementById(errorId);
    if (!errorElement) return;
    
    const valor = input.value;
    if (!valor) {
        errorElement.textContent = '';
        errorElement.style.color = '';
        input.classList.remove('field-error', 'field-success');
        return;
    }
    
    const resultado = validarTelefono(valor);
    if (!resultado.valido) {
        errorElement.textContent = '✗ ' + resultado.mensaje;
        errorElement.style.color = '#ef4444';
        input.classList.add('field-error');
        input.classList.remove('field-success');
    } else {
        errorElement.textContent = '✓ Teléfono válido';
        errorElement.style.color = '#22c55e';
        input.classList.remove('field-error');
        input.classList.add('field-success');
    }
}

function formatearTelefono(input) {
    let valor = input.value.replace(/\D/g, '');
    if (valor.length > 11) {
        valor = valor.substring(0, 11);
    }
    input.value = valor;
}

// ==================== VALIDACIÓN RAZÓN SOCIAL ====================

function validarRazonSocial(valor) {
    if (!valor || valor.trim() === '') {
        return { valido: false, mensaje: 'La razón social es obligatoria' };
    }
    
    const patronRazonSocial = /^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\.\-&]+$/;
    
    if (!patronRazonSocial.test(valor)) {
        return { 
            valido: false, 
            mensaje: 'Solo letras, números, puntos, guiones, espacios y &' 
        };
    }
    
    if (valor.length > 60) {
        return { 
            valido: false, 
            mensaje: 'No puede exceder los 60 caracteres' 
        };
    }
    
    return { valido: true };
}

function validarRazonSocialEnTiempoReal(input) {
    const errorElement = document.getElementById('razon-social-error');
    if (!errorElement) return;
    
    const valor = input.value;
    if (!valor) {
        errorElement.textContent = '';
        errorElement.style.color = '';
        input.classList.remove('field-error', 'field-success');
        return;
    }
    
    const resultado = validarRazonSocial(valor);
    if (!resultado.valido) {
        errorElement.textContent = '✗ ' + resultado.mensaje;
        errorElement.style.color = '#ef4444';
        input.classList.add('field-error');
        input.classList.remove('field-success');
    } else {
        errorElement.textContent = '✓ Válido';
        errorElement.style.color = '#22c55e';
        input.classList.remove('field-error');
        input.classList.add('field-success');
    }
}

// ==================== VALIDACIÓN FORMULARIO ====================

function validarFormularioAntesDeEnviar(form, nombreFormulario) {
    if (!window.FieldValidator) {
        console.warn('FieldValidator no disponible');
        return true;
    }
    
    const isValid = window.FieldValidator.validateForm(form);
    
    if (!isValid) {
        mostrarToast(`Por favor, corrige los errores en el formulario de ${nombreFormulario}.`, true);
        
        const primerError = form.querySelector('.field-error');
        if (primerError) {
            primerError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            primerError.focus();
        }
        
        return false;
    }
    
    return true;
}

// ==================== MOSTRAR/OCULTAR CAMPOS POR TIPO ====================

function toggleCamposPorTipo() {
    const tipo = tipoClienteSelect?.value;
    const camposNatural = document.getElementById("campos-natural");
    const camposJuridico = document.getElementById("campos-juridico");
    const inputsNatural = camposNatural?.querySelectorAll("input, select");
    const inputsJuridico = camposJuridico?.querySelectorAll("input, select");
    
    if (tipo === "natural") {
        if (camposNatural) camposNatural.style.display = "grid";
        if (camposJuridico) camposJuridico.style.display = "none";

        inputsNatural?.forEach(input => {
            input.required = NATURAL_REQUIRED_FIELDS.has(input.name);
        });
        inputsJuridico?.forEach(input => {
            input.required = false;
            if (input.name !== "tipo_cliente") {
                input.value = "";
            }
        });
    } else if (tipo === "juridico") {
        if (camposNatural) camposNatural.style.display = "none";
        if (camposJuridico) camposJuridico.style.display = "grid";

        inputsJuridico?.forEach(input => {
            input.required = JURIDICO_REQUIRED_FIELDS.has(input.name);
        });
        inputsNatural?.forEach(input => {
            input.required = false;
            if (input.name !== "tipo_cliente") {
                input.value = "";
            }
        });
    } else {
        if (camposNatural) camposNatural.style.display = "none";
        if (camposJuridico) camposJuridico.style.display = "none";
        inputsNatural?.forEach(input => input.required = false);
        inputsJuridico?.forEach(input => input.required = false);
    }
    
    if (window.FieldValidator) {
        setTimeout(() => window.FieldValidator.init(), 50);
        if (typeof window.FieldValidator.resetForm === 'function') {
            window.FieldValidator.resetForm(formCliente);
        }
    }
}

// ==================== INICIALIZACIÓN ====================

function initClientes() {
    btnNuevoCliente?.addEventListener("click", abrirFormularioNuevo);
    formCliente?.addEventListener("submit", onSubmitCliente);
    tipoClienteSelect?.addEventListener("change", toggleCamposPorTipo);
    inputBuscarClientes?.addEventListener("input", onBuscarClientes);
    filtroTipoCliente?.addEventListener("change", onFiltrarTipo);
    document.addEventListener("click", onTablaClick);
    cargarClientes();
    
    initRIFAutocomplete();
    initRazonSocialValidation();
    initTelefonoValidation();
    initModalEliminar();
    initModalVerCliente();
}

function initRIFAutocomplete() {
    const rifInput = document.getElementById('rif-input');
    if (!rifInput) return;
    
    rifInput.addEventListener('input', function() {
        const start = this.selectionStart;
        const oldLength = this.value.length;
        
        formatearRIF(this);
        
        const newLength = this.value.length;
        const diff = newLength - oldLength;
        let newPos = start + diff;
        
        if (this.value.charAt(newPos - 1) === '-') {
            newPos = newPos + 1;
        }
        if (newPos > this.value.length) {
            newPos = this.value.length;
        }
        
        this.setSelectionRange(newPos, newPos);
        validarRIFEnTiempoReal(this);
    });
    
    rifInput.addEventListener('blur', function() {
        if (this.value) {
            const limpio = this.value.replace(/[^a-zA-Z0-9]/g, '');
            if (limpio.length >= 9) {
                const letra = limpio.charAt(0);
                const numeros = limpio.substring(1);
                if (numeros.length >= 8) {
                    const verificador = numeros.length > 8 ? numeros.charAt(8) : '';
                    this.value = `${letra}-${numeros.substring(0, 8)}${verificador ? '-' + verificador : ''}`;
                }
            }
            validarRIFEnTiempoReal(this);
        }
    });
    
    rifInput.addEventListener('keydown', function(e) {
        const teclasPermitidas = [
            'Backspace', 'Delete', 'Tab', 'Escape', 'Enter',
            'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
            'Home', 'End', 'PageUp', 'PageDown'
        ];
        
        if (teclasPermitidas.includes(e.key)) {
            return;
        }
        
        if (!/^[a-zA-Z0-9]$/.test(e.key)) {
            e.preventDefault();
        }
    });
    
    rifInput.addEventListener('keyup', function() {
        if (this.value.length > 12) {
            this.value = this.value.substring(0, 12);
        }
    });
}

function initRazonSocialValidation() {
    const razonSocialInput = document.getElementById('razon-social-input');
    if (!razonSocialInput) return;
    
    razonSocialInput.addEventListener('input', function() {
        validarRazonSocialEnTiempoReal(this);
    });
    
    razonSocialInput.addEventListener('blur', function() {
        if (this.value) {
            validarRazonSocialEnTiempoReal(this);
        }
    });
}

function initTelefonoValidation() {
    const telefonos = document.querySelectorAll('input[name="celular"], input[name="telefono"]');
    
    telefonos.forEach(input => {
        let errorElement = input.parentElement.querySelector('.field-error');
        if (!errorElement) {
            errorElement = document.createElement('small');
            errorElement.className = 'field-error';
            errorElement.id = input.name + '-error';
            input.parentElement.appendChild(errorElement);
        }
        
        input.addEventListener('input', function() {
            formatearTelefono(this);
            validarTelefonoEnTiempoReal(this);
        });
        
        input.addEventListener('blur', function() {
            if (this.value) {
                validarTelefonoEnTiempoReal(this);
            }
        });
    });
}

function initModalEliminar() {
    const confirmBtn = document.getElementById('btn-confirmar-eliminar-cliente');
    if (confirmBtn) {
        confirmBtn.removeEventListener('click', confirmarEliminarCliente);
        confirmBtn.addEventListener('click', confirmarEliminarCliente);
    }
    
    const modal = document.getElementById('modal-eliminar-cliente');
    if (modal) {
        const overlay = modal.querySelector('.modal__overlay');
        if (overlay) {
            overlay.removeEventListener('click', cerrarModalEliminar);
            overlay.addEventListener('click', cerrarModalEliminar);
        }
    }
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modal = document.getElementById('modal-eliminar-cliente');
            if (modal && !modal.hasAttribute('hidden')) {
                cerrarModalEliminar();
            }
        }
    });
}

function initModalVerCliente() {
    const modal = document.getElementById('modal-ver-cliente');
    if (modal) {
        const overlay = modal.querySelector('.modal__overlay');
        if (overlay) {
            overlay.removeEventListener('click', cerrarModalVerCliente);
            overlay.addEventListener('click', cerrarModalVerCliente);
        }
    }
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modal = document.getElementById('modal-ver-cliente');
            if (modal && !modal.hasAttribute('hidden')) {
                cerrarModalVerCliente();
            }
        }
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initClientes);
} else {
    initClientes();
}

// ==================== FUNCIONES DE UI ====================

function abrirFormularioNuevo() {
    limpiarFormulario();
    modoEdicion = false;
    
    const tipoSelect = document.getElementById('tipo-cliente');
    if (tipoSelect) {
        tipoSelect.value = "";
        tipoSelect.disabled = false;
    }
    
    toggleCamposPorTipo();
    if (window.UiModal && typeof window.UiModal.openById === "function") {
        window.UiModal.openById("modal-cliente");
        if (window.FieldValidator) {
            setTimeout(() => window.FieldValidator.init(), 100);
        }
    }
}

function onTablaClick(event) {
    const btn = event.target.closest("button[data-action]");
    if (!btn) return;

    const id = btn.dataset.id;
    const action = btn.dataset.action;
    if (!id || !action) return;

    if (action === "edit") {
        abrirEdicion(id);
        return;
    }

    if (action === "delete") {
        eliminarCliente(id);
        return;
    }
    
    if (action === "view") {
        abrirModalVerCliente(id);
        return;
    }
}

// ==================== CRUD ====================

async function cargarClientes() {
    try {
        const data = await fetchJson("/api/clientes");
        clientes = Array.isArray(data.clientes) ? data.clientes : [];
        renderClientes();
    } catch (error) {
        mostrarToast(error.message || "No se pudo cargar la lista de clientes.", true);
    }
}

function renderClientes() {
    if (!tablaClientes) return;
    if (!Array.isArray(clientes)) {
        clientes = [];
    }

    const listaFiltrada = clientes.filter(cliente => {
        const tipo = getTipoCliente(cliente);
        const textoBusqueda = [
            cliente.id,
            cliente.nombre,
            cliente.apellido,
            cliente.razon_social,
            cliente.rif,
            cliente.correo,
            cliente.direccion,
        ]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();

        if (searchQuery && !textoBusqueda.includes(searchQuery.toLowerCase())) {
            return false;
        }

        if (tipoFilter && tipo !== tipoFilter) {
            return false;
        }

        return true;
    });

    const totalClientes = clientes.length;
    const totalNatural = clientes.filter(c => getTipoCliente(c) === "natural").length;
    const totalJuridico = clientes.filter(c => getTipoCliente(c) === "juridico").length;

    if (statClientes) statClientes.textContent = String(totalClientes);
    if (statNatural) statNatural.textContent = String(totalNatural);
    if (statJuridico) statJuridico.textContent = String(totalJuridico);

    if (!listaFiltrada.length) {
        tablaClientes.innerHTML = `<tr><td colspan="8" class="table__empty">No hay clientes registrados que coincidan con la búsqueda.</td></tr>`;
        return;
    }

    tablaClientes.innerHTML = listaFiltrada
        .map((cliente) => {
            const tipo = getTipoCliente(cliente);
            const nombreDisplay = tipo === "natural"
                ? escapeHtml(cliente.nombre || "")
                : escapeHtml(cliente.razon_social || cliente.nombre || "");
            const segundoValor = tipo === "natural"
                ? escapeHtml(cliente.apellido || "")
                : escapeHtml(cliente.rif || "");
            const celular = escapeHtml(cliente.celular || cliente.telefono || "");
            const correo = escapeHtml(cliente.correo || "");
            const direccion = escapeHtml(cliente.direccion || "");
            const clienteId = escapeHtml(String(cliente.id || cliente.rif || ""));

            return `
                <tr>
                    <td class="col-id"><span class="chip">${clienteId}</span></td>
                    <td><span class="badge ${tipo === 'natural' ? 'badge--natural' : 'badge--juridico'}">${tipo === 'natural' ? 'Persona Natural' : 'Persona Jurídica'}</span></td>
                    <td>${nombreDisplay}</td>
                    <td>${segundoValor}</td>
                    <td>${celular}</td>
                    <td>${correo}</td>
                    <td>${direccion}</td>
                    <td class="table__actions">
                        <div class="row-actions">
                            <button class="icon-action" type="button" data-action="edit" data-id="${clienteId}" title="Editar">
                                ${Iconos.lapiz}
                            </button>
                            <button class="icon-action" type="button" data-action="view" data-id="${clienteId}" title="Ver detalles">
                                ${Iconos.ojo}
                            </button>
                            <button class="icon-action icon-action--danger" type="button" data-action="delete" data-id="${clienteId}" title="Eliminar">
                                ${Iconos.basura}
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        })
        .join("");
}

function abrirEdicion(id) {
    const cliente = clientes.find((item) => String(item.id) === String(id) || String(item.rif) === String(id));
    if (!cliente || !formCliente) return;

    limpiarFormulario();
    modoEdicion = true;

    const tipo = getTipoCliente(cliente);
    const tipoSelect = document.getElementById('tipo-cliente');
    
    if (tipoSelect) {
        tipoSelect.value = tipo;
        tipoSelect.disabled = true;
    }
    
    toggleCamposPorTipo();

    if (tipo === "natural") {
        const nombreCompleto = cliente.nombre || "";
        const espacioIndex = nombreCompleto.indexOf(' ');
        let nombre = nombreCompleto;
        let apellido = cliente.apellido || "";
        if (espacioIndex > 0) {
            nombre = nombreCompleto.substring(0, espacioIndex);
            apellido = nombreCompleto.substring(espacioIndex + 1);
        }

        setFieldValue("cedula", String(cliente.id || ""));
        setFieldValue("nombre", nombre);
        setFieldValue("apellido", apellido);
        setFieldValue("celular", cliente.celular || cliente.telefono || "");
        setFieldValue("correo", cliente.correo || "");
        setFieldValue("direccion", cliente.direccion || "");
    } else {
        const rifLimpio = cliente.rif || String(cliente.id || "");
        let rifFormateado = rifLimpio;
        if (rifLimpio.length >= 9) {
            const letra = rifLimpio.charAt(0);
            const numeros = rifLimpio.substring(1);
            if (numeros.length >= 8) {
                rifFormateado = `${letra}-${numeros.substring(0, 8)}-${numeros.charAt(8) || ''}`;
            }
        }
        
        setFieldValue("rif", rifFormateado);
        setFieldValue("razon_social", cliente.razon_social || cliente.nombre || "");
        setFieldValue("telefono", cliente.celular || cliente.telefono || "");
        setFieldValue("correo_juridico", cliente.correo || "");
        setFieldValue("direccion_juridico", cliente.direccion || "");
    }

    if (clienteIdInput) {
        clienteIdInput.value = String(cliente.id || cliente.rif || "");
    }
    formCliente.dataset.editing = "true";

    if (window.UiModal && typeof window.UiModal.openById === "function") {
        window.UiModal.openById("modal-cliente");
        if (window.FieldValidator) {
            setTimeout(() => window.FieldValidator.init(), 100);
        }
    }
}

async function onSubmitCliente(event) {
    event.preventDefault();
    
    if (!validarFormularioAntesDeEnviar(formCliente, 'cliente')) {
        return;
    }

    const tipo = tipoClienteSelect?.value;
    let payload = {};
    let url = "";
    let method = "";
    
    const isEdit = formCliente.dataset.editing === "true";
    const clienteId = clienteIdInput?.value || "";

    if (tipo === "natural") {
        const cedula = getFieldValue("cedula");
        const nombre = getFieldValue("nombre");
        const apellido = getFieldValue("apellido");
        const celular = getFieldValue("celular");
        const correo = getFieldValue("correo");
        const direccion = getFieldValue("direccion");

        if (!cedula || !nombre || !apellido || !celular) {
            mostrarToast("Cédula, nombre, apellido y celular son obligatorios.", true);
            return;
        }

        if (!/^\d+$/.test(cedula)) {
            mostrarToast("La cédula debe contener solo números.", true);
            return;
        }

        const resultadoTelefono = validarTelefono(celular);
        if (!resultadoTelefono.valido) {
            mostrarToast(resultadoTelefono.mensaje, true);
            const telefonoInput = document.querySelector('input[name="celular"]');
            if (telefonoInput) {
                telefonoInput.focus();
                telefonoInput.classList.add('field-error');
            }
            return;
        }

        payload = {
            Id_cliente: cedula,
            nombre_cliente: nombre,
            apellido_cliente: apellido,
            direccion_cliente: direccion,
            telefono_cliente: celular,
            correo_cliente: correo,
        };

        if (isEdit) {
            if (!clienteId) {
                mostrarToast("No se encontró el cliente a actualizar.", true);
                return;
            }
            url = `/api/clientes/natural/${encodeURIComponent(clienteId)}`;
            method = "PUT";
        } else {
            url = "/api/clientes/natural";
            method = "POST";
        }
    } else if (tipo === "juridico") {
        const rifInput = document.getElementById('rif-input');
        const razonSocialInput = document.getElementById('razon-social-input');
        const rif = getFieldValue("rif");
        const razonSocial = getFieldValue("razon_social");
        const telefono = getFieldValue("telefono");
        const correo = getFieldValue("correo_juridico");
        const direccion = getFieldValue("direccion_juridico");

        if (!rif) {
            mostrarToast("El RIF es obligatorio.", true);
            if (rifInput) rifInput.focus();
            return;
        }

        const patronRIF = /^[JE]-\d{8}-\d$/;
        if (!patronRIF.test(rif)) {
            mostrarToast("El RIF debe tener el formato: J-12345678-9 o E-12345678-9 (12 caracteres)", true);
            if (rifInput) {
                rifInput.focus();
                rifInput.classList.add('field-error');
                const errorElement = document.getElementById('rif-error');
                if (errorElement) {
                    errorElement.textContent = "Formato inválido: Use J-12345678-9 o E-12345678-9";
                    errorElement.style.color = '#ef4444';
                }
            }
            return;
        }

        if (!razonSocial) {
            mostrarToast("La razón social es obligatoria.", true);
            if (razonSocialInput) razonSocialInput.focus();
            return;
        }
        
        const resultadoRazonSocial = validarRazonSocial(razonSocial);
        if (!resultadoRazonSocial.valido) {
            mostrarToast(resultadoRazonSocial.mensaje, true);
            if (razonSocialInput) {
                razonSocialInput.focus();
                razonSocialInput.classList.add('field-error');
                const errorElement = document.getElementById('razon-social-error');
                if (errorElement) {
                    errorElement.textContent = resultadoRazonSocial.mensaje;
                    errorElement.style.color = '#ef4444';
                }
            }
            return;
        }

        if (!telefono) {
            mostrarToast("El teléfono es obligatorio.", true);
            return;
        }

        const resultadoTelefono = validarTelefono(telefono);
        if (!resultadoTelefono.valido) {
            mostrarToast(resultadoTelefono.mensaje, true);
            const telefonoInput = document.querySelector('input[name="telefono"]');
            if (telefonoInput) {
                telefonoInput.focus();
                telefonoInput.classList.add('field-error');
            }
            return;
        }

        payload = {
            Id_cliente: rif,
            razon_social: razonSocial,
            rif: rif,
            direccion_cliente: direccion,
            telefono_cliente: telefono,
            correo_cliente: correo,
        };

        if (isEdit) {
            if (!clienteId) {
                mostrarToast("No se encontró el cliente a actualizar.", true);
                return;
            }
            url = `/api/clientes/juridico/${encodeURIComponent(clienteId)}`;
            method = "PUT";
        } else {
            url = "/api/clientes/juridico";
            method = "POST";
        }
    } else {
        mostrarToast("Seleccione el tipo de cliente.", true);
        return;
    }

    try {
        await fetchJson(url, { method, body: JSON.stringify(payload) });
        mostrarToast(isEdit ? "Cliente actualizado exitosamente." : "Cliente creado exitosamente.");
        limpiarFormulario();
        if (window.UiModal && typeof window.UiModal.closeById === "function") {
            window.UiModal.closeById("modal-cliente");
        }
        cargarClientes();
    } catch (error) {
        console.error('Error al guardar cliente:', error);
        mostrarToast(error.message || "No se pudo guardar el cliente.", true);
    }
}

function onBuscarClientes(event) {
    searchQuery = String(event.target.value || "").trim();
    renderClientes();
}

function onFiltrarTipo(event) {
    tipoFilter = String(event.target.value || "").trim();
    renderClientes();
}

function eliminarCliente(id) {
    const cliente = clientes.find((item) => String(item.id) === String(id) || String(item.rif) === String(id));
    
    let nombreCliente = id;
    if (cliente) {
        const tipo = getTipoCliente(cliente);
        nombreCliente = tipo === "natural" 
            ? `${cliente.nombre || ''} ${cliente.apellido || ''}`.trim() || id
            : cliente.razon_social || cliente.nombre || id;
    }
    
    abrirModalEliminar(id, nombreCliente);
}

function limpiarFormulario() {
    if (!formCliente) return;
    formCliente.reset();
    if (clienteIdInput) {
        clienteIdInput.value = "";
    }
    delete formCliente.dataset.editing;
    modoEdicion = false;
    
    const tipoSelect = document.getElementById('tipo-cliente');
    if (tipoSelect) {
        tipoSelect.disabled = false;
        tipoSelect.value = "";
    }

    const rifError = document.getElementById('rif-error');
    if (rifError) {
        rifError.textContent = '';
        rifError.style.color = '';
    }
    const rifInput = document.getElementById('rif-input');
    if (rifInput) {
        rifInput.classList.remove('field-error', 'field-success');
    }

    const razonSocialError = document.getElementById('razon-social-error');
    if (razonSocialError) {
        razonSocialError.textContent = '';
        razonSocialError.style.color = '';
    }
    const razonSocialInput = document.getElementById('razon-social-input');
    if (razonSocialInput) {
        razonSocialInput.classList.remove('field-error', 'field-success');
    }

    const telefonos = document.querySelectorAll('input[name="celular"], input[name="telefono"]');
    telefonos.forEach(input => {
        input.classList.remove('field-error', 'field-success');
        const errorElement = document.getElementById(input.name + '-error');
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.style.color = '';
        }
    });

    if (window.FieldValidator) {
        window.FieldValidator.resetForm(formCliente);
    }
    
    const camposNatural = document.getElementById("campos-natural");
    const camposJuridico = document.getElementById("campos-juridico");
    if (camposNatural) {
        camposNatural.querySelectorAll("input").forEach(input => input.value = "");
    }
    if (camposJuridico) {
        camposJuridico.querySelectorAll("input").forEach(input => input.value = "");
    }
    
    if (window.FieldValidator) {
        window.FieldValidator.resetForm(formCliente);
    }
}

function getFieldValue(fieldName) {
    const field = formCliente?.elements?.namedItem(fieldName);
    return field && "value" in field ? String(field.value).trim() : "";
}

function setFieldValue(fieldName, value) {
    const field = formCliente?.elements?.namedItem(fieldName);
    if (field && "value" in field) {
        field.value = value;
    }
}

// ==================== FETCH ====================

async function fetchJson(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
                ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
            },
            credentials: "same-origin",
            ...options,
        });

        let data;
        try {
            data = await response.json();
        } catch (e) {
            data = { success: false, message: 'Error al procesar la respuesta del servidor' };
        }

        if (!response.ok || data.success === false) {
            const errorMsg = data.message || data.error || `Error ${response.status}: ${response.statusText}`;
            throw new Error(errorMsg);
        }

        return data;
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// ==================== UTILITIES ====================

function mostrarToast(message, isError = false) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.toggle("toast--error", isError);
    toast.classList.add("is-visible");
    window.clearTimeout(mostrarToast._timer);
    mostrarToast._timer = window.setTimeout(() => {
        toast.classList.remove("is-visible");
    }, 2600);
}

function getTipoCliente(cliente) {
    if (!cliente) return "";
    if (cliente.rif || cliente.razon_social || cliente.tipo === "juridico") {
        return "juridico";
    }
    return "natural";
}

function escapeHtml(text) {
    if (text === null || text === undefined) return "";
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}