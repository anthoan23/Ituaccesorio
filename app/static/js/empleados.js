// ============================================
// 1. CONSTANTES Y CONFIGURACIÓN
// ============================================
const CONFIG = {
  API: {
    EMPLEADOS: '/api/empleados',
    CONSULTAR: '/api/empleados/consultar',
    LISTA: '/api/empleados/lista',
    GRAFICOS: '/api/empleados/graficos',
    VERIFICAR_CEDULA: '/api/empleados/verificar-cedula' // Nueva endpoint para verificar cédula
  },
  CHART_COLORS: {
    PIE_1: {
      BACKGROUND: ['#ffce54', '#f3c500', '#ffe36b', '#e67e00', '#d4a017', '#f39c12', '#e67e22', '#f1c40f'],
      BORDER: ['#ffce54', '#f3c500', '#ffe36b', '#e67e00', '#d4a017', '#f39c12', '#e67e22', '#f1c40f']
    },
    PIE_2: {
      BACKGROUND: ['rgba(54, 162, 235, 0.7)', 'rgba(255, 99, 132, 0.7)', 'rgba(255, 206, 86, 0.7)', 'rgba(75, 192, 192, 0.7)', 'rgba(153, 102, 255, 0.7)', 'rgba(255, 159, 64, 0.7)'],
      BORDER: ['rgba(54, 162, 235, 1)', 'rgba(255, 99, 132, 1)', 'rgba(255, 206, 86, 1)', 'rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)', 'rgba(255, 159, 64, 1)']
    }
  }
};

let grafico1 = null;
let grafico2 = null;
let especialidadesList = [];
let cargosList = [];
let especialidadesArray = [];
window.especialidadesArray = especialidadesArray;

// Variable para controlar si la cédula ya está verificada
let cedulaVerificada = {
  isValid: false,
  message: '',
  exists: false,
  checking: false
};

// ============================================
// 2. UTILIDADES E ICONOS
// ============================================
const Iconos = {
  lapiz: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25Zm18-11.5a1 1 0 0 0 0-1.41l-1.34-1.34a1 1 0 0 0-1.41 0l-1.12 1.12 3.75 3.75L21 5.75Z" fill="currentColor"/></svg>`,
  basura: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 7h12l-1 14H7L6 7Zm3-3h6l1 2H8l1-2Z" fill="currentColor"/></svg>`,
  ojo: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" fill="currentColor"/></svg>`
};

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
      const msg =
        (isJson && payload && (payload.message || payload.error)) ||
        String(payload || response.statusText || "Error en la solicitud");
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
      alert(message);
      return;
    }
    console.info(message);
  },

  capitalizarTexto(texto) {
    if (!texto) return '';
    return texto.toLowerCase().split(' ').map(palabra => 
      palabra.charAt(0).toUpperCase() + palabra.slice(1)
    ).join(' ');
  },

  validarCampos() {
    const reglas = {
      soloNumeros: (valor) => /^\d+$/.test(valor),
      soloLetras: (valor) => /^[a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+$/.test(valor),
      telefono: (valor) => valor === '' || /^\d{11}$/.test(valor),
      email: (valor) => valor === '' || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(valor),
      sinCaracteresEspeciales: (valor) => valor === '' || /^[a-zA-Z0-9\s,.-]+$/.test(valor)
    };
    return reglas;
  },

  // Función para verificar cédula en tiempo real
  async verificarCedula(cedula, excludeCurrentId = null) {
    if (!cedula || cedula.length < 6) {
      return { exists: false, message: '' };
    }
    
    try {
      const response = await this.fetchJson(CONFIG.API.CONSULTAR, {
        method: 'POST',
        body: JSON.stringify({ cedula: cedula })
      });
      
      // Si existe un ID a excluir (para edición) y coincide, no considerarlo como duplicado
      if (excludeCurrentId && response.empleado && response.empleado.id_empleado == excludeCurrentId) {
        return { exists: false, message: '' };
      }
      
      return { 
        exists: response.success && response.empleado,
        message: response.success && response.empleado ? '⚠️ Esta cédula ya está registrada en el sistema' : ''
      };
    } catch (error) {
      // Si hay error, asumimos que no existe para no bloquear
      return { exists: false, message: '' };
    }
  }
};

