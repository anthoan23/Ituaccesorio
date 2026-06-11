document.addEventListener('DOMContentLoaded', () => {
    cargarVentasHoy();
    cargarProductosBajoStock();
    cargarProductosSinStock();
    cargarActividadReciente();
});

async function cargarVentasHoy() {
    const ventasContainer = document.getElementById('ventas-hoy-value');
    const ventasCountContainer = document.getElementById('ventas-hoy-count');
    if (!ventasContainer) return;

    try {
        const response = await fetch('/api/dashboard/ventas-hoy', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin'
        });

        const data = await response.json();

        if (data.success) {
            const moneda = data.moneda === 'VES' ? 'Bs.' : '$';
            ventasContainer.innerHTML = `${moneda} ${data.total_formateado}`;
            if (ventasCountContainer) {
                ventasCountContainer.innerHTML = `${data.cantidad_ventas} venta${data.cantidad_ventas !== 1 ? 's' : ''} hoy`;
            }
        } else {
            ventasContainer.innerHTML = '$0.00';
            if (ventasCountContainer) ventasCountContainer.innerHTML = '0 ventas hoy';
        }
    } catch (error) {
        console.error('Error cargando ventas de hoy:', error);
        ventasContainer.innerHTML = '$0.00';
        if (ventasCountContainer) ventasCountContainer.innerHTML = 'Error al cargar';
    }
}

async function cargarActividadReciente() {
    const container = document.getElementById('actividad-reciente-list');
    if (!container) return;

    try {
        const response = await fetch('/api/dashboard/actividad-reciente', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin'
        });

        const data = await response.json();

        if (data.success && data.actividades && data.actividades.length > 0) {
            container.innerHTML = data.actividades.map(actividad => {
                // Obtener icono según el módulo
                let icono = '';
                const modulo = (actividad.modulo_nombre || '').toLowerCase();
                if (modulo.includes('venta')) icono = '💰';
                else if (modulo.includes('inventario')) icono = '📦';
                else if (modulo.includes('producto')) icono = '📱';
                else if (modulo.includes('proveedor')) icono = '🏭';
                else if (modulo.includes('orden')) icono = '📋';
                else icono = '🔔';
                
                return `
                    <div class="activity__item">
                        <span class="activity__icon">${icono}</span>
                        <div class="activity__content">
                            <p class="activity__text">
                                <strong>${escapeHtml(actividad.usuario_id || 'Sistema')}</strong> 
                                ${escapeHtml(actividad.descripcion || actividad.accion || 'Actividad registrada')}
                            </p>
                            <span class="activity__time">
                                <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                                    <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2Zm1 11h5v-2h-4V6h-2v7Z" fill="currentColor"/>
                                </svg>
                                ${escapeHtml(actividad.tiempo_relativo || 'recientemente')}
                            </span>
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            container.innerHTML = '<div class="empty-message">No hay actividad reciente</div>';
        }
    } catch (error) {
        console.error('Error cargando actividad reciente:', error);
        container.innerHTML = '<div class="empty-message">Error al cargar actividad</div>';
    }
}

async function cargarProductosBajoStock() {
    const container = document.getElementById('low-stock-list');
    if (!container) return;

    try {
        const response = await fetch('/api/dashboard/bajo-stock', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin'
        });

        const data = await response.json();

        if (data.success && data.productos && data.productos.length > 0) {
            container.innerHTML = data.productos.map(producto => {
                const stock = producto.existencia || 0;
                const foto = producto.foto_inventario || '';
                
                let stockClass = '';
                let stockText = '';
                if (stock === 0) {
                    stockClass = 'badge--danger';
                    stockText = 'Sin stock';
                } else if (stock <= 5) {
                    stockClass = 'badge--warning';
                    stockText = 'Bajo stock';
                } else if (stock <= 10) {
                    stockClass = 'badge--info';
                    stockText = 'Stock límite';
                } else {
                    stockClass = 'badge--success';
                    stockText = 'Stock disponible';
                }
                
                const imagenHtml = foto ? 
                    `<img src="${foto}" alt="${escapeHtml(producto.nombre_producto || 'Producto')}" class="low-stock-img">` : 
                    `<div class="low-stock-img low-stock-img--empty">📦</div>`;
                
                return `
                    <div class="low-stock-item">
                        <div class="low-stock-thumb">
                            ${imagenHtml}
                        </div>
                        <div class="low-stock-info">
                            <div class="low-stock-name">${escapeHtml(producto.nombre_producto || 'Sin nombre')}</div>
                            <div class="low-stock-marca">${escapeHtml(producto.nombre_marca || 'Sin marca')} • ${escapeHtml(producto.nombre_clase || 'Sin clase')}</div>
                        </div>
                        <div class="low-stock-stock">
                            <div class="low-stock-cantidad">${stock} uds</div>
                            <span class="low-stock-badge ${stockClass}">${stockText}</span>
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            container.innerHTML = '<div class="empty-message">✅ No hay productos con bajo stock</div>';
        }
    } catch (error) {
        console.error('Error cargando productos con bajo stock:', error);
        container.innerHTML = '<div class="empty-message">❌ Error al cargar los datos</div>';
    }
}

async function cargarProductosSinStock() {
    // Esta función es para otra card si decides agregarla
    // Por ahora no la usamos
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}