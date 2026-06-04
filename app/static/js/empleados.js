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
  }
};

// ============================================
// 3. MANEJADORES DE MODALES (SIMPLE)
// ============================================
function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    // Si es el modal de empleados, asegurar estado correcto
    if (id === 'modal-registrar-empleado') {
      // Verificar si estamos en modo edición
      const editId = document.getElementById('edit-id-empleado');
      
      if (!editId) {
        // Modo registro - asegurar textos correctos
        const modalTitle = modal.querySelector('.modal__title');
        if (modalTitle) modalTitle.textContent = 'Registrar nuevo empleado';
        
        const submitBtn = modal.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.textContent = 'Guardar empleado';
        
        // Resetear formulario
        const form = modal.querySelector('form');
        if (form) form.reset();
        
        // Ocultar especialidades
        const especialidadesContainer = document.getElementById('especialidades-container');
        if (especialidadesContainer) {
          especialidadesContainer.style.display = 'none';
        }
        
        // Limpiar especialidades
        limpiarEspecialidades();
        
        // Resetear select de cargo
        const cargoSelect = document.getElementById('reg-cargo-empleado');
        if (cargoSelect) {
          cargoSelect.value = '';
        }
      }
    }
    
    modal.removeAttribute("hidden");
    modal.setAttribute("aria-hidden", "false");
  }
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.setAttribute("hidden", "");
    modal.setAttribute("aria-hidden", "true");
    
    // Limpiar el formulario y restaurar textos a estado inicial
    if (id === 'modal-registrar-empleado') {
      const form = modal.querySelector('form');
      if (form) {
        form.reset();
        
        // Restaurar título del modal
        const modalTitle = modal.querySelector('.modal__title');
        if (modalTitle) {
          modalTitle.textContent = 'Registrar nuevo empleado';
        }
        
        // Restaurar texto del botón
        const submitBtn = modal.querySelector('button[type="submit"]');
        if (submitBtn) {
          submitBtn.textContent = 'Guardar empleado';
        }
        
        // Limpiar especialidades
        const especialidadesContainer = document.getElementById('especialidades-container');
        if (especialidadesContainer) {
          especialidadesContainer.style.display = 'none';
        }
        
        // Limpiar lista de especialidades
        const listaEspecialidades = document.getElementById('lista-especialidades');
        if (listaEspecialidades) {
          listaEspecialidades.innerHTML = '<div class="especialidades-empty">No hay especialidades agregadas</div>';
        }
        
        // Limpiar hidden input
        const hiddenInput = document.getElementById('especialidades-hidden');
        if (hiddenInput) {
          hiddenInput.value = '';
        }
        
        // Limpiar arreglo de especialidades
        especialidadesArray = [];
        window.especialidadesArray = especialidadesArray;
        
        // Eliminar campo oculto de edición
        const editId = document.getElementById('edit-id-empleado');
        if (editId) {
          editId.remove();
        }
        
        // Resetear select de cargo
        const cargoSelect = document.getElementById('reg-cargo-empleado');
        if (cargoSelect) {
          cargoSelect.value = '';
        }
      }
    }
  }
}

