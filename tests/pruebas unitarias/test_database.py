"""Pruebas unitarias de la clase base conectar (app.models.database).

Aquí no se usan los fixtures `conexion_falsa` ni `conexion_caída`, porque
`conectar` es justamente la clase que crea las conexiones: se prueba con
`unittest.mock.patch` sobre `mysql.connector.connect` y con variables de
entorno controladas mediante `monkeypatch`.
"""
from unittest.mock import MagicMock, patch

import mysql.connector
import pytest

from app.models.database import conectar

MENSAJE_ERROR_CONEXION = (
    "No se pudo conectar con la base de datos. "
    "Inténtalo de nuevo más tarde o comunícate con los técnicos."
)

# ==================== Datos de frontera ====================
HOST = "127.0.0.1"
PUERTO = 3307
BASE_DATOS = "ituaccesoriobd"
USUARIO = "root"
CONTRASENA = "clave-segura"

HOST_SECUNDARIO = "127.0.0.2"
BASE_DATOS_SECUNDARIA = "seguridad"
CONTRASENA_SECUNDARIA = "clave-secundaria"


class TestCrearConexion:

    def test_usa_usuario_y_password_del_entorno(self, monkeypatch):
        monkeypatch.setenv("DB_USER", USUARIO)
        monkeypatch.setenv("DB_PASSWORD", CONTRASENA)
        conexion = MagicMock()

        with patch(
            "app.models.database.mysql.connector.connect", return_value=conexion
        ) as conectar_mock:
            resultado = conectar()._crear_conexion(HOST, PUERTO, BASE_DATOS)

        assert resultado is conexion
        conectar_mock.assert_called_once_with(
            host=HOST,
            port=PUERTO,
            user=USUARIO,
            password=CONTRASENA,
            database=BASE_DATOS,
        )

    def test_password_explicita_tiene_prioridad(self, monkeypatch):
        monkeypatch.setenv("DB_USER", USUARIO)
        monkeypatch.setenv("DB_PASSWORD", "password-del-entorno")
        conexion = MagicMock()

        with patch(
            "app.models.database.mysql.connector.connect", return_value=conexion
        ) as conectar_mock:
            resultado = conectar()._crear_conexion(
                HOST, PUERTO, BASE_DATOS, password="password-explicita"
            )

        assert resultado is conexion
        assert conectar_mock.call_args.kwargs["password"] == "password-explicita"

    def test_password_vacia_explicita_se_respeta(self, monkeypatch):
        monkeypatch.setenv("DB_USER", USUARIO)
        monkeypatch.setenv("DB_PASSWORD", "password-del-entorno")

        with patch(
            "app.models.database.mysql.connector.connect", return_value=MagicMock()
        ) as conectar_mock:
            conectar()._crear_conexion(HOST, PUERTO, BASE_DATOS, password="")

        assert conectar_mock.call_args.kwargs["password"] == ""

    def test_error_de_mysql_devuelve_none(self, monkeypatch):
        monkeypatch.setenv("DB_USER", USUARIO)
        monkeypatch.setenv("DB_PASSWORD", CONTRASENA)
        error = mysql.connector.Error("acceso denegado")
        instancia = conectar()

        with patch(
            "app.models.database.mysql.connector.connect", side_effect=error
        ):
            resultado = instancia._crear_conexion(HOST, PUERTO, BASE_DATOS)

        assert resultado is None
        assert instancia.ultimo_error is error

    def test_error_de_mysql_se_imprime_por_consola(self, monkeypatch, capsys):
        monkeypatch.setenv("DB_USER", USUARIO)
        monkeypatch.setenv("DB_PASSWORD", CONTRASENA)
        error = mysql.connector.Error("sin ruta al servidor")

        with patch(
            "app.models.database.mysql.connector.connect", side_effect=error
        ):
            conectar()._crear_conexion(HOST, PUERTO, BASE_DATOS)

        salida = capsys.readouterr().out
        assert f"Error al conectar a {BASE_DATOS} ({HOST}): {error}" in salida

    def test_conexion_exitosa_no_cambia_ultimo_error(self, monkeypatch):
        monkeypatch.setenv("DB_USER", USUARIO)
        monkeypatch.setenv("DB_PASSWORD", CONTRASENA)
        instancia = conectar()

        with patch(
            "app.models.database.mysql.connector.connect", return_value=MagicMock()
        ):
            instancia._crear_conexion(HOST, PUERTO, BASE_DATOS)

        assert instancia.ultimo_error is None


