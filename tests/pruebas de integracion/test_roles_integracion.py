"""Pruebas de integración de la clase Permiso contra MySQL real (BD seguridad)."""
import pytest

from app.models.permisos import Permiso
from app.models.database import conectar


ROL_ADMIN = "1"
MODULO_ID_VALIDO = "1"   # Empleados
MODULO_ID_INEXISTENTE = "999999"
MODULO_NOMBRE_EXISTENTE = "Empleados"


def _restaurar_permiso_admin(modulo_id: str, consultar=1, registrar=1, modificar=1, eliminar=1):
    """Restaura el permiso de Admin para un módulo (por si el test lo modifica)."""
    db = conectar().conexion2()
    if not db:
        return
    cursor = db.cursor()
    try:
        cursor.execute(
            "UPDATE permiso SET consultar=%s, registrar=%s, modificar=%s, eliminar=%s "
            "WHERE rol_id=%s AND modulo_id=%s",
            (consultar, registrar, modificar, eliminar, ROL_ADMIN, modulo_id),
        )
        db.commit()
    finally:
        cursor.close()
        db.close()


def _eliminar_permiso(rol_id: str, modulo_id: str):
    db = conectar().conexion2()
    if not db:
        return
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM permiso WHERE rol_id=%s AND modulo_id=%s",
            (rol_id, modulo_id),
        )
        db.commit()
    finally:
        cursor.close()
        db.close()


# ==================== LISTAR POR ROL ====================

class TestListarPermisosPorRol:

    def test_admin_tiene_todos_los_permisos_del_seed(self):
        permisos = Permiso().listar_permisos_por_rol(rol_id=ROL_ADMIN)

        assert permisos is not None
        assert len(permisos) == 16
        assert all(p["consultar"] == 1 for p in permisos)
        assert all(p["registrar"] == 1 for p in permisos)
        assert all(p["modificar"] == 1 for p in permisos)
        assert all(p["eliminar"] == 1 for p in permisos)

    def test_rol_inexistente_devuelve_lista_vacia(self):
        permisos = Permiso().listar_permisos_por_rol(rol_id="999999")
        assert permisos == []

    def test_sin_rol(self):
        assert Permiso().listar_permisos_por_rol() is None

    def test_ordenados_por_nombre_modulo(self):
        permisos = Permiso().listar_permisos_por_rol(rol_id=ROL_ADMIN)
        nombres = [p["modulo_nombre"] for p in permisos]
        assert nombres == sorted(nombres)


class TestListarPermisosCompletosPorRol:

    def test_admin_ve_los_16_modulos(self):
        permisos = Permiso().listar_permisos_completos_por_rol(rol_id=ROL_ADMIN)

        assert permisos is not None
        assert len(permisos) == 16
        assert all(p["consultar"] == 1 for p in permisos)

    def test_rol_sin_permisos_ve_modulos_con_false(self):
        # Creamos un rol temporal sin permisos y verificamos que ve los 16 módulos con false
        from app.models.roles import Rol
        Rol(nombre="RolPermTest", descripcion="Temp").agregar_rol()
        try:
            from app.models.database import conectar
            db = conectar().conexion2()
            cursor = db.cursor()
            cursor.execute("SELECT id FROM rol WHERE nombre = 'RolPermTest' LIMIT 1")
            id_rol = str(cursor.fetchone()[0])
            cursor.close()
            db.close()

            permisos = Permiso().listar_permisos_completos_por_rol(rol_id=id_rol)

            assert len(permisos) == 16
            assert all(p["consultar"] is False or p["consultar"] == 0 for p in permisos)
            assert all(p["registrar"] is False or p["registrar"] == 0 for p in permisos)
        finally:
            db = conectar().conexion2()
            cursor = db.cursor()
            cursor.execute("DELETE FROM rol WHERE nombre = 'RolPermTest'")
            db.commit()
            cursor.close()
            db.close()


# ==================== GUARDAR PERMISO ====================

