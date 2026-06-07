/* global UiModal */

(function () {
  'use strict';

  function $id(id) {
    return document.getElementById(id);
  }

  function openModal(id) {
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

  function closeModal(id) {
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
      
      // Si es un string en formato MySQL/Timestamp (YYYY-MM-DD HH:MM:SS)
      if (typeof fechaHora === 'string') {
        // Reemplazar espacio por T para hacerlo ISO compatible
        let fechaStr = fechaHora.replace(' ', 'T');
        
        // Si no tiene zona horaria, agregar la zona local
        if (!fechaStr.includes('Z') && !fechaStr.includes('+')) {
          fechaStr = fechaStr + 'T00:00:00';
        }
        
        fecha = new Date(fechaStr);
        
        // Si falla, intentar con el string original
        if (isNaN(fecha.getTime())) {
          fecha = new Date(fechaHora);
        }
      } else {
        fecha = new Date(fechaHora);
      }
      
      // Verificar si la fecha es válida
      if (isNaN(fecha.getTime())) {
        console.warn('Fecha inválida:', fechaHora);
        return fechaHora; // Devolver el string original si no se puede formatear
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

  function mostrarDetalleEvento(evento) {
    $id('d-id').textContent = evento.id || '';
    $id('d-usuario').textContent = evento.usuario || '';
    $id('d-accion').textContent = evento.accion || '';
    $id('d-descripcion').textContent = evento.descripcion || '';
    $id('d-fecha').textContent = formatFecha(evento.fecha);
    
    openModal('modal-detalle');
  }

  function refrescarPagina() {
    window.location.reload();
  }

  function bindEvents() {
    const btnRefrescar = $id('btn-refrescar');
    btnRefrescar?.addEventListener('click', refrescarPagina);

    // Agregar evento de click para ver detalle
    document.querySelectorAll('.evento-row').forEach(row => {
      row.addEventListener('click', () => {
        const id = row.getAttribute('data-id');
        const usuario = row.getAttribute('data-usuario');
        const accion = row.getAttribute('data-accion');
        const descripcion = row.getAttribute('data-descripcion');
        const fecha = row.getAttribute('data-fecha');
        
        mostrarDetalleEvento({ id, usuario, accion, descripcion, fecha });
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
    if (usuarioFoto) {
        return `<div class="user-cell" style="display: flex; align-items: center; gap: 8px;">
                    <img src="${usuarioFoto}" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover;">
                    <span>${usuarioNombre || usuarioId}</span>
                </div>`;
    }
    return `<div class="user-cell" style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 32px; height: 32px; border-radius: 50%; background: #f3c500; display: flex; align-items: center; justify-content: center; font-weight: bold;">
                    ${(usuarioNombre || usuarioId || 'U').charAt(0).toUpperCase()}
                </div>
                <span>${usuarioNombre || usuarioId}</span>
            </div>`;
}
})();

