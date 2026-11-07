"""Pruebas unitarias de la clase Usuarios (app.models.usuarios).

Cubre consultas, verificaciones, mutaciones, login y perfil. Los fixtures
`conexion_falsa` y `conexion_caída` viven en tests/pruebas unitarias/conftest.py
y los helpers en helpers.py. La bitácora se mockea para no tocar la BD de
seguridad y los hashes se comprueban con werkzeug real o con un valor fijo.
"""
from contextlib import contextmanager
from unittest.mock import patch

import pytest
from werkzeug.security import check_password_hash, generate_password_hash

from app.models.usuarios import Usuarios
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

MENSAJE_ERROR_CONEXION = "Error al conectar a la base de datos."

# ==================== Datos de frontera ====================
ID_USUARIO = "USR-010"

NOMBRE_MINIMO = "Ana"  # 3 caracteres (se permite desde 1)
NOMBRE_MAXIMO = "N" * 50  # 50 caracteres (máximo)

CEDULA_MINIMA = "123456"  # 6 dígitos (mínimo)
CEDULA_MAXIMA = "12345678"  # 8 dígitos (máximo)

PASSWORD_MINIMA = "Clave1"  # 6 caracteres (mínimo)
PASSWORD_MAXIMA = "P" * 50  # 50 caracteres (máximo)

ROL_VALIDO = "2"
FOTO_PERFIL = "/static/img/usuarios/ana.png"


def usuario(**cambios):
    """Crea un Usuarios con datos válidos salvo los campos indicados."""
    datos = {
        "id": ID_USUARIO,
        "nombre": NOMBRE_MINIMO,
        "cedula": CEDULA_MAXIMA,
        "password": PASSWORD_MINIMA,
        "rol_id": ROL_VALIDO,
        "foto_perfil": "",
        "activo": True,
        "usuario_id": None,
    }
    datos.update(cambios)
    return Usuarios(**datos)


@contextmanager
def verificaciones_agregar(nombre=False, cedula=False, rol=True):
    """Evita que agregar_usuario consulte la BD para sus verificaciones."""
    with patch.object(
        Usuarios, "verificar_usuario_por_nombre", return_value=nombre
    ), patch.object(
        Usuarios, "verificar_cedula_en_uso", return_value=cedula
    ), patch.object(
        Usuarios, "verificar_rol_y_cedula", return_value=rol
    ):
        yield


@contextmanager
def verificaciones_actualizar(por_id=True, cedula=False, rol=True):
    """Evita que actualizar_usuario consulte la BD para sus verificaciones."""
    with patch.object(
        Usuarios, "verificar_usuario_por_id", return_value=por_id
    ), patch.object(
        Usuarios, "verificar_cedula_en_uso", return_value=cedula
    ), patch.object(
        Usuarios, "verificar_rol_y_cedula", return_value=rol
    ):
        yield


@contextmanager
def hash_fijo(valor="hash-falso"):
    """Sustituye el hash real por un valor determinista."""
    with patch.object(Usuarios, "_hash_password", return_value=valor):
        yield


class TestHashDeContrasenas:

    def test_hash_no_es_la_contrasena_en_claro(self):
        password_hash = Usuarios()._hash_password(PASSWORD_MINIMA)

        assert password_hash != PASSWORD_MINIMA
        assert check_password_hash(password_hash, PASSWORD_MINIMA) is True

    def test_verify_password_correcta(self):
        password_hash = generate_password_hash(PASSWORD_MINIMA)

        assert Usuarios()._verify_password(PASSWORD_MINIMA, password_hash) is True

    def test_verify_password_incorrecta(self):
        password_hash = generate_password_hash(PASSWORD_MINIMA)

        assert Usuarios()._verify_password("OtraClave", password_hash) is False