class TestGuardarPermiso:

    def test_guarda_permiso_nuevo(self):
        modulo_id = "16"  # Personal
        try:
            _eliminar_permiso("1", modulo_id)
            resultado = Permiso().guardar_permiso(
                rol_id=ROL_ADMIN, modulo_id=modulo_id,
                registrar=True, modificar=False, eliminar=False,
            )
            assert resultado == "Permiso guardado exitosamente."

            permisos = Permiso().listar_permisos_por_rol(rol_id=ROL_ADMIN)
            fila = next(p for p in permisos if p["modulo_id"] == int(modulo_id))
            assert fila["consultar"] == 1
            assert fila["registrar"] == 1
            assert fila["modificar"] == 0
            assert fila["eliminar"] == 0
        finally:
            _restaurar_permiso_admin(modulo_id)

    def test_actualiza_permiso_existente(self):
        try:
            Permiso().guardar_permiso(
                rol_id=ROL_ADMIN, modulo_id=MODULO_ID_VALIDO,
                registrar=False, modificar=False, eliminar=False,
            )
            permisos = Permiso().listar_permisos_por_rol(rol_id=ROL_ADMIN)
            fila = next(p for p in permisos if p["modulo_id"] == int(MODULO_ID_VALIDO))
            assert fila["consultar"] == 0
            assert fila["registrar"] == 0
        finally:
            _restaurar_permiso_admin(MODULO_ID_VALIDO)

    def test_consultar_true_si_alguno_activo(self):
        try:
            Permiso().guardar_permiso(
                rol_id=ROL_ADMIN, modulo_id=MODULO_ID_VALIDO,
                registrar=False, modificar=True, eliminar=False,
            )
            permisos = Permiso().listar_permisos_por_rol(rol_id=ROL_ADMIN)
            fila = next(p for p in permisos if p["modulo_id"] == int(MODULO_ID_VALIDO))
            assert fila["consultar"] == 1
        finally:
            _restaurar_permiso_admin(MODULO_ID_VALIDO)

    @pytest.mark.parametrize(
        "rol_id, modulo_id, esperado",
        [
            pytest.param("", "1", "Rol y módulo son obligatorios.", id="rol-vacio"),
            pytest.param("1", "", "Rol y módulo son obligatorios.", id="modulo-vacio"),
            pytest.param(
                "abc", "1",
                "El campo Rol solo puede contener números.",
                id="rol-no-numerico",
            ),
            pytest.param(
                "1", "abc",
                "El campo Módulo solo puede contener números.",
                id="modulo-no-numerico",
            ),
        ],
    )
    def test_datos_invalidos(self, rol_id, modulo_id, esperado):
        resultado = Permiso().guardar_permiso(
            rol_id=rol_id, modulo_id=modulo_id, registrar=True
        )
        assert resultado == esperado


# ==================== GUARDAR MASIVO ====================

class TestGuardarPermisosMasivos:

    def test_guarda_varios_permisos(self):
        permisos_a_guardar = [
            {"modulo_id": "1", "registrar": True, "modificar": True, "eliminar": True},
            {"modulo_id": "2", "registrar": True, "modificar": False, "eliminar": False},
        ]
        try:
            exitosos, errores = Permiso().guardar_permisos_masivos(
                rol_id=ROL_ADMIN, permisos=permisos_a_guardar
            )
            assert exitosos == 2
            assert errores == []
        finally:
            _restaurar_permiso_admin("1")
            _restaurar_permiso_admin("2")

    def test_ignora_modulos_invalidos(self):
        permisos_a_guardar = [
            {"modulo_id": "1", "registrar": True},
            {"modulo_id": "abc", "registrar": True},
            {"modulo_id": "", "registrar": True},
        ]
        try:
            exitosos, errores = Permiso().guardar_permisos_masivos(
                rol_id=ROL_ADMIN, permisos=permisos_a_guardar
            )
            assert exitosos == 1
            assert len(errores) == 2
        finally:
            _restaurar_permiso_admin("1")

    def test_rol_vacio(self):
        exitosos, errores = Permiso().guardar_permisos_masivos(
            rol_id="", permisos=[]
        )
        assert exitosos == 0
        assert errores == ["Rol es obligatorio"]


# ==================== ELIMINAR PERMISO ====================

