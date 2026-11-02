"""Pruebas unitarias de la clase Modulo (app.models.modulos).

Los fixtures `conexion_falsa`, `conexion_caída` y `db_falsa` viven en
tests/pruebas unitarias/conftest.py; los helpers en
tests/pruebas unitarias/helpers.py.
"""
from unittest.mock import patch

import pytest

from app.models.modulos import Modulo
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

MENSAJE_ERROR_CONEXION = "Error al conectar a la base de datos."

# ==================== Datos de frontera ====================
ID_MINIMO = "1"  # 1 dígito (mínimo)
ID_MAXIMO = "1234567890"  # 10 dígitos (máximo)

NOMBRE_MINIMO = "M"  # 1 carácter (mínimo)
NOMBRE_MAXIMO = "M" * 50  # 50 caracteres (máximo)

DESCRIPCION_MINIMA = "D"  # 1 carácter (mínimo)
DESCRIPCION_MAXIMA = "D" * 255  # 255 caracteres (máximo)

USUARIO_ID = "7"


class TestListarModulos:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {"id": 1, "nombre": "Usuarios", "descripcion": "Gestión de usuarios"},
            {"id": 2, "nombre": "Ventas", "descripcion": "Gestión de ventas"},
        ]
        cursor.fetchall.return_value = filas

        resultado = Modulo().listar_modulos()

        assert resultado == filas
        assert ultima_sentencia(cursor) == (
            "SELECT id, nombre, descripcion FROM modulo ORDER BY nombre"
        )

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Modulo().listar_modulos() == []

    def test_conexion_caida_devuelve_none(self, conexion_caída):
        assert Modulo().listar_modulos() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Modulo().listar_modulos()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Modulo().listar_modulos()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestVerificarModuloPorId:

    def test_modulo_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert Modulo(id=ID_MAXIMO).verificar_modulo_por_id() is True

        assert ultima_sentencia(cursor) == (
            "SELECT 1 FROM modulo WHERE id = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == (ID_MAXIMO,)

    def test_modulo_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Modulo(id=ID_MAXIMO).verificar_modulo_por_id() is False

    def test_sin_id_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Modulo().verificar_modulo_por_id() is False

        cursor.execute.assert_not_called()

    def test_conexion_caida_devuelve_false(self, conexion_caída):
        assert Modulo(id=ID_MAXIMO).verificar_modulo_por_id() is False

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Modulo(id=ID_MAXIMO).verificar_modulo_por_id()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Modulo(id=ID_MAXIMO).verificar_modulo_por_id()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestVerificarModuloPorNombre:

    def test_modulo_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert Modulo(nombre="Usuarios").verificar_modulo_por_nombre() is True

        assert ultima_sentencia(cursor) == (
            "SELECT 1 FROM modulo WHERE nombre = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == ("Usuarios",)

    def test_modulo_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Modulo(nombre="Inexistente").verificar_modulo_por_nombre() is False

    def test_sin_nombre_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Modulo().verificar_modulo_por_nombre() is False

        cursor.execute.assert_not_called()

    def test_conexion_caida_devuelve_false(self, conexion_caída):
        assert Modulo(nombre="Usuarios").verificar_modulo_por_nombre() is False

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Modulo(nombre="Usuarios").verificar_modulo_por_nombre()

        cierra_recursos(db, cursor)


class TestObtenerModuloPorId:

    def test_modulo_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {"id": 1, "nombre": "Usuarios", "descripcion": "Gestión"}
        cursor.fetchone.return_value = esperado

        resultado = Modulo(id=ID_MAXIMO).obtener_modulo_por_id()

        assert resultado == esperado
        assert ultima_sentencia(cursor) == (
            "SELECT id, nombre, descripcion FROM modulo WHERE id = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == (ID_MAXIMO,)

    def test_parametro_tiene_prioridad(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": 1}

        Modulo(id="99").obtener_modulo_por_id(modulo_id="1")

        assert cursor.execute.call_args.args[1] == ("1",)

    def test_modulo_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Modulo(id=ID_MAXIMO).obtener_modulo_por_id() is None

    def test_sin_id_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Modulo().obtener_modulo_por_id() is None

        cursor.execute.assert_not_called()

    def test_conexion_caida_devuelve_none(self, conexion_caída):
        assert Modulo(id=ID_MAXIMO).obtener_modulo_por_id() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": 1}

        Modulo(id=ID_MAXIMO).obtener_modulo_por_id()

        cierra_recursos(db, cursor)


class TestAgregarModulo:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None  # el módulo aún no existe
        cursor.lastrowid = 9

        modulo = Modulo(nombre="Usuarios", descripcion="Gestión de usuarios")
        resultado = modulo.agregar_modulo()

        assert resultado == "Módulo agregado exitosamente."
        assert ultima_sentencia(cursor) == (
            "INSERT INTO modulo (nombre, descripcion) VALUES (%s, %s)"
        )
        assert cursor.execute.call_args.args[1] == (
            "Usuarios",
            "Gestión de usuarios",
        )
        assert modulo.id == "9"
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 2 operaciones (buscar duplicado + INSERT): cada una cierra su cursor
        cierra_recursos(db, cursor)

    def test_valores_minimos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        cursor.lastrowid = 1

        resultado = Modulo(
            nombre=NOMBRE_MINIMO, descripcion=DESCRIPCION_MINIMA
        ).agregar_modulo()

        assert resultado == "Módulo agregado exitosamente."
        assert cursor.execute.call_args.args[1] == (
            NOMBRE_MINIMO,
            DESCRIPCION_MINIMA,
        )

    def test_valores_maximos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        cursor.lastrowid = 2

        resultado = Modulo(
            nombre=NOMBRE_MAXIMO, descripcion=DESCRIPCION_MAXIMA
        ).agregar_modulo()

        assert resultado == "Módulo agregado exitosamente."
        assert cursor.execute.call_args.args[1] == (
            NOMBRE_MAXIMO,
            DESCRIPCION_MAXIMA,
        )

    def test_descripcion_vacia_se_inserta_como_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        cursor.lastrowid = 3

        Modulo(nombre="Usuarios", descripcion="").agregar_modulo()

        assert cursor.execute.call_args.args[1] == ("Usuarios", None)

    @pytest.mark.parametrize(
        "nombre, descripcion, esperado",
        [
            pytest.param(
                "",
                "",
                "El campo Nombre no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                "M" * 51,
                "",
                "El campo Nombre no puede tener más de 50 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                "Modulo 1",
                "",
                "El campo Nombre solo puede contener letras y números (sin espacios).",
                id="nombre-con-espacios",
            ),
            pytest.param(
                "Modulo#1",
                "",
                "El campo Nombre solo puede contener letras y números (sin espacios).",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                "Usuarios",
                "D" * 256,
                "El campo Descripción no puede tener más de 255 caracteres.",
                id="descripcion-demasiado-larga",
            ),
            pytest.param(
                "Usuarios",
                "Gestión #1",
                "El campo Descripción no puede contener caracteres especiales.",
                id="descripcion-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(
        self, conexion_falsa, nombre, descripcion, esperado
    ):
        db, cursor = conexion_falsa

        resultado = Modulo(nombre=nombre, descripcion=descripcion).agregar_modulo()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_modulo_duplicado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)  # ya existe ese nombre

        resultado = Modulo(nombre="Usuarios").agregar_modulo()

        assert resultado == "El módulo 'Usuarios' ya existe."
        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Modulo(nombre="Usuarios").agregar_modulo()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        # 1ª llamada: consulta de duplicado; 2ª: el INSERT que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = Modulo(nombre="Usuarios").agregar_modulo()

        assert resultado == "Error al agregar módulo."
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_en_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        cursor.lastrowid = 9

        with patch("app.models.modulos.Bitacora") as bitacora_cls:
            Modulo(nombre="Usuarios", usuario_id=USUARIO_ID).agregar_modulo()

        bitacora_cls.assert_called_once_with(
            accion="Crear módulo",
            descripcion="Se creó el módulo: Usuarios",
            usuario_id=USUARIO_ID,
            modulo_nombre="Usuarios",
        )
        bitacora_cls.return_value.registrar.assert_called_once_with()

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        cursor.lastrowid = 9

        with patch("app.models.modulos.Bitacora") as bitacora_cls:
            Modulo(nombre="Usuarios").agregar_modulo()

        bitacora_cls.assert_not_called()


class TestActualizarModulo:

    def test_datos_validos_con_el_mismo_nombre(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), {"id": ID_MAXIMO, "nombre": "Usuarios"}]

        resultado = Modulo(
            ID_MAXIMO, "Usuarios", "Gestión de usuarios"
        ).actualizar_modulo()

        assert resultado == "Módulo actualizado exitosamente."
        assert ultima_sentencia(cursor) == (
            "UPDATE modulo SET nombre = %s, descripcion = %s WHERE id = %s"
        )
        assert cursor.execute.call_args.args[1] == (
            "Usuarios",
            "Gestión de usuarios",
            ID_MAXIMO,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 3 operaciones (verificar, consultar nombre, UPDATE)
        cierra_recursos(db, cursor)

    def test_nombre_cambiado_sin_duplicado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), {"nombre": "Usuarios"}, None]

        resultado = Modulo(
            ID_MAXIMO, "Seguridad", "Gestión de seguridad"
        ).actualizar_modulo()

        assert resultado == "Módulo actualizado exitosamente."
        assert cursor.execute.call_args.args[1] == (
            "Seguridad",
            "Gestión de seguridad",
            ID_MAXIMO,
        )
        db.commit.assert_called_once()

    def test_nombre_duplicado_de_otro_modulo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), {"nombre": "Usuarios"}, (1,)]

        resultado = Modulo(ID_MAXIMO, "Seguridad", "").actualizar_modulo()

        assert resultado == "El módulo 'Seguridad' ya existe."
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    def test_mismo_nombre_sin_importar_mayusculas(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), {"nombre": "usuarios"}]

        resultado = Modulo(ID_MAXIMO, "Usuarios", "").actualizar_modulo()

        assert resultado == "Módulo actualizado exitosamente."
        assert cursor.execute.call_count == 3  # verificar, consultar, UPDATE

    def test_modulo_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Modulo(ID_MAXIMO, "Usuarios", "").actualizar_modulo()

        assert resultado == f"El módulo con ID {ID_MAXIMO} no existe."
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "id_modulo, nombre, descripcion, esperado",
        [
            pytest.param(
                "",
                "Usuarios",
                "",
                "El ID del módulo es obligatorio.",
                id="id-vacio",
            ),
            pytest.param(
                "   ",
                "Usuarios",
                "",
                "El ID del módulo es obligatorio.",
                id="id-solo-espacios",
            ),
            pytest.param(
                "abc",
                "Usuarios",
                "",
                "El campo Módulo solo puede contener números.",
                id="id-no-numerico",
            ),
            pytest.param(
                "12345678901",
                "Usuarios",
                "",
                "El campo Módulo no puede tener más de 10 dígitos.",
                id="id-demasiado-largo",
            ),
            pytest.param(
                ID_MAXIMO,
                "",
                "",
                "El campo Nombre no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                ID_MAXIMO,
                "M" * 51,
                "",
                "El campo Nombre no puede tener más de 50 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                ID_MAXIMO,
                "Modulo 1",
                "",
                "El campo Nombre solo puede contener letras y números (sin espacios).",
                id="nombre-con-espacios",
            ),
            pytest.param(
                ID_MAXIMO,
                "Usuarios",
                "D" * 256,
                "El campo Descripción no puede tener más de 255 caracteres.",
                id="descripcion-demasiado-larga",
            ),
            pytest.param(
                ID_MAXIMO,
                "Usuarios",
                "Gestión #1",
                "El campo Descripción no puede contener caracteres especiales.",
                id="descripcion-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(
        self, conexion_falsa, id_modulo, nombre, descripcion, esperado
    ):
        db, cursor = conexion_falsa

        resultado = Modulo(id_modulo, nombre, descripcion).actualizar_modulo()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_error_de_conexion_al_actualizar(self, db_falsa):
        db, cursor = db_falsa
        cursor.fetchone.side_effect = [(1,), {"id": ID_MAXIMO, "nombre": "Usuarios"}]

        # verificar, obtener y luego la conexión para el UPDATE: falla la última
        with patch(
            "app.models.database.conectar.conexion2",
            side_effect=[db, db, None],
        ):
            resultado = Modulo(ID_MAXIMO, "Usuarios", "").actualizar_modulo()

        assert resultado == MENSAJE_ERROR_CONEXION
        sin_sentencia(cursor, "UPDATE")

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), {"id": ID_MAXIMO, "nombre": "Usuarios"}]
        # 1ª: existencia; 2ª: consulta de nombre; 3ª: el UPDATE que falla
        cursor.execute.side_effect = [None, None, Exception("fallo simulado")]

        resultado = Modulo(ID_MAXIMO, "Usuarios", "").actualizar_modulo()

        assert resultado == "Error al actualizar módulo."
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_en_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), {"id": ID_MAXIMO, "nombre": "Usuarios"}]

        with patch("app.models.modulos.Bitacora") as bitacora_cls:
            Modulo(
                ID_MAXIMO, "Usuarios", "", usuario_id=USUARIO_ID
            ).actualizar_modulo()

        bitacora_cls.assert_called_once_with(
            accion="Actualizar módulo",
            descripcion=(
                f"Se actualizó el módulo ID: {ID_MAXIMO} "
                "- Nuevo nombre: Usuarios"
            ),
            usuario_id=USUARIO_ID,
            modulo_nombre="Usuarios",
        )
        bitacora_cls.return_value.registrar.assert_called_once_with()


