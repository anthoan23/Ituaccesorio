/* global UiModal */

(function () {
  'use strict';

  function $id(id) {
    return document.getElementById(id);
  }

  function abrirModal(id) {
    if (window.UiModal && typeof window.UiModal.openById === 'function') {
      window.UiModal.openById(id);
      return;
    }
    const el = $id(id);
    if (el) {
      el.hidden = false;
      el.setAttribute('aria-hidden', 'false');
    }
  }

  function cerrarModal(id) {
    if (window.UiModal && typeof window.UiModal.closeById === 'function') {
      window.UiModal.closeById(id);
      return;
    }
    const el = $id(id);
    if (el) {
      el.hidden = true;
      el.setAttribute('aria-hidden', 'true');
    }
  }

  function formatFecha(fechaHora) {
    if (!fechaHora) return '';
    
    try {
      let fecha;
      
      if (typeof fechaHora === 'string') {
        let fechaStr = fechaHora.replace(' ', 'T');
        if (!fechaStr.includes('Z') && !fechaStr.includes('+')) {
          fechaStr = fechaStr + 'T00:00:00';
        }
        fecha = new Date(fechaStr);
        if (isNaN(fecha.getTime())) {
          fecha = new Date(fechaHora);
        }
      } else {
        fecha = new Date(fechaHora);
      }
      
      if (isNaN(fecha.getTime())) {
        console.warn('Fecha inválida:', fechaHora);
        return fechaHora;
      }
      
      return fecha.toLocaleString('es-VE', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      });
    } catch (e) {
      console.error('Error formateando fecha:', e);
      return fechaHora;
    }
  }

  function getBadgeClass(accion) {
    const accionLower = String(accion || '').toLowerCase().trim();
    if (accionLower === 'crear' || accionLower.includes('creación')) return 'crear';
    if (accionLower === 'actualizar' || accionLower.includes('edición') || accionLower.includes('modificar')) return 'actualizar';
    if (accionLower === 'eliminar' || accionLower.includes('borrar')) return 'eliminar';
    if (accionLower === 'login' || accionLower.includes('inicio sesión')) return 'login';
    if (accionLower === 'logout' || accionLower.includes('cierre sesión')) return 'logout';
    if (accionLower === 'error' || accionLower.includes('fallo')) return 'error';
    return 'default';
  }

  function mostrarDetalleEvento(evento) {
    $id('d-id').textContent = evento.id || '';
    $id('d-usuario').textContent = evento.usuario || '';
    $id('d-accion').textContent = evento.accion || '';
    $id('d-modulo').textContent = evento.modulo || 'General';
    $id('d-descripcion').textContent = evento.descripcion || '';
    $id('d-fecha').textContent = formatFecha(evento.fecha);

    abrirModal('modal-detalle');
  }

  function refrescarPagina() {
    window.location.reload();
  }

  function bindEvents() {
    const btnRefrescar = $id('btn-refrescar');
    btnRefrescar?.addEventListener('click', refrescarPagina);

    document.querySelectorAll('.evento-row').forEach(row => {
      row.addEventListener('click', () => {
        const id = row.getAttribute('data-id');
        const usuario = row.getAttribute('data-usuario');
        const accion = row.getAttribute('data-accion');
        const modulo = row.getAttribute('data-modulo');
        const descripcion = row.getAttribute('data-descripcion');
        const fecha = row.getAttribute('data-fecha');

        mostrarDetalleEvento({ id, usuario, accion, modulo, descripcion, fecha });
      });
    });
  }

  function init() {
    bindEvents();
    
    // Formatear fechas en la tabla
    document.querySelectorAll('.col-fecha').forEach(cell => {
      const fechaOriginal = cell.textContent;
      if (fechaOriginal && fechaOriginal !== 'No hay eventos' && !cell.classList.contains('formateado')) {
        const fechaFormateada = formatFecha(fechaOriginal);
        if (fechaFormateada !== fechaOriginal) {
          cell.textContent = fechaFormateada;
        }
        cell.classList.add('formateado');
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    void init();
  }

  function renderizarUsuarioConFoto(usuarioId, usuarioNombre, usuarioFoto) {
    const inicial = (usuarioNombre || usuarioId || 'U').charAt(0).toUpperCase();
    
    if (usuarioFoto) {
      return `
        <div class="user-cell">
          <img src="${usuarioFoto}" alt="${usuarioNombre || usuarioId}" class="user-avatar">
          <span>${usuarioNombre || usuarioId}</span>
        </div>
      `;
    }
    return `
      <div class="user-cell">
        <div class="user-avatar">${inicial}</div>
        <span>${usuarioNombre || usuarioId}</span>
      </div>
    `;
  }

  window.renderizarUsuarioConFoto = renderizarUsuarioConFoto;
})();