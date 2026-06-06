const tablaUsuarios = document.getElementById("tabla-usuarios");
const tablaRoles = document.getElementById("tabla-roles");
const tablaModulos = document.getElementById("tabla-modulos");

const formUsuario = document.getElementById("form-usuario");
const formRol = document.getElementById("form-rol");
const formModulo = document.getElementById("form-modulo");

const toast = document.getElementById("toast");
const confirmMessage = document.getElementById("confirmacion-mensaje");
const confirmActionBtn = document.getElementById("confirmacion-btn");
const confirmModalId = "modal-confirmacion";

const statUsuarios = document.getElementById("stat-usuarios");
const statRoles = document.getElementById("stat-roles");
const statModulos = document.getElementById("stat-modulos");
const fotoPerfilInput = document.getElementById("foto-perfil-input");
const fotoPerfilButton = document.getElementById("btn-foto-perfil");
const fotoPerfilName = document.getElementById("foto-perfil-name");
const fotoPerfilPreview = document.getElementById("foto-perfil-preview");

const currentUser = window.currentUser || {};
const currentUserId = currentUser?.id == null ? "" : String(currentUser.id);
const currentUserRolId = currentUser?.rolId ? Number(currentUser.rolId) : null;
const currentUserRolNombre = String(currentUser?.rolNombre || "").trim().toLowerCase();
const esAdminActual = currentUserRolId === 1 || currentUserRolNombre === "admin";

const selectUsuarioRol = formUsuario?.querySelector("select[name='rol_id']");
const selectUsuarioCedula = formUsuario?.querySelector("select[name='cedula_personal']");

const tableTabButtons = Array.from(document.querySelectorAll("[data-table-tab]"));
const tableTabPanels = Array.from(document.querySelectorAll("[data-table-panel]"));
let activeTableTabKey = tableTabButtons.find(btn => btn.getAttribute("aria-selected") === "true")?.dataset.tableTab || "usuarios";

const adminModals = {
    usuarios: document.getElementById("modal-admin-usuarios"),
    roles: document.getElementById("modal-admin-roles"),
    modulos: document.getElementById("modal-admin-modulos"),
};

const adminButtons = {
    usuarios: document.getElementById("btn-admin-usuarios"),
    roles: document.getElementById("btn-admin-roles"),
    modulos: document.getElementById("btn-admin-modulos"),
};

let activeAdminKey = null;
let pendingConfirmAction = null;
let currentFotoPreviewUrl = null;

const state = {
    usuarios: [],
    roles: [],
    modulos: [],
    empleados: [],
    clientes: [],
};

const csrfToken = document.querySelector("input[name='_csrf_token']")?.value || "";

// ==================== FUNCIONES DE VALIDACIÓN ====================

function validarFormularioAntesDeEnviar(form, nombreFormulario) {
    if (!window.FieldValidator) {
        console.warn('FieldValidator no disponible');
        return true;
    }
    
    const isValid = window.FieldValidator.validateForm(form);
    
    if (!isValid) {
        mostrarToast(`Por favor, corrige los errores en el formulario de ${nombreFormulario}.`, true);
        
        const primerError = form.querySelector('.field-error');
        if (primerError) {
            primerError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            primerError.focus();
        }
        
        return false;
    }
    
    return true;
}

// ==================== CARGAR OPCIONES DE CÉDULA POR ROL ====================

