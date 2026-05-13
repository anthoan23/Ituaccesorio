document.addEventListener("DOMContentLoaded", () => {
	const viewButtons = Array.from(document.querySelectorAll("[data-view-target]"));
	const viewPanels = Array.from(document.querySelectorAll(".content.vista-1, .content.vista-2, .content.vista-3, .content.vista-4"));

	if (!viewButtons.length || !viewPanels.length) {
		return;
	}

	const activateView = (targetClass) => {
		viewPanels.forEach((panel) => {
			panel.hidden = !panel.classList.contains(targetClass);
		});

		viewButtons.forEach((button) => {
			const isActive = button.dataset.viewTarget === targetClass;
			button.classList.toggle("is-active", isActive);
			button.setAttribute("aria-pressed", String(isActive));
		});
	};

	viewButtons.forEach((button) => {
		button.addEventListener("click", () => {
			activateView(button.dataset.viewTarget);
		});
	});

	activateView("vista-1");
});
