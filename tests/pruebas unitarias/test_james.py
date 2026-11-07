"""Pruebas unitarias de la clase James (app.models.james).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.
"""
import pytest

from app.models.james import James
from helpers import cierra_recursos, sin_sentencia

MENSAJE_ERROR_CONEXION = "Error al conectar a la base de datos."

# ==================== Datos de frontera ====================
ID_ORDEN = "OS-0001"
ID_ORDEN_INEXISTENTE = "OS-9999"


class TestConsultarInformacionOrden:

    def test_orden_sin_interacciones(self, conexion_falsa):
        db, cursor = conexion_falsa
        orden = {
            "id_orden": ID_ORDEN,
            "estado_orden": "En reparación",
            "descripcion_reparacion": "Cambio de pantalla",
            "costo_reparacion": 50,
        }
        cursor.fetchone.return_value = orden
        cursor.fetchall.return_value = []

        resultado = James(ID_ORDEN).consultar_informacion_orden()

        assert resultado == {
            "orden": orden,
            "interacciones": [],
            "resumen": {
                "total_interacciones": 0,
                "total_tests": 0,
                "estado_actual": "En reparación",
            },
        }
        assert cursor.execute.call_args_list[0].args[1] == (ID_ORDEN,)
        assert cursor.execute.call_args_list[1].args[1] == (ID_ORDEN,)

    def test_agrupa_interacciones_y_tests(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {
            "id_orden": ID_ORDEN,
            "estado_orden": "Listo",
        }
        cursor.fetchall.return_value = [
            {
                "id_interaccion": 1,
                "accion_interaccion": "Diagnóstico",
                "id_empleado_interaccion": "E1",
                "id_test": 10,
                "numero_test": 1,
                "nombre_test": "Pantalla",
                "resultado_test": "OK",
            },
            {
                "id_interaccion": 1,
                "accion_interaccion": "Diagnóstico",
                "id_empleado_interaccion": "E1",
                "id_test": 11,
                "numero_test": 2,
                "nombre_test": "Batería",
                "resultado_test": "Falla",
            },
            {
                "id_interaccion": 2,
                "accion_interaccion": "Reparación",
                "id_empleado_interaccion": "E2",
                "id_test": None,
                "numero_test": None,
                "nombre_test": None,
                "resultado_test": None,
            },
        ]

        resultado = James(ID_ORDEN).consultar_informacion_orden()

        assert len(resultado["interacciones"]) == 2
        primera = resultado["interacciones"][0]
        assert primera["id_interaccion"] == 1
        assert primera["accion_interaccion"] == "Diagnóstico"
        assert primera["id_empleado_interaccion"] == "E1"
        assert [test["id_test"] for test in primera["tests"]] == [10, 11]
        assert primera["tests"][1] == {
            "id_test": 11,
            "numero_test": 2,
            "nombre_test": "Batería",
            "resultado_test": "Falla",
        }
        segunda = resultado["interacciones"][1]
        assert segunda["id_interaccion"] == 2
        assert segunda["tests"] == []
        assert resultado["resumen"] == {
            "total_interacciones": 2,
            "total_tests": 2,
            "estado_actual": "Listo",
        }

    @pytest.mark.parametrize(
        "id_test",
        [
            pytest.param(None, id="none"),
            pytest.param(0, id="cero"),
            pytest.param("", id="cadena-vacia"),
        ],
    )
    def test_test_sin_id_no_se_agrega(self, conexion_falsa, id_test):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {
            "id_orden": ID_ORDEN,
            "estado_orden": "En proceso",
        }
        cursor.fetchall.return_value = [
            {
                "id_interaccion": 1,
                "accion_interaccion": "Diagnóstico",
                "id_empleado_interaccion": "E1",
                "id_test": id_test,
                "numero_test": 1,
                "nombre_test": "Pantalla",
                "resultado_test": "OK",
            }
        ]

        resultado = James(ID_ORDEN).consultar_informacion_orden()

        assert resultado["interacciones"][0]["tests"] == []
        assert resultado["resumen"]["total_tests"] == 0

    def test_orden_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = James(ID_ORDEN_INEXISTENTE).consultar_informacion_orden()

        assert resultado == (
            f"No se encontró ninguna orden con ID '{ID_ORDEN_INEXISTENTE}'."
        )
        # Solo se ejecuta la consulta principal
        assert cursor.execute.call_count == 1
        cursor.fetchall.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = James(ID_ORDEN).consultar_informacion_orden()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_en_consulta_principal(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = James(ID_ORDEN).consultar_informacion_orden()

        assert resultado == "Error al consultar la información: fallo simulado"

    def test_error_en_consulta_de_interacciones(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {
            "id_orden": ID_ORDEN,
            "estado_orden": "En proceso",
        }
        cursor.execute.side_effect = [None, Exception("fallo en interacciones")]

        resultado = James(ID_ORDEN).consultar_informacion_orden()

        assert resultado == (
            "Error al consultar la información: fallo en interacciones"
        )

    def test_usa_cursor_de_diccionario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {
            "id_orden": ID_ORDEN,
            "estado_orden": "Listo",
        }
        cursor.fetchall.return_value = []

        James(ID_ORDEN).consultar_informacion_orden()

        db.cursor.assert_called_once_with(dictionary=True)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {
            "id_orden": ID_ORDEN,
            "estado_orden": "Listo",
        }
        cursor.fetchall.return_value = []

        James(ID_ORDEN).consultar_informacion_orden()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestConsultarTecnicosConEspecialidadesYOrdenes:

    def test_agrupa_tecnicos_y_ordena_por_ordenes(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "id_empleado": "E1",
                "nombre_cargo": "Técnico",
                "nombre_especialidad": "Celulares",
                "descripcion_especialidad": "Móviles",
                "nivel_capacitacion": "Alto",
                "total_ordenes_asignadas": 2,
            },
            {
                "id_empleado": "E2",
                "nombre_cargo": "Técnico",
                "nombre_especialidad": "Computación",
                "descripcion_especialidad": "Laptops",
                "nivel_capacitacion": "Medio",
                "total_ordenes_asignadas": 5,
            },
            {
                "id_empleado": "E1",
                "nombre_cargo": "Técnico",
                "nombre_especialidad": "Computación",
                "descripcion_especialidad": "Laptops",
                "nivel_capacitacion": "Bajo",
                "total_ordenes_asignadas": 2,
            },
        ]

        resultado = James().consultar_tecnicos_con_especialidades_y_ordenes()

        assert resultado["total_tecnicos"] == 2
        # Ordenados de mayor a menor por órdenes asignadas
        assert [t["id_empleado"] for t in resultado["tecnicos"]] == ["E2", "E1"]
        tecnico_e1 = resultado["tecnicos"][1]
        assert tecnico_e1["cargo"] == "Técnico"
        assert tecnico_e1["total_ordenes_asignadas"] == 2
        assert len(tecnico_e1["especialidades"]) == 2
        assert tecnico_e1["especialidades"][0] == {
            "nombre_especialidad": "Celulares",
            "descripcion_especialidad": "Móviles",
            "nivel_capacitacion": "Alto",
        }
        assert tecnico_e1["especialidades"][1]["nombre_especialidad"] == "Computación"

    def test_filtra_solo_cargos_de_tecnico(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        James().consultar_tecnicos_con_especialidades_y_ordenes()

        sentencia = cursor.execute.call_args.args[0]
        assert "c.Nombre_cargo LIKE '%Técnico%'" in sentencia
        assert "ORDER BY e.ID_empleado, esp.Nombre_especialidad" in sentencia

    @pytest.mark.parametrize(
        "filas",
        [
            pytest.param([], id="lista-vacia"),
            pytest.param(None, id="fetchall-none"),
        ],
    )
    def test_sin_tecnicos_registrados(self, conexion_falsa, filas):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = filas

        resultado = James().consultar_tecnicos_con_especialidades_y_ordenes()

        assert resultado == "No se encontraron técnicos registrados."

    def test_conexion_caida(self, conexion_caída):
        resultado = James().consultar_tecnicos_con_especialidades_y_ordenes()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_devuelve_mensaje(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = James().consultar_tecnicos_con_especialidades_y_ordenes()

        assert resultado == "Error al consultar técnicos: fallo simulado"

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        James().consultar_tecnicos_con_especialidades_y_ordenes()

        cierra_recursos(db, cursor)

    def test_cierra_recursos_aunque_falle(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        James().consultar_tecnicos_con_especialidades_y_ordenes()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        James().consultar_tecnicos_con_especialidades_y_ordenes()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()