async function cargarOpcionesCedula(rolId) {
    if (!selectUsuarioCedula) return;
    
    // Buscar el rol seleccionado para saber si es Cliente
    const rolSeleccionado = state.roles.find(r => String(r.id) === String(rolId));
    const esRolCliente = rolSeleccionado && (String(rolSeleccionado.nombre || "").toLowerCase() === "cliente");
    
    selectUsuarioCedula.innerHTML = '<option value="">Cargando...</option>';
    selectUsuarioCedula.disabled = true;
    
    try {
        let data;
        if (esRolCliente) {
            const response = await fetch("/api/usuarios/clientes", {
                headers: {
                    'Accept': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'
            });
            data = await response.json();
            
            if (data.success && data.clientes) {
                const options = ['<option value="">Seleccione un cliente...</option>'];
                data.clientes.forEach(cliente => {
                    const cedula = cliente.cedula;
                    const nombre = cliente.nombre_completo || "";
                    const celular = cliente.celular || "";
                    const label = `${cedula} - ${nombre} ${celular ? `(${celular})` : ''}`.trim();
                    options.push(`<option value="${escapeHtml(String(cedula))}">${escapeHtml(label)}</option>`);
                });
                selectUsuarioCedula.innerHTML = options.join("");
            } else {
                selectUsuarioCedula.innerHTML = '<option value="">No hay clientes disponibles</option>';
            }
        } else {
            const response = await fetch("/api/usuarios/empleados", {
                headers: {
                    'Accept': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'
            });
            data = await response.json();
            
            if (data.success && data.empleados) {
                const options = ['<option value="">Seleccione un empleado...</option>'];
                data.empleados.forEach(empleado => {
                    const cedula = empleado.cedula;
                    const nombre = empleado.nombre_completo || "";
                    options.push(`<option value="${escapeHtml(String(cedula))}">${escapeHtml(`${cedula} - ${nombre}`)}</option>`);
                });
                selectUsuarioCedula.innerHTML = options.join("");
            } else {
                selectUsuarioCedula.innerHTML = '<option value="">No hay empleados disponibles</option>';
            }
        }
    } catch (error) {
        console.error("Error cargando opciones de cédula:", error);
        selectUsuarioCedula.innerHTML = '<option value="">Error al cargar datos</option>';
    } finally {
        selectUsuarioCedula.disabled = false;
    }
}

// ==================== FUNCIONES DE PERMISOS ====================

async function cargarPermisosPorRol(rolId) {
    const container = document.getElementById("permisos-rol-container");
    const grid = document.getElementById("permisos-grid");
    const btnGuardar = document.getElementById("btn-guardar-permisos");
    
    if (!rolId || !container || !grid) return;
    
    const rolSeleccionado = state.roles.find(r => String(r.id) === String(rolId));
    const esRolAdmin = rolSeleccionado && (rolSeleccionado.id === 1 || String(rolSeleccionado.nombre || "").toLowerCase() === "admin");
    
    if (esRolAdmin) {
        grid.innerHTML = `
            <div class="permiso-item disabled">
                <span class="permiso-modulo">⚠️ El rol Administrador tiene todos los permisos del sistema por defecto</span>
            </div>
        `;
        if (btnGuardar) btnGuardar.style.display = "none";
        container.style.display = "block";
        return;
    }
    
    try {
        const response = await fetch(`/api/permisos/rol/${rolId}`, {
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'same-origin'
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || "Error al cargar permisos");
        }
        
        const permisos = data.permisos || [];
        
        if (!permisos.length) {
            grid.innerHTML = '<div class="permiso-item disabled">No hay módulos disponibles para configurar permisos</div>';
            if (btnGuardar) btnGuardar.style.display = "none";
        } else {
            grid.innerHTML = permisos.map(permiso => `
                <div class="permiso-item" data-modulo-id="${permiso.modulo_id}">
                    <span class="permiso-modulo">${escapeHtml(permiso.modulo_nombre || "Módulo")}</span>
                    <div class="permiso-checkboxes">
                        <label>
                            <input type="checkbox" ${permiso.registrar ? 'checked' : ''} data-permiso="registrar">
                            Registrar
                        </label>
                        <label>
                            <input type="checkbox" ${permiso.modificar ? 'checked' : ''} data-permiso="modificar">
                            Modificar
                        </label>
                        <label>
                            <input type="checkbox" ${permiso.eliminar ? 'checked' : ''} data-permiso="eliminar">
                            Eliminar
                        </label>
                    </div>
                </div>
            `).join("");
            if (btnGuardar) btnGuardar.style.display = "flex";
        }
        container.style.display = "block";
    } catch (error) {
        console.error("Error cargando permisos:", error);
        mostrarToast("Error al cargar permisos: " + error.message, true);
        container.style.display = "none";
    }
}

async function guardarPermisosRol(rolId) {
    const rolSeleccionado = state.roles.find(r => String(r.id) === String(rolId));
    const esRolAdmin = rolSeleccionado && (rolSeleccionado.id === 1 || String(rolSeleccionado.nombre || "").toLowerCase() === "admin");
    
    if (esRolAdmin) {
        mostrarToast("No se pueden modificar los permisos del rol Administrador", true);
        return;
    }
    
    const items = document.querySelectorAll(".permiso-item");
    if (!items.length) {
        mostrarToast("No hay permisos para guardar", true);
        return;
    }
    
    const permisos = [];
    items.forEach(item => {
        const moduloId = item.dataset.moduloId;
        if (moduloId) {
            const registrar = item.querySelector('input[data-permiso="registrar"]')?.checked || false;
            const modificar = item.querySelector('input[data-permiso="modificar"]')?.checked || false;
            const eliminar = item.querySelector('input[data-permiso="eliminar"]')?.checked || false;
            
            permisos.push({
                modulo_id: parseInt(moduloId),
                registrar: registrar,
                modificar: modificar,
                eliminar: eliminar
            });
        }
    });
    
    try {
        const response = await fetch(`/api/permisos/rol/${rolId}`, {
            method: "PUT",
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'same-origin',
            body: JSON.stringify({ permisos: permisos })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || "Error al guardar permisos");
        }
        
        mostrarToast("Permisos actualizados correctamente");
    } catch (error) {
        console.error("Error guardando permisos:", error);
        mostrarToast("Error al guardar permisos: " + error.message, true);
    }
}

// ==================== FUNCIONES DE UI ====================

function setupRolChangeListener() {
    if (selectUsuarioRol) {
        selectUsuarioRol.removeEventListener("change", window._rolChangeHandler);
        
        window._rolChangeHandler = async (e) => {
            const rolId = e.target.value;
            const container = document.getElementById("permisos-rol-container");
            
            if (rolId) {
                await cargarOpcionesCedula(rolId);
                await cargarPermisosPorRol(rolId);
            } else {
                if (container) container.style.display = "none";
                if (selectUsuarioCedula) {
                    selectUsuarioCedula.innerHTML = '<option value="">Primero seleccione un rol</option>';
                    selectUsuarioCedula.disabled = true;
                }
            }
        };
        
        selectUsuarioRol.addEventListener("change", window._rolChangeHandler);
    }
}

function setupGuardarPermisosListener() {
    const btnGuardar = document.getElementById("btn-guardar-permisos");
    if (btnGuardar) {
        btnGuardar.removeEventListener("click", window._guardarPermisosHandler);
        
        window._guardarPermisosHandler = () => {
            const rolId = selectUsuarioRol?.value;
            if (rolId) {
                guardarPermisosRol(rolId);
            } else {
                mostrarToast("Seleccione un rol primero", true);
            }
        };
        
        btnGuardar.addEventListener("click", window._guardarPermisosHandler);
    }
}

function setupPasswordToggle() {
    const passwordToggle = document.querySelector("[data-password-toggle]");
    if (passwordToggle) {
        passwordToggle.addEventListener("click", function() {
            const passwordInput = this.closest(".password-field")?.querySelector("input");
            if (passwordInput) {
                const type = passwordInput.type === "password" ? "text" : "password";
                passwordInput.type = type;
                this.textContent = type === "password" ? "Mostrar" : "Ocultar";
            }
        });
    }
}

// ==================== FUNCIONES DE TABLA ====================

function setupTableTabs() {
    tableTabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const key = String(btn.dataset.tableTab || "");
            if (!key) return;
            setActiveTableTab(key);
        });
    });
}