// ============================================
// 4. MANEJADORES DE TABLA
// ============================================
function renderTabla(empleados) {
  const tbody = document.getElementById("tabla-empleados");
  const contador = document.querySelector("[data-count]");
  
  if (!tbody) return;

  if (!empleados || empleados.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="table__empty">No hay empleados para mostrar.</td></tr>`;
    if (contador) {
      contador.setAttribute("data-count", "0");
      contador.textContent = "0";
    }
    return;
  }

  tbody.innerHTML = empleados.map(empleado => `
    <tr data-cedula="${Utils.escapeHtml(empleado.cedula || '')}">
      <td>${Utils.escapeHtml(empleado.cedula || '')}</td>
      <td>${Utils.escapeHtml(empleado.nombre || '')}</td>
      <td>${Utils.escapeHtml(empleado.apellido || '')}</td>
      <td>${Utils.escapeHtml(empleado.cargo || '-')}</td>
      <td class="table__actions">
        <div class="row-actions" aria-label="Acciones del empleado">
          <button type="button" class="table-action table-action--accent" data-action="editar" data-cedula="${Utils.escapeHtml(empleado.cedula || '')}">Modificar</button>
          <button type="button" class="table-action table-action--ghost" data-action="ver" data-cedula="${Utils.escapeHtml(empleado.cedula || '')}">Ver</button>
          <button type="button" class="table-action table-action--danger" data-action="eliminar" data-cedula="${Utils.escapeHtml(empleado.cedula || '')}">Eliminar</button>
        </div>
      </td>
    </tr>
  `).join('');

  if (contador) {
    contador.setAttribute("data-count", String(empleados.length));
    contador.textContent = String(empleados.length);
  }
}

// ============================================
// 5. MANEJADORES DE GRÁFICOS
// ============================================
async function cargarGraficos() {
  try {
    const data = await Utils.fetchJson(CONFIG.API.GRAFICOS);
    
    if (data.cargos && data.cargos.length > 0) {
      const labels = data.cargos.map(item => item.Nombre_cargo);
      const values = data.cargos.map(item => item.cantidad_personas);
      crearGraficoPie('miGrafico1', CONFIG.CHART_COLORS.PIE_1, labels, values);
    }
    
    if (data.especialidades && data.especialidades.length > 0) {
      const labels = data.especialidades.map(item => item.Nombre_especialidad);
      const values = data.especialidades.map(item => item.cantidad_personas);
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
let especialidadesList = [];
let cargosList = [];
let especialidadesArray = [];
window.especialidadesArray = especialidadesArray;

async function cargarCargosYEspecialidades() {
  try {
    const data = await Utils.fetchJson(CONFIG.API.LISTA);
    
    if (data.cargos && data.cargos.length > 0) {
      cargosList = data.cargos;
      llenarSelectCargos();
    }
    
    if (data.especialidades && data.especialidades.length > 0) {
      especialidadesList = data.especialidades;
      llenarSelectEspecialidades();
    }
  } catch (error) {
    console.error('Error cargando datos:', error);
    cargosList = [
      { ID_cargo: 1, Nombre_cargo: 'Administrador' },
      { ID_cargo: 2, Nombre_cargo: 'Tecnico' },
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
}

function toggleEspecialidades() {
  const cargoSelect = document.getElementById('reg-cargo-empleado');
  const container = document.getElementById('especialidades-container');
  const selectedOption = cargoSelect?.options[cargoSelect.selectedIndex];
  const cargoNombre = selectedOption?.textContent;
  const isTecnico = cargoNombre === 'Tecnico' || cargoNombre === 'Técnico';
  
  if (container) {
    container.style.display = isTecnico ? 'block' : 'none';
  }
  if (!isTecnico) limpiarEspecialidades();
}

function agregarEspecialidad() {
  const selectEspecialidad = document.getElementById('select-especialidad');
  const especialidadId = selectEspecialidad?.value;
  if (!especialidadId) return;
  
  const especialidadNombre = selectEspecialidad?.options[selectEspecialidad.selectedIndex]?.textContent;
  
  if (especialidadesArray.some(e => e.id === especialidadId)) {
    Utils.showMessage('Esta especialidad ya ha sido agregada', true);
    selectEspecialidad.value = '';
    return;
  }

  especialidadesArray.push({ id: especialidadId, nombre: especialidadNombre });
  actualizarListaEspecialidades();
  selectEspecialidad.value = '';
  actualizarHiddenInput();
}

function eliminarEspecialidad(especialidadId) {
  especialidadesArray = especialidadesArray.filter(esp => esp.id !== especialidadId);
  window.especialidadesArray = especialidadesArray;
  actualizarListaEspecialidades();
  actualizarHiddenInput();
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
      <span class="remove-especialidad" data-id="${esp.id}" style="cursor:pointer;">×</span>
    </div>
  `).join('');

  document.querySelectorAll('.remove-especialidad').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      eliminarEspecialidad(btn.getAttribute('data-id'));
    });
  });
}