// ============================================
// 3. MANEJADORES DE MODALES
// ============================================
function openModal(id, mode = 'register', empleadoData = null, especialidadesData = null) {
  const modal = document.getElementById(id);
  if (!modal) return;
  
  if (id === 'modal-registrar-empleado') {
    const modalTitle = modal.querySelector('.modal__title');
    const submitBtn = modal.querySelector('#modal-submit-btn');
    const form = modal.querySelector('#form-registrar-empleado');
    const especialidadesContainer = document.getElementById('especialidades-container');
    
    if (mode === 'register') {
      if (modalTitle) modalTitle.textContent = 'Registrar nuevo empleado';
      if (submitBtn) {
        submitBtn.textContent = 'Guardar empleado';
        submitBtn.disabled = false;
        submitBtn.style.display = '';
      }
      if (form) {
        form.dataset.mode = 'register';
        form.reset();
      }
      
      habilitarCamposFormulario(true);
      
      if (especialidadesContainer) {
        especialidadesContainer.style.display = 'none';
      }
      
      limpiarEspecialidades();
      
      const editIdInput = document.getElementById('edit-id-empleado');
      if (editIdInput) editIdInput.value = '';
      
      const cedulaInput = document.getElementById('reg-cedula-empleado');
      if (cedulaInput) {
        cedulaInput.disabled = false;
        cedulaInput.value = '';
        // Limpiar estado de validación
        limpiarValidacionCedula();
      }
      
      // Resetear variable de verificación
      cedulaVerificada = {
        isValid: false,
        message: '',
        exists: false,
        checking: false
      };
      
    } else if (mode === 'edit') {
      if (modalTitle) modalTitle.textContent = 'Modificar empleado';
      if (submitBtn) {
        submitBtn.textContent = 'Actualizar empleado';
        submitBtn.disabled = false;
        submitBtn.style.display = '';
      }
      if (form) form.dataset.mode = 'edit';
      
      habilitarCamposFormulario(true);
      const cedulaInput = document.getElementById('reg-cedula-empleado');
      if (cedulaInput) {
        cedulaInput.disabled = true;
        // En edición, la cédula es válida por defecto (no se puede cambiar)
        cedulaVerificada = {
          isValid: true,
          message: '',
          exists: false,
          checking: false
        };
        const cedulaHint = document.getElementById('cedula-hint');
        if (cedulaHint) {
          cedulaHint.textContent = 'La cédula no se puede modificar en edición';
          cedulaHint.style.color = '#6c757d';
        }
      }
      
      if (empleadoData) {
        cargarDatosEnFormulario(empleadoData, especialidadesData);
      }
    }
    
    modal.removeAttribute("hidden");
    modal.setAttribute("aria-hidden", "false");
    
  } else if (id === 'modal-ver-empleado') {
    if (empleadoData) {
      mostrarDetalleEmpleado(empleadoData, especialidadesData);
    }
    modal.removeAttribute("hidden");
    modal.setAttribute("aria-hidden", "false");
    
  } else if (id === 'modal-eliminar-empleado') {
    modal.removeAttribute("hidden");
    modal.setAttribute("aria-hidden", "false");
  }
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.setAttribute("hidden", "");
    modal.setAttribute("aria-hidden", "true");
    
    if (id === 'modal-registrar-empleado') {
      const form = modal.querySelector('#form-registrar-empleado');
      const modalTitle = modal.querySelector('.modal__title');
      const submitBtn = modal.querySelector('#modal-submit-btn');
      const especialidadesContainer = document.getElementById('especialidades-container');
      
      if (form) {
        form.reset();
        form.dataset.mode = 'register';
        
        const cedulaInput = document.getElementById('reg-cedula-empleado');
        if (cedulaInput) cedulaInput.disabled = false;
      }
      
      if (modalTitle) modalTitle.textContent = 'Registrar nuevo empleado';
      if (submitBtn) {
        submitBtn.textContent = 'Guardar empleado';
        submitBtn.disabled = false;
        submitBtn.style.display = '';
      }
      
      if (especialidadesContainer) {
        especialidadesContainer.style.display = 'none';
      }
      
      habilitarCamposFormulario(true);
      
      const listaEspecialidades = document.getElementById('lista-especialidades');
      if (listaEspecialidades) {
        listaEspecialidades.innerHTML = '<div class="especialidades-empty">No hay especialidades agregadas</div>';
      }
      
      const hiddenInput = document.getElementById('especialidades-hidden');
      if (hiddenInput) hiddenInput.value = '';
      
      especialidadesArray = [];
      window.especialidadesArray = especialidadesArray;
      
      const editId = document.getElementById('edit-id-empleado');
      if (editId) editId.value = '';
      
      const cargoSelect = document.getElementById('reg-cargo-empleado');
      if (cargoSelect) cargoSelect.value = '';
      
      const selectEspecialidad = document.getElementById('select-especialidad');
      if (selectEspecialidad) selectEspecialidad.value = '';
      
      // Limpiar validación de cédula
      limpiarValidacionCedula();
    }
  }
}

function limpiarValidacionCedula() {
  const cedulaInput = document.getElementById('reg-cedula-empleado');
  const cedulaHint = document.getElementById('cedula-hint');
  
  if (cedulaInput) {
    cedulaInput.style.borderColor = '';
    cedulaInput.classList.remove('input-error', 'input-success');
  }
  
  if (cedulaHint) {
    cedulaHint.textContent = 'Solo números (máximo 8 dígitos)';
    cedulaHint.style.color = '#6c757d';
  }
}

function mostrarValidacionCedula(isValid, exists, message) {
  const cedulaInput = document.getElementById('reg-cedula-empleado');
  const cedulaHint = document.getElementById('cedula-hint');
  const submitBtn = document.getElementById('modal-submit-btn');
  
  if (!cedulaInput) return;
  
  if (exists) {
    // Cédula ya registrada - ERROR
    cedulaInput.style.borderColor = '#dc3545';
    cedulaInput.classList.add('input-error');
    cedulaInput.classList.remove('input-success');
    if (cedulaHint) {
      cedulaHint.textContent = message || '⚠️ Esta cédula ya está registrada en el sistema';
      cedulaHint.style.color = '#dc3545';
    }
    if (submitBtn) submitBtn.disabled = true;
  } else if (isValid && cedulaInput.value.length >= 6) {
    // Cédula válida y no registrada - ÉXITO
    cedulaInput.style.borderColor = '#28a745';
    cedulaInput.classList.add('input-success');
    cedulaInput.classList.remove('input-error');
    if (cedulaHint) {
      cedulaHint.textContent = '✓ Cédula disponible para registrar';
      cedulaHint.style.color = '#28a745';
    }
    if (submitBtn) submitBtn.disabled = false;
  } else if (cedulaInput.value.length > 0 && cedulaInput.value.length < 6) {
    // Cédula incompleta
    cedulaInput.style.borderColor = '#ffc107';
    cedulaInput.classList.remove('input-error', 'input-success');
    if (cedulaHint) {
      cedulaHint.textContent = '⚠️ La cédula debe tener 8 dígitos';
      cedulaHint.style.color = '#ffc107';
    }
    if (submitBtn) submitBtn.disabled = true;
  } else {
    // Sin valor o valor inválido
    cedulaInput.style.borderColor = '';
    cedulaInput.classList.remove('input-error', 'input-success');
    if (cedulaHint) {
      cedulaHint.textContent = 'Solo números (máximo 8 dígitos)';
      cedulaHint.style.color = '#6c757d';
    }
    if (submitBtn) submitBtn.disabled = true;
  }
}