function setActiveTableTab(key) {
    activeTableTabKey = key;

    tableTabButtons.forEach(btn => {
        const isActive = String(btn.dataset.tableTab || "") === key;
        btn.setAttribute("aria-selected", isActive ? "true" : "false");
        btn.classList.toggle("is-active", isActive);
        btn.tabIndex = isActive ? 0 : -1;
    });

    tableTabPanels.forEach(panel => {
        const panelKey = String(panel.dataset.tablePanel || "");
        panel.hidden = panelKey !== key;
    });

    syncAdminButtonsWithTab();
}

function syncAdminButtonsWithTab() {
    Object.keys(adminButtons).forEach(key => {
        const btn = adminButtons[key];
        if (!btn) return;

        const isActive = key === activeTableTabKey;
        btn.setAttribute("aria-pressed", isActive ? "true" : "false");
        if (isActive) {
            btn.classList.remove("btn--ghost");
            btn.classList.add("btn--yellow");
        } else {
            btn.classList.remove("btn--yellow");
            btn.classList.add("btn--ghost");
        }
    });
}

// ==================== FUNCIONES DE MODAL ====================

function setupAdminToggles() {
    Object.keys(adminButtons).forEach(key => {
        const btn = adminButtons[key];
        const modal = adminModals[key];
        if (!btn || !modal) return;

        btn.addEventListener("click", () => {
            if (activeTableTabKey !== key) {
                setActiveTableTab(key);
                return;
            }

            const isOpen = !modal.hidden;
            if (isOpen) {
                closeAdminModal(key);
            } else {
                openAdminModal(key);
            }
        });
    });

    document.querySelectorAll("[data-modal-close]").forEach(el => {
        el.addEventListener("click", () => {
            const key = String(el.dataset.modalClose || "");
            if (!key) return;
            closeAdminModal(key);
        });
    });

    document.addEventListener("keydown", event => {
        if (event.key !== "Escape") return;
        if (!activeAdminKey) return;
        closeAdminModal(activeAdminKey);
    });
}

