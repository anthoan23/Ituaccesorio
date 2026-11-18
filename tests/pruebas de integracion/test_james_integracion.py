"""Pruebas de integración de la clase James contra MySQL real.

Solo se prueba la parte de consultas a la BD: el resumen para la IA.
El servicio de Gemini (app/services/james.py) es externo y no se cubre aquí.
"""
import pytest

from app.models.empleados import Empleados
from app.models.especialidades import Especialidad
from app.models.james import James
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
CEDULA_CLIENTE = "84000001"
CEDULA_TECNICO = "84000101"
IMEI_EQUIPO = "863000000000001"


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
        crear_cliente_temporal(CEDULA_CLIENTE, nombre="Cliente", apellido="James")
        id_producto = crear_producto_temporal(
            nombre="Prod Integra James", clase=CLASE_TELEFONO, marca=MARCA_SEED
        )
        imei = _crear_equipo(id_producto, IMEI_EQUIPO, color="Azul", capacidad="256GB")
        id_orden = _crear_orden_servicio(CEDULA_CLIENTE, imei)
        yield {"cliente_id": CEDULA_CLIENTE, "id_producto": id_producto, "id_orden": id_orden}
    finally:
        if id_orden:
            _eliminar_orden_servicio(id_orden)
        _eliminar_equipo(IMEI_EQUIPO)
        if id_producto:
            eliminar_producto_temporal(id_producto)
        eliminar_cliente_temporal(CEDULA_CLIENTE)


class TestConsultarInformacionOrden:

    def test_orden_pendiente(self, orden_taller):
        info = orden_taller
        resultado = James(ID_orden=info["id_orden"]).consultar_informacion_orden()

        orden = resultado["orden"]
        assert orden["id_orden"] == info["id_orden"]
        assert orden["estado_orden"] == "Pendiente"
        assert orden["descripcion_reparacion"] == "Pantalla rota de prueba"
        assert orden["nota_orden"] is None
        assert orden["fecha_salida"] is None
        assert orden["id_producto"] == info["id_producto"]
        assert orden["nombre_producto"] == "Prod Integra James"
        assert orden["clase_producto"] == "Telefono"
        assert orden["marca_producto"] == "Samsung"
        assert orden["color_equipo"] == "Azul"
        assert orden["capacidad_equipo"] == "256GB"

        # Interacción inicial (Pendiente) sin tests
        interacciones = resultado["interacciones"]
        assert len(interacciones) == 1
        assert interacciones[0]["accion_interaccion"] == "Pendiente"
        assert str(interacciones[0]["id_empleado_interaccion"]) == EMPLEADO_ADMIN
        assert interacciones[0]["tests"] == []

        resumen = resultado["resumen"]
        assert resumen == {
            "total_interacciones": 1,
            "total_tests": 0,
            "estado_actual": "Pendiente",
        }

    def test_orden_con_revision_tecnica(self, orden_taller):
        info = orden_taller
        Tests(
            ID_orden=info["id_orden"],
            Numero_test=1,
            lista_tests=[
                {"nombre": "Mica", "resultado": "Funciona"},
                {"nombre": "LCD", "resultado": "No funciona"},
            ],
            ID_empleado=int(EMPLEADO_ADMIN),
        ).registrar_revision_test()

        resultado = James(ID_orden=info["id_orden"]).consultar_informacion_orden()

        # La revisión crea una segunda interacción (la última en el orden ASC)
        interaccion_revision = next(
            i for i in resultado["interacciones"] if i["tests"]
        )
        nombres = {t["nombre_test"] for t in interaccion_revision["tests"]}
        assert nombres == {"Mica", "LCD"}

        resumen = resultado["resumen"]
        assert resumen["total_interacciones"] == 2  # Pendiente + Revisión
        assert resumen["total_tests"] == 2

    def test_orden_inexistente(self):
        id_fantasma = "OS9999999"
        resultado = James(ID_orden=id_fantasma).consultar_informacion_orden()

        assert resultado == f"No se encontró ninguna orden con ID '{id_fantasma}'."


class TestConsultarTecnicosConEspecialidades:

    def test_incluye_tecnico_temporal_con_especialidad(self):
        id_especialidad = None
        try:
            resultado = Especialidad(
                nombre_especialidad="Esp James",
                descripcion_especialidad="Especialidad temporal de James",
            ).agregar_especialidad()
            id_especialidad = Especialidad(
                nombre_especialidad="Esp James"
            ).obtener_id_por_nombre()
            assert resultado == "Especialidad agregada exitosamente."

            resultado = Empleados(
                id_empleado=CEDULA_TECNICO,
                id_cargo="CRG0000001",  # Técnico
                nombre_empleado="Tecnico",
                apellido_empleado="James",
                celular_empleado="04141234567",
                correo_empleado="tecnico@mail.com",
                direccion_empleado="Barquisimeto",
                especialidades=[id_especialidad],
            ).agregar_empleado()
            assert resultado == "Empleado agregado exitosamente."

            datos = James().consultar_tecnicos_con_especialidades_y_ordenes()

            assert isinstance(datos, dict)
            assert datos["total_tecnicos"] >= 1
            tecnico = next(
                (
                    t
                    for t in datos["tecnicos"]
                    if t["id_empleado"] == int(CEDULA_TECNICO)
                ),
                None,
            )
            assert tecnico is not None
            assert tecnico["cargo"] == "Técnico"
            assert tecnico["total_ordenes_asignadas"] == 0
            especialidad = next(
                (
                    e
                    for e in tecnico["especialidades"]
                    if e["nombre_especialidad"] == "Esp James"
                ),
                None,
            )
            assert especialidad is not None
        finally:
            if Empleados(id_empleado=CEDULA_TECNICO).verificar_empleado():
                Empleados(id_empleado=CEDULA_TECNICO).eliminar_empleado()
            if id_especialidad and Especialidad(
                id_especialidad
            ).verificar_especialidad_por_id():
                Especialidad(id_especialidad).eliminar_especialidad()