// Función para verificar cédula con debounce
let debounceTimer;
async function verificarCedulaEnTiempoReal(cedula, excludeCurrentId = null) {
  // Limpiar timer anterior
  if (debounceTimer) clearTimeout(debounceTimer);
  
  // Si la cédula está vacía o es muy corta, resetear
  if (!cedula || cedula.length < 6) {
    mostrarValidacionCedula(false, false, '');
    cedulaVerificada = { isValid: false, message: '', exists: false, checking: false };
    return;
  }
  
  // Si la cédula no es solo números
  if (!/^\d+$/.test(cedula)) {
    mostrarValidacionCedula(false, false, '⚠️ Solo se permiten números');
    cedulaVerificada = { isValid: false, message: '', exists: false, checking: false };
    return;
  }
  
  // Si tiene exactamente 8 dígitos, verificar
  if (cedula.length === 8) {
    // Mostrar estado de verificación
    const cedulaHint = document.getElementById('cedula-hint');
    if (cedulaHint) {
      cedulaHint.textContent = '🔍 Verificando cédula...';
      cedulaHint.style.color = '#17a2b8';
    }
    
    cedulaVerificada.checking = true;
    
    // Debounce para no hacer muchas peticiones
    debounceTimer = setTimeout(async () => {
      try {
        const result = await Utils.verificarCedula(cedula, excludeCurrentId);
        cedulaVerificada = {
          isValid: !result.exists,
          message: result.message,
          exists: result.exists,
          checking: false
        };
        mostrarValidacionCedula(!result.exists, result.exists, result.message);
      } catch (error) {
        console.error('Error verificando cédula:', error);
        cedulaVerificada = { isValid: true, message: '', exists: false, checking: false };
        mostrarValidacionCedula(true, false, '');
      }
    }, 500);
  } else {
    // Cédula incompleta
    mostrarValidacionCedula(false, false, '');
    cedulaVerificada = { isValid: false, message: '', exists: false, checking: false };
  }
}

function mostrarDetalleEmpleado(empleado, especialidades = null) {
  let empleadoData = empleado;
  let especialidadesData = especialidades;
  
  if (empleado && empleado.empleado && !especialidades) {
    empleadoData = empleado.empleado;
    especialidadesData = empleado.especialidades || [];
  }
  
  console.log('Empleado a mostrar:', empleadoData);
  console.log('Especialidades a mostrar:', especialidadesData);
  
  const inicial = (empleadoData.nombre?.charAt(0) || '?').toUpperCase();
  const inicialSpan = document.getElementById('detalle-inicial');
  if (inicialSpan) inicialSpan.textContent = inicial;
  
  const campos = {
    'detalle-cedula': empleadoData.cedula || '-',
    'detalle-nombre-completo': `${empleadoData.nombre || ''} ${empleadoData.apellido || ''}`.trim() || '-',
    'detalle-cargo': empleadoData.cargo || empleadoData.nombre_cargo || '-',
    'detalle-celular': empleadoData.celular || 'No registrado',
    'detalle-correo': empleadoData.correo || 'No registrado',
    'detalle-direccion': empleadoData.direccion || 'No registrada'
  };
  
  Object.keys(campos).forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = campos[id];
  });
  
  const especialidadesContainer = document.getElementById('detalle-especialidades-container');
  const especialidadesDiv = document.getElementById('detalle-especialidades');
  
  if (especialidadesContainer && especialidadesDiv) {
    if (especialidadesData && especialidadesData.length > 0) {
      especialidadesDiv.innerHTML = especialidadesData
        .map(esp => {
          const nombreEsp = esp.nombre || esp.Nombre_especialidad || esp.nombre_especialidad || esp;
          return `<span class="especialidad-tag-readonly">${Utils.escapeHtml(nombreEsp)}</span>`;
        })
        .join('');
      especialidadesContainer.style.display = 'block';
    } else {
      especialidadesContainer.style.display = 'none';
      especialidadesDiv.innerHTML = '';
    }
  }
}

function habilitarCamposFormulario(habilitar) {
  const campos = [
    'reg-cedula-empleado',
    'reg-nombre-empleado',
    'reg-apellido-empleado',
    'reg-cargo-empleado',
    'reg-celular-empleado',
    'reg-correo-empleado',
    'reg-direccion-empleado'
  ];
  
  campos.forEach(campoId => {
    const campo = document.getElementById(campoId);
    if (campo) {
      campo.disabled = !habilitar;
    }
  });
  
  const selectEspecialidad = document.getElementById('select-especialidad');
  if (selectEspecialidad) {
    selectEspecialidad.disabled = !habilitar;
  }
  
  const removeButtons = document.querySelectorAll('.remove-especialidad');
  removeButtons.forEach(btn => {
    if (habilitar) {
      btn.style.display = '';
    } else {
      btn.style.display = 'none';
    }
  });
}

