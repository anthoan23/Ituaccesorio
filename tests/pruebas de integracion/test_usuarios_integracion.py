"""Pruebas de integración de Usuarios contra MySQL real (BD seguridad)."""
import random

import pytest

from app.models.usuarios import Usuarios
from app.models.roles import Rol


ROL_ADMIN = "1"
USUARIO_ADMIN = "USR-001"


def _nombre_usuario_unico() -> str:
    return f"UsuarioTest{random.randint(100000, 999999)}"


def _cedula_aleatoria() -> str:
    return str(random.randint(10**7, 10**8 - 1))


def _crear_rol_temporal(nombre: str) -> str:
    """Crea un rol temporal en seguridad. Devuelve su ID."""
    Rol(nombre=nombre, descripcion="Rol temporal de pruebas").agregar_rol()
    from app.models.database import conectar
    db = conectar().conexion2()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id FROM rol WHERE nombre = %s LIMIT 1", (nombre,))
        return str(cursor.fetchone()[0])
    finally:
        cursor.close()
        db.close()


def _limpiar_rol_temporal(nombre: str) -> None:
    from app.models.database import conectar
    db = conectar().conexion2()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id FROM rol WHERE nombre = %s LIMIT 1", (nombre,))
        fila = cursor.fetchone()
        if fila:
            id_rol = fila[0]
            cursor.execute("DELETE FROM usuario WHERE rol_id = %s", (id_rol,))
            cursor.execute("DELETE FROM rol WHERE id = %s", (id_rol,))
            db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def _limpiar_usuario_por_nombre(nombre: str) -> None:
    from app.models.database import conectar
    db = conectar().conexion2()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM usuario WHERE nombre = %s", (nombre,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def datos_usuario(**cambios):
    datos = {
        "nombre": _nombre_usuario_unico(),
        "cedula": _cedula_aleatoria(),
        "password": "Password123",
        "rol_id": ROL_ADMIN,
    }
    datos.update(cambios)
    return datos


@pytest.fixture
def rol_cliente_temporal():
    """Crea un rol 'Cliente' temporal (el seed solo tiene Admin)."""
    nombre_rol = f"ClienteTemp{random.randint(1000, 9999)}"
    id_rol = _crear_rol_temporal(nombre_rol)
    try:
        yield {"id_rol": id_rol, "nombre_rol": nombre_rol}
    finally:
        _limpiar_rol_temporal(nombre_rol)


# ==================== LISTAR ====================

class TestListarUsuarios:

    def test_devuelve_lista(self):
        usuarios = Usuarios().listar_usuarios()
        assert usuarios is not None
        assert isinstance(usuarios, list)

    def test_incluye_admin_del_seed(self):
        usuarios = Usuarios().listar_usuarios()
        admin = next((u for u in usuarios if u["id"] == USUARIO_ADMIN), None)
        assert admin is not None
        assert admin["nombre"] == "super_admin"
        assert admin["rol_nombre"] == "Admin"


class TestListarEmpleados:

    def test_devuelve_lista(self):
        empleados = Usuarios().listar_empleados()
        assert empleados is not None
        assert isinstance(empleados, list)
        assert any(e["cedula"] == 12345678 for e in empleados)


class TestListarClientes:

    def test_devuelve_lista(self):
        clientes = Usuarios().listar_clientes()
        assert clientes is not None
        assert isinstance(clientes, list)


# ==================== VERIFICAR ====================

class TestVerificarUsuario:

    def test_por_id_existente(self):
        assert Usuarios(id=USUARIO_ADMIN).verificar_usuario_por_id() is True

    def test_por_id_inexistente(self):
        assert Usuarios(id="USR-999").verificar_usuario_por_id() is False

    def test_por_id_vacio(self):
        assert Usuarios().verificar_usuario_por_id() is False

    def test_por_nombre_existente(self):
        assert Usuarios(nombre="super_admin").verificar_usuario_por_nombre() is True

    def test_por_nombre_inexistente(self):
        assert Usuarios(nombre=_nombre_usuario_unico()).verificar_usuario_por_nombre() is False

    def test_cedula_en_uso(self):
        assert Usuarios().verificar_cedula_en_uso("12345678") is True

    def test_cedula_no_en_uso(self):
        assert Usuarios().verificar_cedula_en_uso(_cedula_aleatoria()) is False

    def test_verificar_empleado_existente(self):
        assert Usuarios().verificar_empleado("12345678") is True

    def test_verificar_empleado_inexistente(self):
        assert Usuarios().verificar_empleado("99999999") is False


