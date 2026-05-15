document.addEventListener('DOMContentLoaded', function () {
    const gridDiv = document.querySelector('#bitacoraGrid');
    if (!gridDiv) return;

    fetch('/api/bitacora/list', { credentials: 'same-origin' })
        .then(function (res) { return res.json(); })
        .then(function (data) {
            const columnDefs = [
                { headerName: 'ID', field: 'id', sortable: true, filter: true, width: 90 },
                { headerName: 'Usuario', field: 'usuario_id', sortable: true, filter: true },
                { headerName: 'Modulo', field: 'modulo_id', sortable: true, filter: true },
                { headerName: 'Accion', field: 'accion', sortable: true, filter: true },
                { headerName: 'Descripcion', field: 'descripcion', sortable: true, filter: true, flex: 1 },
                { headerName: 'Fecha', field: 'fecha_hora', sortable: true, filter: true },
            ];

            const gridOptions = {
                columnDefs: columnDefs,
                rowData: data || [],
                defaultColDef: {
                    resizable: true,
                },
                pagination: true,
                paginationPageSize: 25,
            };

            new agGrid.Grid(gridDiv, gridOptions);
        })
        .catch(function (err) {
            console.error('No se pudo cargar la bitacora:', err);
            gridDiv.innerHTML = '<p>Error al cargar los registros.</p>';
        });
});
