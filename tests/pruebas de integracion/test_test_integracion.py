"""Pruebas de integración de la clase Tests (revisión técnica) contra MySQL real.

Nota: el método buscar_test() consulta tablas legadas (revision_orden, orden_e)
que no existen en el esquema actual, por lo que no se prueba aquí.
"""
import pytest

from app.models.test import Tests
from app.models.database import conectar
from seed_helpers import (
    crear_cliente_temporal,
    crear_producto_temporal,
    eliminar_cliente_temporal,
    eliminar_producto_temporal,
)

EMPLEADO_ADMIN = "12345678"
CLASE_TELEFONO = "1"
MARCA_SEED = "3"

# Datos fijos por prueba (rangos reservados para este módulo).
CEDULA_CLIENTE = "83000001"
IMEI_EQUIPO = "862000000000001"


# ==================== HELPERS LOCALES (solo para este módulo) ====================


def _crear_equipo(
    id_producto: str, imei: str, color: str = "Negro", capacidad: str = "128GB"
) -> str:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO Equipo (ID_equipo, ID_producto, Color, Capacidad, Clave, Patron) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (imei, id_producto, color, capacidad, 1234, "1-2-3-4"),
        )
        db.commit()
        return imei
    finally:
        cursor.close()
        db.close()


def _eliminar_equipo(imei: str) -> None:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Equipo WHERE ID_equipo = %s", (imei,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def _siguiente_id_orden_servicio(cursor) -> str:
    cursor.execute("SELECT MAX(ID_orden_servicio) FROM Orden_servicio")
    ultimo = cursor.fetchone()[0]
    if not ultimo or not str(ultimo).startswith("OS"):
        numero = 0
    else:
        try:
            numero = int(str(ultimo)[2:])
        except ValueError:
            numero = 0
    return f"OS{str(numero + 1).zfill(7)}"


def _siguiente_id_interaccion(cursor) -> str:
    cursor.execute("SELECT MAX(ID_interaccion) FROM Interaccion")
    ultimo = cursor.fetchone()[0]
    if not ultimo or not str(ultimo).startswith("INT"):
        numero = 0
    else:
        try:
            numero = int(str(ultimo)[3:])
        except ValueError:
            numero = 0
    return f"INT{str(numero + 1).zfill(6)}"


def _crear_orden_servicio(
    id_cliente: str,
    id_equipo: str,
    descripcion: str = "Pantalla rota de prueba",
    estado: str = "Pendiente",
) -> str:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        id_orden = _siguiente_id_orden_servicio(cursor)
        cursor.execute(
            "INSERT INTO Orden_servicio (ID_orden_servicio, ID_equipo, ID_cliente, "
            "Estado_orden_servicio, Descripcion_reparacion, Nota_orden_servicio, Fecha_entrada) "
            "VALUES (%s, %s, %s, %s, %s, %s, NOW())",
            (id_orden, id_equipo, id_cliente, estado, descripcion, None),
        )
        cursor.execute(
            "INSERT INTO Interaccion (ID_interaccion, ID_orden_servicio, ID_empleado, Accion) "
            "VALUES (%s, %s, %s, %s)",
            (_siguiente_id_interaccion(cursor), id_orden, EMPLEADO_ADMIN, estado),
        )
        db.commit()
        return id_orden
    finally:
        cursor.close()
        db.close()