function openAdminModal(key) {
    Object.keys(adminModals).forEach(otherKey => {
        if (otherKey !== key) closeAdminModal(otherKey);
    });

    const modal = adminModals[key];
    const btn = adminButtons[key];

    if (modal) modal.hidden = false;
    activeAdminKey = key;
    document.body.classList.add("modal-open");

    if (btn) {
        btn.setAttribute("aria-expanded", "true");
    }

    const dialog = modal?.querySelector(".modal__dialog");
    if (dialog && typeof dialog.focus === "function") {
        dialog.focus();
    }
}

function closeAdminModal(key) {
    const modal = adminModals[key];
    const btn = adminButtons[key];
    if (modal) modal.hidden = true;
    if (btn) {
        btn.setAttribute("aria-expanded", "false");
    }

    if (activeAdminKey === key) {
        activeAdminKey = null;
    }

    const anyOpen = Object.keys(adminModals).some(k => adminModals[k] && !adminModals[k].hidden);
    if (!anyOpen) {
        document.body.classList.remove("modal-open");
    }
}

// ==================== CONFIRMACIÓN ====================

function abrirConfirmacion(mensaje, onConfirm) {
    pendingConfirmAction = onConfirm;
    if (confirmMessage) {
        confirmMessage.textContent = mensaje;
    }
    if (window.UiModal && typeof window.UiModal.openById === "function") {
        window.UiModal.openById(confirmModalId);
        return;
    }
    const aceptado = confirm(mensaje);
    if (aceptado) {
        onConfirm();
    }
}

async function onConfirmAction() {
    if (!pendingConfirmAction) return;
    const action = pendingConfirmAction;
    pendingConfirmAction = null;

    if (confirmActionBtn) confirmActionBtn.disabled = true;
    try {
        await action();
    } catch (error) {
        mostrarToast(error.message || "No se pudo completar la accion.", true);
    } finally {
        if (confirmActionBtn) confirmActionBtn.disabled = false;
        if (window.UiModal && typeof window.UiModal.closeById === "function") {
            window.UiModal.closeById(confirmModalId);
        }
    }
}

// ==================== RENDERIZADO ====================

function renderSelects() {
    if (selectUsuarioRol) {
        selectUsuarioRol.innerHTML = renderOptions(state.roles);
        const currentValue = selectUsuarioRol.getAttribute("data-current-value");
        if (currentValue) {
            selectUsuarioRol.value = currentValue;
        }
    }
    if (selectUsuarioCedula) {
        selectUsuarioCedula.innerHTML = '<option value="">Seleccione un rol primero</option>';
        selectUsuarioCedula.disabled = true;
    }
}

function renderOptions(items) {
    const options = ['<option value="">Seleccione...</option>'];
    items.forEach(item => {
        options.push(`<option value="${escapeHtml(String(item.id))}">${escapeHtml(item.nombre || "")}</option>`);
    });
    return options.join("");
}

