"""Pruebas de integración de la clase OrdenEntregaModel contra MySQL real."""
import re

import pytest

from app.models.ordenes_compra import OrdenCompra
from app.models.ordenes_entregas import OrdenEntregaModel
from app.models.database import conectar
from seed_helpers import (
    crear_producto_temporal,
    eliminar_producto_temporal,
)

EMPLEADO_ADMIN = "12345678"
CLASE_TELEFONO = "1"
MARCA_SEED = "3"
PATRON_ID_ENTREGA = re.compile(r"^ENT\d{7}$")


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
            (id_proveedor, "J-81200101-1", nombre),
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


def _crear_existencia(
    id_producto: str, existencia: int = 10, costo: float = 100.0
) -> str:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT CONCAT('INV', LPAD(COALESCE(MAX(CAST(SUBSTRING(ID_inventario, 4) AS UNSIGNED)), 0) + 1, 6, '0')) "
            "FROM Existencias_productos"
        )
        id_inventario = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO Existencias_productos (ID_inventario, ID_producto, Existencia, Costo_venta, ID_categoria) "
            "VALUES (%s, %s, %s, %s, NULL)",
            (id_inventario, id_producto, existencia, costo),
        )
        db.commit()
        return id_inventario
    finally:
        cursor.close()
        db.close()


def _eliminar_existencia(id_inventario: str) -> None:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM Existencias_productos WHERE ID_inventario = %s",
            (id_inventario,),
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


def _cambiar_estado_orden(id_orden: str, estado: str) -> None:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute(
            "UPDATE Orden_compra SET Estado_orden_compra = %s WHERE ID_orden_compra = %s",
            (estado, id_orden),
        )
        db.commit()
    finally:
        cursor.close()
        db.close()


def _stock(id_inventario: str) -> int:
    db = conectar().conexion1()
    if not db:
        return 0
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT Existencia FROM Existencias_productos WHERE ID_inventario = %s",
            (id_inventario,),
        )
        fila = cursor.fetchone()
        return int(fila[0] or 0) if fila else 0
    finally:
        cursor.close()
        db.close()


def _abasteces_de_producto(id_producto: str) -> list:
    db = conectar().conexion1()
    if not db:
        return []
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT a.Cantidad_entregada FROM Abastece a "
            "INNER JOIN Existencias_productos e ON a.ID_inventario = e.ID_inventario "
            "WHERE e.ID_producto = %s",
            (id_producto,),
        )
        return [int(fila[0]) for fila in cursor.fetchall()]
    finally:
        cursor.close()
        db.close()


@pytest.fixture
def orden_para_entrega():
    """Producto SIN existencias + proveedor + costo + orden pendiente."""
    id_proveedor = None
    id_producto = None
    id_orden = None
    try:
        id_proveedor = _crear_proveedor("Proveedor Integra Entregas")
        id_producto = crear_producto_temporal(
            nombre="Prod Integra Entregas", clase=CLASE_TELEFONO, marca=MARCA_SEED
        )
        _asignar_costo(id_proveedor, id_producto, costo=100.0)
        id_orden = _crear_orden(
            id_proveedor, [(id_producto, 3)], estado="Pendiente"
        )
        yield {
            "id_proveedor": id_proveedor,
            "id_producto": id_producto,
            "id_orden": id_orden,
            "costo": 100.0,
        }
    finally:
        # La entrega crea Existencias_productos: se borran con el producto.
        if id_orden:
            _eliminar_orden(id_orden)
        if id_producto:
            eliminar_producto_temporal(id_producto)
        if id_proveedor:
            _eliminar_proveedor(id_proveedor)


