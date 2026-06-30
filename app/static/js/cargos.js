// ============================================
// 1. CONSTANTES Y CONFIGURACIÓN
// ============================================
const CONFIG = {
    API: {
        CARGOS: '/api/cargos'
    },
    UI: {
        LOADING_CLASS: 'is-loading',
        DISABLED_CLASS: 'is-disabled',
        TIMEOUT: 30000
    },
    VALIDATION: {
        MIN_NOMBRE: 4,
        MAX_NOMBRE: 30,
        MAX_DESCRIPCION: 250
    }
};

// ============================================
// 2. SISTEMA DE NOTIFICACIONES
// ============================================
const NotificationSystem = {
    show(message, type = 'info') {
        if (!message) return;

        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }

        const notification = document.createElement('div');
        notification.className = `notification notification--${type}`;
        notification.setAttribute('role', 'alert');

        notification.innerHTML = `
            <span class="notification__message">${message}</span>
            <button class="notification__close" aria-label="Cerrar notificación">&times;</button>
        `;

        const closeBtn = notification.querySelector('.notification__close');
        closeBtn.addEventListener('click', () => {
            notification.classList.add('notification--closing');
            setTimeout(() => notification.remove(), 300);
        });

        container.appendChild(notification);

        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.add('notification--closing');
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    },

    success(message) { this.show(message, 'success'); },
    error(message) { this.show(message, 'error'); },
    info(message) { this.show(message, 'info'); },
    warning(message) { this.show(message, 'warning'); }
};

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
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.UI.TIMEOUT);

        try {
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
                signal: controller.signal,
                ...options,
                headers,
            });

            clearTimeout(timeoutId);

            const contentType = response.headers.get("content-type") || "";
            const isJson = contentType.includes("application/json");
            const payload = isJson ? await response.json() : await response.text();

            if (!response.ok) {
                const msg = (isJson && payload && (payload.message || payload.error)) ||
                    String(payload || response.statusText || "Error en la solicitud");
                throw new Error(msg);
            }

            return payload;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('La solicitud ha superado el tiempo de espera');
            }
            throw error;
        }
    },

    escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    },

    normalizeCargo(cargo) {
        return {
            id: cargo?.id ?? cargo?.ID_cargo ?? cargo?.id_cargo ?? "",
            nombre: cargo?.nombre ?? cargo?.Nombre_cargo ?? cargo?.nombre_cargo ?? "",
            descripcion: cargo?.descripcion ?? cargo?.Descripcion_cargo ?? cargo?.descripcion_cargo ?? "",
        };
    },

    debounce(func, wait = 300) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    throttle(func, limit = 1000) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    setLoading(element, isLoading) {
        if (!element) return;
        if (isLoading) {
            element.classList.add(CONFIG.UI.LOADING_CLASS);
            element.disabled = true;
        } else {
            element.classList.remove(CONFIG.UI.LOADING_CLASS);
            element.disabled = false;
        }
    }
};

// ============================================
// 4. MANEJADOR DE MODALES
// ============================================
const ModalManager = {
    open(id) {
        if (window.UiModal && typeof window.UiModal.openById === "function") {
            window.UiModal.openById(id);
            return;
        }

        const modal = document.getElementById(id);
        if (modal) {
            modal.removeAttribute("hidden");
            modal.setAttribute("aria-hidden", "false");
            document.body.classList.add('modal-open');
        }
    },

    close(id) {
        if (window.UiModal && typeof window.UiModal.closeById === "function") {
            window.UiModal.closeById(id);
            return;
        }

        const modal = document.getElementById(id);
        if (modal) {
            modal.setAttribute("hidden", "");
            modal.setAttribute("aria-hidden", "true");
            document.body.classList.remove('modal-open');
        }
    },

    isOpen(id) {
        const modal = document.getElementById(id);
        return modal && !modal.hasAttribute('hidden') && modal.style.display !== 'none';
    }
};