function cargarDatosEnFormulario(empleado, especialidades = null) {
  let empleadoData = empleado;
  let especialidadesData = especialidades;
  
  if (empleado && empleado.empleado && !especialidades) {
    empleadoData = empleado.empleado;
    especialidadesData = empleado.especialidades || [];
  }
  
  console.log('Cargando datos para edición - Empleado:', empleadoData);
  console.log('Cargando datos para edición - Especialidades:', especialidadesData);
  
  const cedulaInput = document.getElementById('reg-cedula-empleado');
  const nombreInput = document.getElementById('reg-nombre-empleado');
  const apellidoInput = document.getElementById('reg-apellido-empleado');
  const cargoSelect = document.getElementById('reg-cargo-empleado');
  const celularInput = document.getElementById('reg-celular-empleado');
  const correoInput = document.getElementById('reg-correo-empleado');
  const direccionInput = document.getElementById('reg-direccion-empleado');
  const editIdInput = document.getElementById('edit-id-empleado');
  
  if (cedulaInput) cedulaInput.value = empleadoData.cedula || '';
  if (nombreInput) nombreInput.value = empleadoData.nombre || '';
  if (apellidoInput) apellidoInput.value = empleadoData.apellido || '';
  if (celularInput) celularInput.value = empleadoData.celular || '';
  if (correoInput) correoInput.value = empleadoData.correo || '';
  if (direccionInput) direccionInput.value = empleadoData.direccion || '';
  if (editIdInput) editIdInput.value = empleadoData.cedula || empleadoData.id_empleado || '';
  
  if (cargoSelect && empleadoData.cargo) {
    const cargoNombre = empleadoData.cargo;
    const option = Array.from(cargoSelect.options).find(opt => opt.text === cargoNombre);
    if (option) cargoSelect.value = option.value;
  }
  
  if (especialidadesData && especialidadesData.length > 0) {
    const especialidadesIds = especialidadesData.map(e => e.id || e.ID_especialidad);
    if (especialidadesIds.length > 0) {
      setEspecialidades(especialidadesIds);
    }
  } else {
    limpiarEspecialidades();
  }
  
  if (cargoSelect && cargoSelect.value) {
    const selectedOption = cargoSelect.options[cargoSelect.selectedIndex];
    const cargoNombre = selectedOption?.textContent;
    const isTecnico = cargoNombre === 'Técnico' || cargoNombre === 'Tecnico';
    const especialidadesContainer = document.getElementById('especialidades-container');
    if (especialidadesContainer) {
      especialidadesContainer.style.display = isTecnico ? 'block' : 'none';
    }
  }
}

async function verEmpleado(cedula) {
  try {
    const response = await Utils.fetchJson(CONFIG.API.CONSULTAR, {
      method: 'POST',
      body: JSON.stringify({ cedula: cedula })
    });
    
    console.log('Respuesta completa del servidor (ver):', response);
    
    if (response.success) {
      openModal('modal-ver-empleado', 'view', response);
    } else {
      Utils.showMessage('No se encontró el empleado', true);
    }
  } catch (error) {
    console.error('Error al cargar empleado:', error);
    Utils.showMessage('Error al cargar datos del empleado', true);
  }
}

async function editarEmpleado(cedula) {
  try {
    const response = await Utils.fetchJson(CONFIG.API.CONSULTAR, {
      method: 'POST',
      body: JSON.stringify({ cedula: cedula })
    });
    
    console.log('Respuesta completa del servidor (editar):', response);
    
    if (response.success) {
      openModal('modal-registrar-empleado', 'edit', response);
      setTimeout(() => {
        toggleEspecialidades();
      }, 100);
    } else {
      Utils.showMessage('No se encontró el empleado', true);
    }
  } catch (error) {
    console.error('Error al cargar empleado para editar:', error);
    Utils.showMessage('Error al cargar datos del empleado', true);
  }
}