class TestConexion1:

    def test_usa_configuracion_principal(self, monkeypatch):
        monkeypatch.setenv("DB_HOST1", HOST)
        monkeypatch.setenv("DB_PORT", str(PUERTO))
        monkeypatch.setenv("DB_NAME1", BASE_DATOS)
        conexion = MagicMock()

        with patch.object(
            conectar, "_crear_conexion", return_value=conexion
        ) as crear_mock:
            resultado = conectar().conexion1()

        assert resultado is conexion
        crear_mock.assert_called_once_with(HOST, PUERTO, BASE_DATOS)

    def test_convierte_el_puerto_a_entero(self, monkeypatch):
        monkeypatch.setenv("DB_HOST1", HOST)
        monkeypatch.setenv("DB_PORT", "3317")
        monkeypatch.setenv("DB_NAME1", BASE_DATOS)

        with patch.object(
            conectar, "_crear_conexion", return_value=MagicMock()
        ) as crear_mock:
            conectar().conexion1()

        assert crear_mock.call_args.args[1] == 3317
        assert isinstance(crear_mock.call_args.args[1], int)

    def test_devuelve_none_si_no_se_pudo_conectar(self, monkeypatch):
        monkeypatch.setenv("DB_HOST1", HOST)
        monkeypatch.setenv("DB_PORT", str(PUERTO))
        monkeypatch.setenv("DB_NAME1", BASE_DATOS)

        with patch.object(conectar, "_crear_conexion", return_value=None):
            assert conectar().conexion1() is None

    def test_lee_las_variables_secundarias_solo_de_conexion2(self, monkeypatch):
        # conexion1 no debe usar las variables de la base secundaria.
        monkeypatch.setenv("DB_HOST1", HOST)
        monkeypatch.setenv("DB_PORT", str(PUERTO))
        monkeypatch.setenv("DB_NAME1", BASE_DATOS)
        monkeypatch.setenv("DB_HOST2", HOST_SECUNDARIO)
        monkeypatch.setenv("DB_NAME2", BASE_DATOS_SECUNDARIA)

        with patch.object(
            conectar, "_crear_conexion", return_value=MagicMock()
        ) as crear_mock:
            conectar().conexion1()

        crear_mock.assert_called_once_with(HOST, PUERTO, BASE_DATOS)


class TestConexion2:

    def test_usa_configuracion_secundaria_y_password2(self, monkeypatch):
        monkeypatch.setenv("DB_HOST2", HOST_SECUNDARIO)
        monkeypatch.setenv("DB_PORT", str(PUERTO))
        monkeypatch.setenv("DB_NAME2", BASE_DATOS_SECUNDARIA)
        monkeypatch.setenv("DB_PASSWORD2", CONTRASENA_SECUNDARIA)
        conexion = MagicMock()

        with patch.object(
            conectar, "_crear_conexion", return_value=conexion
        ) as crear_mock:
            resultado = conectar().conexion2()

        assert resultado is conexion
        crear_mock.assert_called_once_with(
            HOST_SECUNDARIO,
            PUERTO,
            BASE_DATOS_SECUNDARIA,
            password=CONTRASENA_SECUNDARIA,
        )

    def test_usa_password_principal_si_falta_password2(self, monkeypatch):
        monkeypatch.setenv("DB_HOST2", HOST_SECUNDARIO)
        monkeypatch.setenv("DB_PORT", str(PUERTO))
        monkeypatch.setenv("DB_NAME2", BASE_DATOS_SECUNDARIA)
        monkeypatch.setenv("DB_PASSWORD", CONTRASENA)
        monkeypatch.delenv("DB_PASSWORD2", raising=False)

        with patch.object(
            conectar, "_crear_conexion", return_value=MagicMock()
        ) as crear_mock:
            conectar().conexion2()

        assert crear_mock.call_args.kwargs["password"] == CONTRASENA

    def test_password2_vacia_no_cae_en_la_principal(self, monkeypatch):
        monkeypatch.setenv("DB_HOST2", HOST_SECUNDARIO)
        monkeypatch.setenv("DB_PORT", str(PUERTO))
        monkeypatch.setenv("DB_NAME2", BASE_DATOS_SECUNDARIA)
        monkeypatch.setenv("DB_PASSWORD", CONTRASENA)
        monkeypatch.setenv("DB_PASSWORD2", "")

        with patch.object(
            conectar, "_crear_conexion", return_value=MagicMock()
        ) as crear_mock:
            conectar().conexion2()

        assert crear_mock.call_args.kwargs["password"] == ""

    def test_devuelve_none_si_no_se_pudo_conectar(self, monkeypatch):
        monkeypatch.setenv("DB_HOST2", HOST_SECUNDARIO)
        monkeypatch.setenv("DB_PORT", str(PUERTO))
        monkeypatch.setenv("DB_NAME2", BASE_DATOS_SECUNDARIA)

        with patch.object(conectar, "_crear_conexion", return_value=None):
            assert conectar().conexion2() is None

    def test_convierte_el_puerto_a_entero(self, monkeypatch):
        monkeypatch.setenv("DB_HOST2", HOST_SECUNDARIO)
        monkeypatch.setenv("DB_PORT", "3317")
        monkeypatch.setenv("DB_NAME2", BASE_DATOS_SECUNDARIA)

        with patch.object(
            conectar, "_crear_conexion", return_value=MagicMock()
        ) as crear_mock:
            conectar().conexion2()

        assert crear_mock.call_args.args[1] == 3317
        assert isinstance(crear_mock.call_args.args[1], int)


