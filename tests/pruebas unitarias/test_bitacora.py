"""Pruebas unitarias de la clase Bitacora (app.models.bitacora) y de la
función helper `listar_actividad_reciente_dashboard`.

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.
"""
from datetime import datetime, timedelta
from unittest.mock import patch

import mysql.connector
import pytest

from app.models.bitacora import Bitacora, listar_actividad_reciente_dashboard
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

MENSAJE_ERROR_CONEXION = (
    "No se pudo conectar con la base de seguridad para registrar la bitácora."
)

# ==================== Datos de frontera ====================
ACCION = "Crear rol"  # 10 caracteres
DESCRIPCION = "Se creó el rol: Vendedor"
USUARIO_ID = "7"
MODULO_NOMBRE = "Usuarios"
MODULO_ID = 3
LIMITE_MINIMO = 1
LIMITE_MAXIMO = 100


class TestObtenerModuloId:

    def test_sin_nombre_devuelve_uno_sin_conectar(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Bitacora().obtener_modulo_id() == 1

        cursor.execute.assert_not_called()
        db.cursor.assert_not_called()

    def test_nombre_de_la_instancia_devuelve_su_id(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": "3"}

        resultado = Bitacora(modulo_nombre=MODULO_NOMBRE).obtener_modulo_id()

        assert resultado == MODULO_ID
        assert "WHERE nombre = %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (MODULO_NOMBRE,)

    def test_parametro_tiene_prioridad_sobre_el_atributo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": "3"}

        Bitacora(modulo_nombre="Otro").obtener_modulo_id(MODULO_NOMBRE)

        assert cursor.execute.call_args.args[1] == (MODULO_NOMBRE,)

    def test_nombre_inexistente_usa_el_primer_modulo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, {"id": "2"}]

        resultado = Bitacora().obtener_modulo_id(MODULO_NOMBRE)

        assert resultado == 2
        assert "ORDER BY id ASC LIMIT 1" in ultima_sentencia(cursor)
        assert cursor.execute.call_count == 2

    def test_sin_modulos_devuelve_uno(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, None]

        assert Bitacora().obtener_modulo_id(MODULO_NOMBRE) == 1

    def test_id_nulo_usa_el_primer_modulo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [{"id": None}, {"id": "4"}]

        assert Bitacora().obtener_modulo_id(MODULO_NOMBRE) == 4

    def test_conexion_caida_devuelve_uno(self, conexion_caída):
        assert Bitacora().obtener_modulo_id(MODULO_NOMBRE) == 1

    def test_error_de_mysql_devuelve_uno(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = mysql.connector.Error("fallo simulado")

        assert Bitacora().obtener_modulo_id(MODULO_NOMBRE) == 1

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": "3"}

        Bitacora().obtener_modulo_id(MODULO_NOMBRE)

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": "3"}

        Bitacora().obtener_modulo_id(MODULO_NOMBRE)

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestRegistrar:

    def test_registra_con_parametros(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch.object(Bitacora, "obtener_modulo_id", return_value=MODULO_ID):
            resultado = Bitacora().registrar(
                accion=ACCION,
                descripcion=DESCRIPCION,
                usuario_id=USUARIO_ID,
                modulo_nombre=MODULO_NOMBRE,
            )

        assert resultado == {"success": True}
        assert ultima_sentencia(cursor) == (
            "INSERT INTO bitacora (usuario_id, modulo_id, accion, descripcion) "
            "VALUES (%s, %s, %s, %s)"
        )
        assert cursor.execute.call_args.args[1] == (
            USUARIO_ID,
            MODULO_ID,
            ACCION,
            DESCRIPCION,
        )
        db.commit.assert_called_once()
        cierra_recursos(db, cursor)

    def test_usa_los_atributos_de_la_instancia(self, conexion_falsa):
        db, cursor = conexion_falsa
        bitacora = Bitacora(ACCION, DESCRIPCION, USUARIO_ID, MODULO_NOMBRE)

        with patch.object(Bitacora, "obtener_modulo_id", return_value=MODULO_ID):
            resultado = bitacora.registrar()

        assert resultado == {"success": True}
        assert cursor.execute.call_args.args[1] == (
            USUARIO_ID,
            MODULO_ID,
            ACCION,
            DESCRIPCION,
        )

    def test_los_parametros_tienen_prioridad(self, conexion_falsa):
        db, cursor = conexion_falsa
        bitacora = Bitacora("Otra acción", "Otra descripción", "99", "Otro")

        with patch.object(Bitacora, "obtener_modulo_id", return_value=MODULO_ID):
            bitacora.registrar(
                accion=ACCION,
                descripcion=DESCRIPCION,
                usuario_id=USUARIO_ID,
                modulo_nombre=MODULO_NOMBRE,
            )

        assert cursor.execute.call_args.args[1] == (
            USUARIO_ID,
            MODULO_ID,
            ACCION,
            DESCRIPCION,
        )

    @pytest.mark.parametrize(
        "accion, descripcion",
        [
            pytest.param("", DESCRIPCION, id="accion-vacia"),
            pytest.param(ACCION, "", id="descripcion-vacia"),
            pytest.param("", "", id="ambas-vacias"),
            pytest.param(None, None, id="ambas-nulas"),
        ],
    )
    def test_accion_o_descripcion_vacia_no_toca_la_bd(
        self, conexion_falsa, accion, descripcion
    ):
        db, cursor = conexion_falsa

        resultado = Bitacora(accion, descripcion).registrar()

        assert resultado == {
            "success": False,
            "warning": "Acción y descripción son obligatorias para registrar en bitácora.",
        }
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Bitacora(ACCION, DESCRIPCION).registrar()

        assert resultado == {
            "success": False,
            "warning": MENSAJE_ERROR_CONEXION,
        }

    def test_error_de_mysql_devuelve_advertencia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = mysql.connector.Error("fallo simulado")

        with patch.object(Bitacora, "obtener_modulo_id", return_value=MODULO_ID):
            resultado = Bitacora(ACCION, DESCRIPCION).registrar()

        assert resultado == {
            "success": False,
            "warning": "No se pudo registrar la bitácora: fallo simulado",
        }
        db.commit.assert_not_called()

    def test_publica_notificacion_en_el_bus(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch.object(
            Bitacora, "obtener_modulo_id", return_value=MODULO_ID
        ), patch(
            "app.models.bitacora.bus_notificaciones.publicar"
        ) as publicar_mock:
            Bitacora(ACCION, DESCRIPCION, USUARIO_ID, MODULO_NOMBRE).registrar()

        publicar_mock.assert_called_once_with(
            {
                "tipo": "bitacora",
                "titulo": "Nueva actividad registrada",
                "accion": ACCION,
                "descripcion": DESCRIPCION,
                "modulo_nombre": MODULO_NOMBRE,
                "usuario_id": USUARIO_ID,
            },
            autor_id=USUARIO_ID,
        )

    def test_sin_modulo_publica_general(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch.object(
            Bitacora, "obtener_modulo_id", return_value=1
        ), patch(
            "app.models.bitacora.bus_notificaciones.publicar"
        ) as publicar_mock:
            Bitacora(ACCION, DESCRIPCION).registrar()

        assert publicar_mock.call_args.args[0]["modulo_nombre"] == "General"

    def test_usuario_numerico_se_convierte_a_texto_en_la_notificacion(
        self, conexion_falsa
    ):
        db, cursor = conexion_falsa

        with patch.object(
            Bitacora, "obtener_modulo_id", return_value=MODULO_ID
        ), patch(
            "app.models.bitacora.bus_notificaciones.publicar"
        ) as publicar_mock:
            Bitacora(ACCION, DESCRIPCION, 7, MODULO_NOMBRE).registrar()

        assert publicar_mock.call_args.args[0]["usuario_id"] == "7"
        assert publicar_mock.call_args.kwargs["autor_id"] == 7

    def test_fallo_al_publicar_no_impide_registrar(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch.object(
            Bitacora, "obtener_modulo_id", return_value=MODULO_ID
        ), patch(
            "app.models.bitacora.bus_notificaciones.publicar",
            side_effect=RuntimeError("bus caído"),
        ):
            resultado = Bitacora(ACCION, DESCRIPCION).registrar()

        assert resultado == {"success": True}
        db.commit.assert_called_once()

    def test_llama_a_obtener_modulo_id_con_el_nombre(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch.object(
            Bitacora, "obtener_modulo_id", return_value=MODULO_ID
        ) as obtener_mock, patch(
            "app.models.bitacora.bus_notificaciones.publicar"
        ):
            Bitacora().registrar(
                accion=ACCION,
                descripcion=DESCRIPCION,
                usuario_id=USUARIO_ID,
                modulo_nombre=MODULO_NOMBRE,
            )

        obtener_mock.assert_called_once_with(MODULO_NOMBRE)

    def test_no_hay_rollback_al_fallar_el_insert(self, conexion_falsa):
        # La implementación actual no hace rollback en `registrar`.
        db, cursor = conexion_falsa
        cursor.execute.side_effect = mysql.connector.Error("fallo simulado")

        with patch.object(Bitacora, "obtener_modulo_id", return_value=MODULO_ID):
            Bitacora(ACCION, DESCRIPCION).registrar()

        db.rollback.assert_not_called()


class TestObtenerInfoUsuario:

    def test_system_devuelve_sistema_sin_conectar(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Bitacora()._obtener_info_usuario("SYSTEM")

        assert resultado == {"nombre": "Sistema", "foto_perfil": None}
        cursor.execute.assert_not_called()

    def test_usuario_vacio_devuelve_sistema(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Bitacora()._obtener_info_usuario("")

        assert resultado == {"nombre": "Sistema", "foto_perfil": None}
        cursor.execute.assert_not_called()

    def test_usuario_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {"nombre": "Ana Pérez", "foto_perfil": "/static/ana.png"}
        cursor.fetchone.return_value = esperado

        resultado = Bitacora()._obtener_info_usuario(USUARIO_ID)

        assert resultado == esperado
        assert "FROM usuario" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (USUARIO_ID,)
        cierra_recursos(db, cursor)

    def test_usuario_inexistente_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Bitacora()._obtener_info_usuario(USUARIO_ID) is None

    def test_conexion_caida_devuelve_none(self, conexion_caída):
        assert Bitacora()._obtener_info_usuario(USUARIO_ID) is None

    def test_error_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Bitacora()._obtener_info_usuario(USUARIO_ID) is None

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"nombre": "Ana", "foto_perfil": None}

        Bitacora()._obtener_info_usuario(USUARIO_ID)

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestListarRecientes:

    def test_con_usuario_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        registros = [
            {
                "id": 10,
                "usuario_id": USUARIO_ID,
                "modulo_id": MODULO_ID,
                "accion": ACCION,
                "descripcion": DESCRIPCION,
                "fecha_hora": None,
                "modulo_nombre": MODULO_NOMBRE,
            }
        ]
        cursor.fetchall.return_value = registros
        cursor.fetchone.return_value = {
            "nombre": "Ana Pérez",
            "foto_perfil": "/static/ana.png",
        }

        resultado = Bitacora().listar_recientes()

        assert resultado[0]["usuario_nombre"] == "Ana Pérez"
        assert resultado[0]["usuario_foto"] == "/static/ana.png"
        assert "FROM bitacora b" in cursor.execute.call_args_list[0].args[0]
        assert cursor.execute.call_args_list[0].args[1] == (100,)

    def test_usuario_system_no_consulta_la_bd_principal(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "id": 10,
                "usuario_id": "SYSTEM",
                "modulo_id": MODULO_ID,
                "accion": ACCION,
                "descripcion": DESCRIPCION,
                "fecha_hora": None,
                "modulo_nombre": MODULO_NOMBRE,
            }
        ]

        resultado = Bitacora().listar_recientes()

        assert resultado[0]["usuario_nombre"] == "Sistema"
        assert resultado[0]["usuario_foto"] is None
        assert cursor.execute.call_count == 1

    def test_usuario_desconocido_usa_su_id(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [{"id": 10, "usuario_id": USUARIO_ID}]
        cursor.fetchone.return_value = None

        resultado = Bitacora().listar_recientes()

        assert resultado[0]["usuario_nombre"] == USUARIO_ID
        assert resultado[0]["usuario_foto"] is None

    def test_sin_registros(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Bitacora().listar_recientes() == []

    def test_fetchall_none_devuelve_lista_vacia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = None

        assert Bitacora().listar_recientes() == []

    def test_limite_se_convierte_a_entero(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Bitacora().listar_recientes(limite="5")

        assert cursor.execute.call_args_list[0].args[1] == (5,)

    def test_conexion_caida(self, conexion_caída):
        assert Bitacora().listar_recientes() == []

    def test_error_de_mysql_devuelve_lista_vacia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = mysql.connector.Error("fallo simulado")

        assert Bitacora().listar_recientes() == []

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Bitacora().listar_recientes()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Bitacora().listar_recientes()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestListarActividadReciente:

    @pytest.mark.parametrize(
        "delta, esperado",
        [
            pytest.param(timedelta(seconds=30), "hace unos segundos", id="segundos"),
            pytest.param(timedelta(seconds=90), "hace 1 minuto", id="un-minuto"),
            pytest.param(
                timedelta(minutes=2, seconds=30),
                "hace 2 minutos",
                id="varios-minutos",
            ),
            pytest.param(
                timedelta(hours=1, minutes=30), "hace 1 hora", id="una-hora"
            ),
            pytest.param(
                timedelta(hours=2, minutes=30), "hace 2 horas", id="varias-horas"
            ),
            pytest.param(
                timedelta(days=1, hours=2), "hace 1 día", id="un-dia"
            ),
            pytest.param(timedelta(days=3), "hace 3 días", id="varios-dias"),
        ],
    )
    def test_tiempo_relativo(self, conexion_falsa, delta, esperado):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "id": 1,
                "usuario_id": "SYSTEM",
                "accion": ACCION,
                "descripcion": DESCRIPCION,
                "fecha_hora": datetime.now() - delta,
                "modulo_nombre": MODULO_NOMBRE,
            }
        ]

        resultado = Bitacora().listar_actividad_reciente()

        assert resultado[0]["tiempo_relativo"] == esperado

    def test_fecha_como_texto_devuelve_recientemente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "id": 1,
                "usuario_id": "SYSTEM",
                "accion": ACCION,
                "descripcion": DESCRIPCION,
                "fecha_hora": "2026-01-01 10:00:00",
                "modulo_nombre": MODULO_NOMBRE,
            }
        ]

        resultado = Bitacora().listar_actividad_reciente()

        assert resultado[0]["tiempo_relativo"] == "recientemente"

    def test_fecha_nula_devuelve_recientemente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "id": 1,
                "usuario_id": "SYSTEM",
                "accion": ACCION,
                "descripcion": DESCRIPCION,
                "fecha_hora": None,
                "modulo_nombre": MODULO_NOMBRE,
            }
        ]

        resultado = Bitacora().listar_actividad_reciente()

        assert resultado[0]["tiempo_relativo"] == "recientemente"

    def test_enriquece_con_datos_del_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "id": 1,
                "usuario_id": USUARIO_ID,
                "accion": ACCION,
                "descripcion": DESCRIPCION,
                "fecha_hora": datetime.now(),
                "modulo_nombre": MODULO_NOMBRE,
            }
        ]
        cursor.fetchone.return_value = {
            "nombre": "Ana Pérez",
            "foto_perfil": "/static/ana.png",
        }

        resultado = Bitacora().listar_actividad_reciente()

        assert resultado[0]["usuario_nombre"] == "Ana Pérez"
        assert resultado[0]["usuario_foto"] == "/static/ana.png"

    def test_sin_registros(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Bitacora().listar_actividad_reciente() == []

    def test_fetchall_none_devuelve_lista_vacia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = None

        assert Bitacora().listar_actividad_reciente() == []

    def test_limite_se_convierte_a_entero(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Bitacora().listar_actividad_reciente(limite="2")

        assert cursor.execute.call_args_list[0].args[1] == (2,)

    def test_conexion_caida(self, conexion_caída):
        assert Bitacora().listar_actividad_reciente() == []

    def test_error_general_devuelve_lista_vacia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = RuntimeError("fallo simulado")

        assert Bitacora().listar_actividad_reciente() == []

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Bitacora().listar_actividad_reciente()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Bitacora().listar_actividad_reciente()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestListarActividadRecienteDashboard:

    def test_delega_con_el_limite_por_defecto(self):
        esperado = [{"id": 1, "accion": ACCION}]

        with patch.object(
            Bitacora, "listar_actividad_reciente", return_value=esperado
        ) as listar_mock:
            resultado = listar_actividad_reciente_dashboard()

        assert resultado == esperado
        listar_mock.assert_called_once_with(5)

    def test_pasa_el_limite_personalizado(self):
        with patch.object(
            Bitacora, "listar_actividad_reciente", return_value=[]
        ) as listar_mock:
            resultado = listar_actividad_reciente_dashboard(limite=LIMITE_MAXIMO)

        assert resultado == []
        listar_mock.assert_called_once_with(LIMITE_MAXIMO)

    def test_sin_datos(self):
        with patch.object(Bitacora, "listar_actividad_reciente", return_value=[]):
            assert listar_actividad_reciente_dashboard(limite=LIMITE_MINIMO) == []

    def test_usa_la_conexion_falsa(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert listar_actividad_reciente_dashboard() == []
