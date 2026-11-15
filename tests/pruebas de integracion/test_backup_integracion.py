"""Pruebas de integración de la clase Backup contra MySQL real (BD seguridad).

Regla de aislamiento: los backups temporales apuntan a rutas de archivo que
NO existen en disco, para que eliminar_backup nunca borre un archivo real.
"""
import pytest

from app.models.backup import Backup
from app.models.database import conectar

USUARIO_ADMIN = "USR-001"

# Datos fijos para todo el módulo (la limpieza borra por nombre, así que
# también elimina residuos de corridas anteriores).
NOMBRE_BACKUP = "backup_test_integracion"
RUTA_BACKUP = "/tmp/opencode/backups/backup_test_integracion.sql"


# ==================== HELPERS LOCALES (solo para este módulo) ====================


def _eliminar_backup_por_nombre(nombre: str) -> None:
    db = conectar().conexion2()
    if not db:
        return
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM backup WHERE nombre = %s", (nombre,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def _buscar_backup(nombre: str) -> dict | None:
    backups = Backup().listar_backups()
    return next((b for b in backups if b["nombre"] == nombre), None)


class TestRegistrarBackup:

    def test_datos_validos(self):
        try:
            resultado = Backup(id_usuario=USUARIO_ADMIN).registrar_backup(
                direccion_bd=RUTA_BACKUP, nombre=NOMBRE_BACKUP
            )

            assert resultado == "Backup registrado exitosamente."

            backup = _buscar_backup(NOMBRE_BACKUP)
            assert backup is not None
            assert backup["estado"] == "completado"
            assert backup["direccion_bd"] == RUTA_BACKUP
            assert backup["id_usuario"] == USUARIO_ADMIN
            assert backup["usuario_nombre"] == "super_admin"
        finally:
            _eliminar_backup_por_nombre(NOMBRE_BACKUP)

    def test_sin_id_usuario(self):
        resultado = Backup().registrar_backup(
            direccion_bd=RUTA_BACKUP, nombre=NOMBRE_BACKUP
        )

        assert resultado == "ID de usuario no proporcionado"


class TestListarBackups:

    def test_devuelve_lista(self):
        assert isinstance(Backup().listar_backups(), list)

    def test_incluye_backup_temporal(self):
        try:
            Backup(id_usuario=USUARIO_ADMIN).registrar_backup(
                direccion_bd=RUTA_BACKUP, nombre=NOMBRE_BACKUP
            )
            backup = _buscar_backup(NOMBRE_BACKUP)

            assert backup is not None
        finally:
            _eliminar_backup_por_nombre(NOMBRE_BACKUP)


class TestObtenerInfoBackup:

    def test_backup_existente(self):
        try:
            Backup(id_usuario=USUARIO_ADMIN).registrar_backup(
                direccion_bd=RUTA_BACKUP, nombre=NOMBRE_BACKUP
            )
            backup = _buscar_backup(NOMBRE_BACKUP)
            info = Backup().obtener_info_backup(backup["id_backup"])

            assert info is not None
            assert info["nombre"] == NOMBRE_BACKUP
            assert info["estado"] == "completado"
            assert info["id_usuario"] == USUARIO_ADMIN
        finally:
            _eliminar_backup_por_nombre(NOMBRE_BACKUP)

    def test_backup_inexistente(self):
        assert Backup().obtener_info_backup(999999) is None


class TestActualizarEstado:

    def test_datos_validos(self):
        id_backup = None
        try:
            Backup(id_usuario=USUARIO_ADMIN).registrar_backup(
                direccion_bd=RUTA_BACKUP, nombre=NOMBRE_BACKUP
            )
            id_backup = _buscar_backup(NOMBRE_BACKUP)["id_backup"]

            resultado = Backup().actualizar_estado(id_backup, "fallido")

            assert resultado == "Estado actualizado exitosamente"
            assert Backup().obtener_info_backup(id_backup)["estado"] == "fallido"
        finally:
            _eliminar_backup_por_nombre(NOMBRE_BACKUP)

    def test_backup_inexistente_reporta_exito(self):
        # El UPDATE no afecta filas, pero el método no valida existencia.
        resultado = Backup().actualizar_estado(999999, "fallido")

        assert resultado == "Estado actualizado exitosamente"


class TestEliminarBackup:

    def test_datos_validos(self):
        Backup(id_usuario=USUARIO_ADMIN).registrar_backup(
            direccion_bd=RUTA_BACKUP, nombre=NOMBRE_BACKUP
        )
        id_backup = _buscar_backup(NOMBRE_BACKUP)["id_backup"]

        resultado = Backup().eliminar_backup(id_backup)

        assert resultado == "Backup eliminado exitosamente"
        assert Backup().obtener_info_backup(id_backup) is None

    def test_backup_inexistente_reporta_exito(self):
        # Sin fila que borrar: devuelve el mensaje de éxito igualmente.
        resultado = Backup().eliminar_backup(999999)

        assert resultado == "Backup eliminado exitosamente"


class TestRestaurarBackup:

    def test_backup_inexistente(self):
        resultado = Backup(id_usuario=USUARIO_ADMIN).restaurar_backup(
            999999, {"host": "127.0.0.2", "database": "ituaccesoriobd"}
        )

        assert resultado == {
            "success": False,
            "message": "No se encontró el backup",
        }

    def test_archivo_de_backup_inexistente(self):
        try:
            Backup(id_usuario=USUARIO_ADMIN).registrar_backup(
                direccion_bd=RUTA_BACKUP, nombre=NOMBRE_BACKUP
            )
            id_backup = _buscar_backup(NOMBRE_BACKUP)["id_backup"]
            resultado = Backup(id_usuario=USUARIO_ADMIN).restaurar_backup(
                id_backup, {"host": "127.0.0.2", "database": "ituaccesoriobd"}
            )

            assert resultado["success"] is False
            assert resultado["message"] == (
                f"El archivo de backup no existe: {RUTA_BACKUP}"
            )
        finally:
            _eliminar_backup_por_nombre(NOMBRE_BACKUP)