function renderUsuarios() {
    if (!tablaUsuarios) return;

    if (!state.usuarios.length) {
        tablaUsuarios.innerHTML = emptyRow(5, "No hay usuarios registrados.");
        return;
    }

    tablaUsuarios.innerHTML = state.usuarios.map(usuario => `
        <tr>
            <td class="col-id"><span class="chip">${escapeHtml(String(usuario.id ?? ""))}</span></td>
            <td>${escapeHtml(usuario.nombre || "")}</td>
            <td>${escapeHtml(String(usuario.cedula_personal ?? ""))}</td>
            <td class="col-rol">${escapeHtml(usuario.rol_nombre || "")}</td>
            <td class="table__actions">
                <div class="row-actions">
                    <button class="icon-action" type="button" data-action="edit-usuario" data-id="${escapeHtml(String(usuario.id))}" title="Editar">✎</button>
                    <button class="icon-action icon-action--danger" type="button" data-action="delete-usuario" data-id="${escapeHtml(String(usuario.id))}" title="Eliminar">🗑</button>
                </div>
            </td>
        </tr>
    `).join("");

    bindTableActions(tablaUsuarios, state.usuarios, "usuario");
}

function renderRoles() {
    if (!tablaRoles) return;

    if (!state.roles.length) {
        tablaRoles.innerHTML = emptyRow(3, "No hay roles creados.");
        return;
    }

    tablaRoles.innerHTML = state.roles.map(rol => {
        const nombreRol = String(rol.nombre || "").trim().toLowerCase();
        const esProtegido = nombreRol === "admin" || nombreRol === "cliente" || rol.id === 1;

        return `
            <tr>
                <td>${escapeHtml(rol.nombre || "")}</td>
                <td>${escapeHtml(rol.descripcion || "")}</td>
                <td class="table__actions">
                    <div class="row-actions">
                        <button class="icon-action" type="button" data-action="edit-rol" data-id="${escapeHtml(String(rol.id))}" title="Editar">✎</button>
                        ${!esProtegido ? `<button class="icon-action icon-action--danger" type="button" data-action="delete-rol" data-id="${escapeHtml(String(rol.id))}" title="Eliminar">🗑</button>` : ''}
                    </div>
                </td>
            </tr>
        `;
    }).join("");

    bindTableActions(tablaRoles, state.roles, "rol");
}

function renderModulos() {
    if (!tablaModulos) return;

    if (!state.modulos.length) {
        tablaModulos.innerHTML = emptyRow(3, "No hay módulos creados.");
        return;
    }

    tablaModulos.innerHTML = state.modulos.map(modulo => `
        <tr>
            <td>${escapeHtml(modulo.nombre || "")}</td>
            <td>${escapeHtml(modulo.descripcion || "")}</td>
            <td class="table__actions">
                <div class="row-actions">
                    <button class="icon-action" type="button" data-action="edit-modulo" data-id="${escapeHtml(String(modulo.id))}" title="Editar">✎</button>
                    <button class="icon-action icon-action--danger" type="button" data-action="delete-modulo" data-id="${escapeHtml(String(modulo.id))}" title="Eliminar">🗑</button>
                </div>
            </td>
        </tr>
    `).join("");

    bindTableActions(tablaModulos, state.modulos, "modulo");
}

function renderStats() {
    if (statUsuarios) statUsuarios.textContent = state.usuarios.length;
    if (statRoles) statRoles.textContent = state.roles.length;
    if (statModulos) statModulos.textContent = state.modulos.length;
}

function renderTodo() {
    renderSelects();
    renderUsuarios();
    renderRoles();
    renderModulos();
    renderStats();
}

// ==================== BIND ACTIONS ====================