function limpiarEspecialidades() {
  especialidadesArray = [];
  window.especialidadesArray = especialidadesArray;
  actualizarListaEspecialidades();
  actualizarHiddenInput();
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
      especialidadesArray.push({ id: id, nombre: esp.Nombre_especialidad });
    }
  });
  window.especialidadesArray = especialidadesArray;
  actualizarListaEspecialidades();
  actualizarHiddenInput();
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
  
  const formData = {
    cedula: document.getElementById('reg-cedula-empleado')?.value.trim() || '',
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
    const response = await Utils.fetchJson(CONFIG.API.EMPLEADOS, {
      method: 'POST',
      body: JSON.stringify(formData)
    });
    
    if (response.success) {
      Utils.showMessage(response.message || 'Empleado registrado exitosamente');
      document.getElementById('form-registrar-empleado')?.reset();
      limpiarEspecialidades();
      closeModal('modal-registrar-empleado');
      await cargarEmpleados();
      await cargarGraficos();
    } else {
      Utils.showMessage(response.error || response.message || 'Error al registrar empleado', true);
    }
  } catch (error) {
    console.error('Error:', error);
    Utils.showMessage(error.message || 'Error al conectar con el servidor', true);
  }
}

async function editarEmpleado(cedula) {
  try {
    const response = await Utils.fetchJson(CONFIG.API.CONSULTAR, {
      method: 'POST',
      body: JSON.stringify({ cedula: cedula })
    });
    
    if (response.success && response.empleado) {
      llenarFormularioEdicion(response.empleado, response.especialidades || []);
      openModal('modal-registrar-empleado');
    } else {
      Utils.showMessage('No se encontró el empleado', true);
    }
  } catch (error) {
    Utils.showMessage('Error al cargar datos del empleado', true);
  }
}

function llenarFormularioEdicion(empleado, especialidades) {
  const cedulaInput = document.getElementById('reg-cedula-empleado');
  const nombreInput = document.getElementById('reg-nombre-empleado');
  const apellidoInput = document.getElementById('reg-apellido-empleado');
  const cargoSelect = document.getElementById('reg-cargo-empleado');
  const celularInput = document.getElementById('reg-celular-empleado');
  const correoInput = document.getElementById('reg-correo-empleado');
  const direccionInput = document.getElementById('reg-direccion-empleado');
  
  if (cedulaInput) cedulaInput.value = empleado.cedula || '';
  if (nombreInput) nombreInput.value = empleado.nombre || '';
  if (apellidoInput) apellidoInput.value = empleado.apellido || '';
  if (cargoSelect) {
    const option = Array.from(cargoSelect.options).find(opt => opt.text === empleado.cargo);
    if (option) cargoSelect.value = option.value;
  }
  if (celularInput) celularInput.value = empleado.celular || '';
  if (correoInput) correoInput.value = empleado.correo || '';
  if (direccionInput) direccionInput.value = empleado.direccion || '';
  
  const esTecnico = empleado.cargo === 'Técnico' || empleado.cargo === 'Tecnico';
  if (esTecnico && especialidades.length > 0) {
    setEspecialidades(especialidades);
    toggleEspecialidades();
  }
  
  const modalTitle = document.querySelector('#modal-registrar-empleado .modal__title');
  if (modalTitle) modalTitle.textContent = 'Editar empleado';
  
  let hiddenId = document.getElementById('edit-id-empleado');
  if (!hiddenId) {
    hiddenId = document.createElement('input');
    hiddenId.type = 'hidden';
    hiddenId.id = 'edit-id-empleado';
    hiddenId.name = 'id_empleado';
    document.getElementById('form-registrar-empleado')?.appendChild(hiddenId);
  }
  hiddenId.value = empleado.cedula;
  
  const submitBtn = document.querySelector('#form-registrar-empleado button[type="submit"]');
  if (submitBtn) {
    submitBtn.textContent = 'Actualizar empleado';
  }
}

