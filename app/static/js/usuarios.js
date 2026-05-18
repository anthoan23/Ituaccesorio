const tablaUsuarios = document.getElementById("tabla-usuarios");
const tablaRoles = document.getElementById("tabla-roles");
const tablaModulos = document.getElementById("tabla-modulos");
const tablaPermisos = document.getElementById("tabla-permisos");

const formUsuario = document.getElementById("form-usuario");
const formRol = document.getElementById("form-rol");
const formModulo = document.getElementById("form-modulo");
const formPermiso = document.getElementById("form-permiso");

const toast = document.getElementById("toast");
const confirmMessage = document.getElementById("confirmacion-mensaje");
const confirmActionBtn = document.getElementById("confirmacion-btn");
const confirmModalId = "modal-confirmacion";

const statUsuarios = document.getElementById("stat-usuarios");
const statRoles = document.getElementById("stat-roles");
const statModulos = document.getElementById("stat-modulos");
const statPermisos = document.getElementById("stat-permisos");
const fotoPerfilInput = document.getElementById("foto-perfil-input");
const fotoPerfilButton = document.getElementById("btn-foto-perfil");
const fotoPerfilName = document.getElementById("foto-perfil-name");
const fotoPerfilPreview = document.getElementById("foto-perfil-preview");

const currentUser = window.currentUser || {};
const currentUserId = currentUser?.id == null ? "" : String(currentUser.id);
const currentUserRole = String(currentUser?.rolNombre || "").trim().toLowerCase();

const selectUsuarioRol = formUsuario?.querySelector("select[name='rol_id']");
const selectUsuarioCedula = formUsuario?.querySelector("select[name='cedula_personal']");
const selectPermisoRol = formPermiso?.querySelector("select[name='rol_id']");
const selectPermisoModulo = formPermiso?.querySelector("select[name='modulo_id']");

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
    permisos: [],
    empleados: [],
};

const csrfToken = document.querySelector("input[name='_csrf_token']")?.value || "";

iniciar();

function iniciar() {
    formUsuario?.addEventListener("submit", onUsuarioSubmit);
    formRol?.addEventListener("submit", onRolSubmit);
    formModulo?.addEventListener("submit", onModuloSubmit);
    formPermiso?.addEventListener("submit", onPermisoSubmit);
    confirmActionBtn?.addEventListener("click", onConfirmAction);
    fotoPerfilButton?.addEventListener("click", () => fotoPerfilInput?.click());
    fotoPerfilInput?.addEventListener("change", () => {
        if (!fotoPerfilName) return;
        const file = fotoPerfilInput.files?.[0];
        fotoPerfilName.textContent = file ? file.name : "Ningun archivo seleccionado";
        actualizarVistaPreviaFoto(file || null);
    });

    setupTableTabs();
    setActiveTableTab(activeTableTabKey);

    setupAdminToggles();

    document.querySelectorAll("[data-reset-form]").forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.dataset.resetForm;
            if (target === "usuario") {
                limpiarFormulario(formUsuario);
            }
            if (target === "rol") {
                limpiarFormulario(formRol);
            }
            if (target === "modulo") {
                limpiarFormulario(formModulo);
            }
            if (target === "permiso") {
                limpiarFormulario(formPermiso);
            }
        });
    });

    cargarTodo();
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
        if (isActive) {
            btn.tabIndex = 0;
        } else {
            btn.tabIndex = -1;
        }
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
        btn.classList.toggle("btn--primary", isActive);
        btn.classList.toggle("btn--ghost", !isActive);
    });
}

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

async function cargarTodo() {
    try {
        const [usuarios, roles, modulos, permisos, empleados] = await Promise.all([
            fetchJson("/api/usuarios"),
            fetchJson("/api/roles"),
            fetchJson("/api/modulos"),
            fetchJson("/api/permisos"),
            fetchJson("/api/usuarios/empleados"),
        ]);

        state.usuarios = usuarios.usuarios || [];
        state.roles = roles.roles || [];
        state.modulos = modulos.modulos || [];
        state.permisos = permisos.permisos || [];
        state.empleados = empleados.empleados || [];

        renderTodo();
    } catch (error) {
        mostrarToast(error.message || "No se pudieron cargar los datos.", true);
    }
}

