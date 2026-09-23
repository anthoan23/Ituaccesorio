// ============================================
// 1. CONSTANTES Y CONFIGURACIÓN
// ============================================
const CONFIG = {
    API: {
        CARGOS: '/api/cargos'
    },
    UI: {
        LOADING_CLASS: 'is-loading',
        TIMEOUT: 30000
    }
};

// ============================================
// 2. VALIDACIÓN ANTI-MANIPULACIÓN DE LA TABLA
// ============================================
const validadorCargos = ValidadorTabla.crear({ tituloEntidad: 'El cargo' });

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
                ...options,
                credentials: "same-origin",
                signal: controller.signal,
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
        if (!form) return false;

        // Usa el validador global si está disponible; el chequeo de campos
        // requeridos actúa como respaldo.
        if (window.FieldValidator && typeof window.FieldValidator.validateForm === 'function') {
            return window.FieldValidator.validateForm(form);
        }

        let isValid = true;
        form.querySelectorAll('[required]').forEach(input => {
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
// 6. MANEJADORES DE TABLA
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
            validadorCargos.registrarFilas(tbody);
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
                    <tr data-id="${id}">
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

        validadorCargos.registrarFilas(tbody);
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
// 7. CRUD DE CARGOS - MÓDULO PRINCIPAL
// ============================================
const CargosModule = {
    cargoPendienteEliminar: null,
    cargoEliminarConfiable: null,
    cargoEditarConfiable: null,
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
            Utils.showMessage(error.message || "No fue posible cargar los cargos.", true);
        }
    },

    abrirModalEditar(button, idConfiable) {
        const inputEditarId = document.getElementById("editar-id-cargo");
        const inputEditarNombre = document.getElementById("editar-nombre-cargo");
        const inputEditarDescripcion = document.getElementById("editar-descripcion-cargo");
        const formEditar = document.getElementById("form-editar-cargo");

        const nombre = button.getAttribute("data-nombre") || "";
        const descripcion = button.getAttribute("data-descripcion") || "";

        if (inputEditarId) inputEditarId.value = idConfiable;
        if (inputEditarNombre) inputEditarNombre.value = nombre;
        if (inputEditarDescripcion) inputEditarDescripcion.value = descripcion === "-" ? "" : descripcion;

        this.cargoEditarConfiable = idConfiable;

        if (formEditar) {
            FormManager.clearValidationStates(formEditar);
        }

        ModalManager.open("modal-editar-cargo");
    },

    abrirModalEliminar(button, idConfiable) {
        const textoEliminar = document.getElementById("texto-confirmar-eliminar-cargo");

        const nombre = button.getAttribute("data-nombre") || "";
        this.cargoPendienteEliminar = { id: idConfiable, nombre };
        this.cargoEliminarConfiable = idConfiable;

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
                Utils.showMessage("Por favor, completa todos los campos requeridos.", true);
                this.isProcessing = false;
                Utils.setLoading(submitBtn, false);
                return;
            }

            const payload = {
                nombre_cargo: formCrear.nombre_cargo.value.trim(),
                descripcion_cargo: formCrear.descripcion_cargo.value.trim(),
            };

            if (!payload.nombre_cargo) {
                Utils.showMessage("El nombre del cargo es requerido.", true);
                this.isProcessing = false;
                Utils.setLoading(submitBtn, false);
                return;
            }

            const result = await Utils.fetchJson(CONFIG.API.CARGOS, {
                method: "POST",
                body: JSON.stringify(payload),
            });

            if (result.success) {
                Utils.showMessage(result.message || "Cargo registrado correctamente.");
                FormManager.resetForm(formCrear);
                await this.cargarCargos();
            } else {
                Utils.showMessage(result.message || "No fue posible registrar el cargo.", true);
            }
        } catch (error) {
            Utils.showMessage(error.message || "No fue posible registrar el cargo.", true);
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
                Utils.showMessage("Por favor, completa todos los campos requeridos.", true);
                this.isProcessing = false;
                Utils.setLoading(submitBtn, false);
                return;
            }

            const idCargo = inputEditarId?.value.trim() || "";

            if (!validadorCargos.validarId(idCargo, 'editar', this.cargoEditarConfiable)) {
                this.isProcessing = false;
                Utils.setLoading(submitBtn, false);
                return;
            }

            const payload = {
                id_cargo: idCargo,
                nombre_cargo: inputEditarNombre?.value.trim() || "",
                descripcion_cargo: inputEditarDescripcion?.value.trim() || "",
            };

            if (!payload.nombre_cargo) {
                Utils.showMessage("El nombre del cargo es requerido.", true);
                this.isProcessing = false;
                Utils.setLoading(submitBtn, false);
                return;
            }

            const result = await Utils.fetchJson(CONFIG.API.CARGOS, {
                method: "PUT",
                body: JSON.stringify(payload),
            });

            if (result.success) {
                Utils.showMessage(result.message || "Cargo modificado correctamente.");
                ModalManager.close("modal-editar-cargo");
                if (formEditar) {
                    FormManager.resetForm(formEditar);
                }
                await this.cargarCargos();
            } else {
                Utils.showMessage(result.message || "No fue posible modificar el cargo.", true);
            }
        } catch (error) {
            Utils.showMessage(error.message || "No fue posible modificar el cargo.", true);
        } finally {
            this.isProcessing = false;
            Utils.setLoading(submitBtn, false);
        }
    },

    async eliminarCargo() {
        if (this.isProcessing) return;
        if (!this.cargoPendienteEliminar?.id) {
            Utils.showMessage("No hay un cargo seleccionado para eliminar.", true);
            return;
        }

        if (!validadorCargos.validarId(this.cargoPendienteEliminar.id, 'eliminar', this.cargoEliminarConfiable)) {
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
                Utils.showMessage(result.message || "Cargo eliminado correctamente.");
                this.cargoPendienteEliminar = null;
                this.cargoEliminarConfiable = null;
                ModalManager.close("modal-eliminar-cargo");
                await this.cargarCargos();
            } else {
                Utils.showMessage(result.message || "No fue posible eliminar el cargo.", true);
            }
        } catch (error) {
            Utils.showMessage(error.message || "No fue posible eliminar el cargo.", true);
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
                    const idConfiable = validadorCargos.validarFila(button, 'editar');
                    if (idConfiable === null) return;
                    this.abrirModalEditar(button, idConfiable);
                } else if (action === "eliminar") {
                    const idConfiable = validadorCargos.validarFila(button, 'eliminar');
                    if (idConfiable === null) return;
                    this.abrirModalEliminar(button, idConfiable);
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
                    this.cargoEditarConfiable = null;
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
// 8. INICIALIZACIÓN
// ============================================
document.addEventListener("DOMContentLoaded", () => {
    CargosModule.init();
});

window.CargosModule = CargosModule;