function bindTableActions(table, items, type) {
    table.querySelectorAll("button[data-action]").forEach(btn => {
        btn.removeEventListener("click", btn._handler);
        
        const handler = async () => {
            const action = btn.dataset.action;
            const id = String(btn.dataset.id || "");
            const item = items.find(entry => String(entry.id) === id);

            if (action === `edit-${type}`) {
                if (type === "usuario") {
                    setActiveTableTab("usuarios");
                    openAdminModal("usuarios");
                    llenarFormularioUsuario(item);
                }
                if (type === "rol") {
                    setActiveTableTab("roles");
                    openAdminModal("roles");
                    llenarFormularioRol(item);
                }
                if (type === "modulo") {
                    setActiveTableTab("modulos");
                    openAdminModal("modulos");
                    llenarFormularioModulo(item);
                }
                return;
            }

            if (action === `delete-${type}`) {
                if (type === "usuario") {
                    if (String(id) === currentUserId) {
                        mostrarToast("No puedes eliminar tu propio usuario.", true);
                        return;
                    }

                    const roleName = String(item?.rol_nombre || "").trim().toLowerCase();
                    if (roleName === "admin" && !esAdminActual) {
                        mostrarToast("Solo otro admin puede eliminar este usuario.", true);
                        return;
                    }
                }

                if (type === "rol") {
                    const nombreRol = String(item?.nombre || "").trim().toLowerCase();
                    if (nombreRol === "admin" || nombreRol === "cliente" || item?.id === 1) {
                        mostrarToast("No se puede eliminar el rol Admin o Cliente.", true);
                        return;
                    }
                }

                const endpoints = {
                    usuario: `/api/usuarios/${id}`,
                    rol: `/api/roles/${id}`,
                    modulo: `/api/modulos/${id}`,
                };
                const labels = {
                    usuario: "usuario",
                    rol: "rol",
                    modulo: "módulo",
                };
                const nombre = item?.nombre ? ` ${item.nombre}` : "";
                const mensaje = `¿Seguro que desea eliminar el ${labels[type]}${nombre}? Esta acción no se puede deshacer.`;

                abrirConfirmacion(mensaje, async () => {
                    await fetchJson(endpoints[type], { method: "DELETE" });
                    mostrarToast("Registro eliminado.");
                    await cargarTodo();
                });
            }
        };
        
        btn._handler = handler;
        btn.addEventListener("click", handler);
    });
}

// ==================== FORMULARIOS ====================

function llenarFormularioUsuario(usuario) {
    if (!formUsuario || !usuario) return;
    
    formUsuario.id.value = usuario.id ?? "";
    formUsuario.nombre.value = usuario.nombre ?? "";
    formUsuario.cedula_personal.value = usuario.cedula_personal ?? "";
    formUsuario.password.required = false;
    formUsuario.password.placeholder = "Dejar vacío para conservar";
    formUsuario.password.value = "";
    formUsuario.rol_id.value = usuario.rol_id ?? "";
    formUsuario.foto_perfil_actual.value = usuario.foto_perfil ?? "";
    
    if (selectUsuarioRol && usuario.rol_id) {
        selectUsuarioRol.setAttribute("data-current-value", usuario.rol_id);
    }
    
    if (usuario.rol_id) {
        cargarOpcionesCedula(usuario.rol_id).then(() => {
            if (selectUsuarioCedula && usuario.cedula_personal) {
                selectUsuarioCedula.value = usuario.cedula_personal;
            }
        });
        cargarPermisosPorRol(usuario.rol_id);
    } else {
        const container = document.getElementById("permisos-rol-container");
        if (container) container.style.display = "none";
        if (selectUsuarioCedula) {
            selectUsuarioCedula.innerHTML = '<option value="">Seleccione un rol primero</option>';
            selectUsuarioCedula.disabled = true;
        }
    }
    
    if (fotoPerfilName) {
        fotoPerfilName.textContent = usuario.foto_perfil ? usuario.foto_perfil.split("/").pop() : "Ningún archivo seleccionado";
    }
    actualizarVistaPreviaFoto(null, usuario.foto_perfil || null);
    if (fotoPerfilInput) {
        fotoPerfilInput.value = "";
    }
}

function llenarFormularioRol(rol) {
    if (!formRol || !rol) return;
    formRol.id.value = rol.id ?? "";
    formRol.nombre.value = rol.nombre ?? "";
    formRol.descripcion.value = rol.descripcion ?? "";
}

function llenarFormularioModulo(modulo) {
    if (!formModulo || !modulo) return;
    formModulo.id.value = modulo.id ?? "";
    formModulo.nombre.value = modulo.nombre ?? "";
    formModulo.descripcion.value = modulo.descripcion ?? "";
}

