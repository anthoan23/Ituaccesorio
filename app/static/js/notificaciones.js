(function () {
	function crearElementoNotificacion(evento) {
		const item = document.createElement("article");
		item.className = "notifications__item";

		const titulo = document.createElement("strong");
		titulo.textContent = evento.titulo || "Nueva notificacion";

		const descripcion = document.createElement("p");
		descripcion.textContent = evento.descripcion || "Se registró una nueva actividad en la bitácora.";

		const meta = document.createElement("small");
		const partesMeta = [];
		if (evento.accion) partesMeta.push(evento.accion);
		if (evento.modulo_nombre) partesMeta.push(evento.modulo_nombre);
		if (evento.fecha_hora) partesMeta.push(evento.fecha_hora);
		meta.textContent = partesMeta.join(" · ");

		item.appendChild(titulo);
		item.appendChild(descripcion);
		item.appendChild(meta);
		return item;
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
			if (emptyState) {
				emptyState.hidden = true;
			}

			list.prepend(item);
			contador += 1;
			actualizarBadge();
		};

		const conectar = () => {
			if (fuente) {
				fuente.close();
			}

			const url = `/notificaciones/stream/${encodeURIComponent(usuarioId)}`;
			fuente = new EventSource(url);

			fuente.addEventListener("open", () => {
				actualizarEstado("Conectado", true);
			});

			fuente.addEventListener("bitacora", (event) => {
				try {
					const data = JSON.parse(event.data || "{}");
					agregarNotificacion(data);
				} catch (error) {
					console.error("No se pudo leer la notificacion SSE", error);
				}
			});

			fuente.onerror = () => {
				actualizarEstado("Reconectando...");
			};
		};

		toggle.addEventListener("click", () => {
			const abierto = panel.hidden;
			panel.hidden = !abierto;
			toggle.setAttribute("aria-expanded", abierto ? "true" : "false");
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