class TestMostrarError:

    def test_devuelve_el_mensaje_para_el_usuario(self, capsys):
        assert conectar().mostrar_error() == MENSAJE_ERROR_CONEXION
        capsys.readouterr()

    def test_imprime_el_ultimo_error_tecnico(self, capsys):
        instancia = conectar()
        instancia.ultimo_error = "timeout de conexión"

        mensaje = instancia.mostrar_error()

        salida = capsys.readouterr().out
        assert mensaje == MENSAJE_ERROR_CONEXION
        assert "Error de conexión a la base de datos: timeout de conexión" in salida

    def test_imprime_none_cuando_no_hay_error(self, capsys):
        conectar().mostrar_error()

        salida = capsys.readouterr().out
        assert "Error de conexión a la base de datos: None" in salida

    def test_no_intenta_crear_conexiones(self):
        with patch.object(conectar, "_crear_conexion") as crear_mock, patch(
            "app.models.database.mysql.connector.connect"
        ) as conectar_mock:
            conectar().mostrar_error()

        crear_mock.assert_not_called()
        conectar_mock.assert_not_called()


class TestCerrarConexion:

    def test_cierra_cursor_y_conexion(self):
        cursor = MagicMock()
        db = MagicMock()

        conectar().cerrar_conexion(cursor, db)

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_sin_cursor_solo_cierra_la_conexion(self):
        db = MagicMock()

        conectar().cerrar_conexion(None, db)

        db.close.assert_called_once()

    def test_sin_conexion_solo_cierra_el_cursor(self):
        cursor = MagicMock()

        conectar().cerrar_conexion(cursor, None)

        cursor.close.assert_called_once()

    def test_ambos_nulos_no_falla(self):
        # No debe lanzar ninguna excepción.
        conectar().cerrar_conexion(None, None)

    def test_error_al_cerrar_cursor_se_ignora(self):
        cursor = MagicMock()
        cursor.close.side_effect = Exception("fallo al cerrar cursor")
        db = MagicMock()

        conectar().cerrar_conexion(cursor, db)

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_error_al_cerrar_conexion_se_ignora(self):
        cursor = MagicMock()
        db = MagicMock()
        db.close.side_effect = Exception("fallo al cerrar conexión")

        conectar().cerrar_conexion(cursor, db)

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    @pytest.mark.parametrize(
        "cursor_vacio, db_vacia",
        [
            pytest.param(True, False, id="sin-cursor"),
            pytest.param(False, True, id="sin-conexion"),
            pytest.param(True, True, id="sin-ambos"),
        ],
    )
    def test_no_falla_con_recursos_vacios(self, cursor_vacio, db_vacia):
        cursor = None if cursor_vacio else MagicMock()
        db = None if db_vacia else MagicMock()

        conectar().cerrar_conexion(cursor, db)

        if cursor is not None:
            cursor.close.assert_called_once()
        if db is not None:
            db.close.assert_called_once()
