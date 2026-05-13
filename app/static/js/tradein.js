document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("tradein-form");
  const equipoSelect = document.getElementById("tradein-equipo");
  const submitButton = document.getElementById("tradein-submit");
  const csrfTokenInput = document.getElementById("tradein-csrf-token");
  const alertaLiberacion = document.getElementById("tradein-liberacion-alerta");
  const montoEstimado = document.getElementById("tradein-monto");
  const precioBase = document.getElementById("tradein-base");
  const deduccionTotal = document.getElementById("tradein-deduccion");
  const detallesFallas = document.getElementById("tradein-detalles");
  const mensajes = document.getElementById("tradein-mensajes");

  function formatMoney(value) {
    const numero = Number(value);
    if (!Number.isFinite(numero)) {
      return "$0.00";
    }

    return `$${new Intl.NumberFormat("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(numero)}`;
  }

  function getLiberadoValue() {
    const seleccionado = document.querySelector('input[name="liberado"]:checked');
    return seleccionado ? seleccionado.value : "";
  }

  function getFallasSeleccionadas() {
    return Array.from(document.querySelectorAll('input[name="fallas"]:checked')).map((checkbox) => checkbox.value);
  }

  function setLiberacionState() {
    const liberado = getLiberadoValue();
    const bloqueado = liberado === "no";

    if (alertaLiberacion) {
      alertaLiberacion.hidden = !bloqueado;
    }

    if (submitButton) {
      submitButton.disabled = bloqueado;
    }

    return !bloqueado;
  }

  function renderResultado(resultado) {
    if (!resultado) {
      return;
    }

    montoEstimado.textContent = formatMoney(resultado.monto_estimado);
    precioBase.textContent = formatMoney(resultado.precio_base);
    deduccionTotal.textContent = formatMoney(resultado.costo_total_repuestos);

    const detalles = Array.isArray(resultado.detalles_fallas) && resultado.detalles_fallas.length > 0
      ? resultado.detalles_fallas
      : [];

    if (detallesFallas) {
      detallesFallas.innerHTML = detalles.length > 0
        ? detalles.map((detalle) => `<li><span>${detalle.etiqueta}</span><strong>${formatMoney(detalle.costo)}</strong></li>`).join("")
        : "<li>No hay fallas seleccionadas.</li>";
    }

    const advertencias = Array.isArray(resultado.advertencias) ? resultado.advertencias : [];
    if (mensajes) {
      mensajes.innerHTML = advertencias.length > 0
        ? advertencias.map((advertencia) => `<p>${advertencia}</p>`).join("")
        : "Cotización generada correctamente.";
    }
  }

  function renderError(mensaje) {
    if (mensajes) {
      mensajes.innerHTML = `<p class="tradein-result__messages--error">${mensaje}</p>`;
    }
  }

  if (!form || !equipoSelect || !submitButton) {
    return;
  }

  setLiberacionState();

  document.querySelectorAll('input[name="liberado"]').forEach((input) => {
    input.addEventListener("change", setLiberacionState);
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const liberado = getLiberadoValue();
    if (liberado !== "si") {
      setLiberacionState();
      renderError("Lo sentimos, el equipo debe estar liberado para calificar");
      return;
    }

    const idProducto = equipoSelect.value;
    if (!idProducto) {
      renderError("Selecciona un equipo para continuar.");
      return;
    }

    const payload = {
      id_producto: idProducto,
      liberado: liberado,
      fallas: getFallasSeleccionadas(),
    };

    submitButton.disabled = true;
    submitButton.textContent = "Cotizando...";

    try {
      const response = await fetch("/api/trade-in/cotizar", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          ...(csrfTokenInput && csrfTokenInput.value ? { "X-CSRFToken": csrfTokenInput.value } : {}),
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok || !data.success) {
        renderError(data.error || "No se pudo generar la cotización.");
        return;
      }

      renderResultado(data);
    } catch (error) {
      console.error(error);
      renderError("Error de conexión. Intenta nuevamente.");
    } finally {
      submitButton.textContent = "Cotizar";
      setLiberacionState();
    }
  });
});
