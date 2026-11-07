"""Pruebas unitarias de la clase Permiso (app.models.permisos).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py; los helpers en
tests/pruebas unitarias/helpers.py.
"""
import pytest

from app.models.permisos import Permiso
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

MENSAJE_ERROR_CONEXION = "Error al conectar a la base de datos."

# ==================== Datos de frontera ====================
ROL_ID = "2"
MODULO_ID = "3"
ROL_ID_MAXIMO = "1234567890"  # 10 dígitos (máximo)
MODULO_ID_MAXIMO = "1234567890"  # 10 dígitos (máximo)


class TestListarPermisosPorRol:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {
                "rol_id": 2,
                "modulo_id": 3,
                "modulo_nombre": "Usuarios",
                "modulo_descripcion": "Gestión",
                "consultar": 1,
                "registrar": 1,
                "modificar": 0,
                "eliminar": 0,
            }
        ]
        cursor.fetchall.return_value = filas

        resultado = Permiso(rol_id=ROL_ID).listar_permisos_por_rol()

        assert resultado == filas
        assert "FROM permiso p" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ROL_ID,)

    def test_sin_rol_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Permiso().listar_permisos_por_rol() is None

        cursor.execute.assert_not_called()

    def test_parametro_tiene_prioridad(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Permiso(rol_id="99").listar_permisos_por_rol(rol_id=ROL_ID)

        assert cursor.execute.call_args.args[1] == (ROL_ID,)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Permiso(rol_id=ROL_ID).listar_permisos_por_rol() == []

    def test_conexion_caida_devuelve_none(self, conexion_caída):
        assert Permiso(rol_id=ROL_ID).listar_permisos_por_rol() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Permiso(rol_id=ROL_ID).listar_permisos_por_rol()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Permiso(rol_id=ROL_ID).listar_permisos_por_rol()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestListarPermisosCompletosPorRol:

    def test_con_modulos_y_permisos(self, conexion_falsa):
        db, cursor = conexion_falsa
        modulos = [
            {"id": 1, "nombre": "Usuarios", "descripcion": "Gestión"},
            {"id": 2, "nombre": "Ventas", "descripcion": "Ventas"},
        ]
        permisos = [
            {
                "modulo_id": 1,
                "registrar": True,
                "modificar": False,
                "eliminar": False,
            }
        ]
        cursor.fetchall.side_effect = [modulos, permisos]

        resultado = Permiso(rol_id=ROL_ID).listar_permisos_completos_por_rol()

        assert resultado == [
            {
                "modulo_id": 1,
                "modulo_nombre": "Usuarios",
                "modulo_descripcion": "Gestión",
                "consultar": True,
                "registrar": True,
                "modificar": False,
                "eliminar": False,
            },
            {
                "modulo_id": 2,
                "modulo_nombre": "Ventas",
                "modulo_descripcion": "Ventas",
                "consultar": False,
                "registrar": False,
                "modificar": False,
                "eliminar": False,
            },
        ]
        assert cursor.execute.call_args.args[1] == (ROL_ID,)

    def test_consultar_es_verdadero_si_hay_cualquier_permiso(self, conexion_falsa):
        db, cursor = conexion_falsa
        modulos = [{"id": 1, "nombre": "Usuarios", "descripcion": "Gestión"}]
        permisos = [
            {
                "modulo_id": 1,
                "registrar": False,
                "modificar": True,
                "eliminar": False,
            }
        ]
        cursor.fetchall.side_effect = [modulos, permisos]

        resultado = Permiso(rol_id=ROL_ID).listar_permisos_completos_por_rol()

        assert resultado[0]["consultar"] is True
        assert resultado[0]["modificar"] is True

    def test_modulo_sin_descripcion_usa_cadena_vacia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.side_effect = [
            [{"id": 1, "nombre": "Usuarios"}],
            [],
        ]

        resultado = Permiso(rol_id=ROL_ID).listar_permisos_completos_por_rol()

        assert resultado[0]["modulo_descripcion"] == ""

    def test_sin_rol_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Permiso().listar_permisos_completos_por_rol() is None

        cursor.execute.assert_not_called()

    def test_sin_modulos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.side_effect = [[], []]

        assert Permiso(rol_id=ROL_ID).listar_permisos_completos_por_rol() == []

    def test_conexion_caida_devuelve_none(self, conexion_caída):
        assert Permiso(rol_id=ROL_ID).listar_permisos_completos_por_rol() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.side_effect = [[], []]

        Permiso(rol_id=ROL_ID).listar_permisos_completos_por_rol()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.side_effect = [[], []]

        Permiso(rol_id=ROL_ID).listar_permisos_completos_por_rol()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestGuardarPermiso:

    def test_inserta_cuando_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Permiso().guardar_permiso(
            ROL_ID, MODULO_ID, registrar=True
        )

        assert resultado == "Permiso guardado exitosamente."
        assert "INSERT INTO permiso" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (
            ROL_ID,
            MODULO_ID,
            True,
            False,
            False,
            True,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 2 operaciones (buscar existente + INSERT): cada una cierra su cursor
        cierra_recursos(db, cursor)

    def test_actualiza_cuando_ya_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        resultado = Permiso().guardar_permiso(
            ROL_ID, MODULO_ID, registrar=True, modificar=True
        )

        assert resultado == "Permiso guardado exitosamente."
        assert "UPDATE permiso" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (
            True,
            True,
            False,
            True,
            ROL_ID,
            MODULO_ID,
        )
        db.commit.assert_called_once()

    def test_consultar_se_deriva_de_los_otros_permisos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        Permiso().guardar_permiso(
            ROL_ID, MODULO_ID, registrar=False, modificar=True, eliminar=False
        )

        # (rol_id, modulo_id, registrar, modificar, eliminar, consultar)
        assert cursor.execute.call_args.args[1][-1] is True

    def test_sin_ningun_permiso_consultar_es_falso(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        Permiso().guardar_permiso(ROL_ID, MODULO_ID)

        assert cursor.execute.call_args.args[1][-1] is False

    @pytest.mark.parametrize(
        "rol_id, modulo_id",
        [
            pytest.param("", MODULO_ID, id="rol-vacio"),
            pytest.param(ROL_ID, "", id="modulo-vacio"),
            pytest.param("", "", id="ambos-vacios"),
        ],
    )
    def test_rol_y_modulo_obligatorios(
        self, conexion_falsa, rol_id, modulo_id
    ):
        db, cursor = conexion_falsa

        resultado = Permiso().guardar_permiso(rol_id, modulo_id)

        assert resultado == "Rol y módulo son obligatorios."
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "rol_id, modulo_id, esperado",
        [
            pytest.param(
                "abc",
                MODULO_ID,
                "El campo Rol solo puede contener números.",
                id="rol-no-numerico",
            ),
            pytest.param(
                "12345678901",
                MODULO_ID,
                "El campo Rol no puede tener más de 10 dígitos.",
                id="rol-demasiado-largo",
            ),
            pytest.param(
                ROL_ID,
                "abc",
                "El campo Módulo solo puede contener números.",
                id="modulo-no-numerico",
            ),
            pytest.param(
                ROL_ID,
                "12345678901",
                "El campo Módulo no puede tener más de 10 dígitos.",
                id="modulo-demasiado-largo",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(
        self, conexion_falsa, rol_id, modulo_id, esperado
    ):
        db, cursor = conexion_falsa

        resultado = Permiso().guardar_permiso(rol_id, modulo_id, registrar=True)

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Permiso().guardar_permiso(ROL_ID, MODULO_ID, registrar=True)

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        # 1ª llamada: consulta de existente; 2ª: el INSERT que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = Permiso().guardar_permiso(ROL_ID, MODULO_ID, registrar=True)

        assert resultado == "Error al guardar permiso."
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestGuardarPermisosMasivos:

    def test_guarda_permisos_nuevos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        permisos = [
            {"modulo_id": "1", "registrar": True},
            {"modulo_id": "2", "modificar": True},
        ]

        exitosos, errores = Permiso().guardar_permisos_masivos(ROL_ID, permisos)

        assert exitosos == 2
        assert errores == []
        assert cursor.execute.call_count == 4  # 2 SELECT + 2 INSERT
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_actualiza_los_existentes_e_inserta_los_nuevos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), None]
        permisos = [
            {"modulo_id": "1", "registrar": True},
            {"modulo_id": "2", "eliminar": True},
        ]

        exitosos, errores = Permiso().guardar_permisos_masivos(ROL_ID, permisos)

        assert exitosos == 2
        assert errores == []
        sentencias = [llamada.args[0] for llamada in cursor.execute.call_args_list]
        assert any("UPDATE permiso" in sql for sql in sentencias)
        assert any("INSERT INTO permiso" in sql for sql in sentencias)
        db.commit.assert_called_once()

    def test_lista_vacia(self, conexion_falsa):
        db, cursor = conexion_falsa

        exitosos, errores = Permiso().guardar_permisos_masivos(ROL_ID, [])

        assert (exitosos, errores) == (0, [])
        db.commit.assert_called_once()
        cursor.execute.assert_not_called()

    def test_sin_rol(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Permiso().guardar_permisos_masivos("", [])

        assert resultado == (0, ["Rol es obligatorio"])
        cursor.execute.assert_not_called()

    def test_rol_invalido(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Permiso().guardar_permisos_masivos("abc", [])

        assert resultado == (0, ["El campo Rol solo puede contener números."])
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Permiso().guardar_permisos_masivos(ROL_ID, [])

        assert resultado == (0, [MENSAJE_ERROR_CONEXION])

    def test_permiso_sin_modulo_id(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Permiso().guardar_permisos_masivos(ROL_ID, [{}])

        assert resultado == (0, ["Módulo ID faltante en uno de los permisos"])
        db.commit.assert_called_once()
        cursor.execute.assert_not_called()

    def test_modulo_invalido(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Permiso().guardar_permisos_masivos(
            ROL_ID, [{"modulo_id": "abc"}]
        )

        assert resultado == (0, ["Módulo inválido: abc"])
        db.commit.assert_called_once()
        cursor.execute.assert_not_called()

    def test_mezcla_de_validos_e_invalidos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        permisos = [
            {"modulo_id": "1", "registrar": True},
            {"modulo_id": ""},
            {"modulo_id": "abc"},
            {"modulo_id": "2", "registrar": True},
        ]

        exitosos, errores = Permiso().guardar_permisos_masivos(ROL_ID, permisos)

        assert exitosos == 2
        assert errores == [
            "Módulo ID faltante en uno de los permisos",
            "Módulo inválido: abc",
        ]
        db.commit.assert_called_once()

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = Permiso().guardar_permisos_masivos(
            ROL_ID, [{"modulo_id": "1"}]
        )

        assert resultado == (0, ["fallo simulado"])
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestEliminarPermiso:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Permiso().eliminar_permiso(ROL_ID, MODULO_ID)

        assert resultado == "Permiso eliminado exitosamente."
        assert ultima_sentencia(cursor) == (
            "DELETE FROM permiso WHERE rol_id = %s AND modulo_id = %s"
        )
        assert cursor.execute.call_args.args[1] == (ROL_ID, MODULO_ID)
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    @pytest.mark.parametrize(
        "rol_id, modulo_id",
        [
            pytest.param("", MODULO_ID, id="rol-vacio"),
            pytest.param(ROL_ID, "", id="modulo-vacio"),
            pytest.param("", "", id="ambos-vacios"),
        ],
    )
    def test_rol_y_modulo_obligatorios(
        self, conexion_falsa, rol_id, modulo_id
    ):
        db, cursor = conexion_falsa

        resultado = Permiso().eliminar_permiso(rol_id, modulo_id)

        assert resultado == "Rol y módulo son obligatorios."
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "rol_id, modulo_id, esperado",
        [
            pytest.param(
                "abc",
                MODULO_ID,
                "El campo Rol solo puede contener números.",
                id="rol-no-numerico",
            ),
            pytest.param(
                ROL_ID,
                "abc",
                "El campo Módulo solo puede contener números.",
                id="modulo-no-numerico",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(
        self, conexion_falsa, rol_id, modulo_id, esperado
    ):
        db, cursor = conexion_falsa

        resultado = Permiso().eliminar_permiso(rol_id, modulo_id)

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Permiso().eliminar_permiso(ROL_ID, MODULO_ID)

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = Permiso().eliminar_permiso(ROL_ID, MODULO_ID)

        assert resultado == "Error al eliminar permiso."
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestVerificarPermiso:

    def test_permiso_registrar_concedido(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {
            "registrar": True,
            "modificar": False,
            "eliminar": False,
        }

        assert Permiso().verificar_permiso(
            ROL_ID, "Usuarios", "registrar"
        ) is True

        assert cursor.execute.call_args.args[1] == (ROL_ID, "Usuarios")

    def test_permiso_registrar_denegado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {
            "registrar": False,
            "modificar": True,
            "eliminar": False,
        }

        assert Permiso().verificar_permiso(
            ROL_ID, "Usuarios", "registrar"
        ) is False

    def test_consultar_con_cualquier_permiso(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {
            "registrar": False,
            "modificar": False,
            "eliminar": True,
        }

        assert Permiso().verificar_permiso(
            ROL_ID, "Usuarios", "consultar"
        ) is True

    def test_consultar_sin_permisos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {
            "registrar": False,
            "modificar": False,
            "eliminar": False,
        }

        assert Permiso().verificar_permiso(
            ROL_ID, "Usuarios", "consultar"
        ) is False

    def test_sin_registro_devuelve_false(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Permiso().verificar_permiso(
            ROL_ID, "Usuarios", "registrar"
        ) is False

    def test_tipo_desconocido_devuelve_false(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {
            "registrar": True,
            "modificar": True,
            "eliminar": True,
        }

        assert Permiso().verificar_permiso(
            ROL_ID, "Usuarios", "otro"
        ) is False

    def test_conexion_caida_devuelve_false(self, conexion_caída):
        assert Permiso().verificar_permiso(
            ROL_ID, "Usuarios", "registrar"
        ) is False

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"registrar": True}

        Permiso().verificar_permiso(ROL_ID, "Usuarios", "registrar")

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"registrar": True}

        Permiso().verificar_permiso(ROL_ID, "Usuarios", "registrar")

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerPermisosUsuario:

    def test_agrega_consultar_si_hay_permisos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "modulo_nombre": "Usuarios",
                "registrar": True,
                "modificar": False,
                "eliminar": False,
            },
            {
                "modulo_nombre": "Ventas",
                "registrar": False,
                "modificar": False,
                "eliminar": False,
            },
        ]

        resultado = Permiso().obtener_permisos_usuario(ROL_ID)

        assert resultado[0]["consultar"] is True
        assert resultado[1]["consultar"] is False
        assert cursor.execute.call_args.args[1] == (ROL_ID,)

    def test_sin_permisos_consultar_es_falso(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "modulo_nombre": "Usuarios",
                "registrar": False,
                "modificar": False,
                "eliminar": False,
            }
        ]

        resultado = Permiso().obtener_permisos_usuario(ROL_ID)

        assert resultado[0]["consultar"] is False

    def test_sin_modulos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Permiso().obtener_permisos_usuario(ROL_ID) == []

    def test_conexion_caida_devuelve_none(self, conexion_caída):
        assert Permiso().obtener_permisos_usuario(ROL_ID) is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Permiso().obtener_permisos_usuario(ROL_ID)

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Permiso().obtener_permisos_usuario(ROL_ID)

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()