def _eliminar_orden_servicio(id_orden: str) -> None:
    """Borra tests, interacciones, fotos, repuestos y la orden."""
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE tri FROM Test_realizados_interaccion tri "
            "INNER JOIN Interaccion i ON tri.ID_interaccion = i.ID_interaccion "
            "WHERE i.ID_orden_servicio = %s",
            (id_orden,),
        )
        cursor.execute(
            "DELETE t FROM Test t "
            "INNER JOIN Test_realizados_interaccion tri ON t.ID_test = tri.ID_test "
            "INNER JOIN Interaccion i ON tri.ID_interaccion = i.ID_interaccion "
            "WHERE i.ID_orden_servicio = %s",
            (id_orden,),
        )
        cursor.execute(
            "DELETE ru FROM Repuestos_usados ru WHERE ru.ID_orden_servicio = %s",
            (id_orden,),
        )
        cursor.execute(
            "DELETE FROM Interaccion WHERE ID_orden_servicio = %s", (id_orden,)
        )
        cursor.execute(
            "DELETE FROM Fotos_orden_servicio WHERE ID_orden_servicio = %s",
            (id_orden,),
        )
        cursor.execute(
            "DELETE FROM Orden_servicio WHERE ID_orden_servicio = %s", (id_orden,)
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


@pytest.fixture
def orden_taller():
    """Cliente + producto + equipo + orden de servicio pendiente."""
    id_producto = None
    id_orden = None
    try:
        crear_cliente_temporal(
            CEDULA_CLIENTE, nombre="Cliente", apellido="Revision"
        )
        id_producto = crear_producto_temporal(
            nombre="Prod Integra Revision", clase=CLASE_TELEFONO, marca=MARCA_SEED
        )
        imei = _crear_equipo(id_producto, IMEI_EQUIPO)
        id_orden = _crear_orden_servicio(CEDULA_CLIENTE, imei)
        yield {"cliente_id": CEDULA_CLIENTE, "id_producto": id_producto, "id_orden": id_orden}
    finally:
        if id_orden:
            _eliminar_orden_servicio(id_orden)
        _eliminar_equipo(IMEI_EQUIPO)
        if id_producto:
            eliminar_producto_temporal(id_producto)
        eliminar_cliente_temporal(CEDULA_CLIENTE)


class TestListasTests:

    def test_orden_sin_tests_devuelve_vacio(self, orden_taller):
        info = orden_taller
        assert Tests(ID_orden=info["id_orden"]).listas_tests() == []

    def test_con_tests_registrados(self, orden_taller):
        info = orden_taller
        resultado = Tests(
            ID_orden=info["id_orden"],
            Numero_test=1,
            lista_tests=[{"nombre": "Mica", "resultado": "Funciona"}],
            ID_empleado=int(EMPLEADO_ADMIN),
        ).registrar_revision_test()
        assert resultado == "Revisión técnica y pruebas registradas exitosamente."

        listas = Tests(ID_orden=info["id_orden"]).listas_tests()

        assert listas == [{"Numero_test": 1, "cantidad": 1}]


class TestConsultarTest:

    def test_orden_sin_tests_devuelve_vacio(self, orden_taller):
        info = orden_taller
        assert (
            Tests(ID_orden=info["id_orden"], Numero_test=1).consultar_test() == []
        )

    def test_con_test_registrado(self, orden_taller):
        info = orden_taller
        Tests(
            ID_orden=info["id_orden"],
            Numero_test=2,
            lista_tests=[
                {"nombre": "LCD", "resultado": "Funciona"},
                {"nombre": "Tactil", "resultado": "No funciona"},
            ],
            ID_empleado=int(EMPLEADO_ADMIN),
        ).registrar_revision_test()

        test = Tests(ID_orden=info["id_orden"], Numero_test=2).consultar_test()

        assert {fila["test"] for fila in test} == {"LCD", "Tactil"}
        assert all(
            fila["Resultado_test"] in ("Funciona", "No funciona") for fila in test
        )

    @pytest.mark.parametrize(
        "id_orden, numero_test, esperado",
        [
            pytest.param(
                "",
                1,
                "El campo ID dela orden no puede estar vacío.",
                id="id-orden-vacio",
            ),
            pytest.param(
                "OS 12#",
                1,
                "El campo ID dela orden solo puede contener letras, números, acentos y espacios.",
                id="id-orden-caracteres-invalidos",
            ),
            pytest.param(
                "OS0000001",
                "",
                "El campo Numero de test no puede estar vacío.",
                id="numero-test-vacio",
            ),
            pytest.param(
                "OS0000001",
                "abc",
                "El campo Numero de test solo puede contener números.",
                id="numero-test-no-numerico",
            ),
            pytest.param(
                "OS0000001",
                "1234",
                "El campo Numero de test no puede tener más de 3 dígitos.",
                id="numero-test-demasiado-largo",
            ),
        ],
    )
    def test_datos_invalidos(self, id_orden, numero_test, esperado):
        assert (
            Tests(ID_orden=id_orden, Numero_test=numero_test).consultar_test()
            == esperado
        )


class TestRegistrarRevisionTest:

    def test_datos_validos(self, orden_taller):
        info = orden_taller
        resultado = Tests(
            ID_orden=info["id_orden"],
            Numero_test=1,
            lista_tests=[
                {"nombre": "Botón Power", "resultado": "Funciona"},
                {"nombre": "Mica", "resultado": "No funciona"},
            ],
            ID_empleado=int(EMPLEADO_ADMIN),
        ).registrar_revision_test()

        assert resultado == "Revisión técnica y pruebas registradas exitosamente."

        # Los tests quedan asociados a la orden
        por_orden = Tests().buscar_test_por_orden(info["id_orden"])
        nombres = {fila["Nombre_test"] for fila in por_orden}
        assert nombres == {"Botón Power", "Mica"}

    def test_orden_inexistente(self):
        resultado = Tests(
            ID_orden="OS9999999",
            Numero_test=1,
            lista_tests=[{"nombre": "Mica", "resultado": "Funciona"}],
            ID_empleado=int(EMPLEADO_ADMIN),
        ).registrar_revision_test()

        assert resultado == "Error interno al procesar el registro de las pruebas."

    def test_lista_tests_mal_formada(self, orden_taller):
        info = orden_taller
        resultado = Tests(
            ID_orden=info["id_orden"],
            Numero_test=1,
            # Un set no es serializable a JSON
            lista_tests={"nombre", "resultado"},
            ID_empleado=int(EMPLEADO_ADMIN),
        ).registrar_revision_test()

        assert resultado == "El formato de la lista de pruebas es incorrecto."

    @pytest.mark.parametrize(
        "id_orden, id_empleado, esperado",
        [
            pytest.param(
                "",
                int(EMPLEADO_ADMIN),
                "El campo ID del Cargo no puede estar vacío.",
                id="id-orden-vacio",
            ),
            pytest.param(
                "OS 12#",
                int(EMPLEADO_ADMIN),
                "El campo ID del Cargo solo puede contener letras, números, acentos y espacios.",
                id="id-orden-caracteres-invalidos",
            ),
            pytest.param(
                "OS0000001",
                None,
                "El campo Cédula no puede estar vacío.",
                id="cedula-vacia",
            ),
            pytest.param(
                "OS0000001",
                "12345",
                "El campo Cédula debe tener al menos 6 dígitos.",
                id="cedula-demasiado-corta",
            ),
            pytest.param(
                "OS0000001",
                "1234567890",
                "El campo Cédula no puede tener más de 9 dígitos.",
                id="cedula-demasiado-larga",
            ),
            pytest.param(
                "OS0000001",
                "12345a",
                "El campo Cédula solo puede contener números.",
                id="cedula-no-numerica",
            ),
        ],
    )
    def test_datos_invalidos(self, id_orden, id_empleado, esperado):
        resultado = Tests(
            ID_orden=id_orden,
            Numero_test=1,
            lista_tests=[{"nombre": "Mica", "resultado": "Funciona"}],
            ID_empleado=id_empleado,
        ).registrar_revision_test()

        assert resultado == esperado


class TestRegistrarTestIndividual:
    """El método registrar_test() lo usa el blueprint de órdenes de servicio."""

    def _valores(self) -> tuple:
        componentes = [1] * 9 + [0] * 9
        return (int(EMPLEADO_ADMIN), 1, *componentes, "Equipo revisado")

    def test_registra_componentes_y_observaciones(self, orden_taller):
        info = orden_taller
        assert Tests().registrar_test(self._valores(), info["id_orden"]) is True

        por_orden = Tests().buscar_test_por_orden(info["id_orden"])

        # 18 componentes + 1 observación
        assert len(por_orden) == 19
        power = next(
            (f for f in por_orden if f["Nombre_test"] == "Botón Power"), None
        )
        assert power is not None
        assert power["Observaciones"] == "Funciona"
        assert power["Num_test"] == 1

        observacion = next(
            (f for f in por_orden if f["Nombre_test"] == "Observaciones"), None
        )
        assert observacion is not None
        assert observacion["Observaciones"] == "Equipo revisado"

    def test_componente_no_funciona(self, orden_taller):
        info = orden_taller
        componentes = [0] * 18
        valores = (int(EMPLEADO_ADMIN), 1, *componentes, None)
        assert Tests().registrar_test(valores, info["id_orden"]) is True

        componentes_registrados = Tests().buscar_test_por_orden(info["id_orden"])
        wifi = next(
            (f for f in componentes_registrados if f["Nombre_test"] == "Wifi"), None
        )
        assert wifi is not None
        assert wifi["Observaciones"] == "No funciona"

    def test_sin_tests_para_registrar_devuelve_false(self, orden_taller):
        info = orden_taller
        # Solo empleado y número: sin componentes ni observaciones
        valores = (int(EMPLEADO_ADMIN), 1, None, None)
        assert Tests().registrar_test(valores, info["id_orden"]) is False


class TestObtenerTestPorOrdenYNumero:

    def test_sin_tests_devuelve_vacio(self, orden_taller):
        info = orden_taller
        assert (
            Tests().obtener_test_por_orden_y_numero(info["id_orden"], "1") == []
        )

    def test_devuelve_componentes_del_numero(self, orden_taller):
        info = orden_taller
        Tests(
            ID_orden=info["id_orden"],
            Numero_test=3,
            lista_tests=[
                {"nombre": "Cornetas", "resultado": "Funciona"},
                {"nombre": "Microfono", "resultado": "No funciona"},
            ],
            ID_empleado=int(EMPLEADO_ADMIN),
        ).registrar_revision_test()

        test = Tests().obtener_test_por_orden_y_numero(info["id_orden"], "3")

        assert {fila["Nombre_test"] for fila in test} == {"Cornetas", "Microfono"}
