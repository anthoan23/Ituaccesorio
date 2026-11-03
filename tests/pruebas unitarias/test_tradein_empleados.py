"""Pruebas unitarias de la clase TradeInEmpleados
(app.models.tradein_empleados).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.
"""
import re
from unittest.mock import MagicMock, patch

import pytest

from app.models.tradein_empleados import TradeInEmpleados
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

# ==================== Datos de frontera ====================
TRADE_IN_ID = "TRD000001"
TRADE_IN_MAXIMO = "TRD999999"

EMPLEADO_MINIMO = "123456"  # 6 dígitos (mínimo)
EMPLEADO_MAXIMO = "12345678"  # 8 dígitos (máximo)

CLIENTE_MINIMO = "123456"
CLIENTE_MAXIMO = "12345678"

ID_PRODUCTO = "1"
ID_EQUIPO = "12345678"  # 8 dígitos (mínimo del IMEI)
IMEI_MAXIMO = "1234567890123456"  # 16 dígitos (máximo)

VALOR_MINIMO = "0.00"
VALOR_MAXIMO = "99999999.99"

COLOR = "Negro"
CAPACIDAD = "128GB"
CLAVE = "1234"
PATRON = "patron de desbloqueo"

TEST_VALIDO = {"nombre": "Pantalla", "resultado": "Funciona"}


def crear_trade_in(**cambios):
    """Crea un trade-in con datos válidos y permite sobreescribir campos."""
    datos = {
        "trade_in_id": TRADE_IN_ID,
        "empleado_id": EMPLEADO_MAXIMO,
        "cliente_id": CLIENTE_MAXIMO,
        "id_producto": ID_PRODUCTO,
        "id_equipo": ID_EQUIPO,
        "valor_pagado": 100.0,
    }
    datos.update(cambios)
    return TradeInEmpleados(**datos)


class TestValidarDatosTradeIn:

    def test_datos_validos(self):
        trade = crear_trade_in(
            color=COLOR,
            capacidad=CAPACIDAD,
            clave=CLAVE,
            patron=PATRON,
        )

        assert trade._validar_datos_trade_in() is None
        assert trade.valor_pagado == 100.0
        assert trade.color == COLOR
        assert trade.capacidad == CAPACIDAD
        assert trade.clave == CLAVE
        assert trade.patron == PATRON

    def test_valor_pagado_con_coma_no_es_convertible(self):
        trade = crear_trade_in(valor_pagado="1500,50")

        assert trade._validar_datos_trade_in() == (
            "El valor pagado debe ser un número válido."
        )

    def test_campos_opcionales_vacios_quedan_en_none(self):
        trade = crear_trade_in(color="", capacidad="", clave="", patron="")

        assert trade._validar_datos_trade_in() is None
        assert trade.color is None
        assert trade.capacidad is None
        assert trade.clave is None
        assert trade.patron is None

    def test_requiere_id_si_se_solicita(self):
        trade = crear_trade_in(trade_in_id=None)

        assert trade._validar_datos_trade_in(requiere_id=True) == (
            "ID de trade-in no especificado."
        )

    def test_id_trade_in_con_formato_invalido(self):
        trade = crear_trade_in(trade_in_id="TRD#1")

        assert trade._validar_datos_trade_in(requiere_id=True) == (
            "El campo ID de Trade-in solo puede contener letras, números, "
            "acentos y espacios."
        )

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"empleado_id": None},
                "Empleado no identificado.",
                id="empleado-vacio",
            ),
            pytest.param(
                {"empleado_id": "12345"},
                "El campo Empleado debe tener al menos 6 dígitos.",
                id="empleado-corto",
            ),
            pytest.param(
                {"empleado_id": "123456789"},
                "El campo Empleado no puede tener más de 8 dígitos.",
                id="empleado-largo",
            ),
            pytest.param(
                {"empleado_id": "12345a"},
                "El campo Empleado solo puede contener números.",
                id="empleado-no-numerico",
            ),
            pytest.param(
                {"cliente_id": None},
                "El campo Cliente es obligatorio.",
                id="cliente-vacio",
            ),
            pytest.param(
                {"cliente_id": "12345"},
                "El campo Cliente debe tener al menos 6 dígitos.",
                id="cliente-corto",
            ),
            pytest.param(
                {"cliente_id": "123456789"},
                "El campo Cliente no puede tener más de 8 dígitos.",
                id="cliente-largo",
            ),
            pytest.param(
                {"id_producto": None},
                "El campo Producto/Modelo es obligatorio.",
                id="producto-vacio",
            ),
            pytest.param(
                {"id_producto": "1#"},
                "El campo Producto solo puede contener letras, números, "
                "acentos y espacios.",
                id="producto-invalido",
            ),
            pytest.param(
                {"id_equipo": None},
                "El campo IMEI/ID del equipo es obligatorio.",
                id="equipo-vacio",
            ),
            pytest.param(
                {"id_equipo": "1234567"},
                "El campo IMEI debe tener al menos 8 dígitos.",
                id="equipo-corto",
            ),
            pytest.param(
                {"id_equipo": "12345678901234567"},
                "El campo IMEI no puede tener más de 16 dígitos.",
                id="equipo-largo",
            ),
            pytest.param(
                {"valor_pagado": None},
                "El campo Valor pagado es obligatorio.",
                id="valor-vacio",
            ),
            pytest.param(
                {"valor_pagado": "-5"},
                "El campo Valor pagado debe ser un número decimal válido "
                "con hasta 2 decimales.",
                id="valor-negativo",
            ),
            pytest.param(
                {"valor_pagado": "1.234"},
                "El campo Valor pagado debe ser un número decimal válido "
                "con hasta 2 decimales.",
                id="valor-tres-decimales",
            ),
            pytest.param(
                {"valor_pagado": "100000000"},
                "El campo Valor pagado debe ser menor o igual a 99999999.99.",
                id="valor-demasiado-alto",
            ),
            pytest.param(
                {"color": "Rojo!"},
                "El campo Color solo puede contener letras, espacios, "
                "acentos y ñ.",
                id="color-invalido",
            ),
            pytest.param(
                {"capacidad": "128-GB"},
                "El campo Capacidad solo puede contener letras, números "
                "y espacios.",
                id="capacidad-invalida",
            ),
            pytest.param(
                {"clave": "12ab"},
                "El campo Clave numérica solo puede contener números.",
                id="clave-no-numerica",
            ),
            pytest.param(
                {"patron": "patron#1"},
                "El campo Patrón no puede contener caracteres especiales.",
                id="patron-invalido",
            ),
        ],
    )
    def test_validaciones_de_campos(self, cambios, esperado):
        assert crear_trade_in(**cambios)._validar_datos_trade_in() == esperado


