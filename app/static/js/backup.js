// ============================================
// 1. CONSTANTES Y CONFIGURACIÓN
// ============================================
const CONFIG = {
    API: {
        BACKUP: '/api/backup',
        DATABASES: '/api/backup/databases'
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

        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: response.statusText }));
            throw new Error(error.message || "Error en la solicitud");
        }

        return response;
    },

    async downloadFile(url, data) {
        const response = await this.fetchJson(url, {
            method: "POST",
            body: JSON.stringify(data)
        });
        
        const blob = await response.blob();
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'backup.sql';
        
        if (contentDisposition) {
            const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (match && match[1]) {
                filename = match[1].replace(/['"]/g, '');
            }
        }
        
        const link = document.createElement('a');
        const url_blob = window.URL.createObjectURL(blob);
        link.href = url_blob;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url_blob);
    },

    showMessage(message, isError = false) {
        // Usar el sistema de notificaciones existente
        if (window.showNotification) {
            window.showNotification(message, isError ? 'error' : 'success');
        } else {
            alert(message);
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
// 4. FUNCIONES PRINCIPALES
// ============================================
let currentRestoreDatabase = null;

async function crearBackup(databaseName) {
    const btn = document.querySelector(`.btn-backup[data-database="${databaseName}"]`);
    const originalText = btn.innerHTML;
    
    try {
        btn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z" fill="currentColor"/></svg> Generando...';
        btn.disabled = true;
        
        await Utils.downloadFile(`${CONFIG.API.BACKUP}`, {
            database_name: databaseName
        });
        
        Utils.showMessage(`Backup de ${databaseName} descargado exitosamente`);
    } catch (error) {
        Utils.showMessage(error.message, true);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

function abrirModalRestaurar(databaseName) {
    currentRestoreDatabase = databaseName;
    const input = document.getElementById("restore_database");
    if (input) {
        input.value = databaseName;
    }
    openModal("modal-restore");
}

async function restaurarBackup(event) {
    event.preventDefault();
    
    const form = document.getElementById("form-restore");
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    try {
        submitBtn.innerHTML = 'Restaurando...';
        submitBtn.disabled = true;
        
        const response = await Utils.fetchJson(`${CONFIG.API.BACKUP}/restore`, {
            method: "POST",
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            Utils.showMessage(result.message);
            closeModal("modal-restore");
            form.reset();
        } else {
            Utils.showMessage(result.message, true);
        }
    } catch (error) {
        Utils.showMessage(error.message, true);
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// ============================================
// 5. EVENTOS E INICIALIZACIÓN
// ============================================
document.addEventListener("DOMContentLoaded", () => {
    // Botones de backup
    document.querySelectorAll(".btn-backup").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const database = btn.getAttribute("data-database");
            if (database) {
                crearBackup(database);
            }
        });
    });
    
    // Botones de restore
    document.querySelectorAll(".btn-restore").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const database = btn.getAttribute("data-database");
            if (database) {
                abrirModalRestaurar(database);
            }
        });
    });
    
    // Formulario de restauración
    const formRestore = document.getElementById("form-restore");
    if (formRestore) {
        formRestore.addEventListener("submit", restaurarBackup);
    }
});