// ============================================
// 5. MANEJADOR DE FORMULARIOS
// ============================================
const FormManager = {
    resetForm(form) {
        if (!form) return;
        form.reset();
        this.clearValidationStates(form);

        if (window.FieldValidator && typeof window.FieldValidator.resetForm === 'function') {
            window.FieldValidator.resetForm(form);
        }
    },

    clearValidationStates(form) {
        if (!form) return;

        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.classList.remove('field-success', 'field-error');
            input.removeAttribute('aria-invalid');

            const errorElement = input.closest('.field-validator-wrapper')?.querySelector('.field-message');
            if (errorElement) {
                errorElement.style.display = 'none';
                errorElement.textContent = '';
            }
        });
    },

    validateForm(form) {
        let isValid = true;
        const requiredInputs = form.querySelectorAll('[required]');

        requiredInputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.classList.add('field-error');
                input.setAttribute('aria-invalid', 'true');
            }
        });

        return isValid;
    }
};

// ============================================
// 6. ICONOS SVG
// ============================================
const Iconos = {
    lapiz: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25Zm18-11.5a1 1 0 0 0 0-1.41l-1.34-1.34a1 1 0 0 0-1.41 0l-1.12 1.12 3.75 3.75L21 5.75Z" fill="currentColor"/></svg>`,
    basura: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 7h12l-1 14H7L6 7Zm3-3h6l1 2H8l1-2Z" fill="currentColor"/></svg>`,
    spinner: `<svg viewBox="0 0 24 24" class="spinner" aria-hidden="true"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" opacity="0.25"/><path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="4" fill="none"/></svg>`
};

// ============================================
// 7. MANEJADORES DE TABLA
// ============================================
const TableManager = {
    renderContador(total) {
        const contador = document.querySelector("[data-count]");
        if (!contador) return;
        contador.setAttribute("data-count", String(total));
        contador.textContent = String(total);
    },

    renderTabla(cargos) {
        const tbody = document.getElementById("tabla-cargos");
        if (!tbody) return;

        if (!cargos || !cargos.length) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="table__empty">No hay cargos para mostrar.</td>
                </tr>
            `;
            this.renderContador(0);
            return;
        }

        tbody.innerHTML = cargos
            .map((raw) => {
                const cargo = Utils.normalizeCargo(raw);
                const id = Utils.escapeHtml(cargo.id);
                const nombre = Utils.escapeHtml(cargo.nombre);
                const descripcion = Utils.escapeHtml(cargo.descripcion || "-");

                return `
                    <tr>
                        <td><span class="chip">${id}</span></td>
                        <td>${nombre}</td>
                        <td>${descripcion}</td>
                        <td class="table__actions">
                            <div class="row-actions" aria-label="Acciones del cargo">
                                <button class="icon-action icon-action--edit" type="button" data-action="editar" 
                                        data-id="${id}" 
                                        data-nombre="${nombre}" 
                                        data-descripcion="${descripcion}" 
                                        aria-label="Modificar">
                                    ${Iconos.lapiz}
                                </button>
                                <button class="icon-action icon-action--danger" type="button" data-action="eliminar" 
                                        data-id="${id}" 
                                        data-nombre="${nombre}" 
                                        aria-label="Eliminar">
                                    ${Iconos.basura}
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            })
            .join("");

        this.renderContador(cargos.length);
    },

    showLoading(tbody) {
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="table__loading">
                        <span class="loading-spinner">${Iconos.spinner}</span>
                        Cargando cargos...
                    </td>
                </tr>
            `;
        }
    },

    showError(tbody, message) {
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="table__error">
                        <span>⚠️ ${message || 'Error al cargar los datos'}</span>
                    </td>
                </tr>
            `;
        }
    }
};

