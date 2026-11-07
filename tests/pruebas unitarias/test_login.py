"""Pruebas unitarias de la clase LoginManager (app.models.login).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.

`LoginManager` delega la mayoria de las operaciones de usuarios en
`Usuarios`; en esas pruebas se reemplaza `_usuarios_model` por un
`MagicMock` para no tocar la base de datos.
"""
from unittest.mock import MagicMock, patch

from app.models.login import LoginManager
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

# ==================== Datos de frontera ====================
CEDULA_VALIDA = "12345678"
NOMBRE_USUARIO = "ana"
PASSWORD_VALIDA = "Clave123"

CEDULA_MINIMA = "123456"  # 6 dígitos (mínimo)
CEDULA_MAXIMA = "123456789"  # 9 dígitos (máximo)

NOMBRE_MINIMO = "Ana"
APELLIDO_MINIMO = "Paz"
CELULAR_VALIDO = "04141234567"
CORREO_VALIDO = "ana@mail.com"
DIRECCION_VALIDA = "Calle 1"

ROL_CLIENTE = {"id": "2", "nombre": "Cliente", "descripcion": "Cliente de la tienda"}
USUARIO_VALIDO = {
    "id": "USR-001",
    "nombre": NOMBRE_USUARIO,
    "cedula": CEDULA_VALIDA,
    "rol_id": "2",
    "rol_nombre": "Cliente",
}


def llamada_con(cursor, fragmento):
    """Devuelve la llamada a execute cuya sentencia contiene el fragmento."""
    return next(
        llamada
        for llamada in cursor.execute.call_args_list
        if fragmento in llamada.args[0]
    )


class TestValidarUsuario:

    def test_credenciales_validas(self, conexion_falsa):
        gestor = LoginManager()
        gestor._usuarios_model = MagicMock()
        gestor._usuarios_model.validar_login.return_value = USUARIO_VALIDO

        resultado = gestor.validar_usuario(NOMBRE_USUARIO, PASSWORD_VALIDA)

        assert resultado == USUARIO_VALIDO
        gestor._usuarios_model.validar_login.assert_called_once_with(
            NOMBRE_USUARIO, PASSWORD_VALIDA
        )

    def test_credenciales_invalidas(self, conexion_falsa):
        gestor = LoginManager()
        gestor._usuarios_model = MagicMock()
        gestor._usuarios_model.validar_login.return_value = None

        assert gestor.validar_usuario(NOMBRE_USUARIO, "incorrecta") is None

    def test_error_del_modelo_devuelve_none(self, conexion_falsa):
        gestor = LoginManager()
        gestor._usuarios_model = MagicMock()
        gestor._usuarios_model.validar_login.side_effect = Exception("fallo")

        assert gestor.validar_usuario(NOMBRE_USUARIO, PASSWORD_VALIDA) is None


class TestObtenerRolCliente:

    def test_rol_encontrado(self, conexion_falsa):
        gestor = LoginManager()
        gestor._usuarios_model = MagicMock()
        gestor._usuarios_model.obtener_rol_por_nombre.return_value = ROL_CLIENTE

        resultado = gestor.obtener_rol_cliente()

        assert resultado == ROL_CLIENTE
        gestor._usuarios_model.obtener_rol_por_nombre.assert_called_once_with(
            "Cliente"
        )

    def test_rol_no_encontrado(self, conexion_falsa):
        gestor = LoginManager()
        gestor._usuarios_model = MagicMock()
        gestor._usuarios_model.obtener_rol_por_nombre.return_value = None

        assert gestor.obtener_rol_cliente() is None

    def test_error_del_modelo_devuelve_none(self, conexion_falsa):
        gestor = LoginManager()
        gestor._usuarios_model = MagicMock()
        gestor._usuarios_model.obtener_rol_por_nombre.side_effect = Exception(
            "fallo"
        )

        assert gestor.obtener_rol_cliente() is None