// ============================================
// 4. MANEJADORES DE TABLA CON ICONOS
// ============================================
function renderTabla(empleados) {
  const tbody = document.getElementById("tabla-empleados");
  const contador = document.querySelector("[data-count]");
  
  if (!tbody) return;

  if (!empleados || empleados.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="table__empty">No hay empleados para mostrar.</td></td>`;
    if (contador) {
      contador.setAttribute("data-count", "0");
      contador.textContent = "0";
    }
    return;
  }

  tbody.innerHTML = empleados.map(empleado => {
    const cedula = Utils.escapeHtml(empleado.cedula || empleado.cedula_empleado || empleado.id_empleado || '');
    const nombre = Utils.escapeHtml(empleado.nombre || empleado.nombre_empleado || '');
    const apellido = Utils.escapeHtml(empleado.apellido || empleado.apellido_empleado || '');
    const cargo = Utils.escapeHtml(empleado.cargo || empleado.nombre_cargo || '-');
    
    return `
      <tr data-cedula="${cedula}">
        <td><span class="chip">${cedula}</span></td>
        <td>${nombre}</td>
        <td>${apellido}</td>
        <td>${cargo}</td>
        <td class="table__actions">
          <div class="row-actions" aria-label="Acciones del empleado">
            <button class="icon-action" type="button" data-action="editar" 
                    data-cedula="${cedula}" 
                    aria-label="Modificar">
              ${Iconos.lapiz}
            </button>
            <button class="icon-action icon-action--view" type="button" data-action="ver" 
                    data-cedula="${cedula}" 
                    aria-label="Ver">
              ${Iconos.ojo}
            </button>
            <button class="icon-action icon-action--danger" type="button" data-action="eliminar" 
                    data-cedula="${cedula}" 
                    data-nombre="${nombre}" 
                    data-apellido="${apellido}" 
                    aria-label="Eliminar">
              ${Iconos.basura}
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');

  if (contador) {
    contador.setAttribute("data-count", String(empleados.length));
    contador.textContent = String(empleados.length);
  }
  
  agregarEventosTabla();
}

function agregarEventosTabla() {
  document.querySelectorAll('[data-action="editar"]').forEach(btn => {
    btn.removeEventListener('click', handleEditarClick);
    btn.addEventListener('click', handleEditarClick);
  });
  
  document.querySelectorAll('[data-action="ver"]').forEach(btn => {
    btn.removeEventListener('click', handleVerClick);
    btn.addEventListener('click', handleVerClick);
  });
  
  document.querySelectorAll('[data-action="eliminar"]').forEach(btn => {
    btn.removeEventListener('click', handleEliminarClick);
    btn.addEventListener('click', handleEliminarClick);
  });
}

function handleEditarClick(e) {
  const cedula = e.currentTarget.getAttribute('data-cedula');
  editarEmpleado(cedula);
}

function handleVerClick(e) {
  const cedula = e.currentTarget.getAttribute('data-cedula');
  verEmpleado(cedula);
}

function handleEliminarClick(e) {
  const cedula = e.currentTarget.getAttribute('data-cedula');
  const nombre = e.currentTarget.getAttribute('data-nombre');
  const apellido = e.currentTarget.getAttribute('data-apellido');
  const nombreCompleto = `${nombre} ${apellido}`.trim();
  
  const confirmText = document.getElementById('texto-confirmar-eliminar-empleado');
  if (confirmText) {
    confirmText.textContent = `¿Estás seguro de que quieres eliminar a "${nombreCompleto}"?`;
  }
  
  const confirmBtn = document.getElementById('btn-confirmar-eliminar-empleado');
  if (confirmBtn) {
    confirmBtn.setAttribute('data-cedula', cedula);
  }
  
  openModal('modal-eliminar-empleado');
}

// ============================================
// 5. MANEJADORES DE GRÁFICOS
// ============================================
async function cargarGraficos() {
  try {
    const data = await Utils.fetchJson(CONFIG.API.GRAFICOS);
    
    if (data.cargos && data.cargos.length > 0) {
      const labels = data.cargos.map(item => item.nombre || item.Nombre_cargo);
      const values = data.cargos.map(item => item.cantidad || item.cantidad_personas || 0);
      crearGraficoPie('miGrafico1', CONFIG.CHART_COLORS.PIE_1, labels, values);
    }
    
    if (data.especialidades && data.especialidades.length > 0) {
      const labels = data.especialidades.map(item => item.nombre || item.Nombre_especialidad);
      const values = data.especialidades.map(item => item.cantidad || item.cantidad_personas || 0);
      crearGraficoPie('miGrafico2', CONFIG.CHART_COLORS.PIE_2, labels, values);
    }
  } catch (error) {
    console.error('Error cargando gráficos:', error);
  }
}

function crearGraficoPie(canvasId, colors, labels, data) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;
  
  if (canvasId === 'miGrafico1' && grafico1) grafico1.destroy();
  if (canvasId === 'miGrafico2' && grafico2) grafico2.destroy();
  
  const chart = new Chart(canvas, {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: colors.BACKGROUND.slice(0, labels.length),
        borderColor: colors.BORDER.slice(0, labels.length),
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { 
          position: 'bottom',
          labels: { font: { size: 11 } }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.label || '';
              const value = context.raw || 0;
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
              return `${label}: ${value} (${percentage}%)`;
            }
          }
        }
      }
    }
  });
  
  if (canvasId === 'miGrafico1') grafico1 = chart;
  if (canvasId === 'miGrafico2') grafico2 = chart;
  
  return chart;
}

// ============================================
// 6. MANEJADORES DE ESPECIALIDADES
// ============================================
async function cargarCargosYEspecialidades() {
  try {
    const data = await Utils.fetchJson(CONFIG.API.LISTA);
    
    if (data.cargos && data.cargos.length > 0) {
      cargosList = data.cargos.map(cargo => ({
        ID_cargo: cargo.id || cargo.ID_cargo,
        Nombre_cargo: cargo.nombre || cargo.Nombre_cargo
      }));
      llenarSelectCargos();
    }
    
    if (data.especialidades && data.especialidades.length > 0) {
      especialidadesList = data.especialidades.map(esp => ({
        ID_especialidad: esp.id || esp.ID_especialidad,
        Nombre_especialidad: esp.nombre || esp.Nombre_especialidad,
        Descripcion_especialidad: esp.descripcion || esp.Descripcion_especialidad
      }));
      llenarSelectEspecialidades();
    }
  } catch (error) {
    console.error('Error cargando datos:', error);
    cargosList = [
      { ID_cargo: 1, Nombre_cargo: 'Administrador' },
      { ID_cargo: 2, Nombre_cargo: 'Técnico' },
      { ID_cargo: 3, Nombre_cargo: 'Supervisor' }
    ];
    especialidadesList = [
      { ID_especialidad: 1, Nombre_especialidad: 'Redes' },
      { ID_especialidad: 2, Nombre_especialidad: 'Sistemas' },
      { ID_especialidad: 3, Nombre_especialidad: 'Software' },
      { ID_especialidad: 4, Nombre_especialidad: 'Hardware' },
      { ID_especialidad: 5, Nombre_especialidad: 'Seguridad Informática' },
      { ID_especialidad: 6, Nombre_especialidad: 'Bases de Datos' },
      { ID_especialidad: 7, Nombre_especialidad: 'Soporte Técnico' }
    ];
    llenarSelectCargos();
    llenarSelectEspecialidades();
  }
}