class TestEliminarModulo:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)  # el módulo sí existe

        resultado = Modulo(id=ID_MAXIMO).eliminar_modulo()

        assert resultado == "Módulo eliminado exitosamente."
        assert ultima_sentencia(cursor) == "DELETE FROM modulo WHERE id = %s"
        assert cursor.execute.call_args.args[1] == (ID_MAXIMO,)
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 2 operaciones (verificar + DELETE): cada una cierra su cursor
        cierra_recursos(db, cursor)

    @pytest.mark.parametrize(
        "id_modulo",
        [
            pytest.param(ID_MINIMO, id="id-minimo"),
            pytest.param(ID_MAXIMO, id="id-maximo"),
        ],
    )
    def test_limites_de_id(self, conexion_falsa, id_modulo):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        resultado = Modulo(id=id_modulo).eliminar_modulo()

        assert resultado == "Módulo eliminado exitosamente."
        assert cursor.execute.call_args.args[1] == (id_modulo,)

    def test_modulo_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Modulo(id=ID_MAXIMO).eliminar_modulo()

        assert resultado == f"El módulo con identificador {ID_MAXIMO} no existe."
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()

    def test_id_vacio_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Modulo().eliminar_modulo()

        assert resultado == "El identificador del módulo no puede estar vacío."
        cursor.execute.assert_not_called()

    def test_id_solo_espacios_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Modulo(id="   ").eliminar_modulo()

        assert resultado == "El identificador del módulo no puede estar vacío."
        cursor.execute.assert_not_called()

    @pytest.mark.parametrize(
        "id_modulo, esperado",
        [
            pytest.param(
                "abc",
                "El campo Módulo solo puede contener números.",
                id="id-no-numerico",
            ),
            pytest.param(
                "12345678901",
                "El campo Módulo no puede tener más de 10 dígitos.",
                id="id-demasiado-largo",
            ),
        ],
    )
    def test_id_invalido_no_toca_la_bd(self, conexion_falsa, id_modulo, esperado):
        db, cursor = conexion_falsa

        resultado = Modulo(id=id_modulo).eliminar_modulo()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Modulo(id=ID_MAXIMO).eliminar_modulo()

        assert resultado == (
            f"El módulo con identificador {ID_MAXIMO} no existe."
        )

    def test_error_de_conexion_al_eliminar(self, db_falsa):
        db, cursor = db_falsa
        cursor.fetchone.return_value = (1,)

        # verificar y luego la conexión para el DELETE: falla la última
        with patch(
            "app.models.database.conectar.conexion2",
            side_effect=[db, None],
        ):
            resultado = Modulo(id=ID_MAXIMO).eliminar_modulo()

        assert resultado == MENSAJE_ERROR_CONEXION
        sin_sentencia(cursor, "DELETE")

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)
        # 1ª: verificar; 2ª: el DELETE que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = Modulo(id=ID_MAXIMO).eliminar_modulo()

        assert resultado == (
            "Error al eliminar módulo. Verifica que no esté en uso por permisos."
        )
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_en_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        with patch("app.models.modulos.Bitacora") as bitacora_cls:
            Modulo(id=ID_MAXIMO, usuario_id=USUARIO_ID).eliminar_modulo()

        bitacora_cls.assert_called_once_with(
            accion="Eliminar módulo",
            descripcion=f"Se eliminó el módulo ID: {ID_MAXIMO}",
            usuario_id=USUARIO_ID,
            modulo_nombre="Usuarios",
        )
        bitacora_cls.return_value.registrar.assert_called_once_with()

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        with patch("app.models.modulos.Bitacora") as bitacora_cls:
            Modulo(id=ID_MAXIMO).eliminar_modulo()

        bitacora_cls.assert_not_called()
