"""Pruebas unitarias de la clase OrdenEntregaModel
(app.models.ordenes_entregas).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.
"""
from unittest.mock import patch

import pytest

from app.models.ordenes_entregas import OrdenEntregaModel
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

# ==================== Datos de frontera ====================
ID_ORDEN = "OC0000001"
ID_ENTREGA = "ENT0000005"
ID_EMPLEADO = "123456"
RECIBIDO_POR = "Ana Pérez"
FECHA_ENTREGA = "2026-01-15 10:30"
ID_PROVEEDOR = 1

# (ID_producto, Cantidad_producto, Costo_producto)
DETALLE_EXISTENTE = ("1", 2, "10.00")
DETALLE_NUEVO = ("2", 3, None)


class TestGenerarIdEntrega:

    def test_sin_conexion_devuelve_id_base(self, conexion_caída):
        assert OrdenEntregaModel()._generar_id_entrega() == "ENT0000000"

    def test_sin_entregas_previas(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert OrdenEntregaModel()._generar_id_entrega() == "ENT0000001"
        assert "MAX(ID_entrega_inventario)" in ultima_sentencia(cursor)
        cierra_recursos(db, cursor)

    def test_con_entregas_previas_incrementa(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("ENT0000042",)

        assert OrdenEntregaModel()._generar_id_entrega() == "ENT0000043"

    def test_ultimo_id_nulo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (None,)

        assert OrdenEntregaModel()._generar_id_entrega() == "ENT0000001"

    def test_ultimo_id_con_formato_invalido(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("ABC",)

        assert OrdenEntregaModel()._generar_id_entrega() == "ENT0000001"

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        OrdenEntregaModel()._generar_id_entrega()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestListarEntregas:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {
                "ID_entrega": ID_ENTREGA,
                "ID_orden_c": ID_ORDEN,
                "Fecha_entrega": FECHA_ENTREGA,
                "Proveedor": "Distribuidora Uno",
                "Recibido_por": RECIBIDO_POR,
                "Estado_orden": "Completada",
            }
        ]
        cursor.fetchall.return_value = filas

        resultado = OrdenEntregaModel().listar_entregas()

        assert resultado == filas
        assert "FROM Entrega_inventario" in ultima_sentencia(cursor)
        cierra_recursos(db, cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert OrdenEntregaModel().listar_entregas() == []

    def test_conexion_caida(self, conexion_caída):
        assert OrdenEntregaModel().listar_entregas() == []

    def test_error_de_bd_devuelve_lista_vacia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert OrdenEntregaModel().listar_entregas() == []

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        OrdenEntregaModel().listar_entregas()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerEntrega:

    def test_entrega_encontrada(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {"ID_entrega": ID_ENTREGA, "ID_orden_c": ID_ORDEN}
        cursor.fetchone.return_value = esperado

        resultado = OrdenEntregaModel().obtener_entrega(ID_ENTREGA)

        assert resultado == esperado
        assert "WHERE ei.ID_entrega_inventario = %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_ENTREGA,)
        cierra_recursos(db, cursor)

    def test_entrega_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert OrdenEntregaModel().obtener_entrega(ID_ENTREGA) is None

    def test_conexion_caida(self, conexion_caída):
        assert OrdenEntregaModel().obtener_entrega(ID_ENTREGA) is None

    def test_error_de_bd_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert OrdenEntregaModel().obtener_entrega(ID_ENTREGA) is None


class TestRegistrarEntrega:

    def test_sin_id_orden(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert OrdenEntregaModel().registrar_entrega() is False
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert OrdenEntregaModel(
            id_orden=ID_ORDEN, id_empleado=ID_EMPLEADO
        ).registrar_entrega() is False

    def test_orden_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = OrdenEntregaModel(
            id_orden=ID_ORDEN, id_empleado=ID_EMPLEADO
        ).registrar_entrega()

        assert resultado is False
        db.commit.assert_not_called()

    def test_orden_no_pendiente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_ORDEN, "Completada", ID_PROVEEDOR)

        resultado = OrdenEntregaModel(
            id_orden=ID_ORDEN, id_empleado=ID_EMPLEADO
        ).registrar_entrega()

        assert resultado is False
        db.commit.assert_not_called()

    def test_sin_detalles(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_ORDEN, "Pendiente", ID_PROVEEDOR)
        cursor.fetchall.return_value = []

        resultado = OrdenEntregaModel(
            id_orden=ID_ORDEN, id_empleado=ID_EMPLEADO
        ).registrar_entrega()

        assert resultado is False
        db.commit.assert_not_called()

    def test_producto_existente_actualiza_stock(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (ID_ORDEN, "Pendiente", ID_PROVEEDOR),  # orden
            ("ENT0000004",),  # _generar_id_entrega
            ("INV0001", 10),  # inventario existente
        ]
        cursor.fetchall.return_value = [DETALLE_EXISTENTE]
        entrega = OrdenEntregaModel(
            id_orden=ID_ORDEN,
            id_empleado=ID_EMPLEADO,
            recibido_por=RECIBIDO_POR,
        )

        resultado = entrega.registrar_entrega()

        assert resultado is True
        assert entrega.id_entrega == "ENT0000005"
        sentencias = [llamada.args[0] for llamada in cursor.execute.call_args_list]
        assert any(
            "INSERT INTO Entrega_inventario" in sql for sql in sentencias
        )
        assert any("INSERT INTO Abastece" in sql for sql in sentencias)
        assert any("Existencia = Existencia + %s" in sql for sql in sentencias)
        assert any(
            "SET Estado_orden_compra = 'Completada'" in sql for sql in sentencias
        )
        abastece = next(
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Abastece" in llamada.args[0]
        )
        assert abastece == ("ENT0000005", "INV0001", 2)
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_producto_nuevo_crea_inventario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (ID_ORDEN, "Pendiente", ID_PROVEEDOR),  # orden
            ("ENT0000004",),  # _generar_id_entrega
            None,  # inventario no existe
            (5,),  # MAX(ID_inventario)
        ]
        cursor.fetchall.return_value = [DETALLE_NUEVO]

        entrega = OrdenEntregaModel(
            id_orden=ID_ORDEN, id_empleado=ID_EMPLEADO
        )
        resultado = entrega.registrar_entrega()

        assert resultado is True
        assert entrega.id_entrega == "ENT0000005"
        inventario = next(
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Existencias_productos" in llamada.args[0]
        )
        assert inventario == ("6", "2", 3, 0.0)
        abastece = next(
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Abastece" in llamada.args[0]
        )
        assert abastece == ("ENT0000005", "6", 3)
        db.commit.assert_called_once()

    def test_calcula_costo_venta_con_ganancia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (ID_ORDEN, "Pendiente", ID_PROVEEDOR),
            ("ENT0000004",),
            None,
            (0,),
        ]
        cursor.fetchall.return_value = [("1", 1, "100.00")]

        OrdenEntregaModel(
            id_orden=ID_ORDEN, id_empleado=ID_EMPLEADO
        ).registrar_entrega()

        inventario = next(
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Existencias_productos" in llamada.args[0]
        )
        assert inventario[3] == 130.0

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (ID_ORDEN, "Pendiente", ID_PROVEEDOR),
            ("ENT0000004",),
            ("INV0001", 10),
        ]
        cursor.fetchall.return_value = [DETALLE_EXISTENTE]

        with patch("app.models.ordenes_entregas.Bitacora") as bitacora:
            OrdenEntregaModel(
                id_orden=ID_ORDEN,
                id_empleado=ID_EMPLEADO,
                recibido_por=RECIBIDO_POR,
                usuario_id="USR-001",
            ).registrar_entrega()

        bitacora.return_value.registrar.assert_called_once()

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (ID_ORDEN, "Pendiente", ID_PROVEEDOR),
            ("ENT0000004",),
            ("INV0001", 10),
        ]
        cursor.fetchall.return_value = [DETALLE_EXISTENTE]

        with patch("app.models.ordenes_entregas.Bitacora") as bitacora:
            OrdenEntregaModel(
                id_orden=ID_ORDEN, id_empleado=ID_EMPLEADO
            ).registrar_entrega()

        bitacora.assert_not_called()

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = OrdenEntregaModel(
            id_orden=ID_ORDEN, id_empleado=ID_EMPLEADO
        ).registrar_entrega()

        assert resultado is False
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestEditarEntrega:

    def test_sin_id_entrega(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert OrdenEntregaModel(fecha_entrega=FECHA_ENTREGA).editar_entrega() is False
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert OrdenEntregaModel(
            id_entrega=ID_ENTREGA, fecha_entrega=FECHA_ENTREGA
        ).editar_entrega() is False

    def test_entrega_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = OrdenEntregaModel(
            id_entrega=ID_ENTREGA, fecha_entrega=FECHA_ENTREGA
        ).editar_entrega()

        assert resultado is False
        db.commit.assert_not_called()

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_ENTREGA,)

        resultado = OrdenEntregaModel(
            id_entrega=ID_ENTREGA, fecha_entrega=FECHA_ENTREGA
        ).editar_entrega()

        assert resultado is True
        assert "UPDATE Entrega_inventario" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (FECHA_ENTREGA, ID_ENTREGA)
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_ENTREGA,)

        with patch("app.models.ordenes_entregas.Bitacora") as bitacora:
            OrdenEntregaModel(
                id_entrega=ID_ENTREGA,
                fecha_entrega=FECHA_ENTREGA,
                usuario_id="USR-001",
            ).editar_entrega()

        bitacora.return_value.registrar.assert_called_once()

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_ENTREGA,)

        with patch("app.models.ordenes_entregas.Bitacora") as bitacora:
            OrdenEntregaModel(
                id_entrega=ID_ENTREGA, fecha_entrega=FECHA_ENTREGA
            ).editar_entrega()

        bitacora.assert_not_called()

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = OrdenEntregaModel(
            id_entrega=ID_ENTREGA, fecha_entrega=FECHA_ENTREGA
        ).editar_entrega()

        assert resultado is False
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestEliminarEntrega:

    def test_sin_id_entrega(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert OrdenEntregaModel().eliminar_entrega() is False
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert OrdenEntregaModel(id_entrega=ID_ENTREGA).eliminar_entrega() is False

    def test_entrega_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert OrdenEntregaModel(
            id_entrega=ID_ENTREGA
        ).eliminar_entrega() is False
        db.commit.assert_not_called()

    def test_datos_validos_revierte_stock(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_ORDEN,)
        cursor.fetchall.return_value = [("INV0001", 2), ("INV0002", 3)]

        resultado = OrdenEntregaModel(id_entrega=ID_ENTREGA).eliminar_entrega()

        assert resultado is True
        sentencias = [llamada.args[0] for llamada in cursor.execute.call_args_list]
        assert sum("GREATEST(Existencia - %s, 0)" in sql for sql in sentencias) == 2
        assert any("DELETE FROM Abastece" in sql for sql in sentencias)
        assert any("DELETE FROM Entrega_inventario" in sql for sql in sentencias)
        assert any(
            "SET Estado_orden_compra = 'Pendiente'" in sql for sql in sentencias
        )
        assert ultima_sentencia(cursor) == (
            "\n                UPDATE Orden_compra \n"
            "                SET Estado_orden_compra = 'Pendiente'\n"
            "                WHERE ID_orden_compra = %s\n            "
        )
        assert cursor.execute.call_args.args[1] == (ID_ORDEN,)
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_sin_productos_entregados(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_ORDEN,)
        cursor.fetchall.return_value = []

        resultado = OrdenEntregaModel(id_entrega=ID_ENTREGA).eliminar_entrega()

        assert resultado is True
        sin_sentencia(cursor, "GREATEST")
        db.commit.assert_called_once()

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_ORDEN,)
        cursor.fetchall.return_value = []

        with patch("app.models.ordenes_entregas.Bitacora") as bitacora:
            OrdenEntregaModel(
                id_entrega=ID_ENTREGA, usuario_id="USR-001"
            ).eliminar_entrega()

        bitacora.return_value.registrar.assert_called_once()

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_ORDEN,)
        cursor.fetchall.return_value = []

        with patch("app.models.ordenes_entregas.Bitacora") as bitacora:
            OrdenEntregaModel(id_entrega=ID_ENTREGA).eliminar_entrega()

        bitacora.assert_not_called()

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = OrdenEntregaModel(id_entrega=ID_ENTREGA).eliminar_entrega()

        assert resultado is False
        db.rollback.assert_called_once()
        db.commit.assert_not_called()