// ============================================
// 8. CRUD DE CARGOS - MÓDULO PRINCIPAL
// ============================================
const CargosModule = {
    cargoPendienteEliminar: null,
    isProcessing: false,

    async cargarCargos() {
        const tbody = document.getElementById("tabla-cargos");
        TableManager.showLoading(tbody);

        try {
            const data = await Utils.fetchJson(CONFIG.API.CARGOS, { method: "GET" });
            const cargos = Array.isArray(data) ? data : (data?.cargos || data?.data || []);
            TableManager.renderTabla(cargos);
        } catch (error) {
            TableManager.showError(tbody, error.message || "No fue posible cargar los cargos.");
            NotificationSystem.error(error.message || "No fue posible cargar los cargos.");
        }
    },

    abrirModalEditar(button) {
        const inputEditarId = document.getElementById("editar-id-cargo");
        const inputEditarNombre = document.getElementById("editar-nombre-cargo");
        const inputEditarDescripcion = document.getElementById("editar-descripcion-cargo");
        const formEditar = document.getElementById("form-editar-cargo");

        const id = button.getAttribute("data-id") || "";
        const nombre = button.getAttribute("data-nombre") || "";
        const descripcion = button.getAttribute("data-descripcion") || "";

        if (inputEditarId) inputEditarId.value = id;
        if (inputEditarNombre) inputEditarNombre.value = nombre;
        if (inputEditarDescripcion) inputEditarDescripcion.value = descripcion === "-" ? "" : descripcion;

        if (formEditar) {
            FormManager.clearValidationStates(formEditar);
        }

        ModalManager.open("modal-editar-cargo");
    },

    abrirModalEliminar(button) {
        const textoEliminar = document.getElementById("texto-confirmar-eliminar-cargo");

        const id = button.getAttribute("data-id") || "";
        const nombre = button.getAttribute("data-nombre") || "";
        this.cargoPendienteEliminar = { id, nombre };

        if (textoEliminar) {
            textoEliminar.textContent = `¿Estás seguro de que quieres eliminar el cargo "${nombre}"?`;
        }

        ModalManager.open("modal-eliminar-cargo");
    },

    async registrarCargo(event) {
        event.preventDefault();

        if (this.isProcessing) return;
        this.isProcessing = true;

        const formCrear = document.getElementById("form-cargo");
        if (!formCrear) {
            this.isProcessing = false;
            return;
        }

        const submitBtn = formCrear.querySelector('[type="submit"]');
        Utils.setLoading(submitBtn, true);

        try {
            if (!FormManager.validateForm(formCrear)) {
                NotificationSystem.warning("Por favor, completa todos los campos requeridos.");
                this.isProcessing = false;
                Utils.setLoading(submitBtn, false);
                return;
            }

            const payload = {
                nombre_cargo: formCrear.nombre_cargo.value.trim(),
                descripcion_cargo: formCrear.descripcion_cargo.value.trim(),
            };

            if (!payload.nombre_cargo) {
                NotificationSystem.warning("El nombre del cargo es requerido.");
                this.isProcessing = false;
                Utils.setLoading(submitBtn, false);
                return;
            }

            const result = await Utils.fetchJson(CONFIG.API.CARGOS, {
                method: "POST",
                body: JSON.stringify(payload),
            });

            if (result.success) {
                NotificationSystem.success(result.message || "Cargo registrado correctamente.");
                FormManager.resetForm(formCrear);
                await this.cargarCargos();
            } else {
                NotificationSystem.error(result.message || "No fue posible registrar el cargo.");
            }
        } catch (error) {
            NotificationSystem.error(error.message || "No fue posible registrar el cargo.");
        } finally {
            this.isProcessing = false;
            Utils.setLoading(submitBtn, false);
        }
    },

    async actualizarCargo(event) {
        event.preventDefault();

        if (this.isProcessing) return;
        this.isProcessing = true;

        const inputEditarId = document.getElementById("editar-id-cargo");
        const inputEditarNombre = document.getElementById("editar-nombre-cargo");
        const inputEditarDescripcion = document.getElementById("editar-descripcion-cargo");
        const formEditar = document.getElementById("form-editar-cargo");
        const submitBtn = formEditar?.querySelector('[type="submit"]');

        Utils.setLoading(submitBtn, true);

        try {
            if (!FormManager.validateForm(formEditar)) {
                NotificationSystem.warning("Por favor, completa todos los campos requeridos.");
                this.isProcessing = false;
                Utils.setLoading(submitBtn, false);
                return;
            }

            const idCargo = inputEditarId?.value.trim() || "";
            const payload = {
                id_cargo: idCargo,
                nombre_cargo: inputEditarNombre?.value.trim() || "",
                descripcion_cargo: inputEditarDescripcion?.value.trim() || "",
            };

            if (!payload.nombre_cargo) {
                NotificationSystem.warning("El nombre del cargo es requerido.");
                this.isProcessing = false;
                Utils.setLoading(submitBtn, false);
                return;
            }

            const result = await Utils.fetchJson(CONFIG.API.CARGOS, {
                method: "PUT",
                body: JSON.stringify(payload),
            });

            if (result.success) {
                NotificationSystem.success(result.message || "Cargo modificado correctamente.");
                ModalManager.close("modal-editar-cargo");
                if (formEditar) {
                    FormManager.resetForm(formEditar);
                }
                await this.cargarCargos();
            } else {
                NotificationSystem.error(result.message || "No fue posible modificar el cargo.");
            }
        } catch (error) {
            NotificationSystem.error(error.message || "No fue posible modificar el cargo.");
        } finally {
            this.isProcessing = false;
            Utils.setLoading(submitBtn, false);
        }
    },

    async eliminarCargo() {
        if (this.isProcessing) return;
        if (!this.cargoPendienteEliminar?.id) {
            NotificationSystem.warning("No hay un cargo seleccionado para eliminar.");
            return;
        }

        this.isProcessing = true;
        const btnConfirmar = document.getElementById("btn-confirmar-eliminar-cargo");
        Utils.setLoading(btnConfirmar, true);

        try {
            const result = await Utils.fetchJson(CONFIG.API.CARGOS, {
                method: "DELETE",
                body: JSON.stringify({ id_cargo: this.cargoPendienteEliminar.id }),
            });

            if (result.success) {
                NotificationSystem.success(result.message || "Cargo eliminado correctamente.");
                this.cargoPendienteEliminar = null;
                ModalManager.close("modal-eliminar-cargo");
                await this.cargarCargos();
            } else {
                NotificationSystem.error(result.message || "No fue posible eliminar el cargo.");
            }
        } catch (error) {
            NotificationSystem.error(error.message || "No fue posible eliminar el cargo.");
        } finally {
            this.isProcessing = false;
            Utils.setLoading(btnConfirmar, false);
        }
    },

    init() {
        const tbody = document.getElementById("tabla-cargos");
        const formCrear = document.getElementById("form-cargo");
        const formEditar = document.getElementById("form-editar-cargo");
        const btnConfirmarEliminar = document.getElementById("btn-confirmar-eliminar-cargo");

        this.registrarCargo = this.registrarCargo.bind(this);
        this.actualizarCargo = this.actualizarCargo.bind(this);
        this.eliminarCargo = this.eliminarCargo.bind(this);
        this.abrirModalEditar = this.abrirModalEditar.bind(this);
        this.abrirModalEliminar = this.abrirModalEliminar.bind(this);

        if (formCrear) {
            formCrear.addEventListener("submit", this.registrarCargo);
        }

        if (formEditar) {
            formEditar.addEventListener("submit", this.actualizarCargo);
        }

        if (tbody) {
            tbody.addEventListener("click", (event) => {
                const button = event.target.closest("button[data-action]");
                if (!button) return;

                const action = button.getAttribute("data-action");
                if (action === "editar") {
                    this.abrirModalEditar(button);
                } else if (action === "eliminar") {
                    this.abrirModalEliminar(button);
                }
            });
        }

        if (btnConfirmarEliminar) {
            btnConfirmarEliminar.addEventListener("click", this.eliminarCargo);
        }

        const modalEditar = document.getElementById("modal-editar-cargo");
        if (modalEditar && formEditar) {
            const observer = new MutationObserver(() => {
                if (modalEditar.hasAttribute('hidden') || modalEditar.style.display === 'none') {
                    if (formEditar && !this.isProcessing) {
                        FormManager.resetForm(formEditar);
                    }
                }
            });

            observer.observe(modalEditar, {
                attributes: true,
                attributeFilter: ['hidden', 'style']
            });

            this._modalObserver = observer;
        }

        this.cargarCargos();
    },

    destroy() {
        if (this._modalObserver) {
            this._modalObserver.disconnect();
            this._modalObserver = null;
        }
    }
};

// ============================================
// 9. INICIALIZACIÓN
// ============================================
document.addEventListener("DOMContentLoaded", () => {
    CargosModule.init();
});

window.CargosModule = CargosModule;