function llenarSelectCargos() {
  const cargoSelect = document.getElementById('reg-cargo-empleado');
  if (!cargoSelect) return;
  
  cargoSelect.innerHTML = '<option value="">Seleccione un cargo</option>';
  cargosList.forEach(cargo => {
    const option = document.createElement('option');
    option.value = cargo.ID_cargo;
    option.textContent = cargo.Nombre_cargo;
    cargoSelect.appendChild(option);
  });
}

function llenarSelectEspecialidades() {
  const selectEspecialidad = document.getElementById('select-especialidad');
  if (!selectEspecialidad) return;
  
  selectEspecialidad.innerHTML = '<option value="">Seleccione una especialidad</option>';
  especialidadesList.forEach(esp => {
    const option = document.createElement('option');
    option.value = esp.ID_especialidad;
    option.textContent = esp.Nombre_especialidad;
    selectEspecialidad.appendChild(option);
  });
  
  selectEspecialidad.removeEventListener('change', autoAgregarEspecialidad);
  selectEspecialidad.addEventListener('change', autoAgregarEspecialidad);
}

function autoAgregarEspecialidad(event) {
  const selectEspecialidad = event.target;
  const especialidadId = selectEspecialidad.value;
  
  if (!especialidadId || especialidadId === "") {
    return;
  }
  
  const form = document.getElementById('form-registrar-empleado');
  if (form && form.dataset.mode === 'view') {
    selectEspecialidad.value = '';
    return;
  }
  
  const especialidadSeleccionada = especialidadesList.find(esp => esp.ID_especialidad == especialidadId);
  
  if (!especialidadSeleccionada) {
    console.error('Especialidad no encontrada:', especialidadId);
    return;
  }
  
  const especialidadNombre = especialidadSeleccionada.Nombre_especialidad;
  
  if (especialidadesArray.some(e => e.id == especialidadId)) {
    selectEspecialidad.style.border = '2px solid red';
    setTimeout(() => {
      selectEspecialidad.style.border = '';
    }, 500);
    Utils.showMessage(`La especialidad "${especialidadNombre}" ya ha sido agregada`, true);
    selectEspecialidad.value = '';
    return;
  }

  especialidadesArray.push({ 
    id: String(especialidadId), 
    nombre: especialidadNombre 
  });
  
  selectEspecialidad.style.border = '2px solid green';
  setTimeout(() => {
    selectEspecialidad.style.border = '';
  }, 500);
  
  actualizarListaEspecialidades();
  selectEspecialidad.value = '';
  actualizarHiddenInput();
  Utils.showMessage(`✓ Especialidad "${especialidadNombre}" agregada`, false);
}

function eliminarEspecialidad(especialidadId) {
  const especialidadEliminada = especialidadesArray.find(esp => esp.id == especialidadId);
  especialidadesArray = especialidadesArray.filter(esp => esp.id != especialidadId);
  window.especialidadesArray = especialidadesArray;
  actualizarListaEspecialidades();
  actualizarHiddenInput();
  
  if (especialidadEliminada) {
    Utils.showMessage(`✓ Especialidad "${especialidadEliminada.nombre}" eliminada`, false);
  }
}

function actualizarListaEspecialidades() {
  const lista = document.getElementById('lista-especialidades');
  if (!lista) return;
  
  if (especialidadesArray.length === 0) {
    lista.innerHTML = '<div class="especialidades-empty">No hay especialidades agregadas</div>';
    return;
  }
  
  lista.innerHTML = especialidadesArray.map(esp => `
    <div class="especialidad-tag" data-id="${esp.id}">
      ${Utils.escapeHtml(esp.nombre)}
      <span class="remove-especialidad" data-id="${esp.id}" style="cursor:pointer; margin-left: 8px;">×</span>
    </div>
  `).join('');

  document.querySelectorAll('.remove-especialidad').forEach(btn => {
    btn.removeEventListener('click', handleRemoveEspecialidad);
    btn.addEventListener('click', handleRemoveEspecialidad);
  });
}

function handleRemoveEspecialidad(e) {
  e.stopPropagation();
  const id = e.currentTarget.getAttribute('data-id');
  eliminarEspecialidad(id);
}

function limpiarEspecialidades() {
  especialidadesArray = [];
  window.especialidadesArray = especialidadesArray;
  actualizarListaEspecialidades();
  actualizarHiddenInput();
  
  const selectEspecialidad = document.getElementById('select-especialidad');
  if (selectEspecialidad) {
    selectEspecialidad.value = '';
  }
}

function actualizarHiddenInput() {
  const hiddenInput = document.getElementById('especialidades-hidden');
  if (hiddenInput) {
    const ids = especialidadesArray.map(e => e.id);
    hiddenInput.value = JSON.stringify(ids);
  }
}

function setEspecialidades(especialidadesIds) {
  especialidadesArray = [];
  especialidadesIds.forEach(id => {
    const esp = especialidadesList.find(e => e.ID_especialidad == id);
    if (esp) {
      especialidadesArray.push({ id: String(id), nombre: esp.Nombre_especialidad });
    }
  });
  window.especialidadesArray = especialidadesArray;
  actualizarListaEspecialidades();
  actualizarHiddenInput();
}

