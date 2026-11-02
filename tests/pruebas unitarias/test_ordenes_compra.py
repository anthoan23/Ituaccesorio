"""Pruebas unitarias de la clase OrdenCompra (app.models.ordenes_compra).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.
"""
from unittest.mock import patch

import pytest

from app.models.ordenes_compra import OrdenCompra
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

# ==================== Datos de frontera ====================
ID_ORDEN = "OC0000001"
ID_EMPLEADO = "123456"
ID_PROVEEDOR = 1
PRODUCTOS = [("1", 2), ("2", 5)]


class TestListarOrdenesPendientes:

    def test_con_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"ID_orden_c": ID_ORDEN, "Estado": "Pendiente"}]
        cursor.fetchall.return_value = filas

        assert OrdenCompra().listar_ordenes_pendientes() == filas
        assert "Estado_orden_compra = 'Pendiente'" in ultima_sentencia(cursor)
        cierra_recursos(db, cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert OrdenCompra().listar_ordenes_pendientes() == []

    def test_conexion_caida(self, conexion_caída):
        assert OrdenCompra().listar_ordenes_pendientes() == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert OrdenCompra().listar_ordenes_pendientes() == []

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        OrdenCompra().listar_ordenes_pendientes()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestListarOrdenesEntregadas:

    def test_con_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"ID_orden_c": ID_ORDEN}]
        cursor.fetchall.return_value = filas

        assert OrdenCompra().listar_ordenes_entregadas() == filas
        assert "Estado_orden_compra = 'Completada'" in ultima_sentencia(cursor)
        cierra_recursos(db, cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert OrdenCompra().listar_ordenes_entregadas() == []

    def test_conexion_caida(self, conexion_caída):
        assert OrdenCompra().listar_ordenes_entregadas() == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert OrdenCompra().listar_ordenes_entregadas() == []


class TestObtenerDetallesOrden:

    def test_orden_con_empleado(self, conexion_falsa):
        db, cursor = conexion_falsa
        orden = {
            "ID_orden_c": ID_ORDEN,
            "ID_proveedor": ID_PROVEEDOR,
            "ID_empleado": ID_EMPLEADO,
        }
        cursor.fetchone.side_effect = [
            orden,
            {"nombre": "Distribuidora Uno"},
            {"Realizado_por": "Ana Pérez"},
            {"Costo_venta": "25.50"},
        ]
        productos = [{"ID_producto": "1", "Cantidad_p": 2}]
        cursor.fetchall.return_value = productos

        resultado = OrdenCompra().obtener_detalles_orden(ID_ORDEN)

        assert resultado["datos_orden"]["nombre"] == "Distribuidora Uno"
        assert resultado["datos_orden"]["Realizado_por"] == "Ana Pérez"
        assert resultado["datos_orden"]["Costo_venta"] == 25.5
        assert resultado["productos_orden"] == productos
        cierra_recursos(db, cursor)

    def test_orden_sin_empleado(self, conexion_falsa):
        db, cursor = conexion_falsa
        orden = {"ID_orden_c": ID_ORDEN, "ID_proveedor": ID_PROVEEDOR}
        cursor.fetchone.side_effect = [
            orden,
            None,
            None,
        ]
        cursor.fetchall.return_value = []

        resultado = OrdenCompra().obtener_detalles_orden(ID_ORDEN)

        assert resultado["datos_orden"]["nombre"] == "Proveedor no encontrado"
        assert resultado["datos_orden"]["Realizado_por"] == "Sistema"
        assert resultado["datos_orden"]["Costo_venta"] == 0

    def test_orden_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert OrdenCompra().obtener_detalles_orden(ID_ORDEN) is None

    def test_conexion_caida(self, conexion_caída):
        assert OrdenCompra().obtener_detalles_orden(ID_ORDEN) is None

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert OrdenCompra().obtener_detalles_orden(ID_ORDEN) is None


class TestObtenerProductosOrden:

    def test_con_productos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"ID_modelo": "1", "Cantidad_p": 2}]
        cursor.fetchall.return_value = filas

        assert OrdenCompra().obtener_productos_orden(ID_ORDEN) == filas
        assert cursor.execute.call_args.args[1] == (ID_ORDEN,)
        cierra_recursos(db, cursor)

    def test_sin_productos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert OrdenCompra().obtener_productos_orden(ID_ORDEN) == []

    def test_conexion_caida(self, conexion_caída):
        assert OrdenCompra().obtener_productos_orden(ID_ORDEN) == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert OrdenCompra().obtener_productos_orden(ID_ORDEN) == []