class TestListarUsuarios:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {
                "id": ID_USUARIO,
                "nombre": NOMBRE_MINIMO,
                "cedula_personal": CEDULA_MAXIMA,
                "rol_id": ROL_VALIDO,
                "rol_nombre": "empleado",
                "activo": 1,
            }
        ]
        cursor.fetchall.return_value = filas

        resultado = Usuarios().listar_usuarios()

        assert resultado == filas
        assert "FROM usuario u" in ultima_sentencia(cursor)
        assert "INNER JOIN rol r" in ultima_sentencia(cursor)
        assert "ORDER BY u.fecha_creacion DESC" in ultima_sentencia(cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Usuarios().listar_usuarios() == []

    def test_conexion_caida(self, conexion_caída):
        assert Usuarios().listar_usuarios() is None

    def test_error_de_bd_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Usuarios().listar_usuarios() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Usuarios().listar_usuarios()

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Usuarios().listar_usuarios()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestListarEmpleados:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {
                "cedula": CEDULA_MINIMA,
                "nombre": NOMBRE_MINIMO,
                "apellido": "Paz",
                "nombre_completo": "Ana Paz",
            }
        ]
        cursor.fetchall.return_value = filas

        resultado = Usuarios().listar_empleados()

        assert resultado == filas
        assert "FROM Empleado e" in ultima_sentencia(cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Usuarios().listar_empleados() == []

    def test_conexion_caida(self, conexion_caída):
        assert Usuarios().listar_empleados() is None

    def test_error_de_bd_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Usuarios().listar_empleados() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Usuarios().listar_empleados()

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Usuarios().listar_empleados()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestListarClientesUsuarios:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {
                "cedula": CEDULA_MAXIMA,
                "nombre_completo": "Ana Paz",
                "celular": "04121234567",
                "correo": "ana@mail.com",
            }
        ]
        cursor.fetchall.return_value = filas

        resultado = Usuarios().listar_clientes()

        assert resultado == filas
        assert "FROM Persona_natural pn" in ultima_sentencia(cursor)
        assert "INNER JOIN Cliente c" in ultima_sentencia(cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Usuarios().listar_clientes() == []

    def test_conexion_caida(self, conexion_caída):
        assert Usuarios().listar_clientes() is None

    def test_error_de_bd_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Usuarios().listar_clientes() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Usuarios().listar_clientes()

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Usuarios().listar_clientes()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestVerificarEmpleado:

    def test_empleado_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert Usuarios().verificar_empleado(CEDULA_MINIMA) is True

        assert ultima_sentencia(cursor) == (
            "SELECT 1 FROM Empleado WHERE ID_empleado = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == (CEDULA_MINIMA,)

    def test_empleado_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Usuarios().verificar_empleado(CEDULA_MINIMA) is False

    def test_conexion_caida(self, conexion_caída):
        assert Usuarios().verificar_empleado(CEDULA_MINIMA) is False

    def test_error_de_bd_devuelve_false(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Usuarios().verificar_empleado(CEDULA_MINIMA) is False

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Usuarios().verificar_empleado(CEDULA_MINIMA)

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Usuarios().verificar_empleado(CEDULA_MINIMA)

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestVerificarCliente:

    def test_cliente_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert Usuarios().verificar_cliente(CEDULA_MAXIMA) is True

        assert ultima_sentencia(cursor) == (
            "SELECT 1 FROM Persona_natural WHERE ID_cliente = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == (CEDULA_MAXIMA,)

    def test_cliente_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Usuarios().verificar_cliente(CEDULA_MAXIMA) is False

    def test_conexion_caida(self, conexion_caída):
        assert Usuarios().verificar_cliente(CEDULA_MAXIMA) is False

    def test_error_de_bd_devuelve_false(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Usuarios().verificar_cliente(CEDULA_MAXIMA) is False

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Usuarios().verificar_cliente(CEDULA_MAXIMA)

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Usuarios().verificar_cliente(CEDULA_MAXIMA)

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestVerificarUsuarioPorId:

    @pytest.mark.parametrize(
        "id_usuario",
        [
            pytest.param("", id="id-vacio"),
            pytest.param(None, id="id-none"),
        ],
    )
    def test_sin_id_devuelve_false(self, conexion_falsa, id_usuario):
        db, cursor = conexion_falsa

        assert Usuarios(id=id_usuario).verificar_usuario_por_id() is False
        cursor.execute.assert_not_called()

    def test_usuario_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert Usuarios(id=ID_USUARIO).verificar_usuario_por_id() is True

        assert ultima_sentencia(cursor) == (
            "SELECT 1 FROM usuario WHERE id = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == (ID_USUARIO,)

    def test_usuario_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Usuarios(id=ID_USUARIO).verificar_usuario_por_id() is False

    def test_conexion_caida(self, conexion_caída):
        assert Usuarios(id=ID_USUARIO).verificar_usuario_por_id() is False

    def test_error_de_bd_devuelve_false(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Usuarios(id=ID_USUARIO).verificar_usuario_por_id() is False

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Usuarios(id=ID_USUARIO).verificar_usuario_por_id()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Usuarios(id=ID_USUARIO).verificar_usuario_por_id()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestVerificarUsuarioPorNombre:

    @pytest.mark.parametrize(
        "nombre",
        [
            pytest.param("", id="nombre-vacio"),
            pytest.param(None, id="nombre-none"),
        ],
    )
    def test_sin_nombre_devuelve_false(self, conexion_falsa, nombre):
        db, cursor = conexion_falsa

        assert Usuarios(nombre=nombre).verificar_usuario_por_nombre() is False
        cursor.execute.assert_not_called()

    def test_usuario_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert Usuarios(nombre=NOMBRE_MINIMO).verificar_usuario_por_nombre() is True

        assert ultima_sentencia(cursor) == (
            "SELECT 1 FROM usuario WHERE nombre = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == (NOMBRE_MINIMO,)

    def test_usuario_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Usuarios(nombre=NOMBRE_MINIMO).verificar_usuario_por_nombre() is False

    def test_conexion_caida(self, conexion_caída):
        assert Usuarios(nombre=NOMBRE_MINIMO).verificar_usuario_por_nombre() is False

    def test_error_de_bd_devuelve_false(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Usuarios(nombre=NOMBRE_MINIMO).verificar_usuario_por_nombre() is False

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Usuarios(nombre=NOMBRE_MINIMO).verificar_usuario_por_nombre()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Usuarios(nombre=NOMBRE_MINIMO).verificar_usuario_por_nombre()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestVerificarCedulaEnUso:

    def test_cedula_en_uso(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert Usuarios().verificar_cedula_en_uso(CEDULA_MAXIMA) is True

        assert ultima_sentencia(cursor) == (
            "SELECT 1 FROM usuario WHERE cedula = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == (CEDULA_MAXIMA,)

    def test_cedula_libre(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Usuarios().verificar_cedula_en_uso(CEDULA_MAXIMA) is False

    def test_excluye_el_propio_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Usuarios().verificar_cedula_en_uso(CEDULA_MAXIMA, ID_USUARIO) is False

        assert "id != %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (CEDULA_MAXIMA, ID_USUARIO)

    def test_sin_usuario_id_no_excluye(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        Usuarios().verificar_cedula_en_uso(CEDULA_MAXIMA)

        assert "id != %s" not in ultima_sentencia(cursor)

    def test_conexion_caida(self, conexion_caída):
        assert Usuarios().verificar_cedula_en_uso(CEDULA_MAXIMA) is False

    def test_error_de_bd_devuelve_false(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Usuarios().verificar_cedula_en_uso(CEDULA_MAXIMA) is False

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        Usuarios().verificar_cedula_en_uso(CEDULA_MAXIMA)

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        Usuarios().verificar_cedula_en_uso(CEDULA_MAXIMA)

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestVerificarRolYCedula:

    @pytest.mark.parametrize(
        "cedula, rol_id",
        [
            pytest.param("", ROL_VALIDO, id="cedula-vacia"),
            pytest.param(CEDULA_MAXIMA, "", id="rol-vacio"),
            pytest.param(None, ROL_VALIDO, id="cedula-none"),
            pytest.param(CEDULA_MAXIMA, None, id="rol-none"),
        ],
    )
    def test_sin_datos_devuelve_false(self, conexion_falsa, cedula, rol_id):
        db, cursor = conexion_falsa

        assert Usuarios(
            cedula=cedula, rol_id=rol_id
        ).verificar_rol_y_cedula() is False
        cursor.execute.assert_not_called()

    def test_rol_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Usuarios(
            cedula=CEDULA_MAXIMA, rol_id=ROL_VALIDO
        ).verificar_rol_y_cedula() is False

    @pytest.mark.parametrize(
        "nombre_rol",
        [
            pytest.param("cliente", id="cliente-minusculas"),
            pytest.param("CLIENTE", id="cliente-mayusculas"),
            pytest.param("Cliente", id="cliente-capitalizado"),
        ],
    )
    def test_rol_cliente_siempre_es_valido(self, conexion_falsa, nombre_rol):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"nombre": nombre_rol}

        assert Usuarios(
            cedula=CEDULA_MAXIMA, rol_id="1"
        ).verificar_rol_y_cedula() is True

        # No consulta la tabla Empleado para el rol cliente
        assert all(
            "FROM Empleado" not in llamada.args[0]
            for llamada in cursor.execute.call_args_list
        )

    def test_rol_empleado_con_empleado_existente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [{"nombre": "Técnico"}, (1,)]

        assert Usuarios(
            cedula=CEDULA_MAXIMA, rol_id=ROL_VALIDO
        ).verificar_rol_y_cedula() is True

        assert any(
            "FROM Empleado" in llamada.args[0]
            for llamada in cursor.execute.call_args_list
        )

    def test_rol_empleado_sin_empleado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [{"nombre": "Técnico"}, None]

        assert Usuarios(
            cedula=CEDULA_MAXIMA, rol_id=ROL_VALIDO
        ).verificar_rol_y_cedula() is False

    def test_conexion_caida(self, conexion_caída):
        assert Usuarios(
            cedula=CEDULA_MAXIMA, rol_id=ROL_VALIDO
        ).verificar_rol_y_cedula() is False

    def test_error_de_bd_devuelve_false(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Usuarios(
            cedula=CEDULA_MAXIMA, rol_id=ROL_VALIDO
        ).verificar_rol_y_cedula() is False

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"nombre": "cliente"}

        Usuarios(cedula=CEDULA_MAXIMA, rol_id=ROL_VALIDO).verificar_rol_y_cedula()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"nombre": "cliente"}

        Usuarios(cedula=CEDULA_MAXIMA, rol_id=ROL_VALIDO).verificar_rol_y_cedula()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestAgregarUsuario:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("USR-007",)
        nuevo = usuario()

        with verificaciones_agregar(), hash_fijo():
            resultado = nuevo.agregar_usuario()

        assert resultado == "Usuario agregado exitosamente."
        sentencia, parametros = cursor.execute.call_args.args
        assert "INSERT INTO usuario" in sentencia
        assert parametros == (
            "USR-008",
            NOMBRE_MINIMO,
            CEDULA_MAXIMA,
            "hash-falso",
            ROL_VALIDO,
            None,
        )
        assert nuevo.id == "USR-008"
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_primer_usuario_genera_usr_001(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with verificaciones_agregar(), hash_fijo():
            resultado = usuario().agregar_usuario()

        assert resultado == "Usuario agregado exitosamente."
        assert cursor.execute.call_args.args[1][0] == "USR-001"

    def test_genera_id_con_fallback_si_no_es_correlativo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [("X",), (5,)]

        with verificaciones_agregar(), hash_fijo():
            resultado = usuario().agregar_usuario()

        assert resultado == "Usuario agregado exitosamente."
        assert cursor.execute.call_args_list[-1].args[1][0] == "USR-006"
        assert any(
            "MAX(CAST(SUBSTRING(id, 5) AS UNSIGNED))" in llamada.args[0]
            for llamada in cursor.execute.call_args_list
        )

    def test_genera_id_si_el_fallback_no_devuelve_nada(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [("USR",), (None,)]

        with verificaciones_agregar(), hash_fijo():
            resultado = usuario().agregar_usuario()

        assert resultado == "Usuario agregado exitosamente."
        assert cursor.execute.call_args_list[-1].args[1][0] == "USR-001"

    def test_foto_perfil_se_guarda(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with verificaciones_agregar(), hash_fijo():
            usuario(foto_perfil=FOTO_PERFIL).agregar_usuario()

        assert cursor.execute.call_args.args[1][-1] == FOTO_PERFIL

    def test_nombre_duplicado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        resultado = usuario().agregar_usuario()

        assert resultado == f"El nombre de usuario '{NOMBRE_MINIMO}' ya existe."
        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    def test_cedula_duplicada(self, conexion_falsa):
        db, cursor = conexion_falsa
        # 1ª: nombre libre; 2ª: cédula en uso
        cursor.fetchone.side_effect = [None, (1,)]

        resultado = usuario().agregar_usuario()

        assert resultado == (
            f"La cédula '{CEDULA_MAXIMA}' ya está asignada a otro usuario."
        )
        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    def test_rol_no_corresponde_a_la_cedula(self, conexion_falsa):
        db, cursor = conexion_falsa
        # nombre libre, cédula libre, rol inexistente
        cursor.fetchone.side_effect = [None, None, None]

        resultado = usuario().agregar_usuario()

        assert resultado == (
            "La cédula no corresponde al tipo de rol seleccionado."
        )
        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"nombre": ""},
                "El campo Nombre no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                {"nombre": "   "},
                "El campo Nombre no puede estar vacío.",
                id="nombre-solo-espacios",
            ),
            pytest.param(
                {"nombre": "N" * 51},
                "El campo Nombre no puede tener más de 50 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                {"nombre": "Ana #1"},
                "El campo Nombre solo puede contener letras, espacios, acentos y ñ.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                {"cedula": ""},
                "El campo Cédula no puede estar vacío.",
                id="cedula-vacia",
            ),
            pytest.param(
                {"cedula": "12345"},
                "El campo Cédula debe tener al menos 6 dígitos.",
                id="cedula-demasiado-corta",
            ),
            pytest.param(
                {"cedula": "123456789"},
                "El campo Cédula no puede tener más de 8 dígitos.",
                id="cedula-demasiado-larga",
            ),
            pytest.param(
                {"cedula": "12345a"},
                "El campo Cédula solo puede contener números.",
                id="cedula-no-numerica",
            ),
            pytest.param(
                {"password": ""},
                "La contraseña es obligatoria.",
                id="password-vacia",
            ),
            pytest.param(
                {"password": "12345"},
                "El campo Contraseña debe tener al menos 6 caracteres.",
                id="password-demasiado-corta",
            ),
            pytest.param(
                {"password": "P" * 51},
                "El campo Contraseña no puede tener más de 50 caracteres.",
                id="password-demasiado-larga",
            ),
            pytest.param(
                {"password": "abc 123"},
                "El campo Contraseña no puede contener espacios.",
                id="password-con-espacios",
            ),
            pytest.param(
                {"rol_id": ""},
                "El rol es obligatorio.",
                id="rol-vacio",
            ),
            pytest.param(
                {"rol_id": "abc"},
                "El campo Rol solo puede contener números.",
                id="rol-no-numerico",
            ),
            pytest.param(
                {"rol_id": "1" * 11},
                "El campo Rol no puede tener más de 10 dígitos.",
                id="rol-demasiado-largo",
            ),
            pytest.param(
                {"foto_perfil": "F" * 101},
                "La ruta de la foto de perfil no puede exceder 100 caracteres.",
                id="foto-demasiado-larga",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(self, conexion_falsa, cambios, esperado):
        db, cursor = conexion_falsa

        resultado = usuario(**cambios).agregar_usuario()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        with verificaciones_agregar():
            resultado = usuario().agregar_usuario()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        # 1ª: MAX(id); 2ª: INSERT que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        with verificaciones_agregar(), hash_fijo():
            resultado = usuario().agregar_usuario()

        assert resultado == "Error al agregar usuario: fallo simulado"
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_guarda_un_hash_real(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with verificaciones_agregar():
            usuario().agregar_usuario()

        password_guardada = cursor.execute.call_args.args[1][3]
        assert password_guardada != PASSWORD_MINIMA
        assert check_password_hash(password_guardada, PASSWORD_MINIMA) is True

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with verificaciones_agregar(), hash_fijo(), patch(
            "app.models.usuarios.Bitacora"
        ) as bitacora_clase:
            resultado = usuario(usuario_id="USR-000").agregar_usuario()

        assert resultado == "Usuario agregado exitosamente."
        bitacora_clase.assert_called_once_with(
            accion="Crear usuario",
            descripcion=(
                f"Se creó el usuario: {NOMBRE_MINIMO} - "
                f"Cédula: {CEDULA_MAXIMA} - Rol ID: {ROL_VALIDO}"
            ),
            usuario_id="USR-000",
            modulo_nombre="Usuarios",
        )
        bitacora_clase.return_value.registrar.assert_called_once_with()

    def test_sin_usuario_id_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with verificaciones_agregar(), hash_fijo(), patch(
            "app.models.usuarios.Bitacora"
        ) as bitacora_clase:
            usuario().agregar_usuario()

        bitacora_clase.assert_not_called()

    def test_error_inesperado_devuelve_mensaje(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch.object(
            Usuarios, "_validar_datos_usuario", side_effect=Exception("boom")
        ):
            resultado = usuario().agregar_usuario()

        assert resultado == "Error en agregar_usuario: boom"
        db.rollback.assert_not_called()


class TestActualizarUsuario:

    def test_datos_validos_sin_password(self, conexion_falsa):
        db, cursor = conexion_falsa

        with verificaciones_actualizar():
            resultado = usuario(password="").actualizar_usuario()

        assert resultado == "Usuario actualizado exitosamente."
        sentencia, parametros = cursor.execute.call_args.args
        assert "UPDATE usuario" in sentencia
        assert "password" not in sentencia
        assert parametros == (
            NOMBRE_MINIMO,
            CEDULA_MAXIMA,
            ROL_VALIDO,
            None,
            ID_USUARIO,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_datos_validos_con_password(self, conexion_falsa):
        db, cursor = conexion_falsa

        with verificaciones_actualizar(), hash_fijo():
            resultado = usuario(password=PASSWORD_MAXIMA).actualizar_usuario()

        assert resultado == "Usuario actualizado exitosamente."
        sentencia, parametros = cursor.execute.call_args.args
        assert "password = %s" in sentencia
        assert parametros == (
            NOMBRE_MINIMO,
            CEDULA_MAXIMA,
            "hash-falso",
            ROL_VALIDO,
            None,
            ID_USUARIO,
        )

    def test_foto_perfil_se_actualiza(self, conexion_falsa):
        db, cursor = conexion_falsa

        with verificaciones_actualizar():
            usuario(foto_perfil=FOTO_PERFIL, password="").actualizar_usuario()

        assert cursor.execute.call_args.args[1][3] == FOTO_PERFIL

    @pytest.mark.parametrize(
        "id_usuario",
        [
            pytest.param("", id="id-vacio"),
            pytest.param(None, id="id-none"),
            pytest.param("   ", id="id-solo-espacios"),
        ],
    )
    def test_sin_id_devuelve_error(self, conexion_falsa, id_usuario):
        db, cursor = conexion_falsa

        resultado = usuario(id=id_usuario).actualizar_usuario()

        assert resultado == "El ID del usuario es obligatorio."
        cursor.execute.assert_not_called()

    def test_usuario_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa

        with verificaciones_actualizar(por_id=False):
            resultado = usuario().actualizar_usuario()

        assert resultado == f"El usuario con ID {ID_USUARIO} no existe."
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_cedula_asignada_a_otro_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa

        with verificaciones_actualizar(cedula=True):
            resultado = usuario().actualizar_usuario()

        assert resultado == (
            f"La cédula '{CEDULA_MAXIMA}' ya está asignada a otro usuario."
        )
        cursor.execute.assert_not_called()

    def test_rol_no_corresponde_a_la_cedula(self, conexion_falsa):
        db, cursor = conexion_falsa

        with verificaciones_actualizar(rol=False):
            resultado = usuario().actualizar_usuario()

        assert resultado == (
            "La cédula no corresponde al tipo de rol seleccionado."
        )
        cursor.execute.assert_not_called()

    def test_verifica_la_cedula_excluyendo_al_propio_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa

        with verificaciones_actualizar(), patch.object(
            Usuarios, "verificar_cedula_en_uso", return_value=False
        ) as verificar_cedula:
            usuario().actualizar_usuario()

        verificar_cedula.assert_called_once_with(CEDULA_MAXIMA, ID_USUARIO)

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"nombre": ""},
                "El campo Nombre no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                {"nombre": "N" * 51},
                "El campo Nombre no puede tener más de 50 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                {"nombre": "Ana #1"},
                "El campo Nombre solo puede contener letras, espacios, acentos y ñ.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                {"cedula": ""},
                "El campo Cédula no puede estar vacío.",
                id="cedula-vacia",
            ),
            pytest.param(
                {"cedula": "12345"},
                "El campo Cédula debe tener al menos 6 dígitos.",
                id="cedula-demasiado-corta",
            ),
            pytest.param(
                {"cedula": "123456789"},
                "El campo Cédula no puede tener más de 8 dígitos.",
                id="cedula-demasiado-larga",
            ),
            pytest.param(
                {"cedula": "12345a"},
                "El campo Cédula solo puede contener números.",
                id="cedula-no-numerica",
            ),
            pytest.param(
                {"password": "12345"},
                "El campo Contraseña debe tener al menos 6 caracteres.",
                id="password-demasiado-corta",
            ),
            pytest.param(
                {"password": "P" * 51},
                "El campo Contraseña no puede tener más de 50 caracteres.",
                id="password-demasiado-larga",
            ),
            pytest.param(
                {"password": "abc 123"},
                "El campo Contraseña no puede contener espacios.",
                id="password-con-espacios",
            ),
            pytest.param(
                {"rol_id": ""},
                "El rol es obligatorio.",
                id="rol-vacio",
            ),
            pytest.param(
                {"rol_id": "abc"},
                "El campo Rol solo puede contener números.",
                id="rol-no-numerico",
            ),
            pytest.param(
                {"rol_id": "1" * 11},
                "El campo Rol no puede tener más de 10 dígitos.",
                id="rol-demasiado-largo",
            ),
            pytest.param(
                {"foto_perfil": "F" * 101},
                "La ruta de la foto de perfil no puede exceder 100 caracteres.",
                id="foto-demasiado-larga",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(self, conexion_falsa, cambios, esperado):
        db, cursor = conexion_falsa

        resultado = usuario(**cambios).actualizar_usuario()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        with verificaciones_actualizar():
            resultado = usuario().actualizar_usuario()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa

        with verificaciones_actualizar():
            cursor.execute.side_effect = Exception("fallo simulado")
            resultado = usuario().actualizar_usuario()

        assert resultado == "Error al actualizar usuario."
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa

        with verificaciones_actualizar(), patch(
            "app.models.usuarios.Bitacora"
        ) as bitacora_clase:
            resultado = usuario(
                password="", usuario_id="USR-000"
            ).actualizar_usuario()

        assert resultado == "Usuario actualizado exitosamente."
        bitacora_clase.assert_called_once_with(
            accion="Actualizar usuario",
            descripcion=(
                f"Se actualizó el usuario ID: {ID_USUARIO} - "
                f"Nuevo nombre: {NOMBRE_MINIMO} - Rol ID: {ROL_VALIDO}"
            ),
            usuario_id="USR-000",
            modulo_nombre="Usuarios",
        )
        bitacora_clase.return_value.registrar.assert_called_once_with()

    def test_error_inesperado_devuelve_mensaje(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch.object(
            Usuarios, "_validar_datos_usuario", side_effect=Exception("boom")
        ):
            resultado = usuario().actualizar_usuario()

        assert resultado == "Error en actualizar_usuario: boom"


class TestEliminarUsuario:

    def test_elimina_usuario_no_admin(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"total": 2},
            {"rol_nombre": "empleado", "usuario_nombre": NOMBRE_MINIMO},
        ]

        with patch.object(Usuarios, "verificar_usuario_por_id", return_value=True):
            resultado = usuario().eliminar_usuario()

        assert resultado == "Usuario eliminado exitosamente."
        assert ultima_sentencia(cursor) == "DELETE FROM usuario WHERE id = %s"
        assert cursor.execute.call_args.args[1] == (ID_USUARIO,)
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_elimina_admin_si_hay_otro_admin(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"total": 2},
            {"rol_nombre": "admin", "usuario_nombre": "Root"},
        ]

        with patch.object(Usuarios, "verificar_usuario_por_id", return_value=True):
            resultado = usuario().eliminar_usuario()

        assert resultado == "Usuario eliminado exitosamente."
        assert "DELETE FROM usuario" in ultima_sentencia(cursor)

    @pytest.mark.parametrize(
        "total_admins",
        [
            pytest.param(1, id="un-admin"),
            pytest.param(0, id="sin-admins"),
        ],
    )
    def test_no_elimina_el_unico_admin(self, conexion_falsa, total_admins):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"total": total_admins},
            {"rol_nombre": "admin", "usuario_nombre": "Root"},
        ]

        with patch.object(Usuarios, "verificar_usuario_por_id", return_value=True):
            resultado = usuario().eliminar_usuario()

        assert resultado == "No se puede eliminar el único administrador del sistema."
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()

    def test_usuario_sin_fila_de_rol(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [{"total": 3}, None]

        with patch.object(Usuarios, "verificar_usuario_por_id", return_value=True):
            resultado = usuario().eliminar_usuario()

        assert resultado == "Usuario eliminado exitosamente."
        assert "DELETE FROM usuario" in ultima_sentencia(cursor)

    def test_conteo_de_admins_none_se_trata_como_cero(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            None,
            {"rol_nombre": "empleado", "usuario_nombre": NOMBRE_MINIMO},
        ]

        with patch.object(Usuarios, "verificar_usuario_por_id", return_value=True):
            resultado = usuario().eliminar_usuario()

        assert resultado == "Usuario eliminado exitosamente."

    @pytest.mark.parametrize(
        "id_usuario",
        [
            pytest.param("", id="id-vacio"),
            pytest.param(None, id="id-none"),
            pytest.param("   ", id="id-solo-espacios"),
        ],
    )
    def test_sin_id_devuelve_error(self, conexion_falsa, id_usuario):
        db, cursor = conexion_falsa

        resultado = usuario(id=id_usuario).eliminar_usuario()

        assert resultado == "El identificador del usuario no puede estar vacío."
        cursor.execute.assert_not_called()

    def test_usuario_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch.object(Usuarios, "verificar_usuario_por_id", return_value=False):
            resultado = usuario().eliminar_usuario()

        assert resultado == (
            f"El usuario con identificador {ID_USUARIO} no existe."
        )
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        with patch.object(Usuarios, "verificar_usuario_por_id", return_value=True):
            resultado = usuario().eliminar_usuario()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"total": 2},
            {"rol_nombre": "empleado", "usuario_nombre": NOMBRE_MINIMO},
        ]
        # 1ª: conteo; 2ª: rol; 3ª: DELETE que falla
        cursor.execute.side_effect = [None, None, Exception("fallo simulado")]

        with patch.object(Usuarios, "verificar_usuario_por_id", return_value=True):
            resultado = usuario().eliminar_usuario()

        assert resultado == (
            "Error al eliminar usuario. Verifica que no esté en uso."
        )
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"total": 2},
            {"rol_nombre": "empleado", "usuario_nombre": NOMBRE_MINIMO},
        ]

        with patch.object(
            Usuarios, "verificar_usuario_por_id", return_value=True
        ), patch("app.models.usuarios.Bitacora") as bitacora_clase:
            resultado = usuario(usuario_id="USR-000").eliminar_usuario()

        assert resultado == "Usuario eliminado exitosamente."
        bitacora_clase.assert_called_once_with(
            accion="Eliminar usuario",
            descripcion=(
                f"Se eliminó el usuario ID: {ID_USUARIO} - "
                f"Nombre: {NOMBRE_MINIMO}"
            ),
            usuario_id="USR-000",
            modulo_nombre="Usuarios",
        )
        bitacora_clase.return_value.registrar.assert_called_once_with()

    def test_error_inesperado_devuelve_mensaje(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch.object(
            Usuarios, "verificar_usuario_por_id", side_effect=Exception("boom")
        ):
            resultado = usuario().eliminar_usuario()

        assert resultado == "Error en eliminar_usuario: boom"


class TestObtenerRolPorNombre:

    def test_rol_encontrado_por_parametro(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {"id": "2", "nombre": "empleado", "descripcion": "Empleado"}
        cursor.fetchone.return_value = esperado

        resultado = Usuarios().obtener_rol_por_nombre("empleado")

        assert resultado == esperado
        assert ultima_sentencia(cursor) == (
            "SELECT id, nombre, descripcion FROM rol WHERE nombre = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == ("empleado",)

    def test_usa_el_nombre_de_la_instancia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": "1", "nombre": "admin"}

        resultado = Usuarios(nombre="admin").obtener_rol_por_nombre()

        assert resultado == {"id": "1", "nombre": "admin"}
        assert cursor.execute.call_args.args[1] == ("admin",)

    def test_parametro_vacio_usa_el_nombre_de_la_instancia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": "1"}

        Usuarios(nombre="admin").obtener_rol_por_nombre("")

        assert cursor.execute.call_args.args[1] == ("admin",)

    def test_sin_nombre_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Usuarios().obtener_rol_por_nombre() is None
        cursor.execute.assert_not_called()

    def test_rol_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Usuarios().obtener_rol_por_nombre("inexistente") is None

    def test_conexion_caida(self, conexion_caída):
        assert Usuarios().obtener_rol_por_nombre("admin") is None

    def test_error_de_bd_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Usuarios().obtener_rol_por_nombre("admin") is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": "1"}

        Usuarios().obtener_rol_por_nombre("admin")

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": "1"}

        Usuarios().obtener_rol_por_nombre("admin")

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestValidarLogin:

    def test_credenciales_validas(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {
            "id": ID_USUARIO,
            "nombre": NOMBRE_MINIMO,
            "cedula": CEDULA_MAXIMA,
            "password": generate_password_hash(PASSWORD_MINIMA),
            "rol_id": ROL_VALIDO,
            "foto_perfil": None,
            "rol_nombre": "empleado",
        }
        cursor.fetchone.return_value = esperado

        resultado = Usuarios().validar_login(NOMBRE_MINIMO, PASSWORD_MINIMA)

        assert resultado == {
            "id": ID_USUARIO,
            "nombre": NOMBRE_MINIMO,
            "cedula": CEDULA_MAXIMA,
            "rol_id": ROL_VALIDO,
            "foto_perfil": None,
            "rol_nombre": "empleado",
        }
        assert "password" not in resultado
        assert "AND u.activo = 1" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (NOMBRE_MINIMO,)

    def test_password_incorrecta(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {
            "id": ID_USUARIO,
            "password": generate_password_hash(PASSWORD_MINIMA),
        }

        assert Usuarios().validar_login(NOMBRE_MINIMO, "Incorrecta") is None

    def test_usuario_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Usuarios().validar_login("nadie", PASSWORD_MINIMA) is None

    def test_conexion_caida(self, conexion_caída):
        assert Usuarios().validar_login(NOMBRE_MINIMO, PASSWORD_MINIMA) is None

    def test_error_de_bd_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Usuarios().validar_login(NOMBRE_MINIMO, PASSWORD_MINIMA) is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        Usuarios().validar_login(NOMBRE_MINIMO, PASSWORD_MINIMA)

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        Usuarios().validar_login(NOMBRE_MINIMO, PASSWORD_MINIMA)

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerUsuarioPorId:

    def test_usuario_encontrado_por_parametro(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {
            "id": ID_USUARIO,
            "nombre": NOMBRE_MINIMO,
            "cedula_personal": CEDULA_MAXIMA,
            "rol_nombre": "empleado",
        }
        cursor.fetchone.return_value = esperado

        resultado = Usuarios().obtener_usuario_por_id(ID_USUARIO)

        assert resultado == esperado
        assert "FROM usuario u" in ultima_sentencia(cursor)
        assert "INNER JOIN rol r" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_USUARIO,)

    def test_usa_el_id_de_la_instancia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": ID_USUARIO}

        resultado = Usuarios(id=ID_USUARIO).obtener_usuario_por_id()

        assert resultado == {"id": ID_USUARIO}
        assert cursor.execute.call_args.args[1] == (ID_USUARIO,)

    @pytest.mark.parametrize(
        "id_usuario",
        [
            pytest.param("", id="id-vacio"),
            pytest.param(None, id="id-none"),
        ],
    )
    def test_sin_id_devuelve_none(self, conexion_falsa, id_usuario):
        db, cursor = conexion_falsa

        assert Usuarios(id=id_usuario).obtener_usuario_por_id() is None
        cursor.execute.assert_not_called()

    def test_usuario_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Usuarios().obtener_usuario_por_id(ID_USUARIO) is None

    def test_conexion_caida(self, conexion_caída):
        assert Usuarios().obtener_usuario_por_id(ID_USUARIO) is None

    def test_error_de_bd_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Usuarios().obtener_usuario_por_id(ID_USUARIO) is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": ID_USUARIO}

        Usuarios().obtener_usuario_por_id(ID_USUARIO)

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": ID_USUARIO}

        Usuarios().obtener_usuario_por_id(ID_USUARIO)

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestActualizarPerfil:

    def test_datos_validos_sin_password(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Usuarios().actualizar_perfil(ID_USUARIO, NOMBRE_MINIMO)

        assert resultado == "Perfil actualizado exitosamente."
        sentencia, parametros = cursor.execute.call_args.args
        assert "UPDATE usuario" in sentencia
        assert "password" not in sentencia
        assert parametros == (NOMBRE_MINIMO, None, ID_USUARIO)
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_actualiza_foto_perfil(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Usuarios().actualizar_perfil(
            ID_USUARIO, NOMBRE_MINIMO, foto_perfil=FOTO_PERFIL
        )

        assert resultado == "Perfil actualizado exitosamente."
        assert cursor.execute.call_args.args[1] == (
            NOMBRE_MINIMO,
            FOTO_PERFIL,
            ID_USUARIO,
        )

    def test_actualiza_password_con_hash(self, conexion_falsa):
        db, cursor = conexion_falsa

        with hash_fijo():
            resultado = Usuarios().actualizar_perfil(
                ID_USUARIO, NOMBRE_MINIMO, password=PASSWORD_MINIMA
            )

        assert resultado == "Perfil actualizado exitosamente."
        sentencia, parametros = cursor.execute.call_args.args
        assert "password = %s" in sentencia
        assert parametros == (NOMBRE_MINIMO, "hash-falso", None, ID_USUARIO)

    def test_guarda_un_hash_real(self, conexion_falsa):
        db, cursor = conexion_falsa

        Usuarios().actualizar_perfil(
            ID_USUARIO, NOMBRE_MINIMO, password=PASSWORD_MINIMA
        )

        password_guardada = cursor.execute.call_args.args[1][1]
        assert password_guardada != PASSWORD_MINIMA
        assert check_password_hash(password_guardada, PASSWORD_MINIMA) is True

    def test_recorta_el_nombre(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Usuarios().actualizar_perfil(ID_USUARIO, "  Ana  ")

        assert resultado == "Perfil actualizado exitosamente."
        assert cursor.execute.call_args.args[1][0] == NOMBRE_MINIMO

    @pytest.mark.parametrize(
        "usuario_id",
        [
            pytest.param("", id="id-vacio"),
            pytest.param(None, id="id-none"),
        ],
    )
    def test_sin_id_devuelve_error(self, conexion_falsa, usuario_id):
        db, cursor = conexion_falsa

        resultado = Usuarios().actualizar_perfil(usuario_id, NOMBRE_MINIMO)

        assert resultado == "El ID del usuario es obligatorio."
        cursor.execute.assert_not_called()

    @pytest.mark.parametrize(
        "nombre, esperado",
        [
            pytest.param(
                "",
                "El campo Nombre no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                "   ",
                "El campo Nombre no puede estar vacío.",
                id="nombre-solo-espacios",
            ),
            pytest.param(
                "N" * 51,
                "El campo Nombre no puede tener más de 50 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                "Ana #1",
                "El campo Nombre solo puede contener letras, espacios, acentos y ñ.",
                id="nombre-caracteres-invalidos",
            ),
        ],
    )
    def test_nombre_invalido_no_toca_la_bd(self, conexion_falsa, nombre, esperado):
        db, cursor = conexion_falsa

        resultado = Usuarios().actualizar_perfil(ID_USUARIO, nombre)

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "password, esperado",
        [
            pytest.param(
                "12345",
                "El campo Contraseña debe tener al menos 6 caracteres.",
                id="password-demasiado-corta",
            ),
            pytest.param(
                "P" * 51,
                "El campo Contraseña no puede tener más de 50 caracteres.",
                id="password-demasiado-larga",
            ),
            pytest.param(
                "abc 123",
                "El campo Contraseña no puede contener espacios.",
                id="password-con-espacios",
            ),
        ],
    )
    def test_password_invalida_no_toca_la_bd(
        self, conexion_falsa, password, esperado
    ):
        db, cursor = conexion_falsa

        resultado = Usuarios().actualizar_perfil(
            ID_USUARIO, NOMBRE_MINIMO, password=password
        )

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_foto_demasiado_larga_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Usuarios().actualizar_perfil(
            ID_USUARIO, NOMBRE_MINIMO, foto_perfil="F" * 101
        )

        assert resultado == (
            "La ruta de la foto de perfil no puede exceder 100 caracteres."
        )
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Usuarios().actualizar_perfil(ID_USUARIO, NOMBRE_MINIMO)

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = Usuarios().actualizar_perfil(ID_USUARIO, NOMBRE_MINIMO)

        assert resultado == "Error al actualizar perfil."
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch("app.models.usuarios.Bitacora") as bitacora_clase:
            resultado = Usuarios(
                usuario_id="USR-000"
            ).actualizar_perfil(ID_USUARIO, NOMBRE_MINIMO)

        assert resultado == "Perfil actualizado exitosamente."
        bitacora_clase.assert_called_once_with(
            accion="Actualizar perfil",
            descripcion="Usuario actualizó su perfil",
            usuario_id="USR-000",
            modulo_nombre="Usuarios",
        )
        bitacora_clase.return_value.registrar.assert_called_once_with()

    def test_error_inesperado_devuelve_mensaje(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch.object(
            Usuarios, "_validar_perfil", side_effect=Exception("boom")
        ):
            resultado = Usuarios().actualizar_perfil(ID_USUARIO, NOMBRE_MINIMO)

        assert resultado == "Error en actualizar_perfil: boom"
