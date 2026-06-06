// ============================================
// 1. CONSTANTES Y CONFIGURACIÓN
// ============================================
const CONFIG = {
    API: {
        ESPECIALIDADES: '/api/especialidades'
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
        if (isError) {
            alert(message);
            return;
        }
        console.info(message);
    },

    normalizeEspecialidad(especialidad) {
        return {
            id: especialidad?.id ?? especialidad?.ID_especialidad ?? especialidad?.id_especialidad ?? "",
            nombre: especialidad?.nombre ?? especialidad?.Nombre_especialidad ?? especialidad?.nombre_especialidad ?? "",
            descripcion: especialidad?.descripcion ?? especialidad?.Descripcion_especialidad ?? especialidad?.descripcion_especialidad ?? "",
        };
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

function renderTabla(especialidades) {
    const tbody = document.getElementById("tabla-especialidades");
    if (!tbody) return;

    if (!especialidades.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4">No hay especialidades para mostrar.</td>
            </tr>
        `;
        renderContador(0);
        return;
    }

    tbody.innerHTML = especialidades
        .map((raw) => {
            const especialidad = Utils.normalizeEspecialidad(raw);
            const id = Utils.escapeHtml(especialidad.id);
            const nombre = Utils.escapeHtml(especialidad.nombre);
            const descripcion = Utils.escapeHtml(especialidad.descripcion || "-");

            return `
                <tr>
                    <td>${id}</td>
                    <td>${nombre}</td>
                    <td>${descripcion}</td>
                    <td class="table__actions">
                        <div class="row-actions" aria-label="Acciones de la especialidad">
                            <button type="button" class="table-action table-action--accent" 
                                    data-action="editar" 
                                    data-id="${id}" 
                                    data-nombre="${nombre}" 
                                    data-descripcion="${descripcion}">
                                Modificar
                            </button>
                            <button type="button" class="table-action" 
                                    data-action="eliminar" 
                                    data-id="${id}" 
                                    data-nombre="${nombre}">
                                Eliminar
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        })
        .join("");

    renderContador(especialidades.length);
}

// ============================================
// 5. CRUD DE ESPECIALIDADES
// ============================================
async function cargarEspecialidades() {
    const data = await Utils.fetchJson(CONFIG.API.ESPECIALIDADES, { method: "GET" });
    const especialidades = Array.isArray(data) ? data : (data?.especialidades || data?.data || []);
    renderTabla(especialidades);
}

function abrirModalEditar(button) {
    const inputEditarId = document.getElementById("editar-id-especialidad");
    const inputEditarNombre = document.getElementById("editar-nombre-especialidad");
    const inputEditarDescripcion = document.getElementById("editar-descripcion-especialidad");

    const id = button.getAttribute("data-id") || "";
    const nombre = button.getAttribute("data-nombre") || "";
    const descripcion = button.getAttribute("data-descripcion") || "";

    if (inputEditarId) inputEditarId.value = id;
    if (inputEditarNombre) inputEditarNombre.value = nombre;
    if (inputEditarDescripcion) inputEditarDescripcion.value = descripcion === "-" ? "" : descripcion;
    
    openModal("modal-editar-especialidad");
}

let especialidadPendienteEliminar = null;

function abrirModalEliminar(button) {
    const textoEliminar = document.getElementById("texto-confirmar-eliminar-especialidad");
    
    const id = button.getAttribute("data-id") || "";
    const nombre = button.getAttribute("data-nombre") || "";
    especialidadPendienteEliminar = { id, nombre };

    if (textoEliminar) {
        textoEliminar.textContent = `¿Estás seguro de que quieres eliminar la especialidad "${nombre}"?`;
    }

    openModal("modal-eliminar-especialidad");
}

async function registrarEspecialidad(event) {
    event.preventDefault();
    const formCrear = document.getElementById("form-especialidad");
    if (!formCrear) return;

    const payload = {
        nombre_especialidad: formCrear.nombre_especialidad.value.trim(),
        descripcion_especialidad: formCrear.descripcion_especialidad.value.trim(),
    };

    if (!payload.nombre_especialidad) {
        Utils.showMessage("El nombre de la especialidad es requerido.", true);
        return;
    }

    try {
        const result = await Utils.fetchJson(CONFIG.API.ESPECIALIDADES, {
            method: "POST",
            body: JSON.stringify(payload),
        });
        
        if (result.success) {
            Utils.showMessage(result.message || "Especialidad registrada correctamente.");
            formCrear.reset();
            await cargarEspecialidades();
        } else {
            Utils.showMessage(result.message || "No fue posible registrar la especialidad.", true);
        }
    } catch (error) {
        Utils.showMessage(error.message || "No fue posible registrar la especialidad.", true);
    }
}

async function actualizarEspecialidad(event) {
    event.preventDefault();
    
    const inputEditarId = document.getElementById("editar-id-especialidad");
    const inputEditarNombre = document.getElementById("editar-nombre-especialidad");
    const inputEditarDescripcion = document.getElementById("editar-descripcion-especialidad");

    const idEspecialidad = inputEditarId?.value.trim() || "";
    const payload = {
        id_especialidad: idEspecialidad,
        nombre_especialidad: inputEditarNombre?.value.trim() || "",
        descripcion_especialidad: inputEditarDescripcion?.value.trim() || "",
    };

    if (!payload.nombre_especialidad) {
        Utils.showMessage("El nombre de la especialidad es requerido.", true);
        return;
    }

    try {
        const result = await Utils.fetchJson(CONFIG.API.ESPECIALIDADES, {
            method: "PUT",
            body: JSON.stringify(payload),
        });
        
        if (result.success) {
            Utils.showMessage(result.message || "Especialidad modificada correctamente.");
            closeModal("modal-editar-especialidad");
            await cargarEspecialidades();
        } else {
            Utils.showMessage(result.message || "No fue posible modificar la especialidad.", true);
        }
    } catch (error) {
        Utils.showMessage(error.message || "No fue posible modificar la especialidad.", true);
    }
}

async function eliminarEspecialidad() {
    if (!especialidadPendienteEliminar?.id) return;

    try {
        const result = await Utils.fetchJson(CONFIG.API.ESPECIALIDADES, {
            method: "DELETE",
            body: JSON.stringify({ id_especialidad: especialidadPendienteEliminar.id }),
        });
        
        if (result.success) {
            Utils.showMessage(result.message || "Especialidad eliminada correctamente.");
            especialidadPendienteEliminar = null;
            closeModal("modal-eliminar-especialidad");
            await cargarEspecialidades();
        } else {
            Utils.showMessage(result.message || "No fue posible eliminar la especialidad.", true);
        }
    } catch (error) {
        Utils.showMessage(error.message || "No fue posible eliminar la especialidad.", true);
    }
}

// ============================================
// 6. EVENTOS E INICIALIZACIÓN
// ============================================
document.addEventListener("DOMContentLoaded", () => {
    // Elementos DOM
    const tbody = document.getElementById("tabla-especialidades");
    const formCrear = document.getElementById("form-especialidad");
    const formEditar = document.getElementById("form-editar-especialidad");
    const btnActualizar = document.getElementById("btn-actualizar-especialidades");
    const btnConfirmarEliminar = document.getElementById("btn-confirmar-eliminar-especialidad");

    // Evento del formulario de creación
    if (formCrear) {
        formCrear.addEventListener("submit", registrarEspecialidad);
    }

    // Evento del formulario de edición
    if (formEditar) {
        formEditar.addEventListener("submit", actualizarEspecialidad);
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
        btnConfirmarEliminar.addEventListener("click", eliminarEspecialidad);
    }

    // Evento del botón actualizar
    if (btnActualizar) {
        btnActualizar.addEventListener("click", () => {
            cargarEspecialidades().catch((error) => {
                Utils.showMessage(error.message || "No fue posible actualizar las especialidades.", true);
            });
        });
    }

    // Cargar datos iniciales
    cargarEspecialidades().catch((error) => {
        Utils.showMessage(error.message || "No fue posible cargar las especialidades.", true);
    });
});