class TestParsearYValidarTests:

    def test_sin_tests(self):
        assert TradeInEmpleados()._parsear_y_validar_tests(None) == (None, [])
        assert TradeInEmpleados()._parsear_y_validar_tests([]) == (None, [])
        assert TradeInEmpleados()._parsear_y_validar_tests("") == (None, [])

    def test_json_valido(self):
        error, tests = TradeInEmpleados()._parsear_y_validar_tests(
            '[{"nombre": "Pantalla", "resultado": "Funciona"}]'
        )

        assert error is None
        assert tests == [TEST_VALIDO]

    def test_json_invalido_devuelve_lista_vacia(self):
        assert TradeInEmpleados()._parsear_y_validar_tests("{no-json") == (None, [])

    def test_no_es_lista(self):
        assert TradeInEmpleados()._parsear_y_validar_tests(123) == (
            "El campo tests debe ser una lista.",
            [],
        )

    def test_elemento_no_es_diccionario(self):
        assert TradeInEmpleados()._parsear_y_validar_tests(["Pantalla"]) == (
            "El test #1 no tiene un formato válido.",
            [],
        )

    def test_test_sin_nombre(self):
        assert TradeInEmpleados()._parsear_y_validar_tests(
            [{"resultado": "Funciona"}]
        ) == ("El test #1 debe tener un nombre.", [])

    def test_test_sin_resultado(self):
        assert TradeInEmpleados()._parsear_y_validar_tests(
            [{"nombre": "Pantalla"}]
        ) == ("El test 'Pantalla' debe tener un resultado.", [])

    def test_resultado_no_permitido(self):
        assert TradeInEmpleados()._parsear_y_validar_tests(
            [{"nombre": "Pantalla", "resultado": "Regular"}]
        ) == (
            "El resultado 'Regular' no es válido para el test 'Pantalla'.",
            [],
        )

    @pytest.mark.parametrize(
        "resultado",
        [
            pytest.param("Funciona", id="funciona"),
            pytest.param("No funciona", id="no-funciona"),
            pytest.param("No aplica", id="no-aplica"),
            pytest.param("Pendiente", id="pendiente"),
            pytest.param("Sin revisar", id="sin-revisar"),
        ],
    )
    def test_resultados_permitidos(self, resultado):
        error, tests = TradeInEmpleados()._parsear_y_validar_tests(
            [{"nombre": "Pantalla", "resultado": resultado}]
        )

        assert error is None
        assert tests[0]["resultado"] == resultado


