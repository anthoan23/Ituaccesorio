// ============================================
// 1. CONSTANTES Y CONFIGURACIÓN
// ============================================
const CONFIG = {
  API: {
    EMPLEADOS: '/api/empleados',
    CONSULTAR: '/api/empleados/consultar',
    LISTA: '/api/empleados/lista',
    GRAFICOS: '/api/empleados/graficos'
  },
  CHART_COLORS: {
    PIE_1: {
      BACKGROUND: ['#f3c500', '#f8dd69', '#e6a817', '#ffce54', '#d4a017', '#f39c12', '#e67e22', '#c9971f'],
      BORDER: ['#1e1e1e', '#1e1e1e', '#1e1e1e', '#1e1e1e', '#1e1e1e', '#1e1e1e', '#1e1e1e', '#1e1e1e']
    },
    PIE_2: {
      BACKGROUND: ['#007AFF', '#34C759', '#5ac8fa', '#5856d6', '#af52de', '#ff9500', '#ff2d55', '#30b0c7', '#5e5ce6', '#bf5af2'],
      BORDER: ['#1e1e1e', '#1e1e1e', '#1e1e1e', '#1e1e1e', '#1e1e1e', '#1e1e1e', '#1e1e1e', '#1e1e1e', '#1e1e1e', '#1e1e1e']
    }
  }
};

// ============================================
// 2. VALIDACIÓN ANTI-MANIPULACIÓN DE LA TABLA
// ============================================
const validadorEmpleados = ValidadorTabla.crear({
  tituloEntidad: 'El empleado',
  campoId: 'data-cedula'
});
let cedulaEliminarConfiable = null;
let cedulaEditarConfiable = null;

// ============================================
// 3. UTILIDADES
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
      ...options,
      credentials: "same-origin",
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

  // Muestra el mensaje en pantalla (FeedbackModal global) y en consola.
  showMessage(message, isError = false) {
    if (!message) return;
    console[isError ? 'error' : 'log'](message);

    if (window.FeedbackModal && typeof window.FeedbackModal.show === 'function') {
      window.FeedbackModal.show({
        type: isError ? 'error' : 'success',
        title: isError ? 'Atención' : 'Aviso',
        message
      });
    }
  }
};

// ============================================
// 4. MANEJO DE SELECT CON ICONO DINÁMICO
// ============================================
function initSelectIcons() {
  const selects = document.querySelectorAll('.select-wrapper select');

  selects.forEach(select => {
    select.removeEventListener('focus', handleSelectFocus);
    select.removeEventListener('blur', handleSelectBlur);
    select.addEventListener('focus', handleSelectFocus);
    select.addEventListener('blur', handleSelectBlur);

    if (select.value && select.value !== '') {
      select.parentElement.classList.add('has-value');
    }

    select.removeEventListener('change', handleSelectChange);
    select.addEventListener('change', handleSelectChange);
  });
}

function handleSelectFocus(e) {
  e.currentTarget.parentElement.classList.add('is-open');
}

function handleSelectBlur(e) {
  e.currentTarget.parentElement.classList.remove('is-open');
}

function handleSelectChange(e) {
  const wrapper = e.currentTarget.parentElement;
  wrapper.classList.toggle('has-value', Boolean(e.currentTarget.value));
}

// ============================================
// 5. LIMPIEZA DE VALIDACIONES EN MODALES
// ============================================
function resetModalValidations(modal) {
  if (!modal) return;

  const form = modal.querySelector('form');
  if (form && window.FieldValidator && typeof window.FieldValidator.resetForm === 'function') {
    try {
      window.FieldValidator.resetForm(form);
    } catch (e) {
      console.debug('Reset form falló, continuando con limpieza manual:', e);
    }
  }

  modal.querySelectorAll('.field-error, .field-success').forEach(el => {
    el.classList.remove('field-error', 'field-success');
  });

  modal.querySelectorAll('.field-message').forEach(el => {
    el.style.display = 'none';
    el.textContent = '';
    el.className = 'field-message field-error';
  });

  modal.querySelectorAll('.validation-icon').forEach(el => {
    el.style.display = 'none';
    el.className = 'validation-icon';
    el.innerHTML = '';
    delete el.dataset.currentType;
    el.classList.remove('visible', 'success', 'error', 'warning', 'icon-appear', 'icon-change', 'icon-hide');
  });

  modal.querySelectorAll('[aria-invalid]').forEach(el => {
    el.removeAttribute('aria-invalid');
  });

  modal.querySelectorAll('.field-counter').forEach(el => el.remove());
  modal.querySelectorAll('.field-warning').forEach(el => el.remove());
}

