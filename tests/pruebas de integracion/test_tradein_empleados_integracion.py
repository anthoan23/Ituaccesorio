"""Pruebas de integración de TradeInEmpleados contra MySQL real."""
import random

import pytest

from app.models.tradein_empleados import TradeInEmpleados
from seed_helpers import (
    crear_cliente_temporal,
    crear_producto_temporal,
    eliminar_cliente_temporal,
    eliminar_producto_temporal,
    limpiar_bitacora_por_descripcion,
)


CLASE_TELEFONO = "1"
MARCA_IPHONE = "1"
EMPLEADO_ADMIN = "12345678"
USUARIO_ADMIN = "USR-001"
CEDULA_CLIENTE = None  # se asigna en fixture


def _cedula_aleatoria() -> str:
    return str(random.randint(10**7, 10**8 - 1))


def _imei_aleatorio() -> str:
    return str(random.randint(10**14, 10**15 - 1))


@pytest.fixture
def cliente_y_producto():
    """Cliente + producto temporal para trade-in. Limpia al final."""
    cedula = _cedula_aleatoria()
    id_producto = None
    crear_cliente_temporal(cedula, nombre="Cliente", apellido="TradeIn")
    try:
        id_producto = crear_producto_temporal(
            nombre="iPhone TradeIn", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
        )
        yield {"cliente_id": cedula, "id_producto": id_producto}
    finally:
        if id_producto:
            eliminar_producto_temporal(id_producto)
        eliminar_cliente_temporal(cedula)
        limpiar_bitacora_por_descripcion("trade-in")


def datos_tradein(**cambios):
    datos = {
        "empleado_id": EMPLEADO_ADMIN,
        "cliente_id": "12345678",
        "id_producto": "1",
        "id_equipo": _imei_aleatorio(),
        "valor_pagado": 300.0,
        "usuario_id": USUARIO_ADMIN,
        "color": "Negro",
        "capacidad": "128GB",
        "clave": "1234",
        "patron": "1-2-3-4",
    }
    datos.update(cambios)
    return datos


def _limpiar_tradein(trade_in_id: str, id_equipo: str) -> None:
    from app.models.database import conectar
    db = conectar().conexion1()
    if not db:
        return
    cursor = db.cursor()
    try:
        # Borrar tests asociados (y sus filas huérfanas en Test)
        cursor.execute(
            "SELECT ID_test FROM Test_realizados_trade_in WHERE ID_Trade_in = %s",
            (trade_in_id,),
        )
        ids_test = [f[0] for f in cursor.fetchall()]
        cursor.execute("DELETE FROM Test_realizados_trade_in WHERE ID_Trade_in = %s", (trade_in_id,))
        for id_test in ids_test:
            cursor.execute("DELETE FROM Test WHERE ID_test = %s", (id_test,))
        cursor.execute("DELETE FROM Fotos_trade_in WHERE ID_Trade_in = %s", (trade_in_id,))
        cursor.execute("DELETE FROM Trade_in WHERE ID_Trade_in = %s", (trade_in_id,))
        cursor.execute("DELETE FROM Equipo WHERE ID_equipo = %s", (id_equipo,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


# ==================== VALIDACIONES ====================

class TestValidarDatosTradeIn:

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"empleado_id": ""},
                "Empleado no identificado.",
                id="empleado-vacio",
            ),
            pytest.param(
                {"empleado_id": "12345"},
                "El campo Empleado debe tener al menos 6 dígitos.",
                id="empleado-demasiado-corto",
            ),
            pytest.param(
                {"cliente_id": ""},
                "El campo Cliente es obligatorio.",
                id="cliente-vacio",
            ),
            pytest.param(
                {"cliente_id": "12345"},
                "El campo Cliente debe tener al menos 6 dígitos.",
                id="cliente-demasiado-corto",
            ),
            pytest.param(
                {"id_producto": ""},
                "El campo Producto/Modelo es obligatorio.",
                id="producto-vacio",
            ),
            pytest.param(
                {"id_producto": "P" * 11},
                "El campo Producto no puede tener más de 10 caracteres.",
                id="producto-demasiado-largo",
            ),
            pytest.param(
                {"id_equipo": ""},
                "El campo IMEI/ID del equipo es obligatorio.",
                id="imei-vacio",
            ),
            pytest.param(
                {"id_equipo": "1234567"},
                "El campo IMEI debe tener al menos 8 dígitos.",
                id="imei-demasiado-corto",
            ),
            pytest.param(
                {"id_equipo": "1" * 17},
                "El campo IMEI no puede tener más de 16 dígitos.",
                id="imei-demasiado-largo",
            ),
            pytest.param(
                {"valor_pagado": ""},
                "El campo Valor pagado es obligatorio.",
                id="valor-vacio",
            ),
            pytest.param(
                {"valor_pagado": -5},
                "El campo Valor pagado debe ser mayor o igual a 0.",
                id="valor-negativo",
            ),
            pytest.param(
                {"valor_pagado": "abc"},
                "El campo Valor pagado debe ser un número decimal válido con hasta 2 decimales.",
                id="valor-no-numerico",
            ),
            pytest.param(
                {"color": "C" * 21},
                "El campo Color no puede tener más de 20 caracteres.",
                id="color-demasiado-largo",
            ),
            pytest.param(
                {"capacidad": "C" * 21},
                "El campo Capacidad no puede tener más de 20 caracteres.",
                id="capacidad-demasiado-larga",
            ),
            pytest.param(
                {"clave": "abc"},
                "El campo Clave numérica solo puede contener números.",
                id="clave-no-numerica",
            ),
        ],
    )
    def test_datos_invalidos(self, cambios, esperado):
        resultado = TradeInEmpleados(
            **datos_tradein(**cambios)
        ).registrar_trade_in()
        assert resultado == {"success": False, "error": esperado}


