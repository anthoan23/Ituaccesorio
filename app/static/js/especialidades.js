window.addEventListener("DOMContentLoaded", () => {
	const counterNodes = document.querySelectorAll("[data-count]");
	const rowNodes = document.querySelectorAll("[data-personal-row]");
	const detailTitle = document.querySelector("[data-personal-detail-title]");
	const detailText = document.querySelector("[data-personal-detail-text]");
	const detailEmail = document.querySelector("[data-personal-detail-email]");
	const detailRole = document.querySelector("[data-personal-detail-role]");
	const detailExtra = document.querySelector("[data-personal-detail-extra]");

	const animateCounter = (node) => {
		const target = Number(node.getAttribute("data-count") || 0);
		const duration = 900;
		const start = performance.now();

		const tick = (now) => {
			const progress = Math.min((now - start) / duration, 1);
			node.textContent = String(Math.round(target * progress));
			if (progress < 1) {
				requestAnimationFrame(tick);
			}
		};

		requestAnimationFrame(tick);
	};

	counterNodes.forEach(animateCounter);

	const setDetails = (row) => {
		if (!row) return;
		rowNodes.forEach((currentRow) => currentRow.classList.toggle("is-selected", currentRow === row));

		if (detailTitle) detailTitle.textContent = row.dataset.detailTitle || "";
		if (detailText) detailText.textContent = row.dataset.detailText || "";
		if (detailEmail) detailEmail.textContent = row.dataset.detailEmail || "";
		if (detailRole) detailRole.textContent = row.dataset.detailRole || "";
		if (detailExtra) detailExtra.textContent = row.dataset.detailExtra || "";
	};

	if (rowNodes.length > 0) {
		setDetails(rowNodes[0]);
	}

	rowNodes.forEach((row) => {
		row.addEventListener("click", () => setDetails(row));
	});
});
