// ============================================
// VALIDACIÓN ANTI-MANIPULACIÓN DE TABLAS
// ============================================
// Copia en memoria de las filas renderizadas: es la referencia
// confiable contra la que se compara el DOM al usar los botones
// de acción, para detectar ids alterados desde el inspector.
(function () {
  'use strict';

  function mostrarErrorValidacion(titulo, mensaje) {
    if (window.FeedbackModal && typeof window.FeedbackModal.show === 'function') {
      window.FeedbackModal.show({
        type: 'error',
        title: titulo,
        message: mensaje
      });
    }
    console.error(mensaje);
  }

  function normalizarId(id) {
    if (id === undefined || id === null) return null;
    const texto = String(id).trim();
    return texto === '' ? null : texto;
  }

  function crearValidadorTabla(opciones = {}) {
    const tituloEntidad = opciones.tituloEntidad || 'El registro';
    const campoId = opciones.campoId || 'data-id';
    const filasSnapshot = new WeakMap();
    const idsEnMemoria = new Set();

    // Registra las filas visibles de la tabla: copia en memoria del id
    // de la fila y del texto visible de la primera columna.
    function registrarFilas(tbody) {
      idsEnMemoria.clear();
      tbody.querySelectorAll(`tr[${campoId}]`).forEach(fila => {
        const id = normalizarId(fila.getAttribute(campoId));
        const celdaId = fila.querySelector('td');
        filasSnapshot.set(fila, {
          id: id ?? '',
          texto: celdaId ? celdaId.textContent.trim() : null
        });
        if (id) idsEnMemoria.add(id);
      });
    }

    // Compara la fila del botón contra la copia en memoria.
    // Devuelve el id confiable de la fila, o null si fue manipulada.
    function validarFila(boton, accion) {
      const fila = boton.closest(`tr[${campoId}]`);
      const snapshot = fila ? filasSnapshot.get(fila) : null;

      if (!fila || !snapshot) {
        mostrarErrorValidacion(
          'Fila inválida',
          `La fila del botón no corresponde a un registro de la tabla. No se puede ${accion}.`
        );
        return null;
      }

      const celdaId = fila.querySelector('td');
      const idActual = normalizarId(fila.getAttribute(campoId)) ?? '';
      const textoActual = celdaId ? celdaId.textContent.trim() : null;

      if (idActual !== String(snapshot.id).trim() || textoActual !== snapshot.texto) {
        mostrarErrorValidacion(
          'Fila modificada',
          `La fila ha sido modificada y no coincide con el registro de la tabla. No se puede ${accion}.`
        );
        return null;
      }

      return snapshot.id;
    }

    // Valida la coincidencia del id de la petición con el id confiable.
    function validarCoincidencia(id, idConfiable, accion) {
      const idNormalizado = normalizarId(id);

      if (!idNormalizado) {
        mostrarErrorValidacion(
          'Id inválido',
          `No se recibió un id válido. No se puede ${accion}.`
        );
        return false;
      }

      if (normalizarId(idConfiable) !== idNormalizado) {
        mostrarErrorValidacion(
          'Id inconsistente',
          `El id "${idNormalizado}" de la petición no coincide con el id que aparece en la tabla. No se puede ${accion}.`
        );
        return false;
      }

      return true;
    }

    // Valida el id que viaja en la petición contra la copia en memoria:
    // 1) debe existir en la tabla y 2) debe coincidir con el id confiable.
    function validarId(id, accion, idConfiable = null) {
      const idNormalizado = normalizarId(id);

      if (!idNormalizado) {
        mostrarErrorValidacion(
          'Id inválido',
          `No se recibió un id válido. No se puede ${accion}.`
        );
        return false;
      }

      if (!idsEnMemoria.has(idNormalizado)) {
        mostrarErrorValidacion(
          `${tituloEntidad} no encontrado`,
          `${tituloEntidad} con el id "${idNormalizado}" no existe en la tabla. No se puede ${accion}.`
        );
        return false;
      }

      return validarCoincidencia(id, idConfiable, accion);
    }

    return {
      registrarFilas,
      validarFila,
      validarId,
      validarCoincidencia
    };
  }

  window.ValidadorTabla = { crear: crearValidadorTabla };
})();
