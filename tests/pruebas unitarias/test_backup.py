"""Pruebas unitarias de la clase Backup (app.models.backup).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.
"""
from unittest.mock import MagicMock, patch

import pymysql
import pytest

from app.models.backup import Backup, obtener_info_backup
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

# ==================== Datos de frontera ====================
ID_BACKUP = 7
USUARIO_ID = "USR-001"
RUTA_BACKUP = "/tmp/respaldo.sql"
NOMBRE_BACKUP = "respaldo_2026.sql"

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "clave",
    "database": "ituaccesoriobd",
    "port": 3307,
}


class TestListarBackups:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {
                "id_backup": ID_BACKUP,
                "id_usuario": USUARIO_ID,
                "usuario_nombre": "Ana",
                "estado": "completado",
                "fecha": "2026-01-01",
                "direccion_bd": RUTA_BACKUP,
                "nombre": NOMBRE_BACKUP,
            }
        ]
        cursor.fetchall.return_value = filas

        resultado = Backup().listar_backups()

        assert resultado == filas
        assert "FROM backup" in ultima_sentencia(cursor)
        cierra_recursos(db, cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Backup().listar_backups() == []

    def test_conexion_caida(self, conexion_caída):
        assert Backup().listar_backups() == []

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Backup().listar_backups()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestRegistrarBackup:

    def test_sin_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Backup().registrar_backup(RUTA_BACKUP, NOMBRE_BACKUP)

        assert resultado == "ID de usuario no proporcionado"
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Backup(
            id_usuario=USUARIO_ID
        ).registrar_backup(RUTA_BACKUP, NOMBRE_BACKUP)

        assert resultado == "Error al conectar a la base de datos de seguridad"

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch("app.models.backup.Bitacora") as bitacora:
            resultado = Backup(
                id_usuario=USUARIO_ID
            ).registrar_backup(RUTA_BACKUP, NOMBRE_BACKUP)

        assert resultado == "Backup registrado exitosamente"
        assert "INSERT INTO backup" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (
            USUARIO_ID,
            "completado",
            RUTA_BACKUP,
            NOMBRE_BACKUP,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        bitacora.return_value.registrar.assert_called_once()
        cierra_recursos(db, cursor)

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = Backup(
            id_usuario=USUARIO_ID
        ).registrar_backup(RUTA_BACKUP, NOMBRE_BACKUP)

        assert resultado == "Error al registrar backup: fallo simulado"
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestActualizarEstado:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Backup().actualizar_estado(ID_BACKUP, "completado")

        assert resultado == "Estado actualizado exitosamente"
        assert ultima_sentencia(cursor) == (
            "UPDATE backup SET estado = %s WHERE id_backup = %s"
        )
        assert cursor.execute.call_args.args[1] == ("completado", ID_BACKUP)
        db.commit.assert_called_once()
        cierra_recursos(db, cursor)

    def test_conexion_caida(self, conexion_caída):
        assert Backup().actualizar_estado(ID_BACKUP, "completado") == (
            "Error al conectar a la base de datos"
        )

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = Backup().actualizar_estado(ID_BACKUP, "completado")

        assert resultado == "Error al actualizar estado: fallo simulado"
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestEliminarBackup:

    def test_datos_validos_elimina_archivo_y_registro(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (RUTA_BACKUP,)

        with patch("app.models.backup.os.path.exists", return_value=True), patch(
            "app.models.backup.os.remove"
        ) as remover, patch("app.models.backup.Bitacora") as bitacora:
            resultado = Backup(id_usuario=USUARIO_ID).eliminar_backup(ID_BACKUP)

        assert resultado == "Backup eliminado exitosamente"
        remover.assert_called_once_with(RUTA_BACKUP)
        assert "DELETE FROM backup" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_BACKUP,)
        db.commit.assert_called_once()
        bitacora.return_value.registrar.assert_called_once()

    def test_sin_registro_solo_borra_la_fila(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with patch("app.models.backup.os.path.exists") as existe:
            resultado = Backup().eliminar_backup(ID_BACKUP)

        assert resultado == "Backup eliminado exitosamente"
        existe.assert_not_called()
        db.commit.assert_called_once()

    def test_error_al_borrar_archivo_no_impide_el_registro(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (RUTA_BACKUP,)

        with patch("app.models.backup.os.path.exists", return_value=True), patch(
            "app.models.backup.os.remove", side_effect=OSError("permiso denegado")
        ):
            resultado = Backup().eliminar_backup(ID_BACKUP)

        assert resultado == "Backup eliminado exitosamente"
        db.commit.assert_called_once()

    def test_conexion_caida(self, conexion_caída):
        assert Backup().eliminar_backup(ID_BACKUP) == (
            "Error al conectar a la base de datos"
        )

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = Backup().eliminar_backup(ID_BACKUP)

        assert resultado == "Error al eliminar backup: fallo simulado"
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestObtenerInfoBackup:

    def test_backup_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {"id_backup": ID_BACKUP, "nombre": NOMBRE_BACKUP}
        cursor.fetchone.return_value = esperado

        assert Backup().obtener_info_backup(ID_BACKUP) == esperado
        assert "FROM backup" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_BACKUP,)

    def test_backup_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Backup().obtener_info_backup(ID_BACKUP) is None

    def test_conexion_caida(self, conexion_caída):
        assert Backup().obtener_info_backup(ID_BACKUP) is None

    def test_funcion_de_modulo_delega_en_la_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id_backup": ID_BACKUP}
        conexion_bd = MagicMock()
        conexion_bd.conexion2.return_value = db
        falso = MagicMock()
        setattr(falso, "__conexion_bd", conexion_bd)

        assert obtener_info_backup(falso, ID_BACKUP) == {"id_backup": ID_BACKUP}


class TestPrepararSqlParaRestaurar:

    def test_elimina_definer(self):
        sql = "CREATE DEFINER=`root`@`localhost` VIEW v AS SELECT 1;"

        resultado = Backup()._preparar_sql_para_restaurar(sql)

        assert "DEFINER" not in resultado
        assert "CREATE  VIEW v AS SELECT 1;" in resultado

    def test_comenta_gtid_purged(self):
        sql = "SET @@GLOBAL.GTID_PURGED='abc';\nSELECT 1;"

        resultado = Backup()._preparar_sql_para_restaurar(sql)

        assert resultado.startswith("-- Comentado al restaurar:")
        assert "SELECT 1;" in resultado

    def test_comenta_sql_log_bin(self):
        sql = "SET @@SESSION.SQL_LOG_BIN=0;"

        resultado = Backup()._preparar_sql_para_restaurar(sql)

        assert resultado.startswith("-- Comentado al restaurar:")

    def test_no_modifica_sql_normal(self):
        sql = "CREATE TABLE prueba (id INT);"

        assert Backup()._preparar_sql_para_restaurar(sql) == sql


class TestStatementDebeOmitirse:

    @pytest.mark.parametrize(
        "statement",
        [
            pytest.param("CREATE USER 'x'@'y'", id="create-user"),
            pytest.param("GRANT ALL ON *.* TO 'x'@'y'", id="grant"),
            pytest.param("REVOKE ALL ON *.* FROM 'x'@'y'", id="revoke"),
            pytest.param("SET @@GLOBAL.GTID_PURGED='abc'", id="gtid"),
            pytest.param("LOCK TABLES prueba WRITE", id="lock"),
            pytest.param("FLUSH PRIVILEGES", id="flush"),
            pytest.param("CREATE ROLE 'r'", id="create-role"),
            pytest.param("DROP USER 'x'@'y'", id="drop-user"),
        ],
    )
    def test_omite_administracion_global(self, statement):
        assert Backup()._statement_debe_omitirse(statement) is True

    @pytest.mark.parametrize(
        "statement",
        [
            pytest.param("CREATE TABLE prueba (id INT)", id="create-table"),
            pytest.param("INSERT INTO prueba VALUES (1)", id="insert"),
            pytest.param("SELECT 1", id="select"),
            pytest.param("CREATE VIEW v AS SELECT 1", id="create-view"),
        ],
    )
    def test_permite_statements_normales(self, statement):
        assert Backup()._statement_debe_omitirse(statement) is False


class TestSplitSqlStatements:

    def test_varios_statements_simples(self):
        sql = "CREATE TABLE a (id INT);\nINSERT INTO a VALUES (1);"

        resultado = Backup()._split_sql_statements(sql)

        assert resultado == ["CREATE TABLE a (id INT)", "INSERT INTO a VALUES (1)"]

    def test_respeta_delimiter_en_procedimiento(self):
        sql = (
            "DELIMITER $$\n"
            "CREATE PROCEDURE p()\n"
            "BEGIN\n"
            "SELECT 1;\n"
            "END$$\n"
            "DELIMITER ;\n"
            "SELECT 2;"
        )

        resultado = Backup()._split_sql_statements(sql)

        assert len(resultado) == 2
        assert "CREATE PROCEDURE p()" in resultado[0]
        assert resultado[1] == "SELECT 2"

    def test_ignora_lineas_vacias(self):
        assert Backup()._split_sql_statements("\n\n") == []

    def test_statement_sin_delimitador_final(self):
        assert Backup()._split_sql_statements("SELECT 1") == ["SELECT 1"]


class TestRestaurarBackup:

    def test_backup_inexistente(self, conexion_falsa):
        with patch.object(Backup, "obtener_info_backup", return_value=None):
            resultado = Backup().restaurar_backup(ID_BACKUP, DB_CONFIG)

        assert resultado == {"success": False, "message": "No se encontró el backup"}

    def test_archivo_no_existe(self, conexion_falsa):
        info = {"direccion_bd": RUTA_BACKUP, "nombre": NOMBRE_BACKUP}
        with patch.object(Backup, "obtener_info_backup", return_value=info), patch(
            "app.models.backup.os.path.exists", return_value=False
        ):
            resultado = Backup().restaurar_backup(ID_BACKUP, DB_CONFIG)

        assert resultado == {
            "success": False,
            "message": f"El archivo de backup no existe: {RUTA_BACKUP}",
        }

    def test_restauracion_exitosa(self, conexion_falsa, tmp_path):
        archivo = tmp_path / "respaldo.sql"
        archivo.write_text("CREATE TABLE a (id INT);\nINSERT INTO a VALUES (1);")
        info = {"direccion_bd": str(archivo), "nombre": NOMBRE_BACKUP}
        conexion = MagicMock()
        cursor_destino = MagicMock()
        conexion.cursor.return_value = cursor_destino

        with patch.object(Backup, "obtener_info_backup", return_value=info), patch(
            "app.models.backup.pymysql.connect", return_value=conexion
        ), patch("app.models.backup.Bitacora") as bitacora:
            resultado = Backup(id_usuario=USUARIO_ID).restaurar_backup(
                ID_BACKUP, DB_CONFIG
            )

        assert resultado["success"] is True
        assert resultado["executed"] == 2
        assert resultado["errors"] is None
        assert "2 statements ejecutados" in resultado["message"]
        conexion.commit.assert_called()
        conexion.close.assert_called_once()
        bitacora.return_value.registrar.assert_called_once()

    def test_omite_statements_de_administracion(self, conexion_falsa, tmp_path):
        archivo = tmp_path / "respaldo.sql"
        archivo.write_text("GRANT ALL ON *.* TO 'x'@'y';\nSELECT 1;")
        info = {"direccion_bd": str(archivo), "nombre": NOMBRE_BACKUP}
        conexion = MagicMock()

        with patch.object(Backup, "obtener_info_backup", return_value=info), patch(
            "app.models.backup.pymysql.connect", return_value=conexion
        ), patch("app.models.backup.Bitacora"):
            resultado = Backup().restaurar_backup(ID_BACKUP, DB_CONFIG)

        assert resultado["executed"] == 1

    def test_error_critico_detiene_la_restauracion(self, conexion_falsa, tmp_path):
        archivo = tmp_path / "respaldo.sql"
        archivo.write_text("SELECT 1;")
        info = {"direccion_bd": str(archivo), "nombre": NOMBRE_BACKUP}
        conexion = MagicMock()
        cursor_destino = MagicMock()
        cursor_destino.execute.side_effect = Exception("syntax error near SELECT")
        conexion.cursor.return_value = cursor_destino

        with patch.object(Backup, "obtener_info_backup", return_value=info), patch(
            "app.models.backup.pymysql.connect", return_value=conexion
        ):
            resultado = Backup().restaurar_backup(ID_BACKUP, DB_CONFIG)

        assert resultado["success"] is False
        assert "Error crítico al restaurar" in resultado["message"]
        conexion.rollback.assert_called_once()
        conexion.close.assert_called_once()

    def test_error_1227_se_omite_y_continua(self, conexion_falsa, tmp_path):
        archivo = tmp_path / "respaldo.sql"
        archivo.write_text("SELECT 1;\nSELECT 2;")
        info = {"direccion_bd": str(archivo), "nombre": NOMBRE_BACKUP}
        conexion = MagicMock()
        cursor_destino = MagicMock()
        error = pymysql.Error("sin privilegios")
        error.errno = 1227
        cursor_destino.execute.side_effect = [error, None]
        conexion.cursor.return_value = cursor_destino

        with patch.object(Backup, "obtener_info_backup", return_value=info), patch(
            "app.models.backup.pymysql.connect", return_value=conexion
        ), patch("app.models.backup.Bitacora"):
            resultado = Backup().restaurar_backup(ID_BACKUP, DB_CONFIG)

        assert resultado["success"] is True
        assert resultado["executed"] == 1
        assert resultado["errors"] is not None

    def test_error_de_pymysql_al_conectar(self, conexion_falsa, tmp_path):
        archivo = tmp_path / "respaldo.sql"
        archivo.write_text("SELECT 1;")
        info = {"direccion_bd": str(archivo), "nombre": NOMBRE_BACKUP}

        with patch.object(Backup, "obtener_info_backup", return_value=info), patch(
            "app.models.backup.pymysql.connect",
            side_effect=pymysql.Error("conexión rechazada"),
        ):
            resultado = Backup().restaurar_backup(ID_BACKUP, DB_CONFIG)

        assert resultado["success"] is False
        assert resultado["message"] == "Error de base de datos: conexión rechazada"

    def test_error_generico_al_restaurar(self, conexion_falsa, tmp_path):
        archivo = tmp_path / "respaldo.sql"
        archivo.write_text("SELECT 1;")
        info = {"direccion_bd": str(archivo), "nombre": NOMBRE_BACKUP}

        with patch.object(Backup, "obtener_info_backup", return_value=info), patch(
            "app.models.backup.pymysql.connect", side_effect=OSError("disco lleno")
        ):
            resultado = Backup().restaurar_backup(ID_BACKUP, DB_CONFIG)

        assert resultado["success"] is False
        assert resultado["message"] == "Error al restaurar backup: disco lleno"
