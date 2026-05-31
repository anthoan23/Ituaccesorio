(() => {
	let recaptchaAdjustTimer = null;

	const ajustarRecaptcha = () => {
		const widgets = document.querySelectorAll(".g-recaptcha");
		if (!widgets.length) {
			return;
		}

		widgets.forEach((widget) => {
			const container = widget.parentElement;
			if (!container) {
				return;
			}

			const isPhoneCaptcha = Boolean(widget.closest(".phone__captcha"));
			// Limpia ajustes previos solo para contenedores que NO sean el captcha del phone.
			if (!isPhoneCaptcha && container.style.height) {
				container.style.height = "";
			}

			const containerWidth = container.getBoundingClientRect().width;
			const widgetWidth = widget.getBoundingClientRect().width || widget.offsetWidth || 304;
			if (!containerWidth || !widgetWidth) {
				return;
			}

			const scaleToFit = Math.min(1, containerWidth / widgetWidth);
			const scale = 0.48;
			widget.style.transformOrigin = "top center";
			widget.style.transform = scale < 1 ? `scale(${scale})` : "";

			// El transform no reduce el alto reservado; ajustamos SOLO el alto del contenedor
			// del captcha en login-phone para eliminar el espacio vacío sin afectar el resto.
			if (isPhoneCaptcha) {
				const baseHeight = widget.offsetHeight || 78;
				container.style.height = `${Math.ceil(baseHeight * scale)}px`;
			} else if (container.style.height) {
				container.style.height = "";
			}
		});
	};

	const programarAjusteRecaptcha = () => {
		if (recaptchaAdjustTimer) {
			clearTimeout(recaptchaAdjustTimer);
		}
		recaptchaAdjustTimer = setTimeout(ajustarRecaptcha, 60);
	};

	window.ajustarRecaptcha = ajustarRecaptcha;
	window.programarAjusteRecaptcha = programarAjusteRecaptcha;
})();