function renderTodo() {
    renderSelects();
    renderUsuarios();
    renderRoles();
    renderModulos();
    renderPermisos();
    renderStats();
}

function renderStats() {
    if (statUsuarios) statUsuarios.textContent = state.usuarios.length;
    if (statRoles) statRoles.textContent = state.roles.length;
    if (statModulos) statModulos.textContent = state.modulos.length;
    if (statPermisos) statPermisos.textContent = state.permisos.length;
}

function renderSelects() {
    if (selectUsuarioRol) {
        selectUsuarioRol.innerHTML = renderOptions(state.roles);
    }
    if (selectUsuarioCedula) {
        selectUsuarioCedula.innerHTML = renderEmpleadoOptions(state.empleados);
    }
    if (selectPermisoRol) {
        selectPermisoRol.innerHTML = renderOptions(state.roles);
    }
    if (selectPermisoModulo) {
        selectPermisoModulo.innerHTML = renderOptions(state.modulos);
    }
}

function renderOptions(items) {
    const options = ['<option value="">Seleccione...</option>'];
    items.forEach(item => {
        options.push(`<option value="${escapeHtml(String(item.id))}">${escapeHtml(item.nombre || "")}</option>`);
    });
    return options.join("");
}

function renderEmpleadoOptions(items) {
    const options = ['<option value="">Seleccione...</option>'];
    items.forEach(item => {
        const cedula = item.cedula ?? "";
        const nombre = item.nombre_completo || [item.nombre, item.apellido].filter(Boolean).join(" ");
        const label = `${cedula} - ${nombre}`.trim();
        options.push(`<option value="${escapeHtml(String(cedula))}">${escapeHtml(label)}</option>`);
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
            <td>${escapeHtml(String(usuario.id ?? ""))}</td>
            <td>${escapeHtml(usuario.nombre || "")}</td>
            <td>${escapeHtml(String(usuario.cedula_personal ?? ""))}</td>
            <td>${escapeHtml(usuario.rol_nombre || "")}</td>
            <td class="table__actions">
                <div class="row-actions">
                    <button class="icon-action" type="button" data-action="edit-usuario" data-id="${escapeHtml(String(usuario.id))}">Editar</button>
                    <button class="icon-action icon-action--danger" type="button" data-action="delete-usuario" data-id="${escapeHtml(String(usuario.id))}">Eliminar</button>
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
        const esProtegido = nombreRol === "admin" || nombreRol === "cliente";
        const proteccionMensaje = esProtegido ? "No se puede eliminar este rol." : "";

        return `
        <tr>
            <td>${escapeHtml(rol.nombre || "")}</td>
            <td>${escapeHtml(rol.descripcion || "")}</td>
            <td class="table__actions">
                <div class="row-actions">
                    <button class="icon-action" type="button" data-action="edit-rol" data-id="${escapeHtml(String(rol.id))}">Editar</button>
                    <button class="icon-action icon-action--danger" type="button" data-action="delete-rol" data-id="${escapeHtml(String(rol.id))}" data-protected="${esProtegido ? "1" : "0"}" data-protected-message="${escapeHtml(proteccionMensaje)}">Eliminar</button>
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
        tablaModulos.innerHTML = emptyRow(3, "No hay modulos creados.");
        return;
    }

    tablaModulos.innerHTML = state.modulos.map(modulo => `
        <tr>
            <td>${escapeHtml(modulo.nombre || "")}</td>
            <td>${escapeHtml(modulo.descripcion || "")}</td>
            <td class="table__actions">
                <div class="row-actions">
                    <button class="icon-action" type="button" data-action="edit-modulo" data-id="${escapeHtml(String(modulo.id))}">Editar</button>
                    <button class="icon-action icon-action--danger" type="button" data-action="delete-modulo" data-id="${escapeHtml(String(modulo.id))}">Eliminar</button>
                </div>
            </td>
        </tr>
    `).join("");

    bindTableActions(tablaModulos, state.modulos, "modulo");
}

function renderPermisos() {
    if (!tablaPermisos) return;

    if (!state.permisos.length) {
        tablaPermisos.innerHTML = emptyRow(6, "No hay permisos configurados.");
        return;
    }

    tablaPermisos.innerHTML = state.permisos.map(permiso => `
        <tr>
            <td>${escapeHtml(permiso.rol_nombre || "")}</td>
            <td>${escapeHtml(permiso.modulo_nombre || "")}</td>
            <td>${toBadge(permiso.registrar)}</td>
            <td>${toBadge(permiso.modificar)}</td>
            <td>${toBadge(permiso.eliminar)}</td>
            <td class="table__actions">
                <div class="row-actions">
                    <button class="icon-action" type="button" data-action="edit-permiso" data-rol-id="${escapeHtml(String(permiso.rol_id))}" data-modulo-id="${escapeHtml(String(permiso.modulo_id))}">Editar</button>
                    <button class="icon-action icon-action--danger" type="button" data-action="delete-permiso" data-rol-id="${escapeHtml(String(permiso.rol_id))}" data-modulo-id="${escapeHtml(String(permiso.modulo_id))}">Eliminar</button>
                </div>
            </td>
        </tr>
    `).join("");

    bindPermisoActions();
}

function bindTableActions(table, items, type) {
    table.querySelectorAll("button[data-action]").forEach(btn => {
        btn.addEventListener("click", async () => {
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
                    if (roleName === "admin" && currentUserRole !== "admin") {
                        mostrarToast("Solo otro admin puede eliminar este usuario.", true);
                        return;
                    }
                }

                if (type === "rol") {
                    const nombreRol = String(item?.nombre || "").trim().toLowerCase();
                    if (nombreRol === "admin" || nombreRol === "cliente") {
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
                    modulo: "modulo",
                };
                const nombre = item?.nombre ? ` ${item.nombre}` : "";
                const mensaje = `¿Seguro que desea eliminar el ${labels[type]}${nombre}? Esta accion no se puede deshacer.`;

                abrirConfirmacion(mensaje, async () => {
                    await fetchJson(endpoints[type], { method: "DELETE" });
                    mostrarToast("Registro eliminado.");
                    await cargarTodo();
                });
            }
        });
    });
}

function bindPermisoActions() {
    tablaPermisos.querySelectorAll("button[data-action]").forEach(btn => {
        btn.addEventListener("click", async () => {
            const action = btn.dataset.action;
            const rolId = Number(btn.dataset.rolId);
            const moduloId = Number(btn.dataset.moduloId);
            const permiso = state.permisos.find(item => Number(item.rol_id) === rolId && Number(item.modulo_id) === moduloId);

            if (action === "edit-permiso") {
                setActiveTableTab("permisos");
                llenarFormularioPermiso(permiso);
                return;
            }

            if (action === "delete-permiso") {
                setActiveTableTab("permisos");
                const rolNombre = permiso?.rol_nombre || "este rol";
                const moduloNombre = permiso?.modulo_nombre || "este modulo";
                const mensaje = `¿Eliminar el permiso del rol ${rolNombre} en ${moduloNombre}?`;

                abrirConfirmacion(mensaje, async () => {
                    await fetchJson("/api/permisos", {
                        method: "DELETE",
                        body: JSON.stringify({ rol_id: rolId, modulo_id: moduloId }),
                    });
                    mostrarToast("Permiso eliminado.");
                    await cargarTodo();
                });
            }
        });
    });
}

function llenarFormularioUsuario(usuario) {
    if (!formUsuario || !usuario) return;
    formUsuario.id.value = usuario.id ?? "";
    formUsuario.nombre.value = usuario.nombre ?? "";
    formUsuario.cedula_personal.value = usuario.cedula_personal ?? "";
    formUsuario.password.required = false;
    formUsuario.password.placeholder = "Dejar vacio para conservar";
    formUsuario.password.value = "";
    formUsuario.rol_id.value = usuario.rol_id ?? "";
    formUsuario.foto_perfil_actual.value = usuario.foto_perfil ?? "";
    if (fotoPerfilName) {
        fotoPerfilName.textContent = usuario.foto_perfil ? usuario.foto_perfil.split("/").pop() : "Ningun archivo seleccionado";
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

function llenarFormularioPermiso(permiso) {
    if (!formPermiso || !permiso) return;
    formPermiso.rol_id.value = permiso.rol_id ?? "";
    formPermiso.modulo_id.value = permiso.modulo_id ?? "";
    formPermiso.registrar.checked = Boolean(Number(permiso.registrar));
    formPermiso.modificar.checked = Boolean(Number(permiso.modificar));
    formPermiso.eliminar.checked = Boolean(Number(permiso.eliminar));
}

async function onUsuarioSubmit(event) {
    event.preventDefault();

    const id = formUsuario.id.value;
    const formData = new FormData();
    formData.append("nombre", formUsuario.nombre.value.trim());
    formData.append("cedula_personal", String(Number(formUsuario.cedula_personal.value)));
    formData.append("password", formUsuario.password.value.trim());
    formData.append("rol_id", String(Number(formUsuario.rol_id.value)));
    formData.append("foto_perfil_actual", formUsuario.foto_perfil_actual.value || "");

    if (fotoPerfilInput?.files?.[0]) {
        formData.append("foto_perfil", fotoPerfilInput.files[0]);
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
        mostrarToast(id ? "Modulo actualizado." : "Modulo creado.");
        await cargarTodo();
    } catch (error) {
        mostrarToast(error.message || "No se pudo guardar el modulo.", true);
    }
}

async function onPermisoSubmit(event) {
    event.preventDefault();

    const payload = {
        rol_id: Number(formPermiso.rol_id.value),
        modulo_id: Number(formPermiso.modulo_id.value),
        registrar: formPermiso.registrar.checked,
        modificar: formPermiso.modificar.checked,
        eliminar: formPermiso.eliminar.checked,
    };

    try {
        await fetchJson("/api/permisos", { method: "POST", body: JSON.stringify(payload) });
        limpiarFormulario(formPermiso);
        mostrarToast("Permiso guardado.");
        await cargarTodo();
    } catch (error) {
        mostrarToast(error.message || "No se pudo guardar el permiso.", true);
    }
}

function limpiarFormulario(form) {
    if (!form) return;
    form.reset();
    if (form === formUsuario) {
        form.password.required = true;
        form.password.placeholder = "Contrasena";
        if (fotoPerfilName) {
            fotoPerfilName.textContent = "Ningun archivo seleccionado";
        }
        actualizarVistaPreviaFoto(null, null);
        if (fotoPerfilInput) {
            fotoPerfilInput.value = "";
        }
    }
    const idField = form.querySelector("input[name='id']");
    if (idField) {
        idField.value = "";
    }
}

async function fetchJson(url, options = {}) {
    const isMultipart = Boolean(options.isMultipart);
    const headers = {
        Accept: "application/json",
        ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
    };

    if (!isMultipart) {
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
        throw new Error(data.error || "No se pudo completar la operacion.");
    }

    return data;
}

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
    return `<tr><td colspan="${colspan}">${escapeHtml(text)}</td></tr>`;
}

function toBadge(value) {
    return Number(value) ? '<span class="badge badge--on">Si</span>' : '<span class="badge">No</span>';
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}
