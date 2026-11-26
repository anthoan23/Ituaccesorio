"""Pruebas de integración del ciclo de vida de Trade-in contra MySQL real."""
from decimal import Decimal

from app.models.database import conectar
from app.models.equipo import Equipo
from app.models.tradein_empleados import TradeInEmpleados

ID_EMPLEADO = "12345678"
ID_CLIENTE = "91000001"
ID_PRODUCTO = "103"
ID_EQUIPO = "99000000990001"

FOTO_1 = "/static/img/tradein/integracion_1.jpg"
FOTO_2 = "/static/img/tradein/integracion_2.jpg"
NOMBRE_TEST_1 = "QA trade-in pantalla"
NOMBRE_TEST_2 = "QA trade-in batería"
NOMBRE_TEST_ACTUALIZADO = "QA trade-in altavoz"


def limpiar_datos_temporales():
    """Elimina los datos exclusivos de esta prueba, incluso tras una interrupción."""
    db = conectar().conexion1()
    if not db:
        raise RuntimeError("No se pudo conectar a la base de datos de integración.")

    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT ID_Trade_in FROM Trade_in WHERE ID_equipo = %s",
            (ID_EQUIPO,),
        )
        ids_trade_in = [fila[0] for fila in cursor.fetchall()]

        if ids_trade_in:
            marcadores = ", ".join(["%s"] * len(ids_trade_in))
            cursor.execute(
                f"DELETE FROM Fotos_trade_in WHERE ID_Trade_in IN ({marcadores})",
                ids_trade_in,
            )
            cursor.execute(
                f"DELETE FROM Test_realizados_trade_in "
                f"WHERE ID_Trade_in IN ({marcadores})",
                ids_trade_in,
            )
            cursor.execute(
                f"DELETE FROM Trade_in WHERE ID_Trade_in IN ({marcadores})",
                ids_trade_in,
            )

        cursor.execute(
            "SELECT ID_test FROM Test WHERE Nombre_test IN (%s, %s, %s)",
            (NOMBRE_TEST_1, NOMBRE_TEST_2, NOMBRE_TEST_ACTUALIZADO),
        )
        ids_tests = [fila[0] for fila in cursor.fetchall()]
        if ids_tests:
            marcadores = ", ".join(["%s"] * len(ids_tests))
            cursor.execute(
                f"DELETE FROM Test_realizados_trade_in "
                f"WHERE ID_test IN ({marcadores})",
                ids_tests,
            )
            cursor.execute(
                f"DELETE FROM Test WHERE ID_test IN ({marcadores})",
                ids_tests,
            )

        cursor.execute("DELETE FROM Equipo WHERE ID_equipo = %s", (ID_EQUIPO,))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()
        db.close()


