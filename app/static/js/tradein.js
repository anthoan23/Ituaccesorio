const tradeinBody = document.getElementById("tradein-body");
const tradeinCount = document.getElementById("tradein-count");

function filaTradein(item) {
  const id = item.ID_Tradein ?? "-";
  const idEmpleado = item.ID_em ?? "-";
  const idCliente = item.ID_c ?? "-";
  const idProducto = item.ID_producto ?? "-";
  const cotizacion = item.Cotizacion ?? "-";
  const fecha = item.Fecha_t ?? "-";

  return `
    <tr>
      <td>${id}</td>
      <td>${idEmpleado}</td>
      <td>${idCliente}</td>
      <td>${idProducto}</td>
      <td>${cotizacion}</td>
      <td>${fecha}</td>
    </tr>
  `;
}

async function cargarTradeins() {
  if (!tradeinBody || !tradeinCount) {
    return;
  }

  try {
    const respuesta = await fetch("/api/trade-in", {
      headers: {
        "Accept": "application/json",
      },
      credentials: "same-origin",
    });

    if (!respuesta.ok) {
      throw new Error("No se pudo consultar el endpoint de trade-in.");
    }

    const data = await respuesta.json();
    const tradeins = Array.isArray(data.tradeins) ? data.tradeins : [];

    tradeinCount.textContent = `${tradeins.length} elementos`;

    if (tradeins.length === 0) {
      tradeinBody.innerHTML = '<tr><td colspan="6" class="tradein-empty">No hay registros para mostrar.</td></tr>';
      return;
    }

    tradeinBody.innerHTML = tradeins.map(filaTradein).join("");
  } catch (error) {
    tradeinBody.innerHTML = '<tr><td colspan="6" class="tradein-empty">Error cargando informacion.</td></tr>';
    tradeinCount.textContent = "0 elementos";
    console.error(error);
  }
}

cargarTradeins();