class TestGenerarIdTradeIn:

    def test_sin_conexion(self, conexion_caída):
        assert TradeInEmpleados()._generar_id_trade_in() == "TRD000001"

    def test_sin_registros_previos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert TradeInEmpleados()._generar_id_trade_in() == "TRD000001"
        assert "MAX(ID_Trade_in)" in ultima_sentencia(cursor)
        cierra_recursos(db, cursor)

    def test_con_registros_previos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("TRD000042",)

        assert TradeInEmpleados()._generar_id_trade_in() == "TRD000043"

    def test_ultimo_id_con_formato_invalido(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("ABC",)

        assert TradeInEmpleados()._generar_id_trade_in() == "TRD000001"

    def test_error_de_bd_devuelve_id_con_fecha(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = TradeInEmpleados()._generar_id_trade_in()

        assert re.match(r"^TRD\d{14}$", resultado)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        TradeInEmpleados()._generar_id_trade_in()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestGenerarIdFotoTradeIn:

    def test_sin_conexion(self, conexion_caída):
        assert TradeInEmpleados()._generar_id_foto_trade_in() == "FTI0000001"

    def test_sin_registros_previos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert TradeInEmpleados()._generar_id_foto_trade_in() == "FTI0000001"
        assert "MAX(ID_foto_trade_in)" in ultima_sentencia(cursor)
        cierra_recursos(db, cursor)

    def test_con_registros_previos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("FTI0000042",)

        assert TradeInEmpleados()._generar_id_foto_trade_in() == "FTI0000043"

    def test_ultimo_id_con_formato_invalido(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("ABC",)

        assert TradeInEmpleados()._generar_id_foto_trade_in() == "FTI0000001"

    def test_error_de_bd_devuelve_id_con_fecha(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = TradeInEmpleados()._generar_id_foto_trade_in()

        assert re.match(r"^FTI\d{14}$", resultado)


class TestRegistrarTradeIn:

    def test_error_de_validacion(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = crear_trade_in(empleado_id=None).registrar_trade_in()

        assert resultado == {"success": False, "error": "Empleado no identificado."}
        cursor.execute.assert_not_called()

    def test_error_en_tests(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = crear_trade_in().registrar_trade_in(
            tests=[{"nombre": "Pantalla", "resultado": "Regular"}]
        )

        assert resultado == {
            "success": False,
            "error": "El resultado 'Regular' no es válido para el test 'Pantalla'.",
        }
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert crear_trade_in().registrar_trade_in() == {
            "success": False,
            "error": "Error de conexión a la base de datos",
        }

    def test_equipo_nuevo_registrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            None,  # equipo no existe
            ("TRD000005",),  # MAX(ID_Trade_in)
        ]

        with patch("app.models.tradein_empleados.Equipo") as equipo, patch(
            "app.models.tradein_empleados.Bitacora"
        ) as bitacora:
            equipo.return_value.registrar_equipo.return_value = (
                "Equipo registrado exitosamente"
            )
            resultado = crear_trade_in(usuario_id="USR-001").registrar_trade_in()

        assert resultado == {
            "success": True,
            "message": "Trade-in registrado correctamente",
            "trade_in_id": "TRD000006",
            "equipo_id": ID_EQUIPO,
            "tests_registrados": 0,
        }
        insert = next(
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Trade_in" in llamada.args[0]
        )
        assert insert[:4] == (
            "TRD000006",
            EMPLEADO_MAXIMO,
            CLIENTE_MAXIMO,
            ID_EQUIPO,
        )
        assert insert[4] == 0
        assert insert[6] == 100.0
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_error_al_registrar_equipo_nuevo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with patch("app.models.tradein_empleados.Equipo") as equipo:
            equipo.return_value.registrar_equipo.return_value = (
                "Error al registrar el equipo"
            )
            resultado = crear_trade_in().registrar_trade_in()

        assert resultado == {
            "success": False,
            "error": "Error al registrar el equipo",
        }
        db.commit.assert_not_called()

    def test_equipo_existente_con_otro_producto_se_actualiza(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (ID_EQUIPO, "2"),  # equipo existe con otro producto
            ("TRD000005",),
        ]

        with patch("app.models.tradein_empleados.Equipo") as equipo:
            equipo.return_value.actualizar_equipo.return_value = (
                "Equipo actualizado exitosamente"
            )
            resultado = crear_trade_in().registrar_trade_in()

        assert resultado["success"] is True
        equipo.assert_called_once_with(
            ID_equipo=ID_EQUIPO,
            ID_producto=ID_PRODUCTO,
            Color=None,
            Capacidad=None,
            Clave=None,
            Patron=None,
        )
        equipo.return_value.actualizar_equipo.assert_called_once()

    def test_equipo_existente_mismo_producto_sin_datos_no_actualiza(
        self, conexion_falsa
    ):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (ID_EQUIPO, ID_PRODUCTO),
            ("TRD000005",),
        ]

        with patch("app.models.tradein_empleados.Equipo") as equipo:
            resultado = crear_trade_in().registrar_trade_in()

        assert resultado["success"] is True
        equipo.assert_not_called()

    def test_equipo_existente_mismo_producto_con_color_actualiza(
        self, conexion_falsa
    ):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (ID_EQUIPO, ID_PRODUCTO),
            ("TRD000005",),
        ]

        with patch("app.models.tradein_empleados.Equipo") as equipo:
            equipo.return_value.actualizar_equipo.return_value = (
                "Equipo actualizado exitosamente"
            )
            resultado = crear_trade_in(color=COLOR).registrar_trade_in()

        assert resultado["success"] is True
        equipo.assert_called_once_with(
            ID_equipo=ID_EQUIPO,
            ID_producto=None,
            Color=COLOR,
            Capacidad=None,
            Clave=None,
            Patron=None,
        )

    def test_registra_fotos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            None,
            ("TRD000005",),
            ("FTI0000010",),
            ("FTI0000011",),
        ]

        with patch("app.models.tradein_empleados.Equipo") as equipo:
            equipo.return_value.registrar_equipo.return_value = "ok"
            resultado = crear_trade_in().registrar_trade_in(
                fotos=["/static/foto1.jpg", "/static/foto2.jpg"]
            )

        assert resultado["success"] is True
        inserts = [
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Fotos_trade_in" in llamada.args[0]
        ]
        assert inserts == [
            ("FTI0000011", "TRD000006", "/static/foto1.jpg"),
            ("FTI0000012", "TRD000006", "/static/foto2.jpg"),
        ]

    def test_registra_tests(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            None,
            ("TRD000005",),
            ("TST000002",),
        ]

        with patch("app.models.tradein_empleados.Equipo") as equipo:
            equipo.return_value.registrar_equipo.return_value = "ok"
            resultado = crear_trade_in().registrar_trade_in(
                tests=[
                    {"nombre": "Pantalla", "resultado": "Funciona"},
                    {"nombre": "Batería", "resultado": "No funciona"},
                ]
            )

        assert resultado["tests_registrados"] == 2
        inserts_test = [
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Test " in llamada.args[0]
        ]
        assert inserts_test == [
            ("TST000003", 1, "Pantalla", "Funciona"),
            ("TST000004", 1, "Batería", "No funciona"),
        ]
        relaciones = [
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Test_realizados_trade_in" in llamada.args[0]
        ]
        assert relaciones == [
            ("TRD000006", "TST000003"),
            ("TRD000006", "TST000004"),
        ]

    def test_consecutivo_de_test_con_formato_invalido(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            None,
            ("TRD000005",),
            ("ABC",),
        ]

        with patch("app.models.tradein_empleados.Equipo") as equipo:
            equipo.return_value.registrar_equipo.return_value = "ok"
            resultado = crear_trade_in().registrar_trade_in(tests=[TEST_VALIDO])

        assert resultado["tests_registrados"] == 1
        insert_test = next(
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Test " in llamada.args[0]
        )
        assert insert_test[0] == "TST000001"

    def test_error_al_registrar_tests_no_aborta(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            None,
            ("TRD000005",),
            ("TST000002",),
        ]

        def ejecutar(sql, params=None):
            if "SELECT MAX(ID_test)" in sql:
                raise Exception("fallo en tests")
            return None

        cursor.execute.side_effect = ejecutar

        with patch("app.models.tradein_empleados.Equipo") as equipo:
            equipo.return_value.registrar_equipo.return_value = "ok"
            resultado = crear_trade_in().registrar_trade_in(tests=[TEST_VALIDO])

        assert resultado["success"] is True
        assert resultado["tests_registrados"] == 0
        db.commit.assert_called_once()

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, ("TRD000005",)]

        with patch("app.models.tradein_empleados.Equipo") as equipo, patch(
            "app.models.tradein_empleados.Bitacora"
        ) as bitacora:
            equipo.return_value.registrar_equipo.return_value = "ok"
            crear_trade_in(usuario_id="USR-001").registrar_trade_in()

        bitacora.return_value.registrar.assert_called_once()

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, ("TRD000005",)]

        with patch("app.models.tradein_empleados.Equipo") as equipo, patch(
            "app.models.tradein_empleados.Bitacora"
        ) as bitacora:
            equipo.return_value.registrar_equipo.return_value = "ok"
            crear_trade_in().registrar_trade_in()

        bitacora.assert_not_called()

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = crear_trade_in().registrar_trade_in()

        assert resultado == {"success": False, "error": "fallo simulado"}
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestActualizarTradeIn:

    def test_error_de_validacion(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = crear_trade_in(trade_in_id=None).actualizar_trade_in()

        assert resultado == {
            "success": False,
            "error": "ID de trade-in no especificado.",
        }
        cursor.execute.assert_not_called()

    def test_error_en_tests(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = crear_trade_in().actualizar_trade_in(tests=123)

        assert resultado == {
            "success": False,
            "error": "El campo tests debe ser una lista.",
        }

    def test_conexion_caida(self, conexion_caída):
        assert crear_trade_in().actualizar_trade_in() == {
            "success": False,
            "error": "Error de conexión a la base de datos",
        }

    def test_equipo_existente_actualiza(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_EQUIPO,)

        with patch("app.models.tradein_empleados.Equipo") as equipo, patch(
            "app.models.tradein_empleados.Bitacora"
        ) as bitacora:
            equipo.return_value.actualizar_equipo.return_value = (
                "Equipo actualizado exitosamente"
            )
            resultado = crear_trade_in(usuario_id="USR-001").actualizar_trade_in()

        assert resultado == {
            "success": True,
            "message": "Trade-in actualizado correctamente",
            "trade_in_id": TRADE_IN_ID,
            "tests_registrados": 0,
        }
        assert any(
            "UPDATE Trade_in" in llamada.args[0]
            for llamada in cursor.execute.call_args_list
        )
        update = next(
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "UPDATE Trade_in" in llamada.args[0]
        )
        assert update == (
            EMPLEADO_MAXIMO,
            CLIENTE_MAXIMO,
            ID_EQUIPO,
            100.0,
            TRADE_IN_ID,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_equipo_nuevo_registrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with patch("app.models.tradein_empleados.Equipo") as equipo:
            equipo.return_value.registrar_equipo.return_value = "ok"
            resultado = crear_trade_in().actualizar_trade_in()

        assert resultado["success"] is True
        equipo.return_value.registrar_equipo.assert_called_once()

    def test_error_al_registrar_equipo_nuevo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with patch("app.models.tradein_empleados.Equipo") as equipo:
            equipo.return_value.registrar_equipo.return_value = (
                "Error al registrar el equipo"
            )
            resultado = crear_trade_in().actualizar_trade_in()

        assert resultado == {
            "success": False,
            "error": "Error al registrar el equipo",
        }
        db.commit.assert_not_called()

    def test_registra_fotos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (ID_EQUIPO,),
            ("FTI0000010",),
        ]

        with patch("app.models.tradein_empleados.Equipo") as equipo:
            equipo.return_value.actualizar_equipo.return_value = "ok"
            resultado = crear_trade_in().actualizar_trade_in(
                fotos=["/static/foto1.jpg"]
            )

        assert resultado["success"] is True
        inserts = [
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Fotos_trade_in" in llamada.args[0]
        ]
        assert inserts == [("FTI0000011", TRADE_IN_ID, "/static/foto1.jpg")]

    def test_registra_tests(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (ID_EQUIPO,),
            ("TST000002",),
        ]

        with patch("app.models.tradein_empleados.Equipo") as equipo:
            equipo.return_value.actualizar_equipo.return_value = "ok"
            resultado = crear_trade_in().actualizar_trade_in(
                tests=[
                    {"nombre": "Pantalla", "resultado": "Funciona"},
                    {"nombre": "Batería", "resultado": "No funciona"},
                ]
            )

        assert resultado["tests_registrados"] == 2
        inserts = [
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Test " in llamada.args[0]
        ]
        assert inserts == [
            ("TST000003", 1, "Pantalla", "Funciona"),
            ("TST000004", 1, "Batería", "No funciona"),
        ]

    def test_elimina_relaciones_anteriores(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_EQUIPO,)

        with patch("app.models.tradein_empleados.Equipo") as equipo:
            equipo.return_value.actualizar_equipo.return_value = "ok"
            crear_trade_in().actualizar_trade_in()

        sentencias = [llamada.args[0] for llamada in cursor.execute.call_args_list]
        assert any("DELETE FROM Fotos_trade_in" in sql for sql in sentencias)
        assert any("DELETE tr FROM Test_realizados_trade_in" in sql for sql in sentencias)

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_EQUIPO,)

        with patch("app.models.tradein_empleados.Equipo") as equipo, patch(
            "app.models.tradein_empleados.Bitacora"
        ) as bitacora:
            equipo.return_value.actualizar_equipo.return_value = "ok"
            crear_trade_in(usuario_id="USR-001").actualizar_trade_in()

        bitacora.return_value.registrar.assert_called_once()

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = crear_trade_in().actualizar_trade_in()

        assert resultado == {"success": False, "error": "fallo simulado"}
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestEliminarTradeIn:

    def test_sin_id(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert crear_trade_in(trade_in_id=None).eliminar_trade_in() == {
            "success": False,
            "error": "ID de trade-in no especificado.",
        }
        cursor.execute.assert_not_called()

    def test_id_con_formato_invalido(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert crear_trade_in(trade_in_id="TRD#1").eliminar_trade_in() == {
            "success": False,
            "error": "El campo ID de Trade-in solo puede contener letras, "
            "números, acentos y espacios.",
        }
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert crear_trade_in().eliminar_trade_in() == {
            "success": False,
            "error": "Error de conexión",
        }

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch("app.models.tradein_empleados.Bitacora") as bitacora:
            resultado = crear_trade_in(usuario_id="USR-001").eliminar_trade_in()

        assert resultado == {
            "success": True,
            "message": "Trade-in eliminado correctamente",
        }
        sentencias = [llamada.args[0] for llamada in cursor.execute.call_args_list]
        assert any("DELETE FROM Fotos_trade_in" in sql for sql in sentencias)
        assert any("DELETE tr FROM Test_realizados_trade_in" in sql for sql in sentencias)
        assert ultima_sentencia(cursor) == (
            "DELETE FROM Trade_in WHERE ID_Trade_in = %s"
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        bitacora.return_value.registrar.assert_called_once()
        cierra_recursos(db, cursor)

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch("app.models.tradein_empleados.Bitacora") as bitacora:
            crear_trade_in().eliminar_trade_in()

        bitacora.assert_not_called()

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = crear_trade_in().eliminar_trade_in()

        assert resultado == {"success": False, "error": "fallo simulado"}
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestObtenerTradeIns:

    def test_con_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id": TRADE_IN_ID, "valor_pagado": 100}]
        cursor.fetchall.return_value = filas

        with patch.object(
            TradeInEmpleados, "obtener_fotos_trade_in", return_value=[{"id": "F1"}]
        ), patch.object(
            TradeInEmpleados, "obtener_tests_trade_in", return_value=[{"nombre": "P"}]
        ):
            resultado = TradeInEmpleados().obtener_trade_ins()

        assert resultado == [
            {
                "id": TRADE_IN_ID,
                "valor_pagado": 100,
                "fotos": [{"id": "F1"}],
                "tests": [{"nombre": "P"}],
            }
        ]
        assert "FROM Trade_in t" in ultima_sentencia(cursor)
        cierra_recursos(db, cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert TradeInEmpleados().obtener_trade_ins() == []

    def test_conexion_caida(self, conexion_caída):
        assert TradeInEmpleados().obtener_trade_ins() == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert TradeInEmpleados().obtener_trade_ins() == []


class TestObtenerTradeInsPorCliente:

    def test_sin_cliente(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert TradeInEmpleados().obtener_trade_ins_por_cliente() == []
        cursor.execute.assert_not_called()

    @pytest.mark.parametrize(
        "cliente",
        [
            pytest.param("12345", id="muy-corto"),
            pytest.param("123456789", id="muy-largo"),
            pytest.param("12345a", id="no-numerico"),
        ],
    )
    def test_cliente_invalido(self, conexion_falsa, cliente):
        db, cursor = conexion_falsa

        assert TradeInEmpleados(
            cliente_id=cliente
        ).obtener_trade_ins_por_cliente() == []
        cursor.execute.assert_not_called()

    def test_con_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id": TRADE_IN_ID}]
        cursor.fetchall.return_value = filas

        assert TradeInEmpleados(
            cliente_id=CLIENTE_MAXIMO
        ).obtener_trade_ins_por_cliente() == filas
        assert cursor.execute.call_args.args[1] == (CLIENTE_MAXIMO,)
        cierra_recursos(db, cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert TradeInEmpleados(
            cliente_id=CLIENTE_MAXIMO
        ).obtener_trade_ins_por_cliente() == []

    def test_conexion_caida(self, conexion_caída):
        assert TradeInEmpleados(
            cliente_id=CLIENTE_MAXIMO
        ).obtener_trade_ins_por_cliente() == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert TradeInEmpleados(
            cliente_id=CLIENTE_MAXIMO
        ).obtener_trade_ins_por_cliente() == []


class TestObtenerDetalleTradeIn:

    def test_sin_id(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert TradeInEmpleados().obtener_detalle_trade_in() == {}
        cursor.execute.assert_not_called()

    def test_id_con_formato_invalido(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert TradeInEmpleados(
            trade_in_id="TRD#1"
        ).obtener_detalle_trade_in() == {}
        cursor.execute.assert_not_called()

    def test_detalle_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {"id": TRADE_IN_ID, "valor_pagado": 100}
        cursor.fetchone.return_value = esperado

        assert TradeInEmpleados(
            trade_in_id=TRADE_IN_ID
        ).obtener_detalle_trade_in() == esperado
        assert cursor.execute.call_args.args[1] == (TRADE_IN_ID,)
        cierra_recursos(db, cursor)

    def test_detalle_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert TradeInEmpleados(
            trade_in_id=TRADE_IN_ID
        ).obtener_detalle_trade_in() == {}

    def test_conexion_caida(self, conexion_caída):
        assert TradeInEmpleados(
            trade_in_id=TRADE_IN_ID
        ).obtener_detalle_trade_in() == {}

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert TradeInEmpleados(
            trade_in_id=TRADE_IN_ID
        ).obtener_detalle_trade_in() == {}


class TestObtenerFotosTradeIn:

    def test_sin_id(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert TradeInEmpleados().obtener_fotos_trade_in() == []
        cursor.execute.assert_not_called()

    def test_usa_el_id_del_modelo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [{"id": "F1", "url": "/f1.jpg"}]

        resultado = TradeInEmpleados(
            trade_in_id=TRADE_IN_ID
        ).obtener_fotos_trade_in()

        assert resultado == [{"id": "F1", "url": "/f1.jpg"}]
        assert cursor.execute.call_args.args[1] == (TRADE_IN_ID,)
        cierra_recursos(db, cursor)

    def test_prioriza_el_id_recibido(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        TradeInEmpleados(trade_in_id=TRADE_IN_ID).obtener_fotos_trade_in(
            "TRD000009"
        )

        assert cursor.execute.call_args.args[1] == ("TRD000009",)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert TradeInEmpleados(
            trade_in_id=TRADE_IN_ID
        ).obtener_fotos_trade_in() == []

    def test_conexion_caida(self, conexion_caída):
        assert TradeInEmpleados(
            trade_in_id=TRADE_IN_ID
        ).obtener_fotos_trade_in() == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert TradeInEmpleados(
            trade_in_id=TRADE_IN_ID
        ).obtener_fotos_trade_in() == []


class TestObtenerTestsTradeIn:

    def test_sin_id(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert TradeInEmpleados().obtener_tests_trade_in() == []
        cursor.execute.assert_not_called()

    def test_usa_el_id_del_modelo(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"ID_test": "TST000001", "nombre": "Pantalla"}]
        cursor.fetchall.return_value = filas

        resultado = TradeInEmpleados(
            trade_in_id=TRADE_IN_ID
        ).obtener_tests_trade_in()

        assert resultado == filas
        assert cursor.execute.call_args.args[1] == (TRADE_IN_ID,)
        cierra_recursos(db, cursor)

    def test_prioriza_el_id_recibido(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        TradeInEmpleados(trade_in_id=TRADE_IN_ID).obtener_tests_trade_in(
            "TRD000009"
        )

        assert cursor.execute.call_args.args[1] == ("TRD000009",)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert TradeInEmpleados(
            trade_in_id=TRADE_IN_ID
        ).obtener_tests_trade_in() == []

    def test_conexion_caida(self, conexion_caída):
        assert TradeInEmpleados(
            trade_in_id=TRADE_IN_ID
        ).obtener_tests_trade_in() == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert TradeInEmpleados(
            trade_in_id=TRADE_IN_ID
        ).obtener_tests_trade_in() == []


class TestObtenerEstadisticas:

    def test_con_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"total": 5},
            {"valor_total": "1500.50"},
            {"equipos": 3},
        ]

        assert TradeInEmpleados().obtener_estadisticas() == {
            "total": 5,
            "valor_total": 1500.5,
            "equipos": 3,
        }
        cierra_recursos(db, cursor)

    def test_sin_datos_devuelve_ceros(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, None, None]

        assert TradeInEmpleados().obtener_estadisticas() == {
            "total": 0,
            "valor_total": 0.0,
            "equipos": 0,
        }

    def test_conexion_caida(self, conexion_caída):
        assert TradeInEmpleados().obtener_estadisticas() == {}

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert TradeInEmpleados().obtener_estadisticas() == {}

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, None, None]

        TradeInEmpleados().obtener_estadisticas()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerProductosDisponibles:

    def test_con_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id": "1", "nombre": "iPhone 13"}]
        cursor.fetchall.return_value = filas

        assert TradeInEmpleados().obtener_productos_disponibles() == filas
        assert "cl.ID_Clase = '1'" in ultima_sentencia(cursor)
        cierra_recursos(db, cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert TradeInEmpleados().obtener_productos_disponibles() == []

    def test_conexion_caida(self, conexion_caída):
        assert TradeInEmpleados().obtener_productos_disponibles() == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert TradeInEmpleados().obtener_productos_disponibles() == []


class TestObtenerClientes:

    def test_busqueda_con_caracteres_especiales(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert TradeInEmpleados().obtener_clientes("Ana#") == []
        cursor.execute.assert_not_called()

    def test_sin_filtro(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [{"id": CLIENTE_MAXIMO}]

        resultado = TradeInEmpleados().obtener_clientes()

        assert resultado == [{"id": CLIENTE_MAXIMO}]
        assert cursor.execute.call_args.args[1] == ()
        assert "WHERE c.ID_cliente LIKE" not in ultima_sentencia(cursor)
        cierra_recursos(db, cursor)

    def test_con_filtro(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        TradeInEmpleados().obtener_clientes("Ana")

        assert cursor.execute.call_args.args[1] == ("%Ana%", "%Ana%", "%Ana%")
        assert "WHERE c.ID_cliente LIKE %s" in ultima_sentencia(cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert TradeInEmpleados().obtener_clientes() == []

    def test_conexion_caida(self, conexion_caída):
        assert TradeInEmpleados().obtener_clientes() == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert TradeInEmpleados().obtener_clientes() == []


class TestVerificarEquipoExistente:

    def test_sin_id_equipo(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert TradeInEmpleados().verificar_equipo_existente() is None
        cursor.execute.assert_not_called()

    @pytest.mark.parametrize(
        "equipo",
        [
            pytest.param("1234567", id="muy-corto"),
            pytest.param("12345678901234567", id="muy-largo"),
            pytest.param("1234567a", id="no-numerico"),
        ],
    )
    def test_id_equipo_invalido(self, conexion_falsa, equipo):
        db, cursor = conexion_falsa

        assert TradeInEmpleados(
            id_equipo=equipo
        ).verificar_equipo_existente() is None
        cursor.execute.assert_not_called()

    def test_equipo_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {"ID_equipo": ID_EQUIPO, "Color": COLOR}
        cursor.fetchone.return_value = esperado

        assert TradeInEmpleados(
            id_equipo=ID_EQUIPO
        ).verificar_equipo_existente() == esperado
        assert cursor.execute.call_args.args[1] == (ID_EQUIPO,)
        cierra_recursos(db, cursor)

    def test_equipo_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert TradeInEmpleados(
            id_equipo=ID_EQUIPO
        ).verificar_equipo_existente() is None

    def test_conexion_caida(self, conexion_caída):
        assert TradeInEmpleados(
            id_equipo=ID_EQUIPO
        ).verificar_equipo_existente() is None

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert TradeInEmpleados(
            id_equipo=ID_EQUIPO
        ).verificar_equipo_existente() is None
