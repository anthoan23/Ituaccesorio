// ============================================
// 1. CONSTANTES Y CONFIGURACIÓN
// ============================================
const CONFIG = {
    API: {
        CARGOS: '/api/cargos'
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
        console.info(message);
    },

    normalizeCargo(cargo) {
        return {
            id: cargo?.id ?? cargo?.ID_cargo ?? cargo?.id_cargo ?? "",
            nombre: cargo?.nombre ?? cargo?.Nombre_cargo ?? cargo?.nombre_cargo ?? "",
            descripcion: cargo?.descripcion ?? cargo?.Descripcion_cargo ?? cargo?.descripcion_cargo ?? "",
        };
    }
};

// ============================================
// 2.5 FUNCIÓN PARA LIMPIAR FORMULARIOS
// ============================================
function resetFormFields(form) {
    if (!form) return;
    
    // Resetear valores del formulario
    form.reset();
    
    // Limpiar estados de validación usando el validador global
    if (window.FieldValidator && typeof window.FieldValidator.resetForm === 'function') {
        window.FieldValidator.resetForm(form);
    } else {
        // Fallback: limpiar manualmente
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.classList.remove('field-success', 'field-error');
            input.removeAttribute('aria-invalid');
            
            // Limpiar mensajes de error
            const errorElement = input.closest('.field-validator-wrapper')?.querySelector('.field-message');
            if (errorElement) {
                errorElement.style.display = 'none';
                errorElement.textContent = '';
            }
        });
    }
}