def test_ciclo_de_vida_trade_in_con_fotos_y_tests():
    limpiar_datos_temporales()
    try:
        assert (
            Equipo(
                ID_equipo=ID_EQUIPO,
                ID_producto=ID_PRODUCTO,
                Color="Negro",
                Capacidad="128GB",
                Clave=1234,
            ).registrar_equipo()
            == f"Equipo {ID_EQUIPO} registrado exitosamente."
        )
        equipo = Equipo(ID_equipo=ID_EQUIPO).Consultar_equipo_por_id()
        assert equipo["ID_producto"] == ID_PRODUCTO
        assert equipo["Color"] == "Negro"

        trade_in = TradeInEmpleados(
            empleado_id=ID_EMPLEADO,
            cliente_id=ID_CLIENTE,
            id_producto=ID_PRODUCTO,
            id_equipo=ID_EQUIPO,
            valor_pagado=200.00,
        )
        registro = trade_in.registrar_trade_in(
            fotos=[FOTO_1, FOTO_2],
            tests=[
                {"nombre": NOMBRE_TEST_1, "resultado": "Funciona"},
                {"nombre": NOMBRE_TEST_2, "resultado": "No funciona"},
            ],
        )

        assert registro["success"] is True, registro
        assert registro["trade_in_id"] == trade_in.trade_in_id
        assert registro["tests_registrados"] == 2
        id_trade_in = registro["trade_in_id"]

        assert (
            Equipo(ID_equipo=ID_EQUIPO).eliminar_equipo()
            == f"No se puede eliminar el equipo {ID_EQUIPO} "
            "porque tiene trade-ins asociados."
        )

        detalle = TradeInEmpleados(trade_in_id=id_trade_in).obtener_detalle_trade_in()
        assert detalle["id"] == id_trade_in
        assert detalle["empleado_id"] == int(ID_EMPLEADO)
        assert detalle["cliente_id"] == ID_CLIENTE
        assert detalle["equipo_id"] == ID_EQUIPO
        assert detalle["producto_id"] == ID_PRODUCTO
        assert detalle["valor_pagado"] == Decimal("200.00")
        assert detalle["Color"] == "Negro"
        assert detalle["Capacidad"] == "128GB"

        fotos = TradeInEmpleados(
            trade_in_id=id_trade_in
        ).obtener_fotos_trade_in()
        assert [foto["url"] for foto in fotos] == [FOTO_1, FOTO_2]

        tests = TradeInEmpleados(
            trade_in_id=id_trade_in
        ).obtener_tests_trade_in()
        assert {
            (test["nombre"], test["resultado"]) for test in tests
        } == {
            (NOMBRE_TEST_1, "Funciona"),
            (NOMBRE_TEST_2, "No funciona"),
        }

        trade_listado = next(
            trade
            for trade in TradeInEmpleados().obtener_trade_ins()
            if trade["id"] == id_trade_in
        )
        assert trade_listado["cliente_id"] == ID_CLIENTE
        assert trade_listado["fotos"] == fotos
        assert {
            test["nombre"] for test in trade_listado["tests"]
        } == {NOMBRE_TEST_1, NOMBRE_TEST_2}

        historial_cliente = TradeInEmpleados(
            cliente_id=ID_CLIENTE
        ).obtener_trade_ins_por_cliente()
        assert any(trade["id"] == id_trade_in for trade in historial_cliente)

        actualizacion = TradeInEmpleados(
            trade_in_id=id_trade_in,
            empleado_id=ID_EMPLEADO,
            cliente_id=ID_CLIENTE,
            id_producto=ID_PRODUCTO,
            id_equipo=ID_EQUIPO,
            valor_pagado=275.50,
            color="Azul",
            capacidad="256GB",
        ).actualizar_trade_in(
            fotos_eliminar=[FOTO_1],
            tests=[
                {
                    "nombre": NOMBRE_TEST_ACTUALIZADO,
                    "resultado": "Sin revisar",
                }
            ],
        )
        assert actualizacion["success"] is True
        assert actualizacion["tests_registrados"] == 1

        detalle_actualizado = TradeInEmpleados(
            trade_in_id=id_trade_in
        ).obtener_detalle_trade_in()
        assert detalle_actualizado["valor_pagado"] == Decimal("275.50")
        assert detalle_actualizado["Color"] == "Azul"
        assert detalle_actualizado["Capacidad"] == "256GB"
        assert [
            foto["url"]
            for foto in TradeInEmpleados(
                trade_in_id=id_trade_in
            ).obtener_fotos_trade_in()
        ] == [FOTO_2]
        assert [
            (test["nombre"], test["resultado"])
            for test in TradeInEmpleados(
                trade_in_id=id_trade_in
            ).obtener_tests_trade_in()
        ] == [(NOMBRE_TEST_ACTUALIZADO, "Sin revisar")]

        eliminacion = TradeInEmpleados(
            trade_in_id=id_trade_in
        ).eliminar_trade_in()
        assert eliminacion == {
            "success": True,
            "message": "Trade-in eliminado correctamente",
        }
        assert TradeInEmpleados(
            trade_in_id=id_trade_in
        ).obtener_detalle_trade_in() == {}
        assert TradeInEmpleados(
            trade_in_id=id_trade_in
        ).obtener_fotos_trade_in() == []
        assert TradeInEmpleados(
            trade_in_id=id_trade_in
        ).obtener_tests_trade_in() == []
        assert (
            Equipo(ID_equipo=ID_EQUIPO).eliminar_equipo()
            == f"Equipo {ID_EQUIPO} eliminado correctamente."
        )
    finally:
        limpiar_datos_temporales()
