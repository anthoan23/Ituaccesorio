"""Pruebas de integración de LoginManager contra MySQL real."""
import random

import pytest

from app.models.login import LoginManager
from app.models.roles import Rol


ROL_ADMIN = "1"
USUARIO_ADMIN = "USR-001"


def _cedula_aleatoria() -> str:
    return str(random.randint(10**7, 10**8 - 1))


def _limpiar_cliente(cedula: str) -> None:
    from app.models.database import conectar
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Persona_natural WHERE ID_cliente = %s", (cedula,))
        cursor.execute("DELETE FROM Cliente WHERE ID_cliente = %s", (cedula,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def _crear_rol_cliente_temporal() -> str:
    nombre_rol = f"ClienteLogin{random.randint(1000, 9999)}"
    Rol(nombre=nombre_rol, descripcion="Rol temporal login").agregar_rol()
    from app.models.database import conectar
    db = conectar().conexion2()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id FROM rol WHERE nombre = %s LIMIT 1", (nombre_rol,))
        return str(cursor.fetchone()[0])
    finally:
        cursor.close()
        db.close()


def _limpiar_rol_temporal(nombre_rol: str) -> None:
    from app.models.database import conectar
    db = conectar().conexion2()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id FROM rol WHERE nombre = %s LIMIT 1", (nombre_rol,))
        fila = cursor.fetchone()
        if fila:
            cursor.execute("DELETE FROM usuario WHERE rol_id = %s", (fila[0],))
            cursor.execute("DELETE FROM rol WHERE id = %s", (fila[0],))
            db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


# ==================== VALIDAR USUARIO ====================

class TestValidarUsuario:

    def test_credenciales_invalidas(self):
        resultado = LoginManager().validar_usuario("super_admin", "mala")
        assert resultado is None

    def test_usuario_inexistente(self):
        resultado = LoginManager().validar_usuario("no_existe_xyz", "x")
        assert resultado is None


# ==================== OBTENER ROL CLIENTE ====================

class TestObtenerRolCliente:

    def test_sin_rol_cliente_en_seed(self):
        # El seed solo tiene Admin; Cliente no existe.
        resultado = LoginManager().obtener_rol_cliente()
        assert resultado is None

    def test_con_rol_cliente_creado(self):
        nombre_rol = f"Cliente{random.randint(1000, 9999)}"
        id_rol = _crear_rol_cliente_temporal()  # crea con nombre aleatorio
        # Este test crea un rol con nombre aleatorio, no "Cliente", así que
        # LoginManager.obtener_rol_cliente sigue devolviendo None.
        # Para probar el happy path, creamos uno "Cliente" exacto:
        try:
            Rol(nombre="Cliente", descripcion="Rol cliente login").agregar_rol()
            resultado = LoginManager().obtener_rol_cliente()
            assert resultado is not None
            assert resultado["nombre"] == "Cliente"
        finally:
            _limpiar_rol_temporal("Cliente")
            _limpiar_rol_temporal(nombre_rol)


# ==================== VERIFICAR EXISTENCIA ====================

class TestVerificarExistencia:

    def test_cedula_en_uso(self):
        assert LoginManager().verificar_usuario_existe_por_cedula("12345678") is True

    def test_cedula_no_en_uso(self):
        assert LoginManager().verificar_usuario_existe_por_cedula(_cedula_aleatoria()) is False

    def test_nombre_existente(self):
        assert LoginManager().verificar_usuario_existe_por_nombre("super_admin") is True

    def test_nombre_inexistente(self):
        assert LoginManager().verificar_usuario_existe_por_nombre("xyz_no_existe") is False


# ==================== CREAR CLIENTE NATURAL ====================

class TestCrearClienteNatural:

    def test_crea_cliente_nuevo(self):
        cedula = _cedula_aleatoria()
        try:
            resultado = LoginManager().crear_cliente_natural(
                cedula=cedula,
                nombre="Cliente",
                apellido="Nuevo",
                celular="0414123456",
                correo=f"{cedula}@mail.com",
                direccion="Barquisimeto",
            )
            assert resultado is True

            datos = LoginManager().obtener_cliente_para_sesion(cedula)
            assert datos is not None
            assert datos["nombre"] == "Cliente"
            assert datos["apellido"] == "Nuevo"
        finally:
            _limpiar_cliente(cedula)

    def test_actualiza_cliente_existente(self):
        cedula = _cedula_aleatoria()
        try:
            LoginManager().crear_cliente_natural(
                cedula=cedula, nombre="Original", apellido="Apellido",
                celular="0414123456",
            )
            resultado = LoginManager().crear_cliente_natural(
                cedula=cedula, nombre="Actualizado", apellido="Apellido",
                celular="0414999999",
            )
            assert resultado is True

            datos = LoginManager().obtener_cliente_para_sesion(cedula)
            assert datos["nombre"] == "Actualizado"
            assert datos["celular"] == "0414999999"
        finally:
            _limpiar_cliente(cedula)


# ==================== VERIFICAR PERFIL ====================

class TestVerificarPerfilCompleto:

    def test_cliente_con_perfil(self):
        cedula = _cedula_aleatoria()
        try:
            LoginManager().crear_cliente_natural(
                cedula=cedula, nombre="Cliente", apellido="Perfil",
                celular="0414123456",
            )
            assert LoginManager().verificar_perfil_completo_cliente(cedula) is True
        finally:
            _limpiar_cliente(cedula)

    def test_cliente_sin_perfil(self):
        assert LoginManager().verificar_perfil_completo_cliente(
            _cedula_aleatoria()
        ) is False


# ==================== OBTENER PARA SESIÓN ====================

class TestObtenerParaSesion:

    def test_cliente_existente(self):
        cedula = _cedula_aleatoria()
        try:
            LoginManager().crear_cliente_natural(
                cedula=cedula, nombre="Cliente", apellido="Sesion",
                celular="0414123456",
            )
            datos = LoginManager().obtener_cliente_para_sesion(cedula)
            assert datos is not None
            assert datos["cedula"] == cedula
        finally:
            _limpiar_cliente(cedula)

    def test_cliente_inexistente(self):
        assert LoginManager().obtener_cliente_para_sesion(
            _cedula_aleatoria()
        ) is None

    def test_empleado_existente(self):
        datos = LoginManager().obtener_empleado_para_sesion("12345678")
        assert datos is not None
        assert datos["cedula"] == 12345678
        assert datos["nombre"] == "Super"

    def test_empleado_inexistente(self):
        assert LoginManager().obtener_empleado_para_sesion("99999999") is None


# ==================== ROLES / USUARIOS ====================

class TestObtenerRolUsuario:

    def test_rol_por_id_existente(self):
        resultado = LoginManager().obtener_rol_por_id(1)
        assert resultado is not None
        assert resultado["nombre"] == "Admin"

    def test_rol_por_id_inexistente(self):
        assert LoginManager().obtener_rol_por_id(999999) is None

    def test_usuario_por_id_existente(self):
        resultado = LoginManager().obtener_usuario_por_id(USUARIO_ADMIN)
        assert resultado is not None
        assert resultado["nombre"] == "super_admin"

    def test_usuario_por_id_inexistente(self):
        assert LoginManager().obtener_usuario_por_id("USR-999") is None


# ==================== CREAR USUARIO ====================

class TestCrearUsuario:

    def test_con_rol_cliente(self):
        nombre_rol = f"ClienteCrear{random.randint(1000, 9999)}"
        id_rol = _crear_rol_cliente_temporal()
        nombre_usuario = f"user{random.randint(100000, 999999)}"
        cedula = _cedula_aleatoria()
        try:
            resultado = LoginManager().crear_usuario(
                nombre=nombre_usuario,
                cedula=cedula,
                password="Password123",
                rol_id=int(id_rol),
            )
            # Si falla por cédula no en Empleado (rol no es Cliente), devuelve None
            # El rol es aleatorio, así que verificar_rol_y_cedula devuelve False
            assert resultado is None
        finally:
            from app.models.database import conectar
            db = conectar().conexion2()
            cursor = db.cursor()
            cursor.execute("DELETE FROM usuario WHERE nombre = %s", (nombre_usuario,))
            db.commit()
            cursor.close()
            db.close()
            _limpiar_rol_temporal(nombre_rol)

    def test_nombre_duplicado(self):
        resultado = LoginManager().crear_usuario(
            nombre="super_admin",
            cedula=_cedula_aleatoria(),
            password="Password123",
            rol_id=int(ROL_ADMIN),
        )
        assert resultado is None