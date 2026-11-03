"""Pruebas unitarias de la clase Tests (app.models.test).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.
"""
from unittest.mock import patch

import pytest

from app.models.test import Tests as ModeloTests
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

# ==================== Datos de frontera ====================
ORDEN_MINIMA = "1"  # 1 carácter (mínimo)
ORDEN_MAXIMA = "1234567890"  # 10 caracteres (máximo)

NUMERO_TEST_MINIMO = "1"  # 1 dígito (mínimo)
NUMERO_TEST_MAXIMO = "999"  # 3 dígitos (máximo)

CEDULA_MINIMA = "123456"  # 6 dígitos (mínimo)
CEDULA_MAXIMA = "123456789"  # 9 dígitos (máximo)

OBSERVACIONES = "Equipo con rayones leves"


class TestBuscarTest:

    def test_con_resultados(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"ID_orden": ORDEN_MINIMA, "Nombre_test": "Pantalla"}]
        cursor.fetchall.return_value = filas

        resultado = ModeloTests(ID_orden=ORDEN_MINIMA).buscar_test()

        assert resultado == filas
        assert "FROM revision_orden" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ORDEN_MINIMA,)
        cierra_recursos(db, cursor)

    def test_sin_resultados(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert ModeloTests(ID_orden=ORDEN_MINIMA).buscar_test() == []

    def test_conexion_caida(self, conexion_caída):
        assert ModeloTests(ID_orden=ORDEN_MINIMA).buscar_test() is None

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        ModeloTests(ID_orden=ORDEN_MINIMA).buscar_test()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestListasTests:

    def test_con_resultados(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"Numero_test": 1, "cantidad": 18}]
        cursor.fetchall.return_value = filas

        resultado = ModeloTests(ID_orden=ORDEN_MINIMA).listas_tests()

        assert resultado == filas
        assert "FROM Interaccion" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ORDEN_MINIMA,)

    def test_sin_resultados(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert ModeloTests(ID_orden=ORDEN_MINIMA).listas_tests() == []

    def test_conexion_caida(self, conexion_caída):
        assert ModeloTests(ID_orden=ORDEN_MINIMA).listas_tests() is None

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        ModeloTests(ID_orden=ORDEN_MINIMA).listas_tests()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestConsultarTest:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"test": "Pantalla", "Resultado_test": "Funciona"}]
        cursor.fetchall.return_value = filas

        resultado = ModeloTests(
            ID_orden=ORDEN_MINIMA, Numero_test=NUMERO_TEST_MINIMO
        ).consultar_test()

        assert resultado == filas
        assert "where i.ID_orden_servicio = %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (
            ORDEN_MINIMA,
            NUMERO_TEST_MINIMO,
        )
        cierra_recursos(db, cursor)

    def test_sin_resultados(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert ModeloTests(
            ID_orden=ORDEN_MINIMA, Numero_test=NUMERO_TEST_MINIMO
        ).consultar_test() == []

    @pytest.mark.parametrize(
        "orden, esperado",
        [
            pytest.param(
                "",
                "El campo ID dela orden no puede estar vacío.",
                id="orden-vacia",
            ),
            pytest.param(
                "12345678901",
                "El campo ID dela orden no puede tener más de 10 caracteres.",
                id="orden-demasiado-larga",
            ),
            pytest.param(
                "12#",
                "El campo ID dela orden solo puede contener letras, números, acentos y espacios.",
                id="orden-caracteres-invalidos",
            ),
        ],
    )
    def test_orden_invalida_no_toca_la_bd(self, conexion_falsa, orden, esperado):
        db, cursor = conexion_falsa

        resultado = ModeloTests(
            ID_orden=orden, Numero_test=NUMERO_TEST_MINIMO
        ).consultar_test()

        assert resultado == esperado
        cursor.execute.assert_not_called()

    @pytest.mark.parametrize(
        "numero, esperado",
        [
            pytest.param(
                "",
                "El campo Numero de test no puede estar vacío.",
                id="numero-vacio",
            ),
            pytest.param(
                "1234",
                "El campo Numero de test no puede tener más de 3 dígitos.",
                id="numero-demasiado-largo",
            ),
            pytest.param(
                "1a",
                "El campo Numero de test solo puede contener números.",
                id="numero-no-numerico",
            ),
        ],
    )
    def test_numero_invalido_no_toca_la_bd(
        self, conexion_falsa, numero, esperado
    ):
        db, cursor = conexion_falsa

        resultado = ModeloTests(
            ID_orden=ORDEN_MINIMA, Numero_test=numero
        ).consultar_test()

        assert resultado == esperado
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert ModeloTests(
            ID_orden=ORDEN_MINIMA, Numero_test=NUMERO_TEST_MINIMO
        ).consultar_test() is None

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        ModeloTests(
            ID_orden=ORDEN_MINIMA, Numero_test=NUMERO_TEST_MINIMO
        ).consultar_test()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestRegistrarRevisionTest:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch("app.models.test.Bitacora") as bitacora:
            resultado = ModeloTests(
                ID_orden=ORDEN_MINIMA,
                Numero_test=NUMERO_TEST_MINIMO,
                lista_tests=[{"nombre": "Pantalla", "resultado": "Funciona"}],
                ID_empleado=CEDULA_MINIMA,
                usuario_id="USR-001",
            ).registrar_revision_test()

        assert resultado == "Revisión técnica y pruebas registradas exitosamente."
        assert ultima_sentencia(cursor) == (
            "CALL sp_registrar_revision_test(%s, %s, %s, %s)"
        )
        assert cursor.execute.call_args.args[1] == (
            ORDEN_MINIMA,
            CEDULA_MINIMA,
            NUMERO_TEST_MINIMO,
            '[{"nombre": "Pantalla", "resultado": "Funciona"}]',
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        bitacora.return_value.registrar.assert_called_once()
        cierra_recursos(db, cursor)

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch("app.models.test.Bitacora") as bitacora:
            ModeloTests(
                ID_orden=ORDEN_MINIMA,
                Numero_test=NUMERO_TEST_MINIMO,
                lista_tests=[],
                ID_empleado=CEDULA_MINIMA,
            ).registrar_revision_test()

        bitacora.assert_not_called()

    @pytest.mark.parametrize(
        "orden, esperado",
        [
            pytest.param(
                "",
                "El campo ID del Cargo no puede estar vacío.",
                id="orden-vacia",
            ),
            pytest.param(
                "12345678901",
                "El campo ID del Cargo no puede tener más de 10 caracteres.",
                id="orden-demasiado-larga",
            ),
            pytest.param(
                "12#",
                "El campo ID del Cargo solo puede contener letras, números, acentos y espacios.",
                id="orden-caracteres-invalidos",
            ),
        ],
    )
    def test_orden_invalida_no_toca_la_bd(self, conexion_falsa, orden, esperado):
        db, cursor = conexion_falsa

        resultado = ModeloTests(
            ID_orden=orden,
            Numero_test=NUMERO_TEST_MINIMO,
            lista_tests=[],
            ID_empleado=CEDULA_MINIMA,
        ).registrar_revision_test()

        assert resultado == esperado
        cursor.execute.assert_not_called()

    @pytest.mark.parametrize(
        "cedula, esperado",
        [
            pytest.param(
                "",
                "El campo Cédula no puede estar vacío.",
                id="cedula-vacia",
            ),
            pytest.param(
                "12345",
                "El campo Cédula debe tener al menos 6 dígitos.",
                id="cedula-demasiado-corta",
            ),
            pytest.param(
                "1234567890",
                "El campo Cédula no puede tener más de 9 dígitos.",
                id="cedula-demasiado-larga",
            ),
            pytest.param(
                "12345a",
                "El campo Cédula solo puede contener números.",
                id="cedula-no-numerica",
            ),
        ],
    )
    def test_cedula_invalida_no_toca_la_bd(
        self, conexion_falsa, cedula, esperado
    ):
        db, cursor = conexion_falsa

        resultado = ModeloTests(
            ID_orden=ORDEN_MINIMA,
            Numero_test=NUMERO_TEST_MINIMO,
            lista_tests=[],
            ID_empleado=cedula,
        ).registrar_revision_test()

        assert resultado == esperado
        cursor.execute.assert_not_called()

    def test_lista_no_serializable(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = ModeloTests(
            ID_orden=ORDEN_MINIMA,
            Numero_test=NUMERO_TEST_MINIMO,
            lista_tests=[object()],
            ID_empleado=CEDULA_MINIMA,
        ).registrar_revision_test()

        assert resultado == "El formato de la lista de pruebas es incorrecto."
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = ModeloTests(
            ID_orden=ORDEN_MINIMA,
            Numero_test=NUMERO_TEST_MINIMO,
            lista_tests=[],
            ID_empleado=CEDULA_MINIMA,
        ).registrar_revision_test()

        assert resultado == "Error al conectar con la base de datos."

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = ModeloTests(
            ID_orden=ORDEN_MINIMA,
            Numero_test=NUMERO_TEST_MINIMO,
            lista_tests=[],
            ID_empleado=CEDULA_MINIMA,
        ).registrar_revision_test()

        assert resultado == "Error interno al procesar el registro de las pruebas."
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestBuscarTestPorOrden:

    def test_orden_vacia(self, conexion_falsa):
        assert ModeloTests().buscar_test_por_orden("") == []

    def test_conexion_caida(self, conexion_caída):
        assert ModeloTests().buscar_test_por_orden(ORDEN_MINIMA) == []

    def test_con_resultados(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"Num_test": 1, "Nombre_test": "Pantalla"}]
        cursor.fetchall.return_value = filas

        resultado = ModeloTests().buscar_test_por_orden(ORDEN_MINIMA)

        assert resultado == filas
        assert "FROM Test t" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ORDEN_MINIMA,)
        cierra_recursos(db, cursor)

    def test_error_de_bd_devuelve_lista_vacia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert ModeloTests().buscar_test_por_orden(ORDEN_MINIMA) == []


class TestRegistrarTest:

    def test_datos_validos_con_interaccion_existente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            ("TST000005",),  # MAX(ID_test)
            ("INT000001",),  # interacción existente
        ]
        cursor.fetchall.return_value = [("TST000006",), ("TST000007",)]

        resultado = ModeloTests().registrar_test(
            (CEDULA_MINIMA, 1, 1, 0), ORDEN_MINIMA
        )

        assert resultado is True
        assert cursor.execute.call_args_list[0].args[0] == "SELECT MAX(ID_test) FROM Test"
        inserts = [
            llamada.args
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Test " in llamada.args[0]
        ]
        assert inserts[0][1] == ("TST000006", 1, "Botón Power", "Funciona")
        assert inserts[1][1] == ("TST000007", 1, "Botón Vol", "No funciona")
        assert any(
            "INSERT INTO Test_realizados_interaccion" in llamada.args[0]
            for llamada in cursor.execute.call_args_list
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_crea_interaccion_si_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (None,),  # MAX(ID_test): no hay tests
            None,  # no hay interacción
            ("INT000004",),  # MAX(ID_interaccion)
        ]
        cursor.fetchall.return_value = [("TST000001",)]

        resultado = ModeloTests().registrar_test((CEDULA_MINIMA, 1, 1), ORDEN_MINIMA)

        assert resultado is True
        sentencias = [llamada.args[0] for llamada in cursor.execute.call_args_list]
        assert any("INSERT INTO Interaccion" in sql for sql in sentencias)
        assert any(
            "INSERT INTO Test_realizados_interaccion" in sql for sql in sentencias
        )
        db.commit.assert_called_once()

    def test_id_de_test_con_formato_invalido_reinicia_el_consecutivo(
        self, conexion_falsa
    ):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            ("ABC",),  # no se puede parsear el consecutivo
            ("INT000001",),
        ]
        cursor.fetchall.return_value = [("TST000001",)]

        ModeloTests().registrar_test((CEDULA_MINIMA, 1, 1), ORDEN_MINIMA)

        insert_test = next(
            llamada.args
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Test " in llamada.args[0]
        )
        assert insert_test[1][0] == "TST000001"

    def test_agrega_observaciones_al_final(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            ("TST000005",),
            ("INT000001",),
        ]
        cursor.fetchall.return_value = [("TST000006",)]
        valores = (CEDULA_MINIMA, 1) + tuple([1] * 18) + (OBSERVACIONES,)

        resultado = ModeloTests().registrar_test(valores, ORDEN_MINIMA)

        assert resultado is True
        insert_obs = [
            llamada.args
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Test " in llamada.args[0]
            and llamada.args[1][2] == "Observaciones"
        ]
        assert insert_obs[0][1][3] == OBSERVACIONES

    def test_sin_tests_devuelve_false(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = ModeloTests().registrar_test((CEDULA_MINIMA, None), ORDEN_MINIMA)

        assert resultado is False
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert ModeloTests().registrar_test((CEDULA_MINIMA, 1, 1), ORDEN_MINIMA) is False

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = ModeloTests().registrar_test((CEDULA_MINIMA, 1, 1), ORDEN_MINIMA)

        assert resultado is False
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestObtenerTestPorOrdenYNumero:

    def test_con_resultados(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"Nombre_test": "Pantalla", "Resultado_test": "Funciona"}]
        cursor.fetchall.return_value = filas

        resultado = ModeloTests().obtener_test_por_orden_y_numero(
            ORDEN_MINIMA, NUMERO_TEST_MINIMO
        )

        assert resultado == filas
        assert "AND t.Numero_test = %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (
            ORDEN_MINIMA,
            NUMERO_TEST_MINIMO,
        )
        cierra_recursos(db, cursor)

    def test_sin_resultados(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert ModeloTests().obtener_test_por_orden_y_numero(
            ORDEN_MINIMA, NUMERO_TEST_MINIMO
        ) == []

    def test_conexion_caida(self, conexion_caída):
        assert ModeloTests().obtener_test_por_orden_y_numero(
            ORDEN_MINIMA, NUMERO_TEST_MINIMO
        ) == []

    def test_error_de_bd_devuelve_lista_vacia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert ModeloTests().obtener_test_por_orden_y_numero(
            ORDEN_MINIMA, NUMERO_TEST_MINIMO
        ) == []
