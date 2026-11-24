"""Pruebas de integración del flujo Especialidad → Empleado contra MySQL real.

Escenario: se registra una especialidad y luego se registra un empleado con
esa especialidad (tabla Capacitacion), y se verifica que no se pueda eliminar
una especialidad en uso (FK `Capacitacion_ibfk_2`).
"""
from app.models.empleados import Empleados
from app.models.especialidades import Especialidad

NOMBRE_ESPECIALIDAD = "Especialidad Temporal QA"
DESCRIPCION_ESPECIALIDAD = "Especialidad temporal de integración"
CEDULA = "98765422"
CELULAR = "04141234568"
CORREO = "esp.integracion@mail.com"
ID_CARGO = "CRG0000001"

# Datos sembrados directamente en la BD de prueba
# (bd/tests/ituaccesoriobd.sql, sección 2.1 registros CRUD).
ID_ESPECIALIDAD_EN_USO = "ESP0000106"
CEDULA_EN_USO = "51000008"


def test_registrar_especialidad_y_empleado_con_esa_especialidad():
    # 1. Registrar la especialidad.
    assert (
        Especialidad(
            nombre_especialidad=NOMBRE_ESPECIALIDAD,
            descripcion_especialidad=DESCRIPCION_ESPECIALIDAD,
        ).agregar_especialidad()
        == "Especialidad agregada exitosamente."
    )

    # El SP Crear_especialidad genera el ID (ESP0000001, ESP0000002, ...).
    id_especialidad = Especialidad(
        nombre_especialidad=NOMBRE_ESPECIALIDAD
    ).obtener_id_por_nombre()
    assert id_especialidad is not None
    assert {
        "id": id_especialidad,
        "nombre": NOMBRE_ESPECIALIDAD,
        "descripcion": DESCRIPCION_ESPECIALIDAD,
    } in Especialidad().listar_especialidades()

    # 2. Registrar un empleado con esa especialidad (Capacitacion).
    assert (
        Empleados(
            id_empleado=CEDULA,
            id_cargo=ID_CARGO,
            nombre_empleado="Integracion",
            apellido_empleado="Especialidad",
            celular_empleado=CELULAR,
            correo_empleado=CORREO,
            direccion_empleado="Barquisimeto",
            especialidades=[id_especialidad],
        ).agregar_empleado()
        == "Empleado agregado exitosamente."
    )

    # La relación se refleja en la consulta de especialidades del empleado.
    especialidades = Empleados(id_empleado=CEDULA).consultar_especialidades_empleado()
    assert len(especialidades) == 1
    assert especialidades[0]["id"] == id_especialidad
    assert especialidades[0]["nombre"] == NOMBRE_ESPECIALIDAD


def test_eliminar_especialidad_con_empleado_registrado():
    # Datos sembrados directamente en la BD de prueba:
    # el empleado 51000008 tiene la especialidad ESP0000106 (Capacitacion).
    assert Especialidad(ID_ESPECIALIDAD_EN_USO).verificar_especialidad_por_id() is True
    assert Empleados(id_empleado=CEDULA_EN_USO).verificar_empleado() is True

    # La FK Capacitacion_ibfk_2 (RESTRICT) debe impedir eliminar la especialidad.
    assert (
        Especialidad(ID_ESPECIALIDAD_EN_USO).eliminar_especialidad()
        == f"No se puede eliminar la especialidad con ID {ID_ESPECIALIDAD_EN_USO} "
        "porque está en uso por empleados."
    )

    # El rollback mantiene la especialidad y el empleado intactos.
    assert Especialidad(ID_ESPECIALIDAD_EN_USO).verificar_especialidad_por_id() is True
    assert Empleados(id_empleado=CEDULA_EN_USO).verificar_empleado() is True