async function actualizarEmpleado(event) {
  event.preventDefault();
  
  const editId = document.getElementById('edit-id-empleado');
  if (!editId) {
    // Si no hay editId, es un registro nuevo
    return registrarEmpleado(event);
  }
  
  const formData = {
    id_empleado: editId.value,
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
    const response = await Utils.fetchJson(CONFIG.API.EMPLEADOS, {
      method: 'PUT',
      body: JSON.stringify(formData)
    });
    
    if (response.success) {
      Utils.showMessage(response.message || 'Empleado actualizado exitosamente');
      closeModal('modal-registrar-empleado');
      await cargarEmpleados();
      await cargarGraficos();
    } else {
      Utils.showMessage(response.error || response.message || 'Error al actualizar', true);
    }
  } catch (error) {
    Utils.showMessage(error.message || 'Error al conectar con el servidor', true);
  }
}

async function verEmpleado(cedula) {
  try {
    const response = await Utils.fetchJson(CONFIG.API.CONSULTAR, {
      method: 'POST',
      body: JSON.stringify({ cedula: cedula })
    });
    
    if (response.success && response.empleado) {
      mostrarModalVer(response.empleado, response.especialidades || []);
    } else {
      Utils.showMessage('No se encontró el empleado', true);
    }
  } catch (error) {
    Utils.showMessage('Error al cargar datos del empleado', true);
  }
}

