(() => {
  "use strict";

  const MODAL_ID = "feedback-modal";
  const TITLE_ID = "feedback-modal-title";
  const MESSAGE_ID = "feedback-modal-message";

  const AUTO_CLOSE_MS = 3500;
  let autoCloseTimer = null;

  function $(id) {
    return document.getElementById(id);
  }

  function setText(el, text) {
    if (!el) return;
    el.textContent = String(text ?? "");
  }

  function setIcon(modal, type) {
    const successIcon = modal?.querySelector("[data-feedback-icon='success']");
    const errorIcon = modal?.querySelector("[data-feedback-icon='error']");
    if (successIcon) successIcon.hidden = type !== "success";
    if (errorIcon) errorIcon.hidden = type !== "error";

    const content = modal?.querySelector(".feedback-modal__content");
    if (content) {
      content.dataset.feedbackType = type;
    }
  }

  function restartAnim(el) {
    if (!el) return;
    el.classList.remove("is-anim");
    // forzar reflow para reiniciar la animación
    void el.offsetWidth;
    el.classList.add("is-anim");
  }

  function scheduleAutoClose() {
    if (!window.UiModal) return;
    if (autoCloseTimer) {
      window.clearTimeout(autoCloseTimer);
      autoCloseTimer = null;
    }
    autoCloseTimer = window.setTimeout(() => {
      window.UiModal.closeById(MODAL_ID);
    }, AUTO_CLOSE_MS);
  }

  function show({ type = "success", title = "Acción", message = "Operación completada." } = {}) {
    const modal = $(MODAL_ID);
    if (!modal || !window.UiModal) return;

    setText($(TITLE_ID), title);
    setText($(MESSAGE_ID), message);
    setIcon(modal, type);
    window.UiModal.openById(MODAL_ID);

    // animación check/X y mensaje
    const iconToAnimate = modal.querySelector(type === "error" ? "[data-feedback-icon='error']" : "[data-feedback-icon='success']");
    restartAnim(iconToAnimate);
    restartAnim($(MESSAGE_ID));

    // autocierre
    scheduleAutoClose();
  }

  function buildSuccessMessage(url, method) {
    const path = String(url || "");
    const m = String(method || "").toUpperCase();

    if (path.includes("/api/carrito")) {
      if (m === "POST") return "Producto agregado al carrito.";
      if (m === "PUT" || m === "PATCH") return "Carrito actualizado.";
      if (m === "DELETE") return "Carrito actualizado.";
    }

    if (path.includes("/api/procesar-pago")) {
      if (m === "POST") return "Pago registrado. Tu pago está siendo verificado.";
    }

    if (path.includes("/api/productos/modelos")) {
      if (m === "POST") return "Producto registrado satisfactoriamente.";
      if (m === "PUT" || m === "PATCH") return "Producto actualizado satisfactoriamente.";
      if (m === "DELETE") return "Producto eliminado satisfactoriamente.";
    }

    if (path.includes("/api/productos/clases")) {
      if (m === "POST") return "Clase registrada satisfactoriamente.";
      if (m === "PUT" || m === "PATCH") return "Clase actualizada satisfactoriamente.";
      if (m === "DELETE") return "Clase eliminada satisfactoriamente.";
    }

    if (path.includes("/api/productos/marcas")) {
      if (m === "POST") return "Marca registrada satisfactoriamente.";
      if (m === "PUT" || m === "PATCH") return "Marca actualizada satisfactoriamente.";
      if (m === "DELETE") return "Marca eliminada satisfactoriamente.";
    }

    if (path.includes("/api/empleados/consultar")) {
      if (m === "POST") return "Empleado registrado satisfactoriamente.";
    }

    if (m === "POST") return "Registro realizado satisfactoriamente.";
    if (m === "PUT" || m === "PATCH") return "Actualización realizada satisfactoriamente.";
    if (m === "DELETE") return "Eliminación realizada satisfactoriamente.";
    return "Acción realizada satisfactoriamente.";
  }

  function shouldHandleRequest(url, options) {
    const method = String(options?.method || "GET").toUpperCase();
    if (method === "GET" || method === "HEAD") return false;

    const u = String(url || "");
    if (!u.includes("/api/")) return false;

    // Evitar modales en auth/login
    if (u.includes("/api/login") || u.includes("/api/auth") || u.includes("/api/token")) return false;
    
    // 🔴 NUEVO: Evitar modal para consultar empleados
    if (u.includes("/api/empleados/consultar")) return false;

    if (u.includes("/api/taller/reparaciones-asignadas")) return false;

    if (u.includes("/api/taller/consultar-ordene")) return false;

    if (u.includes("/api/taller/consultar-test")) return false;

    return true;
  }
  
  function attachFetchInterceptor() {
    if (window.__feedbackFetchPatched) return;
    window.__feedbackFetchPatched = true;

    const originalFetch = window.fetch.bind(window);

    window.fetch = async (input, init = {}) => {
      const url = typeof input === "string" ? input : input?.url;
      const options = init || {};

      let response;
      try {
        response = await originalFetch(input, init);
      } catch (err) {
        if (shouldHandleRequest(url, options)) {
          show({
            type: "error",
            title: "Error",
            message: "No se pudo realizar el envío. Verifica tu conexión e inténtalo de nuevo.",
          });
        }
        throw err;
      }

      if (!shouldHandleRequest(url, options)) {
        return response;
      }

      // Para no consumir el body que los módulos podrían leer, trabajamos con clone().
      const cloned = response.clone();
      let data = null;

      try {
        const contentType = cloned.headers.get("content-type") || "";
        if (contentType.includes("application/json")) {
          data = await cloned.json();
        }
      } catch {
        data = null;
      }

      const success = response.ok && !(data && data.success === false);

      if (success) {
        show({
          type: "success",
          title: "Acción exitosa",
          message: buildSuccessMessage(url, options?.method),
        });
      } else {
        const errMsg = (data && (data.error || data.message)) || "No se pudo realizar el envío.";
        show({
          type: "error",
          title: "No se pudo completar",
          message: String(errMsg),
        });
      }

      return response;
    };
  }

  document.addEventListener("DOMContentLoaded", () => {
    attachFetchInterceptor();
  });

  window.FeedbackModal = {
    showSuccess: (message, title = "Acción exitosa") => show({ type: "success", title, message }),
    showError: (message, title = "No se pudo completar") => show({ type: "error", title, message }),
    show,
  };
})();