document.addEventListener("DOMContentLoaded", () => {
	if (window.__loginPhoneInitialized) {
		return;
	}
	window.__loginPhoneInitialized = true;

	const form = document.getElementById("login-form");
	const nombreInput = document.getElementById("login-nombre");
	const passwordInput = document.getElementById("login-password");
	const csrfTokenInput = document.getElementById("csrf-token");
	const registroStep1 = document.getElementById("registro-step1");
	const registroStep2 = document.getElementById("registro-step2");
	const registroStep1Form = document.getElementById("registro-cliente-step1-form");
	const registroStep2Form = document.getElementById("registro-cliente-step2-form");
	const registroVolverStep1 = document.getElementById("registro-volver-step1");
	const registroOpenBtn = document.querySelector('[data-open-modal="modal-registro-cliente"]');
	const registroUsuarioInput = document.getElementById("registro-usuario");
	const registroCedulaInput = document.getElementById("registro-cedula");
	const registroPasswordInput = document.getElementById("registro-password");
	const registroPasswordConfirmInput = document.getElementById("registro-password-confirm");
	const perfilNombreInput = document.getElementById("perfil-nombre");
	const perfilApellidoInput = document.getElementById("perfil-apellido");
	const perfilCelularInput = document.getElementById("perfil-celular");
	const perfilCorreoInput = document.getElementById("perfil-correo");
	const perfilDireccionInput = document.getElementById("perfil-direccion");
	const feedbackMessage = document.getElementById("feedback-login-message");

	if (!form || !nombreInput || !passwordInput) {
		return;
	}

	const csrfHeaders = () => ({
		"Content-Type": "application/json",
		Accept: "application/json",
		...(csrfTokenInput && csrfTokenInput.value ? { "X-CSRFToken": csrfTokenInput.value } : {}),
	});

	const setRegistroStep = (step) => {
		if (!registroStep1 || !registroStep2) {
			return;
		}
		const showStep1 = step === 1;
		registroStep1.hidden = !showStep1;
		registroStep2.hidden = showStep1;
	};

	const resetRegistro = () => {
		setRegistroStep(1);
		registroStep1Form?.reset();
		registroStep2Form?.reset();
	};

	const abrirPerfilIncompleto = () => {
		setRegistroStep(2);
		if (window.UiModal && typeof window.UiModal.openById === "function") {
			window.UiModal.openById("modal-registro-cliente");
		}
	};

	const mostrarMensaje = (mensaje) => {
		if (feedbackMessage) {
			feedbackMessage.textContent = mensaje;
		}
		if (window.UiModal && typeof window.UiModal.openById === "function") {
			window.UiModal.openById("modal-feedback-login");
			return;
		}
		alert(mensaje);
	};

	form.addEventListener("submit", async (event) => {
		event.preventDefault();

		const recaptchaContainer = form.querySelector(".g-recaptcha");
		const recaptchaResponse = form.querySelector('[name="g-recaptcha-response"]')?.value?.trim() || "";
		if (recaptchaContainer && !recaptchaResponse) {
			mostrarMensaje("Completa el captcha para continuar.");
			return;
		}
		if (!recaptchaContainer) {
			mostrarMensaje("Captcha no configurado. Contacta al administrador.");
			return;
		}

		const payload = {
			nombre: nombreInput.value.trim(),
			password: passwordInput.value,
			recaptcha: recaptchaResponse,
		};

		try {
			const response = await fetch("/api/login", {
				method: "POST",
				headers: csrfHeaders(),
				body: JSON.stringify(payload),
			});

			const data = await response.json().catch(() => ({}));

			if (response.ok && data.success) {
				if (data.require_profile_completion) {
					abrirPerfilIncompleto();
					return;
				}
				window.location.href = "/";
				return;
			}

			mostrarMensaje(data.error || "No se pudo iniciar sesión.");
			if (window.grecaptcha && typeof window.grecaptcha.reset === "function") {
				window.grecaptcha.reset();
			}
		} catch (error) {
			mostrarMensaje("Error de conexión. Intenta nuevamente.");
			if (window.grecaptcha && typeof window.grecaptcha.reset === "function") {
				window.grecaptcha.reset();
			}
		}
	});

	registroOpenBtn?.addEventListener("click", () => {
		resetRegistro();
	});

	registroVolverStep1?.addEventListener("click", () => {
		setRegistroStep(1);
	});

	registroStep1Form?.addEventListener("submit", async (event) => {
		event.preventDefault();

		const password = (registroPasswordInput?.value || "").trim();
		const passwordConfirm = (registroPasswordConfirmInput?.value || "").trim();
		if (!password || password !== passwordConfirm) {
			mostrarMensaje("Las contraseñas no coinciden.");
			return;
		}

		const payload = {
			nombre: (registroUsuarioInput?.value || "").trim(),
			cedula: (registroCedulaInput?.value || "").trim(),
			password,
		};

		try {
			const response = await fetch("/api/registro/cliente/paso-1", {
				method: "POST",
				headers: csrfHeaders(),
				body: JSON.stringify(payload),
			});
			const data = await response.json().catch(() => ({}));

			if (response.ok && data.success) {
				setRegistroStep(2);
				mostrarMensaje("Cuenta creada. Completa ahora tus datos personales.");
				return;
			}

			mostrarMensaje(data.error || "No se pudo crear la cuenta.");
		} catch (error) {
			mostrarMensaje("Error de conexión. Intenta nuevamente.");
		}
	});

	registroStep2Form?.addEventListener("submit", async (event) => {
		event.preventDefault();

		const payload = {
			nombre: (perfilNombreInput?.value || "").trim(),
			apellido: (perfilApellidoInput?.value || "").trim(),
			celular: (perfilCelularInput?.value || "").trim(),
			correo: (perfilCorreoInput?.value || "").trim(),
			direccion: (perfilDireccionInput?.value || "").trim(),
		};

		try {
			const response = await fetch("/api/registro/cliente/paso-2", {
				method: "POST",
				headers: csrfHeaders(),
				body: JSON.stringify(payload),
			});
			const data = await response.json().catch(() => ({}));

			if (response.ok && data.success) {
				window.location.href = "/";
				return;
			}

			mostrarMensaje(data.error || "No se pudo completar el perfil.");
		} catch (error) {
			mostrarMensaje("Error de conexión. Intenta nuevamente.");
		}
	});

	const params = new URLSearchParams(window.location.search);
	if (params.get("completar_perfil") === "1") {
		abrirPerfilIncompleto();
	}

	if (typeof window.programarAjusteRecaptcha === "function") {
		window.programarAjusteRecaptcha();
		window.addEventListener("resize", window.programarAjusteRecaptcha);
		window.addEventListener("orientationchange", window.programarAjusteRecaptcha);
	}
	if (typeof window.ajustarRecaptcha === "function") {
		setTimeout(window.ajustarRecaptcha, 400);
	}
});
