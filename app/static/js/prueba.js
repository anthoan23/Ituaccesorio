console.log("Cargando script de prueba.js...");

const listaPruebaBd1 = document.getElementById("lista-prueba-bd1");
const listaPruebaBd2 = document.getElementById("lista-prueba-bd2");
const contadorBd1 = document.getElementById("contador-bd1");
const contadorBd2 = document.getElementById("contador-bd2");
const formCliente = document.querySelector("#form-cliente .data-form");
const formModulo = document.querySelector("#form-modulo .data-form");
const panelCliente = document.getElementById("form-cliente");
const panelModulo = document.getElementById("form-modulo");

const feedback = crearFeedback();
const formEstado = {
    cliente: false,
    modulo: false,
};
const modoEdicion = {
    cliente: null,
    modulo: null,
};

document.querySelectorAll("[data-form-target]").forEach(button => {
    button.addEventListener("click", () => {
        abrirFormulario(button.dataset.formTarget);
    });
});

document.querySelectorAll("[data-form-close]").forEach(button => {
    button.addEventListener("click", () => {
        cerrarFormulario(button.dataset.formClose);
    });
});

if (formCliente) {
    formCliente.addEventListener("submit", event => {
        event.preventDefault();
        const modo = modoEdicion.cliente ? "editar" : "crear";
        const endpoint = modoEdicion.cliente ? `/api/prueba/cliente/${modoEdicion.cliente}` : "/api/prueba/cliente";
        enviarFormulario("cliente", formCliente, endpoint, modo);
    });
}

if (formModulo) {
    formModulo.addEventListener("submit", event => {
        event.preventDefault();
        const modo = modoEdicion.modulo ? "editar" : "crear";
        const endpoint = modoEdicion.modulo ? `/api/prueba/modulo/${modoEdicion.modulo}` : "/api/prueba/modulo";
        enviarFormulario("modulo", formModulo, endpoint, modo);
    });
}

document.querySelectorAll("#lista-prueba-bd1, #lista-prueba-bd2").forEach(lista => {
    lista.addEventListener("click", event => {
        const boton = event.target.closest("button[data-accion]");
        if (!boton) {
            return;
        }

        const registro = obtenerRegistroDesdeBoton(boton);
        const accion = boton.dataset.accion;
        const origen = boton.dataset.origen;

        if (accion === "eliminar") {
            eliminarRegistro(origen, registro);
            return;
        }

        if (accion === "modificar") {
            abrirEdicion(origen, registro);
        }
    });
});

recargarConsulta();

function enviarFormulario(tipo, formulario, endpoint, modo = "crear") {
    const payload = Object.fromEntries(new FormData(formulario).entries());

    fetch(endpoint, {
        method: modo === "editar" ? "PUT" : "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    })
        .then(async response => {
            const data = await response.json().catch(() => ({}));
            return { response, data };
        })
        .then(({ response, data }) => {
            if (!response.ok || !data.success) {
                mostrarMensaje(data.error || `No se pudo ${modo === "editar" ? "actualizar" : "registrar"} ${tipo}.`, "error");
                return;
            }

            formulario.reset();
            if (tipo === "modulo") {
                modoEdicion.modulo = null;
            }

            if (tipo === "cliente") {
                modoEdicion.cliente = null;
            }

            mostrarMensaje(`Se ${modo === "editar" ? "actualizó" : "registró"} ${tipo} correctamente.`, "ok");
            recargarConsulta();
            cerrarFormulario(tipo);
        })
        .catch(error => {
            console.error(`Error enviando ${tipo}:`, error);
            mostrarMensaje(`Error enviando ${tipo}.`, "error");
        });
}

function recargarConsulta() {
    fetch("/api/prueba")
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                mostrarMensaje("No se pudieron cargar los datos.", "error");
                return;
            }

            renderLista(listaPruebaBd1, contadorBd1, data.resultados_bd1 || [], "BD1");
            renderLista(listaPruebaBd2, contadorBd2, data.resultados_bd2 || [], "BD2");
        })
        .catch(error => {
            console.error("Error cargando datos de prueba:", error);
            mostrarMensaje("Error cargando los datos.", "error");
        });
}