// Iconos SVG (igual que en especialidades)
const Iconos = {
    lapiz: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25Zm18-11.5a1 1 0 0 0 0-1.41l-1.34-1.34a1 1 0 0 0-1.41 0l-1.12 1.12 3.75 3.75L21 5.75Z" fill="currentColor"/></svg>`,
    basura: `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 7h12l-1 14H7L6 7Zm3-3h6l1 2H8l1-2Z" fill="currentColor"/></svg>`
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

function renderTabla(cargos) {
    const tbody = document.getElementById("tabla-cargos");
    if (!tbody) return;

    if (!cargos.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="table__empty">No hay cargos para mostrar.</td>
            </tr>
        `;
        renderContador(0);
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

    renderContador(cargos.length);
}

// ============================================
// 5. CRUD DE CARGOS
// ============================================
async function cargarCargos() {
    const data = await Utils.fetchJson(CONFIG.API.CARGOS, { method: "GET" });
    const cargos = Array.isArray(data) ? data : (data?.cargos || data?.data || []);
    renderTabla(cargos);
}

function abrirModalEditar(button) {
    const inputEditarId = document.getElementById("editar-id-cargo");
    const inputEditarNombre = document.getElementById("editar-nombre-cargo");
    const inputEditarDescripcion = document.getElementById("editar-descripcion-cargo");

    const id = button.getAttribute("data-id") || "";
    const nombre = button.getAttribute("data-nombre") || "";
    const descripcion = button.getAttribute("data-descripcion") || "";

    // PRIMERO: Cargar los datos
    if (inputEditarId) inputEditarId.value = id;
    if (inputEditarNombre) inputEditarNombre.value = nombre;
    if (inputEditarDescripcion) inputEditarDescripcion.value = descripcion === "-" ? "" : descripcion;
    
    // DESPUÉS: Limpiar estados de validación (sin borrar los valores)
    const formEditar = document.getElementById("form-editar-cargo");
    if (formEditar) {
        // Solo limpiar clases y estados, NO resetear valores
        const inputs = formEditar.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.classList.remove('field-success', 'field-error');
            input.removeAttribute('aria-invalid');
            
            // Limpiar mensajes de error
            const errorElement = input.closest('.field-validator-wrapper')?.querySelector('.field-message');
            if (errorElement) {
                errorElement.style.display = 'none';
                errorElement.textContent = '';
            }
        });
        
        // Si existe el validador global, usarlo solo para limpiar clases
        if (window.FieldValidator && typeof window.FieldValidator.resetForm === 'function') {
            // Guardar los valores actuales
            const values = {};
            inputs.forEach(input => {
                values[input.name || input.id] = input.value;
            });
            
            window.FieldValidator.resetForm(formEditar);
            
            // Restaurar los valores
            inputs.forEach(input => {
                const key = input.name || input.id;
                if (values[key] !== undefined) {
                    input.value = values[key];
                }
            });
        }
    }
    
    openModal("modal-editar-cargo");
}

let cargoPendienteEliminar = null;

function abrirModalEliminar(button) {
    const textoEliminar = document.getElementById("texto-confirmar-eliminar-cargo");
    
    const id = button.getAttribute("data-id") || "";
    const nombre = button.getAttribute("data-nombre") || "";
    cargoPendienteEliminar = { id, nombre };

    if (textoEliminar) {
        textoEliminar.textContent = `¿Estás seguro de que quieres eliminar el cargo "${nombre}"?`;
    }

    openModal("modal-eliminar-cargo");
}

async function registrarCargo(event) {
    event.preventDefault();
    const formCrear = document.getElementById("form-cargo");
    if (!formCrear) return;

    const payload = {
        nombre_cargo: formCrear.nombre_cargo.value.trim(),
        descripcion_cargo: formCrear.descripcion_cargo.value.trim(),
    };

    if (!payload.nombre_cargo) {
        Utils.showMessage("El nombre del cargo es requerido.", true);
        return;
    }

    try {
        const result = await Utils.fetchJson(CONFIG.API.CARGOS, {
            method: "POST",
            body: JSON.stringify(payload),
        });
        
        if (result.success) {
            Utils.showMessage(result.message || "Cargo registrado correctamente.");
            
            // Limpiar el formulario y sus estados de validación
            resetFormFields(formCrear);
            
            // Recargar la tabla
            await cargarCargos();
        } else {
            Utils.showMessage(result.message || "No fue posible registrar el cargo.", true);
        }
    } catch (error) {
        Utils.showMessage(error.message || "No fue posible registrar el cargo.", true);
    }
}

async function actualizarCargo(event) {
    event.preventDefault();
    
    const inputEditarId = document.getElementById("editar-id-cargo");
    const inputEditarNombre = document.getElementById("editar-nombre-cargo");
    const inputEditarDescripcion = document.getElementById("editar-descripcion-cargo");
    const formEditar = document.getElementById("form-editar-cargo");

    const idCargo = inputEditarId?.value.trim() || "";
    const payload = {
        id_cargo: idCargo,
        nombre_cargo: inputEditarNombre?.value.trim() || "",
        descripcion_cargo: inputEditarDescripcion?.value.trim() || "",
    };

    if (!payload.nombre_cargo) {
        Utils.showMessage("El nombre del cargo es requerido.", true);
        return;
    }

    try {
        const result = await Utils.fetchJson(CONFIG.API.CARGOS, {
            method: "PUT",
            body: JSON.stringify(payload),
        });
        
        if (result.success) {
            Utils.showMessage(result.message || "Cargo modificado correctamente.");
            
            // Cerrar el modal
            closeModal("modal-editar-cargo");
            
            // Limpiar el formulario de edición después de cerrar
            if (formEditar) {
                resetFormFields(formEditar);
            }
            
            // Recargar la tabla
            await cargarCargos();
        } else {
            Utils.showMessage(result.message || "No fue posible modificar el cargo.", true);
        }
    } catch (error) {
        Utils.showMessage(error.message || "No fue posible modificar el cargo.", true);
    }
}

async function eliminarCargo() {
    if (!cargoPendienteEliminar?.id) return;

    try {
        const result = await Utils.fetchJson(CONFIG.API.CARGOS, {
            method: "DELETE",
            body: JSON.stringify({ id_cargo: cargoPendienteEliminar.id }),
        });
        
        if (result.success) {
            Utils.showMessage(result.message || "Cargo eliminado correctamente.");
            cargoPendienteEliminar = null;
            closeModal("modal-eliminar-cargo");
            await cargarCargos();
        } else {
            Utils.showMessage(result.message || "No fue posible eliminar el cargo.", true);
        }
    } catch (error) {
        Utils.showMessage(error.message || "No fue posible eliminar el cargo.", true);
    }
}

// ============================================
// 6. EVENTOS E INICIALIZACIÓN
// ============================================
document.addEventListener("DOMContentLoaded", () => {
    // Elementos DOM
    const tbody = document.getElementById("tabla-cargos");
    const formCrear = document.getElementById("form-cargo");
    const formEditar = document.getElementById("form-editar-cargo");
    const btnConfirmarEliminar = document.getElementById("btn-confirmar-eliminar-cargo");

    // Evento del formulario de creación
    if (formCrear) {
        formCrear.addEventListener("submit", registrarCargo);
    }

    // Evento del formulario de edición
    if (formEditar) {
        formEditar.addEventListener("submit", actualizarCargo);
    }

    // Evento de la tabla (para editar y eliminar)
    if (tbody) {
        tbody.addEventListener("click", (event) => {
            const button = event.target.closest("button[data-action]");
            if (!button) return;

            const action = button.getAttribute("data-action");
            if (action === "editar") {
                abrirModalEditar(button);
            } else if (action === "eliminar") {
                abrirModalEliminar(button);
            }
        });
    }

    // Evento del botón confirmar eliminar
    if (btnConfirmarEliminar) {
        btnConfirmarEliminar.addEventListener("click", eliminarCargo);
    }

    // Evento para limpiar el formulario de edición cuando se cierra el modal
    const modalEditar = document.getElementById("modal-editar-cargo");
    if (modalEditar) {
        // Escuchar cuando el modal se cierra
        const observer = new MutationObserver(() => {
            if (modalEditar.hasAttribute('hidden') || modalEditar.style.display === 'none') {
                if (formEditar) {
                    resetFormFields(formEditar);
                }
            }
        });
        
        observer.observe(modalEditar, {
            attributes: true,
            attributeFilter: ['hidden', 'style']
        });
    }

    // Cargar datos iniciales
    cargarCargos().catch((error) => {
        Utils.showMessage(error.message || "No fue posible cargar los cargos.", true);
    });
});