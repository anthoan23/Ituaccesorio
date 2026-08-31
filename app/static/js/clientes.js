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

// ==================== ICONOS SVG ====================

const Iconos = {
    lapiz: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25Zm18-11.5a1 1 0 0 0 0-1.41l-1.34-1.34a1 1 0 0 0-1.41 0l-1.12 1.12 3.75 3.75L21 5.75Z" fill="currentColor"/></svg>`,
    basura: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 7h12l-1 14H7L6 7Zm3-3h6l1 2H8l1-2Z" fill="currentColor"/></svg>`,
    ojo: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" fill="currentColor"/></svg>`
};

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

// ==================== MODAL DETALLES ====================

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
    const tipo = getTipoCliente(cliente);
    let inicial = '?';
    if (tipo === 'natural') {
        inicial = (cliente.nombre || '?').charAt(0).toUpperCase();
    } else {
        inicial = (cliente.razon_social || cliente.nombre || '?').charAt(0).toUpperCase();
    }
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

// ==================== VALIDACIÓN DE NOMBRE ====================

function validarNombre(valor) {
    if (!valor || valor.trim() === '') {
        return { valido: false, mensaje: 'El nombre es obligatorio' };
    }
    if (valor.trim().length < 3) {
        return { valido: false, mensaje: 'El nombre debe tener al menos 3 letras' };
    }
    if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(valor)) {
        return { valido: false, mensaje: 'Solo letras, espacios, acentos y ñ' };
    }
    if (valor.length > 20) {
        return { valido: false, mensaje: 'No puede exceder los 20 caracteres' };
    }
    return { valido: true };
}

function validarNombreEnTiempoReal(input) {
    const errorElement = document.getElementById('nombre-error');
    if (!errorElement) {
        // Crear elemento de error si no existe
        const parent = input.parentElement;
        const error = document.createElement('small');
        error.className = 'field-error';
        error.id = 'nombre-error';
        parent.appendChild(error);
    }
    const errorEl = document.getElementById('nombre-error');
    if (!errorEl) return;
    const valor = input.value;
    if (!valor) {
        errorEl.textContent = '';
        errorEl.style.color = '';
        input.classList.remove('field-error', 'field-success');
        return;
    }
    const resultado = validarNombre(valor);
    if (!resultado.valido) {
        errorEl.textContent = '✗ ' + resultado.mensaje;
        errorEl.style.color = '#ef4444';
        input.classList.add('field-error');
        input.classList.remove('field-success');
    } else {
        errorEl.textContent = '✓ Válido';
        errorEl.style.color = '#22c55e';
        input.classList.remove('field-error');
        input.classList.add('field-success');
    }
}

// ==================== VALIDACIÓN DE APELLIDO ====================

function validarApellido(valor) {
    if (!valor || valor.trim() === '') {
        return { valido: false, mensaje: 'El apellido es obligatorio' };
    }
    if (valor.trim().length < 3) {
        return { valido: false, mensaje: 'El apellido debe tener al menos 3 letras' };
    }
    if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(valor)) {
        return { valido: false, mensaje: 'Solo letras, espacios, acentos y ñ' };
    }
    if (valor.length > 20) {
        return { valido: false, mensaje: 'No puede exceder los 20 caracteres' };
    }
    return { valido: true };
}

function validarApellidoEnTiempoReal(input) {
    const errorElement = document.getElementById('apellido-error');
    if (!errorElement) {
        const parent = input.parentElement;
        const error = document.createElement('small');
        error.className = 'field-error';
        error.id = 'apellido-error';
        parent.appendChild(error);
    }
    const errorEl = document.getElementById('apellido-error');
    if (!errorEl) return;
    const valor = input.value;
    if (!valor) {
        errorEl.textContent = '';
        errorEl.style.color = '';
        input.classList.remove('field-error', 'field-success');
        return;
    }
    const resultado = validarApellido(valor);
    if (!resultado.valido) {
        errorEl.textContent = '✗ ' + resultado.mensaje;
        errorEl.style.color = '#ef4444';
        input.classList.add('field-error');
        input.classList.remove('field-success');
    } else {
        errorEl.textContent = '✓ Válido';
        errorEl.style.color = '#22c55e';
        input.classList.remove('field-error');
        input.classList.add('field-success');
    }
}

