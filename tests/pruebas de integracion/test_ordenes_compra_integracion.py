"""Pruebas de integración de la clase OrdenCompra contra MySQL real."""
import pytest

from app.models.ordenes_compra import OrdenCompra
from app.models.database import conectar
from seed_helpers import (
    crear_producto_temporal,
    eliminar_producto_temporal,
)

EMPLEADO_ADMIN = "12345678"
CLASE_TELEFONO = "1"
MARCA_SEED = "3"


# ==================== HELPERS LOCALES (solo para este módulo) ====================


def _crear_proveedor(nombre: str) -> int:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT COALESCE(MAX(ID_proveedor), 0) + 1 FROM Proveedor")
        id_proveedor = int(cursor.fetchone()[0])
        cursor.execute(
            "INSERT INTO Proveedor (ID_proveedor, Rif_proveedor, Nombre_proveedor) "
            "VALUES (%s, %s, %s)",
            (id_proveedor, "J-81100101-1", nombre),
        )
        db.commit()
        return id_proveedor
    finally:
        cursor.close()
        db.close()


def _eliminar_proveedor(id_proveedor: int) -> None:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Suministra WHERE ID_proveedor = %s", (id_proveedor,))
        cursor.execute("DELETE FROM Proveedor WHERE ID_proveedor = %s", (id_proveedor,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def _asignar_costo(id_proveedor: int, id_producto: str, costo: float) -> None:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO Suministra (ID_proveedor, ID_producto, Costo_producto) "
            "VALUES (%s, %s, %s)",
            (id_proveedor, id_producto, costo),
        )
        db.commit()
    finally:
        cursor.close()
        db.close()


def _quitar_costo(id_proveedor: int, id_producto: str) -> None:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM Suministra WHERE ID_proveedor = %s AND ID_producto = %s",
            (id_proveedor, id_producto),
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def _siguiente_id_orden(cursor) -> str:
    cursor.execute("SELECT MAX(ID_orden_compra) FROM Orden_compra")
    ultimo = cursor.fetchone()[0]
    if not ultimo or not str(ultimo).startswith("OC"):
        numero = 0
    else:
        try:
            numero = int(str(ultimo)[2:])
        except ValueError:
            numero = 0
    return f"OC{str(numero + 1).zfill(7)}"


def _crear_orden(
    id_proveedor: int, productos: list, estado: str = "Pendiente"
) -> str:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        id_orden = _siguiente_id_orden(cursor)
        cursor.execute(
            "INSERT INTO Orden_compra (ID_orden_compra, ID_empleado, ID_proveedor, "
            "Estado_orden_compra, Fecha_orden_compra) VALUES (%s, %s, %s, %s, NOW())",
            (id_orden, EMPLEADO_ADMIN, id_proveedor, estado),
        )
        for id_producto, cantidad in productos:
            cursor.execute(
                "INSERT INTO Detalle_orden (ID_orden_compra, ID_producto, Cantidad_producto) "
                "VALUES (%s, %s, %s)",
                (id_orden, str(id_producto), cantidad),
            )
        db.commit()
        return id_orden
    finally:
        cursor.close()
        db.close()


def _eliminar_entregas_de_orden(id_orden: str) -> None:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM Abastece WHERE ID_entrega_inventario IN "
            "(SELECT ID_entrega_inventario FROM Entrega_inventario WHERE ID_orden_compra = %s)",
            (id_orden,),
        )
        cursor.execute(
            "DELETE FROM Entrega_inventario WHERE ID_orden_compra = %s", (id_orden,)
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def _eliminar_orden(id_orden: str) -> None:
    _eliminar_entregas_de_orden(id_orden)
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Detalle_orden WHERE ID_orden_compra = %s", (id_orden,))
        cursor.execute("DELETE FROM Orden_compra WHERE ID_orden_compra = %s", (id_orden,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


@pytest.fixture
def orden_basica():
    """Proveedor + producto + costo de suministro. Devuelve los IDs."""
    id_proveedor = None
    id_producto = None
    try:
        id_proveedor = _crear_proveedor("Proveedor Integra Ordenes Compra")
        id_producto = crear_producto_temporal(
            nombre="Prod Integra Ordenes Compra",
            clase=CLASE_TELEFONO,
            marca=MARCA_SEED,
        )
        _asignar_costo(id_proveedor, id_producto, costo=100.0)
        yield {
            "id_proveedor": id_proveedor,
            "id_producto": id_producto,
            "costo": 100.0,
        }
    finally:
        if id_producto:
            _quitar_costo(id_proveedor, id_producto)
            eliminar_producto_temporal(id_producto)
        if id_proveedor:
            _eliminar_proveedor(id_proveedor)


@pytest.fixture
def orden_pendiente(orden_basica):
    """Orden de compra pendiente con un producto. Se limpia al final."""
    info = orden_basica
    id_orden = _crear_orden(
        info["id_proveedor"], [(info["id_producto"], 2)], estado="Pendiente"
    )
    yield {**info, "id_orden": id_orden}
    _eliminar_orden(id_orden)


class TestListarOrdenes:

    def test_pendientes_incluye_la_orden_temporal(self, orden_pendiente):
        info = orden_pendiente
        pendientes = OrdenCompra().listar_ordenes_pendientes()
        fila = next(
            (o for o in pendientes if o["ID_orden_c"] == info["id_orden"]), None
        )

        assert fila is not None
        assert fila["Estado"] == "Pendiente"
        assert fila["ID_proveedor"] == info["id_proveedor"]
        assert float(fila["Costo_venta"]) == info["costo"] * 2

    def test_entregadas_no_incluye_orden_sin_entrega(self, orden_pendiente):
        info = orden_pendiente
        entregadas = OrdenCompra().listar_ordenes_entregadas()

        assert all(o["ID_orden_c"] != info["id_orden"] for o in entregadas)


class TestCatalogosDeOrden:

    def test_listar_proveedores(self, orden_basica):
        info = orden_basica
        proveedores = OrdenCompra().listar_proveedores()
        fila = next(
            (p for p in proveedores if p["id"] == info["id_proveedor"]), None
        )

        assert fila is not None
        assert fila["nombre"] == "Proveedor Integra Ordenes Compra"

    # Nota: listar_empleados() de OrdenCompra no se prueba porque su SQL
    # referencia la columna Cedula_empleado, que no existe en la tabla
    # Empleado del esquema real (la consulta falla y devuelve []).

    def test_obtener_productos_proveedor(self, orden_basica):
        info = orden_basica
        productos = OrdenCompra().obtener_productos_proveedor(info["id_proveedor"])
        fila = next(
            (p for p in productos if str(p["ID_modelo"]) == info["id_producto"]), None
        )

        assert fila is not None
        assert float(fila["Costo"]) == info["costo"]

    def test_obtener_productos_proveedor_sin_id(self):
        assert OrdenCompra().obtener_productos_proveedor(None) == []


class TestAgregarOrdenCompra:

    def test_datos_validos(self, orden_basica):
        info = orden_basica
        id_orden = None
        try:
            modelo = OrdenCompra(
                id_empleado=int(EMPLEADO_ADMIN),
                id_proveedor=info["id_proveedor"],
                productos=[(info["id_producto"], 3)],
            )
            assert modelo.agregar_orden_compra() is True

            id_orden = modelo.id_orden
            assert id_orden is not None and id_orden.startswith("OC")

            pendientes = OrdenCompra().listar_ordenes_pendientes()
            assert any(o["ID_orden_c"] == id_orden for o in pendientes)
        finally:
            if id_orden:
                _eliminar_orden(id_orden)

    def test_sin_datos_devuelve_false(self):
        assert OrdenCompra().agregar_orden_compra() is False

    def test_sin_productos_devuelve_false(self, orden_basica):
        info = orden_basica
        modelo = OrdenCompra(
            id_empleado=int(EMPLEADO_ADMIN), id_proveedor=info["id_proveedor"]
        )
        assert modelo.agregar_orden_compra() is False


class TestActualizarOrdenCompra:

    def test_datos_validos(self, orden_pendiente):
        info = orden_pendiente
        modelo = OrdenCompra(
            id_orden=info["id_orden"],
            id_empleado=int(EMPLEADO_ADMIN),
            id_proveedor=info["id_proveedor"],
            productos=[(info["id_producto"], 7)],
        )

        assert modelo.actualizar_orden_compra() is True

        detalles = OrdenCompra().obtener_detalles_orden(info["id_orden"])
        cantidades = [int(p["Cantidad_p"]) for p in detalles["productos_orden"]]
        assert cantidades == [7]

    def test_producto_inexistente(self, orden_pendiente):
        info = orden_pendiente
        modelo = OrdenCompra(
            id_orden=info["id_orden"],
            id_empleado=int(EMPLEADO_ADMIN),
            id_proveedor=info["id_proveedor"],
            productos=[("999999", 1)],
        )
        with pytest.raises(ValueError) as exc:
            modelo.actualizar_orden_compra()

        assert str(exc.value) == "El producto con ID '999999' no existe en el catálogo"

    def test_orden_inexistente_devuelve_false(self, orden_basica):
        info = orden_basica
        modelo = OrdenCompra(
            id_orden="OC9999999",
            id_empleado=int(EMPLEADO_ADMIN),
            id_proveedor=info["id_proveedor"],
            productos=[(info["id_producto"], 1)],
        )
        assert modelo.actualizar_orden_compra() is False

    def test_orden_no_pendiente_devuelve_false(self, orden_pendiente):
        info = orden_pendiente
        assert OrdenCompra(id_orden=info["id_orden"]).anular_orden_compra() is True

        modelo = OrdenCompra(
            id_orden=info["id_orden"],
            id_empleado=int(EMPLEADO_ADMIN),
            id_proveedor=info["id_proveedor"],
            productos=[(info["id_producto"], 1)],
        )
        assert modelo.actualizar_orden_compra() is False

    def test_sin_id(self, orden_basica):
        info = orden_basica
        modelo = OrdenCompra(
            id_empleado=int(EMPLEADO_ADMIN),
            id_proveedor=info["id_proveedor"],
            productos=[(info["id_producto"], 1)],
        )
        with pytest.raises(ValueError) as exc:
            modelo.actualizar_orden_compra()

        assert str(exc.value) == "ID de orden es requerido para actualizar"


class TestAnularOrdenCompra:

    def test_datos_validos(self, orden_pendiente):
        info = orden_pendiente
        assert OrdenCompra(id_orden=info["id_orden"]).anular_orden_compra() is True

        pendientes = OrdenCompra().listar_ordenes_pendientes()
        assert all(o["ID_orden_c"] != info["id_orden"] for o in pendientes)

    def test_segunda_anulacion_devuelve_false(self, orden_pendiente):
        info = orden_pendiente
        OrdenCompra(id_orden=info["id_orden"]).anular_orden_compra()
        assert OrdenCompra(id_orden=info["id_orden"]).anular_orden_compra() is False

    def test_orden_inexistente_devuelve_false(self):
        assert OrdenCompra(id_orden="OC9999999").anular_orden_compra() is False

    def test_sin_id_devuelve_false(self):
        assert OrdenCompra().anular_orden_compra() is False


class TestDetallesOrden:

    def test_obtener_detalles_orden(self, orden_pendiente):
        info = orden_pendiente
        detalles = OrdenCompra().obtener_detalles_orden(info["id_orden"])

        assert detalles is not None
        assert detalles["datos_orden"]["ID_orden_c"] == info["id_orden"]
        assert detalles["datos_orden"]["Estado"] == "Pendiente"
        assert detalles["datos_orden"]["nombre"] == "Proveedor Integra Ordenes Compra"
        assert float(detalles["datos_orden"]["Costo_venta"]) == info["costo"] * 2

        productos = detalles["productos_orden"]
        assert len(productos) == 1
        assert str(productos[0]["ID_producto"]) == info["id_producto"]
        assert int(productos[0]["Cantidad_p"]) == 2
        assert float(productos[0]["Costo"]) == info["costo"]

    def test_obtener_detalles_orden_inexistente(self):
        assert OrdenCompra().obtener_detalles_orden("OC9999999") is None
        assert OrdenCompra().obtener_detalles_orden(None) is None

    def test_obtener_productos_orden(self, orden_pendiente):
        info = orden_pendiente
        productos = OrdenCompra().obtener_productos_orden(info["id_orden"])

        assert len(productos) == 1
        assert str(productos[0]["ID_modelo"]) == info["id_producto"]
        assert int(productos[0]["Cantidad_p"]) == 2

    def test_obtener_productos_orden_inexistente(self):
        assert OrdenCompra().obtener_productos_orden("OC9999999") == []
