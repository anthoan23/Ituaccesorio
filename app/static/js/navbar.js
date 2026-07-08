document.addEventListener("DOMContentLoaded", () => {
	// ==================== MODO CLARO / OSCURO ====================

	const themeToggleBtn = document.querySelector('[data-theme-toggle]');

	function getStoredTheme() {
		try {
			return localStorage.getItem('theme');
		} catch (e) {
			return null;
		}
	}

	function setStoredTheme(theme) {
		try {
			localStorage.setItem('theme', theme);
		} catch (e) {
			/* almacenamiento no disponible, seguimos sin persistir */
		}
	}

	function applyTheme(theme) {
		document.documentElement.setAttribute('data-theme', theme);
		if (themeToggleBtn) {
			themeToggleBtn.setAttribute(
				'aria-label',
				theme === 'light' ? 'Cambiar a modo oscuro' : 'Cambiar a modo claro'
			);
		}
	}

	// El <head> ya aplicó el tema guardado antes del primer paint;
	// aquí solo sincronizamos el aria-label y dejamos listo el click.
	applyTheme(document.documentElement.getAttribute('data-theme') || getStoredTheme() || 'dark');

	if (themeToggleBtn) {
		themeToggleBtn.addEventListener('click', () => {
			const current = document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
			const next = current === 'light' ? 'dark' : 'light';
			applyTheme(next);
			setStoredTheme(next);
		});
	}

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

	// ==================== CARRITO DE COMPRAS ====================

	function getAuthToken() {
		try {
			return localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || '';
		} catch (e) {
			return '';
		}
	}

	function getCsrfToken() {
		return document.querySelector("input[name='_csrf_token']")?.value || '';
	}

	async function fetchCarritoBackend(url, options = {}) {
		const headers = {
			Accept: 'application/json',
			...(getCsrfToken() ? { 'X-CSRFToken': getCsrfToken() } : {}),
			...(getAuthToken() ? { Authorization: `Bearer ${getAuthToken()}` } : {}),
		};

		if (options.body && !(options.body instanceof FormData)) {
			headers['Content-Type'] = 'application/json';
		}

		const response = await fetch(url, {
			method: options.method || 'GET',
			headers,
			credentials: 'same-origin',
			body: options.body,
		});

		const data = await response.json().catch(() => ({}));

		if (!response.ok || data.success === false) {
			throw new Error(data.error || `Error ${response.status}`);
		}

		return data;
	}

	const cartToggle = document.querySelector('[data-cart-toggle]');
	const cartPanel = document.querySelector('[data-cart-panel]');
	const cartBadge = document.querySelector('[data-cart-badge]');
	const cartList = document.querySelector('[data-cart-list]');
	const cartCount = document.querySelector('[data-cart-count]');
	const cartTotal = document.querySelector('[data-cart-total]');
	const cartCheckout = document.querySelector('[data-cart-checkout]');

	// Estado del carrito (simulado)
	let cartItems = [];

	function normalizeCartItem(item) {
		const id = item.producto_id || item.ID_inventario || item.id || item.inventario_id;
		const quantity = Number(item.cantidad || item.Cantidad_producto || item.quantity || 0);
		const price = Number(item.precio_usd || item.Costo_venta || item.price || item.precio || 0);
		const name = item.nombre || item.Nombre_producto || item.name || 'Producto';
		const image = item.imagen || item.Foto_inventario || item.image || null;

		return {
			id: String(id ?? ''),
			name,
			price,
			quantity,
			image,
		};
	}

	// Cargar carrito desde el backend para reflejar el estado real del usuario
	async function loadCart() {
		try {
			const data = await fetchCarritoBackend('/api/carrito');
			const items = Array.isArray(data.items) ? data.items : [];
			cartItems = items.map(normalizeCartItem).filter((item) => item.id);
		} catch (e) {
			try {
				const saved = localStorage.getItem('cart_items');
				cartItems = saved ? JSON.parse(saved) : [];
			} catch (error) {
				cartItems = [];
			}
		}
		updateCartUI();
	}

	async function saveCart() {
		try {
			localStorage.setItem('cart_items', JSON.stringify(cartItems));
		} catch (e) {
			// Ignorar almacenamiento local si no está disponible
		}

		updateCartUI();
	}

	async function syncCartItemToBackend(itemId, quantity) {
		if (!itemId) return;

		if (quantity <= 0) {
			await fetchCarritoBackend(`/api/carrito/${itemId}`, {
				method: 'DELETE',
			});
			return;
		}

		await fetchCarritoBackend('/api/carrito', {
			method: 'PUT',
			body: JSON.stringify({
				producto_id: itemId,
				cantidad: quantity,
			}),
		});
	}

	// Actualizar UI del carrito
	function updateCartUI() {
		const totalItems = cartItems.reduce((sum, item) => sum + item.quantity, 0);
		const totalPrice = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);

		// Badge
		if (totalItems > 0) {
			cartBadge.textContent = totalItems > 99 ? '99+' : totalItems;
			cartBadge.removeAttribute('hidden');
		} else {
			cartBadge.setAttribute('hidden', '');
		}

		// Count
		if (cartCount) {
			cartCount.textContent = `${totalItems} producto${totalItems !== 1 ? 's' : ''}`;
		}

		// Total
		if (cartTotal) {
			cartTotal.textContent = `Bs. ${totalPrice.toLocaleString('es-VE')}`;
		}

		// Checkout button
		if (cartCheckout) {
			cartCheckout.disabled = totalItems === 0;
		}

		// Lista de productos
		renderCartItems();
	}

	// Renderizar items del carrito
	function renderCartItems() {
		if (!cartList) return;

		if (cartItems.length === 0) {
			cartList.innerHTML = `
				<div class="cart-panel__empty">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
						<circle cx="9" cy="21" r="1"/>
						<circle cx="20" cy="21" r="1"/>
						<path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
					</svg>
					<p>Tu carrito está vacío</p>
				</div>
			`;
			return;
		}

		cartList.innerHTML = cartItems.map((item, index) => `
			<div class="cart-item" data-cart-index="${index}">
				<div class="cart-item__image">
					${item.image ? `<img src="${item.image}" alt="${item.name}">` : 
					`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
						<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
						<path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
					</svg>`}
				</div>
				<div class="cart-item__info">
					<div class="cart-item__name">${escapeHtml(item.name)}</div>
					<div class="cart-item__detail">
						<span class="cart-item__quantity">
							<button type="button" data-cart-action="decrease" data-index="${index}">-</button>
							<span>${item.quantity}</span>
							<button type="button" data-cart-action="increase" data-index="${index}">+</button>
						</span>
						<span>× Bs. ${item.price.toLocaleString('es-VE')}</span>
					</div>
				</div>
				<div class="cart-item__price">Bs. ${(item.price * item.quantity).toLocaleString('es-VE')}</div>
				<button class="cart-item__remove" type="button" data-cart-action="remove" data-index="${index}" aria-label="Eliminar producto">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<line x1="18" y1="6" x2="6" y2="18"/>
						<line x1="6" y1="6" x2="18" y2="18"/>
					</svg>
				</button>
			</div>
		`).join('');
	}

	// Función auxiliar para escapar HTML
	function escapeHtml(str) {
		if (!str) return '';
		return String(str)
			.replace(/&/g, '&amp;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;')
			.replace(/"/g, '&quot;')
			.replace(/'/g, '&#39;');
	}

	// Toggle del panel del carrito
	cartToggle?.addEventListener('click', (e) => {
		e.stopPropagation();
		const isHidden = cartPanel.hasAttribute('hidden');
		if (isHidden) {
			cartPanel.removeAttribute('hidden');
			loadCart(); // Recargar al abrir
		} else {
			cartPanel.setAttribute('hidden', '');
		}
	});

	// Cerrar panel al hacer click fuera
	document.addEventListener('click', (e) => {
		const isClickInside = cartToggle?.contains(e.target) || cartPanel?.contains(e.target);
		if (!isClickInside && cartPanel && !cartPanel.hasAttribute('hidden')) {
			cartPanel.setAttribute('hidden', '');
		}
	});

	// Eventos de acciones del carrito (delegación)
	cartList?.addEventListener('click', async (e) => {
		e.preventDefault();
		e.stopPropagation();

		const btn = e.target.closest('[data-cart-action]');
		if (!btn) return;

		const action = btn.dataset.cartAction;
		const index = parseInt(btn.dataset.index);

		if (isNaN(index) || index < 0 || index >= cartItems.length) return;

		const itemId = cartItems[index]?.id;
		let nextQuantity = cartItems[index].quantity;

		if (action === 'increase') {
			nextQuantity += 1;
		} else if (action === 'decrease') {
			if (nextQuantity > 1) {
				nextQuantity -= 1;
			} else {
				cartItems.splice(index, 1);
				nextQuantity = 0;
			}
		} else if (action === 'remove') {
			cartItems.splice(index, 1);
			nextQuantity = 0;
		}

		try {
			if (nextQuantity > 0 && cartItems[index]) {
				cartItems[index].quantity = nextQuantity;
			}
			saveCart();
			await syncCartItemToBackend(itemId, nextQuantity);
			await loadCart();
			cartPanel?.removeAttribute('hidden');
		} catch (error) {
			console.error('Error actualizando carrito:', error);
			await loadCart();
			cartPanel?.removeAttribute('hidden');
		}
	});

	// Botón "Ir a pagar"
	cartCheckout?.addEventListener('click', () => {
		if (cartItems.length === 0) return;
		window.location.href = '/pagar';
	});

	// Función para agregar producto al carrito (pública)
	window.addToCart = function(product) {
		const existing = cartItems.find(item => String(item.id) === String(product.id));
		if (existing) {
			existing.quantity += product.quantity || 1;
		} else {
			cartItems.push({
				id: String(product.id),
				name: product.name,
				price: Number(product.price || 0),
				quantity: product.quantity || 1,
				image: product.image || null
			});
		}
		saveCart();

		// Abrir panel del carrito sin cerrarlo automáticamente
		cartPanel.removeAttribute('hidden');
	};

	// Función para obtener el total de items en el carrito
	window.getCartTotal = function() {
		return cartItems.reduce((sum, item) => sum + item.quantity, 0);
	};

	// Función para obtener el carrito completo
	window.getCartItems = function() {
		return [...cartItems];
	};

	// Función para vaciar el carrito
	window.clearCart = function() {
		cartItems = [];
		saveCart();
	};

	// Inicializar carrito
	loadCart();
});