class TestVerificarUsuarioExistePorCedula:

    def test_usuario_existe(self, conexion_falsa):
        gestor = LoginManager()
        gestor._usuarios_model = MagicMock()
        gestor._usuarios_model.verificar_cedula_en_uso.return_value = True

        resultado = gestor.verificar_usuario_existe_por_cedula(12345678)

        assert resultado is True
        # La cedula se convierte a texto antes de delegar
        gestor._usuarios_model.verificar_cedula_en_uso.assert_called_once_with(
            CEDULA_VALIDA
        )

    def test_usuario_no_existe(self, conexion_falsa):
        gestor = LoginManager()
        gestor._usuarios_model = MagicMock()
        gestor._usuarios_model.verificar_cedula_en_uso.return_value = False

        assert gestor.verificar_usuario_existe_por_cedula(CEDULA_VALIDA) is False

    def test_error_del_modelo_devuelve_false(self, conexion_falsa):
        gestor = LoginManager()
        gestor._usuarios_model = MagicMock()
        gestor._usuarios_model.verificar_cedula_en_uso.side_effect = Exception(
            "fallo"
        )

        assert gestor.verificar_usuario_existe_por_cedula(CEDULA_VALIDA) is False


class TestVerificarUsuarioExistePorNombre:

    def test_usuario_existe(self, conexion_falsa):
        gestor = LoginManager()

        with patch("app.models.login.Usuarios") as usuarios_cls:
            usuarios_cls.return_value.verificar_usuario_por_nombre.return_value = (
                True
            )

            resultado = gestor.verificar_usuario_existe_por_nombre(NOMBRE_USUARIO)

        assert resultado is True
        usuarios_cls.assert_called_once_with(nombre=NOMBRE_USUARIO)

    def test_usuario_no_existe(self, conexion_falsa):
        gestor = LoginManager()

        with patch("app.models.login.Usuarios") as usuarios_cls:
            usuarios_cls.return_value.verificar_usuario_por_nombre.return_value = (
                False
            )

            resultado = gestor.verificar_usuario_existe_por_nombre(NOMBRE_USUARIO)

        assert resultado is False

    def test_error_del_modelo_devuelve_false(self, conexion_falsa):
        gestor = LoginManager()

        with patch("app.models.login.Usuarios") as usuarios_cls:
            usuarios_cls.return_value.verificar_usuario_por_nombre.side_effect = (
                Exception("fallo")
            )

            resultado = gestor.verificar_usuario_existe_por_nombre(NOMBRE_USUARIO)

        assert resultado is False