class TestEliminarPermiso:

    def test_elimina_permiso_existente(self):
        modulo_id = "16"
        try:
            Permiso().guardar_permiso(
                rol_id=ROL_ADMIN, modulo_id=modulo_id, registrar=True
            )

            resultado = Permiso().eliminar_permiso(
                rol_id=ROL_ADMIN, modulo_id=modulo_id
            )
            assert resultado == "Permiso eliminado exitosamente."

            permisos = Permiso().listar_permisos_por_rol(rol_id=ROL_ADMIN)
            assert not any(p["modulo_id"] == int(modulo_id) for p in permisos)
        finally:
            _restaurar_permiso_admin(modulo_id)

    def test_eliminar_inexistente_no_falla(self):
        resultado = Permiso().eliminar_permiso(
            rol_id="999999", modulo_id="999999"
        )
        assert resultado == "Permiso eliminado exitosamente."

    @pytest.mark.parametrize(
        "rol_id, modulo_id, esperado",
        [
            pytest.param("", "1", "Rol y módulo son obligatorios.", id="rol-vacio"),
            pytest.param("1", "", "Rol y módulo son obligatorios.", id="modulo-vacio"),
        ],
    )
    def test_datos_invalidos(self, rol_id, modulo_id, esperado):
        assert Permiso().eliminar_permiso(rol_id=rol_id, modulo_id=modulo_id) == esperado


# ==================== VERIFICAR PERMISO ====================

class TestVerificarPermiso:

    def test_admin_puede_consultar_empleados(self):
        assert Permiso().verificar_permiso(
            rol_id=ROL_ADMIN,
            modulo_nombre=MODULO_NOMBRE_EXISTENTE,
            permiso_tipo="consultar",
        ) is True

    def test_admin_puede_registrar_empleados(self):
        assert Permiso().verificar_permiso(
            rol_id=ROL_ADMIN,
            modulo_nombre=MODULO_NOMBRE_EXISTENTE,
            permiso_tipo="registrar",
        ) is True

    def test_consultar_es_true_si_cualquier_permiso_activo(self):
        try:
            Permiso().guardar_permiso(
                rol_id=ROL_ADMIN, modulo_id=MODULO_ID_VALIDO,
                registrar=False, modificar=False, eliminar=True,
            )
            assert Permiso().verificar_permiso(
                rol_id=ROL_ADMIN, modulo_nombre=MODULO_NOMBRE_EXISTENTE,
                permiso_tipo="consultar",
            ) is True
        finally:
            _restaurar_permiso_admin(MODULO_ID_VALIDO)

    def test_consultar_es_false_si_todos_inactivos(self):
        try:
            Permiso().guardar_permiso(
                rol_id=ROL_ADMIN, modulo_id=MODULO_ID_VALIDO,
                registrar=False, modificar=False, eliminar=False,
            )
            assert Permiso().verificar_permiso(
                rol_id=ROL_ADMIN, modulo_nombre=MODULO_NOMBRE_EXISTENTE,
                permiso_tipo="consultar",
            ) is False
        finally:
            _restaurar_permiso_admin(MODULO_ID_VALIDO)

    def test_rol_inexistente(self):
        assert Permiso().verificar_permiso(
            rol_id="999999",
            modulo_nombre=MODULO_NOMBRE_EXISTENTE,
            permiso_tipo="consultar",
        ) is False

    def test_modulo_inexistente(self):
        assert Permiso().verificar_permiso(
            rol_id=ROL_ADMIN,
            modulo_nombre="ModuloQueNoExiste",
            permiso_tipo="consultar",
        ) is False


# ==================== OBTENER PERMISOS DE USUARIO ====================

class TestObtenerPermisosUsuario:

    def test_admin_tiene_todos(self):
        permisos = Permiso().obtener_permisos_usuario(usuario_id="USR-001")

        assert permisos is not None
        assert len(permisos) == 16
        assert all(p["consultar"] == 1 for p in permisos)

    def test_usuario_inexistente_devuelve_todos_false(self):
        permisos = Permiso().obtener_permisos_usuario(usuario_id="USR-999")

        assert permisos is not None
        assert len(permisos) == 16
        assert all(p["consultar"] == 0 for p in permisos)