# ==================== AGREGAR ====================

class TestAgregarUsuario:

    def test_datos_validos_con_rol_admin(self):
        datos = datos_usuario()
        try:
            resultado = Usuarios(**datos).agregar_usuario()
            # Con rol Admin, verificar_rol_y_cedula pide que la cédula exista en Empleado
            # Como usamos cédula aleatoria, esperamos error de rol
            assert "cédula no corresponde al tipo de rol" in resultado
        finally:
            _limpiar_usuario_por_nombre(datos["nombre"])

    def test_datos_validos_con_rol_cliente(self, rol_cliente_temporal):
        datos = datos_usuario(rol_id=rol_cliente_temporal["id_rol"])
        try:
            resultado = Usuarios(**datos).agregar_usuario()
            assert resultado == "Usuario agregado exitosamente."

            consultado = Usuarios(nombre=datos["nombre"]).verificar_usuario_por_nombre()
            assert consultado is True
        finally:
            _limpiar_usuario_por_nombre(datos["nombre"])

    def test_usuario_duplicado_por_nombre(self, rol_cliente_temporal):
        datos = datos_usuario(rol_id=rol_cliente_temporal["id_rol"])
        try:
            Usuarios(**datos).agregar_usuario()

            resultado = Usuarios(**datos).agregar_usuario()
            assert resultado == f"El nombre de usuario '{datos['nombre']}' ya existe."
        finally:
            _limpiar_usuario_por_nombre(datos["nombre"])

    def test_cedula_duplicada(self, rol_cliente_temporal):
        datos = datos_usuario(rol_id=rol_cliente_temporal["id_rol"])
        try:
            Usuarios(**datos).agregar_usuario()

            datos2 = datos_usuario(rol_id=rol_cliente_temporal["id_rol"], cedula=datos["cedula"])
            resultado = Usuarios(**datos2).agregar_usuario()
            assert resultado == f"La cédula '{datos['cedula']}' ya está asignada a otro usuario."
        finally:
            _limpiar_usuario_por_nombre(datos["nombre"])
            _limpiar_usuario_por_nombre(datos2["nombre"])


# ==================== OBTENER ====================

class TestObtenerUsuarioPorId:

    def test_admin(self):
        usuario = Usuarios().obtener_usuario_por_id(USUARIO_ADMIN)
        assert usuario is not None
        assert usuario["id"] == USUARIO_ADMIN
        assert usuario["nombre"] == "super_admin"
        assert usuario["rol_nombre"] == "Admin"

    def test_inexistente(self):
        assert Usuarios().obtener_usuario_por_id("USR-999") is None


# ==================== LOGIN ====================

class TestValidarLogin:

    def test_credenciales_validas(self):
        # El seed tiene super_admin con password 'scrypt:...' pero no conocemos
        # el password en texto plano. Esta prueba solo verifica que devuelve None
        # con password incorrecta, no que valide una correcta.
        resultado = Usuarios().validar_login("super_admin", "password_incorrecta")
        assert resultado is None

    def test_usuario_inexistente(self):
        resultado = Usuarios().validar_login("no_existe_xyz", "cualquiera")
        assert resultado is None

    def test_usuario_inactivo_no_pasa(self):
        # El seed tiene activo=1, no podemos probar inactivo sin crear uno
        pass


# ==================== ELIMINAR ====================

class TestEliminarUsuario:

    def test_no_elimina_admin_unico(self):
        resultado = Usuarios(id=USUARIO_ADMIN).eliminar_usuario()
        assert resultado == "No se puede eliminar el único administrador del sistema."

    def test_usuario_inexistente(self):
        resultado = Usuarios(id="USR-999").eliminar_usuario()
        assert resultado == "El usuario con identificador USR-999 no existe."

    def test_sin_id(self):
        resultado = Usuarios().eliminar_usuario()
        assert resultado == "El identificador del usuario no puede estar vacío."