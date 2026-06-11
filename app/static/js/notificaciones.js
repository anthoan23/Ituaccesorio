(function () {
    let panelAbierto = false;
    let inicializado = false;

    function crearElementoNotificacion(evento) {
        const item = document.createElement("article");
        item.className = "notifications__item";

        const header = document.createElement("div");
        header.className = "notifications__header";
        header.style.display = "flex";
        header.style.alignItems = "center";
        header.style.gap = "0.75rem";
        header.style.marginBottom = "0.5rem";

        if (evento.usuario_foto) {
            const foto = document.createElement("img");
            foto.src = evento.usuario_foto;
            foto.alt = evento.usuario_nombre || "Usuario";
            foto.style.width = "32px";
            foto.style.height = "32px";
            foto.style.borderRadius = "50%";
            foto.style.objectFit = "cover";
            header.appendChild(foto);
        } else {
            const icono = document.createElement("div");
            icono.textContent = (evento.usuario_nombre || "U").charAt(0).toUpperCase();
            icono.style.width = "32px";
            icono.style.height = "32px";
            icono.style.borderRadius = "50%";
            icono.style.background = "#f3c500";
            icono.style.color = "#111";
            icono.style.display = "flex";
            icono.style.alignItems = "center";
            icono.style.justifyContent = "center";
            icono.style.fontWeight = "bold";
            header.appendChild(icono);
        }

        const nombre = document.createElement("strong");
        nombre.textContent = evento.usuario_nombre || "Sistema";
        nombre.style.fontSize = "0.9rem";
        header.appendChild(nombre);
        item.appendChild(header);

        const titulo = document.createElement("div");
        titulo.style.fontWeight = "bold";
        titulo.style.marginBottom = "0.25rem";
        titulo.textContent = evento.titulo || evento.accion || "Nueva notificación";
        item.appendChild(titulo);

        const descripcion = document.createElement("p");
        descripcion.textContent = evento.descripcion || "Se registró una nueva actividad en la bitácora.";
        descripcion.style.margin = "0.25rem 0";
        descripcion.style.fontSize = "0.85rem";
        descripcion.style.color = "rgba(255, 255, 255, 0.82)";
        item.appendChild(descripcion);

        const meta = document.createElement("small");
        const partesMeta = [];
        if (evento.modulo_nombre) partesMeta.push(evento.modulo_nombre);
        if (evento.fecha_hora) {
            const fecha = new Date(evento.fecha_hora);
            const ahora = new Date();
            const diffMs = ahora - fecha;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);

            if (diffMins < 1) {
                partesMeta.push("hace unos segundos");
            } else if (diffMins < 60) {
                partesMeta.push(`hace ${diffMins} minuto${diffMins !== 1 ? 's' : ''}`);
            } else if (diffHours < 24) {
                partesMeta.push(`hace ${diffHours} hora${diffHours !== 1 ? 's' : ''}`);
            } else {
                partesMeta.push(fecha.toLocaleDateString());
            }
        }
        meta.textContent = partesMeta.join(" · ");
        meta.style.fontSize = "0.72rem";
        meta.style.color = "rgba(255, 255, 255, 0.55)";
        item.appendChild(meta);

        return item;
    }

    async function cargarNotificaciones() {
        try {
            const statusEl = document.querySelector("[data-notifications-status]");
            if (statusEl) statusEl.textContent = "Cargando...";
            
            const response = await fetch('/api/bitacora/ultimas-notificaciones', {
                headers: {
                    'Accept': 'application/json',
                    'X-CSRFToken': document.querySelector('input[name="_csrf_token"]')?.value || ''
                },
                credentials: 'same-origin'
            });

            if (!response.ok) {
                if (statusEl) statusEl.textContent = "Error";
                return;
            }

            const data = await response.json();
            const notificaciones = data.notificaciones || [];
            const list = document.querySelector("[data-notifications-list]");
            const emptyState = document.querySelector("[data-notifications-empty]");
            const badge = document.querySelector("[data-notifications-badge]");

            if (!list) return;

            if (statusEl) statusEl.textContent = "Conectado";

            if (notificaciones.length === 0) {
                if (emptyState) emptyState.hidden = false;
                list.innerHTML = '<div class="notifications__empty">No hay notificaciones</div>';
                if (badge) badge.hidden = true;
                return;
            }

            if (emptyState) emptyState.hidden = true;
            list.innerHTML = '';

            notificaciones.forEach(notificacion => {
                const item = crearElementoNotificacion(notificacion);
                list.appendChild(item);
            });

            if (badge && !panelAbierto) {
                badge.hidden = false;
                badge.textContent = String(notificaciones.length);
            }
        } catch (error) {
            console.error("Error cargando notificaciones:", error);
            const statusEl = document.querySelector("[data-notifications-status]");
            if (statusEl) statusEl.textContent = "Error";
        }
    }

    function inicializarNotificaciones() {
        if (inicializado) return;
        inicializado = true;

        const root = document.querySelector("[data-notifications-root]");
        const toggle = document.querySelector("[data-notifications-toggle]");
        const panel = document.querySelector("[data-notifications-panel]");
        const badge = document.querySelector("[data-notifications-badge]");

        if (!toggle || !panel) {
            console.log("Faltan elementos");
            return;
        }

        if (root) root.style.position = 'relative';
        
        // Configurar clases iniciales
        panel.classList.add('notifications__panel--hidden');
        panel.classList.remove('notifications__panel--visible');

        // Configurar scroll en la lista
        const list = document.querySelector("[data-notifications-list]");
        if (list) {
            list.style.maxHeight = '300px';
            list.style.overflowY = 'auto';
        }

        // Cargar notificaciones iniciales
        cargarNotificaciones();

        // Remover cualquier listener anterior
        const newToggle = toggle.cloneNode(true);
        toggle.parentNode.replaceChild(newToggle, toggle);
        
        newToggle.addEventListener("click", async function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            if (panel.classList.contains('notifications__panel--hidden')) {
                await cargarNotificaciones();
                panel.classList.remove('notifications__panel--hidden');
                panel.classList.add('notifications__panel--visible');
                if (badge) badge.hidden = true;
                panelAbierto = true;
                console.log("Panel abierto");
            } else {
                panel.classList.remove('notifications__panel--visible');
                panel.classList.add('notifications__panel--hidden');
                panelAbierto = false;
                console.log("Panel cerrado");
            }
        });

        // Cerrar al hacer clic fuera
        document.addEventListener("click", function(e) {
            const rootEl = document.querySelector("[data-notifications-root]");
            if (rootEl && !rootEl.contains(e.target) && panel.classList.contains('notifications__panel--visible')) {
                panel.classList.remove('notifications__panel--visible');
                panel.classList.add('notifications__panel--hidden');
                panelAbierto = false;
                console.log("Panel cerrado por clic fuera");
            }
        });

        console.log("Notificaciones inicializadas");
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializarNotificaciones);
    } else {
        inicializarNotificaciones();
    }
})();