class TestListarProveedores:

    def test_con_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id": ID_PROVEEDOR, "nombre": "Distribuidora Uno"}]
        cursor.fetchall.return_value = filas

        assert OrdenCompra().listar_proveedores() == filas
        assert "FROM Proveedor" in ultima_sentencia(cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert OrdenCompra().listar_proveedores() == []

    def test_conexion_caida(self, conexion_caída):
        assert OrdenCompra().listar_proveedores() == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert OrdenCompra().listar_proveedores() == []


class TestListarEmpleados:

    def test_con_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id": ID_EMPLEADO, "nombre_completo": "Ana Pérez"}]
        cursor.fetchall.return_value = filas

        assert OrdenCompra().listar_empleados() == filas
        assert "FROM Empleado" in ultima_sentencia(cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert OrdenCompra().listar_empleados() == []

    def test_conexion_caida(self, conexion_caída):
        assert OrdenCompra().listar_empleados() == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert OrdenCompra().listar_empleados() == []


class TestObtenerProductosProveedor:

    def test_sin_id_proveedor(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert OrdenCompra().obtener_productos_proveedor(None) == []
        cursor.execute.assert_not_called()

    def test_con_productos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"ID_modelo": "1", "N_modelo": "Cargador"}]
        cursor.fetchall.return_value = filas

        assert OrdenCompra().obtener_productos_proveedor(ID_PROVEEDOR) == filas
        assert cursor.execute.call_args.args[1] == (ID_PROVEEDOR,)

    def test_sin_productos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert OrdenCompra().obtener_productos_proveedor(ID_PROVEEDOR) == []

    def test_conexion_caida(self, conexion_caída):
        assert OrdenCompra().obtener_productos_proveedor(ID_PROVEEDOR) == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert OrdenCompra().obtener_productos_proveedor(ID_PROVEEDOR) == []


class TestAgregarOrdenCompra:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("OC0000005",)
        orden = OrdenCompra(
            id_empleado=ID_EMPLEADO,
            id_proveedor=ID_PROVEEDOR,
            productos=PRODUCTOS,
        )

        resultado = orden.agregar_orden_compra()

        assert resultado is True
        assert orden.id_orden == "OC0000006"
        assert "INSERT INTO Orden_compra" in cursor.execute.call_args_list[1].args[0]
        assert cursor.execute.call_args_list[1].args[1] == (
            "OC0000006",
            ID_EMPLEADO,
            ID_PROVEEDOR,
        )
        inserts = [
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Detalle_orden" in llamada.args[0]
        ]
        assert inserts == [
            ("OC0000006", "1", 2),
            ("OC0000006", "2", 5),
        ]
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_primera_orden_sin_consecutivo_previo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (None,)
        orden = OrdenCompra(
            id_empleado=ID_EMPLEADO,
            id_proveedor=ID_PROVEEDOR,
            productos=PRODUCTOS,
        )

        orden.agregar_orden_compra()

        assert orden.id_orden == "OC0000001"

    def test_consecutivo_con_formato_invalido(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("OCABC",)
        orden = OrdenCompra(
            id_empleado=ID_EMPLEADO,
            id_proveedor=ID_PROVEEDOR,
            productos=PRODUCTOS,
        )

        orden.agregar_orden_compra()

        assert orden.id_orden == "OC0000001"

    def test_faltan_datos(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert OrdenCompra().agregar_orden_compra() is False
        cursor.execute.assert_not_called()

    def test_sin_productos(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert OrdenCompra(
            id_empleado=ID_EMPLEADO, id_proveedor=ID_PROVEEDOR
        ).agregar_orden_compra() is False

    def test_conexion_caida(self, conexion_caída):
        assert OrdenCompra(
            id_empleado=ID_EMPLEADO,
            id_proveedor=ID_PROVEEDOR,
            productos=PRODUCTOS,
        ).agregar_orden_compra() is False

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = OrdenCompra(
            id_empleado=ID_EMPLEADO,
            id_proveedor=ID_PROVEEDOR,
            productos=PRODUCTOS,
        ).agregar_orden_compra()

        assert resultado is False
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestActualizarOrdenCompra:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (ID_ORDEN, "Pendiente"),  # orden pendiente
            ("1",),  # producto 1 existe
            ("2",),  # producto 2 existe
        ]

        with patch("app.models.ordenes_compra.Bitacora") as bitacora:
            resultado = OrdenCompra(
                id_orden=ID_ORDEN,
                id_empleado=ID_EMPLEADO,
                id_proveedor=ID_PROVEEDOR,
                productos=PRODUCTOS,
                usuario_id="USR-001",
            ).actualizar_orden_compra()

        assert resultado is True
        sentencias = [llamada.args[0] for llamada in cursor.execute.call_args_list]
        assert any("UPDATE Orden_compra" in sql for sql in sentencias)
        assert any("DELETE FROM Detalle_orden" in sql for sql in sentencias)
        inserts = [
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Detalle_orden" in llamada.args[0]
        ]
        assert inserts == [
            (ID_ORDEN, "1", 2),
            (ID_ORDEN, "2", 5),
        ]
        db.commit.assert_called_once()
        bitacora.return_value.registrar.assert_called_once()

    def test_sin_id_orden(self, conexion_falsa):
        with pytest.raises(ValueError, match="ID de orden es requerido"):
            OrdenCompra(
                id_empleado=ID_EMPLEADO,
                id_proveedor=ID_PROVEEDOR,
                productos=PRODUCTOS,
            ).actualizar_orden_compra()

    def test_faltan_datos(self, conexion_falsa):
        with pytest.raises(ValueError, match="Empleado, proveedor y productos"):
            OrdenCompra(id_orden=ID_ORDEN).actualizar_orden_compra()

    def test_conexion_caida(self, conexion_caída):
        with pytest.raises(RuntimeError, match="No se pudo conectar"):
            OrdenCompra(
                id_orden=ID_ORDEN,
                id_empleado=ID_EMPLEADO,
                id_proveedor=ID_PROVEEDOR,
                productos=PRODUCTOS,
            ).actualizar_orden_compra()

    def test_orden_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert OrdenCompra(
            id_orden=ID_ORDEN,
            id_empleado=ID_EMPLEADO,
            id_proveedor=ID_PROVEEDOR,
            productos=PRODUCTOS,
        ).actualizar_orden_compra() is False

        db.commit.assert_not_called()

    def test_orden_no_pendiente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_ORDEN, "Completada")

        assert OrdenCompra(
            id_orden=ID_ORDEN,
            id_empleado=ID_EMPLEADO,
            id_proveedor=ID_PROVEEDOR,
            productos=PRODUCTOS,
        ).actualizar_orden_compra() is False

        db.commit.assert_not_called()

    def test_producto_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (ID_ORDEN, "Pendiente"),
            None,  # el primer producto no existe
        ]

        resultado = OrdenCompra(
            id_orden=ID_ORDEN,
            id_empleado=ID_EMPLEADO,
            id_proveedor=ID_PROVEEDOR,
            productos=PRODUCTOS,
        ).actualizar_orden_compra()

        assert resultado is False
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert OrdenCompra(
            id_orden=ID_ORDEN,
            id_empleado=ID_EMPLEADO,
            id_proveedor=ID_PROVEEDOR,
            productos=PRODUCTOS,
        ).actualizar_orden_compra() is False

        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestAnularOrdenCompra:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 1

        with patch("app.models.ordenes_compra.Bitacora") as bitacora:
            resultado = OrdenCompra(
                id_orden=ID_ORDEN, usuario_id="USR-001"
            ).anular_orden_compra()

        assert resultado is True
        assert "SET Estado_orden_compra = 'Anulada'" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_ORDEN,)
        db.commit.assert_called_once()
        bitacora.return_value.registrar.assert_called_once()
        cierra_recursos(db, cursor)

    def test_sin_filas_afectadas(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 0

        assert OrdenCompra(id_orden=ID_ORDEN).anular_orden_compra() is False

    def test_sin_id_orden(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert OrdenCompra().anular_orden_compra() is False
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert OrdenCompra(id_orden=ID_ORDEN).anular_orden_compra() is False

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert OrdenCompra(id_orden=ID_ORDEN).anular_orden_compra() is False
        db.rollback.assert_called_once()
        db.commit.assert_not_called()
