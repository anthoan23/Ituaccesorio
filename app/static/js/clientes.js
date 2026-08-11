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
const csrfToken = document.querySelector("input[name='_csrf_token']")?.value || "";

// ==================== VALIDACIÓN RIF ====================

// Función para formatear RIF automáticamente
function formatearRIF(input) {
    // Eliminar cualquier caracter que no sea letra o número
    let valor = input.value.replace(/[^a-zA-Z0-9]/g, '');
    
    // Convertir letra a mayúscula
    valor = valor.toUpperCase();
    
    // Validar que empiece con J o E
    if (valor.length > 0 && !['J', 'E'].includes(valor.charAt(0))) {
        // Si no empieza con J o E, reemplazar con J
        valor = 'J' + valor.substring(1);
    }
    
    // Aplicar formato: J-12345678-9
    let resultado = '';
    let numeros = '';
    let letra = '';
    
    if (valor.length > 0) {
        letra = valor.charAt(0);
        numeros = valor.substring(1);
        
        // Limitar a 9 dígitos (8 + 1 verificador)
        numeros = numeros.substring(0, 9);
        
        // Construir el resultado
        resultado = letra;
        if (numeros.length > 0) {
            resultado += '-';
            if (numeros.length <= 8) {
                resultado += numeros;
            } else {
                resultado += numeros.substring(0, 8) + '-' + numeros.substring(8);
            }
        }
    }
    
    input.value = resultado;
}

// Validación específica para RIF
function validarRIF(valor) {
    // Limpiar el valor para la validación
    const limpio = valor.replace(/[^a-zA-Z0-9]/g, '');
    
    // Verificar que tenga al menos 2 caracteres
    if (limpio.length < 2) {
        return { valido: false, mensaje: 'El RIF debe comenzar con J o E y tener al menos 8 dígitos.' };
    }
    
    // Verificar que el primer caracter sea J o E
    const primeraLetra = limpio.charAt(0);
    if (!['J', 'E'].includes(primeraLetra)) {
        return { valido: false, mensaje: 'El RIF debe comenzar con J (Persona Jurídica) o E (Empresa).' };
    }
    
    // Extraer los números
    const numeros = limpio.substring(1);
    const numerosValidos = numeros.replace(/[^0-9]/g, '');
    
    // Verificar que tenga exactamente 8 dígitos numéricos (sin contar el verificador)
    if (numerosValidos.length < 8) {
        return { valido: false, mensaje: `El RIF debe tener al menos 8 dígitos numéricos (actual: ${numerosValidos.length}).` };
    }
    
    // Verificar que todos los caracteres después de la letra sean números
    if (numeros.length !== numerosValidos.length) {
        return { valido: false, mensaje: 'El RIF solo debe contener letra J/E seguida de 8 dígitos numéricos.' };
    }
    
    return { valido: true };
}

// Función para validar el RIF en tiempo real
function validarRIFEnTiempoReal(input) {
    const errorElement = document.getElementById('rif-error');
    if (!errorElement) return;
    
    const valor = input.value;
    if (!valor) {
        errorElement.textContent = '';
        input.classList.remove('field-error');
        return;
    }
    
    const resultado = validarRIF(valor);
    if (!resultado.valido) {
        errorElement.textContent = resultado.mensaje;
        input.classList.add('field-error');
    } else {
        errorElement.textContent = '';
        input.classList.remove('field-error');
    }
}

// Función para limpiar RIF (eliminar guiones)
function limpiarRIF(valor) {
    return valor.replace(/[^a-zA-Z0-9]/g, '');
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
    
    // Reinicializar validadores
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
    
    // INICIALIZAR RIF AUTOCOMPLETADO
    initRIFAutocomplete();
}

function initRIFAutocomplete() {
    // Buscar el campo RIF en el formulario
    const rifInput = document.getElementById('rif-input');
    if (!rifInput) return;
    
    // Evento para formatear mientras escribe
    rifInput.addEventListener('input', function(e) {
        // Guardar posición del cursor
        const start = this.selectionStart;
        const end = this.selectionEnd;
        const oldLength = this.value.length;
        
        // Aplicar formato
        formatearRIF(this);
        
        // Ajustar posición del cursor
        const newLength = this.value.length;
        const diff = newLength - oldLength;
        let newPos = start + diff;
        
        // Si el cursor está después de un guion, moverlo después del siguiente caracter
        if (this.value.charAt(newPos - 1) === '-') {
            newPos = newPos + 1;
        }
        
        // Asegurar que la posición no sea mayor que la longitud
        if (newPos > this.value.length) {
            newPos = this.value.length;
        }
        
        this.setSelectionRange(newPos, newPos);
        
        // Validar en tiempo real
        validarRIFEnTiempoReal(this);
    });
    
    // Evento para validar al salir del campo
    rifInput.addEventListener('blur', function() {
        // Si el RIF está incompleto, mostrar error
        if (this.value) {
            validarRIFEnTiempoReal(this);
            
            // Intentar completar automáticamente si tiene todos los dígitos
            const limpio = this.value.replace(/[^a-zA-Z0-9]/g, '');
            if (limpio.length >= 2) {
                const primeraLetra = limpio.charAt(0);
                const numeros = limpio.substring(1).replace(/[^0-9]/g, '');
                
                // Si tiene 8 dígitos numéricos, formatear correctamente
                if (numeros.length >= 8) {
                    const verificador = numeros.length > 8 ? numeros.charAt(8) : '';
                    this.value = `${primeraLetra}-${numeros.substring(0, 8)}${verificador ? '-' + verificador : ''}`;
                    validarRIFEnTiempoReal(this);
                }
            }
        }
    });
    
    // Evento para validar antes de enviar
    rifInput.addEventListener('keydown', function(e) {
        // Permitir teclas de navegación y borrado
        const teclasPermitidas = [
            'Backspace', 'Delete', 'Tab', 'Escape', 'Enter',
            'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
            'Home', 'End', 'PageUp', 'PageDown'
        ];
        
        if (teclasPermitidas.includes(e.key)) {
            return;
        }
        
        // Verificar que sea solo letras y números
        if (!/^[a-zA-Z0-9]$/.test(e.key)) {
            e.preventDefault();
        }
    });
}

