"""Pruebas unitarias de la clase Rol (app.models.roles).

Los fixtures `conexion_falsa`, `conexion_caída` y `db_falsa` viven en
tests/pruebas unitarias/conftest.py; los helpers en
tests/pruebas unitarias/helpers.py.
"""
from unittest.mock import patch

import pytest

from app.models.roles import Rol
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

MENSAJE_ERROR_CONEXION = "Error al conectar a la base de datos."

# ==================== Datos de frontera ====================
ID_MINIMO = "1"  # 1 dígito (mínimo)
ID_MAXIMO = "1234567890"  # 10 dígitos (máximo)

NOMBRE_MINIMO = "R"  # 1 carácter (mínimo)
NOMBRE_MAXIMO = "R" * 50  # 50 caracteres (máximo)

DESCRIPCION_MINIMA = "D"  # 1 carácter (mínimo)
DESCRIPCION_MAXIMA = "D" * 255  # 255 caracteres (máximo)

USUARIO_ID = "7"


class TestListarRoles:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {"id": 2, "nombre": "Admin", "descripcion": "Administra el sistema"},
            {"id": 3, "nombre": "Vendedor", "descripcion": "Atiende la tienda"},
        ]
        cursor.fetchall.return_value = filas

        resultado = Rol().listar_roles()

        assert resultado == filas
        assert ultima_sentencia(cursor) == (
            "SELECT id, nombre, descripcion FROM rol ORDER BY nombre"
        )

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Rol().listar_roles() == []

    def test_conexion_caida_devuelve_none(self, conexion_caída):
        assert Rol().listar_roles() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Rol().listar_roles()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Rol().listar_roles()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestVerificarRolPorId:

    def test_rol_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert Rol(id=ID_MAXIMO).verificar_rol_por_id() is True

        assert ultima_sentencia(cursor) == (
            "SELECT 1 FROM rol WHERE id = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == (ID_MAXIMO,)

    def test_rol_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Rol(id=ID_MAXIMO).verificar_rol_por_id() is False

    def test_sin_id_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Rol().verificar_rol_por_id() is False

        cursor.execute.assert_not_called()

    def test_conexion_caida_devuelve_false(self, conexion_caída):
        assert Rol(id=ID_MAXIMO).verificar_rol_por_id() is False

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Rol(id=ID_MAXIMO).verificar_rol_por_id()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Rol(id=ID_MAXIMO).verificar_rol_por_id()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestVerificarRolPorNombre:

    def test_rol_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert Rol(nombre="Vendedor").verificar_rol_por_nombre() is True

        assert ultima_sentencia(cursor) == (
            "SELECT 1 FROM rol WHERE nombre = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == ("Vendedor",)

    def test_rol_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Rol(nombre="Inexistente").verificar_rol_por_nombre() is False

    def test_sin_nombre_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Rol().verificar_rol_por_nombre() is False

        cursor.execute.assert_not_called()

    def test_conexion_caida_devuelve_false(self, conexion_caída):
        assert Rol(nombre="Vendedor").verificar_rol_por_nombre() is False

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Rol(nombre="Vendedor").verificar_rol_por_nombre()

        cierra_recursos(db, cursor)


class TestObtenerRolPorId:

    def test_rol_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {"id": 2, "nombre": "Vendedor", "descripcion": "Atiende"}
        cursor.fetchone.return_value = esperado

        resultado = Rol(id=ID_MAXIMO).obtener_rol_por_id()

        assert resultado == esperado
        assert ultima_sentencia(cursor) == (
            "SELECT id, nombre, descripcion FROM rol WHERE id = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == (ID_MAXIMO,)

    def test_parametro_tiene_prioridad(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": 2}

        Rol(id="99").obtener_rol_por_id(rol_id="2")

        assert cursor.execute.call_args.args[1] == ("2",)

    def test_rol_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Rol(id=ID_MAXIMO).obtener_rol_por_id() is None

    def test_sin_id_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Rol().obtener_rol_por_id() is None

        cursor.execute.assert_not_called()

    def test_conexion_caida_devuelve_none(self, conexion_caída):
        assert Rol(id=ID_MAXIMO).obtener_rol_por_id() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": 2}

        Rol(id=ID_MAXIMO).obtener_rol_por_id()

        cierra_recursos(db, cursor)


class TestObtenerIdPorNombre:

    def test_rol_existe_devuelve_id_como_texto(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (5,)

        resultado = Rol(nombre="Vendedor").obtener_id_por_nombre()

        assert resultado == "5"
        assert ultima_sentencia(cursor) == (
            "SELECT id FROM rol WHERE nombre = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == ("Vendedor",)

    def test_parametro_tiene_prioridad(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (5,)

        Rol(nombre="Admin").obtener_id_por_nombre(nombre="Vendedor")

        assert cursor.execute.call_args.args[1] == ("Vendedor",)

    def test_rol_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Rol(nombre="Inexistente").obtener_id_por_nombre() is None

    def test_sin_nombre_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Rol().obtener_id_por_nombre() is None

        cursor.execute.assert_not_called()

    def test_conexion_caida_devuelve_none(self, conexion_caída):
        assert Rol(nombre="Vendedor").obtener_id_por_nombre() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (5,)

        Rol(nombre="Vendedor").obtener_id_por_nombre()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (5,)

        Rol(nombre="Vendedor").obtener_id_por_nombre()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestAgregarRol:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None  # el rol aún no existe
        cursor.lastrowid = 9

        rol = Rol(nombre="Vendedor", descripcion="Atiende la tienda")
        resultado = rol.agregar_rol()

        assert resultado == "Rol agregado exitosamente."
        assert ultima_sentencia(cursor) == (
            "INSERT INTO rol (nombre, descripcion) VALUES (%s, %s)"
        )
        assert cursor.execute.call_args.args[1] == (
            "Vendedor",
            "Atiende la tienda",
        )
        assert rol.id == "9"
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 2 operaciones (buscar duplicado + INSERT): cada una cierra su cursor
        cierra_recursos(db, cursor)

    def test_valores_minimos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        cursor.lastrowid = 1

        resultado = Rol(
            nombre=NOMBRE_MINIMO, descripcion=DESCRIPCION_MINIMA
        ).agregar_rol()

        assert resultado == "Rol agregado exitosamente."
        assert cursor.execute.call_args.args[1] == (
            NOMBRE_MINIMO,
            DESCRIPCION_MINIMA,
        )
        db.commit.assert_called_once()

    def test_valores_maximos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        cursor.lastrowid = 2

        resultado = Rol(
            nombre=NOMBRE_MAXIMO, descripcion=DESCRIPCION_MAXIMA
        ).agregar_rol()

        assert resultado == "Rol agregado exitosamente."
        assert cursor.execute.call_args.args[1] == (
            NOMBRE_MAXIMO,
            DESCRIPCION_MAXIMA,
        )
        db.commit.assert_called_once()

    def test_nombre_y_descripcion_se_limpian(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        cursor.lastrowid = 3

        Rol(nombre="  Vendedor  ", descripcion="  Atiende  ").agregar_rol()

        assert cursor.execute.call_args.args[1] == ("Vendedor", "Atiende")

    def test_descripcion_vacia_se_inserta_como_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        cursor.lastrowid = 3

        Rol(nombre="Vendedor", descripcion="").agregar_rol()

        assert cursor.execute.call_args.args[1] == ("Vendedor", None)

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
                "R" * 51,
                "",
                "El campo Nombre no puede tener más de 50 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                "Vendedor #1",
                "",
                "El campo Nombre solo puede contener letras, espacios, acentos y ñ.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                "Vendedor",
                "D" * 256,
                "El campo Descripción no puede tener más de 255 caracteres.",
                id="descripcion-demasiado-larga",
            ),
            pytest.param(
                "Vendedor",
                "Atiende #1",
                "El campo Descripción no puede contener caracteres especiales.",
                id="descripcion-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(
        self, conexion_falsa, nombre, descripcion, esperado
    ):
        db, cursor = conexion_falsa

        resultado = Rol(nombre=nombre, descripcion=descripcion).agregar_rol()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_rol_duplicado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)  # ya existe ese nombre

        resultado = Rol(nombre="Vendedor").agregar_rol()

        assert resultado == "El rol 'Vendedor' ya existe."
        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Rol(nombre="Vendedor").agregar_rol()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        # 1ª llamada: consulta de duplicado; 2ª: el INSERT que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = Rol(nombre="Vendedor").agregar_rol()

        assert resultado == "Error al agregar rol."
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_en_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        cursor.lastrowid = 9

        with patch("app.models.roles.Bitacora") as bitacora_cls:
            Rol(nombre="Vendedor", usuario_id=USUARIO_ID).agregar_rol()

        bitacora_cls.assert_called_once_with(
            accion="Crear rol",
            descripcion="Se creó el rol: Vendedor",
            usuario_id=USUARIO_ID,
            modulo_nombre="Usuarios",
        )
        bitacora_cls.return_value.registrar.assert_called_once_with()

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        cursor.lastrowid = 9

        with patch("app.models.roles.Bitacora") as bitacora_cls:
            Rol(nombre="Vendedor").agregar_rol()

        bitacora_cls.assert_not_called()


class TestActualizarRol:

    def test_datos_validos_con_el_mismo_nombre(self, conexion_falsa):
        db, cursor = conexion_falsa
        # 1ª consulta (verificar id): existe; 2ª (nombre): es el mismo rol
        cursor.fetchone.side_effect = [(1,), {"id": ID_MAXIMO, "nombre": "Vendedor"}]

        resultado = Rol(
            ID_MAXIMO, "Vendedor", "Atiende la tienda"
        ).actualizar_rol()

        assert resultado == "Rol actualizado exitosamente."
        assert ultima_sentencia(cursor) == (
            "UPDATE rol SET nombre = %s, descripcion = %s WHERE id = %s"
        )
        assert cursor.execute.call_args.args[1] == (
            "Vendedor",
            "Atiende la tienda",
            ID_MAXIMO,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 3 operaciones (verificar, consultar nombre, UPDATE)
        cierra_recursos(db, cursor)

    def test_nombre_cambiado_sin_duplicado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), {"nombre": "Vendedor"}, None]

        resultado = Rol(
            ID_MAXIMO, "Supervisor", "Supervisa la tienda"
        ).actualizar_rol()

        assert resultado == "Rol actualizado exitosamente."
        assert cursor.execute.call_args.args[1] == (
            "Supervisor",
            "Supervisa la tienda",
            ID_MAXIMO,
        )
        db.commit.assert_called_once()

    def test_nombre_duplicado_de_otro_rol(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), {"nombre": "Vendedor"}, (1,)]

        resultado = Rol(ID_MAXIMO, "Supervisor", "").actualizar_rol()

        assert resultado == "El rol 'Supervisor' ya existe."
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    def test_mismo_nombre_sin_importar_mayusculas(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), {"nombre": "vendedor"}]

        resultado = Rol(ID_MAXIMO, "Vendedor", "").actualizar_rol()

        assert resultado == "Rol actualizado exitosamente."
        assert cursor.execute.call_count == 3  # verificar, consultar, UPDATE

    def test_rol_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Rol(ID_MAXIMO, "Vendedor", "").actualizar_rol()

        assert resultado == f"El rol con ID {ID_MAXIMO} no existe."
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "id_rol, nombre, descripcion, esperado",
        [
            pytest.param(
                "",
                "Vendedor",
                "",
                "El ID del rol es obligatorio.",
                id="id-vacio",
            ),
            pytest.param(
                "   ",
                "Vendedor",
                "",
                "El ID del rol es obligatorio.",
                id="id-solo-espacios",
            ),
            pytest.param(
                "abc",
                "Vendedor",
                "",
                "El campo Rol solo puede contener números.",
                id="id-no-numerico",
            ),
            pytest.param(
                "12345678901",
                "Vendedor",
                "",
                "El campo Rol no puede tener más de 10 dígitos.",
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
                "R" * 51,
                "",
                "El campo Nombre no puede tener más de 50 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                ID_MAXIMO,
                "Vendedor #1",
                "",
                "El campo Nombre solo puede contener letras, espacios, acentos y ñ.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                ID_MAXIMO,
                "Vendedor",
                "D" * 256,
                "El campo Descripción no puede tener más de 255 caracteres.",
                id="descripcion-demasiado-larga",
            ),
            pytest.param(
                ID_MAXIMO,
                "Vendedor",
                "Atiende #1",
                "El campo Descripción no puede contener caracteres especiales.",
                id="descripcion-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(
        self, conexion_falsa, id_rol, nombre, descripcion, esperado
    ):
        db, cursor = conexion_falsa

        resultado = Rol(id_rol, nombre, descripcion).actualizar_rol()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_error_de_conexion_al_actualizar(self, db_falsa):
        db, cursor = db_falsa
        cursor.fetchone.side_effect = [(1,), {"id": ID_MAXIMO, "nombre": "Vendedor"}]

        # verificar, obtener y luego la conexión para el UPDATE: falla la última
        with patch(
            "app.models.database.conectar.conexion2",
            side_effect=[db, db, None],
        ):
            resultado = Rol(ID_MAXIMO, "Vendedor", "").actualizar_rol()

        assert resultado == MENSAJE_ERROR_CONEXION
        sin_sentencia(cursor, "UPDATE")

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), {"id": ID_MAXIMO, "nombre": "Vendedor"}]
        # 1ª: existencia; 2ª: consulta de nombre; 3ª: el UPDATE que falla
        cursor.execute.side_effect = [None, None, Exception("fallo simulado")]

        resultado = Rol(ID_MAXIMO, "Vendedor", "").actualizar_rol()

        assert resultado == "Error al actualizar rol."
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_en_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), {"id": ID_MAXIMO, "nombre": "Vendedor"}]

        with patch("app.models.roles.Bitacora") as bitacora_cls:
            Rol(ID_MAXIMO, "Vendedor", "", usuario_id=USUARIO_ID).actualizar_rol()

        bitacora_cls.assert_called_once_with(
            accion="Actualizar rol",
            descripcion=f"Se actualizó el rol ID: {ID_MAXIMO} - Nuevo nombre: Vendedor",
            usuario_id=USUARIO_ID,
            modulo_nombre="Usuarios",
        )
        bitacora_cls.return_value.registrar.assert_called_once_with()


