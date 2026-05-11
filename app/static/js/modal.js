(() => {
    const modalSelector = '[data-modal]';
    const openSelector = '[data-open-modal]';
    const closeSelector = '[data-close-modal]';

    function getModal(id) {
        if (!id) return null;
        return document.getElementById(id);
    }

    function isOpen(modal) {
        return !!modal && !modal.hasAttribute('hidden');
    }

    function syncBodyState() {
        const anyOpen = Array.from(document.querySelectorAll(modalSelector)).some((modal) => isOpen(modal));
        document.body.classList.toggle('ui-modal-open', anyOpen);
    }

    function openById(id) {
        const modal = getModal(id);
        if (!modal) return;
        modal.removeAttribute('hidden');
        modal.setAttribute('aria-hidden', 'false');
        syncBodyState();

        const firstFocusable = modal.querySelector('input, select, textarea, button');
        if (firstFocusable) firstFocusable.focus();
    }

    function closeModal(modal) {
        if (!modal) return;
        modal.setAttribute('hidden', '');
        modal.setAttribute('aria-hidden', 'true');
        syncBodyState();
    }

    function closeById(id) {
        closeModal(getModal(id));
    }

    document.addEventListener('click', (event) => {
        const openBtn = event.target.closest(openSelector);
        if (openBtn) {
            openById(openBtn.getAttribute('data-open-modal'));
            return;
        }

        const closeBtn = event.target.closest(closeSelector);
        if (closeBtn) {
            const modal = closeBtn.closest(modalSelector);
            closeModal(modal);
            return;
        }

        const backdrop = event.target.closest(modalSelector);
        if (backdrop && event.target === backdrop) {
            closeModal(backdrop);
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key !== 'Escape') return;
        const openModal = Array.from(document.querySelectorAll(modalSelector)).find((modal) => isOpen(modal));
        if (openModal) closeModal(openModal);
    });

    window.UiModal = {
        openById,
        closeById,
    };
})();
