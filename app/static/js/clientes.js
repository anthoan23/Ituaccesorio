// ============================================
// CLIENTES - JavaScript corregido
// ============================================

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

// ==================== FUNCIONES PARA CAPITALIZAR ====================

function capitalizarInput(event) {
    const input = event.target;
    const valor = input.value;
    if (!valor) return;
    const primeraLetra = valor.charAt(0).toUpperCase();
    const resto = valor.slice(1);
    input.value = primeraLetra + resto;
    const end = input.value.length;
    input.setSelectionRange(end, end);
}

function capitalizarAlPerderFoco(event) {
    const input = event.target;
    if (input.value) {
        const primeraLetra = input.value.charAt(0).toUpperCase();
        const resto = input.value.slice(1);
        input.value = primeraLetra + resto;
    }
}

// ==================== MODAL ELIMINACIÓN ====================

function abrirModalEliminar(clienteId, nombreCliente) {
    const modal = document.getElementById('modal-eliminar-cliente');
    if (!modal) return;
    const confirmText = document.getElementById('texto-confirmar-eliminar-cliente');
    if (confirmText) confirmText.textContent = `¿Estás seguro de que quieres eliminar a "${nombreCliente}"?`;
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

// ==================== MODAL DETALLES ====================

function abrirModalVerCliente(clienteId) {
    const cliente = clientes.find((item) => String(item.id) === String(clienteId) || String(item.rif) === String(clienteId));
    if (!cliente) {
        mostrarToast('Cliente no encontrado.', true);
        return;
    }
    const modal = document.getElementById('modal-ver-cliente');
    if (!modal) return;
    const tipo = getTipoCliente(cliente);
    let inicial = tipo === 'natural' ? (cliente.nombre || '?').charAt(0).toUpperCase() : (cliente.razon_social || cliente.nombre || '?').charAt(0).toUpperCase();
    
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

// ==================== VERIFICACIÓN DE DUPLICADOS ====================

function verificarDuplicadoEnTabla(valor, columna, tablaSelector) {
    const filas = document.querySelectorAll(`${tablaSelector} tr`);
    let esDuplicado = false;
    filas.forEach(fila => {
        const celdas = fila.querySelectorAll('td');
        if (celdas.length > columna) {
            const textoCelda = celdas[columna].textContent.trim();
            if (textoCelda === valor && valor !== '') {
                esDuplicado = true;
            }
        }
    });
    return esDuplicado;
}

// ==================== VALIDACIONES Y RENDERIZADO ====================

function validarNombreEnTiempoReal(input) {
    const errorElement = document.getElementById('nombre-error');
    if (!errorElement) return;
    const valor = input.value;
    
    if (!valor) {
        errorElement.textContent = '';
        input.classList.remove('field-error', 'field-success');
        return;
    }
    
    if (valor.trim().length < 3) {
        errorElement.textContent = '✗ Mínimo 3 letras';
        errorElement.style.color = '#ef4444';
        input.classList.add('field-error');
        input.classList.remove('field-success');
        return;
    }

    if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(valor) || valor.length > 20) {
        errorElement.textContent = '✗ Solo letras (máx. 20)';
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

function validarApellidoEnTiempoReal(input) {
    const errorElement = document.getElementById('apellido-error');
    if (!errorElement) return;
    const valor = input.value;
    
    if (!valor) {
        errorElement.textContent = '';
        input.classList.remove('field-error', 'field-success');
        return;
    }
    
    if (valor.trim().length < 3) {
        errorElement.textContent = '✗ Mínimo 3 letras';
        errorElement.style.color = '#ef4444';
        input.classList.add('field-error');
        input.classList.remove('field-success');
        return;
    }

    if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(valor) || valor.length > 20) {
        errorElement.textContent = '✗ Solo letras (máx. 20)';
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

function validarRazonSocialEnTiempoReal(input) {
    const errorElement = document.getElementById('razon-social-error');
    if (!errorElement) return;
    const valor = input.value;
    
    if (!valor) {
        errorElement.textContent = '';
        input.classList.remove('field-error', 'field-success');
        return;
    }
    if (valor.trim().length < 3 || !/^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\.\-&]+$/.test(valor) || valor.length > 60) {
        errorElement.textContent = '✗ Válido (3 a 60 caracteres)';
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

function validarCedula(input) {
    const valor = input.value.trim();
    const errorElement = document.getElementById('cedula-error');
    if (!errorElement) return;
    
    const tipoSelect = document.getElementById('tipo-cliente');
    
    if (!valor) {
        errorElement.textContent = '';
        input.classList.remove('field-error', 'field-success');
        return;
    }
    if (!/^\d{7,8}$/.test(valor)) {
        errorElement.textContent = '✗ Debe tener 7 u 8 dígitos';
        errorElement.style.color = '#ef4444';
        input.classList.add('field-error');
        input.classList.remove('field-success');
        return;
    }
    
    const isEdit = document.getElementById('form-cliente')?.dataset?.editing === 'true';
    if (!isEdit && verificarDuplicadoEnTabla(valor, 0, '#tabla-clientes')) {
        errorElement.textContent = `✗ La cédula "${valor}" ya está registrada`;
        errorElement.style.color = '#ef4444';
        input.classList.add('field-error');
        input.classList.remove('field-success');
        if (tipoSelect) {
            tipoSelect.classList.remove('field-success');
            tipoSelect.classList.add('field-error');
        }
        mostrarToast(`La cédula "${valor}" ya está registrada.`, true);
        return;
    }
    
    errorElement.textContent = '✓ Cédula disponible';
    errorElement.style.color = '#22c55e';
    input.classList.remove('field-error');
    input.classList.add('field-success');
    if (tipoSelect) {
        tipoSelect.classList.remove('field-error');
        tipoSelect.classList.add('field-success');
    }
}

function validarRIF(input) {
    const valor = input.value;
    const errorElement = document.getElementById('rif-error');
    if (!errorElement) return;
    
    if (!valor || valor.trim() === '') {
        errorElement.textContent = '';
        input.classList.remove('field-error', 'field-success');
        return;
    }
    
    if (!/^[JE]-\d{8}-\d$/.test(valor)) {
        errorElement.textContent = '✗ Formato inválido. Use J-12345678-9';
        errorElement.style.color = '#ef4444';
        input.classList.add('field-error');
        input.classList.remove('field-success');
        return;
    }
    
    const isEdit = document.getElementById('form-cliente')?.dataset?.editing === 'true';
    if (!isEdit && verificarDuplicadoEnTabla(valor, 0, '#tabla-clientes')) {
        errorElement.textContent = `✗ El RIF "${valor}" ya está registrado`;
        errorElement.style.color = '#ef4444';
        input.classList.add('field-error');
        input.classList.remove('field-success');
        mostrarToast(`El RIF "${valor}" ya está registrado.`, true);
        return;
    }
    
    errorElement.textContent = '✓ RIF disponible';
    errorElement.style.color = '#22c55e';
    input.classList.remove('field-error');
    input.classList.add('field-success');
}

function validarTelefonoEnTiempoReal(input) {
    const errorId = input.name + '-error';
    const errorElement = document.getElementById(errorId);
    if (!errorElement) return;
    const valor = input.value;
    
    if (!valor) {
        errorElement.textContent = '';
        input.classList.remove('field-error', 'field-success');
        return;
    }
    
    const limpio = valor.replace(/\D/g, '');
    const prefijo = limpio.substring(0, 4);
    const prefijosPermitidos = ['0416', '0426', '0414', '0424', '0412', '0422', '0251'];
    
    if (limpio.length !== 11 || !prefijosPermitidos.includes(prefijo)) {
        errorElement.textContent = '✗ Formato inválido (11 dígitos)';
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

function validarCorreoEnTiempoReal(input) {
    const errorId = input.name + '-error';
    let errorElement = document.getElementById(errorId);
    if (!errorElement) {
        errorElement = document.createElement('small');
        errorElement.className = 'field-error';
        errorElement.id = errorId;
        input.parentElement.appendChild(errorElement);
    }
    
    const valor = input.value.trim();
    if (!valor) {
        errorElement.textContent = '';
        input.classList.remove('field-error', 'field-success');
        return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(valor)) {
        errorElement.textContent = '✗ Correo no válido';
        errorElement.style.color = '#ef4444';
        input.classList.add('field-error');
        input.classList.remove('field-success');
    } else {
        errorElement.textContent = '✓ Correo válido';
        errorElement.style.color = '#22c55e';
        input.classList.remove('field-error');
        input.classList.add('field-success');
    }
}

function validarDireccionEnTiempoReal(input) {
    const errorId = input.name + '-error';
    let errorElement = document.getElementById(errorId);
    if (!errorElement) {
        errorElement = document.createElement('small');
        errorElement.className = 'field-error';
        errorElement.id = errorId;
        input.parentElement.appendChild(errorElement);
    }
    
    const valor = input.value.trim();
    if (!valor) {
        errorElement.textContent = '';
        input.classList.remove('field-error', 'field-success');
        return;
    }
    if (valor.length > 40) {
        errorElement.textContent = '✗ Máximo 40 caracteres';
        errorElement.style.color = '#ef4444';
        input.classList.add('field-error');
        input.classList.remove('field-success');
    } else {
        errorElement.textContent = '✓ Dirección válida';
        errorElement.style.color = '#22c55e';
        input.classList.remove('field-error');
        input.classList.add('field-success');
    }
}

function formatearRIF(input) {
    let valor = input.value;
    let limpio = valor.replace(/[^A-Za-z0-9]/g, '');
    if (limpio.length === 0) {
        input.value = '';
        return;
    }
    limpio = limpio.toUpperCase();
    if (!['J', 'E'].includes(limpio.charAt(0))) limpio = 'J' + limpio.substring(1);
    
    const letra = limpio.charAt(0);
    let numeros = limpio.substring(1).replace(/\D/g, '').substring(0, 9);
    let resultado = letra;
    
    if (numeros.length > 0) {
        resultado += '-';
        if (numeros.length <= 8) resultado += numeros;
        else resultado += numeros.substring(0, 8) + '-' + numeros.substring(8, 9);
    }
    if (input.value !== resultado) {
        input.value = resultado;
        validarRIF(input);
    }
}

function formatearTelefono(input) {
    let valor = input.value.replace(/\D/g, '');
    if (valor.length > 11) valor = valor.substring(0, 11);
    input.value = valor;
}

function toggleCamposPorTipo() {
    const tipo = tipoClienteSelect?.value;
    const camposNatural = document.getElementById("campos-natural");
    const camposJuridico = document.getElementById("campos-juridico");
    const inputsNatural = camposNatural?.querySelectorAll("input, select");
    const inputsJuridico = camposJuridico?.querySelectorAll("input, select");
    
    if (tipo === "natural") {
        if (camposNatural) camposNatural.style.display = "grid";
        if (camposJuridico) camposJuridico.style.display = "none";
        inputsNatural?.forEach(input => input.required = NATURAL_REQUIRED_FIELDS.has(input.name));
        inputsJuridico?.forEach(input => { input.required = false; if (input.name !== "tipo_cliente") input.value = ""; });
    } else if (tipo === "juridico") {
        if (camposNatural) camposNatural.style.display = "none";
        if (camposJuridico) camposJuridico.style.display = "grid";
        inputsJuridico?.forEach(input => input.required = JURIDICO_REQUIRED_FIELDS.has(input.name));
        inputsNatural?.forEach(input => { input.required = false; if (input.name !== "tipo_cliente") input.value = ""; });
    } else {
        if (camposNatural) camposNatural.style.display = "none";
        if (camposJuridico) camposJuridico.style.display = "none";
        inputsNatural?.forEach(input => input.required = false);
        inputsJuridico?.forEach(input => input.required = false);
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
    initValidacionesTiempoReal();
    initModalEliminar();
    initModalVerCliente();
    initCapitalizacionCampos();
}

function initCapitalizacionCampos() {
    const campos = ['input[name="nombre"]', 'input[name="apellido"]', 'input[name="direccion"]', 'input[name="direccion_juridico"]', 'input[name="razon_social"]'];
    campos.forEach(selector => {
        document.querySelectorAll(selector).forEach(element => {
            element.removeEventListener('input', capitalizarInput);
            element.removeEventListener('blur', capitalizarAlPerderFoco);
            element.addEventListener('input', capitalizarInput);
            element.addEventListener('blur', capitalizarAlPerderFoco);
        });
    });
}

function initValidacionesTiempoReal() {
    const nom = document.querySelector('input[name="nombre"]');
    if (nom) {
        nom.addEventListener('input', function() { validarNombreEnTiempoReal(this); });
        nom.addEventListener('blur', function() { if (this.value) validarNombreEnTiempoReal(this); });
    }
    
    const ape = document.querySelector('input[name="apellido"]');
    if (ape) {
        ape.addEventListener('input', function() { validarApellidoEnTiempoReal(this); });
        ape.addEventListener('blur', function() { if (this.value) validarApellidoEnTiempoReal(this); });
    }
    
    const rs = document.getElementById('razon-social-input');
    if (rs) {
        rs.addEventListener('input', function() { validarRazonSocialEnTiempoReal(this); });
        rs.addEventListener('blur', function() { if (this.value) validarRazonSocialEnTiempoReal(this); });
    }

    const ced = document.getElementById('cedula-input');
    if (ced) {
        ced.addEventListener('input', function() {
            this.value = this.value.replace(/\D/g, '');
            if (this.value.length > 8) this.value = this.value.substring(0, 8);
            validarCedula(this);
        });
        ced.addEventListener('blur', function() { if (this.value) validarCedula(this); });
    }

    document.querySelectorAll('input[name="celular"], input[name="telefono"]').forEach(input => {
        input.addEventListener('input', function() { formatearTelefono(this); validarTelefonoEnTiempoReal(this); });
        input.addEventListener('blur', function() { if (this.value) validarTelefonoEnTiempoReal(this); });
    });

    document.querySelectorAll('input[name="correo"], input[name="correo_juridico"]').forEach(input => {
        input.addEventListener('input', function() { validarCorreoEnTiempoReal(this); });
        input.addEventListener('blur', function() { if (this.value) validarCorreoEnTiempoReal(this); });
    });

    document.querySelectorAll('input[name="direccion"], input[name="direccion_juridico"]').forEach(input => {
        input.addEventListener('input', function() { validarDireccionEnTiempoReal(this); });
        input.addEventListener('blur', function() { if (this.value) validarDireccionEnTiempoReal(this); });
    });

    const rifInput = document.getElementById('rif-input');
    if (rifInput) {
        rifInput.addEventListener('input', function() { formatearRIF(this); });
        rifInput.addEventListener('blur', function() { if (this.value) validarRIF(this); });
        rifInput.addEventListener('keydown', function(e) {
            const teclasPermitidas = ['Backspace', 'Delete', 'Tab', 'Escape', 'Enter', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End', 'PageUp', 'PageDown'];
            if (teclasPermitidas.includes(e.key) || e.ctrlKey || e.metaKey) return;
            if (!/^[A-Za-z0-9]$/.test(e.key)) { e.preventDefault(); return; }
        });
    }
}

function initModalEliminar() {
    const confirmBtn = document.getElementById('btn-confirmar-eliminar-cliente');
    if (confirmBtn) confirmBtn.addEventListener('click', confirmarEliminarCliente);
    const modal = document.getElementById('modal-eliminar-cliente');
    if (modal) {
        const overlay = modal.querySelector('.modal__overlay');
        if (overlay) overlay.addEventListener('click', cerrarModalEliminar);
    }
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const m = document.getElementById('modal-eliminar-cliente');
            if (m && !m.hasAttribute('hidden')) cerrarModalEliminar();
        }
    });
}

function initModalVerCliente() {
    const modal = document.getElementById('modal-ver-cliente');
    if (modal) {
        const overlay = modal.querySelector('.modal__overlay');
        if (overlay) overlay.addEventListener('click', cerrarModalVerCliente);
    }
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const m = document.getElementById('modal-ver-cliente');
            if (m && !m.hasAttribute('hidden')) cerrarModalVerCliente();
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
    if (tipoClienteSelect) {
        tipoClienteSelect.value = "";
        tipoClienteSelect.disabled = false;
        tipoClienteSelect.classList.remove('field-error', 'field-success');
    }
    toggleCamposPorTipo();
    if (window.UiModal && typeof window.UiModal.openById === "function") window.UiModal.openById("modal-cliente");
}

function onTablaClick(event) {
    const btn = event.target.closest("button[data-action]");
    if (!btn) return;
    const id = btn.dataset.id;
    const action = btn.dataset.action;
    if (action === "editar") abrirEdicion(id);
    else if (action === "eliminar") eliminarCliente(id);
    else if (action === "ver") abrirModalVerCliente(id);
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
    if (!Array.isArray(clientes)) clientes = [];
    const listaFiltrada = clientes.filter(cliente => {
        const tipo = getTipoCliente(cliente);
        const textoBusqueda = [cliente.id, cliente.nombre, cliente.apellido, cliente.razon_social, cliente.rif, cliente.correo, cliente.direccion].filter(Boolean).join(" ").toLowerCase();
        if (searchQuery && !textoBusqueda.includes(searchQuery.toLowerCase())) return false;
        if (tipoFilter && tipo !== tipoFilter) return false;
        return true;
    });
    
    if (statClientes) statClientes.textContent = String(clientes.length);
    if (statNatural) statNatural.textContent = String(clientes.filter(c => getTipoCliente(c) === "natural").length);
    if (statJuridico) statJuridico.textContent = String(clientes.filter(c => getTipoCliente(c) === "juridico").length);
    
    if (!listaFiltrada.length) {
        tablaClientes.innerHTML = `<tr><td colspan="8" class="table__empty">No hay clientes registrados que coincidan con la búsqueda.</td></tr>`;
        return;
    }
    
    tablaClientes.innerHTML = listaFiltrada.map((cliente) => {
        const tipo = getTipoCliente(cliente);
        const nombreDisplay = tipo === "natural" ? escapeHtml(cliente.nombre || "") : escapeHtml(cliente.razon_social || cliente.nombre || "");
        const segundoValor = tipo === "natural" ? escapeHtml(cliente.apellido || "") : escapeHtml(cliente.rif || "");
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
                        <button class="icon-action icon-action--edit" type="button" data-action="editar" data-id="${clienteId}" title="Editar">${Iconos.lapiz}</button>
                        <button class="icon-action icon-action--view" type="button" data-action="ver" data-id="${clienteId}" title="Ver detalles">${Iconos.ojo}</button>
                        <button class="icon-action icon-action--danger" type="button" data-action="eliminar" data-id="${clienteId}" title="Eliminar">${Iconos.basura}</button>
                    </div>
                </td>
            </tr>
        `;
    }).join("");
}

function abrirEdicion(id) {
    const cliente = clientes.find((item) => String(item.id) === String(id) || String(item.rif) === String(id));
    if (!cliente || !formCliente) return;
    limpiarFormulario();
    modoEdicion = true;
    const tipo = getTipoCliente(cliente);
    if (tipoClienteSelect) {
        tipoClienteSelect.value = tipo;
        tipoClienteSelect.disabled = true;
        tipoClienteSelect.classList.remove('field-error', 'field-success');
    }
    toggleCamposPorTipo();
    const cedulaInput = document.getElementById('cedula-input');
    if (cedulaInput && tipo === 'natural') {
        cedulaInput.disabled = true;
        const err = document.getElementById('cedula-error');
        if (err) { err.textContent = '✓ Edición (no se puede modificar)'; err.style.color = '#60a5fa'; }
        cedulaInput.classList.add('field-success');
    }
    if (tipo === "natural") {
        setFieldValue("cedula", String(cliente.id || ""));
        setFieldValue("nombre", cliente.nombre || "");
        setFieldValue("apellido", cliente.apellido || "");
        setFieldValue("celular", cliente.celular || cliente.telefono || "");
        setFieldValue("correo", cliente.correo || "");
        setFieldValue("direccion", cliente.direccion || "");
        
        ['input[name="nombre"]', 'input[name="apellido"]', 'input[name="celular"]'].forEach(sel => {
            const el = document.querySelector(sel);
            if (el) el.classList.add('field-success');
        });
    } else {
        let rifLimpio = cliente.rif || String(cliente.id || "");
        let rifFormateado = rifLimpio;
        if (!rifLimpio.includes('-') && rifLimpio.length >= 9) rifFormateado = `${rifLimpio.charAt(0)}-${rifLimpio.substring(1, 9)}-${rifLimpio.charAt(9) || ''}`;
        setFieldValue("rif", rifFormateado);
        setFieldValue("razon_social", cliente.razon_social || cliente.nombre || "");
        setFieldValue("telefono", cliente.celular || cliente.telefono || "");
        setFieldValue("correo_juridico", cliente.correo || "");
        setFieldValue("direccion_juridico", cliente.direccion || "");
        
        ['input[name="rif"]', 'input[name="razon_social"]', 'input[name="telefono"]'].forEach(sel => {
            const el = document.querySelector(sel);
            if (el) el.classList.add('field-success');
        });
    }
    if (clienteIdInput) clienteIdInput.value = String(cliente.id || cliente.rif || "");
    formCliente.dataset.editing = "true";
    if (window.UiModal && typeof window.UiModal.openById === "function") window.UiModal.openById("modal-cliente");
}

async function onSubmitCliente(event) {
    event.preventDefault();
    const tipo = tipoClienteSelect?.value;
    let payload = {}, url = "", method = "";
    const isEdit = formCliente.dataset.editing === "true";
    const clienteId = clienteIdInput?.value || "";

    if (tipo === "natural") {
        // Validaciones locales antes de enviar
        const nombreVal = getFieldValue("nombre");
        const apellidoVal = getFieldValue("apellido");
        if (nombreVal.trim().length < 3) {
            mostrarToast("El nombre debe tener al menos 3 letras.", true);
            return;
        }
        if (apellidoVal.trim().length < 3) {
            mostrarToast("El apellido debe tener al menos 3 letras.", true);
            return;
        }

        payload = {
            Id_cliente: getFieldValue("cedula"),
            nombre_cliente: nombreVal,
            apellido_cliente: apellidoVal,
            telefono_cliente: getFieldValue("celular"),
            correo_cliente: getFieldValue("correo"),
            direccion_cliente: getFieldValue("direccion")
        };
        url = isEdit ? `/api/clientes/natural/${encodeURIComponent(clienteId)}` : "/api/clientes/natural";
        method = isEdit ? "PUT" : "POST";
    } else if (tipo === "juridico") {
        payload = {
            Id_cliente: getFieldValue("rif"),
            razon_social: getFieldValue("razon_social"),
            rif: getFieldValue("rif"),
            telefono_cliente: getFieldValue("telefono"),
            correo_cliente: getFieldValue("correo_juridico"),
            direccion_cliente: getFieldValue("direccion_juridico")
        };
        url = isEdit ? `/api/clientes/juridico/${encodeURIComponent(getFieldValue("rif"))}` : "/api/clientes/juridico";
        method = isEdit ? "PUT" : "POST";
    } else {
        mostrarToast("Seleccione el tipo de cliente.", true);
        return;
    }

    try {
        await fetchJson(url, { method, body: JSON.stringify(payload) });
        mostrarToast(isEdit ? "Cliente actualizado exitosamente." : "Cliente creado exitosamente.");
        limpiarFormulario();
        if (window.UiModal && typeof window.UiModal.closeById === "function") window.UiModal.closeById("modal-cliente");
        cargarClientes();
    } catch (error) {
        mostrarToast(error.message || "No se pudo guardar el cliente.", true);
    }
}

function onBuscarClientes(event) { searchQuery = String(event.target.value || "").trim(); renderClientes(); }
function onFiltrarTipo(event) { tipoFilter = String(event.target.value || "").trim(); renderClientes(); }

function eliminarCliente(id) {
    const cliente = clientes.find((item) => String(item.id) === String(id) || String(item.rif) === String(id));
    let nombreCliente = id;
    if (cliente) {
        const tipo = getTipoCliente(cliente);
        nombreCliente = tipo === "natural" ? `${cliente.nombre || ''} ${cliente.apellido || ''}`.trim() || id : cliente.razon_social || cliente.nombre || id;
    }
    abrirModalEliminar(id, nombreCliente);
}

function limpiarFormulario() {
    if (!formCliente) return;
    formCliente.reset();
    if (clienteIdInput) clienteIdInput.value = "";
    delete formCliente.dataset.editing;
    modoEdicion = false;
    if (tipoClienteSelect) { tipoClienteSelect.disabled = false; tipoClienteSelect.value = ""; }
    
    document.querySelectorAll('.field-error').forEach(el => { el.textContent = ''; el.style.color = ''; });
    document.querySelectorAll('.field-error, .field-success').forEach(el => el.classList.remove('field-error', 'field-success'));
    
    const cNat = document.getElementById("campos-natural");
    const cJur = document.getElementById("campos-juridico");
    if (cNat) cNat.querySelectorAll("input").forEach(i => i.value = "");
    if (cJur) cJur.querySelectorAll("input").forEach(i => i.value = "");
}

function getFieldValue(fieldName) {
    const field = formCliente?.elements?.namedItem(fieldName);
    return field && "value" in field ? String(field.value).trim() : "";
}

function setFieldValue(fieldName, value) {
    const field = formCliente?.elements?.namedItem(fieldName);
    if (field && "value" in field) field.value = value;
}

// ==================== FETCH Y UTILS ====================

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
        try { data = await response.json(); } catch (e) { data = { success: false, message: 'Error al procesar la respuesta' }; }
        if (!response.ok || data.success === false) throw new Error(data.message || data.error || `Error ${response.status}`);
        return data;
    } catch (error) {
        throw error;
    }
}

function mostrarToast(message, isError = false) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.toggle("toast--error", isError);
    toast.classList.add("is-visible");
    window.clearTimeout(mostrarToast._timer);
    mostrarToast._timer = window.setTimeout(() => toast.classList.remove("is-visible"), 3000);
}

function getTipoCliente(cliente) {
    if (!cliente) return "";
    if (cliente.rif || cliente.razon_social || cliente.tipo === "juridico") return "juridico";
    return "natural";
}

function escapeHtml(text) {
    if (text === null || text === undefined) return "";
    return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}