// ============================================
// 6. MANEJADORES DE MODALES
// ============================================
// Los modales usan el componente ui-modal; UiModal (global) ya maneja
// el cierre por ESC, click fuera y botones [data-close-modal].
function mostrarModal(modal) {
  if (window.UiModal && typeof window.UiModal.openById === 'function') {
    window.UiModal.openById(modal.id);
    return;
  }
  modal.removeAttribute('hidden');
  modal.setAttribute('aria-hidden', 'false');
}

function ocultarModal(modal) {
  if (window.UiModal && typeof window.UiModal.closeById === 'function') {
    window.UiModal.closeById(modal.id);
    return;
  }
  modal.setAttribute('hidden', '');
  modal.setAttribute('aria-hidden', 'true');
}

function resetSelects() {
  document.querySelectorAll('.select-wrapper select').forEach(select => {
    select.parentElement.classList.remove('is-open', 'has-value');
  });
}

// Restaura el formulario del modal de registro a su estado inicial.
// Se ejecuta al abrirlo en modo "register" y al cerrarse (vía observer).
function limpiarFormularioEmpleado() {
  cedulaEditarConfiable = null;

  const form = document.getElementById('form-registrar-empleado');
  if (form) {
    form.reset();
    form.dataset.mode = 'register';
  }

  const cedulaInput = document.getElementById('reg-cedula-empleado');
  if (cedulaInput) {
    cedulaInput.disabled = false;
    cedulaInput.value = '';
  }

  habilitarCamposFormulario(true);

  const especialidadesContainer = document.getElementById('especialidades-container');
  if (especialidadesContainer) especialidadesContainer.style.display = 'none';

  limpiarEspecialidades();
  resetSelects();
}

function observarCierreModal(id, alCerrar) {
  const modal = document.getElementById(id);
  if (!modal) return;

  const observer = new MutationObserver(() => {
    if (modal.hasAttribute('hidden')) alCerrar();
  });
  observer.observe(modal, { attributes: true, attributeFilter: ['hidden'] });
}

function openModal(id, mode = 'register', empleadoData = null, especialidadesData = null) {
  const modal = document.getElementById(id);
  if (!modal) return;

  resetModalValidations(modal);

  if (id === 'modal-registrar-empleado') {
    const modalTitle = modal.querySelector('.ui-modal__title');
    const submitBtn = modal.querySelector('#modal-submit-btn');
    const form = modal.querySelector('#form-registrar-empleado');

    if (mode === 'edit') {
      if (modalTitle) modalTitle.textContent = 'Modificar empleado';
      if (submitBtn) {
        submitBtn.textContent = 'Actualizar empleado';
        submitBtn.disabled = false;
        submitBtn.style.display = '';
      }
      if (form) form.dataset.mode = 'edit';

      habilitarCamposFormulario(true);
      const cedulaInput = document.getElementById('reg-cedula-empleado');
      if (cedulaInput) cedulaInput.disabled = true;

      if (empleadoData) {
        cargarDatosEnFormulario(empleadoData, especialidadesData);
      }
    } else {
      limpiarFormularioEmpleado();
      if (modalTitle) modalTitle.textContent = 'Registrar nuevo empleado';
      if (submitBtn) {
        submitBtn.textContent = 'Guardar empleado';
        submitBtn.disabled = false;
        submitBtn.style.display = '';
      }
    }

    setTimeout(initSelectIcons, 50);

    if (window.FieldValidator && typeof window.FieldValidator.initModalFields === 'function') {
      setTimeout(() => window.FieldValidator.initModalFields(modal), 100);
    }

  } else if (id === 'modal-ver-empleado') {
    if (empleadoData) {
      mostrarDetalleEmpleado(empleadoData, especialidadesData);
    }
  }

  mostrarModal(modal);
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) ocultarModal(modal);
}

