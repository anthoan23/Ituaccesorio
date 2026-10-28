"""Pruebas unitarias de la clase Cargo (app.models.cargos).

Los fixtures `conexion_falsa` y `conexion_caída` viven en tests/conftest.py
y se comparten con todos los archivos de prueba.
"""
import pytest

from app.models.cargos import Cargo
from tests.helpers import cierra_recursos, sin_sentencia, ultima_sentencia

MENSAJE_ERROR_CONEXION = (
    "No se pudo conectar con la base de datos. "
    "Inténtalo de nuevo más tarde o comunícate con los técnicos."
)

# ==================== Datos de frontera ====================
ID_MINIMO = "123456789"  # 9 dígitos (mínimo permitido)
ID_MAXIMO = "1234567890"  # 10 dígitos (máximo permitido)

NOMBRE_MINIMO = "Caj"  # 3 caracteres (mínimo)
NOMBRE_MAXIMO = "C" * 30  # 30 caracteres (máximo)

DESCRIPCION_MINIMA = "Ati"  # 3 caracteres (mínimo)
DESCRIPCION_MAXIMA = "D" * 250  # 250 caracteres (máximo)


class TestListarCargos:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {"id": "2", "nombre": "Cajero", "descripcion": "Atiende la caja"},
            {"id": "5", "nombre": "Gerente", "descripcion": "Administra el local"},
        ]

        resultado = Cargo().listar_cargos()

        assert resultado == [
            {"id": "2", "nombre": "Cajero", "descripcion": "Atiende la caja"},
            {"id": "5", "nombre": "Gerente", "descripcion": "Administra el local"},
        ]
        assert "FROM Cargo" in ultima_sentencia(cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        resultado = Cargo().listar_cargos()

        assert resultado == []

    def test_conexion_caida(self, conexion_caída):
        resultado = Cargo().listar_cargos()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Cargo().listar_cargos()

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Cargo().listar_cargos()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestAgregarCargo:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None  # el cargo aún no existe

        cargo = Cargo(ID_MAXIMO, NOMBRE_MINIMO, DESCRIPCION_MINIMA)
        resultado = cargo.agregar_cargo()

        assert resultado == "Cargo agregado exitosamente."
        assert ultima_sentencia(cursor) == "CALL Crear_cargo(%s, %s)"
        assert cursor.execute.call_args_list[-1].args == (
            "CALL Crear_cargo(%s, %s)",
            (NOMBRE_MINIMO, DESCRIPCION_MINIMA),
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 2 operaciones (buscar duplicado + CALL): cada una cierra su cursor
        cierra_recursos(db, cursor)

    def test_valores_minimos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Cargo(ID_MAXIMO, NOMBRE_MINIMO, DESCRIPCION_MINIMA).agregar_cargo()

        assert resultado == "Cargo agregado exitosamente."
        db.commit.assert_called_once()

    def test_valores_maximos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Cargo(ID_MAXIMO, NOMBRE_MAXIMO, DESCRIPCION_MAXIMA).agregar_cargo()

        assert resultado == "Cargo agregado exitosamente."
        assert cursor.execute.call_args_list[-1].args == (
            "CALL Crear_cargo(%s, %s)",
            (NOMBRE_MAXIMO, DESCRIPCION_MAXIMA),
        )
        db.commit.assert_called_once()

    @pytest.mark.parametrize(
        "nombre, descripcion, esperado",
        [
            pytest.param(
                "",
                DESCRIPCION_MINIMA,
                "El campo Nombre no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                "Ca",
                DESCRIPCION_MINIMA,
                "El campo Nombre debe tener al menos 3 caracteres.",
                id="nombre-demasiado-corto",
            ),
            pytest.param(
                "C" * 31,
                DESCRIPCION_MINIMA,
                "El campo Nombre no puede tener más de 30 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                "Caja #1",
                DESCRIPCION_MINIMA,
                "El campo Nombre solo puede contener letras, acentos y espacios.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                NOMBRE_MINIMO,
                "",
                "El campo Descripción no puede estar vacío.",
                id="descripcion-vacia",
            ),
            pytest.param(
                NOMBRE_MINIMO,
                "At",
                "El campo Descripción debe tener al menos 3 caracteres.",
                id="descripcion-demasiado-corta",
            ),
            pytest.param(
                NOMBRE_MINIMO,
                "D" * 251,
                "El campo Descripción no puede tener más de 250 caracteres.",
                id="descripcion-demasiado-larga",
            ),
            pytest.param(
                NOMBRE_MINIMO,
                "@#$%",
                "El campo Descripción solo puede contener letras, números, acentos y espacios.",
                id="descripcion-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(
        self, conexion_falsa, nombre, descripcion, esperado
    ):
        db, cursor = conexion_falsa

        resultado = Cargo(ID_MAXIMO, nombre, descripcion).agregar_cargo()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_cargo_duplicado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_MAXIMO,)  # ya existe ese nombre

        resultado = Cargo(ID_MAXIMO, "Cajero", DESCRIPCION_MINIMA).agregar_cargo()

        assert resultado == "El cargo 'Cajero' ya existe."
        sin_sentencia(cursor, "CALL")
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Cargo(ID_MAXIMO, NOMBRE_MINIMO, DESCRIPCION_MINIMA).agregar_cargo()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        # 1ª llamada: consulta de duplicado; 2ª: el CALL que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = Cargo(ID_MAXIMO, NOMBRE_MINIMO, DESCRIPCION_MINIMA).agregar_cargo()

        assert resultado == "Error al agregar cargo."
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestEliminarCargo:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)  # el cargo sí existe

        resultado = Cargo(ID_MAXIMO).eliminar_cargo()

        assert resultado == "Cargo eliminado exitosamente."
        assert "DELETE FROM Cargo" in ultima_sentencia(cursor)
        assert cursor.execute.call_args_list[-1].args == (
            "DELETE FROM Cargo WHERE ID_cargo = %s",
            (ID_MAXIMO,),
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 2 operaciones (verificar existencia + DELETE): cada una cierra su cursor
        cierra_recursos(db, cursor)

    def test_id_minimo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        resultado = Cargo(ID_MINIMO).eliminar_cargo()

        assert resultado == "Cargo eliminado exitosamente."
        assert cursor.execute.call_args_list[-1].args == (
            "DELETE FROM Cargo WHERE ID_cargo = %s",
            (ID_MINIMO,),
        )

    def test_id_maximo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        resultado = Cargo(ID_MAXIMO).eliminar_cargo()

        assert resultado == "Cargo eliminado exitosamente."

    @pytest.mark.parametrize(
        "id_cargo, esperado",
        [
            pytest.param(
                "",
                "El campo ID del Cargo no puede estar vacío.",
                id="id-vacio",
            ),
            pytest.param(
                "1234567",
                "El campo ID del Cargo debe tener al menos 9 caracteres.",
                id="id-demasiado-corto",
            ),
            pytest.param(
                "12345678901",
                "El campo ID del Cargo no puede tener más de 10 caracteres.",
                id="id-demasiado-largo",
            ),
            pytest.param(
                # Nota: un id de solo letras SÍ pasa validar_texto_numero
                # (permite letras), por eso usamos un carácter especial.
                "12345678#",
                "El campo ID del Cargo solo puede contener letras, números, acentos y espacios.",
                id="id-caracteres-invalidos",
            ),
        ],
    )
    def test_id_invalido_no_tocan_la_bd(self, conexion_falsa, id_cargo, esperado):
        db, cursor = conexion_falsa

        resultado = Cargo(id_cargo).eliminar_cargo()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_cargo_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Cargo(ID_MAXIMO).eliminar_cargo()

        assert resultado == f"El cargo con identificador {ID_MAXIMO} no existe."
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Cargo(ID_MAXIMO).eliminar_cargo()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)
        # 1ª llamada: consulta de existencia; 2ª: el DELETE que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = Cargo(ID_MAXIMO).eliminar_cargo()

        assert resultado == (
            "Error al eliminar cargo. Verifica que no esté en uso por empleados."
        )
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestActualizarCargo:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        # 1ª consulta (verificar id): existe; 2ª (nombre): es el mismo cargo
        cursor.fetchone.side_effect = [(1,), (ID_MAXIMO,)]

        resultado = Cargo(ID_MAXIMO, "Gerente", "Administra el local").actualizar_cargo()

        assert resultado == "Cargo actualizado exitosamente."
        assert "UPDATE Cargo" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args == (
            ultima_sentencia(cursor),
            ("Gerente", "Administra el local", ID_MAXIMO),
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 3 operaciones (verificar, consultar nombre, UPDATE)
        cierra_recursos(db, cursor)

    def test_valores_minimos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (ID_MAXIMO,)]

        resultado = Cargo(
            ID_MAXIMO, NOMBRE_MINIMO, DESCRIPCION_MINIMA
        ).actualizar_cargo()

        assert resultado == "Cargo actualizado exitosamente."
        db.commit.assert_called_once()

    def test_valores_maximos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (ID_MAXIMO,)]

        resultado = Cargo(
            ID_MAXIMO, NOMBRE_MAXIMO, DESCRIPCION_MAXIMA
        ).actualizar_cargo()

        assert resultado == "Cargo actualizado exitosamente."
        assert cursor.execute.call_args_list[-1].args[1] == (
            NOMBRE_MAXIMO,
            DESCRIPCION_MAXIMA,
            ID_MAXIMO,
        )
        db.commit.assert_called_once()

    @pytest.mark.parametrize(
        "id_cargo, nombre, descripcion, esperado",
        [
            pytest.param(
                "",
                "Gerente",
                "Administra",
                "El campo ID del Cargo no puede estar vacío.",
                id="id-vacio",
            ),
            pytest.param(
                "1234567",
                "Gerente",
                "Administra",
                "El campo ID del Cargo debe tener al menos 9 caracteres.",
                id="id-demasiado-corto",
            ),
            pytest.param(
                "12345678901",
                "Gerente",
                "Administra",
                "El campo ID del Cargo no puede tener más de 10 caracteres.",
                id="id-demasiado-largo",
            ),
            pytest.param(
                # Nota: un id de solo letras SÍ pasa validar_texto_numero
                # (permite letras), por eso usamos un carácter especial.
                "12345678#",
                "Gerente",
                "Administra",
                "El campo ID del Cargo solo puede contener letras, números, acentos y espacios.",
                id="id-caracteres-invalidos",
            ),
            pytest.param(
                ID_MAXIMO,
                "",
                "Administra",
                "El campo Nombre no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                ID_MAXIMO,
                "Ge",
                "Administra",
                "El campo Nombre debe tener al menos 3 caracteres.",
                id="nombre-demasiado-corto",
            ),
            pytest.param(
                ID_MAXIMO,
                "G" * 31,
                "Administra",
                "El campo Nombre no puede tener más de 30 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                ID_MAXIMO,
                "Gerente #1",
                "Administra",
                "El campo Nombre solo puede contener letras, acentos y espacios.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                ID_MAXIMO,
                "Gerente",
                "",
                "El campo Descripción no puede estar vacío.",
                id="descripcion-vacia",
            ),
            pytest.param(
                ID_MAXIMO,
                "Gerente",
                "Ad",
                "El campo Descripción debe tener al menos 3 caracteres.",
                id="descripcion-demasiado-corta",
            ),
            pytest.param(
                ID_MAXIMO,
                "Gerente",
                "D" * 251,
                "El campo Descripción no puede tener más de 250 caracteres.",
                id="descripcion-demasiado-larga",
            ),
            pytest.param(
                ID_MAXIMO,
                "Gerente",
                "@#$%",
                "El campo Descripción solo puede contener letras, números, acentos y espacios.",
                id="descripcion-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(
        self, conexion_falsa, id_cargo, nombre, descripcion, esperado
    ):
        db, cursor = conexion_falsa

        resultado = Cargo(id_cargo, nombre, descripcion).actualizar_cargo()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_cargo_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Cargo(ID_MAXIMO, "Gerente", "Administra").actualizar_cargo()

        assert resultado == f"El cargo con identificador {ID_MAXIMO} no existe."
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    def test_nombre_duplicado_de_otro_cargo(self, conexion_falsa):
        db, cursor = conexion_falsa
        # 1ª consulta (verificar id): existe; 2ª (nombre): pertenece a otro cargo
        cursor.fetchone.side_effect = [(1,), ("999999999",)]

        resultado = Cargo(ID_MAXIMO, "Cajero", DESCRIPCION_MINIMA).actualizar_cargo()

        assert resultado == "El cargo 'Cajero' ya existe."
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    def test_mismo_nombre_del_mismo_cargo_se_permite(self, conexion_falsa):
        db, cursor = conexion_falsa
        # 2ª consulta devuelve el mismo id: no hay duplicado ajeno
        cursor.fetchone.side_effect = [(1,), (ID_MAXIMO,)]

        resultado = Cargo(
            ID_MAXIMO, NOMBRE_MINIMO, DESCRIPCION_MINIMA
        ).actualizar_cargo()

        assert resultado == "Cargo actualizado exitosamente."
        db.commit.assert_called_once()

    def test_conexion_caida(self, conexion_caída):
        resultado = Cargo(ID_MAXIMO, "Gerente", "Administra").actualizar_cargo()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (ID_MAXIMO,)]
        # 1ª: existencia; 2ª: consulta de nombre; 3ª: el UPDATE que falla
        cursor.execute.side_effect = [None, None, Exception("fallo simulado")]

        resultado = Cargo(ID_MAXIMO, "Gerente", "Administra").actualizar_cargo()

        assert resultado == "Error al actualizar cargo."
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestVerificarCargoPorId:

    def test_cargo_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert Cargo(ID_MAXIMO).verificar_cargo_por_id() is True

        assert ultima_sentencia(cursor) == (
            "SELECT 1 FROM Cargo WHERE ID_cargo = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == (ID_MAXIMO,)

    def test_cargo_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Cargo(ID_MAXIMO).verificar_cargo_por_id() is False

    def test_conexion_caida(self, conexion_caída):
        assert Cargo(ID_MAXIMO).verificar_cargo_por_id() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Cargo(ID_MAXIMO).verificar_cargo_por_id()

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Cargo(ID_MAXIMO).verificar_cargo_por_id()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerIdPorNombre:

    def test_cargo_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_MAXIMO,)

        resultado = Cargo(nombre_cargo="Cajero").obtener_id_por_nombre()

        assert resultado == ID_MAXIMO
        assert "SELECT ID_cargo FROM Cargo" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == ("Cajero",)

    def test_cargo_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Cargo(nombre_cargo="Inexistente").obtener_id_por_nombre()

        assert resultado is None

    def test_conexion_caida(self, conexion_caída):
        assert Cargo(nombre_cargo="Cajero").obtener_id_por_nombre() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_MAXIMO,)

        Cargo(nombre_cargo="Cajero").obtener_id_por_nombre()

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_MAXIMO,)

        Cargo(nombre_cargo="Cajero").obtener_id_por_nombre()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()