class TestRegistrarEntrega:

    def test_datos_validos(self, orden_para_entrega):
        info = orden_para_entrega
        modelo = OrdenEntregaModel(
            id_orden=info["id_orden"], id_empleado=int(EMPLEADO_ADMIN)
        )

        assert modelo.registrar_entrega() is True

        # Genera un ID de entrega con formato ENT#######
        assert PATRON_ID_ENTREGA.match(modelo.id_entrega)

        # La orden pasa a Completada
        pendientes_ids = [
            o["ID_orden_c"]
            for o in OrdenCompra().listar_ordenes_pendientes()
        ]
        assert info["id_orden"] not in pendientes_ids

        # Crea la existencia con costo de venta = costo * 1.3
        db = conectar().conexion1()
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT Existencia, Costo_venta FROM Existencias_productos "
                "WHERE ID_producto = %s",
                (info["id_producto"],),
            )
            existencia, costo_venta = cursor.fetchone()
        finally:
            cursor.close()
            db.close()

        assert existencia == 3
        assert float(costo_venta) == 130.0

        # Registra el abastecimiento
        assert _abasteces_de_producto(info["id_producto"]) == [3]

        # La entrega es consultable
        entrega = OrdenEntregaModel().obtener_entrega(modelo.id_entrega)
        assert entrega["ID_orden_c"] == info["id_orden"]

    def test_con_inventario_existente_aumenta_el_stock(self, orden_para_entrega):
        info = orden_para_entrega
        id_inventario = _crear_existencia(
            info["id_producto"], existencia=5, costo=120.0
        )
        try:
            modelo = OrdenEntregaModel(
                id_orden=info["id_orden"], id_empleado=int(EMPLEADO_ADMIN)
            )
            assert modelo.registrar_entrega() is True

            assert _stock(id_inventario) == 8
            assert _abasteces_de_producto(info["id_producto"]) == [3]
        finally:
            # Abastece referencia la existencia: hay que borrarla antes.
            _eliminar_entregas_de_orden(info["id_orden"])
            _eliminar_existencia(id_inventario)

    def test_orden_no_pendiente_devuelve_false(self, orden_para_entrega):
        info = orden_para_entrega
        _cambiar_estado_orden(info["id_orden"], "Anulada")

        modelo = OrdenEntregaModel(
            id_orden=info["id_orden"], id_empleado=int(EMPLEADO_ADMIN)
        )
        assert modelo.registrar_entrega() is False

    def test_orden_sin_detalles_devuelve_false(self, orden_para_entrega):
        info = orden_para_entrega
        # Quitar el costo de Suministra deja la orden sin detalles entregables
        _quitar_costo(info["id_proveedor"], info["id_producto"])

        modelo = OrdenEntregaModel(
            id_orden=info["id_orden"], id_empleado=int(EMPLEADO_ADMIN)
        )
        assert modelo.registrar_entrega() is False

    def test_orden_inexistente_devuelve_false(self):
        modelo = OrdenEntregaModel(
            id_orden="OC9999999", id_empleado=int(EMPLEADO_ADMIN)
        )
        assert modelo.registrar_entrega() is False

    def test_sin_orden_devuelve_false(self):
        assert (
            OrdenEntregaModel(id_empleado=int(EMPLEADO_ADMIN)).registrar_entrega()
            is False
        )


class TestListarEntregas:

    def test_incluye_entrega_temporal(self, orden_para_entrega):
        info = orden_para_entrega
        modelo = OrdenEntregaModel(
            id_orden=info["id_orden"], id_empleado=int(EMPLEADO_ADMIN)
        )
        modelo.registrar_entrega()

        entregas = OrdenEntregaModel().listar_entregas()
        fila = next(
            (e for e in entregas if e["ID_entrega"] == modelo.id_entrega), None
        )

        assert fila is not None
        assert fila["ID_orden_c"] == info["id_orden"]
        assert fila["Estado_orden"] == "Completada"
        assert fila["Recibido_por"] == "Super Admin"

    def test_obtener_entrega_inexistente(self):
        assert OrdenEntregaModel().obtener_entrega("ENT9999999") is None


class TestEditarEntrega:

    def test_datos_validos(self, orden_para_entrega):
        info = orden_para_entrega
        modelo = OrdenEntregaModel(
            id_orden=info["id_orden"], id_empleado=int(EMPLEADO_ADMIN)
        )
        modelo.registrar_entrega()

        editor = OrdenEntregaModel(
            id_entrega=modelo.id_entrega,
            fecha_entrega="2026-01-15 10:30:00",
        )
        assert editor.editar_entrega() is True

        entrega = OrdenEntregaModel().obtener_entrega(modelo.id_entrega)
        assert entrega["Fecha_entrega"] == "2026-01-15 10:30"

    def test_entrega_inexistente_devuelve_false(self):
        assert (
            OrdenEntregaModel(id_entrega="ENT9999999").editar_entrega() is False
        )

    def test_sin_id_devuelve_false(self):
        assert (
            OrdenEntregaModel(fecha_entrega="2026-01-15 10:30:00").editar_entrega()
            is False
        )


class TestEliminarEntrega:

    def test_datos_validos(self, orden_para_entrega):
        info = orden_para_entrega
        id_inventario = _crear_existencia(
            info["id_producto"], existencia=5, costo=120.0
        )
        try:
            modelo = OrdenEntregaModel(
                id_orden=info["id_orden"], id_empleado=int(EMPLEADO_ADMIN)
            )
            modelo.registrar_entrega()
            assert _stock(id_inventario) == 8

            assert (
                OrdenEntregaModel(id_entrega=modelo.id_entrega).eliminar_entrega()
                is True
            )

            # Revierte el stock y devuelve la orden a Pendiente
            assert _stock(id_inventario) == 5
            assert _abasteces_de_producto(info["id_producto"]) == []
            pendientes = OrdenCompra().listar_ordenes_pendientes()
            assert any(o["ID_orden_c"] == info["id_orden"] for o in pendientes)
        finally:
            _eliminar_entregas_de_orden(info["id_orden"])
            _eliminar_existencia(id_inventario)

    def test_entrega_inexistente_devuelve_false(self):
        assert (
            OrdenEntregaModel(id_entrega="ENT9999999").eliminar_entrega() is False
        )

    def test_sin_id_devuelve_false(self):
        assert OrdenEntregaModel().eliminar_entrega() is False