// ==================== VALIDACIÓN DE RAZÓN SOCIAL ====================

function validarRazonSocial(valor) {
    if (!valor || valor.trim() === '') {
        return { valido: false, mensaje: 'La razón social es obligatoria' };
    }
    if (valor.trim().length < 3) {
        return { valido: false, mensaje: 'La razón social debe tener al menos 3 letras' };
    }
    const patronRazonSocial = /^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\.\-&]+$/;
    if (!patronRazonSocial.test(valor)) {
        return { valido: false, mensaje: 'Solo letras, números, puntos, guiones, espacios y &' };
    }
    if (valor.length > 60) {
        return { valido: false, mensaje: 'No puede exceder los 60 caracteres' };
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

// ==================== VALIDACIÓN DE CÉDULA ====================

function validarCedula(input) {
    const valor = input.value.trim();
    const errorElement = document.getElementById('cedula-error');
    if (!errorElement) return { valido: false, mensaje: '' };
    
    if (!valor) {
        errorElement.textContent = '';
        errorElement.style.color = '';
        input.classList.remove('field-error', 'field-success');
        return { valido: false, mensaje: '' };
    }
    
    if (!/^\d{7,8}$/.test(valor)) {
        errorElement.textContent = '✗ La cédula debe tener 7 u 8 dígitos numéricos';
        errorElement.style.color = '#ef4444';
        input.classList.add('field-error');
        input.classList.remove('field-success');
        return { valido: false, mensaje: 'Formato inválido' };
    }
    
    const isEdit = document.getElementById('form-cliente')?.dataset?.editing === 'true';
    if (!isEdit) {
        const esDuplicado = verificarDuplicadoEnTabla(valor, 0, '#tabla-clientes');
        if (esDuplicado) {
            errorElement.textContent = `✗ La cédula "${valor}" ya está registrada`;
            errorElement.style.color = '#ef4444';
            input.classList.add('field-error');
            input.classList.remove('field-success');
            mostrarToast(`La cédula "${valor}" ya está registrada.`, true);
            return { valido: false, mensaje: 'Cédula ya registrada' };
        }
    }
    
    errorElement.textContent = '✓ Cédula disponible';
    errorElement.style.color = '#22c55e';
    input.classList.remove('field-error');
    input.classList.add('field-success');
    return { valido: true, mensaje: '' };
}

// ==================== VALIDACIÓN RIF CORREGIDA ====================

function validarRIF(input) {
    const valor = input.value;
    const errorElement = document.getElementById('rif-error');
    if (!errorElement) return { valido: false, mensaje: '' };
    
    // Si está vacío, limpiar mensajes
    if (!valor || valor.trim() === '') {
        errorElement.textContent = '';
        errorElement.style.color = '';
        input.classList.remove('field-error', 'field-success');
        return { valido: false, mensaje: '' };
    }
    
    // Verificar formato con guiones
    const patronRIF = /^[JE]-\d{8}-\d$/;
    if (!patronRIF.test(valor)) {
        errorElement.textContent = '✗ Formato inválido. Use J-12345678-9 o E-12345678-9';
        errorElement.style.color = '#ef4444';
        input.classList.add('field-error');
        input.classList.remove('field-success');
        return { valido: false, mensaje: 'Formato inválido' };
    }
    
    // Verificar que la primera letra sea J o E
    const letra = valor.charAt(0);
    if (!['J', 'E'].includes(letra)) {
        errorElement.textContent = '✗ Debe comenzar con J o E';
        errorElement.style.color = '#ef4444';
        input.classList.add('field-error');
        input.classList.remove('field-success');
        return { valido: false, mensaje: 'Debe comenzar con J o E' };
    }
    
    // Verificar que después del primer guión solo haya números
    const partes = valor.split('-');
    if (partes.length === 3) {
        // Verificar que la segunda parte solo tenga números
        if (!/^\d+$/.test(partes[1])) {
            errorElement.textContent = '✗ Después del primer guión solo deben ir números';
            errorElement.style.color = '#ef4444';
            input.classList.add('field-error');
            input.classList.remove('field-success');
            return { valido: false, mensaje: 'Solo números después del guión' };
        }
        // Verificar que la tercera parte solo tenga un número
        if (!/^\d$/.test(partes[2])) {
            errorElement.textContent = '✗ El último dígito debe ser un número del 0 al 9';
            errorElement.style.color = '#ef4444';
            input.classList.add('field-error');
            input.classList.remove('field-success');
            return { valido: false, mensaje: 'Último dígito debe ser número' };
        }
        // Verificar que la segunda parte tenga exactamente 8 dígitos
        if (partes[1].length !== 8) {
            errorElement.textContent = `✗ Debe tener 8 dígitos (actual: ${partes[1].length})`;
            errorElement.style.color = '#ef4444';
            input.classList.add('field-error');
            input.classList.remove('field-success');
            return { valido: false, mensaje: 'Debe tener 8 dígitos' };
        }
    }
    
    const isEdit = document.getElementById('form-cliente')?.dataset?.editing === 'true';
    if (!isEdit) {
        const esDuplicado = verificarDuplicadoEnTabla(valor, 0, '#tabla-clientes');
        if (esDuplicado) {
            errorElement.textContent = `✗ El RIF "${valor}" ya está registrado`;
            errorElement.style.color = '#ef4444';
            input.classList.add('field-error');
            input.classList.remove('field-success');
            mostrarToast(`El RIF "${valor}" ya está registrado.`, true);
            return { valido: false, mensaje: 'RIF ya registrado' };
        }
    }
    
    errorElement.textContent = '✓ RIF disponible';
    errorElement.style.color = '#22c55e';
    input.classList.remove('field-error');
    input.classList.add('field-success');
    return { valido: true, mensaje: '' };
}

// ==================== FORMATEAR RIF CORREGIDO ====================

function formatearRIF(input) {
    // Obtener el valor actual
    let valor = input.value;
    
    // Remover todo excepto letras y números
    let limpio = valor.replace(/[^A-Za-z0-9]/g, '');
    
    // Si está vacío, limpiar y salir
    if (limpio.length === 0) {
        input.value = '';
        return;
    }
    
    // Convertir a mayúsculas
    limpio = limpio.toUpperCase();
    
    // Verificar la primera letra - SOLO J o E
    const primeraLetra = limpio.charAt(0);
    if (!['J', 'E'].includes(primeraLetra)) {
        // Si no es J o E, forzar J
        limpio = 'J' + limpio.substring(1);
    }
    
    // Extraer la letra y los números
    const letra = limpio.charAt(0);
    let numeros = limpio.substring(1);
    
    // Limitar los números a 9 dígitos (8 + 1 verificador)
    numeros = numeros.replace(/\D/g, '').substring(0, 9);
    
    // Construir el RIF formateado
    let resultado = letra;
    
    if (numeros.length > 0) {
        resultado += '-';
        if (numeros.length <= 8) {
            resultado += numeros;
        } else {
            // Si hay más de 8 dígitos, poner el guión
            resultado += numeros.substring(0, 8) + '-' + numeros.substring(8, 9);
        }
    }
    
    // Si el resultado es diferente, actualizar el input
    if (input.value !== resultado) {
        // Guardar la posición del cursor
        const cursorPos = input.selectionStart;
        input.value = resultado;
        
        // Ajustar la posición del cursor
        let newPos = cursorPos;
        const diff = resultado.length - valor.length;
        newPos = Math.min(newPos + diff, resultado.length);
        
        // Saltar los guiones automáticamente
        if (resultado.charAt(newPos) === '-') {
            newPos++;
        }
        if (newPos > resultado.length) {
            newPos = resultado.length;
        }
        
        try {
            input.setSelectionRange(newPos, newPos);
        } catch (e) {
            // Ignorar errores de selección
        }
    }
    
    // Validar automáticamente después de formatear
    validarRIF(input);
}

// ==================== VALIDACIÓN TELÉFONO ====================

function validarTelefono(telefono) {
    if (!telefono) return { valido: false, mensaje: 'El teléfono es obligatorio' };
    const telefonoLimpio = telefono.replace(/\D/g, '');
    
    const prefijo = telefonoLimpio.substring(0, 4);
    const prefijosPermitidos = ['0416', '0426', '0414', '0424', '0412', '0422', '0251'];
    if (!prefijosPermitidos.includes(prefijo)) {
        return { valido: false, mensaje: `El prefijo ${prefijo} no está permitido` };
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
    initNombreValidation();
    initApellidoValidation();
    initRazonSocialValidation();
    initTelefonoValidation();
    initModalEliminar();
    initModalVerCliente();
    initCapitalizacionCampos();
    initCedulaValidation();
}

function initCapitalizacionCampos() {
    const camposCapitalizar = [
        'input[name="nombre"]',
        'input[name="apellido"]',
        'input[name="direccion"]',
        'input[name="direccion_juridico"]',
        'input[name="razon_social"]'
    ];
    camposCapitalizar.forEach(selector => {
        const elementos = document.querySelectorAll(selector);
        elementos.forEach(element => {
            element.removeEventListener('input', capitalizarInput);
            element.removeEventListener('blur', capitalizarAlPerderFoco);
            element.addEventListener('input', capitalizarInput);
            element.addEventListener('blur', capitalizarAlPerderFoco);
        });
    });
}

function initNombreValidation() {
    const nombreInput = document.querySelector('input[name="nombre"]');
    if (!nombreInput) return;
    // Crear elemento de error si no existe
    let errorElement = document.getElementById('nombre-error');
    if (!errorElement) {
        errorElement = document.createElement('small');
        errorElement.className = 'field-error';
        errorElement.id = 'nombre-error';
        nombreInput.parentElement.appendChild(errorElement);
    }
    nombreInput.removeEventListener('input', nombreInput._nombreHandler);
    nombreInput._nombreHandler = function() {
        validarNombreEnTiempoReal(this);
    };
    nombreInput.addEventListener('input', nombreInput._nombreHandler);
    nombreInput.addEventListener('blur', function() {
        if (this.value) {
            validarNombreEnTiempoReal(this);
        }
    });
}

function initApellidoValidation() {
    const apellidoInput = document.querySelector('input[name="apellido"]');
    if (!apellidoInput) return;
    let errorElement = document.getElementById('apellido-error');
    if (!errorElement) {
        errorElement = document.createElement('small');
        errorElement.className = 'field-error';
        errorElement.id = 'apellido-error';
        apellidoInput.parentElement.appendChild(errorElement);
    }
    apellidoInput.removeEventListener('input', apellidoInput._apellidoHandler);
    apellidoInput._apellidoHandler = function() {
        validarApellidoEnTiempoReal(this);
    };
    apellidoInput.addEventListener('input', apellidoInput._apellidoHandler);
    apellidoInput.addEventListener('blur', function() {
        if (this.value) {
            validarApellidoEnTiempoReal(this);
        }
    });
}

// ==================== INICIALIZACIÓN DE RIF MEJORADA ====================

function initRIFAutocomplete() {
    const rifInput = document.getElementById('rif-input');
    if (!rifInput) return;
    
    // Remover event listeners previos
    rifInput.removeEventListener('input', rifInput._rifInputHandler);
    rifInput.removeEventListener('blur', rifInput._rifBlurHandler);
    rifInput.removeEventListener('keydown', rifInput._rifKeydownHandler);
    
    // Handler para el evento input
    rifInput._rifInputHandler = function(e) {
        // Guardar la posición del cursor antes de formatear
        const start = this.selectionStart;
        const oldLength = this.value.length;
        
        // Aplicar el formateo
        formatearRIF(this);
        
        // Ajustar la posición del cursor después del formateo
        const newLength = this.value.length;
        const diff = newLength - oldLength;
        let newPos = start + diff;
        
        // Saltar guiones automáticamente
        if (this.value.charAt(newPos) === '-') {
            newPos++;
        }
        if (newPos > this.value.length) {
            newPos = this.value.length;
        }
        
        try {
            this.setSelectionRange(newPos, newPos);
        } catch (e) {
            // Ignorar errores de selección
        }
    };
    
    // Handler para el evento blur
    rifInput._rifBlurHandler = function() {
        if (this.value) {
            // Limpiar y formatear al perder el foco
            const limpio = this.value.replace(/-/g, '');
            if (limpio.length >= 9 && /^[JE]\d{8,9}$/.test(limpio)) {
                const letra = limpio.charAt(0);
                const numeros = limpio.substring(1);
                if (numeros.length >= 8) {
                    const digitos = numeros.substring(0, 8);
                    const verificador = numeros.length > 8 ? numeros.charAt(8) : '';
                    this.value = `${letra}-${digitos}${verificador ? '-' + verificador : ''}`;
                }
            }
            validarRIF(this);
        }
    };
    
    // Handler para el evento keydown - Solo permitir letras y números
    rifInput._rifKeydownHandler = function(e) {
        const teclasPermitidas = [
            'Backspace', 'Delete', 'Tab', 'Escape', 'Enter',
            'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
            'Home', 'End', 'PageUp', 'PageDown'
        ];
        
        // Permitir teclas de control
        if (teclasPermitidas.includes(e.key)) {
            return;
        }
        
        // Si es Ctrl+C, Ctrl+V, Ctrl+X, etc.
        if (e.ctrlKey || e.metaKey) {
            return;
        }
        
        // Solo permitir letras (A-Z) y números (0-9)
        if (!/^[A-Za-z0-9]$/.test(e.key)) {
            e.preventDefault();
            return;
        }
        
        // Si ya hay una letra al inicio, no permitir más letras
        const valor = this.value;
        const letrasEncontradas = valor.match(/[A-Za-z]/g) || [];
        if (letrasEncontradas.length >= 1 && /[A-Za-z]/.test(e.key)) {
            // Si ya hay una letra, no permitir otra (excepto si es la primera posición)
            e.preventDefault();
            return;
        }
    };
    
    // Agregar los event listeners
    rifInput.addEventListener('input', rifInput._rifInputHandler);
    rifInput.addEventListener('blur', rifInput._rifBlurHandler);
    rifInput.addEventListener('keydown', rifInput._rifKeydownHandler);
}

function initRazonSocialValidation() {
    const razonSocialInput = document.getElementById('razon-social-input');
    if (!razonSocialInput) return;
    razonSocialInput.removeEventListener('input', razonSocialInput._razonHandler);
    razonSocialInput._razonHandler = function() {
        validarRazonSocialEnTiempoReal(this);
    };
    razonSocialInput.addEventListener('input', razonSocialInput._razonHandler);
    razonSocialInput.addEventListener('blur', function() {
        if (this.value) {
            validarRazonSocialEnTiempoReal(this);
        }
    });
}

function initTelefonoValidation() {
    const telefonos = document.querySelectorAll('input[name="celular"], input[name="telefono"]');
    telefonos.forEach(input => {
        let errorElement = document.getElementById(input.name + '-error');
        if (!errorElement) {
            errorElement = document.createElement('small');
            errorElement.className = 'field-error';
            errorElement.id = input.name + '-error';
            input.parentElement.appendChild(errorElement);
        }
        input.removeEventListener('input', input._telefonoHandler);
        input._telefonoHandler = function() {
            formatearTelefono(this);
            validarTelefonoEnTiempoReal(this);
        };
        input.addEventListener('input', input._telefonoHandler);
        input.addEventListener('blur', function() {
            if (this.value) {
                validarTelefonoEnTiempoReal(this);
            }
        });
    });
}

function initCedulaValidation() {
    const cedulaInput = document.getElementById('cedula-input');
    if (!cedulaInput) return;
    
    cedulaInput.removeEventListener('input', cedulaInput._cedulaHandler);
    cedulaInput.removeEventListener('blur', cedulaInput._cedulaBlurHandler);
    
    cedulaInput._cedulaHandler = function() {
        this.value = this.value.replace(/\D/g, '');
        if (this.value.length > 8) {
            this.value = this.value.substring(0, 8);
        }
        validarCedula(this);
    };
    
    cedulaInput._cedulaBlurHandler = function() {
        if (this.value) {
            validarCedula(this);
        }
    };
    
    cedulaInput.addEventListener('input', cedulaInput._cedulaHandler);
    cedulaInput.addEventListener('blur', cedulaInput._cedulaBlurHandler);
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
    const cedulaInput = document.getElementById('cedula-input');
    if (cedulaInput) {
        cedulaInput.disabled = false;
        const errorElement = document.getElementById('cedula-error');
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.style.color = '';
        }
        cedulaInput.classList.remove('field-error', 'field-success');
        cedulaInput.value = '';
    }
    const rifInput = document.getElementById('rif-input');
    if (rifInput) {
        rifInput.classList.remove('field-error', 'field-success');
        rifInput.value = '';
    }
    const rifError = document.getElementById('rif-error');
    if (rifError) {
        rifError.textContent = '';
        rifError.style.color = '';
    }
    // Limpiar mensajes de error de nombre, apellido y razón social
    document.querySelectorAll('.field-error').forEach(el => {
        el.textContent = '';
        el.style.color = '';
    });
    document.querySelectorAll('.field-error, .field-success').forEach(el => {
        el.classList.remove('field-error', 'field-success');
    });
    toggleCamposPorTipo();
    if (window.UiModal && typeof window.UiModal.openById === "function") {
        window.UiModal.openById("modal-cliente");
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
        ].filter(Boolean).join(" ").toLowerCase();
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
    tablaClientes.innerHTML = listaFiltrada.map((cliente) => {
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
    }).join("");
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
    const cedulaInput = document.getElementById('cedula-input');
    if (cedulaInput) {
        cedulaInput.disabled = true;
        const errorElement = document.getElementById('cedula-error');
        if (errorElement) {
            errorElement.textContent = '✓ Edición (no se puede modificar)';
            errorElement.style.color = '#60a5fa';
        }
        cedulaInput.classList.remove('field-error');
        cedulaInput.classList.add('field-success');
    }
    if (tipo === "natural") {
        const nombre = cliente.nombre || "";
        const apellido = cliente.apellido || "";
        setFieldValue("cedula", String(cliente.id || ""));
        setFieldValue("nombre", nombre);
        setFieldValue("apellido", apellido);
        setFieldValue("celular", cliente.celular || cliente.telefono || "");
        setFieldValue("correo", cliente.correo || "");
        setFieldValue("direccion", cliente.direccion || "");
        // Marcar nombre y apellido como válidos en edición
        const nombreInput = document.querySelector('input[name="nombre"]');
        const apellidoInput = document.querySelector('input[name="apellido"]');
        if (nombreInput) {
            nombreInput.classList.remove('field-error');
            nombreInput.classList.add('field-success');
            const errorEl = document.getElementById('nombre-error');
            if (errorEl) {
                errorEl.textContent = '✓ Válido';
                errorEl.style.color = '#22c55e';
            }
        }
        if (apellidoInput) {
            apellidoInput.classList.remove('field-error');
            apellidoInput.classList.add('field-success');
            const errorEl = document.getElementById('apellido-error');
            if (errorEl) {
                errorEl.textContent = '✓ Válido';
                errorEl.style.color = '#22c55e';
            }
        }
    } else {
        let rifLimpio = cliente.rif || String(cliente.id || "");
        let rifFormateado = rifLimpio;
        if (!rifLimpio.includes('-') && rifLimpio.length >= 9) {
            const letra = rifLimpio.charAt(0);
            const numeros = rifLimpio.substring(1);
            if (numeros.length >= 8) {
                rifFormateado = `${letra}-${numeros.substring(0, 8)}-${numeros.charAt(8) || ''}`;
            }
        } else if (rifLimpio.includes('-')) {
            const partes = rifLimpio.split('-');
            if (partes.length === 3) {
                rifFormateado = rifLimpio;
            } else if (partes.length === 2) {
                const letra = partes[0];
                const numeros = partes[1];
                if (numeros.length >= 8) {
                    rifFormateado = `${letra}-${numeros.substring(0, 8)}-${numeros.charAt(8) || ''}`;
                }
            }
        }
        setFieldValue("rif", rifFormateado);
        setFieldValue("razon_social", cliente.razon_social || cliente.nombre || "");
        setFieldValue("telefono", cliente.celular || cliente.telefono || "");
        setFieldValue("correo_juridico", cliente.correo || "");
        setFieldValue("direccion_juridico", cliente.direccion || "");
        
        const rifInput = document.getElementById('rif-input');
        if (rifInput) {
            rifInput.classList.remove('field-error');
            rifInput.classList.add('field-success');
            const rifError = document.getElementById('rif-error');
            if (rifError) {
                rifError.textContent = '✓ Edición (no se puede modificar)';
                rifError.style.color = '#60a5fa';
            }
        }
        // Marcar razón social como válida en edición
        const razonSocialInput = document.getElementById('razon-social-input');
        if (razonSocialInput) {
            razonSocialInput.classList.remove('field-error');
            razonSocialInput.classList.add('field-success');
            const errorEl = document.getElementById('razon-social-error');
            if (errorEl) {
                errorEl.textContent = '✓ Válido';
                errorEl.style.color = '#22c55e';
            }
        }
    }
    if (clienteIdInput) {
        clienteIdInput.value = String(cliente.id || cliente.rif || "");
    }
    formCliente.dataset.editing = "true";
    if (window.UiModal && typeof window.UiModal.openById === "function") {
        window.UiModal.openById("modal-cliente");
    }
}

async function onSubmitCliente(event) {
    event.preventDefault();
    
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
        
        // Validar nombre
        const resultadoNombre = validarNombre(nombre);
        if (!resultadoNombre.valido) {
            mostrarToast(resultadoNombre.mensaje, true);
            const nombreInput = document.querySelector('input[name="nombre"]');
            if (nombreInput) nombreInput.focus();
            return;
        }
        
        // Validar apellido
        const resultadoApellido = validarApellido(apellido);
        if (!resultadoApellido.valido) {
            mostrarToast(resultadoApellido.mensaje, true);
            const apellidoInput = document.querySelector('input[name="apellido"]');
            if (apellidoInput) apellidoInput.focus();
            return;
        }
        
        if (!cedula) {
            mostrarToast("La cédula es obligatoria.", true);
            return;
        }
        if (!/^\d+$/.test(cedula)) {
            mostrarToast("La cédula debe contener solo números.", true);
            return;
        }
        if (cedula.length < 7 || cedula.length > 8) {
            mostrarToast("La cédula debe tener 7 u 8 dígitos.", true);
            return;
        }
        
        if (!isEdit) {
            const esDuplicado = verificarDuplicadoEnTabla(cedula, 0, '#tabla-clientes');
            if (esDuplicado) {
                mostrarToast(`La cédula "${cedula}" ya está registrada.`, true);
                const cedulaInput = document.getElementById('cedula-input');
                if (cedulaInput) {
                    cedulaInput.focus();
                    cedulaInput.classList.add('field-error');
                    const errorElement = document.getElementById('cedula-error');
                    if (errorElement) {
                        errorElement.textContent = `✗ La cédula "${cedula}" ya está registrada`;
                        errorElement.style.color = '#ef4444';
                    }
                }
                return;
            }
        }
        
        const resultadoTelefono = validarTelefono(celular);
        if (!resultadoTelefono.valido) {
            mostrarToast(resultadoTelefono.mensaje, true);
            const telefonoInput = document.querySelector('input[name="celular"]');
            if (telefonoInput) telefonoInput.focus();
            return;
        }
        if (correo && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) {
            mostrarToast("El correo electrónico no es válido.", true);
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
        let rif = getFieldValue("rif");
        const razonSocial = getFieldValue("razon_social");
        const telefono = getFieldValue("telefono");
        const correo = getFieldValue("correo_juridico");
        const direccion = getFieldValue("direccion_juridico");
        
        // Validar razón social
        const resultadoRazonSocial = validarRazonSocial(razonSocial);
        if (!resultadoRazonSocial.valido) {
            mostrarToast(resultadoRazonSocial.mensaje, true);
            const razonSocialInput = document.getElementById('razon-social-input');
            if (razonSocialInput) razonSocialInput.focus();
            return;
        }
        
        if (rif && !rif.includes('-') && rif.length >= 9) {
            const letra = rif.charAt(0).toUpperCase();
            const numeros = rif.substring(1);
            if (numeros.length >= 8) {
                rif = `${letra}-${numeros.substring(0, 8)}-${numeros.charAt(8) || ''}`;
            }
        } else if (rif && rif.includes('-')) {
            const partes = rif.split('-');
            if (partes.length === 2) {
                const letra = partes[0];
                const numeros = partes[1];
                if (numeros.length >= 8) {
                    rif = `${letra}-${numeros.substring(0, 8)}-${numeros.charAt(8) || ''}`;
                }
            }
        }
        const rifField = document.querySelector('input[name="rif"]');
        if (rifField) {
            rifField.value = rif;
        }
        
        if (!rif) {
            mostrarToast("El RIF es obligatorio.", true);
            const rifInput = document.getElementById('rif-input');
            if (rifInput) rifInput.focus();
            return;
        }
        const letraRIF = rif.charAt(0);
        if (!['J', 'E'].includes(letraRIF)) {
            mostrarToast("El RIF debe comenzar con J o E.", true);
            const rifInput = document.getElementById('rif-input');
            if (rifInput) rifInput.focus();
            return;
        }
        const patronRIF = /^[JE]-\d{8}-\d$/;
        if (!patronRIF.test(rif)) {
            mostrarToast("El RIF debe tener el formato: J-12345678-9 o E-12345678-9", true);
            const rifInput = document.getElementById('rif-input');
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
        
        if (!isEdit) {
            const esDuplicado = verificarDuplicadoEnTabla(rif, 0, '#tabla-clientes');
            if (esDuplicado) {
                mostrarToast(`El RIF "${rif}" ya está registrado.`, true);
                const rifInput = document.getElementById('rif-input');
                if (rifInput) {
                    rifInput.focus();
                    rifInput.classList.add('field-error');
                    const errorElement = document.getElementById('rif-error');
                    if (errorElement) {
                        errorElement.textContent = `✗ El RIF "${rif}" ya está registrado`;
                        errorElement.style.color = '#ef4444';
                    }
                }
                return;
            }
        }
        
        if (!telefono) {
            mostrarToast("El teléfono es obligatorio.", true);
            return;
        }
        const resultadoTelefono = validarTelefono(telefono);
        if (!resultadoTelefono.valido) {
            mostrarToast(resultadoTelefono.mensaje, true);
            return;
        }
        if (correo && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) {
            mostrarToast("El correo electrónico no es válido.", true);
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
            url = `/api/clientes/juridico/${encodeURIComponent(rif)}`;
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
    const cedulaInput = document.getElementById('cedula-input');
    if (cedulaInput) {
        cedulaInput.disabled = false;
        const errorElement = document.getElementById('cedula-error');
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.style.color = '';
        }
        cedulaInput.classList.remove('field-error', 'field-success');
        cedulaInput.value = '';
    }
    const rifError = document.getElementById('rif-error');
    if (rifError) {
        rifError.textContent = '';
        rifError.style.color = '';
    }
    const rifInput = document.getElementById('rif-input');
    if (rifInput) {
        rifInput.classList.remove('field-error', 'field-success');
        rifInput.value = '';
    }
    const razonSocialError = document.getElementById('razon-social-error');
    if (razonSocialError) {
        razonSocialError.textContent = '';
        razonSocialError.style.color = '';
    }
    const razonSocialInput = document.getElementById('razon-social-input');
    if (razonSocialInput) {
        razonSocialInput.classList.remove('field-error', 'field-success');
        razonSocialInput.value = '';
    }
    // Limpiar errores de nombre y apellido
    const nombreError = document.getElementById('nombre-error');
    if (nombreError) {
        nombreError.textContent = '';
        nombreError.style.color = '';
    }
    const nombreInput = document.querySelector('input[name="nombre"]');
    if (nombreInput) {
        nombreInput.classList.remove('field-error', 'field-success');
    }
    const apellidoError = document.getElementById('apellido-error');
    if (apellidoError) {
        apellidoError.textContent = '';
        apellidoError.style.color = '';
    }
    const apellidoInput = document.querySelector('input[name="apellido"]');
    if (apellidoInput) {
        apellidoInput.classList.remove('field-error', 'field-success');
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
    const camposNatural = document.getElementById("campos-natural");
    const camposJuridico = document.getElementById("campos-juridico");
    if (camposNatural) {
        camposNatural.querySelectorAll("input").forEach(input => input.value = "");
    }
    if (camposJuridico) {
        camposJuridico.querySelectorAll("input").forEach(input => input.value = "");
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
    }, 3000);
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