function mostrarModalVer(empleado, especialidades) {
  let modal = document.getElementById('modal-ver-empleado');
  if (!modal) {
    const modalHTML = `
      <div class="modal" id="modal-ver-empleado" role="dialog" aria-modal="true" hidden>
        <div class="modal__overlay" data-close-modal></div>
        <div class="modal__container modal__container--md">
          <div class="modal__header">
            <h2 class="modal__title">Detalles del empleado</h2>
            <button type="button" class="modal__close" data-close-modal aria-label="Cerrar">×</button>
          </div>
          <div class="modal__body"></div>
          <div class="modal__footer">
            <button type="button" class="ui-btn ui-btn--primary" data-close-modal>Cerrar</button>
          </div>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    modal = document.getElementById('modal-ver-empleado');
  }
  
  const contenido = `
    <div class="ver-empleado-content">
      <div class="ver-empleado-field">
        <label>Cédula:</label>
        <span>${Utils.escapeHtml(empleado.cedula || '')}</span>
      </div>
      <div class="ver-empleado-field">
        <label>Nombre:</label>
        <span>${Utils.escapeHtml(empleado.nombre || '')}</span>
      </div>
      <div class="ver-empleado-field">
        <label>Apellido:</label>
        <span>${Utils.escapeHtml(empleado.apellido || '')}</span>
      </div>
      <div class="ver-empleado-field">
        <label>Cargo:</label>
        <span>${Utils.escapeHtml(empleado.cargo || '')}</span>
      </div>
      <div class="ver-empleado-field">
        <label>Celular:</label>
        <span>${Utils.escapeHtml(empleado.celular || '-')}</span>
      </div>
      <div class="ver-empleado-field">
        <label>Correo:</label>
        <span>${Utils.escapeHtml(empleado.correo || '-')}</span>
      </div>
      <div class="ver-empleado-field">
        <label>Dirección:</label>
        <span>${Utils.escapeHtml(empleado.direccion || '-')}</span>
      </div>
      ${empleado.cargo === 'Técnico' || empleado.cargo === 'Tecnico' ? `
        <div class="ver-empleado-field">
          <label>Especialidades:</label>
          <span>${especialidades.length > 0 ? especialidades.join(', ') : 'Ninguna'}</span>
        </div>
      ` : ''}
    </div>
  `;
  
  const body = modal.querySelector('.modal__body');
  if (body) body.innerHTML = contenido;
  
  openModal('modal-ver-empleado');
}

let empleadoPendienteEliminar = null;

function confirmarEliminarEmpleado(cedula, nombre, apellido) {
  empleadoPendienteEliminar = { cedula, nombre, apellido };
  const textoElem = document.getElementById('texto-confirmar-eliminar-empleado');
  if (textoElem) {
    textoElem.textContent = `¿Estás seguro de que quieres eliminar a ${nombre} ${apellido}?`;
  }
  openModal('modal-eliminar-empleado');
}

async function eliminarEmpleado() {
  if (!empleadoPendienteEliminar?.cedula) return;
  
  try {
    const response = await Utils.fetchJson(CONFIG.API.EMPLEADOS, {
      method: 'DELETE',
      body: JSON.stringify({ id_empleado: empleadoPendienteEliminar.cedula })
    });
    
    if (response.success) {
      Utils.showMessage(response.message || 'Empleado eliminado exitosamente');
      empleadoPendienteEliminar = null;
      closeModal('modal-eliminar-empleado');
      await cargarEmpleados();
      await cargarGraficos();
    } else {
      Utils.showMessage(response.error || response.message || 'Error al eliminar', true);
    }
  } catch (error) {
    Utils.showMessage(error.message || 'Error al conectar con el servidor', true);
  }
}

// ============================================
// 8. EVENTOS E INICIALIZACIÓN
// ============================================
document.addEventListener("DOMContentLoaded", async () => {
  // Inicializar modales
  const modal = document.getElementById('modal-registrar-empleado');
  if (modal) {
    modal.setAttribute('hidden', '');
  }
  
  // Eventos de los modales
  document.querySelectorAll('[data-open-modal]').forEach(btn => {
    btn.addEventListener('click', () => {
      const modalId = btn.getAttribute('data-open-modal');
      openModal(modalId);
    });
  });
  
  document.querySelectorAll('[data-close-modal]').forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = btn.closest('[data-modal]');
      if (modal) {
        closeModal(modal.id);
      }
    });
  });
  
  // Evento del formulario
  const form = document.getElementById('form-registrar-empleado');
  if (form) {
    form.addEventListener('submit', (e) => {
      const editId = document.getElementById('edit-id-empleado');
      if (editId) {
        actualizarEmpleado(e);
      } else {
        registrarEmpleado(e);
      }
    });
  }
  
  // Evento del select de cargo
  const cargoSelect = document.getElementById('reg-cargo-empleado');
  if (cargoSelect) {
    cargoSelect.addEventListener('change', toggleEspecialidades);
  }
  
  // Evento del botón de agregar especialidad
  const btnAgregarEspecialidad = document.getElementById('btn-agregar-especialidad');
  if (btnAgregarEspecialidad) {
    btnAgregarEspecialidad.addEventListener('click', agregarEspecialidad);
  }
  
  // Eventos de la tabla
  const tbody = document.getElementById('tabla-empleados');
  if (tbody) {
    tbody.addEventListener('click', (event) => {
      const button = event.target.closest('button[data-action]');
      if (!button) return;
      
      const action = button.getAttribute('data-action');
      const cedula = button.getAttribute('data-cedula');
      const nombre = button.getAttribute('data-nombre') || '';
      const apellido = button.getAttribute('data-apellido') || '';
      
      if (action === 'editar') {
        editarEmpleado(cedula);
      } else if (action === 'eliminar') {
        confirmarEliminarEmpleado(cedula, nombre, apellido);
      } else if (action === 'ver') {
        verEmpleado(cedula);
      }
    });
  }
  
  // Evento del botón de confirmar eliminar
  const btnConfirmarEliminar = document.getElementById('btn-confirmar-eliminar-empleado');
  if (btnConfirmarEliminar) {
    btnConfirmarEliminar.addEventListener('click', eliminarEmpleado);
  }
  
  // Evento del botón actualizar
  const btnActualizar = document.getElementById('btn-actualizar-empleados');
  if (btnActualizar) {
    btnActualizar.addEventListener('click', () => {
      cargarEmpleados().catch(error => {
        Utils.showMessage(error.message || 'No fue posible actualizar los empleados.', true);
      });
    });
  }
  
  // Cargar datos iniciales
  await cargarCargosYEspecialidades();
  await cargarEmpleados();
  await cargarGraficos();
});