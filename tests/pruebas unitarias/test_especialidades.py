"""Pruebas unitarias de la clase Especialidad (app.models.especialidades).

Los fixtures `conexion_falsa` y `conexion_caída` viven en tests/conftest.py
y los helpers en tests/helpers.py.
"""
import pytest

from app.models.especialidades import Especialidad
from tests.helpers import cierra_recursos, sin_sentencia, ultima_sentencia

MENSAJE_ERROR_CONEXION = (
    "No se pudo conectar con la base de datos. "
    "Inténtalo de nuevo más tarde o comunícate con los técnicos."
)

# ==================== Datos de frontera ====================
ID_MINIMO = "123456789"  # 9 caracteres (mínimo)
ID_MAXIMO = "1234567890"  # 10 caracteres (máximo)

NOMBRE_MINIMO = "Esp"  # 3 caracteres (mínimo)
NOMBRE_MAXIMO = "E" * 30  # 30 caracteres (máximo)

DESCRIPCION_MINIMA = "Ati"  # 3 caracteres (mínimo)
DESCRIPCION_MAXIMA = "D" * 250  # 250 caracteres (máximo)


class ErrorConErrno(Exception):
    """Imita un error de MySQL con su atributo errno (p. ej. 1451: clave foránea)."""

    def __init__(self, errno):
        super().__init__(f"Error simulado {errno}")
        self.errno = errno


