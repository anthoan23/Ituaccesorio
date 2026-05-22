document.addEventListener('DOMContentLoaded', () => {
	const sections = Array.from(document.querySelectorAll('.content'));
	const viewButtons = Array.from(document.querySelectorAll('[data-view-target]'));
	const breadcrumbSection = document.getElementById('breadcrumb-section');
	const titles = {
		'vista-1': 'Órdenes pendientes',
		'vista-2': 'Órdenes entregadas',
	};

	const activateView = (viewId) => {
		sections.forEach((section) => {
			section.hidden = section.classList.contains(viewId) ? false : section.classList.contains('content');
		});

		viewButtons.forEach((button) => {
			button.classList.toggle('is-active', button.dataset.viewTarget === viewId);
		});

		if (breadcrumbSection) {
			breadcrumbSection.textContent = titles[viewId] || '';
		}

		window.location.hash = viewId;
	};

	viewButtons.forEach((button) => {
		button.addEventListener('click', () => activateView(button.dataset.viewTarget));
	});

	const initialView = window.location.hash.replace('#', '') || 'vista-1';
	activateView(titles[initialView] ? initialView : 'vista-1');

	if (tablaOrdenesPendientes && !tablaOrdenesPendientes.children.length) {
		tablaOrdenesPendientes.innerHTML = '<tr><td colspan="5" class="table__empty">No hay órdenes de compra pendientes.</td></tr>';
	}

	if (tablaOrdenesEntregadas && !tablaOrdenesEntregadas.children.length) {
		tablaOrdenesEntregadas.innerHTML = '<tr><td colspan="5" class="table__empty">No hay órdenes de compra entregadas.</td></tr>';
	}

	if (formRecepcionArticulos) {
		formRecepcionArticulos.addEventListener('submit', (event) => {
			event.preventDefault();
		});
	}
});
