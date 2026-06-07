(function () {
	function crearElementoNotificacion(evento) {
		const item = document.createElement("article");
		item.className = "notifications__item";

		// Header con foto y nombre del usuario
		const header = document.createElement("div");
		header.className = "notifications__header";
		header.style.display = "flex";
		header.style.alignItems = "center";
		header.style.gap = "0.75rem";
		header.style.marginBottom = "0.5rem";

		// Foto del usuario
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

		// Nombre del usuario
		const nombre = document.createElement("strong");
		nombre.textContent = evento.usuario_nombre || "Sistema";
		nombre.style.fontSize = "0.9rem";
		header.appendChild(nombre);

		item.appendChild(header);

		// Título de la acción
		const titulo = document.createElement("div");
		titulo.style.fontWeight = "bold";
		titulo.style.marginBottom = "0.25rem";
		titulo.textContent = evento.titulo || "Nueva notificación";
		item.appendChild(titulo);

		// Descripción
		const descripcion = document.createElement("p");
		descripcion.textContent = evento.descripcion || "Se registró una nueva actividad en la bitácora.";
		descripcion.style.margin = "0.25rem 0";
		descripcion.style.fontSize = "0.85rem";
		descripcion.style.color = "rgba(255, 255, 255, 0.82)";
		item.appendChild(descripcion);

		// Meta información
		const meta = document.createElement("small");
		const partesMeta = [];
		if (evento.accion) partesMeta.push(evento.accion);
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

	async function cargarNotificacionesHistoricas() {
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
			const badge = document.querySelector("[data-notifications-badge]");
			
			if (!list) return;
			
			if (notificaciones.length === 0) {
				if (emptyState) emptyState.hidden = false;
				return;
			}
			
			if (emptyState) emptyState.hidden = true;
			
			// Limpiar lista actual
			list.innerHTML = '';
			
			// Agregar notificaciones históricas
			notificaciones.forEach(notificacion => {
				const item = crearElementoNotificacion(notificacion);
				list.appendChild(item);
			});
			
			// Actualizar badge con el contador (últimas 3)
			if (badge) {
				badge.hidden = false;
				badge.textContent = String(notificaciones.length);
			}
		} catch (error) {
			console.error("Error cargando notificaciones históricas:", error);
		}
	}

	function inicializarNotificaciones() {
		const usuarioId = document.body?.dataset?.userId;
		const root = document.querySelector("[data-notifications-root]");
		const toggle = document.querySelector("[data-notifications-toggle]");
		const panel = document.querySelector("[data-notifications-panel]");
		const list = document.querySelector("[data-notifications-list]");
		const emptyState = document.querySelector("[data-notifications-empty]");
		const badge = document.querySelector("[data-notifications-badge]");
		const status = document.querySelector("[data-notifications-status]");

		if (!usuarioId || !root || !toggle || !panel || !list || !status || !window.EventSource) {
			return;
		}

		panel.hidden = true;
		toggle.setAttribute("aria-expanded", "false");

		let contador = 0;
		let fuente = null;

		const actualizarBadge = () => {
			if (!badge) return;
			if (contador <= 0) {
				badge.hidden = true;
				badge.textContent = "0";
				return;
			}
			badge.hidden = false;
			badge.textContent = contador > 99 ? "99+" : String(contador);
		};

		const actualizarEstado = (texto, conectado = false) => {
			status.textContent = texto;
			status.dataset.connected = conectado ? "true" : "false";
		};

		const agregarNotificacion = (evento) => {
			const item = crearElementoNotificacion(evento);
			if (emptyState) emptyState.hidden = true;
			
			// Agregar al principio de la lista
			list.prepend(item);
			contador += 1;
			actualizarBadge();
			
			// Limitar a 20 notificaciones en el panel
			while (list.children.length > 20) {
				list.removeChild(list.lastChild);
			}
		};

		const conectar = () => {
			if (fuente) {
				fuente.close();
			}

			const url = `/notificaciones/stream/${encodeURIComponent(usuarioId)}`;
			fuente = new EventSource(url);

			fuente.addEventListener("open", () => {
				console.log("✅ SSE Conectado");
				actualizarEstado("Conectado", true);
			});

			fuente.addEventListener("bitacora", (event) => {
				try {
					const data = JSON.parse(event.data || "{}");
					console.log("📨 Notificación recibida:", data);
					agregarNotificacion(data);
				} catch (error) {
					console.error("No se pudo leer la notificacion SSE", error);
				}
			});

			fuente.onerror = () => {
				console.log("⚠️ SSE Reconectando...");
				actualizarEstado("Reconectando...");
			};
		};

		// Cuando se abre el panel, cargar notificaciones históricas
		toggle.addEventListener("click", async () => {
			const abierto = panel.hidden;
			panel.hidden = !abierto;
			toggle.setAttribute("aria-expanded", abierto ? "true" : "false");
			
			if (abierto) {
				// Al abrir el panel, cargar las últimas 3 notificaciones
				await cargarNotificacionesHistoricas();
				// Resetear contador de nuevas notificaciones
				contador = 0;
				actualizarBadge();
			}
		});

		document.addEventListener("click", (event) => {
			if (root.contains(event.target)) {
				return;
			}
			panel.hidden = true;
			toggle.setAttribute("aria-expanded", "false");
		});

		window.addEventListener("beforeunload", () => {
			if (fuente) {
				fuente.close();
			}
		});

		actualizarEstado("Conectando...");
		conectar();
	}

	document.addEventListener("DOMContentLoaded", inicializarNotificaciones);
})();