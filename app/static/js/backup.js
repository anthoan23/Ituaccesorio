// app/static/js/backup.js
// ============================================
// 1. CONSTANTES Y CONFIGURACIÓN
// ============================================
const CONFIG = {
    API: {
        BACKUP_LISTAR: '/api/backup/listar',
        BACKUP_CREAR: '/api/backup/crear',
        BACKUP_SUBIR: '/api/backup/subir',
        BACKUP_ELIMINAR: '/api/backup/eliminar',
        BACKUP_RESTAURAR: '/api/backup/restaurar'
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

    escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    },

    formatDate(dateString) {
        if (!dateString) return "-";
        try {
            const date = new Date(dateString);
            return date.toLocaleString('es-ES', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        } catch {
            return dateString;
        }
    },

    showMessage(message, isError = false) {
        // Usar el sistema de notificaciones si existe
        if (window.notify && typeof window.notify === 'function') {
            window.notify(message, isError ? 'error' : 'success');
        } else {
            console.info(message);
        }
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
        modal.setAttribute("hidden", "");
        modal.setAttribute("aria-hidden", "true");
    }
}

// ============================================
// 4. MANEJADORES DE TABLA
// ============================================
function renderContador(total) {
    const contador = document.querySelector("[data-count]");
    if (!contador) return;
    contador.setAttribute("data-count", String(total));
    contador.textContent = String(total);
}

function renderTabla(backups) {
    const tbody = document.getElementById("tabla-backups");
    if (!tbody) return;

    if (!backups || !backups.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="table__empty">No hay respaldos registrados.</td>
            </tr>
        `;
        renderContador(0);
        return;
    }

    const iconos = {
        basura: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 7h12l-1 14H7L6 7Zm3-3h6l1 2H8l1-2Z" fill="currentColor"/></svg>`,
        descargar: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>`,
        restaurar: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9m0 0v6m0-6h-6"/><path d="M3 3v6h6"/></svg>`
    };

    tbody.innerHTML = backups
        .map((backup) => {
            const id = Utils.escapeHtml(backup.id_backup);
            const usuario = Utils.escapeHtml(backup.usuario_nombre || backup.id_usuario || "-");
            const nombre = Utils.escapeHtml(backup.nombre || "Sin nombre");
            const fecha = Utils.formatDate(backup.fecha);
            const estado = Utils.escapeHtml(backup.estado || "desconocido");
            
            let badgeClass = "badge--warning";
            if (estado.toLowerCase() === "completado") {
                badgeClass = "badge--success";
            } else if (estado.toLowerCase() === "fallido" || estado.toLowerCase() === "error") {
                badgeClass = "badge--error";
            }

            return `
                <tr>
                    <td><span class="chip">${id}</span></td>
                    <td>${usuario}</td>
                    <td>${nombre}</td>
                    <td>${fecha}</td>
                    <td><span class="badge ${badgeClass}">${estado}</span></td>
                    <td class="table__actions">
                        <div class="row-actions" aria-label="Acciones del respaldo">
                            <button class="icon-action icon-action--restore" type="button" data-action="restaurar" 
                                    data-id="${id}" 
                                    data-nombre="${nombre}" 
                                    aria-label="Restaurar">
                                ${iconos.restaurar}
                            </button>
                            <button class="icon-action icon-action--download" type="button" data-action="descargar" 
                                    data-id="${id}" 
                                    data-archivo="${Utils.escapeHtml(backup.direccion_bd || '')}" 
                                    aria-label="Descargar">
                                ${iconos.descargar}
                            </button>
                            <button class="icon-action icon-action--danger" type="button" data-action="eliminar" 
                                    data-id="${id}" 
                                    data-nombre="${nombre}" 
                                    aria-label="Eliminar">
                                ${iconos.basura}
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        })
        .join("");

    renderContador(backups.length);
}

// ============================================
// 5. CRUD DE BACKUPS
// ============================================
async function cargarBackups() {
    try {
        const data = await Utils.fetchJson(CONFIG.API.BACKUP_LISTAR, { method: "GET" });
        const backups = Array.isArray(data) ? data : (data?.backups || data?.data || []);
        renderTabla(backups);
    } catch (error) {
        Utils.showMessage(error.message || "No fue posible cargar los respaldos.", true);
    }
}

function abrirModalSeleccionarBD() {
    const options = document.querySelectorAll('.backup-option');
    options.forEach(opt => opt.style.borderColor = 'rgba(243, 197, 0, 0.25)');
    openModal("modal-seleccionar-bd");
}

async function crearBackup(tipoBD) {
    try {
        const result = await Utils.fetchJson(CONFIG.API.BACKUP_CREAR, {
            method: "POST",
            body: JSON.stringify({ tipo_bd: tipoBD }),
        });

        if (result.success) {
            Utils.showMessage(result.message || "Backup creado exitosamente.");
            closeModal("modal-seleccionar-bd");
            await cargarBackups();
        } else {
            Utils.showMessage(result.message || "No fue posible crear el backup.", true);
        }
    } catch (error) {
        Utils.showMessage(error.message || "Error al crear el backup.", true);
    }
}

// ============================================
// 6. ELIMINAR BACKUP
// ============================================
let backupPendienteEliminar = null;

function abrirModalEliminar(button) {
    const textoEliminar = document.getElementById("texto-confirmar-eliminar-backup");
    
    const id = button.getAttribute("data-id") || "";
    const nombre = button.getAttribute("data-nombre") || "";
    backupPendienteEliminar = { id, nombre };

    if (textoEliminar) {
        textoEliminar.textContent = `¿Estás seguro de que quieres eliminar el respaldo "${nombre}"?`;
    }

    openModal("modal-eliminar-backup");
}

async function eliminarBackup() {
    if (!backupPendienteEliminar?.id) return;

    try {
        const result = await Utils.fetchJson(
            `${CONFIG.API.BACKUP_ELIMINAR}/${backupPendienteEliminar.id}`,
            { method: "DELETE" }
        );

        if (result.success) {
            Utils.showMessage(result.message || "Backup eliminado correctamente.");
            backupPendienteEliminar = null;
            closeModal("modal-eliminar-backup");
            await cargarBackups();
        } else {
            Utils.showMessage(result.message || "No fue posible eliminar el backup.", true);
        }
    } catch (error) {
        Utils.showMessage(error.message || "Error al eliminar el backup.", true);
    }
}

// ============================================
// 7. DESCARGAR BACKUP
// ============================================
function descargarBackup(button) {
    const id = button.getAttribute("data-id") || "";
    if (!id) {
        Utils.showMessage("No se encontró el ID del backup.", true);
        return;
    }

    // Guardar el contenido original del botón para restaurarlo después
    const originalText = button.innerHTML;
    button.innerHTML = '⏳ Descargando...';
    button.disabled = true;

    const token = Utils.getAccessToken();
    const csrf = Utils.getCsrfToken();
    
    fetch(`/api/backup/descargar/${id}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'X-CSRFToken': csrf
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.message || 'Error al descargar');
            });
        }
        // Obtener el nombre del archivo de los headers
        const contentDisposition = response.headers.get('content-disposition');
        let filename = `backup_${id}.sql`;
        if (contentDisposition) {
            const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (match && match[1]) {
                filename = match[1].replace(/['"]/g, '');
            }
        }
        return response.blob().then(blob => {
            return { blob, filename };
        });
    })
    .then(({ blob, filename }) => {
        // Crear un enlace de descarga
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        // Liberar la URL después de un tiempo
        setTimeout(() => {
            URL.revokeObjectURL(link.href);
        }, 100);
        
        Utils.showMessage(`Archivo "${filename}" descargado correctamente.`);
    })
    .catch(error => {
        Utils.showMessage(error.message || "Error al descargar el archivo.", true);
    })
    .finally(() => {
        // Restaurar el botón
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

// ============================================
// 8. SUBIR BACKUP
// ============================================
async function subirBackup(event) {
    event.preventDefault();
    const form = document.getElementById("form-subir-backup");
    if (!form) return;

    const formData = new FormData(form);
    
    // Verificar que se haya seleccionado un archivo
    const archivoInput = form.querySelector('input[type="file"]');
    if (!archivoInput || !archivoInput.files || !archivoInput.files[0]) {
        Utils.showMessage("Por favor selecciona un archivo SQL.", true);
        return;
    }

    // Verificar que el archivo tenga extensión .sql
    const archivo = archivoInput.files[0];
    if (!archivo.name.endsWith('.sql')) {
        Utils.showMessage("El archivo debe tener extensión .sql.", true);
        return;
    }

    // Mostrar indicador de carga
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn?.textContent || "Subir Backup";
    if (submitBtn) {
        submitBtn.textContent = "⏳ Subiendo...";
        submitBtn.disabled = true;
    }
    
    try {
        const result = await Utils.fetchJson(CONFIG.API.BACKUP_SUBIR, {
            method: "POST",
            body: formData,
        });

        if (result.success) {
            Utils.showMessage(result.message || "Backup subido exitosamente.");
            closeModal("modal-subir-backup");
            form.reset();
            await cargarBackups();
        } else {
            Utils.showMessage(result.message || "No fue posible subir el backup.", true);
        }
    } catch (error) {
        Utils.showMessage(error.message || "Error al subir el backup.", true);
    } finally {
        // Restaurar el botón
        if (submitBtn) {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }
}

// ============================================
// 9. RESTAURAR BACKUP
// ============================================
let backupPendienteRestaurar = null;

function abrirModalRestaurar(button) {
    const id = button.getAttribute("data-id") || "";
    const nombre = button.getAttribute("data-nombre") || "";
    backupPendienteRestaurar = { id, nombre };
    
    // Actualizar el texto del modal
    const nombreSpan = document.getElementById("restaurar-nombre-backup");
    if (nombreSpan) {
        nombreSpan.textContent = `"${nombre}"`;
    }
    
    const idInput = document.getElementById("restaurar-id-backup");
    if (idInput) {
        idInput.value = id;
    }
    
    // Desmarcar checkbox y deshabilitar botón
    const checkbox = document.getElementById("confirmar-restauracion");
    const btnRestaurar = document.getElementById("btn-confirmar-restaurar-backup");
    if (checkbox) {
        checkbox.checked = false;
    }
    if (btnRestaurar) {
        btnRestaurar.disabled = true;
    }
    
    openModal("modal-restaurar-backup");
}

async function restaurarBackup() {
    if (!backupPendienteRestaurar?.id) return;
    
    const btnRestaurar = document.getElementById("btn-confirmar-restaurar-backup");
    const textoOriginal = btnRestaurar?.textContent || "Sí, restaurar backup";
    
    try {
        // Deshabilitar botón y mostrar estado de carga
        if (btnRestaurar) {
            btnRestaurar.disabled = true;
            btnRestaurar.textContent = "⏳ Restaurando...";
        }
        
        const result = await Utils.fetchJson(
            `${CONFIG.API.BACKUP_RESTAURAR}/${backupPendienteRestaurar.id}`,
            { method: "POST" }
        );

        if (result.success) {
            Utils.showMessage(result.message || "Backup restaurado exitosamente.");
            backupPendienteRestaurar = null;
            closeModal("modal-restaurar-backup");
            await cargarBackups();
        } else {
            Utils.showMessage(result.message || "No fue posible restaurar el backup.", true);
            // Re-habilitar botón
            if (btnRestaurar) {
                btnRestaurar.disabled = false;
                btnRestaurar.textContent = textoOriginal;
            }
        }
    } catch (error) {
        Utils.showMessage(error.message || "Error al restaurar el backup.", true);
        if (btnRestaurar) {
            btnRestaurar.disabled = false;
            btnRestaurar.textContent = textoOriginal;
        }
    }
}

// ============================================
// 10. EVENTOS E INICIALIZACIÓN
// ============================================
document.addEventListener("DOMContentLoaded", () => {
    const tbody = document.getElementById("tabla-backups");
    const btnCrear = document.getElementById("btn-crear-backup");
    const btnSubir = document.getElementById("btn-subir-backup");
    const btnConfirmarEliminar = document.getElementById("btn-confirmar-eliminar-backup");
    const btnConfirmarRestaurar = document.getElementById("btn-confirmar-restaurar-backup");
    const formSubir = document.getElementById("form-subir-backup");
    const checkboxConfirmar = document.getElementById("confirmar-restauracion");

    // Evento: Crear backup - Abrir modal de selección
    if (btnCrear) {
        btnCrear.addEventListener("click", abrirModalSeleccionarBD);
    }

    // Evento: Opciones de base de datos en el modal
    const options = document.querySelectorAll('.backup-option');
    options.forEach(opt => {
        opt.addEventListener("click", () => {
            const tipo = opt.getAttribute("data-tipo");
            if (tipo) {
                crearBackup(tipo);
            }
        });
    });

    // Evento: Subir backup
    if (btnSubir) {
        btnSubir.addEventListener("click", () => {
            // Resetear el formulario al abrir el modal
            const form = document.getElementById("form-subir-backup");
            if (form) {
                form.reset();
            }
            openModal("modal-subir-backup");
        });
    }

    // Evento: Formulario de subida
    if (formSubir) {
        formSubir.addEventListener("submit", subirBackup);
    }

    // Evento: Acciones de la tabla (restaurar, descargar y eliminar)
    if (tbody) {
        tbody.addEventListener("click", (event) => {
            const button = event.target.closest("button[data-action]");
            if (!button) return;

            const action = button.getAttribute("data-action");
            if (action === "eliminar") {
                abrirModalEliminar(button);
            } else if (action === "descargar") {
                descargarBackup(button);
            } else if (action === "restaurar") {
                abrirModalRestaurar(button);
            }
        });
    }

    // Evento: Confirmar eliminar
    if (btnConfirmarEliminar) {
        btnConfirmarEliminar.addEventListener("click", eliminarBackup);
    }

    // Evento: Confirmar restaurar
    if (btnConfirmarRestaurar) {
        btnConfirmarRestaurar.addEventListener("click", restaurarBackup);
    }

    // Evento: Checkbox de confirmación para restaurar
    if (checkboxConfirmar && btnConfirmarRestaurar) {
        checkboxConfirmar.addEventListener("change", () => {
            btnConfirmarRestaurar.disabled = !checkboxConfirmar.checked;
        });
    }

    // Cargar datos iniciales
    cargarBackups().catch((error) => {
        Utils.showMessage(error.message || "No fue posible cargar los respaldos.", true);
    });
});