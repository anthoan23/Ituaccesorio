(() => {
  "use strict";

  const CATEGORIES_STORAGE_KEY = "ituaccesorio_categorias";

  function loadCategories() {
    try {
      const raw = localStorage.getItem(CATEGORIES_STORAGE_KEY);
      if (!raw) return [];
      const parsed = JSON.parse(raw);
      if (!Array.isArray(parsed)) return [];
      return parsed
        .map((value) => String(value).trim())
        .filter((value) => value.length > 0);
    } catch {
      return [];
    }
  }

  function saveCategories(categories) {
    localStorage.setItem(CATEGORIES_STORAGE_KEY, JSON.stringify(categories));
  }

  function normalizeForCompare(value) {
    return String(value).trim().toLowerCase();
  }

  function renderCategorySelects(categories) {
    const selects = document.querySelectorAll("select[data-categories-select='true']");
    selects.forEach((select) => {
      const firstOption = select.querySelector("option")?.cloneNode(true);
      select.innerHTML = "";
      if (firstOption) select.appendChild(firstOption);

      categories.forEach((category) => {
        const option = document.createElement("option");
        option.value = category;
        option.textContent = category;
        select.appendChild(option);
      });
    });
  }

  function addCategoryByName(name) {
    const trimmed = String(name ?? "").trim();
    if (!trimmed) return false;

    const categories = loadCategories();
    const exists = categories.some((c) => normalizeForCompare(c) === normalizeForCompare(trimmed));
    if (exists) {
      renderCategorySelects(categories);
      return true;
    }

    const updated = [...categories, trimmed];
    saveCategories(updated);
    renderCategorySelects(updated);
    return true;
  }

  /**
   * Intenta extraer una tasa numérica (USD -> Bs) desde distintas formas comunes de JSON.
   * Esto nos permite soportar respuestas de APIs no oficiales que varían el formato.
   */
  function extractRate(payload) {
    if (!payload) return null;

    const candidates = [];

    // Formatos típicos: { price: 123.45 }
    candidates.push(payload.price);

    // DolarApi (VE): { promedio: 499.8608 }
    candidates.push(payload.promedio);

    // { bcv: { price: 123.45 } } o { monitors: { bcv: { price: 123.45 } } }
    candidates.push(payload?.bcv?.price);
    candidates.push(payload?.monitors?.bcv?.price);

    // Algunos devuelven: { monitors: { bcv: { value: 123.45 } } }
    candidates.push(payload?.bcv?.value);
    candidates.push(payload?.monitors?.bcv?.value);

    // Otros: { data: { bcv: { price: 123.45 } } }
    candidates.push(payload?.data?.bcv?.price);
    candidates.push(payload?.data?.monitors?.bcv?.price);

    // Si viene como array, intentar primer elemento
    if (Array.isArray(payload) && payload.length > 0) {
      candidates.push(payload[0]?.price);
      candidates.push(payload[0]?.bcv?.price);
      candidates.push(payload[0]?.monitors?.bcv?.price);

      // DolarApi (VE): lista de cotizaciones
      const oficialUsd = payload.find(
        (item) =>
          item &&
          String(item.moneda).toUpperCase() === "USD" &&
          String(item.fuente).toLowerCase() === "oficial",
      );
      candidates.push(oficialUsd?.promedio);
    }

    for (const value of candidates) {
      const number = typeof value === "string" ? Number(value.replace(",", ".")) : Number(value);
      if (Number.isFinite(number) && number > 0) return number;
    }

    return null;
  }

  async function fetchBcvUsdToVesRate() {
    // API pública (fuente oficial / BCV) con CORS:
    // Base URL documentada: https://ve.dolarapi.com
    // Usamos el endpoint de dólar oficial.
    const endpoints = [
      "https://ve.dolarapi.com/v1/dolares/oficial",
      "https://ve.dolarapi.com/v1/cotizaciones",
      "https://ve.dolarapi.com/v1/dolares",
    ];

    for (const url of endpoints) {
      try {
        const response = await fetch(url, { cache: "no-store" });
        if (!response.ok) continue;
        const json = await response.json();
        const rate = extractRate(json);
        if (rate) return rate;
      } catch {
        // Intentar siguiente endpoint
      }
    }

    return null;
  }

  function formatMoney(value) {
    if (!Number.isFinite(value)) return "";
    return value.toFixed(2);
  }

  function setBodyScrollLocked() {
    const anyModalOpen = document.querySelector(".modal:not(.is-hidden)");
    document.body.style.overflow = anyModalOpen ? "hidden" : "";
  }

  document.addEventListener("DOMContentLoaded", async () => {
    const toggleButton = document.getElementById("btn-registrar-producto");
    const modal = document.getElementById("modal-registro-producto");
    const cancelButton = document.getElementById("btn-cancelar-producto");

    const categoryModal = document.getElementById("modal-categoria");
    const categoryForm = document.getElementById("form-categoria");
    const categoryNameInput = document.getElementById("categoria-nombre");
    const categoryCancelButton = document.getElementById("btn-cancelar-categoria");

    const addCategoryButton = document.getElementById("btn-agregar-categoria");
    const addCategoryModalButton = document.getElementById("btn-agregar-categoria-modal");

    const usdInput = document.getElementById("precio-usd");
    const bsInput = document.getElementById("precio-bs");

    // Categorías (sin precargar): se renderizan desde localStorage.
    const initialCategories = loadCategories();
    renderCategorySelects(initialCategories);

    const openProductModal = () => {
      if (!modal) return;
      modal.classList.remove("is-hidden");
      modal.setAttribute("aria-hidden", "false");
      if (toggleButton) toggleButton.setAttribute("aria-expanded", "true");
      setBodyScrollLocked();

      const firstInput = modal.querySelector("input, select, textarea");
      if (firstInput) firstInput.focus({ preventScroll: true });
    };

    const closeProductModal = () => {
      if (!modal) return;
      modal.classList.add("is-hidden");
      modal.setAttribute("aria-hidden", "true");
      if (toggleButton) toggleButton.setAttribute("aria-expanded", "false");
      setBodyScrollLocked();
      if (toggleButton) toggleButton.focus({ preventScroll: true });
    };

    const openCategoryModal = () => {
      if (!categoryModal) return;
      categoryModal.classList.remove("is-hidden");
      categoryModal.setAttribute("aria-hidden", "false");
      setBodyScrollLocked();
      if (categoryNameInput) {
        categoryNameInput.value = "";
        categoryNameInput.focus({ preventScroll: true });
      }
    };

    const closeCategoryModal = () => {
      if (!categoryModal) return;
      categoryModal.classList.add("is-hidden");
      categoryModal.setAttribute("aria-hidden", "true");
      setBodyScrollLocked();
    };

    // Siempre iniciar cerrado (evita que se “quede abierto” por cache/estilos).
    closeProductModal();
    closeCategoryModal();

    // Si el usuario llega con un hash viejo, lo limpiamos para que no “parezca” navegación.
    if (window.location.hash === "#registro-producto" || window.location.hash === "#modal-registro-producto") {
      history.replaceState(null, "", window.location.pathname + window.location.search);
    }

    if (toggleButton && modal) {
      toggleButton.addEventListener("click", openProductModal);
    }

    if (cancelButton) {
      cancelButton.addEventListener("click", closeProductModal);
    }

    if (addCategoryButton) {
      addCategoryButton.addEventListener("click", openCategoryModal);
    }

    if (addCategoryModalButton) {
      addCategoryModalButton.addEventListener("click", openCategoryModal);
    }

    if (categoryCancelButton) {
      categoryCancelButton.addEventListener("click", closeCategoryModal);
    }

    if (categoryForm) {
      categoryForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const ok = addCategoryByName(categoryNameInput?.value);
        if (ok) {
          closeCategoryModal();
        } else if (categoryNameInput) {
          categoryNameInput.focus({ preventScroll: true });
        }
      });
    }

    // Cerrar al hacer click fuera (backdrop)
    [modal, categoryModal].forEach((m) => {
      if (!m) return;
      m.addEventListener("click", (event) => {
        const target = event.target;
        if (target && target instanceof HTMLElement && target.dataset.modalClose === "true") {
          if (m === modal) closeProductModal();
          if (m === categoryModal) closeCategoryModal();
        }
      });
    });

    // Cerrar con Escape (prioriza categoría si está abierta)
    document.addEventListener("keydown", (event) => {
      if (event.key !== "Escape") return;
      if (categoryModal && !categoryModal.classList.contains("is-hidden")) {
        closeCategoryModal();
        return;
      }
      if (modal && !modal.classList.contains("is-hidden")) {
        closeProductModal();
      }
    });

    // Conversión USD -> Bs usando BCV
    let bcvRate = null;
    if (usdInput && bsInput) {
      bsInput.placeholder = "Cargando...";
      bcvRate = await fetchBcvUsdToVesRate();

      const recalc = () => {
        const usdValue = Number(usdInput.value);
        if (!Number.isFinite(usdValue) || usdValue < 0) {
          bsInput.value = "";
          return;
        }
        if (!Number.isFinite(bcvRate) || bcvRate <= 0) {
          bsInput.value = "";
          return;
        }
        bsInput.value = formatMoney(usdValue * bcvRate);
      };

      usdInput.addEventListener("input", recalc);
      usdInput.addEventListener("change", recalc);

      // Si ya hay un valor, recalcular al cargar
      recalc();

      // Si no pudimos obtener tasa, dejar el campo vacío (igual el usuario ve USD).
      if (!bcvRate) {
        bsInput.placeholder = "No disponible";
      }
    }
  });
})();
