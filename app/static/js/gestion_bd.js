// ============================================
// 1. CONSTANTES Y CONFIGURACIÓN
// ============================================
const CONFIG = {
  API: {
    BACKUP_CREATE: '/api/backup/create',
    BACKUP_RESTORE: '/api/backup/restore',
    BACKUP_LIST: '/api/backup/list',
    BACKUP_DELETE: '/api/backup/delete'
  }
};

let currentAction = null;
let currentDb = null;

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

    // Para FormData no establecemos Content-Type, el navegador lo maneja automáticamente
    if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
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

  showMessage(message, isError = false) {
    if (!message) return;
    if (isError) {
      console.error(message);
      this.showToast(message, 'error');
    } else {
      console.info(message);
      this.showToast(message, 'success');
    }
  },

  showToast(message, type = 'info') {
    // Eliminar toasts existentes del mismo tipo si hay muchos
    const existingToasts = document.querySelectorAll('.toast');
    if (existingToasts.length >= 5) {
      existingToasts[0].remove();
    }

    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.className = 'toast-container';
      toastContainer.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 10px;
      `;
      document.body.appendChild(toastContainer);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Colores según tipo
    const colors = {
      success: '#28a745',
      error: '#dc3545',
      info: '#17a2b8',
      warning: '#ffc107'
    };
    
    toast.style.cssText = `
      background: ${colors[type] || colors.info};
      color: ${type === 'warning' ? '#000' : '#fff'};
      padding: 12px 20px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      animation: slideIn 0.3s ease;
      max-width: 350px;
      display: flex;
      align-items: center;
      gap: 10px;
    `;
    
    // Iconos según tipo
    const icons = {
      success: '✅',
      error: '❌',
      info: 'ℹ️',
      warning: '⚠️'
    };
    
    toast.innerHTML = `${icons[type] || icons.info} ${message}`;
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
      toast.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => {
        toast.remove();
        if (toastContainer.children.length === 0) {
          toastContainer.remove();
        }
      }, 300);
    }, 4000);
  },

  descargarArchivo(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  },

  formatearFecha() {
    const now = new Date();
    return now.toISOString().slice(0, 19).replace(/:/g, '-');
  },

  formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },

  escapeHtml(value) {
    if (!value) return '';
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
};

// ============================================
// 3. MANEJADORES DE MODALES
// ============================================
function openModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  
  modal.removeAttribute("hidden");
  modal.setAttribute("aria-hidden", "false");
  document.body.style.overflow = 'hidden';
  
  // Si es el modal de restore, limpiar formulario
  if (id === 'modal-restore') {
    const form = document.getElementById('form-restore');
    if (form) {
      form.reset();
    }
    const fileInput = document.getElementById('backup-file-input');
    if (fileInput) {
      fileInput.value = '';
    }
  }
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.setAttribute("hidden", "");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = '';
  }
}

// ============================================
// 4. FUNCIONES DE BACKUP (DESCARGAR)
// ============================================
async function realizarBackup(dbName) {
  const btn = document.querySelector(`.btn-backup[data-db="${dbName}"]`);
  const originalText = btn ? btn.textContent : 'Respaldo';
  
  try {
    if (btn) {
      btn.disabled = true;
      btn.textContent = '⏳ Generando...';
    }
    
    Utils.showToast(`Iniciando respaldo de ${dbName}...`, 'info');
    
    const response = await fetch(CONFIG.API.BACKUP_CREATE, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': Utils.getCsrfToken()
      },
      credentials: 'same-origin',
      body: JSON.stringify({ database: dbName })
    });
    
    if (!response.ok) {
      let errorMessage = 'Error al generar el respaldo';
      try {
        const errorData = await response.json();
        errorMessage = errorData.message || errorData.error || errorMessage;
      } catch (e) {
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }
    
    const blob = await response.blob();
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = `${dbName}_backup_${Utils.formatearFecha()}.sql`;
    
    if (contentDisposition) {
      const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
      if (match && match[1]) {
        filename = match[1].replace(/['"]/g, '');
      }
    }
    
    Utils.descargarArchivo(blob, filename);
    Utils.showToast(`✅ Respaldo de ${dbName} completado exitosamente`, 'success');
    
    // Actualizar lista de backups después de crear uno nuevo
    await cargarListaBackups();
    
  } catch (error) {
    console.error('Error en backup:', error);
    Utils.showToast(error.message || 'Error al generar el respaldo', 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = originalText;
    }
  }
}

// ============================================
// 5. FUNCIONES DE RESTORE (SUBIR)
// ============================================
async function realizarRestore(formData) {
  try {
    const dbName = formData.get('database_name');
    
    Utils.showToast(`Restaurando ${dbName}... Esto puede tomar unos momentos`, 'info');
    
    const response = await fetch(CONFIG.API.BACKUP_RESTORE, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': Utils.getCsrfToken()
      },
      credentials: 'same-origin'
    });
    
    const contentType = response.headers.get("content-type") || "";
    const isJson = contentType.includes("application/json");
    const result = isJson ? await response.json() : await response.text();
    
    if (!response.ok) {
      const msg = (isJson && result && (result.message || result.error)) || 'Error al restaurar la base de datos';
      throw new Error(msg);
    }
    
    const mensaje = (isJson && result.message) || `✅ Base de datos ${dbName} restaurada exitosamente`;
    Utils.showToast(mensaje, 'success');
    
    // Cerrar modal
    closeModal('modal-restore');
    
    // Recargar la página después de 2 segundos
    setTimeout(() => {
      if (confirm('Base de datos restaurada. ¿Deseas recargar la página para ver los cambios?')) {
        window.location.reload();
      }
    }, 1500);
    
  } catch (error) {
    console.error('Error en restore:', error);
    Utils.showToast(error.message || 'Error al restaurar la base de datos', 'error');
    throw error;
  }
}

// ============================================
// 6. FUNCIONES PARA LISTAR Y GESTIONAR BACKUPS
// ============================================
async function cargarListaBackups() {
  try {
    const response = await Utils.fetchJson(CONFIG.API.BACKUP_LIST, {
      method: 'GET'
    });
    
    if (response.success && response.backups) {
      mostrarListaBackups(response.backups);
    }
  } catch (error) {
    console.error('Error al cargar lista de backups:', error);
  }
}

function mostrarListaBackups(backups) {
  // Crear o actualizar sección de lista de backups si existe
  let listaContainer = document.getElementById('lista-backups-container');
  
  if (!listaContainer) {
    // Si no existe el contenedor, no mostrar la sección
    return;
  }
  
  let html = '<div class="backups-list">';
  
  for (const [dbName, dbBackups] of Object.entries(backups)) {
    if (dbBackups.length > 0) {
      html += `
        <div class="backup-group">
          <h4 class="backup-group-title">${Utils.escapeHtml(dbName)}</h4>
          <ul class="backup-files-list">
      `;
      
      dbBackups.forEach(backup => {
        html += `
          <li class="backup-file-item">
            <div class="backup-file-info">
              <span class="backup-filename">📄 ${Utils.escapeHtml(backup.filename)}</span>
              <span class="backup-filesize">${Utils.escapeHtml(backup.size_kb)} KB</span>
              <span class="backup-date">${Utils.escapeHtml(backup.modified)}</span>
            </div>
            <button class="btn-delete-backup" data-db="${Utils.escapeHtml(dbName)}" data-filename="${Utils.escapeHtml(backup.filename)}">
              🗑️ Eliminar
            </button>
          </li>
        `;
      });
      
      html += `
          </ul>
        </div>
      `;
    }
  }
  
  if (Object.values(backups).every(arr => arr.length === 0)) {
    html += '<p class="no-backups">No hay backups disponibles</p>';
  }
  
  html += '</div>';
  listaContainer.innerHTML = html;
  
  // Agregar eventos a los botones de eliminar
  document.querySelectorAll('.btn-delete-backup').forEach(btn => {
    btn.removeEventListener('click', handleEliminarBackup);
    btn.addEventListener('click', handleEliminarBackup);
  });
}

async function handleEliminarBackup(e) {
  const btn = e.currentTarget;
  const dbName = btn.getAttribute('data-db');
  const filename = btn.getAttribute('data-filename');
  
  if (confirm(`¿Estás seguro de que quieres eliminar el backup "${filename}" de ${dbName}?`)) {
    try {
      const response = await Utils.fetchJson(CONFIG.API.BACKUP_DELETE, {
        method: 'DELETE',
        body: JSON.stringify({
          database: dbName,
          filename: filename
        })
      });
      
      if (response.success) {
        Utils.showToast(response.message || 'Backup eliminado exitosamente', 'success');
        await cargarListaBackups();
      } else {
        Utils.showToast(response.error || 'Error al eliminar backup', 'error');
      }
    } catch (error) {
      console.error('Error al eliminar backup:', error);
      Utils.showToast(error.message || 'Error al eliminar backup', 'error');
    }
  }
}

// ============================================
// 7. VALIDACIONES DEL FORMULARIO
// ============================================
function validarArchivoBackup(file) {
  if (!file || file.size === 0) {
    Utils.showToast('Por favor selecciona un archivo de respaldo', 'error');
    return false;
  }
  
  // Validar tamaño del archivo (50MB máximo)
  const maxSize = 50 * 1024 * 1024;
  if (file.size > maxSize) {
    Utils.showToast(`El archivo no puede superar los ${Utils.formatBytes(maxSize)}`, 'error');
    return false;
  }
  
  // Validar extensión
  const validExtensions = ['.sql', '.gz', '.zip'];
  const fileName = file.name.toLowerCase();
  const isValidExtension = validExtensions.some(ext => fileName.endsWith(ext));
  
  if (!isValidExtension) {
    Utils.showToast(`Formato no válido. Usa: ${validExtensions.join(', ')}`, 'error');
    return false;
  }
  
  return true;
}

// ============================================
// 8. MANEJADORES DE EVENTOS DE BOTONES
// ============================================
function handleBackupClick(e) {
  const btn = e.currentTarget;
  const dbName = btn.getAttribute('data-db');
  
  if (dbName) {
    currentAction = 'backup';
    currentDb = dbName;
    
    const backupDbNameSpan = document.getElementById('backup-db-name');
    if (backupDbNameSpan) {
      backupDbNameSpan.textContent = dbName;
    }
    
    openModal('modal-backup');
  }
}

function handleRestoreClick(e) {
  const btn = e.currentTarget;
  const dbName = btn.getAttribute('data-db');
  
  if (dbName) {
    currentAction = 'restore';
    currentDb = dbName;
    
    const restoreDbNameInput = document.getElementById('restore-db-name');
    const restoreDbNameDisplay = document.getElementById('restore-db-name-display');
    
    if (restoreDbNameInput) {
      restoreDbNameInput.value = dbName;
    }
    if (restoreDbNameDisplay) {
      restoreDbNameDisplay.textContent = dbName;
    }
    
    openModal('modal-restore');
  }
}

// ============================================
// 9. INICIALIZACIÓN DE ANIMACIONES Y ESTILOS
// ============================================
function agregarEstilosAnimacion() {
  if (!document.querySelector('#backup-toast-styles')) {
    const style = document.createElement('style');
    style.id = 'backup-toast-styles';
    style.textContent = `
      @keyframes slideIn {
        from {
          transform: translateX(100%);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }
      
      @keyframes slideOut {
        from {
          transform: translateX(0);
          opacity: 1;
        }
        to {
          transform: translateX(100%);
          opacity: 0;
        }
      }
      
      /* Estilos para la lista de backups */
      .backups-list {
        margin-top: 1rem;
      }
      
      .backup-group {
        margin-bottom: 1.5rem;
      }
      
      .backup-group-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: var(--muted, #68707d);
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }
      
      .backup-files-list {
        list-style: none;
        padding: 0;
        margin: 0;
      }
      
      .backup-file-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem;
        border-bottom: 1px solid rgba(20, 22, 26, 0.08);
        gap: 1rem;
        flex-wrap: wrap;
      }
      
      .backup-file-item:hover {
        background: rgba(243, 197, 0, 0.05);
      }
      
      .backup-file-info {
        flex: 1;
        display: flex;
        align-items: center;
        gap: 1rem;
        flex-wrap: wrap;
      }
      
      .backup-filename {
        font-family: monospace;
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--ink, #14161a);
        word-break: break-all;
      }
      
      .backup-filesize {
        font-size: 0.75rem;
        color: var(--muted, #68707d);
        background: rgba(0, 0, 0, 0.05);
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
      }
      
      .backup-date {
        font-size: 0.7rem;
        color: var(--muted, #68707d);
      }
      
      .btn-delete-backup {
        appearance: none;
        border: 1px solid rgba(220, 53, 69, 0.3);
        background: transparent;
        color: #dc3545;
        border-radius: 999px;
        padding: 0.4rem 0.8rem;
        font-size: 0.75rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.15s ease;
      }
      
      .btn-delete-backup:hover {
        background: #dc3545;
        color: white;
        transform: translateY(-1px);
      }
      
      .no-backups {
        text-align: center;
        color: var(--muted, #68707d);
        padding: 2rem;
        font-style: italic;
      }
      
      /* Mejoras para los modales */
      .modal .ui-form__actions {
        margin-top: 1.5rem;
      }
      
      .confirm-text-hint {
        font-size: 0.85rem;
        color: #6c757d;
        margin-top: 0.5rem;
      }
      
      /* Estado de carga para botones */
      .btn-loading {
        opacity: 0.7;
        cursor: not-allowed;
      }
    `;
    document.head.appendChild(style);
  }
}

// ============================================
// 10. CIERRE DE MODALES (Click fuera y ESC)
// ============================================
function setupModalCloseHandlers() {
  // Cerrar al hacer clic fuera del modal
  document.addEventListener('click', (e) => {
    if (e.target.classList && e.target.classList.contains('modal')) {
      const modalId = e.target.getAttribute('id');
      closeModal(modalId);
    }
  });
  
  // Cerrar con tecla ESC
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const modalesAbiertos = document.querySelectorAll('.modal[aria-hidden="false"]');
      modalesAbiertos.forEach(modal => {
        closeModal(modal.getAttribute('id'));
      });
    }
  });
}

// ============================================
// 11. INICIALIZACIÓN PRINCIPAL
// ============================================
document.addEventListener('DOMContentLoaded', () => {
  
  // Agregar estilos de animación
  agregarEstilosAnimacion();
  
  // Configurar manejadores de cierre de modales
  setupModalCloseHandlers();
  
  // Botones de backup (descargar)
  const backupButtons = document.querySelectorAll('.btn-backup');
  backupButtons.forEach(btn => {
    btn.removeEventListener('click', handleBackupClick);
    btn.addEventListener('click', handleBackupClick);
  });
  
  // Botones de restore (subir)
  const restoreButtons = document.querySelectorAll('.btn-restore');
  restoreButtons.forEach(btn => {
    btn.removeEventListener('click', handleRestoreClick);
    btn.addEventListener('click', handleRestoreClick);
  });
  
  // Botón confirmar backup
  const confirmBackupBtn = document.getElementById('btn-confirmar-backup');
  if (confirmBackupBtn) {
    const newBtn = confirmBackupBtn.cloneNode(true);
    confirmBackupBtn.parentNode.replaceChild(newBtn, confirmBackupBtn);
    newBtn.addEventListener('click', () => {
      if (currentDb) {
        realizarBackup(currentDb);
        closeModal('modal-backup');
        currentAction = null;
        currentDb = null;
      }
    });
  }
  
  // Formulario de restauración
  const restoreForm = document.getElementById('form-restore');
  if (restoreForm) {
    // Remover event listeners anteriores
    const newForm = restoreForm.cloneNode(true);
    restoreForm.parentNode.replaceChild(newForm, restoreForm);
    
    newForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const fileInput = newForm.querySelector('input[type="file"]');
      const file = fileInput ? fileInput.files[0] : null;
      
      if (!validarArchivoBackup(file)) {
        return;
      }
      
      // Mostrar indicador de carga
      const submitBtn = newForm.querySelector('button[type="submit"]');
      const originalText = submitBtn ? submitBtn.textContent : 'Subir y restaurar';
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Restaurando...';
      }
      
      try {
        const formData = new FormData(newForm);
        await realizarRestore(formData);
        newForm.reset();
      } catch (error) {
        console.error('Error en restauración:', error);
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = originalText;
        }
      }
    });
  }
  
  // Botones de cierre de modales
  document.querySelectorAll('[data-close-modal]').forEach(btn => {
    btn.removeEventListener('click', (e) => {});
    btn.addEventListener('click', (e) => {
      const modal = btn.closest('.modal');
      if (modal) {
        closeModal(modal.getAttribute('id'));
      }
    });
  });
  
  // Validación en tiempo real del archivo seleccionado
  const fileInputs = document.querySelectorAll('input[type="file"][name="backup_file"]');
  fileInputs.forEach(input => {
    input.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        if (!validarArchivoBackup(file)) {
          e.target.value = '';
        } else {
          Utils.showToast(`Archivo seleccionado: ${file.name} (${Utils.formatBytes(file.size)})`, 'info');
        }
      }
    });
  });
  
  // Cargar lista de backups si existe el contenedor
  if (document.getElementById('lista-backups-container')) {
    cargarListaBackups();
  }
  
  console.log('✅ Gestión de copias de seguridad inicializada correctamente');
});

// ============================================
// 12. EXPORTAR FUNCIONES PARA USO GLOBAL
// ============================================
window.backupApp = {
  openModal,
  closeModal,
  realizarBackup,
  realizarRestore,
  cargarListaBackups,
  Utils
};