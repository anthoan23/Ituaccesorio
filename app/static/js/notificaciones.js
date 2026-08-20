(function () {
    let notificacionesNoLeidas = 0;
    let panelAbierto = false;
    let inicializado = false;
    const STORAGE_KEY = 'notificaciones_vistas';

    // Función para obtener las notificaciones ya vistas
    function getNotificacionesVistas() {
        try {
            const vistas = sessionStorage.getItem(STORAGE_KEY);
            return vistas ? JSON.parse(vistas) : [];
        } catch {
            return [];
        }
    }

    // Función para guardar notificaciones vistas
    function guardarNotificacionVista(id) {
        try {
            const vistas = getNotificacionesVistas();
            if (!vistas.includes(id)) {
                vistas.push(id);
                sessionStorage.setItem(STORAGE_KEY, JSON.stringify(vistas));
            }
        } catch (error) {
            console.error('Error guardando notificación vista:', error);
        }
    }

    // Función para verificar si una notificación ya fue vista
    function notificacionYaVista(id) {
        const vistas = getNotificacionesVistas();
        return vistas.includes(id);
    }

    // Función para marcar TODAS las notificaciones como vistas
    function marcarTodasComoVistas(notificaciones) {
        try {
            const vistas = getNotificacionesVistas();
            const nuevosIds = notificaciones
                .map(n => n.id)
                .filter(id => id && !vistas.includes(id));
            
            if (nuevosIds.length > 0) {
                const todasVistas = [...vistas, ...nuevosIds];
                sessionStorage.setItem(STORAGE_KEY, JSON.stringify(todasVistas));
                console.log(`✅ ${nuevosIds.length} nuevas notificaciones marcadas como vistas en sesión`);
            }
        } catch (error) {
            console.error('Error marcando notificaciones como vistas:', error);
        }
    }

    function crearElementoNotificacion(evento) {
        const item = document.createElement("article");
        item.className = "notifications__item";
        if (evento.id) {
            item.dataset.notificacionId = evento.id;
        }

        const header = document.createElement("div");
        header.className = "notifications__header";
        header.style.display = "flex";
        header.style.alignItems = "center";
        header.style.gap = "0.75rem";
        header.style.marginBottom = "0.5rem";

        // Avatar con soporte para tema claro/oscuro
        const avatarWrapper = document.createElement("div");
        avatarWrapper.className = "avatar-icon";
        
        if (evento.usuario_foto) {
            const foto = document.createElement("img");
            foto.src = evento.usuario_foto;
            foto.alt = evento.usuario_nombre || "Usuario";
            foto.className = "avatar-img";
            foto.style.width = "32px";
            foto.style.height = "32px";
            foto.style.borderRadius = "50%";
            foto.style.objectFit = "cover";
            avatarWrapper.appendChild(foto);
        } else {
            const inicial = (evento.usuario_nombre || "U").charAt(0).toUpperCase();
            avatarWrapper.textContent = inicial;
            avatarWrapper.style.width = "32px";
            avatarWrapper.style.height = "32px";
            avatarWrapper.style.borderRadius = "50%";
            avatarWrapper.style.background = "var(--yellow, #f3c500)";
            avatarWrapper.style.color = "var(--ink, #121212)";
            avatarWrapper.style.display = "flex";
            avatarWrapper.style.alignItems = "center";
            avatarWrapper.style.justifyContent = "center";
            avatarWrapper.style.fontWeight = "bold";
            avatarWrapper.style.fontSize = "0.9rem";
            avatarWrapper.style.flexShrink = "0";
        }
        header.appendChild(avatarWrapper);

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
        item.appendChild(meta);

        return item;
    }

    function actualizarBadge() {
        const badge = document.querySelector("[data-notifications-badge]");
        if (!badge) return;
        
        if (notificacionesNoLeidas <= 0) {
            badge.hidden = true;
            badge.textContent = "0";
        } else {
            badge.hidden = false;
            badge.textContent = notificacionesNoLeidas > 99 ? "99+" : String(notificacionesNoLeidas);
        }
        console.log("Badge actualizado:", notificacionesNoLeidas);
    }

    function agregarNotificacion(evento) {
        const list = document.querySelector("[data-notifications-list]");
        const emptyState = document.querySelector("[data-notifications-empty]");
        
        if (!list) return;
        
        // Verificar si la notificación ya fue vista
        if (evento.id && notificacionYaVista(evento.id)) {
            console.log(`Notificación ${evento.id} ya vista, no se incrementa contador`);
            const item = crearElementoNotificacion(evento);
            if (emptyState) emptyState.hidden = true;
            list.prepend(item);
            return;
        }
        
        const item = crearElementoNotificacion(evento);
        if (emptyState) emptyState.hidden = true;
        
        list.prepend(item);
        
        while (list.children.length > 20) {
            list.removeChild(list.lastChild);
        }
        
        if (!panelAbierto) {
            notificacionesNoLeidas++;
            actualizarBadge();
        }
    }

    async function cargarNotificacionesHistoricas(marcarComoVistas = true) {
        try {
            const response = await fetch('/api/bitacora/ultimas-notificaciones', {
                headers: {
                    'Accept': 'application/json',
                    'X-CSRFToken': document.querySelector('input[name="_csrf_token"]')?.value || ''
                },
                credentials: 'same-origin'
            });

            if (!response.ok) return;

            const data = await response.json();
            const notificaciones = data.notificaciones || [];
            const list = document.querySelector("[data-notifications-list]");
            const emptyState = document.querySelector("[data-notifications-empty]");

            if (!list) return;

            if (notificaciones.length === 0) {
                if (emptyState) emptyState.hidden = false;
                list.innerHTML = '<div class="notifications__empty">No hay notificaciones</div>';
                notificacionesNoLeidas = 0;
                actualizarBadge();
                return;
            }

            if (emptyState) emptyState.hidden = true;
            list.innerHTML = '';

            let noVistas = 0;

            notificaciones.forEach(notificacion => {
                const item = crearElementoNotificacion(notificacion);
                list.appendChild(item);
                
                if (notificacion.id && !notificacionYaVista(notificacion.id)) {
                    noVistas++;
                }
            });

            if (marcarComoVistas) {
                marcarTodasComoVistas(notificaciones);
                notificacionesNoLeidas = 0;
            } else {
                notificacionesNoLeidas = noVistas;
            }
            
            actualizarBadge();
            
        } catch (error) {
            console.error("Error cargando notificaciones históricas:", error);
        }
    }

    function inicializarNotificaciones() {
        if (inicializado) return;
        inicializado = true;

        const usuarioId = document.body?.dataset?.userId;
        const root = document.querySelector("[data-notifications-root]");
        const toggle = document.querySelector("[data-notifications-toggle]");
        const panel = document.querySelector("[data-notifications-panel]");
        const status = document.querySelector("[data-notifications-status]");

        if (!usuarioId || !toggle || !panel) {
            return;
        }

        panel.hidden = true;
        panelAbierto = false;
        toggle.setAttribute("aria-expanded", "false");
        if (status) status.textContent = "Listo";

        cargarNotificacionesHistoricas(false);

        toggle.addEventListener("click", async (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            console.log("Click en notificaciones - Panel abierto:", panelAbierto);
            
            if (panelAbierto) {
                panel.hidden = true;
                panelAbierto = false;
                toggle.setAttribute("aria-expanded", "false");
                console.log("Panel cerrado");
            } else {
                await cargarNotificacionesHistoricas(true);
                panel.hidden = false;
                panelAbierto = true;
                toggle.setAttribute("aria-expanded", "true");
                console.log("Panel abierto - notificaciones marcadas como vistas en sesión");
            }
        });

        document.addEventListener("click", (event) => {
            if (root && !root.contains(event.target) && panelAbierto) {
                panel.hidden = true;
                panelAbierto = false;
                toggle.setAttribute("aria-expanded", "false");
                console.log("Panel cerrado por clic fuera");
            }
        });

        let fuente = null;
        
        function conectarSSE() {
            if (fuente) {
                fuente.close();
            }
            
            const url = `/notificaciones/stream/${encodeURIComponent(usuarioId)}`;
            console.log("Conectando SSE a:", url);
            fuente = new EventSource(url);
            
            fuente.addEventListener("open", () => {
                console.log("SSE Conectado");
                if (status) status.textContent = "Conectado";
            });
            
            fuente.addEventListener("bitacora", (event) => {
                try {
                    const data = JSON.parse(event.data || "{}");
                    console.log("Nueva notificación recibida:", data);
                    agregarNotificacion(data);
                } catch (error) {
                    console.error("Error al procesar notificación SSE:", error);
                }
            });
            
            fuente.onerror = (error) => {
                console.log("SSE Error:", error);
                if (status) status.textContent = "Reconectando...";
                setTimeout(conectarSSE, 3000);
            };
        }
        
        conectarSSE();
        
        window.addEventListener("beforeunload", () => {
            if (fuente) fuente.close();
        });
        
        console.log("Notificaciones inicializadas correctamente");
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializarNotificaciones);
    } else {
        inicializarNotificaciones();
    }
})();