# ==================== REGISTRAR TRADE-IN ====================

class TestRegistrarTradeIn:

    def test_tradein_valido(self, cliente_y_producto):
        info = cliente_y_producto
        trade_in_id = None
        id_equipo = _imei_aleatorio()
        try:
            resultado = TradeInEmpleados(
                **datos_tradein(
                    id_equipo=id_equipo,
                    cliente_id=info["cliente_id"],
                    id_producto=info["id_producto"],
                )
            ).registrar_trade_in()

            assert resultado["success"] is True
            assert resultado["message"] == "Trade-in registrado correctamente"
            trade_in_id = resultado["trade_in_id"]
            assert trade_in_id.startswith("TRD")
            assert resultado["equipo_id"] == id_equipo
            assert resultado["tests_registrados"] == 0

            # Verificar que el trade-in existe en BD
            from app.models.database import conectar
            db = conectar().conexion1()
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                "SELECT ID_empleado, ID_cliente, ID_equipo, cotizacion "
                "FROM Trade_in WHERE ID_Trade_in = %s",
                (trade_in_id,),
            )
            fila = cursor.fetchone()
            cursor.close()
            db.close()

            assert fila is not None
            assert fila["ID_empleado"] == int(EMPLEADO_ADMIN)
            assert fila["ID_cliente"] == info["cliente_id"]
            assert fila["ID_equipo"] == id_equipo
            assert float(fila["cotizacion"]) == 300.0
        finally:
            if trade_in_id:
                _limpiar_tradein(trade_in_id, id_equipo)

    def test_tradein_con_tests(self, cliente_y_producto):
        info = cliente_y_producto
        trade_in_id = None
        id_equipo = _imei_aleatorio()
        try:
            resultado = TradeInEmpleados(
                **datos_tradein(
                    id_equipo=id_equipo,
                    cliente_id=info["cliente_id"],
                    id_producto=info["id_producto"],
                )
            ).registrar_trade_in(
                tests=[
                    {"nombre": "Pantalla", "resultado": "Funciona"},
                    {"nombre": "Batería", "resultado": "No funciona"},
                ]
            )

            assert resultado["success"] is True
            trade_in_id = resultado["trade_in_id"]
            assert resultado["tests_registrados"] == 2

            # Verificar tests en BD
            from app.models.database import conectar
            db = conectar().conexion1()
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                "SELECT t.Nombre_test, t.Resultado_test FROM Test t "
                "JOIN Test_realizados_trade_in tr ON t.ID_test = tr.ID_test "
                "WHERE tr.ID_Trade_in = %s ORDER BY t.Nombre_test",
                (trade_in_id,),
            )
            tests = cursor.fetchall()
            cursor.close()
            db.close()

            assert len(tests) == 2
            assert {t["Nombre_test"] for t in tests} == {"Pantalla", "Batería"}
        finally:
            if trade_in_id:
                _limpiar_tradein(trade_in_id, id_equipo)

    def test_tests_invalidos(self, cliente_y_producto):
        info = cliente_y_producto
        resultado = TradeInEmpleados(
            **datos_tradein(
                cliente_id=info["cliente_id"],
                id_producto=info["id_producto"],
            )
        ).registrar_trade_in(
            tests=[{"nombre": "Pantalla", "resultado": "Inexistente"}]
        )
        assert resultado == {
            "success": False,
            "error": "El resultado 'Inexistente' no es válido para el test 'Pantalla'.",
        }

    def test_tests_sin_nombre(self, cliente_y_producto):
        info = cliente_y_producto
        resultado = TradeInEmpleados(
            **datos_tradein(
                cliente_id=info["cliente_id"],
                id_producto=info["id_producto"],
            )
        ).registrar_trade_in(
            tests=[{"nombre": "", "resultado": "Funciona"}]
        )
        assert resultado == {
            "success": False,
            "error": "El test #1 debe tener un nombre.",
        }

    def test_tests_sin_resultado(self, cliente_y_producto):
        info = cliente_y_producto
        resultado = TradeInEmpleados(
            **datos_tradein(
                cliente_id=info["cliente_id"],
                id_producto=info["id_producto"],
            )
        ).registrar_trade_in(
            tests=[{"nombre": "Pantalla", "resultado": ""}]
        )
        assert resultado == {
            "success": False,
            "error": "El test 'Pantalla' debe tener un resultado.",
        }


