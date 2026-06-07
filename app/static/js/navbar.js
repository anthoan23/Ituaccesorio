document.addEventListener("DOMContentLoaded", () => {
	// ==================== CONTROL DEL MENÚ HAMBURGUESA ====================
	
	const menuToggle = document.getElementById('menu-toggle-btn');
	const backdrop = document.getElementById('menu-backdrop');
	const drawer = document.getElementById('main-drawer');
	
	function openMenu() {
		if (drawer) drawer.style.transform = 'translateX(0)';
		if (backdrop) {
			backdrop.style.opacity = '1';
			backdrop.style.pointerEvents = 'auto';
		}
		document.body.style.overflow = 'hidden';
	}
	
	function closeMenu() {
		if (drawer) drawer.style.transform = '';
		if (backdrop) {
			backdrop.style.opacity = '';
			backdrop.style.pointerEvents = '';
		}
		document.body.style.overflow = '';
	}
	
	function toggleMenu() {
		if (drawer && drawer.style.transform === 'translateX(0px)') {
			closeMenu();
		} else {
			openMenu();
		}
	}
	
	if (menuToggle) {
		menuToggle.addEventListener('click', toggleMenu);
	}
	
	if (backdrop) {
		backdrop.addEventListener('click', closeMenu);
	}
	
	// Cerrar menú SOLO al hacer click en enlaces de navegación (no en botones de grupo)
	const drawerLinks = document.querySelectorAll('.drawer__link:not(.drawer__group-toggle)');
	drawerLinks.forEach(link => {
		link.addEventListener('click', closeMenu);
	});
	
	// ==================== TOGGLES DE SUBMENÚ ====================
	
	const groupToggles = document.querySelectorAll("[data-nav-group-toggle]");
	groupToggles.forEach((toggle) => {
		const groupId = toggle.getAttribute("data-nav-group-toggle");
		const group = document.querySelector(`[data-nav-group="${groupId}"]`);
		if (!group) return;

		const sync = (expanded) => {
			toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
			group.toggleAttribute("hidden", !expanded);
		};

		sync(toggle.getAttribute("aria-expanded") === "true");
		toggle.addEventListener("click", (e) => {
			// Prevenir que el evento se propague y cierre el menú
			e.stopPropagation();
			sync(group.hasAttribute("hidden"));
		});
	});
	
	// ==================== PERMISOS EN EL NAVBAR ====================
	
	let permisosUsuario = {};
	
	async function cargarPermisosNavbar() {
		try {
			const response = await fetch('/api/usuarios/mis-permisos', {
				headers: {
					'Accept': 'application/json',
					'X-CSRFToken': document.querySelector('input[name="_csrf_token"]')?.value || ''
				},
				credentials: 'same-origin'
			});
			
			if (response.ok) {
				const data = await response.json();
				permisosUsuario = data.permisos || {};
				aplicarPermisosNavbar();
			}
		} catch (error) {
			console.error('Error cargando permisos:', error);
		}
	}
	
	function tienePermisoNavbar(modulo, permiso = 'consultar') {
		const userRole = document.querySelector('.user__role')?.textContent?.toLowerCase() || '';
		if (userRole === 'admin') return true;
		
		const permisosModulo = permisosUsuario[modulo];
		if (!permisosModulo) return false;
		
		return permisosModulo[permiso] === true || permisosModulo[permiso] === 1;
	}
	
	function aplicarPermisosNavbar() {
		const navLinks = document.querySelectorAll('[data-permiso]');
		
		navLinks.forEach(link => {
			const modulo = link.dataset.modulo;
			const permiso = link.dataset.permiso || 'consultar';
			
			if (modulo && !tienePermisoNavbar(modulo, permiso)) {
				link.style.display = 'none';
				
				const parentSubmenu = link.closest('.drawer__submenu');
				if (parentSubmenu) {
					const parentGroup = parentSubmenu.closest('[data-nav-group]');
					if (parentGroup) {
						const visibleLinks = parentGroup.querySelectorAll('.drawer__submenu-link:not([style*="display: none"])');
						if (visibleLinks.length === 0) {
							const groupToggle = document.querySelector(`[data-nav-group-toggle="${parentGroup.id}"]`);
							if (groupToggle) groupToggle.style.display = 'none';
							parentGroup.style.display = 'none';
						}
					}
				}
			}
		});
		
		const tienePermisosAdmin = tienePermisoNavbar('Usuarios') || tienePermisoNavbar('Bitácora');
		const adminSection = document.getElementById('admin-section');
		if (adminSection) {
			adminSection.style.display = tienePermisosAdmin ? 'block' : 'none';
		}
	}
	
	cargarPermisosNavbar();
	
	// ==================== SCROLL EN NAV ====================
	
	const navContainer = document.getElementById('drawerNav');
	const scrollUpBtn = document.querySelector('.nav-scroll-up');
	const scrollDownBtn = document.querySelector('.nav-scroll-down');
	
	function updateScrollButtons() {
		if (!navContainer) return;
		const canScrollUp = navContainer.scrollTop > 20;
		const canScrollDown = navContainer.scrollHeight - navContainer.scrollTop - navContainer.clientHeight > 20;
		
		if (scrollUpBtn) scrollUpBtn.style.opacity = canScrollUp ? '1' : '0.3';
		if (scrollDownBtn) scrollDownBtn.style.opacity = canScrollDown ? '1' : '0.3';
	}
	
	if (scrollUpBtn) {
		scrollUpBtn.addEventListener('click', () => {
			navContainer.scrollBy({ top: -80, behavior: 'smooth' });
		});
	}
	
	if (scrollDownBtn) {
		scrollDownBtn.addEventListener('click', () => {
			navContainer.scrollBy({ top: 80, behavior: 'smooth' });
		});
	}
	
	if (navContainer) {
		navContainer.addEventListener('scroll', updateScrollButtons);
		setTimeout(updateScrollButtons, 100);
	}
	
	// ==================== PERFIL DE USUARIO ====================
	
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

	// Función para inicializar validadores en el modal
	const initModalValidators = () => {
		if (window.FieldValidator && window.FieldValidator.initModalFields) {
			const modal = document.getElementById('modal-mi-perfil');
			if (modal && modal.style.display !== 'none') {
				window.FieldValidator.initModalFields(modal);
			}
		}
		
		// También asegurar que los campos existentes tengan validación
		const modalFields = document.querySelectorAll('#modal-mi-perfil input, #modal-mi-perfil select, #modal-mi-perfil textarea');
		modalFields.forEach(field => {
			if (!field.closest('.field-validator-wrapper') && field.id !== 'mi-perfil-cedula' && field.id !== 'mi-perfil-rol') {
				if (window.FieldValidator && window.FieldValidator.FieldValidator) {
					try {
						new window.FieldValidator.FieldValidator(field, {
							liveValidation: true,
							required: { enabled: field.hasAttribute('required') }
						});
					} catch(e) {
						console.warn('Error initializing validator:', e);
					}
				}
			}
		});
	};

	document.querySelector('[data-open-modal="modal-mi-perfil"]')?.addEventListener("click", async () => {
		try {
			const usuario = await loadProfile();
			syncForm(usuario);
			
			// Inicializar validadores después de que el modal se abra
			setTimeout(() => {
				initModalValidators();
			}, 100);
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