(() => {
    const modal = document.getElementById('modal');
    const modalDialog = modal && modal.querySelector('.modal__dialog');
    const modalTitle = document.getElementById('modal-title');
    const modalClose = document.getElementById('modal-cerrar');
    const btnRegistrar = document.getElementById('btn-registrar');
    const btnRegistrarCargo = document.getElementById('btn-registrar-cargo');
    const btnRegistrarEspecialidad = document.getElementById('btn-registrar-especialidad');
    const form = document.getElementById('form-empleado');
    const toast = document.getElementById('toast');

    if (!modal || !form) return;

    function openModal(kind = 'empleado') {
        modal.classList.add('is-open');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        if (modalTitle) {
            if (kind === 'empleado') modalTitle.textContent = 'Registrar empleado';
            else if (kind === 'cargo') modalTitle.textContent = 'Registrar cargo';
            else if (kind === 'especialidad') modalTitle.textContent = 'Registrar especialidad';
        }
        form.dataset.kind = kind;
        // focus first input if exists
        const first = form.querySelector('input, select, textarea, button');
        if (first) first.focus();
    }

    function closeModal() {
        modal.classList.remove('is-open');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        form.reset();
        delete form.dataset.kind;
    }

    function showToast(text) {
        if (!toast) return;
        toast.textContent = text;
        toast.classList.add('is-show');
        setTimeout(() => toast.classList.remove('is-show'), 2200);
    }

    function obtenerCsrfToken() {
        const csrfInput = form.querySelector('input[name="_csrf_token"]');
        return csrfInput ? csrfInput.value : '';
    }

    // Button handlers
    btnRegistrar && btnRegistrar.addEventListener('click', () => openModal('empleado'));
    btnRegistrarCargo && btnRegistrarCargo.addEventListener('click', () => openModal('cargo'));
    btnRegistrarEspecialidad && btnRegistrarEspecialidad.addEventListener('click', () => openModal('especialidad'));

    // Close handlers
    modalClose && modalClose.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('is-open')) closeModal();
    });

    // Submit handler
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const kind = form.dataset.kind || 'registro';

        // Los formularios de cargo/especialidad no tienen endpoint en backend todavía.
        if (kind !== 'empleado') {
            showToast(`${kind.charAt(0).toUpperCase() + kind.slice(1)} guardado`);
            closeModal();
            return;
        }

        const cedula = (form.querySelector('input[name="id"]')?.value || '').trim();
        const nombre = (form.querySelector('input[name="nombre"]')?.value || '').trim();
        const apellido = (form.querySelector('input[name="apellido"]')?.value || '').trim();
        const celularPrefijo = (form.querySelector('select[name="celular_prefijo"]')?.value || '').trim();
        const celularNumero = (form.querySelector('input[name="celular_numero"]')?.value || '').trim();
        const correo = (form.querySelector('input[name="correo"]')?.value || '').trim();
        const direccion = (form.querySelector('input[name="direccion"]')?.value || '').trim();
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
                    'Accept': 'application/json',
                    ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json().catch(() => ({}));

            if (response.ok && data.success) {
                showToast(data.message || 'Empleado agregado exitosamente');
                closeModal();
                await cargarEmpleados();
                return;
            }

            showToast(data.error || 'No se pudo agregar el empleado');
        } catch (error) {
            console.error(error);
            showToast('Error de conexión al guardar empleado');
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
                    tr.innerHTML = `<td colspan="4" style="text-align:center; font-weight:700; color: #6a6a6a;">No hay empleados registrados</td>`;
                    tbody.appendChild(tr);
                    return;
                }

                data.forEach(emp => {
                    const tr = document.createElement('tr');
                    const cedula = emp.cedula ?? emp.ID_em ?? '';
                    const nombre = (emp.nombre || '') + (emp.apellido ? ' ' + emp.apellido : '');
                    const rol = emp.rol ?? '';
                    tr.innerHTML = `
                        <td>${cedula}</td>
                        <td>${nombre}</td>
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