function abrirFormulario(tipo) {
    const panel = tipo === "cliente" ? panelCliente : panelModulo;
    if (!panel) {
        return;
    }

    panel.classList.add("is-open");
    panel.setAttribute("aria-hidden", "false");
    panel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function cerrarFormulario(tipo) {
    const panel = tipo === "cliente" ? panelCliente : panelModulo;
    if (!panel) {
        return;
    }

    panel.classList.remove("is-open");
    panel.setAttribute("aria-hidden", "true");

    if (tipo === "cliente") {
        modoEdicion.cliente = null;
    }

    if (tipo === "modulo") {
        modoEdicion.modulo = null;
    }
}

function renderLista(contenedor, contador, registros, etiquetaBd) {
    if (!contenedor) {
        return;
    }

    if (contador) {
        contador.textContent = `${registros.length} registro${registros.length === 1 ? "" : "s"}`;
    }

    if (!Array.isArray(registros) || registros.length === 0) {
        contenedor.innerHTML = `
            <li class="registro-vacio">
                <strong>${etiquetaBd}</strong>
                <span>No hay resultados para mostrar.</span>
            </li>
        `;
        return;
    }

    contenedor.innerHTML = registros
        .map((registro, indice) => renderRegistro(registro, indice + 1))
        .join("");
}

function renderRegistro(registro, numero) {
    const origen = registro && Object.prototype.hasOwnProperty.call(registro, "ID_c") ? "cliente" : "modulo";
    const idRegistro = origen === "cliente" ? registro.ID_c : registro.id;
    const entradas = Object.entries(registro || {});
    const camposVisibles = entradas.filter(([clave]) => !/correo|descripcion/i.test(clave));
    const campos = camposVisibles.length > 0
        ? camposVisibles.map(([clave, valor]) => `
            <div class="campo">
                <span class="campo__label">${escapeHtml(formatearClave(clave))}</span>
                <span class="campo__valor">${escapeHtml(formatearValor(valor))}</span>
            </div>
        `).join("")
        : '<div class="campo"><span class="campo__valor">Sin información disponible</span></div>';

    return `
        <li class="registro-card" data-registro='${escapeHtml(encodeURIComponent(JSON.stringify(registro || {})))}' data-origen="${origen}">
            <div class="registro-card__header">
                <span class="registro-card__badge">#${numero}</span>
                <span class="registro-card__meta">${escapeHtml(resumirRegistro(registro))}</span>
            </div>
            <div class="registro-card__body">
                ${campos}
                <div class="registro-card__actions">
                    <button type="button" class="card-action card-action--primary" data-accion="modificar" data-origen="${origen}" data-id="${escapeHtml(String(idRegistro ?? ""))}">Modificar</button>
                    <button type="button" class="card-action card-action--danger" data-accion="eliminar" data-origen="${origen}" data-id="${escapeHtml(String(idRegistro ?? ""))}">Eliminar</button>
                </div>
            </div>
        </li>
    `;
}

function obtenerRegistroDesdeBoton(boton) {
    const card = boton.closest(".registro-card");
    if (!card) {
        return {};
    }

    const encoded = card.dataset.registro || "{}";
    try {
        return JSON.parse(decodeURIComponent(encoded));
    } catch (error) {
        console.error("No se pudo leer el registro:", error);
        return {};
    }
}

function abrirEdicion(origen, registro) {
    if (origen === "cliente") {
        modoEdicion.cliente = registro.ID_c;
        if (formCliente) {
            if (formCliente.id_cliente) {
                formCliente.id_cliente.value = registro.ID_c || "";
            }
            formCliente.nombre_cliente.value = registro.Nombre_c || "";
            formCliente.apellido_cliente.value = registro.Apellido_c || "";
            formCliente.celular_cliente.value = registro.Celular_c || "";
            formCliente.correo_cliente.value = registro.Correo_c || "";
            formCliente.direccion_cliente.value = registro.Direccion_c || "";
            formCliente.tipo_cliente.value = registro.Tipo_c || "";
        }

        abrirFormulario("cliente");
        mostrarMensaje(`Editando cliente #${registro.ID_c}.`, "ok");
        return;
    }

    modoEdicion.modulo = registro.id;
    if (formModulo) {
        formModulo.nombre_modulo.value = registro.nombre || "";
        formModulo.descripcion_modulo.value = registro.descripcion || "";
    }

    abrirFormulario("modulo");
    mostrarMensaje(`Editando módulo #${registro.id}.`, "ok");
}

function eliminarRegistro(origen, registro) {
    const id = origen === "cliente" ? registro.ID_c : registro.id;
    if (id === undefined || id === null || id === "") {
        mostrarMensaje("No se pudo identificar el registro.", "error");
        return;
    }

    const endpoint = origen === "cliente"
        ? `/api/prueba/cliente/${id}`
        : `/api/prueba/modulo/${id}`;

    fetch(endpoint, { method: "DELETE" })
        .then(async response => {
            const data = await response.json().catch(() => ({}));
            return { response, data };
        })
        .then(({ response, data }) => {
            if (!response.ok || !data.success) {
                mostrarMensaje(data.error || "No se pudo eliminar el registro.", "error");
                return;
            }

            mostrarMensaje("Registro eliminado correctamente.", "ok");
            recargarConsulta();
        })
        .catch(error => {
            console.error("Error eliminando registro:", error);
            mostrarMensaje("Error eliminando el registro.", "error");
        });
}

function resumirRegistro(registro) {
    const entradas = Object.entries(registro || {});
    if (entradas.length === 0) {
        return "Registro vacío";
    }

    const prioritario = entradas.find(([clave]) => /nombre|marca|titulo|usuario/i.test(clave));
    if (prioritario) {
        return `${formatearClave(prioritario[0])}: ${formatearValor(prioritario[1])}`;
    }

    const [clave, valor] = entradas[0];
    return `${formatearClave(clave)}: ${formatearValor(valor)}`;
}

function formatearClave(clave) {
    return String(clave)
        .replaceAll("_", " ")
        .replace(/\b\w/g, letra => letra.toUpperCase());
}

function formatearValor(valor) {
    if (valor === null || valor === undefined || valor === "") {
        return "—";
    }

    return String(valor);
}

function escapeHtml(str) {
    return String(str)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function crearFeedback() {
    const elemento = document.createElement("div");
    elemento.className = "form-feedback";
    document.body.appendChild(elemento);
    return elemento;
}

function mostrarMensaje(texto, tipo) {
    if (!feedback) {
        return;
    }

    feedback.textContent = texto;
    feedback.className = `form-feedback ${tipo}`;

    clearTimeout(formEstado.timer);
    formEstado.timer = setTimeout(() => {
        feedback.className = "form-feedback";
    }, 2500);
}