// Ejecutar inicialización cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initClientes);
} else {
    initClientes();
}

// ==================== FUNCIONES DE UI ====================

function abrirFormularioNuevo() {
    limpiarFormulario();
    if (tipoClienteSelect) tipoClienteSelect.value = "";
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
}

// ==================== CRUD ====================

async function cargarClientes() {
    try {
        const data = await fetchJson("/api/clientes");
        clientes = Array.isArray(data.clientes) ? data.clientes : [];
        if (!Array.isArray(data.clientes)) {
            console.warn('La respuesta de /api/clientes no regresó un arreglo válido:', data.clientes);
        }
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
                            <button class="icon-action" type="button" data-action="edit" data-id="${clienteId}" title="Editar">✎</button>
                            <button class="icon-action icon-action--danger" type="button" data-action="delete" data-id="${clienteId}" title="Eliminar">🗑</button>
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

    const tipo = getTipoCliente(cliente);
    if (tipoClienteSelect) tipoClienteSelect.value = tipo;
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
        // Para jurídico, mostrar el RIF con formato
        const rifLimpio = cliente.rif || String(cliente.id || "");
        // Formatear RIF para mostrar: J-12345678-9
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
    
    // Validar formulario antes de enviar
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
        const rif = getFieldValue("rif");
        const razonSocial = getFieldValue("razon_social");
        const telefono = getFieldValue("telefono");
        const correo = getFieldValue("correo_juridico");
        const direccion = getFieldValue("direccion_juridico");

        // VALIDAR RIF ANTES DE ENVIAR
        const resultadoRIF = validarRIF(rif);
        if (!resultadoRIF.valido) {
            mostrarToast(resultadoRIF.mensaje, true);
            if (rifInput) {
                rifInput.focus();
                rifInput.classList.add('field-error');
                const errorElement = document.getElementById('rif-error');
                if (errorElement) {
                    errorElement.textContent = resultadoRIF.mensaje;
                }
            }
            return;
        }

        if (!rif || !razonSocial || !telefono) {
            mostrarToast("RIF, razón social y teléfono son obligatorios.", true);
            return;
        }

        // Limpiar RIF para guardar (eliminar guiones)
        const rifLimpio = limpiarRIF(rif);

        payload = {
            Id_cliente: rifLimpio,
            razon_social: razonSocial,
            rif: rifLimpio,
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
        mostrarToast(isEdit ? "Cliente actualizado." : "Cliente creado.");
        limpiarFormulario();
        if (window.UiModal && typeof window.UiModal.closeById === "function") {
            window.UiModal.closeById("modal-cliente");
        }
        cargarClientes();
    } catch (error) {
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

async function eliminarCliente(id) {
    if (!confirm(`¿Estás seguro de eliminar al cliente con ID ${id}?`)) {
        return;
    }
    
    try {
        await fetchJson(`/api/clientes/${encodeURIComponent(id)}`, { method: "DELETE" });
        mostrarToast("Cliente eliminado.");
        cargarClientes();
    } catch (error) {
        mostrarToast(error.message || "No se pudo eliminar el cliente.", true);
    }
}

function limpiarFormulario() {
    if (!formCliente) return;
    formCliente.reset();
    if (clienteIdInput) {
        clienteIdInput.value = "";
    }
    delete formCliente.dataset.editing;

    // Limpiar error de RIF
    const rifError = document.getElementById('rif-error');
    if (rifError) rifError.textContent = '';
    const rifInput = document.getElementById('rif-input');
    if (rifInput) rifInput.classList.remove('field-error');

    if (window.FieldValidator) {
        window.FieldValidator.resetForm(formCliente);
    }
    
    // Limpiar campos condicionales
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
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
        },
        credentials: "same-origin",
        ...options,
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok || data.success === false) {
        throw new Error(data.error || data.message || "No se pudo completar la operación.");
    }

    return data;
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