# ==================== LISTAR ====================

class TestObtenerTradeIns:

    def test_devuelve_lista(self):
        assert isinstance(TradeInEmpleados().obtener_trade_ins(), list)


class TestObtenerTradeInsPorCliente:

    def test_sin_cliente_devuelve_vacio(self):
        assert TradeInEmpleados().obtener_trade_ins_por_cliente() == []

    def test_por_cliente_valido(self, cliente_y_producto):
        info = cliente_y_producto
        resultado = TradeInEmpleados(
            cliente_id=info["cliente_id"]
        ).obtener_trade_ins_por_cliente()
        assert isinstance(resultado, list)


# ==================== ACTUALIZAR ====================

class TestActualizarTradeIn:

    def test_actualiza_tradein_existente(self, cliente_y_producto):
        info = cliente_y_producto
        trade_in_id = None
        id_equipo = _imei_aleatorio()
        try:
            resultado = TradeInEmpleados(
                **datos_tradein(
                    id_equipo=id_equipo,
                    cliente_id=info["cliente_id"],
                    id_producto=info["id_producto"],
                )
            ).registrar_trade_in()
            trade_in_id = resultado["trade_in_id"]

            actualizado = TradeInEmpleados(
                **datos_tradein(
                    trade_in_id=trade_in_id,
                    id_equipo=id_equipo,
                    cliente_id=info["cliente_id"],
                    id_producto=info["id_producto"],
                    valor_pagado=350.0,
                )
            ).actualizar_trade_in()

            assert actualizado["success"] is True
            assert actualizado["message"] == "Trade-in actualizado correctamente"
        finally:
            if trade_in_id:
                _limpiar_tradein(trade_in_id, id_equipo)


# ==================== ELIMINAR ====================

class TestEliminarTradeIn:

    def test_elimina_tradein(self, cliente_y_producto):
        info = cliente_y_producto
        trade_in_id = None
        id_equipo = _imei_aleatorio()
        try:
            resultado = TradeInEmpleados(
                **datos_tradein(
                    id_equipo=id_equipo,
                    cliente_id=info["cliente_id"],
                    id_producto=info["id_producto"],
                )
            ).registrar_trade_in()
            trade_in_id = resultado["trade_in_id"]

            eliminado = TradeInEmpleados(
                trade_in_id=trade_in_id
            ).eliminar_trade_in()

            assert eliminado == {
                "success": True, "message": "Trade-in eliminado correctamente"
            }

            from app.models.database import conectar
            db = conectar().conexion1()
            cursor = db.cursor()
            cursor.execute(
                "SELECT 1 FROM Trade_in WHERE ID_Trade_in = %s", (trade_in_id,)
            )
            assert cursor.fetchone() is None
            cursor.close()
            db.close()

            trade_in_id = None  # ya fue eliminado, no limpiar de nuevo
        finally:
            _limpiar_tradein(trade_in_id, id_equipo) if trade_in_id else None

    def test_sin_id(self):
        resultado = TradeInEmpleados().eliminar_trade_in()
        assert resultado == {"success": False, "error": "ID de trade-in no especificado."}


# ==================== ESTADÍSTICAS ====================

class TestEstadisticas:

    def test_devuelve_estructura(self):
        stats = TradeInEmpleados().obtener_estadisticas()
        assert "total" in stats
        assert "valor_total" in stats
        assert "equipos" in stats
        assert isinstance(stats["valor_total"], float)


# ==================== CATÁLOGOS ====================

class TestProductosDisponibles:

    def test_devuelve_lista(self):
        assert isinstance(
            TradeInEmpleados().obtener_productos_disponibles(), list
        )


class TestClientes:

    def test_sin_q_devuelve_lista(self):
        assert isinstance(TradeInEmpleados().obtener_clientes(), list)

    def test_con_q_valido(self, cliente_y_producto):
        info = cliente_y_producto
        resultado = TradeInEmpleados().obtener_clientes(q=info["cliente_id"])
        assert any(c["id"] == info["cliente_id"] for c in resultado)


class TestVerificarEquipoExistente:

    def test_equipo_inexistente(self):
        assert TradeInEmpleados(
            id_equipo="999999999999999"
        ).verificar_equipo_existente() is None

    def test_sin_id_equipo(self):
        assert TradeInEmpleados().verificar_equipo_existente() is None

    def test_imei_invalido(self):
        assert TradeInEmpleados(
            id_equipo="12345"
        ).verificar_equipo_existente() is None