function toggleEspecialidades() {
  const cargoSelect = document.getElementById('reg-cargo-empleado');
  const container = document.getElementById('especialidades-container');
  const selectedOption = cargoSelect?.options[cargoSelect.selectedIndex];
  const cargoNombre = selectedOption?.textContent;
  const isTecnico = cargoNombre === 'Técnico' || cargoNombre === 'Tecnico';
  
  if (container) {
    container.style.display = isTecnico ? 'block' : 'none';
  }
  if (!isTecnico) limpiarEspecialidades();
}

// ============================================
// 7. CRUD DE EMPLEADOS
// ============================================
async function cargarEmpleados() {
  try {
    const data = await Utils.fetchJson(CONFIG.API.EMPLEADOS, { method: 'GET' });
    const empleados = Array.isArray(data) ? data : (data?.empleados || data?.data || []);
    renderTabla(empleados);
  } catch (error) {
    Utils.showMessage(error.message || 'No fue posible cargar los empleados.', true);
    renderTabla([]);
  }
}

async function registrarEmpleado(event) {
  event.preventDefault();
  
  // Verificar si la cédula es válida (no existe)
  if (cedulaVerificada.exists) {
    Utils.showMessage('No se puede registrar: La cédula ya está registrada en el sistema', true);
    return;
  }
  
  if (cedulaVerificada.checking) {
    Utils.showMessage('Esperando verificación de cédula...', true);
    return;
  }
  
  const form = document.getElementById('form-registrar-empleado');
  const mode = form.dataset.mode;
  const editId = document.getElementById('edit-id-empleado')?.value;
  
  const cedulaValue = document.getElementById('reg-cedula-empleado')?.value.trim() || '';
  
  // Validar longitud de cédula
  if (cedulaValue.length !== 8) {
    Utils.showMessage('La cédula debe tener exactamente 8 dígitos', true);
    return;
  }
  
  const formData = {
    cedula: cedulaValue,
    nombre: document.getElementById('reg-nombre-empleado')?.value.trim(),
    apellido: document.getElementById('reg-apellido-empleado')?.value.trim(),
    id_cargo: document.getElementById('reg-cargo-empleado')?.value,
    celular: document.getElementById('reg-celular-empleado')?.value.trim(),
    correo: document.getElementById('reg-correo-empleado')?.value.trim(),
    direccion: document.getElementById('reg-direccion-empleado')?.value.trim(),
    especialidades: especialidadesArray.map(e => e.id)
  };
  
  if (!formData.cedula || !formData.nombre || !formData.apellido || !formData.id_cargo) {
    Utils.showMessage('Por favor complete los campos requeridos: Cédula, Nombre, Apellido y Cargo', true);
    return;
  }
  
  try {
    let response;
    
    if (mode === 'edit' && editId) {
      const updateData = {
        id_empleado: editId,
        cedula: formData.cedula,
        nombre: formData.nombre,
        apellido: formData.apellido,
        id_cargo: formData.id_cargo,
        celular: formData.celular,
        correo: formData.correo,
        direccion: formData.direccion,
        especialidades: formData.especialidades
      };
      
      response = await Utils.fetchJson(CONFIG.API.EMPLEADOS, {
        method: 'PUT',
        body: JSON.stringify(updateData)
      });
      
      if (response.success) {
        Utils.showMessage(response.message || 'Empleado actualizado exitosamente');
      }
    } else {
      response = await Utils.fetchJson(CONFIG.API.EMPLEADOS, {
        method: 'POST',
        body: JSON.stringify(formData)
      });
      
      if (response.success) {
        Utils.showMessage(response.message || 'Empleado registrado exitosamente');
      }
    }
    
    if (response.success) {
      form.reset();
      limpiarEspecialidades();
      closeModal('modal-registrar-empleado');
      await cargarEmpleados();
      await cargarGraficos();
    } else {
      Utils.showMessage(response.error || response.message || 'Error al procesar la solicitud', true);
    }
  } catch (error) {
    console.error('Error:', error);
    Utils.showMessage(error.message || 'Error al conectar con el servidor', true);
  }
}

async function eliminarEmpleado(cedula) {
  try {
    const response = await Utils.fetchJson(CONFIG.API.EMPLEADOS, {
      method: 'DELETE',
      body: JSON.stringify({ id_empleado: cedula })
    });
    
    if (response.success) {
      Utils.showMessage(response.message || 'Empleado eliminado exitosamente');
      closeModal('modal-eliminar-empleado');
      await cargarEmpleados();
      await cargarGraficos();
    } else {
      Utils.showMessage(response.error || response.message || 'Error al eliminar empleado', true);
    }
  } catch (error) {
    Utils.showMessage(error.message || 'Error al conectar con el servidor', true);
  }
}

// ============================================
// 8. CIERRE DE MODALES (Click fuera y ESC)
// ============================================
document.addEventListener('click', (e) => {
  if (e.target.classList && e.target.classList.contains('modal')) {
    const modalId = e.target.getAttribute('id');
    closeModal(modalId);
  }
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    const modalesAbiertos = document.querySelectorAll('.modal[aria-hidden="false"]');
    modalesAbiertos.forEach(modal => {
      closeModal(modal.getAttribute('id'));
    });
  }
});

