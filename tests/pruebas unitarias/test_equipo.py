"""Pruebas unitarias de la clase Equipo (app.models.equipo).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.
"""
import pytest

from app.models.equipo import Equipo
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

MENSAJE_ERROR_CONEXION = "Error al conectar con la base de datos."

# ==================== Datos de frontera ====================
ID_EQUIPO = "356789012345678"  # IMEI de 15 dígitos
ID_PRODUCTO = "PROD-01"

ID_MAXIMO = "1" * 16  # 16 caracteres (límite real del código)

COLOR_MAXIMO = "C" * 30  # 30 caracteres (máximo al registrar)
CAPACIDAD_MAXIMA_REGISTRO = "128GB_"  # 6 caracteres (máximo al registrar)
CAPACIDAD_MAXIMA_ACTUALIZACION = "C" * 20  # 20 caracteres (máximo al actualizar)
CLAVE_VALIDA = "1234"
PATRON_MAXIMO = "1-2-3-4-5-6-7-8-9"  # 17 caracteres (máximo)


def llamada_con(cursor, fragmento):
    """Devuelve la llamada a execute cuya sentencia contiene el fragmento."""
    return next(
        llamada
        for llamada in cursor.execute.call_args_list
        if fragmento in llamada.args[0]
    )


class TestConsultarEquipoPorId:

    def test_equipo_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {
            "ID_equipo": ID_EQUIPO,
            "ID_producto": ID_PRODUCTO,
            "Color": "Negro",
            "Capacidad": "128GB",
            "Nombre_producto": "iPhone 13",
        }
        cursor.fetchone.return_value = esperado

        resultado = Equipo(ID_equipo=ID_EQUIPO).Consultar_equipo_por_id()

        assert resultado == esperado
        assert "FROM Equipo" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_EQUIPO,)
        db.cursor.assert_called_once_with(dictionary=True)

    def test_equipo_no_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Equipo(ID_equipo=ID_EQUIPO).Consultar_equipo_por_id() is None

    @pytest.mark.parametrize(
        "id_equipo",
        [
            pytest.param(None, id="none"),
            pytest.param("", id="vacio"),
        ],
    )
    def test_sin_id_no_toca_la_bd(self, conexion_falsa, id_equipo):
        db, cursor = conexion_falsa

        assert Equipo(ID_equipo=id_equipo).Consultar_equipo_por_id() is None
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert Equipo(ID_equipo=ID_EQUIPO).Consultar_equipo_por_id() is None

    def test_error_de_bd_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Equipo(ID_equipo=ID_EQUIPO).Consultar_equipo_por_id() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        Equipo(ID_equipo=ID_EQUIPO).Consultar_equipo_por_id()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        Equipo(ID_equipo=ID_EQUIPO).Consultar_equipo_por_id()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestRegistrarEquipo:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None  # el equipo aún no existe

        resultado = Equipo(
            ID_equipo=ID_EQUIPO, ID_producto=ID_PRODUCTO
        ).registrar_equipo()

        assert resultado == f"Equipo {ID_EQUIPO} registrado exitosamente."
        assert llamada_con(cursor, "INSERT INTO Equipo").args[1] == (
            ID_EQUIPO,
            ID_PRODUCTO,
            None,
            None,
            None,
            None,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_datos_completos_convierte_clave_a_entero(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Equipo(
            ID_equipo=ID_EQUIPO,
            ID_producto=ID_PRODUCTO,
            Color="Negro",
            Capacidad="128GB",
            Clave=CLAVE_VALIDA,
            Patron=PATRON_MAXIMO,
        ).registrar_equipo()

        assert resultado == f"Equipo {ID_EQUIPO} registrado exitosamente."
        assert llamada_con(cursor, "INSERT INTO Equipo").args[1] == (
            ID_EQUIPO,
            ID_PRODUCTO,
            "Negro",
            "128GB",
            1234,
            PATRON_MAXIMO,
        )
        db.commit.assert_called_once()

    def test_valores_minimos_y_maximos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Equipo(
            ID_equipo=ID_MAXIMO,
            ID_producto="P",
            Color=COLOR_MAXIMO,
            Capacidad=CAPACIDAD_MAXIMA_REGISTRO,
            Patron=PATRON_MAXIMO,
        ).registrar_equipo()

        assert resultado == f"Equipo {ID_MAXIMO} registrado exitosamente."
        assert llamada_con(cursor, "INSERT INTO Equipo").args[1] == (
            ID_MAXIMO,
            "P",
            COLOR_MAXIMO,
            CAPACIDAD_MAXIMA_REGISTRO,
            None,
            PATRON_MAXIMO,
        )
        db.commit.assert_called_once()

    def test_campos_opcionales_vacios_se_guardan_como_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        Equipo(
            ID_equipo=ID_EQUIPO,
            ID_producto=ID_PRODUCTO,
            Color="",
            Capacidad="",
            Clave="",
            Patron="",
        ).registrar_equipo()

        assert llamada_con(cursor, "INSERT INTO Equipo").args[1] == (
            ID_EQUIPO,
            ID_PRODUCTO,
            None,
            None,
            None,
            None,
        )

    def test_equipo_duplicado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_EQUIPO,)  # ya existe

        resultado = Equipo(
            ID_equipo=ID_EQUIPO, ID_producto=ID_PRODUCTO
        ).registrar_equipo()

        assert resultado == f"El equipo '{ID_EQUIPO}' ya existe."
        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "id_equipo, id_producto, esperado",
        [
            pytest.param(
                None,
                ID_PRODUCTO,
                "El ID del equipo es obligatorio.",
                id="equipo-vacio",
            ),
            pytest.param(
                "",
                ID_PRODUCTO,
                "El ID del equipo es obligatorio.",
                id="equipo-cadena-vacia",
            ),
            pytest.param(
                ID_EQUIPO,
                None,
                "El ID del producto es obligatorio.",
                id="producto-vacio",
            ),
            pytest.param(
                "1" * 17,
                ID_PRODUCTO,
                "El ID del equipo no puede tener más de 15 caracteres.",
                id="equipo-demasiado-largo",
            ),
        ],
    )
    def test_validaciones_previas_no_tocan_la_bd(
        self, conexion_falsa, id_equipo, id_producto, esperado
    ):
        db, cursor = conexion_falsa

        resultado = Equipo(
            ID_equipo=id_equipo, ID_producto=id_producto
        ).registrar_equipo()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "campo, esperado",
        [
            pytest.param(
                {"Color": "C" * 31},
                "El color no puede tener más de 30 caracteres.",
                id="color-demasiado-largo",
            ),
            pytest.param(
                {"Capacidad": "C" * 7},
                "La capacidad no puede tener más de 6 caracteres.",
                id="capacidad-demasiado-larga",
            ),
            pytest.param(
                {"Clave": "12a"},
                "La clave debe ser un número entero válido.",
                id="clave-no-numerica",
            ),
            pytest.param(
                {"Patron": "1" * 18},
                "El patrón no puede tener más de 17 caracteres.",
                id="patron-demasiado-largo",
            ),
        ],
    )
    def test_validaciones_posteriores_no_insertan(
        self, conexion_falsa, campo, esperado
    ):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Equipo(
            ID_equipo=ID_EQUIPO, ID_producto=ID_PRODUCTO, **campo
        ).registrar_equipo()

        assert resultado == esperado
        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Equipo(
            ID_equipo=ID_EQUIPO, ID_producto=ID_PRODUCTO
        ).registrar_equipo()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        # 1ª llamada: SELECT de duplicado; 2ª: el INSERT que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = Equipo(
            ID_equipo=ID_EQUIPO, ID_producto=ID_PRODUCTO
        ).registrar_equipo()

        assert resultado == "Error al registrar el equipo: fallo simulado"
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestActualizarEquipo:

    def test_datos_validos_todos_los_campos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_EQUIPO,)  # el equipo existe

        resultado = Equipo(
            ID_equipo=ID_EQUIPO,
            ID_producto=ID_PRODUCTO,
            Color="Negro",
            Capacidad="128GB",
            Clave=CLAVE_VALIDA,
            Patron=PATRON_MAXIMO,
        ).actualizar_equipo()

        assert resultado == f"Equipo {ID_EQUIPO} actualizado correctamente."
        sentencia = ultima_sentencia(cursor)
        assert "UPDATE Equipo SET" in sentencia
        for campo in ("ID_producto = %s", "Color = %s", "Capacidad = %s",
                      "Clave = %s", "Patron = %s"):
            assert campo in sentencia
        assert cursor.execute.call_args.args[1] == [
            ID_PRODUCTO,
            "Negro",
            "128GB",
            1234,
            PATRON_MAXIMO,
            ID_EQUIPO,
        ]
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_actualizacion_parcial_solo_color(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_EQUIPO,)

        resultado = Equipo(
            ID_equipo=ID_EQUIPO, Color="Azul"
        ).actualizar_equipo()

        assert resultado == f"Equipo {ID_EQUIPO} actualizado correctamente."
        assert ultima_sentencia(cursor) == (
            "UPDATE Equipo SET Color = %s WHERE ID_equipo = %s"
        )
        assert cursor.execute.call_args.args[1] == ["Azul", ID_EQUIPO]

    def test_color_vacio_se_guarda_como_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_EQUIPO,)

        Equipo(ID_equipo=ID_EQUIPO, Color="").actualizar_equipo()

        assert cursor.execute.call_args.args[1] == [None, ID_EQUIPO]

    def test_sin_datos_para_actualizar(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_EQUIPO,)

        resultado = Equipo(ID_equipo=ID_EQUIPO).actualizar_equipo()

        assert resultado == "No hay datos para actualizar."
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    def test_equipo_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Equipo(
            ID_equipo=ID_EQUIPO, Color="Azul"
        ).actualizar_equipo()

        assert resultado == f"No se encontró el equipo {ID_EQUIPO}."
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "campo, esperado",
        [
            pytest.param(
                {"Color": "C" * 31},
                "El color no puede tener más de 30 caracteres.",
                id="color-demasiado-largo",
            ),
            pytest.param(
                {"Capacidad": "C" * 21},
                "La capacidad no puede tener más de 20 caracteres.",
                id="capacidad-demasiado-larga",
            ),
            pytest.param(
                {"Clave": "abc"},
                "La clave debe ser un número entero válido.",
                id="clave-no-numerica",
            ),
            pytest.param(
                {"Patron": "1" * 18},
                "El patrón no puede tener más de 17 caracteres.",
                id="patron-demasiado-largo",
            ),
        ],
    )
    def test_datos_invalidos_no_actualizan(self, conexion_falsa, campo, esperado):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_EQUIPO,)

        resultado = Equipo(ID_equipo=ID_EQUIPO, **campo).actualizar_equipo()

        assert resultado == esperado
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    def test_valor_maximo_de_capacidad_permitido(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_EQUIPO,)

        resultado = Equipo(
            ID_equipo=ID_EQUIPO,
            Capacidad=CAPACIDAD_MAXIMA_ACTUALIZACION,
        ).actualizar_equipo()

        assert resultado == f"Equipo {ID_EQUIPO} actualizado correctamente."
        assert cursor.execute.call_args.args[1] == [
            CAPACIDAD_MAXIMA_ACTUALIZACION,
            ID_EQUIPO,
        ]

    def test_sin_id_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Equipo(ID_equipo="").actualizar_equipo()

        assert resultado == "El ID del equipo es obligatorio."
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Equipo(
            ID_equipo=ID_EQUIPO, Color="Azul"
        ).actualizar_equipo()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_EQUIPO,)
        # 1ª llamada: SELECT de existencia; 2ª: el UPDATE que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = Equipo(
            ID_equipo=ID_EQUIPO, Color="Azul"
        ).actualizar_equipo()

        assert resultado == "Error al actualizar el equipo: fallo simulado"
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestEliminarEquipo:

    def test_eliminar_correctamente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(ID_EQUIPO,), (0,), (0,)]

        resultado = Equipo(ID_equipo=ID_EQUIPO).eliminar_equipo()

        assert resultado == f"Equipo {ID_EQUIPO} eliminado correctamente."
        assert llamada_con(cursor, "DELETE FROM Equipo").args[1] == (ID_EQUIPO,)
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_equipo_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Equipo(ID_equipo=ID_EQUIPO).eliminar_equipo()

        assert resultado == f"No se encontró el equipo {ID_EQUIPO}."
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()

    def test_equipo_con_trade_ins_asociados(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(ID_EQUIPO,), (2,)]

        resultado = Equipo(ID_equipo=ID_EQUIPO).eliminar_equipo()

        assert resultado == (
            f"No se puede eliminar el equipo {ID_EQUIPO} "
            "porque tiene trade-ins asociados."
        )
        sin_sentencia(cursor, "DELETE")
        assert cursor.execute.call_count == 2
        db.commit.assert_not_called()

    def test_equipo_con_ordenes_de_servicio_asociadas(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(ID_EQUIPO,), (0,), (1,)]

        resultado = Equipo(ID_equipo=ID_EQUIPO).eliminar_equipo()

        assert resultado == (
            f"No se puede eliminar el equipo {ID_EQUIPO} "
            "porque tiene órdenes de servicio asociadas."
        )
        sin_sentencia(cursor, "DELETE")
        assert cursor.execute.call_count == 3
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "id_equipo",
        [
            pytest.param(None, id="none"),
            pytest.param("", id="vacio"),
        ],
    )
    def test_sin_id_no_toca_la_bd(self, conexion_falsa, id_equipo):
        db, cursor = conexion_falsa

        resultado = Equipo(ID_equipo=id_equipo).eliminar_equipo()

        assert resultado == "El ID del equipo es obligatorio."
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Equipo(ID_equipo=ID_EQUIPO).eliminar_equipo()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(ID_EQUIPO,), (0,), (0,)]
        # 1ª: existencia; 2ª: trade-ins; 3ª: órdenes; 4ª: DELETE que falla
        cursor.execute.side_effect = [None, None, None, Exception("fallo simulado")]

        resultado = Equipo(ID_equipo=ID_EQUIPO).eliminar_equipo()

        assert resultado == "Error al eliminar el equipo: fallo simulado"
        db.rollback.assert_called_once()
        db.commit.assert_not_called()