class TestCrearUsuario:

    def test_creacion_exitosa(self, conexion_falsa):
        gestor = LoginManager()

        with patch("app.models.login.Usuarios") as usuarios_cls:
            usuario = usuarios_cls.return_value
            usuario.verificar_usuario_por_nombre.return_value = False
            usuario.verificar_cedula_en_uso.return_value = False
            usuario.agregar_usuario.return_value = "Usuario agregado exitosamente."
            usuario.id = "USR-001"

            resultado = gestor.crear_usuario(
                NOMBRE_USUARIO,
                CEDULA_VALIDA,
                PASSWORD_VALIDA,
                2,
                "perfil.png",
            )

        assert resultado == "USR-001"
        usuarios_cls.assert_called_once_with(
            nombre=NOMBRE_USUARIO,
            cedula=CEDULA_VALIDA,
            password=PASSWORD_VALIDA,
            rol_id="2",
            foto_perfil="perfil.png",
        )
        usuario.verificar_cedula_en_uso.assert_called_once_with(CEDULA_VALIDA)
        usuario.agregar_usuario.assert_called_once_with()

    def test_sin_foto_perfil_por_defecto(self, conexion_falsa):
        gestor = LoginManager()

        with patch("app.models.login.Usuarios") as usuarios_cls:
            usuario = usuarios_cls.return_value
            usuario.verificar_usuario_por_nombre.return_value = False
            usuario.verificar_cedula_en_uso.return_value = False
            usuario.agregar_usuario.return_value = "Usuario agregado exitosamente."
            usuario.id = "USR-002"

            resultado = gestor.crear_usuario(
                NOMBRE_USUARIO, CEDULA_VALIDA, PASSWORD_VALIDA, 2
            )

        assert resultado == "USR-002"
        usuarios_cls.assert_called_once_with(
            nombre=NOMBRE_USUARIO,
            cedula=CEDULA_VALIDA,
            password=PASSWORD_VALIDA,
            rol_id="2",
            foto_perfil=None,
        )

    def test_nombre_duplicado(self, conexion_falsa):
        gestor = LoginManager()

        with patch("app.models.login.Usuarios") as usuarios_cls:
            usuario = usuarios_cls.return_value
            usuario.verificar_usuario_por_nombre.return_value = True

            resultado = gestor.crear_usuario(
                NOMBRE_USUARIO, CEDULA_VALIDA, PASSWORD_VALIDA, 2
            )

        assert resultado is None
        usuario.verificar_cedula_en_uso.assert_not_called()
        usuario.agregar_usuario.assert_not_called()

    def test_cedula_duplicada(self, conexion_falsa):
        gestor = LoginManager()

        with patch("app.models.login.Usuarios") as usuarios_cls:
            usuario = usuarios_cls.return_value
            usuario.verificar_usuario_por_nombre.return_value = False
            usuario.verificar_cedula_en_uso.return_value = True

            resultado = gestor.crear_usuario(
                NOMBRE_USUARIO, CEDULA_VALIDA, PASSWORD_VALIDA, 2
            )

        assert resultado is None
        usuario.agregar_usuario.assert_not_called()

    def test_error_al_agregar_usuario(self, conexion_falsa):
        gestor = LoginManager()

        with patch("app.models.login.Usuarios") as usuarios_cls:
            usuario = usuarios_cls.return_value
            usuario.verificar_usuario_por_nombre.return_value = False
            usuario.verificar_cedula_en_uso.return_value = False
            usuario.agregar_usuario.return_value = "Error al agregar usuario: x"

            resultado = gestor.crear_usuario(
                NOMBRE_USUARIO, CEDULA_VALIDA, PASSWORD_VALIDA, 2
            )

        assert resultado is None

    def test_error_inesperado_devuelve_none(self, conexion_falsa):
        gestor = LoginManager()

        with patch("app.models.login.Usuarios") as usuarios_cls:
            usuario = usuarios_cls.return_value
            usuario.verificar_usuario_por_nombre.side_effect = Exception("fallo")

            resultado = gestor.crear_usuario(
                NOMBRE_USUARIO, CEDULA_VALIDA, PASSWORD_VALIDA, 2
            )

        assert resultado is None


