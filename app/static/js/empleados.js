(() => {
    const modalEmpleado = document.getElementById('modal');
    const modalTitle = document.getElementById('modal-title');
    const modalClose = document.getElementById('modal-cerrar');
    const btnRegistrar = document.getElementById('btn-registrar');
    const btnRegistrarCargo = document.getElementById('btn-registrar-cargo');
    const btnRegistrarEspecialidad = document.getElementById('btn-registrar-especialidad');

    const modalCargo = document.getElementById('modal-cargo');
    const modalEspecialidad = document.getElementById('modal-especialidad');
    const modalCargoClose = document.getElementById('modal-cargo-cerrar');
    const modalEspecialidadClose = document.getElementById('modal-especialidad-cerrar');

    const formEmpleado = document.getElementById('form-empleado');
    const formCargo = document.getElementById('form-cargo');
    const formEspecialidad = document.getElementById('form-especialidad');
    const toast = document.getElementById('toast');

    if (!modalEmpleado || !formEmpleado) return;

    function showToast(text) {
        if (!toast) return;
        toast.textContent = text;
        toast.classList.add('is-show');
        setTimeout(() => toast.classList.remove('is-show'), 2200);
    }

    function openEmpleadoModal() {
        modalEmpleado.classList.add('is-open');
        modalEmpleado.setAttribute('aria-hidden', 'false');
        if (modalTitle) modalTitle.textContent = 'Registrar empleado';
        document.body.style.overflow = 'hidden';

        const first = formEmpleado.querySelector('input, select, textarea, button');
        if (first) first.focus();
    }

    function closeEmpleadoModal() {
        modalEmpleado.classList.remove('is-open');
        modalEmpleado.setAttribute('aria-hidden', 'true');
        formEmpleado.reset();
        syncBodyScroll();
    }

    function openSimpleModal(modalEl) {
        if (!modalEl) return;
        modalEl.setAttribute('aria-hidden', 'false');
        modalEl.style.display = 'block';
        document.body.style.overflow = 'hidden';

        const firstInput = modalEl.querySelector('input, select, textarea, button');
        if (firstInput) firstInput.focus();
    }

    function closeSimpleModal(modalEl) {
        if (!modalEl) return;
        modalEl.setAttribute('aria-hidden', 'true');
        modalEl.style.display = 'none';
        syncBodyScroll();
    }

    function syncBodyScroll() {
        const empleadoOpen = modalEmpleado.classList.contains('is-open');
        const cargoOpen = modalCargo && modalCargo.getAttribute('aria-hidden') === 'false';
        const especialidadOpen = modalEspecialidad && modalEspecialidad.getAttribute('aria-hidden') === 'false';
        document.body.style.overflow = empleadoOpen || cargoOpen || especialidadOpen ? 'hidden' : '';
    }

    function obtenerCsrfToken() {
        const csrfInput = formEmpleado.querySelector('input[name="_csrf_token"]');
        return csrfInput ? csrfInput.value : '';
    }

    // Abrir modales
    btnRegistrar && btnRegistrar.addEventListener('click', openEmpleadoModal);
    btnRegistrarCargo && btnRegistrarCargo.addEventListener('click', () => openSimpleModal(modalCargo));
    btnRegistrarEspecialidad && btnRegistrarEspecialidad.addEventListener('click', () => openSimpleModal(modalEspecialidad));

    // Cerrar modal empleado
    modalClose && modalClose.addEventListener('click', closeEmpleadoModal);
    modalEmpleado.addEventListener('click', (e) => {
        if (e.target === modalEmpleado) closeEmpleadoModal();
    });

    // Cerrar modal cargo
    modalCargoClose && modalCargoClose.addEventListener('click', () => closeSimpleModal(modalCargo));
    modalCargo && modalCargo.addEventListener('click', (e) => {
        if (e.target === modalCargo) closeSimpleModal(modalCargo);
    });

    // Cerrar modal especialidad
    modalEspecialidadClose && modalEspecialidadClose.addEventListener('click', () => closeSimpleModal(modalEspecialidad));
    modalEspecialidad && modalEspecialidad.addEventListener('click', (e) => {
        if (e.target === modalEspecialidad) closeSimpleModal(modalEspecialidad);
    });

    document.addEventListener('keydown', (e) => {
        if (e.key !== 'Escape') return;
        if (modalEmpleado.classList.contains('is-open')) {
            closeEmpleadoModal();
            return;
        }
        if (modalCargo && modalCargo.getAttribute('aria-hidden') === 'false') {
            closeSimpleModal(modalCargo);
            return;
        }
        if (modalEspecialidad && modalEspecialidad.getAttribute('aria-hidden') === 'false') {
            closeSimpleModal(modalEspecialidad);
        }
    });

    // Submit modal cargo
    formCargo && formCargo.addEventListener('submit', (e) => {
        e.preventDefault();
        const cargo = formCargo.cargo_nombre.value.trim();
        if (!cargo) {
            formCargo.cargo_nombre.focus();
            return;
        }

        fetch('/api/cargos', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                Accept: 'application/json',
                ...(obtenerCsrfToken() ? { 'X-CSRFToken': obtenerCsrfToken() } : {}),
            },
            body: JSON.stringify({ cargo }),
        })
            .then(async (response) => ({ response, data: await response.json().catch(() => ({})) }))
            .then(({ response, data }) => {
                if (response.ok && data.success) {
                    showToast(data.message || `Cargo "${cargo}" guardado`);
                    closeSimpleModal(modalCargo);
                    formCargo.reset();
                    return;
                }
                showToast(data.error || 'No se pudo agregar el cargo');
            })
            .catch((error) => {
                console.error(error);
                showToast('Error de conexion al guardar cargo');
            });
    });

    // Submit modal especialidad
    formEspecialidad && formEspecialidad.addEventListener('submit', (e) => {
        e.preventDefault();
        const especialidad = formEspecialidad.especialidad_nombre.value.trim();
        if (!especialidad) {
            formEspecialidad.especialidad_nombre.focus();
            return;
        }

        fetch('/api/especialidades', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                Accept: 'application/json',
                ...(obtenerCsrfToken() ? { 'X-CSRFToken': obtenerCsrfToken() } : {}),
            },
            body: JSON.stringify({ especialidad }),
        })
            .then(async (response) => ({ response, data: await response.json().catch(() => ({})) }))
            .then(({ response, data }) => {
                if (response.ok && data.success) {
                    showToast(data.message || `Especialidad "${especialidad}" guardada`);
                    closeSimpleModal(modalEspecialidad);
                    formEspecialidad.reset();
                    return;
                }
                showToast(data.error || 'No se pudo agregar la especialidad');
            })
            .catch((error) => {
                console.error(error);
                showToast('Error de conexion al guardar especialidad');
            });
    });

    // Submit modal empleado
    formEmpleado.addEventListener('submit', async (e) => {
        e.preventDefault();

        const cedula = (formEmpleado.querySelector('input[name="id"]')?.value || '').trim();
        const nombre = (formEmpleado.querySelector('input[name="nombre"]')?.value || '').trim();
        const apellido = (formEmpleado.querySelector('input[name="apellido"]')?.value || '').trim();
        const celularPrefijo = (formEmpleado.querySelector('select[name="celular_prefijo"]')?.value || '').trim();
        const celularNumero = (formEmpleado.querySelector('input[name="celular_numero"]')?.value || '').trim();
        const correo = (formEmpleado.querySelector('input[name="correo"]')?.value || '').trim();
        const direccion = (formEmpleado.querySelector('input[name="direccion"]')?.value || '').trim();
        const celular = `${celularPrefijo}${celularNumero}`;

        if (!cedula || !nombre || !apellido || !celular || !correo || !direccion) {
            showToast('Todos los campos son obligatorios');
            return;
        }

        const payload = {
            cedula,
            nombre,
            apellido,
            celular,
            correo,
            direccion,
        };

        try {
            const csrfToken = obtenerCsrfToken();
            const response = await fetch('/api/empleados', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    Accept: 'application/json',
                    ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json().catch(() => ({}));

            if (response.ok && data.success) {
                showToast(data.message || 'Empleado agregado exitosamente');
                closeEmpleadoModal();
                await cargarEmpleados();
                return;
            }

            showToast(data.error || 'No se pudo agregar el empleado');
        } catch (error) {
            console.error(error);
            showToast('Error de conexion al guardar empleado');
        }
    });

    // Cargar lista de empleados desde el controlador
    async function cargarEmpleados() {
        const tbody = document.getElementById('tabla-empleados');
        if (!tbody) return;

        try {
            const res = await fetch('/api/empleados', { credentials: 'same-origin' });
            if (!res.ok) throw new Error('Error al obtener empleados');

            const data = await res.json();
            tbody.innerHTML = '';

            if (!Array.isArray(data) || data.length === 0) {
                const tr = document.createElement('tr');
                tr.innerHTML = '<td colspan="4" style="text-align:center; font-weight:700; color: #6a6a6a;">No hay empleados registrados</td>';
                tbody.appendChild(tr);
                return;
            }

            data.forEach((emp) => {
                const tr = document.createElement('tr');
                const cedula = emp.cedula ?? emp.ID_em ?? '';
                const nombreCompleto = (emp.nombre || '') + (emp.apellido ? ` ${emp.apellido}` : '');
                const rol = emp.rol ?? '';

                tr.innerHTML = `
                    <td>${cedula}</td>
                    <td>${nombreCompleto}</td>
                    <td>${rol}</td>
                    <td class="table__actions"><div class="row-actions"><button class="icon-action" type="button" aria-label="Editar" data-id="${cedula}">✎</button><button class="icon-action" type="button" aria-label="Eliminar" data-id="${cedula}">🗑</button></div></td>
                `;

                tbody.appendChild(tr);
            });
        } catch (err) {
            console.error(err);
        }
    }

    // Cargar al inicio
    cargarEmpleados();
})();