// ============================================
// 9. INICIALIZACIÓN
// ============================================
document.addEventListener('DOMContentLoaded', async () => {
  await cargarCargosYEspecialidades();
  await cargarEmpleados();
  await cargarGraficos();
  
  const formEmpleado = document.getElementById('form-registrar-empleado');
  if (formEmpleado) {
    formEmpleado.removeEventListener('submit', registrarEmpleado);
    formEmpleado.addEventListener('submit', registrarEmpleado);
  }
  
  const cargoSelect = document.getElementById('reg-cargo-empleado');
  if (cargoSelect) {
    cargoSelect.removeEventListener('change', toggleEspecialidades);
    cargoSelect.addEventListener('change', toggleEspecialidades);
  }
  
  const btnActualizar = document.getElementById('btn-actualizar-empleados');
  if (btnActualizar) {
    btnActualizar.removeEventListener('click', cargarEmpleados);
    btnActualizar.addEventListener('click', cargarEmpleados);
  }
  
  const btnNuevo = document.querySelector('[data-open-modal="modal-registrar-empleado"]');
  if (btnNuevo) {
    btnNuevo.removeEventListener('click', () => openModal('modal-registrar-empleado', 'register'));
    btnNuevo.addEventListener('click', () => openModal('modal-registrar-empleado', 'register'));
  }
  
  const confirmarEliminar = document.getElementById('btn-confirmar-eliminar-empleado');
  if (confirmarEliminar) {
    confirmarEliminar.removeEventListener('click', () => {
      const cedula = confirmarEliminar.getAttribute('data-cedula');
      if (cedula) eliminarEmpleado(cedula);
    });
    confirmarEliminar.addEventListener('click', () => {
      const cedula = confirmarEliminar.getAttribute('data-cedula');
      if (cedula) eliminarEmpleado(cedula);
    });
  }
  
  document.querySelectorAll('[data-close-modal]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const modal = btn.closest('.modal');
      if (modal) {
        closeModal(modal.getAttribute('id'));
      }
    });
  });
  
  // ============================================
  // VALIDACIÓN DE CÉDULA EN TIEMPO REAL
  // ============================================
  const cedulaInput = document.getElementById('reg-cedula-empleado');
  if (cedulaInput) {
    // Evento input para validar en tiempo real
    cedulaInput.addEventListener('input', (e) => {
      let valor = e.target.value.replace(/\D/g, ''); // Solo números
      if (valor.length > 8) valor = valor.slice(0, 8);
      e.target.value = valor;
      
      const mode = document.getElementById('form-registrar-empleado')?.dataset.mode;
      const editId = document.getElementById('edit-id-empleado')?.value;
      
      if (mode === 'edit') {
        // En modo edición, no validar porque la cédula está deshabilitada
        return;
      }
      
      verificarCedulaEnTiempoReal(valor, editId);
    });
    
    // Evento blur para validación final
    cedulaInput.addEventListener('blur', (e) => {
      const valor = e.target.value;
      const mode = document.getElementById('form-registrar-empleado')?.dataset.mode;
      
      if (mode === 'edit') return;
      
      if (valor && valor.length !== 8) {
        mostrarValidacionCedula(false, false, '⚠️ La cédula debe tener exactamente 8 dígitos');
      }
    });
  }
  
  const reglasValidacion = Utils.validarCampos();
  
  const nombreInput = document.getElementById('reg-nombre-empleado');
  const apellidoInput = document.getElementById('reg-apellido-empleado');
  
  [nombreInput, apellidoInput].forEach(input => {
    if (input) {
      input.addEventListener('input', (e) => {
        const valor = e.target.value;
        if (!reglasValidacion.soloLetras(valor) && valor !== '') {
          e.target.style.borderColor = '#dc3545';
          e.target.setCustomValidity('Solo se permiten letras, espacios, acentos y ñ');
        } else {
          e.target.style.borderColor = '';
          e.target.setCustomValidity('');
          if (valor.length > 0 && e.inputType !== 'deleteContentBackward') {
            const palabras = valor.split(' ');
            const capitalizado = palabras.map(p => p.charAt(0).toUpperCase() + p.slice(1).toLowerCase()).join(' ');
            if (capitalizado !== valor) {
              e.target.value = capitalizado;
            }
          }
        }
      });
    }
  });
  
  const celularInput = document.getElementById('reg-celular-empleado');
  if (celularInput) {
    celularInput.addEventListener('input', (e) => {
      const valor = e.target.value;
      if (!reglasValidacion.telefono(valor) && valor !== '') {
        e.target.style.borderColor = '#dc3545';
        e.target.setCustomValidity('El celular debe tener 11 dígitos (ej: 04141234567)');
      } else {
        e.target.style.borderColor = '';
        e.target.setCustomValidity('');
      }
    });
  }
  
  const correoInput = document.getElementById('reg-correo-empleado');
  if (correoInput) {
    correoInput.addEventListener('input', (e) => {
      const valor = e.target.value;
      if (!reglasValidacion.email(valor) && valor !== '') {
        e.target.style.borderColor = '#dc3545';
        e.target.setCustomValidity('Ingrese un correo electrónico válido');
      } else {
        e.target.style.borderColor = '';
        e.target.setCustomValidity('');
      }
    });
  }
  
  const direccionInput = document.getElementById('reg-direccion-empleado');
  if (direccionInput) {
    direccionInput.addEventListener('input', (e) => {
      const valor = e.target.value;
      if (!reglasValidacion.sinCaracteresEspeciales(valor) && valor !== '') {
        e.target.style.borderColor = '#dc3545';
        e.target.setCustomValidity('Sin caracteres especiales (solo letras, números, espacios, comas, puntos y guiones)');
      } else {
        e.target.style.borderColor = '';
        e.target.setCustomValidity('');
      }
    });
  }
});

window.empleadosApp = {
  openModal,
  closeModal,
  cargarEmpleados,
  cargarGraficos,
  verEmpleado,
  editarEmpleado,
  eliminarEmpleado
};