class TestCrearClienteNatural:

    def test_cliente_y_persona_nuevos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, None]

        resultado = LoginManager().crear_cliente_natural(
            CEDULA_VALIDA,
            NOMBRE_MINIMO,
            APELLIDO_MINIMO,
            CELULAR_VALIDO,
            CORREO_VALIDO,
            DIRECCION_VALIDA,
        )

        assert resultado is True
        assert llamada_con(cursor, "INSERT INTO Cliente").args[1] == (
            CEDULA_VALIDA,
            DIRECCION_VALIDA,
            CELULAR_VALIDO,
            CORREO_VALIDO,
        )
        assert llamada_con(cursor, "INSERT INTO Persona_natural").args[1] == (
            CEDULA_VALIDA,
            NOMBRE_MINIMO,
            APELLIDO_MINIMO,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_cliente_y_persona_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,)]

        resultado = LoginManager().crear_cliente_natural(
            CEDULA_VALIDA,
            NOMBRE_MINIMO,
            APELLIDO_MINIMO,
            CELULAR_VALIDO,
            CORREO_VALIDO,
            DIRECCION_VALIDA,
        )

        assert resultado is True
        assert llamada_con(cursor, "UPDATE Cliente").args[1] == (
            DIRECCION_VALIDA,
            CELULAR_VALIDO,
            CORREO_VALIDO,
            CEDULA_VALIDA,
        )
        assert llamada_con(cursor, "UPDATE Persona_natural").args[1] == (
            NOMBRE_MINIMO,
            APELLIDO_MINIMO,
            CEDULA_VALIDA,
        )
        sin_sentencia(cursor, "INSERT")
        db.commit.assert_called_once()

    def test_cliente_existente_persona_nueva(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), None]

        resultado = LoginManager().crear_cliente_natural(
            CEDULA_VALIDA,
            NOMBRE_MINIMO,
            APELLIDO_MINIMO,
            CELULAR_VALIDO,
            CORREO_VALIDO,
            DIRECCION_VALIDA,
        )

        assert resultado is True
        llamada_con(cursor, "UPDATE Cliente")
        llamada_con(cursor, "INSERT INTO Persona_natural")
        db.commit.assert_called_once()

    def test_cliente_nuevo_persona_existente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, (1,)]

        resultado = LoginManager().crear_cliente_natural(
            CEDULA_VALIDA,
            NOMBRE_MINIMO,
            APELLIDO_MINIMO,
            CELULAR_VALIDO,
            CORREO_VALIDO,
            DIRECCION_VALIDA,
        )

        assert resultado is True
        llamada_con(cursor, "INSERT INTO Cliente")
        llamada_con(cursor, "UPDATE Persona_natural")
        db.commit.assert_called_once()

    def test_correo_y_direccion_opcionales(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, None]

        LoginManager().crear_cliente_natural(
            CEDULA_VALIDA,
            NOMBRE_MINIMO,
            APELLIDO_MINIMO,
            CELULAR_VALIDO,
        )

        assert llamada_con(cursor, "INSERT INTO Cliente").args[1] == (
            CEDULA_VALIDA,
            None,
            CELULAR_VALIDO,
            None,
        )

    def test_conexion_caida(self, conexion_caída):
        resultado = LoginManager().crear_cliente_natural(
            CEDULA_VALIDA,
            NOMBRE_MINIMO,
            APELLIDO_MINIMO,
            CELULAR_VALIDO,
        )

        assert resultado is False

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = LoginManager().crear_cliente_natural(
            CEDULA_VALIDA,
            NOMBRE_MINIMO,
            APELLIDO_MINIMO,
            CELULAR_VALIDO,
        )

        assert resultado is False
        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)