function limpiarFormulario(form) {
    if (!form) return;
    form.reset();
    
    if (window.FieldValidator) {
        window.FieldValidator.resetForm(form);
    }
    
    if (form === formUsuario) {
        form.password.required = true;
        form.password.placeholder = "Contraseña";
        if (fotoPerfilName) {
            fotoPerfilName.textContent = "Ningún archivo seleccionado";
        }
        actualizarVistaPreviaFoto(null, null);
        if (fotoPerfilInput) {
            fotoPerfilInput.value = "";
        }
        const container = document.getElementById("permisos-rol-container");
        if (container) container.style.display = "none";
        if (selectUsuarioRol) {
            selectUsuarioRol.removeAttribute("data-current-value");
        }
        if (selectUsuarioCedula) {
            selectUsuarioCedula.innerHTML = '<option value="">Seleccione un rol primero</option>';
            selectUsuarioCedula.disabled = true;
        }
    }
    
    const idField = form.querySelector("input[name='id']");
    if (idField) {
        idField.value = "";
    }
}

// ==================== SUBMIT HANDLERS ====================

async function onUsuarioSubmit(event) {
    event.preventDefault();

    if (!validarFormularioAntesDeEnviar(formUsuario, 'usuario')) {
        return;
    }

    const id = formUsuario.id.value;
    const cedulaPersonal = formUsuario.cedula_personal.value;
    
    if (!cedulaPersonal) {
        mostrarToast("Debe seleccionar una cédula válida.", true);
        return;
    }
    
    const formData = new FormData();
    formData.append("nombre", formUsuario.nombre.value.trim());
    formData.append("cedula_personal", String(Number(cedulaPersonal)));
    formData.append("password", formUsuario.password.value.trim());
    formData.append("rol_id", String(Number(formUsuario.rol_id.value)));
    formData.append("foto_perfil_actual", formUsuario.foto_perfil_actual.value || "");

    if (fotoPerfilInput?.files?.[0]) {
        const file = fotoPerfilInput.files[0];
        if (file.size > 2 * 1024 * 1024) {
            mostrarToast("La imagen no puede superar los 2MB.", true);
            return;
        }
        formData.append("foto_perfil", file);
    }

    const method = id ? "PUT" : "POST";
    const url = id ? `/api/usuarios/${id}` : "/api/usuarios";

    try {
        await fetchJson(url, { method, body: formData, isMultipart: true });
        
        limpiarFormulario(formUsuario);
        closeAdminModal("usuarios");
        mostrarToast(id ? "Usuario actualizado." : "Usuario creado.");
        await cargarTodo();
    } catch (error) {
        mostrarToast(error.message || "No se pudo guardar el usuario.", true);
    }
}

async function onRolSubmit(event) {
    event.preventDefault();

    if (!validarFormularioAntesDeEnviar(formRol, 'rol')) {
        return;
    }

    const id = formRol.id.value;
    const payload = {
        nombre: formRol.nombre.value.trim(),
        descripcion: formRol.descripcion.value.trim(),
    };

    const method = id ? "PUT" : "POST";
    const url = id ? `/api/roles/${id}` : "/api/roles";

    try {
        await fetchJson(url, { method, body: JSON.stringify(payload) });
        limpiarFormulario(formRol);
        closeAdminModal("roles");
        mostrarToast(id ? "Rol actualizado." : "Rol creado.");
        await cargarTodo();
    } catch (error) {
        mostrarToast(error.message || "No se pudo guardar el rol.", true);
    }
}

async function onModuloSubmit(event) {
    event.preventDefault();

    if (!validarFormularioAntesDeEnviar(formModulo, 'módulo')) {
        return;
    }

    const id = formModulo.id.value;
    const payload = {
        nombre: formModulo.nombre.value.trim(),
        descripcion: formModulo.descripcion.value.trim(),
    };

    const method = id ? "PUT" : "POST";
    const url = id ? `/api/modulos/${id}` : "/api/modulos";

    try {
        await fetchJson(url, { method, body: JSON.stringify(payload) });
        limpiarFormulario(formModulo);
        closeAdminModal("modulos");
        mostrarToast(id ? "Módulo actualizado." : "Módulo creado.");
        await cargarTodo();
    } catch (error) {
        mostrarToast(error.message || "No se pudo guardar el módulo.", true);
    }
}