// Desglosa la respuesta de la API en los datos del empleado y su lista
// de especialidades, según venga anidada ({empleado, especialidades}) o plana.
function desglosarRespuestaEmpleado(respuesta, especialidades = null) {
  if (respuesta?.empleado && !especialidades) {
    return {
      datos: respuesta.empleado,
      listaEspecialidades: respuesta.especialidades || []
    };
  }
  return { datos: respuesta, listaEspecialidades: especialidades };
}

function mostrarDetalleEmpleado(empleado, especialidades = null) {
  const { datos: empleadoData, listaEspecialidades: especialidadesData } = desglosarRespuestaEmpleado(empleado, especialidades);

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
    if (campo) campo.disabled = !habilitar;
  });

  const selectEspecialidad = document.getElementById('select-especialidad');
  if (selectEspecialidad) selectEspecialidad.disabled = !habilitar;

  document.querySelectorAll('.remove-especialidad').forEach(btn => {
    btn.style.display = habilitar ? '' : 'none';
  });
}

function cargarDatosEnFormulario(empleado, especialidades = null) {
  const { datos: empleadoData, listaEspecialidades: especialidadesData } = desglosarRespuestaEmpleado(empleado, especialidades);

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
    const option = Array.from(cargoSelect.options).find(opt => opt.text === empleadoData.cargo);
    if (option) {
      cargoSelect.value = option.value;
      cargoSelect.parentElement?.classList.add('has-value');
    }
  }

  if (especialidadesData && especialidadesData.length > 0) {
    const especialidadesIds = especialidadesData.map(e => e.id || e.ID_especialidad);
    if (especialidadesIds.length > 0) {
      setEspecialidades(especialidadesIds);
    }
  } else {
    limpiarEspecialidades();
  }

  toggleEspecialidades();
}