class TestEliminarRol:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        # 1ª consulta: datos del rol; 2ª: verificación de existencia
        cursor.fetchone.side_effect = [{"nombre": "Vendedor"}, (1,)]

        resultado = Rol(id=ID_MAXIMO).eliminar_rol()

        assert resultado == "Rol eliminado exitosamente."
        assert ultima_sentencia(cursor) == "DELETE FROM rol WHERE id = %s"
        assert cursor.execute.call_args.args[1] == (ID_MAXIMO,)
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 3 operaciones (obtener, verificar, DELETE): cada una cierra su cursor
        cierra_recursos(db, cursor)

    @pytest.mark.parametrize(
        "nombre_rol",
        [
            pytest.param("Admin", id="admin"),
            pytest.param("ADMIN", id="admin-mayusculas"),
            pytest.param("Cliente", id="cliente"),
            pytest.param("cliente", id="cliente-minusculas"),
        ],
    )
    def test_no_permite_eliminar_admin_ni_cliente(
        self, conexion_falsa, nombre_rol
    ):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"nombre": nombre_rol}

        resultado = Rol(id=ID_MAXIMO).eliminar_rol()

        assert resultado == "No se puede eliminar el rol Admin o Cliente."
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()

    def test_rol_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, None]

        resultado = Rol(id=ID_MAXIMO).eliminar_rol()

        assert resultado == f"El rol con identificador {ID_MAXIMO} no existe."
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()

    def test_id_vacio_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Rol().eliminar_rol()

        assert resultado == "El identificador del rol no puede estar vacío."
        cursor.execute.assert_not_called()

    def test_id_solo_espacios_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Rol(id="   ").eliminar_rol()

        assert resultado == "El identificador del rol no puede estar vacío."
        cursor.execute.assert_not_called()

    @pytest.mark.parametrize(
        "id_rol, esperado",
        [
            pytest.param(
                "abc",
                "El campo Rol solo puede contener números.",
                id="id-no-numerico",
            ),
            pytest.param(
                "12345678901",
                "El campo Rol no puede tener más de 10 dígitos.",
                id="id-demasiado-largo",
            ),
            pytest.param(
                "12a",
                "El campo Rol solo puede contener números.",
                id="id-letras-y-numeros",
            ),
        ],
    )
    def test_id_invalido_no_toca_la_bd(self, conexion_falsa, id_rol, esperado):
        db, cursor = conexion_falsa

        resultado = Rol(id=id_rol).eliminar_rol()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Rol(id=ID_MAXIMO).eliminar_rol()

        assert resultado == (
            f"El rol con identificador {ID_MAXIMO} no existe."
        )

    def test_error_de_conexion_al_eliminar(self, db_falsa):
        db, cursor = db_falsa
        cursor.fetchone.side_effect = [{"nombre": "Vendedor"}, (1,)]

        # obtener, verificar y luego la conexión para el DELETE: falla la última
        with patch(
            "app.models.database.conectar.conexion2",
            side_effect=[db, db, None],
        ):
            resultado = Rol(id=ID_MAXIMO).eliminar_rol()

        assert resultado == MENSAJE_ERROR_CONEXION
        sin_sentencia(cursor, "DELETE")

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, (1,)]
        # 1ª: obtener; 2ª: verificar; 3ª: el DELETE que falla
        cursor.execute.side_effect = [None, None, Exception("fallo simulado")]

        resultado = Rol(id=ID_MAXIMO).eliminar_rol()

        assert resultado == (
            "Error al eliminar rol. Verifica que no esté en uso por usuarios."
        )
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_en_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [{"nombre": "Vendedor"}, (1,)]

        with patch("app.models.roles.Bitacora") as bitacora_cls:
            Rol(id=ID_MAXIMO, usuario_id=USUARIO_ID).eliminar_rol()

        bitacora_cls.assert_called_once_with(
            accion="Eliminar rol",
            descripcion=f"Se eliminó el rol ID: {ID_MAXIMO} - Nombre: Vendedor",
            usuario_id=USUARIO_ID,
            modulo_nombre="Usuarios",
        )
        bitacora_cls.return_value.registrar.assert_called_once_with()

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [{"nombre": "Vendedor"}, (1,)]

        with patch("app.models.roles.Bitacora") as bitacora_cls:
            Rol(id=ID_MAXIMO).eliminar_rol()

        bitacora_cls.assert_not_called()