// ==================== DATA FETCHING ====================

async function cargarTodo() {
    try {
        const [usuarios, roles, modulos, empleados] = await Promise.all([
            fetchJson("/api/usuarios"),
            fetchJson("/api/roles"),
            fetchJson("/api/modulos"),
            fetchJson("/api/usuarios/empleados"),
        ]);

        state.usuarios = usuarios.usuarios || [];
        state.roles = roles.roles || [];
        state.modulos = modulos.modulos || [];
        state.empleados = empleados.empleados || [];

        renderTodo();
    } catch (error) {
        mostrarToast(error.message || "No se pudieron cargar los datos.", true);
    }
}

async function fetchJson(url, options = {}) {
    const isMultipart = Boolean(options.isMultipart);
    const headers = {
        Accept: "application/json",
        ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
    };

    if (!isMultipart && options.body && !(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }

    const response = await fetch(url, {
        headers,
        credentials: "same-origin",
        method: options.method || "GET",
        body: options.body,
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "No se pudo completar la operación.");
    }

    return data;
}

// ==================== UTILITIES ====================

function mostrarToast(message, isError = false) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.toggle("toast--error", isError);
    toast.classList.add("is-visible");
    window.clearTimeout(mostrarToast._timer);
    mostrarToast._timer = window.setTimeout(() => {
        toast.classList.remove("is-visible");
    }, 2400);
}

function actualizarVistaPreviaFoto(file, fotoExistente = null) {
    if (!fotoPerfilPreview) return;

    if (currentFotoPreviewUrl) {
        URL.revokeObjectURL(currentFotoPreviewUrl);
        currentFotoPreviewUrl = null;
    }

    if (file) {
        currentFotoPreviewUrl = URL.createObjectURL(file);
        fotoPerfilPreview.src = currentFotoPreviewUrl;
        return;
    }

    if (fotoExistente) {
        fotoPerfilPreview.src = fotoExistente;
        return;
    }

    fotoPerfilPreview.src = "/static/img/LOGO.png";
}

function emptyRow(colspan, text) {
    return `<tr><td colspan="${colspan}" class="table__empty">${escapeHtml(text)}</td></tr>`;
}

function escapeHtml(value) {
    if (value === null || value === undefined) return "";
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

// ==================== INITIALIZATION ====================

function iniciar() {
    formUsuario?.addEventListener("submit", onUsuarioSubmit);
    formRol?.addEventListener("submit", onRolSubmit);
    formModulo?.addEventListener("submit", onModuloSubmit);
    confirmActionBtn?.addEventListener("click", onConfirmAction);
    
    fotoPerfilButton?.addEventListener("click", () => fotoPerfilInput?.click());
    fotoPerfilInput?.addEventListener("change", () => {
        if (!fotoPerfilName) return;
        const file = fotoPerfilInput.files?.[0];
        
        if (file && !file.type.startsWith('image/')) {
            mostrarToast("Solo se permiten archivos de imagen.", true);
            fotoPerfilInput.value = "";
            return;
        }
        
        if (file && file.size > 2 * 1024 * 1024) {
            mostrarToast("La imagen no puede superar los 2MB.", true);
            fotoPerfilInput.value = "";
            return;
        }
        
        fotoPerfilName.textContent = file ? file.name : "Ningún archivo seleccionado";
        actualizarVistaPreviaFoto(file || null);
    });

    setupTableTabs();
    setActiveTableTab(activeTableTabKey);
    setupAdminToggles();
    setupRolChangeListener();
    setupGuardarPermisosListener();
    setupPasswordToggle();

    document.querySelectorAll("[data-reset-form]").forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.dataset.resetForm;
            if (target === "usuario") limpiarFormulario(formUsuario);
            if (target === "rol") limpiarFormulario(formRol);
            if (target === "modulo") limpiarFormulario(formModulo);
        });
    });

    Object.keys(adminModals).forEach(key => {
        const modal = adminModals[key];
        if (!modal) return;
        const observer = new MutationObserver(() => {
            if (!modal.hidden && window.FieldValidator) {
                window.FieldValidator.init();
            }
        });
        observer.observe(modal, { attributes: true, attributeFilter: ['hidden'] });
    });

    cargarTodo();
}

iniciar();