class TestVerificarPerfilCompletoCliente:

    def test_perfil_completo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        resultado = LoginManager().verificar_perfil_completo_cliente(CEDULA_VALIDA)

        assert resultado is True
        assert "FROM Persona_natural" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (CEDULA_VALIDA,)

    def test_perfil_incompleto(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert (
            LoginManager().verificar_perfil_completo_cliente(CEDULA_VALIDA)
            is False
        )

    def test_conexion_caida(self, conexion_caída):
        assert (
            LoginManager().verificar_perfil_completo_cliente(CEDULA_VALIDA)
            is False
        )

    def test_error_de_bd_devuelve_false(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert (
            LoginManager().verificar_perfil_completo_cliente(CEDULA_VALIDA)
            is False
        )
        cierra_recursos(db, cursor)

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        LoginManager().verificar_perfil_completo_cliente(CEDULA_VALIDA)

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        LoginManager().verificar_perfil_completo_cliente(CEDULA_VALIDA)

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerClienteParaSesion:

    def test_cliente_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {
            "cedula": CEDULA_VALIDA,
            "nombre": NOMBRE_MINIMO,
            "apellido": APELLIDO_MINIMO,
            "celular": CELULAR_VALIDO,
            "correo": CORREO_VALIDO,
            "direccion": DIRECCION_VALIDA,
        }
        cursor.fetchone.return_value = esperado

        resultado = LoginManager().obtener_cliente_para_sesion(CEDULA_VALIDA)

        assert resultado == esperado
        assert "JOIN Persona_natural" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (CEDULA_VALIDA,)
        db.cursor.assert_called_once_with(dictionary=True)

    def test_cliente_no_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert (
            LoginManager().obtener_cliente_para_sesion(CEDULA_VALIDA) is None
        )

    def test_conexion_caida(self, conexion_caída):
        assert LoginManager().obtener_cliente_para_sesion(CEDULA_VALIDA) is None

    def test_error_de_bd_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert LoginManager().obtener_cliente_para_sesion(CEDULA_VALIDA) is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        LoginManager().obtener_cliente_para_sesion(CEDULA_VALIDA)

        cierra_recursos(db, cursor)


class TestObtenerEmpleadoParaSesion:

    def test_empleado_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {
            "cedula": CEDULA_VALIDA,
            "nombre": NOMBRE_MINIMO,
            "apellido": APELLIDO_MINIMO,
            "celular": CELULAR_VALIDO,
            "correo": CORREO_VALIDO,
            "direccion": DIRECCION_VALIDA,
            "cargo": "1",
        }
        cursor.fetchone.return_value = esperado

        resultado = LoginManager().obtener_empleado_para_sesion(CEDULA_VALIDA)

        assert resultado == esperado
        assert "FROM Empleado" in ultima_sentencia(cursor)
        assert "ID_cargo AS cargo" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (CEDULA_VALIDA,)
        db.cursor.assert_called_once_with(dictionary=True)

    def test_empleado_no_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert (
            LoginManager().obtener_empleado_para_sesion(CEDULA_VALIDA) is None
        )

    def test_conexion_caida(self, conexion_caída):
        assert LoginManager().obtener_empleado_para_sesion(CEDULA_VALIDA) is None

    def test_error_de_bd_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert LoginManager().obtener_empleado_para_sesion(CEDULA_VALIDA) is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        LoginManager().obtener_empleado_para_sesion(CEDULA_VALIDA)

        cierra_recursos(db, cursor)


class TestObtenerRolPorId:

    def test_rol_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ROL_CLIENTE

        resultado = LoginManager().obtener_rol_por_id(2)

        assert resultado == ROL_CLIENTE
        assert "FROM rol" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (2,)
        db.cursor.assert_called_once_with(dictionary=True)

    def test_rol_no_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert LoginManager().obtener_rol_por_id(99) is None

    def test_conexion_caida(self, conexion_caída):
        assert LoginManager().obtener_rol_por_id(2) is None

    def test_error_de_bd_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert LoginManager().obtener_rol_por_id(2) is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        LoginManager().obtener_rol_por_id(2)

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ROL_CLIENTE

        LoginManager().obtener_rol_por_id(2)

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerUsuarioPorId:

    def test_usuario_encontrado(self, conexion_falsa):
        gestor = LoginManager()
        gestor._usuarios_model = MagicMock()
        gestor._usuarios_model.obtener_usuario_por_id.return_value = USUARIO_VALIDO

        resultado = gestor.obtener_usuario_por_id("USR-001")

        assert resultado == USUARIO_VALIDO
        gestor._usuarios_model.obtener_usuario_por_id.assert_called_once_with(
            "USR-001"
        )

    def test_usuario_no_encontrado(self, conexion_falsa):
        gestor = LoginManager()
        gestor._usuarios_model = MagicMock()
        gestor._usuarios_model.obtener_usuario_por_id.return_value = None

        assert gestor.obtener_usuario_por_id("USR-999") is None

    def test_error_del_modelo_devuelve_none(self, conexion_falsa):
        gestor = LoginManager()
        gestor._usuarios_model = MagicMock()
        gestor._usuarios_model.obtener_usuario_por_id.side_effect = Exception(
            "fallo"
        )

        assert gestor.obtener_usuario_por_id("USR-001") is None