class TestListarEspecialidades:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {"id": "1", "nombre": "Celulares", "descripcion": "Reparación de móviles"},
        ]

        resultado = Especialidad().listar_especialidades()

        assert resultado == [
            {"id": "1", "nombre": "Celulares", "descripcion": "Reparación de móviles"},
        ]
        assert "FROM Especialidad" in ultima_sentencia(cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Especialidad().listar_especialidades() == []

    def test_conexion_caida(self, conexion_caída):
        resultado = Especialidad().listar_especialidades()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Especialidad().listar_especialidades()

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Especialidad().listar_especialidades()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestAgregarEspecialidad:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None  # la especialidad aún no existe

        resultado = Especialidad(
            "", NOMBRE_MINIMO, DESCRIPCION_MINIMA
        ).agregar_especialidad()

        assert resultado == "Especialidad agregada exitosamente."
        assert ultima_sentencia(cursor) == "CALL Crear_especialidad(%s, %s)"
        assert cursor.execute.call_args_list[-1].args == (
            "CALL Crear_especialidad(%s, %s)",
            (NOMBRE_MINIMO, DESCRIPCION_MINIMA),
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 2 operaciones (buscar duplicado + CALL): cada una cierra su cursor
        cierra_recursos(db, cursor)

    def test_valores_minimos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Especialidad(
            "", NOMBRE_MINIMO, DESCRIPCION_MINIMA
        ).agregar_especialidad()

        assert resultado == "Especialidad agregada exitosamente."
        db.commit.assert_called_once()

    def test_valores_maximos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Especialidad(
            "", NOMBRE_MAXIMO, DESCRIPCION_MAXIMA
        ).agregar_especialidad()

        assert resultado == "Especialidad agregada exitosamente."
        assert cursor.execute.call_args_list[-1].args == (
            "CALL Crear_especialidad(%s, %s)",
            (NOMBRE_MAXIMO, DESCRIPCION_MAXIMA),
        )
        db.commit.assert_called_once()

    @pytest.mark.parametrize(
        "nombre, descripcion, esperado",
        [
            pytest.param(
                "",
                DESCRIPCION_MINIMA,
                "El campo Nombre de la especialidad no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                "Es",
                DESCRIPCION_MINIMA,
                "El campo Nombre de la especialidad debe tener al menos 3 caracteres.",
                id="nombre-demasiado-corto",
            ),
            pytest.param(
                "E" * 31,
                DESCRIPCION_MINIMA,
                "El campo Nombre de la especialidad no puede tener más de 30 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                "Cel #1",
                DESCRIPCION_MINIMA,
                "El campo Nombre de la especialidad solo puede contener letras, acentos y espacios.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                NOMBRE_MINIMO,
                "",
                "El campo Descripción de la especialidad no puede estar vacío.",
                id="descripcion-vacia",
            ),
            pytest.param(
                NOMBRE_MINIMO,
                "At",
                "El campo Descripción de la especialidad debe tener al menos 3 caracteres.",
                id="descripcion-demasiado-corta",
            ),
            pytest.param(
                NOMBRE_MINIMO,
                "D" * 251,
                "El campo Descripción de la especialidad no puede tener más de 250 caracteres.",
                id="descripcion-demasiado-larga",
            ),
            pytest.param(
                NOMBRE_MINIMO,
                "@#$%",
                "El campo Descripción de la especialidad solo puede contener letras, números, acentos y espacios.",
                id="descripcion-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(self, conexion_falsa, nombre, descripcion, esperado):
        db, cursor = conexion_falsa

        resultado = Especialidad("", nombre, descripcion).agregar_especialidad()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_especialidad_duplicada(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_MAXIMO,)  # ya existe ese nombre

        resultado = Especialidad("", "Celulares", DESCRIPCION_MINIMA).agregar_especialidad()

        assert resultado == "La especialidad 'Celulares' ya existe."
        sin_sentencia(cursor, "CALL")
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Especialidad(
            "", NOMBRE_MINIMO, DESCRIPCION_MINIMA
        ).agregar_especialidad()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        # 1ª llamada: consulta de duplicado; 2ª: el CALL que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = Especialidad(
            "", NOMBRE_MINIMO, DESCRIPCION_MINIMA
        ).agregar_especialidad()

        assert resultado == "Error al agregar especialidad."
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestEliminarEspecialidad:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)  # la especialidad sí existe

        resultado = Especialidad(ID_MAXIMO).eliminar_especialidad()

        assert resultado == "Especialidad eliminada exitosamente."
        assert ultima_sentencia(cursor) == (
            "DELETE FROM Especialidad WHERE ID_especialidad = %s"
        )
        assert cursor.execute.call_args_list[-1].args == (
            "DELETE FROM Especialidad WHERE ID_especialidad = %s",
            (ID_MAXIMO,),
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 2 operaciones (verificar existencia + DELETE)
        cierra_recursos(db, cursor)

    def test_id_minimo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        resultado = Especialidad(ID_MINIMO).eliminar_especialidad()

        assert resultado == "Especialidad eliminada exitosamente."
        assert cursor.execute.call_args_list[-1].args == (
            "DELETE FROM Especialidad WHERE ID_especialidad = %s",
            (ID_MINIMO,),
        )

    def test_id_maximo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert Especialidad(ID_MAXIMO).eliminar_especialidad() == (
            "Especialidad eliminada exitosamente."
        )

    @pytest.mark.parametrize(
        "id_especialidad, esperado",
        [
            pytest.param(
                "",
                "El campo ID de la especialidad no puede estar vacío.",
                id="id-vacio",
            ),
            pytest.param(
                "1234567",
                "El campo ID de la especialidad debe tener al menos 9 caracteres.",
                id="id-demasiado-corto",
            ),
            pytest.param(
                "12345678901",
                "El campo ID de la especialidad no puede tener más de 10 caracteres.",
                id="id-demasiado-largo",
            ),
            pytest.param(
                # Nota: un id de solo letras SÍ pasa validar_texto_numero
                # (permite letras), por eso usamos un carácter especial.
                "12345678#",
                "El campo ID de la especialidad solo puede contener letras, números, acentos y espacios.",
                id="id-caracteres-invalidos",
            ),
        ],
    )
    def test_id_invalido_no_tocan_la_bd(self, conexion_falsa, id_especialidad, esperado):
        db, cursor = conexion_falsa

        resultado = Especialidad(id_especialidad).eliminar_especialidad()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_especialidad_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Especialidad(ID_MAXIMO).eliminar_especialidad()

        assert resultado == f"La especialidad con identificador {ID_MAXIMO} no existe."
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Especialidad(ID_MAXIMO).eliminar_especialidad()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)
        # 1ª llamada: consulta de existencia; 2ª: el DELETE que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = Especialidad(ID_MAXIMO).eliminar_especialidad()

        assert resultado == (
            "Error al eliminar especialidad. Verifica que no esté en uso por empleados."
        )
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_error_clave_foranea_errno_1451(self, conexion_falsa):
        # errno 1451: la especialidad está referenciada por empleados (Capacitacion)
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)
        cursor.execute.side_effect = [None, ErrorConErrno(1451)]

        resultado = Especialidad(ID_MAXIMO).eliminar_especialidad()

        assert resultado == (
            f"No se puede eliminar la especialidad con ID {ID_MAXIMO} "
            "porque está en uso por empleados."
        )
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestActualizarEspecialidad:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        # 1ª consulta (verificar id): existe; 2ª (nombre): es la misma especialidad
        cursor.fetchone.side_effect = [(1,), (ID_MAXIMO,)]

        resultado = Especialidad(
            ID_MAXIMO, "Celulares", "Repara teléfonos"
        ).actualizar_especialidad()

        assert resultado == "Especialidad actualizada exitosamente."
        assert "UPDATE Especialidad" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (
            "Celulares",
            "Repara teléfonos",
            ID_MAXIMO,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 3 operaciones (verificar, consultar nombre, UPDATE)
        cierra_recursos(db, cursor)

    def test_valores_minimos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (ID_MAXIMO,)]

        resultado = Especialidad(
            ID_MAXIMO, NOMBRE_MINIMO, DESCRIPCION_MINIMA
        ).actualizar_especialidad()

        assert resultado == "Especialidad actualizada exitosamente."
        db.commit.assert_called_once()

    def test_valores_maximos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (ID_MAXIMO,)]

        resultado = Especialidad(
            ID_MAXIMO, NOMBRE_MAXIMO, DESCRIPCION_MAXIMA
        ).actualizar_especialidad()

        assert resultado == "Especialidad actualizada exitosamente."
        assert cursor.execute.call_args.args[1] == (
            NOMBRE_MAXIMO,
            DESCRIPCION_MAXIMA,
            ID_MAXIMO,
        )
        db.commit.assert_called_once()

    @pytest.mark.parametrize(
        "id_especialidad, nombre, descripcion, esperado",
        [
            pytest.param(
                "",
                "Celulares",
                "Repara",
                "El campo ID de la especialidad no puede estar vacío.",
                id="id-vacio",
            ),
            pytest.param(
                "1234567",
                "Celulares",
                "Repara",
                "El campo ID de la especialidad debe tener al menos 9 caracteres.",
                id="id-demasiado-corto",
            ),
            pytest.param(
                "12345678901",
                "Celulares",
                "Repara",
                "El campo ID de la especialidad no puede tener más de 10 caracteres.",
                id="id-demasiado-largo",
            ),
            pytest.param(
                # Un id de solo letras pasa validar_texto_numero (permite letras)
                "12345678#",
                "Celulares",
                "Repara",
                "El campo ID de la especialidad solo puede contener letras, números, acentos y espacios.",
                id="id-caracteres-invalidos",
            ),
            pytest.param(
                ID_MAXIMO,
                "",
                "Repara",
                "El campo Nombre de la especialidad no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                ID_MAXIMO,
                "Ce",
                "Repara",
                "El campo Nombre de la especialidad debe tener al menos 3 caracteres.",
                id="nombre-demasiado-corto",
            ),
            pytest.param(
                ID_MAXIMO,
                "E" * 31,
                "Repara",
                "El campo Nombre de la especialidad no puede tener más de 30 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                ID_MAXIMO,
                "Cel #1",
                "Repara",
                "El campo Nombre de la especialidad solo puede contener letras, acentos y espacios.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                ID_MAXIMO,
                "Celulares",
                "",
                "El campo Descripción de la especialidad no puede estar vacío.",
                id="descripcion-vacia",
            ),
            pytest.param(
                ID_MAXIMO,
                "Celulares",
                "Re",
                "El campo Descripción de la especialidad debe tener al menos 3 caracteres.",
                id="descripcion-demasiado-corta",
            ),
            pytest.param(
                ID_MAXIMO,
                "Celulares",
                "D" * 251,
                "El campo Descripción de la especialidad no puede tener más de 250 caracteres.",
                id="descripcion-demasiado-larga",
            ),
            pytest.param(
                ID_MAXIMO,
                "Celulares",
                "@#$%",
                "El campo Descripción de la especialidad solo puede contener letras, números, acentos y espacios.",
                id="descripcion-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(
        self, conexion_falsa, id_especialidad, nombre, descripcion, esperado
    ):
        db, cursor = conexion_falsa

        resultado = Especialidad(
            id_especialidad, nombre, descripcion
        ).actualizar_especialidad()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_especialidad_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Especialidad(
            ID_MAXIMO, "Celulares", "Repara"
        ).actualizar_especialidad()

        assert resultado == (
            f"La especialidad con identificador {ID_MAXIMO} no existe."
        )
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    def test_nombre_duplicado_de_otra_especialidad(self, conexion_falsa):
        db, cursor = conexion_falsa
        # 1ª consulta (verificar id): existe; 2ª (nombre): pertenece a otra
        cursor.fetchone.side_effect = [(1,), ("999999999",)]

        resultado = Especialidad(
            ID_MAXIMO, "Celulares", DESCRIPCION_MINIMA
        ).actualizar_especialidad()

        assert resultado == "La especialidad 'Celulares' ya existe."
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    def test_mismo_nombre_de_la_misma_especialidad_se_permite(self, conexion_falsa):
        db, cursor = conexion_falsa
        # 2ª consulta devuelve el mismo id: no hay duplicado ajeno
        cursor.fetchone.side_effect = [(1,), (ID_MAXIMO,)]

        resultado = Especialidad(
            ID_MAXIMO, NOMBRE_MINIMO, DESCRIPCION_MINIMA
        ).actualizar_especialidad()

        assert resultado == "Especialidad actualizada exitosamente."
        db.commit.assert_called_once()

    def test_conexion_caida(self, conexion_caída):
        resultado = Especialidad(
            ID_MAXIMO, "Celulares", "Repara"
        ).actualizar_especialidad()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (ID_MAXIMO,)]
        # 1ª: existencia; 2ª: consulta de nombre; 3ª: el UPDATE que falla
        cursor.execute.side_effect = [None, None, Exception("fallo simulado")]

        resultado = Especialidad(
            ID_MAXIMO, "Celulares", "Repara"
        ).actualizar_especialidad()

        assert resultado == "Error al actualizar especialidad."
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestVerificarEspecialidadPorId:

    def test_especialidad_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert Especialidad(ID_MAXIMO).verificar_especialidad_por_id() is True

        assert ultima_sentencia(cursor) == (
            "SELECT 1 FROM Especialidad WHERE ID_especialidad = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == (ID_MAXIMO,)

    def test_especialidad_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Especialidad(ID_MAXIMO).verificar_especialidad_por_id() is False

    def test_conexion_caida(self, conexion_caída):
        assert Especialidad(ID_MAXIMO).verificar_especialidad_por_id() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Especialidad(ID_MAXIMO).verificar_especialidad_por_id()

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Especialidad(ID_MAXIMO).verificar_especialidad_por_id()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerEspecialidadPorId:

    def test_especialidad_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {
            "id": "1",
            "nombre": "Celulares",
            "descripcion": "Reparación de móviles",
        }
        cursor.fetchone.return_value = esperado

        # Ojo: este método NO hace strip() del id y usa cursor diccionario
        assert Especialidad(ID_MAXIMO).obtener_especialidad_por_id() == esperado
        assert "FROM Especialidad" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_MAXIMO,)

    def test_especialidad_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Especialidad(ID_MAXIMO).obtener_especialidad_por_id() is None

    def test_conexion_caida(self, conexion_caída):
        assert Especialidad(ID_MAXIMO).obtener_especialidad_por_id() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": "1"}

        Especialidad(ID_MAXIMO).obtener_especialidad_por_id()

        cursor.close.assert_called_once()
        db.close.assert_called_once()


class TestObtenerIdPorNombre:

    def test_especialidad_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_MAXIMO,)

        resultado = Especialidad(nombre_especialidad="Celulares").obtener_id_por_nombre()

        assert resultado == ID_MAXIMO
        assert "SELECT ID_especialidad FROM Especialidad" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == ("Celulares",)

    def test_especialidad_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Especialidad(
            nombre_especialidad="Inexistente"
        ).obtener_id_por_nombre()

        assert resultado is None

    def test_conexion_caida(self, conexion_caída):
        assert Especialidad(nombre_especialidad="Celulares").obtener_id_por_nombre() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_MAXIMO,)

        Especialidad(nombre_especialidad="Celulares").obtener_id_por_nombre()

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_MAXIMO,)

        Especialidad(nombre_especialidad="Celulares").obtener_id_por_nombre()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()
