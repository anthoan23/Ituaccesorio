"""Pruebas de integración de la clase Permiso contra MySQL real (BD seguridad).

Regla de aislamiento: los tests de escritura usan SIEMPRE un rol temporal;
nunca modifican los permisos del rol Admin (rol 1) del seed.
"""
import pytest

from app.models.database import conectar
from app.models.permisos import Permiso

MODULO_EMPLEADOS = "1"      # Empleados
MODULO_INEXISTENTE = "999999"
USUARIO_ADMIN = "USR-001"
USUARIO_INEXISTENTE = "USR-999"
# Módulo "Cargos" (id 3): ninguna otra prueba de la suite escribe sus permisos.
MODULO_NO_TOCADO = "Cargos"


def _crear_rol_temporal() -> str:
    db = conectar().conexion2()
    if not db:
        raise RuntimeError("No se pudo conectar a la BD de seguridad")
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO rol (nombre, descripcion) VALUES (%s, %s)",
            ("RolPermIntegracion", "Rol temporal de pruebas de permisos"),
        )
        db.commit()
        return str(cursor.lastrowid)
    finally:
        cursor.close()
        db.close()


def _eliminar_rol_temporal(id_rol: str) -> None:
    db = conectar().conexion2()
    if not db:
        return
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM permiso WHERE rol_id = %s", (id_rol,))
        cursor.execute("DELETE FROM rol WHERE id = %s", (id_rol,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


@pytest.fixture
def rol_temporal():
    id_rol = _crear_rol_temporal()
    try:
        yield id_rol
    finally:
        _eliminar_rol_temporal(id_rol)


class TestListarPermisosPorRol:

    def test_rol_sin_permisos_devuelve_lista_vacia(self, rol_temporal):
        assert Permiso().listar_permisos_por_rol(rol_id=rol_temporal) == []

    def test_rol_inexistente_devuelve_lista_vacia(self):
        assert Permiso().listar_permisos_por_rol(rol_id="999999") == []

    def test_sin_rol_devuelve_none(self):
        assert Permiso().listar_permisos_por_rol() is None

    def test_ordenados_por_nombre_modulo(self, rol_temporal):
        Permiso().guardar_permiso(
            rol_id=rol_temporal, modulo_id=MODULO_EMPLEADOS, registrar=True
        )
        permisos = Permiso().listar_permisos_por_rol(rol_id=rol_temporal)
        nombres = [p["modulo_nombre"] for p in permisos]

        assert nombres == sorted(nombres)

    def test_permiso_guardado_aparece(self, rol_temporal):
        Permiso().guardar_permiso(
            rol_id=rol_temporal,
            modulo_id=MODULO_EMPLEADOS,
            registrar=True,
            modificar=False,
            eliminar=True,
        )
        permisos = Permiso().listar_permisos_por_rol(rol_id=rol_temporal)

        assert len(permisos) == 1
        fila = permisos[0]
        assert fila["modulo_id"] == int(MODULO_EMPLEADOS)
        assert fila["modulo_nombre"] == "Empleados"
        assert fila["consultar"] == 1
        assert fila["registrar"] == 1
        assert fila["modificar"] == 0
        assert fila["eliminar"] == 1


class TestListarPermisosCompletosPorRol:

    def test_rol_sin_permisos_ve_todos_los_modulos_en_false(self, rol_temporal):
        permisos = Permiso().listar_permisos_completos_por_rol(rol_id=rol_temporal)

        assert len(permisos) == 16
        assert all(p["consultar"] in (0, False) for p in permisos)
        assert all(p["registrar"] in (0, False) for p in permisos)
        assert all(p["modificar"] in (0, False) for p in permisos)
        assert all(p["eliminar"] in (0, False) for p in permisos)

    def test_refleja_el_permiso_guardado(self, rol_temporal):
        Permiso().guardar_permiso(
            rol_id=rol_temporal, modulo_id=MODULO_EMPLEADOS, registrar=True
        )
        permisos = Permiso().listar_permisos_completos_por_rol(rol_id=rol_temporal)
        fila = next(p for p in permisos if p["modulo_id"] == int(MODULO_EMPLEADOS))

        assert fila["consultar"] in (1, True)
        assert fila["registrar"] in (1, True)

    def test_sin_rol_devuelve_none(self):
        assert Permiso().listar_permisos_completos_por_rol() is None


class TestGuardarPermiso:

    def test_guarda_permiso_nuevo(self, rol_temporal):
        resultado = Permiso().guardar_permiso(
            rol_id=rol_temporal,
            modulo_id=MODULO_EMPLEADOS,
            registrar=True,
            modificar=False,
            eliminar=False,
        )

        assert resultado == "Permiso guardado exitosamente."
        fila = Permiso().listar_permisos_por_rol(rol_id=rol_temporal)[0]
        assert fila["consultar"] == 1
        assert fila["registrar"] == 1
        assert fila["modificar"] == 0

    def test_actualiza_permiso_existente(self, rol_temporal):
        Permiso().guardar_permiso(
            rol_id=rol_temporal, modulo_id=MODULO_EMPLEADOS, registrar=True
        )
        resultado = Permiso().guardar_permiso(
            rol_id=rol_temporal,
            modulo_id=MODULO_EMPLEADOS,
            registrar=False,
            modificar=True,
            eliminar=False,
        )

        assert resultado == "Permiso guardado exitosamente."
        fila = Permiso().listar_permisos_por_rol(rol_id=rol_temporal)[0]
        assert fila["registrar"] == 0
        assert fila["modificar"] == 1
        assert fila["consultar"] == 1

    def test_permisos_falsos(self, rol_temporal):
        Permiso().guardar_permiso(
            rol_id=rol_temporal, modulo_id=MODULO_EMPLEADOS, registrar=True
        )
        resultado = Permiso().guardar_permiso(
            rol_id=rol_temporal,
            modulo_id=MODULO_EMPLEADOS,
            registrar=False,
            modificar=False,
            eliminar=False,
        )

        assert resultado == "Permiso guardado exitosamente."
        fila = Permiso().listar_permisos_por_rol(rol_id=rol_temporal)[0]
        assert fila["consultar"] == 0
        assert fila["registrar"] == 0

    @pytest.mark.parametrize(
        "rol_id, modulo_id, esperado",
        [
            pytest.param(
                "", "1", "Rol y módulo son obligatorios.", id="rol-vacio"
            ),
            pytest.param(
                "1", "", "Rol y módulo son obligatorios.", id="modulo-vacio"
            ),
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
            pytest.param(
                "1" * 11,
                "1",
                "El campo Rol no puede tener más de 10 dígitos.",
                id="rol-demasiado-largo",
            ),
            pytest.param(
                "1", "1" * 11,
                "El campo Módulo no puede tener más de 10 dígitos.",
                id="modulo-demasiado-largo",
            ),
        ],
    )
    def test_datos_invalidos(self, rol_id, modulo_id, esperado):
        resultado = Permiso().guardar_permiso(
            rol_id=rol_id, modulo_id=modulo_id, registrar=True
        )
        assert resultado == esperado


class TestGuardarPermisosMasivos:

    def test_guarda_varios_permisos(self, rol_temporal):
        permisos_a_guardar = [
            {"modulo_id": "1", "registrar": True, "modificar": True, "eliminar": True},
            {"modulo_id": "2", "registrar": True, "modificar": False, "eliminar": False},
        ]
        exitosos, errores = Permiso().guardar_permisos_masivos(
            rol_id=rol_temporal, permisos=permisos_a_guardar
        )

        assert (exitosos, errores) == (2, [])
        filas = Permiso().listar_permisos_por_rol(rol_id=rol_temporal)
        assert len(filas) == 2

    def test_ignora_modulos_invalidos(self, rol_temporal):
        permisos_a_guardar = [
            {"modulo_id": "1", "registrar": True},
            {"modulo_id": "abc", "registrar": True},
            {"modulo_id": "", "registrar": True},
        ]
        exitosos, errores = Permiso().guardar_permisos_masivos(
            rol_id=rol_temporal, permisos=permisos_a_guardar
        )

        assert exitosos == 1
        assert len(errores) == 2

    def test_rol_vacio(self):
        exitosos, errores = Permiso().guardar_permisos_masivos(
            rol_id="", permisos=[]
        )

        assert (exitosos, errores) == (0, ["Rol es obligatorio"])

    def test_rol_no_numerico(self):
        exitosos, errores = Permiso().guardar_permisos_masivos(
            rol_id="abc", permisos=[]
        )

        assert exitosos == 0
        assert errores == ["El campo Rol solo puede contener números."]


class TestEliminarPermiso:

    def test_elimina_permiso_existente(self, rol_temporal):
        Permiso().guardar_permiso(
            rol_id=rol_temporal, modulo_id=MODULO_EMPLEADOS, registrar=True
        )
        resultado = Permiso().eliminar_permiso(
            rol_id=rol_temporal, modulo_id=MODULO_EMPLEADOS
        )

        assert resultado == "Permiso eliminado exitosamente."
        assert Permiso().listar_permisos_por_rol(rol_id=rol_temporal) == []

    def test_eliminar_inexistente_no_falla(self):
        resultado = Permiso().eliminar_permiso(
            rol_id="999999", modulo_id="999999"
        )

        assert resultado == "Permiso eliminado exitosamente."

    @pytest.mark.parametrize(
        "rol_id, modulo_id, esperado",
        [
            pytest.param(
                "", "1", "Rol y módulo son obligatorios.", id="rol-vacio"
            ),
            pytest.param(
                "1", "", "Rol y módulo son obligatorios.", id="modulo-vacio"
            ),
            pytest.param(
                "abc", "1",
                "El campo Rol solo puede contener números.",
                id="rol-no-numerico",
            ),
        ],
    )
    def test_datos_invalidos(self, rol_id, modulo_id, esperado):
        resultado = Permiso().eliminar_permiso(rol_id=rol_id, modulo_id=modulo_id)
        assert resultado == esperado


class TestVerificarPermiso:

    def test_permiso_registrar_concedido(self, rol_temporal):
        Permiso().guardar_permiso(
            rol_id=rol_temporal, modulo_id=MODULO_EMPLEADOS, registrar=True
        )
        assert (
            Permiso().verificar_permiso(
                rol_id=rol_temporal,
                modulo_nombre="Empleados",
                permiso_tipo="registrar",
            )
            is True
        )
        # 'consultar' es verdadero si cualquier permiso está activo
        assert (
            Permiso().verificar_permiso(
                rol_id=rol_temporal,
                modulo_nombre="Empleados",
                permiso_tipo="consultar",
            )
            is True
        )

    def test_permiso_denegado(self, rol_temporal):
        Permiso().guardar_permiso(
            rol_id=rol_temporal, modulo_id=MODULO_EMPLEADOS, registrar=True
        )
        assert (
            Permiso().verificar_permiso(
                rol_id=rol_temporal,
                modulo_nombre="Empleados",
                permiso_tipo="eliminar",
            )
            is False
        )

    def test_sin_permisos(self, rol_temporal):
        assert (
            Permiso().verificar_permiso(
                rol_id=rol_temporal,
                modulo_nombre="Empleados",
                permiso_tipo="consultar",
            )
            is False
        )

    def test_rol_inexistente(self):
        assert (
            Permiso().verificar_permiso(
                rol_id="999999",
                modulo_nombre="Empleados",
                permiso_tipo="consultar",
            )
            is False
        )

    def test_modulo_inexistente(self, rol_temporal):
        assert (
            Permiso().verificar_permiso(
                rol_id=rol_temporal,
                modulo_nombre="ModuloQueNoExiste",
                permiso_tipo="consultar",
            )
            is False
        )


class TestObtenerPermisosUsuario:

    def test_devuelve_los_16_modulos(self):
        permisos = Permiso().obtener_permisos_usuario(usuario_id=USUARIO_ADMIN)

        assert permisos is not None
        assert len(permisos) == 16
        # El módulo "Cargos" no es tocado por otras pruebas: su permiso
        # del seed (todo en 1) debe seguir intacto.
        cargos = next(
            p for p in permisos if p["modulo_nombre"] == MODULO_NO_TOCADO
        )
        assert cargos["consultar"] in (1, True)

    def test_usuario_inexistente_devuelve_todos_false(self):
        permisos = Permiso().obtener_permisos_usuario(usuario_id=USUARIO_INEXISTENTE)

        assert permisos is not None
        assert len(permisos) == 16
        assert all(p["consultar"] in (0, False) for p in permisos)

    def test_usuario_del_rol_temporal(self, rol_temporal):
        # Se liga el rol temporal a un usuario nuevo para verificar el join.
        from app.models.database import conectar

        db = conectar().conexion2()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO usuario (id, nombre, cedula, password, rol_id) "
                "VALUES ('USR-TMP', 'Temporal', %s, 'x', %s)",
                (int(rol_temporal) * 1000 + 1, rol_temporal),
            )
            db.commit()
        finally:
            cursor.close()
            db.close()

        try:
            permisos = Permiso().obtener_permisos_usuario(usuario_id="USR-TMP")

            assert len(permisos) == 16
            assert all(p["consultar"] in (0, False) for p in permisos)
        finally:
            db = conectar().conexion2()
            cursor = db.cursor()
            try:
                cursor.execute("DELETE FROM usuario WHERE id = 'USR-TMP'")
                db.commit()
            finally:
                cursor.close()
                db.close()
