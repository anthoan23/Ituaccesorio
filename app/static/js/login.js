document.addEventListener("DOMContentLoaded", () => {
	const form = document.getElementById("login-form");
	const nombreInput = document.getElementById("login-nombre");
	const passwordInput = document.getElementById("login-password");
	const csrfTokenInput = document.getElementById("csrf-token");

	if (!form || !nombreInput || !passwordInput) {
		return;
	}

	form.addEventListener("submit", async (event) => {
		event.preventDefault();

		const payload = {
			nombre: nombreInput.value.trim(),
			password: passwordInput.value,
		};

		try {
			const response = await fetch("/api/login", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"Accept": "application/json",
					...(csrfTokenInput && csrfTokenInput.value ? { "X-CSRFToken": csrfTokenInput.value } : {}),
				},
				body: JSON.stringify(payload),
			});

			const data = await response.json().catch(() => ({}));

			if (response.ok && data.success) {
				window.location.href = "/";
				return;
			}

			alert(data.error || "No se pudo iniciar sesión.");
		} catch (error) {
			alert("Error de conexión. Intenta nuevamente.");
		}
	});
});
