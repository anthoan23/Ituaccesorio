document.addEventListener("DOMContentLoaded", () => {
	const perfilForm = document.getElementById("mi-perfil-form");
	const nombreInput = document.getElementById("mi-perfil-nombre");
	const cedulaInput = document.getElementById("mi-perfil-cedula");
	const rolInput = document.getElementById("mi-perfil-rol");
	const passwordInput = document.getElementById("mi-perfil-password");
	const passwordConfirmInput = document.getElementById("mi-perfil-password-confirm");
	const fotoInput = document.getElementById("mi-perfil-foto-input");
	const fotoBtn = document.getElementById("mi-perfil-foto-btn");
	const fotoName = document.getElementById("mi-perfil-foto-name");
	const fotoPreview = document.getElementById("mi-perfil-foto-preview");
	const csrfToken = perfilForm?.querySelector("input[name='_csrf_token']")?.value || "";

	const setupPasswordToggles = () => {
		document.querySelectorAll("[data-password-toggle]").forEach((button) => {
			const container = button.closest(".password-field");
			const input = container?.querySelector("input");
			if (!input) return;

			const updateLabel = () => {
				const showing = input.type === "text";
				button.textContent = showing ? "Ocultar" : "Mostrar";
				button.setAttribute("aria-label", showing ? "Ocultar contraseña" : "Mostrar contraseña");
			};

			updateLabel();
			button.addEventListener("click", () => {
				input.type = input.type === "password" ? "text" : "password";
				updateLabel();
			});
		});
	};

	setupPasswordToggles();

	if (!perfilForm || !nombreInput) {
		return;
	}

	let previewUrl = null;

	const headers = (isMultipart = false) => {
		const result = {
			Accept: "application/json",
			...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
		};

		if (!isMultipart) {
			result["Content-Type"] = "application/json";
		}
		return result;
	};

	const loadProfile = async () => {
		const response = await fetch("/api/usuarios/mi-perfil", {
			method: "GET",
			headers: headers(),
			credentials: "same-origin",
		});
		const data = await response.json().catch(() => ({}));
		if (!response.ok || data.success === false) {
			throw new Error(data.error || "No se pudo cargar tu perfil.");
		}
		return data.usuario || {};
	};

	const syncForm = (usuario) => {
		nombreInput.value = usuario.nombre || "";
		if (cedulaInput) cedulaInput.value = usuario.cedula ?? usuario.cedula_personal ?? "";
		if (rolInput) rolInput.value = usuario.rol_nombre || "";
		if (passwordInput) passwordInput.value = "";
		if (passwordConfirmInput) passwordConfirmInput.value = "";
		if (fotoInput) fotoInput.value = "";
		if (fotoName) fotoName.textContent = "Ningún archivo seleccionado";
		setPreview(null, usuario.foto_perfil || null);
	};

	const setPreview = (file, existing) => {
		if (!fotoPreview) {
			return;
		}
		if (previewUrl) {
			URL.revokeObjectURL(previewUrl);
			previewUrl = null;
		}
		if (file) {
			previewUrl = URL.createObjectURL(file);
			fotoPreview.src = previewUrl;
			return;
		}
		if (existing) {
			fotoPreview.src = existing;
			return;
		}
		fotoPreview.src = "/static/img/LOGO.png";
	};

	document.querySelector('[data-open-modal="modal-mi-perfil"]')?.addEventListener("click", async () => {
		try {
			const usuario = await loadProfile();
			syncForm(usuario);
		} catch (error) {
			alert(error.message || "No se pudo cargar tu perfil.");
		}
	});

	fotoBtn?.addEventListener("click", () => fotoInput?.click());

	fotoInput?.addEventListener("change", () => {
		const file = fotoInput.files?.[0];
		if (fotoName) {
			fotoName.textContent = file ? file.name : "Ningún archivo seleccionado";
		}
		setPreview(file || null, null);
	});

	perfilForm.addEventListener("submit", async (event) => {
		event.preventDefault();

		const password = (passwordInput?.value || "").trim();
		const passwordConfirm = (passwordConfirmInput?.value || "").trim();
		if (password && password !== passwordConfirm) {
			alert("La confirmación de contraseña no coincide.");
			return;
		}

		const formData = new FormData();
		formData.append("nombre", nombreInput.value.trim());
		if (password) {
			formData.append("password", password);
		}
		if (fotoInput?.files?.[0]) {
			formData.append("foto_perfil", fotoInput.files[0]);
		}

		try {
			const response = await fetch("/api/usuarios/mi-perfil", {
				method: "PUT",
				headers: headers(true),
				credentials: "same-origin",
				body: formData,
			});
			const data = await response.json().catch(() => ({}));
			if (!response.ok || data.success === false) {
				alert(data.error || "No se pudo actualizar tu perfil.");
				return;
			}
			window.location.reload();
		} catch (error) {
			alert("Error de conexión. Intenta nuevamente.");
		}
	});
});