async function verEmpleado(cedula, cedulaConfiable = null) {
  if (!validadorEmpleados.validarId(cedula, 'consultar', cedulaConfiable)) return;

  try {
    const response = await Utils.fetchJson(CONFIG.API.CONSULTAR, {
      method: 'POST',
      body: JSON.stringify({ cedula: cedula })
    });

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

async function editarEmpleado(cedula, cedulaConfiable = null) {
  if (!validadorEmpleados.validarId(cedula, 'editar', cedulaConfiable)) return;
  cedulaEditarConfiable = String(cedula).trim();

  try {
    const response = await Utils.fetchJson(CONFIG.API.CONSULTAR, {
      method: 'POST',
      body: JSON.stringify({ cedula: cedula })
    });

    if (response.success) {
      openModal('modal-registrar-empleado', 'edit', response);
      setTimeout(() => {
        toggleEspecialidades();
        initSelectIcons();
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
// 7. TABLA DE EMPLEADOS
// ============================================
function normalizarEmpleado(empleado) {
  return {
    cedula: empleado?.cedula ?? empleado?.cedula_empleado ?? empleado?.id_empleado ?? '',
    nombre: empleado?.nombre ?? empleado?.nombre_empleado ?? '',
    apellido: empleado?.apellido ?? empleado?.apellido_empleado ?? '',
    cargo: empleado?.cargo ?? empleado?.nombre_cargo ?? '-'
  };
}

function renderTabla(empleados) {
  const tbody = document.getElementById("tabla-empleados");
  const contador = document.querySelector("[data-count]");

  if (!tbody) return;

  if (!empleados || empleados.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="table__empty">No hay empleados para mostrar.</td></tr>`;
    validadorEmpleados.registrarFilas(tbody);
    if (contador) {
      contador.setAttribute("data-count", "0");
      contador.textContent = "0";
    }
    return;
  }

  tbody.innerHTML = empleados.map(empleado => {
    const datos = normalizarEmpleado(empleado);
    const cedula = Utils.escapeHtml(datos.cedula);
    const nombre = Utils.escapeHtml(datos.nombre);
    const apellido = Utils.escapeHtml(datos.apellido);
    const cargo = Utils.escapeHtml(datos.cargo);

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

  validadorEmpleados.registrarFilas(tbody);

  if (contador) {
    contador.setAttribute("data-count", String(empleados.length));
    contador.textContent = String(empleados.length);
  }
}

function handleEditarClick(button) {
  const cedula = button.getAttribute('data-cedula');
  const cedulaConfiable = validadorEmpleados.validarFila(button, 'editar');
  if (cedulaConfiable === null) return;
  editarEmpleado(cedula, cedulaConfiable);
}

function handleVerClick(button) {
  const cedula = button.getAttribute('data-cedula');
  const cedulaConfiable = validadorEmpleados.validarFila(button, 'consultar');
  if (cedulaConfiable === null) return;
  verEmpleado(cedula, cedulaConfiable);
}

function handleEliminarClick(button) {
  const cedula = button.getAttribute('data-cedula');
  const cedulaConfiable = validadorEmpleados.validarFila(button, 'eliminar');
  if (cedulaConfiable === null) return;
  cedulaEliminarConfiable = cedulaConfiable;

  const nombre = button.getAttribute('data-nombre');
  const apellido = button.getAttribute('data-apellido');
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
// 8. GRÁFICOS
// ============================================
let graficoCargos = null;
let graficoEspecialidades = null;

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

function crearGraficoPie(canvasId, colores, labels, datos) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;

  if (canvasId === 'miGrafico1' && graficoCargos) graficoCargos.destroy();
  if (canvasId === 'miGrafico2' && graficoEspecialidades) graficoEspecialidades.destroy();

  const chart = new Chart(canvas, {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        data: datos,
        backgroundColor: colores.BACKGROUND.slice(0, labels.length),
        borderColor: colores.BORDER.slice(0, labels.length),
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            font: { size: 11 },
            color: getComputedStyle(document.documentElement).getPropertyValue('--text-strong').trim() || '#ffffff'
          }
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

  if (canvasId === 'miGrafico1') graficoCargos = chart;
  if (canvasId === 'miGrafico2') graficoEspecialidades = chart;

  return chart;
}

// ============================================
// 9. CARGOS Y ESPECIALIDADES DEL FORMULARIO
// ============================================
let especialidadesList = [];
let cargosList = [];
let especialidadesArray = [];

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
    console.error('Error cargando cargos y especialidades:', error);
    Utils.showMessage('No fue posible cargar los cargos y especialidades. Recarga la página para reintentar.', true);
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

  setTimeout(initSelectIcons, 50);
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

  setTimeout(initSelectIcons, 50);
}

function resaltarTemporal(selectEspecialidad, color) {
  selectEspecialidad.style.border = `2px solid ${color}`;
  setTimeout(() => {
    selectEspecialidad.style.border = '';
  }, 500);
}

function autoAgregarEspecialidad(event) {
  const selectEspecialidad = event.target;
  const especialidadId = selectEspecialidad.value;

  if (!especialidadId) return;

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
    resaltarTemporal(selectEspecialidad, 'red');
    selectEspecialidad.value = '';
    Utils.showMessage(`La especialidad "${especialidadNombre}" ya ha sido agregada`, true);
    return;
  }

  especialidadesArray.push({
    id: String(especialidadId),
    nombre: especialidadNombre
  });

  resaltarTemporal(selectEspecialidad, 'green');
  actualizarListaEspecialidades();
  selectEspecialidad.value = '';
  actualizarHiddenInput();
  Utils.showMessage(`✓ Especialidad "${especialidadNombre}" agregada`, false);
}

function eliminarEspecialidadSeleccionada(especialidadId) {
  const especialidadEliminada = especialidadesArray.find(esp => esp.id == especialidadId);
  especialidadesArray = especialidadesArray.filter(esp => esp.id != especialidadId);
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
      <span class="remove-especialidad" data-id="${esp.id}">×</span>
    </div>
  `).join('');

  document.querySelectorAll('.remove-especialidad').forEach(btn => {
    btn.removeEventListener('click', handleRemoveEspecialidad);
    btn.addEventListener('click', handleRemoveEspecialidad);
  });
}

function handleRemoveEspecialidad(e) {
  e.stopPropagation();
  eliminarEspecialidadSeleccionada(e.currentTarget.getAttribute('data-id'));
}

function limpiarEspecialidades() {
  especialidadesArray = [];
  actualizarListaEspecialidades();
  actualizarHiddenInput();

  const selectEspecialidad = document.getElementById('select-especialidad');
  if (selectEspecialidad) selectEspecialidad.value = '';
}

function actualizarHiddenInput() {
  const hiddenInput = document.getElementById('especialidades-hidden');
  if (hiddenInput) {
    hiddenInput.value = JSON.stringify(especialidadesArray.map(e => e.id));
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
// 10. CRUD DE EMPLEADOS
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

  const form = document.getElementById('form-registrar-empleado');
  const mode = form.dataset.mode;
  const editId = document.getElementById('edit-id-empleado')?.value;

  const formData = {
    cedula: document.getElementById('reg-cedula-empleado')?.value.trim(),
    nombre: document.getElementById('reg-nombre-empleado')?.value.trim(),
    apellido: document.getElementById('reg-apellido-empleado')?.value.trim(),
    id_cargo: document.getElementById('reg-cargo-empleado')?.value,
    celular: document.getElementById('reg-celular-empleado')?.value.trim(),
    correo: document.getElementById('reg-correo-empleado')?.value.trim(),
    direccion: document.getElementById('reg-direccion-empleado')?.value.trim(),
    especialidades: especialidadesArray.map(e => e.id)
  };

  try {
    let response;

    if (mode === 'edit' && editId) {
      if (!validadorEmpleados.validarId(editId, 'actualizar', cedulaEditarConfiable)) return;

      response = await Utils.fetchJson(CONFIG.API.EMPLEADOS, {
        method: 'PUT',
        body: JSON.stringify({ id_empleado: editId, ...formData })
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
  if (!validadorEmpleados.validarId(cedula, 'eliminar', cedulaEliminarConfiable)) return;

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
// 11. INICIALIZACIÓN
// ============================================
document.addEventListener('DOMContentLoaded', () => {
  initSelectIcons();
  vincularEventos();
  observarCierreModal('modal-registrar-empleado', limpiarFormularioEmpleado);
  observarCierreModal('modal-eliminar-empleado', () => {
    cedulaEliminarConfiable = null;
  });

  // Las tres cargas son independientes: se lanzan en paralelo.
  Promise.all([
    cargarCargosYEspecialidades(),
    cargarEmpleados(),
    cargarGraficos()
  ]).then(() => initSelectIcons());
});

function vincularEventos() {
  const formEmpleado = document.getElementById('form-registrar-empleado');
  if (formEmpleado) {
    formEmpleado.addEventListener('submit', registrarEmpleado);
  }

  const cargoSelect = document.getElementById('reg-cargo-empleado');
  if (cargoSelect) {
    cargoSelect.addEventListener('change', toggleEspecialidades);
  }

  const btnNuevo = document.querySelector('[data-open-modal="modal-registrar-empleado"]');
  if (btnNuevo) {
    btnNuevo.addEventListener('click', () => openModal('modal-registrar-empleado', 'register'));
  }

  const confirmarEliminar = document.getElementById('btn-confirmar-eliminar-empleado');
  if (confirmarEliminar) {
    confirmarEliminar.addEventListener('click', () => {
      const cedula = confirmarEliminar.getAttribute('data-cedula');
      if (cedula) eliminarEmpleado(cedula);
    });
  }

  iniciarEventosTabla();
}

// Delegación de eventos: un solo listener para todos los botones de la tabla.
function iniciarEventosTabla() {
  const tbody = document.getElementById('tabla-empleados');
  if (!tbody) return;

  tbody.addEventListener('click', (event) => {
    const button = event.target.closest('button[data-action]');
    if (!button) return;

    const action = button.getAttribute('data-action');
    if (action === 'editar') handleEditarClick(button);
    else if (action === 'ver') handleVerClick(button);
    else if (action === 'eliminar') handleEliminarClick(button);
  });
}

window.empleadosApp = {
  openModal,
  closeModal,
  cargarEmpleados,
  cargarGraficos,
  verEmpleado,
  editarEmpleado,
  eliminarEmpleado,
  initSelectIcons,
  resetModalValidations
};
