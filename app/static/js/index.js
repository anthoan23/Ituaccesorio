document.addEventListener('DOMContentLoaded', () => {
    cargarProductosBajoStock();
    cargarProductosSinStock();
});

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
                
                // Determinar clase de stock
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
                
                // Imagen o placeholder
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
            container.innerHTML = '<div class="empty-message">No hay productos con bajo stock</div>';
        }
    } catch (error) {
        console.error('Error cargando productos con bajo stock:', error);
        container.innerHTML = '<div class="empty-message">Error al cargar los datos</div>';
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