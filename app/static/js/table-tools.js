(() => {
  const DEFAULT_PAGE_SIZE = 10;
  const PAGE_SIZES = [10, 25, 50, 100];
  const DEBOUNCE_DELAY = 300;
  const tableStates = new Map();

  function initAllTables() {
    document.querySelectorAll("table.table").forEach((table) => {
      if (table.dataset.tableToolsInitialized === "true") return;
      initTable(table);
    });
  }

  function initTable(table) {
    const tbody = table.tBodies?.[0];
    if (!tbody) return;

    table.dataset.tableToolsInitialized = "true";

    const state = {
      page: 1,
      pageSize: DEFAULT_PAGE_SIZE,
      query: "",
      controls: null,
      observer: null,
      isRefreshing: false,
      debounceTimer: null,
    };

    const controls = buildControls(table);
    attachControls(table, controls.container);
    wireControls(controls, state, table);

    const observer = new MutationObserver(() => {
      if (!state.isRefreshing) {
        refreshTable(table);
      }
    });
    observer.observe(tbody, { childList: true });

    state.controls = controls;
    state.observer = observer;
    tableStates.set(table, state);
    refreshTable(table);
  }

  function buildControls() {
    const container = document.createElement("div");
    container.className = "table-controls";
    container.setAttribute("data-table-controls", "true");

    const searchLabel = document.createElement("label");
    searchLabel.className = "table-controls__search";
    const searchText = document.createElement("span");
    searchText.textContent = "Buscar";
    const searchInput = document.createElement("input");
    searchInput.type = "search";
    searchInput.placeholder = "Buscar en la tabla";
    searchInput.setAttribute("aria-label", "Buscar en la tabla");
    searchInput.className = "table-controls__input";
    searchLabel.append(searchText, searchInput);

    const meta = document.createElement("div");
    meta.className = "table-controls__meta";

    const pager = document.createElement("div");
    pager.className = "table-controls__pager";

    const prevBtn = document.createElement("button");
    prevBtn.type = "button";
    prevBtn.className = "table-controls__btn";
    prevBtn.textContent = "Anterior";

    const info = document.createElement("span");
    info.className = "table-controls__info";
    info.setAttribute("aria-live", "polite");

    const nextBtn = document.createElement("button");
    nextBtn.type = "button";
    nextBtn.className = "table-controls__btn";
    nextBtn.textContent = "Siguiente";

    pager.append(prevBtn, info, nextBtn);

    const sizeLabel = document.createElement("label");
    sizeLabel.className = "table-controls__size";
    const sizeText = document.createElement("span");
    sizeText.textContent = "Filas";
    const sizeSelect = document.createElement("select");
    sizeSelect.className = "table-controls__select";
    PAGE_SIZES.forEach((size) => {
      const option = document.createElement("option");
      option.value = String(size);
      option.textContent = String(size);
      if (size === DEFAULT_PAGE_SIZE) {
        option.selected = true;
      }
      sizeSelect.appendChild(option);
    });
    sizeLabel.append(sizeText, sizeSelect);

    meta.append(pager, sizeLabel);
    container.append(searchLabel, meta);

    return {
      container,
      searchInput,
      prevBtn,
      nextBtn,
      info,
      sizeSelect,
    };
  }

  function attachControls(table, controls) {
    const wrapper = table.closest(".table-wrap");
    if (wrapper?.parentElement) {
      wrapper.parentElement.insertBefore(controls, wrapper);
      return;
    }
    table.parentElement?.insertBefore(controls, table);
  }

  function wireControls(controls, state, table) {
    controls.searchInput.addEventListener("input", (event) => {
      if (state.debounceTimer) clearTimeout(state.debounceTimer);
      
      const newQuery = event.target.value || "";
      const isDeleting = newQuery.length < state.query.length;
      
      if (isDeleting && newQuery.length < 2) {
        // Borrado rápido
        state.query = newQuery;
        state.page = 1;
        requestAnimationFrame(() => refreshTable(table));
      } else {
        state.debounceTimer = setTimeout(() => {
          state.query = newQuery;
          state.page = 1;
          refreshTable(table);
        }, DEBOUNCE_DELAY);
      }
    });

    controls.sizeSelect.addEventListener("change", (event) => {
      const value = Number(event.target.value);
      state.pageSize = Number.isNaN(value) ? DEFAULT_PAGE_SIZE : value;
      state.page = 1;
      refreshTable(table);
    });

    controls.prevBtn.addEventListener("click", () => {
      if (state.page > 1) {
        state.page -= 1;
        refreshTable(table);
      }
    });

    controls.nextBtn.addEventListener("click", () => {
      state.page += 1;
      refreshTable(table);
    });
  }

  function refreshTable(table) {
    const tbody = table.tBodies?.[0];
    if (!tbody) return;

    const state = tableStates.get(table);
    if (!state || state.isRefreshing) return;

    state.isRefreshing = true;

    try {
      const dataRows = getDataRows(tbody);
      const placeholderRows = getPlaceholderRows(tbody);
      const hasDataRows = dataRows.length > 0;

      // Manejar placeholders
      if (!hasDataRows) {
        placeholderRows.forEach((row) => {
          row.hidden = false;
        });
        removeNoResultsRow(tbody);
        updateControls(state, 0, 0, 0);
        state.controls.container.classList.toggle("is-empty", true);
        return;
      }

      placeholderRows.forEach((row) => {
        row.hidden = true;
      });

      const query = state.query.trim().toLowerCase();
      const filteredRows = query
        ? dataRows.filter((row) => row.textContent.toLowerCase().includes(query))
        : dataRows;

      const total = filteredRows.length;
      const totalPages = Math.max(1, Math.ceil(total / state.pageSize));
      
      // Ajustar página actual si es necesario
      if (state.page > totalPages) {
        state.page = totalPages;
      }

      const startIndex = (state.page - 1) * state.pageSize;
      const endIndex = startIndex + state.pageSize;

      // Ocultar todas las filas
      dataRows.forEach((row) => {
        row.hidden = true;
      });

      // Mostrar filas filtradas y paginadas
      if (total > 0) {
        for (let i = startIndex; i < Math.min(endIndex, total); i++) {
          filteredRows[i].hidden = false;
        }
      }

      // MANEJO DE "SIN RESULTADOS" - EVITA LOOPS
      const existingNoResultsRow = tbody.querySelector("tr[data-table-tools-empty='true']");
      
      if (total === 0 && query) {
        // Solo agregar si no existe
        if (!existingNoResultsRow) {
          const row = document.createElement("tr");
          row.dataset.tableToolsEmpty = "true";
          const cell = document.createElement("td");
          cell.className = "table__empty";
          cell.colSpan = getColumnCount(table);
          cell.textContent = "Sin resultados.";
          row.appendChild(cell);
          tbody.appendChild(row);
        }
      } else {
        // Eliminar si existe
        if (existingNoResultsRow) {
          existingNoResultsRow.remove();
        }
      }

      updateControls(state, total, startIndex, endIndex);
      state.controls.container.classList.toggle("is-empty", total === 0 && !query);
      
    } finally {
      state.isRefreshing = false;
    }
  }

  function updateControls(state, total, startIndex, endIndex) {
    const { info, prevBtn, nextBtn } = state.controls;
    const totalPages = Math.max(1, Math.ceil(total / state.pageSize));
    const start = total ? startIndex + 1 : 0;
    const end = total ? Math.min(endIndex, total) : 0;

    info.textContent = total ? `${start}-${end} de ${total}` : "0 resultados";

    if (totalPages > 1) {
      prevBtn.style.display = "";
      nextBtn.style.display = "";
      prevBtn.disabled = state.page <= 1;
      nextBtn.disabled = state.page >= totalPages;
    } else {
      prevBtn.style.display = "none";
      nextBtn.style.display = "none";
    }
  }

  function getDataRows(tbody) {
    return Array.from(tbody.rows).filter((row) => !isPlaceholderRow(row));
  }

  function getPlaceholderRows(tbody) {
    return Array.from(tbody.rows).filter(
      (row) => isPlaceholderRow(row) && row.dataset.tableToolsEmpty !== "true",
    );
  }

  function isPlaceholderRow(row) {
    if (row.dataset.tableToolsEmpty === "true") return true;
    const cells = Array.from(row.cells || []);
    if (cells.length === 1) {
      const cell = cells[0];
      const colSpan = Number(cell.getAttribute("colspan") || 1);
      if (cell.classList.contains("table__empty")) return true;
      if (colSpan > 1) return true;
    }
    return Boolean(row.querySelector("td.table__empty"));
  }

  function removeNoResultsRow(tbody) {
    const row = tbody.querySelector("tr[data-table-tools-empty='true']");
    if (row) row.remove();
  }

  function getColumnCount(table) {
    const headerRow = table.tHead?.rows?.[0];
    if (headerRow) return headerRow.cells.length;
    const firstRow = table.tBodies?.[0]?.rows?.[0];
    if (firstRow) return firstRow.cells.length;
    return 1;
  }

  // Limpiar timers al descargar página
  window.addEventListener('beforeunload', () => {
    for (const [_, state] of tableStates) {
      if (state.debounceTimer) clearTimeout(state.debounceTimer);
      if (state.observer) state.observer.disconnect();
    }
  });

  document.addEventListener("DOMContentLoaded", initAllTables);

  window.TableTools = {
    initAll: initAllTables,
    refreshAll: () => {
      tableStates.forEach((_, table) => refreshTable(table));
    },
  };
})();